"""Resumption and fixed-query tests using tiny synthetic prepared folds."""

import json
from pathlib import Path as path_type
import tempfile
import unittest
from contextlib import ExitStack as exit_stack
from unittest.mock import patch
import numpy as np
import torch
from hit_to_lead import data as data_module, training, runner, evaluation, settings
from hit_to_lead.data import series_dataset
from hit_to_lead.io import write
from hit_to_lead.settings import configuration


class training_tests(unittest.TestCase):
    def test_split_queries_resume_and_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = path_type(temporary).resolve()
            folder = root / "fold_0"
            folder.mkdir()
            pools = []
            for index, subset in enumerate(["train", "validation", "test"]):
                pools.append(
                    dict(
                        pool_id=f"pool{index}",
                        group=f"group{index}",
                        endpoint="microsomal_clearance",
                        subset=subset,
                        feature_indices=list(range(index * 15, (index + 1) * 15)),
                        objective=np.linspace(-1, 1, 15).tolist(),
                    )
                )
            write(folder / "dataset.json", dict(pools=pools))
            rng = np.random.default_rng(123)
            np.savez(
                folder / "features.npz",
                pca_32=rng.normal(size=(45, 32)).astype(np.float32),
                training_indices=np.arange(15),
            )
            with patch.object(data_module, "data_root", root), patch.object(
                training, "data_directory", lambda _: folder
            ):
                data = series_dataset(0, "microsomal_clearance", True)
                cases = data.cases("validation", 1)
                self.assertTrue(
                    all(case.meta["query"] == cases[0].meta["query"] for case in cases)
                )
                self.assertTrue(
                    all(
                        not set(case.meta["observed"]) & set(case.meta["query"])
                        for case in cases
                    )
                )
                config = configuration("cnp")
                first, resumed = root / "first", root / "resumed"
                kwargs = dict(
                    batch_size=2, validation_cases=cases[:2], validate_every=1
                )
                training.train(data, config, 11, first, 4, **kwargs)
                original = training.validate
                calls = [0]

                def interrupt(model, cases):
                    calls[0] += 1
                    if calls[0] == 2:
                        raise RuntimeError("simulated interruption")
                    return original(model, cases)

                with patch.object(training, "validate", interrupt):
                    with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
                        training.train(data, config, 11, resumed, 4, **kwargs)
                training.train(data, config, 11, resumed, 4, **kwargs)
                a = torch.load(first / "resume.pt", weights_only=False)
                b = torch.load(resumed / "resume.pt", weights_only=False)
                for key, value in a["model"].items():
                    torch.testing.assert_close(value, b["model"][key], atol=0, rtol=0)
                self.assertEqual(a["best"], b["best"])
                with self.assertRaisesRegex(RuntimeError, "different provenance"):
                    training.train(data, dict(config, lr=0.02), 11, first, 4, **kwargs)
                # Exercise selection, dependent controls, and saved evaluation as
                # one small workflow, independently of the expensive real folds.
                output = root / "benchmark"
                with exit_stack() as patches:
                    for module in (runner, training, evaluation):
                        patches.enter_context(
                            patch.object(module, "benchmark_root", output)
                        )
                    for module in (runner, training, settings):
                        patches.enter_context(
                            patch.object(module, "ensemble_seeds", (11,))
                        )
                    patches.enter_context(
                        patch.object(runner, "recovery_root", output / "recovery")
                    )
                    patches.enter_context(patch.object(runner, "search_updates", 2))
                    patches.enter_context(patch.object(runner, "final_updates", 2))
                    patches.enter_context(patch.object(runner, "search_trials", ({},)))
                    for method in (
                        "transfer",
                        "finetune",
                        "alpaca",
                        "alpaca_no_offset",
                    ):
                        result = runner.fit_condition(0, "microsomal_clearance", method)
                        self.assertEqual(result["status"], "complete")
                        self.assertEqual(
                            runner.fit_condition(0, "microsomal_clearance", method),
                            result,
                        )
                    evaluation.evaluate_family(
                        0, "microsomal_clearance", "alpaca_no_offset"
                    )
                    completed = (
                        output
                        / "evaluations/fold_0/microsomal_clearance/alpaca_no_offset/completed.json"
                    )
                    self.assertTrue(completed.exists())
                    evaluation.evaluate_family(
                        0, "microsomal_clearance", "alpaca_no_offset"
                    )
                broken = json.loads((folder / "dataset.json").read_text())
                broken["pools"][1]["group"] = "group0"
                write(folder / "dataset.json", broken)
                with self.assertRaises(AssertionError):
                    series_dataset(0, "microsomal_clearance")
