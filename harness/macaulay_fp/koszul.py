"""Explicit (first-order) trivial-syzygy counts.

Two trivial-syzygy families are counted by direct combinatorics:

* Koszul pairs  f_j e_i - f_i e_j  for i < j, present once the layer reaches
  degree d_i + d_j; the number of independent multiples at layer D is the number
  of multiplier monomials of degree D - d_i - d_j (per-layer: exactly;
  cumulative: at most).  This is EXP-ALPF-013's ``trivial_koszul(D)`` =
  sum_{i<j} C(n - 1 + D - d_i - d_j, D - d_i - d_j) in ordinary mode, generalised
  to the ring's monomial count.
* Frobenius  f_i^2 = f_i  (p = 2, pure squarefree ring only): one relation per
  generator among multipliers of degree <= d_i, so it is a CUMULATIVE-convention
  object present from D = 2 d_i, with multiples counted by monomials of degree
  <= D - 2 d_i.  It is never counted per-layer (its rows span several multiplier
  degrees) and never for p > 2 or in the presence of a free variable (f^2 = f
  fails there; the counterexample f = a_1 + a_2 at p > 2 is EXP-PFDR-20ee58's
  Stage 0 hand check).

These counts are EXACT only below the first degree at which second syzygies
(relations among the trivial ones, degree d_i + d_j + d_k) appear.  The
series-based allowance ``rows - pred`` of :mod:`series` is the full alternating
count and is what KN-FIND-006 used; :mod:`macaulay` reports deficits against
BOTH and labels them.
"""

from __future__ import annotations

from typing import Optional, Sequence

from .poly import Ring


def koszul_pair_count(ring: Ring, generator_degrees: Sequence[int], degree: int, convention: str) -> int:
    degs = [d for d in generator_degrees if d > 0]
    total = 0
    for i in range(len(degs)):
        for j in range(i + 1, len(degs)):
            md = degree - degs[i] - degs[j]
            if md < 0:
                continue
            if convention == "per_layer":
                total += ring.count_monomials_exact(md)
            elif convention == "cumulative":
                total += ring.count_monomials_upto(md)
            else:
                raise ValueError(f"unknown convention {convention!r}")
    return total


def frobenius_count(ring: Ring, generator_degrees: Sequence[int], degree: int, convention: str,
                    frobenius: Optional[bool] = None) -> int:
    if frobenius is None:
        frobenius = ring.p == 2 and ring.n_free == 0
    if not frobenius or convention != "cumulative":
        return 0
    total = 0
    for d in generator_degrees:
        if d <= 0:
            continue
        md = degree - 2 * d
        if md >= 0:
            total += ring.count_monomials_upto(md)
    return total


def koszul_count(ring: Ring, generator_degrees: Sequence[int], degree: int, convention: str,
                 frobenius: Optional[bool] = None) -> int:
    """Koszul pairs plus (cumulative, p = 2, squarefree) Frobenius relations."""
    return (koszul_pair_count(ring, generator_degrees, degree, convention)
            + frobenius_count(ring, generator_degrees, degree, convention, frobenius))
