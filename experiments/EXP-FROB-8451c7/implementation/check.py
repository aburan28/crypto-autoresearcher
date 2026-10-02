#!/usr/bin/env python3
"""Independent checker for EXP-FROB-8451c7 run artifacts.

Recomputes Arm A integers and Phi_8(2) from the frozen ceilings without
importing run.py. Verifies raw-result.json / manifest.yaml agreement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

G5, G6 = 6725, 39201
N_LEDGER = 131
PREREG = {
    "least_m_g5": 11,
    "least_m_g6": 9,
    "semaev_degree_g5": 512,
    "semaev_degree_g6": 128,
    "phi8": 17,
}


def least_m(ceiling: int, target_bits: int) -> tuple[int, int]:
    target = 1 << target_bits
    product = 1
    m = 0
    while product < target:
        product *= ceiling
        m += 1
    return m, 1 << (m - 2)


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
    stage = raw.get("stage")
    if stage not in (0, 1):
        errs.append(f"bad stage {stage!r}")

    m5, d5 = least_m(G5, N_LEDGER)
    m6, d6 = least_m(G6, N_LEDGER)
    phi8 = (1 << 4) + 1
    image_ok = 8 * (G6 ** 3) < (1 << 51)
    if (m5, d5, m6, d6, phi8) != (
        PREREG["least_m_g5"],
        PREREG["semaev_degree_g5"],
        PREREG["least_m_g6"],
        PREREG["semaev_degree_g6"],
        PREREG["phi8"],
    ) or not image_ok:
        errs.append("independent Arm A recomputation disagrees with preregistered targets")

    if stage == 0:
        ledger = raw.get("ledger") or {}
        g5 = ledger.get("g5") or {}
        g6 = ledger.get("g6") or {}
        if g5.get("least_m") != m5 or g6.get("least_m") != m6:
            errs.append("stage0 ledger least_m mismatch vs independent recomputation")
        if g5.get("semaev_degree") != d5 or g6.get("semaev_degree") != d6:
            errs.append("stage0 semaev_degree mismatch")
        if ledger.get("phi8") != phi8:
            errs.append("stage0 phi8 mismatch")
        if raw.get("preregistered_match") is not True:
            errs.append("stage0 preregistered_match is not true")
        # Stage0 freeze files must exist
        root = Path(__file__).resolve().parents[1]
        for rel in ("stage0/preregistered-predictions.json", "stage0/arm-a-ledger.json"):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")

    if stage == 1:
        if raw.get("phi8") != phi8:
            errs.append("stage1 phi8 mismatch")
        outcome = raw.get("outcome")
        if outcome not in ("O-LEDGER", "O-POSITIVE-TOY", "O-ARTIFACT", "O-IMPEDIMENT"):
            errs.append(f"bad outcome {outcome!r}")
        panels = raw.get("panels") or {}
        torus = panels.get("torus") or {}
        if torus.get("boolean_count_before_quotient") != 68:
            errs.append("torus before-quotient must be g*n=68")
        if "boolean_count_after_quotient" not in torus:
            errs.append("torus missing after-quotient count")
        if raw.get("claims", {}).get("break") or raw.get("claims", {}).get("exponent_move"):
            errs.append("forbidden break/exponent claim present")
        man = man_path.read_text(encoding="utf-8")
        if outcome and f"outcome: {outcome}" not in man:
            errs.append("manifest outcome disagrees with raw-result")

    if "bedrock" in raw_path.read_text(encoding="utf-8").lower() and "NOT_USED" not in raw.get(
        "amazon_bedrock", ""
    ):
        # Allow the explicit NOT_USED marker only.
        if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
            errs.append("Bedrock marker missing/invalid")

    if errs:
        print("FAIL:")
        for e in errs:
            print(" ", e)
        return 1
    print("OK: stage", stage, "raw-result.json and manifest.yaml validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
