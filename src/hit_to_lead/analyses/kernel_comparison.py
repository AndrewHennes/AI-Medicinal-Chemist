"""Validation-selected covariance comparisons on the common five folds.

Predictive uncertainty is for a new observation.
"""

from pathlib import Path as path_type
import copy
import itertools

import numpy as np
import pandas as pd
import torch
from torch import nn

from ..data import series_dataset
from ..evaluation import prediction_rows, acquisition_rows, summaries
from ..io import digest, read, rng_for, write
from ..models.base import mlp
from ..models.gaussian_process import kernel_model
from ..models.posterior import flat_offset_posterior
from ..settings import artifact_root, data_root
from ..training import atomic_torch_save, implementation_hashes, validate


def tanimoto(x, z):
    """Positive-semidefinite Tanimoto similarity for nonnegative fingerprints."""
    if (x < 0).any() or (z < 0).any():
        raise ValueError("Tanimoto requires nonnegative fingerprint coordinates")
    product = x @ z.T
    denominator = x.square().sum(-1)[:, None] + z.square().sum(-1)[None] - product
    return torch.where(denominator > 0, product / denominator.clamp_min(1e-30), 1.0)


class comparison_gp(kernel_model):
    """Conventional PSD kernels with a separately specified MiniMol mean network."""

    def __init__(self, configuration):
        config = dict(configuration, method="neural_mean_gp", feature_dim=16)
        super().__init__(config)
        self.mean_net = (
            mlp(config["pca_components"], config["width"], 1, config["depth"])
            if config["mean_type"] == "neural"
            else None
        )

    def embeddings(self, context, query):
        count = self.c["pca_components"]
        mean_context = context.x[:, :count]
        mean_query = query[:, :count]
        if self.c["kernel"] == "tanimoto":
            covariance_context, covariance_query = context.x[:, 32:], query[:, 32:]
        else:
            covariance_context, covariance_query = mean_context, mean_query
        if self.mean_net is None:
            context_mean = mean_context.new_zeros(len(mean_context))
            query_mean = mean_query.new_zeros(len(mean_query))
        else:
            context_mean = self.mean_net(mean_context)[:, 0]
            query_mean = self.mean_net(mean_query)[:, 0]
        return tuple(
            t.double()
            for t in (covariance_context, covariance_query, context_mean, query_mean)
        )

    def kernel(self, x, z, phi):
        length, amplitude, _ = self.hyperparameters(phi)
        kind = self.c["kernel"]
        if kind == "tanimoto":
            return amplitude * tanimoto(x, z)
        if kind == "linear":
            return amplitude * (x @ z.T) / x.shape[-1]
        distance = ((x[:, None] - z[None]) / length).square().mean(-1)
        if kind == "rbf":
            return amplitude * torch.exp(-distance / 2)
        if kind == "rational_quadratic":
            shape = self.c.get("rq_shape", 1.0)
            return amplitude * (1 + distance / (2 * shape)).pow(-shape)
        if kind == "matern":
            radius = (5 * distance + 1e-20).sqrt()
            return amplitude * (1 + radius + 5 * distance / 3) * torch.exp(-radius)
        raise ValueError(f"Unknown kernel: {kind}")

    def posterior(self, xc, xq, mc, mq, y, phi):
        _, amplitude, noise = self.hyperparameters(phi)
        diagonal = (
            amplitude * xq.square().mean(-1)
            if self.c["kernel"] == "linear"
            else amplitude.expand(len(xq))
        )
        return flat_offset_posterior(
            mc,
            mq,
            self.kernel(xc, xc, phi),
            self.kernel(xq, xc, phi),
            diagonal,
            noise,
            y,
        )


