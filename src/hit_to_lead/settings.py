"""Editable run settings, resolved independently of the current directory.

The configuration files live beside the source package. For an editable install,
changing config/paths.json changes where artifacts are written. Runtime code
requires absolute external paths; repository-local paths derive from __file__.
"""

import json
from pathlib import Path as path_type

repository_root = path_type(__file__).resolve().parents[2]
path_config_file = repository_root / "config" / "paths.json"
run_config_file = repository_root / "config" / "benchmark.json"
path_settings = json.loads(path_config_file.read_text())
run_settings = json.loads(run_config_file.read_text())
for name, value in path_settings.items():
    if not path_type(value).is_absolute():
        raise ValueError(f"{name} must be an absolute path in {path_config_file}")
artifact_root = path_type(path_settings["artifacts_root"]).resolve()
data_root = artifact_root / "data"
benchmark_root = artifact_root / "benchmark"
configured_methods = tuple(run_settings["methods"])
configured_endpoints = tuple(run_settings["endpoints"])
outer_folds = tuple(run_settings["folds"])
ensemble_seeds = tuple(run_settings["seeds"])
context_sizes = tuple(run_settings["context_sizes"])
search_updates = int(run_settings["search_updates"])
final_updates = int(run_settings["final_updates"])
training_batch_size = int(run_settings["batch_size"])
validation_interval = int(run_settings["validate_every"])
validation_pool_limit = int(run_settings["validation_pool_limit"])
worker_count = int(run_settings["workers"])
base_parameters = dict(
    input_dim=32,
    width=64,
    depth=2,
    feature_dim=16,
    latent_dim=16,
    heads=4,
    layers=2,
    dropout=0.0,
    kernel="matern",
    inner_steps=3,
    inner_lr=0.01,
    inner_penalty=0.01,
    latent_samples=32,
    gp_inner_maxiter=150,
    gp_inner_tolerance=1e-6,
    gp_prior_strength=0.1,
    ift_damping=1e-6,
    lr=0.001,
    weight_decay=0.001,
    max_context=24,
)
search_trials = (
    {},
    {"width": 128, "feature_dim": 32, "latent_dim": 32, "inner_lr": 0.003},
    {
        "width": 64,
        "feature_dim": 32,
        "layers": 3,
        "inner_steps": 5,
        "inner_lr": 0.03,
        "kernel": "rbf",
        "lr": 0.0003,
    },
)


def configuration(method: str, trial: int = 0) -> dict:
    """One of three predeclared trials; no Cartesian-grid expansion."""
    parameters = dict(base_parameters, **search_trials[trial], method=method)
    if method == "reference_weighted":
        parameters.update(weight_temperature=(0.1, 0.3, 1.0)[trial])
    if method == "reference":
        parameters.update(
            width=64,
            depth=2,
            layers=2,
            graph_steps=24,
            lr=(0.001, 0.0003, 0.003)[trial],
        )
    return parameters


def configure_comparison(config_path):
    """Select a source-tree benchmark recipe before importing runner modules."""
    global run_settings, configured_methods, configured_endpoints, outer_folds
    global ensemble_seeds, context_sizes, search_updates, final_updates
    global training_batch_size, validation_interval, validation_pool_limit
    global worker_count, benchmark_root
    config_path = path_type(config_path)
    if not config_path.is_absolute():
        raise ValueError("Comparison configuration must be an absolute path")
    overrides = json.loads(config_path.read_text())
    run_settings = dict(run_settings, **overrides)
    configured_methods = tuple(run_settings["methods"])
    configured_endpoints = tuple(run_settings["endpoints"])
    outer_folds = tuple(run_settings["folds"])
    ensemble_seeds = tuple(run_settings["seeds"])
    context_sizes = tuple(run_settings["context_sizes"])
    search_updates = run_settings["search_updates"]
    final_updates = run_settings["final_updates"]
    training_batch_size = run_settings["batch_size"]
    validation_interval = run_settings["validate_every"]
    validation_pool_limit = run_settings["validation_pool_limit"]
    worker_count = run_settings["workers"]
    benchmark_root = artifact_root / run_settings["output_directory"]
