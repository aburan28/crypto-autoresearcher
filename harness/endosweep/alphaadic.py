"""alpha-adic expansions of scalars on prime-field curves with a cheap chain endomorphism.

On a Koblitz curve the Frobenius tau is free, so writing the scalar in base
tau (``k = sum d_i tau^i``) replaces every doubling by a free map.  On a
prime-field curve with class number above one the cheapest endomorphism
``alpha`` is an isogeny chain (``4 + omega`` of norm 175 on GOST CryptoPro-B,
about 80 M_eq with an affine input), and the question is whether the same
trick pays: expand ``k`` in base ``alpha``, evaluate by Horner
``Q <- alpha(Q) + d_i P``.  The quick estimate compares the chain's price
per bit, ``C_alpha / log2 N(alpha)``, with a doubling; a reviewer pointed out
that this assumes the same addition density per bit, and a digit set modulo
``N(alpha)`` does not have it.  This module measures it.

What it does, for every element of the cheap-chain catalogue of each curve
(``research/endosweep_msm_20261008/curves.input.json``, frozen from the
chain and curve sweeps):

1. **reduction** -- ``k`` is first reduced to ``z = x + y*omega`` in ``O_K``
   with ``z -> k (mod n)`` under ``omega -> lambda_omega`` and ``N(z)``
   small: Lagrange reduction of the relation lattice under the norm form,
   then Babai rounding (``N(z) / n`` is reported).  Without it the expansion
   of the integer ``k`` is twice as long (the ``unreduced`` ablation);
2. **digit sets** -- ``int``: the balanced integers modulo ``N(alpha)``
   (a complete residue system because ``alpha`` is primitive, so
   ``O/(alpha) = Z/N(alpha)``; the table is ``1..(N-1)/2`` times ``P``);
   ``voronoi``: the minimal-norm representative of every class of
   ``O/(alpha)`` (elements ``x + y*omega``, the table needs ``omega(P)``);
   ``naf<w>``: width-``w`` alpha-NAF, digits the minimal-norm
   representatives of the classes of ``O/(alpha^w)`` prime to ``alpha``,
   so every non-zero digit is followed by ``w - 1`` zeros -- only offered
   where the table ``(N^w - N^(w-1))/2`` stays below ``NAF_TABLE_CAP``,
   i.e. for norm 2 and 3; residues modulo any ideal are computed from its
   Hermite normal form;
3. **termination** -- ``|T(z)| <= (|z| + R)/|alpha|`` with ``R`` the largest
   digit, so every orbit enters the disk ``|z| <= R/(|alpha| - 1)`` and
   stays there; every element of that disk is iterated to 0 (or a cycle is
   reported), which is a complete proof for the digit rule used;
4. **cost** -- ``(L - 1)`` applications of ``alpha`` to a Jacobian point
   (every step a general step: the chain sweep's affine-first saving does
   not apply inside Horner), ``(nnz - 1)`` additions (mixed with an affine
   table, full with a Jacobian table), the table and, for ``voronoi`` and
   ``naf``, ``omega(P)``; mean +- sd over ``samples`` scalars;
5. **comparison** -- the same curve's width-w NAF and 2-GLV from
   ``costmodel.multiscalar_cost`` (analytic, S = 0.8 M, I = 100 M) and from
   ``curvesweep.scalar_model`` (the sweep's own recoding with the curve's
   arithmetic, M_eq = M + S, Fermat inversion);
6. **verification** -- every expansion is checked to reconstruct ``k`` modulo
   ``n`` through ``lambda_alpha``; on CryptoPro-B a few are evaluated on
   points with the real ``4 + omega`` chain (``chains.constants.json``).

Operation counts, not timings.

    python -m harness.endosweep.alphaadic --out-dir research/endosweep_msm_20261008
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import time
from dataclasses import dataclass, field
from fractions import Fraction

from . import costmodel as CM
from . import curvesweep as CV
from . import lattice as LA
from . import msm as MS
from . import quadorder as QO

FORMAT = "endosweep-alphaadic/1"
GENERATOR = "harness/endosweep/alphaadic.py"
NAF_TABLE_CAP = 64
CHAINS_JSON = os.path.join("research", "endosweep_chainsweep_20261006", "chains.constants.json")


# ---------------------------------------------------------------------------
# O_K arithmetic helpers (quadorder conventions: z = (x, y) = x + y*omega)
# ---------------------------------------------------------------------------

def nrm(D: int, z) -> int:
    return QO.norm(D, z[0], z[1])


def exact_div(D: int, z, a) -> tuple[int, int]:
    """z / a in O_K (asserted exact)."""
    num = QO.multiply(D, z, QO.conjugate(D, *a))
    N = nrm(D, a)
    if num[0] % N or num[1] % N:
        raise ArithmeticError("not divisible")
    return num[0] // N, num[1] // N


@dataclass
class Ideal:
    """The principal ideal gamma*O as a Z-lattice in HNF: {(A, 0), (B, C)},
    0 <= B < A; residues are canonical pairs (x mod A after clearing y mod C)."""
    D: int
    gamma: tuple[int, int]
    A: int
    B: int
    C: int

    @classmethod
    def of(cls, D: int, gamma) -> "Ideal":
        g1 = tuple(gamma)
        g2 = QO.multiply(D, gamma, (0, 1))
        # column HNF on the y-coordinates
        (x1, y1), (x2, y2) = g1, g2
        g, s, t = _egcd(y1, y2)
        # v = s*g1 + t*g2 has y = g; u = (y2/g)*g1 - (y1/g)*g2 has y = 0
        vx = s * x1 + t * x2
        ux = (y2 // g) * x1 - (y1 // g) * x2
        A, C = abs(ux), abs(g)
        if g < 0:
            vx, g = -vx, -g
        B = vx % A
        assert A * C == nrm(D, gamma)
        return cls(D, g1, A, B, C)

    def residue(self, z) -> tuple[int, int]:
        x, y = z
        q = y // self.C
        x, y = x - q * self.B, y - q * self.C
        return x % self.A, y

    def contains(self, z) -> bool:
        return self.residue(z) == (0, 0)


def _egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0) if a >= 0 else (-a, -1, 0)
    g, s, t = _egcd(b, a % b)
    return g, t, s - (a // b) * t


def minimal_reps(D: int, I: Ideal, *, exclude: Ideal | None = None) -> dict:
    """Minimal-norm representative of every class of O/I (classes inside
    `exclude` dropped), ties broken by (|y|, y, |x|, -x)."""
    need = I.A * I.C
    tau, nw = QO.omega_trace_norm(D)
    reps: dict = {}
    R = 2
    while True:
        reps.clear()
        ymax = int(math.isqrt(4 * R * R // max(4 * nw - tau * tau, 1))) + 2
        for y in range(-ymax, ymax + 1):
            for x in range(-2 * R - abs(y), 2 * R + abs(y) + 1):
                z = (x, y)
                Nz = nrm(D, z)
                if Nz > R * R:
                    continue
                r = I.residue(z)
                key = (Nz, abs(y), y, abs(x), -x)
                if r not in reps or key < reps[r][0]:
                    reps[r] = (key, z)
        full = len(reps) == need
        if full:
            # a representative found inside radius R is minimal only if every
            # class has one of norm <= (R/2)^2... recheck with a doubled radius
            worst = max(v[0][0] for v in reps.values())
            if worst * 4 <= R * R:
                break
        R *= 2
    out = {r: v[1] for r, v in reps.items()}
    if exclude is not None:
        out = {r: z for r, z in out.items() if not exclude.contains(z)}
    return out


# ---------------------------------------------------------------------------
# reduction of k to a short element of O_K
# ---------------------------------------------------------------------------

@dataclass
class NormReducer:
    """Relation lattice {(x, y): x + y*lam = 0 mod n}, Lagrange-reduced under
    the norm form, and Babai rounding against it."""
    D: int
    n: int
    lam: int
    u: tuple[int, int] = (0, 0)
    v: tuple[int, int] = (0, 0)

    def __post_init__(self):
        D = self.D
        tau, nw = QO.omega_trace_norm(D)

        def Q(a):
            return a[0] * a[0] + tau * a[0] * a[1] + nw * a[1] * a[1]

        def B2(a, b):
            return 2 * a[0] * b[0] + tau * (a[0] * b[1] + a[1] * b[0]) + 2 * nw * a[1] * b[1]

        u, v = (self.n, 0), ((-self.lam) % self.n, 1)
        if Q(u) > Q(v):
            u, v = v, u
        while True:
            mu = round(Fraction(B2(u, v), 2 * Q(u)))
            v = (v[0] - mu * u[0], v[1] - mu * u[1])
            if Q(v) >= Q(u):
                break
            u, v = v, u
        self.u, self.v, self._Q = u, v, Q

    def reduce(self, k: int) -> tuple[int, int]:
        (a, b), (c, d) = self.u, self.v
        det = a * d - b * c
        t = (k % self.n, 0)
        f1 = round(Fraction(t[0] * d - t[1] * c, det))
        f2 = round(Fraction(-t[0] * b + t[1] * a, det))
        z = (t[0] - f1 * a - f2 * c, t[1] - f1 * b - f2 * d)
        assert (z[0] + z[1] * self.lam - k) % self.n == 0
        return z

    def norm_bound(self) -> int:
        """N(z) <= ((|u| + |v|)/2)^2 for every rounded z (a theorem about the basis)."""
        return math.ceil(((math.sqrt(self._Q(self.u)) + math.sqrt(self._Q(self.v))) / 2) ** 2)


# ---------------------------------------------------------------------------
# digit rules and expansions
# ---------------------------------------------------------------------------

@dataclass
class DigitRule:
    name: str
    D: int
    alpha: tuple[int, int]
    w: int
    I1: Ideal                       # (alpha)
    Iw: Ideal                       # (alpha^w)
    table: dict                     # residue mod alpha^w -> digit
    integer_digits: bool
    note: str = ""

    def digit(self, z) -> tuple[int, int]:
        if self.w > 1 and self.I1.contains(z):
            return (0, 0)
        return self.table[self.Iw.residue(z)]

    @property
    def max_abs(self) -> float:
        return max(math.sqrt(nrm(self.D, d)) for d in self.table.values())

    def nonzero_digits_up_to_sign(self) -> list[tuple[int, int]]:
        seen, out = set(), []
        for d in self.table.values():
            if d == (0, 0):
                continue
            k = max(d, (-d[0], -d[1]))
            if k not in seen:
                seen.add(k)
                out.append(k)
        return sorted(out)


def int_rule(D: int, alpha) -> DigitRule:
    I = Ideal.of(D, alpha)
    if I.C != 1:
        raise ValueError("alpha is not primitive: O/(alpha) is not cyclic")
    N = I.A
    table = {}
    for r in range(N):
        d = r if r <= N // 2 else r - N
        table[I.residue((d, 0))] = (d, 0)
    assert len(table) == N
    return DigitRule("int", D, tuple(alpha), 1, I, I, table, True,
                     f"balanced integers mod {N}")


def voronoi_rule(D: int, alpha) -> DigitRule:
    I = Ideal.of(D, alpha)
    reps = minimal_reps(D, I)
    return DigitRule("voronoi", D, tuple(alpha), 1, I, I, reps, all(z[1] == 0 for z in reps.values()),
                     "minimal-norm representatives of O/(alpha)")


def naf_rule(D: int, alpha, w: int) -> DigitRule:
    I1 = Ideal.of(D, alpha)
    Iw = Ideal.of(D, QO.power(D, tuple(alpha), w))
    reps = minimal_reps(D, Iw, exclude=I1)
    return DigitRule(f"naf{w}", D, tuple(alpha), w, I1, Iw, reps, all(z[1] == 0 for z in reps.values()),
                     f"width-{w} alpha-NAF: minimal-norm representatives of (O/alpha^{w})* ")


def expand(rule: DigitRule, z, *, max_len: int = 100000) -> list[tuple[int, int]]:
    """z = sum d_i alpha^i, least significant first."""
    D, a = rule.D, rule.alpha
    out = []
    while z != (0, 0):
        d = rule.digit(z)
        out.append(d)
        z = exact_div(D, (z[0] - d[0], z[1] - d[1]), a)
        if len(out) > max_len:
            raise RuntimeError("expansion did not terminate")
    return out


def termination_certificate(rule: DigitRule) -> dict:
    """Iterate T(z) = (z - d(z))/alpha on every z with |z| <= R/(|alpha| - 1)."""
    D = rule.D
    absa = math.sqrt(nrm(D, rule.alpha))
    R = rule.max_abs
    if absa <= 1:
        return {"terminates": False, "reason": "|alpha| <= 1"}
    rad = R / (absa - 1.0)
    bound = int(rad * rad) + 1
    tau, nw = QO.omega_trace_norm(D)
    ymax = int(math.isqrt(4 * bound // max(4 * nw - tau * tau, 1))) + 1
    elems = [(x, y) for y in range(-ymax, ymax + 1) for x in range(-bound - abs(y), bound + abs(y) + 1)
             if nrm(D, (x, y)) <= rad * rad + 1e-9]
    good = {(0, 0)}
    cycles = []
    for z0 in elems:
        path, z = [], z0
        seen = set()
        while z not in good:
            if z in seen:
                cycles.append(z)
                break
            seen.add(z)
            path.append(z)
            d = rule.digit(z)
            z = exact_div(D, (z[0] - d[0], z[1] - d[1]), rule.alpha)
        else:
            good.update(path)
    return {"terminates": not cycles, "disk_radius": round(rad, 4), "elements_checked": len(elems),
            "max_digit_abs": round(R, 4), "abs_alpha": round(absa, 4),
            "cycle_example": list(cycles[0]) if cycles else None}


# ---------------------------------------------------------------------------
# curves and costs
# ---------------------------------------------------------------------------

def arith_for(c: dict) -> CV.Arith:
    p = int(c["p"], 16)
    note = c["arithmetic"]
    inv = (bin(p - 2).count("1"), (p - 2).bit_length())
    if note.startswith("a = -3") or "isomorphic to an a = -3" in note:
        dbl = (3, 5)
    elif note.startswith("small a"):
        dbl = (1, 8)
    elif note.startswith("a = 0"):
        dbl = (2, 5)
    else:
        dbl = (2, 8)
    return CV.Arith(dbl, inv=inv, note=note)


def chain_proj_ops(order) -> tuple[int, int]:
    """alpha on a Jacobian input: every step a general step, then the tail."""
    M = S = 0
    for ell in order:
        m, s = CV.step_ops(ell, "optimised", False)
        M, S = M + m, S + s
    m, s = CV.CS.tail_ops("optimised")
    return M + m, S + s


@dataclass
class Ops:
    M: float = 0.0
    S: float = 0.0
    I: float = 0.0

    def add(self, ms, k=1.0):
        self.M += k * ms[0]
        self.S += k * ms[1]
        return self

    def m_eq(self, inv_ms) -> float:
        return self.M + self.S + self.I * (inv_ms[0] + inv_ms[1])

    def m_cm(self) -> float:
        return self.M + CM.S_PER_M * self.S + CM.I_PER_M * self.I


def table_ops(rule: DigitRule, ar: CV.Arith, omega_ops: tuple[int, int] | None, affine: bool) -> tuple[Ops, int]:
    """Precomputation of every digit multiple d*P (up to sign).

    Multiples of P up to max|x| (one DBL, then one ADD each), multiples of
    omega(P) up to max|y| likewise, one ADD per digit with x and y both
    non-zero; omega(P) itself at its chain cost (affine input).  An affine
    table adds the batched conversion (curvesweep's count, one Fermat
    inversion)."""
    digs = rule.nonzero_digits_up_to_sign()
    o = Ops()
    mx = max((abs(d[0]) for d in digs), default=0)
    my = max((abs(d[1]) for d in digs), default=0)
    if mx >= 2:
        o.add(ar.dbl).add(ar.add, mx - 2)
    if my >= 1:
        if omega_ops is None:
            raise ValueError("digits need omega(P)")
        o.add(omega_ops)
        if my >= 2:
            o.add(ar.dbl).add(ar.add, my - 2)
    mixed = sum(1 for d in digs if d[0] and d[1])
    o.add(ar.add, mixed)
    if affine:
        cnt = len(digs)
        bm, bs = (cnt + 2 * (cnt - 1) + 3 * cnt, cnt)        # curvesweep._batch without the inversion
        o.add((bm, bs))
        o.I += 1
    return o, len(digs)


def omega_cost(rule_alpha, rows: list[dict]) -> tuple[int, int] | None:
    """omega(P) from alpha(P) when alpha = a +- omega (one chain + a*P + 1 ADD,
    priced as the chain alone plus small change), else omega's own chain."""
    a, b = rule_alpha
    row = next((r for r in rows if tuple(r["element"]) == tuple(rule_alpha)), None)
    if row is not None and abs(b) == 1:
        m, s = row["ops"]["optimised"]["M"], row["ops"]["optimised"]["S"]
        extra = (0, 0) if a == 0 else (11 * (1 + abs(a).bit_length()), 5 * (1 + abs(a).bit_length()))
        return m + extra[0], s + extra[1]
    om = next((r for r in rows if tuple(r["element"]) == (0, 1)), None)
    if om is not None:
        return om["ops"]["optimised"]["M"], om["ops"]["optimised"]["S"]
    return None


