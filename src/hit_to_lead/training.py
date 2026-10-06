"""Validation-only selection, resumable fresh fits, and matched transfer controls."""

import time
import math
import hashlib
import json
from pathlib import Path as path_type
import numpy as np
import torch
from torch import nn
from .settings import (
    benchmark_root,
    ensemble_seeds,
    training_batch_size,
    validation_interval,
    validation_pool_limit,
)
from .data import validation_weights
from .io import read, write, digest, rng_for
from .models import build


def implementation_hashes():
    """Hash only this package's scientific modules, independent of user cwd."""
    package = path_type(__file__).resolve().parent
    return {
        str(path.relative_to(package)): digest(path)
        for path in sorted(package.rglob("*.py"))
    }


def validate(model, cases):
    model.eval()
    values = []
    with torch.no_grad():
        for e in cases:
            values.append(
                float(-model.predict(e.context, e.query).log_prob(e.target).mean())
            )
    if not np.isfinite(values).all():
        raise FloatingPointError("Nonfinite validation NLL")
    return float(validation_weights(cases) @ values)


def train(
    data,
    c,
    seed,
    path,
    updates,
    batch_size=training_batch_size,
    validation_cases=None,
    validate_every=validation_interval,
):
    path = path_type(path)
    path.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    model = build(c, data.endpoint)
    cases = validation_cases or data.cases("validation", 1, validation_pool_limit)
    signature = dict(
        configuration=c,
        seed=seed,
        updates=updates,
        batch_size=batch_size,
        validate_every=validate_every,
        validation_cases_sha256=hashlib.sha256(
            json.dumps([e.meta for e in cases], sort_keys=True).encode()
        ).hexdigest(),
        endpoint=data.endpoint,
        fold=data.fold,
        scale=data.scale,
        training_role=getattr(data, "training_role", "full_outer_train"),
        roles_sha256=getattr(data, "roles_sha256", None),
        dataset_sha256=digest(data_directory(data) / "dataset.json"),
        feature_sha256=digest(data_directory(data) / "features.npz"),
        implementation=implementation_hashes(),
    )
    spec = path / "specification.json"
    if spec.exists():
        if read(spec) != signature:
            raise RuntimeError(
                "Existing fit has different provenance. Choose a new output directory: "
                + str(path)
            )
    else:
        write(spec, signature)
    if (path / "completed.json").exists():
        return read(path / "completed.json")
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"]
    )
    rng = rng_for("meta_training", data.fold, data.endpoint, seed)
    start_step = 0
    best = float("inf")
    history = []
    elapsed = 0.0
    if (path / "resume.pt").exists():
        resume = torch.load(path / "resume.pt", weights_only=False, map_location="cpu")
        model.load_state_dict(resume["model"])
        optimizer.load_state_dict(resume["optimizer"])
        start_step = resume["step"]
        best = resume["best"]
        history = resume["history"]
        elapsed = resume["elapsed"]
        rng.bit_generator.state = resume["numpy_rng"]
        torch.set_rng_state(resume["torch_rng"])
    start = time.time()
    for step in range(start_step + 1, updates + 1):
        model.train()
        optimizer.zero_grad()
        episodes = data.sample(rng, batch_size, c["max_context"])
        loss_value = 0.0
        inner_diagnostics = []
        for episode in episodes:
            loss = model.loss(episode)
            if not torch.isfinite(loss):
                raise FloatingPointError((c["method"], step, "nonfinite loss"))
            (loss / batch_size).backward()
            loss_value += float(loss.detach()) / batch_size
            if getattr(model, "last_fit", None):
                inner_diagnostics.append(dict(model.last_fit))
        auxiliary_weight = c.get("auxiliary_pair_weight", 0.0)
        if auxiliary_weight:
            from .models.pair_supervision import pair_loss

            auxiliary = auxiliary_weight * pair_loss(
                model, data, rng, c.get("auxiliary_pair_batch", 64)
            )
            if not torch.isfinite(auxiliary):
                raise FloatingPointError("Nonfinite auxiliary pair likelihood")
            auxiliary.backward()
            loss_value += float(auxiliary.detach())
        norm = nn.utils.clip_grad_norm_(
            model.parameters(), 5.0, error_if_nonfinite=True
        )
        optimizer.step()
        for group in optimizer.param_groups:
            group["lr"] = c["lr"] * (
                0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * step / updates))
            )
        if step == 1 or step % validate_every == 0 or step == updates:
            score = validate(model, cases)
            row = dict(
                step=step,
                loss=loss_value,
                validation_nll=score,
                gradient_norm=float(norm),
                seconds=elapsed + time.time() - start,
            )
            if inner_diagnostics:
                row["inner_optimizer"] = inner_diagnostics
            history.append(row)
            if score < best:
                best = score
                atomic_torch_save(
                    path / "best.pt",
                    dict(
                        model=model.state_dict(),
                        configuration=c,
                        seed=seed,
                        step=step,
                        validation_nll=score,
                        endpoint=data.endpoint,
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
                    elapsed=elapsed + time.time() - start,
                    numpy_rng=rng.bit_generator.state,
                    torch_rng=torch.get_rng_state(),
                ),
            )
            write(path / "progress.json", row)
            write(path / "history.json", history)
    saved = torch.load(path / "best.pt", weights_only=False, map_location="cpu")
    result = dict(
        method=c["method"],
        endpoint=data.endpoint,
        fold=data.fold,
        seed=seed,
        steps=updates,
        best_step=saved["step"],
        validation_nll=best,
        seconds=elapsed + time.time() - start,
        path=str(path / "best.pt"),
    )
    write(path / "completed.json", result)
    return result


def data_directory(data):
    from .settings import data_root

    return data_root / f"fold_{data.fold}"


def atomic_torch_save(path, value):
    path = path_type(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(value, tmp)
    tmp.replace(path)


def load(path, configuration_override=None):
    saved = torch.load(path, weights_only=False, map_location="cpu")
    config = (
        saved["configuration"]
        if configuration_override is None
        else configuration_override
    )
    model = build(config, saved["endpoint"])
    model.load_state_dict(saved["model"])
    model.eval()
    return model


def load_ensemble(fold, endpoint, method):
    base = benchmark_root / "runs" / f"fold_{fold}" / endpoint
    c = read(base / method / "selection.json")["configuration"]
    trained_method = "transfer" if method == "finetune" else method
    return [
        load(base / trained_method / "final" / f"seed_{seed}/best.pt", c)
        for seed in ensemble_seeds
    ]
