"""Ensure all-assay plots cannot hide a missing assay or duplicate a control."""

import unittest
import pandas as pd
from hit_to_lead.reporting import macro_curves


class report_tests(unittest.TestCase):
    def test_missing_assay_excludes_method(self):
        table = pd.DataFrame(
            [
                dict(endpoint="a", method="full", context_size=1, nll=1.0),
                dict(endpoint="b", method="full", context_size=1, nll=3.0),
                dict(endpoint="a", method="partial", context_size=1, nll=-10.0),
            ]
        )
        aggregate, methods = macro_curves(table, "context_size", ["nll"], ["a", "b"])
        self.assertEqual(methods, ["full"])
        self.assertEqual(aggregate.iloc[0].nll, 2.0)

    def test_partial_context_duplicate_and_nan_are_not_hidden(self):
        rows = [
            dict(endpoint=e, method=m, context_size=n, nll=2.0)
            for e in ("a", "b")
            for n in (1, 2)
            for m in ("full", "missing", "duplicate", "undefined")
        ]
        table = pd.DataFrame(rows)
        table = table[
            ~(
                (table.method == "missing")
                & (table.endpoint == "b")
                & (table.context_size == 2)
            )
        ]
        duplicate = table[table.method == "duplicate"].iloc[[0]]
        table = pd.concat([table, duplicate], ignore_index=True)
        table.loc[(table.method == "undefined") & (table.endpoint == "b"), "nll"] = (
            float("nan")
        )
        aggregate, methods = macro_curves(table, "context_size", ["nll"], ["a", "b"])
        self.assertEqual(methods, ["full", "undefined"])
        self.assertTrue(aggregate[aggregate.method == "undefined"].nll.isna().all())