def configs_for(c: dict) -> list[tuple[dict, DigitRule]]:
    out = []
    D = c["D"]
    for row in c["rows"]:
        alpha = tuple(row["element"])
        out.append((row, int_rule(D, alpha)))
        out.append((row, voronoi_rule(D, alpha)))
        N = row["norm"]
        w = 2
        while (N ** w - N ** (w - 1)) // 2 <= NAF_TABLE_CAP:
            out.append((row, naf_rule(D, alpha, w)))
            w += 1
    return out


def measure(c: dict, row: dict, rule: DigitRule, ar: CV.Arith, red: NormReducer, ks: list[int],
            *, reduce_first: bool = True) -> dict:
    D, n = c["D"], int(c["n"], 16)
    lam_w = int(row["lam_omega"], 16)
    lam_a = (rule.alpha[0] + rule.alpha[1] * lam_w) % n
    proj = chain_proj_ops(row["order"])
    om = omega_cost(rule.alpha, c["rows"])
    tabs = {}
    for affine in (True, False):
        try:
            tabs[affine] = table_ops(rule, ar, om, affine)
        except ValueError:
            return {"skipped": "digits need omega(P) and no omega chain is available"}
    lens, nnzs, costs_eq, costs_cm, ratios, tables_eq = [], [], [], [], [], []
    verified = 0
    for k in ks:
        z = red.reduce(k) if reduce_first else (k, 0)
        ratios.append(nrm(D, z) / n)
        ds = expand(rule, z)
        acc = 0
        for d in reversed(ds):
            acc = (acc * lam_a + d[0] + d[1] * lam_w) % n
        if acc != k % n:
            raise AssertionError("expansion does not reconstruct k")
        verified += 1
        L = len(ds)
        nnz = sum(1 for d in ds if d != (0, 0))
        best = None
        for affine, (tab, _) in tabs.items():
            o = Ops(tab.M, tab.S, tab.I)
            o.add(proj, L - 1)
            o.add(ar.madd if affine else ar.add, nnz - 1)
            e = o.m_eq(ar.inv)
            if best is None or e < best[0]:
                best = (e, o.m_cm(), affine, tab.m_eq(ar.inv))
        lens.append(L)
        nnzs.append(nnz)
        costs_eq.append(best[0])
        costs_cm.append(best[1])
        tables_eq.append(best[3])
    msd = lambda xs: [round(statistics.fmean(xs), 3), round(statistics.pstdev(xs), 3)]
    bits = n.bit_length()
    return {
        "alpha": list(rule.alpha), "norm": row["norm"], "order": row["order"], "rule": rule.name,
        "reduced": reduce_first, "w": rule.w, "digit_table_points": tabs[True][1],
        "integer_digits": rule.integer_digits, "C_alpha_affine_Meq": row["ops"]["optimised"]["M_eq"],
        "C_alpha_proj": {"M": proj[0], "S": proj[1], "M_eq": proj[0] + proj[1]},
        "omega_P_ops": list(om) if om else None,
        "samples": len(ks), "verified_mod_n": verified,
        "length": msd(lens), "nonzero": msd(nnzs),
        "nonzero_density": round(statistics.fmean(nnzs) / statistics.fmean(lens), 4),
        "N_z_over_n": msd(ratios), "table_M_eq": round(statistics.fmean(tables_eq), 1),
        "total_M_eq": msd(costs_eq), "total_M_cm": msd(costs_cm),
        "per_bit_M_eq": round(statistics.fmean(costs_eq) / bits, 3),
        "loop_per_bit_M_eq": round((statistics.fmean(costs_eq) - statistics.fmean(tables_eq)) / bits, 3),
        "alpha_share_of_loop": round((statistics.fmean(lens) - 1) * (proj[0] + proj[1])
                                     / (statistics.fmean(costs_eq) - statistics.fmean(tables_eq)), 4),
        "naive_per_bit_estimate": round((proj[0] + proj[1]) / math.log2(row["norm"]), 3),
    }


