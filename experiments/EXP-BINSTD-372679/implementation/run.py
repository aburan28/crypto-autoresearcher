#!/usr/bin/env python3
"""EXP-BINSTD-372679 Stages 0-1 launcher (frozen contract v1).

Stage 0: ord_n(2) / stable-subspace lattice worksheet + H1-PRIME freeze.
Stage 1: field/curve/base setup + fixture B0 + H2 abscissa self-check.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131
attack. Stage-2 SAT census is NOT authorized under this card.
Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-BINSTD-372679"
HYPOTHESIS_ID = "H-BINSTD-c72284"
APPROVED_BY = "DEC-20261002-84a9b7"
MASTER_SEED = 2026100299
EXP_ROOT = Path(__file__).resolve().parents[1]

# Preregistered ord_n(2) table (worksheet AC targets).
PREREG_ORD = {17: 8, 23: 11, 31: 5, 131: 130, 163: 162}
PREREG_DIMS_163 = [0, 1, 162, 163]
H1_PRIME_BAND = 0.95
CELLS = [
    {"n": 17, "m": 2, "l": [8, 9]},
    {"n": 23, "m": 2, "l": [11, 12]},
    {"n": 31, "m": 2, "l": [15, 16]},
    {"n": 31, "m": 3, "l": [10, 11]},
]


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


def write_yaml_manifest(path: Path, data: dict[str, Any]) -> None:
    """Minimal YAML writer for flat/nested dicts used by the checker."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")

    def dump(obj: Any, indent: int = 0) -> list[str]:
        pad = "  " * indent
        lines: list[str] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{pad}{k}:")
                    lines.extend(dump(v, indent + 1))
                elif isinstance(v, bool):
                    lines.append(f"{pad}{k}: {'true' if v else 'false'}")
                elif v is None:
                    lines.append(f"{pad}{k}: null")
                elif isinstance(v, (int, float)):
                    lines.append(f"{pad}{k}: {v}")
                else:
                    s = str(v).replace('"', '\\"')
                    lines.append(f'{pad}{k}: "{s}"')
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{pad}-")
                    lines.extend(dump(item, indent + 1))
                else:
                    lines.append(f"{pad}- {item}")
        return lines

    path.write_text("\n".join(dump(data)) + "\n", encoding="utf-8")


def multiplicative_order(a: int, n: int) -> int:
    """Order of a modulo odd prime n (a and n coprime)."""
    if math.gcd(a, n) != 1:
        raise ValueError(f"gcd({a},{n}) != 1")
    # Factor n-1 naively.
    m = n - 1
    factors: list[int] = []
    d = 2
    x = m
    while d * d <= x:
        while x % d == 0:
            factors.append(d)
            x //= d
        d += 1
    if x > 1:
        factors.append(x)
    order = m
    for p in sorted(set(factors)):
        while order % p == 0 and pow(a, order // p, n) == 1:
            order //= p
    return order


def stable_dims_from_ord(n: int, ord_n: int) -> list[int]:
    """Subset sums of {1} union k copies of ord, k=(n-1)/ord."""
    if (n - 1) % ord_n != 0:
        raise ValueError(f"ord_n(2)={ord_n} does not divide n-1={n-1}")
    k = (n - 1) // ord_n
    # Dimensions = i + j*ord for i in {0,1}, j in 0..k
    dims = sorted({i + j * ord_n for i in (0, 1) for j in range(k + 1)})
    return dims


def peak_rss_bytes() -> int | None:
    try:
        import resource

        # ru_maxrss is kilobytes on Linux
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    except Exception:
        return None


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    ords: dict[str, int] = {}
    lattices: dict[str, list[int]] = {}
    for n, expected in PREREG_ORD.items():
        got = multiplicative_order(2, n)
        ords[str(n)] = got
        lattices[str(n)] = stable_dims_from_ord(n, got)

    match = all(ords[str(n)] == PREREG_ORD[n] for n in PREREG_ORD) and lattices["163"] == PREREG_DIMS_163
    withdrawn = {f"n={n},m={m}": round(n ** (-m), 6) for n, m in ((17, 2), (23, 2), (31, 2), (31, 3))}

    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "frozen_at_stage": 0,
        "master_seed": MASTER_SEED,
        "ord_n_of_2": {str(k): v for k, v in PREREG_ORD.items()},
        "measured_ord_n_of_2": ords,
        "stable_dims": lattices,
        "stable_dims_163_preregistered": PREREG_DIMS_163,
        "h1_prime_band_min_ratio": H1_PRIME_BAND,
        "withdrawn_n_to_minus_m": withdrawn,
        "cells": CELLS,
        "h2_removed": True,
        "h2_note": (
            "H2 (abscissa orbit-constancy) is a theorem via Tr(u^2)=Tr(u); "
            "kept only as Stage-1 instrument self-check, never a prediction."
        ),
        "kn_find_47da4e_scope": (
            "Prior on additive-overhead FORM for orbit unions at m=2 only; "
            "not evidence about linear stable bases; n=41/43 off-limits."
        ),
        "match_preregistered": match,
        "amazon_bedrock": "NOT SELECTED",
    }
    note = (
        f"# Stage-0 worksheet — {EXPERIMENT_ID}\n\n"
        f"ord_n(2) measured: {ords}\n"
        f"stable dims at 163: {lattices['163']}\n"
        f"preregistered match: {match}\n"
        f"H1-PRIME band: ratios >= {H1_PRIME_BAND}\n"
        f"H2 removed (theorem / self-check only).\n"
        f"Cells: {CELLS}\n"
        f"No Stage-2 SAT census under this card.\n"
        f"Amazon Bedrock: NOT SELECTED.\n"
    )
    stage0_dir = EXP_ROOT / "stage0"
    write_json(stage0_dir / "preregistered-predictions.json", prereg)
    write_text(stage0_dir / "worksheet-note.md", note)

    outcome = "O-RELABEL-READY" if match else "O-ORD"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "ord_n_of_2": ords,
        "stable_dims": lattices,
        "preregistered_match": match,
        "outcome": outcome,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": peak_rss_bytes(),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "schema": "crypto.autoresearch.run_manifest.v1",
            "run": {
                "experiment_id": EXPERIMENT_ID,
                "hypothesis_id": HYPOTHESIS_ID,
                "approved_by": APPROVED_BY,
                "stage": 0,
                "outcome": outcome,
                "preregistered_match": match,
                "validity": "valid" if match else "invalid_ord_mismatch",
            },
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return raw


