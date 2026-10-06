"""Algebra, differentiation, information boundaries, and acquisition invariants.

No external datasets or checkpoints are required. Tests use CPU and a small
synthetic context. They do not launch a scientific performance benchmark.
"""

import itertools
import unittest
import numpy as np
import torch
from hit_to_lead.distributions import (
    measured_context,
    prediction_episode,
    predictive_distribution,
    mixture,
)
from hit_to_lead.models.posterior import flat_offset_posterior
from hit_to_lead.settings import configured_methods, configured_endpoints, configuration
from hit_to_lead.models import build
from hit_to_lead.evaluation import acquisition_counts

torch.set_num_threads(1)


def example(n=4):
    torch.manual_seed(112)
    x = torch.randn(n, 32) * 0.5
    y = torch.randn(n)
    q = torch.randn(5, 32) * 0.5
    return prediction_episode(measured_context(x, y), q, torch.randn(5), {})


class model_tests(unittest.TestCase):
    def test_all_families_train_and_condition(self):
        for method in configured_methods:
            with self.subTest(method=method):
                torch.manual_seed(11)
                model = build(configuration(method), configured_endpoints[0])
                episode = example()
                if method != "finetune":
                    loss = model.loss(episode)
                    self.assertTrue(torch.isfinite(loss))
                    loss.backward()
                    gradients = [
                        p.grad for p in model.parameters() if p.grad is not None
                    ]
                    self.assertTrue(gradients)
                    self.assertTrue(all((torch.isfinite(g).all() for g in gradients)))
                    self.assertGreater(
                        sum((float(g.abs().sum()) for g in gradients)), 0.0
                    )
                state = {k: v.clone() for k, v in model.state_dict().items()}
                model.eval()
                with torch.no_grad():
                    p = model.predict(episode.context, episode.query)
                    self.assertTrue(torch.isfinite(p.log_prob(episode.target)).all())
                    self.assertTrue((p.moments()[1] > 0).all())
                    singleton = measured_context(
                        episode.context.x[:1], episode.context.y[:1]
                    )
                    self.assertTrue(
                        torch.isfinite(
                            model.predict(singleton, episode.query).scale
                        ).all()
                    )
                for k, v in state.items():
                    torch.testing.assert_close(v, model.state_dict()[k], rtol=0, atol=0)

    def test_offsets_support_order_and_query_isolation(self):
        episode = example()
        for method in [m for m in configured_methods if m != "alpaca_no_offset"]:
            with self.subTest(method=method):
                torch.manual_seed(11)
                model = build(configuration(method), configured_endpoints[0]).eval()
                order = torch.tensor([0, 3, 1, 2])
                reordered = measured_context(
                    episode.context.x[order], episode.context.y[order]
                )
                shifted = measured_context(episode.context.x, episode.context.y + 3.0)
                with torch.no_grad():
                    p = model.predict(episode.context, episode.query)
                    reordered_p = model.predict(reordered, episode.query)
                    shifted_p = model.predict(shifted, episode.query)
                    first = model.predict(episode.context, episode.query[:2])
                    rest = model.predict(episode.context, episode.query[2:])
                for left, right in zip(p.moments(), reordered_p.moments()):
                    torch.testing.assert_close(left, right, atol=2e-05, rtol=2e-05)
                torch.testing.assert_close(
                    p.loc + 3, shifted_p.loc, atol=2e-05, rtol=2e-05
                )
                torch.testing.assert_close(
                    p.scale, shifted_p.scale, atol=2e-05, rtol=2e-05
                )
                torch.testing.assert_close(
                    p.loc, torch.cat([first.loc, rest.loc], 1), atol=2e-05, rtol=2e-05
                )
                torch.testing.assert_close(
                    p.scale,
                    torch.cat([first.scale, rest.scale], 1),
                    atol=2e-05,
                    rtol=2e-05,
                )

    def test_posterior_against_large_intercept_prior(self):
        torch.manual_seed(111)
        xc = torch.randn(4, 6, dtype=torch.float64)
        xq = torch.randn(3, 6, dtype=torch.float64)
        kcc = xc @ xc.T
        kqc = xq @ xc.T
        diag = xq.square().sum(1)
        mc = torch.randn(4, dtype=torch.float64)
        mq = torch.randn(3, dtype=torch.float64)
        y = torch.randn(4, dtype=torch.float64)
        noise = 0.2
        prediction = flat_offset_posterior(mc, mq, kcc, kqc, diag, noise, y)
        broad = 1000000.0
        matrix = kcc + noise * torch.eye(4) + broad
        cross = kqc + broad
        exact = mq + cross @ torch.linalg.solve(matrix, y - mc)
        variance = (
            diag
            + broad
            + noise
            - (cross * torch.linalg.solve(matrix, cross.T).T).sum(1)
        )
        torch.testing.assert_close(
            prediction.moments()[0], exact, atol=1e-05, rtol=1e-05
        )
        torch.testing.assert_close(
            prediction.moments()[1], variance, atol=1e-05, rtol=1e-05
        )
        single = flat_offset_posterior(
            mc[:1], mq, kcc[:1, :1], kqc[:, :1], diag, noise, y[:1]
        )
        torch.testing.assert_close(single.moments()[0], mq + y[0] - mc[0])
        torch.testing.assert_close(
            single.moments()[1], diag + kcc[0, 0] - 2 * kqc[:, 0] + 2 * noise
        )

    def test_full_alpaca_prior(self):
        model = build(configuration("alpaca"), configured_endpoints[0]).double()
        episode = example()
        c = measured_context(episode.context.x.double(), episode.context.y.double())
        q = episode.query.double()
        hc = model.basis(c.x)
        hq = model.basis(q)
        factor = model.prior_chol()
        prior = factor @ factor.T
        hc = torch.cat([hc, torch.ones(len(hc), 1, dtype=torch.float64)], 1)
        hq = torch.cat([hq, torch.ones(len(hq), 1, dtype=torch.float64)], 1)
        cov = torch.zeros(len(prior) + 1, len(prior) + 1, dtype=torch.float64)
        cov[:-1, :-1] = prior
        cov[-1, -1] = 1000000.0
        m = torch.cat([model.prior_mean, torch.zeros(1, dtype=torch.float64)])
        noise = torch.nn.functional.softplus(model.raw_noise) + 0.0001
        precision = torch.linalg.inv(cov) + hc.T @ hc / noise
        postcov = torch.linalg.inv(precision)
        postmean = postcov @ (torch.linalg.solve(cov, m) + hc.T @ c.y / noise)
        pred = model.predict(c, q)
        torch.testing.assert_close(
            pred.moments()[0], hq @ postmean, atol=1e-05, rtol=1e-05
        )
        torch.testing.assert_close(
            pred.moments()[1],
            (hq @ postcov * hq).sum(1) + noise,
            atol=1e-05,
            rtol=1e-05,
        )

    def test_maml_second_order_gradient(self):
        c = configuration("maml")
        c["inner_lr"] = 0.1
        model = build(c, configured_endpoints[0]).double()
        e = example()
        e = prediction_episode(
            measured_context(e.context.x.double(), e.context.y.double()),
            e.query.double(),
            e.target.double(),
            {},
        )
        parameter = model.net.head.weight
        loss = model.loss(e)
        grad = torch.autograd.grad(loss, parameter)[0]
        i, j = (1, 3)
        original = float(parameter[i, j].detach())
        epsilon = 1e-05
        with torch.no_grad():
            parameter[i, j] = original + epsilon
        plus = float(model.loss(e).detach())
        with torch.no_grad():
            parameter[i, j] = original - epsilon
        minus = float(model.loss(e).detach())
        with torch.no_grad():
            parameter[i, j] = original
        self.assertAlmostEqual(
            float(grad[i, j]), (plus - minus) / (2 * epsilon), places=6
        )

    def test_adkf_implicit_hypergradient(self):
        torch.manual_seed(47)
        c = configuration("adkf_ift")
        c.update(gp_inner_tolerance=1e-10, gp_inner_maxiter=300, ift_damping=1e-09)
        model = build(c, configured_endpoints[0]).double()
        e = example(6)
        e = prediction_episode(
            measured_context(e.context.x.double(), e.context.y.double()),
            e.query.double(),
            e.target.double(),
            {},
        )
        parameter = model.adapter[-1].weight
        loss = model.loss(e)
        grad = torch.autograd.grad(loss, parameter)[0]
        i, j = (0, 2)
        original = float(parameter[i, j].detach())
        epsilon = 0.01
        with torch.no_grad():
            parameter[i, j] = original + epsilon
        plus = float(
            -model.predict(e.context, e.query).log_prob(e.target).mean().detach()
        )
        with torch.no_grad():
            parameter[i, j] = original - epsilon
        minus = float(
            -model.predict(e.context, e.query).log_prob(e.target).mean().detach()
        )
        with torch.no_grad():
            parameter[i, j] = original
        finite = (plus - minus) / (2 * epsilon)
        self.assertLess(abs(float(grad[i, j]) - finite), 1e-05 + 0.001 * abs(finite))

    def test_anil_only_adapts_head(self):
        e = example()
        model = build(configuration("anil"), configured_endpoints[0])
        params = model.adapted(e.context)
        changed = []
        for name, original in model.net.named_parameters():
            if name.startswith("body."):
                torch.testing.assert_close(original, params[name], rtol=0, atol=0)
            else:
                changed.append(float((original - params[name]).detach().abs().sum()))
        self.assertGreater(sum(changed), 0.0)

    def test_ensemble_and_native_density(self):
        a = predictive_distribution.normal(torch.tensor([1.0]), torch.tensor([4.0]))
        b = predictive_distribution.normal(torch.tensor([3.0]), torch.tensor([9.0]))
        p = mixture([a, b])
        mean, var = p.moments()
        torch.testing.assert_close(mean, torch.tensor([2.0]))
        torch.testing.assert_close(var, torch.tensor([7.5]))
        expected = torch.log(
            (
                torch.exp(a.log_prob(torch.tensor([2.0])))
                + torch.exp(b.log_prob(torch.tensor([2.0])))
            )
            / 2
        )
        torch.testing.assert_close(p.log_prob(torch.tensor([2.0])), expected)
        lo, hi = a.interval()
        self.assertAlmostEqual(float(lo[0]), 1 - 1.64485362695 * 2, places=6)
        self.assertAlmostEqual(float(hi[0]), 1 + 1.64485362695 * 2, places=6)

    def test_random_expectation_ties_and_initial_success(self):
        for y in ([0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 1.0, 2.0, 3.0]):
            ref = 4
            observed = []
            expectation = None
            for order in itertools.permutations(range(4)):
                counts, expectation = acquisition_counts(y, ref, order)
                observed.append(counts)
            np.testing.assert_allclose(np.mean(observed, axis=0), expectation)
        counts, expectation = acquisition_counts([0.0, 1.0, 2.0], 0, [])
        self.assertEqual(counts, [0.0] * 4)
        self.assertEqual(expectation, [0.0] * 4)

    def test_summary_macro_weights_and_paired_intervals(self):
        from hit_to_lead.evaluation import summaries, paired_acquisition_intervals

        cases = []
        points = []
        acquisitions = []
        for method in ("reference", "cnp"):
            for i in range(3):
                row = dict(
                    method=method,
                    endpoint="test",
                    fold=0,
                    pool_id=str(i),
                    group=str(i),
                    draw=0,
                    pool_size=15,
                    context_size=1,
                    spearman=0.5,
                    nll=1.0,
                    coverage90=0.9,
                    width90=2.0,
                    mse=0.25,
                )
                cases.append(row)
                for y in (0.0, 1.0):
                    points.append(dict(**row, target=y, squared_error=0.25))
                acquisitions.append(
                    dict(
                        **row,
                        top1=3.0 + (method == "cnp"),
                        top2=2.0,
                        top3=1.0,
                        top4=0.0
                    )
                )
        ps, acq = summaries(cases, points, acquisitions)
        self.assertAlmostEqual(ps[0]["r2"], 0.0)
        ci = paired_acquisition_intervals(acquisitions, replicates=10)
        for r in ci:
            if r["top"] == 1:
                self.assertAlmostEqual(r["difference"], 1.0)
                self.assertAlmostEqual(r["lower"], 1.0)
                self.assertAlmostEqual(r["upper"], 1.0)
