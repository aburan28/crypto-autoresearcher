"""
Independent [k]P=Q certificate re-verification, per docs/claims-and-
verification.md and AGENTS.md rule 4. Every claimed solve in this
experiment (baseline rho/BSGS, SSSA anomalous solve) is re-checked here,
independently of whichever routine produced k, before being counted as a
result anywhere.
"""
from __future__ import annotations
from .ecc import scalar_mult


def verify_certificate(k: int, P, Q, a: int, p: int) -> bool:
    if k is None:
        return False
    return scalar_mult(k, P, a, p) == Q