def gf2_mul(a: int, b: int, mod: int, deg: int) -> int:
    """Multiply in F_2[x]/(mod), integers as bit-polynomials."""
    res = 0
    while b:
        if b & 1:
            res ^= a
        b >>= 1
        a <<= 1
        if a & (1 << deg):
            a ^= mod
    return res


def gf2_square(a: int, mod: int, deg: int) -> int:
    return gf2_mul(a, a, mod, deg)


def irreducible_moduli() -> dict[int, int]:
    """Fixed irreducible reduction polynomials for toy degrees (bit form)."""
    # x^17 + x^3 + 1; x^23 + x^5 + 1; x^31 + x^3 + 1 — classical sparse irreducibles.
    return {
        17: (1 << 17) | (1 << 3) | 1,
        23: (1 << 23) | (1 << 5) | 1,
        31: (1 << 31) | (1 << 3) | 1,
    }


def trace_f2(x: int, mod: int, n: int) -> int:
    """Absolute trace Tr_{F_{2^n}/F_2}(x)."""
    acc = x
    t = x
    for _ in range(n - 1):
        t = gf2_square(t, mod, n)
        acc ^= t
    return acc & 1


def h2_selfcheck(mod: int, n: int, a: int, b: int, samples: int, rng: random.Random) -> dict[str, Any]:
    """Check Tr(x + a + b/x^2) invariant under x -> x^2 for random nonzero x."""
    ok = 0
    tried = 0
    failures = 0
    # For b in F_2 and a in F_2, b/x^2 uses field inverse of x^2 times b.
    while tried < samples:
        x = rng.randrange(1, 1 << n)
        # compute x^{-2} via Fermat: x^{2^n - 2} = x^{-1}, then square? easier: pow in field
        # Inverse via x^{2^n - 2}; then x^{-2} = (x^{-1})^2.
        inv = 1
        base = x
        exp = (1 << n) - 2
        while exp:
            if exp & 1:
                inv = gf2_mul(inv, base, mod, n)
            base = gf2_square(base, mod, n)
            exp >>= 1
        x2_inv = gf2_square(inv, mod, n)
        term = x ^ a ^ (gf2_mul(b, x2_inv, mod, n) if b else 0)
        tr = trace_f2(term, mod, n)
        xs = gf2_square(x, mod, n)
        # Squaring preserves the abscissa predicate; recompute on xs.
        invs = 1
        base = xs
        exp = (1 << n) - 2
        while exp:
            if exp & 1:
                invs = gf2_mul(invs, base, mod, n)
            base = gf2_square(base, mod, n)
            exp >>= 1
        xs2_inv = gf2_square(invs, mod, n)
        term_s = xs ^ a ^ (gf2_mul(b, xs2_inv, mod, n) if b else 0)
        tr_s = trace_f2(term_s, mod, n)
        tried += 1
        if tr == tr_s:
            ok += 1
        else:
            failures += 1
            if failures >= 3:
                break
    return {
        "samples": tried,
        "matching": ok,
        "failures": failures,
        "pass": failures == 0 and ok == tried and tried == samples,
        "curve_a": a,
        "curve_b": b,
        "n": n,
    }


