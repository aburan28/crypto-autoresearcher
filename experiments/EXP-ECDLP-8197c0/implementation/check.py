#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-8197c0 Stage 0-1 run artifacts."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-ECDLP-8197c0"
STAGE1_OUTCOMES = {
    "O-FLOOR",
    "O-CONCENTRATION",
    "O-INCONCLUSIVE",
    "O-D1-MISS",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
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
    man = man_path.read_text(encoding="utf-8")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
        errs.append("Bedrock marker missing/invalid")
    if raw.get("claims", {}).get("break") or raw.get("claims", {}).get("exponent_move"):
        errs.append("forbidden break/exponent claim present")

    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]

    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/weil-ceiling.yaml",
            "stage0/d1-d2-breaks.yaml",
            "stage0/precommit-hashes.json",
            "stage0/selfchecks.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        n8 = 256
        sigma_star = 1 / math.sqrt(n8)
        floor = math.sqrt(n8)
        if abs(sigma_star - 0.0625) > 1e-12:
            errs.append(f"independent sigma* {sigma_star} != 1/16")
        if abs(floor - 16) > 1e-12:
            errs.append(f"independent floor {floor} != 16")
        if raw.get("status") != "completed":
            errs.append(f"stage0 status {raw.get('status')!r} is not completed")
        if raw.get("worksheet_ok") is not True:
            errs.append("worksheet_ok must be true")
        if raw.get("selfchecks_all_pass") is not True:
            errs.append("selfchecks_all_pass must be true")
        if "stage: 0" not in man:
            errs.append("manifest missing stage: 0")
        if "run: Magma" in man or "run: Sage" in man:
            errs.append("Magma/Sage success path in manifest")

    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in STAGE1_OUTCOMES:
            errs.append(f"bad stage1 outcome {outcome!r}")
        if outcome and f"outcome: {outcome}" not in man:
            errs.append("manifest outcome disagrees with raw-result")
        for rel in (
            "stage1/cells.yaml",
            "stage1/ladder.json",
            "stage1/d1-control.json",
            "stage1/decision-rules.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        if not (run_dir / "RESULTS.md").is_file():
            errs.append("missing RESULTS.md")
        if "amazon_bedrock: NOT SELECTED" not in man:
            errs.append("manifest missing amazon_bedrock NOT SELECTED")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