def fingerprints(data, config, output):
    """Build real Morgan bits from audited feature-index SMILES, never MiniMol."""
    from rdkit import Chem as chemistry, rdBase as rdkit_base
    from rdkit.Chem import rdFingerprintGenerator as fingerprint_generator

    output = path_type(output)
    output.mkdir(parents=True, exist_ok=True)
    spec = dict(
        dataset_sha256=digest(data_root / f"fold_{data.fold}" / "dataset.json"),
        radius=config["morgan_radius"],
        bits=config["morgan_bits"],
        include_chirality=config["morgan_chirality"],
        rdkit_version=rdkit_base.rdkitVersion,
    )
    filename = output / f"fold_{data.fold}.npz"
    specification = output / f"fold_{data.fold}.json"
    if filename.exists():
        previous = read(specification)
        if previous["configuration"] != spec or previous["sha256"] != digest(filename):
            raise RuntimeError("Fingerprint cache provenance mismatch")
        data.fingerprint_provenance = copy.deepcopy(previous)
        with np.load(filename) as stored:
            return stored["fingerprints"]
    smiles_by_index = {}
    for pool in data.metadata["pools"]:
        for index, smiles in zip(
            pool["feature_indices"], pool["molecules"], strict=True
        ):
            if index in smiles_by_index and smiles_by_index[index] != smiles:
                raise ValueError("Conflicting molecular identities at feature index")
            smiles_by_index[index] = smiles
    result = np.zeros((len(data.x), spec["bits"]), dtype=np.uint8)
    generator = fingerprint_generator.GetMorganGenerator(
        radius=spec["radius"],
        fpSize=spec["bits"],
        includeChirality=spec["include_chirality"],
    )
    for index, smiles in smiles_by_index.items():
        molecule = chemistry.MolFromSmiles(smiles)
        if molecule is None:
            raise ValueError(f"Invalid SMILES at feature index {index}")
        result[index] = generator.GetFingerprintAsNumPy(molecule)
    np.savez_compressed(filename, fingerprints=result)
    provenance = dict(configuration=spec, sha256=digest(filename))
    write(specification, provenance)
    data.fingerprint_provenance = copy.deepcopy(provenance)
    return result


class kernel_dataset(series_dataset):
    """Keep context sampling in PCA geometry for every covariance representation."""

    def sample(self, rng, size, max_context=24):
        original = self.x
        try:
            self.x = original[:, :32]
            choices = super().sample(rng, size, max_context)
        finally:
            self.x = original
        return [
            self.episode(
                self.by_id[episode.meta["pool_id"]],
                episode.meta["observed"],
                episode.meta["query"],
            )
            for episode in choices
        ]


def load_data(fold, endpoint, config, output, include_test=False):
    data = kernel_dataset(fold, endpoint, include_test=include_test)
    data.fingerprint_provenance = None
    if "tanimoto" in config["kernels"]:
        bits = fingerprints(data, config, output / "fingerprints")
        data.x = np.concatenate([data.x, bits.astype(np.float32)], axis=1)
    return data


def fit(data, configuration, seed, output, updates, config, cases):
    """Train a fresh fit or resume its exact optimizer/RNG state."""
    output.mkdir(parents=True, exist_ok=True)
    fingerprint_provenance = getattr(data, "fingerprint_provenance", None)
    if configuration["kernel"] == "tanimoto" and fingerprint_provenance is None:
        raise ValueError("Tanimoto fitting requires audited fingerprint provenance")
    signature = dict(
        model=configuration,
        seed=seed,
        updates=updates,
        endpoint=data.endpoint,
        fold=data.fold,
        scale=data.scale,
        batch_size=config["batch_size"],
        validate_every=config["validate_every"],
        validation_cases=[episode.meta for episode in cases],
        data={
            name: digest(data_root / f"fold_{data.fold}" / name)
            for name in ("dataset.json", "features.npz")
        },
        fingerprints=copy.deepcopy(fingerprint_provenance),
        implementation=implementation_hashes(),
    )
    specification = output / "specification.json"
    if specification.exists() and read(specification) != signature:
        raise RuntimeError(f"Existing fit has different provenance: {output}")
    write(specification, signature)
    torch.manual_seed(seed)
    model = comparison_gp(configuration)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=configuration["lr"], weight_decay=0.001
    )
    rng = rng_for("kernel_comparison", data.fold, data.endpoint, seed)
    best, start = float("inf"), 0
    history = []
    resume_file = output / "resume.pt"
    if resume_file.exists():
        resume = torch.load(resume_file, weights_only=False, map_location="cpu")
        model.load_state_dict(resume["model"])
        optimizer.load_state_dict(resume["optimizer"])
        rng.bit_generator.state = resume["rng"]
        torch.set_rng_state(resume["torch_rng"])
        best, start, history = resume["best"], resume["step"], resume["history"]
    for step in range(start + 1, updates + 1):
        model.train()
        optimizer.zero_grad()
        loss_value = 0.0
        for episode in data.sample(rng, config["batch_size"], config["max_context"]):
            loss = model.loss(episode) / config["batch_size"]
            if not torch.isfinite(loss):
                raise FloatingPointError("Nonfinite GP training loss")
            loss.backward()
            loss_value += float(loss.detach())
        nn.utils.clip_grad_norm_(model.parameters(), 5.0, error_if_nonfinite=True)
        optimizer.step()
        if step == 1 or step % config["validate_every"] == 0 or step == updates:
            score = validate(model, cases)
            history.append(dict(step=step, loss=loss_value, validation_nll=score))
            if score < best:
                best = score
                atomic_torch_save(
                    output / "best.pt",
                    dict(
                        model=model.state_dict(),
                        configuration=configuration,
                        validation_nll=best,
                        step=step,
                    ),
                )
            atomic_torch_save(
                resume_file,
                dict(
                    model=model.state_dict(),
                    optimizer=optimizer.state_dict(),
                    rng=rng.bit_generator.state,
                    torch_rng=torch.get_rng_state(),
                    step=step,
                    best=best,
                    history=history,
                ),
            )
            write(output / "history.json", history)
    saved = torch.load(output / "best.pt", weights_only=False, map_location="cpu")
    model.load_state_dict(saved["model"])
    model.eval()
    return model, saved["validation_nll"]


