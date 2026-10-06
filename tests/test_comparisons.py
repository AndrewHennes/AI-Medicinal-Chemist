"""Optimizer mathematics, disjoint information flow, and delayed-feedback checks."""

import copy
import unittest
from types import SimpleNamespace as simple_namespace
import numpy as np
import torch
from hit_to_lead.distributions import measured_context
from hit_to_lead.models import build
from hit_to_lead.settings import configuration
from hit_to_lead.policy.network import acquisition_policy, collate
from hit_to_lead.policy.optimizers import (
    actor_parameters,
    conjugate_gradient,
    pack,
    ppo_update,
    trpo_update,
    dpo_loss,
)
from hit_to_lead.policy.grpo import group_rollout, grpo_objective, grpo_update
from hit_to_lead.policy.episodes import prediction_engine, assign_roles
from hit_to_lead.batch.episodes import joint_posterior, batch_engine, simulate
from hit_to_lead.batch.models import make_model, select_neural, relaxed_slots
from hit_to_lead.batch.search import random_expectation, batch_times
from hit_to_lead.batch.training import (
    supervised_loss,
    gumbel_loss,
    policy_rollouts,
    ppo_step,
)


def fixture():
    rng = np.random.default_rng(22)
    pools = []
    x = rng.normal(size=(48, 32)).astype(np.float32) * 0.2
    for index in range(8):
        pools.append(
            dict(
                pool_id=f"p{index}",
                group=f"g{index}",
                indices=np.arange(index * 6, (index + 1) * 6),
                y=np.array([2.0, 1.0, 0.5, -0.5, -1.0, 0.0]),
                objective=[2.0, 1.0, 0.5, -0.5, -1.0, 0.0],
                subset="train" if index < 6 else "validation" if index == 6 else "test",
            )
        )
    return simple_namespace(
        fold=0,
        endpoint="microsomal_clearance",
        x=x,
        pools=pools,
        training=pools[:6],
        policy_training=pools[:6],
    )


