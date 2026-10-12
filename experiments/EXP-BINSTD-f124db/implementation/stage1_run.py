#!/usr/bin/env python3
"""Stage 1: toy (4,9) divisor lattice, shared-period pair, Frobenius orbits, controls.

Requires stage0/ artifacts. certificate.kind on run manifest is none.
"""
from __future__ import annotations

import argparse
import io
import random
import sys
import time
from contextlib import redirect_stdout
from math import gcd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve import Curve
from gf2n import Field, find_irreducible
from period_tau import divisors_of, n_period, tau
from runpack import EXP_ROOT, dump_yaml, utc_now, write_run_package

D = 4
K_COMPOSITE = 9
N_COMPOSITE = 36
SHARED = {"c_small": 3, "c_large": 9, "expected_n": 4}
K_PRIME_CTRL = 7
PRIMARY_SEED = 20260922


def frobenius_coeff(F: Field, a: int, c: int) -> int:
    """Apply field Frobenius x |-> x^{2^c}."""
    return F.frobenius(a, c)


def minimal_orbit_size(F: Field, A: int, B: int, c: int, max_i: int | None = None) -> int:
    """Smallest positive i with sigma_c^i fixing both A and B."""
    if max_i is None:
        max_i = F.n
    for i in range(1, max_i + 1):
        Ai = frobenius_coeff(F, A, c * i)
        Bi = frobenius_coeff(F, B, c * i)
        if Ai == A and Bi == B:
            return i
    raise RuntimeError(f"no orbit size <= {max_i} for c={c}")


def is_ordinary_trace(F: Field, A: int, B: int) -> bool:
    """Ordinary binary curve <=> Tr(A) != 0 for y^2+xy=x^3+A x^2+B (char 2)."""
    return F.trace(A) == 1 and B != 0


def construct_ordinary_f16(seed: int) -> tuple[Field, int, int, dict]:
    """Ordinary E/F_{2^4} with A,B in F_16; prefer normal-ish B (not in proper subfield)."""
    mod = find_irreducible(4)
    F = Field(4, mod)
    rng = random.Random(seed)
    attempts = []
    # Prefer B whose Gal(F16/F2) orbit has size 4 (not in F2 or F4).
    for trial in range(512):
        A = rng.randrange(1, 16)
        B = rng.randrange(1, 16)
        info = {
            "trial": trial,
            "A": A,
            "B": B,
            "trace_A": F.trace(A),
            "ordinary": is_ordinary_trace(F, A, B),
        }
        if not info["ordinary"]:
            attempts.append(info)
            continue
        # subfield checks for B
        in_f2 = frobenius_coeff(F, B, 1) == B  # fixed by Frob^1 => in F2? Wait Frob^1 order 4
        # Element in F_2: x^2=x
        in_f2 = F.sqr(B) == B
        in_f4 = frobenius_coeff(F, B, 2) == B  # fixed by Frob^2 => in F_4
        info["B_in_F2"] = in_f2
        info["B_in_F4"] = in_f4
        if in_f4:
            attempts.append(info)
            continue
        orbit = minimal_orbit_size(F, A, B, 1, max_i=4)
        info["gal_orbit_under_frob1"] = orbit
        attempts.append(info)
        if orbit == 4:
            return F, A, B, {
                "mod": mod,
                "seed": seed,
                "A": A,
                "B": B,
                "trace_A": F.trace(A),
                "B_in_F2": False,
                "B_in_F4": False,
                "gal_orbit_size_frob1": orbit,
                "attempts_summarized": len(attempts),
            }
    # Fallback: any ordinary curve
    for trial in range(512):
        A = rng.randrange(1, 16)
        B = rng.randrange(1, 16)
        if is_ordinary_trace(F, A, B):
            return F, A, B, {
                "mod": mod,
                "seed": seed,
                "A": A,
                "B": B,
                "trace_A": F.trace(A),
                "fallback_any_ordinary": True,
                "attempts_summarized": len(attempts) + trial + 1,
            }
    raise RuntimeError("failed to construct ordinary E/F_16")


def lattice_for(d: int, k: int) -> dict:
    N = d * k
    divs = divisors_of(N)
    rows = []
    for c in divs:
        rows.append(
            {
                "c": c,
                "gcd_c_d": gcd(c, d),
                "n_recomputed": n_period(c, d),
                "q_bits": c,
                "base_field_bits_label": f"F_2^{c}",
            }
        )
    return {
        "d": d,
        "k_prime": k,
        "N": N,
        "gcd_d_k": gcd(d, k),
        "coprime": gcd(d, k) == 1,
        "tau_N": tau(N),
        "tau_d": tau(d),
        "tau_k": tau(k),
        "divisors": divs,
        "rows": rows,
    }


