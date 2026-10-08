"""Tests for harness/endosweep/msm.py (Pippenger model + counted MSM) and alphaadic.py."""
from __future__ import annotations

import random
from collections import Counter

import numpy as np
import pytest

from harness.endosweep import alphaadic as AA
from harness.endosweep import lattice as LA
from harness.endosweep import msm as MS
from harness.endosweep import quadorder as QO


# --- hexagonal digits ------------------------------------------------------------

@pytest.mark.parametrize("h", [2, 3, 4, 5, 6, 8, 9, 12, 16])
def test_hexagon_is_complete_residue_system_with_orbit_weights(h):
    digits = {MS.hex_rep(a, b, h) for a in range(h) for b in range(h)}
    assert len(digits) == h * h
    assert MS.hex_buckets(h)["digits"] == h * h
    brute = Counter(MS.rotate_to_sector(x, y)[:2] for x, y in digits if (x, y) != (0, 0))
    bx, by, prob = MS._hex_arrays(h)
    mine = {(int(x), int(y)): round(p * h * h) for x, y, p in zip(bx, by, prob)}
    assert brute == Counter(mine)


def test_rotation_is_multiplication_by_a_unit():
    for x in range(-6, 7):
        for y in range(-6, 7):
            if (x, y) == (0, 0):
                continue
            xs, ys, j = MS.rotate_to_sector(x, y)
            assert xs >= 1 and ys >= 0
            assert QO.multiply(-3, QO.power(-3, (0, 1), j), (xs, ys)) == (x, y)


def test_hex_expansion_reconstructs_and_radix2_is_refused():
    rng = random.Random(3)
    for _ in range(300):
        a, b = rng.randrange(-10 ** 12, 10 ** 12), rng.randrange(-10 ** 12, 10 ** 12)
        for c in (2, 3, 5, 8):
            e = MS.hex_expand(a, b, c)
            assert sum(x << (c * i) for i, (x, _) in enumerate(e)) == a
            assert sum(y << (c * i) for i, (_, y) in enumerate(e)) == b
    with pytest.raises(ValueError):
        MS.hex_expand(-1, 0, 1)


def test_signed_windows():
    for c in range(1, 8):
        W = 12 // c + 1
        for m in range(4096):
            d = MS.signed_windows(m, c, W)
            assert sum(x << (c * i) for i, x in enumerate(d)) == m
            assert all(abs(x) <= 1 << (c - 1) for x in d)


def test_uniform_window_closed_form_matches_general():
    for c in (2, 4, 7):
        for npts in (16, 300, 5000):
            B = 1 << (c - 1)
            pv = np.full(B + 1, 2.0 / (1 << c))
            pv[0] = pv[B] = 1.0 / (1 << c)
            u, g = MS.uniform_window_1d(c, npts), MS.general_window_1d(pv, npts)
            for k in ("acc", "run_r", "run_t", "nonempty"):
                assert u[k] == pytest.approx(g[k], rel=1e-9, abs=1e-9)


# --- the model against the counted implementation -------------------------------------

@pytest.fixture(scope="module")
def secp():
    cv = MS.secp256k1()
    spec = next(s for s in MS.curve_specs() if s.name == "secp256k1")
    return cv, spec, MS.shapes(spec)


@pytest.mark.parametrize("mode", ["mixed", "batch_affine"])
def test_counted_msm_is_correct_and_matches_model(secp, mode):
    cv, spec, (plain_s, glv_s, g, fold_s) = secp
    rng = random.Random(7)
    N = 128
    pts, ks, expected = MS._instance(cv, N, rng)
    red_glv = LA.reduce([1, cv.lam3], cv.n)
    red_fold = LA.reduce([1, cv.lam_omega], cv.n)
    costs = MS.op_costs(spec.model, mode)
    models = {"plain": MS.model_1d(N, 5, plain_s, costs, variant="plain"),
              "glv": MS.model_1d(N, 6, glv_s, costs, variant="glv", endo_M=N * 1.0),
              "fold": MS.model_fold(N, 3, fold_s, costs)}
    for variant, m in models.items():
        R, W, F, J = MS.run_counted(cv, variant, mode, pts, ks, m.c, red_glv, red_fold)
        assert R == expected
        o = J.ops
        assert F.M == (2 * o["dbl"] + 11 * o["add"] + 7 * o["madd"] + 2 * o["aff"] + o["endo_M"]
                       + 3 * o["aff"] - 3 * o["inv_rounds"])
        assert F.S == 5 * o["dbl"] + 5 * o["add"] + 4 * o["madd"] + o["aff"]
        assert abs(F.total_M - m.total_M) / m.total_M < 0.03, (variant, F.total_M, m.total_M)


