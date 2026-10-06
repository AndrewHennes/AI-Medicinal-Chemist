"""Outcome-supervised group-relative optimization for acquisition trajectories.

Each group samples complete trajectories from one identical starting context.
The reward is minus purchases to the optimum. Advantages use the population
standard deviation within that group. The objective averages actions within
trajectories, then trajectories within groups, as in DeepSeekMath equation 3.
The finite action space permits exact categorical KL to a frozen reference.
"""

import numpy as np
import torch
from torch.nn import functional
from .network import collate
from .optimizers import actor_parameters


def group_rollout(groups, epsilon=1e-6):
    states, actions, log_probabilities, advantages, weights = [], [], [], [], []
    informative = 0
    if not groups or any(len(group) < 2 for group in groups):
        raise ValueError("GRPO requires at least two trajectories per group")
    for group in groups:
        if any(not trajectory for trajectory in group):
            raise ValueError("GRPO groups must start at a nonterminal context")
        identities = {
            (trajectory[0][0]["pool_id"], trajectory[0][0]["reference"])
            for trajectory in group
        }
        if len(identities) != 1:
            raise ValueError(
                "All trajectories in a GRPO group must share the starting context"
            )
        rewards = -np.asarray([len(trajectory) for trajectory in group], dtype=float)
        deviation = rewards.std(ddof=0)
        normalized = (rewards - rewards.mean()) / max(deviation, epsilon)
        informative += int(deviation > epsilon)
        for trajectory, advantage in zip(group, normalized):
            for state, action, old_logp, _ in trajectory:
                states.append(state)
                actions.append(action)
                log_probabilities.append(old_logp)
                advantages.append(advantage)
                weights.append(1 / (len(groups) * len(group) * len(trajectory)))
    return dict(
        states=states,
        actions=torch.tensor(actions),
        old_logp=torch.tensor(log_probabilities),
        advantage=torch.tensor(advantages, dtype=torch.float32),
        weight=torch.tensor(weights, dtype=torch.float32),
        informative_groups=informative,
    )


def grpo_objective(logits, reference_logits, rollout, clip, beta):
    current_logp = functional.log_softmax(logits, -1)
    reference_logp = functional.log_softmax(reference_logits.detach(), -1)
    selected = current_logp.gather(1, rollout["actions"][:, None]).squeeze(1)
    ratio = (selected - rollout["old_logp"]).exp()
    advantage = rollout["advantage"]
    surrogate = torch.minimum(
        ratio * advantage, ratio.clamp(1 - clip, 1 + clip) * advantage
    )
    divergence = (current_logp.exp() * (current_logp - reference_logp)).sum(-1)
    return (rollout["weight"] * (-surrogate + beta * divergence)).sum(), divergence


def grpo_update(model, reference, optimizer, groups, config):
    model.eval()
    reference.eval()
    rollout = group_rollout(groups)
    batch = collate(rollout["states"])
    with torch.no_grad():
        reference_logits = reference(batch)[0]
    for _ in range(config.get("epochs", 2)):
        loss, divergence = grpo_objective(
            model(batch)[0],
            reference_logits,
            rollout,
            config["clip"],
            config.get("beta", 0.01),
        )
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            actor_parameters(model), 1.0, error_if_nonfinite=True
        )
        optimizer.step()
    return dict(
        loss=float(loss.detach()),
        kl=float((rollout["weight"] * divergence.detach()).sum()),
        informative_groups=rollout["informative_groups"],
        groups=len(groups),
        updates=config.get("epochs", 2),
    )
