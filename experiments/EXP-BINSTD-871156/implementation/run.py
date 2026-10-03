#!/usr/bin/env python3
"""EXP-BINSTD-871156 Stages 0-1 launcher (rank-diverse ℓ=4 successor).

Successor to EXP-BINSTD-8196d7 after EV-BINSTD-56dda7 / DEC-20261003-efdb94
(O-INCONCLUSIVE: (17,4) constant r_Tr=0). Does NOT re-run the frozen v1
catalog (seed 202610038782). Diversity-seeking catalog targets
distinct_rTr≥3 and distinct_Nnl≥2 before any Spearman ≤−0.70 band reading.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n≥131
transfer. Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from itertools import combinations
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import encode_trace_nnl  # noqa: E402
from gf2n import Field  # noqa: E402
from product_space import (  # noqa: E402
    f2_rank,
    geometric_basis,
    poly_basis,
    random_basis,
)

EXPERIMENT_ID = "EXP-BINSTD-871156"
HYPOTHESIS_ID = "H-BINSTD-6d5b4a"
APPROVED_BY = "DEC-20261003-a16e9b"
PREDECESSOR_EXP = "EXP-BINSTD-8196d7"
PREDECESSOR_EV = "EV-BINSTD-56dda7"
EXP_ROOT = Path(__file__).resolve().parents[1]

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}

SPEARMAN_BAND = -0.70
CATALOG_SEED = 202610038196
BOOTSTRAP_REPS = 200
BOOTSTRAP_SEED = 202610038197
MIN_CATALOG = 24
MAX_CATALOG = 128
FLOOR_RTR = 3
FLOOR_NNL = 2
GEO_SEEDS = (3, 5, 7, 9, 11, 13, 17, 19, 23, 29, 31)
AUTHORIZED_STAGE1_CELLS = [(17, 3), (17, 4)]
# Parent v1 seed — must not be reused (not a re-run).
FORBIDDEN_V1_SEED = 202610038782


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


def _rank_diversity(shapes: list[dict], F, n: int) -> tuple[set[int], set[int]]:
    rtrs: set[int] = set()
    nnls: set[int] = set()
    for s in shapes:
        ra, _rb, na, _nb, ok, _det = encode_trace_nnl(F, CURVE_B[n], s["basis"], XR[n])
        if ok:
            rtrs.add(ra)
            nnls.add(na)
    return rtrs, nnls


def build_catalog(n: int, ell: int, seek_floors: bool) -> dict:
    import numpy as np

    assert CATALOG_SEED != FORBIDDEN_V1_SEED
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
    for g in (3, 5, 7, 11, 13, 17):
        for add in (1, 3, 5, 9, 17, 33):
            try_add(f"twist_g{g}_a{add}", affine_twist_basis(ell, n, F, g, add))
            if len(shapes) >= MIN_CATALOG:
                break
        if len(shapes) >= MIN_CATALOG:
            break
    # Coordinate ℓ-subsets of the monomial basis — local probe found these
    # supply the only nonzero / higher r_Tr at (17,4) under the shared pin.
    units = [1 << j for j in range(n)]
    for combo in combinations(range(n), ell):
        try_add(f"coord_{'_'.join(map(str, combo))}", [units[i] for i in combo])
        if len(shapes) >= MIN_CATALOG:
            break

    guard = 0
    while len(shapes) < MIN_CATALOG and guard < 800:
        try_add(f"rand_{len(shapes)}", random_basis(ell, n, rng))
        guard += 1

    rtrs, nnls = _rank_diversity(shapes, F, n) if seek_floors else (set(), set())
    construction_notes = {
        "min_catalog": MIN_CATALOG,
        "max_catalog": MAX_CATALOG,
        "seek_floors": seek_floors,
        "floor_rTr": FLOOR_RTR,
        "floor_Nnl": FLOOR_NNL,
        "forbidden_v1_seed": FORBIDDEN_V1_SEED,
        "catalog_seed": CATALOG_SEED,
        "rTr_distinct_after_min": len(rtrs) if seek_floors else None,
        "Nnl_distinct_after_min": len(nnls) if seek_floors else None,
    }

    if seek_floors:
        # Pass 1: scan remaining coordinate ℓ-subsets for rank-expanding bases.
        for combo in combinations(range(n), ell):
            if len(rtrs) >= FLOOR_RTR and len(nnls) >= FLOOR_NNL:
                break
            if len(shapes) >= MAX_CATALOG:
                break
            b = [units[i] for i in combo]
            key = frozenset(b)
            if key in seen or f2_rank(b, n) < ell:
                continue
            ra, _rb, na, _nb, ok, _det = encode_trace_nnl(F, CURVE_B[n], b, XR[n])
            if not ok:
                continue
            expands = (ra not in rtrs) or (na not in nnls)
            if expands:
                seen.add(key)
                shapes.append(
                    {
                        "kind": f"coord_div_{'_'.join(map(str, combo))}",
                        "basis": b,
                    }
                )
                rtrs.add(ra)
                nnls.add(na)

        # Pass 2: random expanders until floors or max catalog.
        guard = 0
        while (
            (len(rtrs) < FLOOR_RTR or len(nnls) < FLOOR_NNL)
            and len(shapes) < MAX_CATALOG
            and guard < 8000
        ):
            b = random_basis(ell, n, rng)
            key = frozenset(int(x) for x in b)
            if key in seen or f2_rank(b, n) < ell:
                guard += 1
                continue
            ra, _rb, na, _nb, ok, _det = encode_trace_nnl(F, CURVE_B[n], b, XR[n])
            if not ok:
                guard += 1
                continue
            expands = (ra not in rtrs) or (na not in nnls)
            if expands or (len(shapes) < MIN_CATALOG + 8 and guard % 4 == 0):
                seen.add(key)
                shapes.append({"kind": f"rand_div_{len(shapes)}", "basis": [int(x) for x in b]})
                rtrs.add(ra)
                nnls.add(na)
            guard += 1
        construction_notes["rTr_distinct_final_prescreen"] = len(rtrs)
        construction_notes["Nnl_distinct_final_prescreen"] = len(nnls)
        construction_notes["prescreen_floor_met"] = (
            len(rtrs) >= FLOOR_RTR and len(nnls) >= FLOOR_NNL
        )
        construction_notes["prescreen_distinct_rTr"] = sorted(rtrs)
        construction_notes["prescreen_distinct_Nnl"] = sorted(nnls)

    out = [{"kind": s["kind"], "basis": [int(x) for x in s["basis"]]} for s in shapes]
    return {
        "catalog": out,
        "catalog_size": len(out),
        "construction_notes": construction_notes,
        "prescreen_distinct_rTr": sorted(rtrs) if seek_floors else None,
        "prescreen_distinct_Nnl": sorted(nnls) if seek_floors else None,
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
        ra, rb, na, nb, ok, _det = encode_trace_nnl(F, CURVE_B[n], b0, XR[n])
        twin_ok = twin_ok and ok
        cells[key] = {
            "n": n,
            "ell": ell,
            "catalog_size": len(cat),
            "catalog": cat,
            "construction_notes": built["construction_notes"],
            "prescreen_distinct_rTr": built["prescreen_distinct_rTr"],
            "prescreen_distinct_Nnl": built["prescreen_distinct_Nnl"],
            "probe_rTr": {"a": ra, "b": rb, "agree": ok},
            "probe_Nnl": {"a": na, "b": nb, "agree": ok},
            "twin_ok": ok,
        }
    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PREDECESSOR_EXP,
        "predecessor_evidence_id": PREDECESSOR_EV,
        "spearman_band": SPEARMAN_BAND,
        "catalog_seed": CATALOG_SEED,
        "forbidden_v1_seed": FORBIDDEN_V1_SEED,
        "bootstrap_reps": BOOTSTRAP_REPS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "min_catalog": MIN_CATALOG,
        "max_catalog": MAX_CATALOG,
        "admission_gates": {
            "distinct_rTr_min": FLOOR_RTR,
            "distinct_Nnl_min": FLOOR_NNL,
            "note": (
                "Stage-1 must meet floors BEFORE any Spearman<=-0.70 band "
                "reading; else O-INCONCLUSIVE. Not a re-run of EXP-BINSTD-8196d7."
            ),
        },
        "authorized_stage1_cells": [{"n": n, "ell": ell} for n, ell in AUTHORIZED_STAGE1_CELLS],
        "encoder_pin": {
            "descend": "encode_s3.descend_s3",
            "r_Tr_def": (
                "F_2-rank of the pure-linear (degree<=1) Trace-derived block "
                "after Weil-descended S_3 (KR-IC-f5c584 on this pin)"
            ),
            "N_nl_def": (
                "count of nonlinear clauses (deg>=2) retaining a non-pivot "
                "variable after Trace-linear elimination"
            ),
            "twins": [
                "encode_s3._rank_and_pivot_vars_a",
                "encode_s3._rank_and_pivot_vars_b",
            ],
        },
        "moduli": {str(k): hex(v) for k, v in MODULI.items()},
        "curve_B": CURVE_B,
        "xR": {str(k): hex(v) for k, v in XR.items()},
        "prediction": (
            f"FORALL (n,ell) in Stage-1 cells: AFTER admission floors "
            f"(distinct_rTr>={FLOOR_RTR}, distinct_Nnl>={FLOOR_NNL}), "
            f"Spearman rho(r_Tr, N_nl) <= {SPEARMAN_BAND} across the frozen "
            "rank-diverse catalog, OR label O-FAIL-BAND."
        ),
        "amazon_bedrock": "NOT_USED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", prereg)
    write_json(EXP_ROOT / "stage0" / "v-catalog.json", {"cells": cells, "twin_ok": twin_ok})
    status = "completed" if twin_ok else "artifact"
    outcome = "O-STAGE0-OK" if twin_ok else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": status,
        "outcome": outcome,
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
        ra, rb, na, nb, ok, det = encode_trace_nnl(F, CURVE_B[n], basis, XR[n])
        if not ok:
            twin_fail = True
        rows.append(
            {
                "kind": entry["kind"],
                "basis": basis,
                "r_Tr_a": ra,
                "r_Tr_b": rb,
                "r_Tr": ra,
                "N_nl_a": na,
                "N_nl_b": nb,
                "N_nl": na,
                "twin_ok": ok,
                "encode_details": {
                    "n_trace_linear_rows": det.get("n_trace_linear_rows"),
                    "n_nonlinear_clauses_raw": det.get("n_nonlinear_clauses_raw"),
                    "nv0": det.get("nv0"),
                },
            }
        )
    xs = [float(r["r_Tr"]) for r in rows]
    ys = [float(r["N_nl"]) for r in rows]
    rho = spearman_rho(xs, ys)
    lo, hi = bootstrap_ci(xs, ys, BOOTSTRAP_REPS, BOOTSTRAP_SEED + n * 10 + ell)
    distinct_rtr = len(set(xs))
    distinct_nnl = len(set(ys))
    floors_met = distinct_rtr >= FLOOR_RTR and distinct_nnl >= FLOOR_NNL
    return {
        "n": n,
        "ell": ell,
        "catalog_size": len(rows),
        "rows": rows,
        "spearman_rho": rho,
        "bootstrap_ci_95": [lo, hi],
        "distinct_rTr": distinct_rtr,
        "distinct_Nnl": distinct_nnl,
        "floors_met": floors_met,
        "twin_fail": twin_fail,
        "band": SPEARMAN_BAND,
        "in_band": floors_met and (rho == rho) and rho <= SPEARMAN_BAND,
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

    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    if pre.get("catalog_seed") == FORBIDDEN_V1_SEED:
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "artifact",
            "outcome": "O-ARTIFACT",
            "reason": "forbidden v1 catalog seed reused (not a re-run of EXP-BINSTD-8196d7)",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "artifact"},
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
        if not panel["floors_met"]:
            any_inconclusive = True
        if panel["floors_met"] and not panel["in_band"]:
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
        "admission_gates": {"distinct_rTr_min": FLOOR_RTR, "distinct_Nnl_min": FLOOR_NNL},
        "null_note": (
            "Shuffled-linear-rank null catalog is Stage 2 (not authorized); "
            "Stage-1 controls are twin agreement + admission floors before band."
        ),
        "not_v1_rerun": True,
        "predecessor_evidence_id": PREDECESSOR_EV,
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    results = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}\n"
        f"Approved by: {APPROVED_BY}\n"
        f"Predecessor: {PREDECESSOR_EXP} / {PREDECESSOR_EV}\n"
        f"Outcome: **{outcome}**\n\n"
        f"Stage-1 cells: {AUTHORIZED_STAGE1_CELLS}\n\n"
        f"Spearman band (pre-registered): <= {SPEARMAN_BAND}\n"
        f"Admission floors: distinct_rTr>={FLOOR_RTR}, distinct_Nnl>={FLOOR_NNL}\n"
        f"Catalog seed: {CATALOG_SEED} (not v1 {FORBIDDEN_V1_SEED})\n\n"
        "## Panels\n\n"
    )
    for key, p in panels.items():
        results += (
            f"- `{key}`: rho={p['spearman_rho']!r}, "
            f"CI95={p['bootstrap_ci_95']!r}, "
            f"distinct_rTr={p['distinct_rTr']}, "
            f"distinct_Nnl={p['distinct_Nnl']}, "
            f"floors_met={p['floors_met']}, "
            f"in_band={p['in_band']}, twin_fail={p['twin_fail']}\n"
        )
    results += (
        "\n## Claims\n\n"
        "- break: false\n"
        "- exponent_move: false\n"
        "- amazon_bedrock: NOT_USED\n"
        "- No n>=131 transfer.\n"
        "- Not a re-run of EXP-BINSTD-8196d7.\n"
        "- Distinct from IDEA-20261001-febbe1 (dim(V·V)→N_var).\n"
    )
    write_text(EXP_ROOT / "RESULTS.md", results)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": "completed",
        "outcome": outcome,
        "panels_summary": {
            k: {
                "spearman_rho": v["spearman_rho"],
                "bootstrap_ci_95": v["bootstrap_ci_95"],
                "in_band": v["in_band"],
                "floors_met": v["floors_met"],
                "distinct_rTr": v["distinct_rTr"],
                "distinct_Nnl": v["distinct_Nnl"],
                "twin_fail": v["twin_fail"],
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
