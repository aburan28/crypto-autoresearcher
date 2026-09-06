"""Column space (monomials of degree <= D) and the pre-flight size gate.

Ported from macaulay.py's ``ColumnSpace`` (bitmask monomials, degree masks) and
generalised to the (mask, exps) monomials of :mod:`poly`.  Columns are indexed
in ascending total degree, so the degree-D block occupies the HIGHEST indices;
:mod:`linalg` relies on this to read top_rank and the fall basis off one
elimination.

The pre-flight gate (:func:`preflight`) computes the row and column counts of a
layer from the shape alone -- binomial arithmetic, no allocation -- and raises
:class:`PreflightAbort` above the declared caps, reporting the counts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .poly import Monomial, Poly, Ring


@dataclass(frozen=True)
class ColumnSpace:
    ring: Ring
    max_degree: int
    monomials: Tuple[Monomial, ...]
    index: Mapping[Monomial, int]
    degree_start: Tuple[int, ...]  # degree_start[d] = first column index of degree d
    degree_end: Tuple[int, ...]    # degree_end[d] = one past the last column of degree d

    @classmethod
    def build(cls, ring: Ring, max_degree: int) -> "ColumnSpace":
        monomials: List[Monomial] = []
        starts: List[int] = []
        ends: List[int] = []
        for d in range(max_degree + 1):
            starts.append(len(monomials))
            monomials.extend(ring.monomials_exact(d))
            ends.append(len(monomials))
        index = {m: i for i, m in enumerate(monomials)}
        return cls(ring, max_degree, tuple(monomials), index, tuple(starts), tuple(ends))

    @property
    def ncols(self) -> int:
        return len(self.monomials)

    def ncols_upto(self, degree: int) -> int:
        return self.degree_end[degree]

    def ncols_exact(self, degree: int) -> int:
        return self.degree_end[degree] - self.degree_start[degree]

    def encode(self, poly: Poly) -> Dict[int, int]:
        """Polynomial -> {column index: residue}."""
        out: Dict[int, int] = {}
        for m, c in poly.items():
            try:
                out[self.index[m]] = c
            except KeyError as exc:
                raise ValueError(
                    f"monomial of degree {self.ring.mono_degree(m)} exceeds column-space "
                    f"degree {self.max_degree}"
                ) from exc
        return out

    def decode(self, entries: Mapping[int, int]) -> Poly:
        return {self.monomials[i]: c for i, c in entries.items() if c}

    def top_mask(self, degree: int) -> int:
        """Bitmask of the degree-``degree`` columns (for the p = 2 backend)."""
        lo, hi = self.degree_start[degree], self.degree_end[degree]
        return ((1 << hi) - 1) ^ ((1 << lo) - 1)


class PreflightAbort(RuntimeError):
    """Raised before allocation when a layer exceeds the declared caps."""

    def __init__(self, counts: "PreflightCounts", max_rows: int, max_cols: int) -> None:
        self.counts = counts
        self.max_rows = max_rows
        self.max_cols = max_cols
        super().__init__(
            f"pre-flight abort at degree {counts.degree} ({counts.convention}): "
            f"rows={counts.rows} (cap {max_rows}), cols={counts.cols} (cap {max_cols})"
        )


@dataclass(frozen=True)
class PreflightCounts:
    degree: int
    convention: str
    rows: int          # multiplier rows before zero-product removal (upper bound on kept rows)
    cols: int          # monomials of degree <= D
    cols_top: int      # monomials of degree exactly D
    rows_by_generator_degree: Tuple[Tuple[int, int], ...]  # (generator degree, rows)

    def as_dict(self) -> dict:
        return {
            "degree": self.degree,
            "convention": self.convention,
            "rows": self.rows,
            "cols": self.cols,
            "cols_top": self.cols_top,
            "rows_by_generator_degree": [list(x) for x in self.rows_by_generator_degree],
        }


def multiplier_count(ring: Ring, gen_degree: int, degree: int, convention: str) -> int:
    """Number of multiplier monomials for one generator at layer ``degree``."""
    md = degree - gen_degree
    if md < 0:
        return 0
    if convention == "per_layer":
        return ring.count_monomials_exact(md)
    if convention == "cumulative":
        return ring.count_monomials_upto(md)
    raise ValueError(f"unknown convention {convention!r}")


def preflight(
    ring: Ring,
    generator_degrees: Sequence[int],
    degree: int,
    convention: str,
    max_rows: Optional[int] = None,
    max_cols: Optional[int] = None,
) -> PreflightCounts:
    """Compute layer sizes from the shape alone; abort above caps BEFORE allocating."""
    per_gen: Dict[int, int] = {}
    rows = 0
    for d in generator_degrees:
        if d < 0:
            continue  # zero generator contributes nothing
        c = multiplier_count(ring, d, degree, convention)
        per_gen[d] = per_gen.get(d, 0) + c
        rows += c
    cols = ring.count_monomials_upto(degree)
    cols_top = ring.count_monomials_exact(degree)
    counts = PreflightCounts(
        degree=degree,
        convention=convention,
        rows=rows,
        cols=cols,
        cols_top=cols_top,
        rows_by_generator_degree=tuple(sorted(per_gen.items())),
    )
    if (max_rows is not None and rows > max_rows) or (max_cols is not None and cols > max_cols):
        raise PreflightAbort(counts, max_rows if max_rows is not None else -1,
                             max_cols if max_cols is not None else -1)
    return counts
