"""Direct (triple-loop / multiset) enumerator for the decomposition-count
vector c_D(r) at arity m = 3, for EXP-RELN-f202be.

This module is one of the two INDEPENDENT implementations required by the
contract (experiments/EXP-RELN-f202be/specification.yaml, invalidation_rules:
"the direct enumerator and the spectral implementation share code ... is
invalid"). It shares no module, function, or imported helper with
source/spectral_crosscheck.py beyond the Python standard library.

It is generic over any finite abelian group given as:
  - a list of B distinct "elements" (opaque, hashable-after-key_fn objects,
    e.g. (x, y) tuples for a curve point, or an int for Z/N),
  - an `add_fn(u, v) -> w` giving the group operation,
  - a `key_fn(w) -> hashable` giving a canonical hash key for a group element
    (needed because curve points at infinity are represented specially).

Enumeration is via itertools.combinations_with_replacement over the B
elements, i.e. true multiset enumeration (each unordered triple with
repetition visited exactly once), NOT an ordered triple loop -- this matches
the contract's "direct triple-loop/multiset enumeration" description at the
multiset (not ordered) level, which is what the count vector c_D(r) counts.
"""
from __future__ import annotations

import itertools
from collections import Counter
from typing import Callable, Hashable, Sequence


def enumerate_triples(
    elements: Sequence,
    add_fn: Callable,
    key_fn: Callable[[object], Hashable],
    neg_index: Sequence[int] | None = None,
) -> dict:
    """Enumerate all size-3 multisets from `elements` under the group op.

    Returns a dict with:
      unreduced: Counter of key(sum) -> count, over ALL C(B+2,3) multisets.
      reduced: Counter of key(sum) -> count, over only the multisets that
        contain NO pair {P, -P} (only meaningful/produced if neg_index given;
        otherwise identical to unreduced).
      M: total multisets = C(B+2,3)
      M_red: total reduced multisets (only if neg_index given, else None)
      B: number of elements
      forced_multisets: number of multisets excluded by the reduction
        (i.e. containing at least one negation pair), only if neg_index given.

    neg_index[i] = index j such that elements[j] == -elements[i] (i.e. the
    negation of elements[i] is also in the base), or -1 if the negation of
    elements[i] is not present in the base. Pass None for plain (non
    negation-closed) bases; then reduced == unreduced and forced_multisets=0.
    """
    B = len(elements)
    unreduced: Counter = Counter()
    reduced: Counter = Counter()
    forced = 0
    has_neg = neg_index is not None

    idx_range = range(B)
    for i, j, k in itertools.combinations_with_replacement(idx_range, 3):
        s = add_fn(add_fn(elements[i], elements[j]), elements[k])
        key = key_fn(s)
        unreduced[key] += 1
        if has_neg:
            contains_pair = (
                neg_index[i] == j or neg_index[i] == k or neg_index[j] == k
            )
            if contains_pair:
                forced += 1
            else:
                reduced[key] += 1
        else:
            reduced[key] += 1

    from math import comb

    M = comb(B + 2, 3)
    result = {
        "unreduced": unreduced,
        "reduced": reduced if has_neg else unreduced,
        "M": M,
        "M_red": (M - forced) if has_neg else M,
        "B": B,
        "forced_multisets": forced if has_neg else 0,
    }
    return result


def sum_of_squares(counter: Counter) -> int:
    """E_3 = sum_r c(r)^2, integer-exact."""
    return int(sum(v * v for v in counter.values()))


def sum_of_counts(counter: Counter) -> int:
    """INV-1 check quantity: sum_r c(r)."""
    return int(sum(counter.values()))


def k_rich_counts(counter: Counter, ks: Sequence[int], universe_size: int) -> dict:
    """#{r : c(r) >= k} for each k, over a universe of size `universe_size`
    (targets with c(r) = 0 are not keys of `counter` and correctly contribute
    0 to every k >= 1 count)."""
    vals = list(counter.values())
    out = {}
    for k in ks:
        out[str(k)] = int(sum(1 for v in vals if v >= k))
    return out
