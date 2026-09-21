"""Semi-regular (Hilbert-series) rank prediction and degree of regularity.

Quotient-ring series.  The ring of :mod:`poly` has Hilbert series

    R(z) = (1 + z)^{n_sq} / (1 - z)^{n_free}

(squarefree variables contribute 1 + z each, free variables 1/(1 - z) each).

Generator factors.  A generator of degree d contributes

    (1 - z^d)            ordinary semi-regular factor (Froberg / Bardet et al.)
    1 / (1 + z^d)        Boolean semi-regular factor (Bardet-Faugere-Salvy),
                         which additionally accounts for the field-equation
                         syzygy f^2 = f that holds for every polynomial in
                         F_2[a]/(a^2 - a).

IMPORTANT PROVENANCE NOTE.  The EXP-DREG-001 prose (DREG_DEFICIT_CLOSED_FORM.md)
describes ``pred`` as "(1+z)^nb . prod(1 - z^{d_i})", but the archived code
``h012_peel_rank.semireg_rank_pred`` updates ``a[j] -= a[j-d]`` IN PLACE in
increasing j, which is the recurrence for division by (1 + z^d), i.e. it
computes the BOOLEAN series (1+z)^nb / prod(1 + z^{d_i}).  The known-answer
integers of KN-FIND-006 (deficit 1 at D = 3, 31 at D = 4, null 0) are only
reproduced with the Boolean factor -- the trivial-syzygy allowance at D = 4 is
then 12 Frobenius + 66 Koszul = 78, exactly what syzygy_degree4.py verified as
rank(G) = nrows - pred[4].  This module therefore defaults ``frobenius`` to
``True`` exactly when p = 2 and the ring is pure squarefree, and records the
choice in every output; the naive factor is available for comparison.

Truncation (DREG convention, ported): the quotient Hilbert function HF[D] is
read off the series until its first non-positive coefficient; from there on
HF is 0.  D_reg = the first degree with a non-positive coefficient
(EXP-ALPF-013's Froberg D_reg, read by explicit index -- the series.list()
truncation bug noted there cannot occur here because the list is dense).

Predicted ranks:
    graded     pred_graded[D] = #monomials(D) - HF[D]
    cumulative pred_cum[D]    = sum_{j <= D} pred_graded[j]      (DREG's pred[D])
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .poly import Ring


def _ring_series(ring: Ring, dmax: int) -> List[int]:
    a = [ring.count_monomials_exact(d) for d in range(dmax + 1)]
    return a


def _multiply_factor(a: List[int], d: int, frobenius: bool) -> None:
    """In place: a *= (1 - z^d)  or  a /= (1 + z^d) when ``frobenius``."""
    if d <= 0:
        raise ValueError("generator degree must be positive")
    n = len(a)
    if frobenius:
        for j in range(d, n):          # a_new[j] = a_old[j] - a_new[j-d]
            a[j] -= a[j - d]
    else:
        for j in range(n - 1, d - 1, -1):  # a_new[j] = a_old[j] - a_old[j-d]
            a[j] -= a[j - d]


@dataclass(frozen=True)
class SeriesPrediction:
    ring: Ring
    generator_degrees: Tuple[int, ...]
    frobenius: bool
    dmax: int
    raw_coefficients: Tuple[int, ...]   # untruncated series coefficients
    hilbert_function: Tuple[int, ...]   # truncated at first non-positive coefficient
    d_reg: Optional[int]                # first D with raw coefficient <= 0 (None if beyond dmax)
    pred_graded: Tuple[int, ...]
    pred_cumulative: Tuple[int, ...]

    def as_dict(self) -> dict:
        return {
            "frobenius_factor": self.frobenius,
            "generator_degrees": list(self.generator_degrees),
            "dmax": self.dmax,
            "raw_coefficients": list(self.raw_coefficients),
            "hilbert_function": list(self.hilbert_function),
            "d_reg": self.d_reg,
            "pred_graded": list(self.pred_graded),
            "pred_cumulative": list(self.pred_cumulative),
        }


def default_frobenius(ring: Ring) -> bool:
    """Boolean factor applies exactly when every polynomial satisfies f^2 = f."""
    return ring.p == 2 and ring.n_free == 0


def semiregular_prediction(
    ring: Ring,
    generator_degrees: Sequence[int],
    dmax: int,
    frobenius: Optional[bool] = None,
) -> SeriesPrediction:
    if frobenius is None:
        frobenius = default_frobenius(ring)
    degs = tuple(int(d) for d in generator_degrees if d > 0)
    a = _ring_series(ring, dmax)
    for d in degs:
        _multiply_factor(a, d, frobenius)
    raw = tuple(a)
    hf: List[int] = []
    d_reg: Optional[int] = None
    ok = True
    for D in range(dmax + 1):
        if ok and raw[D] > 0:
            hf.append(raw[D])
        else:
            if ok:
                d_reg = D
            ok = False
            hf.append(0)
    pred_graded = tuple(ring.count_monomials_exact(D) - hf[D] for D in range(dmax + 1))
    cum: List[int] = []
    tot = 0
    for D in range(dmax + 1):
        tot += pred_graded[D]
        cum.append(tot)
    return SeriesPrediction(
        ring=ring,
        generator_degrees=degs,
        frobenius=frobenius,
        dmax=dmax,
        raw_coefficients=raw,
        hilbert_function=tuple(hf),
        d_reg=d_reg,
        pred_graded=pred_graded,
        pred_cumulative=tuple(cum),
    )


def growth_of_extra_generator(
    ring: Ring,
    generator_degrees: Sequence[int],
    extra_degree: int,
    dmax: int,
    frobenius: Optional[bool] = None,
) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """Predicted rank increment (graded, cumulative) from appending one more
    generator of degree ``extra_degree`` to the sequence -- the semi-regular
    growth a syzygy born at that degree would show in its multiples."""
    base = semiregular_prediction(ring, generator_degrees, dmax, frobenius)
    ext = semiregular_prediction(ring, tuple(generator_degrees) + (extra_degree,), dmax, base.frobenius)
    graded = tuple(ext.pred_graded[D] - base.pred_graded[D] for D in range(dmax + 1))
    cum = tuple(ext.pred_cumulative[D] - base.pred_cumulative[D] for D in range(dmax + 1))
    return graded, cum
