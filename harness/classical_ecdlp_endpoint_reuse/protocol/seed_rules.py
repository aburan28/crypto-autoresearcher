#!/usr/bin/env python3
"""Public experiment randomization only; this module never draws target scalars."""
from __future__ import annotations
import hashlib
import random

DOMAIN = b"classical.ecdlp.endpoint-reuse.v1\0"

def public_seed(protocol_hash: str, external_nonce: str, fixture_id: str,
                replicate: int, purpose: str) -> int:
    if len(protocol_hash) != 64 or any(x not in "0123456789abcdef" for x in protocol_hash):
        raise ValueError("canonical frozen protocol SHA-256 required")
    if not external_nonce or replicate < 0 or not fixture_id or not purpose:
        raise ValueError("nonempty post-freeze nonce, fixture, purpose and nonnegative replicate required")
    values = (protocol_hash, external_nonce, fixture_id, str(replicate), purpose)
    raw = DOMAIN + b"\0".join(v.encode("ascii") for v in values)
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")

def arm_order(arms: list[str], protocol_hash: str, external_nonce: str,
              fixture_id: str, replicate: int) -> list[str]:
    if len(arms) != len(set(arms)):
        raise ValueError("duplicate arm")
    values = list(arms)
    random.Random(public_seed(protocol_hash, external_nonce, fixture_id,
                              replicate, "arm_order")).shuffle(values)
    return values

def table_parameters(r: int) -> tuple[int, int, int]:
    if r < 2:
        raise ValueError("positive prime subgroup order required")
    t = r.bit_length() // 3
    denominator = 1 << (2 * t)
    initial_chains = (r + denominator // 2) // denominator
    return t, initial_chains, 4 * initial_chains
