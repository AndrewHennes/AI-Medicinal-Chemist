"""Train and compare hard subsets for arbitrary configured positive batch sizes."""

from pathlib import Path as path_type
import numpy as np
import pandas as pd
import torch
from ..settings import artifact_root, data_root
from ..io import read, write, rng_for, digest
from ..training import atomic_torch_save, implementation_hashes
from ..policy.episodes import role_data
from ..policy.benchmark import fit_predictors
from .episodes import batch_engine, evaluate
from .models import make_model
from .training import supervised_loss, gumbel_loss, policy_rollouts, ppo_step


def fit(engine, config, model_config, seed, path, backbone_hashes):
    path.mkdir(parents=True, exist_ok=True)
    signature = dict(
        config=config,
        model_config=model_config,
        seed=seed,
        implementation=implementation_hashes(),
        backbone_hashes=backbone_hashes,
    )
    if (path / "specification.json").exists() and read(
        path / "specification.json"
    ) != signature:
        raise RuntimeError(
            "Batch fit provenance changed; select a new output_directory"
        )
    write(path / "specification.json", signature)
    if (path / "completed.json").exists():
        return read(path / "completed.json")
    torch.manual_seed(seed)
    model = make_model(model_config)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config["learning_rate"], weight_decay=0.001
    )
    rng = rng_for("batch_comparison", engine.data.fold, engine.data.endpoint, seed)
    best, history, start = float("inf"), [], 0
    if (path / "resume.pt").exists():
        saved = torch.load(path / "resume.pt", weights_only=False, map_location="cpu")
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
        rng.bit_generator.state = saved["rng"]
        torch.set_rng_state(saved["torch_rng"])
        best, history, start = saved["best"], saved["history"], saved["step"] + 1
    for step in range(start, config["updates"] + 1):
        loss_value = None
        if step:
            if model_config["family"] == "batch_ppo":
                records = policy_rollouts(
                    model, engine, rng, config["batch_sizes"], config["rollouts"]
                )
                loss_value = ppo_step(model, optimizer, records, rng)
            else:
                model.train()
                loss_fn = (
                    gumbel_loss
                    if model_config["family"] == "gumbel"
                    else supervised_loss
                )
                loss = loss_fn(
                    model, engine, rng, config["batch_sizes"], config["training_states"]
                )
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), 1.0, error_if_nonfinite=True
                )
                optimizer.step()
                loss_value = float(loss.detach())
        if step % config["validate_every"] == 0 or step == config["updates"]:
            model.eval()
            rows = evaluate(
                engine,
                model,
                model_config["family"],
                config["batch_sizes"],
                subset="validation",
                draws=1,
                pool_limit=config["validation_pool_limit"],
            )
            ratios = [
                row["rounds"][0] / row["random_rounds"][0]
                for row in rows
                if row["random_rounds"][0] > 0
            ]
            score = float(np.mean(ratios))
            if not np.isfinite(score):
                raise FloatingPointError("Invalid batch validation score")
            history.append(
                dict(step=step, validation_relative_rounds=score, loss=loss_value)
            )
            if score < best:
                best = score
                atomic_torch_save(
                    path / "best.pt",
                    dict(
                        model=model.state_dict(),
                        configuration=model_config,
                        step=step,
                        score=score,
                    ),
                )
            atomic_torch_save(
                path / "resume.pt",
                dict(
                    model=model.state_dict(),
                    optimizer=optimizer.state_dict(),
                    rng=rng.bit_generator.state,
                    torch_rng=torch.get_rng_state(),
                    step=step,
                    best=best,
                    history=history,
                ),
            )
            write(path / "history.json", history)
    result = dict(
        checkpoint=str(path / "best.pt"),
        score=best,
        seed=seed,
        configuration=model_config,
    )
    write(path / "completed.json", result)
    return result


