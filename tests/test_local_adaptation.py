"""Scientific checks for fixed targets, local evidence, and native uncertainty."""

import copy
import tempfile
import unittest
from pathlib import Path as path_type
from types import SimpleNamespace as simple_namespace
from unittest.mock import patch

import numpy as np
import torch

from hit_to_lead.analyses.local_adaptation import (
    design,
    distribution,
    experiment_rows,
    learning_rows,
    load_verified_models,
    metrics,
    run,
    summaries,
)
from hit_to_lead.distributions import predictive_distribution
from hit_to_lead.io import digest, read, write
from hit_to_lead.models import build
from hit_to_lead.settings import configuration


def fixture():
    rng = np.random.default_rng(8)
    features = rng.normal(size=(36, 32)).astype(np.float32)
    pools = [
        dict(
            pool_id=f"pool_{index}",
            group=f"group_{index}",
            subset="test",
            indices=np.arange(index * 18, index * 18 + size),
            y=np.sin(np.arange(size) * 0.7),
        )
        for index, size in enumerate((18, 6))
    ]
    data = simple_namespace(
        fold=0, endpoint="microsomal_clearance", x=features, pools=pools, scale=0.7
    )
    config = dict(
        context_sizes=[1, 2, 3, 5, 10],
        query_count=5,
        minimum_pool_size=3,
        draws=2,
        expected_outcome_control=True,
        experiment_context_size=2,
        experiment_draws=2,
        maximum_candidates=3,
        seed=2026,
    )
    return data, config


class context_model:
    """A deterministic context-dependent model for transparent leakage tests."""

    def predict(self, context, query):
        distance = torch.cdist(query, context.x).square() / query.shape[1]
        weights = torch.softmax(-distance, -1)
        mean = weights @ context.y
        variance = 0.1 + distance.min(-1).values
        return predictive_distribution.normal(mean, variance)


