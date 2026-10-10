#!/usr/bin/env python3
"""Frozen reversible NCT circuit builders for EXP-CSIDH-906d0e.

build_F and build_I construct the two frozen circuits of
experiments/EXP-CSIDH-906d0e/specification.yaml for one discriminant and
one input pair, mirroring classgroup.py step for step. The gate sequence
is data-independent, so the allocation width and the gate counts are the
same for every input pair; the driver records that as an instrument check.
"""
from __future__ import annotations

from reversible import Circuit, WIDTH, MASK

REDUCTION_BOUND = 8
FIX_BOUND = 3


def _signed16(v: int) -> int:
    return v & MASK


def _bit_and(c: Circuit, x: int, y: int) -> int:
    """Fresh bit: x AND y."""
    out = c._alloc()
    c.tof(x, y, out)
    return out


def _eq_bits(c: Circuit, r1: list[int], r2: list[int]) -> int:
    """Fresh bit: register equality (bitwise xor-reduce then NOR)."""
    acc = c._alloc()
    c.x(acc)
    for i in range(WIDTH):
        d = c._alloc()
        c.cnot(r1[i], d)
        c.cnot(r2[i], d)
        nd = c._alloc()
        c.x(nd)
        c.cnot(d, nd)
        acc = _bit_and(c, acc, nd)
    return acc


class BuiltCircuit:
    def __init__(self, circuit: Circuit, out_regs: dict[str, list[int]],
                 ok_bit: int) -> None:
        self.circuit = circuit
        self.out = out_regs
        self.ok_bit = ok_bit

    def output_form(self) -> tuple[int, int, int]:
        c = self.circuit
        return (c.signed(self.out["a"]), c.signed(self.out["b"]),
                c.signed(self.out["c"]))

    def refused(self) -> bool:
        return not self.circuit._get(self.ok_bit)


def _validation(c: Circuit, ins: dict[str, list[int]], disc: int) -> int:
    """Parity and discriminant equations for both forms.

    Returns a fresh bit that is 1 when both inputs are valid forms of the
    frozen discriminant with positive a and odd b.
    """
    valid = c._alloc()
    c.x(valid)
    for idx in (1, 2):
        b = ins[f"b{idx}"]
        a = ins[f"a{idx}"]
        cc = ins[f"c{idx}"]
        # parity: b odd (b[0] is a control bit, never written)
        # a > 0
        apos = c._alloc()
        c.x(apos)
        c.cnot(c.is_neg(a), apos)
        c.cnot(c.eq_reg(a, 0), apos)
        # disc equation: b^2 - 4ac == disc
        bsq = c.mul(b, b)
        four = c.reg(4)
        a4 = c.mul(four, a)
        fourac = c.mul(a4, cc)
        d = c.sub(bsq, fourac)
        eq = c.eq_reg(d, _signed16(disc))
        term = _bit_and(c, _bit_and(c, b[0], apos), eq)
        valid = _bit_and(c, valid, term)
    return valid


def _gauss_reduce(c: Circuit, a: list[int], b: list[int], cc: list[int],
                  disc: int) -> tuple[list[int], list[int], list[int]]:
    """The frozen 8-iteration Gauss reduction, idempotent on reduced forms."""
    minus_disc = c.reg(-disc)
    four = c.reg(4)
    for _ in range(REDUCTION_BOUND):
        two_a = c.add(a, a)
        _q, r = c.fdivmod(b, two_a)
        gt = c.cmps_lt(a, r)  # r > a
        r2 = c.sub(r, two_a)
        b2 = c.csel(gt, r2, r)
        bsq = c.mul(b2, b2)
        num = c.add(bsq, minus_disc)
        four_a = c.mul(four, a)
        c2, _r2 = c.fdivmod(num, four_a)
        swap = c.cmps_lt(c2, a)  # a > c
        a3 = c.csel(swap, c2, a)
        c3 = c.csel(swap, a, c2)
        b3 = c.csel(swap, c.neg(b2), b2)
        # edge convention: when a = c the reduced representative takes b >= 0
        eqac = _eq_bits(c, a3, c3)
        flip = _bit_and(c, eqac, c.is_neg(b3))
        b3 = c.csel(flip, c.neg(b3), b3)
        a, b, cc = a3, b3, c3
    return a, b, cc