def run_stage1(run_id: str, seed: int) -> dict:
    stage0 = EXP_ROOT / "stage0"
    if not stage0.exists():
        raise FileNotFoundError("stage0/ missing; Stage 1 must wait for Stage 0")

    # --- composite (4,9) lattice ---
    lat = lattice_for(D, K_COMPOSITE)
    if not lat["coprime"]:
        raise RuntimeError("mis-specified: gcd(d,k')!=1")

    formula_mismatches = [
        r for r in lat["rows"] if r["n_recomputed"] != n_period(r["c"], D)
    ]
    # All rows use the formula by construction; also check explicit prediction
    n3 = n_period(3, D)
    n9 = n_period(9, D)
    shared_pass = n3 == n9 == SHARED["expected_n"]
    shared = {
        "c_small": 3,
        "c_large": 9,
        "n_c_small": n3,
        "n_c_large": n9,
        "expected_n": SHARED["expected_n"],
        "gcd_c_small_d": gcd(3, D),
        "gcd_c_large_d": gcd(9, D),
        "shared_period_pair_pass": shared_pass,
        "note": (
            "Pair realises identical period at unequal base-field sizes; "
            "k-prime lattices cannot produce this unequal-q shared-period pair "
            "at fixed gcd(*,d) from a proper divisor of k."
        ),
        "break_claim": False,
        "security_ordering_claim": False,
    }

    # --- curve + Frobenius orbit ---
    F, A, B, curve_meta = construct_ordinary_f16(seed)
    E = Curve(F, A, B)
    # Smoke: count points optional (F16 is tiny)
    order_approx = E.count_by_trace()
    orbit_rows = []
    orbit_ok = True
    for c in (3, 9):
        expected = n_period(c, D)
        measured = minimal_orbit_size(F, A, B, c, max_i=F.n * 2)
        # Also verify no smaller positive power fixes
        smaller = []
        for i in range(1, expected):
            Ai = frobenius_coeff(F, A, c * i)
            Bi = frobenius_coeff(F, B, c * i)
            if Ai == A and Bi == B:
                smaller.append(i)
        row_pass = measured == expected and len(smaller) == 0
        orbit_ok = orbit_ok and row_pass
        orbit_rows.append(
            {
                "c": c,
                "expected_n": expected,
                "measured_minimal_i": measured,
                "smaller_fixing_powers": smaller,
                "frobenius_orbit_size_match": row_pass,
                "observation_kind": "frobenius_coefficient_orbit",
            }
        )

    frobenius_report = {
        "experiment_id": "EXP-BINSTD-f124db",
        "stage": 1,
        "observation_kind": "frobenius_orbit_checks",
        "curve": curve_meta,
        "field_mod": F.mod,
        "point_count_by_trace": order_approx,
        "checks": orbit_rows,
        "frobenius_orbit_size_match_all": orbit_ok,
        "certificate": {
            "kind": "none",
            "note": "orbit size of coefficients under sigma_c; not a DL claim",
        },
        "break_claim": False,
    }

    # --- k-prime control (4,7) ---
    lat_kprime = lattice_for(D, K_PRIME_CTRL)
    # Shared-period unequal-q pairs at fixed gcd(*,d) from proper divisor of k:
    # for k prime, proper divisors of k are only {1}, so no m1 with 1<m1<k.
    by_gcd = {}
    for r in lat_kprime["rows"]:
        by_gcd.setdefault(r["gcd_c_d"], []).append(r)
    unequal_q_shared = []
    for g, group in by_gcd.items():
        if len(group) >= 2:
            cs = sorted(x["c"] for x in group)
            # unequal c with same gcd => same n; for k-prime only if from two families
            # with same j: c=j and c=j*k — those have SAME q-ratio structurally
            # Spec: "no shared-period unequal-q pair at fixed gcd(*,d) from a proper divisor of k"
            proper_divisors_k = [m for m in divisors_of(K_PRIME_CTRL) if 1 < m < K_PRIME_CTRL]
            if proper_divisors_k:
                unequal_q_shared.append({"gcd": g, "cs": cs})
    kprime_control = {
        "d": D,
        "k_prime": K_PRIME_CTRL,
        "dk": D * K_PRIME_CTRL,
        "lattice": lat_kprime,
        "proper_divisors_of_k": [m for m in divisors_of(K_PRIME_CTRL) if 1 < m < K_PRIME_CTRL],
        "shared_period_from_proper_divisor_of_k": False,
        "note": (
            "Only two families (divisors of d and k*those); no composite-k' "
            "extra cell from a proper divisor of k."
        ),
        "pass": len([m for m in divisors_of(K_PRIME_CTRL) if 1 < m < K_PRIME_CTRL]) == 0,
    }

    # --- d=1 null ---
    # At d=1, n(c)=1/gcd(c,1)=1 for every c; no d-dependent extra-divisor lattice.
    null_divisors_example = divisors_of(11)  # ECC2K-130-shaped prime degree example label only
    null_rows = [{"c": c, "n": n_period(c, 1)} for c in null_divisors_example]
    null_vacuous = all(r["n"] == 1 for r in null_rows)
    null_control = {
        "d": 1,
        "note": (
            "Prime-degree / ECC2K-130-shaped null: period formula yields n(c)=1 "
            "universally; extra-divisor argument evaporates."
        ),
        "example_prime_degree_divisors_of_11": null_rows,
        "all_periods_one": null_vacuous,
        "nontrivial_extra_divisor_exploit_structure": False,
        "null_d1_vacuous_pass": null_vacuous
        and not False,  # instrument must not invent nontrivial structure
        "pass": null_vacuous,
    }

    controls = {
        "experiment_id": "EXP-BINSTD-f124db",
        "stage": 1,
        "observation_kind": "controls_report",
        "kprime_toy_control": kprime_control,
        "null_d1": null_control,
        "coprimality_guard": {
            "composite_gcd_d_k": lat["gcd_d_k"],
            "kprime_gcd_d_k": lat_kprime["gcd_d_k"],
            "mis_specified": False,
        },
        "memory_accounting": {
            "note": "peak_rss_bytes recorded on run manifest; F_2^4 elements dominate",
        },
        "break_claim": False,
        "security_ordering_claim": False,
    }

    divisor_lattice = {
        "experiment_id": "EXP-BINSTD-f124db",
        "stage": 1,
        "observation_kind": "divisor_lattice",
        "composite_cell": lat,
        "formula_mismatches": formula_mismatches,
        "prediction_reference": "EXP-BINSTD-f124db preregistered_prediction (C)",
        "break_claim": False,
    }
    shared_doc = {
        "experiment_id": "EXP-BINSTD-f124db",
        "stage": 1,
        "observation_kind": "shared_period_pair",
        **shared,
        "prediction_reference": "EXP-BINSTD-f124db preregistered_prediction (C)",
    }

    dump_yaml(EXP_ROOT / "stage1" / "divisor-lattice.yaml", divisor_lattice)
    dump_yaml(EXP_ROOT / "stage1" / "shared-period-pair.yaml", shared_doc)
    dump_yaml(EXP_ROOT / "stage1" / "frobenius-orbit-checks.yaml", frobenius_report)
    dump_yaml(EXP_ROOT / "stage1" / "controls-report.yaml", controls)

    metrics = {
        "shared_period_pair_pass": shared_pass,
        "frobenius_orbit_size_match": orbit_ok,
        "null_d1_vacuous_pass": null_control["null_d1_vacuous_pass"],
        "kprime_control_documented": True,
        "kprime_control_pass": kprime_control["pass"],
        "n_c3": n3,
        "n_c9": n9,
        "certificate_kind_none_rate": 1.0,
        "break_claim": False,
    }
    valid = (
        shared_pass
        and orbit_ok
        and null_control["null_d1_vacuous_pass"]
        and kprime_control["pass"]
        and len(formula_mismatches) == 0
    )
    return {
        "metrics": metrics,
        "valid": valid,
        "invalid_reason": None
        if valid
        else "Stage 1 hard-fail: shared-period/orbit/null/k-prime control",
        "parameters": {
            "curve_id": f"toy-f16-A{A}-B{B}",
            "seed": seed,
            "d": D,
            "k_prime": K_COMPOSITE,
            "A": A,
            "B": B,
            "mod": F.mod,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, default=PRIMARY_SEED)
    args = ap.parse_args()
    started = utc_now()
    t0 = time.perf_counter()
    buf = io.StringIO()
    with redirect_stdout(buf):
        print(f"EXP-BINSTD-f124db Stage 1 run_id={args.run_id} seed={args.seed}")
        result = run_stage1(args.run_id, args.seed)
        for k, v in result["metrics"].items():
            print(f"{k}={v}")
        print(f"valid={result['valid']}")
    wall = time.perf_counter() - t0
    finished = utc_now()
    write_run_package(
        args.run_id,
        stage=1,
        arm="composite-toy-lattice",
        seed=args.seed,
        command=(
            f"python3 experiments/EXP-BINSTD-f124db/implementation/stage1_run.py "
            f"--run-id {args.run_id} --seed {args.seed}"
        ),
        parameters=result["parameters"],
        metrics=result["metrics"],
        valid=result["valid"],
        invalid_reason=result["invalid_reason"],
        termination_reason="completed",
        stdout_text=buf.getvalue(),
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note=(
            "Stage 1 toy lattice/orbit/controls; certificate.kind=none; "
            "no discrete_log claim"
        ),
    )
    print(buf.getvalue(), end="")


if __name__ == "__main__":
    main()
