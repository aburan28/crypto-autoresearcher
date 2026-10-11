"""Tests for lambda coordinates (harness/endosweep/lambdacoord.py) and the binary GLS curve (gls.py)."""
from __future__ import annotations

import random

from harness.endosweep import binary as BI
from harness.endosweep import gls as GL
from harness.endosweep import lambdacoord as LC

_F163 = (163, (7, 6, 3, 0))
_K163 = dict(a=1, b=1, n=0x04000000000000000000020108A2E0CC0D99F8A5EF, h=2,
             G=(0x02FE13C0537BBC11ACAA07D793DE4E6D5E5C94EEE8, 0x0289070FB05D38FF58321F2E800536D538CCDAA3D9))
_B163 = dict(a=1, b=0x020A601907B8C953CA1481EB10512F78744A3205FD, n=0x040000000000000000000292FE77E70C12A4234C33, h=2,
             G=(0x03F0EBA16286A2D57EA0991168D4994637E8343E36, 0x00D51FBC6C71A0094FA2CDD545B11C5C0C797324F1))


def _curves(c, field=_F163):
    F = LC.CountedField(*field)
    return F, LC.GeneralCurve(F, c["a"], c["b"]), LC.LambdaCurve(F, c["a"], c["b"])


def test_lambda_formulas_agree_with_affine_including_edge_cases():
    for c in (_K163, _B163):
        _, E, C = _curves(c)
        checks = LC.verify_formulas(E, C, trials=4, seed=9)
        assert all(checks.values()), checks
    # a larger curve: K-283 (a = 0, b = 1), where the alternative doubling keeps its Z^4 term
    _, E, C = _curves(dict(a=0, b=1), (283, (12, 7, 5, 0)))
    checks = LC.verify_formulas(E, C, trials=3, seed=4)
    assert all(checks.values()), checks


def test_operation_counts_are_the_papers_table_3():
    _, E, C = _curves(_B163)
    oc = LC.op_counts(E, C)
    lam, ld = oc["lambda"], oc["LD"]

    def mc(c):
        return (c["M"], c["S"], c["Mc"])
    assert mc(lam["full_addition"]) == (11, 2, 0)
    assert mc(lam["mixed_addition"]) == (8, 2, 0)
    assert mc(lam["doubling_main"]) == (4, 4, 0)                    # m_a free (a = 1)
    assert mc(lam["doubling_alt"]) == (3, 4, 1)                     # one multiplication by a^2 + b
    assert mc(lam["doubling_and_addition"]) == (10, 6, 0)
    assert mc(lam["frobenius"]) == (0, 3, 0)
    assert (lam["affine_to_lambda_affine"]["I"], lam["affine_to_lambda_affine"]["M"]) == (1, 1)
    assert mc(ld["doubling"]) == (3, 5, 1) and mc(ld["mixed_addition"]) == (8, 5, 0)
    assert oc["dbl_formula_used"] == "main"
    _, E, C = _curves(_K163)
    oc = LC.op_counts(E, C)
    assert oc["dbl_formula_used"] == "alt"
    assert mc(oc["lambda"]["doubling_alt"]) == (3, 3, 0)            # a^2 + b = 0 on K-163: the Z^4 term vanishes


def test_lambda_scalar_multiplications_match_ld_and_count_what_they_execute():
    F, _, C = _curves(_K163)
    E = BI.BinaryCurve(F, 1, 1)
    n, G = _K163["n"], _K163["G"]
    kob, _ = BI.koblitz(E, n, 2, G)
    rng = random.Random(8)
    for k in [rng.randrange(1, n) for _ in range(2)]:
        ref = E.mul_affine(k, G)
        for w in (2, 4):
            consts = BI.tnaf_constants(kob, w)
            assert BI.mul_wnaf_counted(E, k, G, w)[0] == ref
            R, c = LC.mul_wnaf_lambda(C, k, G, w)
            d = BI.wnaf(k, w)
            L, nz = len(d), sum(1 for x in d if x)
            assert R == ref
            assert (c["main"]["M"], c["main"]["S"]) == (3 * (L - 1) + 8 * (nz - 1), 3 * (L - 1) + 2 * (nz - 1))
            R, c = LC.mul_wnaf_lambda(C, k, G, w, da=True)
            assert R == ref
            assert (c["main"]["M"], c["main"]["S"]) == (3 * (L - nz) + 10 * (nz - 1), 3 * (L - nz) + 6 * (nz - 1))
            R, c = LC.mul_tnaf_lambda(C, kob, k, G, w, consts)
            dt = BI.tnaf(kob.Z.reduce_mod((k, 0), kob.delta), kob, w, *consts)
            Lt, nzt = len(dt), sum(1 for x in dt if x)
            assert R == ref
            assert (c["main"]["M"], c["main"]["S"]) == (8 * (nzt - 1), 3 * (Lt - 1) + 2 * (nzt - 1))
            assert c["convert"]["I"] == 1


