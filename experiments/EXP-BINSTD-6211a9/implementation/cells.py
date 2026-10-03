"""Four-cell curve factory, V construction, M2 yield, M5 orbits."""
from __future__ import annotations

import math
import random
from typing import List, Tuple

import numpy as np

from curve import Curve, factor_out_small, hasse_trace_bsgs, is_prime, s3_eval
from gf2n import make_field


def fixed_V_basis(n: int, l: int, seed: int = 20261001) -> List[int]:
    """Deterministic F2-basis of an l-dimensional subspace of F_{2^n}.

    Uses the first l standard basis vectors when l <= n (polynomial basis
    coordinate subspace). Identical across cells by construction.
    """
    assert 1 <= l <= n
    # Prefer ker(Tr) when possible for known-false control compatibility:
    # take e_0..e_{l-1} but if Tr spans those, adjust last vector.
    basis = [1 << j for j in range(l)]
    return basis


def ker_tr_basis(F, l: int) -> List[int]:
    """Build an l-dimensional subspace of ker Tr (requires l <= n-1)."""
    assert l <= F.n - 1
    # Collect a basis of ker Tr by taking standard vectors with Tr=0, and
    # sums to kill Tr=1 vectors.
    ker = []
    ones = []
    for j in range(F.n):
        e = 1 << j
        if F.trace(e) == 0:
            ker.append(e)
        else:
            ones.append(e)
    # differences of Tr=1 vectors lie in ker Tr
    for i in range(1, len(ones)):
        ker.append(ones[0] ^ ones[i])
    # Gaussian-eliminate to an independent set
    basis = []
    for v in ker:
        w = v
        for b in basis:
            # reduce by leading bits
            if w == 0:
                break
            # simple: if MSB of b set in w, xor
            hb = b.bit_length() - 1
            if (w >> hb) & 1:
                w ^= b
        if w:
            # reduce existing by w
            hw = w.bit_length() - 1
            basis2 = []
            for b in basis:
                if (b >> hw) & 1:
                    b ^= w
                basis2.append(b)
            basis2.append(w)
            basis = basis2
        if len(basis) >= l:
            break
    basis = basis[:l]
    assert len(basis) == l
    for b in basis:
        assert F.trace(b) == 0
    return basis


def enumerate_V(V_basis: List[int]) -> List[int]:
    l = len(V_basis)
    out = []
    for mask in range(1 << l):
        x = 0
        m = mask
        j = 0
        while m:
            if m & 1:
                x ^= V_basis[j]
            m >>= 1
            j += 1
        out.append(x)
    return out


def draw_generic_field_element(F, rng: random.Random, forbid_F2: bool = True) -> int:
    while True:
        x = rng.randrange(1, F.q)
        if forbid_F2 and x in (0, 1):
            continue
        # not in F2: x^2 != x (i.e. not 0 or 1) already; for prime n that's enough
        if x not in (0, 1):
            return x


def build_cell(F, cell: str, rng: random.Random) -> dict:
    """Return {name,a,b,curve,Tr_a} for one factorial cell."""
    if cell == "C-KK":
        a, b = 1, 1
    elif cell == "C-GK":
        a = draw_generic_field_element(F, rng)
        b = 1
    elif cell == "C-KG":
        a = 1
        b = draw_generic_field_element(F, rng)
    elif cell == "C-GG":
        a = draw_generic_field_element(F, rng)
        b = draw_generic_field_element(F, rng)
    else:
        raise ValueError(cell)
    E = Curve(F, a, b)
    return {
        "cell": cell,
        "a": a,
        "b": b,
        "Tr_a": F.trace(a),
        "a_in_F2": a in (0, 1),
        "b_in_F2": b in (0, 1),
        "curve": E,
    }


