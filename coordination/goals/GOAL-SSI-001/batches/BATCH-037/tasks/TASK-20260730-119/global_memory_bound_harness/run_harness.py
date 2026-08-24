"""Run global memory-bound schema harness and write receipt."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from . import ledger_checks as checks
from .test_global_memory_bound import (
    TestForbiddenFlags,
    TestMemoryMapAndClassification,
    TestObligationLedger,
    TestScaffold,
)


def main() -> int:
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for cls in (TestObligationLedger, TestMemoryMapAndClassification, TestForbiddenFlags, TestScaffold):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {
        "harness": "global_memory_bound_harness",
        "task_id": "TASK-20260730-119",
        "batch_id": "BATCH-037",
        "goal_id": "GOAL-SSI-001",
        "zero_compute": True,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "passed": result.wasSuccessful(),
        "checks": {
            "obligation_ledger": checks.check_obligation_ledger(),
            "memory_map_status": checks.check_memory_map_status(),
            "classification": checks.check_classification(),
            "mutation_status": checks.check_mutation_status(),
            "no_invented_numerics": checks.check_no_invented_numerics(),
            "forbidden_clearance_flags": checks.check_forbidden_clearance_flags(),
            "scaffold_read_only": checks.check_scaffold_read_only(),
        },
    }
    out = Path(__file__).resolve().parent / "harness_receipt.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(out), "passed": receipt["passed"], "tests_run": receipt["tests_run"]}, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
