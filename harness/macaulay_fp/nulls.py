"""Null generators, all driven by a seeded ``random.Random`` (deterministic).

1. HISTOGRAM-MATCHED (macaulay.py's ``random_matched_polynomial`` carried to
   F_p): for each generator, draw the same number of DISTINCT monomials at each
   total degree as the template has, uniformly from the ring's monomials of that
   degree, with coefficients uniform in [1, p-1].  At p = 2 the coefficients are
   all 1 and the object is EXP-DREG-001's ``boolean_null`` / KN-FIND-006's
   "support-matched null" (that record's term for this construction).
   Optional planted root: for p > 2 one coefficient is corrected so the
   polynomial vanishes at the point (support and histogram unchanged); for
   p = 2 macaulay.py's monomial-swap procedure is ported verbatim (histogram
   kept unless the constant term must be toggled, reported as
   ``degree_histogram_exact``).

2. SUPPORT-MATCHED (identical support): the template's monomials with fresh
   coefficients uniform in [1, p-1].  At p = 2 this is the IDENTITY map; the
   result carries ``degenerate_at_p2 = True`` so a caller never mistakes it for
   a control.

3. BLOCK-FACTORED (H-PFDR-4148b8 / IDEA-20260903-e1e38b): prod_k q_k with q_k a
   uniformly random form of declared degree e_k in the variables of block k
   (coefficients uniform in F_p, zero allowed, so "uniformly random form";
   ``nonzero_coefficients=True`` restricts to [1, p-1]).  Blocks are declared as
   lists of squarefree-variable indices; free variables may be included by
   negative index -(j+1).

4. COEFFICIENT SCRAMBLE (curve / target scramble primitive): re-draw the
   coefficients of the monomials selected by a caller predicate uniformly in
   [1, p-1] (or in F_p including 0 with ``allow_zero``).  Which monomials carry
   the curve constants or the target is a builder-level fact; the meter only
   supplies the primitive and records the selected monomials.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .poly import Monomial, Poly, Ring


@dataclass(frozen=True)
class NullMeta:
    kind: str
    seed: Optional[int]
    p: int
    degree_histogram_exact: bool = True
    planted: bool = False
    degenerate_at_p2: bool = False
    notes: Tuple[str, ...] = ()

    def as_dict(self) -> dict:
        d = dict(self.__dict__)
        d["notes"] = list(self.notes)
        return d


def _nonzero(rng: random.Random, p: int) -> int:
    return rng.randrange(1, p) if p > 2 else 1


def _sample_histogram_support(ring: Ring, histogram: Dict[int, int], rng: random.Random) -> List[Monomial]:
    selected: List[Monomial] = []
    for degree, count in sorted(histogram.items()):
        candidates = ring.monomials_exact(degree)
        if count > len(candidates):
            raise ValueError(
                f"cannot sample {count} distinct degree-{degree} monomials from {len(candidates)} candidates"
            )
        selected.extend(rng.sample(candidates, count))
    return selected


def _point_value_of_monomial(ring: Ring, m: Monomial, sq_values: Sequence[int], free_values: Sequence[int]) -> int:
    return ring.evaluate({m: 1}, sq_values, free_values)


def histogram_matched_polynomial(
    ring: Ring,
    template: Poly,
    rng: random.Random,
    planted_point: Optional[Tuple[Sequence[int], Sequence[int]]] = None,
) -> Tuple[Poly, bool]:
    """Degree-histogram-matched random polynomial; returns (poly, histogram_exact)."""
    hist = ring.degree_histogram(template)
    support = _sample_histogram_support(ring, hist, rng)
    poly: Poly = {m: _nonzero(rng, ring.p) for m in support}
    exact = True
    if planted_point is None:
        return poly, exact
    sq_vals, free_vals = planted_point
    value = ring.evaluate(poly, sq_vals, free_vals)
    if value == 0:
        return poly, exact
    p = ring.p
    if p > 2:
        # Correct one coefficient on a monomial that is nonzero at the point.
        order = list(poly)
        rng.shuffle(order)
        for m in order:
            mv = _point_value_of_monomial(ring, m, sq_vals, free_vals)
            if mv == 0:
                continue
            new_c = (poly[m] - value * pow(mv, -1, p)) % p
            if new_c != 0:
                poly[m] = new_c
                break
        else:
            # Every candidate would need coefficient 0: toggle the constant (rare).
            one = ring.one()
            poly[one] = (poly.get(one, 0) - value) % p
            if poly[one] == 0:
                del poly[one]
            exact = False
    else:
        # macaulay.py's swap procedure at p = 2 (monomials are bitmasks; value = 1).
        selected = set(poly)
        swapped = False
        degrees = list(hist)
        rng.shuffle(degrees)
        for degree in degrees:
            selected_d = [m for m in selected if ring.mono_degree(m) == degree]
            rng.shuffle(selected_d)
            candidates = ring.monomials_exact(degree)
            rng.shuffle(candidates)
            for old in selected_d:
                old_value = _point_value_of_monomial(ring, old, sq_vals, free_vals)
                for new in candidates:
                    if new in selected:
                        continue
                    new_value = _point_value_of_monomial(ring, new, sq_vals, free_vals)
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
            one = ring.one()
            if one in selected:
                selected.remove(one)
            else:
                selected.add(one)
            exact = False
        poly = {m: 1 for m in selected}
    if ring.evaluate(poly, sq_vals, free_vals) != 0:
        raise AssertionError("failed to plant requested root")
    return poly, exact


def histogram_matched_system(
    ring: Ring,
    templates: Sequence[Poly],
    seed: int,
    planted_point: Optional[Tuple[Sequence[int], Sequence[int]]] = None,
) -> Tuple[List[Poly], NullMeta]:
    rng = random.Random(seed)
    polys: List[Poly] = []
    exact = True
    for t in templates:
        q, e = histogram_matched_polynomial(ring, t, rng, planted_point)
        polys.append(q)
        exact = exact and e
    return polys, NullMeta("histogram_matched", seed, ring.p, degree_histogram_exact=exact,
                           planted=planted_point is not None)


def dreg_boolean_null(ring: Ring, templates: Sequence[Poly], rng: random.Random) -> List[Poly]:
    """EXP-DREG-001's ``boolean_null`` ported verbatim (p = 2, squarefree): same
    RNG call sequence (``rng.sample(range(nb), d)`` until ``cnt`` distinct), so
    a caller holding the builder's RNG state reproduces the archived null."""
    if ring.p != 2 or ring.n_free != 0:
        raise ValueError("dreg_boolean_null is a p = 2 squarefree construction")
    nb = ring.n_sq
    null: List[Poly] = []
    for f in templates:
        by_deg: Dict[int, int] = {}
        for m in f:
            d = ring.mono_degree(m)
            by_deg[d] = by_deg.get(d, 0) + 1
        nf: Dict[Monomial, int] = {}
        for d, cnt in by_deg.items():
            seen = set()
            while len(seen) < cnt:
                idxs = rng.sample(range(nb), d)
                mask = 0
                for i in idxs:
                    mask |= 1 << i
                mm = (mask, ())
                if mm not in nf:
                    seen.add(mm)
                    nf[mm] = 1
        null.append(nf)
    return null


