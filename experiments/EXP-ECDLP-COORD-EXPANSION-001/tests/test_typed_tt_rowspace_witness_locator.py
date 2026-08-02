from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "typed_tt_rowspace_witness_locator_test",
    EXP_ROOT / "src" / "typed_tt_rowspace_witness_locator.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load row-space locator producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTRowspaceWitnessLocatorTests(unittest.TestCase):
    def test_sealed_modes_preserve_support_and_witnesses(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-ROWSPACE-WITNESS-LOCATOR-V1" / "RUN-001"
        per_target = json.loads((run_dir / "per-target.json").read_text(encoding="utf-8"))
        reuse = json.loads((run_dir / "reuse.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertTrue(per_target["summary"]["all_candidate_witnesses_valid"])
        self.assertTrue(per_target["summary"]["all_supports_match"])
        self.assertTrue(reuse["summary"]["all_candidate_witnesses_valid"])
        self.assertTrue(reuse["summary"]["all_supports_match"])

    def test_reuse_is_strictly_cheaper_in_source_queries(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-ROWSPACE-WITNESS-LOCATOR-V1" / "RUN-001"
        per_target = json.loads((run_dir / "per-target.json").read_text(encoding="utf-8"))
        reuse = json.loads((run_dir / "reuse.json").read_text(encoding="utf-8"))
        self.assertTrue(all(
            reuse_row["candidate_source_ops"]["unique_queries"] <= per_row["candidate_source_ops"]["unique_queries"]
            for per_row, reuse_row in zip(per_target["rows"], reuse["rows"])
        ))
        self.assertTrue(any(
            reuse_row["candidate_source_ops"]["unique_queries"] < per_row["candidate_source_ops"]["unique_queries"]
            for per_row, reuse_row in zip(per_target["rows"], reuse["rows"])
        ))
        self.assertTrue(all(row["candidate_predicted_entries_fraction"] == 1.0 for row in reuse["rows"]))


if __name__ == "__main__":
    unittest.main()
