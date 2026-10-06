"""Reproduce augmentation comparisons using the named JSON configuration."""

import os
import sys
from pathlib import Path as path_type

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
repository_root = path_type(__file__).resolve().parents[1]
sys.path.insert(0, str(repository_root / "src"))

if __name__ == "__main__":
    from hit_to_lead.analyses.augmentation import run

    run(repository_root / "config/augmentation_analyses.json")
