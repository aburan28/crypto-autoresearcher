"""Stage 3 for EXP-ECDLP-a98ea9: T1-T4 digit ADV on the declared band.

Main measurement only. q_maj is exact (complete enumeration). ADV is
recorded as an observation. This file does not compute D, does not apply
CLOSURE/LEAD/INCONCLUSIVE, does not fit beta as a claim, and does not
authorize Stage 4 or 5.

Tested scale is disclosed: seven prime orders in the 16-19 bit part of
the 16-26 bit band, spanning more than 6x. The 20-26 bit cells are not
run and are not claimed.
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy

from ec_jac import Curve, affine_xy, is_infinity, jac_add, jac_infinity
from kfree_transport import canonical_order_n_lift, ordinary_base_p_digits
from qmaj import q_maj_exact
from runrecord import _dump_yaml, write_run_record
from static_provenance import check_kfree_module

HERE = Path(__file__).resolve().parent
RUN_DIR = HERE.parent / "runs" / "RUN-ECDLP-a98ea9-S3"
REPORT_PATH = HERE.parent / "execution-report-stage3.yaml"
TASK_ID = "TASK-20260907-5947b6"
SEEDS = [3, 5, 7, 11, 13, 17, 19, 23]
RS = (1, 2, 3, 4)
SS = (2, 3, 4, 5, 6, 7, 8)

# Six Stage 1 instances (DEV-2 band) plus one 19-bit prime-order curve
# so the package meets "at least six prime orders" and "at least 6x"
# inside the 16-26 bit band. The sixth Stage 1 order is 162611; the
# added order is 375391 (ratio vs smallest Stage 1 n=39503 is ~9.50).
INSTANCES = [
    {"id": "S1-a", "p": 47237, "A": 31367, "B": 41141, "N": 47057, "n": 47057, "S": (2, 97), "source": "RUN-ECDLP-a98ea9-S1"},
    {"id": "S1-b", "p": 128629, "A": 119056, "B": 83257, "N": 128001, "n": 42667, "S": (87124, 110926), "source": "RUN-ECDLP-a98ea9-S1"},
    {"id": "S1-c", "p": 234527, "A": 185876, "B": 26302, "N": 233812, "n": 58453, "S": (159550, 198939), "source": "RUN-ECDLP-a98ea9-S1"},
    {"id": "S1-d", "p": 325411, "A": 259076, "B": 82146, "N": 325222, "n": 162611, "S": (255196, 53661), "source": "RUN-ECDLP-a98ea9-S1"},
    {"id": "S1-e", "p": 949423, "A": 610648, "B": 188380, "N": 948072, "n": 39503, "S": (377953, 722598), "source": "RUN-ECDLP-a98ea9-S1"},
    {"id": "S1-f", "p": 1422461, "A": 1184784, "B": 515035, "N": 1422774, "n": 79043, "S": (616886, 329503), "source": "RUN-ECDLP-a98ea9-S1"},
    {
        "id": "S3-span",
        "p": 374639,
        "A": 315643,
        "B": 116233,
        "N": 375391,
        "n": 375391,
        "S": (1, 172378),
        "source": "find_curve(bits=19, seed=101, bit_lo=18, bit_hi=19)",
    },
]


def _frac(q: Fraction) -> str:
    return f"{q.numerator}/{q.denominator}"


def _bucket(value: int, modulus: int, s: int) -> int:
    """Integer interval bucket. Matches int(x*s/modulus) for modulus < 2^53."""
    if modulus <= 0 or s <= 0:
        raise ValueError("modulus and s must be positive")
    return min((int(value) * s) // modulus, s - 1)


def _legendre_label(digit: int, p: int) -> int:
    """0 if digit==0, 1 if QR, 2 if QNR."""
    if digit % p == 0:
        return 0
    return 1 if pow(digit, (p - 1) // 2, p) == 1 else 2


def _walk_lifts(curve: Curve, S, n: int, r: int) -> dict:
    """Walk [k]S-hat at precision r. Identity (k=0) has no affine x."""
    Shat = canonical_order_n_lift(curve, S, n, r)
    mod = curve.p**r
    P = jac_infinity()
    xs: list[int | None] = []
    digits: list[list[int] | None] = []
    for _k in range(n):
        if is_infinity(P, mod):
            xs.append(None)
            digits.append(None)
        else:
            ax, _ay = affine_xy(curve, P, mod)
            xs.append(int(ax))
            digits.append(ordinary_base_p_digits(ax, curve.p, r))
        P = jac_add(curve, P, Shat, mod)
    closed = is_infinity(P, mod)
    identity_count = sum(1 for x in xs if x is None)
    return {
        "xs": xs,
        "digits": digits,
        "walk_closed": closed,
        "identity_count": identity_count,
        "identity_at_k0": xs[0] is None,
    }


def _labels_t1(digits: list, j: int, p: int, s: int) -> np.ndarray:
    v = np.empty(len(digits), dtype=np.int64)
    for k, d in enumerate(digits):
        if d is None:
            v[k] = 0
        else:
            v[k] = _bucket(d[j], p, s)
    return v


def _labels_t2(digits: list, j: int, p: int) -> np.ndarray:
    v = np.empty(len(digits), dtype=np.int64)
    for k, d in enumerate(digits):
        if d is None:
            v[k] = 0
        else:
            v[k] = _legendre_label(d[j], p)
    return v


def _labels_t3(xs: list, modulus: int, s: int) -> np.ndarray:
    v = np.empty(len(xs), dtype=np.int64)
    for k, x in enumerate(xs):
        if x is None:
            v[k] = 0
        else:
            v[k] = _bucket(x, modulus, s)
    return v


def _labels_t4(digits: list, p: int, s: int) -> np.ndarray:
    alphabet = p * p
    v = np.empty(len(digits), dtype=np.int64)
    for k, d in enumerate(digits):
        if d is None:
            v[k] = 0
        else:
            v[k] = _bucket(d[0] + d[1] * p, alphabet, s)
    return v


def _cell(statistic: str, inst: dict, r: int, s: int, q: Fraction, extra: dict | None = None) -> dict:
    adv = q - Fraction(1, s)
    row = {
        "statistic": statistic,
        "instance_id": inst["id"],
        "p": inst["p"],
        "n": inst["n"],
        "r": r,
        "s": s,
        "q_maj": _frac(q),
        "q_maj_float": float(q),
        "ADV": _frac(adv),
        "ADV_float": float(adv),
        "estimator": "q_maj_exact (FFT pair-counts)",
        "enumeration": "complete",
        "identity_label": 0,
    }
    if extra:
        row.update(extra)
    return row


def _check_instance(inst: dict) -> dict:
    p, A, B, n, N = inst["p"], inst["A"], inst["B"], inst["n"], inst["N"]
    S = tuple(inst["S"])
    reasons = []
    if not sympy.isprime(n):
        reasons.append("n_not_prime")
    if not sympy.isprime(p):
        reasons.append("p_not_prime")
    if n.bit_length() < 16 or n.bit_length() > 26:
        reasons.append("n_outside_16_26")
    if p % n == 0 or n % p == 0:
        reasons.append("gcd_n_p_not_1")
    if N == p:
        reasons.append("anomalous")
    if N == p + 1:
        reasons.append("supersingular")
    disc = (-16 * (4 * A**3 + 27 * B**2)) % p
    if disc == 0:
        reasons.append("singular")
    rhs = (S[0] ** 3 + A * S[0] + B) % p
    if rhs != (S[1] * S[1]) % p:
        reasons.append("S_not_on_curve")
    return {
        "instance_id": inst["id"],
        "p": p,
        "n": n,
        "bits_n": n.bit_length(),
        "bits_p": p.bit_length(),
        "disc_mod_p": disc,
        "pass": not reasons,
        "reasons": reasons,
    }


def main() -> int:
    t0 = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    provenance = check_kfree_module(HERE / "kfree_transport.py")
    checks = [_check_instance(inst) for inst in INSTANCES]
    ns = [inst["n"] for inst in INSTANCES]
    span = max(ns) / min(ns)
    scale = {
        "declared_band_bits": [16, 26],
        "tested_n": ns,
        "tested_bits_n": [n.bit_length() for n in ns],
        "n_min": min(ns),
        "n_max": max(ns),
        "span_ratio": span,
        "span_at_least_6x": span >= 6.0,
        "instance_count": len(INSTANCES),
        "at_least_six_prime_orders": len(INSTANCES) >= 6,
        "band_top_26_bit_tested": False,
        "band_20_to_26_tested": False,
        "disclosure": (
            "Complete enumeration on seven prime orders in the 16-19 bit "
            "part of the declared 16-26 bit band. Span vs smallest n is "
            f"{span:.4f} (>= 6). 20-26 bit cells were not run and are "
            "not claimed. DEV-2 is not used as a license to stop at the "
            "Stage 1 16-18 bit set: S3-span (n=375391) was added."
        ),
    }
    cells: list[dict] = []
    walk_reports: list[dict] = []
    walk_ok = True
    for inst in INSTANCES:
        curve = Curve(inst["p"], inst["A"], inst["B"])
        n = inst["n"]
        S = tuple(inst["S"])
        for r in RS:
            t_walk = time.time()
            walked = _walk_lifts(curve, S, n, r)
            walk_s = time.time() - t_walk
            ok = walked["walk_closed"] and walked["identity_count"] == 1 and walked["identity_at_k0"]
            walk_ok = walk_ok and ok
            walk_reports.append({
                "instance_id": inst["id"],
                "n": n,
                "r": r,
                "walk_closed": walked["walk_closed"],
                "identity_count": walked["identity_count"],
                "identity_at_k0": walked["identity_at_k0"],
                "walk_seconds": round(walk_s, 3),
                "pass": ok,
            })
            print(f"walk {inst['id']} n={n} r={r} {walk_s:.2f}s ok={ok}", flush=True)
            xs = walked["xs"]
            digits = walked["digits"]
            modulus = inst["p"] ** r
            for s in SS:
                for j in range(min(3, r)):
                    t_q = time.time()
                    q = q_maj_exact(_labels_t1(digits, j, inst["p"], s), n)
                    cells.append(_cell(f"T1_digit{j}", inst, r, s, q, {"j": j, "q_seconds": round(time.time() - t_q, 3)}))
                t_q = time.time()
                q = q_maj_exact(_labels_t3(xs, modulus, s), n)
                cells.append(_cell("T3_x_interval", inst, r, s, q, {
                    "definition": "min((x*s)//p^r, s-1) on affine x in [0, p^r)",
                    "q_seconds": round(time.time() - t_q, 3),
                }))
                if r >= 2:
                    t_q = time.time()
                    q = q_maj_exact(_labels_t4(digits, inst["p"], s), n)
                    cells.append(_cell("T4_digit0_digit1", inst, r, s, q, {
                        "definition": "min(((d0+d1*p)*s)//p^2, s-1)",
                        "q_seconds": round(time.time() - t_q, 3),
                    }))
            for j in range(min(3, r)):
                t_q = time.time()
                lab = _labels_t2(digits, j, inst["p"])
                q = q_maj_exact(lab, n)
                cells.append(_cell("T2_legendre", inst, r, 3, q, {
                    "j": j,
                    "image": "0=zero, 1=QR, 2=QNR",
                    "s_note": "natural image size 3; not swept over s=2..8",
                    "q_seconds": round(time.time() - t_q, 3),
                }))
            print(f"  cells so far {len(cells)}", flush=True)

    hard_gates = {
        "static_provenance": bool(provenance.get("passed")),
        "instance_precheck": all(c["pass"] for c in checks),
        "walk_closed_identity": walk_ok,
        "six_prime_orders": scale["at_least_six_prime_orders"],
        "span_at_least_6x": scale["span_at_least_6x"],
        "all_n_in_16_26": all(16 <= n.bit_length() <= 26 for n in ns),
    }
    passed = all(hard_gates.values())
    raw = {
        "stage": 3,
        "run_id": "RUN-ECDLP-a98ea9-S3",
        "experiment_id": "EXP-ECDLP-a98ea9",
        "hypothesis_id": "H-ECDLP-07c7c6",
        "task_id": TASK_ID,
        "amendment": "v4_stage3_authorized",
        "authorized_stages": [0, 1, 2, 3],
        "certificate": {"kind": "none"},
        "digit_ADV_computed": True,
        "D_computed": False,
        "two_branch_applied": False,
        "beta_fitted_as_claim": False,
        "stage4_authorized": False,
        "stage5_authorized": False,
        "static_provenance": provenance,
        "instance_precheck": checks,
        "tested_scale": scale,
        "identity_convention": (
            "k=0 is the identity and has no affine x. That one label is 0. "
            "Disclosed; one point in n >= 39503."
        ),
        "statistic_definitions": {
            "T1_digitj": "ordinary base-p digit j of affine x, interval-bucketed into s classes via min((d_j*s)//p, s-1); j in {0,1,2} and j < r",
            "T2_legendre": "quadratic character of digit j: 0 if d_j=0, 1 if QR, 2 if QNR; natural s=3",
            "T3_x_interval": "interval bucket of the full representative x in [0, p^r): min((x*s)//p^r, s-1)",
            "T4_digit0_digit1": "pair (d0,d1) as d0+d1*p, interval-bucketed into s classes over p^2; r>=2 only",
        },
        "walk": walk_reports,
        "cells": cells,
        "cell_count": len(cells),
        "hard_gates": hard_gates,
        "validity": "valid" if passed else "gate_failure",
        "validity_reason": (
            "Stage 3 complete-enumeration T1-T4 ADV recorded; D and two-branch not applied"
            if passed
            else f"gate failure: {[k for k, v in hard_gates.items() if not v]}"
        ),
        "scientific_boundary": (
            "Stage 3 observations only. ADV cells are not H support. "
            "No D, no CLOSURE/LEAD/INCONCLUSIVE, no Stage 4/5, no D2."
        ),
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    wall = time.time() - t0
    summary = {
        "hard_gates": hard_gates,
        "cell_count": len(cells),
        "tested_scale": {k: scale[k] for k in (
            "n_min", "n_max", "span_ratio", "span_at_least_6x",
            "instance_count", "band_top_26_bit_tested",
        )},
        "validity": raw["validity"],
        "digit_ADV_computed": True,
        "D_computed": False,
        "two_branch_applied": False,
        "wall_clock_seconds": round(wall, 3),
    }
    write_run_record(
        RUN_DIR,
        stage="3",
        command="python3 implementation/stage3.py",
        params={
            "authorized_stages": [0, 1, 2, 3],
            "r": list(RS),
            "s": list(SS),
            "instance_ids": [inst["id"] for inst in INSTANCES],
            "seeds_declared_unused_for_ADV": SEEDS,
        },
        seeds={"declared": SEEDS, "note": "ADV is exact enumeration; seeds do not enter Stage 3 cells."},
        validity=raw["validity"],
        validity_reason=raw["validity_reason"],
        wall_clock_s=wall,
        stdout=json.dumps(summary, indent=2) + "\n",
        stderr="",
        raw_result_file="raw-result.json",
        model_id="cursor-grok-4.6-cloud-agent",
        repo_root=HERE.parents[2],
        extra_artifacts={},
        task_id=TASK_ID,
        scientific_boundary=(
            "Stage 3 T1-T4 ADV observations only. No D, no two-branch, "
            "no Stage 4/5, no D2 disposition."
        ),
    )
    report = {
        "execution_report": {
            "experiment_id": "EXP-ECDLP-a98ea9",
            "hypothesis_id": "H-ECDLP-07c7c6",
            "task_id": TASK_ID,
            "run_id": "RUN-ECDLP-a98ea9-S3",
            "amendment": "v4_stage3_authorized",
            "authorized_stages": [0, 1, 2, 3],
            "certificate": {"kind": "none"},
            "digit_ADV_computed": True,
            "D_computed": False,
            "two_branch_applied": False,
            "beta_fitted_as_claim": False,
            "hard_gates": hard_gates,
            "cell_count": len(cells),
            "tested_scale": scale,
            "validity": raw["validity"],
            "validity_reason": raw["validity_reason"],
            "wall_clock_seconds": round(wall, 3),
            "scientific_boundary": (
                "Stage 3 only under v4_stage3_authorized. ADV cells are "
                "observations. No D, no two-branch, no Stage 4/5, no D2."
            ),
        }
    }
    REPORT_PATH.write_text(_dump_yaml(report) + "\n")
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
