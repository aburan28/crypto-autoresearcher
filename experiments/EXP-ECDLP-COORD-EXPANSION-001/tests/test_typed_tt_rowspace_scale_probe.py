from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "typed_tt_rowspace_scale_probe_test",
    EXP_ROOT / "src" / "typed_tt_rowspace_scale_probe.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load row-space scale probe")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTRowspaceScaleProbeTests(unittest.TestCase):
    def test_bounded_scale_receipt_preserves_negative_boundary(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-ROWSPACE-SCALE-PROBE-V1" / "RUN-001"
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertFalse(raw["summary"]["all_sample_matches"])
        self.assertTrue(raw["summary"]["all_prefix_bounded"])
        self.assertFalse(raw["summary"]["breakthrough_claim"])

    def test_budget_sweep_rank_tracks_prefix_budget(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-ROWSPACE-SCALE-PROBE-V1" / "RUN-001"
        ranks = []
        for name, expected in (("budget-16.json", 16), ("budget-32.json", 32), ("budget-64.json", 64)):
            raw = json.loads((run_dir / name).read_text(encoding="utf-8"))
            ranks.append(raw["rows"][0]["rowspace_rank"])
            self.assertEqual(raw["rows"][0]["rowspace_rank"], expected)
            self.assertGreater(raw["rows"][0]["total_sample_mismatches"], 0)
        self.assertEqual(ranks, [16, 32, 64])


if __name__ == "__main__":
    unittest.main()
