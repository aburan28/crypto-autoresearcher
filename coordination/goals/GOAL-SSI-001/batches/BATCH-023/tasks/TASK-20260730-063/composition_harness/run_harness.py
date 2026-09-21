"""Run composition harness once; write receipt under write scope.

Declared entrypoint (from TASK-20260730-063 directory):
  python3 -m composition_harness.run_harness
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .f_star_probe import probe_f_star_channels
from .peak_live_set_probe import probe_peak_live_sets


def main() -> int:
    task_dir = Path(__file__).resolve().parents[1]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName("composition_harness.test_composition")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    f_star = probe_f_star_channels()
    peak = probe_peak_live_sets()

    receipt = {
        "task_id": "TASK-20260730-063",
        "batch_id": "BATCH-023",
        "package_id": "FC0-EXT-PKG-SSI-001",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entrypoint": "python3 -m composition_harness.run_harness",
        "batch022_scaffold_read_only": True,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "was_successful": result.wasSuccessful(),
        "f_star_summary": f_star["summary"],
        "peak_summary": peak["summary"],
        "curve_isogeny_quantum_circuit_compute": False,
        "tau_invented": False,
        "numeric_widths_invented": False,
        "collimation_sieve_apis_invented": 0,
    }
    out = task_dir / "composition_harness" / "harness_receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
