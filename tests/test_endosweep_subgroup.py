"""Tests for harness/endosweep/subgroup.py: membership tests and cofactor clearing
from the O-module structure of E(F_q), exhaustively on toy curves and on
points of BLS12-381 G1 (positive control) and CP6-782 G1."""
from __future__ import annotations

import random

import pytest

from harness.endosweep import explicit as EX
from harness.endosweep import quadorder as QO
from harness.endosweep import subgroup as SG
from harness.endosweep.toyverify import Curve


def _all_points(E: Curve):
    pts = [None]
    for x in range(E.p):
        rhs = (x * x * x + E.a * x + E.b) % E.p
        if rhs == 0:
            pts.append((x, 0))
            continue
        ys = SG.prime_nth_roots(rhs, 2, E.p)
        for y in ys:
            pts.append((x, y))
    return pts


def _exhaustive(E, phi, r, h, mem, clr, eff):
    """Every point of E(F_q): membership, clearing onto G, the [h] relation."""
    pts = _all_points(E)
    assert len(pts) == h * r
    ratio = clr.eigenvalue * pow(h, -1, r) % r
    images = set()
    for Q in pts:
        truth = E.mul(r, Q) is None
        assert (SG.apply_element(E, phi, mem.c0, mem.c1, Q) is None) == truth
        R = SG.apply_element(E, phi, clr.c0, clr.c1, Q)
        assert E.mul(r, R) is None
        assert R == E.mul(ratio, E.mul(h, Q))
        images.add(R)
        assert E.mul(r, E.mul(eff, Q)) is None
    assert len(images) == r                      # onto G
    return pts


def _small_ell_counts(E, pts, D, pim1, ells):
    for ell in ells:
        counted = sum(1 for Q in pts if E.mul(ell, Q) is None)
        assert counted == SG.kernel_order(D, (ell, 0), pim1), ell


# --- exact algebra -------------------------------------------------------------

def test_element_index_is_norm_for_principal_ideals():
    rng = random.Random(1)
    for D in (-3, -4, -8, -19, -23, -339):
        for _ in range(30):
            a, b = rng.randrange(-50, 50), rng.randrange(-50, 50)
            if (a, b) == (0, 0):
                continue
            assert SG.element_index(D, [(a, b)]) == QO.norm(D, a, b)


def test_prime_ideal_index_and_frobenius_sign():
    D, r = -23, 607
    lam = QO.omega_eigenvalues(D, r)[0]
    assert SG.element_index(D, [(r, 0), (-lam % r, 1)]) == r
    with pytest.raises(ValueError):
        SG.frobenius_element(D, 21613, 0, 1, lam, r)          # not of norm q


# --- toy curves, every point --------------------------------------------------