def support_matched_system(ring: Ring, templates: Sequence[Poly], seed: int) -> Tuple[List[Poly], NullMeta]:
    rng = random.Random(seed)
    polys = [{m: _nonzero(rng, ring.p) for m in t} for t in templates]
    degenerate = ring.p == 2
    notes = ("at p = 2 every nonzero coefficient is 1: the support-matched null is the input itself",) if degenerate else ()
    return polys, NullMeta("support_matched", seed, ring.p, degenerate_at_p2=degenerate, notes=notes)


def random_form(ring: Ring, variables: Sequence[int], degree: int, rng: random.Random,
                nonzero_coefficients: bool = False) -> Poly:
    """Uniformly random form of total degree ``degree`` in the listed variables.

    ``variables``: squarefree indices >= 0, free variables as -(j+1).
    """
    sq = [v for v in variables if v >= 0]
    fr = [-(v + 1) for v in variables if v < 0]
    sub = Ring(ring.p, len(sq), len(fr))
    out: Poly = {}
    for (mask, exps) in sub.monomials_exact(degree):
        c = _nonzero(rng, ring.p) if nonzero_coefficients else rng.randrange(0, ring.p)
        if c == 0:
            continue
        big_mask = 0
        for i, v in enumerate(sq):
            if mask >> i & 1:
                big_mask |= 1 << v
        big_exps = [0] * ring.n_free
        for j, fv in enumerate(fr):
            big_exps[fv] += exps[j]
        out[(big_mask, tuple(big_exps))] = c
    return out


def block_factored_generator(
    ring: Ring,
    blocks: Sequence[Sequence[int]],
    degrees: Sequence[int],
    rng: random.Random,
    nonzero_coefficients: bool = False,
) -> Tuple[Poly, List[Poly]]:
    """prod_k q_k with q_k a random form of degree degrees[k] on block k."""
    if len(blocks) != len(degrees):
        raise ValueError("one degree per block")
    factors = [random_form(ring, b, e, rng, nonzero_coefficients) for b, e in zip(blocks, degrees)]
    prod: Poly = {ring.one(): 1}
    for q in factors:
        prod = ring.mul(prod, q)
    return prod, factors


def block_factored_system(
    ring: Ring,
    blocks: Sequence[Sequence[int]],
    degrees: Sequence[int],
    seed: int,
    count: int = 1,
    extra_generators: Sequence[Poly] = (),
    nonzero_coefficients: bool = False,
) -> Tuple[List[Poly], NullMeta, List[List[Poly]]]:
    """``count`` block-factored generators followed by ``extra_generators``
    (e.g. the unchanged membership generators)."""
    rng = random.Random(seed)
    gens: List[Poly] = []
    factor_lists: List[List[Poly]] = []
    for _ in range(count):
        g, fs = block_factored_generator(ring, blocks, degrees, rng, nonzero_coefficients)
        gens.append(g)
        factor_lists.append(fs)
    gens.extend(dict(e) for e in extra_generators)
    return gens, NullMeta("block_factored", seed, ring.p,
                          notes=(f"blocks={[list(b) for b in blocks]} degrees={list(degrees)}",)), factor_lists


def scramble_coefficients(
    ring: Ring,
    polys: Sequence[Poly],
    seed: int,
    select: Callable[[int, Monomial, int], bool],
    allow_zero: bool = False,
) -> Tuple[List[Poly], NullMeta, List[List[Monomial]]]:
    """Re-draw coefficients of the monomials for which ``select(gen_index,
    monomial, coeff)`` is true.  Returns the scrambled system, meta, and the
    selected monomials per generator (for the record)."""
    rng = random.Random(seed)
    out: List[Poly] = []
    selected: List[List[Monomial]] = []
    for gi, f in enumerate(polys):
        g = dict(f)
        sel: List[Monomial] = []
        for m in sorted(f):
            if select(gi, m, f[m]):
                sel.append(m)
                c = rng.randrange(0, ring.p) if allow_zero else _nonzero(rng, ring.p)
                if c == 0:
                    del g[m]
                else:
                    g[m] = c
        out.append(g)
        selected.append(sel)
    return out, NullMeta("coefficient_scramble", seed, ring.p), selected
