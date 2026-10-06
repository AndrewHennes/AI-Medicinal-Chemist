"""Joint GP states and complete delayed-feedback acquisition episodes."""

import numpy as np
import torch
from ..distributions import measured_context
from ..evaluation import start_hit
from .search import log_ei, batch_times, random_expectation, select_classical
from .models import select_neural


def joint_posterior(model, context, query):
    """Joint observation covariance for the conventional-kernel neural-mean GP.

    Uses the same flat intercept as its marginal prediction.
    """
    if model.c["method"] != "neural_mean_gp":
        raise ValueError("Batch covariance requires the neural_mean_gp backend")
    xc, xq, mc, mq = model.embeddings(context, query)
    noise = model.hyperparameters(model.phi)[2]
    covariance = model.kernel(xc, xc, model.phi) + noise * torch.eye(
        len(xc), dtype=torch.float64
    )
    factor = torch.linalg.cholesky((covariance + covariance.T) / 2)
    one = torch.ones(len(xc), dtype=torch.float64)
    precision_one = torch.cholesky_solve(one[:, None], factor)[:, 0]
    residual = context.y.double() - mc
    precision_residual = torch.cholesky_solve(residual[:, None], factor)[:, 0]
    precision = one @ precision_one
    intercept = (one @ precision_residual) / precision
    cross = model.kernel(xq, xc, model.phi)
    mean = mq + intercept + cross @ (precision_residual - precision_one * intercept)
    solved = torch.cholesky_solve(cross.T, factor)
    loading = 1 - cross @ precision_one
    joint = model.kernel(xq, xq, model.phi) + noise * torch.eye(
        len(xq), dtype=torch.float64
    )
    joint = joint - cross @ solved + torch.outer(loading, loading) / precision
    return mean, (joint + joint.T) / 2


class batch_engine:
    def __init__(self, data, models, dimension=32):
        self.data, self.models, self.dimension = data, models, dimension
        for model in models:
            model.eval().requires_grad_(False)

    @torch.no_grad()
    def state(self, pool, observed, batch_size):
        ids = np.array(
            [index for index in range(len(pool["y"])) if index not in observed]
        )
        if not len(ids) or batch_size < 1:
            raise ValueError("A batch needs positive size and available candidates")
        x = torch.tensor(self.data.x[pool["indices"]], dtype=torch.float32)
        values = pool["y"][observed] - pool["y"][observed[0]]
        context = measured_context(
            x[observed], torch.tensor(values, dtype=torch.float32)
        )
        parts = [joint_posterior(model, context, x[ids]) for model in self.models]
        means = torch.stack([part[0] for part in parts])
        mean = means.mean(0)
        covariance = (
            torch.stack(
                [
                    part[1] + torch.outer(part[0] - mean, part[0] - mean)
                    for part in parts
                ]
            )
            .mean(0)
            .numpy()
        )
        utility = -mean.numpy()
        sd = np.sqrt(np.diag(covariance).clip(0))
        correlation = np.clip(
            covariance / np.maximum(sd[:, None] * sd[None, :], 1e-12), -1, 1
        )
        coordinates = x[ids].numpy()
        distance = ((coordinates[:, None] - coordinates[None, :]) ** 2).mean(-1)
        relations = np.stack(
            [
                correlation,
                np.log1p(distance),
                np.abs(utility[:, None] - utility[None, :]),
            ],
            -1,
        )
        best = float(-np.min(values))
        expected_improvement = log_ei(utility, sd, best)
        # Prior signed differences supply the delta feature in this new runner.
        delta = (
            -torch.stack(
                [
                    (
                        model.mean_net(x[ids])[:, 0]
                        - model.mean_net(x[observed[:1]])[0, 0]
                    )
                    for model in self.models
                ]
            )
            .mean(0)
            .numpy()
        )
        count = len(ids)
        requested = min(batch_size, count)
        candidate = np.concatenate(
            [
                coordinates[:, : self.dimension],
                np.repeat(x[observed[:1], : self.dimension].numpy(), count, axis=0),
            ],
            -1,
        )
        scalars = np.column_stack(
            [
                utility,
                sd,
                np.full(count, best),
                delta,
                np.zeros(count),
                np.clip(expected_improvement, -40, 10) / 10,
            ]
        )
        global_features = np.array(
            [
                np.log1p(count),
                np.log1p(len(observed)),
                best,
                float(-values.mean()),
                float(values.std()),
                requested / count,
                np.log1p(requested),
            ],
            np.float32,
        )
        return dict(
            ids=ids,
            features=np.concatenate([candidate, scalars], -1).astype(np.float32),
            relations=relations.astype(np.float32),
            global_features=global_features,
            mu=utility,
            sd=sd,
            covariance=covariance,
            best=best,
            delta=delta,
            log_ei=expected_improvement,
            requested_count=requested,
        )


def simulate(engine, pool, reference, batch_size, method, model=None, seed=11):
    observed = [reference]
    batches = []
    while np.min(pool["y"][observed]) > np.min(pool["y"]):
        state = engine.state(pool, observed, batch_size)
        if model is None:
            selected = select_classical(state, batch_size, method, seed + len(batches))
        else:
            selected, _ = select_neural(model, state, batch_size)
        chosen = state["ids"][selected].tolist()
        if len(set(chosen)) != min(batch_size, len(state["ids"])) or set(chosen) & set(
            observed
        ):
            raise ValueError("Invalid subset returned by selector")
        batches.append(chosen)
        # Reveal the entire set only after all members have been selected.
        observed.extend(chosen)
    rounds, compounds = batch_times(pool, reference, batches)
    random_rounds, random_compounds = random_expectation(pool, reference, batch_size)
    return dict(
        pool_id=pool["pool_id"],
        group=pool["group"],
        pool_size=len(pool["y"]),
        batch_size=batch_size,
        batches=batches,
        rounds=rounds,
        compounds=compounds,
        random_rounds=random_rounds,
        random_compounds=random_compounds,
    )


def evaluate(
    engine, model, method, batch_sizes, subset="test", draws=4, pool_limit=None
):
    rows = []
    pools = [pool for pool in engine.data.pools if pool["subset"] == subset]
    if pool_limit:
        pools = sorted(pools, key=lambda pool: pool["pool_id"])[:pool_limit]
    for pool in pools:
        for draw in range(draws):
            for batch_size in batch_sizes:
                rows.append(
                    dict(
                        simulate(
                            engine,
                            pool,
                            start_hit(pool, draw),
                            batch_size,
                            method,
                            model,
                        ),
                        draw=draw,
                    )
                )
    return rows