def comparators(c: dict, ar: CV.Arith, samples: int = 200) -> dict:
    """wNAF and 2-GLV of the same curve: costmodel.py (analytic) and
    curvesweep.scalar_model (recoded, M_eq) with the curve's cheapest chain."""
    n = int(c["n"], 16)
    row = min(c["rows"], key=lambda r: r["ops"]["optimised"]["M_eq"])
    lam = MS.chain_eigenvalue(row, n, c["D"])
    model = MS._model_key_for(c["arithmetic"])
    red = LA.reduce([1, lam], n)
    bb = red.babai_bound.bit_length()
    ident = CM.Generator("1", 1, 0.0, "identity")
    ops = row["ops"]["optimised"]
    g = CM.Generator("alpha", lam, ops["M"] + CM.S_PER_M * ops["S"], "isogeny")
    base_cm = CM.multiscalar_cost(n.bit_length(), [ident], model)
    glv_cm = CM.multiscalar_cost(bb, [ident, g], model)
    sm = CV.scalar_model(ar, n, lam, {"M": ops["M"], "S": ops["S"]}, samples=samples)
    return {"chain": list(row["element"]), "chain_order": row["order"], "chain_M_eq": ops["M_eq"],
            "costmodel": {"wnaf_M": round(base_cm.total_M, 1), "wnaf_w": base_cm.window,
                          "glv2_M": round(glv_cm.total_M, 1), "glv2_w": glv_cm.window, "coeff_bits": bb,
                          "units": "M, S = 0.8 M, I = 100 M, costmodel.py"},
            "curvesweep": {"wnaf_M_eq": sm["baseline"][sm["best_baseline"]], "wnaf_config": sm["best_baseline"],
                           "glv2_M_eq": sm["glv"][sm["best_glv"]], "glv2_config": sm["best_glv"],
                           "units": "M_eq = M + S, Fermat inversion, curvesweep.py recoding"},
            "doubling_M_eq": ar.dbl[0] + ar.dbl[1]}