class local_adaptation_tests(unittest.TestCase):
    def test_fixed_queries_nested_contexts_and_complete_cohorts(self):
        data, config = fixture()
        rows = learning_rows(data, [context_model()], "test_model", config)
        for pool in data.pools:
            for draw in range(config["draws"]):
                selected = [
                    row
                    for row in rows
                    if row["pool_id"] == pool["pool_id"]
                    and row["draw"] == draw
                    and row["control"] == "actual"
                ]
                query_sets = {tuple(row["queries"]) for row in selected}
                self.assertEqual(len(query_sets), 1)
                self.assertTrue(
                    all(
                        not set(row["observed"]) & set(row["queries"])
                        for row in selected
                    )
                )
                self.assertTrue(
                    all(
                        set(first["observed"]).issubset(second["observed"])
                        for first, second in zip(selected, selected[1:])
                    )
                )
        summary, _ = summaries(rows, [])
        complete = summary[
            (summary.endpoint == data.endpoint)
            & (summary.cohort == "complete")
            & (summary.control == "actual")
        ]
        self.assertEqual(complete.context_size.tolist(), config["context_sizes"])
        self.assertEqual(complete.pools.tolist(), [1] * 5)
        self.assertTrue(np.isfinite(complete.nll).all())

    def test_predictions_cannot_use_hidden_labels_and_offset_cancels(self):
        data, config = fixture()
        pool = data.pools[0]
        reference, queries, candidates = design(pool, 0)
        observed = [reference, candidates[0]]
        values = pool["y"].copy()
        first = distribution(
            [context_model()], data.x[pool["indices"]], values, observed, queries
        )
        values[queries] += 10000
        second = distribution(
            [context_model()], data.x[pool["indices"]], values, observed, queries
        )
        third = distribution(
            [context_model()], data.x[pool["indices"]], values + 20, observed, queries
        )
        torch.testing.assert_close(first.loc, second.loc, rtol=0, atol=0)
        torch.testing.assert_close(first.loc, third.loc, rtol=1e-5, atol=1e-6)

    def test_independent_counterfactuals_and_native_mixture_density(self):
        data, config = fixture()
        rows = experiment_rows(data, [context_model()], "test_model", config)
        selected = [
            row for row in rows if row["pool_id"] == "pool_0" and row["draw"] == 0
        ]
        self.assertEqual(len({tuple(row["observed"]) for row in selected}), 1)
        self.assertEqual(len({tuple(row["queries"]) for row in selected}), 1)
        self.assertTrue(
            all(
                row["candidate"] not in row["observed"] + row["queries"]
                for row in selected
            )
        )
        changed = copy.deepcopy(data)
        candidate = selected[0]["candidate"]
        changed.pools[0]["y"][candidate] += 100
        # Keep the retrospective design fixed when changing this one hidden outcome.
        with patch(
            "hit_to_lead.analyses.local_adaptation.design",
            side_effect=lambda pool, draw, *args: design(
                data.pools[0 if pool["pool_id"] == "pool_0" else 1], draw, *args
            ),
        ):
            modified = experiment_rows(changed, [context_model()], "test_model", config)
        other = next(row for row in selected if row["candidate"] != candidate)
        other_after = next(
            row
            for row in modified
            if row["pool_id"] == "pool_0"
            and row["draw"] == 0
            and row["candidate"] == other["candidate"]
        )
        self.assertEqual(other["after"], other_after["after"])
        prediction = predictive_distribution(
            torch.tensor([[-2.0, 1.0], [2.0, 3.0]]), torch.full((2, 2), 0.3)
        )
        target = np.array([-2.0, 3.0])
        result = metrics(prediction, target, 2.0)
        expected = float(-prediction.log_prob(torch.tensor(target)).mean())
        self.assertAlmostEqual(result["nll"], expected, places=6)
        self.assertAlmostEqual(
            result["nll_transformed"], expected + np.log(2), places=6
        )
        mean, variance = prediction.moments()
        gaussian_nll = float(
            -torch.distributions.Normal(mean, variance.sqrt())
            .log_prob(torch.tensor(target))
            .mean()
        )
        self.assertGreater(abs(gaussian_nll - expected), 0.5)

    def test_provenance_and_small_end_to_end_report(self):
        data, config = fixture()
        config.update(
            folds=[0],
            endpoints=[data.endpoint],
            seeds=[11],
            draws=1,
            experiment_draws=1,
            context_sizes=[1, 2],
            query_count=2,
            maximum_candidates=1,
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = path_type(temporary)
            fold = root / "data" / "fold_0"
            fold.mkdir(parents=True)
            write(fold / "dataset.json", {"test": "fixture"})
            np.savez(fold / "features.npz", fixture=np.zeros(1))
            checkpoint = root / "fit" / "best.pt"
            checkpoint.parent.mkdir()
            parameters = configuration("neural_mean_gp")
            model = build(parameters, data.endpoint)
            torch.save(
                dict(
                    configuration=parameters,
                    endpoint=data.endpoint,
                    seed=11,
                    model=model.state_dict(),
                ),
                checkpoint,
            )
            specification = dict(
                configuration=parameters,
                endpoint=data.endpoint,
                fold=0,
                seed=11,
                scale=data.scale,
                dataset_sha256=digest(fold / "dataset.json"),
                feature_sha256=digest(fold / "features.npz"),
            )
            write(checkpoint.parent / "specification.json", specification)
            model_config = dict(
                method="neural_mean_gp", checkpoint_template=str(checkpoint)
            )
            config.update(
                models=[model_config], output_directory=str(root / "analysis")
            )
            recipe = root / "recipe.json"
            write(recipe, config)
            with patch("hit_to_lead.settings.data_root", root / "data"), patch(
                "hit_to_lead.settings.artifact_root", root
            ), patch(
                "hit_to_lead.analyses.local_adaptation.series_dataset",
                return_value=data,
            ), patch(
                "hit_to_lead.data_import.import_prepared_data"
            ):
                models, _ = load_verified_models(data, model_config, [11])
                self.assertEqual(len(models), 1)
                result = run(recipe)
                self.assertTrue((result / "reports" / "local_adaptation.pdf").exists())
                saved = read(result / "completed.json")
                self.assertGreater(saved["experiment_cases"], 0)
                self.assertEqual(result, run(recipe))
                specification["fold"] = 1
                write(checkpoint.parent / "specification.json", specification)
                with self.assertRaisesRegex(ValueError, "fold mismatch"):
                    load_verified_models(data, model_config, [11])
