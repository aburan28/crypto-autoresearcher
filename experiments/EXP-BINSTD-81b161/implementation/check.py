#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-81b161 run artifacts."""
from __future__ import annotations
import json, sys
from pathlib import Path
_IMPL = Path(__file__).resolve().parent
sys.path.insert(0, str(_IMPL))
from encode_s3 import encode_n_var
from gf2n import Field
from product_space import dim_vv_agree

EXPERIMENT_ID = "EXP-BINSTD-81b161"
STAGE0 = {"O-STAGE0-OK","O-ARTIFACT"}
STAGE1 = {"O-STAGE1-FLOORS-MET","O-INCONCLUSIVE","O-ARTIFACT","O-IMPEDIMENT"}
DIAG_173 = {"O-ESCAPE-OK-17-3","O-INSTRUMENT-BOUNDARY-17-3","O-ARTIFACT"}
NULL_OUTCOMES = {"O-NULL-REACHES-LEGACY-BAND","O-NULL-CEILING-BELOW-LEGACY","O-NULL-INCONCLUSIVE","O-IMPEDIMENT"}
MODULI = {17:(1<<17)|(1<<3)|1,19:(1<<19)|(1<<5)|(1<<2)|(1<<1)|1,23:(1<<23)|(1<<5)|1}
CURVE_B={17:1,19:1,23:1}; XR={17:0x1A3F,19:0x2B41,23:0x55}
FLOOR_DIMVV, FLOOR_NVAR = 5, 4
FORBIDDEN_CATALOG_SEEDS = {2026100317,2026100320,2026100330,2026100340}
REQUIRED_CATALOG_SEED = 2026100350
LEGACY_BAND = 0.70

