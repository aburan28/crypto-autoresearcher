"""
Fingerprint-equivalence structural-presence check for EXP-RELN-141a86
Stage 0c: an enumerated candidate set is exhaustive AND deduplicated by
numeric fingerprint (grammar_engine.numeric_fingerprint), so the correct
test for "is this known target expression discoverable by the frozen
exhaustive search at or below complexity C" is whether ANY entry in the
enumerated set (levels 1..C) has the SAME fingerprint as the target --
not exact canonical-string identity, since the engine's own dedup
correctly folds algebraically equivalent trees into one representative
(confirmed on INV-A6: the hand-built target
sub(add(div(conc,mu),CONST),mu) canonicalizes to a DIFFERENT tree shape
than the earlier-registered algebraically-identical
sub(CONST,sub(mu,div(conc,mu))); both compute conc/mu + CONST - mu, and
the contract's own recovery rule accepts "an algebraically equivalent
form ... after symbolic simplification").
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import grammar_engine as ge


def find_equivalent(target_expr, pack: str, levels: Dict[int, List[Tuple]],
                     max_complexity: int) -> Optional[Dict]:
    """
    Search levels[1..max_complexity] (already-enumerated canonical forms
    for `pack`) for an entry with the same numeric fingerprint as
    `target_expr`. Returns the first match found (by complexity ascending,
    matching the engine's own enumeration_order), with its complexity and
    canonical string, or None if no match exists within the levels given
    (NOT necessarily "not recoverable" -- only "not found within the
    levels actually searched", which the caller must scope honestly to
    however far enumeration reached).
    """
    leaves = ge.LEAVES_BY_PACK.get(pack) or _CUSTOM_PACKS.get(pack)
    target_canon = ge.canonicalize(target_expr)
    target_fp = ge.numeric_fingerprint(target_canon, leaves)
    target_nc = ge.node_count(target_canon)
    for c in range(1, max_complexity + 1):
        for e in levels.get(c, []):
            if ge.numeric_fingerprint(e, leaves) == target_fp:
                return {
                    "found": True,
                    "complexity_of_representative": c,
                    "representative_canonical_string": ge.to_canonical_string(e),
                    "target_canonical_string": ge.to_canonical_string(target_canon),
                    "target_node_count": target_nc,
                    "exact_string_match": ge.to_canonical_string(e) == ge.to_canonical_string(target_canon),
                }
    return None


# Packs not in grammar_engine.LEAVES_BY_PACK (built ad hoc for identity-only
# checks, per the contract's node_counting_rule note: "conc supplied as a
# leaf for this identity check only").
_CUSTOM_PACKS = {
    "inv_a6_identity_pack": ["conc", "mu", "CONST"],
}


def register_custom_packs():
    ge.LEAVES_BY_PACK.setdefault("inv_a6_identity_pack", ["conc", "mu", "CONST"])
    ge._SAMPLE_GRID.setdefault("conc", [ge.Fraction(3, 2), ge.Fraction(5, 2)])
