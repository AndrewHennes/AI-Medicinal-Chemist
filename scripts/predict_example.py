"""Use the saved reference ensemble on one held-out series; no fitting."""

import os
import sys
from pathlib import Path as path_type

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
repository_root = path_type(__file__).resolve().parents[1]
sys.path.insert(0, str(repository_root / "src"))


def main():
    import numpy as np
    import torch
    from hit_to_lead.settings import data_root, artifact_root, path_settings
    from hit_to_lead.data import series_dataset
    from hit_to_lead.inference import predictor
    from hit_to_lead.io import write

    torch.set_num_threads(1)
    fold, endpoint, method = 0, "microsomal_clearance", "reference"
    data = series_dataset(fold, endpoint, include_test=True)
    case = next(
        e
        for e in data.cases("test", 1)
        if e.meta["context_size"] == 5 and e.meta["pool_size"] >= 15
    )
    pool = data.by_id[case.meta["pool_id"]]
    raw = np.load(
        path_type(path_settings["prepared_data_source"]) / "raw_minimol.npy",
        mmap_mode="r",
    )
    base = (
        path_type(path_settings["published_benchmark_root"])
        / "runs"
        / f"fold_{fold}"
        / endpoint
        / method
        / "final"
    )
    predictor = predictor(
        [base / f"seed_{seed}" / "best.pt" for seed in (11, 29, 47)],
        data_root / f"fold_{fold}" / "features.npz",
        data.scale,
    )
    measured, queries = case.meta["observed"], case.meta["query"]
    context_x = raw[pool["indices"][measured]]
    query_x = raw[pool["indices"][queries]]
    # objective is already log-transformed. Hidden query values are never passed.
    measured_values = np.asarray(pool["objective"])[measured]
    posterior = predictor.predict(context_x, measured_values, query_x)
    chosen, scores = predictor.select_next(context_x, measured_values, query_x)
    destination = artifact_root / "examples" / "held_out_series_prediction.json"
    write(
        destination,
        dict(
            endpoint=endpoint,
            method=method,
            fold=fold,
            pool_id=pool["pool_id"],
            measured_pool_indices=measured,
            query_pool_indices=queries,
            mean_relative_to_initial_hit=posterior.mean.tolist(),
            standard_deviation=posterior.standard_deviation.tolist(),
            lower90=posterior.lower90.tolist(),
            upper90=posterior.upper90.tolist(),
            chosen_query_row=chosen,
            chosen_pool_index=queries[chosen],
            log_ei=scores.tolist(),
            units="log10 clearance relative to the initial measured compound",
            selection_scope="The five fixed hidden query molecules in this example, not the full remaining pool",
        ),
    )
    print(destination)


if __name__ == "__main__":
    main()
