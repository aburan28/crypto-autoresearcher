#!/usr/bin/env python3
"""EXP-BINSTD-9b18fc Stages 0-1 launcher (diversity + scoped (17,4) successor).

Successor after EV-BINSTD-69cb29 / DEC-20261003-5e4cb9 (EXP-BINSTD-16ee30
O-INCONCLUSIVE: (17,3) dimVV floors unmet; (17,4) floors-met ρ≈−0.24 disclosed).
Also cites EV-BINSTD-a99d47. Does NOT re-run EXP-BINSTD-16ee30 or 5b2fd0 v1.

Stage 0: Enhanced diversity-seeking V catalog (min 32, max 72) with dimVV-first
         seek on (17,3); freeze band 0.70; new seeds; twin probe.
Stage 1: n=17, ell in {3,4}; twin meters; FORALL admission floors for package
         band; SCOPED (17,4) floors-met fail-band replication reading authorized
         independently when that cell meets floors.

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

EXPERIMENT_ID = "EXP-BINSTD-9b18fc"
HYPOTHESIS_ID = "H-BINSTD-73ea03"
APPROVED_BY = "DEC-20261003-6e578e"
PREDECESSOR_EXP = "EXP-BINSTD-16ee30"
PREDECESSOR_EV = "EV-BINSTD-69cb29"
PREDECESSOR_EV_V1 = "EV-BINSTD-a99d47"
FORBIDDEN_CATALOG_SEEDS = (2026100317, 2026100320)
EXP_ROOT = Path(__file__).resolve().parents[1]

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}

SPEARMAN_BAND = 0.70
CATALOG_SEED = 2026100330
BOOTSTRAP_REPS = 200
BOOTSTRAP_SEED = 2026100331
MIN_CATALOG = 32
MAX_CATALOG = 72
FLOOR_DIMVV = 3
FLOOR_NVAR = 2
AUTHORIZED_STAGE1_CELLS = [(17, 3), (17, 4)]
GEO_SEEDS = (
    2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33,
)


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
    import numpy as np

    rng = np.random.default_rng(seed)
    n = len(xs)
    samples = []
    for _ in range(reps):
        idx = rng.integers(0, n, size=n)
        rho = spearman_rho([xs[i] for i in idx], [ys[i] for i in idx])
        if rho == rho:
            samples.append(rho)
    if not samples:
        return float("nan"), float("nan")
    lo = float(np.quantile(samples, 0.025))
    hi = float(np.quantile(samples, 0.975))
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


def sparse_weight_basis(ell: int, n: int, positions: list[int]) -> list[int]:
    """ell basis vectors with prescribed bit supports (padded if needed)."""
    out: list[int] = []
    for i in range(ell):
        if i < len(positions):
            v = 1 << (positions[i] % n)
        else:
            v = 1 << ((i * 3 + 1) % n)
        # Mix with a second bit to escape pure monomial poly cluster.
        if i % 2 == 1:
            v ^= 1 << ((positions[i % len(positions)] + 5) % n)
        if f2_rank(out + [v], n) > f2_rank(out, n):
            out.append(v)
        else:
            for j in range(n):
                cand = 1 << j
                if f2_rank(out + [cand], n) > f2_rank(out, n):
                    out.append(cand)
                    break
    return out[:ell]



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


def complement_mix_basis(ell: int, n: int, F, g: int) -> list[int]:
    """Mix geometric generators with high-weight poly bits to exit {5,6} cluster."""
    geo = geometric_basis(ell, F, seed_elem=g)
    out: list[int] = []
    for i in range(ell):
        hi = (1 << ((n - 1 - i) % n)) | (1 << ((n - 3 - i) % n))
        cand = geo[i] ^ hi
        if f2_rank(out + [cand], n) > f2_rank(out, n):
            out.append(cand)
        elif f2_rank(out + [geo[i]], n) > f2_rank(out, n):
            out.append(geo[i])
        else:
            for j in range(n):
                c2 = 1 << j
                if f2_rank(out + [c2], n) > f2_rank(out, n):
                    out.append(c2)
                    break
    return out[:ell]


def _field_mul(F, a: int, b: int, n: int) -> int:
    if hasattr(F, "mul"):
        return int(F.mul(a, b))
    # Polynomial multiply mod MODULI[n]
    res = 0
    aa, bb = int(a), int(b)
    while bb:
        if bb & 1:
            res ^= aa
        bb >>= 1
        aa <<= 1
        if aa & (1 << n):
            aa ^= MODULI[n]
    return res & ((1 << n) - 1)


def multiplicative_translate_basis_fixed(ell: int, n: int, F, g: int, scale: int) -> list[int]:
    base = geometric_basis(ell, F, seed_elem=g)
    out: list[int] = []
    for v in base:
        tv = _field_mul(F, v, scale, n)
        if f2_rank(out + [tv], n) > f2_rank(out, n):
            out.append(tv)
        else:
            out.append(int(v))
    while len(out) < ell:
        cand = 1 << (len(out) % n)
        if f2_rank(out + [cand], n) > f2_rank(out, n):
            out.append(cand)
        else:
            out.append(cand ^ (scale & ((1 << n) - 1)))
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

    if CATALOG_SEED in FORBIDDEN_CATALOG_SEEDS:
        raise RuntimeError(f"forbidden prior catalog_seed {CATALOG_SEED}")

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
    for g in (3, 5, 7, 11, 13, 17, 19, 23):
        for add in (1, 3, 5, 9, 17, 21, 33):
            try_add(f"twist_g{g}_a{add}", affine_twist_basis(ell, n, F, g, add))
    for g in (3, 5, 7, 11, 13):
        try_add(f"compmix_g{g}", complement_mix_basis(ell, n, F, g))
    for g in (3, 5, 7, 11):
        for scale in (3, 5, 7, 9, 11, 13, 17):
            try_add(
                f"mtranslate_g{g}_s{scale}",
                multiplicative_translate_basis_fixed(ell, n, F, g, scale),
            )
    # Sparse / staggered supports aimed at breaking dimVV={5,6} on ell=3.
    for offset in range(0, n):
        pos = [(offset + k * 2) % n for k in range(ell)]
        try_add(f"sparse_o{offset}", sparse_weight_basis(ell, n, pos))
    for offset in range(0, n):
        pos = [(offset + k * 3) % n for k in range(ell)]
        try_add(f"sparse3_o{offset}", sparse_weight_basis(ell, n, pos))

    guard = 0
    while len(shapes) < MIN_CATALOG and guard < 800:
        b = random_basis(ell, n, rng)
        try_add(f"rand_{len(shapes)}", b)
        guard += 1

    # Cap at MAX after structured fill; keep first MAX unique by insertion order.
    if len(shapes) > MAX_CATALOG:
        shapes = shapes[:MAX_CATALOG]
        seen = {frozenset(s["basis"]) for s in shapes}

    dims, nvars = _diversity(shapes, F, n, seek_nvar=seek_floors)
    construction_notes = {
        "min_catalog": MIN_CATALOG,
        "max_catalog": MAX_CATALOG,
        "seek_floors": seek_floors,
        "recipe": "dimVV-first enhanced diversity (sparse/compmix/mtranslate/twist)",
        "dimVV_distinct_after_structured": len(dims),
        "Nvar_distinct_after_structured": len(nvars) if seek_floors else None,
        "not_a_rerun_of_seeds": list(FORBIDDEN_CATALOG_SEEDS),
    }

    if seek_floors:
        # DimVV-first: prefer candidates introducing new dimVV; then N_var.
        guard = 0
        while (
            (len(dims) < FLOOR_DIMVV or len(nvars) < FLOOR_NVAR)
            and len(shapes) < MAX_CATALOG
            and guard < 2000
        ):
            b = random_basis(ell, n, rng)
            key = frozenset(int(x) for x in b)
            if key in seen or f2_rank(b, n) < ell:
                guard += 1
                continue
            d = dim_vv_path_a(b, F)
            na, _nb, nok, _det = encode_n_var(F, CURVE_B[n], b, XR[n])
            expands_dim = d not in dims
            expands_nvar = nok and na not in nvars
            # DimVV-first: always take new dimVV; else take new N_var; else rare pad.
            take = expands_dim or (
                len(dims) >= FLOOR_DIMVV and expands_nvar
            ) or (len(shapes) < MIN_CATALOG + 8 and guard % 5 == 0)
            if take:
                seen.add(key)
                kind = "rand_dim" if expands_dim else ("rand_nvar" if expands_nvar else "rand_pad")
                shapes.append({"kind": f"{kind}_{len(shapes)}", "basis": [int(x) for x in b]})
                dims.add(d)
                if nok:
                    nvars.add(na)
            guard += 1
        construction_notes["dimVV_distinct_final_prescreen"] = len(dims)
        construction_notes["Nvar_distinct_final_prescreen"] = len(nvars)
        construction_notes["prescreen_floor_met"] = (
            len(dims) >= FLOOR_DIMVV and len(nvars) >= FLOOR_NVAR
        )
        construction_notes["prescreen_dimVV_floor_met"] = len(dims) >= FLOOR_DIMVV

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
    for n in (17, 19, 23):
        for ell in (3, 4):
            key = f"n{n}_l{ell}"
            built = build_catalog(n, ell, seek_floors=(key in stage1_keys))
            cat = built["catalog"]
            F = Field(n, MODULI[n])
            if cat:
                da, db, dok = dim_vv_agree(cat[0]["basis"], F)
                na, nb, nok, _ = encode_n_var(F, CURVE_B[n], cat[0]["basis"], XR[n])
                probe_ok = dok and nok
                twin_ok = twin_ok and probe_ok
            else:
                probe_ok = False
                twin_ok = False
            cells[key] = {
                "n": n,
                "ell": ell,
                "catalog_size": len(cat),
                "catalog": cat,
                "construction_notes": built["construction_notes"],
                "prescreen_distinct_dimVV": built["prescreen_distinct_dimVV"],
                "prescreen_distinct_Nvar": built["prescreen_distinct_Nvar"],
                "probe_twin_ok": probe_ok,
            }

    pred = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "predecessor_evidence_id": PREDECESSOR_EV,
        "predecessor_evidence_id_v1": PREDECESSOR_EV_V1,
        "predecessor_experiment_id": PREDECESSOR_EXP,
        "not_a_rerun_of": [PREDECESSOR_EXP, "EXP-BINSTD-5b2fd0"],
        "forbidden_catalog_seeds": list(FORBIDDEN_CATALOG_SEEDS),
        "catalog_seed": CATALOG_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_reps": BOOTSTRAP_REPS,
        "spearman_band": SPEARMAN_BAND,
        "min_catalog": MIN_CATALOG,
        "max_catalog": MAX_CATALOG,
        "admission_gates": {
            "distinct_dimVV_min": FLOOR_DIMVV,
            "distinct_Nvar_min": FLOOR_NVAR,
            "note": (
                "Package FORALL Stage-1 cells must meet floors BEFORE any "
                "O-SUPPORT/O-FAIL-BAND package band reading; else package "
                "O-INCONCLUSIVE. Scoped (17,4) floors-met fail-band replication "
                "is independently authorized when n17_l4 floors met."
            ),
        },
        "scoped_cell_failband_replication": {
            "cell": {"n": 17, "ell": 4},
            "authorized": True,
            "rule": (
                "When n17_l4 admission floors met and CI95 entirely below "
                "spearman_band 0.70 under twin agreement, record "
                "scoped_17_4_outcome=O-CELL-FAIL-BAND-17-4 (replication of "
                "EV-BINSTD-69cb29 disclosed cell reading under a NEW catalog). "
                "Does not upgrade package O-INCONCLUSIVE to package O-FAIL-BAND "
                "while any Stage-1 cell fails floors."
            ),
            "cites": [PREDECESSOR_EV, "DEC-20261003-5e4cb9"],
        },
        "authorized_stage1_cells": [{"n": n, "ell": ell} for n, ell in AUTHORIZED_STAGE1_CELLS],
        "moduli": {str(k): hex(v) for k, v in MODULI.items()},
        "curve_B": {str(k): v for k, v in CURVE_B.items()},
        "xR": {str(k): hex(v) for k, v in XR.items()},
        "encoder_pin": {
            "descend": "encode_s3.descend_s3",
            "dimVV_twins": [
                "product_space.dim_vv_path_a",
                "product_space.dim_vv_path_b",
            ],
            "n_var_def": "remaining vars after linear elim on Weil-descended S_3",
            "n_var_twins": [
                "encode_s3._rank_and_pivot_vars_a",
                "encode_s3._rank_and_pivot_vars_b",
            ],
        },
        "prediction": (
            "FORALL (n,ell) in Stage-1 cells: AFTER admission floors "
            "(>=3 distinct dimVV, >=2 distinct N_var) on the enhanced "
            "diversity-seeking catalog, Spearman rho(dim(V·V), N_var) >= 0.7, "
            "OR label package O-FAIL-BAND. Independently: if (17,4) floors met "
            "and CI95 entirely <0.70, label scoped_17_4_outcome "
            "O-CELL-FAIL-BAND-17-4."
        ),
        "amazon_bedrock": "NOT_USED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    write_json(EXP_ROOT / "stage0" / "v-catalog.json", {"cells": cells, "twin_ok": twin_ok})

    outcome_hint = "O-STAGE0-OK" if twin_ok else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PREDECESSOR_EXP,
        "predecessor_evidence_id": PREDECESSOR_EV,
        "stage": 0,
        "status": "completed" if twin_ok else "artifact",
        "outcome_hint": outcome_hint,
        "twin_ok": twin_ok,
        "catalog_seed": CATALOG_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "cell_catalog_sizes": {k: v["catalog_size"] for k, v in cells.items()},
        "stage1_prescreen": {
            k: {
                "prescreen_distinct_dimVV": cells[k]["prescreen_distinct_dimVV"],
                "prescreen_distinct_Nvar": cells[k]["prescreen_distinct_Nvar"],
                "construction_notes": cells[k]["construction_notes"],
            }
            for k in stage1_keys
        },
        "freeze": {
            "preregistered_predictions": "stage0/preregistered-predictions.json",
            "v_catalog": "stage0/v-catalog.json",
        },
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "not_a_rerun_of": [PREDECESSOR_EXP, "EXP-BINSTD-5b2fd0"],
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "status": raw["status"],
            "twin_ok": twin_ok,
            "outcome_hint": outcome_hint,
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
        "ci_entirely_below_band": (
            floors_met
            and lo == lo
            and hi == hi
            and hi < SPEARMAN_BAND
        ),
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

    pred = json.loads(pre_path.read_text(encoding="utf-8"))
    if pred.get("catalog_seed") in FORBIDDEN_CATALOG_SEEDS:
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "invalid",
            "outcome": "O-ARTIFACT",
            "reason": "forbidden prior catalog_seed in freeze",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "invalid"},
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

    # Scoped (17,4) fail-band replication (independent of package FORALL floors).
    p174 = panels.get("n17_l4") or {}
    if p174.get("twin_fail"):
        scoped_17_4 = "O-ARTIFACT"
    elif not p174.get("admission_floors_met"):
        scoped_17_4 = "O-CELL-INCONCLUSIVE-17-4"
    elif p174.get("ci_entirely_below_band"):
        scoped_17_4 = "O-CELL-FAIL-BAND-17-4"
    elif p174.get("in_band"):
        scoped_17_4 = "O-CELL-IN-BAND-17-4"
    else:
        scoped_17_4 = "O-CELL-OUT-OF-BAND-UNCLEAR-CI-17-4"

    write_json(EXP_ROOT / "stage1" / "panels.json", panels)
    control = {
        "twin_required": True,
        "any_twin_fail": any_twin_fail,
        "spearman_band": SPEARMAN_BAND,
        "admission_gates": {
            "distinct_dimVV_min": FLOOR_DIMVV,
            "distinct_Nvar_min": FLOOR_NVAR,
        },
        "scoped_17_4_outcome": scoped_17_4,
        "predecessor_evidence_id": PREDECESSOR_EV,
        "predecessor_evidence_id_v1": PREDECESSOR_EV_V1,
        "null_note": (
            "Random-Boolean matched-catalog null is Stage 2 (not authorized); "
            "Stage-1 controls are twin agreement + distinct-value admission floors; "
            "scoped (17,4) fail-band replication is independently authorized."
        ),
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    results = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}\n"
        f"Approved by: {APPROVED_BY}\n"
        f"Predecessor: {PREDECESSOR_EXP} / {PREDECESSOR_EV} "
        f"(also cites {PREDECESSOR_EV_V1})\n"
        f"Package outcome: **{outcome}**\n"
        f"Scoped (17,4) outcome: **{scoped_17_4}**\n\n"
        f"Stage-1 cells: {AUTHORIZED_STAGE1_CELLS}\n\n"
        f"Admission floors (package FORALL): >={FLOOR_DIMVV} distinct dimVV, "
        f">={FLOOR_NVAR} distinct N_var\n"
        f"Spearman band (pre-registered; package read only after FORALL floors): "
        f">= {SPEARMAN_BAND}\n"
        "Scoped (17,4) fail-band replication authorized when that cell meets floors "
        "(independent of (17,3) floors).\n\n"
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
            f"band_reading_authorized={p['band_reading_authorized']}, "
            f"ci_entirely_below_band={p['ci_entirely_below_band']}\n"
        )
    results += (
        "\n## Claims\n\n"
        "- break: false\n"
        "- exponent_move: false\n"
        "- amazon_bedrock: NOT_USED\n"
        "- No n>=131 transfer.\n"
        f"- Not a re-run of {PREDECESSOR_EXP} or EXP-BINSTD-5b2fd0 v1.\n"
        f"- catalog_seed={CATALOG_SEED} (forbidden priors: {list(FORBIDDEN_CATALOG_SEEDS)}).\n"
    )
    write_text(EXP_ROOT / "RESULTS.md", results)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PREDECESSOR_EXP,
        "predecessor_evidence_id": PREDECESSOR_EV,
        "predecessor_evidence_id_v1": PREDECESSOR_EV_V1,
        "stage": 1,
        "status": "completed",
        "outcome": outcome,
        "scoped_17_4_outcome": scoped_17_4,
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
                "ci_entirely_below_band": v["ci_entirely_below_band"],
            }
            for k, v in panels.items()
        },
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "not_a_rerun_of": [PREDECESSOR_EXP, "EXP-BINSTD-5b2fd0"],
        "catalog_seed": CATALOG_SEED,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "completed",
            "outcome": outcome,
            "scoped_17_4_outcome": scoped_17_4,
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
