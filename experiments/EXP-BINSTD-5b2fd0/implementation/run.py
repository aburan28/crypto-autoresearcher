#!/usr/bin/env python3
"""EXP-BINSTD-5b2fd0 Stages 0-1 launcher (frozen contract v1).

Stage 0: Freeze V catalog (≥12 shapes per (n,ℓ) cell), seeds, Spearman band
         0.70, encoder pin, twin self-check on one probe V.
Stage 1: n=17, ℓ∈{3,4} — for each frozen V measure twin dim(V·V) and twin
         N_var; compute Spearman ρ(dimVV, N_var) with bootstrap CI; write
         RESULTS.md with exactly one O-* label.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n≥131
transfer. Amazon Bedrock is not selected.
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
    geometric_basis,
    poly_basis,
    random_basis,
)

EXPERIMENT_ID = "EXP-BINSTD-5b2fd0"
HYPOTHESIS_ID = "H-BINSTD-880e8b"
APPROVED_BY = "DEC-20261003-672507"
EXP_ROOT = Path(__file__).resolve().parents[1]

# Frozen field moduli (irreducible).
MODULI = {
    17: (1 << 17) | (1 << 3) | 1,  # t^17+t^3+1
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,  # t^23+t^5+1
}
# Curve B constants for S_3 (binary Weierstrass y^2+xy=x^3+A x^2+B); only B enters S_3.
CURVE_B = {17: 1, 19: 1, 23: 1}
# Frozen xR per n (nonzero field elements).
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}

SPEARMAN_BAND = 0.70
CATALOG_SEED = 2026100317
BOOTSTRAP_REPS = 200
BOOTSTRAP_SEED = 2026100318
AUTHORIZED_STAGE1_CELLS = [(17, 3), (17, 4)]


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
    """Minimal YAML writer (no PyYAML dependency for manifests)."""
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


def build_catalog(n: int, ell: int, need: int = 12) -> list[dict]:
    """≥12 distinct dim-ℓ subspaces with frozen construction recipe."""
    F = Field(n, MODULI[n])
    import numpy as np

    rng = np.random.default_rng(CATALOG_SEED + 1000 * n + ell)
    shapes: list[dict] = []
    # Structured families
    shapes.append({"kind": "poly", "basis": poly_basis(ell)})
    for g in (3, 5, 7, 9, 11):
        shapes.append({"kind": f"geo_g{g}", "basis": geometric_basis(ell, F, seed_elem=g)})
    # Random subspaces until we have ≥need unique bases (as frozensets)
    seen = {frozenset(s["basis"]) for s in shapes}
    guard = 0
    while len(shapes) < need and guard < 200:
        b = random_basis(ell, n, rng)
        key = frozenset(b)
        if key not in seen:
            seen.add(key)
            shapes.append({"kind": f"rand_{len(shapes)}", "basis": b})
        guard += 1
    # Serialize bases as ints
    out = []
    for s in shapes[: max(need, len(shapes))]:
        out.append({"kind": s["kind"], "basis": [int(x) for x in s["basis"]]})
    return out


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    cells = {}
    twin_ok = True
    for n, ell in [(17, 3), (17, 4), (19, 3), (19, 4), (23, 3), (23, 4)]:
        cat = build_catalog(n, ell, need=12)
        F = Field(n, MODULI[n])
        # Twin self-check on first V
        b0 = cat[0]["basis"]
        da, db, dok = dim_vv_agree(b0, F)
        na, nb, nok, _det = encode_n_var(F, CURVE_B[n], b0, XR[n])
        cell_ok = dok and nok
        twin_ok = twin_ok and cell_ok
        cells[f"n{n}_l{ell}"] = {
            "n": n,
            "ell": ell,
            "catalog_size": len(cat),
            "catalog": cat,
            "probe_dimVV": {"a": da, "b": db, "agree": dok},
            "probe_Nvar": {"a": na, "b": nb, "agree": nok},
            "twin_ok": cell_ok,
        }
    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "spearman_band": SPEARMAN_BAND,
        "catalog_seed": CATALOG_SEED,
        "bootstrap_reps": BOOTSTRAP_REPS,
        "bootstrap_seed": BOOTSTRAP_SEED,
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
            f"FORALL (n,ell) in Stage-1 cells: Spearman rho(dim(V·V), N_var) "
            f">= {SPEARMAN_BAND} across the frozen >=12-shape catalog, OR "
            "label product-dim-not-predictive / O-FAIL-BAND."
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
    rho = spearman_rho(xs, ys)
    lo, hi = bootstrap_ci(xs, ys, BOOTSTRAP_REPS, BOOTSTRAP_SEED + n * 10 + ell)
    distinct_dim = len(set(xs))
    distinct_nvar = len(set(ys))
    return {
        "n": n,
        "ell": ell,
        "catalog_size": len(rows),
        "rows": rows,
        "spearman_rho": rho,
        "bootstrap_ci_95": [lo, hi],
        "distinct_dimVV": distinct_dim,
        "distinct_Nvar": distinct_nvar,
        "twin_fail": twin_fail,
        "band": SPEARMAN_BAND,
        "in_band": (rho == rho) and rho >= SPEARMAN_BAND,
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
        if panel["distinct_dimVV"] < 3 or panel["distinct_Nvar"] < 2:
            any_inconclusive = True
        if not panel["in_band"]:
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
        "null_note": (
            "Random-Boolean matched-catalog null is Stage 2 (not authorized); "
            "Stage-1 controls are twin agreement + distinct-value floors."
        ),
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    results = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}\n"
        f"Approved by: {APPROVED_BY}\n"
        f"Outcome: **{outcome}**\n\n"
        f"Stage-1 cells: {AUTHORIZED_STAGE1_CELLS}\n\n"
        f"Spearman band (pre-registered): >= {SPEARMAN_BAND}\n\n"
        "## Panels\n\n"
    )
    for key, p in panels.items():
        results += (
            f"- `{key}`: rho={p['spearman_rho']!r}, "
            f"CI95={p['bootstrap_ci_95']!r}, "
            f"distinct_dimVV={p['distinct_dimVV']}, "
            f"distinct_Nvar={p['distinct_Nvar']}, "
            f"in_band={p['in_band']}, twin_fail={p['twin_fail']}\n"
        )
    results += (
        "\n## Claims\n\n"
        "- break: false\n"
        "- exponent_move: false\n"
        "- amazon_bedrock: NOT_USED\n"
        "- No n>=131 transfer.\n"
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
                "distinct_dimVV": v["distinct_dimVV"],
                "distinct_Nvar": v["distinct_Nvar"],
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
