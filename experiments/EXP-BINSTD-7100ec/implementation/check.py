#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-7100ec Stage 0 run artifacts."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-BINSTD-7100ec"
OUTCOMES = {
    "O-C1-HOLD",
    "O-C1-COUNTEREXAMPLE",
    "O-C2-FAIL",
    "O-C3-MIXED",
    "O-IMPEDIMENT",
}
EXP_ROOT = Path(__file__).resolve().parents[1]
RHO_NEG_CONST = math.sqrt(math.pi) / 2.0


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    errs: list[str] = []
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
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

    stage = raw.get("stage")
    if stage != 0:
        errs.append(f"unexpected stage {stage!r}")
    outcome = raw.get("outcome")
    if outcome not in OUTCOMES:
        errs.append(f"outcome {outcome!r} not in {sorted(OUTCOMES)}")

    man = man_path.read_text(encoding="utf-8")
    if "stage: 0" not in man:
        errs.append("manifest missing stage: 0")
    if outcome and f"outcome: {outcome}" not in man:
        errs.append("manifest outcome disagrees with raw-result")

    if outcome == "O-IMPEDIMENT":
        if raw.get("status") not in ("failed_infrastructure", "completed"):
            errs.append(f"impediment status {raw.get('status')!r} unexpected")
    else:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/c1-inclusion-rules.md",
            "stage0/c1-census.json",
            "stage0/c1-census.md",
            "stage0/c2-rho-table.json",
            "stage0/c3-delta-table.json",
            "stage0/support-restatement-cafcf1.md",
            "stage0/c07598-section.md",
            "RESULTS.md",
        ):
            if not (EXP_ROOT / rel).is_file():
                errs.append(f"missing {rel}")
        neg = int(round(RHO_NEG_CONST * (2**8)))
        tau = int(round(neg / math.sqrt(17)))
        if neg != 227 or tau != 55:
            errs.append(f"independent n17 fixture got ({neg},{tau}) != (227,55)")
        results = EXP_ROOT / "RESULTS.md"
        if results.is_file():
            text = results.read_text(encoding="utf-8")
            hits = [lab for lab in OUTCOMES if f"**{lab}**" in text]
            if len(hits) != 1:
                errs.append(f"RESULTS.md must name exactly one O-* label, found {hits}")
            elif hits[0] != outcome:
                errs.append("RESULTS.md label disagrees with raw-result outcome")
        if raw.get("status") != "completed":
            errs.append(f"status {raw.get('status')!r} is not completed")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
