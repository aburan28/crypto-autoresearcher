"""Part-1 k | (r-1) modular predicate for EXP-BINSTD-6a150a.

Pinned to match EXP-BINSTD-178742 implementation/typed/part1_surface.py
functions k_divides_r_minus_1 and the twin modular routes used for
replication. No invented parameters. Amazon Bedrock not used.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


ROWS = [
    {"name": "c2pnb176v1", "m": 176, "label_derived_k_if_dmin_16": 11},
    {"name": "c2pnb208w1", "m": 208, "label_derived_k_if_dmin_16": 13},
    {"name": "c2pnb272w1", "m": 272, "label_derived_k_if_dmin_16": 17},
    {"name": "c2pnb304w1", "m": 304, "label_derived_k_if_dmin_16": 19},
    {"name": "c2pnb368w1", "m": 368, "label_derived_k_if_dmin_16": 23},
]


def k_divides_r_minus_1(k: int, r: int) -> bool:
    """Exact arithmetic predicate: k | (r - 1). Matches EXP-BINSTD-178742."""
    if k <= 0:
        raise ValueError("k must be positive")
    return (r - 1) % k == 0


def route_a(k: int, r: int) -> bool:
    return k_divides_r_minus_1(k, r)


def route_b(k: int, r: int) -> bool:
    """Twin: r ≡ 1 (mod k) via modular reduction of r."""
    if k <= 0:
        raise ValueError("k must be positive")
    return (r % k) == 1


def score_row(
    name: str,
    m: int,
    k: Optional[int],
    r: Optional[int],
    *,
    primary_sourced: bool,
    source: str,
    source_sha256: Optional[str],
    tier: Optional[str],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Score one c2pnb row. Undecided or non-TIER-P → NOT COMPUTED."""
    out: Dict[str, Any] = {
        "row": name,
        "m": m,
        "source": source,
        "tier": tier,
        "source_sha256": source_sha256,
        "primary_sourced": bool(primary_sourced),
        "certificate_kind": "none",
    }
    if (
        not primary_sourced
        or tier != "TIER-P"
        or k is None
        or r is None
        or not source_sha256
    ):
        out.update(
            {
                "k": k,
                "r": None if r is None else str(r),
                "r_mod_k": None,
                "verdict": "NOT COMPUTED",
                "reason": reason or "IMP-X962",
                "route_a": None,
                "route_b": None,
                "twin_agree": None,
                "ok": True,
            }
        )
        return out

    a = route_a(k, r)
    b = route_b(k, r)
    twin = a == b
    if not twin:
        out.update(
            {
                "k": k,
                "r": str(r),
                "r_mod_k": r % k,
                "verdict": "ARTIFACT",
                "reason": "twin_disagreement",
                "route_a": a,
                "route_b": b,
                "twin_agree": False,
                "ok": False,
            }
        )
        return out

    out.update(
        {
            "k": k,
            "r": str(r),
            "r_digit_count": len(str(r)),
            "r_mod_k": r % k,
            "verdict": "TRUE" if a else "FALSE",
            "reason": None,
            "route_a": a,
            "route_b": b,
            "twin_agree": True,
            "ok": True,
        }
    )
    return out
