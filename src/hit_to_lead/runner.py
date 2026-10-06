"""Validation-only configuration selection with explicit numerical failures."""

import math
import os
import traceback
import shutil
from pathlib import Path as path_type
from concurrent.futures import (
    ProcessPoolExecutor as process_pool_executor,
    as_completed,
)
import torch
from .settings import (
    benchmark_root,
    configured_methods,
    outer_folds,
    configured_endpoints,
    worker_count,
    ensemble_seeds,
    search_trials,
    search_updates,
    final_updates,
    validation_pool_limit,
    configuration,
)
from .io import read, write, digest
from .data import series_dataset
from .training import train, load, implementation_hashes
from .evaluation import evaluate_family

recovery_root = benchmark_root / "recovery"


def numerical(error):
    message = str(error).lower()
    if isinstance(error, FloatingPointError):
        return True
    if isinstance(error, torch.linalg.LinAlgError):
        return True
    if isinstance(error, AssertionError):
        return any(
            (
                f.name == "validate"
                and f.filename
                == str(path_type(__file__).resolve().with_name("training.py"))
                for f in traceback.extract_tb(error.__traceback__)
            )
        )
    if (
        isinstance(error, ValueError)
        and "invalid values" in message
        and ("nan" in message or "inf" in message)
    ):
        return True
    if (
        isinstance(error, ValueError)
        and "out of range float values are not json compliant" in message
    ):
        return True
    if isinstance(error, (ValueError, RuntimeError)):
        return any(
            (
                s in message
                for s in (
                    "non-finite",
                    "nonfinite",
                    "tensor([[nan",
                    "tensor([nan",
                    "tensor([[inf",
                    "positive-definite",
                    "positive definite",
                    "failed stationarity",
                    "invalid predictive variance",
                )
            )
        )
    return False


def guarded_validation(model, cases):
    """Reject the entire configuration if any validation case is nonfinite."""
    model.eval()
    values = []
    with torch.no_grad():
        for episode in cases:
            prediction = model.predict(episode.context, episode.query)
            if (
                not torch.isfinite(prediction.loc).all()
                or not torch.isfinite(prediction.scale).all()
            ):
                raise FloatingPointError(
                    "Nonfinite validation prediction for " + str(episode.meta)
                )
            value = float(-prediction.log_prob(episode.target).mean())
            if not math.isfinite(value):
                raise FloatingPointError("Nonfinite validation NLL")
            values.append(value)
    from .data import validation_weights

    return float(validation_weights(cases) @ values)


def attempt_fit(data, c, seed, path, updates, cases):
    failure = path / "numerical_failure.json"
    if failure.exists():
        return None
    try:
        return train(data, c, seed, path, updates, validation_cases=cases)
    except Exception as error:
        if not numerical(error):
            raise
        write(
            failure,
            dict(
                error=repr(error),
                traceback=traceback.format_exc(),
                configuration=c,
                seed=seed,
                status="configuration rejected; no test data consulted",
                implementation=implementation_hashes(),
            ),
        )
        return None


def save_original_selection(base):
    selection = base / "selection.json"
    original = base / "selection_before_recovery.json"
    if selection.exists() and (not original.exists()):
        shutil.copy2(selection, original)


