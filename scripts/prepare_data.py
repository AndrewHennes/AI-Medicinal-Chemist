"""Run directly from any working directory; edit config JSON rather than CLI flags."""

import os
import sys
from pathlib import Path as path_type

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
repository_root = path_type(__file__).resolve().parents[1]
sys.path.insert(0, str(repository_root / "src"))

if __name__ == "__main__":
    from hit_to_lead.data_import import import_prepared_data

    print(import_prepared_data())
