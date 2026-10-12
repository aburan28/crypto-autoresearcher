#!/usr/bin/env python3
"""EXP-BINSTD-16ee30 Stages 0-1 launcher (catalog-expansion successor).

Successor to EXP-BINSTD-5b2fd0 after EV-BINSTD-a99d47 / DEC-20261003-f82374
(O-INCONCLUSIVE: distinct-value floors). Does NOT re-run the frozen v1 catalog.

Stage 0: Diversity-seeking V catalog (>=24 shapes, <=48); freeze band 0.70,
         new seeds, encoder pin; twin probe; Stage-1 cells seek floors.
Stage 1: n=17, ell in {3,4}; twin meters; ADMISSION GATE before Spearman band.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import encode_n_var  # noqa: E402
from gf2n import Field  # noqa: E402
from product_space import (  # noqa: E402
    dim_vv_agree,
    dim_vv_path_a,
    f2_rank,
    geometric_basis,
    poly_basis,
    random_basis,
)

EXPERIMENT_ID = "EXP-BINSTD-16ee30"
HYPOTHESIS_ID = "H-BINSTD-7cbce1"
APPROVED_BY = "DEC-20261003-928974"
PREDECESSOR_EXP = "EXP-BINSTD-5b2fd0"
PREDECESSOR_EV = "EV-BINSTD-a99d47"
EXP_ROOT = Path(__file__).resolve().parents[1]

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}

SPEARMAN_BAND = 0.70
CATALOG_SEED = 2026100320
BOOTSTRAP_REPS = 200
BOOTSTRAP_SEED = 2026100321
MIN_CATALOG = 24
MAX_CATALOG = 48
FLOOR_DIMVV = 3
FLOOR_NVAR = 2
AUTHORIZED_STAGE1_CELLS = [(17, 3), (17, 4)]
GEO_SEEDS = (2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17, 19, 21, 23, 25)


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
    lines = []
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            s = str(v).replace("\n", " ")
            lines.append(f'{k}: "{s}"')
    write_text(path, "\n".join(lines) + "\n")


def spearman_rho(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")

    def ranks(vals: list[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: vals[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    deny = math.sqrt(sum((b - my) ** 2 for b in ry))
    if denx == 0.0 or deny == 0.0:
        return float("nan")
    return num / (denx * deny)


def bootstrap_ci(xs: list[float], ys: list[float], reps: int, seed: int) -> tuple[float, float]:
    import random

    rng = random.Random(seed)
    n = len(xs)
    rhos = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        rhos.append(spearman_rho([xs[i] for i in idx], [ys[i] for i in idx]))
    rhos = [r for r in rhos if r == r]
    if not rhos:
        return float("nan"), float("nan")
    rhos.sort()
    lo = rhos[int(0.025 * (len(rhos) - 1))]
    hi = rhos[int(0.975 * (len(rhos) - 1))]
    return lo, hi


def shifted_poly_basis(ell: int, n: int, shift: int) -> list[int]:
    basis = []
    for j in range(ell):
        e = (shift + j) % n
        basis.append(1 << e)
    if f2_rank(basis, n) < ell:
        out: list[int] = []
        for v in basis + [1 << j for j in range(n)]:
            if f2_rank(out + [v], n) > f2_rank(out, n):
                out.append(v)
            if len(out) == ell:
                break
        return out
    return basis


def affine_twist_basis(ell: int, n: int, F, g: int, add: int) -> list[int]:
    base = geometric_basis(ell, F, seed_elem=g)
    out = [base[0]]
    for i, v in enumerate(base[1:], start=1):
        twisted = v ^ ((add << (i % n)) & ((1 << n) - 1))
        if f2_rank(out + [twisted], n) > f2_rank(out, n):
            out.append(twisted)
        else:
            out.append(v)
    while len(out) < ell:
        cand = 1 << (len(out) % n)
        if f2_rank(out + [cand], n) > f2_rank(out, n):
            out.append(cand)
        else:
            out.append(cand ^ add)
        if len(out) > ell + 4:
            break
    return out[:ell]


def _diversity(shapes: list[dict], F, n: int, seek_nvar: bool) -> tuple[set[int], set[int]]:
    dims: set[int] = set()
    nvars: set[int] = set()
    for s in shapes:
        dims.add(dim_vv_path_a(s["basis"], F))
        if seek_nvar:
            na, _nb, nok, _det = encode_n_var(F, CURVE_B[n], s["basis"], XR[n])
            if nok:
                nvars.add(na)
    return dims, nvars


def build_catalog(n: int, ell: int, seek_floors: bool) -> dict:
    import numpy as np

    F = Field(n, MODULI[n])
    rng = np.random.default_rng(CATALOG_SEED + 1000 * n + ell)
    shapes: list[dict] = []
    seen: set = set()

    def try_add(kind: str, basis: list[int]) -> bool:
        basis = [int(x) for x in basis]
        if len(basis) != ell or f2_rank(basis, n) < ell:
            return False
        key = frozenset(basis)
        if key in seen:
            return False
        seen.add(key)
        shapes.append({"kind": kind, "basis": basis})
        return True

    try_add("poly", poly_basis(ell))
    for g in GEO_SEEDS:
        try_add(f"geo_g{g}", geometric_basis(ell, F, seed_elem=g))
    for shift in range(0, n):
        try_add(f"shift_s{shift}", shifted_poly_basis(ell, n, shift))
        if len(shapes) >= MIN_CATALOG // 2:
            break
    for g in (3, 5, 7, 11, 13):
        for add in (1, 3, 5, 9, 17):
            try_add(f"twist_g{g}_a{add}", affine_twist_basis(ell, n, F, g, add))
            if len(shapes) >= MIN_CATALOG:
                break
        if len(shapes) >= MIN_CATALOG:
            break

    guard = 0
    while len(shapes) < MIN_CATALOG and guard < 500:
        b = random_basis(ell, n, rng)
        try_add(f"rand_{len(shapes)}", b)
        guard += 1

    dims, nvars = _diversity(shapes, F, n, seek_nvar=seek_floors)
    construction_notes = {
        "min_catalog": MIN_CATALOG,
        "max_catalog": MAX_CATALOG,
        "seek_floors": seek_floors,
        "dimVV_distinct_after_min": len(dims),
        "Nvar_distinct_after_min": len(nvars) if seek_floors else None,
    }

    if seek_floors:
        guard = 0
        while (
            (len(dims) < FLOOR_DIMVV or len(nvars) < FLOOR_NVAR)
            and len(shapes) < MAX_CATALOG
            and guard < 800
        ):
            b = random_basis(ell, n, rng)
            key = frozenset(int(x) for x in b)
            if key in seen or f2_rank(b, n) < ell:
                guard += 1
                continue
            d = dim_vv_path_a(b, F)
            na, _nb, nok, _det = encode_n_var(F, CURVE_B[n], b, XR[n])
            expands = (d not in dims) or (nok and na not in nvars)
            if expands or (len(shapes) < MIN_CATALOG + 4 and guard % 3 == 0):
                seen.add(key)
                shapes.append({"kind": f"rand_div_{len(shapes)}", "basis": [int(x) for x in b]})
                dims.add(d)
                if nok:
                    nvars.add(na)
            guard += 1
        construction_notes["dimVV_distinct_final_prescreen"] = len(dims)
        construction_notes["Nvar_distinct_final_prescreen"] = len(nvars)
        construction_notes["prescreen_floor_met"] = (
            len(dims) >= FLOOR_DIMVV and len(nvars) >= FLOOR_NVAR
        )

    out = [{"kind": s["kind"], "basis": [int(x) for x in s["basis"]]} for s in shapes]
    return {
        "catalog": out,
        "catalog_size": len(out),
        "construction_notes": construction_notes,
        "prescreen_distinct_dimVV": sorted(dims) if seek_floors else None,
        "prescreen_distinct_Nvar": sorted(nvars) if seek_floors else None,
    }


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    cells = {}
    twin_ok = True
    stage1_keys = {f"n{n}_l{ell}" for n, ell in AUTHORIZED_STAGE1_CELLS}
    for n, ell in [(17, 3), (17, 4), (19, 3), (19, 4), (23, 3), (23, 4)]:
        key = f"n{n}_l{ell}"
        built = build_catalog(n, ell, seek_floors=(key in stage1_keys))
        cat = built["catalog"]
        F = Field(n, MODULI[n])
        b0 = cat[0]["basis"]
        da, db, dok = dim_vv_agree(b0, F)
        na, nb, nok, _det = encode_n_var(F, CURVE_B[n], b0, XR[n])
        cell_ok = dok and nok
        twin_ok = twin_ok and cell_ok
        cells[key] = {
            "n": n,
            "ell": ell,
            "catalog_size": len(cat),
            "catalog": cat,
            "construction_notes": built["construction_notes"],
            "prescreen_distinct_dimVV": built["prescreen_distinct_dimVV"],
            "prescreen_distinct_Nvar": built["prescreen_distinct_Nvar"],
            "probe_dimVV": {"a": da, "b": db, "agree": dok},
            "probe_Nvar": {"a": na, "b": nb, "agree": nok},
            "twin_ok": cell_ok,
        }
    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PREDECESSOR_EXP,
        "predecessor_evidence_id": PREDECESSOR_EV,
        "spearman_band": SPEARMAN_BAND,
        "catalog_seed": CATALOG_SEED,
        "bootstrap_reps": BOOTSTRAP_REPS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "min_catalog": MIN_CATALOG,
        "max_catalog": MAX_CATALOG,
        "admission_gates": {
            "distinct_dimVV_min": FLOOR_DIMVV,
            "distinct_Nvar_min": FLOOR_NVAR,
            "note": (
                "Stage-1 must meet floors BEFORE any Spearman>=0.70 band "
                "reading; else O-INCONCLUSIVE. Not a re-run of v1 catalog."
            ),
        },
        "authorized_stage1_cells": [{"n": n, "ell": ell} for n, ell in AUTHORIZED_STAGE1_CELLS],
        "encoder_pin": {
            "descend": "encode_s3.descend_s3",
            "n_var_def": "remaining vars after linear elim on Weil-descended S_3",
            "dimVV_twins": ["product_space.dim_vv_path_a", "product_space.dim_vv_path_b"],
            "n_var_twins": ["encode_s3._rank_and_pivot_vars_a", "encode_s3._rank_and_pivot_vars_b"],
        },
        "moduli": {str(k): hex(v) for k, v in MODULI.items()},
        "curve_B": CURVE_B,
        "xR": {str(k): hex(v) for k, v in XR.items()},
        "prediction": (
            f"FORALL (n,ell) in Stage-1 cells: AFTER admission floors "
            f"(>={FLOOR_DIMVV} distinct dimVV, >={FLOOR_NVAR} distinct N_var), "
            f"Spearman rho(dim(V·V), N_var) >= {SPEARMAN_BAND} across the "
            "frozen diversity-seeking catalog, OR label O-FAIL-BAND."
        ),
        "amazon_bedrock": "NOT_USED",
        "not_a_rerun_of": PREDECESSOR_EXP,
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", prereg)
    write_json(EXP_ROOT / "stage0" / "v-catalog.json", {"cells": cells, "twin_ok": twin_ok})
    status = "completed" if twin_ok else "artifact"
    outcome = "O-STAGE0-OK" if twin_ok else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PREDECESSOR_EXP,
        "predecessor_evidence_id": PREDECESSOR_EV,
        "stage": 0,
        "status": status,
        "outcome_hint": outcome,
        "twin_ok": twin_ok,
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "freeze": {
            "preregistered_predictions": "stage0/preregistered-predictions.json",
            "v_catalog": "stage0/v-catalog.json",
        },
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "status": status,
            "outcome_hint": outcome,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def measure_cell(n: int, ell: int, catalog: list[dict]) -> dict:
    F = Field(n, MODULI[n])
    rows = []
    twin_fail = False
    for entry in catalog:
        basis = entry["basis"]
        da, db, dok = dim_vv_agree(basis, F)
        na, nb, nok, det = encode_n_var(F, CURVE_B[n], basis, XR[n])
        if not (dok and nok):
            twin_fail = True
        rows.append(
            {
                "kind": entry["kind"],
                "basis": basis,
                "dimVV_a": da,
                "dimVV_b": db,
                "dimVV": da,
                "Nvar_a": na,
                "Nvar_b": nb,
                "N_var": na,
                "twin_ok": dok and nok,
                "encode_details": {
                    "lin_rank_a": det.get("lin_rank_a"),
                    "lin_rank_b": det.get("lin_rank_b"),
                    "nv0": det.get("nv0"),
                },
            }
        )
    xs = [float(r["dimVV"]) for r in rows]
    ys = [float(r["N_var"]) for r in rows]
    distinct_dim = len(set(xs))
    distinct_nvar = len(set(ys))
    floors_met = distinct_dim >= FLOOR_DIMVV and distinct_nvar >= FLOOR_NVAR
    rho = spearman_rho(xs, ys) if floors_met else float("nan")
    lo, hi = (
        bootstrap_ci(xs, ys, BOOTSTRAP_REPS, BOOTSTRAP_SEED + n * 10 + ell)
        if floors_met
        else (float("nan"), float("nan"))
    )
    rho_disclosed = spearman_rho(xs, ys)
    return {
        "n": n,
        "ell": ell,
        "catalog_size": len(rows),
        "rows": rows,
        "admission_floors_met": floors_met,
        "spearman_rho": rho,
        "spearman_rho_disclosed_pre_admission": rho_disclosed,
        "bootstrap_ci_95": [lo, hi],
        "distinct_dimVV": distinct_dim,
        "distinct_Nvar": distinct_nvar,
        "twin_fail": twin_fail,
        "band": SPEARMAN_BAND,
        "in_band": floors_met and (rho == rho) and rho >= SPEARMAN_BAND,
        "band_reading_authorized": floors_met and not twin_fail,
    }


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    cat_path = EXP_ROOT / "stage0" / "v-catalog.json"
    pre_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not cat_path.is_file() or not pre_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze files",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment"},
        )
        return raw

    catalog_doc = json.loads(cat_path.read_text(encoding="utf-8"))
    panels = {}
    any_twin_fail = False
    any_inconclusive = False
    all_in_band = True
    for n, ell in AUTHORIZED_STAGE1_CELLS:
        key = f"n{n}_l{ell}"
        cat = catalog_doc["cells"][key]["catalog"]
        panel = measure_cell(n, ell, cat)
        panels[key] = panel
        any_twin_fail = any_twin_fail or panel["twin_fail"]
        if not panel["admission_floors_met"]:
            any_inconclusive = True
        if panel["admission_floors_met"] and not panel["in_band"]:
            all_in_band = False

    if any_twin_fail:
        outcome = "O-ARTIFACT"
    elif any_inconclusive:
        outcome = "O-INCONCLUSIVE"
    elif all_in_band:
        outcome = "O-SUPPORT"
    else:
        outcome = "O-FAIL-BAND"

    write_json(EXP_ROOT / "stage1" / "panels.json", panels)
    control = {
        "twin_required": True,
        "any_twin_fail": any_twin_fail,
        "spearman_band": SPEARMAN_BAND,
        "admission_gates": {
            "distinct_dimVV_min": FLOOR_DIMVV,
            "distinct_Nvar_min": FLOOR_NVAR,
        },
        "predecessor_evidence_id": PREDECESSOR_EV,
        "null_note": (
            "Random-Boolean matched-catalog null is Stage 2 (not authorized); "
            "Stage-1 controls are twin agreement + distinct-value admission floors."
        ),
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    results = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}\n"
        f"Approved by: {APPROVED_BY}\n"
        f"Predecessor: {PREDECESSOR_EXP} / {PREDECESSOR_EV}\n"
        f"Outcome: **{outcome}**\n\n"
        f"Stage-1 cells: {AUTHORIZED_STAGE1_CELLS}\n\n"
        f"Admission floors: >={FLOOR_DIMVV} distinct dimVV, >={FLOOR_NVAR} distinct N_var\n"
        f"Spearman band (pre-registered; read only after floors): >= {SPEARMAN_BAND}\n\n"
        "## Panels\n\n"
    )
    for key, p in panels.items():
        results += (
            f"- `{key}`: floors_met={p['admission_floors_met']}, "
            f"rho={p['spearman_rho']!r}, "
            f"CI95={p['bootstrap_ci_95']!r}, "
            f"distinct_dimVV={p['distinct_dimVV']}, "
            f"distinct_Nvar={p['distinct_Nvar']}, "
            f"in_band={p['in_band']}, twin_fail={p['twin_fail']}, "
            f"band_reading_authorized={p['band_reading_authorized']}\n"
        )
    results += (
        "\n## Claims\n\n"
        "- break: false\n"
        "- exponent_move: false\n"
        "- amazon_bedrock: NOT_USED\n"
        "- No n>=131 transfer.\n"
        f"- Not a re-run of {PREDECESSOR_EXP} v1 catalog.\n"
    )
    write_text(EXP_ROOT / "RESULTS.md", results)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PREDECESSOR_EXP,
        "predecessor_evidence_id": PREDECESSOR_EV,
        "stage": 1,
        "status": "completed",
        "outcome": outcome,
        "panels_summary": {
            k: {
                "admission_floors_met": v["admission_floors_met"],
                "spearman_rho": v["spearman_rho"],
                "bootstrap_ci_95": v["bootstrap_ci_95"],
                "in_band": v["in_band"],
                "distinct_dimVV": v["distinct_dimVV"],
                "distinct_Nvar": v["distinct_Nvar"],
                "twin_fail": v["twin_fail"],
                "band_reading_authorized": v["band_reading_authorized"],
            }
            for k, v in panels.items()
        },
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "completed",
            "outcome": outcome,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = Path(args.trial_plan)
    if not plan.is_file():
        print(f"missing trial plan: {plan}", file=sys.stderr)
        return 2
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    print(json.dumps({"ok": True, "stage": args.stage, "run_dir": str(run_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
