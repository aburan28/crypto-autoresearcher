#!/usr/bin/env python3
"""Stage 2: Artin-Schreier level / genus agreement at shared-period pair c=3,9.

Declared method: magic-number / Ord_σ(γ) for γ in {B, sqrt(B)} under the
order-n Frobenius σ_c : x |-> x^{2^c} acting on F_{2^4} (coefficients live
in F_{16}). Genus candidates follow the GHS formula branch
g ∈ {2^{m-1}, 2^{m-1}-1}.

Requires stage1/. certificate.kind on run manifest is none.
Optional cost table labeled observational_open.
Does NOT claim a break or security ordering.
"""
from __future__ import annotations

import argparse
import io
import sys
import time
from contextlib import redirect_stdout
from math import gcd
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gf2n import Field
from period_tau import n_period
from runpack import EXP_ROOT, dump_yaml, utc_now, write_run_package

D = 4
PAIR = (3, 9)


def apply_poly_sigma(F: Field, coeffs: list[int], gamma: int, c: int) -> int:
    """Evaluate additive poly f=sum coeffs[i] X^i at σ, applied to gamma (char 2)."""
    acc = 0
    x = gamma
    for a in coeffs:
        if a & 1:
            acc ^= x
        x = F.frobenius(x, c)
    return acc


def ord_sigma(F: Field, gamma: int, c: int, n: int) -> dict:
    """Minimal monic Ord_σ(γ) in F_2[X] with Ord(σ)(γ)=0, searching deg <= n.

    Builds F2-linear dependence among {γ, σ(γ), ..., σ^n(γ)} via Gaussian
    elimination on bit coordinates in F_{2^{F.n}}.
    """
    # Vectors: for i=0..n, the F2-coords of σ^i(γ) as length-F.n bitvectors
    dim = F.n
    cols = n + 1
    # Matrix rows[bit] has bits for columns 0..n (powers) — we solve among first n+1
    # Actually: find smallest d and a0..a_{d-1} with σ^d(γ) = sum_{i<d} a_i σ^i(γ)
    vectors = []
    x = gamma
    for i in range(n + 1):
        vectors.append(x)
        x = F.frobenius(x, c)

    # GE on dim x (n+1) matrix; columns are vectors[0..n]
    # Represent each column as an int with dim bits
    # We search increasing degree d=1..n for dependence among columns 0..d
    for d in range(1, n + 1):
        # columns 0..d-1 and target column d: solve M a = v_d over F2
        # Augmented: dim rows, d cols + rhs
        rows = [0] * dim
        for j in range(d):
            v = vectors[j]
            for b in range(dim):
                if (v >> b) & 1:
                    rows[b] |= 1 << j
        rhs = vectors[d]
        for b in range(dim):
            if (rhs >> b) & 1:
                rows[b] |= 1 << d

        # GE
        mat = rows[:]
        piv_col = [-1] * dim
        r = 0
        consistent = True
        for col in range(d):
            piv = None
            for i in range(r, dim):
                if (mat[i] >> col) & 1:
                    piv = i
                    break
            if piv is None:
                continue
            mat[r], mat[piv] = mat[piv], mat[r]
            for i in range(dim):
                if i != r and ((mat[i] >> col) & 1):
                    mat[i] ^= mat[r]
            piv_col[r] = col
            r += 1
        for i in range(r, dim):
            if (mat[i] >> d) & 1:
                consistent = False
                break
        if not consistent:
            continue
        # Recover coefficients a0..a_{d-1}; monic X^d + sum a_i X^i
        a = [0] * d
        for i in range(r):
            col = piv_col[i]
            if col < 0:
                continue
            if (mat[i] >> d) & 1:
                a[col] = 1
        coeffs = a + [1]  # monic
        # Verify
        if apply_poly_sigma(F, coeffs, gamma, c) != 0:
            continue
        # Check minimality: no lower degree monic works — by increasing d search
        return {
            "degree_m": d,
            "coeffs_low_to_high": coeffs,
            "poly_string": " + ".join(
                (
                    ("1" if i == 0 and bit else f"X^{i}" if bit and i > 0 else "")
                    for i, bit in enumerate(coeffs)
                    if bit
                )
            ).replace("X^1", "X")
            or "0",
            "verified_annihilates": True,
        }
    raise RuntimeError(f"no Ord found for gamma={gamma} c={c} n={n}")


