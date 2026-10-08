"""Independent certificate re-verification (separate from solver hot path).

Uses schoolbook field mul where available; rebuilds Curve from parameters.
"""
from __future__ import annotations

from curve import Curve
from gf2n import Field, TableField


def verify_discrete_log(curve: Curve, P, Q, k: int) -> bool:
    """Fresh [k]P == Q on a newly constructed curve object."""
    F = curve.F
    # Rebuild with schoolbook-capable field wrapper
    Fs = Field(F.n, F.mod)
    E2 = Curve(Fs, curve.A, curve.B)
    # Map points as ints (same representation)
    P2 = None if P is None else (int(P[0]), int(P[1]))
    Q2 = None if Q is None else (int(Q[0]), int(Q[1]))
    R = E2.mul(int(k) % (1 << 40), P2)  # k is small at n=19 (mod ell < 2^17)
    # Use full k
    R = E2.mul(int(k), P2)
    return R == Q2


def verify_decomposition(curve: Curve, R, P, z: int, V_contains) -> bool:
    """Check R == [z]P and x(P) in V' using a fresh curve object."""
    F = curve.F
    Fs = Field(F.n, F.mod)
    E2 = Curve(Fs, curve.A, curve.B)
    P2 = (int(P[0]), int(P[1]))
    R2 = (int(R[0]), int(R[1]))
    if not V_contains(P2[0]):
        return False
    got = E2.mul(int(z), P2)
    return got == R2


def verify_discrete_log_mod(curve: Curve, P, Q, k: int, mod: int) -> bool:
    return verify_discrete_log(curve, P, Q, k % mod)
