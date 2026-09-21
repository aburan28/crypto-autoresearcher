from __future__ import annotations
import json
import unittest
from pathlib import Path

from . import ledger_checks as checks
from .test_instantiation import TestPositive, TestInjectionsRejected


def main() -> int:
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite([
        loader.loadTestsFromTestCase(TestPositive),
        loader.loadTestsFromTestCase(TestInjectionsRejected),
    ])
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    all_checks = checks.run_all_checks()
    checks_ok = all(v.get("passed") for v in all_checks.values())

    receipt = {
        "harness": "instantiation_harness",
        "task_id": "TASK-20260730-127",
        "batch_id": "BATCH-039",
        "goal_id": "GOAL-SSI-001",
        "gate_chosen": "A",
        "scale_label": "protocol_toy_scaffold_scale",
        "cryptographic_scale": False,
        "query_memory_cleared": False,
        "zero_compute": True,
        "non_extrapolation": True,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "passed": result.wasSuccessful() and checks_ok,
        "checks_ok": checks_ok,
        "checks": all_checks,
    }
    out = Path(__file__).resolve().parent / "harness_receipt.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"receipt": str(out), "passed": receipt["passed"],
                      "tests_run": receipt["tests_run"]}, indent=2))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
