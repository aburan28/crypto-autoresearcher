#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-b94ec8 Stage 0-2 run artifacts.

Recomputes ord_n(2) and the m=4 admissibility screen without importing
run.py stage logic. Verifies raw-result.json / manifest.yaml agreement.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-BINSTD-b94ec8"
STAGE1_OUTCOMES = {"SETUP_PASS", "O-ARTIFACT", "O-IMPEDIMENT"}
STAGE2_OUTCOMES = {"O-NULL", "O-DIVISOR", "O-SHAPE", "O-ARTIFACT", "O-IMPEDIMENT"}
WORKSHEET_NS = (17, 23, 29, 31, 37, 41)
ADMISSIBLE = {(31, 5), (31, 6)}
M_ARITY = 4


def ord_n_of_2(n: int) -> int:
    a = 1
    for d in range(1, n):
        a = (a * 2) % n
        if a == 1:
            return d
    raise ValueError(n)


def stable_dims(n: int) -> list[int]:
    d = ord_n_of_2(n)
    f = (n - 1) // d
    return sorted({j * d for j in range(f + 1)} | {j * d + 1 for j in range(f + 1)})


def m4_screen() -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for n in WORKSHEET_NS:
        l_max = 1 + (n // M_ARITY)
        for l in stable_dims(n):
            if l >= 2 and M_ARITY * (l - 1) <= n and l <= l_max:
                out.add((n, l))
    return out


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
    screen = m4_screen()
    if screen != ADMISSIBLE:
        errs.append(f"independent screen {sorted(screen)} != {sorted(ADMISSIBLE)}")

    # Spot-check search sizes
    for l, want in ((5, 43690.666666666664), (6, 699050.6666666666)):
        got = (1 << (M_ARITY * l)) / math.factorial(M_ARITY)
        if abs(got - want) > 1e-6:
            errs.append(f"search size l={l}: {got} != {want}")

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
        cells = {tuple(c) for c in (raw.get("admissible_cells") or [])}
        if raw.get("status") == "completed" and cells != ADMISSIBLE:
            errs.append(f"admissible_cells {cells} != {ADMISSIBLE}")

    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in STAGE1_OUTCOMES:
            errs.append(f"bad stage1 outcome {outcome!r}")
        man = man_path.read_text(encoding="utf-8")
        if outcome and f"outcome: {outcome}" not in man:
            errs.append("manifest outcome disagrees with raw-result")
        if outcome == "SETUP_PASS":
            for rel in (
                "stage1/curves-and-bases.json",
                "stage1/fixture-E0.json",
            ):
                if not (root / rel).is_file():
                    errs.append(f"missing {rel}")
            if raw.get("e0_overall_ok") is not True:
                errs.append("SETUP_PASS requires e0_overall_ok true")
            if raw.get("structure_equal_across_curve_shapes") is not True:
                errs.append("SETUP_PASS requires structure equality")
        if ords[31] != 5:
            errs.append("ord_31(2) self-check failed")

    elif stage == 2:
        outcome = raw.get("outcome")
        if outcome not in STAGE2_OUTCOMES:
            errs.append(f"bad stage2 outcome {outcome!r}")
        man = man_path.read_text(encoding="utf-8")
        if outcome and f"outcome: {outcome}" not in man:
            errs.append("manifest outcome disagrees with raw-result")
        for rel in (
            "stage2/leaf-counts.jsonl",
            "stage2/arm-summaries.json",
            "RESULTS.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        if (root / "RESULTS.md").is_file() and outcome:
            body = (root / "RESULTS.md").read_text(encoding="utf-8")
            if f"**{outcome}**" not in body and f"outcome: **{outcome}**" not in body:
                # Accept either bold outcome form used by Stage-2 RESULTS.
                if outcome not in body:
                    errs.append("RESULTS.md does not name the Stage-2 O-* outcome")
        if raw.get("claims", {}).get("deployed_attack"):
            errs.append("forbidden deployed_attack claim present")
        # Exactly one O-* in arm-summaries when present
        arm_path = root / "stage2" / "arm-summaries.json"
        if arm_path.is_file():
            arms = json.loads(arm_path.read_text(encoding="utf-8"))
            if arms.get("outcome") != outcome:
                errs.append("arm-summaries outcome disagrees with raw-result")
        if ords[31] != 5:
            errs.append("ord_31(2) self-check failed")
    else:
        errs.append(f"bad stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
