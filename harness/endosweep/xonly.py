"""x-only two-dimensional GLV with the conjugate chain as the difference point.

A two-dimensional differential addition chain on the x-line computes
``x(k1 P + k2 Q)`` from ``x(P)``, ``x(Q)`` and ``x(P - Q)`` (Bernstein's
binary chain also uses ``x(P + Q)``, one differential addition away).  With
``Q = beta(P)`` for an endomorphism ``beta``, the obstacle is the difference
``x(P - beta P) = x((1 - beta) P)``: the x-line knows ``x(P)`` and
``x(beta P)`` but not their difference.  If ``Tr beta = 1`` then
``1 - beta = conj(beta)``, so

    x(P - beta P) = x(conj(beta) P),

and ``conj(beta)`` is the dual isogeny of ``beta``: on a curve with class
number above one it is the *conjugate chain*, the same prime-degree steps
through the conjugate prime ideals, evaluated at the same cost as ``beta``.
The trace-one elements of the maximal order of an odd discriminant ``D_K``
are ``(1 + m sqrt(D_K))/2`` for odd ``m`` (and their negatives give trace
-1), of norm ``(1 + m^2 |D_K|)/4``; the smallest are ``omega`` and
``conj(omega) = 1 - omega``.  An even discriminant has no element of odd
trace at all, and neither does an order of even conductor.

This module

1. implements x-only arithmetic on ``y^2 = x^3 + a x + b`` in XZ
   coordinates with every field operation counted: doubling
   ``dbl-2002-bj-3`` (2M + 5S + 1*a + 1*b2 + 1*b4), differential addition
   ``dadd-2002-it-3`` (7M + 2S + 1*a + 1*b) and, for an affine difference,
   ``mdadd-2002-it-3`` (6M + 2S + 1*a + 1*b), all transcribed from the EFD
   page "XZ coordinates for short Weierstrass curves"; a multiplication by a
   curve or map constant is counted apart from a general multiplication and
   is charged as one M unless the constant is small (|c| < 2^16);
2. the uniform one-dimensional Montgomery ladder (one xDBL and one mdadd per
   bit of ``n``, a fixed number of iterations);
3. Bernstein's uniform two-dimensional binary chain ("Differential addition
   chains", 2006, section 4), with the recursion ``C_D(A, B)`` transcribed
   from the paper, run for a fixed number of levels (the Babai bound of the
   GLV lattice) so its operation sequence is the same for every scalar;
4. x-only evaluation of a chain endomorphism built by ``explicit.py``: each
   prime step is ``x -> N(x) / psi(x)^2`` (Kohel form, from
   ``chainsweep.rational_map_polys``), the first on the affine input by
   monic Horner, later ones homogeneously, then ``x -> u^2 x``;
5. the end-to-end check: x(omega P) = x([lambda] P), x(conj(omega) P) =
   x([1 - lambda] P), x(omega P - P) = x(conj(omega) P) with omega evaluated
   on full points, and x(k P) from the 2-D chain and from the ladder against
   a Jacobian double-and-add for random k;
6. a survey of the trace-one elements ``(1 + m sqrt D)/2`` for odd ``m`` up
   to a bound, each priced in closed form with its own GLV lattice
   (modelled), and the construction and measurement of the best one when it
   is not ``omega`` (on Tom-256, where ``omega`` needs a 1039-isogeny).

Every operation count reported by ``run`` is a count of operations executed
by this code (measured), except the map cost of a chain with a step above
``build_max_ell``, which is charged from ``costmodel.xonly_chain_cost`` and
marked modelled; ``costmodel.xonly_*`` gives every number in closed form and
a test pins that the closed form and the executed counts agree.  Nothing
here is a timing.

    python -m harness.endosweep.xonly --out-dir research/endosweep_xonly_20261008
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import statistics
import time
from dataclasses import dataclass, field

from sympy import factorint

from . import chainsweep as CS
from . import costmodel as CM
from . import explicit as EX
from . import lattice as LA
from . import quadorder as QO
from .targets import Target, deployed_targets, verify
from .toyverify import Curve

FORMAT = "endosweep-xonly/1"
GENERATOR = "harness/endosweep/xonly.py"
SMALL_CONSTANT = 1 << 16


# ---------------------------------------------------------------------------
# counted field
# ---------------------------------------------------------------------------

@dataclass
class XCounter:
    """F_p with counted multiplications (M), squarings (S), multiplications
    by a fixed constant (``Mc_full`` or ``Mc_small``) and inversions (I, each
    executed as a Fermat power through ``sqr``/``mul``, so its cost is
    already inside M and S).  Additions and multiplications by 2, 4, 8 are
    not counted, as in the EFD's operation counts."""
    p: int
    M: int = 0
    S: int = 0
    Mc_full: int = 0
    Mc_small: int = 0
    I: int = 0

    def mul(self, x, y):
        self.M += 1
        return x * y % self.p

    def sqr(self, x):
        self.S += 1
        return x * x % self.p

    def cmul(self, c, x):
        c %= self.p
        if min(c, self.p - c) < SMALL_CONSTANT:
            self.Mc_small += 1
        else:
            self.Mc_full += 1
        return c * x % self.p

    def inv(self, x):
        """x^(p-2) by left-to-right square-and-multiply, counted."""
        self.I += 1
        e = self.p - 2
        r = x % self.p
        for bit in bin(e)[3:]:
            r = self.sqr(r)
            if bit == "1":
                r = self.mul(r, x)
        return r

    def snapshot(self) -> dict:
        return {"M": self.M, "S": self.S, "Mc_full": self.Mc_full, "Mc_small": self.Mc_small,
                "I": self.I, "M_eq": self.M + self.S + self.Mc_full}

    def reset(self):
        self.M = self.S = self.Mc_full = self.Mc_small = self.I = 0


def ops_diff(after: dict, before: dict) -> dict:
    return {k: after[k] - before[k] for k in after}


# ---------------------------------------------------------------------------
# x-only arithmetic in XZ coordinates (EFD g1p/auto-shortw-xz)
# ---------------------------------------------------------------------------

