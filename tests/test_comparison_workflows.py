"""Small synthetic end-to-end runs, including reporting and restart behavior."""

from contextlib import ExitStack as exit_stack
from pathlib import Path as path_type
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from hit_to_lead import data as data_module, training
from hit_to_lead.io import read, write
from hit_to_lead.settings import repository_root
from hit_to_lead.policy import benchmark as policy_benchmark
from hit_to_lead.batch import benchmark as batch_benchmark


class workflow_tests(unittest.TestCase):
    def test_small_policy_and_batch_comparisons(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = path_type(temporary)
            folder = root / "data/fold_0"
            folder.mkdir(parents=True)
            pools = []
            for index in range(8):
                pools.append(
                    dict(
                        pool_id=f"p{index}",
                        group=f"g{index}",
                        endpoint="microsomal_clearance",
                        subset=(
                            "train"
                            if index < 6
                            else "validation" if index == 6 else "test"
                        ),
                        feature_indices=list(range(6 * index, 6 * (index + 1))),
                        objective=[2.0, 1.0, 0.5, -0.5, -1.0, 0.0],
                    )
                )
            write(folder / "dataset.json", dict(pools=pools))
            np.savez(
                folder / "features.npz",
                pca_32=np.random.default_rng(2).normal(size=(48, 32)).astype(np.float32)
                * 0.2,
                training_indices=np.arange(36),
            )
            with exit_stack() as patches:
                patches.enter_context(
                    patch.object(data_module, "data_root", root / "data")
                )
                patches.enter_context(
                    patch.object(training, "data_directory", lambda _: folder)
                )
                for module in (policy_benchmark, batch_benchmark):
                    patches.enter_context(patch.object(module, "artifact_root", root))
                    patches.enter_context(
                        patch.object(module, "data_root", root / "data")
                    )
                policy = read(repository_root / "config/policy_comparison.json")
                policy.update(
                    folds=[0],
                    endpoints=["microsomal_clearance"],
                    seeds=[11],
                    predictor_seeds=[11],
                    predictor_updates=2,
                    predictor_batch_size=2,
                    predictor_validate_every=1,
                    updates=2,
                    validate_every=1,
                    validation_draws=1,
                    validation_pool_limit=1,
                    test_draws=1,
                    width=8,
                    groups=1,
                    group_size=2,
                    preference_groups=16,
                    preference_batch=2,
                    predictor_auxiliary_pair_weight=0.1,
                    predictor_auxiliary_pair_batch=2,
                )
                policy["trials"] = {
                    key: values[:1] for key, values in policy["trials"].items()
                }
                write(root / "policy.json", policy)
                policy_benchmark.run(root / "policy.json")
                result = read(root / policy["output_directory"] / "completed.json")
                self.assertEqual(result["rows"], 6)
                # Re-running identical settings loads completed fits and preserves evaluations.
                policy_benchmark.run(root / "policy.json")
                self.assertEqual(
                    read(root / policy["output_directory"] / "completed.json"), result
                )
                batch = read(repository_root / "config/batch_selection.json")
                batch.update(
                    folds=[0],
                    endpoints=["microsomal_clearance"],
                    seeds=[11],
                    predictor_seeds=[11],
                    predictor_updates=2,
                    predictor_batch_size=2,
                    predictor_validate_every=1,
                    updates=2,
                    validate_every=1,
                    validation_pool_limit=1,
                    test_draws=1,
                    width=8,
                    depth=1,
                    heads=2,
                    training_states=2,
                    rollouts=1,
                    dimension=0,
                    controls=["ei_topk", "qei"],
                )
                write(root / "batch.json", batch)
                batch_benchmark.run(root / "batch.json")
                self.assertEqual(
                    read(root / batch["output_directory"] / "completed.json")[
                        "episodes"
                    ],
                    18,
                )
                self.assertTrue(
                    (
                        root / batch["output_directory"] / "figures/comparison.pdf"
                    ).exists()
                )
