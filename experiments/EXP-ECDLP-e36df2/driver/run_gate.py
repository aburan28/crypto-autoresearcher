"""Single entry point enforcing the two BLOCKING GATES before any Stage 2/3
compute: Stage 0 (0 mismatches) and Stage 1 (positive-control curve/primes
frozen). Per specification.yaml stopping_rules and handoff constraints."""
from __future__ import annotations

import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_ROOT = os.path.join(THIS_DIR, "..")


def check_gates():
    stage0_path = os.path.join(EXP_ROOT, "stage0_regression_transcript.json")
    if not os.path.isfile(stage0_path):
        print("HALT: stage0_regression_transcript.json missing; run "
              "stage0_regression.py first.", file=sys.stderr)
        sys.exit(1)
    with open(stage0_path) as f:
        stage0 = json.load(f)
    if not stage0.get("passed") or stage0.get("total_mismatch", 1) != 0:
        print(f"HALT: Stage 0 regression FAILED "
              f"(mismatches={stage0.get('total_mismatch')}); refusing to "
              f"run Stage 2/3 per the blocking-gate stopping rule.",
              file=sys.stderr)
        sys.exit(1)
    pc_path = os.path.join(EXP_ROOT, "frozen_positive_control_curve.json")
    if not os.path.isfile(pc_path):
        print("HALT: frozen_positive_control_curve.json missing; run "
              "positive_control.py first (Stage 1 must complete and be "
              "frozen before Stage 2).", file=sys.stderr)
        sys.exit(1)
    print(f"Gates OK: Stage 0 passed ({stage0['total_checked']} checked, "
          f"0 mismatches); positive control curve frozen at {pc_path}.")


if __name__ == "__main__":
    check_gates()
    import orchestrate
    orchestrate.run_all()
