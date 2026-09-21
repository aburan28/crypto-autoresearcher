"""Exact F_p polynomial layer for the Macaulay deficit meter.

Ring shape.  A :class:`Ring` has ``n_sq`` SQUAREFREE variables ``a_0..a_{n_sq-1}``
subject to ``a(a - 1) = 0`` (so ``a^2 -> a`` and every monomial is multilinear in
them) and ``n_free`` ORDINARY variables ``u_0..u_{n_free-1}`` with no quotient.

* squarefree / digit mode  : ``n_free == 0``
* ordinary-monomial mode   : ``n_sq == 0``
* mixed mode               : ``n_sq > 0`` and ``n_free >= 1`` (the battery uses
  exactly one free variable ``u``; any number is supported)

Monomials are tuples ``(mask, exps)``: ``mask`` is the bitmask of squarefree
variables present and ``exps`` a tuple of ``n_free`` non-negative exponents.
Total degree is ``popcount(mask) + sum(exps)``.  Multiplication is bitwise OR on
the mask (this is exactly the reduction ``a^2 -> a``, which is coefficient
preserving in F_p[a]/(a^2 - a) for every p) and exponent addition on the free
part.

Polynomials are ``dict[monomial, int]`` with coefficients reduced to ``[1, p-1]``
(zero coefficients are never stored).  All arithmetic uses Python integers, so
the same code is exact at p = 2 and at the 256-bit P-256 prime; no floating
point is ever used.

Ported from ``experiments/EXP-SBRG-60c55e/driver/macaulay.py`` (frozenset-of-
bitmask Boolean polynomials): ``monomial_degree``, ``poly_degree``,
``multiply_by_monomial`` (bitwise OR), ``evaluate``, ``all_monomials_exact/upto``
are generalised here to the (mask, exps) representation with coefficients.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple

Monomial = Tuple[int, Tuple[int, ...]]
Poly = Dict[Monomial, int]


def _compositions(total: int, parts: int) -> Iterator[Tuple[int, ...]]:
    """All tuples of ``parts`` non-negative integers summing to ``total``."""
    if parts == 0:
        if total == 0:
            yield ()
        return
    if parts == 1:
        yield (total,)
        return
    for first in range(total, -1, -1):
        for rest in _compositions(total - first, parts - 1):
            yield (first,) + rest


@dataclass(frozen=True)
class Ring:
    """Ring shape and characteristic.  Immutable; all helpers are pure."""

    p: int
    n_sq: int
    n_free: int = 0

    def __post_init__(self) -> None:
        if self.p < 2:
            raise ValueError("p must be a prime >= 2")
        if self.n_sq < 0 or self.n_free < 0:
            raise ValueError("variable counts must be non-negative")
        # Cheap primality screen (deterministic Miller-Rabin bases cover < 3.3e24;
        # for larger p we trust the caller, as the battery uses named primes).
        if not _probable_prime(self.p):
            raise ValueError(f"p = {self.p} is not prime")

    # ----- shape queries --------------------------------------------------
    @property
    def mode(self) -> str:
        if self.n_free == 0:
            return "squarefree"
        if self.n_sq == 0:
            return "ordinary"
        return "mixed"

    @property
    def nvars(self) -> int:
        return self.n_sq + self.n_free

    def one(self) -> Monomial:
        return (0, (0,) * self.n_free)

    def sq_var(self, i: int) -> Monomial:
        if not 0 <= i < self.n_sq:
            raise IndexError(f"squarefree variable {i} out of range")
        return (1 << i, (0,) * self.n_free)

    def free_var(self, j: int) -> Monomial:
        if not 0 <= j < self.n_free:
            raise IndexError(f"free variable {j} out of range")
        e = [0] * self.n_free
        e[j] = 1
        return (0, tuple(e))

    # ----- monomial combinatorics ----------------------------------------
    def count_monomials_exact(self, degree: int) -> int:
        """Number of ring monomials of total degree exactly ``degree`` (no allocation)."""
        if degree < 0:
            return 0
        total = 0
        for i in range(0, min(degree, self.n_sq) + 1):
            j = degree - i
            if self.n_free == 0:
                free_count = 1 if j == 0 else 0
            else:
                free_count = comb(j + self.n_free - 1, self.n_free - 1)
            total += comb(self.n_sq, i) * free_count
        return total

    def count_monomials_upto(self, degree: int) -> int:
        return sum(self.count_monomials_exact(d) for d in range(degree + 1))

    def monomials_exact(self, degree: int) -> List[Monomial]:
        """All monomials of total degree exactly ``degree`` (deterministic order)."""
        out: List[Monomial] = []
        if degree < 0:
            return out
        for i in range(0, min(degree, self.n_sq) + 1):
            j = degree - i
            if self.n_free == 0 and j != 0:
                continue
            free_parts = list(_compositions(j, self.n_free))
            for idxs in combinations(range(self.n_sq), i):
                mask = 0
                for idx in idxs:
                    mask |= 1 << idx
                for e in free_parts:
                    out.append((mask, e))
        return out

    def monomials_upto(self, degree: int) -> List[Monomial]:
        out: List[Monomial] = []
        for d in range(degree + 1):
            out.extend(self.monomials_exact(d))
        return out

    # ----- monomial arithmetic --------------------------------------------
    @staticmethod
    def mono_degree(m: Monomial) -> int:
        return bin(m[0]).count("1") + sum(m[1])

    @staticmethod
    def mono_mul(a: Monomial, b: Monomial) -> Monomial:
        return (a[0] | b[0], tuple(x + y for x, y in zip(a[1], b[1])))

    # ----- polynomial arithmetic ------------------------------------------
    def reduce(self, poly: Poly) -> Poly:
        p = self.p
        return {m: c % p for m, c in poly.items() if c % p}

    def add(self, a: Poly, b: Poly) -> Poly:
        out = dict(a)
        p = self.p
        for m, c in b.items():
            v = (out.get(m, 0) + c) % p
            if v:
                out[m] = v
            else:
                out.pop(m, None)
        return out

    def scale(self, a: Poly, s: int) -> Poly:
        s %= self.p
        if s == 0:
            return {}
        return {m: (c * s) % self.p for m, c in a.items()}

    def sub(self, a: Poly, b: Poly) -> Poly:
        return self.add(a, self.scale(b, -1))

    def mul_monomial(self, poly: Poly, mono: Monomial, coeff: int = 1) -> Poly:
        """Multiply by ``coeff * mono`` and reduce a^2 -> a.

        Distinct source terms can collapse onto the same reduced monomial (mask OR)
        and their coefficients then ADD mod p; at p = 2 this is macaulay.py's
        cancellation on collision.
        """
        out: Poly = {}
        p = self.p
        coeff %= p
        if coeff == 0:
            return out
        for m, c in poly.items():
            r = (m[0] | mono[0], tuple(x + y for x, y in zip(m[1], mono[1])))
            v = (out.get(r, 0) + c * coeff) % p
            if v:
                out[r] = v
            else:
                out.pop(r, None)
        return out

    def mul(self, a: Poly, b: Poly) -> Poly:
        out: Poly = {}
        for m, c in b.items():
            out = self.add(out, self.mul_monomial(a, m, c))
        return out

    def power(self, a: Poly, e: int) -> Poly:
        result: Poly = {self.one(): 1}
        base = dict(a)
        while e:
            if e & 1:
                result = self.mul(result, base)
            e >>= 1
            if e:
                base = self.mul(base, base)
        return result

    def constant(self, c: int) -> Poly:
        c %= self.p
        return {self.one(): c} if c else {}

    def degree(self, poly: Poly) -> int:
        """Total degree after reduction; -1 for the zero polynomial."""
        if not poly:
            return -1
        return max(self.mono_degree(m) for m in poly)

    def top_form(self, poly: Poly) -> Poly:
        """Homogeneous part of maximal total degree (the leading form)."""
        d = self.degree(poly)
        return {m: c for m, c in poly.items() if self.mono_degree(m) == d}

    def degree_part(self, poly: Poly, degree: int) -> Poly:
        return {m: c for m, c in poly.items() if self.mono_degree(m) == degree}

    def degree_histogram(self, poly: Poly) -> Dict[int, int]:
        """Number of monomials at each total degree (macaulay.py's degree_histogram)."""
        hist: Dict[int, int] = {}
        for m in poly:
            d = self.mono_degree(m)
            hist[d] = hist.get(d, 0) + 1
        return hist

    def evaluate(self, poly: Poly, sq_values: Sequence[int], free_values: Sequence[int] = ()) -> int:
        """Evaluate at a point.  Squarefree values must be 0 or 1 for the quotient
        to be respected (checked); free values are arbitrary residues."""
        if len(sq_values) != self.n_sq or len(free_values) != self.n_free:
            raise ValueError("point has the wrong shape for this ring")
        for v in sq_values:
            if v not in (0, 1):
                raise ValueError("squarefree variables take values in {0, 1}")
        mask_one = 0
        for i, v in enumerate(sq_values):
            if v:
                mask_one |= 1 << i
        acc = 0
        p = self.p
        for (mask, exps), c in poly.items():
            if mask & ~mask_one:
                continue
            term = c
            for e, fv in zip(exps, free_values):
                if e:
                    term = term * pow(fv % p, e, p) % p
            acc = (acc + term) % p
        return acc

    def is_homogeneous(self, poly: Poly) -> bool:
        degs = {self.mono_degree(m) for m in poly}
        return len(degs) <= 1

    def to_string(self, poly: Poly, sq_names: Sequence[str] | None = None,
                  free_names: Sequence[str] | None = None) -> str:
        """Human-readable rendering (deterministic order), for logs and notes."""
        if not poly:
            return "0"
        sq_names = list(sq_names) if sq_names else [f"a{i}" for i in range(self.n_sq)]
        free_names = list(free_names) if free_names else [f"u{j}" for j in range(self.n_free)]
        terms = []
        for (mask, exps), c in sorted(poly.items(), key=lambda kv: (-self.mono_degree(kv[0]), kv[0])):
            factors = [sq_names[i] for i in range(self.n_sq) if mask >> i & 1]
            for j, e in enumerate(exps):
                if e == 1:
                    factors.append(free_names[j])
                elif e > 1:
                    factors.append(f"{free_names[j]}^{e}")
            body = "*".join(factors) if factors else "1"
            if c == 1 and factors:
                terms.append(body)
            elif factors:
                terms.append(f"{c}*{body}")
            else:
                terms.append(str(c))
        return " + ".join(terms)


def _probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for q in small:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def poly_from_terms(ring: Ring, terms: Iterable[Tuple[int, Sequence[int], Sequence[int]]]) -> Poly:
    """Build a polynomial from ``(coeff, sq_indices, free_exponents)`` triples."""
    out: Poly = {}
    for c, sq_idx, exps in terms:
        mask = 0
        for i in sq_idx:
            mask |= 1 << i
        e = tuple(exps) if ring.n_free else ()
        if len(e) != ring.n_free:
            raise ValueError("free exponent tuple has the wrong length")
        out = ring.add(out, {(mask, e): c % ring.p} if c % ring.p else {})
    return out


def boolean_masks_to_poly(ring: Ring, masks: Iterable[int]) -> Poly:
    """Import a macaulay.py Boolean polynomial (frozenset of bitmasks) at p = 2."""
    if ring.p != 2 or ring.n_free != 0:
        raise ValueError("Boolean import requires p = 2 and a pure squarefree ring")
    out: Poly = {}
    for m in masks:
        key = (int(m), ())
        if key in out:
            del out[key]
        else:
            out[key] = 1
    return out


def poly_to_boolean_masks(poly: Poly) -> frozenset:
    """Export a p = 2 squarefree polynomial to macaulay.py's representation."""
    return frozenset(m[0] for m in poly)
