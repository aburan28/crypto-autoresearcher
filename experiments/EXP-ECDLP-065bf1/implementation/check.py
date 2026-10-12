#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-065bf1 run artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from elliptic import on_curve, scalar_mul  # noqa: E402

EXPERIMENT_ID = "EXP-ECDLP-065bf1"
OUTCOMES = {
    "O-REP-SENSITIVE",
    "O-INCIDENCE-INSUFFICIENT",
    "O-NO-DIFF",
    "O-MIXED",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
P = 17
CURVE_A = 1
CURVE_B = 1
G = (0, 1)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path, man_path = run_dir / "raw-result.json", run_dir / "manifest.yaml"
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
    if claims.get("break") or claims.get("exponent_move") or claims.get("solve"):
        errs.append("forbidden break/exponent/solve claim present")
    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    if stage == 0:
        for rel in ("stage0/preregistered-predictions.json", "stage0/fixtures.json"):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        if (root / "stage0" / "preregistered-predictions.json").is_file():
            pred = json.loads((root / "stage0" / "preregistered-predictions.json").read_text())
            if pred.get("arm_ii_authorized") or pred.get("exponent_moved"):
                errs.append("forbidden arm/exponent authorization")
            cells = pred.get("cells")
            if not isinstance(cells, list):
                errs.append("cells must be a list (integer fields, not string-keyed n/p map)")
            else:
                for cell in cells:
                    if not isinstance(cell.get("p"), int) or not isinstance(cell.get("k"), int):
                        errs.append(f"cell {cell.get('id')} p/k must be ints")
            if pred.get("p") != P:
                errs.append("frozen p mismatch")
            if not on_curve(*G, CURVE_A, CURVE_B, P):
                errs.append("G off curve")
            if scalar_mul(2, G, CURVE_A, P, "A") != scalar_mul(2, G, CURVE_A, P, "B"):
                errs.append("dual route k=2 disagree")
        if raw.get("outcome") not in ("O-STAGE0-OK", "O-ARTIFACT"):
            errs.append(f"bad stage0 outcome {raw.get('outcome')!r}")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        if outcome in ("O-REP-SENSITIVE", "O-INCIDENCE-INSUFFICIENT", "O-NO-DIFF", "O-MIXED"):
            if not (root / "stage0" / "preregistered-predictions.json").is_file():
                errs.append("scientific outcome without Stage-0 freeze")
        md = (root / "RESULTS.md").read_text(encoding="utf-8") if (root / "RESULTS.md").is_file() else ""
        if md and outcome and f"outcome: {outcome}" not in md:
            errs.append("RESULTS.md does not name raw outcome")
    else:
        errs.append(f"bad stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
