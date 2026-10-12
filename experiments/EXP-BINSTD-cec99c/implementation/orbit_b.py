#!/usr/bin/env python3
"""Orbit meter B: BFS under generators Frob and negation, then min of the orbit.

Does not import orbit_a. Independent of (k,s) product enumeration.
"""
from __future__ import annotations

from typing import Iterable, Sequence, Tuple

Rel = Tuple[Tuple[int, int], ...]


def _frob(F, rel: Rel) -> Rel:
    return tuple(sorted((F.square(x), F.square(y)) for x, y in rel))


def _neg(rel: Rel) -> Rel:
    return tuple(sorted((x, x ^ y) for x, y in rel))


def canonical_b(F, n: int, rel: Sequence[Tuple[int, int]]) -> Rel:
    start: Rel = tuple(sorted(rel))
    seen = {start}
    stack = [start]
    while stack:
        cur = stack.pop()
        for nxt in (_frob(F, cur), _neg(cur)):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    if len(seen) > 2 * n:
        raise RuntimeError("orbit larger than |<Frob,neg>|")
    return min(seen)


def unique_orbit_count_b(F, n: int, rels: Iterable[Sequence[Tuple[int, int]]]) -> int:
    return len({canonical_b(F, n, rel) for rel in rels})