def _write_outputs(c: Circuit, valid: int, a: list[int], b: list[int],
                   cc: list[int]) -> dict[str, list[int]]:
    out_a = c.output_reg()
    out_b = c.output_reg()
    out_c = c.output_reg()
    for i in range(WIDTH):
        c.tof(a[i], valid, out_a[i])
        c.tof(b[i], valid, out_b[i])
        c.tof(cc[i], valid, out_c[i])
    return {"a": out_a, "b": out_b, "c": out_c}


def build_F(disc: int, f1: tuple[int, int, int], f2: tuple[int, int, int]) -> BuiltCircuit:
    """Circuit-F: Dirichlet composition + reduction (frozen algorithm)."""
    c = Circuit()
    ins = {
        "a1": c.input_reg(f1[0]), "b1": c.input_reg(f1[1]), "c1": c.input_reg(f1[2]),
        "a2": c.input_reg(f2[0]), "b2": c.input_reg(f2[1]), "c2": c.input_reg(f2[2]),
    }
    valid = _validation(c, ins, disc)

    fa1, fb1, fc1 = ins["a1"], ins["b1"], ins["c1"]
    for _ in range(FIX_BOUND):
        g = c.gcd(fa1, ins["a2"])
        coprime = c.eq_reg(g, 1)
        # T transform of the first form (identity when already coprime);
        # the CRT congruence b1 = b2 (mod 2) holds because both b's are
        # validated odd.
        s1 = c.add(c.add(fa1, fb1), fc1)
        s2 = c.add(fb1, c.add(fc1, fc1))
        fa1 = c.csel(coprime, fa1, s1)
        fb1 = c.csel(coprime, fb1, s2)
        fc1 = c.csel(coprime, fc1, fc1)
    # final coprimality check on the fixed forms
    g = c.gcd(fa1, ins["a2"])
    g_one = c.eq_reg(g, 1)
    valid2 = _bit_and(c, valid, g_one)

    # CRT: half = (b2 - b1)/2 ; inv = s mod a2 from ext_gcd(a1, a2)
    diff = c.sub(ins["b2"], fb1)
    half = c.asr1(diff)
    _gg, s, _t = c.ext_gcd(fa1, ins["a2"])
    _qi, inv = c.fdivmod(s, ins["a2"])
    _qh, halfm = c.fdivmod(half, ins["a2"])
    prod = c.mul(halfm, inv)
    _qt, tt = c.fdivmod(prod, ins["a2"])
    two_a1 = c.add(fa1, fa1)
    m1t = c.mul(two_a1, tt)
    bmid = c.add(fb1, m1t)
    amid = c.mul(fa1, ins["a2"])
    bsq = c.mul(bmid, bmid)
    minus_disc = c.reg(-disc)
    num = c.add(bsq, minus_disc)
    four = c.reg(4)
    four_am = c.mul(four, amid)
    cmid, _rc = c.fdivmod(num, four_am)

    ra, rb, rc = _gauss_reduce(c, amid, bmid, cmid, disc)
    outs = _write_outputs(c, valid2, ra, rb, rc)
    return BuiltCircuit(c, outs, valid2)