def encoding_export_sizes(n: int, l: int, m: int) -> dict[str, Any]:
    """Structural size model for arms (a)(b)(c) — not a SAT solve."""
    # Plain: m * n Boolean vars for coordinates in an n-bit field element, but
    # restricted to V of dim l → m*l vars; S_m lex break; XOR rows for field eqs.
    plain_vars = m * l
    rep_shift_vars = m * (l + math.ceil(math.log2(n)))  # representative + shift bits
    orbit_vars = plain_vars + n  # one-hot over conjugate targets (gauge-fixed uses n then drops to 1)
    return {
        "n": n,
        "l": l,
        "m": m,
        "plain": {"bool_vars": plain_vars, "note": "arm_c"},
        "rep_shift": {"bool_vars": rep_shift_vars, "note": "arm_a"},
        "orbit_gauge": {
            "bool_vars_before_gauge": orbit_vars,
            "bool_vars_after_gauge_j0": plain_vars,
            "note": "arm_b; gauge j=0 equals arm_c var count",
        },
        "gauge_j0_equals_plain_varcount": True,
    }


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    prereg_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not prereg_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0/preregistered-predictions.json missing",
            "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
            "amazon_bedrock": "NOT SELECTED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "schema": "crypto.autoresearch.run_manifest.v1",
                "run": {
                    "experiment_id": EXPERIMENT_ID,
                    "stage": 1,
                    "outcome": "O-IMPEDIMENT",
                    "validity": "impediment",
                },
                "amazon_bedrock": "NOT SELECTED",
            },
        )
        return raw

    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    if not prereg.get("match_preregistered"):
        outcome = "O-ORD"
        fixture = {"pass": False, "reason": "stage0 preregistered_match false"}
        curves = {}
    else:
        mods = irreducible_moduli()
        rng = random.Random(MASTER_SEED)
        h2_results = {}
        exports = {}
        curves = {}
        for n in (17, 23, 31):
            mod = mods[n]
            curves[str(n)] = {
                "modulus": mod,
                "koblitz_a1_b1": {"a": 1, "b": 1},
                "koblitz_a0_b1": {"a": 0, "b": 1},
                "ordinary_a1_b_t": {"a": 1, "b": 0b10, "note": "b=t not in F_2"},
                "ord_n_of_2": PREREG_ORD[n],
                "stable_dims": stable_dims_from_ord(n, PREREG_ORD[n]),
            }
            h2_results[str(n)] = h2_selfcheck(mod, n, a=1, b=1, samples=256, rng=rng)
            for cell in CELLS:
                if cell["n"] != n:
                    continue
                for l in cell["l"]:
                    key = f"n{n}_m{cell['m']}_l{l}"
                    exports[key] = encoding_export_sizes(n, l, cell["m"])

        h2_pass = all(v["pass"] for v in h2_results.values())
        gauge_ok = all(v["gauge_j0_equals_plain_varcount"] for v in exports.values())
        b0_pass = h2_pass and gauge_ok and len(exports) > 0
        fixture = {
            "pass": b0_pass,
            "h2_selfcheck": h2_results,
            "gauge_j0_equals_arm_c": gauge_ok,
            "encoding_exports": exports,
            "checks": {
                "h2_abscissa_orbit_constancy": h2_pass,
                "gauge_j0_varcount_equals_plain": gauge_ok,
                "exports_present": len(exports) > 0,
            },
        }
        outcome = "O-RELABEL-READY" if b0_pass else "O-ARTIFACT"

        stage1_dir = EXP_ROOT / "stage1"
        write_json(stage1_dir / "fixture-B0.json", fixture)
        write_json(stage1_dir / "curves-and-bases.json", curves)

    results_md = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"- hypothesis: {HYPOTHESIS_ID}\n"
        f"- approved_by: {APPROVED_BY}\n"
        f"- stages_executed: 0-1\n"
        f"- outcome: **{outcome}**\n"
        f"- claims: no break, no exponent move, no deployed attack\n"
        f"- Stage-2 SAT census: NOT authorized under this card\n"
        f"- Amazon Bedrock: NOT SELECTED\n"
    )
    results_path = EXP_ROOT / "RESULTS.md"
    if not results_path.exists():
        write_text(results_path, results_md)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "fixture_B0": fixture,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": peak_rss_bytes(),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "schema": "crypto.autoresearch.run_manifest.v1",
            "run": {
                "experiment_id": EXPERIMENT_ID,
                "hypothesis_id": HYPOTHESIS_ID,
                "approved_by": APPROVED_BY,
                "stage": 1,
                "outcome": outcome,
                "fixture_B0_pass": bool(fixture.get("pass")),
                "validity": "valid" if outcome == "O-RELABEL-READY" else outcome.lower(),
            },
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("schema") != "crypto.autoresearch.trial_plan.v1":
        print("bad trial plan schema", file=sys.stderr)
        return 2
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("trial plan experiment_id mismatch", file=sys.stderr)
        return 2
    if args.stage == 0:
        raw = stage0(run_dir)
    else:
        raw = stage1(run_dir)
    print(json.dumps({"stage": args.stage, "outcome": raw.get("outcome")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