@dataclass
class XCurve:
    """y^2 = x^3 + a x + b; points on the x-line are (X : Z), identity (1 : 0)."""
    p: int
    a: int
    b: int
    F: XCounter = field(default=None)

    def __post_init__(self):
        self.a %= self.p
        self.b %= self.p
        if self.F is None:
            self.F = XCounter(self.p)
        self.b2 = 2 * self.b % self.p
        self.b4 = 4 * self.b % self.p

    def xdbl(self, P):
        """dbl-2002-bj-3: 2M + 5S + 1*b2 + 1*a + 1*b4."""
        F, p = self.F, self.p
        X1, Z1 = P
        XX = F.sqr(X1)
        ZZ = F.sqr(Z1)
        A = 2 * (F.sqr((X1 + Z1) % p) - XX - ZZ) % p
        aZZ = F.cmul(self.a, ZZ)
        X3 = (F.sqr((XX - aZZ) % p) - F.cmul(self.b2, F.mul(A, ZZ))) % p
        Z3 = (F.mul(A, (XX + aZZ) % p) + F.cmul(self.b4, F.sqr(ZZ))) % p
        return (X3, Z3)

    def xadd(self, P2, P3, P1, affine_diff: bool = False):
        """x(P2 + P3) from x(P2), x(P3) and the difference x(P1) = x(P2 - P3).

        dadd-2002-it-3 (7M + 2S + 1*a + 1*b); with ``affine_diff`` the
        difference is (X1 : 1) and the multiplication by Z1 is skipped, which
        is mdadd-2002-it-3 (6M + 2S + 1*a + 1*b).  The choice is structural
        (a flag), never a test on the value, so the operation count does not
        depend on the data.
        """
        F, p = self.F, self.p
        X2, Z2 = P2
        X3, Z3 = P3
        X1, Z1 = P1
        T1 = F.mul(X2, X3)
        T2 = F.mul(Z2, Z3)
        T3 = F.mul(X2, Z3)
        T4 = F.mul(Z2, X3)
        T5 = F.cmul(self.a, T2)
        T7 = F.sqr((T1 - T5) % p)
        T9 = 4 * F.cmul(self.b, T2) % p
        T11 = F.mul(T9, (T3 + T4) % p)
        T12 = (T7 - T11) % p
        X5 = T12 if affine_diff else F.mul(Z1, T12)
        T14 = F.sqr((T3 - T4) % p)
        Z5 = F.mul(X1, T14)
        return (X5, Z5)

    def normalise(self, P) -> int | None:
        X, Z = P
        if Z % self.p == 0:
            return None
        return X * pow(Z, -1, self.p) % self.p


def ladder(C: XCurve, k: int, x: int, bits: int):
    """Montgomery ladder for x(kP), ``bits`` fixed iterations, one xDBL and one
    mdadd (difference x(P), affine) per iteration; R1 - R0 = P throughout."""
    if not 0 <= k < (1 << bits):
        raise ValueError("scalar out of range for the fixed ladder length")
    P = (x % C.p, 1)
    R0, R1 = (1, 0), P
    for i in range(bits - 1, -1, -1):
        if (k >> i) & 1:
            R0, R1 = C.xadd(R0, R1, P, affine_diff=True), C.xdbl(R1)
        else:
            R0, R1 = C.xdbl(R0), C.xadd(R0, R1, P, affine_diff=True)
    return R0


# ---------------------------------------------------------------------------
# Bernstein's uniform two-dimensional binary chain
# ---------------------------------------------------------------------------

DIFFS = ((1, 0), (0, 1), (1, 1), (1, -1))


def bernstein_levels(A: int, B: int, L: int, D_final: int | None = None) -> list[tuple[int, int, int]]:
    """The (A, B, D) of every line of C_D(A, B), from the top (0, 0) down.

    Bernstein 2006, section 4: C_D(A, B) is C_d(a, b) followed by three
    pairs, with (a, b) = (A // 2, B // 2) and d = 0, 1, D, 1 - D according
    as (a + A, b + B) mod 2 is (0, 1), (1, 0), (0, 0), (1, 1); the final
    D = A mod 2 puts (A, B) itself in the last line.  ``L`` lines below the
    top: A, B < 2^L is required, and leading zero bits are allowed, so the
    number of lines is fixed and independent of the scalar.
    """
    if not (0 <= A < (1 << L) and 0 <= B < (1 << L)):
        raise ValueError("multiscalar out of range for the fixed chain length")
    D = A & 1 if D_final is None else D_final
    out = [(A, B, D)]
    for _ in range(L):
        a, b = A >> 1, B >> 1
        par = ((a + A) & 1, (b + B) & 1)
        d = {(0, 1): 0, (1, 0): 1, (0, 0): D, (1, 1): 1 - D}[par]
        A, B, D = a, b, d
        out.append((A, B, D))
    assert (A, B) == (0, 0)
    return out[::-1]


def line_pairs(A: int, B: int, D: int) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    """The three pairs of the line for (A, B, D): odd-odd, even-even, mixed."""
    return ((A + ((A + 1) & 1), B + ((B + 1) & 1)),
            (A + (A & 1), B + (B & 1)),
            (A + ((A + D) & 1), B + ((B + D + 1) & 1)))


def top_line(d: int) -> list[tuple[int, int]]:
    """The three corners of (0, 0) present for the top line's d: the corner
    (a + (a + d + 1 mod 2), b + (b + d mod 2)) is the one omitted."""
    missing = ((d + 1) & 1, d & 1)
    return [c for c in ((0, 0), (1, 0), (0, 1), (1, 1)) if c != missing]


