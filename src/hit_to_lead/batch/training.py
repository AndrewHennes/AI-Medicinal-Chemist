"""Subset supervision, differentiable top-k, and delayed-feedback PPO training."""

import numpy as np
import torch
from torch.nn import functional
from ..policy.episodes import starting_case
from .search import collate_states
from .models import relaxed_slots


def sample_state(engine, rng, batch_sizes):
    for _ in range(100):
        pool, reference = starting_case(engine.data.policy_training, rng)
        eligible = np.flatnonzero(
            (pool["y"] > np.min(pool["y"])) & (np.arange(len(pool["y"])) != reference)
        )
        count = (
            0 if rng.random() < 0.35 else int(rng.integers(min(len(eligible), 10) + 1))
        )
        observed = [reference] + rng.choice(eligible, count, replace=False).tolist()
        state = engine.state(pool, observed, int(rng.choice(batch_sizes)))
        if len(state["ids"]) < 2:
            continue
        labels = (pool["y"][state["ids"]] == np.min(pool["y"])).astype(np.float32)
        utility = -(pool["y"][state["ids"]] - pool["y"][reference])
        return state, labels, utility
    raise ValueError("No nonterminal subset-training states")


def supervised_loss(model, engine, rng, batch_sizes, count=12):
    states, sets, labels, maxima = [], [], [], []
    for _ in range(count):
        state, target, utility = sample_state(engine, rng, batch_sizes)
        size = state["requested_count"]
        for mode in range(3):
            if mode == 0:
                chosen = rng.choice(len(target), size, replace=False)
            else:
                scores = state["mu"] if mode == 1 else state["log_ei"]
                noisy = scores / max(np.std(scores), 0.1) + 0.7 * rng.gumbel(
                    size=len(scores)
                )
                chosen = np.argsort(-noisy)[:size]
            states.append(state)
            sets.append(chosen)
            labels.append(float(target[chosen].max()))
            maxima.append(float(utility[chosen].max()))
    indices = torch.zeros(len(sets), max(map(len, sets)), dtype=torch.long)
    valid = torch.zeros_like(indices, dtype=torch.bool)
    for index, subset in enumerate(sets):
        indices[index, : len(subset)] = torch.tensor(subset)
        valid[index, : len(subset)] = True
    logits, predicted_maximum = model(collate_states(states), indices, valid)
    return functional.binary_cross_entropy_with_logits(
        logits, torch.tensor(labels)
    ) + 0.1 * functional.smooth_l1_loss(predicted_maximum, torch.tensor(maxima))


def gumbel_loss(model, engine, rng, batch_sizes, count=16):
    requested = int(rng.choice(batch_sizes))
    rows = [sample_state(engine, rng, [requested]) for _ in range(count)]
    batch = collate_states([row[0] for row in rows])
    scores, _ = model(batch)
    hit = torch.zeros_like(scores)
    for index, (_, target, _) in enumerate(rows):
        hit[index, : len(target)] = torch.tensor(target)
    slots = relaxed_slots(scores, requested, model.c["temperature"])
    live = (
        torch.arange(requested)[None, :]
        < torch.tensor([row[0]["requested_count"] for row in rows])[:, None]
    )
    slot_hit = (slots * hit[:, None, :]).sum(-1).clamp(0, 1)
    success = 1 - torch.prod(1 - slot_hit * live, dim=1)
    target = hit / hit.sum(1, keepdim=True)
    return (
        -success.clamp_min(1e-5).log().mean()
        - 0.1 * (target * functional.log_softmax(scores, 1)).sum(1).mean()
    )


@torch.no_grad()
def policy_rollouts(model, engine, rng, batch_sizes, count=6):
    records = []
    model.eval()
    for _ in range(count):
        pool, reference = starting_case(engine.data.policy_training, rng)
        batch_size = int(rng.choice(batch_sizes))
        observed, episode_records = [reference], []
        rounds = 0
        while np.min(pool["y"][observed]) > np.min(pool["y"]):
            state = engine.state(pool, observed, batch_size)
            pending = []
            for _ in range(state["requested_count"]):
                logits, value = model(collate_states([state], [pending]))
                distribution = torch.distributions.Categorical(logits=logits)
                action = int(distribution.sample()[0])
                episode_records.append(
                    dict(
                        state=state,
                        pending=pending.copy(),
                        action=action,
                        logp=float(distribution.log_prob(torch.tensor([action]))[0]),
                        value=float(value[0]),
                        round=rounds,
                    )
                )
                pending.append(action)
            observed.extend(state["ids"][pending].tolist())
            rounds += 1
        for row in episode_records:
            row["return"] = -(rounds - row["round"])
        records.extend(episode_records)
    return records


def ppo_step(model, optimizer, records, rng):
    if not records:
        return 0.0
    target = torch.tensor([row["return"] for row in records], dtype=torch.float32)
    old = torch.tensor([row["logp"] for row in records])
    actions = torch.tensor([row["action"] for row in records])
    advantage = target - torch.tensor([row["value"] for row in records])
    advantage = (advantage - advantage.mean()) / advantage.std(
        unbiased=False
    ).clamp_min(1.0)
    scale = target.std(unbiased=False).clamp_min(1.0)
    for _ in range(2):
        order = rng.permutation(len(records))
        for begin in range(0, len(order), 64):
            indices = order[begin : begin + 64]
            batch = collate_states(
                [records[index]["state"] for index in indices],
                [records[index]["pending"] for index in indices],
            )
            scores, value = model(batch)
            distribution = torch.distributions.Categorical(logits=scores)
            ratio = (distribution.log_prob(actions[indices]) - old[indices]).exp()
            loss = -torch.minimum(
                ratio * advantage[indices], ratio.clamp(0.8, 1.2) * advantage[indices]
            ).mean()
            loss = (
                loss
                + 0.25 * ((value - target[indices]) / scale).square().mean()
                - 0.01 * distribution.entropy().mean()
            )
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                model.parameters(), 1.0, error_if_nonfinite=True
            )
            optimizer.step()
    return float(loss.detach())
