"""Fresh, disjoint-role policy comparisons with validation-only selection.

This runner applies the archived optimizer equations to the current benchmark
data interface. Its outputs are new experiments, separate from historical tables.
"""

import copy
import math
from pathlib import Path as path_type
import numpy as np
import pandas as pd
import torch
from ..io import read, write, digest, rng_for
from ..settings import artifact_root, configuration, data_root
from ..training import train, load, atomic_torch_save, implementation_hashes
from .episodes import (
    role_data,
    prediction_engine,
    grouped_rollouts,
    evaluate_policy,
    validation_score,
)
from .network import acquisition_policy, collate
from .optimizers import actor_parameters, pack, ppo_update, trpo_update, dpo_loss
from .grpo import grpo_update


def fit_predictors(data, config, output):
    specification = dict(
        fold=data.fold,
        endpoint=data.endpoint,
        roles=data.roles,
        outcome_scale=data.scale,
        roles_sha256=data.roles_sha256,
    )
    write(output / "roles.json", specification)
    model_config = configuration(config["predictor_method"])
    model_config.update(
        auxiliary_pair_weight=config.get("predictor_auxiliary_pair_weight", 0.0),
        auxiliary_pair_batch=config.get("predictor_auxiliary_pair_batch", 64),
    )
    models, hashes = [], {}
    for seed in config["predictor_seeds"]:
        directory = output / "predictors" / f"seed_{seed}"
        train(
            data,
            model_config,
            seed,
            directory,
            config["predictor_updates"],
            batch_size=config.get("predictor_batch_size", 8),
            validate_every=config.get("predictor_validate_every", 200),
        )
        checkpoint = directory / "best.pt"
        models.append(load(checkpoint))
        hashes[str(checkpoint)] = digest(checkpoint)
    return models, hashes


def trajectory_log_probability(model, record):
    if not record:
        raise ValueError("A preference trajectory must contain a purchase")
    logits = model(collate([item[0] for item in record]))[0]
    actions = torch.tensor([item[1] for item in record])
    return torch.log_softmax(logits, -1).gather(1, actions[:, None]).sum()


def preference_records(initial, engine, pools, seed, count):
    rng = rng_for(
        "fixed_policy_preferences", seed, engine.data.fold, engine.data.endpoint
    )
    groups = grouped_rollouts(initial, engine, pools, rng, groups=count, group_size=2)
    return [
        (min(group, key=len), max(group, key=len))
        for group in groups
        if len(group[0]) != len(group[1])
    ]


