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


def test_flint_and_pure_python_division_polynomials_and_kernels_agree():
    from harness.endosweep import explicit as EX
    pytest.importorskip("flint")
    T = TG.verify(next(t for t in TG.deployed_targets() if t.name == "GOST CryptoPro-B"))
    p, a, b = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p
    py = EX.division_polynomials(p, a, b, 7)
    fl = EX.division_polynomials_flint(p, a, b, 7)
    assert py[5] == fl[5] and py[7] == fl[7]
    E = TV.Curve(p, a, b)
    trace = p + 1 - T.n
    for ell in (5, 7):
        by_factoring = sorted(EX.rational_kernels(E, ell, py))
        by_frobenius = sorted(EX.rational_kernels_frobenius(E, ell, trace, fl))
        assert by_factoring == by_frobenius and len(by_factoring) == 2


def test_cryptopro_b_degree_155_chain_omega_itself():
    """omega = (1+sqrt(-619))/2 of norm 5*31 as a 5-isogeny followed by a 31-isogeny."""
    pytest.importorskip("flint")
    from harness.endosweep import explicit as EX
    T = TG.verify(next(t for t in TG.deployed_targets() if t.name == "GOST CryptoPro-B"))
    res = EX.build_chain_endomorphism(T.p, T.coeffs["a"], T.coeffs["b"], T.n, T.h, -619, (0, 1),
                                      curve_name=T.name)
    assert res.found, res.note
    assert res.steps == [5, 31] and res.degree == 155 and res.glv_check["max_coeff_bits"] <= 128


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


