#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-3abd24 run artifacts.

Recomputes dual Möbius degree on the easy control without importing run.py
stage orchestration. Validates raw-result / manifest agreement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from fp_semaev import least_prime_above, s3_eval_a, s3_eval_b  # noqa: E402
from mobius_fp import dual_degree, pointwise_inv  # noqa: E402

EXPERIMENT_ID = "EXP-ECDLP-3abd24"
OUTCOMES = {
    "O-FULL",
    "O-HALF",
    "O-BOUNDED",
    "O-MIXED",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    errs: list[str] = []
    if not raw_path.is_file() or raw_path.stat().st_size == 0:
        errs.append("missing/empty raw-result.json")
    if not man_path.is_file() or man_path.stat().st_size == 0:
        errs.append("missing/empty manifest.yaml")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
        errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move"):
        errs.append("forbidden break/exponent claim present")
    outcome = raw.get("outcome")
    if outcome not in OUTCOMES:
        errs.append(f"unknown outcome {outcome!r}")

    # Dual S_3 expansions agree on a probe triple.
    p = 19
    va = s3_eval_a(1, 1, 3, 5, 7, p)
    vb = s3_eval_b(1, 1, 3, 5, 7, p)
    if va != vb:
        errs.append("S_3 dual-expansion probe mismatch")

    # Dual Möbius on easy control f = 3 + a0 over F_p, n=8.
    p8 = least_prime_above(2**13)
    table = [((3 + (mask & 1)) % p8) for mask in range(1 << 8)]
    inv = pointwise_inv(table, p8)
    if inv is None:
        errs.append("easy-control inverse failed")
    else:
        da, db, agree = dual_degree(inv, p8)
        if not agree or da != 1:
            errs.append(f"easy-control dual degree {da},{db} agree={agree}")

    root = Path(__file__).resolve().parents[1]
    stage = raw.get("stage")
    if stage == 0:
        freeze = root / "stage0" / "preregistered-predictions.json"
        if not freeze.is_file():
            errs.append("missing stage0/preregistered-predictions.json")
        else:
            pre = json.loads(freeze.read_text(encoding="utf-8"))
            cells = pre.get("cells")
            if not isinstance(cells, list) or not cells:
                errs.append("freeze cells must be a list of rows")
            else:
                for row in cells:
                    if not isinstance(row, dict) or not isinstance(row.get("n"), int):
                        errs.append("freeze row missing integer n")
                        break
    if stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        man = man_path.read_text(encoding="utf-8")
        if f"outcome: {outcome}" not in man and f'outcome: "{outcome}"' not in man:
            # tolerate yaml quoting
            if f"outcome: {outcome}" not in man.replace('"', ""):
                errs.append("manifest outcome disagrees with raw-result")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
