#!/usr/bin/env python3
"""EXP-BINSTD-4b846c Stages 0-2: cell-scoped (17,4) + (17,3) escape + Stage-2 null."""
from __future__ import annotations
import argparse, json, math, sys, time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
sys.path.insert(0, str(_IMPL))
from encode_s3 import encode_n_var
from gf2n import Field
from product_space import dim_vv_agree, dim_vv_path_a, f2_rank, geometric_basis, poly_basis, random_basis

EXPERIMENT_ID = "EXP-BINSTD-4b846c"
HYPOTHESIS_ID = "H-BINSTD-07aa73"
APPROVED_BY = "DEC-20261003-7fbcb8"
PREDECESSOR_EXP = "EXP-BINSTD-9b18fc"
PREDECESSOR_EV = "EV-BINSTD-90c856"
PREDECESSOR_EV_PRIOR = "EV-BINSTD-69cb29"
PREDECESSOR_EV_V1 = "EV-BINSTD-a99d47"
FORBIDDEN_CATALOG_SEEDS = (2026100317, 2026100320, 2026100330)
EXP_ROOT = Path(__file__).resolve().parents[1]
MODULI = {17: (1 << 17) | (1 << 3) | 1, 19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1, 23: (1 << 23) | (1 << 5) | 1}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}
SPEARMAN_BAND = 0.70
CATALOG_SEED = 2026100340
BOOTSTRAP_REPS = 200
BOOTSTRAP_SEED = 2026100341
NULL_SEED = 2026100342
NULL_REPS = 200
MIN_CATALOG, MAX_CATALOG = 32, 72
FLOOR_DIMVV, FLOOR_NVAR = 3, 2
PACKAGE_CELLS = [(17, 4)]
DIAGNOSTIC_CELLS = [(17, 3)]
AUTHORIZED_STAGE1_CELLS = PACKAGE_CELLS + DIAGNOSTIC_CELLS
KNOWN_COLLAPSE_DIMVV_17_3 = {5, 6}
GEO_SEEDS = (2,3,4,5,6,7,8,9,11,13,15,17,19,21,23,25,27,29,31,33)

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")

def write_yaml_manifest(path: Path, obj: dict) -> None:
    lines = ["---"]
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            lines.append(f"{k}: {v}")
    write_text(path, "\n".join(lines) + "\n")

def spearman_rho(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    def ranks(vals):
        order = sorted(range(n), key=lambda i: vals[i])
        out = [0.0]*n
        i = 0
        while i < n:
            j = i
            while j+1 < n and vals[order[j+1]] == vals[order[i]]:
                j += 1
            avg = (i+j)/2.0 + 1.0
            for k in range(i, j+1):
                out[order[k]] = avg
            i = j+1
        return out
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx)/n, sum(ry)/n
    num = sum((a-mx)*(b-my) for a,b in zip(rx,ry))
    denx = math.sqrt(sum((a-mx)**2 for a in rx))
    deny = math.sqrt(sum((b-my)**2 for b in ry))
    if denx == 0.0 or deny == 0.0:
        return float("nan")
    return num/(denx*deny)

def bootstrap_ci(xs, ys, reps, seed):
    import numpy as np
    rng = np.random.default_rng(seed)
    n = len(xs)
    rhos = []
    for _ in range(reps):
        idx = rng.integers(0, n, size=n)
        r = spearman_rho([xs[i] for i in idx], [ys[i] for i in idx])
        if r == r:
            rhos.append(r)
    if not rhos:
        return float("nan"), float("nan")
    return float(np.quantile(rhos, 0.025)), float(np.quantile(rhos, 0.975))

