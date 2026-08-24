"""Bounded zero-compute harness for TASK-20260730-059.

Emits checkable coverage + unittest results under the write scope.
Does not run curve/isogeny/quantum-circuit computation.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .lifetime_hooks import LifetimeRegistry
from .verify import Verify
from .types import PublicInstance, CandidateSecret


def main() -> int:
    out_dir = Path(__file__).resolve().parent
    # Ensure package-relative discovery works from task directory.
    sys.path.insert(0, str(out_dir.parent))
    suite = unittest.defaultTestLoader.loadTestsFromName("scaffold.test_scaffold")
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    cov = LifetimeRegistry().coverage()
    # Smoke call of Verify signature (no-crypto).
    verify_smoke = Verify(
        PublicInstance(token="x", scaffold_accept_token="k"),
        CandidateSecret(token="k"),
    )

    receipt = {
        "task_id": "TASK-20260730-059",
        "package_id": "FC0-EXT-PKG-SSI-001",
        "harness": "scaffold/run_harness.py",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "curve_isogeny_quantum_circuit_compute": False,
        "collimation_sieve_apis_invented": 0,
        "verify_smoke_result": bool(verify_smoke),
        "coverage": cov,
        "unittest": {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "was_successful": result.wasSuccessful(),
        },
        "interpretation_limit": (
            "Scaffolding / stubs / state-machine skeleton only. "
            "Not end-to-end resource vector. Not QUERY_MEMORY clearance. "
            "Not PIN_COMPLETE. Not CollimationSieve."
        ),
    }
    receipt_path = out_dir / "harness_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {receipt_path}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
