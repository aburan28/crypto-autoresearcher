"""Exact generating-function / dynamic-program convolution of CBD product laws."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from typing import Dict, Iterable, List, Tuple

from fips_semantics import cbd_law_fraction


Law = Dict[int, Fraction]


def normalize(law: Law) -> Law:
    total = sum(law.values())
    if total != 1:
        # keep as-is if already Fraction summing to 1; else scale
        return {k: v / total for k, v in law.items()}
    return dict(law)


def mass(law: Law) -> Fraction:
    return sum(law.values())


def convolution(a: Law, b: Law) -> Law:
    out: Law = defaultdict(lambda: Fraction(0))
    for xa, pa in a.items():
        for xb, pb in b.items():
            out[xa + xb] += pa * pb
    return dict(out)


def product_law(a: Law, b: Law) -> Law:
    out: Law = defaultdict(lambda: Fraction(0))
    for xa, pa in a.items():
        for xb, pb in b.items():
            out[xa * xb] += pa * pb
    return dict(out)


def iter_convolution(law: Law, n: int) -> Law:
    if n < 0:
        raise ValueError("n must be nonnegative")
    out: Law = {0: Fraction(1)}
    if n == 0:
        return out
    # double-and-add without truncation
    bits = bin(n)[2:]
    for ch in bits:
        out = convolution(out, out)
        if ch == "1":
            out = convolution(out, law)
    return out


def negate_law(law: Law) -> Law:
    return {-k: v for k, v in law.items()}


def estimator_aligned_no_compression_law(n: int, k: int, ks: int, ke: int, ke_ct: int) -> Law:
    """Exact Fraction law matching pinned no-compression product pairing.

    Pinned Kyber_failure uses B1=product(CBD_ke, CBD_ks) and B2=product(CBD_ks, CBD_ke_ct)
    even though the algebraic ML-KEM noise is e^T y - s^T e1 with y,e1 ~ CBD_ke_ct.
    """
    b1 = product_law(cbd_law_fraction(ke), cbd_law_fraction(ks))
    b2 = product_law(cbd_law_fraction(ks), cbd_law_fraction(ke_ct))
    c1 = iter_convolution(b1, k * n)
    c2 = iter_convolution(b2, k * n)
    c = convolution(c1, c2)
    return convolution(c, cbd_law_fraction(ke_ct))


def no_compression_one_coordinate_law(
    n: int, k: int, eta1: int, eta2: int
) -> Law:
    """Exact law of one output coordinate of e^T y - s^T e1 + e2 without compression.

    Each polynomial product contributes n independent CBD products (signs absorbed
    by CBD symmetry). Module rank k contributes k such products for e*y and k for
    s*e1, plus one CBD_eta2 for e2.
    """
    if n < 1 or k < 1:
        raise ValueError("n,k >= 1")
    chi_s = cbd_law_fraction(eta1)
    chi_e = cbd_law_fraction(eta1)
    chi_y = cbd_law_fraction(eta2)
    chi_e1 = cbd_law_fraction(eta2)
    chi_e2 = cbd_law_fraction(eta2)

    prod_ey = product_law(chi_e, chi_y)
    prod_se1 = product_law(chi_s, chi_e1)
    # one coordinate: n independent products per polynomial
    ey_coord = iter_convolution(prod_ey, n)
    se1_coord = iter_convolution(prod_se1, n)
    term = convolution(ey_coord, negate_law(se1_coord))
    # k modules
    total = iter_convolution(term, k)
    return convolution(total, chi_e2)



def survival(law: Law, threshold: int) -> Fraction:
    """P[|X| > threshold] with strict inequality (pinned estimator convention)."""
    s = Fraction(0)
    for x, p in law.items():
        if abs(x) > threshold:
            s += p
    return s


def survival_table(law: Law) -> Dict[int, Fraction]:
    if not law:
        return {}
    vmax = max(abs(x) for x in law)
    return {t: survival(law, t) for t in range(0, vmax + 1)}


def joint_n2_k1_eta2(eta1: int = 2, eta2: int = 2) -> Dict[Tuple[int, int], Fraction]:
    """Exact joint law of two no-compression coordinates for n=2, k=1.

    For n=2, (e*y)_0 = e0*y0 - e1*y1, (e*y)_1 = e0*y1 + e1*y0.
    Same for s*e1. Then nu = ey - se1 + (e2_0, e2_1) with independent e2 coeffs.
    """
    chi_s = cbd_law_fraction(eta1)
    chi_e = cbd_law_fraction(eta1)
    chi_y = cbd_law_fraction(eta2)
    chi_e1 = cbd_law_fraction(eta2)
    chi_e2 = cbd_law_fraction(eta2)

    joint: Dict[Tuple[int, int], Fraction] = defaultdict(lambda: Fraction(0))

    # Enumerate all CBD coeffs for e,y,s,e1,e2 (each 2 coeffs)
    # Supports are tiny: eta<=3 => at most 7 values.
    def support(law: Law):
        return list(law.keys())

    for e0 in support(chi_e):
        for e1 in support(chi_e):
            pe = chi_e[e0] * chi_e[e1]
            for y0 in support(chi_y):
                for y1 in support(chi_y):
                    py = chi_y[y0] * chi_y[y1]
                    ey0 = e0 * y0 - e1 * y1
                    ey1 = e0 * y1 + e1 * y0
                    for s0 in support(chi_s):
                        for s1 in support(chi_s):
                            ps = chi_s[s0] * chi_s[s1]
                            for f0 in support(chi_e1):
                                for f1 in support(chi_e1):
                                    pf = chi_e1[f0] * chi_e1[f1]
                                    se0 = s0 * f0 - s1 * f1
                                    se1 = s0 * f1 + s1 * f0
                                    for g0 in support(chi_e2):
                                        for g1 in support(chi_e2):
                                            pg = chi_e2[g0] * chi_e2[g1]
                                            n0 = ey0 - se0 + g0
                                            n1 = ey1 - se1 + g1
                                            joint[(n0, n1)] += pe * py * ps * pf * pg
    return dict(joint)


def joint_any_and_marginal(
    joint: Dict[Tuple[int, int], Fraction]
) -> Tuple[Law, Dict[int, dict]]:
    """Return one-coordinate marginal and per-threshold union/independence stats."""
    marg: Law = defaultdict(lambda: Fraction(0))
    for (a, b), p in joint.items():
        marg[a] += p
    # sanity: marg should also equal law of second coord
    marg2: Law = defaultdict(lambda: Fraction(0))
    for (a, b), p in joint.items():
        marg2[b] += p
    if marg != marg2:
        # allow equality of masses per key
        if {k: marg[k] for k in sorted(marg)} != {k: marg2[k] for k in sorted(marg2)}:
            raise AssertionError("joint marginals disagree")

    vmax = max(max(abs(a), abs(b)) for a, b in joint)
    rows = {}
    for t in range(0, vmax + 1):
        p_marg = survival(marg, t)
        p_any = sum(p for (a, b), p in joint.items() if abs(a) > t or abs(b) > t)
        n = 2
        union = n * p_marg
        indep = 1 - (1 - p_marg) ** n
        rows[t] = {
            "p_marginal": p_marg,
            "p_any": p_any,
            "n_times_p": union,
            "independence_formula": indep,
            "union_slack": union - p_any,
            "union_ok": p_any <= min(Fraction(1), union),
            "indep_delta": p_any - indep,
        }
    return dict(marg), rows
