"""Integrity guards for numerical and narrative historical evidence."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path as path_type
from hit_to_lead.analysis_catalog import load_verified_catalog, make_catalog


class catalog_tests(unittest.TestCase):
    def test_catalog_integrity_and_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = path_type(directory)
            archive = root / "results/analysis_history/example"
            archive.mkdir(parents=True)
            artifact = archive / "summary.csv"
            artifact.write_text("method,value\ncontrol,1\n")
            record = dict(
                file="results/analysis_history/example/summary.csv",
                sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                kind="summary_table",
            )
            catalog = dict(
                studies=[
                    dict(
                        id="example",
                        status="archived_results",
                        files=[record],
                        source_code=[],
                    )
                ]
            )
            manifest = root / "results/analysis_history/catalog.json"
            manifest.write_text(json.dumps(catalog))
            self.assertEqual(len(load_verified_catalog(root)["studies"]), 1)
            self.assertTrue(make_catalog(root).is_file())
            artifact.write_text("method,value\ncontrol,2\n")
            with self.assertRaises(ValueError):
                load_verified_catalog(root)
            record["file"] = "../../outside.csv"
            manifest.write_text(json.dumps(catalog))
            with self.assertRaises(ValueError):
                load_verified_catalog(root)
            with self.assertRaises(ValueError):
                load_verified_catalog("relative_path")
