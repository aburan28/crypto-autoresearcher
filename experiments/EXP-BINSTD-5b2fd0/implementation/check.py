#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-5b2fd0 run artifacts.

Recomputes twin dim(V·V) and N_var on a probe row without importing run.py
stage orchestration. Validates raw-result / manifest agreement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import encode_n_var  # noqa: E402
from gf2n import Field  # noqa: E402
from product_space import dim_vv_agree  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-5b2fd0"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}


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

    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/v-catalog.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        if (root / "stage0" / "v-catalog.json").is_file():
            cat = json.loads((root / "stage0" / "v-catalog.json").read_text())
            # Independent twin recompute on n17_l3 first catalog entry
            cell = cat["cells"]["n17_l3"]
            basis = cell["catalog"][0]["basis"]
            F = Field(17, MODULI[17])
            da, db, dok = dim_vv_agree(basis, F)
            na, nb, nok, _ = encode_n_var(F, CURVE_B[17], basis, XR[17])
            if not (dok and nok):
                errs.append("independent twin disagree on stage0 probe")
            probe = cell.get("probe_dimVV") or {}
            if probe.get("a") != da or probe.get("b") != db:
                errs.append("stage0 probe_dimVV mismatch vs independent recompute")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"outcome not in set: {outcome!r}")
        # Spot-check first row of n17_l3
        panels_path = root / "stage1" / "panels.json"
        if panels_path.is_file():
            panels = json.loads(panels_path.read_text())
            panel = panels.get("n17_l3") or {}
            rows = panel.get("rows") or []
            if rows:
                r0 = rows[0]
                F = Field(17, MODULI[17])
                da, db, dok = dim_vv_agree(r0["basis"], F)
                na, nb, nok, _ = encode_n_var(F, CURVE_B[17], r0["basis"], XR[17])
                if not (dok and nok):
                    errs.append("stage1 row0 twin disagree")
                if r0.get("dimVV") != da or r0.get("N_var") != na:
                    errs.append("stage1 row0 values mismatch independent twin")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