def run(config_file):
    config_file = path_type(config_file)
    if not config_file.is_absolute():
        raise ValueError("The configuration path must be absolute")
    config = read(config_file)
    if config["predictor_method"] != "neural_mean_gp" or any(
        size < 1 for size in config["batch_sizes"]
    ):
        raise ValueError("Use a neural_mean_gp backend and positive batch sizes")
    output = artifact_root / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    protocol = dict(
        config=config,
        implementation=implementation_hashes(),
        data_hashes={
            f"fold_{fold}": digest(data_root / f"fold_{fold}" / "dataset.json")
            for fold in config["folds"]
        },
    )
    if (output / "protocol.json").exists() and read(
        output / "protocol.json"
    ) != protocol:
        raise RuntimeError("Batch protocol changed; select a new output_directory")
    write(output / "protocol.json", protocol)
    torch.set_num_threads(1)
    all_rows = []
    for fold in config["folds"]:
        for endpoint in config["endpoints"]:
            data = role_data(fold, endpoint)
            base = output / f"fold_{fold}" / endpoint
            models, hashes = fit_predictors(data, config, base)
            engine = batch_engine(data, models, config["dimension"])
            methods = []
            for family in config["families"]:
                for seed in config["seeds"]:
                    model_config = dict(
                        family=family,
                        dimension=config["dimension"],
                        width=config["width"],
                        depth=config["depth"],
                        heads=config["heads"],
                        temperature=config["temperature"],
                    )
                    result = fit(
                        engine,
                        config,
                        model_config,
                        seed,
                        base / family / f"seed_{seed}",
                        hashes,
                    )
                    saved = torch.load(
                        result["checkpoint"], weights_only=False, map_location="cpu"
                    )
                    model = make_model(model_config)
                    model.load_state_dict(saved["model"])
                    model.eval()
                    methods.append((family, seed, model))
            methods.extend((method, -1, None) for method in config["controls"])
            for method, seed, model in methods:
                rows = evaluate(
                    engine,
                    model,
                    method,
                    config["batch_sizes"],
                    draws=config["test_draws"],
                )
                all_rows.extend(
                    dict(row, method=method, seed=seed, fold=fold, endpoint=endpoint)
                    for row in rows
                )
                print(fold, endpoint, method, seed, "complete", flush=True)
            write(
                base / "evaluation.json",
                [
                    row
                    for row in all_rows
                    if row["fold"] == fold and row["endpoint"] == endpoint
                ],
            )
    summary = []
    records = []
    for row in all_rows:
        for metric in ("rounds", "compounds"):
            for top in range(1, 5):
                records.append(
                    dict(
                        endpoint=row["endpoint"],
                        method=row["method"],
                        pool_id=row["pool_id"],
                        pool_size=row["pool_size"],
                        batch_size=row["batch_size"],
                        metric=metric,
                        top_k=top,
                        value=row[metric][top - 1],
                        random_value=row["random_" + metric][top - 1],
                    )
                )
    frame = pd.DataFrame(records)
    frame.to_csv(output / "acquisition_cases.csv", index=False)
    for cutoff in (3, 15, 20, 25, 30):
        pools = (
            frame[frame.pool_size >= cutoff]
            .groupby(
                ["endpoint", "method", "pool_id", "batch_size", "metric", "top_k"]
            )[["value", "random_value"]]
            .mean()
            .reset_index()
        )
        for key, block in pools.groupby(
            ["endpoint", "method", "batch_size", "metric", "top_k"]
        ):
            summary.append(
                dict(
                    zip(["endpoint", "method", "batch_size", "metric", "top_k"], key),
                    cutoff=cutoff,
                    value=block.value.mean(),
                    pools=len(block),
                )
            )
    table = pd.DataFrame(summary)
    table.to_csv(output / "summary.csv", index=False)
    from ..history import batch_figures

    batch_figures(table, output / "figures", "New batch-selection comparison")
    write(output / "completed.json", dict(episodes=len(all_rows)))
