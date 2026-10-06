"""Import the exact curated folds without silently reconstructing a different split."""

import shutil
from pathlib import Path as path_type
from .io import digest, read, write
from .settings import data_root, outer_folds, path_settings, repository_root


def import_prepared_data() -> path_type:
    """Copy verified fold files into the configured artifact root.

    Inputs contain curated, transformed objective values and frozen MiniMol PCA.

    Existing conflicting destination files are rejected, never overwritten.
    """
    source = path_type(path_settings["prepared_data_source"])
    manifest = read(
        repository_root / "results" / "published" / "prepared_data_manifest.json"
    )
    expected = {
        str(path_type(row["path"]).relative_to(source)): row
        for row in manifest
        if path_type(row["path"]).is_relative_to(source)
    }
    # A relocated exact source has the same fold filenames and hashes.
    if not expected:
        expected = {
            "/".join(path_type(row["path"]).parts[-2:]): row for row in manifest
        }
    copied = []
    for fold in outer_folds:
        for name in ("dataset.json", "features.npz"):
            relative = f"fold_{fold}/{name}"
            original, destination = source / relative, data_root / relative
            expected_hash = expected[relative]["sha256"]
            if digest(original) != expected_hash:
                raise ValueError(
                    f"Prepared input differs from the published data: {original}"
                )
            if destination.exists():
                if digest(destination) != expected_hash:
                    raise ValueError(f"Conflicting prepared file: {destination}")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                temporary = destination.with_suffix(destination.suffix + ".copying")
                shutil.copyfile(original, temporary)
                temporary.replace(destination)
            copied.append(dict(file=relative, sha256=expected_hash))
    write(data_root / "import_manifest.json", dict(source=str(source), files=copied))
    from .data import series_dataset
    from .settings import configured_endpoints

    for fold in outer_folds:
        for endpoint in configured_endpoints:
            series_dataset(fold, endpoint).audit_splits()
    return data_root