def build_I(disc: int, f1: tuple[int, int, int], f2: tuple[int, int, int]) -> BuiltCircuit:
    """Circuit-I: ideal multiplication + reduction (frozen algorithm)."""
    c = Circuit()
    ins = {
        "a1": c.input_reg(f1[0]), "b1": c.input_reg(f1[1]), "c1": c.input_reg(f1[2]),
        "a2": c.input_reg(f2[0]), "b2": c.input_reg(f2[1]), "c2": c.input_reg(f2[2]),
    }
    valid = _validation(c, ins, disc)

    omega_const = c.reg((disc - 1) // 4)
    one = c.reg(1)
    # m_i = (-b_i - 1) / 2
    nb1 = c.sub(c.neg(ins["b1"]), one)
    m1 = c.asr1(nb1)
    nb2 = c.sub(c.neg(ins["b2"]), one)
    m2 = c.asr1(nb2)
    # the four product generators (ring: omega^2 = omega + (disc-1)/4)
    v1x = c.mul(ins["a1"], ins["a2"])
    v1y = c.reg(0)
    v2x = c.mul(ins["a1"], m2)
    v2y = c.copy(ins["a1"])
    v3x = c.mul(ins["a2"], m1)
    v3y = c.copy(ins["a2"])
    v4x = c.add(c.mul(m1, m2), omega_const)
    v4y = c.add(c.add(m1, m2), one)
    # content k = gcd of all eight coordinates
    k = c.gcd(c.abs(v1x), c.abs(v1y))
    for x in (v2x, v2y, v3x, v3y, v4x, v4y):
        k = c.gcd(k, c.abs(x))
    # g23 = gcd(a1, a2); ext-gcd #1 gives the (s, t) column combination
    g23 = c.gcd(c.abs(v2y), c.abs(v3y))
    _g1, s, t = c.ext_gcd(c.abs(v2y), c.abs(v3y))
    cAx = c.add(c.mul(s, v2x), c.mul(t, v3x))
    cAy = c.add(c.mul(s, v2y), c.mul(t, v3y))
    a2g, _ra = c.fdivmod(ins["a2"], g23)
    a1g, _rb = c.fdivmod(ins["a1"], g23)
    cBx = c.sub(c.mul(a2g, v2x), c.mul(a1g, v3x))
    cBy = c.sub(c.mul(a2g, v2y), c.mul(a1g, v3y))
    # g4 = gcd(g23, |v4y|); ext-gcd #2 with the sign-fixed coefficient
    y4neg = c.is_neg(v4y)
    y4abs = c.csel(y4neg, c.neg(v4y), v4y)
    g4 = c.gcd(c.abs(g23), y4abs)
    _g2, s2, t2raw = c.ext_gcd(c.abs(g23), y4abs)
    t2 = c.csel(y4neg, c.neg(t2raw), t2raw)
    cWx = c.add(c.mul(s2, cAx), c.mul(t2, v4x))
    cWy = c.add(c.mul(s2, cAy), c.mul(t2, v4y))
    y4g, _ry = c.fdivmod(v4y, g4)
    g23g, _rg = c.fdivmod(g23, g4)
    cCx = c.sub(c.mul(y4g, cAx), c.mul(g23g, v4x))
    cCy = c.sub(c.mul(y4g, cAy), c.mul(g23g, v4y))
    # refusal check: h3 = g4 must equal the content k
    h3_eq_k = _eq_bits(c, g4, k)
    # h1 = gcd(v1x, cBx, cCx)
    h1 = c.gcd(c.abs(v1x), c.abs(cBx))
    h1 = c.gcd(h1, c.abs(cCx))
    # A = h1 / k ; M = (cWx / k) mod A
    A, _rA = c.fdivmod(h1, k)
    wk, _rk = c.fdivmod(cWx, k)
    _qM, M = c.fdivmod(wk, A)
    ok = _bit_and(c, valid, h3_eq_k)
    # form (A, -2M-1, (b'^2 - disc)/(4A))
    two_M = c.add(M, M)
    bp = c.neg(c.add(two_M, one))
    bpsq = c.mul(bp, bp)
    minus_disc = c.reg(-disc)
    num = c.add(bpsq, minus_disc)
    four = c.reg(4)
    four_A = c.mul(four, A)
    cprime, _rc2 = c.fdivmod(num, four_A)

    ra, rb, rc = _gauss_reduce(c, A, bp, cprime, disc)
    outs = _write_outputs(c, ok, ra, rb, rc)
    return BuiltCircuit(c, outs, ok)