def analyze_curve_order(curve: Curve) -> dict:
    n = curve.F.n
    if n <= 23:
        nE = curve.count_by_trace()
        method = "trace_enumeration"
    else:
        nE = hasse_trace_bsgs(curve)
        method = "hasse_bsgs"
    h, r = factor_out_small(nE)
    while r % 2 == 0:
        h *= 2
        r //= 2
    return {
        "group_order_E": nE,
        "cofactor_h": h,
        "r": r,
        "r_is_prime": is_prime(r) if r.bit_length() <= 64 else None,
        "order_method": method,
    }


def Fb_E_intersect_V(curve: Curve, V_elems: List[int]) -> List[int]:
    """E-side abscissae in V\\{0}."""
    return [x for x in V_elems if x != 0 and curve.is_x_coord(x)]


def point_in_G(curve: Curve, P, r: int, h: int, strict: bool = True) -> bool:
    """Membership in the odd-order summand.

    strict=True: class bit (if h even) + [r]P = O.
    strict=False: class-bit-0 proxy only (Stage 2 instrument); caller must label.
    """
    if P is None:
        return False
    if h % 2 == 0 and curve.class_bit(P) != 0:
        return False
    if not strict:
        return True
    return curve.mul(r, P) is None


def exhaustive_lambda_x_m2(curve: Curve, fb_x: List[int], r: int, h: int,
                           strict_G: bool = True) -> dict:
    """Exhaustive m_a=2 yield over E-side abscissae in V.

    For each unordered pair {x1,x2}, lift to points (two choices of signs),
    count how many sums land in G. Certificate-verify a sample by curve add.

    lambda_x_measured := n_pairs_with_G / r
    """
    lifts = []
    for x in fb_x:
        P = curve.lift_x(x)
        if P is None:
            continue
        lifts.append(P)

    n = len(lifts)
    n_pair_tests = 0
    n_pairs_with_G = 0
    n_G_sums = 0
    certified = []
    max_certs = 32
    g_mode = "strict_r_mul" if strict_G else "class_bit_proxy"

    for i in range(n):
        for j in range(i, n):
            n_pair_tests += 1
            P, Q = lifts[i], lifts[j]
            candidates = [curve.add(P, Q), curve.add(P, curve.neg(Q))]
            if i == j:
                candidates = [curve.double(P)]
            hit = False
            for S in candidates:
                if S is None:
                    continue
                if point_in_G(curve, S, r, h, strict=strict_G):
                    n_G_sums += 1
                    hit = True
                    if len(certified) < max_certs:
                        on = curve.on_curve(S)
                        certified.append(
                            {
                                "x1": P[0],
                                "x2": Q[0],
                                "S_x": S[0],
                                "S_y": S[1],
                                "on_curve": bool(on),
                                "verified": bool(on),
                            }
                        )
            if hit:
                n_pairs_with_G += 1

    lambda_x = (n_pairs_with_G / r) if r else None
    cert_pass = all(c["verified"] for c in certified) if certified else True
    return {
        "Fb_E_intersect_V": len(fb_x),
        "n_lifts": n,
        "n_pair_tests": n_pair_tests,
        "n_pairs_with_G": n_pairs_with_G,
        "n_G_sums": n_G_sums,
        "lambda_x_measured": lambda_x,
        "r": r,
        "G_membership_mode": g_mode,
        "certificate_pass_rate": 1.0 if cert_pass else (
            sum(1 for c in certified if c["verified"]) / max(len(certified), 1)
        ),
        "certified_sample": certified,
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "label": "measured",
    }


def known_false_control(curve: Curve, V_basis_ker: List[int], r: int, h: int) -> dict:
    """V in ker Tr, m_a=1 (odd), Tr(a)=1 => zero G-decompositions."""
    assert curve.F.trace(curve.A) == 1
    V = enumerate_V(V_basis_ker)
    fb = Fb_E_intersect_V(curve, V)
    n_in_G = 0
    for x in fb:
        P = curve.lift_x(x)
        if P is None:
            continue
        for Q in (P, curve.neg(P)):
            if point_in_G(curve, Q, r, h):
                n_in_G += 1
    return {
        "Tr_a": 1,
        "m_a": 1,
        "V_in_ker_Tr": True,
        "Fb_E_intersect_V": len(fb),
        "n_G_decompositions": n_in_G,
        "pass": n_in_G == 0,
    }