def fit_condition(fold, endpoint, method):
    torch.set_num_threads(1)
    data = series_dataset(fold, endpoint)
    base = benchmark_root / "runs" / f"fold_{fold}" / endpoint / method
    cases = data.cases("validation", 1, validation_pool_limit)
    status = recovery_root / "conditions" / f"fold_{fold}" / endpoint / f"{method}.json"
    if status.exists() and read(status)["status"] in ("complete", "unavailable"):
        return read(status)
    write(status, dict(status="training", fold=fold, endpoint=endpoint, method=method))
    if method == "alpaca_no_offset":
        parent = base.parent / "alpaca" / "selection.json"
        if not parent.exists():
            record = dict(
                status="unavailable",
                fold=fold,
                endpoint=endpoint,
                method=method,
                reason="The offset-enabled ALPaCA condition is unavailable",
            )
            write(status, record)
            return record
        selected = read(parent)
        config = dict(selected["configuration"], method=method)
        for seed in ensemble_seeds:
            result = attempt_fit(
                data,
                config,
                seed,
                base / "final" / f"seed_{seed}",
                final_updates,
                cases,
            )
            if result is None:
                record = dict(
                    status="unavailable",
                    fold=fold,
                    endpoint=endpoint,
                    method=method,
                    reason="Matched no-offset fit failed; no independent retuning",
                )
                write(status, record)
                return record
        write(
            base / "selection.json",
            dict(
                configuration=config,
                source_selection=selected,
                criterion="Matched offset-model hyperparameters; fresh weights; no ablation-specific search",
            ),
        )
        record = dict(status="complete", fold=fold, endpoint=endpoint, method=method)
        write(status, record)
        return record
    if method == "finetune":
        transfer = base.parent / "transfer"
        if not (transfer / "selection.json").exists():
            record = dict(
                status="unavailable",
                fold=fold,
                endpoint=endpoint,
                method=method,
                reason="Transfer prerequisite unavailable",
            )
            write(status, record)
            return record
        selected = read(transfer / "selection.json")
        candidates = []
        for trial, (lr, steps, penalty) in enumerate(
            ((0.003, 1, 0.1), (0.01, 3, 0.01), (0.03, 5, 0.1))
        ):
            c = dict(
                selected["configuration"],
                method=method,
                inner_lr=lr,
                inner_steps=steps,
                inner_penalty=penalty,
            )
            result = dict(
                trial=trial, configuration=c, validation_nll=None, eligible=False
            )
            try:
                scores = [
                    guarded_validation(
                        load(transfer / "final" / f"seed_{seed}/best.pt", c), cases
                    )
                    for seed in ensemble_seeds
                ]
                result.update(
                    validation_nll=scores[0],
                    eligible=True,
                    member_validation_nll=scores,
                )
            except Exception as error:
                if not numerical(error):
                    raise
                result["failure"] = repr(error)
            candidates.append(result)
        eligible = [c for c in candidates if c["eligible"]]
        write(base / "recovery_candidates.json", candidates)
        if not eligible:
            record = dict(
                status="unavailable",
                fold=fold,
                endpoint=endpoint,
                method=method,
                reason="No predeclared fine-tuning rule finite on validation for every member",
            )
        else:
            winner = min(eligible, key=lambda c: c["validation_nll"])
            save_original_selection(base)
            write(
                base / "selection.json",
                dict(
                    **winner,
                    candidates=candidates,
                    training="Exact selected transfer checkpoints; numerical stability required for all three members; ranking still uses seed 11 validation NLL",
                ),
            )
            record = dict(
                status="complete",
                fold=fold,
                endpoint=endpoint,
                method=method,
                trial=winner["trial"],
            )
        write(status, record)
        return record
    candidates = []
    for trial in range(len(search_trials)):
        c = configuration(method, trial)
        if method == "reference":
            c["lr"] = (0.001, 0.0003, 0.003)[trial]
        result = attempt_fit(
            data,
            c,
            ensemble_seeds[0],
            base / "search" / f"trial_{trial}",
            search_updates,
            cases,
        )
        candidates.append(
            dict(
                trial=trial,
                configuration=c,
                validation_nll=None if result is None else result["validation_nll"],
                eligible=result is not None,
            )
        )
    eligible = sorted(
        [c for c in candidates if c["eligible"]], key=lambda c: c["validation_nll"]
    )
    write(base / "recovery_candidates.json", candidates)
    for winner in eligible:
        trial = winner["trial"]
        final = base / "final"
        rejected = base / f"final_rejected_trial_{trial}"
        if rejected.exists():
            continue
        specs = list(final.glob("seed_*/specification.json"))
        if specs and read(specs[0])["configuration"] != winner["configuration"]:
            old_config = read(specs[0])["configuration"]
            old_trial = next(
                (c["trial"] for c in candidates if c["configuration"] == old_config)
            )
            old_destination = base / f"final_rejected_trial_{old_trial}"
            if old_destination.exists():
                raise RuntimeError(
                    "Conflicting recovery archive " + str(old_destination)
                )
            final.rename(old_destination)
        failed = False
        for seed in ensemble_seeds:
            if (
                attempt_fit(
                    data,
                    winner["configuration"],
                    seed,
                    final / f"seed_{seed}",
                    final_updates,
                    cases,
                )
                is None
            ):
                failed = True
                break
        if failed:
            final.rename(rejected)
            write(
                rejected / "rejection.json",
                dict(
                    trial=trial,
                    reason="A required final member failed numerically; configuration excluded before test evaluation",
                ),
            )
            continue
        save_original_selection(base)
        write(
            base / "selection.json",
            dict(
                **winner,
                candidates=candidates,
                criterion="Lowest seed-11 validation NLL among predeclared settings completing all three final fits; no test selection",
            ),
        )
        record = dict(
            status="complete", fold=fold, endpoint=endpoint, method=method, trial=trial
        )
        write(status, record)
        return record
    record = dict(
        status="unavailable",
        fold=fold,
        endpoint=endpoint,
        method=method,
        reason="No predeclared configuration completed all required fits without numerical failure",
    )
    write(status, record)
    return record


