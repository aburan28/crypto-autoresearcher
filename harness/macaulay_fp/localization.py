"""The leading-form / shrink-test localization bit of EXP-ALPF-013.

At a degree D, partition generators into a declared ROW SUBSET (e.g. the
summation-polynomial rows) and the rest (factor-base rows).  With the
per-layer leading-form matrix phi_D:

    ker(D)       = rows - rank(phi_D)
    nontriv(D)   = ker(D) - trivial(D)
    nontriv_full = nontriv on all generators
    nontriv_fb   = nontriv on the complement of the subset only
    SHRINK       : involves_subset_shrink = nontriv_full > nontriv_fb
    DIRECT       : involves_subset_direct = ker_full > ker_fb

The localization bit is ``nontriv_full - nontriv_fb`` (positive iff some
nontrivial syzygy has support on the subset rows).  ``trivial`` is available
in both readings: EXP-ALPF-013's explicit pairwise Koszul count (``pairwise``)
and the series allowance rows - pred (``series``); both are reported.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from .macaulay import analyze_layer
from .poly import Poly, Ring


@dataclass(frozen=True)
class LocalizationResult:
    degree: int
    convention: str
    leading_forms: bool
    subset: tuple
    n_subset_rows: int
    n_fb_rows: int
    ker_full: int
    ker_fb: int
    nontriv_full_pairwise: int
    nontriv_fb_pairwise: int
    nontriv_full_series: Optional[int]
    nontriv_fb_series: Optional[int]
    involves_subset_direct: bool
    involves_subset_shrink_pairwise: bool
    involves_subset_shrink_series: Optional[bool]

    @property
    def localization_bit_pairwise(self) -> int:
        return self.nontriv_full_pairwise - self.nontriv_fb_pairwise

    @property
    def localization_bit_series(self) -> Optional[int]:
        if self.nontriv_full_series is None or self.nontriv_fb_series is None:
            return None
        return self.nontriv_full_series - self.nontriv_fb_series

    def as_dict(self) -> dict:
        d = dict(self.__dict__)
        d["subset"] = list(self.subset)
        d["localization_bit_pairwise"] = self.localization_bit_pairwise
        d["localization_bit_series"] = self.localization_bit_series
        return d


def localization_gate(
    ring: Ring,
    polys: Sequence[Poly],
    degree: int,
    subset: Sequence[int],
    convention: str = "per_layer",
    leading_forms: bool = True,
    frobenius: Optional[bool] = None,
    max_rows: Optional[int] = None,
    max_cols: Optional[int] = None,
) -> LocalizationResult:
    subset_t = tuple(sorted(set(int(i) for i in subset)))
    for i in subset_t:
        if not 0 <= i < len(polys):
            raise IndexError(f"subset index {i} out of range")
    fb = [i for i in range(len(polys)) if i not in subset_t]
    full = analyze_layer(ring, polys, degree, convention, leading_forms=leading_forms,
                         frobenius=frobenius, max_rows=max_rows, max_cols=max_cols)
    fbl = analyze_layer(ring, polys, degree, convention, leading_forms=leading_forms,
                        frobenius=frobenius, max_rows=max_rows, max_cols=max_cols,
                        generator_subset=fb)
    ker_full = full.syzygy_dim
    ker_fb = fbl.syzygy_dim
    # For per-layer leading forms the nontrivial count is ker - trivial where the
    # rank is the top (= full, forms are homogeneous) rank; use the series top
    # deficit when available, else the pairwise reading only.
    if leading_forms and convention == "per_layer":
        ntf_series = full.top_deficit_series
        nfb_series = fbl.top_deficit_series
    else:
        ntf_series = full.deficit_series
        nfb_series = fbl.deficit_series
    ntf_pair = full.deficit_pairwise
    nfb_pair = fbl.deficit_pairwise
    return LocalizationResult(
        degree=degree,
        convention=convention,
        leading_forms=leading_forms,
        subset=subset_t,
        n_subset_rows=full.row_count - fbl.row_count,
        n_fb_rows=fbl.row_count,
        ker_full=ker_full,
        ker_fb=ker_fb,
        nontriv_full_pairwise=ntf_pair,
        nontriv_fb_pairwise=nfb_pair,
        nontriv_full_series=ntf_series,
        nontriv_fb_series=nfb_series,
        involves_subset_direct=ker_full > ker_fb,
        involves_subset_shrink_pairwise=ntf_pair > nfb_pair,
        involves_subset_shrink_series=(None if ntf_series is None or nfb_series is None
                                       else ntf_series > nfb_series),
    )
