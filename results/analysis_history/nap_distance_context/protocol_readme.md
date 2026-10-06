# Distances to the acquired set as NAP inputs

This controlled extension adds Morgan Tanimoto or Minimol-derived molecular distances to the existing NAP that uses only GP mean and standard deviation. It keeps the chosen neural pair mean plus conventional covariance GP frozen and reuses the exact grouped folds, outcome transforms, initial hits, training objective, and baseline outputs from `outputs/nap_set_context`.

The 28 configurations cover radius-two/radius-three Tanimoto, PCA32/PCA128/full512 Euclidean RMS Minimol distances, full512 cosine distance, nearest-distance versus minimum/mean/maximum/sample-SD summaries, and acquisition widths 32/64. Acquired molecules include the initial hit. The singleton distance SD is zero. Extra inputs are distances only, not measured values or neural delta predictions. The PPO critic retains the same counts as the old baseline.

Five grouped folds, all six endpoints, and three policy seeds are used. Screening and refinement use validation only. Two candidates per family/fold/endpoint receive full training before one architecture is selected and repeated. The final 270 checkpoints are hashed before test evaluation. All outputs are written in this directory; prior experiments remain unchanged.

Primary evaluation is acquisitions to any top-1 compound in pools of at least 15. Top-2/3/4, all pools of at least three, endpoint tables, and minimum-size curves are also reported. Paired intervals cluster on linked series groups.

Run without command-line options from any directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_distance_context/distance_run.py
```

CPU execution uses eight worker processes, each with one PyTorch thread. Completed jobs are resumed. `progress.json` records the active stage. The final report is `reports/nap_distance_results.pdf`, with machine-readable tables, checkpoints, trajectories, configuration choices, and integrity audits alongside it.