def eval_condition(job):
    fold, endpoint, method = job
    state = read(
        recovery_root / "conditions" / f"fold_{fold}" / endpoint / f"{method}.json"
    )
    if state["status"] != "complete":
        return state
    failure = (
        benchmark_root
        / "evaluations"
        / f"fold_{fold}"
        / endpoint
        / method
        / "evaluation_failure.json"
    )
    if failure.exists():
        return read(failure)
    try:
        evaluate_family(fold, endpoint, method)
        return dict(status="complete", fold=fold, endpoint=endpoint, method=method)
    except Exception as error:
        if not numerical(error):
            raise
        result = dict(
            status="unavailable",
            fold=fold,
            endpoint=endpoint,
            method=method,
            reason="Numerical failure on held-out evaluation; no replacement selected",
            error=repr(error),
            traceback=traceback.format_exc(),
        )
        write(
            benchmark_root
            / "evaluations"
            / f"fold_{fold}"
            / endpoint
            / method
            / "evaluation_failure.json",
            result,
        )
        return result


def run_jobs(pool, jobs, fn, stage):
    errors = []
    outputs = []
    futures = {
        pool.submit(fn, *job) if fn == fit_condition else pool.submit(fn, job): job
        for job in jobs
    }
    for future in as_completed(futures):
        job = futures[future]
        try:
            result = future.result()
            outputs.append(result)
            print(stage, job, result["status"], flush=True)
        except Exception as error:
            result = dict(
                job=list(job),
                stage=stage,
                error=repr(error),
                traceback=traceback.format_exc(),
            )
            errors.append(result)
            write(recovery_root / "fatal_errors.json", errors)
            print("ERROR", stage, job, repr(error), flush=True)
        write(
            benchmark_root / "run_status.json",
            dict(
                stage=stage,
                device="cpu",
                workers=worker_count,
                pid=os.getpid(),
                stage_completed=len(outputs) + len(errors),
                stage_total=len(jobs),
                fatal_errors=len(errors),
                recovery=True,
            ),
        )
    if errors:
        raise RuntimeError(
            "Recovery encountered programming/provenance errors; see recovery/fatal_errors.json"
        )
    return outputs


def main():
    """Run fresh or resume-compatible CPU fits, then evaluate and report.

    Dependent controls follow their parent models. Numerical failure makes an
    entire condition unavailable. A test failure never triggers retuning.
    The output tree is separate from the published experiment directories.
    """
    import fcntl
    import platform
    from .settings import run_settings, data_root
    from .reporting import report_run

    recovery_root.mkdir(parents=True, exist_ok=True)
    for fold in outer_folds:
        if not (data_root / f"fold_{fold}" / "dataset.json").exists():
            raise FileNotFoundError("Run scripts/prepare_data.py before the benchmark.")
    dependencies = {"finetune": "transfer", "alpaca_no_offset": "alpaca"}
    for child, parent in dependencies.items():
        if child in configured_methods and parent not in configured_methods:
            raise ValueError(f"{child} requires {parent} in the configured run")
    protocol = dict(
        settings=run_settings,
        implementation=implementation_hashes(),
        data_hashes={
            f"fold_{f}/{name}": digest(data_root / f"fold_{f}" / name)
            for f in outer_folds
            for name in ("dataset.json", "features.npz")
        },
        device="cpu",
        python=platform.python_version(),
        selection="Validation NLL only; unstable configurations excluded before testing",
        likelihood="Native marginal mixtures; no post-hoc calibration",
        acquisition="K=1 Gaussian moment EI; one free worse-half hit",
        offset_ablation="Reuse ALPaCA selected configuration, initialize afresh",
    )
    with (benchmark_root / "benchmark.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        protocol_path = benchmark_root / "protocol.json"
        if protocol_path.exists() and read(protocol_path) != protocol:
            raise RuntimeError(
                "Run provenance changed. Select a new artifacts_root in config/paths.json."
            )
        write(protocol_path, protocol)
        try:
            with process_pool_executor(max_workers=worker_count) as executor:
                primary = [
                    (f, e, m)
                    for f in outer_folds
                    for e in configured_endpoints
                    for m in configured_methods
                    if m not in dependencies
                ]
                run_jobs(executor, primary, fit_condition, "training")
                dependent = [
                    (f, e, m)
                    for f in outer_folds
                    for e in configured_endpoints
                    for m in configured_methods
                    if m in dependencies
                ]
                if dependent:
                    run_jobs(executor, dependent, fit_condition, "dependent_controls")
                results = run_jobs(
                    executor,
                    [
                        (f, e, m)
                        for f in outer_folds
                        for e in configured_endpoints
                        for m in configured_methods
                    ],
                    eval_condition,
                    "evaluation",
                )
            write(recovery_root / "evaluation_status.json", results)
            report_run()
            write(
                benchmark_root / "run_status.json",
                dict(
                    stage="complete",
                    evaluations=len(results),
                    unavailable=sum(r["status"] != "complete" for r in results),
                ),
            )
        except BaseException as error:
            write(
                benchmark_root / "run_status.json",
                dict(stage="failed", error=repr(error)),
            )
            raise