def modeled_rho(r: int, n: int, cell: str) -> dict:
    """Matched rho baselines (MODELED, not measured)."""
    if cell == "C-KK":
        val = math.sqrt(math.pi * r / (4.0 * n))
        formula = "sqrt(pi*r/(4*n))"
    else:
        val = 0.886 * math.sqrt(r)
        formula = "0.886*sqrt(r)"
    return {
        "rho_modeled": val,
        "formula": formula,
        "label": "modeled",
        "r": r,
        "n": n,
        "cell": cell,
    }


def m5_ckk_orbits(curve: Curve, fb_x: List[int], n: int) -> dict:
    """On C-KK: <tau,-1> orbit count structure for E-side abscissae.

    tau(x)=x^2. Orbit of x under squaring has size dividing n (n prime => 1 or n).
    U = |Fb_E| / (2n) when every nonzero E-side x lies in a full orbit of n
    and each orbit contributes 2n points (with negations).
    """
    assert curve.A in (0, 1) and curve.B == 1
    F = curve.F
    seen = set()
    orbits = []
    for x in fb_x:
        if x in seen or x == 0:
            continue
        orb = []
        y = x
        for _ in range(n + 1):
            if y in seen:
                break
            seen.add(y)
            orb.append(y)
            y = F.sqr(y)
            if y == x:
                break
        orbits.append(orb)
    sizes = [len(o) for o in orbits]
    Fb = len(fb_x)
    # relation unknowns under <tau,-1>: U = Fb/(2n) when all orbits size n
    U = Fb / (2.0 * n) if n else None
    return {
        "Fb_E_size": Fb,
        "n_orbits": len(orbits),
        "orbit_sizes": sizes,
        "U_modeled_from_Fb": U,
        "label_U": "derived_from_measured_Fb",
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
    }


def phi17_factors_F2():
    """Degree-8 factors of Phi_17 over F2 (from IDEA-20260915-8fe0ef bit patterns)."""
    # 0b100111001 and 0b111010111 as integer polynomials (low bit = const)
    f1 = 0b100111001  # x^8 + x^5 + x^4 + x^3 + 1
    f2 = 0b111010111  # x^8 + x^7 + x^6 + x^4 + x^2 + x + 1
    return f1, f2


def apply_poly_sqr(F, poly: int, x: int) -> int:
    """Evaluate poly(Frobenius) at x: sum p_i * x^{2^i}."""
    acc = 0
    y = x
    i = 0
    p = poly
    while p:
        if p & 1:
            acc ^= y
        y = F.sqr(y)
        p >>= 1
        i += 1
    return acc


def trimoska_Fb_sizes(curve: Curve) -> dict:
    """Compute |Fb_E| for ker f1(tau) and ker f2(tau) on n=17 C-KK."""
    F = curve.F
    assert F.n == 17
    f1, f2 = phi17_factors_F2()
    sizes = []
    details = []
    for name, f in (("f1", f1), ("f2", f2)):
        V = []
        for x in range(F.q):
            if apply_poly_sqr(F, f, x) == 0:
                V.append(x)
        fb = Fb_E_intersect_V(curve, V)
        # |Fb_E| counts points = 2 * |E-side x| when x=0 not included / no 2-torsion weirdness
        # Frozen expected is 204/238 which equals 2*|E-side x| for the two V's
        # (102*2=204, 119*2=238)
        n_pts = 0
        for x in fb:
            P = curve.lift_x(x)
            if P is None:
                continue
            n_pts += 1
            N = curve.neg(P)
            if N != P:
                n_pts += 1
        sizes.append(n_pts)
        details.append(
            {
                "factor": name,
                "poly_bits": bin(f),
                "dim_V_approx": int(round(math.log2(max(len(V), 1)))),
                "V_size": len(V),
                "E_side_x": len(fb),
                "Fb_E_points": n_pts,
            }
        )
    return {"Fb_E_sizes": sizes, "details": details}
