#!/usr/bin/env python3
"""EXP-SSIQ-c0a99a Stages 0-1: Arm I degree-thinning meters (integer-only).

Stage 0 freezes cells, formula, thresholds, and twin fixture probes.
Stage 1 samples B-smooth integers, measures k(d) and cover probability.

Observations only. No Magma/Sage/AUXIN/Bedrock. No isogeny walk. No attack.
No exponent claim. Arm II (Deuring) and Arm III (end-to-end) are NOT authorized.
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

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from meters import (  # noqa: E402
    character_cover,
    cover_formula,
    fourteen_prime_product,
    k_both,
    sample_bsmooth_factors,
    simulate_cover,
    two_prime_k2,
)
from ntheory import (  # noqa: E402
    miller_rabin,
    reconstruct,
    sieve_primes,
    split_window_x,
)

EXPERIMENT_ID = "EXP-SSIQ-c0a99a"
HYPOTHESIS_ID = "H-SSIQ-dfee7e"
APPROVED_BY = "DEC-20261003-f31aec"
EXP_ROOT = Path(__file__).resolve().parents[1]

P_I = 5 * (1 << 248) - 1
P_V = 27 * (1 << 500) - 1
P_REG = (1 << 40) - 87  # 1099511627689, MR-checked
B20 = 1 << 20
B12 = 1 << 12
RHO_GRID = [0.02, 0.05, 0.1, 0.2, 0.4, 0.8]
N_SAMPLES_K = 20000
N_COVER = 10000
N_HASH_SEEDS = 50
N_REGRESSION = 400
ARM_SEED = 2026100301
HASH_SEED = 2026100302
MEDIAN_REPRESENTATION = 80
MEDIAN_NEGLIGIBLE = 8
GSTAR_REPRESENTATION = 4.0
GSTAR_NEGLIGIBLE = 1.3
H1_PASS = 0.02
H1_FAIL = 0.1
MIN_CELL_N = 100

CELLS = [
    {"id": "sqisign_i_b20", "p": P_I, "B": B20, "log2_B": 20, "role": "arm_i"},
    {"id": "sqisign_v_b20", "p": P_V, "B": B20, "log2_B": 20, "role": "arm_i"},
    {"id": "regression_p40_b12", "p": P_REG, "B": B12, "log2_B": 12, "role": "regression"},
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


def quantile(sorted_vals: list[int], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    if q <= 0:
        return float(sorted_vals[0])
    if q >= 1:
        return float(sorted_vals[-1])
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return float(sorted_vals[lo])
    w = idx - lo
    return sorted_vals[lo] * (1 - w) + sorted_vals[hi] * w


def median_int(vals: list[int]) -> float:
    return quantile(sorted(vals), 0.5)


def run_stage0(run_dir: Path) -> dict:
    t0 = time.time()
    if not miller_rabin(P_I) or not miller_rabin(P_V) or not miller_rabin(P_REG):
        raise RuntimeError("frozen primes failed Miller-Rabin")
    primes = sieve_primes(B20)
    rng = random.Random(ARM_SEED)
    d14, f14 = fourteen_prime_product(primes)
    X14 = split_window_x(P_I, B20)
    m14 = k_both(f14, d14, X14)
    X2 = split_window_x(P_I, B20)
    d2, f2 = two_prime_k2(primes, 40, rng, X2)
    m2 = k_both(f2, d2, X2)
    fixtures = {
        "lemma34_note": "k>=1 expected for B-smooth d<=D_max under split-window X; violations are O-ARTIFACT",
        "fourteen_prime": {
            "d": d14,
            "omega": 14,
            "k_a": m14["k_a"],
            "k_b": m14["k_b"],
            "twin_ok": m14["agree"],
            "X": X14,
        },
        "k2": {
            "d": d2,
            "factors": [[p, e] for p, e in f2],
            "k_a": m2["k_a"],
            "k_b": m2["k_b"],
            "twin_ok": m2["agree"] and m2["k_a"] == 2,
            "X": X2,
            "formula_at_rho": {str(rho): cover_formula(2, rho) for rho in RHO_GRID},
        },
        "character_mod": 5,
        "primes_sieved_to": B20,
        "n_primes": len(primes),
    }
    twin_ok = bool(m14["agree"] and m2["agree"] and m2["k_a"] == 2)
    predictions = {
        "schema": "crypto.autoresearch.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "frozen_at_stage": 0,
        "formula": "P_cover = 1 - (1 - rho^2)^{k/2}",
        "rho_grid": RHO_GRID,
        "n_samples_k": N_SAMPLES_K,
        "n_cover": N_COVER,
        "n_hash_seeds": N_HASH_SEEDS,
        "n_regression": N_REGRESSION,
        "arm_seed": ARM_SEED,
        "hash_seed": HASH_SEED,
        "median_representation": MEDIAN_REPRESENTATION,
        "median_negligible": MEDIAN_NEGLIGIBLE,
        "gstar_representation": GSTAR_REPRESENTATION,
        "gstar_negligible": GSTAR_NEGLIGIBLE,
        "h1_pass_maxdev": H1_PASS,
        "h1_fail_maxdev": H1_FAIL,
        "min_cell_n": MIN_CELL_N,
        "cells": CELLS,
        "p_i": P_I,
        "p_v": P_V,
        "p_reg": P_REG,
        "B20": B20,
        "B12": B12,
        "arm_ii_authorized": False,
        "arm_iii_authorized": False,
        "exponent_moved": False,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", predictions)
    write_json(EXP_ROOT / "stage0" / "fixtures.json", fixtures)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": "O-STAGE0-OK" if twin_ok else "O-ARTIFACT",
        "twin_ok": twin_ok,
        "fixtures_ok": twin_ok,
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
        "wall_clock_seconds": time.time() - t0,
        "n_primes": len(primes),
        "k2_k": m2["k_a"],
        "fourteen_k": m14["k_a"],
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "run_dir": str(run_dir),
            "outcome": raw["outcome"],
            "twin_ok": twin_ok,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def _gstar_from_ks(ks: list[int]) -> float:
    if not ks:
        return float("nan")
    best = None
    for rho in RHO_GRID:
        costs = []
        for k in ks:
            p = cover_formula(k, rho)
            if p <= 0:
                continue
            costs.append(rho / p)
        if not costs:
            continue
        mean_c = sum(costs) / len(costs)
        if best is None or mean_c < best:
            best = mean_c
    if best is None or best <= 0:
        return float("nan")
    return 1.0 / best


def run_stage1(run_dir: Path) -> dict:
    t0 = time.time()
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    fix_path = EXP_ROOT / "stage0" / "fixtures.json"
    if not pred_path.is_file() or not fix_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze",
            "claims": {"break": False, "exponent_move": False},
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(run_dir / "manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 1, "outcome": "O-IMPEDIMENT", "amazon_bedrock": "NOT_USED"})
        return raw
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    fixtures = json.loads(fix_path.read_text(encoding="utf-8"))
    primes = sieve_primes(B20)
    rng = random.Random(ARM_SEED + 1)
    hash_rng_a = random.Random(HASH_SEED)
    hash_rng_b = random.Random(HASH_SEED + 17)
    artifact_flags: list[str] = []
    panels: dict[str, Any] = {}
    control_rows: list[dict[str, Any]] = []

    # k=2 control: formula vs simulation
    k2 = fixtures["k2"]
    d2 = int(k2["d"])
    f2 = [(int(p), int(e)) for p, e in k2["factors"]]
    X2 = int(k2["X"])
    m2 = k_both(f2, d2, X2)
    if not m2["agree"] or m2["k_a"] != 2:
        artifact_flags.append("k2_twin_or_k_not_2")
    k2_devs = []
    for rho in RHO_GRID:
        pa = simulate_cover(m2["A"], d2, 2, rho, 200, hash_rng_a, "a")
        pb = simulate_cover(m2["A"], d2, 2, rho, 200, hash_rng_b, "b")
        formula = cover_formula(2, rho)
        k2_devs.append(abs(pa - formula))
        k2_devs.append(abs(pb - formula))
        control_rows.append({"control": "k2", "rho": rho, "p_a": pa, "p_b": pb, "formula": formula})
    if max(k2_devs) > 0.05:
        artifact_flags.append("k2_cover_not_rho_squared")

    # character control: cost per success equals incumbent (gain ~ 1)
    d14 = int(fixtures["fourteen_prime"]["d"])
    # rebuild 14-prime factors
    d14b, f14 = fourteen_prime_product(primes)
    if d14b != d14:
        artifact_flags.append("fourteen_prime_mismatch")
    X14 = int(fixtures["fourteen_prime"]["X"])
    m14 = k_both(f14, d14, X14)
    char_hit = character_cover(m14["A"], d14, 5)
    control_rows.append({"control": "character_mod5", "hit": char_hit, "k": m14["k_a"]})

    for cell in CELLS:
        cid = cell["id"]
        p, B = int(cell["p"]), int(cell["B"])
        X = split_window_x(p, B)
        dmax = integer_dmax(p)
        role = cell["role"]
        n_take = N_REGRESSION if role == "regression" else N_SAMPLES_K
        ks: list[int] = []
        omegas: list[int] = []
        n_k0 = 0
        n_twin_fail = 0
        cover_devs: list[float] = []
        n_cover_used = 0
        for i in range(n_take):
            fac = sample_bsmooth_factors(primes, B, dmax, rng)
            if fac is None:
                continue
            d = reconstruct(fac)
            met = k_both(fac, d, X)
            if not met["agree"]:
                n_twin_fail += 1
                continue
            k = int(met["k_a"])
            ks.append(k)
            omegas.append(len(fac))
            if k < 1:
                n_k0 += 1
            if n_cover_used < (N_COVER if role == "arm_i" else min(200, N_COVER)):
                for rho in RHO_GRID:
                    formula = cover_formula(k, rho)
                    pa = simulate_cover(met["A"], d, k, rho, N_HASH_SEEDS if role == "arm_i" else 20, hash_rng_a, "a")
                    pb = simulate_cover(met["A"], d, k, rho, N_HASH_SEEDS if role == "arm_i" else 20, hash_rng_b, "b")
                    cover_devs.append(abs(pa - formula))
                    cover_devs.append(abs(pb - formula))
                n_cover_used += 1
        ks_sorted = sorted(ks)
        med = median_int(ks) if ks else float("nan")
        gstar = _gstar_from_ks(ks)
        maxdev = max(cover_devs) if cover_devs else float("nan")
        panels[cid] = {
            "p": p,
            "B": B,
            "X": X,
            "dmax": dmax,
            "role": role,
            "n_k": len(ks),
            "n_k0": n_k0,
            "n_twin_fail": n_twin_fail,
            "median_k": med,
            "p10_k": quantile(ks_sorted, 0.1) if ks_sorted else None,
            "p90_k": quantile(ks_sorted, 0.9) if ks_sorted else None,
            "mean_omega": (sum(omegas) / len(omegas)) if omegas else None,
            "gstar": gstar,
            "h1_maxdev": maxdev,
            "n_cover": n_cover_used,
            "underpowered": len(ks) < MIN_CELL_N,
        }
        if n_twin_fail:
            artifact_flags.append(f"{cid}_twin_fail")
        if n_k0:
            artifact_flags.append(f"{cid}_k_below_1")

    arm_i = [panels[c["id"]] for c in CELLS if c["role"] == "arm_i"]
    powered = [c for c in arm_i if not c["underpowered"]]
    if artifact_flags:
        outcome = "O-ARTIFACT"
    elif not powered:
        outcome = "O-INCONCLUSIVE"
    else:
        h1_bad = any((c["h1_maxdev"] == c["h1_maxdev"]) and c["h1_maxdev"] > H1_FAIL for c in powered)
        if h1_bad:
            outcome = "O-ARTIFACT"
        else:
            repr_hit = any(c["median_k"] >= MEDIAN_REPRESENTATION and c["gstar"] >= GSTAR_REPRESENTATION for c in powered)
            negl_all = all(c["median_k"] < MEDIAN_NEGLIGIBLE for c in powered)
            if repr_hit:
                outcome = "O-REPRESENTATION"
            elif negl_all:
                outcome = "O-NEGLIGIBLE"
            else:
                outcome = "O-MIXED"

    write_json(EXP_ROOT / "stage1" / "panels.json", panels)
    write_json(EXP_ROOT / "stage1" / "control-table.json", {"rows": control_rows, "artifact_flags": artifact_flags})
    results = "\n".join(
        [
            f"# RESULTS EXP-SSIQ-c0a99a Stages 0-1",
            "",
            f"outcome: {outcome}",
            f"hypothesis: {HYPOTHESIS_ID}",
            f"approved_by: {APPROVED_BY}",
            "",
            "Exactly one O-* label. Integer-only Arm I. No exponent claim.",
            "Amazon Bedrock: NOT_USED. Magma/Sage: not used.",
            "",
            f"artifact_flags: {artifact_flags}",
            f"panels: {json.dumps({k: {'median_k': v.get('median_k'), 'gstar': v.get('gstar'), 'n_k': v.get('n_k')} for k,v in panels.items()})}",
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
        "artifact_flags": artifact_flags,
        "panels_summary": {k: {"median_k": v.get("median_k"), "gstar": v.get("gstar"), "n_k": v.get("n_k"), "h1_maxdev": v.get("h1_maxdev")} for k, v in panels.items()},
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
        "wall_clock_seconds": time.time() - t0,
        "pred_n_samples_k": pred.get("n_samples_k"),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "run_dir": str(run_dir),
            "outcome": outcome,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def integer_dmax(p: int) -> int:
    from ntheory import integer_nth_root

    return integer_nth_root(p // 2, 3)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(args.trial_plan).read_text(encoding="utf-8"))
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("trial-plan experiment_id mismatch", file=sys.stderr)
        return 2
    if args.stage == 0:
        raw = run_stage0(run_dir)
    else:
        raw = run_stage1(run_dir)
    print(json.dumps({"outcome": raw.get("outcome"), "stage": args.stage}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