# ---------------------------------------------------------------------------
# points: CryptoPro-B with the real 4 + omega chain
# ---------------------------------------------------------------------------

def _aff_add_ab(p, a, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return x3, (lam * (x1 - x3) - y1) % p


def _aff_mul_ab(p, a, k, P):
    if k < 0:
        k, P = -k, (P[0], (-P[1]) % p)
    R = None
    while k:
        if k & 1:
            R = _aff_add_ab(p, a, R, P)
        P = _aff_add_ab(p, a, P, P)
        k >>= 1
    return R


def chain_map(ch: dict, p: int):
    steps = [([int(x, 16) for x in s["N"]], [int(x, 16) for x in s["psi"]], [int(x, 16) for x in s["M"]])
             for s in ch["steps"]]
    u = int(ch["isomorphism_u"], 16)
    u2, u3 = u * u % p, pow(u, 3, p)

    def ev(f, x):
        r = 0
        for c in reversed(f):
            r = (r * x + c) % p
        return r

    def phi(P):
        if P is None:
            return None
        x, y = P
        for N, psi, M in steps:
            d = pow(ev(psi, x), -1, p)
            x, y = ev(N, x) * d * d % p, y * ev(M, x) % p * pow(d, 3, p) % p
        return u2 * x % p, u3 * y % p
    return phi


def verify_on_points(chain_id: str = "4+1w/7.5.5", scalars: int = 4, seed: int = 11) -> dict:
    data = json.load(open(CHAINS_JSON))
    p, a, n = int(data["p"], 16), int(data["a"], 16), int(data["n"], 16)
    lam_w = int(data["omega_root"], 16)
    ch = next(x for x in data["chains"] if x["id"] == chain_id)
    phi = chain_map(ch, p)
    tv = ch["test_vectors"][0]
    P = (int(tv["P"][0], 16), int(tv["P"][1], 16))
    assert phi(P) == (int(tv["phiP"][0], 16), int(tv["phiP"][1], 16))
    lam_chain = int(ch["eigenvalue"], 16)
    ea, eb = ch["element"]
    if lam_chain == (ea + eb * lam_w) % n:
        alpha = (ea, eb)
    elif lam_chain == (-(ea + eb * lam_w)) % n:
        alpha = (-ea, -eb)
    else:
        raise AssertionError("chain eigenvalue is neither alpha nor -alpha at the pinned omega root")
    D = data["D_K"]
    rng = random.Random(seed)
    red = NormReducer(D, n, lam_w)
    # omega(P) = alpha(P) - a*P (b = 1), checked against [lam_w] P
    oP = _aff_add_ab(p, a, phi(P), _aff_mul_ab(p, a, -alpha[0], P)) if alpha[1] == 1 else None
    if alpha[1] == -1:
        oP = _aff_add_ab(p, a, _aff_mul_ab(p, a, alpha[0], P), (phi(P)[0], (-phi(P)[1]) % p))
    assert oP == _aff_mul_ab(p, a, lam_w, P)
    out = []
    for rule in (int_rule(D, alpha), voronoi_rule(D, alpha)):
        for _ in range(scalars):
            k = rng.randrange(1, n)
            ds = expand(rule, red.reduce(k))
            Q = None
            for d in reversed(ds):
                Q = phi(Q)
                dP = _aff_add_ab(p, a, _aff_mul_ab(p, a, d[0], P), _aff_mul_ab(p, a, d[1], oP))
                Q = _aff_add_ab(p, a, Q, dP)
            ok = Q == _aff_mul_ab(p, a, k, P)
            if not ok:
                raise AssertionError("alpha-adic Horner on points disagrees with k*P")
            out.append({"rule": rule.name, "k": hex(k), "digits": len(ds), "ok": ok})
    return {"chain": chain_id, "alpha_realised": list(alpha), "checks": out, "all_ok": all(x["ok"] for x in out)}


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def run(samples: int = 1000, seed: int = 20261008, progress: bool = False) -> dict:
    inputs = MS.load_inputs()
    res = {"format": FORMAT, "generator": GENERATOR, "samples": samples, "seed": seed, "curves": []}
    for c in inputs["curves"]:
        n = int(c["n"], 16)
        ar = arith_for(c)
        lam_w = int(c["rows"][0]["lam_omega"], 16)
        red = NormReducer(c["D"], n, lam_w)
        rng = random.Random(seed)
        ks = [rng.randrange(1, n) for _ in range(samples)]
        cr = {"curve": c["name"], "D": c["D"], "n_bits": n.bit_length(), "arithmetic": ar.note,
              "doubling_ops": list(ar.dbl), "inversion_ops": list(ar.inv),
              "reducer": {"u": list(red.u), "v": list(red.v), "norm_bound_over_n": round(red.norm_bound() / n, 4)},
              "comparators": comparators(c, ar), "rows": [], "termination": {}}
        for row, rule in configs_for(c):
            key = f"{row['element'][0]}+{row['element'][1]}w/{rule.name}"
            cr["termination"][key] = termination_certificate(rule)
            if not cr["termination"][key]["terminates"]:
                cr["rows"].append({"alpha": row["element"], "rule": rule.name, "skipped": "does not terminate"})
                continue
            t0 = time.time()
            m = measure(c, row, rule, ar, red, ks)
            cr["rows"].append(m)
            if progress:
                print(c["name"], key, m.get("total_M_eq"), m.get("length"), round(time.time() - t0, 1), flush=True)
        # ablation: the integer k expanded without reduction (cheapest element, int digits)
        row = min(c["rows"], key=lambda r: r["ops"]["optimised"]["M_eq"])
        m = measure(c, row, int_rule(c["D"], tuple(row["element"])), ar, red, ks[:200], reduce_first=False)
        m["rule"] = "int/unreduced"
        cr["rows"].append(m)
        res["curves"].append(cr)
    res["points"] = verify_on_points()
    return res


def best_rows(cr: dict, k: int = 5) -> list[dict]:
    rows = [r for r in cr["rows"] if "total_M_eq" in r and r.get("reduced", True)]
    return sorted(rows, key=lambda r: r["total_M_eq"][0])[:k]


def markdown(res: dict) -> str:
    L = ["# alpha-adic expansions on prime-field curves with chain endomorphisms", "",
         f"{res['samples']} random scalars per configuration (seed {res['seed']}); every expansion verified "
         "to reconstruct k mod n.  Operation counts (M_eq = M + S, the curve's own Fermat inversion), not timings.", ""]
    for cr in res["curves"]:
        cp = cr["comparators"]
        L += [f"## {cr['curve']} (D = {cr['D']}, n: {cr['n_bits']} bits; {cr['arithmetic']})", "",
              f"Comparators: width-w NAF {cp['curvesweep']['wnaf_M_eq']} M_eq ({cp['curvesweep']['wnaf_config']}), "
              f"2-GLV with {cp['chain'][0]} + {cp['chain'][1]}w {cp['curvesweep']['glv2_M_eq']} M_eq "
              f"({cp['curvesweep']['glv2_config']}) [curvesweep recoding]; costmodel.py: wNAF "
              f"{cp['costmodel']['wnaf_M']} M, 2-GLV {cp['costmodel']['glv2_M']} M (S = 0.8 M, I = 100 M).  "
              f"Doubling {cp['doubling_M_eq']} M_eq.", "",
              "| alpha | N(alpha) | digits | table points | C_alpha (affine in / Jacobian in) | length | non-zero density | "
              "table M_eq | total M_eq (mean +- sd) | per bit | loop per bit | C_proj/log2 N | vs wNAF | vs 2-GLV |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in cr["rows"]:
            if "total_M_eq" not in r:
                L.append(f"| {r['alpha'][0]} + {r['alpha'][1]}w | | {r['rule']} | | | | | | {r['skipped']} | | | | | |")
                continue
            t = r["total_M_eq"]
            L.append(f"| {r['alpha'][0]} + {r['alpha'][1]}w | {r['norm']} | {r['rule']} | {r['digit_table_points']} | "
                     f"{r['C_alpha_affine_Meq']} / {r['C_alpha_proj']['M_eq']} | {r['length'][0]:.1f} +- {r['length'][1]:.1f} | "
                     f"{r['nonzero_density']:.3f} | {r['table_M_eq']:.0f} | {t[0]:.0f} +- {t[1]:.0f} | {r['per_bit_M_eq']:.2f} | "
                     f"{r['loop_per_bit_M_eq']:.2f} | "
                     f"{r['naive_per_bit_estimate']:.2f} | {t[0] / cp['curvesweep']['wnaf_M_eq']:.2f}x | "
                     f"{t[0] / cp['curvesweep']['glv2_M_eq']:.2f}x |")
        nt = [k for k, v in cr["termination"].items() if not v["terminates"]]
        L += ["", f"Termination: {len(cr['termination']) - len(nt)} of {len(cr['termination'])} digit rules proved "
              "terminating by exhausting the absorbing disk" + (f"; non-terminating: {', '.join(nt)}" if nt else "") + ".", ""]
    pts = res["points"]
    L += ["## On points", "", f"CryptoPro-B, chain {pts['chain']} (realised as {pts['alpha_realised']}): "
          f"{sum(1 for x in pts['checks'] if x['ok'])} of {len(pts['checks'])} Horner evaluations with the real "
          "chain equal k*P.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", default=os.path.join("research", "endosweep_msm_20261008"))
    ap.add_argument("--samples", type=int, default=1000)
    ap.add_argument("--markdown-only", action="store_true", help="rewrite alphaadic.md from alphaadic.json")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    if a.markdown_only:
        res = json.load(open(os.path.join(a.out_dir, "alphaadic.json")))
        with open(os.path.join(a.out_dir, "alphaadic.md"), "w") as f:
            f.write(markdown(res))
        return 0
    t0 = time.time()
    res = run(samples=a.samples, progress=True)
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(a.out_dir, "alphaadic.json"), "w") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(a.out_dir, "alphaadic.md"), "w") as f:
        f.write(markdown(res))
    print(f"wrote alphaadic.json ({res['elapsed_s']} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
