"""Shared helpers for EXP-FIB-001: canonical point sign convention, seeded RNGs,
and small utilities. New glue confined to experiments/EXP-FIB-001/ per the
frozen spec's implementation note.
"""
from __future__ import annotations

import hashlib
import random

from harness.toycurve import EllipticCurve, Point


def canon_lift(E: EllipticCurve, x: int) -> Point | None:
    """A fixed-sign point with x-coordinate x, or None if x is not on E.

    Fixes y to the smaller of {y, p-y} so every factor-base element maps to
    exactly one point (the "canonical" convention used to build the n_R
    enumeration table). Deterministic, public-data only.
    """
    pt = E.lift_x(x)
    if pt is None:
        return None
    _, y = pt
    yneg = (-y) % E.p
    return (x, min(y, yneg))


def seeded_rng(seed: int, tag: str) -> random.Random:
    h = hashlib.sha256(f"EXP-FIB-001:{seed}:{tag}".encode()).hexdigest()
    return random.Random(int(h, 16))


def sha256_of(obj) -> str:
    import json
    blob = json.dumps(obj, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()
