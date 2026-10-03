#!/usr/bin/env python3
"""Independent checker for EXP-CERTBIN-ec9d83 Stages 0-1. Does not import routes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-CERTBIN-ec9d83"
STAGE0_OUTCOMES = {"O-FREEZE", "O-IMPEDIMENT"}
STAGE1_OUTCOMES = {"O-IDENTITY", "O-COUNTEREXAMPLE", "O-ARTIFACT", "O-IMPEDIMENT"}
ENTRY_BYTES = 16
GIB = 2 ** 30

EXPECTED_B = {
    "n83-m3": 52544464,
    "n83-m4": 872790,
    "n131-m4": 3574951633,
    "n83-m7": 5325,
    "n131-m7": 617668,
}


def mk(m: int, B: int) -> int:
    k = m // 2
    if k == 1:
        return B
    if k == 2:
        return B * (B + 1) // 2
    if k == 3:
        return B * (B + 1) * (B + 2) // 6
    raise ValueError(k)


def pair_gib(B: int) -> float:
    return (B * (B - 1) // 2) * ENTRY_BYTES / GIB


def three_sig_match(computed: float, printed: float) -> bool:
    return abs(computed - printed) / abs(printed) < 0.005


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
    man = man_path.read_text(encoding="utf-8")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT SELECTED", "NOT_USED"):
        errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move") or claims.get("ecdlp_solve"):
        errs.append("forbidden break/exponent/solve claim present")
    if raw.get("n_ge_131_solve"):
        errs.append("n>=131 solve flag set")

    stage = raw.get("stage")
    outcome = raw.get("outcome")
    if f"stage: {stage}" not in man:
        errs.append("manifest stage disagrees")
    if outcome and f"outcome: {outcome}" not in man:
        errs.append("manifest outcome disagrees with raw-result")

    if stage == 0:
        if outcome not in STAGE0_OUTCOMES:
            errs.append(f"stage0 outcome {outcome!r}")
        if outcome == "O-FREEZE":
            freeze_path = run_dir / "r_mem_frozen.json"
            if not freeze_path.is_file():
                errs.append("missing r_mem_frozen.json")
            else:
                freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
                ids = [row["id"] for row in freeze.get("rows", [])]
                if ids != list(EXPECTED_B):
                    errs.append(f"frozen ids {ids!r}")
                for row in freeze.get("rows", []):
                    if row.get("B") != EXPECTED_B.get(row["id"]):
                        errs.append(f"B mismatch {row.get('id')}")
                    if row.get("k") != row.get("m", 0) // 2:
                        errs.append(f"k != floor(m/2) on {row.get('id')}")
    elif stage == 1:
        if outcome not in STAGE1_OUTCOMES:
            errs.append(f"stage1 outcome {outcome!r}")
        if outcome != "O-IMPEDIMENT":
            by_id = {c["id"]: c for c in raw.get("comparisons") or []}
            if set(by_id) != set(EXPECTED_B):
                errs.append(f"comparison ids {sorted(by_id)}")
            for rid, B in EXPECTED_B.items():
                cell = by_id.get(rid)
                if not cell:
                    continue
                m = cell["m"]
                expect_mk = mk(m, B)
                expect_mp = B * (B - 1) // 2
                if cell.get("M_k") != expect_mk or cell.get("M_pair") != expect_mp:
                    errs.append(f"independent M_k/M_pair mismatch on {rid}")
                if rid == "n83-m7" and cell.get("pair_gib") is not None:
                    if not three_sig_match(pair_gib(B), 0.211):
                        errs.append("independent pair_gib m7 failed three-sig vs 0.211")
            agree = raw.get("implementations_agree")
            printed = raw.get("matches_printed")
            pair_ok = raw.get("pair_gib_ok")
            if agree is False and outcome != "O-ARTIFACT":
                errs.append("routes disagree but outcome is not O-ARTIFACT")
            if agree and (printed is False or pair_ok is False) and outcome != "O-COUNTEREXAMPLE":
                errs.append("printed/pair miss should be O-COUNTEREXAMPLE")
            if agree and printed and pair_ok and outcome != "O-IDENTITY":
                errs.append("agreement+match should be O-IDENTITY")
    else:
        errs.append(f"unexpected stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
