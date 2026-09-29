#!/usr/bin/env python3
"""primary_metrics satisfies the experiment schema field `metrics`."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_ledger import Ctx, check_experiment


def _write_spec(directory: Path, *, metrics=None, primary_metrics=None) -> Path:
    lines = [
        "experiment:",
        "  id: EXP-ECDLP-000001",
        "  hypothesis_id: H-ECDLP-000001",
        "  version: 1",
        "  status: draft",
        "  budget:",
        "    maximum_runs: 1",
        "  success_criterion: gates hold",
    ]
    if metrics is not None:
        lines.append("  metrics:")
        for item in metrics:
            lines.append(f"    - {item}")
    if primary_metrics is not None:
        lines.append("  primary_metrics:")
        for item in primary_metrics:
            lines.append(f"    - {item}")
    path = directory / "specification.yaml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class PrimaryMetricsAliasTests(unittest.TestCase):
    def _errors(self, path: Path) -> list[str]:
        ctx = Ctx(set())
        check_experiment(str(path), ctx)
        return [e for e in ctx.errors if "metrics" in e]

    def test_primary_metrics_satisfies_required_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_spec(
                Path(tmp),
                primary_metrics=["fixture_pass", "real_remainder_pass"],
            )
            self.assertEqual(self._errors(path), [])

    def test_metrics_field_still_satisfies_required_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_spec(Path(tmp), metrics=["fixture_pass"])
            self.assertEqual(self._errors(path), [])

    def test_neither_metrics_nor_primary_metrics_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_spec(Path(tmp))
            self.assertTrue(
                any("missing required field 'metrics'" in e
                    for e in self._errors(path))
            )


if __name__ == "__main__":
    unittest.main()