class comparison_tests(unittest.TestCase):
    def test_compound_proportional_pair_sampling(self):
        from hit_to_lead.models.pair_supervision import sample_pairs, pair_loss

        data = fixture()
        data.training = data.training[:2]
        data.training[0]["y"] = data.training[0]["y"][:2]
        data.training[0]["indices"] = data.training[0]["indices"][:2]
        pairs = sample_pairs(data, np.random.default_rng(7), 4000)
        fraction = sum(pool["pool_id"] == "p0" for pool, _, _ in pairs) / len(pairs)
        self.assertAlmostEqual(fraction, 0.25, delta=0.03)
        self.assertTrue(all(first != second for _, first, second in pairs))
        model = build(configuration("neural_mean_gp"), "microsomal_clearance")
        loss = pair_loss(model, data, np.random.default_rng(4), 4)
        loss.backward()
        self.assertTrue(torch.isfinite(loss))

    def test_group_relative_weights_and_zero_reward_spread(self):
        state = dict(
            scalar=np.array([[0.2, 0.5], [-0.3, 0.2]], np.float32),
            context_size=1,
            pool_id="p",
            reference=0,
        )

        def record(length, action):
            return [(state, action, float(-np.log(2)), 0.0) for _ in range(length)]

        rollout = group_rollout(
            [[record(1, 0), record(3, 1)], [record(2, 0), record(2, 1)]]
        )
        torch.testing.assert_close(rollout["weight"].sum(), torch.tensor(1.0))
        self.assertEqual(rollout["informative_groups"], 1)
        torch.testing.assert_close(
            rollout["advantage"][:4], torch.tensor([1.0, -1.0, -1.0, -1.0])
        )
        logits = torch.zeros(8, 2, requires_grad=True)
        loss, _ = grpo_objective(logits, logits.detach(), rollout, 0.2, 0.0)
        loss.backward()
        self.assertLess(float(logits.grad[0, 0]), 0.0)
        self.assertGreater(float(logits.grad[1, 1]), 0.0)
        tied = group_rollout([[record(2, 0), record(2, 1)]])
        self.assertTrue(torch.equal(tied["advantage"], torch.zeros(4)))
        wrong = copy.deepcopy(state)
        wrong["reference"] = 1
        with self.assertRaisesRegex(ValueError, "share the starting context"):
            group_rollout([[record(1, 0), [(wrong, 0, 0.0, 0.0)]]])

    def test_optimizers_and_trust_region(self):
        torch.manual_seed(11)
        states = [
            dict(
                scalar=np.array([[0.2, 0.5], [-0.3, 0.2], [0.8, 0.4]], np.float32),
                context_size=1,
                pool_id="p",
                reference=0,
            )
            for _ in range(4)
        ]
        model = acquisition_policy(dict(width=8, feature_count=2, decoder_depth=1))
        with torch.no_grad():
            scores, values = model(collate(states))
            logp = torch.log_softmax(scores, -1)
        records = [
            [
                (
                    states[index],
                    index % 3,
                    float(logp[index, index % 3]),
                    float(values[index]),
                )
                for index in range(length)
            ]
            for length in [2, 4]
        ]
        trpo_config = dict(
            max_kl=0.01,
            damping=0.1,
            cg_steps=10,
            line_search_steps=10,
            backtrack=0.5,
            acceptance_ratio=0.1,
        )
        result = trpo_update(
            model,
            torch.optim.Adam(model.critic.parameters(), lr=0.001),
            pack(records),
            trpo_config,
            np.random.default_rng(1),
        )
        self.assertLessEqual(result["kl"], 0.010001)
        if result["accepted"]:
            self.assertGreater(result["surrogate_gain"], 0.0)
        ppo_update(
            model,
            torch.optim.Adam(model.parameters(), lr=0.001),
            pack(records),
            dict(clip=0.2, entropy=0.01),
            np.random.default_rng(2),
        )
        reference = copy.deepcopy(model).requires_grad_(False)
        before = [p.detach().clone() for p in model.critic.parameters()]
        grpo_update(
            model,
            reference,
            torch.optim.Adam(actor_parameters(model), lr=0.001),
            [records],
            dict(clip=0.2, beta=0.01, epochs=1),
        )
        for prior, current in zip(before, model.critic.parameters()):
            torch.testing.assert_close(prior, current, atol=0, rtol=0)
        matrix = torch.tensor([[3.0, 0.5], [0.5, 2.0]])
        vector = torch.tensor([1.0, 2.0])
        torch.testing.assert_close(
            conjugate_gradient(lambda value: matrix @ value, vector),
            torch.linalg.solve(matrix, vector),
        )
        self.assertLess(
            dpo_loss(
                torch.tensor([1.0]),
                torch.tensor([0.0]),
                torch.tensor([0.0]),
                torch.tensor([0.0]),
                1.0,
            ),
            dpo_loss(
                torch.tensor([0.0]),
                torch.tensor([1.0]),
                torch.tensor([0.0]),
                torch.tensor([0.0]),
                1.0,
            ),
        )

    def test_measured_only_features_and_disjoint_roles(self):
        data = fixture()
        roles = assign_roles(data)
        self.assertEqual(set(roles), {pool["group"] for pool in data.training})
        self.assertEqual(set(roles.values()), {"predictor", "policy"})
        model = build(configuration("reference"), "microsomal_clearance")
        pool = data.pools[0]
        changed = copy.deepcopy(pool)
        changed["y"][2:] = np.arange(4) * 100
        first = prediction_engine(data, [model], "mean_sd_phi").state(pool, [0, 1])
        second = prediction_engine(data, [model], "mean_sd_phi").state(changed, [0, 1])
        np.testing.assert_array_equal(first["scalar"], second["scalar"])
        np.testing.assert_array_equal(first["latent"], second["latent"])

    def test_joint_gp_and_hard_subsets(self):
        data = fixture()
        pool = data.pools[0]
        model = build(configuration("neural_mean_gp"), "microsomal_clearance")
        x = torch.tensor(data.x[pool["indices"]])
        context = measured_context(x[:2], torch.tensor([0.0, -1.0]))
        mean, covariance = joint_posterior(model, context, x[2:])
        expected_mean, expected_variance = model.predict(context, x[2:]).moments()
        torch.testing.assert_close(mean, expected_mean)
        torch.testing.assert_close(covariance.diagonal(), expected_variance)
        self.assertGreater(float(torch.linalg.eigvalsh(covariance).min().detach()), 0.0)
        engine = batch_engine(data, [model], dimension=0)
        state = engine.state(pool, [0], 2)
        for family in ("deep_sets", "pair_transformer", "gumbel", "batch_ppo"):
            network = make_model(
                dict(
                    family=family,
                    dimension=0,
                    width=8,
                    heads=2,
                    depth=1,
                    temperature=0.5,
                )
            )
            for size in (1, 2, 5, 20):
                selected, _ = select_neural(network, state, size)
                self.assertEqual(len(set(selected)), min(size, 5))
        rows = simulate(engine, pool, 0, 2, "ei_topk")
        self.assertEqual(rows["compounds"][0], sum(map(len, rows["batches"])))
        self.assertTrue(all(len(batch) == 2 for batch in rows["batches"][:-1]))
        rounds, compounds = batch_times(pool, 0, [[1, 4]])
        self.assertEqual((rounds[0], compounds[0]), (1, 2))
        self.assertEqual(
            random_expectation(pool, 0, 1)[0], random_expectation(pool, 0, 1)[1]
        )

    def test_batch_learning_and_deferred_reveal(self):
        data = fixture()
        engine = batch_engine(
            data,
            [build(configuration("neural_mean_gp"), "microsomal_clearance")],
            dimension=0,
        )
        rng = np.random.default_rng(123)
        for family in ("deep_sets", "pair_transformer", "gumbel"):
            model = make_model(
                dict(
                    family=family,
                    dimension=0,
                    width=8,
                    heads=2,
                    depth=1,
                    temperature=0.5,
                )
            )
            objective = gumbel_loss if family == "gumbel" else supervised_loss
            loss = objective(model, engine, rng, [1, 2, 5], count=2)
            loss.backward()
            self.assertTrue(torch.isfinite(loss))
            self.assertTrue(
                any(
                    parameter.grad is not None and parameter.grad.abs().sum() > 0
                    for parameter in model.parameters()
                )
            )
        model = make_model(
            dict(
                family="batch_ppo",
                dimension=0,
                width=8,
                heads=2,
                depth=1,
                temperature=0.5,
            )
        )
        records = policy_rollouts(model, engine, rng, [2], count=2)
        for row in records:
            if row["pending"]:
                self.assertNotIn(row["action"], row["pending"])
        self.assertTrue(
            np.isfinite(
                ppo_step(
                    model, torch.optim.Adam(model.parameters(), lr=0.001), records, rng
                )
            )
        )
        slots = relaxed_slots(torch.randn(2, 5, requires_grad=True), 2, 0.5)
        torch.testing.assert_close(slots.sum(-1), torch.ones(2, 2))

    def test_reference_ablations_are_differentiable(self):
        from hit_to_lead.distributions import prediction_episode

        torch.manual_seed(1)
        context = measured_context(torch.randn(3, 32), torch.tensor([0.0, 0.2, -0.4]))
        query = torch.randn(4, 32)
        for method in (
            "reference_unchanged",
            "reference_mean_only",
            "reference_kernel_only",
            "reference_weighted",
        ):
            model = build(configuration(method), "protein_binding")
            loss = model.loss(prediction_episode(context, query, torch.randn(4), {}))
            loss.backward()
            self.assertTrue(torch.isfinite(loss))
            self.assertTrue(
                all(
                    torch.isfinite(parameter.grad).all()
                    for parameter in model.parameters()
                    if parameter.grad is not None
                )
            )
