"""Check matching, information boundaries, augmentation, and resumable fitting."""

import copy
import tempfile
import unittest
from pathlib import Path as path_type
from types import SimpleNamespace as simple_namespace
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

from hit_to_lead.analyses.augmentation import (
    case_manifest,
    evaluate,
    evaluate_checkpoint,
    fit_policy,
    fixed_cases,
    lower_half_context,
    purchase_counts,
    remove_top,
    rollout,
    summarize,
    training_case,
)
from hit_to_lead.models import build
from hit_to_lead.io import digest
from hit_to_lead.policy.benchmark import load_actor
from hit_to_lead.policy.episodes import prediction_engine
from hit_to_lead.settings import configuration


def synthetic_data():
    pools = []
    for index, subset in enumerate(("train", "train", "validation", "test")):
        values = np.arange(12, dtype=float)[::-1]
        pools.append(
            dict(
                pool_id=f"pool_{index}",
                group=f"group_{index}",
                indices=np.arange(index * 12, (index + 1) * 12),
                y=values,
                objective=values.copy(),
                subset=subset,
            )
        )
    return simple_namespace(
        fold=0,
        endpoint="microsomal_clearance",
        roles_sha256="synthetic",
        x=np.random.default_rng(7).normal(size=(48, 32)).astype(np.float32) * 0.1,
        pools=pools,
        policy_training=pools[:2],
    )


class augmentation_tests(unittest.TestCase):
    def test_worst_fraction_context_and_training_only_removal(self):
        data = synthetic_data()
        pool = data.pools[0]
        original = copy.deepcopy(pool)
        for fraction in (0.1, 0.2, 0.3, 0.4, 0.5):
            observed = lower_half_context(pool, np.random.default_rng(3), fraction, 5)
            self.assertTrue(set(observed) <= set(range(max(1, int(12 * fraction)))))
            self.assertEqual(len(set(observed)), min(5, max(1, int(12 * fraction))))
        reduced = remove_top(pool, 5, np.random.default_rng(3))
        np.testing.assert_array_equal(reduced["y"], np.arange(5, 12)[::-1])
        np.testing.assert_array_equal(reduced["indices"], np.arange(7))
        np.testing.assert_array_equal(pool["y"], original["y"])
        self.assertNotEqual(pool["pool_id"], reduced["pool_id"])
        with self.assertRaisesRegex(ValueError, "leave at least three"):
            remove_top(pool, 10, np.random.default_rng(1))
        with self.assertRaisesRegex(ValueError, "training pools"):
            training_case([data.pools[-1]], np.random.default_rng(1), {})
        sizes = set()
        for _ in range(50):
            _, context = training_case(
                [pool],
                np.random.default_rng(_),
                dict(context_max=5, fraction=0.5, augmentation_probability=1.0),
            )
            sizes.add(len(context))
            self.assertTrue(set(context) <= set(range(6)))
        self.assertEqual(sizes, {2, 3, 4, 5})

    def test_common_cases_rank_ties_and_hidden_label_invariance(self):
        data = synthetic_data()
        cases = fixed_cases(data, "test", 0.5, 4)
        self.assertEqual(
            case_manifest(cases), case_manifest(fixed_cases(data, "test", 0.5, 4))
        )
        pool = dict(data.pools[0], y=np.array([3, 2, 1, 0, 0], float))
        counts = purchase_counts(pool, [0], [1, 3])
        self.assertEqual(counts["top1"], 2)
        self.assertEqual(counts["random_top1"], 5 / 3)
        self.assertEqual(purchase_counts(pool, [3], [])["top4"], 0)
        model = build(configuration("reference"), data.endpoint)
        observed = [0, 1, 2]
        pool = data.pools[0]
        changed = copy.deepcopy(pool)
        changed["y"][3:] *= 100
        original_state = prediction_engine(data, [model]).state(pool, observed)
        changed_state = prediction_engine(data, [model]).state(changed, observed)
        np.testing.assert_array_equal(original_state["scalar"], changed_state["scalar"])

    def test_tiny_policy_fit_restart_and_evaluation(self):
        torch.set_num_threads(1)
        data = synthetic_data()
        engine = prediction_engine(
            data, [build(configuration("reference"), data.endpoint)]
        )
        config = dict(
            width=8,
            updates=1,
            validate_every=1,
            validation_draws=1,
            validation_pool_limit=2,
            episodes_per_update=2,
        )
        trial = dict(learning_rate=1e-4, clip=0.2, entropy=0.01)
        arm = dict(name="multi_hit_5", fraction=0.5, context_max=5)
        with tempfile.TemporaryDirectory() as temporary:
            output = path_type(temporary)
            result = fit_policy(engine, config, arm, trial, 11, output, {})
            self.assertEqual(
                result, fit_policy(engine, config, arm, trial, 11, output, {})
            )
            (output / "completed.json").unlink()
            self.assertEqual(
                result, fit_policy(engine, config, arm, trial, 11, output, {})
            )
            cases = fixed_cases(data, "test", 0.5, 1)
            actor = load_actor(result["path"])
            records, row = rollout(
                actor, engine, data.pools[0], [0, 1], np.random.default_rng(8)
            )
            self.assertEqual(len(records), row["top1"])
            evaluated = evaluate(actor, engine, cases)
            self.assertEqual(evaluated[0]["pool_size"], 12)
            self.assertEqual(evaluated[0]["initial_context"], cases[0][1])
            checkpoint = path_type(result["path"])
            evaluation_file = output / "evaluations" / "fraction_50.json"
            cached = evaluate_checkpoint(engine, cases, checkpoint, evaluation_file, {})
            self.assertEqual(cached[0]["actor_checkpoint_sha256"], digest(checkpoint))
            self.assertEqual(result["checkpoint_sha256"], digest(checkpoint))
            with patch(
                "hit_to_lead.analyses.augmentation.evaluate",
                side_effect=AssertionError("Cache was not reused"),
            ):
                self.assertEqual(
                    cached,
                    evaluate_checkpoint(engine, cases, checkpoint, evaluation_file, {}),
                )
            rows = [
                dict(
                    item,
                    method="baseline",
                    fraction=0.5,
                    endpoint=data.endpoint,
                    fold=0,
                    seed=11,
                )
                for item in evaluated
            ]
            summarize(rows, output)
            self.assertTrue((output / "figures/augmentation_comparison.pdf").exists())
            table = pd.read_csv(output / "acquisition_summary.csv")
            self.assertEqual(set(table.endpoint), {data.endpoint, "all"})
            with self.assertRaisesRegex(RuntimeError, "provenance changed"):
                fit_policy(engine, dict(config, updates=2), arm, trial, 11, output, {})
            saved = torch.load(checkpoint, weights_only=False, map_location="cpu")
            saved["model"]["log_temperature"] += 0.1
            torch.save(saved, checkpoint)
            with self.assertRaisesRegex(
                RuntimeError, "Cached evaluation provenance changed"
            ):
                evaluate_checkpoint(engine, cases, checkpoint, evaluation_file, {})
            with self.assertRaisesRegex(
                RuntimeError, "Completed actor checkpoint changed"
            ):
                fit_policy(engine, config, arm, trial, 11, output, {})