def fit_actor(engine, config, arm, trial, seed, path, backbone_hashes):
    path.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(seed)
    example_pool = engine.data.policy_training[0]
    state = engine.state(example_pool, [0])
    network_config = dict(
        feature_count=state["scalar"].shape[1],
        latent_input_size=state["latent"].shape[1],
        latent_dimension=arm.get("latent_dimension", 0),
        width=config["width"],
        decoder_depth=2,
    )
    if network_config["latent_dimension"] and not network_config["latent_input_size"]:
        raise ValueError(
            "Latent acquisition features require the neural reference predictor"
        )
    model = acquisition_policy(network_config)
    initial = copy.deepcopy(model).eval().requires_grad_(False)
    algorithm = arm["algorithm"]
    if algorithm == "trpo":
        parameters = model.critic.parameters()
    else:
        parameters = (
            model.parameters() if algorithm == "ppo" else actor_parameters(model)
        )
    optimizer = torch.optim.AdamW(
        parameters, lr=trial["learning_rate"], weight_decay=0.001
    )
    rng = rng_for(
        "matched_policy_rollouts", engine.data.fold, engine.data.endpoint, seed
    )
    minibatch_rng = rng_for(
        "matched_policy_minibatches", engine.data.fold, engine.data.endpoint, seed
    )
    signature = dict(
        config=config,
        arm=arm,
        trial=trial,
        seed=seed,
        roles_sha256=engine.data.roles_sha256,
        backbone_hashes=backbone_hashes,
        implementation=implementation_hashes(),
    )
    if (path / "specification.json").exists() and read(
        path / "specification.json"
    ) != signature:
        raise RuntimeError(
            "Policy run provenance changed; choose a new output_directory"
        )
    write(path / "specification.json", signature)
    if (path / "completed.json").exists():
        return read(path / "completed.json")
    preferences = (
        preference_records(
            initial,
            engine,
            engine.data.policy_training,
            seed,
            config.get("preference_groups", 128),
        )
        if algorithm == "dpo"
        else []
    )
    if algorithm == "dpo" and not preferences:
        raise ValueError("No unequal-cost preference pairs in the training data")
    start = 0
    transitions = 0
    history = []
    best = math.inf
    if (path / "resume.pt").exists():
        saved = torch.load(path / "resume.pt", weights_only=False, map_location="cpu")
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
        rng.bit_generator.state = saved["rng"]
        minibatch_rng.bit_generator.state = saved["minibatch_rng"]
        torch.set_rng_state(saved["torch_rng"])
        start, best, history, transitions = (
            saved["step"],
            saved["best"],
            saved["history"],
            saved["transitions"],
        )
    for step in range(start, config["updates"] + 1):
        statistics = {}
        if step > start or start > 0:
            if step == start and start > 0:
                continue
            if algorithm == "dpo":
                indices = minibatch_rng.integers(
                    len(preferences), size=config.get("preference_batch", 8)
                )
                chosen, rejected, reference_chosen, reference_rejected = [], [], [], []
                for index in indices:
                    preferred, other = preferences[index]
                    chosen.append(trajectory_log_probability(model, preferred))
                    rejected.append(trajectory_log_probability(model, other))
                    reference_chosen.append(sum(row[2] for row in preferred))
                    reference_rejected.append(sum(row[2] for row in other))
                loss = dpo_loss(
                    torch.stack(chosen),
                    torch.stack(rejected),
                    torch.tensor(reference_chosen),
                    torch.tensor(reference_rejected),
                    trial["beta"],
                )
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    actor_parameters(model), 1.0, error_if_nonfinite=True
                )
                optimizer.step()
                statistics = dict(
                    loss=float(loss.detach()), preference_pairs=len(preferences)
                )
            else:
                groups = grouped_rollouts(
                    model,
                    engine,
                    engine.data.policy_training,
                    rng,
                    groups=config["groups"],
                    group_size=config["group_size"],
                )
                records = [record for group in groups for record in group]
                transitions += sum(map(len, records))
                if algorithm == "grpo":
                    statistics = grpo_update(model, initial, optimizer, groups, trial)
                else:
                    rollout = pack(records)
                    update = ppo_update if algorithm == "ppo" else trpo_update
                    statistics = update(model, optimizer, rollout, trial, minibatch_rng)
        if (
            step == 0
            or step % config["validate_every"] == 0
            or step == config["updates"]
        ):
            rows = evaluate_policy(
                model,
                engine,
                draws=config["validation_draws"],
                pool_limit=config.get("validation_pool_limit"),
            )
            score = validation_score(rows)
            if not np.isfinite(score):
                raise FloatingPointError("Nonfinite policy validation score")
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
                    path / "best.pt",
                    dict(
                        model=model.state_dict(),
                        configuration=network_config,
                        arm=arm,
                        trial=trial,
                        step=step,
                        validation_score=score,
                        seed=seed,
                    ),
                )
            atomic_torch_save(
                path / "resume.pt",
                dict(
                    model=model.state_dict(),
                    optimizer=optimizer.state_dict(),
                    step=step,
                    best=best,
                    history=history,
                    transitions=transitions,
                    rng=rng.bit_generator.state,
                    minibatch_rng=minibatch_rng.bit_generator.state,
                    torch_rng=torch.get_rng_state(),
                ),
            )
            write(path / "history.json", history)
    result = dict(
        path=str(path / "best.pt"),
        validation_score=best,
        transitions=transitions,
        seed=seed,
        arm=arm,
        trial=trial,
        updates=config["updates"],
    )
    write(path / "completed.json", result)
    return result


