#!/usr/bin/env python3
"""Blind re-derivation of T1_digit0 q_maj on S1-a.

Standalone enumerator. Implements F_p Weierstrass addition and FFT
pair-counts locally. Does not import anything under
experiments/EXP-ECDLP-a98ea9/implementation/.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np

# Parameters from review_plan.blind_rederivation.parameters only.
P = 47237
A = 31367
B = 41141
N_ORDER = 47057
SX, SY = 2, 97
S_IMAGE = 2
IDENTITY_LABEL = 0


def _modinv(x: int, mod: int) -> int:
    return pow(int(x) % mod, -1, mod)


def on_curve(pt: tuple[int, int] | None) -> bool:
    if pt is None:
        return True
    x, y = pt
    lhs = (y * y) % P
    rhs = (pow(x, 3, P) + (A * x) % P + B) % P
    return lhs == rhs


def ec_add(p1: tuple[int, int] | None, p2: tuple[int, int] | None) -> tuple[int, int] | None:
    """Affine addition on y^2 = x^3 + A x + B over F_P. None is the identity."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None
        # Doubling: lambda = (3 x1^2 + A) / (2 y1)
        num = (3 * x1 * x1 + A) % P
        den = (2 * y1) % P
        lam = (num * _modinv(den, P)) % P
    else:
        num = (y2 - y1) % P
        den = (x2 - x1) % P
        lam = (num * _modinv(den, P)) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def digit0_label(pt: tuple[int, int] | None, s: int) -> int:
    if pt is None:
        return IDENTITY_LABEL
    x, _y = pt
    return min((x * s) // P, s - 1)


def circular_conv_fft(u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, float]:
    """Exact-length-n circular convolution via FFT; return (real conv, max |imag|)."""
    fu = np.fft.fft(u)
    fv = np.fft.fft(v)
    conv = np.fft.ifft(fu * fv)
    imag_err = float(np.max(np.abs(conv.imag)))
    return conv.real, imag_err


def recover_nonneg_ints(values: np.ndarray, abs_tol: float = 1e-6) -> tuple[np.ndarray, float]:
    """Round real values to nearest integer with a rounding-error check."""
    rounded = np.rint(values)
    err = float(np.max(np.abs(values - rounded)))
    if err >= abs_tol:
        raise RuntimeError(f"FFT rounding error {err} exceeds tolerance {abs_tol}")
    if np.any(rounded < -0.5):
        raise RuntimeError("FFT recovered a negative count")
    return rounded.astype(np.int64), err


def walk_labels() -> tuple[np.ndarray, dict]:
    gen = (SX, SY)
    if not on_curve(gen):
        raise RuntimeError("generator S is not on the curve")

    labels = np.empty(N_ORDER, dtype=np.int8)
    pt: tuple[int, int] | None = None  # [0]S = identity
    early_identity = 0
    off_curve = 0
    for k in range(N_ORDER):
        if k > 0 and pt is None:
            early_identity += 1
        if not on_curve(pt):
            off_curve += 1
        labels[k] = digit0_label(pt, S_IMAGE)
        pt = ec_add(pt, gen)

    walk_closed = pt is None
    if not walk_closed:
        raise RuntimeError("[n]S is not the identity; walk did not close")
    if early_identity:
        raise RuntimeError(f"identity appeared at {early_identity} nonzero k < n")
    if off_curve:
        raise RuntimeError(f"{off_curve} walk points failed the curve equation")

    fiber_sizes = {int(a): int(np.sum(labels == a)) for a in range(S_IMAGE)}
    checksum = {
        "walk_closed_identity": walk_closed,
        "early_identity_count": early_identity,
        "off_curve_count": off_curve,
        "fiber_sizes": fiber_sizes,
        "label_sum": int(np.sum(labels)),
        "n": N_ORDER,
    }
    return labels, checksum


def pair_counts(labels: np.ndarray) -> tuple[np.ndarray, dict]:
    n = labels.shape[0]
    s = S_IMAGE
    indicators = [np.where(labels == a, 1.0, 0.0) for a in range(s)]
    N_abc = np.zeros((s, s, s), dtype=np.int64)
    fft_imag_errs: list[float] = []
    fft_round_errs: list[float] = []

    for a in range(s):
        for b in range(s):
            conv_real, imag_err = circular_conv_fft(indicators[a], indicators[b])
            fft_imag_errs.append(imag_err)
            conv_int, round_err = recover_nonneg_ints(conv_real)
            fft_round_errs.append(round_err)
            # conv_int[m] = # {(k, ell) : v(k)=a, v(ell)=b, (k+ell) mod n = m}
            for c in range(s):
                N_abc[a, b, c] = int(np.sum(conv_int[labels == c]))

    total = int(N_abc.sum())
    expected_total = n * n
    if total != expected_total:
        raise RuntimeError(f"pair-count sum {total} != n^2 {expected_total}")

    fiber_sizes = [int(np.sum(labels == a)) for a in range(s)]
    for a in range(s):
        for b in range(s):
            row = int(N_abc[a, b].sum())
            expected_row = fiber_sizes[a] * fiber_sizes[b]
            if row != expected_row:
                raise RuntimeError(
                    f"N[{a},{b},*] sum {row} != |A_{a}|*|A_{b}| {expected_row}"
                )

    checksum = {
        "pair_count_sum": total,
        "n_squared": expected_total,
        "fft_max_imag_abs": max(fft_imag_errs) if fft_imag_errs else 0.0,
        "fft_max_round_abs": max(fft_round_errs) if fft_round_errs else 0.0,
        "fiber_sizes": {str(i): fiber_sizes[i] for i in range(s)},
        "row_products_ok": True,
    }
    return N_abc, checksum


def q_maj_from_N(N_abc: np.ndarray) -> Fraction:
    n = N_ORDER
    maj = 0
    for a in range(S_IMAGE):
        for b in range(S_IMAGE):
            maj += int(np.max(N_abc[a, b]))
    return Fraction(maj, n * n)


def main() -> None:
    labels, walk_checksum = walk_labels()
    N_abc, pair_checksum = pair_counts(labels)
    q = q_maj_from_N(N_abc)

    n_abc_records = []
    max_c_records = []
    for a in range(S_IMAGE):
        for b in range(S_IMAGE):
            support = []
            for c in range(S_IMAGE):
                count = int(N_abc[a, b, c])
                n_abc_records.append({"a": a, "b": b, "c": c, "count": count})
                if count > 0:
                    support.append(c)
            max_c_records.append(
                {
                    "a": a,
                    "b": b,
                    "max_N": int(np.max(N_abc[a, b])),
                    "support_c": support,
                }
            )

    out = {
        "instance_id": "S1-a",
        "p": P,
        "A": A,
        "B": B,
        "n": N_ORDER,
        "S": [SX, SY],
        "r": 1,
        "s": S_IMAGE,
        "statistic": "T1_digit0",
        "identity_label": IDENTITY_LABEL,
        "q_maj_numerator": q.numerator,
        "q_maj_denominator": q.denominator,
        "q_maj": f"{q.numerator}/{q.denominator}",
        "maj_sum": int(sum(rec["max_N"] for rec in max_c_records)),
        "n_squared": N_ORDER * N_ORDER,
        "N_abc": n_abc_records,
        "max_c_per_ab": max_c_records,
        "walk_checksum": walk_checksum,
        "pair_checksum": pair_checksum,
        "fft_length": N_ORDER,
        "fft_dtype": "complex128",
        "n_squared_lt_2_53": (N_ORDER * N_ORDER) < (2**53),
    }

    dest = Path(__file__).resolve().parent / "blind_raw.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"q_maj": out["q_maj"], "written": str(dest)}, indent=2))


if __name__ == "__main__":
    main()
