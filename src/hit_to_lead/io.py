"""Atomic metadata I/O, deterministic seeds, and content hashes."""

import hashlib
import json
from pathlib import Path as path_type
import numpy as np


def seed_for(*parts):
    return int.from_bytes(
        hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:4], "little"
    )


def rng_for(*parts):
    return np.random.default_rng(seed_for(*parts))


def write(path, obj):
    path = path_type(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False))
    tmp.replace(path)


def read(path):
    return json.loads(path_type(path).read_text())


def digest(path):
    return hashlib.sha256(path_type(path).read_bytes()).hexdigest()
