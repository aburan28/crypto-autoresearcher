#!/usr/bin/env python3
"""EXP-BINSTD-c896e5 Stages 0-1: Nagao disjoint-coset vs chained S_3 yield.

In-Python Koblitz arithmetic + dual Field/TableField meters.
Not a Magma/Sage presence detector. No ECDLP solve. No n>=131.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from curve import Curve  # noqa: E402
from gf2 import MODULI, Field, TableField, field_for  # noqa: E402
from yield_meter import (  # noqa: E402
    collect_relations,
    factor_base,
    poly_x_span,
    unique_count,
)

EXPERIMENT_ID = "EXP-BINSTD-c896e5"
HYPOTHESIS_ID = "H-BINSTD-b130e3"
APPROVED_BY = "DEC-20261003-34592e"
EXP_ROOT = Path(__file__).resolve().parents[1]

CURVE_A = 0
CURVE_B = 1
RHO_NUM, RHO_DEN = 1, 1
FREEZE_CELLS = ((17, 3), (17, 4), (19, 3), (19, 4), (23, 3), (23, 4))
AUTHORIZED_STAGE1 = ((17, 3),)
N_REP = 3
NULL_SEEDS = (2026100311, 2026100312, 2026100313)
B_WALL_SECONDS = 0.05
B_WALL_CAP = 5.0
NULL_PAIR_TRIES = 64


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


def timed_scan(curve: Curve, fb, n: int, nagao_only: bool) -> dict[str, Any]:
    t0 = time.perf_counter()
    passes = 0
    last = set()
    while True:
        last = collect_relations(curve, fb, n, nagao_only)
        passes += 1
        elapsed = time.perf_counter() - t0
        if elapsed >= B_WALL_SECONDS or elapsed >= B_WALL_CAP:
            break
        if passes >= 10**6:
            break
    elapsed = max(time.perf_counter() - t0, 1e-9)
    uniq = unique_count(last)
    charged = uniq * passes
    return {
        "unique": uniq,
        "passes": passes,
        "wall_seconds": elapsed,
        "charged_relations": charged,
        "rels_per_sec": charged / elapsed,
        "rels": [[{"x": p[0], "y": p[1]} for p in rel] for rel in sorted(last)[:8]],
    }


def dual_fields(n: int):
    return field_for(n, table=False), field_for(n, table=True)


def freeze_rows() -> list[dict[str, Any]]:
    rows = []
    for n, ell in FREEZE_CELLS:
        F = field_for(n, table=False)
        curve = Curve(F, CURVE_A, CURVE_B)
        xs = poly_x_span(n, ell)
        fb = factor_base(curve, xs)
        rows.append(
            {
                "n": n,
                "ell": ell,
                "curve_A": CURVE_A,
                "curve_B": CURVE_B,
                "modulus": MODULI[n],
                "v_xcoords": xs,
                "fb_size": len(fb),
                "fb_points": [{"x": p[0], "y": p[1]} for p in fb],
            }
        )
    return rows


def twin_ok_cell(n: int, ell: int, fb) -> bool:
    Fa, Fb = dual_fields(n)
    ca, cb = Curve(Fa, CURVE_A, CURVE_B), Curve(Fb, CURVE_A, CURVE_B)
    ra = collect_relations(ca, fb, n, nagao_only=False)
    rb = collect_relations(cb, fb, n, nagao_only=False)
    na = collect_relations(ca, fb, n, nagao_only=True)
    nb = collect_relations(cb, fb, n, nagao_only=True)
    return ra == rb and na == nb


def null_hits(curve: Curve, fb, n: int, ell: int, seed: int) -> int:
    rng = random.Random(seed ^ n ^ (ell << 8))
    fb_set = set(fb)
    vmask = (1 << ell) - 1
    hits = 0
    tries = 0
    while tries < NULL_PAIR_TRIES:
        x1 = rng.randrange(1, 1 << n)
        x2 = rng.randrange(1, 1 << n)
        if (x1 & vmask) == x1 or (x2 & vmask) == x2:
            continue
        P = curve.lift_x(x1)
        Q = curve.lift_x(x2)
        tries += 1
        if P is None or Q is None:
            continue
        S = curve.add(P, Q)
        if S is None:
            continue
        R = curve.neg(S)
        if R in fb_set:
            hits += 1
    return hits


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    rows = freeze_rows()
    n17 = next(r for r in rows if r["n"] == 17 and r["ell"] == 3)
    fb = [(p["x"], p["y"]) for p in n17["fb_points"]]
    if len(fb) < 3:
        raise RuntimeError("n=17 ell=3 factor base too small")
    twins = twin_ok_cell(17, 3, fb)
    Fa, Fb = dual_fields(17)
    if not isinstance(Fa, Field) or not isinstance(Fb, TableField):
        twins = False
    mul_probe = Fa.mul(7, 11) == Fb.mul(7, 11)
    pred = {
        "schema": "EXP-BINSTD-c896e5.preregistered-predictions.v1",
        "rho": {"numer": RHO_NUM, "denom": RHO_DEN},
        "charge_rule": "repeat deterministic pair-scan until wall >= B_WALL_SECONDS; rps = unique*passes/wall",
        "b_wall_seconds": B_WALL_SECONDS,
        "b_wall_cap": B_WALL_CAP,
        "n_rep": N_REP,
        "null_seeds": list(NULL_SEEDS),
        "nagao_partition": "diagonal G=<Frobenius,negation> on FB x FB; canonical lex-min pair",
        "chained_s3": "every unordered FB pair; R=-(P+Q) in FB",
        "curve_A": CURVE_A,
        "curve_B": CURVE_B,
        "authorized_stage1_cells": [{"n": n, "ell": ell} for n, ell in AUTHORIZED_STAGE1],
        "freeze_cells": [{"n": n, "ell": ell} for n, ell in FREEZE_CELLS],
        "no_n_object_keys": True,
        "amazon_bedrock": "NOT SELECTED",
    }
    catalog = {
        "schema": "EXP-BINSTD-c896e5.v-catalog.v1",
        "cells": rows,
        "note": "list rows with integer n; never n-as-object-key",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    write_json(EXP_ROOT / "stage0" / "v-catalog.json", catalog)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": "O-STAGE0-OK" if twins and mul_probe else "O-ARTIFACT",
        "twin_ok": twins and mul_probe,
        "fb_size_n17_ell3": n17["fb_size"],
        "mul_probe": mul_probe,
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "amazon_bedrock": "NOT SELECTED",
        "magma_sage_auxin": "NOT USED",
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "outcome": raw["outcome"],
            "valid": raw["outcome"] == "O-STAGE0-OK",
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return raw


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    cat_path = EXP_ROOT / "stage0" / "v-catalog.json"
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not cat_path.is_file() or not pred_path.is_file():
        raise FileNotFoundError("Stage 0 freeze missing")
    catalog = json.loads(cat_path.read_text(encoding="utf-8"))
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    if not isinstance(catalog.get("cells"), list):
        raise RuntimeError("v-catalog cells must be a list of rows")
    rho = pred.get("rho") or {}
    if rho.get("numer") != RHO_NUM or rho.get("denom") != RHO_DEN:
        raise RuntimeError("rho mutated after freeze")
    row = next(
        r for r in catalog["cells"] if r.get("n") == 17 and r.get("ell") == 3
    )
    n = int(row["n"])
    ell = int(row["ell"])
    fb = [(int(p["x"]), int(p["y"])) for p in row["fb_points"]]
    Fa, Fb = dual_fields(n)
    ca, cb = Curve(Fa, CURVE_A, CURVE_B), Curve(Fb, CURVE_A, CURVE_B)
    twins = twin_ok_cell(n, ell, fb)
    nagao_a = timed_scan(ca, fb, n, nagao_only=True)
    chained_a = timed_scan(ca, fb, n, nagao_only=False)
    nagao_b = timed_scan(cb, fb, n, nagao_only=True)
    chained_b = timed_scan(cb, fb, n, nagao_only=False)
    if nagao_a["unique"] != nagao_b["unique"] or chained_a["unique"] != chained_b["unique"]:
        twins = False
    rps_n = nagao_a["rels_per_sec"]
    rps_c = chained_a["rels_per_sec"]
    # R >= rho=1 iff nagao rps * denom >= chained rps * numer
    holds = (rps_n * RHO_DEN >= rps_c * RHO_NUM) if rps_c > 0 else False
    both_zero = nagao_a["unique"] == 0 and chained_a["unique"] == 0
    null_rows = []
    for seed in pred["null_seeds"]:
        hits_a = null_hits(ca, fb, n, ell, int(seed))
        hits_b = null_hits(cb, fb, n, ell, int(seed))
        null_rows.append(
            {
                "n": n,
                "ell": ell,
                "seed": int(seed),
                "hits_a": hits_a,
                "hits_b": hits_b,
                "twins_agree": hits_a == hits_b,
            }
        )
        if hits_a != hits_b:
            twins = False
    null_total = sum(r["hits_a"] for r in null_rows)
    if not twins:
        outcome = "O-ARTIFACT"
    elif both_zero:
        outcome = "O-INCONCLUSIVE"
    elif holds:
        outcome = "O-SUPPORT"
    else:
        outcome = "O-FAIL-BAND"
    panel = {
        "n": n,
        "ell": ell,
        "fb_size": len(fb),
        "nagao_unique": nagao_a["unique"],
        "chained_unique": chained_a["unique"],
        "nagao_rps": rps_n,
        "chained_rps": rps_c,
        "R_numer": rps_n,
        "R_den": rps_c if rps_c else 0.0,
        "rho_numer": RHO_NUM,
        "rho_den": RHO_DEN,
        "band_holds": holds,
        "twins_agree": twins,
        "nagao_passes": nagao_a["passes"],
        "chained_passes": chained_a["passes"],
        "null_total_hits": null_total,
    }
    write_json(EXP_ROOT / "stage1" / "panels.json", {"cells": [panel]})
    write_json(
        EXP_ROOT / "stage1" / "control-table.json",
        {
            "cells": [
                {
                    "n": n,
                    "ell": ell,
                    "twins_agree": twins,
                    "null_total_hits": null_total,
                    "null_rows": null_rows,
                }
            ]
        },
    )
    results = "\n".join(
        [
            "# EXP-BINSTD-c896e5 Stage 1 RESULTS",
            "",
            f"outcome: {outcome}",
            f"hypothesis: {HYPOTHESIS_ID}",
            f"approved_by: {APPROVED_BY}",
            "",
            "Exactly one O-* label. Toy Nagao vs chained-S_3 rels/sec race.",
            "No ECDLP solve. No exponent. No n>=131. No Magma/Sage/AUXIN/Bedrock.",
            "",
        ]
    )
    write_text(EXP_ROOT / "RESULTS.md", results)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "twin_ok": twins,
        "band_holds": holds,
        "both_zero": both_zero,
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "amazon_bedrock": "NOT SELECTED",
        "magma_sage_auxin": "NOT USED",
        "wall_clock_seconds": time.time() - t0,
        "nagao_unique": nagao_a["unique"],
        "chained_unique": chained_a["unique"],
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": outcome,
            "valid": outcome
            in {"O-SUPPORT", "O-FAIL-BAND", "O-INCONCLUSIVE", "O-ARTIFACT", "O-IMPEDIMENT"},
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True, choices=[0, 1])
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if "bedrock" in args.trial_plan.lower() or "bedrock" in str(run_dir).lower():
        print("Bedrock prohibited", file=sys.stderr)
        return 2
    try:
        if args.stage == 0:
            raw = stage0(run_dir)
        else:
            raw = stage1(run_dir)
    except FileExistsError as exc:
        print(f"IMPEDIMENT overwrite: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"stage": args.stage, "outcome": raw.get("outcome")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
