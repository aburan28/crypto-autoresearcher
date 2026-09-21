"""
CTRL-EXITMAP-CONSISTENCY: before a discovered or planted isogeny path is
credited as a TRANSFER path (to a genuinely distinct special curve E''),
check it is not in fact a SELF-MAP of E (an endomorphism composite that
returns to E's own F_p-isomorphism class).

Per IDEA-20260727-005 (C1, self-map neutrality): every group homomorphism
G -> G is multiplication by a scalar, i.e. an F_p-rational endomorphism
composite that closes back into the SAME curve contributes nothing beyond
the trivial degree-invariant relation and must never be counted as reaching
a distinct special curve. In this experiment's own vertex/edge model
(class_walk.py, dedup key = (j_invariant, trace)), a composite walk that
returns to the START vertex's own dedup key IS exactly such a self-map (a
closed endomorphism loop on E), independent of how many intermediate
distinct-looking vertices it passed through.

This predicate is exact and structural: no heuristic judgment is involved.
"""
from __future__ import annotations


def is_self_map(start_key, end_key) -> bool:
    """start_key/end_key are (j_invariant, trace) dedup keys as used by
    class_walk.py. A credited path is a self-map iff its endpoint's dedup
    key equals the start vertex's dedup key (it closes back onto E's own
    F_p-isomorphism class)."""
    return start_key == end_key


def classify_path(start_key, end_key, is_special_target: bool) -> dict:
    """
    Returns a dict describing whether a path may be credited as a TRANSFER
    path. A path is creditable only if (a) its endpoint is NOT the self-map
    case, and (b) its endpoint actually satisfies a special-family
    predicate. Any path failing (a) is VOID per INV-EXITMAP, flagged rather
    than silently dropped.
    """
    self_map = is_self_map(start_key, end_key)
    creditable = (not self_map) and is_special_target
    return {
        "self_map": self_map,
        "is_special_target": is_special_target,
        "creditable_as_transfer_path": creditable,
        "void_reason": "INV-EXITMAP: endpoint is a self-map of E, not a distinct special curve" if self_map and is_special_target else None,
    }
