"""Construct each benchmark family from its recorded configuration."""

from .reference import reference_model
from .gradient import gradient_model
from .neural_process import cnp_model, anp_model, tnp_model
from .alpaca import alpaca_model, alpaca_no_offset_model
from .gaussian_process import kernel_model
from .reference_ablations import reference_ablation_model


def build(configuration: dict, endpoint: str):
    """Return a freshly initialized conditional predictor on CPU."""
    method = configuration["method"]
    if method == "reference":
        return reference_model(configuration, endpoint)
    if method in (
        "reference_unchanged",
        "reference_mean_only",
        "reference_kernel_only",
        "reference_weighted",
    ):
        return reference_ablation_model(configuration, endpoint)
    if method in ("transfer", "finetune", "maml", "anil"):
        return gradient_model(configuration)
    families = {
        "cnp": cnp_model,
        "anp": anp_model,
        "tnp_d": tnp_model,
        "alpaca": alpaca_model,
        "alpaca_no_offset": alpaca_no_offset_model,
        "neural_mean_gp": kernel_model,
        "dkt": kernel_model,
        "adkf_ift": kernel_model,
    }
    if method not in families:
        raise ValueError(
            f"Unknown method {method!r}. Available methods: {tuple(families)}"
        )
    return families[method](configuration)