def genus_candidates(m: int) -> list[int]:
    if m < 1:
        return []
    g0 = 1 << (m - 1)
    return [g0, g0 - 1] if g0 - 1 >= 1 else [g0]


def load_stage1_curve() -> dict:
    path = EXP_ROOT / "stage1" / "frobenius-orbit-checks.yaml"
    if not path.exists():
        raise FileNotFoundError("stage1/frobenius-orbit-checks.yaml missing")
    data = yaml.safe_load(path.read_text())
    return data


def run_stage2(run_id: str, write_cost: bool) -> dict:
    stage1 = EXP_ROOT / "stage1"
    if not stage1.exists():
        raise FileNotFoundError("stage1/ missing; Stage 2 must wait for Stage 1")

    fr = load_stage1_curve()
    curve = fr["curve"]
    mod = fr["field_mod"]
    A, B = curve["A"], curve["B"]
    F = Field(4, mod)

    method = {
        "name": "ord_sigma_magic_number_on_F16",
        "description": (
            "Artin-Schreier / magic-number level m = deg(Ord_σ(γ)) for "
            "γ ∈ {B, sqrt(B)} under σ_c: x↦x^{2^c} on the coefficient field "
            "F_{2^4}. Genus candidates g ∈ {2^{m-1}, 2^{m-1}-1} (GHS branch). "
            "Full Weil-descent cover construction is not required for the "
            "H-0e3641-1 agreement test at this toy scale."
        ),
        "sqrt_convention": "char-2 square root via (n-1) squarings (unique bijection)",
    }

    sqrt_B = F.sqrt(B)
    per_c = []
    for c in PAIR:
        n = n_period(c, D)
        assert n == 4
        ord_B = ord_sigma(F, B, c, n)
        ord_sqrt = ord_sigma(F, sqrt_B, c, n)
        # Primary convention (d11575 dual): report both B and B^{1/2}
        m_B = ord_B["degree_m"]
        m_sqrt = ord_sqrt["degree_m"]
        per_c.append(
            {
                "c": c,
                "period_n": n,
                "gcd_c_d": gcd(c, D),
                "ord_B": ord_B,
                "ord_sqrt_B": ord_sqrt,
                "m_B": m_B,
                "m_sqrt_B": m_sqrt,
                "genus_candidates_from_m_B": genus_candidates(m_B),
                "genus_candidates_from_m_sqrt_B": genus_candidates(m_sqrt),
                "base_field_bits": c,
            }
        )

    # Agreement: same period => same m under each convention
    mB_vals = [r["m_B"] for r in per_c]
    mS_vals = [r["m_sqrt_B"] for r in per_c]
    agree_B = len(set(mB_vals)) == 1
    agree_S = len(set(mS_vals)) == 1
    genus_agree = agree_B and agree_S

    agreement = {
        "experiment_id": "EXP-BINSTD-f124db",
        "stage": 2,
        "observation_kind": "genus_agreement",
        "heuristic_under_test": "HEUR-BINSTD-6fe132-H1",
        "method": method,
        "curve_ref": {
            "A": A,
            "B": B,
            "mod": mod,
            "seed": curve.get("seed"),
            "source": "stage1/frobenius-orbit-checks.yaml",
        },
        "cells": per_c,
        "m_B_values": mB_vals,
        "m_sqrt_B_values": mS_vals,
        "m_B_agreement": agree_B,
        "m_sqrt_B_agreement": agree_S,
        "genus_agreement_shared_period": genus_agree,
        "instrument_unavailable": False,
        "cost_ordering_reported_open": True,
        "prediction_reference": "EXP-BINSTD-f124db preregistered_prediction (D)(E)",
        "certificate": {
            "kind": "none",
            "note": "AS-level/genus measurement; not a discrete_log claim",
        },
        "break_claim": False,
        "security_ordering_claim": False,
        "optimistic_assumptions_restated": [
            "Quarter-scale (d=4 vs d=16) may not preserve regime balance.",
            "k'=9 offers only one nontrivial proper divisor m1=3.",
            "Net cost ordering remains UNKNOWN (HEUR-H2).",
        ],
    }

    dump_yaml(EXP_ROOT / "stage2" / "genus-agreement.yaml", agreement)

    # Prefer exactly one of genus-agreement / instrument_unavailable.
    # Do NOT write instrument_unavailable when genus path succeeded.

    if write_cost:
        # Optional observational open cost table — measured wall not charged
        # for a real IC run; only labels the OPEN comparison framing.
        c_small, c_large = PAIR
        g_ref = per_c[0]["genus_candidates_from_m_sqrt_B"]
        cost = {
            "experiment_id": "EXP-BINSTD-f124db",
            "stage": 2,
            "observation_kind": "cost_table_observational_open",
            "label": "observational_open",
            "cost_ordering_reported_open": True,
            "direction": "unknown",
            "HEUR": "HEUR-BINSTD-6fe132-H2",
            "regime_split_declared": {
                "small_genus": "Gaudry/GTTD-style recalled small-genus IC (not executed)",
                "large_genus": "Enge-Gaudry L(1/2) recalled large-genus IC (not executed)",
                "note": (
                    "No index-calculus charged here; table records the OPEN "
                    "comparison frame only. Measured vs modeled columns separate."
                ),
            },
            "cells": [
                {
                    "c": c_small,
                    "q_bits": c_small,
                    "period_n": 4,
                    "genus_candidates": g_ref,
                    "charged_time": None,
                    "charged_memory": None,
                    "measured_or_modeled": "not_executed",
                },
                {
                    "c": c_large,
                    "q_bits": c_large,
                    "period_n": 4,
                    "genus_candidates": g_ref,
                    "charged_time": None,
                    "charged_memory": None,
                    "measured_or_modeled": "not_executed",
                },
            ],
            "security_ordering_claim": False,
            "break_claim": False,
            "scale_gap": "d=4 toy vs d=16 deployed; regime balance may differ",
        }
        dump_yaml(EXP_ROOT / "stage2" / "cost-table.yaml", cost)

    metrics = {
        "genus_agreement_shared_period": genus_agree,
        "m_B_agreement": agree_B,
        "m_sqrt_B_agreement": agree_S,
        "instrument_unavailable": False,
        "cost_ordering_reported_open": True,
        "m_B_values": mB_vals,
        "m_sqrt_B_values": mS_vals,
        "certificate_kind_none_rate": 1.0,
        "break_claim": False,
    }
    return {
        "metrics": metrics,
        "valid": genus_agree,
        "invalid_reason": None
        if genus_agree
        else "Stage 2 hard-fail: genus/AS-level disagreement at shared period",
        "parameters": {
            "curve_id": f"toy-f16-A{A}-B{B}",
            "seed": curve.get("seed"),
            "A": A,
            "B": B,
            "mod": mod,
            "pair": list(PAIR),
            "method": method["name"],
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--write-cost-table", action="store_true", default=True)
    ap.add_argument("--no-cost-table", action="store_true")
    args = ap.parse_args()
    write_cost = not args.no_cost_table
    started = utc_now()
    t0 = time.perf_counter()
    buf = io.StringIO()
    with redirect_stdout(buf):
        print(f"EXP-BINSTD-f124db Stage 2 run_id={args.run_id}")
        result = run_stage2(args.run_id, write_cost=write_cost)
        for k, v in result["metrics"].items():
            print(f"{k}={v}")
        print(f"valid={result['valid']}")
    wall = time.perf_counter() - t0
    finished = utc_now()
    write_run_package(
        args.run_id,
        stage=2,
        arm="genus-agreement",
        seed=result["parameters"].get("seed"),
        command=(
            f"python3 experiments/EXP-BINSTD-f124db/implementation/stage2_run.py "
            f"--run-id {args.run_id}"
            + (" --no-cost-table" if not write_cost else "")
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
            "Stage 2 AS-level/genus agreement measurement; certificate.kind=none; "
            "cost left OPEN; no break/security-ordering claim"
        ),
    )
    print(buf.getvalue(), end="")


if __name__ == "__main__":
    main()
