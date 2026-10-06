"""Matched training-context and candidate-removal studies using the current models."""

import math
from pathlib import Path as path_type

import numpy as np
import pandas as pd
import torch

from ..io import digest, read, rng_for, write
from ..policy.benchmark import fit_predictors, load_actor
from ..policy.episodes import prediction_engine, role_data, validation_score
from ..policy.network import acquisition_policy, collate
from ..policy.optimizers import pack, ppo_update
from ..settings import artifact_root, data_root
from ..training import atomic_torch_save, implementation_hashes


def lower_half_context(pool, rng, fraction=0.5, count=1):
    """Sample an ordered free context from the worst fraction of a minimization pool.

    Ties are randomized before sorting. A fraction is converted to a count using
    floor, with a minimum of one. The first selected molecule is the reference.
    """
    if not 0 < fraction <= 1 or count < 1:
        raise ValueError("Require a fraction in (0, 1] and a positive context size")
    order = rng.permutation(len(pool["y"]))
    worst = order[np.argsort(-np.asarray(pool["y"])[order], kind="stable")]
    eligible = worst[: max(1, int(len(order) * fraction))]
    return [
        int(value)
        for value in rng.choice(eligible, min(count, len(eligible)), replace=False)
    ]


def remove_top(pool, count, rng):
    """Remove exactly count best molecules, retaining at least three and original order.

    This creates a new pool identity for the prediction cache. It never mutates
    the source pool; all compound-indexed arrays used by the prediction engine
    are subset together. Boundary ties are randomized, so tied optima can remain.
    """
    if count < 0 or count > len(pool["y"]) - 3:
        raise ValueError("Top removal must leave at least three compounds")
    if not count:
        return pool
    order = rng.permutation(len(pool["y"]))
    best = order[np.argsort(np.asarray(pool["y"])[order], kind="stable")][:count]
    kept = np.setdiff1d(np.arange(len(order)), best)
    result = dict(pool)
    for name in ("indices", "y", "objective"):
        if name in pool:
            result[name] = np.asarray(pool[name])[kept].copy()
    result["pool_id"] = f'{pool["pool_id"]}_without_' + "_".join(map(str, sorted(best)))
    result["source_pool_id"] = pool["pool_id"]
    result["retained_positions"] = kept.tolist()
    return result


