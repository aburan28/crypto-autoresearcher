"""Tests for harness/endosweep: exact algebra, lattices, registry, sweep, toy maps."""
from __future__ import annotations

import pytest

from harness.endosweep import costmodel as CM
from harness.endosweep import lattice as LA
from harness.endosweep import quadorder as QO
from harness.endosweep import sweep as SW
from harness.endosweep import targets as TG
from harness.endosweep import toyverify as TV


SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72


# --- quadorder ---------------------------------------------------------------

def test_norm_trace_conjugate_multiply_consistent():
    for D in (-3, -4, -7, -8, -11, -20, -23):
        for a in range(-4, 5):
            for b in range(-4, 5):
                c = QO.conjugate(D, a, b)
                prod = QO.multiply(D, (a, b), c)
                assert prod == (QO.norm(D, a, b), 0)
                assert QO.trace(D, a, b) == a + c[0]


def test_secp256k1_glv_eigenvalue_reproduced():
    roots = QO.omega_eigenvalues(-3, SECP_N)
    zeta3 = sorted((r - 1) % SECP_N for r in roots)       # omega = zeta_6 = zeta_3 + 1
    assert SECP_LAMBDA in zeta3
    assert pow(SECP_LAMBDA, 3, SECP_N) == 1


def test_min_nonscalar_degree_matches_known_small_cases():
    assert [QO.min_nonscalar_degree(D) for D in (-3, -4, -7, -8, -11, -19, -43)] == [1, 1, 2, 2, 3, 5, 11]


def test_elements_of_norm_matches_brute_force():
    for D in (-3, -7, -20, -23):
        tau, nw = QO.omega_trace_norm(D)
        for N in range(1, 60):
            bf = {(a, b) for a in range(-40, 41) for b in range(1, 20)
                  if a * a + a * b * tau + b * b * nw == N}
            found = {(e.a, e.b) for e in QO.elements_of_norm(D, N, primitive_only=False,
                                                              up_to_units_and_conjugation=False)}
            assert found == bf, (D, N)


def test_class_orders_and_principal_powers():
    # h(-23) = 3, h(-47) = 5, h(-71) = 7 (2 splits in each: D = 1 mod 8)
    for D, ell, order in ((-23, 2, 3), (-47, 2, 5), (-71, 2, 7), (-20, 3, 2), (-3, 7, 1)):
        assert QO.prime_ideal_class_order(D, ell) == order
        el = QO.smallest_principal_power(D, ell)
        assert el is not None and el.norm == ell ** order and el.primitive
    assert QO.smallest_principal_power(-3, 2) is None        # 2 is inert in Z[zeta_3]


def test_cornacchia_agrees_with_search():
    for D in (-3, -7, -11, -23, -47):
        for N in range(3, 300):
            c = QO.cornacchia_element(D, N)
            prim = QO.elements_of_norm(D, N, primitive_only=True, up_to_units_and_conjugation=False)
            if prim and N % (-D) != 0:
                assert c is not None and c.norm == N, (D, N)
            if c is not None:
                assert c.norm == N


def test_small_discriminant_scan_finds_secp256k1_and_certifies_p256():
    secp = next(t for t in TG.deployed_targets() if t.name == "secp256k1")
    scan = QO.small_discriminant_scan(QO.frobenius_discriminant(secp.q, secp.trace), 10_000)
    assert scan.found == -3
    p256 = next(t for t in TG.deployed_targets() if t.name == "NIST P-256")
    scan = QO.small_discriminant_scan(QO.frobenius_discriminant(p256.q, p256.trace), 10_000)
    assert scan.found is None and "degree >= 2500" in scan.certificate


def test_fundamental_discriminants_sequence():
    assert list(QO.fundamental_discriminants(24)) == [-3, -4, -7, -8, -11, -15, -19, -20, -23, -24]


# --- lattice -----------------------------------------------------------------

def test_lll_reduces_and_decomposition_is_exact():
    n = SECP_N
    red = LA.reduce([1, SECP_LAMBDA], n)
    cb = LA.coefficient_bits(red, samples=20)
    assert cb["bound_bits"] <= 129 and cb["empirical_max_bits"] <= 128
    for k in (1, 2, n - 1, 123456789 ** 3 % n):
        ks = red.decompose(k)
        assert (ks[0] + ks[1] * SECP_LAMBDA - k) % n == 0
        assert max(abs(x) for x in ks) < red.babai_bound


def test_unbalanced_lattice_is_detected():
    # G2-style: lambda = x small, {1, psi} alone leaves a 1-bit basis vector
    n = TG.structural_targets()[1].n                      # BLS12-381 r
    x = -0xD201000000010000
    red = LA.reduce([1, x % n], n)
    bits = sorted(LA.inf_norm(b).bit_length() for b in red.basis)
    assert bits[0] <= 65 and bits[1] >= 190


# --- cost model --------------------------------------------------------------