def main() -> int:
    if len(sys.argv)!=2:
        print("usage: check.py <run_dir>", file=sys.stderr); return 2
    run_dir = Path(sys.argv[1])
    raw_path, man_path = run_dir/"raw-result.json", run_dir/"manifest.yaml"
    errs=[]
    if not raw_path.is_file() or raw_path.stat().st_size==0: errs.append("missing/empty raw-result.json")
    if not man_path.is_file() or man_path.stat().st_size==0: errs.append("missing/empty manifest.yaml")
    if errs:
        print("FAIL:", *errs, sep="\n  "); return 1
    raw=json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id")!=EXPERIMENT_ID: errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED","NOT SELECTED"): errs.append("Bedrock marker missing/invalid")
    claims=raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move"): errs.append("forbidden break/exponent claim present")
    stage=raw.get("stage"); root=Path(__file__).resolve().parents[1]
    if stage==0:
        for rel in ("stage0/preregistered-predictions.json","stage0/v-catalog.json"):
            if not (root/rel).is_file(): errs.append(f"missing freeze file {rel}")
        if (root/"stage0"/"v-catalog.json").is_file():
            cat=json.loads((root/"stage0"/"v-catalog.json").read_text())
            for key in ("n17_l4","n17_l3"):
                if len(cat["cells"][key]["catalog"])<48: errs.append(f"{key} catalog_size < 48")
            basis=cat["cells"]["n17_l4"]["catalog"][0]["basis"]
            F=Field(17,MODULI[17])
            da,db,dok=dim_vv_agree(basis,F)
            na,nb,nok,_=encode_n_var(F,CURVE_B[17],basis,XR[17])
            if not (dok and nok): errs.append("stage0 probe twin recompute failed on n17_l4")
        pre=root/"stage0"/"preregistered-predictions.json"
        if pre.is_file():
            pred=json.loads(pre.read_text()); seed=pred.get("catalog_seed")
            if seed in FORBIDDEN_CATALOG_SEEDS: errs.append("prior catalog_seed reused")
            if seed!=REQUIRED_CATALOG_SEED: errs.append(f"catalog_seed {seed} != required {REQUIRED_CATALOG_SEED}")
            cells=(pred.get("package_scope") or {}).get("cells") or []
            if cells!=[{"n":17,"ell":4}]: errs.append("package_scope must be cell-scoped to (17,4) only")
            if not (pred.get("stage2_null") or {}).get("authorized"): errs.append("stage2_null not authorized in freeze")
            if pred.get("legacy_spearman_band")!=LEGACY_BAND: errs.append("legacy band not frozen at 0.70")
            gates=pred.get("admission_gates") or {}
            if gates.get("distinct_dimVV_min")!=FLOOR_DIMVV or gates.get("distinct_Nvar_min")!=FLOOR_NVAR:
                errs.append("admission floors must be dimVV>=5 and Nvar>=4")
            if (pred.get("legacy_band_role") or "") != "null_reachability_target_not_weil_uniqueness":
                errs.append("legacy_band_role must declare not-Weil-uniqueness")
            if raw.get("outcome_hint") not in STAGE0: errs.append(f"bad stage0 outcome_hint {raw.get('outcome_hint')!r}")
    elif stage==1:
        for rel in ("stage1/panels.json","stage1/control-table.json","RESULTS.md"):
            if not (root/rel).is_file(): errs.append(f"missing {rel}")
        outcome=raw.get("outcome")
        if outcome not in STAGE1: errs.append(f"bad outcome {outcome!r}")
        diag=raw.get("diagnostic_17_3_outcome")
        if diag not in DIAG_173: errs.append(f"bad diagnostic_17_3_outcome {diag!r}")
        if outcome in ("O-FAIL-BAND","O-SUPPORT"):
            errs.append("package must not emit Weil uniqueness band labels")
        if (root/"stage1"/"panels.json").is_file():
            panels=json.loads((root/"stage1"/"panels.json").read_text())
            p174=panels.get("n17_l4") or {}; rows=p174.get("rows") or []
            if rows:
                basis=rows[0]["basis"]; F=Field(17,MODULI[17])
                da,db,dok=dim_vv_agree(basis,F)
                na,nb,nok,_=encode_n_var(F,CURVE_B[17],basis,XR[17])
                if not (dok and nok): errs.append("stage1 n17_l4 row0 twin recompute failed")
            if outcome=="O-STAGE1-FLOORS-MET":
                if p174.get("distinct_dimVV",0)<FLOOR_DIMVV or p174.get("distinct_Nvar",0)<FLOOR_NVAR:
                    errs.append("O-STAGE1-FLOORS-MET without enriched admission floors")
            if outcome=="O-INCONCLUSIVE":
                if p174.get("admission_floors_met"):
                    errs.append("O-INCONCLUSIVE while (17,4) floors met")
    elif stage==2:
        if not (root/"stage2"/"null-results.json").is_file() and raw.get("outcome")!="O-IMPEDIMENT":
            errs.append("missing stage2/null-results.json")
        outcome=raw.get("outcome")
        if outcome not in NULL_OUTCOMES: errs.append(f"bad null outcome {outcome!r}")
        if (root/"stage2"/"null-results.json").is_file():
            doc=json.loads((root/"stage2"/"null-results.json").read_text())
            if doc.get("null_outcome")!=outcome and outcome!="O-IMPEDIMENT":
                errs.append("null-results null_outcome mismatch vs raw")
            perm=doc.get("permutation_dimVV_null") or {}
            rb=doc.get("random_boolean_matched_catalog") or {}
            reaches = bool(perm.get("reaches_legacy_band") or rb.get("reaches_legacy_band"))
            if outcome=="O-NULL-REACHES-LEGACY-BAND" and not reaches:
                errs.append("O-NULL-REACHES-LEGACY-BAND without a null arm reaching 0.70")
            if outcome=="O-NULL-CEILING-BELOW-LEGACY" and reaches:
                errs.append("O-NULL-CEILING-BELOW-LEGACY while a null arm reaches 0.70")
    if errs:
        print("FAIL:", *errs, sep="\n  "); return 1
    print("OK"); return 0

if __name__=="__main__":
    raise SystemExit(main())
