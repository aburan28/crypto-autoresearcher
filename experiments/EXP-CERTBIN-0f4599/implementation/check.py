#!/usr/bin/env python3
"""Independent checker for EXP-CERTBIN-0f4599 run artifacts.

Recomputes C(B+2,3) twins, dim(W cap V), and a planted triple membership
without importing run.py orchestration.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from combinadic import c_agree, dim_intersection  # noqa: E402
from curve import Curve  # noqa: E402
from gf2n import Field, is_irreducible  # noqa: E402

EXPERIMENT_ID = "EXP-CERTBIN-0f4599"
OUTCOMES = {
    "O-NULL",
    "O-SLICE",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
N = 19
MODULUS = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1


def parse_point(s: str):
    if s == "O":
        return None
    a, b = s.split(",")
    return (int(a, 16), int(b, 16))


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

    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    irr, _ = is_irreducible(MODULUS)
    if not irr:
        errs.append("frozen modulus not irreducible")

    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/curve.json",
            "stage0/cells.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        cells_p = root / "stage0" / "cells.json"
        if cells_p.is_file():
            blob = json.loads(cells_p.read_text())
            F = Field(N, MODULUS)
            E = Curve(F)
            for c in blob.get("cells") or []:
                ca, cb, ok = c_agree(c["B"], 3)
                if not ok or ca != c["C"]:
                    errs.append(f"C twin fail on {c.get('tag')}")
                dcap = dim_intersection(c["basis_v"], c["basis_w"], N)
                if dcap > 0:
                    errs.append(f"W meets V on {c.get('tag')}")
                fb0 = parse_point(c["fb_encoded"][0])
                if fb0 is None or not E.on_curve(fb0):
                    errs.append(f"FB[0] not on curve for {c.get('tag')}")
        if raw.get("outcome") not in OUTCOMES:
            errs.append(f"outcome not in set: {raw.get('outcome')!r}")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"outcome not in set: {outcome!r}")
        panels_p = root / "stage1" / "panels.json"
        if panels_p.is_file():
            panels = json.loads(panels_p.read_text())
            if panels.get("outcome") != outcome:
                errs.append("panels outcome != raw outcome")
            F = Field(N, MODULUS)
            E = Curve(F)
            cells_p = root / "stage0" / "cells.json"
            cells = json.loads(cells_p.read_text())["cells"] if cells_p.is_file() else []
            if cells:
                c0 = cells[0]
                fb = [parse_point(s) for s in c0["fb_encoded"][:3]]
                if any(P is None or not E.on_curve(P) for P in fb):
                    errs.append("independent on-curve fail for frozen FB prefix")
                s = E.add(E.add(fb[0], fb[1]), fb[2])
                if s is not None and not E.on_curve(s):
                    errs.append("planted triple sum off curve")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
