"""Run synthetic model, leakage, posterior and resumption checks from any cwd."""

import os
import sys
import unittest
from pathlib import Path as path_type

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
repository_root = path_type(__file__).resolve().parents[1]
sys.path.insert(0, str(repository_root / "src"))

if __name__ == "__main__":
    from hit_to_lead.io import write
    from hit_to_lead.settings import artifact_root

    suite = unittest.defaultTestLoader.discover(str(repository_root / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    write(
        artifact_root / "checks" / "unit_tests.json",
        dict(
            tests=result.testsRun,
            failures=len(result.failures),
            errors=len(result.errors),
            passed=result.wasSuccessful(),
        ),
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
