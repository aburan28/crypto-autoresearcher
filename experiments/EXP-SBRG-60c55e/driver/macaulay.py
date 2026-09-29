"""Boolean Macaulay / syzygy instrumentation for Semaev relation systems.

Polynomials are represented as ``frozenset[int]``.  Each integer is the bitmask
of a square-free monomial; membership means coefficient 1 over F_2.  For
example ``{0, 0b001, 0b110}`` is ``1 + x0 + x1*x2``.

The central metric is deliberately linear-algebraic rather than a heuristic
"first fall = degree of regularity" proxy.  At a requested Macaulay degree D we
form rows m*f_i with deg(m)=D-deg(f_i), reduce in the Boolean quotient
x_j^2=x_j, and compare the ranks of:

    H_D : coefficients of degree-exactly-D monomials
    M_D : coefficients of all monomials of degree <= D

Then

    fall_dim(D)    = rank(M_D) - rank(H_D)
    syzygy_dim(D) = nrows - rank(M_D)

``fall_dim`` counts independent row combinations whose top-degree part cancels
but which leave a non-zero lower-degree polynomial. ``syzygy_dim`` counts exact
zero combinations among the same rows.  This identity avoids computing a
nullspace basis and makes the experiment practical for many target points.

These are *instrumentation metrics*, not by themselves a complexity theorem.
They must be compared against matched controls and followed by actual solver
measurements before any ECDLP claim is made.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import random
from typing import Iterable, Mapping, Sequence

Poly = frozenset[int]


def monomial_degree(mask: int) -> int:
    return int(mask).bit_count()


def poly_degree(poly: Poly) -> int:
    if not poly:
        return -1
    return max(monomial_degree(m) for m in poly)


def add_polys(a: Poly, b: Poly) -> Poly:
    """Addition in F_2[x]/(x_i^2-x_i): symmetric difference of supports."""
    return frozenset(set(a).symmetric_difference(b))


def multiply_by_monomial(poly: Poly, multiplier: int) -> Poly:
    """Multiply by a square-free monomial and Boolean-reduce.

    Exponents reduce via x_i^2=x_i, so monomial multiplication is bitwise OR.
    Distinct source terms can collapse to the same reduced monomial and cancel.
    """
    out: set[int] = set()
    for term in poly:
        reduced = term | multiplier
        if reduced in out:
            out.remove(reduced)
        else:
            out.add(reduced)
    return frozenset(out)


def evaluate(poly: Poly, assignment_mask: int) -> int:
    """Evaluate a Boolean polynomial at a bit-mask assignment."""
    acc = 0
    complement = ~assignment_mask
    for monomial in poly:
        acc ^= int((monomial & complement) == 0)
    return acc


def all_monomials_exact(nvars: int, degree: int) -> list[int]:
    if degree < 0 or degree > nvars:
        return []
    if degree == 0:
        return [0]
    out: list[int] = []
    for idxs in combinations(range(nvars), degree):
        mask = 0
        for idx in idxs:
            mask |= 1 << idx
        out.append(mask)
    return out


def all_monomials_upto(nvars: int, degree: int) -> list[int]:
    out: list[int] = []
    for d in range(min(degree, nvars) + 1):
        out.extend(all_monomials_exact(nvars, d))
    return out


@dataclass(frozen=True)
class RankStats:
    rank: int
    xor_count: int
    inserted_rows: int
    zero_rows: int


class GF2Basis:
    """Deterministic sparse-ish row basis using Python integer bitsets."""

    __slots__ = ("pivots", "xor_count", "inserted_rows", "zero_rows")

    def __init__(self, pivots: Mapping[int, int] | None = None) -> None:
        self.pivots: dict[int, int] = dict(pivots or {})
        self.xor_count = 0
        self.inserted_rows = 0
        self.zero_rows = 0

    def clone(self) -> "GF2Basis":
        return GF2Basis(self.pivots)

    @property
    def rank(self) -> int:
        return len(self.pivots)

    def add(self, row: int) -> bool:
        """Insert a row. Return True iff it increases rank."""
        x = int(row)
        while x:
            pivot = x.bit_length() - 1
            basis_row = self.pivots.get(pivot)
            if basis_row is None:
                self.pivots[pivot] = x
                self.inserted_rows += 1
                return True
            x ^= basis_row
            self.xor_count += 1
        self.zero_rows += 1
        return False

    def extend(self, rows: Iterable[int]) -> RankStats:
        start_xor = self.xor_count
        start_inserted = self.inserted_rows
        start_zero = self.zero_rows
        for row in rows:
            self.add(row)
        return RankStats(
            rank=self.rank,
            xor_count=self.xor_count - start_xor,
            inserted_rows=self.inserted_rows - start_inserted,
            zero_rows=self.zero_rows - start_zero,
        )


def gf2_rank(rows: Iterable[int]) -> RankStats:
    basis = GF2Basis()
    basis.extend(rows)
    return RankStats(
        rank=basis.rank,
        xor_count=basis.xor_count,
        inserted_rows=basis.inserted_rows,
        zero_rows=basis.zero_rows,
    )


@dataclass(frozen=True)
class ColumnSpace:
    nvars: int
    max_degree: int
    monomials: tuple[int, ...]
    index: Mapping[int, int]
    degree_masks: Mapping[int, int]

    @classmethod
    def build(cls, nvars: int, max_degree: int) -> "ColumnSpace":
        monomials = tuple(all_monomials_upto(nvars, max_degree))
        index = {m: i for i, m in enumerate(monomials)}
        degree_masks: dict[int, int] = {}
        for i, m in enumerate(monomials):
            degree_masks.setdefault(monomial_degree(m), 0)
            degree_masks[monomial_degree(m)] |= 1 << i
        return cls(nvars, max_degree, monomials, index, degree_masks)

    def encode(self, poly: Poly) -> int:
        row = 0
        for m in poly:
            try:
                idx = self.index[m]
            except KeyError as exc:
                raise ValueError(
                    f"monomial degree {monomial_degree(m)} exceeds column-space "
                    f"degree {self.max_degree}"
                ) from exc
            row ^= 1 << idx
        return row

    def degree_projection(self, row: int, degree: int) -> int:
        return row & self.degree_masks.get(degree, 0)


@dataclass(frozen=True)
class MacaulayLayer:
    degree: int
    row_count: int
    top_rank: int
    full_rank: int
    fall_dim: int
    syzygy_dim: int
    zero_product_rows: int
    nnz_total: int
    nnz_top: int
    row_density: float
    top_density: float
    full_xor_count: int
    top_xor_count: int

    def as_dict(self) -> dict[str, int | float]:
        return {
            "degree": self.degree,
            "row_count": self.row_count,
            "top_rank": self.top_rank,
            "full_rank": self.full_rank,
            "fall_dim": self.fall_dim,
            "syzygy_dim": self.syzygy_dim,
            "zero_product_rows": self.zero_product_rows,
            "nnz_total": self.nnz_total,
            "nnz_top": self.nnz_top,
            "row_density": self.row_density,
            "top_density": self.top_density,
            "full_xor_count": self.full_xor_count,
            "top_xor_count": self.top_xor_count,
        }


def layer_rows(polys: Sequence[Poly], nvars: int, degree: int) -> list[Poly]:
    """Return the degree-D Boolean Macaulay layer."""
    rows: list[Poly] = []
    multiplier_cache: dict[int, list[int]] = {}
    for poly in polys:
        d = poly_degree(poly)
        if d < 0 or d > degree:
            continue
        md = degree - d
        multipliers = multiplier_cache.get(md)
        if multipliers is None:
            multipliers = all_monomials_exact(nvars, md)
            multiplier_cache[md] = multipliers
        for multiplier in multipliers:
            rows.append(multiply_by_monomial(poly, multiplier))
    return rows


def analyze_layer(
    polys: Sequence[Poly],
    nvars: int,
    degree: int,
    columns: ColumnSpace | None = None,
) -> MacaulayLayer:
    columns = columns or ColumnSpace.build(nvars, degree)
    if columns.nvars != nvars or columns.max_degree < degree:
        raise ValueError("column space incompatible with requested layer")

    prows = layer_rows(polys, nvars, degree)
    rows = [columns.encode(p) for p in prows]
    top_rows = [columns.degree_projection(r, degree) for r in rows]

    full = gf2_rank(rows)
    top = gf2_rank(top_rows)
    row_count = len(rows)
    zero_products = sum(1 for p in prows if not p)
    nnz_total = sum(r.bit_count() for r in rows)
    nnz_top = sum(r.bit_count() for r in top_rows)
    ncols_full = len(columns.monomials)
    ncols_top = len(all_monomials_exact(nvars, degree))

    return MacaulayLayer(
        degree=degree,
        row_count=row_count,
        top_rank=top.rank,
        full_rank=full.rank,
        fall_dim=full.rank - top.rank,
        syzygy_dim=row_count - full.rank,
        zero_product_rows=zero_products,
        nnz_total=nnz_total,
        nnz_top=nnz_top,
        row_density=(nnz_total / (row_count * ncols_full)) if row_count and ncols_full else 0.0,
        top_density=(nnz_top / (row_count * ncols_top)) if row_count and ncols_top else 0.0,
        full_xor_count=full.xor_count,
        top_xor_count=top.xor_count,
    )


def analyze_degrees(
    polys: Sequence[Poly], nvars: int, min_degree: int, max_degree: int
) -> list[MacaulayLayer]:
    columns = ColumnSpace.build(nvars, max_degree)
    return [
        analyze_layer(polys, nvars, d, columns)
        for d in range(min_degree, max_degree + 1)
    ]


def degree_histogram(poly: Poly) -> dict[int, int]:
    hist: dict[int, int] = {}
    for monomial in poly:
        d = monomial_degree(monomial)
        hist[d] = hist.get(d, 0) + 1
    return hist


def _sample_histogram_support(
    histogram: Mapping[int, int], nvars: int, rng: random.Random
) -> set[int]:
    selected: set[int] = set()
    for degree, count in sorted(histogram.items()):
        candidates = all_monomials_exact(nvars, degree)
        if count > len(candidates):
            raise ValueError(
                f"cannot sample {count} distinct degree-{degree} monomials "
                f"from {len(candidates)} candidates"
            )
        selected.update(rng.sample(candidates, count))
    return selected


def random_matched_polynomial(
    template: Poly,
    nvars: int,
    rng: random.Random,
    planted_assignment: int | None = None,
) -> tuple[Poly, bool]:
    """Generate a degree-histogram-matched random Boolean polynomial."""
    hist = degree_histogram(template)
    selected = _sample_histogram_support(hist, nvars, rng)
    exact_histogram = True

    if planted_assignment is not None:
        poly = frozenset(selected)
        if evaluate(poly, planted_assignment):
            swapped = False
            degrees = list(hist)
            rng.shuffle(degrees)
            for degree in degrees:
                selected_d = [m for m in selected if monomial_degree(m) == degree]
                rng.shuffle(selected_d)
                candidates = all_monomials_exact(nvars, degree)
                rng.shuffle(candidates)
                for old in selected_d:
                    old_value = int((old & ~planted_assignment) == 0)
                    for new in candidates:
                        if new in selected:
                            continue
                        new_value = int((new & ~planted_assignment) == 0)
                        if new_value != old_value:
                            selected.remove(old)
                            selected.add(new)
                            swapped = True
                            break
                    if swapped:
                        break
                if swapped:
                    break
            if not swapped:
                if 0 in selected:
                    selected.remove(0)
                else:
                    selected.add(0)
                exact_histogram = False

    result = frozenset(selected)
    if planted_assignment is not None and evaluate(result, planted_assignment):
        raise AssertionError("failed to plant requested Boolean root")
    return result, exact_histogram


def random_matched_system(
    templates: Sequence[Poly],
    nvars: int,
    seed: int,
    planted_assignment: int | None = None,
) -> tuple[list[Poly], dict[str, int | bool]]:
    rng = random.Random(seed)
    polys: list[Poly] = []
    exact = True
    for template in templates:
        p, this_exact = random_matched_polynomial(
            template, nvars, rng, planted_assignment=planted_assignment
        )
        polys.append(p)
        exact = exact and this_exact
    return polys, {
        "seed": seed,
        "planted": planted_assignment is not None,
        "degree_histogram_exact": exact,
    }


@dataclass(frozen=True)
class BatchTargetStats:
    target_index: int
    fixed_rank: int
    target_rank: int
    total_rank: int
    rowspace_intersection_dim: int
    baseline_xors: int
    incremental_xors: int
    target_rows: int

    def as_dict(self) -> dict[str, int]:
        return {
            "target_index": self.target_index,
            "fixed_rank": self.fixed_rank,
            "target_rank": self.target_rank,
            "total_rank": self.total_rank,
            "rowspace_intersection_dim": self.rowspace_intersection_dim,
            "baseline_xors": self.baseline_xors,
            "incremental_xors": self.incremental_xors,
            "target_rows": self.target_rows,
        }


@dataclass(frozen=True)
class BatchStats:
    degree: int
    fixed_rows: int
    fixed_rank: int
    fixed_precompute_xors: int
    targets: tuple[BatchTargetStats, ...]
    baseline_total_xors: int
    batched_total_xors: int
    xor_speedup: float

    def as_dict(self) -> dict[str, object]:
        return {
            "degree": self.degree,
            "fixed_rows": self.fixed_rows,
            "fixed_rank": self.fixed_rank,
            "fixed_precompute_xors": self.fixed_precompute_xors,
            "targets": [t.as_dict() for t in self.targets],
            "baseline_total_xors": self.baseline_total_xors,
            "batched_total_xors": self.batched_total_xors,
            "xor_speedup": self.xor_speedup,
        }


def _encode_layer_rows(
    polys: Sequence[Poly], nvars: int, degree: int, columns: ColumnSpace
) -> list[int]:
    return [columns.encode(p) for p in layer_rows(polys, nvars, degree)]


def analyze_batch_reuse(
    fixed_polys: Sequence[Poly],
    target_poly_sets: Sequence[Sequence[Poly]],
    nvars: int,
    degree: int,
) -> BatchStats:
    """Measure exact row-space reuse across many target specializations."""
    columns = ColumnSpace.build(nvars, degree)
    fixed_rows = _encode_layer_rows(fixed_polys, nvars, degree, columns)

    fixed_basis = GF2Basis()
    fixed_basis.extend(fixed_rows)
    fixed_xors = fixed_basis.xor_count

    target_stats: list[BatchTargetStats] = []
    baseline_total_xors = 0
    incremental_total_xors = 0

    for target_index, target_polys in enumerate(target_poly_sets):
        target_rows = _encode_layer_rows(target_polys, nvars, degree, columns)

        target_only = GF2Basis()
        target_only.extend(target_rows)

        baseline = GF2Basis()
        baseline.extend(fixed_rows)
        baseline.extend(target_rows)
        baseline_total_xors += baseline.xor_count

        incremental = fixed_basis.clone()
        incremental.extend(target_rows)
        incremental_xors = incremental.xor_count
        incremental_total_xors += incremental_xors

        total_rank = incremental.rank
        intersection = fixed_basis.rank + target_only.rank - total_rank
        if intersection < 0:
            raise AssertionError("row-space intersection dimension became negative")

        target_stats.append(
            BatchTargetStats(
                target_index=target_index,
                fixed_rank=fixed_basis.rank,
                target_rank=target_only.rank,
                total_rank=total_rank,
                rowspace_intersection_dim=intersection,
                baseline_xors=baseline.xor_count,
                incremental_xors=incremental_xors,
                target_rows=len(target_rows),
            )
        )

    batched_total_xors = fixed_xors + incremental_total_xors
    xor_speedup = (
        baseline_total_xors / batched_total_xors
        if batched_total_xors
        else (float("inf") if baseline_total_xors else 1.0)
    )

    return BatchStats(
        degree=degree,
        fixed_rows=len(fixed_rows),
        fixed_rank=fixed_basis.rank,
        fixed_precompute_xors=fixed_xors,
        targets=tuple(target_stats),
        baseline_total_xors=baseline_total_xors,
        batched_total_xors=batched_total_xors,
        xor_speedup=xor_speedup,
    )


def first_nonzero_fall(layers: Sequence[MacaulayLayer]) -> int | None:
    for layer in layers:
        if layer.fall_dim > 0:
            return layer.degree
    return None


def first_excess_fall(
    real_layers: Sequence[MacaulayLayer], control_layers: Sequence[MacaulayLayer]
) -> int | None:
    by_degree = {layer.degree: layer for layer in control_layers}
    for real in real_layers:
        control = by_degree.get(real.degree)
        if control is not None and real.fall_dim > control.fall_dim:
            return real.degree
    return None
