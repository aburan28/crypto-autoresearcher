from __future__ import annotations
import json, unittest
from pathlib import Path
from . import ledger_checks as checks
from .test_composition_aggregation import TestPackage

def main() -> int:
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPackage)
  result = unittest.TextTestRunner(verbosity=2).run(suite)
  receipt = {
    "harness": "composition_aggregation_harness",
    "task_id": "TASK-20260730-123",
    "batch_id": "BATCH-038",
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
    },
  }
  out = Path(__file__).resolve().parent / "harness_receipt.json"
  out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
  print(json.dumps({"receipt": str(out), "passed": receipt["passed"], "tests_run": receipt["tests_run"]}, indent=2))
  return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
  raise SystemExit(main())