def training_case(pools, rng, arm):
    """Mix unchanged cases with feasible multi-hit or top-removal augmentation."""
    large = [pool for pool in pools if len(pool["y"]) >= 15]
    for _ in range(100):
        choices = large if large and rng.random() < 0.5 else pools
        pool = choices[int(rng.integers(len(choices)))]
        if pool["subset"] != "train":
            raise ValueError("Augmentation is restricted to training pools")
        maximum = min(arm.get("remove_max", 0), len(pool["y"]) - 3)
        if maximum and rng.random() < arm.get("augmentation_probability", 0.5):
            pool = remove_top(pool, int(rng.integers(1, maximum + 1)), rng)
        count = 1
        feasible = min(arm.get("context_max", 1), max(1, len(pool["y"]) // 2))
        if feasible > 1 and rng.random() < arm.get("augmentation_probability", 0.5):
            count = int(rng.integers(2, feasible + 1))
        observed = lower_half_context(pool, rng, arm.get("fraction", 0.5), count)
        if np.min(np.asarray(pool["y"])[observed]) > np.min(pool["y"]):
            return pool, observed
    raise ValueError("Could not find a nonterminal training context")


def fixed_cases(data, subset, fraction, draws, pool_limit=None):
    """Keep pool selection and latent random draws identical across treatment arms."""
    pools = [pool for pool in data.pools if pool["subset"] == subset]
    if pool_limit and len(pools) > pool_limit:
        rng = rng_for("augmentation_validation_pools", data.fold, data.endpoint)
        pools = [pools[index] for index in rng.permutation(len(pools))[:pool_limit]]
    cases = []
    for pool in pools:
        for draw in range(draws):
            rng = rng_for(
                "augmentation_start",
                data.fold,
                data.endpoint,
                subset,
                pool["pool_id"],
                draw,
            )
            observed = lower_half_context(pool, rng, fraction)
            cases.append((pool, observed, draw))
    return cases


def case_manifest(cases):
    return [
        dict(pool_id=pool["pool_id"], group=pool["group"], observed=observed, draw=draw)
        for pool, observed, draw in cases
    ]


def purchase_counts(pool, initial, order):
    """Ties at the kth rank qualify; count only purchases after the free context."""
    values = np.asarray(pool["y"])
    best = float(values[initial].min())
    counts, random = {}, {}
    for rank in range(1, 5):
        threshold = float(np.sort(values)[min(rank, len(values)) - 1])
        if best <= threshold:
            counts[f"top{rank}"] = 0
            random[f"random_top{rank}"] = 0.0
        else:
            positions = [
                position + 1
                for position, index in enumerate(order)
                if values[index] <= threshold
            ]
            if not positions:
                raise ValueError(
                    "The supplied trajectory never reaches a qualifying molecule"
                )
            counts[f"top{rank}"] = positions[0]
            qualifying = int(np.sum(values <= threshold))
            random[f"random_top{rank}"] = (len(values) - len(initial) + 1) / (
                qualifying + 1
            )
    return {**counts, **random}


@torch.no_grad()
def rollout(model, engine, pool, initial, rng=None, rule="policy"):
    """Only the environment sees hidden labels to assign rewards and termination."""
    observed = list(initial)
    records, order = [], []
    while np.min(np.asarray(pool["y"])[observed]) > np.min(pool["y"]):
        state = engine.state(pool, observed)
        if rule == "direct_ei":
            action, logp, value = int(np.argmax(state["log_ei"])), 0.0, 0.0
        else:
            model.eval()
            scores, values = model(collate([state]))
            probabilities = torch.softmax(scores[0], -1).double().numpy()
            probabilities /= probabilities.sum()
            action = (
                int(np.argmax(probabilities))
                if rng is None
                else int(rng.choice(len(probabilities), p=probabilities))
            )
            logp, value = float(torch.log_softmax(scores[0], -1)[action]), float(
                values[0]
            )
        molecule = int(state["ids"][action])
        records.append((state, action, logp, value))
        observed.append(molecule)
        order.append(molecule)
    row = dict(
        pool_id=pool["pool_id"],
        group=pool["group"],
        pool_size=len(pool["y"]),
        reference=initial[0],
        initial_context=list(initial),
        order=order,
    )
    row.update(purchase_counts(pool, initial, order))
    return records, row


def evaluate(model, engine, cases, rule="policy"):
    return [
        dict(rollout(model, engine, pool, observed, rule=rule)[1], draw=draw)
        for pool, observed, draw in cases
    ]


def evaluate_checkpoint(engine, cases, checkpoint, output, predictor_hashes):
    """Reuse acquisition cases only for identical actor/predictor files and starts."""
    checkpoint = path_type(checkpoint)
    output = path_type(output)
    if not checkpoint.is_absolute() or not output.is_absolute():
        raise ValueError("Checkpoint and evaluation paths must be absolute")
    for path, expected in predictor_hashes.items():
        if digest(path_type(path)) != expected:
            raise RuntimeError("Predictor checkpoint changed before evaluation")
    signature = dict(
        actor_checkpoint=str(checkpoint),
        actor_checkpoint_sha256=digest(checkpoint),
        actor_specification_sha256=digest(checkpoint.parent / "specification.json"),
        predictor_hashes=predictor_hashes,
        fold=engine.data.fold,
        endpoint=engine.data.endpoint,
        roles_sha256=engine.data.roles_sha256,
        feature_set=engine.feature_set,
        cases=case_manifest(cases),
        implementation=implementation_hashes(),
    )
    if output.exists():
        saved = read(output)
        if saved["provenance"] != signature:
            raise RuntimeError(
                "Cached evaluation provenance changed; use a new output_directory"
            )
        return saved["rows"]
    actor = load_actor(checkpoint)
    if digest(checkpoint) != signature["actor_checkpoint_sha256"]:
        raise RuntimeError("Actor checkpoint changed while loading")
    rows = [
        dict(
            row,
            actor_checkpoint=str(checkpoint),
            actor_checkpoint_sha256=signature["actor_checkpoint_sha256"],
        )
        for row in evaluate(actor, engine, cases)
    ]
    write(output, dict(provenance=signature, rows=rows))
    return rows


def fit_policy(engine, config, arm, trial, seed, output, predictor_hashes):
    """Train from a fresh initialization, or resume the identical recorded run."""
    output.mkdir(parents=True, exist_ok=True)
    cases = fixed_cases(
        engine.data,
        "validation",
        arm["fraction"],
        config["validation_draws"],
        config.get("validation_pool_limit"),
    )
    signature = dict(
        config=config,
        arm=arm,
        trial=trial,
        seed=seed,
        predictor_hashes=predictor_hashes,
        roles_sha256=engine.data.roles_sha256,
        validation_cases=case_manifest(cases),
        implementation=implementation_hashes(),
    )
    spec = output / "specification.json"
    if spec.exists() and read(spec) != signature:
        raise RuntimeError(
            "Augmentation provenance changed; use a new output_directory"
        )
    write(spec, signature)
    if (output / "completed.json").exists():
        completed = read(output / "completed.json")
        if completed.get("checkpoint_sha256") != digest(output / "best.pt"):
            raise RuntimeError(
                "Completed actor checkpoint changed; use a new output_directory"
            )
        return completed
    torch.manual_seed(seed)
    first = engine.state(engine.data.policy_training[0], [0])
    network_config = dict(
        feature_count=first["scalar"].shape[1], width=config["width"], decoder_depth=2
    )
    model = acquisition_policy(network_config)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=trial["learning_rate"], weight_decay=0.001
    )
    rng = rng_for("augmentation_rollouts", engine.data.fold, engine.data.endpoint, seed)
    minibatch_rng = rng_for(
        "augmentation_minibatches", engine.data.fold, engine.data.endpoint, seed
    )
    start, best, history, transitions = 0, math.inf, [], 0
    if (output / "resume.pt").exists():
        saved = torch.load(output / "resume.pt", weights_only=False, map_location="cpu")
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
        rng.bit_generator.state = saved["rng"]
        minibatch_rng.bit_generator.state = saved["minibatch_rng"]
        torch.set_rng_state(saved["torch_rng"])
        start, best, history, transitions = (
            saved["step"] + 1,
            saved["best"],
            saved["history"],
            saved["transitions"],
        )
    for step in range(start, config["updates"] + 1):
        statistics = {}
        if step:
            records = []
            for _ in range(config["episodes_per_update"]):
                pool, initial = training_case(engine.data.policy_training, rng, arm)
                record, _ = rollout(model, engine, pool, initial, rng)
                records.append(record)
            transitions += sum(map(len, records))
            statistics = ppo_update(
                model, optimizer, pack(records), trial, minibatch_rng
            )
        if (
            not step
            or step % config["validate_every"] == 0
            or step == config["updates"]
        ):
            score = validation_score(evaluate(model, engine, cases))
            if not np.isfinite(score):
                raise FloatingPointError("Nonfinite validation acquisition score")
            history.append(
                dict(
                    step=step,
                    validation_purchases=score,
                    transitions=transitions,
                    **statistics,
                )
            )
            if score < best:
                best = score
                atomic_torch_save(
                    output / "best.pt",
                    dict(
                        model=model.state_dict(),
                        configuration=network_config,
                        step=step,
                        validation_score=score,
                        arm=arm,
                        trial=trial,
                        seed=seed,
                    ),
                )
            atomic_torch_save(
                output / "resume.pt",
                dict(
                    model=model.state_dict(),
                    optimizer=optimizer.state_dict(),
                    step=step,
                    best=best,
                    transitions=transitions,
                    history=history,
                    rng=rng.bit_generator.state,
                    minibatch_rng=minibatch_rng.bit_generator.state,
                    torch_rng=torch.get_rng_state(),
                ),
            )
            write(output / "history.json", history)
    result = dict(
        path=str(output / "best.pt"),
        checkpoint_sha256=digest(output / "best.pt"),
        validation_score=best,
        seed=seed,
        trial=trial,
        arm=arm,
        transitions=transitions,
    )
    write(output / "completed.json", result)
    return result


def summarize(rows, output):
    """Average starts and fitted seeds per pool, then pools, then endpoints equally."""
    frame = pd.DataFrame(rows)
    frame.to_csv(output / "acquisition_cases.csv", index=False)
    metrics = [f"top{rank}" for rank in range(1, 5)]
    tables = []
    for cutoff in (3, 15, 20, 25, 30):
        eligible = frame[frame.pool_size >= cutoff]
        pooled = (
            eligible.groupby(["endpoint", "method", "fraction", "pool_id"])[metrics]
            .mean()
            .reset_index()
        )
        for (endpoint, method, fraction), block in pooled.groupby(
            ["endpoint", "method", "fraction"]
        ):
            tables.append(
                dict(
                    endpoint=endpoint,
                    method=method,
                    fraction=fraction,
                    cutoff=cutoff,
                    pools=len(block),
                    **block[metrics].mean().to_dict(),
                )
            )
    table = pd.DataFrame(tables)
    macro = (
        table.groupby(["method", "fraction", "cutoff"])[metrics].mean().reset_index()
    )
    macro["endpoint"] = "all"
    table = pd.concat([table, macro], ignore_index=True)
    table.to_csv(output / "acquisition_summary.csv", index=False)
    from .augmentation_plots import plot_results

    plot_results(table, output / "figures")


def run(config_file):
    config_file = path_type(config_file)
    if not config_file.is_absolute():
        raise ValueError("Configuration path must be absolute")
    config = read(config_file)
    output = artifact_root / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    protocol = dict(
        config=config,
        dataset_hashes={
            str(fold): digest(data_root / f"fold_{fold}" / "dataset.json")
            for fold in config["folds"]
        },
        implementation=implementation_hashes(),
        results_kind="fresh current-model policy-augmentation replication; not an exact historical replay",
    )
    if (output / "protocol.json").exists() and read(
        output / "protocol.json"
    ) != protocol:
        raise RuntimeError("Protocol changed; choose a new output_directory")
    write(output / "protocol.json", protocol)
    torch.set_num_threads(1)
    rows = []
    for fold in config["folds"]:
        for endpoint in config["endpoints"]:
            data = role_data(fold, endpoint)
            base = output / f"fold_{fold}" / endpoint
            models, hashes = fit_predictors(data, config, base)
            engine = prediction_engine(data, models, config["feature_set"])
            test_cases = {
                fraction: fixed_cases(data, "test", fraction, config["test_draws"])
                for fraction in config["fractions"]
            }
            write(
                base / "test_cases.json",
                {
                    str(fraction): case_manifest(cases)
                    for fraction, cases in test_cases.items()
                },
            )
            for arm in config["arms"]:
                candidates = [
                    fit_policy(
                        engine,
                        config,
                        arm,
                        trial,
                        config["seeds"][0],
                        base
                        / arm["name"]
                        / f"trial_{index}"
                        / f'seed_{config["seeds"][0]}',
                        hashes,
                    )
                    for index, trial in enumerate(config["trials"])
                ]
                selected = min(
                    candidates, key=lambda result: result["validation_score"]
                )
                write(
                    base / arm["name"] / "selection.json",
                    dict(candidates=candidates, selected=selected),
                )
                fitted = [selected] + [
                    fit_policy(
                        engine,
                        config,
                        arm,
                        selected["trial"],
                        seed,
                        base / arm["name"] / "selected" / f"seed_{seed}",
                        hashes,
                    )
                    for seed in config["seeds"][1:]
                ]
                fractions = (
                    config["fractions"]
                    if arm["name"] == "baseline"
                    else [arm["fraction"]]
                )
                for result in fitted:
                    for fraction in fractions:
                        checkpoint = path_type(result["path"])
                        evaluated = evaluate_checkpoint(
                            engine,
                            test_cases[fraction],
                            checkpoint,
                            checkpoint.parent
                            / "evaluations"
                            / f"fraction_{round(100 * fraction)}.json",
                            hashes,
                        )
                        rows.extend(
                            dict(
                                row,
                                method=arm["name"],
                                fraction=fraction,
                                endpoint=endpoint,
                                fold=fold,
                                seed=result["seed"],
                            )
                            for row in evaluated
                        )
                print(fold, endpoint, arm["name"], "complete", flush=True)
            for fraction, cases in test_cases.items():
                for row in evaluate(None, engine, cases, rule="direct_ei"):
                    common = dict(
                        fraction=fraction, endpoint=endpoint, fold=fold, seed=-1
                    )
                    rows.append(dict(row, method="direct_ei", **common))
                    random = dict(row, method="random", **common)
                    random.update(
                        {f"top{rank}": row[f"random_top{rank}"] for rank in range(1, 5)}
                    )
                    rows.append(random)
            write(
                base / "evaluation.json",
                [
                    row
                    for row in rows
                    if row["fold"] == fold and row["endpoint"] == endpoint
                ],
            )
    summarize(rows, output)
    write(
        output / "completed.json",
        dict(
            rows=len(rows), conditions=len(config["folds"]) * len(config["endpoints"])
        ),
    )
