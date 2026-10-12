#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-16ee30 run artifacts."""
from __future__ import annotations
import json, sys
from pathlib import Path
_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))
from encode_s3 import encode_n_var
from gf2n import Field
from product_space import dim_vv_agree

EXPERIMENT_ID = "EXP-BINSTD-16ee30"
OUTCOMES = {"O-SUPPORT","O-FAIL-BAND","O-INCONCLUSIVE","O-ARTIFACT","O-IMPEDIMENT","O-STAGE0-OK"}
MODULI = {17:(1<<17)|(1<<3)|1, 19:(1<<19)|(1<<5)|(1<<2)|(1<<1)|1, 23:(1<<23)|(1<<5)|1}
CURVE_B = {17:1,19:1,23:1}
XR = {17:0x1A3F,19:0x2B41,23:0x55}
FLOOR_DIMVV, FLOOR_NVAR = 3, 2

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr); return 2
    run_dir = Path(sys.argv[1])
    raw_path, man_path = run_dir/"raw-result.json", run_dir/"manifest.yaml"
    errs = []
    if not raw_path.is_file() or raw_path.stat().st_size == 0: errs.append("missing/empty raw-result.json")
    if not man_path.is_file() or man_path.stat().st_size == 0: errs.append("missing/empty manifest.yaml")
    if errs:
        print("FAIL:", *errs, sep="\n  "); return 1
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID: errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED","NOT SELECTED"): errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move"): errs.append("forbidden break/exponent claim present")
    stage = raw.get("stage"); root = Path(__file__).resolve().parents[1]
    if stage == 0:
        for rel in ("stage0/preregistered-predictions.json","stage0/v-catalog.json"):
            if not (root/rel).is_file(): errs.append(f"missing freeze file {rel}")
        if (root/"stage0"/"v-catalog.json").is_file():
            cat = json.loads((root/"stage0"/"v-catalog.json").read_text())
            cell = cat["cells"]["n17_l3"]; basis = cell["catalog"][0]["basis"]
            F = Field(17, MODULI[17])
            da, db, dok = dim_vv_agree(basis, F)
            na, nb, nok, _ = encode_n_var(F, CURVE_B[17], basis, XR[17])
            if not (dok and nok): errs.append("stage0 probe twin recompute failed")
            if len(cell["catalog"]) < 24: errs.append(f"catalog_size {len(cell['catalog'])} < 24")
        pre = root/"stage0"/"preregistered-predictions.json"
        if pre.is_file():
            pred = json.loads(pre.read_text())
            if pred.get("catalog_seed") == 2026100317: errs.append("v1 catalog_seed reused; successor must use new seed")
            gates = pred.get("admission_gates") or {}
            if gates.get("distinct_dimVV_min") != FLOOR_DIMVV: errs.append("admission dimVV floor missing/wrong")
            if gates.get("distinct_Nvar_min") != FLOOR_NVAR: errs.append("admission N_var floor missing/wrong")
    elif stage == 1:
        for rel in ("stage1/panels.json","stage1/control-table.json","RESULTS.md"):
            if not (root/rel).is_file(): errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES: errs.append(f"bad outcome {outcome!r}")
        if (root/"stage1"/"panels.json").is_file():
            panels = json.loads((root/"stage1"/"panels.json").read_text())
            cell = panels.get("n17_l3") or {}; rows = cell.get("rows") or []
            if rows:
                basis = rows[0]["basis"]; F = Field(17, MODULI[17])
                da, db, dok = dim_vv_agree(basis, F)
                na, nb, nok, _ = encode_n_var(F, CURVE_B[17], basis, XR[17])
                if not (dok and nok): errs.append("stage1 row0 twin recompute failed")
            if outcome in ("O-SUPPORT","O-FAIL-BAND"):
                for k,p in panels.items():
                    if p.get("distinct_dimVV",0) < FLOOR_DIMVV or p.get("distinct_Nvar",0) < FLOOR_NVAR:
                        errs.append(f"{k}: band outcome without admission floors")
                    if not p.get("band_reading_authorized", False):
                        errs.append(f"{k}: band outcome without band_reading_authorized")
    if errs:
        print("FAIL:", *errs, sep="\n  "); return 1
    print("OK"); return 0

if __name__ == "__main__":
    raise SystemExit(main())
