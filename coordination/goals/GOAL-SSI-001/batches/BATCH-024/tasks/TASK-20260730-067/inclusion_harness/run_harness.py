"""Run inclusion harness once; write receipt under write scope.

Declared entrypoint (from TASK-20260730-067 directory):
  python3 -m inclusion_harness.run_harness
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .f_sim_probe import probe_f_sim_treatment
from .path_probe import probe_path_justified_inclusions


def main() -> int:
    task_dir = Path(__file__).resolve().parents[1]
    # Ensure task dir is on sys.path for `python3 -m inclusion_harness.run_harness`.
    if str(task_dir) not in sys.path:
        sys.path.insert(0, str(task_dir))

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName("inclusion_harness.test_inclusion")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    path_report = probe_path_justified_inclusions()
    f_sim_report = probe_f_sim_treatment()

    receipt = {
        "task_id": "TASK-20260730-067",
        "batch_id": "BATCH-024",
        "package_id": "FC0-EXT-PKG-SSI-001",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entrypoint": "python3 -m inclusion_harness.run_harness",
        "batch022_scaffold_read_only": True,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "was_successful": result.wasSuccessful(),
        "path_justified_summary": path_report["summary"],
        "required_union_status": path_report["required_union"]["status"],
        "path_justified_constituents": path_report["required_union"][
            "path_justified_constituents"
        ],
        "f_sim_summary": f_sim_report["summary"],
        "curve_isogeny_quantum_circuit_compute": False,
        "tau_invented": False,
        "numeric_widths_invented": False,
        "collimation_sieve_apis_invented": 0,
        "query_memory_cleared": False,
        "qm_stopping_cleared": False,
    }
    out = task_dir / "inclusion_harness" / "harness_receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
