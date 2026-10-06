"""Kernel validity and uncertainty checks, independent of chemical benchmark results."""

import unittest
import numpy as np
import torch
from hit_to_lead.analyses.kernel_comparison import (
    comparison_gp,
    tanimoto,
    kernel_dataset,
)
from hit_to_lead.distributions import measured_context, prediction_episode


class kernel_comparison_tests(unittest.TestCase):
    def configuration(self, kernel):
        return dict(
            input_dim=32,
            pca_components=4,
            width=8,
            depth=2,
            kernel=kernel,
            mean_type="neural",
            rq_shape=1.0,
        )

    def test_positive_semidefinite_and_posterior(self):
        torch.manual_seed(35)
        features = torch.cat(
            [torch.randn(7, 32), (torch.rand(7, 12) > 0.5).float()], dim=1
        )
        for kind in ("rbf", "matern", "linear", "rational_quadratic", "tanimoto"):
            model = comparison_gp(self.configuration(kind))
            context = measured_context(features[:3], torch.tensor([0.0, -0.3, 0.8]))
            xc, xq, mc, mq = model.embeddings(context, features[3:])
            covariance = model.kernel(
                torch.cat([xc, xq]), torch.cat([xc, xq]), model.phi
            )
            self.assertGreaterEqual(
                float(torch.linalg.eigvalsh(covariance).min().detach()), -1e-9
            )
            distribution = model.predict(context, features[3:])
            self.assertTrue(torch.isfinite(distribution.scale).all())
            self.assertTrue((distribution.scale > 0).all())
            episode = prediction_episode(
                context, features[3:], torch.arange(4).float(), {}
            )
            model.loss(episode).backward()
            self.assertTrue(
                all(
                    torch.isfinite(p.grad).all()
                    for p in model.parameters()
                    if p.grad is not None
                )
            )
            shifted = model.predict(
                measured_context(context.x, context.y + 3), features[3:]
            )
            torch.testing.assert_close(
                shifted.loc, distribution.loc + 3, atol=2e-7, rtol=1e-7
            )
            torch.testing.assert_close(shifted.scale, distribution.scale)

    def test_tanimoto_and_linear_variance(self):
        bits = torch.tensor([[1.0, 0, 1], [1.0, 1, 0], [0.0, 0, 0]])
        result = tanimoto(bits, bits)
        self.assertAlmostEqual(float(result[0, 1]), 1 / 3, places=6)
        self.assertEqual(float(result[2, 2]), 1)
        with self.assertRaises(ValueError):
            tanimoto(bits - 1, bits)
        model = comparison_gp(self.configuration("linear"))
        context = measured_context(torch.randn(2, 32), torch.tensor([0.0, 0.2]))
        query = torch.randn(3, 32)
        xc, xq, mc, mq = model.embeddings(context, query)
        _, amplitude, _ = model.hyperparameters(model.phi)
        torch.testing.assert_close(
            model.kernel(xq, xq, model.phi).diagonal(), amplitude * xq.square().mean(-1)
        )

    def test_sampling_does_not_depend_on_fingerprint_representation(self):
        data = object.__new__(kernel_dataset)
        data.fold, data.endpoint = 0, "synthetic"
        data.x = np.random.default_rng(5).normal(size=(20, 32)).astype(np.float32)
        pool = dict(pool_id="p", group="g", indices=np.arange(20), y=np.arange(20))
        data.training, data.large, data.by_id = [pool], [pool], {"p": pool}
        first = data.sample(np.random.default_rng(10), 5)
        data.x = np.concatenate([data.x, np.ones((20, 8), dtype=np.float32)], axis=1)
        second = data.sample(np.random.default_rng(10), 5)
        self.assertEqual([e.meta for e in first], [e.meta for e in second])
        self.assertEqual(second[0].query.shape[-1], 40)

    def test_small_complete_kernel_workflow(self):
        from pathlib import Path as path_type
        import tempfile
        from unittest.mock import patch
        from hit_to_lead import data as data_module
        from hit_to_lead.analyses import kernel_comparison as benchmark
        from hit_to_lead.io import digest, read, write
        from hit_to_lead.settings import repository_root

        with tempfile.TemporaryDirectory() as temporary:
            root = path_type(temporary)
            folder = root / "data/fold_0"
            folder.mkdir(parents=True)
            pools = []
            for index, subset in enumerate(("train", "validation", "test")):
                pools.append(
                    dict(
                        pool_id=f"p{index}",
                        group=f"g{index}",
                        endpoint="microsomal_clearance",
                        subset=subset,
                        feature_indices=list(range(index * 6, (index + 1) * 6)),
                        objective=[1.1, 0.6, 0.3, 0.2, -0.4, -0.5],
                        molecules=[
                            "C" * (j + 1) for j in range(index * 6, (index + 1) * 6)
                        ],
                    )
                )
            write(folder / "dataset.json", dict(pools=pools))
            np.savez(
                folder / "features.npz",
                pca_32=np.random.default_rng(2)
                .normal(size=(18, 32))
                .astype(np.float32),
                training_indices=np.arange(6),
            )
            config = read(repository_root / "config/kernel_comparison.json")
            config.update(
                folds=[0],
                endpoints=["microsomal_clearance"],
                seeds=[11],
                kernels=["matern", "linear"],
                mean_types=["zero", "neural"],
                pca_components=[4],
                learning_rates=[0.001],
                search_updates=2,
                final_updates=2,
                batch_size=2,
                validate_every=1,
                prediction_draws=1,
                acquisition_draws=1,
                mean_width=8,
            )
            write(root / "recipe.json", config)
            with patch.object(data_module, "data_root", root / "data"), patch.object(
                benchmark, "data_root", root / "data"
            ), patch.object(benchmark, "artifact_root", root), patch.object(
                benchmark,
                "implementation_hashes",
                return_value={"synthetic_test": "stable"},
            ):
                benchmark.run(root / "recipe.json")
                output = root / config["output_directory"]
                self.assertTrue((output / "reports/kernel_comparison.pdf").exists())
                checkpoint = (
                    output
                    / "fold_0/microsomal_clearance/neural_matern/final/seed_11/best.pt"
                )
                first = checkpoint.read_bytes()
                benchmark.run(root / "recipe.json")
                self.assertEqual(checkpoint.read_bytes(), first)
                config["mean_width"] = 12
                write(root / "recipe.json", config)
                with self.assertRaisesRegex(RuntimeError, "different configuration"):
                    benchmark.run(root / "recipe.json")
                try:
                    import rdkit
                except ImportError:
                    return
                self.assertIsNotNone(rdkit)
                data = benchmark.kernel_dataset(0, "microsomal_clearance")
                bits = benchmark.fingerprints(data, config, output / "fingerprints")
                self.assertEqual(bits.shape, (18, 2048))
                self.assertTrue(np.isin(bits, (0, 1)).all())
                np.testing.assert_equal(
                    bits, benchmark.fingerprints(data, config, output / "fingerprints")
                )

                fingerprint_config = dict(config, kernels=["tanimoto"])
                descriptor_data = benchmark.load_data(
                    0, "microsomal_clearance", fingerprint_config, output
                )
                cases = descriptor_data.cases("validation", 1)
                parameters = next(
                    benchmark.candidates(fingerprint_config, "tanimoto", "neural")
                )
                fit_directory = output / "descriptor_fit"
                benchmark.fit(
                    descriptor_data,
                    parameters,
                    11,
                    fit_directory,
                    2,
                    fingerprint_config,
                    cases,
                )
                recorded = read(fit_directory / "specification.json")["fingerprints"]
                self.assertEqual(
                    recorded["sha256"], digest(output / "fingerprints/fold_0.npz")
                )
                self.assertEqual(
                    recorded["configuration"]["rdkit_version"],
                    rdkit.rdBase.rdkitVersion,
                )
                # A regenerated cache can be internally valid yet incompatible
                # with an earlier fit. Bind the actual descriptor artifact too.
                regenerated = bits.copy()
                regenerated[0, 0] = 1 - regenerated[0, 0]
                fingerprint_file = output / "fingerprints/fold_0.npz"
                np.savez_compressed(fingerprint_file, fingerprints=regenerated)
                cache_record = read(output / "fingerprints/fold_0.json")
                cache_record["sha256"] = digest(fingerprint_file)
                write(output / "fingerprints/fold_0.json", cache_record)
                changed_data = benchmark.load_data(
                    0, "microsomal_clearance", fingerprint_config, output
                )
                self.assertNotEqual(
                    changed_data.fingerprint_provenance["sha256"], recorded["sha256"]
                )
                with self.assertRaisesRegex(RuntimeError, "different provenance"):
                    benchmark.fit(
                        changed_data,
                        parameters,
                        11,
                        fit_directory,
                        2,
                        fingerprint_config,
                        cases,
                    )
                # Version changes are checked independently of the bit values.
                descriptor_data.fingerprint_provenance["configuration"][
                    "rdkit_version"
                ] += "_changed"
                with self.assertRaisesRegex(RuntimeError, "different provenance"):
                    benchmark.fit(
                        descriptor_data,
                        parameters,
                        11,
                        fit_directory,
                        2,
                        fingerprint_config,
                        cases,
                    )
