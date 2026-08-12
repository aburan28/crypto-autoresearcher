"""Independently structured direct / variable-elimination exact engines."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from typing import Dict, Iterable, List, Tuple

from fips_semantics import (
    FAMILIES,
    Q,
    cbd_law_fraction,
    compress_fips,
    ctr_q,
    decompress_fips,
)
from exact_dp import Law, convolution, iter_convolution, negate_law, product_law, survival


def product_support_weights(eta_a: int, eta_b: int) -> Dict[int, Fraction]:
    return product_law(cbd_law_fraction(eta_a), cbd_law_fraction(eta_b))


def direct_no_compression_one_coordinate(
    n: int, k: int, eta1: int, eta2: int
) -> Law:
    """Same law as exact_dp.no_compression_one_coordinate_law, built by successive
    single-product convolutions (different control flow)."""
    ey = product_support_weights(eta1, eta2)
    se = product_support_weights(eta1, eta2)
    acc: Law = {0: Fraction(1)}
    # k modules × n products for ey, then for -se, then +e2
    for _ in range(k * n):
        acc = convolution(acc, ey)
    for _ in range(k * n):
        acc = convolution(acc, negate_law(se))
    acc = convolution(acc, cbd_law_fraction(eta2))
    return acc


def compressed_scalar_failure_and_noise(
    eta1: int, eta2: int, du: int, dv: int, message_bit: int
) -> dict:
    """Exact n=1,k=1 compressed shared-variable instance over Z_q.

    Variables: A uniform on Z_q; s,e,y ~ CBD_eta1; e1,e2 ~ CBD_eta2.
    Spec says s,e,y independent_CBD_eta1 and e1,e2 CBD_eta2.
    """
    chi1 = cbd_law_fraction(eta1)
    chi2 = cbd_law_fraction(eta2)
    mu = decompress_fips(message_bit, 1)  # 0 or 1665

    # Aggregate over A by grouping on values that matter; full enumeration.
    # Weight for A is 1/q each.
    # Track law of decoded bit failure and of centered noise ctr_q(w - mu).
    fail_mass = Fraction(0)
    noise: Law = defaultdict(lambda: Fraction(0))
    wrap_hist: Dict[int, Fraction] = defaultdict(lambda: Fraction(0))
    identity_failures = 0

    s_vals = list(chi1.items())
    e_vals = list(chi1.items())
    y_vals = list(chi1.items())
    e1_vals = list(chi2.items())
    e2_vals = list(chi2.items())
    inv_q = Fraction(1, Q)
    cf_du = lambda x: compress_fips(x, du)
    df_du = lambda y: decompress_fips(y, du)
    cf_dv = lambda x: compress_fips(x, dv)
    df_dv = lambda y: decompress_fips(y, dv)
    cf1 = lambda x: compress_fips(x, 1)

    # Precompute for speed: iterate CBD first, A last is fine.
    for s, ps in s_vals:
        for e, pe in e_vals:
            for y, py in y_vals:
                for e1, p1 in e1_vals:
                    for e2, p2 in e2_vals:
                        p_cbd = ps * pe * py * p1 * p2 * inv_q
                        ey = e * y
                        for A in range(Q):
                            p = p_cbd
                            t = (A * s + e) % Q
                            u0 = (A * y + e1) % Q
                            v0 = (t * y + e2 + mu) % Q
                            u_hat = df_du(cf_du(u0))
                            v_hat = df_dv(cf_dv(v0))
                            w = (v_hat - s * u_hat) % Q
                            if cf1(w) != message_bit:
                                fail_mass += p
                            noise_val = ctr_q(w - mu)
                            noise[noise_val] += p

                            # identity: ctr_q(w-mu) == ctr_q(e*y + e2 + c_v - s*e1 - s*c_u)
                            c_u = ctr_q(u_hat - u0)
                            c_v = ctr_q(v_hat - v0)
                            rhs = ey + e2 + c_v - s * e1 - s * c_u
                            lhs = w - mu
                            # difference must be multiple of q
                            diff = lhs - rhs
                            if diff % Q != 0:
                                identity_failures += 1
                            wrap_hist[diff // Q] += p

    total = sum(noise.values())
    return {
        "message_bit": message_bit,
        "eta1": eta1,
        "eta2": eta2,
        "du": du,
        "dv": dv,
        "failure_probability": fail_mass,
        "noise_law": {str(k): str(v) for k, v in sorted(noise.items())},
        "noise_mass": str(total),
        "identity_failures": identity_failures,
        "wrap_multiple_histogram": {str(k): str(v) for k, v in sorted(wrap_hist.items())},
        "support_min": min(noise) if noise else None,
        "support_max": max(noise) if noise else None,
    }


def compressed_scalar_all_families(messages=(0, 1)) -> dict:
    out = {}
    for name, params in FAMILIES.items():
        out[name] = {}
        for m in messages:
            out[name][m] = compressed_scalar_failure_and_noise(
                params["eta1"], params["eta2"], params["du"], params["dv"], m
            )
    return out
