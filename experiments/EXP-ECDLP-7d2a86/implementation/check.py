#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-7d2a86 Stage 0-1 run artifacts."""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

EXPERIMENT_ID = "EXP-ECDLP-7d2a86"
STAGE1_OUTCOMES = {"O-IMPEDIMENT", "O-ARTIFACT", "LADDER_COMPLETE"}


def binom_le(n: int, d: int) -> int:
    return sum(comb(n, k) for k in range(d + 1))


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
    if raw.get("claims", {}).get("break") or raw.get("claims", {}).get("exponent_move"):
        errs.append("forbidden break/exponent claim present")

    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    man = man_path.read_text(encoding="utf-8")

    if stage == 0:
        for rel in (
            "stage0/counting-table.yaml",
            "stage0/size-law-and-lstar.yaml",
            "stage0/power-table.yaml",
            "stage0/stream-rule.yaml",
            "stage0/precommit-hashes.json",
            "stage0/selfchecks.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        # Independent recomputation of (16,23) D=4 dims
        rows = 23 * binom_le(16, 2)
        cols = binom_le(16, 4)
        if rows != 3151 or cols != 2517:
            errs.append(f"independent (16,23) D4 dims {rows}/{cols} != 3151/2517")
        if raw.get("status") != "completed":
            errs.append(f"stage0 status {raw.get('status')!r} is not completed")
        if raw.get("worksheet_ok") is not True:
            errs.append("worksheet_ok must be true")
        if raw.get("selfchecks_all_pass") is not True:
            errs.append("selfchecks_all_pass must be true")
        if "stage: 0" not in man:
            errs.append("manifest missing stage: 0")

    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in STAGE1_OUTCOMES:
            errs.append(f"bad stage1 outcome {outcome!r}")
        if outcome and f"outcome: {outcome}" not in man:
            errs.append("manifest outcome disagrees with raw-result")
        for rel in (
            "stage1/inputs.json",
            "stage1/c-pin.json",
            "stage1/c-fix.json",
            "stage1/c-self.json",
            "stage1/cell-summary.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        if outcome == "O-IMPEDIMENT":
            if not raw.get("impediments"):
                errs.append("O-IMPEDIMENT requires impediments list")
            if raw.get("C_FIX") is not True:
                errs.append("O-IMPEDIMENT admission surface requires C_FIX true")
        if "stage: 1" not in man:
            errs.append("manifest missing stage: 1")
    else:
        errs.append(f"bad stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
