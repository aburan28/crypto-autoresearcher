"""Tests for harness/endosweep/frobenius.py (Frobenius expansions over F_2, F_3, F_4) and blinding.py (GLV blinding)."""
from __future__ import annotations

import random

import pytest

from harness.endosweep import blinding as BL
from harness.endosweep import frobenius as FR
from harness.endosweep import lattice as LA


# --- Z[phi] and expansions ----------------------------------------------------

@pytest.mark.parametrize("q,t,w", [(2, 1, 4), (2, -1, 5), (3, 1, 2), (3, -2, 3), (4, 1, 2), (4, -1, 3), (4, 3, 2)])
def test_expansion_round_trips_and_terminates(q, t, w):
    ds = FR.digit_set(q, t, w)
    Z = FR.Zphi(q, t)
    rng = random.Random(q * 100 + t * 10 + w)
    for _ in range(50):
        rho = (rng.randrange(-10 ** 30, 10 ** 30), rng.randrange(-10 ** 30, 10 ** 30))
        dg = FR.expand(ds, rho)
        assert FR.evaluate(ds, dg) == rho
        # after a nonzero digit the next w - 1 digits are zero
        for i, d in enumerate(dg[:-1]):
            if d:
                assert all(x == 0 for x in dg[i + 1:i + w])
    assert FR.termination_certificate(ds)["all_terminate"]
    for u, al in ds.alpha.items():
        assert (al[0] + al[1] * ds.s_w - u) % q ** w == 0       # alpha_u = u (mod phi^w)
    assert Z.div_phi(Z.mul((5, 7), (0, 1))) == (5, 7)


def test_bits_per_nonzero_digit_law():
    inst = FR.instance(3, -1, 59)
    Z = FR.Zphi(3, -1)
    ks = [random.Random(i).randrange(1, inst.n) for i in range(300)]
    for w in (1, 2, 3):
        st = FR.expansion_stats(Z, FR.digit_set(3, -1, w), inst.delta, ks)
        measured = FR.log2(3) / st["density"]
        assert abs(measured - FR.bits_per_nonzero_predicted(3, w)) < 0.3      # m = 59: end effects
        assert abs(st["mean_length"] - inst.m) < 3


def test_instances_and_q4_split():
    assert FR.instance(3, -1, 59) is not None and FR.instance(3, -1, 61) is None
    I = FR.instance(2, 1, 163)
    assert I.h == 2 and I.n.bit_length() == 163
    assert FR.q4_koblitz_split((67, 101))["n_equals_product_of_two_Koblitz_cofactor_quotients"]
    fam = FR.families()
    assert sorted(fam[3]) == [-2, -1, 1, 2] and sorted(fam[4]) == [-3, -1, 1, 3]


def test_char3_field_inverse_and_cube():
    k, c1, c0 = FR.find_trinomial_f3(23)
    F = FR.Char3Field(23, k, c1, c0)
    rng = random.Random(1)
    for _ in range(5):
        a = F.random(rng)
        if a == F.zero:
            continue
        assert F._mul(a, F.inv(a)) == F.one
        assert F.cube(a) == F._mul(F._mul(a, a), a)


def test_char3_expansion_on_points_and_model_exact():
    fam = FR.families()
    inst = FR.instance(3, -1, 59)
    curve = next(c for c in fam[3][-1] if c["a4"] == 0)
    r = FR.verify_char3(inst, curve, scalars=2, counted=2, widths=(1, 2))
    assert r["all_checks_pass"], r["checks"]


def test_f4_twist_class_on_points_and_model_exact():
    fam = FR.families()
    inst = FR.instance(4, -1, 31)
    curve = fam[4][-1][0]
    assert curve["a"] not in (0, 1)                    # a = w: the +1M class of the cost table
    r = FR.verify_char2_f4(inst, curve, scalars=2, counted=2, widths=(1, 2))
    assert r["all_checks_pass"], r["checks"]


def test_koblitz_crosscheck_against_binary_py():
    r = FR.koblitz_crosscheck(163, 1, ks=1, widths=(2, 4))
    assert r["delta_equals_binary_py"] and r["digits_equal_solinas_tnaf"]
    assert r["stub_counts_equal_binary_py_counts"]


# --- blinding -------------------------------------------------------------------

def _secp():
    return BL._secp256k1()


def test_classical_blinding_is_erased_by_decomposition():
    c = _secp()
    red = LA.reduce(c.lams, c.n)
    dec = BL.Decomposer(red)
    rng = random.Random(3)
    for _ in range(200):
        k = rng.randrange(1, c.n)
        assert dec.decompose_unreduced(k) == red.decompose(k)
        assert dec.decompose_unreduced(k + rng.randrange(1 << 64) * c.n) == red.decompose(k)


def test_c5_blinding_reconstructs_and_costs_e_over_d():
    c = _secp()
    red = LA.reduce(c.lams, c.n)
    rng = random.Random(4)
    extra = []
    for _ in range(300):
        k = rng.randrange(1, c.n)
        v = red.decompose(k)
        x, r = BL.blind(v, red.basis, BL.split_bits(64, 2), rng)
        assert BL.reconstructs(x, c.lams, k, c.n)
        assert all(-(1 << 31) <= ri < (1 << 31) for ri in r)
        extra.append(max(abs(a).bit_length() for a in x) - max(abs(a).bit_length() for a in v))
    assert abs(sum(extra) / len(extra) - 32) < 1.5


def test_lattice_geometry_and_exact_entropy():
    c = _secp()
    red = LA.reduce(c.lams, c.n)
    lam1 = BL.lambda1_inf(red)
    assert 0 < lam1 <= min(LA.inf_norm(b) for b in red.basis)
    s0 = lam1.bit_length() - 1
    assert BL.box_count(red, [s0, s0]) == 1               # nothing but 0 below lambda_1^inf
    v = red.decompose(random.Random(5).randrange(1, c.n))
    assert BL.exact_window_entropy(red, v, [5, 5], [s0, s0]) == pytest.approx(10.0)
    assert BL.split_bits(64, 4) == [16, 16, 16, 16] and sum(BL.split_bits(65, 4)) == 65
