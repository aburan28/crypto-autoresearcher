#!/usr/bin/env python3
"""Orbit meter A: enumerate all ⟨Frob,neg⟩ images by (k,s) and take lex-min.

Does not import orbit_b. Relation = sorted tuple of affine (x,y) points.
"""
from __future__ import annotations

from typing import Iterable, Sequence, Tuple

Rel = Tuple[Tuple[int, int], ...]


def apply_ks(F, P: Tuple[int, int], k: int, negate: bool) -> Tuple[int, int]:
    x, y = P
    for _ in range(k):
        x, y = F.square(x), F.square(y)
    if negate:
        y = x ^ y
    return (x, y)


def canonical_a(F, n: int, rel: Sequence[Tuple[int, int]]) -> Rel:
    best: Rel | None = None
    for k in range(n):
        for negate in (False, True):
            mapped = tuple(sorted(apply_ks(F, P, k, negate) for P in rel))
            if best is None or mapped < best:
                best = mapped
    assert best is not None
    return best


def unique_orbit_count_a(F, n: int, rels: Iterable[Sequence[Tuple[int, int]]]) -> int:
    return len({canonical_a(F, n, rel) for rel in rels})
