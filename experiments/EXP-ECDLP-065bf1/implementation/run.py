#!/usr/bin/env python3
"""EXP-ECDLP-065bf1 Stages 0-1: structural-width audit of direct encodings.

Public known-scalar forward presentations only. Dual-route Python.
No Magma/Sage/AUXIN/Bedrock. No inverse solving. No exponent claim.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from elliptic import (  # noqa: E402
    add_affine_a,
    add_affine_b,
    on_curve,
    scalar_mul,
)
from meters import (  # noqa: E402
    permute_presentation,
    presentation_stats,
    random_coeff_clone,
)

EXPERIMENT_ID = "EXP-ECDLP-065bf1"
HYPOTHESIS_ID = "H-ECDLP-0fd4b9"
APPROVED_BY = "DEC-20261003-c6641c"
EXP_ROOT = Path(__file__).resolve().parents[1]

P = 17
CURVE_A = 1
CURVE_B = 1
G = (0, 1)
CELLS = [
    {"id": "toy_f17_k2", "p": P, "k": 2, "A": CURVE_A, "B": CURVE_B},
    {"id": "toy_f17_k3", "p": P, "k": 3, "A": CURVE_A, "B": CURVE_B},
]
NULL_SEED = 2026100303
DELTA_MIN = 1


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
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            s = str(v).replace('"', '\\"')
            lines.append(f'{k}: "{s}"')
    write_text(path, "\n".join(lines) + "\n")


def T(c: int, **exps: int) -> tuple[int, dict[str, int]]:
    return (c, {k: v for k, v in exps.items() if v})


def affine_presentation(k: int, p: int, curve_a: int, g: tuple[int, int]) -> tuple[list[str], list[dict], dict[str, int]]:
    """Affine Weierstrass successive +G encoding of [k]G."""
    pts_a = []
    acc = g
    pts_a.append(acc)
    for _ in range(k - 1):
        acc = add_affine_a(acc, g, curve_a, p)
        pts_a.append(acc)
    pts_b = []
    acc = g
    pts_b.append(acc)
    for _ in range(k - 1):
        acc = add_affine_b(acc, g, curve_a, p)
        pts_b.append(acc)
    if pts_a != pts_b:
        raise RuntimeError("dual addition routes disagree on public forward points")
    variables = ["xG", "yG"]
    constraints = [
        {
            "name": "curve_G",
            "terms": [T(-1, yG=2), T(1, xG=3), T(curve_a, xG=1), T(CURVE_B)],
        }
    ]
    wit = {"xG": g[0] % p, "yG": g[1] % p}
    prev_x, prev_y = "xG", "yG"
    for i, pt in enumerate(pts_a[1:], start=2):
        xi, yi, lami = f"x{i}", f"y{i}", f"lam{i}"
        variables.extend([lami, xi, yi])
        # Successive +G: first step is doubling G; later steps add G to (i-1)G.
        if i == 2:
            wit[lami] = (
                (3 * wit[prev_x] * wit[prev_x] + curve_a)
                * pow((2 * wit[prev_y]) % p, -1, p)
            ) % p
        else:
            dx = (wit["xG"] - wit[prev_x]) % p
            wit[lami] = ((wit["yG"] - wit[prev_y]) * pow(dx, -1, p)) % p
        if i == 2:
            # doubling: 2 yG * lam2 = 3 xG^2 + A
            constraints.append(
                {
                    "name": f"slope_{i}",
                    "terms": [T(2, yG=1, **{lami: 1}), T(-3, xG=2), T(-curve_a)],
                }
            )
            constraints.append(
                {
                    "name": f"x_{i}",
                    "terms": [T(-1, **{xi: 1}), T(1, **{lami: 2}), T(-2, xG=1)],
                }
            )
            constraints.append(
                {
                    "name": f"y_{i}",
                    "terms": [
                        T(-1, **{yi: 1}),
                        T(1, **{lami: 1, "xG": 1}),
                        T(-1, **{lami: 1, xi: 1}),
                        T(-1, yG=1),
                    ],
                }
            )
        else:
            constraints.append(
                {
                    "name": f"slope_{i}",
                    "terms": [
                        T(1, **{prev_x: 1, lami: 1}),
                        T(-1, **{"xG": 1, lami: 1}),
                        T(-1, **{prev_y: 1}),
                        T(1, yG=1),
                    ],
                }
            )
            constraints.append(
                {
                    "name": f"x_{i}",
                    "terms": [
                        T(-1, **{xi: 1}),
                        T(1, **{lami: 2}),
                        T(-1, **{prev_x: 1}),
                        T(-1, xG=1),
                    ],
                }
            )
            constraints.append(
                {
                    "name": f"y_{i}",
                    "terms": [
                        T(-1, **{yi: 1}),
                        T(1, **{lami: 1, prev_x: 1}),
                        T(-1, **{lami: 1, xi: 1}),
                        T(-1, **{prev_y: 1}),
                    ],
                }
            )
        constraints.append(
            {
                "name": f"curve_{i}",
                "terms": [T(-1, **{yi: 2}), T(1, **{xi: 3}), T(curve_a, **{xi: 1}), T(CURVE_B)],
            }
        )
        wit[xi], wit[yi] = pt
        prev_x, prev_y = xi, yi
    return variables, constraints, wit


def projective_presentation(k: int, p: int, curve_a: int, g: tuple[int, int]) -> tuple[list[str], list[dict], dict[str, int]]:
    """Same forward chain with extra homogeneous Z auxiliaries (Z=1 slice)."""
    variables, constraints, wit = affine_presentation(k, p, curve_a, g)
    # Add ZG=1 and Zi=1 with Xi = xi*Zi, Yi = yi*Zi (identity at Z=1).
    extra_vars = ["ZG"]
    extra_cons = [{"name": "ZG_one", "terms": [T(1, ZG=1), T(-1)]}]
    extra_wit = {"ZG": 1}
    extra_cons.append(
        {
            "name": "XG_def",
            "terms": [T(1, XG=1), T(-1, xG=1, ZG=1)],
        }
    )
    extra_cons.append(
        {
            "name": "YG_def",
            "terms": [T(1, YG=1), T(-1, yG=1, ZG=1)],
        }
    )
    extra_vars.extend(["XG", "YG"])
    extra_wit["XG"] = wit["xG"]
    extra_wit["YG"] = wit["yG"]
    for i in range(2, k + 1):
        z, xh, yh = f"Z{i}", f"X{i}", f"Y{i}"
        extra_vars.extend([z, xh, yh])
        extra_wit[z] = 1
        extra_wit[xh] = wit[f"x{i}"]
        extra_wit[yh] = wit[f"y{i}"]
        extra_cons.append({"name": f"{z}_one", "terms": [T(1, **{z: 1}), T(-1)]})
        extra_cons.append(
            {"name": f"{xh}_def", "terms": [T(1, **{xh: 1}), T(-1, **{f"x{i}": 1, z: 1})]}
        )
        extra_cons.append(
            {"name": f"{yh}_def", "terms": [T(1, **{yh: 1}), T(-1, **{f"y{i}": 1, z: 1})]}
        )
    return variables + extra_vars, constraints + extra_cons, {**wit, **extra_wit}


def measure_cell(cell: dict[str, Any]) -> dict[str, Any]:
    p = int(cell["p"])
    k = int(cell["k"])
    curve_a = int(cell["A"])
    q_a = scalar_mul(k, G, curve_a, p, "A")
    q_b = scalar_mul(k, G, curve_a, p, "B")
    if q_a != q_b:
        return {"id": cell["id"], "twin_ok": False, "reason": "scalar_mul dual disagree"}
    if not on_curve(*G, curve_a, CURVE_B, p) or not on_curve(*q_a, curve_a, CURVE_B, p):
        return {"id": cell["id"], "twin_ok": False, "reason": "points off curve"}
    av, ac, aw = affine_presentation(k, p, curve_a, G)
    pv, pc, pw = projective_presentation(k, p, curve_a, G)
    aff = presentation_stats(av, ac, aw, p)
    proj = presentation_stats(pv, pc, pw, p)
    ev, ec, ew = permute_presentation(av, ac, aw)
    perm = presentation_stats(ev, ec, ew, p)
    rnd = presentation_stats(av, random_coeff_clone(ac, NULL_SEED + k, p), aw, p)
    twin_ok = bool(aff["twin_ok"] and proj["twin_ok"] and perm["twin_ok"] and rnd["rank_agree"] and rnd["width_agree"])
    perm_iso = perm["width"] == aff["width"] and perm["n_vars"] == aff["n_vars"] and perm["n_edges"] == aff["n_edges"]
    if perm["rank"] != aff["rank"]:
        perm_iso = False
    rep_delta = {
        "n_vars": abs(proj["n_vars"] - aff["n_vars"]),
        "width": abs((proj["width"] or 0) - (aff["width"] or 0)),
        "max_degree": abs(proj["max_degree"] - aff["max_degree"]),
        "n_aux": abs(proj["n_aux"] - aff["n_aux"]),
    }
    rep_diff = any(v >= DELTA_MIN for v in rep_delta.values())
    incidence_rank_diff = (
        rnd["rank"] is not None
        and aff["rank"] is not None
        and rnd["matrix_rows"] == aff["matrix_rows"]
        and rnd["matrix_cols"] == aff["matrix_cols"]
        and abs(rnd["rank"] - aff["rank"]) >= DELTA_MIN
    )
    return {
        "id": cell["id"],
        "p": p,
        "k": k,
        "Q": list(q_a),
        "twin_ok": twin_ok,
        "perm_iso": perm_iso,
        "rep_diff": rep_diff,
        "incidence_rank_diff": incidence_rank_diff,
        "rep_delta": rep_delta,
        "affine": aff,
        "projective": proj,
        "perm": {kk: perm[kk] for kk in ("n_vars", "n_edges", "width", "rank", "twin_ok", "witness_ok")},
        "random_coeff": {kk: rnd[kk] for kk in ("rank", "width", "twin_ok", "witness_ok", "matrix_rows", "matrix_cols")},
        "amazon_bedrock": "NOT SELECTED",
    }


def decide_outcome(panels: list[dict[str, Any]]) -> str:
    if any(not p.get("twin_ok") for p in panels):
        return "O-ARTIFACT"
    if any(not p.get("perm_iso") for p in panels):
        return "O-ARTIFACT"
    any_rep = any(p.get("rep_diff") for p in panels)
    any_inc = any(p.get("incidence_rank_diff") for p in panels)
    if any_rep and any_inc:
        return "O-MIXED"
    if any_rep:
        return "O-REP-SENSITIVE"
    if any_inc:
        return "O-INCIDENCE-INSUFFICIENT"
    return "O-NO-DIFF"


def run_stage0(run_dir: Path) -> dict:
    t0 = time.time()
    if not on_curve(*G, CURVE_A, CURVE_B, P):
        raise RuntimeError("G not on frozen curve")
    q2a = scalar_mul(2, G, CURVE_A, P, "A")
    q2b = scalar_mul(2, G, CURVE_A, P, "B")
    q3a = scalar_mul(3, G, CURVE_A, P, "A")
    q3b = scalar_mul(3, G, CURVE_A, P, "B")
    twin_ok = q2a == q2b and q3a == q3b
    # k=1 nearby object: identity presentation must have width 0 on a 1-var dummy
    k1_vars = ["xG"]
    k1_cons = [{"name": "dummy_zero", "terms": [T(1, xG=1), T(-G[0])]}]
    k1_wit = {"xG": G[0]}
    from meters import presentation_stats as _ps

    k1 = _ps(k1_vars, k1_cons, k1_wit, P)
    fixtures = {
        "G": list(G),
        "curve": {"p": P, "A": CURVE_A, "B": CURVE_B},
        "k2_Q": list(q2a),
        "k3_Q": list(q3a),
        "routes_agree": twin_ok,
        "k1_nearby": {"width": k1["width"], "n_vars": k1["n_vars"], "twin_ok": k1["twin_ok"]},
        "ptm_k1_max_width": 1,
    }
    predictions = {
        "schema": "crypto.autoresearch.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "frozen_at_stage": 0,
        "formula": "rep_diff := max(|n_vars|,|width|,|max_degree|,|n_aux|) >= 1",
        "delta_min": DELTA_MIN,
        "null_seed": NULL_SEED,
        "cells": CELLS,
        "p": P,
        "A": CURVE_A,
        "B": CURVE_B,
        "k2": 2,
        "k3": 3,
        "G": list(G),
        "arm_ii_authorized": False,
        "exponent_moved": False,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", predictions)
    write_json(EXP_ROOT / "stage0" / "fixtures.json", fixtures)
    outcome = "O-STAGE0-OK" if twin_ok and k1["twin_ok"] else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": outcome,
        "twin_ok": twin_ok,
        "fixtures_ok": twin_ok,
        "claims": {"break": False, "exponent_move": False, "solve": False},
        "amazon_bedrock": "NOT_USED",
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "run_id": run_dir.name,
            "stage": 0,
            "outcome": outcome,
            "valid": True,
        },
    )
    return raw


def run_stage1(run_dir: Path) -> dict:
    t0 = time.time()
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not pred_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze",
            "claims": {"break": False, "exponent_move": False, "solve": False},
            "amazon_bedrock": "NOT_USED",
            "wall_clock_seconds": time.time() - t0,
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "run_id": run_dir.name, "stage": 1, "outcome": "O-IMPEDIMENT", "valid": False},
        )
        return raw
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    cells = pred["cells"]
    panels = [measure_cell(c) for c in cells]
    outcome = decide_outcome(panels)
    control_table = {
        "perm_iso": [p["perm_iso"] for p in panels],
        "twin_ok": [p["twin_ok"] for p in panels],
        "rep_diff": [p["rep_diff"] for p in panels],
        "incidence_rank_diff": [p["incidence_rank_diff"] for p in panels],
    }
    write_json(EXP_ROOT / "stage1" / "panels.json", {"cells": panels})
    write_json(EXP_ROOT / "stage1" / "control-table.json", control_table)
    md = [
        f"# RESULTS {EXPERIMENT_ID}",
        "",
        f"outcome: {outcome}",
        "",
        "Public known-scalar forward presentations only. No ECDLP solve.",
        "No exponent claim. Amazon Bedrock NOT SELECTED.",
        "",
        f"**{outcome}**",
        "",
        "Cells:",
    ]
    for p in panels:
        md.append(
            f"- {p['id']}: rep_diff={p['rep_diff']} incidence_rank_diff={p['incidence_rank_diff']} "
            f"twin_ok={p['twin_ok']} perm_iso={p['perm_iso']}"
        )
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(md) + "\n")
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "panels": [{k: p[k] for k in ("id", "twin_ok", "perm_iso", "rep_diff", "incidence_rank_diff", "rep_delta")} for p in panels],
        "claims": {"break": False, "exponent_move": False, "solve": False},
        "amazon_bedrock": "NOT_USED",
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {"experiment_id": EXPERIMENT_ID, "run_id": run_dir.name, "stage": 1, "outcome": outcome, "valid": True},
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
    if args.stage == 0:
        run_stage0(run_dir)
    else:
        run_stage1(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