def test_two_isogeny_chains_on_a_256_bit_class_number_3_curve():
    """Degree-2 steps in kernel-polynomial form, at real scale, on a CM curve from H_{-23}."""
    from harness.endosweep import explicit as EX
    E, N, n, t, j = TV.cm_curve_from_class_polynomial(-23, TV.HILBERT_CLASS_POLY_M23, 256, seed=3)
    assert E.p.bit_length() >= 250 and (t * t - 4 * E.p) % 23 == 0
    for element, steps in (((1, 1), [2, 2, 2]), ((5, 1), [2, 2, 3, 3]), ((0, 1), [2, 3])):
        r = EX.build_chain_endomorphism(E.p, E.a, E.b, n, N // n, -23, element)
        assert r.found, (element, r.note)
        assert r.steps == steps and r.glv_check["max_coeff_bits"] <= r.glv_check["babai_bound_bits"]


# --- FourQ, genus 2, corpus ----------------------------------------------------

def test_fourq_maps_verify_and_decompose():
    from harness.endosweep import fourq as FQ
    res = FQ.verify_fourq()
    assert res.verified_parameters
    assert res.cm_discriminant == -40
    assert res.psi_relation.startswith("psi^2 = 0 psi + 32")
    assert res.phi_relation.startswith("phi^2 = 0 phi + -80")
    assert all(res.endomorphism_checks[k] for k in res.endomorphism_checks if "norm <= 64" not in k)
    assert res.decomposition["reconstructs kP (4 random k)"]
    assert res.decomposition["max_coeff_bits"] <= 63
    T, _ = FQ.fourq_target()
    assert T.verified and len(T.declared_generators) == 2


def test_genus2_toy_rank4_decomposition():
    from harness.endosweep import genus2 as G2
    for fam in ("BK", "FKT"):
        r = G2.verify_genus2_toy(fam, bits=9, seed=1)
        assert r.eigenvalue is not None
        assert all(v is True for k, v in r.checks.items() if isinstance(v, bool)), r.checks
        assert r.ops_add["M"] > 0 and r.ops_dbl["M"] > 0


def test_corpus_ingestion_and_scan(tmp_path):
    from harness.endosweep import corpus as CO
    cat = tmp_path / "gost"
    cat.mkdir()
    curve = {
        "name": "cryptopro-b", "category": "gost", "field": {"type": "Prime", "bits": 256,
            "p": "0x8000000000000000000000000000000000000000000000000000000000000c99"},
        "form": "Weierstrass",
        "params": {"a": {"raw": "0x8000000000000000000000000000000000000000000000000000000000000c96"},
                   "b": {"raw": "0x3e1af419a269a5f866a7d3c25c3df80ae979259373ff2b182f49d4ce7e1bbc8b"}},
        "order": "0x800000000000000000000000000000015f700cfff1a624e5e497161bcc8a198f", "cofactor": "0x1",
        "characteristics": {"cm_disc": "-619", "conductor": "4646402506017662432554672533504826433"},
    }
    binary = {"name": "k163", "category": "gost", "field": {"type": "Binary", "bits": 163}, "form": "Weierstrass"}
    (cat / "curves.json").write_text(__import__("json").dumps({"curves": [curve, binary]}))
    loaded = CO.load_std_curves(str(tmp_path))
    assert len(loaded) == 2
    T, entry, _ = loaded[0]
    e = CO.scan_entry(T, entry, disc_bound=10_000, explicit_max_prime=7, explicit_time_budget_s=60)
    assert e.verified and e.scan_D == -619 and e.db_agreement == "agree"
    assert e.cheapest_chain["chain"] == "5^2*7" and e.explicit["found"] is True
    assert loaded[1][1].skipped.startswith("field type Binary")


# --- chainsweep --------------------------------------------------------------

from harness.endosweep import chainsweep as CS   # noqa: E402
from harness.endosweep import explicit as EX    # noqa: E402


def test_chain_op_model_reproduces_the_measured_evaluator_counts():
    # crypto#1408 derived ~128 M for the projective 5*5*7 chain and ~272 M for 5*31
    assert CS.chain_ops([5, 5, 7], "generic") == {"M": 124, "S": 4, "I": 0, "M_eq": 128}
    assert CS.chain_ops([5, 31], "generic")["M_eq"] == 272
    # the generic evaluator does not care about the order; the optimised one does
    assert len({CS.chain_ops(o, "generic")["M_eq"] for o in CS.distinct_orders([5, 5, 7])}) == 1
    assert CS.chain_ops([7, 5, 5], "optimised") == {"M": 78, "S": 2, "I": 0, "M_eq": 80}
    assert CS.chain_ops([5, 5, 7], "optimised")["M_eq"] == 89
    assert CS.chain_ops([31, 5], "optimised")["M_eq"] < CS.chain_ops([5, 31], "optimised")["M_eq"] / 1.9


def test_distinct_orders_and_class_number():
    assert CS.distinct_orders([5, 5, 7]) == [(5, 5, 7), (5, 7, 5), (7, 5, 5)]
    assert len(CS.distinct_orders([5, 7, 7, 23])) == 12
    assert [CS.class_number(D) for D in (-3, -4, -23, -56, -163, -619)] == [1, 1, 3, 4, 1, 5]


def test_catalogue_of_d_minus_619_starts_with_the_known_chains():
    cat = CS.catalogue(-619, 1000, 31)
    els = {(e["a"], e["b"]): e["steps"] for e in cat}
    assert els[(4, 1)] == [5, 5, 7] and els[(0, 1)] == [5, 31] and els[(9, 1)] == [5, 7, 7]
    assert els[(15, 2)] == [5, 5, 5, 7]
    for e in cat:
        assert QO.norm(-619, e["a"], e["b"]) == e["norm"]
        assert all(QO.kronecker_symbol_disc(-619, l) != -1 for l in e["steps"])
    best = min((CS.best_order(e["steps"], "optimised") for e in cat), key=lambda t: t[1]["M_eq"])
    assert best[0] == (7, 5, 5) and best[1]["M_eq"] == 80


def test_outside_bound_certifies_the_catalogue():
    ob = CS.outside_lower_bound(-619, 20000, 61, "optimised")
    assert ob["large_step"]["ell"] == 71                 # 67 is inert in Q(sqrt(-619))
    assert ob["bound"] > 2 * 80                          # every chain within 2x of the best is inside
    # brute force on small bounds: nothing outside is cheaper than the bound
    from sympy import factorint
    small = CS.outside_lower_bound(-619, 300, 23, "optimised")
    outside = 0
    for N in range(2, 3000):
        fac = factorint(N)
        if N <= 300 and max(fac) <= 23:
            continue                                     # inside the small catalogue
        for el in QO.elements_of_norm(-619, N):
            steps = sorted(sum(([l] * e for l, e in fac.items()), []))
            assert CS.best_order(steps, "optimised")[1]["M_eq"] >= small["bound"]
            outside += 1
    assert outside > 20


def test_wnaf_model_matches_reconstruction_and_counts_are_positive():
    import random
    rng = random.Random(3)
    for w in range(2, 8):
        for _ in range(20):
            k = rng.randrange(1, 1 << 256)
            d = CS.wnaf_digits(k, w)
            assert sum(x << i for i, x in enumerate(d)) == k
            nz = [i for i, x in enumerate(d) if x]
            assert all(b - a >= w for a, b in zip(nz, nz[1:]))
    base = CS.baseline_ops(rng.randrange(1, 1 << 256), 5, "affine")
    assert base["I"] == 1 and base["S"] > 256


def test_build_every_ordering_of_4_plus_omega_on_cryptopro_b():
    T = next(t for t in TG.deployed_targets() if t.name == "GOST CryptoPro-B")
    TG.verify(T)
    p, a, b, n = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p, T.n
    root = QO.omega_eigenvalues(-619, n)[0]
    lams = set()
    for order in CS.distinct_orders([5, 5, 7]):
        r = EX.build_chain_endomorphism(p, a, b, n, T.h, -619, (4, 1), steps=list(order),
                                        conjugates=False, omega_root=root)
        assert r.found and r.steps == list(order)
        lams.add(min(r.eigenvalue, n - r.eigenvalue))
        rec = CS.export_chain(T, -619, r, root, vectors=1, seed=5)
        assert rec["order"] == list(order) and len(rec["steps"]) == 3
        assert rec["model_ops"]["optimised"] == CS.chain_ops(order, "optimised")
    assert len(lams) == 1                                # one endomorphism, three walks
    with pytest.raises(ValueError):
        EX.build_chain_endomorphism(p, a, b, n, T.h, -619, (4, 1), steps=[5, 7])


# --- cross-curve sweep ---------------------------------------------------------

import json as _json   # noqa: E402
import os as _os       # noqa: E402

from harness.endosweep import arkworks as AK      # noqa: E402
from harness.endosweep import curvesweep as CV    # noqa: E402

_ARK = _os.path.join(_os.path.dirname(__file__), "..", "research", "endosweep_curves_20261006", "arkworks",
                     "curves.json")


def _ark_target(name: str) -> TG.Target:
    from harness.endosweep.corpus import _int
    e = next(c for c in _json.load(open(_ARK))["curves"] if c["name"] == name)
    p, n, h = _int(e["field"]["p"]), _int(e["order"]), _int(e["cofactor"])
    a = _int(e["params"]["a"])
    if e["form"] == "Weierstrass":
        return TG.Target(name, p, "weierstrass", {"a": a, "b": _int(e["params"]["b"])}, n, h)
    return TG.Target(name, p, "edwards", {"a": a, "d": _int(e["params"]["d"])}, n, h)


def test_corpus_parses_signed_hex():
    from harness.endosweep.corpus import _int
    assert [_int(s) for s in ("-0x05", "0x1F", "17", "-17", {"raw": "-0x05"}, "+0x10")] == [-5, 31, 17, -17, -5, 16]


def test_arkworks_source_parsing_without_network():
    src = '''
impl CurveConfig for C { const COFACTOR: &'static [u64] = &[
        0x1, 0x2,
    ]; }
impl SWCurveConfig for C {
    const COEFF_A: Fq = Fq::ZERO;
    const COEFF_B: Fq =
        MontFp!("-17");
    const GENERATOR: Affine = Affine::new_unchecked(GX, GY);
}
pub const GX: Fq = MontFp!("1");
pub const GY: Fq = MontFp!("3");
'''
    p = 101
    block = AK._block(src, AK.re.compile(r"impl\s+SWCurveConfig\s+for\s+\w+\s*\{"))
    assert AK._const(block, "COEFF_A", p) == 0 and AK._const(block, "COEFF_B", p) == 84
    assert AK._cofactor(src) == 1 + (2 << 64)
    assert AK._generator(src, block, p) == (1, 3)
    with pytest.raises(ValueError):
        AK._expr("Fq::from(7)", p)


def test_arkworks_extraction_is_complete_and_generators_check():
    doc = _json.load(open(_ARK))
    assert doc["commit"] == "e2d16a27e2cfa9f972ae9772df827a22730011b4"
    names = {c["name"] for c in doc["curves"]}
    assert {"mnt4_753", "mnt6_753", "cp6_782", "bw6_761", "grumpkin", "ed_on_bls12_381_bandersnatch"} <= names
    for c in doc["curves"]:
        assert "unparsed" not in c, c["name"]
        assert c["generator_check"] == "generator on the curve, killed by h*n", c["name"]
        assert all(s["url"].startswith("https://raw.githubusercontent.com/arkworks-rs/curves/" + doc["commit"])
                   for s in c["sources"])


def test_order_pin_for_a_g1_smaller_than_4_sqrt_q():
    import re
    from math import isqrt
    T = TG.verify(_ark_target("bw6_761"))                       # n has 377 bits, p 761
    assert T.verified and "only multiple of n in the Hasse interval" in T.verification
    K = int(re.search(r"order > (\d+)", T.verification).group(1))
    assert K * T.n >= 4 * isqrt(T.q) + 2                        # every other multiple of n in the interval is excluded
    bad = TG.verify(TG.Target("bw6_761 wrong", T.p, "weierstrass", dict(T.coeffs), T.n, T.h + 6))
    assert bad.verified is False


def test_edwards_curves_convert_to_a_verified_weierstrass_model():
    T = TG.verify(_ark_target("ed_on_bls12_381_bandersnatch"))
    W = TG.weierstrass_target(T)
    assert T.verified and W.verified and W.model == "weierstrass" and W.n == T.n and W.h == T.h


def test_closed_form_best_order_matches_brute_force():
    import itertools
    import random
    rng = random.Random(1)
    for _ in range(200):
        ms = sorted(rng.choice([2, 3, 5, 7, 11, 23, 31]) for _ in range(rng.randrange(1, 6)))
        for v in ("optimised", "generic"):
            brute = min(CV.chain_ops(o, v)["M_eq"] for o in set(itertools.permutations(ms)))
            assert CV.best_order(ms, v)[1]["M_eq"] == brute
    assert CV.chain_ops((7, 5, 5), "optimised") == CS.chain_ops((7, 5, 5), "optimised")
    assert CV.multiset_orderings([5, 5, 7]) == 3 and len(CV.distinct_orders([2] * 15)) == 1


def test_cost_bounded_catalogue_is_exhaustive():
    """Every element a norm-bounded brute force finds under the cost limit is in it, and vice versa."""
    for D in (-619, -339, -8, -91):
        cc = CV.complete_catalogue(D, 2.0)
        limit = cc["limit"]
        got = {(e["a"], e["b"]) for e in cc["catalogue"]}
        brute = {(e["a"], e["b"]) for e in CV.catalogue(D, 200_000, 400)
                 if CV.best_order(e["steps"], "optimised")[1]["M_eq"] <= limit}
        assert brute <= got and all(e["norm"] <= 200_000 or (e["a"], e["b"]) not in brute for e in cc["catalogue"])
        assert cc["best"] == min(CV.best_order(e["steps"], "optimised")[1]["M_eq"] for e in cc["catalogue"])
    assert CV.complete_catalogue(-619, 2.0)["best"] == 80


def test_bandersnatch_sqrt_minus_2_is_a_verified_degree_2_endomorphism():
    T = _ark_target("ed_on_bls12_381_bandersnatch")
    r = CV.sweep_curve(T, -8, source="test", build=True)
    assert r.kind == "chain" and r.best_order == [2] and r.best_verified and r.eigenvalues_consistent
    assert r.best_chain_M_eq["optimised"] == 6 and r.model_ops["ratio"] > 1.4


def test_automorphism_curves_verify_the_unit():
    T = next(t for t in TG.deployed_targets() if t.name == "secp256k1")
    ok, lam, what = CV.verify_automorphism(TG.verify(T), -3)
    assert ok and pow(lam, 3, T.n) == 1 and lam != 1


def test_checkpoint_resumes_finished_curves_only(tmp_path):
    path = tmp_path / "checkpoint.jsonl"
    path.write_text(_json.dumps({"name": "done", "D": -3, "kind": "automorphism"}) + "\n"
                    + _json.dumps({"name": "failed", "D": -91, "error": "TimeoutError: budget"}) + "\n"
                    + '{"name": "trunc')                                   # the run died mid-line
    assert set(CV._load_checkpoint(str(path))) == {"done"}
    assert CV._load_checkpoint(str(tmp_path / "missing.jsonl")) == {} and CV._load_checkpoint(None) == {}


def test_scalar_frobenius_kernels_are_grouped_by_subgroup():
    """43 divides the conductor of Z[pi] on the GOST 2001 test curve and Frobenius is the scalar 7 on E[43]:
    all 44 subgroups are rational, f_43 splits into 308 cubics, and every kernel is a product of 7 of them."""
    pytest.importorskip("flint")
    T = TG.verify(next(t for t in TG.deployed_targets() if t.name == "GOST 2001 test curve"))
    p, a, b = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p
    t = p + 1 - T.n * T.h
    assert (t * t - 4 * p) % 43 == 0
    ks = EX.rational_kernels(TV.Curve(p, a, b), 43, EX.division_polynomials_flint(p, a, b, 45), trace=t)
    assert len(ks) == 44 and {len(k) - 1 for k in ks} == {21}
    cr = EX.build_chain_endomorphism(p, a, b, T.n, T.h, -915, (8, 1), curve_name=T.name, steps=(43, 7),
                                     conjugates=False, omega_root=QO.omega_eigenvalues(-915, T.n)[0])
    assert cr.found


# --- NIST: binary curves --------------------------------------------------------

from harness.endosweep import binary as BI    # noqa: E402
from harness.endosweep import nist as NI      # noqa: E402

_F163 = (163, (7, 6, 3, 0))
_K163 = dict(a=1, b=1, n=0x04000000000000000000020108A2E0CC0D99F8A5EF, h=2,
             G=(0x02FE13C0537BBC11ACAA07D793DE4E6D5E5C94EEE8, 0x0289070FB05D38FF58321F2E800536D538CCDAA3D9))
_B163 = dict(a=1, b=0x020A601907B8C953CA1481EB10512F78744A3205FD, n=0x040000000000000000000292FE77E70C12A4234C33, h=2,
             G=(0x03F0EBA16286A2D57EA0991168D4994637E8343E36, 0x00D51FBC6C71A0094FA2CDD545B11C5C0C797324F1))


def _bcurve(c):
    return BI.BinaryCurve(BI.Field(*_F163), c["a"], c["b"])


def test_binary_field_and_lopez_dahab_formulas_agree_with_affine():
    import random
    rng = random.Random(3)
    for c in (_K163, _B163):
        E = _bcurve(c)
        F = E.F
        x = rng.getrandbits(163)
        assert F.mul(x, F.inv(x)) == 1 and F.sqr(x) == F.mul(x, x) and F.sqr(F.sqrt(x)) == x
        for _ in range(4):
            P, Q = E.random_point(rng), E.random_point(rng)
            assert E.on_curve(P) and E.on_curve(Q)
            D = E.ld_dbl(E.ld(P))
            assert E.ld_to_affine(D) == E.dbl(P)
            assert E.ld_to_affine(E.ld_madd(E.ld(P), Q)) == E.add(P, Q)
            assert E.ld_to_affine(E.ld_madd(D, Q)) == E.add(E.dbl(P), Q)
            assert E.batch_to_affine([D, E.ld_frobenius(D)]) == [E.dbl(P), E.frobenius(E.dbl(P))]
        assert E.ld_madd(E.ld(P), E.neg(P)) is BI.INF


def test_binary_curves_verify_and_koblitz_tau_is_an_endomorphism():
    for c in (_K163, _B163):
        E = _bcurve(c)
        v = BI.verify(E, c["n"], c["h"], c["G"])
        assert v.ok, v.note
        scan = QO.small_discriminant_scan(QO.frobenius_discriminant(E.F.q, v.trace), 10_000)
        assert (scan.found == -7) == BI.is_koblitz(E)
    E = _bcurve(_K163)
    kob, checks = BI.koblitz(E, _K163["n"], _K163["h"], _K163["G"])
    assert all(checks.values()), checks
    assert kob.mu == 1 and (kob.lam ** 2 - kob.lam + 2) % kob.n == 0
    bad = BI.verify(_bcurve(_K163), _K163["n"], _K163["h"] + 2, _K163["G"])
    assert not bad.ok


def test_tnaf_and_wnaf_agree_and_count_what_they_execute():
    import random
    E = _bcurve(_K163)
    n, G = _K163["n"], _K163["G"]
    kob, _ = BI.koblitz(E, n, _K163["h"], G)
    rng = random.Random(5)
    for k in [rng.randrange(1, n) for _ in range(3)]:
        ref = E.mul_affine(k, G)
        for w in (2, 4, 5):
            tw, alpha = BI.tnaf_constants(kob, w)
            assert alpha[1] == (1, 0)
            R, c = BI.mul_tnaf_counted(E, kob, k, G, w, (tw, alpha))
            assert R == ref
            d = BI.tnaf(tuple(c["rho"]), kob, w, tw, alpha)
            nz = sum(1 for x in d if x)
            assert c["main"] == {"M": 8 * (nz - 1), "S": 3 * (len(d) - 1) + 5 * (nz - 1), "I": 0}
            R2, c2 = BI.mul_wnaf_counted(E, k, G, w)
            assert R2 == ref
            d2 = BI.wnaf(k, w)
            nz2 = sum(1 for x in d2 if x)
            assert c2["main"] == {"M": 3 * (len(d2) - 1) + 8 * (nz2 - 1), "S": 5 * (len(d2) - 1) + 5 * (nz2 - 1), "I": 0}
            assert len(d) <= 163 + 4                     # partial reduction keeps the expansion about m long


def test_exact_discriminant_from_a_checked_factorization():
    # P-224: 4q - t^2 = 3^3 * 29 * 79 * 7523 * 40927 * 11549194661 * p45
    N = 85437550031088170535288062946642707984656696913911429425696631461483
    fac = [[3, 3], [29, 1], [79, 1], [7523, 1], [40927, 1], [11549194661, 1],
           [388425074903852603481408727235725774844022299, 1]]
    checked = NI.check_factorization(N, fac)
    DK, f = NI.exact_discriminant(-N, checked)
    assert f == 3 and DK * f * f == -N and QO.is_fundamental(DK)
    with pytest.raises(ValueError):
        NI.check_factorization(N, fac[:-1])
    with pytest.raises(ValueError):
        NI.check_factorization(N * 4, fac + [[4, 1]])


def test_min_nonscalar_degree_closed_form_matches_brute_force():
    for D in range(-3, -3000, -1):
        if not QO.is_discriminant(D):
            continue
        brute = min(QO.norm(D, a, 1) for a in range(-abs(D) // 2 - 2, abs(D) // 2 + 3))
        assert QO.min_nonscalar_degree(D) == brute, D
    assert QO.min_nonscalar_degree(-(2 ** 255)) == 2 ** 253 and QO.min_nonscalar_degree(-(2 ** 255 + 3)) == 2 ** 253 + 1


def test_nist_results_rest_on_checked_certificates():
    base = _os.path.join(_os.path.dirname(__file__), "..", "research", "endosweep_nist_20261006")
    certs = NI.load_factorizations(_os.path.join(base, "factorizations.jsonl"))     # re-multiplied, primes re-tested
    assert len(certs) == 11
    doc = _json.load(open(_os.path.join(base, "nist.json")))
    assert len(doc["curves"]) == 20 and all(r["verified"] for r in doc["curves"].values())
    for name, r in doc["curves"].items():
        q, t = int(r["q"]), int(r["t"])
        if r["exact"]:
            DK, f = int(r["exact"]["D_K"]), int(r["exact"]["f"])
            assert DK * f * f == t * t - 4 * q, name
            if "factorization" in r["exact"]:
                fac = certs[4 * q - t * t]
                core = 1
                for p, e in fac:
                    core *= p ** (e % 2)
                # fundamental: the squarefree core itself (= 3 mod 4) or four times it (core = 1, 2 mod 4)
                assert DK == -core if core % 4 == 3 else DK == -4 * core, name
            else:
                assert QO.is_fundamental(DK), name
        else:
            assert name == "nist/B-571" and r["bound"]["abs_D_K_at_least"] > 10 ** 15
        if name.startswith("nist/K-"):
            assert r["exact"]["D_K"] == -7 and r["tau"]["all_checks_pass"]
            assert r["summary"]["S_free"]["ratio"] > 2 and r["summary"]["S_equals_M"]["ratio"] > 1.5


def test_partial_certificate_raises_the_b571_bound(tmp_path):
    base = _os.path.join(_os.path.dirname(__file__), "..", "research", "endosweep_nist_20261006")
    partials = NI.load_partial_certificates(_os.path.join(base, "factorizations.jsonl"))
    assert len(partials) == 1
    (N, known), = partials.items()
    part = NI.partial_factorization(N, bound=10 ** 4, known=known)
    assert not part["complete"] and part["cofactor_digits"] == 130 and not part["cofactor_square"]
    assert part["abs_D_K_at_least"] == 137 * 1502689 * 5608493523058319 * 3563521804312876303 * 10 ** 4
    bad = tmp_path / "bad.jsonl"
    bad.write_text(_json.dumps({"N": str(N), "partial_factors": [["137", 1]], "cofactor": str(N // 137 - 1)}) + "\n")
    with pytest.raises(ValueError):
        NI.load_partial_certificates(str(bad))
