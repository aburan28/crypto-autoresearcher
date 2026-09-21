"""
INDEPENDENT certificate checker. Deliberately re-implements its own minimal
EC point addition and scalar multiplication from scratch, importing NOTHING
from rho_solver.py, ec_group_ops.py, or ec_affine.py, so that it shares no
state or code path with the solver (contract invalidation rule: "A
certificate checker sharing state or code paths with the solver invalidates
the whole run"). It re-derives, independently, that [k]P == Q on the curve
the claim is made against.
"""
from __future__ import annotations


def _add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2 and y1 == y2:
        if y1 == 0:
            return None
        lam = ((3 * x1 * x1 + a) * pow((2 * y1) % p, p - 2, p)) % p
    else:
        lam = ((y2 - y1) * pow((x2 - x1) % p, p - 2, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def _scalar_mul(k, P, a, p):
    if k % 1 != 0:
        raise ValueError("k must be an integer")
    k = int(k)
    if k == 0 or P is None:
        return None
    if k < 0:
        return _scalar_mul(-k, (P[0], (-P[1]) % p), a, p)
    R = None
    base = P
    while k:
        if k & 1:
            R = _add(R, base, a, p)
        base = _add(base, base, a, p)
        k >>= 1
    return R


def verify_on_curve(P, a, b, p):
    if P is None:
        return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0


def verify_dlp_solution(p: int, a: int, b: int, P, Q, k: int) -> dict:
    """
    Returns a dict: {"verified": bool, "reason": str}. Independently checks:
      1. P and Q both lie on y^2 = x^3+ax+b over F_p.
      2. [k]P == Q via this module's own scalar multiplication.
    """
    if not verify_on_curve(P, a, b, p):
        return {"verified": False, "reason": "P not on curve"}
    if not verify_on_curve(Q, a, b, p):
        return {"verified": False, "reason": "Q not on curve"}
    computed = _scalar_mul(k, P, a, p)
    if computed == Q:
        return {"verified": True, "reason": "kP == Q (independent recomputation)"}
    return {"verified": False, "reason": f"kP != Q: got {computed}, expected {Q}"}
