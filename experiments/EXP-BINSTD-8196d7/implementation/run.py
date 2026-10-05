#!/usr/bin/env python3
"""EXP-BINSTD-8196d7 Stages 0-1 launcher (frozen contract v1).

Stage 0: Freeze V catalog (≥12 shapes per (n,ℓ) cell), seeds, Spearman band
         −0.70, encoder pin, Trace-linear twin self-check on one probe V.
Stage 1: n=17, ℓ∈{3,4} — for each frozen V measure twin r_Tr and twin N_nl;
         compute Spearman ρ(r_Tr, N_nl) with bootstrap CI; write RESULTS.md
         with exactly one O-* label.

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

from encode_s3 import encode_trace_nnl  # noqa: E402
from gf2n import Field  # noqa: E402
from product_space import geometric_basis, poly_basis, random_basis  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-8196d7"
HYPOTHESIS_ID = "H-BINSTD-b102b7"
APPROVED_BY = "DEC-20261003-7d1fec"
EXP_ROOT = Path(__file__).resolve().parents[1]

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}

# Pre-registered: higher Trace rank → fewer residual nonlinear clauses.
SPEARMAN_BAND = -0.70
CATALOG_SEED = 202610038782
BOOTSTRAP_REPS = 200
BOOTSTRAP_SEED = 202610038783
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
    shapes.append({"kind": "poly", "basis": poly_basis(ell)})
    for g in (3, 5, 7, 9, 11):
        shapes.append({"kind": f"geo_g{g}", "basis": geometric_basis(ell, F, seed_elem=g)})
    seen = {frozenset(s["basis"]) for s in shapes}
    guard = 0
    while len(shapes) < need and guard < 200:
        b = random_basis(ell, n, rng)
        key = frozenset(b)
        if key not in seen:
            seen.add(key)
            shapes.append({"kind": f"rand_{len(shapes)}", "basis": b})
        guard += 1
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
        b0 = cat[0]["basis"]
        ra, rb, na, nb, ok, _det = encode_trace_nnl(F, CURVE_B[n], b0, XR[n])
        twin_ok = twin_ok and ok
        cells[f"n{n}_l{ell}"] = {
            "n": n,
            "ell": ell,
            "catalog_size": len(cat),
            "catalog": cat,
            "probe_rTr": {"a": ra, "b": rb, "agree": ok},
            "probe_Nnl": {"a": na, "b": nb, "agree": ok},
            "twin_ok": ok,
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
            f"FORALL (n,ell) in Stage-1 cells: Spearman rho(r_Tr, N_nl) "
            f"<= {SPEARMAN_BAND} across the frozen >=12-shape catalog, OR "
            "label Trace-rank-not-predictive / O-FAIL-BAND."
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
    return {
        "n": n,
        "ell": ell,
        "catalog_size": len(rows),
        "rows": rows,
        "spearman_rho": rho,
        "bootstrap_ci_95": [lo, hi],
        "distinct_rTr": distinct_rtr,
        "distinct_Nnl": distinct_nnl,
        "twin_fail": twin_fail,
        "band": SPEARMAN_BAND,
        "in_band": (rho == rho) and rho <= SPEARMAN_BAND,
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
        if panel["distinct_rTr"] < 3 or panel["distinct_Nnl"] < 2:
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
            "Shuffled-linear-rank null catalog is Stage 2 (not authorized); "
            "Stage-1 controls are twin agreement + distinct-r_Tr >= 3 floor."
        ),
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    results = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}\n"
        f"Approved by: {APPROVED_BY}\n"
        f"Outcome: **{outcome}**\n\n"
        f"Stage-1 cells: {AUTHORIZED_STAGE1_CELLS}\n\n"
        f"Spearman band (pre-registered): <= {SPEARMAN_BAND}\n\n"
        "## Panels\n\n"
    )
    for key, p in panels.items():
        results += (
            f"- `{key}`: rho={p['spearman_rho']!r}, "
            f"CI95={p['bootstrap_ci_95']!r}, "
            f"distinct_rTr={p['distinct_rTr']}, "
            f"distinct_Nnl={p['distinct_Nnl']}, "
            f"in_band={p['in_band']}, twin_fail={p['twin_fail']}\n"
        )
    results += (
        "\n## Claims\n\n"
        "- break: false\n"
        "- exponent_move: false\n"
        "- amazon_bedrock: NOT_USED\n"
        "- No n>=131 transfer.\n"
        "- Distinct from IDEA-20261001-febbe1 (dim(V·V)→N_var) and "
        "IDEA-20261001-20561e (peak-RSS band).\n"
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