def test_toy_bls12_u_minus5_reproduces_phi_equals_minus_u2_exhaustively():
    u, p, r = -5, 7207, 601
    h = (u - 1) ** 2 // 3
    assert r == u ** 4 - u ** 2 + 1 and p == h * r + u        # the BLS12 family at u = -5
    E = next(Curve(p, 0, b) for b in range(1, 50)
             if Curve(p, 0, b).mul(h * r, Curve(p, 0, b).point(b)) is None
             and len(_all_points(Curve(p, 0, b))) == h * r)
    beta = next(z for z in (pow(g, (p - 1) // 3, p) for g in range(2, 50)) if z != 1)
    P = EX.point_of_order(E, r, h, 2)
    alpha = SG.j0_unit(E, r, beta, P)
    if alpha.lam != (-u * u) % r:                             # take the other cube root
        beta = beta * beta % p
        alpha = SG.j0_unit(E, r, beta, P)
    assert alpha.lam == (-u * u) % r
    M = SG.module_structure(-3, p, r, h, alpha)
    mem = SG.short_elements(M, alpha, "membership")
    clr = SG.short_elements(M, alpha, "clearing")
    # u^2 + phi is a valid membership element, of norm exactly r
    assert any((c.c0, c.c1) in ((u * u, 1), (-u * u, -1)) for c in mem)
    assert all(c.kernel == r for c in mem)
    # the cofactor group is Z/((1-u)/3) x Z/(1-u); 1 - u is the effective cofactor
    assert M.cofactor_invariants == ((1 - u) // 3, 1 - u) and M.effective_cofactor == 1 - u
    m0 = next(c for c in mem if (c.c0, c.c1) in ((u * u, 1), (-u * u, -1)))
    pts = _exhaustive(E, SG.unit_map_j0(E, beta), r, h, m0, clr[0], M.effective_cofactor)
    _small_ell_counts(E, pts, -3, M.pim1, (2, 3))


def test_toy_sqrt_minus2_two_isogeny_exhaustively():
    p, a, b, h, r = 1049, 854, 659, 24, 43                     # j = 8000, #E = 2^3 * 3 * 43
    E = Curve(p, a, b)
    alpha, phi, res = SG.chain_alpha(E, r, h, -8, (0, 1), (2,), "sqrt(-2)")
    M = SG.module_structure(-8, p, r, h, alpha)
    mem = SG.short_elements(M, alpha, "membership")
    clr = SG.short_elements(M, alpha, "clearing")
    assert mem and clr and all(c.kernel == r for c in mem) and all(c.kernel == h for c in clr)
    pts = _exhaustive(E, phi, r, h, mem[0], clr[0], M.effective_cofactor)
    _small_ell_counts(E, pts, -8, M.pim1, (2, 3, 4))


def test_toy_class_number_3_chain_of_three_2_isogenies_exhaustively():
    # D = -23 (class number 3): 1 + omega has norm 8, a closed walk of three 2-isogenies
    p, a, b, h, r = 21613, 12563, 1171, 36, 607
    E = Curve(p, a, b)
    alpha, phi, res = SG.chain_alpha(E, r, h, -23, (1, 1), (2, 2, 2), "1 + omega")
    assert len(res.steps) == 3
    M = SG.module_structure(-23, p, r, h, alpha)
    mem = SG.short_elements(M, alpha, "membership")
    clr = SG.short_elements(M, alpha, "clearing")
    pts = _exhaustive(E, phi, r, h, mem[0], clr[0], M.effective_cofactor)
    _small_ell_counts(E, pts, -23, M.pim1, (2, 3, 4, 6, 9))
    # an element of rr whose kernel is larger than r is NOT a membership test: 2 * beta
    bad = (2 * mem[0].c0, 2 * mem[0].c1)
    assert SG.kernel_order(-23, alpha.to_omega(*bad), M.pim1) == r * SG.kernel_order(-23, (2, 0), M.pim1) > r
    assert any(SG.apply_element(E, phi, bad[0], bad[1], Q) is None and E.mul(r, Q) is not None for Q in pts)


# --- BLS12-381 G1: positive control ---------------------------------------------

def test_bls12_381_g1_control_reproduces_known_test_and_h_eff():
    c = SG._arkworks("bls12_381")
    E = Curve(c["p"], c["a"], c["b"])
    r, h, u = c["n"], c["h"], SG.BLS12_381_U
    P = EX.point_of_order(E, r, h, 3)
    alpha = SG.j0_unit(E, r, SG.BLS12_381_BETA, P)
    assert alpha.lam == (-u * u) % r                          # phi(P) = -u^2 P on G1
    M = SG.module_structure(-3, c["p"], r, h, alpha)
    mem = SG.short_elements(M, alpha, "membership")
    clr = SG.short_elements(M, alpha, "clearing")
    beta = next(m for m in mem if (m.c0, m.c1) in ((u * u, 1), (-u * u, -1)))
    assert beta.norm == r and beta.kernel == r                # kernel of u^2 + phi on E(F_p) is G1
    assert M.effective_cofactor == 1 - u                      # h_eff = 1 - u
    assert any((m.c0, m.c1) == (1 - u, 0) for m in clr)
    phi = SG.unit_map_j0(E, SG.BLS12_381_BETA)
    rng = random.Random(5)
    T3 = None
    while T3 is None:                                         # a point of order 3: [u]T = T,
        T3 = E.mul(h * r // 3, SG.random_point(E, rng))       # arkworks' early-out case
    assert T3 is not None and E.mul(u, T3) == T3
    for kind in range(12):
        Q = SG.random_point(E, rng)
        if kind % 3 == 1:
            Q = E.mul(h, Q)
        elif kind % 3 == 2:
            Q = E.add(E.mul(h, Q), T3)
        truth = E.mul(r, Q) is None
        assert (SG.apply_element(E, phi, beta.c0, beta.c1, Q) is None) == truth
    assert SG.apply_element(E, phi, beta.c0, beta.c1, T3) is not None


# --- CP6-782 G1 -------------------------------------------------------------------

def test_cp6_782_membership_and_clearing_on_points():
    c = SG._arkworks("cp6_782")
    E = Curve(c["p"], c["a"], c["b"])
    r, h = c["n"], c["h"]
    alpha, phi, res = SG.chain_alpha(E, r, h, -339, (4, 1), (7, 3, 5), "4 + omega")
    M = SG.module_structure(-339, c["p"], r, h, alpha)
    mem = SG.short_elements(M, alpha, "membership", box=2)
    clr = SG.short_elements(M, alpha, "clearing", box=2)
    assert mem[0].height_bits <= r.bit_length() / 2 + 8       # the kill criterion, not met
    assert clr[0].height_bits <= h.bit_length() / 2 + 8
    assert M.cofactor_invariants[0] == 6
    rng = random.Random(9)
    ratio = clr[0].eigenvalue * pow(h, -1, r) % r
    for i in range(4):
        R = SG.random_point(E, rng)
        hR = E.mul(h, R)
        Q = hR if i % 2 else E.add(hR, E.mul(r, SG.random_point(E, rng)))
        assert (SG.apply_element(E, phi, mem[0].c0, mem[0].c1, Q) is None) == (i % 2 == 1)
        assert SG.apply_element(E, phi, clr[0].c0, clr[0].c1, R) == E.mul(ratio, hR)


def test_cost_model_counts_fixed_scalars():
    ar = SG.CV.arithmetic(2 ** 255 - 19, 5)
    k = (1 << 254) + 12345
    full = SG.scalar_ops(ar, k)
    half = SG.msm_ops(ar, (1 << 127) + 3, (1 << 127) + 5, {"M": 10, "S": 0, "M_eq": 10})
    assert half["M_eq"] < full["M_eq"] and full["bits"] == 255
    assert SG.msm_ops(ar, 7, 0, {"M": 10, "S": 0, "M_eq": 10}) == SG.scalar_ops(ar, 7)
