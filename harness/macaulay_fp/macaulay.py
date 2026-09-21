"""F_p Macaulay deficit meter: layers, rank profile, falls, syzygies, deficits.

Port of ``experiments/EXP-SBRG-60c55e/driver/macaulay.py`` (Boolean, p = 2,
per-layer multipliers) to F_p with three ring modes and two multiplier
conventions.  Field-generic: p = 2 reproduces the Boolean meter exactly.

Conventions (recorded in every :class:`LayerResult`):

PER-LAYER   rows m * f_i with deg m = D - deg f_i EXACTLY (macaulay.py).
            Zero-product rows are KEPT in row_count (macaulay.py counts them,
            so syzygy_dim includes them; ``zero_product_rows`` reports how many).
CUMULATIVE  rows m * f_i with deg m <= D - deg f_i (EXP-DREG-001's
            ``macaulay_rows``, the convention behind KN-FIND-006).  Zero-product
            rows are DROPPED (DREG's ``if prod``); ``zero_product_rows`` reports
            how many were dropped.

Degree of a row.  A row is the REDUCED product (a^2 -> a); its degree is the
degree after reduction, which can be lower than deg m + deg f_i when squarefree
monomials collapse.  Such rows are kept (they are falls in the Boolean meter's
sense).  The top-degree projection of a layer at D is the restriction to the
columns of TOTAL degree exactly D (squarefree count plus free exponents); in
mixed mode the total degree is the grading, so u^2 * a_1 * a_2 has degree 4.

Metrics per layer (all exact integers):
    row_count, zero_product_rows, ncols_full (deg <= D), ncols_top (deg = D)
    top_rank    = rank of the degree-D projection
    full_rank   = rank of the whole layer
    fall_dim    = full_rank - top_rank   (macaulay.py)
    syzygy_dim  = row_count - full_rank  (macaulay.py)
    koszul_pairwise  = explicit first-order trivial count (:mod:`koszul`)
    pred_rank        = series-predicted rank (graded for per-layer leading forms,
                       cumulative for the cumulative convention)
    koszul_series    = row_count - zero_product_rows - pred_rank  (DREG's trivial allowance)
    deficit_series   = pred_rank - rank   (KN-FIND-006's deficit; rank = full_rank)
    deficit_pairwise = syzygy_dim - koszul_pairwise
    top_deficit_series = pred_graded - top_rank  (per-layer: EXP-ALPF-013's
                       nontrivial(D) on the leading forms)

The graded (per-degree) DREG deficit is ``deficit_series(D) - deficit_series(D-1)``
under the cumulative convention; :func:`deficit_profile` reports it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .columns import ColumnSpace, PreflightCounts, preflight
from .koszul import koszul_count
from .linalg import Echelon, project_top, rank_of
from .poly import Monomial, Poly, Ring
from .series import SeriesPrediction, default_frobenius, semiregular_prediction

CONVENTIONS = ("per_layer", "cumulative")


@dataclass(frozen=True)
class RowProvenance:
    generator: int
    multiplier: Monomial


@dataclass(frozen=True)
class LayerResult:
    degree: int
    convention: str
    mode: str
    p: int
    leading_forms: bool
    frobenius_factor: bool
    row_count: int
    zero_product_rows: int
    ncols_full: int
    ncols_top: int
    top_rank: int
    full_rank: int
    fall_dim: int
    syzygy_dim: int
    koszul_pairwise: int
    pred_rank: Optional[int]
    koszul_series: Optional[int]
    deficit_series: Optional[int]
    deficit_pairwise: int
    top_deficit_series: Optional[int]
    nnz_total: int
    nnz_top: int
    reduction_ops: int
    preflight: PreflightCounts
    fall_basis: Optional[Tuple[Poly, ...]] = None
    provenance: Optional[Tuple[RowProvenance, ...]] = None

    def as_dict(self) -> dict:
        return {
            "degree": self.degree,
            "convention": self.convention,
            "mode": self.mode,
            "p": self.p,
            "leading_forms": self.leading_forms,
            "frobenius_factor": self.frobenius_factor,
            "row_count": self.row_count,
            "zero_product_rows": self.zero_product_rows,
            "ncols_full": self.ncols_full,
            "ncols_top": self.ncols_top,
            "top_rank": self.top_rank,
            "full_rank": self.full_rank,
            "fall_dim": self.fall_dim,
            "syzygy_dim": self.syzygy_dim,
            "koszul_pairwise": self.koszul_pairwise,
            "pred_rank": self.pred_rank,
            "koszul_series": self.koszul_series,
            "deficit_series": self.deficit_series,
            "deficit_pairwise": self.deficit_pairwise,
            "top_deficit_series": self.top_deficit_series,
            "nnz_total": self.nnz_total,
            "nnz_top": self.nnz_top,
            "reduction_ops": self.reduction_ops,
            "preflight": self.preflight.as_dict(),
        }


def generator_degrees(ring: Ring, polys: Sequence[Poly]) -> List[int]:
    return [ring.degree(f) for f in polys]


def layer_rows(
    ring: Ring,
    polys: Sequence[Poly],
    degree: int,
    convention: str = "per_layer",
    leading_forms: bool = False,
    keep_zero_rows: Optional[bool] = None,
    generator_subset: Optional[Sequence[int]] = None,
) -> Tuple[List[Poly], List[RowProvenance], int]:
    """Return (rows, provenance, zero_product_count) for the layer at ``degree``."""
    if convention not in CONVENTIONS:
        raise ValueError(f"convention must be one of {CONVENTIONS}")
    if keep_zero_rows is None:
        keep_zero_rows = convention == "per_layer"
    rows: List[Poly] = []
    prov: List[RowProvenance] = []
    zero_products = 0
    cache: Dict[int, List[Monomial]] = {}
    indices = range(len(polys)) if generator_subset is None else list(generator_subset)
    for gi in indices:
        f = polys[gi]
        if leading_forms:
            f = ring.top_form(f)
        d = ring.degree(f)
        if d < 0 or d > degree:
            continue
        md = degree - d
        if convention == "per_layer":
            mults = cache.get(md)
            if mults is None:
                mults = ring.monomials_exact(md)
                cache[md] = mults
        else:
            mults = cache.get(-md - 1)
            if mults is None:
                mults = ring.monomials_upto(md)
                cache[-md - 1] = mults
        for m in mults:
            prod = ring.mul_monomial(f, m)
            if not prod:
                zero_products += 1
                if not keep_zero_rows:
                    continue
            rows.append(prod)
            prov.append(RowProvenance(gi, m))
    return rows, prov, zero_products


def analyze_layer(
    ring: Ring,
    polys: Sequence[Poly],
    degree: int,
    convention: str = "per_layer",
    columns: Optional[ColumnSpace] = None,
    leading_forms: bool = False,
    frobenius: Optional[bool] = None,
    prediction: Optional[SeriesPrediction] = None,
    max_rows: Optional[int] = None,
    max_cols: Optional[int] = None,
    want_fall_basis: bool = False,
    want_provenance: bool = False,
    generator_subset: Optional[Sequence[int]] = None,
    keep_zero_rows: Optional[bool] = None,
) -> LayerResult:
    """Analyse one Macaulay layer.  Pre-flights sizes before any allocation."""
    if convention not in CONVENTIONS:
        raise ValueError(f"convention must be one of {CONVENTIONS}")
    if frobenius is None:
        frobenius = default_frobenius(ring)
    sub = list(range(len(polys))) if generator_subset is None else list(generator_subset)
    used = [polys[i] for i in sub]
    if leading_forms:
        used = [ring.top_form(f) for f in used]
    degs = generator_degrees(ring, used)
    pf = preflight(ring, degs, degree, convention, max_rows=max_rows, max_cols=max_cols)

    columns = columns or ColumnSpace.build(ring, degree)
    if columns.ring != ring or columns.max_degree < degree:
        raise ValueError("column space incompatible with requested layer")

    prows, prov, zero_products = layer_rows(
        ring, polys, degree, convention, leading_forms,
        keep_zero_rows=keep_zero_rows, generator_subset=generator_subset,
    )
    top_start = columns.degree_start[degree]
    ech = Echelon(ring.p, top_start=top_start)
    nnz_total = 0
    nnz_top = 0
    for poly in prows:
        entries = columns.encode(poly)
        nnz_total += len(entries)
        nnz_top += sum(1 for c in entries if c >= top_start)
        ech.add(ech.encode(entries))
    full_rank = ech.rank
    top_rank = ech.top_rank()
    row_count = len(prows)
    fall_dim = full_rank - top_rank
    syzygy_dim = row_count - full_rank

    kz = koszul_count(ring, degs, degree, convention, frobenius)
    pred_rank: Optional[int] = None
    top_deficit: Optional[int] = None
    if prediction is None:
        prediction = semiregular_prediction(ring, degs, degree, frobenius)
    if prediction.dmax >= degree:
        if convention == "cumulative":
            pred_rank = prediction.pred_cumulative[degree]
        else:
            pred_rank = prediction.pred_graded[degree]
        top_deficit = prediction.pred_graded[degree] - top_rank
    nonzero_rows = row_count - (zero_products if (keep_zero_rows if keep_zero_rows is not None else convention == "per_layer") else 0)
    koszul_series = None if pred_rank is None else nonzero_rows - pred_rank
    deficit_series = None if pred_rank is None else pred_rank - full_rank

    fall_basis = None
    if want_fall_basis:
        fall_basis = tuple(columns.decode(_row_entries(ring.p, r)) for r in ech.fall_rows())

    return LayerResult(
        degree=degree,
        convention=convention,
        mode=ring.mode,
        p=ring.p,
        leading_forms=leading_forms,
        frobenius_factor=frobenius,
        row_count=row_count,
        zero_product_rows=zero_products,
        ncols_full=columns.ncols_upto(degree),
        ncols_top=columns.ncols_exact(degree),
        top_rank=top_rank,
        full_rank=full_rank,
        fall_dim=fall_dim,
        syzygy_dim=syzygy_dim,
        koszul_pairwise=kz,
        pred_rank=pred_rank,
        koszul_series=koszul_series,
        deficit_series=deficit_series,
        deficit_pairwise=syzygy_dim - kz,
        top_deficit_series=top_deficit,
        nnz_total=nnz_total,
        nnz_top=nnz_top,
        reduction_ops=ech.stats.reduction_ops,
        preflight=pf,
        fall_basis=fall_basis,
        provenance=tuple(prov) if want_provenance else None,
    )


def _row_entries(p: int, row) -> Dict[int, int]:
    from .linalg import row_to_dict
    return row_to_dict(p, row)


def analyze_degrees(
    ring: Ring,
    polys: Sequence[Poly],
    min_degree: int,
    max_degree: int,
    convention: str = "per_layer",
    leading_forms: bool = False,
    frobenius: Optional[bool] = None,
    max_rows: Optional[int] = None,
    max_cols: Optional[int] = None,
    want_fall_basis: bool = False,
) -> List[LayerResult]:
    """Analyse degrees min..max with one shared column space and one prediction."""
    columns = ColumnSpace.build(ring, max_degree)
    if frobenius is None:
        frobenius = default_frobenius(ring)
    used = [ring.top_form(f) for f in polys] if leading_forms else list(polys)
    prediction = semiregular_prediction(ring, generator_degrees(ring, used), max_degree, frobenius)
    return [
        analyze_layer(
            ring, polys, d, convention, columns, leading_forms, frobenius, prediction,
            max_rows=max_rows, max_cols=max_cols, want_fall_basis=want_fall_basis,
        )
        for d in range(min_degree, max_degree + 1)
    ]


@dataclass(frozen=True)
class DeficitProfile:
    convention: str
    frobenius_factor: bool
    degrees: Tuple[int, ...]
    rows: Tuple[int, ...]
    cols: Tuple[int, ...]
    rank: Tuple[int, ...]
    pred: Tuple[int, ...]
    koszul_pairwise: Tuple[int, ...]
    koszul_series: Tuple[int, ...]
    deficit_cumulative: Tuple[int, ...]   # pred - rank (KN-FIND-006's def_cum)
    deficit_graded: Tuple[int, ...]       # def_cum(D) - def_cum(D-1) (KN-FIND-006's per-degree deficit)
    deficit_pairwise: Tuple[int, ...]     # rows - rank - koszul_pairwise
    fall_dim: Tuple[int, ...]
    syzygy_dim: Tuple[int, ...]

    def as_dict(self) -> dict:
        return {k: (list(v) if isinstance(v, tuple) else v) for k, v in self.__dict__.items()}


def deficit_profile(layers: Sequence[LayerResult]) -> DeficitProfile:
    """Degree-resolved deficit table in the style of EXP-DREG-001 deficit_by_degree.py.

    Under the cumulative convention ``deficit_cumulative`` is DREG's ``def_cum``
    and ``deficit_graded`` its per-degree increment (the quantities KN-FIND-006
    reports as 1 at D = 3 and 31 at D = 4).  Under the per-layer convention the
    same fields are computed from the graded prediction and are the leading-
    form / top-degree readings; the ``convention`` field says which.
    """
    if not layers:
        raise ValueError("no layers")
    conv = layers[0].convention
    if any(l.convention != conv for l in layers):
        raise ValueError("mixed conventions in one profile")
    degs = tuple(l.degree for l in layers)
    if any(l.pred_rank is None for l in layers):
        raise ValueError("series prediction missing for some layer")
    defcum = tuple(l.deficit_series for l in layers)  # type: ignore[arg-type]
    graded: List[int] = []
    prev = 0
    for l in layers:
        cur = l.deficit_series  # type: ignore[assignment]
        graded.append(cur - prev)  # type: ignore[operator]
        prev = cur  # type: ignore[assignment]
    return DeficitProfile(
        convention=conv,
        frobenius_factor=layers[0].frobenius_factor,
        degrees=degs,
        rows=tuple(l.row_count for l in layers),
        cols=tuple(l.ncols_full for l in layers),
        rank=tuple(l.full_rank for l in layers),
        pred=tuple(l.pred_rank for l in layers),  # type: ignore[arg-type]
        koszul_pairwise=tuple(l.koszul_pairwise for l in layers),
        koszul_series=tuple(l.koszul_series for l in layers),  # type: ignore[arg-type]
        deficit_cumulative=defcum,
        deficit_graded=tuple(graded),
        deficit_pairwise=tuple(l.deficit_pairwise for l in layers),
        fall_dim=tuple(l.fall_dim for l in layers),
        syzygy_dim=tuple(l.syzygy_dim for l in layers),
    )


def first_nonzero_fall(layers: Sequence[LayerResult]) -> Optional[int]:
    for layer in layers:
        if layer.fall_dim > 0:
            return layer.degree
    return None


def first_excess_fall(real_layers: Sequence[LayerResult], control_layers: Sequence[LayerResult]) -> Optional[int]:
    by_degree = {layer.degree: layer for layer in control_layers}
    for real in real_layers:
        control = by_degree.get(real.degree)
        if control is not None and real.fall_dim > control.fall_dim:
            return real.degree
    return None


def first_nontrivial_syzygy(layers: Sequence[LayerResult], against: str = "series") -> Optional[int]:
    """EXP-ALPF-013's d_ff: first degree with a nontrivial (non-Koszul) syzygy.

    ``against='series'`` uses ``top_deficit_series`` for per-layer leading-form
    layers (ker - trivial with the full alternating count) and ``deficit_series``
    otherwise; ``against='pairwise'`` uses ``deficit_pairwise``.
    """
    for layer in layers:
        if against == "pairwise":
            v = layer.deficit_pairwise
        elif layer.leading_forms and layer.convention == "per_layer":
            v = layer.top_deficit_series
        else:
            v = layer.deficit_series
        if v is not None and v > 0:
            return layer.degree
    return None


def verify_layer_two_eliminations(ring: Ring, polys: Sequence[Poly], degree: int,
                                  convention: str = "per_layer", leading_forms: bool = False) -> Tuple[int, int]:
    """Independent route (macaulay.py's): rank(M_D) and rank(H_D) by two eliminations."""
    columns = ColumnSpace.build(ring, degree)
    prows, _, _ = layer_rows(ring, polys, degree, convention, leading_forms)
    top_start = columns.degree_start[degree]
    top_mask = columns.top_mask(degree)
    e = Echelon(ring.p)
    rows = [e.encode(columns.encode(pr)) for pr in prows]
    full = rank_of(ring.p, rows)
    top = rank_of(ring.p, [project_top(ring.p, r, top_mask, top_start) for r in rows])
    return full, top


def fall_content_contains(ring: Ring, layer: LayerResult, columns: ColumnSpace, h: Poly) -> bool:
    """Is ``h`` (of degree < layer.degree) in the fall space of ``layer``?"""
    if layer.fall_basis is None:
        raise ValueError("layer was analysed without want_fall_basis=True")
    if ring.degree(h) >= layer.degree:
        return False
    e = Echelon(ring.p)
    for b in layer.fall_basis:
        e.add(e.encode(columns.encode(b)))
    return e.contains(e.encode(columns.encode(h)))