def test_scalar_counts_reproduce_binary_py_ld_means():
    F, _, C = _curves(_B163)
    E = BI.BinaryCurve(F, _B163["a"], _B163["b"])
    ld = BI.scalar_counts(E, _B163["G"], _B163["n"], kob=None, widths=(3,), scalars=2, references=1)
    lam = LC.scalar_counts(E, C, _B163["G"], _B163["n"], widths=(3,), scalars=2, references=1)
    assert lam["all_algorithms_agree"] and lam["reference_agrees"]
    assert lam["configs"]["ld/wnaf/w3"]["M"] == ld["configs"]["wnaf/w3"]["M"]
    assert lam["configs"]["ld/wnaf/w3"]["S"] == ld["configs"]["wnaf/w3"]["S"]


def test_fq2_arithmetic_and_counts():
    F = LC.CountedField(13, GL.FIELDS[13])
    K = GL.Fq2(F)
    rng = random.Random(2)
    for _ in range(20):
        a, b = K.random(rng), K.random(rng)
        if a == 0:
            continue
        assert K.mul(a, K.inv(a)) == 1
        assert K.sqr(a) == K.mul(a, a) == K.mul_raw(a, a)
        assert K.sqr(K.sqrt(a)) == a
        assert K.conj(K.mul(a, b)) == K.mul(K.conj(a), K.conj(b)) and K.conj(K.conj(a)) == a
        assert K.mul_u(a) == K.mul(K.u, a) and K.mul_const(b & K.mask, a) == K.mul(b & K.mask, a)
        z = K.solve_quadratic(a)
        assert (z is None) == (K.trace(a) == 1)
        if z is not None:
            assert K.sqr(z) ^ z == a
    K.reset()
    K.mul(3, 5 << 13)
    K.sqr(7)
    assert K.counts()["base_M"] == 3 and K.counts()["base_S"] == 2
    assert K.trace(K.u) == 1                                     # a' = u has trace 1 over F_{q^2}


def test_agm_point_counting_matches_brute_force_and_twist_formula():
    assert GL.is_irreducible(127, (63, 0)) and not GL.is_irreducible(5, (4, 0))   # x^5+x^4+1 = (x^2+x+1)(x^3+x+1)
    rng = random.Random(1)
    for m in (7, 11):
        F = LC.CountedField(m, GL.FIELDS[m])
        for _ in range(3):
            c = rng.randrange(2, 1 << m)
            assert GL.agm_trace(m, GL.FIELDS[m], c) == GL.brute_trace(F, 0, c)
    F = LC.CountedField(5, (2, 0))
    K = GL.Fq2(F)
    for b in (3, 6, 9):
        t = GL.brute_trace(F, 0, b)
        tt = GL.brute_trace(K, K.u, b)
        assert 1024 + 1 - tt == 31 ** 2 + t * t                 # #E~(F_q^2) = (q - 1)^2 + t^2


def test_toy_gls_instance_psi_and_two_dimensional_glv():
    s = GL.find_gls(13, GL.FIELDS[13], seed=5)
    inst = GL.build(13, GL.FIELDS[13], s["b"], s["t"], s["r"])
    assert all(inst["checks"].values()), inst["checks"]
    r, delta = inst["r"], inst["delta"]
    assert (delta * delta + 1) % r == 0
    assert inst["coefficient_bits"]["empirical_max_bits"] <= inst["coefficient_bits"]["bound_bits"] <= 14
    sc = GL.scalar_counts(inst, widths=(2, 3), scalars=3, references=2)
    assert sc["all_algorithms_agree"] and sc["reference_agrees"]
    cf = sc["configs"]
    # psi is free, so the 2-GLV main loop does about half the doublings
    assert cf["lambda/glv-da/w3"]["main_base_M"] < 0.75 * cf["lambda/1d-da/w3"]["main_base_M"]
    oc = GL.op_counts_gls(inst)["Fq_level"]
    assert oc["lambda psi"]["Fq"] == "0M + 0S"
    assert oc["lambda mixed_addition"]["Fq"] == "24M + 4S" and oc["lambda doubling_alt"]["Fq"] == "11M + 8S"