def chain_plan(A: int, B: int, L: int) -> list[list[tuple]]:
    """Integer-only plan of the chain: per line, three operations
    ('add', target, u, v, diff) / ('dbl', target, half) in the uniform
    add-double-add order.  Raises if a step is not available (it never is,
    by Bernstein's proof; the tests check it on random pairs)."""
    levels = bernstein_levels(A, B, L)
    state = set(top_line(levels[0][2]))
    plan = []
    for (An, Bn, Dn) in levels[1:]:
        t_oo, t_ee, t_mx = line_pairs(An, Bn, Dn)
        ops = []
        for t in (t_oo, t_ee, t_mx):
            if t is t_ee:
                half = (t[0] // 2, t[1] // 2)
                if half not in state:
                    raise AssertionError(f"doubling source {half} missing")
                ops.append(("dbl", t, half))
                continue
            found = None
            for u in sorted(state):
                v = (t[0] - u[0], t[1] - u[1])
                if v in state and v != u:
                    dif = (u[0] - v[0], u[1] - v[1])
                    if dif in DIFFS or (-dif[0], -dif[1]) in DIFFS:
                        found = (u, v, dif)
                        break
            if found is None:
                raise AssertionError(f"no differential addition for {t}")
            ops.append(("add", t, *found))
        plan.append(ops)
        state = {t_oo, t_ee, t_mx}
    if (A, B) not in state:
        raise AssertionError("(A, B) is not in the last line")
    return plan


def chain_2d(C: XCurve, k1: int, k2: int, xs: dict, L: int):
    """x(k1 P + k2 Q) for k1, k2 >= 0 by Bernstein's binary chain.

    ``xs`` maps the differences (1, 0), (0, 1), (1, 1), (1, -1) to x(P),
    x(Q), x(P + Q), x(P - Q) as (X, Z, affine) triples.  Every line is one
    differential addition, one doubling and one differential addition.
    """
    O = (1, 0)
    pts = {(0, 0): O, (1, 0): xs[(1, 0)][:2], (0, 1): xs[(0, 1)][:2], (1, 1): xs[(1, 1)][:2]}
    plan = chain_plan(k1, k2, L)
    for ops in plan:
        new = {}
        for op in ops:
            if op[0] == "dbl":
                new[op[1]] = C.xdbl(pts[op[2]])
            else:
                _, t, u, v, dif = op
                key = dif if dif in xs else (-dif[0], -dif[1])
                X, Z, aff = xs[key]
                new[t] = C.xadd(pts[u], pts[v], (X, Z), affine_diff=aff)
        pts = new
    return pts[(k1, k2)]


# ---------------------------------------------------------------------------
# chain endomorphisms on the x-line
# ---------------------------------------------------------------------------

@dataclass
class XChain:
    """One chain endomorphism as x-only maps: per step (ell, N, psi), then u^2."""
    element: tuple[int, int]
    matched_element: tuple[int, int]
    eigenvalue: int
    steps: list[int]
    polys: list[tuple[int, list[int], list[int]]]
    u: int
    full_maps: list = field(default_factory=list, repr=False)

    def apply_x(self, C: XCurve, x: int):
        """x(phi P) as (X : Z) from the affine x(P), counted.

        First step (affine input): X' = N(x), Z' = psi(x)^2, monic Horner
        (ell - 1 + s - 1 M, 1 S).  Later steps on (X : Z), with N and psi
        homogenised: x' = N_h(X, Z) / (Z psi_h(X, Z)^2) because ell = 2s + 1;
        powers Z^2..Z^ell (1 S + ell - 2 M), Horner from the monic leading
        term (ell - 1 + s - 1 M and ell + s constant multiplications), psi_h^2
        (1 S) and Z psi_h^2 (1 M).  The isomorphism back to E is X -> u^2 X.
        """
        F, p = C.F, C.p
        X, Z = x % p, 1
        for i, (ell, N, psi) in enumerate(self.polys):
            s = len(psi) - 1
            if i == 0:
                acc = (X + N[ell - 1]) % p
                for c in N[ell - 2::-1]:
                    acc = (F.mul(acc, X) + c) % p
                accp = (X + psi[s - 1]) % p if s >= 1 else 1
                for c in psi[s - 2::-1] if s >= 2 else []:
                    accp = (F.mul(accp, X) + c) % p
                X, Z = acc, F.sqr(accp)
                continue
            zp = [1, Z, F.sqr(Z)]
            for _ in range(3, ell + 1):
                zp.append(F.mul(zp[-1], Z))
            acc = (X + F.cmul(N[ell - 1], Z)) % p
            for j in range(ell - 2, -1, -1):
                acc = (F.mul(acc, X) + F.cmul(N[j], zp[ell - j])) % p
            accp = (X + F.cmul(psi[s - 1], Z)) % p
            for j in range(s - 2, -1, -1):
                accp = (F.mul(accp, X) + F.cmul(psi[j], zp[s - j])) % p
            X, Z = acc, F.mul(Z, F.sqr(accp))
        X = F.cmul(self.u * self.u, X)
        return (X, Z)

    def apply_full(self, P):
        """phi(P) on full affine points (uncounted; verification only)."""
        for m in self.full_maps:
            P = m(P)
        if P is None:
            return None
        u, p = self.u, self.full_maps[0].E.p
        return (u * u * P[0] % p, pow(u, 3, p) * P[1] % p)


def build_xchain(T: Target, D: int, element: tuple[int, int], steps: list[int], omega_root: int) -> XChain:
    p, a, b, n, h = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p, T.n, T.h
    res = EX.build_chain_endomorphism(p, a, b, n, h, D, element, curve_name=T.name, steps=list(steps),
                                      conjugates=False, omega_root=omega_root)
    if not res.found:
        raise RuntimeError(f"{T.name}: element {element} in order {steps} not built: {res.note}")
    E = Curve(p, a, b)
    cur, polys, maps = E, [], []
    for ell, hpoly in zip(res.steps, res.kernel_polys):
        N, psi, _M = CS.rational_map_polys(cur, hpoly, ell)
        iso = EX.KernelIsogeny(cur, hpoly, ell)
        polys.append((ell, list(N), list(psi)))
        maps.append(iso)
        cur = iso.codomain
    return XChain(tuple(element), tuple(res.matched_element), res.eigenvalue, list(res.steps), polys,
                  res.isomorphism_u, maps)


# ---------------------------------------------------------------------------
# references (uncounted)
# ---------------------------------------------------------------------------

def jacobian_mul(p: int, a: int, k: int, P):
    """k*P by left-to-right double-and-add in Jacobian coordinates
    (dbl-2007-bl, add-2007-bl); returns the affine point or None."""
    a %= p

    def dbl(Q):
        X, Y, Z = Q
        if Z == 0 or Y == 0:
            return (1, 1, 0)
        XX, YY, ZZ = X * X % p, Y * Y % p, Z * Z % p
        YYYY = YY * YY % p
        S = 2 * ((X + YY) ** 2 - XX - YYYY) % p
        M = (3 * XX + a * ZZ * ZZ) % p
        T = (M * M - 2 * S) % p
        return (T, (M * (S - T) - 8 * YYYY) % p, ((Y + Z) ** 2 - YY - ZZ) % p)

    def add(Q, R):
        if Q[2] == 0:
            return R
        if R[2] == 0:
            return Q
        X1, Y1, Z1 = Q
        X2, Y2, Z2 = R
        Z1Z1, Z2Z2 = Z1 * Z1 % p, Z2 * Z2 % p
        U1, U2 = X1 * Z2Z2 % p, X2 * Z1Z1 % p
        S1, S2 = Y1 * Z2 * Z2Z2 % p, Y2 * Z1 * Z1Z1 % p
        H = (U2 - U1) % p
        r = 2 * (S2 - S1) % p
        if H == 0:
            return dbl(Q) if r == 0 else (1, 1, 0)
        I = 4 * H * H % p
        J = H * I % p
        V = U1 * I % p
        X3 = (r * r - J - 2 * V) % p
        Y3 = (r * (V - X3) - 2 * S1 * J) % p
        Z3 = ((Z1 + Z2) ** 2 - Z1Z1 - Z2Z2) * H % p
        return (X3, Y3, Z3)

    if P is None:
        return None
    if k < 0:
        k, P = -k, (P[0], (-P[1]) % p)
    R = (1, 1, 0)
    Pj = (P[0], P[1], 1)
    for bit in bin(k)[2:] if k else "":
        R = dbl(R)
        if bit == "1":
            R = add(R, Pj)
    if R[2] == 0:
        return None
    zi = pow(R[2], -1, p)
    return (R[0] * zi * zi % p, R[1] * zi * zi * zi % p)


# ---------------------------------------------------------------------------
# the curves
# ---------------------------------------------------------------------------

# Tom-256 (ZKAttest, ePrint 2021/1183), as J08nY/std-curves lists it at commit
# 77fe6e3585ca2c2225b59d7df24b7c775437276f (other/curves.json); verified from
# the constants by targets.verify before use.
TOM256 = {
    "p": 0xffffffff0000000100000000000000017e72b42b30e7317793135661b1c4b117,
    "a": 0xffffffff0000000100000000000000017e72b42b30e7317793135661b1c4b114,
    "b": 0xb441071b12f4a0366fb552f8e21ed4ac36b06aceeb354224863e60f20219fc56,
    "n": 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
    "h": 1,
    "source": "J08nY/std-curves@77fe6e3585ca2c2225b59d7df24b7c775437276f other/curves.json (Tom-256)",
}

CP6_SOURCE = "research/endosweep_curves_20261006/arkworks/curves.json (cp6_782, arkworks-rs/curves@e2d16a27)"


def load_targets(repo_root: str = ".") -> list[tuple[Target, str]]:
    out = []
    T = next(t for t in deployed_targets() if t.name == "GOST CryptoPro-B")
    out.append((T, "harness/endosweep/targets.py (RFC 4357 id-GostR3410-2001-CryptoPro-B-ParamSet)"))
    path = os.path.join(repo_root, "research", "endosweep_curves_20261006", "arkworks", "curves.json")
    with open(path) as f:
        ark = json.load(f)
    c = next(c for c in ark["curves"] if c["name"] == "cp6_782")
    p = int(c["field"]["p"], 16)
    out.append((Target("CP6-782", p, "weierstrass",
                       {"a": int(c["params"]["a"]["raw"], 16), "b": int(c["params"]["b"]["raw"], 16)},
                       int(c["order"], 16), int(c["cofactor"], 16), notes="arkworks cp6_782 G1"), CP6_SOURCE))
    out.append((Target("Tom-256", TOM256["p"], "weierstrass", {"a": TOM256["a"], "b": TOM256["b"]},
                       TOM256["n"], TOM256["h"], notes="ZKAttest Tom-256"), TOM256["source"]))
    for T, _ in out:
        verify(T)
        if not T.verified:
            raise RuntimeError(f"{T.name}: {T.verification}")
    return out


# ---------------------------------------------------------------------------
# trace-one elements and their modelled chain cost
# ---------------------------------------------------------------------------

def trace_one_element(m: int) -> tuple[int, int]:
    """(1 + m sqrt D)/2 = (1 - m)/2 + m*omega, for odd m (D = 1 mod 4)."""
    if m % 2 == 0:
        raise ValueError("m must be odd")
    return ((1 - m) // 2, m)


def trace_one_elements(D: int, mmax: int = 15) -> list[dict]:
    """The trace-one elements (1 + m sqrt D)/2, odd m <= mmax, with norm and
    prime steps; empty for an even discriminant (Tr(a + b sqrt(D/4)) = 2a)."""
    if D % 4 != 1:
        return []
    out = []
    for m in range(1, mmax + 1, 2):
        el = trace_one_element(m)
        N, steps = element_steps(D, el)
        out.append({"m": m, "element": list(el), "norm": N, "steps": steps})
    return out


def element_steps(D: int, el: tuple[int, int]) -> tuple[int, list[int]]:
    """Norm and prime steps, largest first (the affine first step saves the most on the largest prime)."""
    N = QO.norm(D, *el)
    fac = factorint(N)
    return N, sorted((q for q, e in fac.items() for _ in range(e)), reverse=True)


def trace_one_survey(D: int, n: int, lam_omega: int, a: int, b: int, p: int, *, mmax: int = 401,
                     keep: int = 8) -> dict:
    """Every trace-one element (1 + m sqrt D)/2, odd m <= mmax: norm, steps,
    modelled chain cost per map, the GLV coefficient size (Babai bound of its
    own lattice, exact) and the modelled R = ladder / 2-D total (best of the
    two difference variants).  Empty for an even discriminant (no element
    has odd trace).  All modelled; the best one is built by ``run``."""
    if D % 4 != 1:
        return {"note": "even discriminant: Tr(a + b sqrt(D/4)) = 2a, no element of trace 1", "rows": []}
    ladder_m = CM.xonly_ladder_cost(n.bit_length(), a, b, p)["M_eq"]
    rows = []
    for m in range(1, mmax + 1, 2):
        el = trace_one_element(m)
        N, steps = element_steps(D, el)
        assert QO.trace(D, *el) == 1 and 4 * N == 1 + m * m * (-D)
        if 2 in steps:
            rows.append({"m": m, "norm": N, "steps": steps, "model_map_M_eq": None,
                         "note": "a 2-isogeny step: no x-only step formula here"})
            continue
        chain = CM.xonly_chain_cost(steps)["M_eq"]
        lam = (el[0] + el[1] * lam_omega) % n
        L = LA.reduce([1, lam], n).babai_bound.bit_length()
        tot = min(CM.xonly_2d_cost(L, a, b, p, 2 * chain, affine_differences=v)["M_eq"] for v in (False, True))
        rows.append({"m": m, "element": list(el), "norm": N, "steps": steps, "model_map_M_eq": chain,
                     "babai_bound_bits": L, "model_2d_M_eq": tot, "model_R": round(ladder_m / tot, 4)})
    ranked = sorted((r for r in rows if r["model_map_M_eq"] is not None), key=lambda r: -r["model_R"])
    return {"mmax": mmax, "ladder_model_M_eq": ladder_m, "count": len(rows),
            "omega": rows[0], "best": ranked[:keep]}


# ---------------------------------------------------------------------------
# one curve, one trace-one element
# ---------------------------------------------------------------------------

def _stats(xs: list[float]) -> dict:
    return {"mean": round(statistics.fmean(xs), 3),
            "sd": round(statistics.pstdev(xs), 3) if len(xs) > 1 else 0.0,
            "min": min(xs), "max": max(xs)}


def curve_discriminant(T: Target) -> tuple[int, int | None]:
    scan = QO.small_discriminant_scan(QO.frobenius_discriminant(T.q, T.trace), 2_000_000)
    if scan.found is None:
        raise RuntimeError(f"{T.name}: no small CM discriminant")
    return scan.found, scan.conductor


def run_curve(T: Target, source: str, *, m: int = 1, scalars: int = 20, map_points: int = 4,
              seed: int = 20261008, build_max_ell: int = 100) -> dict:
    """The x-only 2-D GLV of one curve with beta = (1 + m sqrt D)/2 (m = 1: omega).

    Builds beta and its conjugate 1 - beta as chains (when every step is at
    most ``build_max_ell``), checks them on points, and runs the ladder and
    the 2-D chain on ``scalars`` random scalars against a Jacobian k*P.
    """
    t0 = time.time()
    p, a, b, n, h = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p, T.n, T.h
    D, conductor = curve_discriminant(T)
    if D % 4 != 1:
        raise RuntimeError(f"{T.name}: even discriminant, no trace-one element")
    lam_w = QO.omega_eigenvalues(D, n)[0]
    el = trace_one_element(m)
    el_bar = (1 - el[0], -el[1])                         # 1 - beta = conj(beta) when Tr beta = 1
    assert QO.conjugate(D, *el) == el_bar
    lam = (el[0] + el[1] * lam_w) % n
    lam_bar = (1 - lam) % n
    N, steps = element_steps(D, el)
    E = Curve(p, a, b)
    C = XCurve(p, a, b)
    F = C.F
    rng = random.Random(seed + m)
    out: dict = {
        "name": T.name, "constants_source": source,
        "p": hex(p), "a": hex(a), "b": hex(b), "n": hex(n), "cofactor": hex(h),
        "p_bits": p.bit_length(), "n_bits": n.bit_length(), "verification": T.verification,
        "D_K": D, "conductor": conductor, "class_number": CS.class_number(D),
        "m": m, "beta": {"element": list(el), "conjugate": list(el_bar), "norm": N, "trace": QO.trace(D, *el),
                         "factors": {str(q): e for q, e in sorted(factorint(N).items())}, "steps": steps},
        "omega_root": hex(lam_w), "beta_root": hex(lam), "beta_bar_root": hex(lam_bar),
        "constants_small": {"a": min(a, p - a) < SMALL_CONSTANT, "b": min(b, p - b) < SMALL_CONSTANT},
    }

    # ---- the two maps ----------------------------------------------------
    built = max(steps) <= build_max_ell
    maps: dict[str, XChain] = {}
    endo_ops: dict[str, dict] = {}
    model = CM.xonly_chain_cost(steps)
    if built:
        tb = time.time()
        maps["beta"] = build_xchain(T, D, el, steps, lam_w)
        maps["beta_bar"] = build_xchain(T, D, el_bar, steps, lam_w)
        out["build_seconds"] = round(time.time() - tb, 2)
        for key, ch in maps.items():
            want = lam if key == "beta" else lam_bar
            assert ch.eigenvalue in (want, (n - want) % n), "built map acts as an unexpected scalar"
        checks = {"x_beta_P": 0, "x_beta_bar_P": 0, "x_betaP_minus_P_eq_x_beta_bar_P": 0}
        for i in range(map_points):
            P = EX.point_of_order(E, n, h, 1000 + 17 * i)
            for key, ch in maps.items():
                before = F.snapshot()
                Xq = ch.apply_x(C, P[0])
                got = ops_diff(F.snapshot(), before)
                assert endo_ops.setdefault(key, got) == got, "map cost depends on the point"
                ref = jacobian_mul(p, a, lam if key == "beta" else lam_bar, P)
                assert C.normalise(Xq) == ref[0], f"x({key} P) != x([lambda] P)"
                checks["x_beta_P" if key == "beta" else "x_beta_bar_P"] += 1
            # beta on full points; the built walk may be -beta (a unit the x-line cannot see)
            bP = maps["beta"].apply_full(P)
            assert bP is not None and E.on_curve(bP)
            if maps["beta"].eigenvalue != lam:
                bP = E.neg(bP)
            assert bP == jacobian_mul(p, a, lam, P), "beta P != [lambda] P on full points"
            diff = E.add(bP, E.neg(P))
            assert diff[0] == C.normalise(maps["beta_bar"].apply_x(C, P[0])), "x(beta P - P) != x(beta_bar P)"
            checks["x_betaP_minus_P_eq_x_beta_bar_P"] += 1
        F.reset()
        out["map_checks"] = checks
        out["beta"]["matched_element"] = list(maps["beta"].matched_element)
        out["beta"]["conjugate_matched_element"] = list(maps["beta_bar"].matched_element)
        out["endomorphism_cost_source"] = "measured: executed counts of the built chains' x-only evaluation"
    else:
        endo_ops = {"beta": dict(model), "beta_bar": dict(model)}
        ell = max(steps)
        out["endomorphism_cost_source"] = (
            f"modelled: the chain has a {ell}-isogeny step, whose kernel polynomial (degree {(ell - 1) // 2}) "
            f"would be found modulo the {ell}-division polynomial of degree {(ell * ell - 1) // 2}; not "
            f"attempted within this run's budget.  x(beta P) and x(beta_bar P) are produced as x([lambda] P) "
            f"and x([1 - lambda] P) by uncounted scalar multiplication and the modelled map counts are "
            f"charged, so the 2-D chain itself is still executed and checked")
    out["endomorphism_ops"] = endo_ops
    out["endomorphism_ops_model"] = model
    out["beta_bar_over_beta"] = round(endo_ops["beta_bar"]["M_eq"] / endo_ops["beta"]["M_eq"], 4)

    # ---- GLV lattice ------------------------------------------------------
    red = LA.reduce([1, lam], n)
    L = red.babai_bound.bit_length()
    out["glv"] = {"basis": [[str(x) for x in row] for row in red.basis], "babai_bound_bits": L}

    # ---- scalars ------------------------------------------------------------
    bits = n.bit_length()
    lad_counts, chain_counts = [], {"projective": [], "affine": []}
    pre_counts = {"projective": [], "affine": []}
    max_coeff_bits = 0
    for i in range(scalars):
        P = EX.point_of_order(E, n, h, 5000 + 31 * i)
        k = rng.randrange(1, n)
        ref = jacobian_mul(p, a, k, P)
        F.reset()
        R = ladder(C, k, P[0], bits)
        lad_counts.append(F.snapshot())
        assert C.normalise(R) == ref[0], "ladder disagrees with Jacobian k*P"
        k1, k2 = red.decompose(k)                          # integer arithmetic only
        max_coeff_bits = max(max_coeff_bits, abs(k1).bit_length(), abs(k2).bit_length())
        assert (k1 + k2 * lam - k) % n == 0
        for variant in ("projective", "affine"):
            F.reset()
            # Q = beta P and P - Q = (1 - beta) P = conj(beta) P: the conjugate chain
            if built:
                XQ = maps["beta"].apply_x(C, P[0])
                XD = maps["beta_bar"].apply_x(C, P[0])
            else:
                XQ = (jacobian_mul(p, a, lam, P)[0], 1)
                XD = (jacobian_mul(p, a, lam_bar, P)[0], 1)
                for key in ("beta", "beta_bar"):              # charge the modelled maps
                    F.M += endo_ops[key]["M"]
                    F.S += endo_ops[key]["S"]
                    F.Mc_full += endo_ops[key]["Mc_full"]
            XS = C.xadd((P[0], 1), XQ, XD, affine_diff=False)  # x(P + Q), difference P - Q
            if variant == "affine":
                # one shared inversion (Montgomery's trick) on Z(Q), Z(P - Q), Z(P + Q)
                z1, z2, z3 = XQ[1], XD[1], XS[1]
                z12 = F.mul(z1, z2)
                inv = F.inv(F.mul(z12, z3))
                i3, i12 = F.mul(inv, z12), F.mul(inv, z3)
                i1, i2 = F.mul(i12, z2), F.mul(i12, z1)
                XQ, XD, XS = (F.mul(XQ[0], i1), 1), (F.mul(XD[0], i2), 1), (F.mul(XS[0], i3), 1)
            pre_counts[variant].append(F.snapshot())
            aff = variant == "affine"
            xs = {(1, 0): (P[0], 1, aff), (0, 1): (*XQ, aff), (1, 1): (*XS, aff), (1, -1): (*XD, aff)}
            # (-k1, -k2) has the same x; a negative k2 is Q -> -Q, which swaps P + Q and P - Q
            s1, s2 = (k1, k2) if k1 >= 0 else (-k1, -k2)
            if s2 < 0:
                s2 = -s2
                xs[(1, 1)], xs[(1, -1)] = xs[(1, -1)], xs[(1, 1)]
            R2 = chain_2d(C, s1, s2, xs, L)
            chain_counts[variant].append(F.snapshot())
            assert C.normalise(R2) == ref[0], f"2-D chain ({variant}) disagrees with Jacobian k*P"
    F.reset()

    def summarise(cs: list[dict]) -> dict:
        return {k: _stats([c[k] for c in cs]) for k in ("M", "S", "Mc_full", "Mc_small", "I", "M_eq")}

    lad = summarise(lad_counts)
    out["scalars_checked"] = scalars
    out["max_coeff_bits"] = max_coeff_bits
    out["ladder"] = {"iterations": bits, "ops": lad, "model": CM.xonly_ladder_cost(bits, a, b, p)}
    out["chain_2d"] = {}
    for variant in ("projective", "affine"):
        tot = summarise(chain_counts[variant])
        out["chain_2d"][variant] = {
            "levels": L, "ops_total": tot, "ops_before_chain": summarise(pre_counts[variant]),
            "model": CM.xonly_2d_cost(L, a, b, p, 2 * model["M_eq"], affine_differences=(variant == "affine")),
            "R": round(lad["M_eq"]["mean"] / tot["M_eq"]["mean"], 4),
        }
    best = min(out["chain_2d"], key=lambda v: out["chain_2d"][v]["ops_total"]["M_eq"]["mean"])
    out["best_variant"] = best
    out["R"] = out["chain_2d"][best]["R"]
    # the same executed counts under two other weightings (re-weighting, not a new measurement)
    lo = {k: lad[k]["mean"] for k in ("M", "S", "Mc_full")}
    sens = {}
    for variant, c in out["chain_2d"].items():
        t = {k: c["ops_total"][k]["mean"] for k in ("M", "S", "Mc_full")}
        map_mc = endo_ops["beta"]["Mc_full"] + endo_ops["beta_bar"]["Mc_full"]
        sens[variant] = {
            "R_S_0.8M": round((lo["M"] + 0.8 * lo["S"] + lo["Mc_full"]) / (t["M"] + 0.8 * t["S"] + t["Mc_full"]), 4),
            "R_curve_constants_free": round((lo["M"] + lo["S"]) / (t["M"] + t["S"] + map_mc), 4),
        }
    out["R_sensitivity"] = sens
    out["uniformity"] = {
        "ladder": f"{bits} iterations of one xDBL and one mdadd for every scalar; the operands are chosen "
                  f"by one conditional swap per bit",
        "chain_2d": f"{L} levels of xADD, xDBL, xADD for every scalar (leading zero bits run through the "
                    f"identity (1 : 0)); which state points and which of the four differences enter each "
                    f"operation depends on the scalar bits, so a constant-time implementation needs "
                    f"constant-time selection (not implemented here); the GLV decomposition here is Python "
                    f"Babai rounding, not constant-time",
    }
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


# ---------------------------------------------------------------------------
# all curves, verdicts, report
# ---------------------------------------------------------------------------

PRED_LOW, PRED_HIGH, KILL_R, KILL_RATIO = 1.18, 1.28, 1.10, 1.3
SMOOTH = ("GOST CryptoPro-B", "CP6-782")


def verdicts(omega_rows: list[dict]) -> dict:
    smooth = [r for r in omega_rows if r["name"] in SMOOTH]
    tom = next((r for r in omega_rows if r["name"] == "Tom-256"), None)
    kill_r = all(r["R"] < KILL_R for r in smooth)
    measured = [r for r in omega_rows if r["endomorphism_cost_source"].startswith("measured")]
    kill_ratio = any(r["beta_bar_over_beta"] > KILL_RATIO for r in measured)
    return {
        "prediction_R_in_range": {r["name"]: PRED_LOW <= r["R"] <= PRED_HIGH for r in smooth},
        "prediction_tom256_R_below_1": None if tom is None else tom["R"] < 1,
        "kill_R_below_1.10_on_both": kill_r,
        "kill_conjugate_cost_above_1.3x": kill_ratio,
        "killed": kill_r or kill_ratio,
    }


def jacobian_reference(repo_root: str = ".") -> dict:
    """The harness's modelled Jacobian wNAF / GLV-2 numbers for these curves (curves.json)."""
    path = os.path.join(repo_root, "research", "endosweep_curves_20261006", "curves.json")
    with open(path) as f:
        d = json.load(f)
    names = {"gost/id-GostR3410-2001-CryptoPro-B-ParamSet": "GOST CryptoPro-B",
             "arkworks/cp6_782": "CP6-782", "other/Tom-256": "Tom-256"}
    out = {}
    for r in d["results"]:
        if r["name"] in names:
            mo = r["model_ops"]
            out[names[r["name"]]] = {
                "best_element": r["best_element"], "best_order": r["best_order"],
                "chain_M_eq_optimised": r["best_chain_M_eq"]["optimised"],
                "best_naf": mo["best_baseline"], "best_naf_M_eq": mo["baseline"][mo["best_baseline"]],
                "best_glv": mo["best_glv"], "best_glv_M_eq": mo["glv"][mo["best_glv"]],
                "ratio": mo["ratio"], "arithmetic": r["arithmetic"],
            }
    return out


def _el(r: dict) -> str:
    if r["m"] == 1:
        return "ω"
    a_, b_ = r["beta"]["element"]
    return f"{a_} + {b_}ω"


def _row(r: dict) -> str:
    src = "measured" if r["endomorphism_cost_source"].startswith("measured") else "**modelled**"
    c = r["chain_2d"]
    lo = r["ladder"]["ops"]["M_eq"]
    return (f"| {r['name']} | {r['D_K']} | {_el(r)} | {r['beta']['norm']} | {'·'.join(map(str, r['beta']['steps']))} | "
            f"{src} | {r['endomorphism_ops']['beta']['M_eq']} | {r['endomorphism_ops']['beta_bar']['M_eq']} | "
            f"{r['beta_bar_over_beta']} | {c['projective']['levels']} | {lo['mean']:.0f} ± {lo['sd']:.0f} | "
            f"{c['projective']['ops_total']['M_eq']['mean']:.0f} ± {c['projective']['ops_total']['M_eq']['sd']:.0f} | "
            f"{c['affine']['ops_total']['M_eq']['mean']:.0f} ± {c['affine']['ops_total']['M_eq']['sd']:.0f} | "
            f"**{r['R']}** ({r['best_variant']}) |")


HEAD = ("| curve | D_K | β | N(β) | steps | map cost | β M_eq | β̄ M_eq | β̄/β | levels | ladder M_eq | "
        "2-D projective M_eq | 2-D affine M_eq | R (best variant) |\n"
        "|:--|--:|:--|--:|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|")


def markdown(res: dict) -> str:
    L = []
    L.append("# x-only 2-D GLV with the conjugate chain as the difference point")
    L.append("")
    L.append("Generated by `harness/endosweep/xonly.py`.  Counts are field operations executed by that code "
             "(measured) unless marked modelled; `M_eq = M + S + Mc_full` (a squaring counted as a "
             "multiplication, a multiplication by a full-size constant as one, by a constant below 2^16 as "
             "free).  R = ladder M_eq / 2-D M_eq (endomorphisms, x(P+Q) and any normalisation included; the "
             "final conversion of the result to affine, equal for both, excluded).  No timing.")
    L.append("")
    L.append("## The candidate: β = ω, conjugate chain ω̄ = 1 − ω for x(P − ωP)")
    L.append("")
    L.append(HEAD)
    for r in res["omega"]:
        L.append(_row(r))
    L.append("")
    v = res["verdicts"]
    L.append("Predictions and kill criteria (fixed in advance):")
    L.append("")
    for name, ok in v["prediction_R_in_range"].items():
        L.append(f"- R ∈ [{PRED_LOW}, {PRED_HIGH}] on {name}: **{'held' if ok else 'did not hold'}**.")
    L.append(f"- R < 1 on Tom-256 (negative control): **{'held' if v['prediction_tom256_R_below_1'] else 'did not hold'}**.")
    L.append(f"- Kill if R < {KILL_R} on both smooth-norm curves: **{'triggered' if v['kill_R_below_1.10_on_both'] else 'not triggered'}**.")
    L.append(f"- Kill if cost(ω̄) > {KILL_RATIO}·cost(ω): **{'triggered' if v['kill_conjugate_cost_above_1.3x'] else 'not triggered'}**.")
    L.append("")
    if res["best_trace_one"]:
        L.append("## The best trace-one element where it is not ω (built and measured)")
        L.append("")
        L.append(HEAD)
        for r in res["best_trace_one"]:
            L.append(_row(r))
        L.append("")
    L.append("## Trace-one elements (1 + m√D)/2, odd m ≤ {}: modelled".format(res["survey_mmax"]))
    L.append("")
    L.append("| curve | m | element | norm | steps | map M_eq (model) | Babai bits | 2-D M_eq (model) | R (model) |")
    L.append("|:--|--:|:--|--:|:--|--:|--:|--:|--:|")
    for name, s in res["survey"].items():
        rows = [s["omega"]] + [r for r in s["best"] if r["m"] != 1][:4]
        for r in rows:
            L.append(f"| {name} | {r['m']} | {r['element'][0]} + {r['element'][1]}ω | {r['norm']} | "
                     f"{'·'.join(map(str, r['steps']))} | {r['model_map_M_eq']} | {r['babai_bound_bits']} | "
                     f"{r['model_2d_M_eq']} | {r['model_R']} |")
    L.append("")
    L.append("## Per curve")
    L.append("")
    for r in res["omega"] + res["best_trace_one"]:
        L.append(f"### {r['name']}, β = {_el(r)}")
        L.append("")
        L.append(f"- Constants: {r['constants_source']}; {r['verification']}.")
        L.append(f"- `p` {r['p_bits']} bits, `n` {r['n_bits']} bits, `D_K = {r['D_K']}`, class number "
                 f"{r['class_number']}; `a` small: {r['constants_small']['a']}, `b` small: {r['constants_small']['b']}.")
        if "map_checks" in r:
            mc = r["map_checks"]
            L.append(f"- β and β̄ built as chains {'·'.join(map(str, r['beta']['steps']))} in {r['build_seconds']} s "
                     f"(matched elements {r['beta']['matched_element']} and {r['beta']['conjugate_matched_element']}, "
                     f"up to ±1).  On points of order n: x(βP) = x([λ]P) {mc['x_beta_P']}×, x(β̄P) = x([1−λ]P) "
                     f"{mc['x_beta_bar_P']}×, x(βP − P) = x(β̄P) with β on full points "
                     f"{mc['x_betaP_minus_P_eq_x_beta_bar_P']}×.")
        else:
            L.append(f"- {r['endomorphism_cost_source']}.")
        for key, sym in (("beta", "β"), ("beta_bar", "β̄")):
            o = r["endomorphism_ops"][key]
            L.append(f"- {sym}: {o['M']} M + {o['S']} S + {o['Mc_full']} Mc = {o['M_eq']} M_eq "
                     f"(closed form {r['endomorphism_ops_model']['M_eq']}).")
        lo = r["ladder"]["ops"]
        L.append(f"- Ladder, {r['ladder']['iterations']} iterations: {lo['M']['mean']:.0f} M + {lo['S']['mean']:.0f} S + "
                 f"{lo['Mc_full']['mean']:.0f} Mc (+ {lo['Mc_small']['mean']:.0f} small) = {lo['M_eq']['mean']:.0f} M_eq, "
                 f"sd {lo['M_eq']['sd']} over {r['scalars_checked']} scalars (closed form {r['ladder']['model']['M_eq']}).")
        for variant, c in r["chain_2d"].items():
            t, pre = c["ops_total"], c["ops_before_chain"]
            L.append(f"- 2-D chain, {variant} differences, {c['levels']} levels: {t['M_eq']['mean']:.0f} M_eq "
                     f"(sd {t['M_eq']['sd']}), of which {pre['M_eq']['mean']:.0f} before the chain (both maps, "
                     f"x(P+Q){', one shared inversion' if variant == 'affine' else ''}); closed form "
                     f"{c['model']['M_eq']}; R = {c['R']}.")
        sv = r["R_sensitivity"]
        L.append("- Same counts, other weightings: R with S = 0.8 M "
                 + ", ".join(f"{v} {s['R_S_0.8M']}" for v, s in sv.items())
                 + "; R with the curve constants a, b free (EFD's convention) "
                 + ", ".join(f"{v} {s['R_curve_constants_free']}" for v, s in sv.items()) + ".")
        L.append(f"- Largest |k_i| over the scalars: {r['max_coeff_bits']} bits (Babai bound {r['glv']['babai_bound_bits']}).")
        jr = res["jacobian_reference"].get(r["name"])
        if jr:
            L.append(f"- Harness Jacobian model (curves.json; variable-time wNAF): best NAF {jr['best_naf_M_eq']} "
                     f"({jr['best_naf']}), best GLV-2 with {jr['best_element'][0]} + {jr['best_element'][1]}ω "
                     f"{jr['best_glv_M_eq']} ({jr['best_glv']}), ratio {jr['ratio']}.")
        L.append("")
    return "\n".join(L) + "\n"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(repo_root: str = ".", *, scalars: int = 20, seed: int = 20261008, mmax: int = 401,
        build_max_ell: int = 100, progress=None) -> dict:
    omega_rows, best_rows, survey = [], [], {}
    for T, src in load_targets(repo_root):
        r = run_curve(T, src, m=1, scalars=scalars, seed=seed, build_max_ell=build_max_ell)
        omega_rows.append(r)
        if progress:
            progress(r)
        p, a, b, n = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p, T.n
        s = trace_one_survey(r["D_K"], n, int(r["omega_root"], 16), a, b, p, mmax=mmax)
        survey[T.name] = s
        top = s["best"][0] if s["best"] else None
        if top and top["m"] != 1 and max(top["steps"]) <= build_max_ell:
            r2 = run_curve(T, src, m=top["m"], scalars=scalars, seed=seed, build_max_ell=build_max_ell)
            best_rows.append(r2)
            if progress:
                progress(r2)
    try:
        import flint  # type: ignore
        fv = flint.__version__
    except ImportError:
        fv = None
    res = {"format": FORMAT, "generator": GENERATOR, "seed": seed, "scalars_per_curve": scalars,
           "python_flint": fv, "survey_mmax": mmax, "build_max_ell": build_max_ell,
           "efd": {"page": "https://hyperelliptic.org/EFD/g1p/auto-shortw-xz.html",
                   "xDBL": "dbl-2002-bj-3", "xADD": "dadd-2002-it-3", "xADD_affine_difference": "mdadd-2002-it-3"},
           "omega": omega_rows, "best_trace_one": best_rows, "survey": survey,
           "jacobian_reference": jacobian_reference(repo_root)}
    res["verdicts"] = verdicts(omega_rows)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="x-only 2-D GLV with the conjugate chain as difference")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--scalars", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--mmax", type=int, default=401)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)

    def progress(r):
        print(f"{r['name']} beta={r['beta']['element']}: R = {r['R']} ({r['best_variant']}), maps "
              f"{r['endomorphism_ops']['beta']['M_eq']} / {r['endomorphism_ops']['beta_bar']['M_eq']} M_eq, "
              f"{r['elapsed_s']} s", flush=True)

    res = run(".", scalars=args.scalars, seed=args.seed, mmax=args.mmax, progress=progress)
    jpath = os.path.join(args.out_dir, "xonly.json")
    with open(jpath, "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    with open(os.path.join(args.out_dir, "xonly.md"), "w") as f:
        f.write(markdown(res))
    with open(os.path.join(args.out_dir, "SHA256SUMS"), "w") as f:
        f.write(f"{sha256_file(jpath)}  xonly.json\n")
    print(json.dumps(res["verdicts"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
