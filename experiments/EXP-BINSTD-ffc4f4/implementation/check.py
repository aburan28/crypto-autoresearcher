#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-ffc4f4 run artifacts.

Recomputes twin dim(V·V) and N_var on a probe without importing run.py
stage orchestration. Refuses parent catalog_seed 2026100327.
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

EXPERIMENT_ID = "EXP-BINSTD-ffc4f4"
PARENT_CATALOG_SEED = 2026100327
CATALOG_SEED = 2026100331
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
    "O-STAGE2-COMPLETE",
}
MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}
DELTA = 0.10


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
        pre_path = root / "stage0" / "preregistered-predictions.json"
        if pre_path.is_file():
            pre = json.loads(pre_path.read_text(encoding="utf-8"))
            if float(pre.get("delta", -1)) != DELTA:
                errs.append("frozen delta mismatch")
            if int(pre.get("catalog_seed", -1)) == PARENT_CATALOG_SEED:
                errs.append("parent catalog_seed 2026100327 reused")
            if int(pre.get("catalog_seed", -1)) != CATALOG_SEED:
                errs.append("catalog_seed mismatch vs frozen successor seed")
        if (root / "stage0" / "v-catalog.json").is_file():
            cat = json.loads((root / "stage0" / "v-catalog.json").read_text())
            cell = cat["cells"]["n17_l3"]
            basis = cell["gp_catalog"][0]["basis"]
            F = Field(17, MODULI[17])
            da, db, dok = dim_vv_agree(basis, F)
            na, nb, nok, _ = encode_n_var(F, CURVE_B[17], basis, XR[17])
            if not (dok and nok):
                errs.append("independent twin disagree on stage0 probe")
            g0 = cell["gp_catalog"][0]
            if g0.get("dimVV") != da or g0.get("N_var") != na:
                errs.append("stage0 gp_catalog[0] mismatch vs independent recompute")
            if int(g0.get("g", 0)) in {3, 5, 7, 9, 11, 13, 17, 19, 21, 25, 27, 33}:
                errs.append("parent GP seed used in successor catalog")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"outcome not in set: {outcome!r}")
        ctl_path = root / "stage1" / "control-table.json"
        if ctl_path.is_file():
            ctl = json.loads(ctl_path.read_text())
            if int(ctl.get("catalog_seed", -1)) == PARENT_CATALOG_SEED:
                errs.append("stage1 reused parent catalog_seed")
        panels_path = root / "stage1" / "panels.json"
        if panels_path.is_file():
            panels = json.loads(panels_path.read_text())
            panel = panels.get("n17_l3") or {}
            pairs = panel.get("pairs") or []
            if pairs:
                p0 = pairs[0]
                F = Field(17, MODULI[17])
                da, db, dok = dim_vv_agree(p0["gp_basis"], F)
                na, nb, nok, _ = encode_n_var(F, CURVE_B[17], p0["gp_basis"], XR[17])
                if not (dok and nok):
                    errs.append("stage1 pair0 GP twin disagree")
                if p0.get("gp_dimVV") != da or p0.get("gp_N_var") != na:
                    errs.append("stage1 pair0 GP values mismatch independent twin")
                if abs(int(p0["gp_dimVV"]) - int(p0["rand_dimVV"])) > 1:
                    errs.append("stage1 pair0 violates |Δ dimVV|<=1 match rule")
    elif stage == 2:
        for rel in ("stage2/gp-panels.json", "stage2/null-panels.json"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"outcome not in set: {outcome!r}")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