def candidates(config, kernel, mean_type):
    counts = (
        [32]
        if kernel == "tanimoto" and mean_type == "zero"
        else config["pca_components"]
    )
    for count, rate in itertools.product(counts, config["learning_rates"]):
        yield dict(
            input_dim=32,
            pca_components=count,
            width=config["mean_width"],
            depth=2,
            kernel=kernel,
            mean_type=mean_type,
            lr=rate,
            rq_shape=1.0,
        )


def figures(prediction, acquisition, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages as pdf_pages

    output.mkdir(parents=True, exist_ok=True)
    with pdf_pages(output / "kernel_comparison.pdf") as pdf:
        for endpoint in sorted(prediction.endpoint.unique()):
            fig, axes = plt.subplots(1, 4, figsize=(18, 4))
            for method, block in prediction[
                (prediction.endpoint == endpoint) & (prediction.cutoff == 3)
            ].groupby("method"):
                block = block.sort_values("context_size")
                for ax, metric in zip(axes, ("r2", "spearman", "nll", "coverage90")):
                    ax.plot(block.context_size, block[metric], "o-", label=method)
                    ax.set(xlabel="Measured compounds", ylabel=metric)
            axes[0].legend(fontsize=6)
            axes[-1].axhline(0.9, color="grey", linestyle="--")
            fig.suptitle(endpoint.replace("_", " "))
            fig.tight_layout()
            pdf.savefig(fig)
            fig.savefig(output / f"{endpoint}_prediction.png", dpi=160)
            plt.close(fig)
            fig, axes = plt.subplots(1, 4, figsize=(18, 4))
            for method, block in acquisition[acquisition.endpoint == endpoint].groupby(
                "method"
            ):
                for index, ax in enumerate(axes, 1):
                    ax.plot(block.cutoff, block[f"top{index}"], "o-", label=method)
                    ax.set(
                        xlabel="Minimum series size", ylabel=f"Purchases to top {index}"
                    )
            axes[0].legend(fontsize=6)
            fig.suptitle(endpoint.replace("_", " ") + " | direct EI")
            fig.tight_layout()
            pdf.savefig(fig)
            fig.savefig(output / f"{endpoint}_acquisition.png", dpi=160)
            plt.close(fig)


def run(config_file):
    """Run the edited JSON recipe, independent of the launching directory."""
    config_file = path_type(config_file)
    if not config_file.is_absolute():
        raise ValueError("The configuration path must be absolute")
    config = read(config_file)
    if (
        not config["seeds"]
        or min(config["pca_components"]) < 1
        or max(config["pca_components"]) > 32
    ):
        raise ValueError("Need seeds and between 1 and 32 prepared PCA components")
    if set(config["mean_types"]) - {"zero", "neural"}:
        raise ValueError("Mean types must be zero or neural")
    torch.set_num_threads(1)
    output = artifact_root / config["output_directory"]
    output.mkdir(parents=True, exist_ok=True)
    signature = dict(configuration=config, implementation=implementation_hashes())
    manifest = output / "manifest.json"
    if manifest.exists() and read(manifest) != signature:
        raise RuntimeError("Run directory already has different configuration or code")
    write(manifest, signature)
    all_prediction, all_points, all_acquisition = [], [], []
    for fold, endpoint in itertools.product(config["folds"], config["endpoints"]):
        data = load_data(fold, endpoint, config, output)
        cases = data.cases("validation", 1, config["validation_pool_limit"])
        selected = {}
        for kernel, mean_type in itertools.product(
            config["kernels"], config["mean_types"]
        ):
            method = f"{mean_type}_{kernel}"
            base = output / f"fold_{fold}" / endpoint / method
            trials = []
            for trial, parameters in enumerate(candidates(config, kernel, mean_type)):
                _, score = fit(
                    data,
                    parameters,
                    config["seeds"][0],
                    base / "search" / f"trial_{trial}",
                    config["search_updates"],
                    config,
                    cases,
                )
                trials.append(
                    dict(configuration=parameters, validation_nll=score, trial=trial)
                )
            winner = min(trials, key=lambda trial: trial["validation_nll"])
            write(
                base / "selection.json",
                dict(winner=winner, candidates=trials, criterion="Validation NLL only"),
            )
            selected[method] = []
            for seed in config["seeds"]:
                model, _ = fit(
                    data,
                    winner["configuration"],
                    seed,
                    base / "final" / f"seed_{seed}",
                    config["final_updates"],
                    config,
                    cases,
                )
                selected[method].append(model)
        # Test labels become available only after every condition was selected.
        test = load_data(fold, endpoint, config, output, include_test=True)
        for method, models in selected.items():
            rows, points = prediction_rows(
                test, models, method, draws=config["prediction_draws"]
            )
            acquisitions = acquisition_rows(
                test, models, method, draws=config["acquisition_draws"]
            )
            base = output / f"fold_{fold}" / endpoint / method
            write(
                base / "evaluation.json",
                dict(
                    predictions=rows,
                    points=points,
                    acquisitions=acquisitions,
                    checkpoints={
                        str(seed): digest(base / "final" / f"seed_{seed}" / "best.pt")
                        for seed in config["seeds"]
                    },
                ),
            )
            all_prediction.extend(rows)
            all_points.extend(points)
            all_acquisition.extend(acquisitions)
        for row in acquisitions:
            random_row = copy.deepcopy(row)
            random_row.update(
                method="random",
                **{f"top{k}": row[f"random_top{k}"] for k in range(1, 5)},
            )
            all_acquisition.append(random_row)
    predictions, acquisitions = summaries(all_prediction, all_points, all_acquisition)
    report = output / "reports"
    report.mkdir(parents=True, exist_ok=True)
    prediction_frame, acquisition_frame = pd.DataFrame(predictions), pd.DataFrame(
        acquisitions
    )
    for frame, keys in (
        (prediction_frame, ["method", "context_size", "cutoff"]),
        (acquisition_frame, ["method", "cutoff"]),
    ):
        macro = frame.groupby(keys).mean(numeric_only=True).reset_index()
        for count_name in ("pools", "rank_eligible_pools"):
            if count_name in frame:
                macro[count_name] = frame.groupby(keys)[count_name].sum().to_numpy()
        macro["endpoint"] = "all"
        if frame is prediction_frame:
            prediction_frame = pd.concat([frame, macro], ignore_index=True)
        else:
            acquisition_frame = pd.concat([frame, macro], ignore_index=True)
    prediction_frame.to_csv(report / "prediction_summary.csv", index=False)
    acquisition_frame.to_csv(report / "acquisition_summary.csv", index=False)
    figures(prediction_frame, acquisition_frame, report)
    write(output / "completed.json", dict(status="complete", reports=str(report)))