def load_actor(path):
    state = torch.load(path, weights_only=False, map_location="cpu")
    model = acquisition_policy(state["configuration"])
    model.load_state_dict(state["model"])
    return model.eval()


def summarize(rows, output, config):
    frame = pd.DataFrame(rows)
    frame.to_csv(output / "acquisition_cases.csv", index=False)
    tables = []
    for cutoff in (3, 15, 20, 25, 30):
        eligible = frame[frame.pool_size >= cutoff]
        pools = (
            eligible.groupby(["endpoint", "method", "pool_id"])[
                [f"top{k}" for k in range(1, 5)]
            ]
            .mean()
            .reset_index()
        )
        for (endpoint, method), block in pools.groupby(["endpoint", "method"]):
            tables.append(
                dict(
                    endpoint=endpoint,
                    method=method,
                    cutoff=cutoff,
                    pools=len(block),
                    **block[[f"top{k}" for k in range(1, 5)]].mean().to_dict(),
                )
            )
    table = pd.DataFrame(tables)
    table.to_csv(output / "acquisition_summary.csv", index=False)
    from ..history import acquisition_figures

    acquisition_figures(table, output / "figures", config["title"])


def run(config_file):
    config_file = path_type(config_file)
    if not config_file.is_absolute():
        raise ValueError("The comparison configuration path must be absolute")
    config = read(config_file)
    output = artifact_root / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    protocol = dict(
        config=config,
        implementation=implementation_hashes(),
        dataset_hashes={
            f"fold_{fold}": digest(data_root / f"fold_{fold}" / "dataset.json")
            for fold in config["folds"]
        },
        results_kind="new common-protocol comparison, separate from archived historical results",
    )
    if (output / "protocol.json").exists() and read(
        output / "protocol.json"
    ) != protocol:
        raise RuntimeError("Comparison protocol changed; select a new output_directory")
    write(output / "protocol.json", protocol)
    torch.set_num_threads(1)
    rows = []
    for fold in config["folds"]:
        for endpoint in config["endpoints"]:
            data = role_data(fold, endpoint)
            base = output / f"fold_{fold}" / endpoint
            models, hashes = fit_predictors(data, config, base)
            for arm in config["arms"]:
                engine = prediction_engine(
                    data, models, arm.get("feature_set", "mean_sd")
                )
                trials = config["trials"][arm["algorithm"]]
                candidates = [
                    fit_actor(
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
                    for index, trial in enumerate(trials)
                ]
                selected = min(candidates, key=lambda row: row["validation_score"])
                write(
                    base / arm["name"] / "selection.json",
                    dict(selected=selected, candidates=candidates),
                )
                fitted = [selected] + [
                    fit_actor(
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
                for fitted_actor in fitted:
                    actor = load_actor(fitted_actor["path"])
                    evaluated = evaluate_policy(
                        actor, engine, subset="test", draws=config["test_draws"]
                    )
                    rows.extend(
                        dict(
                            row,
                            method=arm["name"],
                            fold=fold,
                            endpoint=endpoint,
                            seed=fitted_actor["seed"],
                        )
                        for row in evaluated
                    )
                print(fold, endpoint, arm["name"], "complete", flush=True)
            controls = evaluate_policy(
                None,
                prediction_engine(data, models),
                subset="test",
                draws=config["test_draws"],
                rule="direct_ei",
            )
            rows.extend(
                dict(row, method="direct_ei", fold=fold, endpoint=endpoint, seed=-1)
                for row in controls
            )
            for row in controls:
                random = dict(
                    row, method="random", fold=fold, endpoint=endpoint, seed=-1
                )
                random.update({f"top{k}": row[f"random_top{k}"] for k in range(1, 5)})
                rows.append(random)
            write(
                base / "evaluation.json",
                [
                    row
                    for row in rows
                    if row["fold"] == fold and row["endpoint"] == endpoint
                ],
            )
    summarize(rows, output, config)
    write(
        output / "completed.json",
        dict(
            conditions=len(config["folds"]) * len(config["endpoints"]), rows=len(rows)
        ),
    )
