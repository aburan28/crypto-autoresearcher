"""Stage 1 for EXP-ECDLP-a98ea9: k-free transport gate and provenance.

Hard gate. Exact digit-for-digit agreement at r in {1,2,3,4}, or STOP.
Does not measure ADV. Does not interpret D2.
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

from curve_find import find_curve, fp_mul
from ec_jac import Curve, NonUnitDenominator, affine_xy, is_infinity, scalar_mult
from kfree_transport import (
    affine_digits,
    canonical_order_n_lift,
    hensel_lift_without_projection,
    ordinary_base_p_digits,
)
from static_provenance import check_kfree_module

SEEDS = [3, 5, 7, 11, 13, 17, 19, 23]
PRECISIONS = (1, 2, 3, 4)
SAMPLES_PER_CURVE = 10000
# Six prime orders in the 16-26 bit band, spanning >6x.
BIT_LADDER = [16, 17, 18, 19, 20, 21]
HERE = Path(__file__).resolve().parent
RUN_DIR = HERE.parent / "runs" / "RUN-ECDLP-a98ea9-S1"


def _digits_of_jac(curve: Curve, P, precision: int):
    return affine_digits(curve, P, precision)


def _reduce_point(curve: Curve, P, from_r: int, to_r: int):
    """Reduce a Jacobian point from mod p^{from_r} to mod p^{to_r}."""
    if to_r > from_r:
        raise ValueError("cannot increase precision by reduction")
    mod = curve.p**to_r
    return (P[0] % mod, P[1] % mod, P[2] % mod)


def verify_lift(curve: Curve, P_fp, n: int, lifted, precision: int) -> dict:
    mod = curve.p**precision
    nP = scalar_mult(n, lifted, mod, curve)
    ax, ay = affine_xy(curve, lifted, mod)
    return {
        "n_times_is_infinity": is_infinity(nP, mod),
        "reduces_to_fp": (ax % curve.p == P_fp[0] % curve.p)
        and (ay % curve.p == P_fp[1] % curve.p),
    }


def run_instance(inst: dict, n_samples: int, seeds: list[int]) -> dict:
    curve: Curve = inst["curve"]
    S = inst["S"]
    n = inst["n"]
    p = inst["p"]
    max_r = max(PRECISIONS)
    t0 = time.time()
    S_hat = canonical_order_n_lift(curve, S, n, max_r)
    lift_check = verify_lift(curve, S, n, S_hat, max_r)
    if not lift_check["n_times_is_infinity"] or not lift_check["reduces_to_fp"]:
        return {
            "p": p,
            "n": n,
            "validity": "failed_gate",
            "validity_reason": "canonical lift of S failed order-n or reduction check",
            "lift_check": lift_check,
        }

    # NULL-2 vs treatment at every r, including the r=1 width-zero identity.
    null2_cells = []
    for r in PRECISIONS:
        treat_r = _reduce_point(curve, S_hat, max_r, r) if r < max_r else S_hat
        if r < max_r:
            # rebuild at native precision so digits live in [0, p^r)
            treat_r = canonical_order_n_lift(curve, S, n, r)
        null_r = hensel_lift_without_projection(curve, S, r)
        d_t = _digits_of_jac(curve, treat_r, r)
        d_n = _digits_of_jac(curve, null_r, r)
        agree = d_t == d_n
        null2_cells.append(
            {
                "r": r,
                "treatment_digits": d_t,
                "null2_digits": d_n,
                "agree": agree,
                "width_zero": r == 1,
                "discriminating": r > 1,
            }
        )
    r1 = next(c for c in null2_cells if c["r"] == 1)
    if not r1["agree"]:
        return {
            "p": p,
            "n": n,
            "validity": "failed_gate",
            "validity_reason": "NULL-2 r=1 consistency check failed",
            "null2_cells": null2_cells,
        }

    per_r = {r: {"compared": 0, "agree": 0, "first_disagreement": None} for r in PRECISIONS}
    pd3_hits = 0
    samples_done = 0
    # Split samples across the eight declared seeds.
    per_seed = n_samples // len(seeds)
    leftover = n_samples - per_seed * len(seeds)
    for i, seed in enumerate(seeds):
        take = per_seed + (1 if i < leftover else 0)
        rng = random.Random(seed)
        for _ in range(take):
            withheld_scalar = rng.randrange(1, n)
            # Path 1: lift S (already have S_hat), then multiply by the scalar.
            # The scalar is known to the harness; it is not passed into
            # kfree_transport.
            path1 = scalar_mult(withheld_scalar, S_hat, p**max_r, curve)
            # Path 2: F_p point only. Compute [withheld_scalar]S over F_p in
            # this driver, then call the k-free lift. The lift never sees
            # withheld_scalar.
            T_fp = fp_mul(withheld_scalar, S, p, curve.A)
            if T_fp is None:
                pd3_hits += 1
                continue
            try:
                path2 = canonical_order_n_lift(curve, T_fp, n, max_r)
            except NonUnitDenominator:
                pd3_hits += 1
                continue
            samples_done += 1
            for r in PRECISIONS:
                if r == max_r:
                    d1 = _digits_of_jac(curve, path1, r)
                    d2 = _digits_of_jac(curve, path2, r)
                else:
                    d1 = ordinary_base_p_digits(affine_xy(curve, path1, p**max_r)[0], p, r)
                    d2 = ordinary_base_p_digits(affine_xy(curve, path2, p**max_r)[0], p, r)
                    # Compare the length-r prefixes of the max-precision digits
                    # (ordinary digits are compatible under reduction).
                per_r[r]["compared"] += 1
                if d1 == d2:
                    per_r[r]["agree"] += 1
                elif per_r[r]["first_disagreement"] is None:
                    per_r[r]["first_disagreement"] = {
                        "withheld_scalar": withheld_scalar,
                        "path1_digits": d1,
                        "path2_digits": d2,
                        "T_fp": list(T_fp),
                    }

    rates = {}
    exact = True
    for r, row in per_r.items():
        rate = (row["agree"] / row["compared"]) if row["compared"] else 0.0
        rates[r] = {
            "compared": row["compared"],
            "agree": row["agree"],
            "agreement_rate": rate,
            "exact": row["compared"] > 0 and row["agree"] == row["compared"],
            "first_disagreement": row["first_disagreement"],
        }
        exact = exact and rates[r]["exact"]

    return {
        "p": p,
        "A": inst["A"],
        "B": inst["B"],
        "N": inst["N"],
        "n": n,
        "S": list(S),
        "bits_p": inst["bits_p"],
        "bits_n": inst["bits_n"],
        "a_p": inst["a_p"],
        "lift_check": lift_check,
        "null2_cells": null2_cells,
        "samples_requested": n_samples,
        "samples_done": samples_done,
        "pd3_non_unit_skips": pd3_hits,
        "per_r": {str(r): rates[r] for r in PRECISIONS},
        "exact_agreement_all_r": exact,
        "seconds": round(time.time() - t0, 3),
    }


def main() -> None:
    t_start = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    provenance = check_kfree_module(HERE / "kfree_transport.py")
    (RUN_DIR / "static-provenance-check.json").write_text(
        json.dumps(provenance, indent=2) + "\n"
    )
    if not provenance["passed"]:
        raw = {
            "stage": 1,
            "validity": "failed_gate",
            "validity_reason": "static provenance gate failed",
            "static_provenance": provenance,
        }
        (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
        print(json.dumps(raw, indent=2))
        raise SystemExit(1)

    instances = []
    instance_rows = []
    all_exact = True
    for bits in BIT_LADDER:
        seed = 1000 + bits
        print(f"finding curve at {bits} bits (seed={seed})", flush=True)
        inst = find_curve(bits, seed=seed, bit_lo=16, bit_hi=26)
        print(
            f"  p={inst['p']} n={inst['n']} bits_n={inst['bits_n']}",
            flush=True,
        )
        row = run_instance(inst, SAMPLES_PER_CURVE, SEEDS)
        instance_rows.append(row)
        all_exact = all_exact and row.get("exact_agreement_all_r", False)
        print(
            f"  exact={row.get('exact_agreement_all_r')} "
            f"samples={row.get('samples_done')} s={row.get('seconds')}",
            flush=True,
        )
        instances.append(
            {
                "p": inst["p"],
                "n": inst["n"],
                "bits_n": inst["bits_n"],
            }
        )
        if row.get("validity") == "failed_gate" or not row.get("exact_agreement_all_r", False):
            break

    validity = "valid" if all_exact and provenance["passed"] else "failed_gate"
    reason = (
        "static provenance passed; transport agreement rate exactly 1.000 "
        "at r in {1,2,3,4} on every completed instance"
        if validity == "valid"
        else "Stage 1 hard gate failed; see per-instance first_disagreement"
    )
    raw = {
        "stage": 1,
        "experiment_id": "EXP-ECDLP-a98ea9",
        "hypothesis_id": "H-ECDLP-07c7c6",
        "seeds": SEEDS,
        "samples_per_curve": SAMPLES_PER_CURVE,
        "precisions": list(PRECISIONS),
        "bit_ladder": BIT_LADDER,
        "static_provenance": provenance,
        "instances": instance_rows,
        "all_exact": all_exact,
        "validity": validity,
        "validity_reason": reason,
        "wall_clock_seconds": round(time.time() - t_start, 3),
        "scientific_boundary": (
            "Stage 1 observes only the transport agreement rate and the "
            "static provenance boolean. No ADV, no D2 disposition."
        ),
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    print(json.dumps({
        "validity": validity,
        "all_exact": all_exact,
        "instances": instances,
        "seconds": raw["wall_clock_seconds"],
    }, indent=2))
    if validity != "valid":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
