"""Digit and direct presentations (IDEA-20260830-84cdb7) as ring builders.

DIRECT presentation: unknowns x_1..x_m are free variables; the interval factor
base V = [0, B) is imposed by the membership generators
    f_V(x) = prod_{v in [0, B)} (x - v).

DIGIT presentation: each unknown is x_k = sum_{i < s} a_{k,i} d^i with digit
variables a_{k,i}; membership is prod_{j < d} (a - j) = 0 per digit.
  * d = 2 : the digits are SQUAREFREE ring variables (a(a - 1) = 0 is the ring
            quotient, so no explicit membership generator is emitted);
  * d > 2 : the digits are free variables with explicit membership generators.

s = 1, d = B collapses to the direct presentation: one digit a_{k,0} = x_k and
the membership generator prod_{j<B}(a_{k,0} - j) = f_V(x_k), generator for
generator.  :func:`digit_presentation` returns the generators in the order
(substituted system polynomials..., membership generators in unknown-major,
digit-minor order), and :func:`direct_presentation` in the order
(system polynomials..., f_V(x_1), ..., f_V(x_m)), so the s = 1 slice test can
compare the two lists element-wise after the trivial variable identification.

Mixed mode helper: :func:`digit_presentation` accepts ``free_names`` for extra
free variables (e.g. the internal node u of EXP-PFDR-20ee58's chained tree)
which are appended after the digit variables.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .poly import Monomial, Poly, Ring


@dataclass(frozen=True)
class Presentation:
    ring: Ring
    generators: Tuple[Poly, ...]
    unknown_polys: Tuple[Poly, ...]   # x_k expressed in the ring (linear forms)
    membership: Tuple[Poly, ...]
    variable_names: Tuple[str, ...]
    description: str


def membership_generator(ring: Ring, var: Monomial, base: int) -> Poly:
    """prod_{j < base} (var - j) in ``ring``."""
    prod: Poly = {ring.one(): 1}
    for j in range(base):
        factor = ring.add({var: 1}, ring.constant(-j))
        prod = ring.mul(prod, factor)
    return prod


def f_V(ring: Ring, var: Monomial, B: int) -> Poly:
    """Direct-presentation membership generator prod_{v in [0, B)} (x - v)."""
    return membership_generator(ring, var, B)


def direct_presentation(
    p: int,
    m: int,
    B: int,
    system: Callable[[Ring, Sequence[Poly]], Sequence[Poly]],
    n_extra_free: int = 0,
) -> Presentation:
    """Ordinary-monomial ring in x_1..x_m (plus ``n_extra_free`` free variables
    appended), generators = system(x) followed by f_V(x_k)."""
    ring = Ring(p, 0, m + n_extra_free)
    xs = [{ring.free_var(k): 1} for k in range(m)]
    sys_polys = [ring.reduce(dict(f)) for f in system(ring, xs)]
    memb = [f_V(ring, ring.free_var(k), B) for k in range(m)]
    names = tuple([f"x{k + 1}" for k in range(m)] + [f"w{j}" for j in range(n_extra_free)])
    return Presentation(ring, tuple(sys_polys) + tuple(memb), tuple(xs), tuple(memb), names,
                        f"direct presentation, m={m}, B={B}, p={p}")


def digit_presentation(
    p: int,
    m: int,
    d: int,
    s: int,
    system: Callable[[Ring, Sequence[Poly]], Sequence[Poly]],
    n_extra_free: int = 0,
) -> Presentation:
    """Digit ring for m unknowns, base d, s digits each.

    d == 2: squarefree digits (mode squarefree, or mixed if n_extra_free > 0).
    d  > 2: free digits with explicit membership generators (ordinary mode).
    """
    if d < 2 or s < 1:
        raise ValueError("need base d >= 2 and s >= 1 digits")
    if d == 2:
        ring = Ring(p, m * s, n_extra_free)
        digit = lambda k, i: ring.sq_var(k * s + i)  # noqa: E731
    else:
        ring = Ring(p, 0, m * s + n_extra_free)
        digit = lambda k, i: ring.free_var(k * s + i)  # noqa: E731
    xs: List[Poly] = []
    for k in range(m):
        x: Poly = {}
        for i in range(s):
            x = ring.add(x, {digit(k, i): pow(d, i, p) % p})
        xs.append(x)
    sys_polys = [ring.reduce(dict(f)) for f in system(ring, xs)]
    memb: List[Poly] = []
    if d > 2:
        for k in range(m):
            for i in range(s):
                memb.append(membership_generator(ring, digit(k, i), d))
    names = tuple([f"a{k + 1}_{i}" for k in range(m) for i in range(s)]
                  + [f"w{j}" for j in range(n_extra_free)])
    return Presentation(ring, tuple(sys_polys) + tuple(memb), tuple(xs), tuple(memb), names,
                        f"digit presentation, m={m}, d={d}, s={s}, p={p}")


def substitute(ring: Ring, poly_in_x: Dict[Tuple[int, ...], int], xs: Sequence[Poly]) -> Poly:
    """Evaluate a polynomial given as {exponent tuple over x_1..x_m: coeff} at
    the ring polynomials ``xs`` (used by callers to write S_3 etc. once)."""
    out: Poly = {}
    for exps, c in poly_in_x.items():
        term: Poly = ring.constant(c)
        for k, e in enumerate(exps):
            if e:
                term = ring.mul(term, ring.power(xs[k], e))
        out = ring.add(out, term)
    return out


def rename_direct_to_digit_s1(direct_ring: Ring, digit_ring: Ring, poly: Poly) -> Poly:
    """Identity map x_k -> a_{k,0} for the s = 1, d = B slice (both ordinary
    rings with the same number of free variables); exists so the comparison in
    the test is an explicit, named step rather than an implicit equality."""
    if direct_ring.n_free != digit_ring.n_free or direct_ring.n_sq or digit_ring.n_sq:
        raise ValueError("s = 1 slice identification needs matching ordinary rings")
    return dict(poly)
