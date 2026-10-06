"""PPO, TRPO, and trajectory-preference DPO from the completed optimizer study.

These update rules retain the original empirical trust-region checks and the
detached critic. GRPO is implemented separately in grpo.py.
"""

import torch
from torch.nn import functional
from torch.nn.utils import parameters_to_vector, vector_to_parameters
from .network import collate


def actor_parameters(model):
    return [p for name, p in model.named_parameters() if not name.startswith("critic.")]


def flat_gradient(value, parameters, create_graph=False):
    gradients = torch.autograd.grad(
        value, parameters, create_graph=create_graph, allow_unused=True
    )
    return torch.cat(
        [
            (g if g is not None else torch.zeros_like(p)).reshape(-1)
            for g, p in zip(gradients, parameters)
        ]
    )


def conjugate_gradient(matrix_vector, b, iterations=10, tolerance=1e-10):
    x = torch.zeros_like(b)
    residual = b.clone()
    direction = residual.clone()
    squared = residual.dot(residual)
    for _ in range(iterations):
        product = matrix_vector(direction)
        denominator = direction.dot(product)
        if not torch.isfinite(denominator) or denominator <= 1e-12:
            break
        alpha = squared / denominator
        x += alpha * direction
        residual -= alpha * product
        new_squared = residual.dot(residual)
        if new_squared <= tolerance:
            break
        direction = residual + new_squared / squared * direction
        squared = new_squared
    return x


def pack(records):
    states, actions, logps, values, returns = ([], [], [], [], [])
    for trajectory in records:
        for j, (state, action, logp, value) in enumerate(trajectory):
            states.append(state)
            actions.append(action)
            logps.append(logp)
            values.append(value)
            returns.append(-(len(trajectory) - j))
    if not states:
        return None
    target = torch.tensor(returns, dtype=torch.float32)
    old_values = torch.tensor(values)
    advantage = target - old_values
    advantage = (advantage - advantage.mean()) / advantage.std(
        unbiased=False
    ).clamp_min(1.0)
    return dict(
        states=states,
        actions=torch.tensor(actions),
        old_logp=torch.tensor(logps),
        target=target,
        advantage=advantage,
        scale=target.std(unbiased=False).clamp_min(1.0),
    )


def ppo_update(model, optimizer, rollout, configuration, rng):
    model.eval()
    updates = 0
    for _ in range(2):
        order = rng.permutation(len(rollout["states"]))
        for start in range(0, len(order), 64):
            indices = order[start : start + 64]
            b = collate([rollout["states"][i] for i in indices])
            score, value = model(b)
            dist = torch.distributions.Categorical(logits=score)
            ratio = (
                dist.log_prob(rollout["actions"][indices])
                - rollout["old_logp"][indices]
            ).exp()
            advantage = rollout["advantage"][indices]
            clip = configuration["clip"]
            actor = -torch.minimum(
                ratio * advantage, ratio.clamp(1 - clip, 1 + clip) * advantage
            ).mean()
            critic = (
                ((value - rollout["target"][indices]) / rollout["scale"])
                .square()
                .mean()
            )
            loss = (
                actor + 0.25 * critic - configuration["entropy"] * dist.entropy().mean()
            )
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            updates += 1
    return dict(loss=float(loss.detach()), updates=updates)


def trpo_actor_update(model, b, actions, advantage, configuration):
    model.eval()
    parameters = actor_parameters(model)
    before = parameters_to_vector(parameters).detach().clone()
    with torch.no_grad():
        old_logp = functional.log_softmax(model(b)[0], 1).detach()
        old_probability = old_logp.exp()
        old_action = old_logp.gather(1, actions[:, None]).squeeze(1)

    def objective():
        logp = functional.log_softmax(model(b)[0], 1)
        ratio = (logp.gather(1, actions[:, None]).squeeze(1) - old_action).exp()
        surrogate = (ratio * advantage).mean()
        kl = (old_probability * (old_logp - logp)).sum(1).mean()
        return (surrogate, kl)

    initial, _ = objective()
    gradient = flat_gradient(initial, parameters).detach()
    if not torch.isfinite(gradient).all() or gradient.norm() < 1e-09:
        return dict(
            accepted=False,
            kl=0.0,
            surrogate_gain=0.0,
            backtracks=0,
            gradient_norm=float(gradient.norm()),
        )

    def hessian_vector(vector):
        _, kl = objective()
        first = flat_gradient(kl, parameters, create_graph=True)
        second = flat_gradient(first.dot(vector), parameters).detach()
        return second + configuration["damping"] * vector

    direction = conjugate_gradient(hessian_vector, gradient, configuration["cg_steps"])
    curvature = direction.dot(hessian_vector(direction))
    if not torch.isfinite(curvature) or curvature <= 0:
        return dict(
            accepted=False,
            kl=0.0,
            surrogate_gain=0.0,
            backtracks=0,
            gradient_norm=float(gradient.norm()),
        )
    full_step = direction * torch.sqrt(
        2 * configuration["max_kl"] / (curvature + 1e-12)
    )
    expected = gradient.dot(full_step).item()
    accepted = False
    old_objective = float(initial.detach())
    for backtracks in range(configuration["line_search_steps"]):
        fraction = configuration["backtrack"] ** backtracks
        with torch.no_grad():
            vector_to_parameters(before + fraction * full_step, parameters)
            new_objective, kl = objective()
            gain = float(new_objective) - old_objective
            accepted = bool(
                torch.isfinite(new_objective)
                and torch.isfinite(kl)
                and (float(kl) <= configuration["max_kl"])
                and (gain > 0)
                and (gain >= configuration["acceptance_ratio"] * fraction * expected)
            )
        if accepted:
            break
    if not accepted:
        with torch.no_grad():
            vector_to_parameters(before, parameters)
        kl, gain = (0.0, 0.0)
    return dict(
        accepted=accepted,
        kl=float(kl),
        surrogate_gain=gain,
        backtracks=backtracks,
        gradient_norm=float(gradient.norm()),
    )


def trpo_update(model, critic_optimizer, rollout, configuration, rng):
    b = collate(rollout["states"])
    result = trpo_actor_update(
        model, b, rollout["actions"], rollout["advantage"], configuration
    )
    actor_after = parameters_to_vector(actor_parameters(model)).detach().clone()
    updates = 0
    for _ in range(2):
        order = rng.permutation(len(rollout["states"]))
        for start in range(0, len(order), 64):
            indices = order[start : start + 64]
            batch = collate([rollout["states"][i] for i in indices])
            _, value = model(batch)
            loss = (
                ((value - rollout["target"][indices]) / rollout["scale"])
                .square()
                .mean()
            )
            critic_optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.critic.parameters(), 1.0)
            critic_optimizer.step()
            updates += 1
    assert torch.equal(
        actor_after, parameters_to_vector(actor_parameters(model)).detach()
    )
    return dict(
        **result, loss=float(loss.detach()), updates=updates + int(result["accepted"])
    )


def dpo_loss(chosen_logp, rejected_logp, reference_chosen, reference_rejected, beta):
    difference = chosen_logp - rejected_logp - (reference_chosen - reference_rejected)
    return -functional.logsigmoid(beta * difference).mean()