def test_glv_conserves_accumulation_but_halves_aggregation(secp):
    """The hypothesis' first claim in its own terms: at a common window the
    split keeps the accumulation count and roughly halves the bucket work."""
    cv, spec, (plain_s, glv_s, g, fold_s) = secp
    costs = MS.op_costs(spec.model, "mixed")
    N, c = 1 << 16, 13
    p, q = MS.model_1d(N, c, plain_s, costs, variant="plain"), MS.model_1d(N, c, glv_s, costs, variant="glv")
    assert q.acc_adds == pytest.approx(p.acc_adds, rel=0.06)
    assert (q.run_r_adds + q.run_t_adds) / (p.run_r_adds + p.run_t_adds) == pytest.approx(0.5, rel=0.1)


def test_curve_specs_eigenvalues():
    for s in MS.curve_specs():
        tau, nw = QO.omega_trace_norm(s.D)
        assert (s.lam_omega ** 2 - tau * s.lam_omega + nw) % s.n == 0
        assert s.lam == (s.alpha[0] + s.alpha[1] * s.lam_omega) % s.n


# --- alpha-adic ------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cpb():
    return next(c for c in MS.load_inputs()["curves"] if c["name"] == "gost/CryptoPro-B")


def test_ideal_hnf_residues():
    for D, g in ((-619, (4, 1)), (-8, (0, 1)), (-8, QO.power(-8, (0, 1), 3)), (-339, (5, 2))):
        I = AA.Ideal.of(D, g)
        assert I.A * I.C == QO.norm(D, *g)
        assert I.contains(g) and I.contains(QO.multiply(D, g, (0, 1)))
        assert not I.contains((1, 0))


def test_alpha_expansions_reconstruct_k(cpb):
    n = int(cpb["n"], 16)
    lam_w = int(cpb["rows"][0]["lam_omega"], 16)
    red = AA.NormReducer(cpb["D"], n, lam_w)
    rng = random.Random(5)
    for rule in (AA.int_rule(-619, (4, 1)), AA.voronoi_rule(-619, (4, 1))):
        assert len(rule.table) == 175
        lam_a = (4 + lam_w) % n
        for _ in range(20):
            k = rng.randrange(1, n)
            z = red.reduce(k)
            assert QO.norm(-619, *z) <= red.norm_bound()
            ds = AA.expand(rule, z)
            acc = 0
            for d in reversed(ds):
                acc = (acc * lam_a + d[0] + d[1] * lam_w) % n
            assert acc == k


def test_termination_certificates():
    assert AA.termination_certificate(AA.int_rule(-619, (4, 1)))["terminates"]
    assert AA.termination_certificate(AA.voronoi_rule(-619, (15, 2)))["terminates"]
    bad = AA.termination_certificate(AA.int_rule(-619, (15, 2)))
    assert not bad["terminates"] and bad["cycle_example"] is not None


def test_naf_digits_are_followed_by_zeros():
    rng = random.Random(9)
    for alpha, w in (((0, 1), 4), ((1, 1), 3)):
        rule = AA.naf_rule(-8, alpha, w)
        for _ in range(20):
            z = (rng.randrange(-10 ** 9, 10 ** 9), rng.randrange(-10 ** 9, 10 ** 9))
            ds = AA.expand(rule, z)
            for i, d in enumerate(ds):
                if d != (0, 0):
                    assert all(x == (0, 0) for x in ds[i + 1:i + w])


def test_alpha_adic_on_points_with_the_real_chain():
    r = AA.verify_on_points(scalars=1)
    assert r["all_ok"] and len(r["checks"]) == 2
