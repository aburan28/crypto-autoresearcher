#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-0e0666 Stage 0-1 run artifacts.

Recomputes ord_n(2) and Lucas #E_1(F_{2^17}) without importing run.py stage
logic. Verifies raw-result.json / manifest.yaml agreement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-BINSTD-0e0666"
STAGE1_OUTCOMES = {"SETUP_PASS", "O-ARTIFACT", "O-IMPEDIMENT"}
WORKSHEET_NS = (17, 23, 31, 41, 131, 163)


def ord_n_of_2(n: int) -> int:
    a = 1
    for d in range(1, n):
        a = (a * 2) % n
        if a == 1:
            return d
    raise ValueError(n)


def koblitz_order_lucas(n: int, a: int) -> int:
    t = 1 if a == 1 else -1
    if n == 1:
        return (1 << 1) + 1 - t
    s0, s1 = 2, t
    for _ in range(2, n + 1):
        s0, s1 = s1, t * s1 - 2 * s0
    return (1 << n) + 1 - s1


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

    ords = {n: ord_n_of_2(n) for n in WORKSHEET_NS}
    e17 = koblitz_order_lucas(17, 1)
    if e17 != 131174:
        errs.append(f"independent Lucas #E_1(F_2^17)={e17} != 131174")

    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/worksheet-note.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        freeze = raw.get("ord_n_2") or {}
        for n, d in ords.items():
            if int(freeze.get(str(n), -1)) != d:
                errs.append(f"ord_n(2) mismatch at n={n}: got {freeze.get(str(n))} want {d}")
                break
        if raw.get("worksheet_ok") is True and raw.get("status") != "completed":
            errs.append("worksheet_ok true but status not completed")
        if raw.get("preregistered_match") is not True and raw.get("status") == "completed":
            errs.append("completed stage0 without preregistered_match")

    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in STAGE1_OUTCOMES:
            errs.append(f"bad stage1 outcome {outcome!r}")
        man = man_path.read_text(encoding="utf-8")
        # Accept flat or nested run.result.outcome (top-level run: / manifest_v2).
        if outcome and f"outcome: {outcome}" not in man:
            errs.append("manifest outcome disagrees with raw-result")
        if not man.lstrip().startswith("run:"):
            errs.append("manifest missing top-level run: (use nested shape or manifest_v2)")
        if outcome == "SETUP_PASS":
            for rel in (
                "stage1/curves-bases-lambda.json",
                "stage1/cayley-accident.json",
                "stage1/fixture-F0.json",
            ):
                if not (root / rel).is_file():
                    errs.append(f"missing {rel}")
            if raw.get("f0_overall_ok") is not True:
                errs.append("SETUP_PASS requires f0_overall_ok true")
            if raw.get("lambda") in (None, 0):
                errs.append("SETUP_PASS requires nonzero lambda")
        if ords[17] != 8:
            errs.append("ord_17(2) self-check failed")
    else:
        errs.append(f"bad stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
