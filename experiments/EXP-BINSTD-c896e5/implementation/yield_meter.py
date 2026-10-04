#!/usr/bin/env python3
"""Nagao disjoint-coset vs chained S_3 unique-relation yield.

G = <Frobenius, negation> acts diagonally on FB×FB. Nagao processes a pair
iff it is the lexicographic minimum of its G-orbit among FB×FB. Chained S_3
processes every unordered pair. Both count unique triples P+Q+R=O with
P,Q,R on the factor base.
"""
from __future__ import annotations

from typing import Iterable, Optional, Sequence, Set, Tuple

from curve import Curve

Point = Tuple[int, int]
Rel = Tuple[Point, ...]


def encode_pt(P: Point) -> Tuple[int, int]:
    return (int(P[0]), int(P[1]))


def g_action(curve: Curve, P: Point, k: int, negate: bool) -> Point:
    Q: Optional[Point] = P
    for _ in range(k):
        Q = curve.frobenius(Q)
        if Q is None:
            return P
    if negate:
        Q = curve.neg(Q)
        if Q is None:
            return P
    return encode_pt(Q)


def pair_canonical(curve: Curve, n: int, P: Point, Q: Point) -> Tuple[Point, Point]:
    best: Optional[Tuple[Point, Point]] = None
    for k in range(n):
        for negate in (False, True):
            Pp = g_action(curve, P, k, negate)
            Qp = g_action(curve, Q, k, negate)
            key = tuple(sorted((Pp, Qp)))
            cand = (key[0], key[1])
            if best is None or cand < best:
                best = cand
    assert best is not None
    return best


def is_canonical_pair(curve: Curve, n: int, P: Point, Q: Point) -> bool:
    a, b = tuple(sorted((encode_pt(P), encode_pt(Q))))
    c, d = pair_canonical(curve, n, P, Q)
    return (a, b) == (c, d)


def collect_relations(
    curve: Curve,
    fb: Sequence[Point],
    n: int,
    nagao_only: bool,
) -> Set[Rel]:
    fb_list = [encode_pt(P) for P in fb]
    fb_set = set(fb_list)
    rels: Set[Rel] = set()
    m = len(fb_list)
    for i in range(m):
        for j in range(i, m):
            P, Q = fb_list[i], fb_list[j]
            if nagao_only and not is_canonical_pair(curve, n, P, Q):
                continue
            S = curve.add(P, Q)
            if S is None:
                rel = tuple(sorted({P, Q}))
                if len(rel) >= 1:
                    rels.add(rel)
                continue
            R = curve.neg(S)
            if R is None:
                continue
            R = encode_pt(R)
            if R in fb_set:
                rels.add(tuple(sorted((P, Q, R))))
    return rels


def unique_count(rels: Iterable[Rel]) -> int:
    return len({tuple(sorted(r)) for r in rels})


def poly_x_span(n: int, ell: int) -> list[int]:
    out = []
    for mask in range(1 << ell):
        x = 0
        for j in range(ell):
            if mask & (1 << j):
                x ^= 1 << j
        if x.bit_length() - 1 < n:
            out.append(x)
    return sorted(set(out))


def factor_base(curve: Curve, xs: Sequence[int]) -> list[Point]:
    pts: list[Point] = []
    seen = set()
    for x in xs:
        if x == 0:
            continue
        P = curve.lift_x(x)
        if P is None:
            continue
        for Q in (P, curve.neg(P)):
            if Q is None:
                continue
            Qe = encode_pt(Q)
            if Qe in seen:
                continue
            if not curve.on_curve(Qe):
                raise RuntimeError("lift not on curve")
            seen.add(Qe)
            pts.append(Qe)
    return pts
