"""
EXP-PMA-001 shared definitions.

These are pure definitional utilities (subset enumeration, the p_S -> q_ij,
c_ijk, Delta_ijk formulas exactly as pinned in specification.yaml, and a
rational-function representation with canonical reduction). They are used
identically by Module A (parity_predicate.py) and Module B
(existence_decider.py) because they encode the frozen problem *data*, not
either module's *decision procedure*. The decision procedures themselves
(squareness-by-divisor-valuation in Module A vs. constructive
coefficient-matching square-root search in Module B) are independent code
paths with no shared logic, as required by the specification's control
CTRL-PMA4-GROUND-TRUTH.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Dict, List, Tuple, Union

import sympy
from sympy import symbols, Poly, gcd as sympy_gcd, ZZ, QQ, GF

t = symbols("t")

# ---------------------------------------------------------------------------
# Subset enumeration: the 15 nonempty subsets of {1,2,3,4}, fixed canonical
# order (by size, then lexicographic). This ordering is the executor's own
# deterministic convention (the specification pins the formulas and field
# list but not a literal numeric parameter box); it is disclosed in
# implementation.md as a protocol-interpretation choice, applied identically
# and never adjusted post hoc.
# ---------------------------------------------------------------------------
INDICES = (1, 2, 3, 4)

NONEMPTY_SUBSETS: List[Tuple[int, ...]] = []
for size in (1, 2, 3, 4):
    for combo in combinations(INDICES, size):
        NONEMPTY_SUBSETS.append(combo)

SUBSET_INDEX = {s: i for i, s in enumerate(NONEMPTY_SUBSETS)}

ANCHOR_TRIPLES = [(1, 2, 3), (1, 2, 4), (1, 3, 4)]
NON_ANCHOR_TRIPLE = (2, 3, 4)
FULL_SET = (1, 2, 3, 4)


def field_domain(field):
    """field is either an int q (odd prime power we treat as GF(q) with
    sympy, restricted in this experiment to prime q in {3,5,7,2,4}) or the
    string 'Q'. Returns the sympy polynomial domain object.
    NOTE: F_4 (q=4, a prime power, not prime) cannot be represented by
    sympy's GF(q) (prime fields only); it is handled specially wherever it
    is used (char-2 refusal control only -- no field arithmetic beyond
    detecting the characteristic is required for F_4 in this experiment)."""
    if field == "Q":
        return QQ
    if field == 4:
        raise ValueError("F_4 has no sympy GF() support; handled specially by char-2 refusal control only")
    return GF(field)


def characteristic(field) -> int:
    if field == "Q":
        return 0
    if field == 4:
        return 2
    return field


# ---------------------------------------------------------------------------
# Canonically-reduced rational function N(t)/D(t) over a fixed domain.
# gcd(N, D) = 1, D monic (leading coefficient 1 in the domain).
# ---------------------------------------------------------------------------
@dataclass
class RationalFunction:
    num: Poly
    den: Poly
    domain: object

    @staticmethod
    def constant(value, domain) -> "RationalFunction":
        num = Poly(value, t, domain=domain)
        den = Poly(1, t, domain=domain)
        return RationalFunction(num, den, domain)

    @staticmethod
    def from_pS(d_S, domain) -> "RationalFunction":
        """p_S = (t+1)/(t+d_S)"""
        num = Poly(t + 1, t, domain=domain)
        den = Poly(t + d_S, t, domain=domain)
        return RationalFunction(num, den, domain).reduced()

    def reduced(self) -> "RationalFunction":
        num, den = self.num, self.den
        if den == 0:
            raise ZeroDivisionError("rational function with zero denominator")
        if num == 0:
            return RationalFunction(Poly(0, t, domain=self.domain), Poly(1, t, domain=self.domain), self.domain)
        g = num.gcd(den)
        if g.degree() > 0 or (g.degree() == 0 and g.LC() != 1):
            num = num.quo(g)
            den = den.quo(g)
        # normalize denominator to monic
        lc = den.LC()
        if lc != 1:
            if self.domain == QQ:
                num = num.mul_ground(sympy.Rational(1, 1) / lc)
                den = den.mul_ground(sympy.Rational(1, 1) / lc)
            else:
                inv_lc = pow(int(lc), -1, self.domain.mod)
                num = num.mul_ground(inv_lc)
                den = den.mul_ground(inv_lc)
        return RationalFunction(num, den, self.domain)

    def __add__(self, other: "RationalFunction") -> "RationalFunction":
        num = self.num * other.den + other.num * self.den
        den = self.den * other.den
        return RationalFunction(num, den, self.domain).reduced()

    def __sub__(self, other: "RationalFunction") -> "RationalFunction":
        num = self.num * other.den - other.num * self.den
        den = self.den * other.den
        return RationalFunction(num, den, self.domain).reduced()

    def __mul__(self, other: "RationalFunction") -> "RationalFunction":
        num = self.num * other.num
        den = self.den * other.den
        return RationalFunction(num, den, self.domain).reduced()

    def __truediv__(self, other: "RationalFunction") -> "RationalFunction":
        if other.num == 0:
            raise ZeroDivisionError("division by the zero rational function")
        num = self.num * other.den
        den = self.den * other.num
        return RationalFunction(num, den, self.domain).reduced()

    def scale(self, c) -> "RationalFunction":
        return self * RationalFunction.constant(c, self.domain)

    def is_zero(self) -> bool:
        return self.num == 0

    def __eq__(self, other) -> bool:
        if not isinstance(other, RationalFunction):
            return NotImplemented
        a = self.reduced()
        b = other.reduced()
        return a.num == b.num and a.den == b.den

    def as_tuple(self):
        return (self.num.all_coeffs(), self.den.all_coeffs())

    def __repr__(self):
        return f"({self.num.as_expr()})/({self.den.as_expr()})"


def four(c):
    return c + c + c + c


def build_p_table(d_values: Dict[Tuple[int, ...], object], domain) -> Dict[Tuple[int, ...], RationalFunction]:
    """d_values maps each nonempty subset S to its d_S parameter.
    Returns p_S for every nonempty S plus p_emptyset = 1."""
    table = {(): RationalFunction.constant(1, domain)}
    for S, d_S in d_values.items():
        table[S] = RationalFunction.from_pS(d_S, domain)
    return table


def q_ij(p_table, i, j, domain) -> RationalFunction:
    pi = p_table[(i,)]
    pj = p_table[(j,)]
    pij = p_table[tuple(sorted((i, j)))]
    return (pi * pj) - pij


def c_ijk(p_table, i, j, k, domain) -> RationalFunction:
    S3 = tuple(sorted((i, j, k)))
    pi, pj, pk = p_table[(i,)], p_table[(j,)], p_table[(k,)]
    pijk = p_table[S3]
    qjk = q_ij(p_table, j, k, domain)
    qik = q_ij(p_table, i, k, domain)
    qij = q_ij(p_table, i, j, domain)
    term = pijk - (pi * pj * pk) + (pi * qjk) + (pj * qik) + (pk * qij)
    return term


def delta_ijk(p_table, i, j, k, domain) -> RationalFunction:
    c = c_ijk(p_table, i, j, k, domain)
    qij = q_ij(p_table, i, j, domain)
    qjk = q_ij(p_table, j, k, domain)
    qki = q_ij(p_table, k, i, domain)
    four_q = qij * qjk * qki
    four_rf = RationalFunction.constant(4, domain)
    return (c * c) - (four_rf * four_q)


def is_square_constant(c, domain) -> bool:
    """Is the scalar c (an element of the constant field, given as a sympy
    domain element / int / Rational) a square in that field?"""
    if domain == QQ:
        r = sympy.Rational(c)
        if r == 0:
            return True
        if r < 0:
            return False
        num, den = r.p, r.q
        n_ok, _ = sympy.integer_nthroot(num, 2)
        d_ok, _ = sympy.integer_nthroot(den, 2)
        return num == n_ok * n_ok and den == d_ok * d_ok
    else:
        q = domain.mod
        c = int(c) % q
        if c == 0:
            return True
        return pow(c, (q - 1) // 2, q) == 1