def shifted_poly_basis(ell, n, shift):
    out = []
    for i in range(ell):
        e = 0
        for j in range(n):
            if ((i + shift + j) % n) < max(1, n // (ell + 1)):
                e |= 1 << j
        if e == 0:
            e = 1 << ((i + shift) % n)
        out.append(e)
    return out

def sparse_weight_basis(ell, n, positions):
    out = []
    for i, p in enumerate(positions[:ell]):
        e = (1 << (p % n)) | (1 << ((p + 1 + i) % n))
        out.append(e)
    return out

def _field_mul(F, a, b, n):
    return int(F.mul(a, b))

def affine_twist_basis(ell, n, F, g, add):
    out = []; x = g % (1 << n) or 1
    for i in range(ell):
        out.append(((x + add*(i+1)) & ((1<<n)-1)) or (1 << (i % n)))
        x = _field_mul(F, x, g, n)
    return out

def complement_mix_basis(ell, n, F, g):
    mask = (1<<n)-1; out = []; x = g % (1<<n) or 1
    for i in range(ell):
        out.append(x if i % 2 == 0 else (mask ^ x))
        x = _field_mul(F, x, g, n) or (1 << (i % n))
    return out

def multiplicative_translate_basis_fixed(ell, n, F, g, scale):
    out = []; x = g % (1<<n) or 1
    for i in range(ell):
        out.append(_field_mul(F, x, scale, n) or (1 << (i % n)))
        x = _field_mul(F, x, g, n) or (1 << ((i+1) % n))
    return out

def product_rank_boost_basis(ell, n, F, seed_bits):
    out = []
    for i in range(ell):
        block = (seed_bits + i*5) % n
        e = 0
        for k in range(max(2, n // ell)):
            e |= 1 << ((block + k*(i+2)) % n)
        if e == 0:
            e = 1 << ((block + i) % n)
        out.append(e)
    if f2_rank(out, n) < ell:
        out = [1 << ((seed_bits + i) % n) for i in range(ell)]
        for i in range(ell):
            out[i] |= 1 << ((seed_bits + 2*i + 3) % n)
    return out

def _diversity(shapes, F, n, seek_nvar):
    dims, nvars = set(), set()
    for s in shapes:
        dims.add(dim_vv_path_a(s["basis"], F))
        if seek_nvar:
            na, _nb, nok, _det = encode_n_var(F, CURVE_B[n], s["basis"], XR[n])
            if nok:
                nvars.add(na)
    return dims, nvars

def build_catalog(n, ell, seek_floors, recipe):
    import numpy as np
    if CATALOG_SEED in FORBIDDEN_CATALOG_SEEDS:
        raise RuntimeError(f"forbidden prior catalog_seed {CATALOG_SEED}")
    F = Field(n, MODULI[n])
    rng = np.random.default_rng(CATALOG_SEED + 1000*n + ell)
    shapes, seen = [], set()
    def try_add(kind, basis):
        basis = [int(x) for x in basis]
        if len(basis) != ell or f2_rank(basis, n) < ell:
            return False
        key = frozenset(basis)
        if key in seen:
            return False
        seen.add(key); shapes.append({"kind": kind, "basis": basis}); return True
    try_add("poly", poly_basis(ell))
    for g in GEO_SEEDS:
        try_add(f"geo_g{g}", geometric_basis(ell, F, seed_elem=g))
    for shift in range(n):
        try_add(f"shift_s{shift}", shifted_poly_basis(ell, n, shift))
    for g in (3,5,7,11,13,17,19,23):
        for add in (1,3,5,9,17,21,33):
            try_add(f"twist_g{g}_a{add}", affine_twist_basis(ell, n, F, g, add))
    for g in (3,5,7,11,13):
        try_add(f"compmix_g{g}", complement_mix_basis(ell, n, F, g))
    for g in (3,5,7,11):
        for scale in (3,5,7,9,11,13,17):
            try_add(f"mtranslate_g{g}_s{scale}", multiplicative_translate_basis_fixed(ell, n, F, g, scale))
    for offset in range(n):
        try_add(f"sparse_o{offset}", sparse_weight_basis(ell, n, [(offset+k*2)%n for k in range(ell)]))
        try_add(f"sparse3_o{offset}", sparse_weight_basis(ell, n, [(offset+k*3)%n for k in range(ell)]))
    if recipe == "product_rank_escape":
        for seed_bits in range(2*n):
            try_add(f"prank_s{seed_bits}", product_rank_boost_basis(ell, n, F, seed_bits))
    guard = 0
    while len(shapes) < MIN_CATALOG and guard < 800:
        try_add(f"rand_{len(shapes)}", random_basis(ell, n, rng)); guard += 1
    if len(shapes) > MAX_CATALOG:
        shapes = shapes[:MAX_CATALOG]
        seen = {frozenset(s["basis"]) for s in shapes}
    dims, nvars = _diversity(shapes, F, n, seek_nvar=seek_floors)
    notes = {"min_catalog": MIN_CATALOG, "max_catalog": MAX_CATALOG, "seek_floors": seek_floors,
             "recipe": recipe, "dimVV_distinct_after_structured": len(dims),
             "Nvar_distinct_after_structured": len(nvars) if seek_floors else None,
             "not_a_rerun_of_seeds": list(FORBIDDEN_CATALOG_SEEDS),
             "known_collapse_target": sorted(KNOWN_COLLAPSE_DIMVV_17_3) if recipe=="product_rank_escape" else None}
    if seek_floors:
        guard = 0
        while (len(dims) < FLOOR_DIMVV or len(nvars) < FLOOR_NVAR) and len(shapes) < MAX_CATALOG and guard < 2500:
            if recipe == "product_rank_escape" and guard % 3:
                b = product_rank_boost_basis(ell, n, F, int(rng.integers(0, 10000)))
            else:
                b = random_basis(ell, n, rng)
            key = frozenset(int(x) for x in b)
            if key in seen or f2_rank(b, n) < ell:
                guard += 1; continue
            d = dim_vv_path_a(b, F)
            na, _nb, nok, _det = encode_n_var(F, CURVE_B[n], b, XR[n])
            escapes = recipe=="product_rank_escape" and d not in KNOWN_COLLAPSE_DIMVV_17_3 and d not in dims
            expands_dim = d not in dims
            expands_nvar = nok and na not in nvars
            take = escapes or expands_dim or (len(dims) >= FLOOR_DIMVV and expands_nvar) or (len(shapes) < MIN_CATALOG+8 and guard % 5 == 0)
            if take:
                seen.add(key)
                kind = "escape_dim" if escapes else ("rand_dim" if expands_dim else ("rand_nvar" if expands_nvar else "rand_pad"))
                shapes.append({"kind": f"{kind}_{len(shapes)}", "basis": [int(x) for x in b]})
                dims.add(d)
                if nok: nvars.add(na)
            guard += 1
        notes["dimVV_distinct_final_prescreen"] = len(dims)
        notes["Nvar_distinct_final_prescreen"] = len(nvars)
        notes["prescreen_floor_met"] = len(dims) >= FLOOR_DIMVV and len(nvars) >= FLOOR_NVAR
        notes["prescreen_dimVV_floor_met"] = len(dims) >= FLOOR_DIMVV
        notes["prescreen_escape_outside_collapse"] = (len(dims - KNOWN_COLLAPSE_DIMVV_17_3) > 0) if recipe=="product_rank_escape" else None
    out = [{"kind": s["kind"], "basis": [int(x) for x in s["basis"]]} for s in shapes]
    return {"catalog": out, "catalog_size": len(out), "construction_notes": notes,
            "prescreen_distinct_dimVV": sorted(dims) if seek_floors else None,
            "prescreen_distinct_Nvar": sorted(nvars) if seek_floors else None}

def stage0(run_dir: Path) -> dict:
    t0 = time.time(); cells = {}; twin_ok = True
    stage1_keys = {f"n{n}_l{ell}" for n,ell in AUTHORIZED_STAGE1_CELLS}
    package_keys = {f"n{n}_l{ell}" for n,ell in PACKAGE_CELLS}
    for n in (17,19,23):
        for ell in (3,4):
            key = f"n{n}_l{ell}"
            recipe = "product_rank_escape" if key=="n17_l3" else ("cell_scoped_diversity" if key in stage1_keys else "background_diversity")
            built = build_catalog(n, ell, seek_floors=(key in stage1_keys), recipe=recipe)
            cat = built["catalog"]; F = Field(n, MODULI[n])
            if cat:
                da, db, dok = dim_vv_agree(cat[0]["basis"], F)
                na, nb, nok, _ = encode_n_var(F, CURVE_B[n], cat[0]["basis"], XR[n])
                probe_ok = dok and nok; twin_ok = twin_ok and probe_ok
            else:
                probe_ok = False; twin_ok = False
            cells[key] = {"n": n, "ell": ell, "catalog_size": len(cat), "catalog": cat,
                "construction_notes": built["construction_notes"],
                "prescreen_distinct_dimVV": built["prescreen_distinct_dimVV"],
                "prescreen_distinct_Nvar": built["prescreen_distinct_Nvar"],
                "probe_twin_ok": probe_ok,
                "role": "package_cell" if key in package_keys else ("diagnostic_escape" if key=="n17_l3" else "background")}
    pred = {
        "experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "approved_by": APPROVED_BY,
        "predecessor_evidence_id": PREDECESSOR_EV, "predecessor_evidence_id_prior": PREDECESSOR_EV_PRIOR,
        "predecessor_evidence_id_v1": PREDECESSOR_EV_V1, "predecessor_experiment_id": PREDECESSOR_EXP,
        "not_a_rerun_of": [PREDECESSOR_EXP, "EXP-BINSTD-16ee30", "EXP-BINSTD-5b2fd0"],
        "forbidden_catalog_seeds": list(FORBIDDEN_CATALOG_SEEDS),
        "catalog_seed": CATALOG_SEED, "bootstrap_seed": BOOTSTRAP_SEED, "null_seed": NULL_SEED,
        "bootstrap_reps": BOOTSTRAP_REPS, "null_reps": NULL_REPS, "spearman_band": SPEARMAN_BAND,
        "min_catalog": MIN_CATALOG, "max_catalog": MAX_CATALOG,
        "package_scope": {"cells": [{"n":17,"ell":4}], "note": "Cell-scoped to (17,4) after EV-90c856/69cb29 collapses."},
        "admission_gates": {"distinct_dimVV_min": FLOOR_DIMVV, "distinct_Nvar_min": FLOOR_NVAR, "package_cells_only": True},
        "diagnostic_17_3_escape": {"cell": {"n":17,"ell":3}, "recipe": "product_rank_escape",
            "known_collapse_dimVV": sorted(KNOWN_COLLAPSE_DIMVV_17_3),
            "cites": [PREDECESSOR_EV, PREDECESSOR_EV_PRIOR, "DEC-20261003-9f58a7"]},
        "cell_scoped_17_4_heur": {"cell": {"n":17,"ell":4}, "heuristic_id": "HEUR-BINSTD-4b846c-H1-CELL-17-4", "authorized": True,
            "cites": [PREDECESSOR_EV, PREDECESSOR_EV_PRIOR]},
        "stage2_null": {"authorized": True, "cell": {"n":17,"ell":4},
            "arms": ["permutation_dimVV_null", "random_boolean_matched_catalog"]},
        "authorized_stage1_cells": [{"n":n,"ell":ell} for n,ell in AUTHORIZED_STAGE1_CELLS],
        "moduli": {str(k): hex(v) for k,v in MODULI.items()},
        "curve_B": {str(k): v for k,v in CURVE_B.items()},
        "xR": {str(k): hex(v) for k,v in XR.items()},
        "encoder_pin": {"descend": "encode_s3.descend_s3",
            "dimVV_twins": ["product_space.dim_vv_path_a","product_space.dim_vv_path_b"],
            "n_var_twins": ["encode_s3._rank_and_pivot_vars_a","encode_s3._rank_and_pivot_vars_b"]},
        "prediction": "CELL-SCOPED (17,4) Spearman>=0.70 after floors; diagnostic (17,3) escape/boundary; Stage-2 null when authorized.",
        "amazon_bedrock": "NOT_USED",
    }
    write_json(EXP_ROOT/"stage0"/"preregistered-predictions.json", pred)
    write_json(EXP_ROOT/"stage0"/"v-catalog.json", {"cells": cells, "twin_ok": twin_ok})
    outcome_hint = "O-STAGE0-OK" if twin_ok else "O-ARTIFACT"
    raw = {"experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PREDECESSOR_EXP, "predecessor_evidence_id": PREDECESSOR_EV,
        "predecessor_evidence_id_prior": PREDECESSOR_EV_PRIOR, "stage": 0,
        "status": "completed" if twin_ok else "artifact", "outcome_hint": outcome_hint, "twin_ok": twin_ok,
        "catalog_seed": CATALOG_SEED, "bootstrap_seed": BOOTSTRAP_SEED, "null_seed": NULL_SEED,
        "package_cells": [{"n":n,"ell":ell} for n,ell in PACKAGE_CELLS],
        "diagnostic_cells": [{"n":n,"ell":ell} for n,ell in DIAGNOSTIC_CELLS],
        "cell_catalog_sizes": {k: v["catalog_size"] for k,v in cells.items()},
        "stage1_prescreen": {k: {"prescreen_distinct_dimVV": cells[k]["prescreen_distinct_dimVV"],
            "prescreen_distinct_Nvar": cells[k]["prescreen_distinct_Nvar"],
            "construction_notes": cells[k]["construction_notes"], "role": cells[k]["role"]} for k in stage1_keys},
        "freeze": {"preregistered_predictions": "stage0/preregistered-predictions.json", "v_catalog": "stage0/v-catalog.json"},
        "wall_clock_seconds": time.time()-t0, "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "not_a_rerun_of": [PREDECESSOR_EXP, "EXP-BINSTD-16ee30", "EXP-BINSTD-5b2fd0"]}
    write_json(run_dir/"raw-result.json", raw)
    write_yaml_manifest(run_dir/"manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 0, "status": raw["status"],
        "twin_ok": twin_ok, "outcome_hint": outcome_hint, "approved_by": APPROVED_BY, "amazon_bedrock": "NOT_USED"})
    return raw

def measure_cell(n, ell, catalog):
    F = Field(n, MODULI[n]); rows = []; twin_fail = False
    for entry in catalog:
        basis = entry["basis"]
        da, db, dok = dim_vv_agree(basis, F)
        na, nb, nok, det = encode_n_var(F, CURVE_B[n], basis, XR[n])
        if not (dok and nok): twin_fail = True
        rows.append({"kind": entry["kind"], "basis": basis, "dimVV_a": da, "dimVV_b": db, "dimVV": da,
            "Nvar_a": na, "Nvar_b": nb, "N_var": na, "twin_ok": dok and nok,
            "encode_details": {"lin_rank_a": det.get("lin_rank_a"), "lin_rank_b": det.get("lin_rank_b"), "nv0": det.get("nv0")}})
    xs = [float(r["dimVV"]) for r in rows]; ys = [float(r["N_var"]) for r in rows]
    distinct_dim, distinct_nvar = len(set(xs)), len(set(ys))
    floors_met = distinct_dim >= FLOOR_DIMVV and distinct_nvar >= FLOOR_NVAR
    rho = spearman_rho(xs, ys) if floors_met else float("nan")
    lo, hi = bootstrap_ci(xs, ys, BOOTSTRAP_REPS, BOOTSTRAP_SEED + n*10 + ell) if floors_met else (float("nan"), float("nan"))
    return {"n": n, "ell": ell, "catalog_size": len(rows), "rows": rows, "admission_floors_met": floors_met,
        "spearman_rho": rho, "spearman_rho_disclosed_pre_admission": spearman_rho(xs, ys),
        "bootstrap_ci_95": [lo, hi], "distinct_dimVV": distinct_dim, "distinct_Nvar": distinct_nvar,
        "distinct_dimVV_values": sorted(set(int(x) for x in xs)), "twin_fail": twin_fail, "band": SPEARMAN_BAND,
        "in_band": floors_met and (rho==rho) and rho >= SPEARMAN_BAND,
        "band_reading_authorized": floors_met and not twin_fail,
        "ci_entirely_below_band": floors_met and lo==lo and hi==hi and hi < SPEARMAN_BAND}

def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    cat_path, pre_path = EXP_ROOT/"stage0"/"v-catalog.json", EXP_ROOT/"stage0"/"preregistered-predictions.json"
    if not cat_path.is_file() or not pre_path.is_file():
        raw = {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment", "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze files", "amazon_bedrock": "NOT_USED", "claims": {"break": False, "exponent_move": False}}
        write_json(run_dir/"raw-result.json", raw)
        write_yaml_manifest(run_dir/"manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment"})
        return raw
    pred = json.loads(pre_path.read_text(encoding="utf-8"))
    if pred.get("catalog_seed") in FORBIDDEN_CATALOG_SEEDS:
        raw = {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "invalid", "outcome": "O-ARTIFACT",
            "reason": "forbidden prior catalog_seed in freeze", "amazon_bedrock": "NOT_USED", "claims": {"break": False, "exponent_move": False}}
        write_json(run_dir/"raw-result.json", raw)
        write_yaml_manifest(run_dir/"manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "invalid"})
        return raw
    catalog_doc = json.loads(cat_path.read_text(encoding="utf-8"))
    panels = {}; any_twin_fail = False
    for n, ell in AUTHORIZED_STAGE1_CELLS:
        key = f"n{n}_l{ell}"
        panel = measure_cell(n, ell, catalog_doc["cells"][key]["catalog"])
        panel["role"] = "package" if (n, ell) in PACKAGE_CELLS else "diagnostic"
        panels[key] = panel; any_twin_fail = any_twin_fail or panel["twin_fail"]
    p173 = panels.get("n17_l3") or {}; dims173 = set(p173.get("distinct_dimVV_values") or [])
    if p173.get("twin_fail"):
        diagnostic_17_3 = "O-ARTIFACT"
    elif p173.get("admission_floors_met"):
        diagnostic_17_3 = "O-ESCAPE-OK-17-3"
    else:
        diagnostic_17_3 = "O-INSTRUMENT-BOUNDARY-17-3"
    p174 = panels.get("n17_l4") or {}
    if any_twin_fail or p174.get("twin_fail"):
        outcome = "O-ARTIFACT"
    elif not p174.get("admission_floors_met"):
        outcome = "O-INCONCLUSIVE"
    elif p174.get("in_band"):
        outcome = "O-SUPPORT"
    else:
        outcome = "O-FAIL-BAND"
    if p174.get("twin_fail"):
        cell_17_4 = "O-ARTIFACT"
    elif not p174.get("admission_floors_met"):
        cell_17_4 = "O-CELL-INCONCLUSIVE-17-4"
    elif p174.get("ci_entirely_below_band"):
        cell_17_4 = "O-CELL-FAIL-BAND-17-4"
    elif p174.get("in_band"):
        cell_17_4 = "O-CELL-IN-BAND-17-4"
    else:
        cell_17_4 = "O-CELL-OUT-OF-BAND-UNCLEAR-CI-17-4"
    write_json(EXP_ROOT/"stage1"/"panels.json", panels)
    control = {"twin_required": True, "any_twin_fail": any_twin_fail, "spearman_band": SPEARMAN_BAND,
        "package_scope": "cell_scoped_17_4_only",
        "admission_gates": {"distinct_dimVV_min": FLOOR_DIMVV, "distinct_Nvar_min": FLOOR_NVAR, "package_cells_only": True},
        "diagnostic_17_3_outcome": diagnostic_17_3, "cell_scoped_17_4_outcome": cell_17_4,
        "predecessor_evidence_id": PREDECESSOR_EV, "predecessor_evidence_id_prior": PREDECESSOR_EV_PRIOR,
        "stage2_authorized_if": bool(p174.get("admission_floors_met") and not p174.get("twin_fail")),
        "null_note": "Stage 2 null AUTHORIZED when (17,4) floors met."}
    write_json(EXP_ROOT/"stage1"/"control-table.json", control)
    results = (f"# RESULTS — {EXPERIMENT_ID}\n\nHypothesis: {HYPOTHESIS_ID}\nApproved by: {APPROVED_BY}\n"
        f"Predecessor: {PREDECESSOR_EXP} / {PREDECESSOR_EV} (also cites {PREDECESSOR_EV_PRIOR}, {PREDECESSOR_EV_V1})\n"
        f"Package outcome (cell-scoped (17,4)): **{outcome}**\nDiagnostic (17,3) outcome: **{diagnostic_17_3}**\n"
        f"Cell (17,4) continuity label: **{cell_17_4}**\n\nPackage cells: {PACKAGE_CELLS}\nDiagnostic cells: {DIAGNOSTIC_CELLS}\n\n"
        f"Admission floors (package cells only): >={FLOOR_DIMVV} distinct dimVV, >={FLOOR_NVAR} distinct N_var\n"
        f"Spearman band: >= {SPEARMAN_BAND}\nStage-2 null authorized when (17,4) floors met.\n\n## Panels\n\n")
    for key, p in panels.items():
        results += (f"- `{key}` ({p.get('role')}): floors_met={p['admission_floors_met']}, rho={p['spearman_rho']!r}, "
            f"CI95={p['bootstrap_ci_95']!r}, distinct_dimVV={p['distinct_dimVV']}, dimVV_values={p.get('distinct_dimVV_values')}, "
            f"distinct_Nvar={p['distinct_Nvar']}, in_band={p['in_band']}, twin_fail={p['twin_fail']}, "
            f"band_reading_authorized={p['band_reading_authorized']}, ci_entirely_below_band={p['ci_entirely_below_band']}\n")
    results += ("\n## Claims\n\n- break: false\n- exponent_move: false\n- amazon_bedrock: NOT_USED\n- No n>=131 transfer.\n"
        f"- Not a re-run of {PREDECESSOR_EXP}, EXP-BINSTD-16ee30, or EXP-BINSTD-5b2fd0 v1.\n"
        f"- catalog_seed={CATALOG_SEED} (forbidden priors: {list(FORBIDDEN_CATALOG_SEEDS)}).\n"
        "- Stage-2 null: see stage2/ after stage=2 trial (if authorized).\n")
    write_text(EXP_ROOT/"RESULTS.md", results)
    raw = {"experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PREDECESSOR_EXP, "predecessor_evidence_id": PREDECESSOR_EV,
        "predecessor_evidence_id_prior": PREDECESSOR_EV_PRIOR, "stage": 1, "status": "completed",
        "outcome": outcome, "diagnostic_17_3_outcome": diagnostic_17_3, "cell_scoped_17_4_outcome": cell_17_4,
        "stage2_authorized": bool(p174.get("admission_floors_met") and not p174.get("twin_fail")),
        "panels_summary": {k: {"role": v.get("role"), "admission_floors_met": v["admission_floors_met"],
            "spearman_rho": v["spearman_rho"], "bootstrap_ci_95": v["bootstrap_ci_95"], "in_band": v["in_band"],
            "distinct_dimVV": v["distinct_dimVV"], "distinct_dimVV_values": v.get("distinct_dimVV_values"),
            "distinct_Nvar": v["distinct_Nvar"], "twin_fail": v["twin_fail"],
            "band_reading_authorized": v["band_reading_authorized"], "ci_entirely_below_band": v["ci_entirely_below_band"]}
            for k,v in panels.items()},
        "wall_clock_seconds": time.time()-t0, "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "not_a_rerun_of": [PREDECESSOR_EXP, "EXP-BINSTD-16ee30", "EXP-BINSTD-5b2fd0"], "catalog_seed": CATALOG_SEED}
    write_json(run_dir/"raw-result.json", raw)
    write_yaml_manifest(run_dir/"manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "completed",
        "outcome": outcome, "diagnostic_17_3_outcome": diagnostic_17_3, "cell_scoped_17_4_outcome": cell_17_4,
        "approved_by": APPROVED_BY, "amazon_bedrock": "NOT_USED"})
    return raw

def stage2(run_dir: Path) -> dict:
    import numpy as np
    t0 = time.time()
    panels_path, ctl_path, pre_path = EXP_ROOT/"stage1"/"panels.json", EXP_ROOT/"stage1"/"control-table.json", EXP_ROOT/"stage0"/"preregistered-predictions.json"
    if not panels_path.is_file() or not ctl_path.is_file() or not pre_path.is_file():
        raw = {"experiment_id": EXPERIMENT_ID, "stage": 2, "status": "impediment", "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0/1 artifacts for null", "amazon_bedrock": "NOT_USED", "claims": {"break": False, "exponent_move": False}}
        write_json(run_dir/"raw-result.json", raw)
        write_yaml_manifest(run_dir/"manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 2, "status": "impediment"})
        return raw
    panels = json.loads(panels_path.read_text(encoding="utf-8"))
    ctl = json.loads(ctl_path.read_text(encoding="utf-8"))
    p174 = panels.get("n17_l4") or {}
    if not p174.get("admission_floors_met") or p174.get("twin_fail"):
        raw = {"experiment_id": EXPERIMENT_ID, "stage": 2, "status": "impediment", "outcome": "O-IMPEDIMENT",
            "reason": "Stage-2 gate failed: (17,4) floors unmet or twin_fail",
            "stage1_cell_scoped_17_4_outcome": ctl.get("cell_scoped_17_4_outcome"),
            "amazon_bedrock": "NOT_USED", "claims": {"break": False, "exponent_move": False}}
        write_json(run_dir/"raw-result.json", raw)
        write_yaml_manifest(run_dir/"manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 2, "status": "impediment"})
        return raw
    rows = p174["rows"]; xs = [float(r["dimVV"]) for r in rows]; ys = [float(r["N_var"]) for r in rows]
    observed_rho = spearman_rho(xs, ys)
    observed_ci = bootstrap_ci(xs, ys, BOOTSTRAP_REPS, BOOTSTRAP_SEED + 174)
    rng = np.random.default_rng(NULL_SEED)
    perm_rhos = []
    for _ in range(NULL_REPS):
        shuffled = list(xs); rng.shuffle(shuffled)
        r = spearman_rho(shuffled, ys)
        if r == r: perm_rhos.append(float(r))
    perm_mean = float(np.mean(perm_rhos)) if perm_rhos else float("nan")
    perm_hi = float(np.quantile(perm_rhos, 0.975)) if perm_rhos else float("nan")
    perm_reaches_band = bool(perm_rhos) and perm_hi >= SPEARMAN_BAND
    support = sorted(set(int(x) for x in xs)) or [0]
    rb_rhos = []
    for _ in range(NULL_REPS):
        fake = [float(support[int(rng.integers(0, len(support)))]) for _ in xs]
        r = spearman_rho(fake, ys)
        if r == r: rb_rhos.append(float(r))
    rb_mean = float(np.mean(rb_rhos)) if rb_rhos else float("nan")
    rb_hi = float(np.quantile(rb_rhos, 0.975)) if rb_rhos else float("nan")
    rb_reaches_band = bool(rb_rhos) and rb_hi >= SPEARMAN_BAND
    observed_below = observed_ci[1]==observed_ci[1] and observed_ci[1] < SPEARMAN_BAND
    if observed_below and (not perm_reaches_band) and (not rb_reaches_band):
        null_outcome = "O-NULL-ALSO-BELOW-BAND"
    elif observed_below and (perm_reaches_band or rb_reaches_band):
        null_outcome = "O-STRUCTURE-SPECIFIC-FAIL-BAND"
    elif (not observed_below) and (perm_reaches_band or rb_reaches_band):
        null_outcome = "O-NULL-NONDISCRIMINATING"
    else:
        null_outcome = "O-NULL-INCONCLUSIVE"
    doc = {"cell": {"n":17,"ell":4},
        "observed": {"spearman_rho": observed_rho, "bootstrap_ci_95": list(observed_ci),
            "ci_entirely_below_band": observed_below, "band": SPEARMAN_BAND},
        "permutation_dimVV_null": {"reps": NULL_REPS, "seed": NULL_SEED, "mean_rho": perm_mean,
            "ci95_hi": perm_hi, "reaches_band": perm_reaches_band},
        "random_boolean_matched_catalog": {"reps": NULL_REPS, "seed": NULL_SEED+1, "support": support,
            "mean_rho": rb_mean, "ci95_hi": rb_hi, "reaches_band": rb_reaches_band,
            "definition": "Independent draws from observed dimVV support; no Weil product-space structure."},
        "null_outcome": null_outcome, "stage1_cell_scoped_17_4_outcome": ctl.get("cell_scoped_17_4_outcome"),
        "amazon_bedrock": "NOT_USED"}
    write_json(EXP_ROOT/"stage2"/"null-results.json", doc)
    results_path = EXP_ROOT/"RESULTS.md"
    if results_path.is_file():
        prev = results_path.read_text(encoding="utf-8")
        if "## Stage-2 null" not in prev:
            results_path.unlink()
            write_text(results_path, prev + "\n## Stage-2 null\n\n" + f"- null_outcome: **{null_outcome}**\n"
                + f"- observed rho={observed_rho!r} CI95={list(observed_ci)!r}\n"
                + f"- permutation mean_rho={perm_mean!r} ci95_hi={perm_hi!r} reaches_band={perm_reaches_band}\n"
                + f"- random_boolean mean_rho={rb_mean!r} ci95_hi={rb_hi!r} reaches_band={rb_reaches_band}\n"
                + "- artifact: stage2/null-results.json\n")
    raw = {"experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "approved_by": APPROVED_BY,
        "predecessor_evidence_id": PREDECESSOR_EV, "stage": 2, "status": "completed", "outcome": null_outcome,
        "null_summary": {"observed_rho": observed_rho, "observed_ci95": list(observed_ci),
            "permutation_mean_rho": perm_mean, "permutation_reaches_band": perm_reaches_band,
            "random_boolean_mean_rho": rb_mean, "random_boolean_reaches_band": rb_reaches_band},
        "wall_clock_seconds": time.time()-t0, "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "not_a_rerun_of": [PREDECESSOR_EXP, "EXP-BINSTD-16ee30", "EXP-BINSTD-5b2fd0"]}
    write_json(run_dir/"raw-result.json", raw)
    write_yaml_manifest(run_dir/"manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 2, "status": "completed",
        "outcome": null_outcome, "approved_by": APPROVED_BY, "amazon_bedrock": "NOT_USED"})
    return raw

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0,1,2])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir); run_dir.mkdir(parents=True, exist_ok=True)
    if not Path(args.trial_plan).is_file():
        print(f"missing trial plan: {args.trial_plan}", file=sys.stderr); return 2
    {0: stage0, 1: stage1, 2: stage2}[args.stage](run_dir)
    print(json.dumps({"ok": True, "stage": args.stage, "run_dir": str(run_dir)})); return 0

if __name__ == "__main__":
    raise SystemExit(main())
