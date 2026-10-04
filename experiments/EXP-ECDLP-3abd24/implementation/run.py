#!/usr/bin/env python3
"""EXP-ECDLP-3abd24 Stages 0-1 launcher (frozen contract v1).

Stage 0: freeze cells (list rows with integer n=2s), p(s), S_3 vs addition,
         easy-control dual Möbius deg=1, column counts.
Stage 1: s∈{4,5,6} digit-S_3 residual inverse-degree ladder; dual Möbius
         meters; same-support null; write RESULTS.md with one O-* label.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n≥131.
Amazon Bedrock is not selected.
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

from fp_semaev import (  # noqa: E402
    digit_eval,
    least_prime_above,
    on_curve,
    point_add,
    s3_eval_a,
    s3_eval_b,
)
from mobius_fp import dual_degree, pointwise_inv  # noqa: E402

EXPERIMENT_ID = "EXP-ECDLP-3abd24"
HYPOTHESIS_ID = "H-ECDLP-3091c2"
APPROVED_BY = "DEC-20261003-2cf084"
EXP_ROOT = Path(__file__).resolve().parents[1]

# Frozen cells: n = 2s Boolean variables. JSON freeze uses list rows.
CELLS = [
    {"n": 8, "s": 4, "p_floor": 2 ** (3 * 4 + 1)},
    {"n": 10, "s": 5, "p_floor": 2 ** (3 * 5 + 1)},
    {"n": 12, "s": 6, "p_floor": 2 ** (3 * 6 + 1)},
]
CURVE_A = 1
CURVE_B = 1
STREAM_SEED = 202610038184
N_UNSAT = 20
N_SAT = 8
N_NULL = 10
N_EASY = 5
TINY_P = 19
TINY_A = 1
TINY_B = 1
FULL_FRAC = 0.90
HALF_FRAC = 0.50


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


def residual_table(p: int, s: int, u: int, rng_coeffs: list[int] | None = None) -> list[int]:
    nvars = 2 * s
    table = []
    for mask in range(1 << nvars):
        a_bits = mask & ((1 << s) - 1)
        b_bits = mask >> s
        x1 = digit_eval(a_bits, s)
        x2 = digit_eval(b_bits, s)
        va = s3_eval_a(CURVE_A, CURVE_B, x1, x2, u, p)
        vb = s3_eval_b(CURVE_A, CURVE_B, x1, x2, u, p)
        if va != vb:
            raise RuntimeError("S_3 dual expansion mismatch")
        val = va
        if rng_coeffs is not None:
            val = rng_coeffs[mask] % p
        table.append(val)
    return table


def easy_table(p: int, nvars: int, c: int) -> list[int]:
    table = []
    for mask in range(1 << nvars):
        table.append((c + (mask & 1)) % p)
    return table


def s3_addition_identity() -> dict[str, Any]:
    pts = []
    for x in range(TINY_P):
        rhs = (x * x * x + TINY_A * x + TINY_B) % TINY_P
        for y in range(TINY_P):
            if (y * y) % TINY_P == rhs:
                pts.append((x, y))
    ok = 0
    checked = 0
    mismatch = 0
    for i, p1 in enumerate(pts[:8]):
        for p2 in pts[i : i + 8]:
            s = point_add(TINY_P, TINY_A, p1, p2)
            if s is None:
                continue
            checked += 1
            va = s3_eval_a(TINY_A, TINY_B, p1[0], p2[0], s[0], TINY_P)
            vb = s3_eval_b(TINY_A, TINY_B, p1[0], p2[0], s[0], TINY_P)
            if va != 0 or vb != 0 or va != vb:
                mismatch += 1
            else:
                ok += 1
    return {
        "tiny_p": TINY_P,
        "points": len(pts),
        "checked_sums": checked,
        "s3_zero_ok": ok,
        "mismatch": mismatch,
        "pass": mismatch == 0 and ok > 0,
    }


def column_counts(n: int) -> list[dict[str, int]]:
    from math import comb

    rows = []
    acc = 0
    for d in range(0, n + 1):
        acc += comb(n, d)
        rows.append({"n": n, "D": d, "C_leq_D": acc})
    return rows


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    id_check = s3_addition_identity()
    cells = []
    for row in CELLS:
        p = least_prime_above(row["p_floor"])
        cells.append({"n": row["n"], "s": row["s"], "p_floor": row["p_floor"], "p": p})
    easy_ok = True
    easy_rows = []
    for cell in cells[:1]:
        p = cell["p"]
        n = cell["n"]
        c = 3
        table = easy_table(p, n, c)
        inv = pointwise_inv(table, p)
        assert inv is not None
        da, db, agree = dual_degree(inv, p)
        easy_rows.append({"n": n, "s": cell["s"], "deg_a": da, "deg_b": db, "agree": agree})
        if not agree or da != 1:
            easy_ok = False
    counts = []
    for cell in cells:
        counts.extend(column_counts(cell["n"]))
    predictions = {
        "experiment_id": EXPERIMENT_ID,
        "amazon_bedrock": "NOT SELECTED",
        "full_frac": FULL_FRAC,
        "half_frac": HALF_FRAC,
        "n_unsat": N_UNSAT,
        "n_sat": N_SAT,
        "n_null": N_NULL,
        "n_easy": N_EASY,
        "stream_seed": STREAM_SEED,
        "curve": {"A": CURVE_A, "B": CURVE_B},
        "cells": cells,
        "prediction": (
            "FULL iff deg(f^{-1})=n on >=90 percent of unsatisfiable digit-S_3 "
            "residuals at every Stage-1 cell; dual Möbius routes agree."
        ),
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", predictions)
    write_json(
        EXP_ROOT / "stage0" / "identity-and-counts.json",
        {
            "s3_addition": id_check,
            "easy_control": easy_rows,
            "column_counts": counts,
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    outcome = "O-STAGE0-OK" if id_check["pass"] and easy_ok else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": outcome,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "twin_ok": easy_ok and id_check["pass"],
        "s3_addition_pass": id_check["pass"],
        "easy_control_pass": easy_ok,
        "cells": cells,
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "outcome": outcome,
            "validity": "valid" if outcome == "O-STAGE0-OK" else "invalid",
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def measure_cell(cell: dict[str, int], seed: int) -> dict[str, Any]:
    p = cell["p"]
    s = cell["s"]
    n = cell["n"]
    rng = random.Random(seed + s * 1009)
    unsat_degs: list[int] = []
    sat_count = 0
    dual_fail = 0
    spectrum_drop = 0
    draws = 0
    while len(unsat_degs) < N_UNSAT or sat_count < N_SAT:
        draws += 1
        if draws > 4000:
            break
        u = rng.randrange(p)
        table = residual_table(p, s, u)
        distinct = len({v for v in table})
        if distinct < 4:
            spectrum_drop += 1
            continue
        zeros = [m for m, v in enumerate(table) if v % p == 0]
        if zeros:
            if sat_count < N_SAT:
                sat_count += 1
            continue
        inv = pointwise_inv(table, p)
        if inv is None:
            continue
        da, db, agree = dual_degree(inv, p)
        if not agree:
            dual_fail += 1
            continue
        if len(unsat_degs) < N_UNSAT:
            unsat_degs.append(da)
    null_degs: list[int] = []
    null_fail = 0
    while len(null_degs) < N_NULL:
        coeffs = [rng.randrange(p) for _ in range(1 << n)]
        if any(c % p == 0 for c in coeffs):
            continue
        inv = pointwise_inv(coeffs, p)
        if inv is None:
            continue
        da, db, agree = dual_degree(inv, p)
        if not agree:
            null_fail += 1
            continue
        null_degs.append(da)
    easy_degs = []
    for i in range(N_EASY):
        c = 2 + i
        if c % p == 0 or (c + 1) % p == 0:
            c = 3
        inv = pointwise_inv(easy_table(p, n, c), p)
        assert inv is not None
        da, db, agree = dual_degree(inv, p)
        easy_degs.append({"n": n, "deg_a": da, "deg_b": db, "agree": agree})
    n_full = sum(1 for d in unsat_degs if d == n)
    n_half = sum(1 for d in unsat_degs if d <= s + 2)
    n_bounded = sum(1 for d in unsat_degs if d <= 2)
    n_null_full = sum(1 for d in null_degs if d == n)
    easy_ok = all(r["agree"] and r["deg_a"] == 1 for r in easy_degs)
    return {
        "n": n,
        "s": s,
        "p": p,
        "unsat_count": len(unsat_degs),
        "sat_count": sat_count,
        "unsat_degs": unsat_degs,
        "frac_full": (n_full / len(unsat_degs)) if unsat_degs else 0.0,
        "frac_half": (n_half / len(unsat_degs)) if unsat_degs else 0.0,
        "frac_bounded": (n_bounded / len(unsat_degs)) if unsat_degs else 0.0,
        "null_degs": null_degs,
        "null_frac_full": (n_null_full / len(null_degs)) if null_degs else 0.0,
        "easy": easy_degs,
        "easy_ok": easy_ok,
        "dual_fail": dual_fail + null_fail,
        "spectrum_drop": spectrum_drop,
        "draws": draws,
    }


def decide(panels: list[dict[str, Any]]) -> str:
    if any(p["dual_fail"] > 0 or not p["easy_ok"] or p["unsat_count"] < N_UNSAT for p in panels):
        if any(p["dual_fail"] > 0 or not p["easy_ok"] for p in panels):
            return "O-ARTIFACT"
        return "O-INCONCLUSIVE"
    if any(p["null_frac_full"] < FULL_FRAC for p in panels):
        return "O-ARTIFACT"
    full = all(p["frac_full"] >= FULL_FRAC for p in panels)
    bounded = all(p["frac_bounded"] >= FULL_FRAC for p in panels)
    half = all(p["frac_half"] >= HALF_FRAC for p in panels if p["s"] >= 5)
    if bounded:
        return "O-BOUNDED"
    if full:
        return "O-FULL"
    if half:
        return "O-HALF"
    return "O-MIXED"


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not pred_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
            "reason": "missing Stage-0 freeze",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "outcome": "O-IMPEDIMENT",
                "validity": "invalid",
                "amazon_bedrock": "NOT_USED",
            },
        )
        return raw
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    cells = pred["cells"]
    panels = [measure_cell(c, STREAM_SEED) for c in cells]
    outcome = decide(panels)
    write_json(
        EXP_ROOT / "stage1" / "panels.json",
        {"cells": panels, "amazon_bedrock": "NOT SELECTED"},
    )
    write_json(
        EXP_ROOT / "stage1" / "control-table.json",
        {
            "rows": [
                {
                    "n": p["n"],
                    "s": p["s"],
                    "frac_full": p["frac_full"],
                    "null_frac_full": p["null_frac_full"],
                    "easy_ok": p["easy_ok"],
                    "dual_fail": p["dual_fail"],
                }
                for p in panels
            ]
        },
    )
    lines = [
        f"# RESULTS {EXPERIMENT_ID}",
        "",
        f"outcome: {outcome}",
        f"hypothesis: {HYPOTHESIS_ID}",
        "authorized_stages: 0,1",
        "amazon_bedrock: NOT SELECTED",
        "claims.break: false",
        "claims.exponent_move: false",
        "",
        "Stage-1 inverse-degree ladder (digit S_3 residual over F_p).",
        "Dual meters: Möbius-fast vs Möbius-naive. No Magma/Sage/AUXIN.",
        "",
    ]
    for p in panels:
        lines.append(
            f"- n={p['n']} s={p['s']} p={p['p']} frac_full={p['frac_full']:.3f} "
            f"null_full={p['null_frac_full']:.3f} easy_ok={p['easy_ok']}"
        )
    lines.append("")
    lines.append(f"Exactly one O-* label: {outcome}")
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(lines) + "\n")
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "panels": [{"n": p["n"], "s": p["s"], "frac_full": p["frac_full"]} for p in panels],
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": outcome,
            "validity": "valid",
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