def test_costmodel_monotone_and_incremental_products():
    g = CM.Generator("1", 1, 0.0, "identity")
    u = CM.Generator("u", 2, 1.0, "unit")
    one = CM.multiscalar_cost(256, [g], "weierstrass_jacobian_a=-3")
    two = CM.multiscalar_cost(128, [g, u], "weierstrass_jacobian_a=-3")
    assert two.total_M < one.total_M
    assert CM.pump_cost_per_height_bit(2) == pytest.approx(8.0)
    assert CM.pump_cost_per_height_bit(3) == pytest.approx((4 + 2 * CM.S_PER_M) / (1.5849625007 / 2), rel=1e-6)


# --- targets -----------------------------------------------------------------

def test_registry_verifies_every_deployed_curve():
    for t in TG.deployed_targets():
        TG.verify(t)
        assert t.verified, (t.name, t.verification)


def test_registry_rejects_a_typo():
    t = next(t for t in TG.deployed_targets() if t.name == "secp256k1")
    t.coeffs = {"a": 0, "b": 8}
    TG.verify(t)
    assert t.verified is False


# --- sweep -------------------------------------------------------------------

def test_sweep_reproduces_glv_on_secp256k1_and_nothing_on_p256():
    opts = SW.SweepOptions(disc_bound=10_000, small_norm_max=8, pump_primes=(7,), max_dim=4,
                           lattice_samples=4)
    secp = TG.verify(next(t for t in TG.deployed_targets() if t.name == "secp256k1"))
    r = SW.sweep_target(secp, opts)
    assert r.cm_discriminant == -3 and r.configs[0].label == "GLV-2 [zeta_3]"
    assert 1.4 < r.configs[0].speedup_vs_generic < 1.6
    assert all(c.coeff_bits_empirical <= c.coeff_bits_bound for c in r.configs if c.cost_M != float("inf"))
    p256 = TG.verify(next(t for t in TG.deployed_targets() if t.name == "NIST P-256"))
    r = SW.sweep_target(p256, opts)
    assert r.cm_discriminant is None and len(r.configs) == 1


def test_sweep_g2_four_dimensional():
    opts = SW.SweepOptions(max_dim=4, lattice_samples=4)
    g2 = TG.verify(TG.structural_targets()[1])
    r = SW.sweep_target(g2, opts)
    best = r.configs[0]
    assert best.dim == 4 and best.coeff_bits_empirical <= 66


# --- toy explicit maps (small bits so the test is fast) ----------------------

def test_toy_j0_pump_and_4dim_decomposition():
    rec = TV.verify_j0_pump(bits=20, seed=3)
    assert all(next(iter(c.values())) for c in rec["checks"])


def test_toy_cm23_two_isogeny_cycle():
    rec = TV.verify_cm23_cycle(bits=20, seed=5)
    assert all(next(iter(c.values())) for c in rec["checks"])


# --- explicit chain endomorphisms --------------------------------------------

def test_kernel_polynomial_velu_matches_point_velu_on_toy_curve():
    from harness.endosweep import explicit as EX
    E, N, n, t = TV.j0_curve_with_7_torsion(20, 3)
    p = E.p
    K, s = None, 0
    while K is None:
        s += 1
        K = E.mul(N // 7, E.point(100 + s))
    pts = [K, E.add(K, K), E.add(E.add(K, K), K)]
    h = [1]
    for (x, _) in pts:
        h = EX.pmul(h, [(-x) % p, 1], p)
    vm, ki = TV.VeluMap(E, K, 7), EX.KernelIsogeny(E, h, 7)
    assert (vm.codomain.a, vm.codomain.b) == (ki.codomain.a, ki.codomain.b)
    P = E.point(77)
    assert vm(P) == ki(P) and ki.codomain.on_curve(ki(P))
    fdiv = EX.division_polynomials(p, E.a, E.b, 7)
    assert sum(c * pow(K[0], i, p) for i, c in enumerate(fdiv[7])) % p == 0
    assert h in EX.rational_kernels(E, 7, fdiv)


def test_cryptopro_b_degree_175_chain_endomorphism_is_real():
    """The sweeper's prediction for GOST CryptoPro-B (D_K = -619, h = 5) built and verified."""
    from harness.endosweep import explicit as EX
    T = TG.verify(next(t for t in TG.deployed_targets() if t.name == "GOST CryptoPro-B"))
    assert T.verified
    scan = QO.small_discriminant_scan(QO.frobenius_discriminant(T.q, T.trace), 10_000)
    assert scan.found == -619 and QO.min_nonscalar_degree(-619) == 155
    res = EX.build_chain_endomorphism(T.p, T.coeffs["a"], T.coeffs["b"], T.n, T.h, -619, (4, 1),
                                      curve_name=T.name)
    assert res.found, res.note
    assert res.steps == [5, 5, 7] and res.degree == 175
    assert res.glv_check["max_coeff_bits"] <= 128
    # the cycle through the class group: three distinct neighbours, back to j(E)
    assert res.walk_js[0] == res.walk_js[-1] and len(set(res.walk_js[:-1])) == 3
