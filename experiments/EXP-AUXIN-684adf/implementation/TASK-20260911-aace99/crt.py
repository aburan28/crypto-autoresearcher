"""Truth-free generalized CRT producer for the AUXIN supplied-residue pipeline."""
from __future__ import annotations
import math

class CRTError(ValueError): pass

def inverse(a: int, m: int, counters: dict | None = None) -> int:
    if m <= 1: raise CRTError("inverse modulus must exceed one")
    if counters is not None: counters["inverse_calls"] = counters.get("inverse_calls", 0) + 1
    old_r, r, old_s, s = a % m, m, 1, 0
    while r:
        q = old_r // r; old_r, r = r, old_r-q*r; old_s, s = s, old_s-q*s
    if old_r != 1: raise CRTError("noninvertible")
    return old_s % m

def fold(n: int, pairs: list[tuple[int, int]], counters: dict | None = None) -> dict:
    """Fold only ordered (residue, modulus) values; it has no truth/reference input."""
    if not isinstance(n, int) or n <= 0: raise CRTError("bad domain")
    a0, modulus = 0, 1
    for index, (a, m) in enumerate(pairs):
        if not isinstance(a, int) or not isinstance(m, int) or m <= 0: raise CRTError("bad pair")
        if counters is not None: counters["gcd_calls"] = counters.get("gcd_calls", 0)+1
        g = math.gcd(modulus, m)
        if (a-a0) % g: return {"status":"inconsistent","reject_index":index,"k0":None,"M":None}
        h = m//g
        u = 0 if h == 1 else ((a-a0)//g*inverse((modulus//g) % h, h, counters)) % h
        modulus, a0 = modulus*h, (a0+modulus*u) % (modulus*h)
    return {"status":"consistent","reject_index":None,"k0":a0,"M":modulus}

def candidates(n: int, result: dict, counters: dict | None = None) -> list[int]:
    if result["status"] == "inconsistent": return []
    m, a = result["M"], result["k0"]
    if n % m: raise CRTError("combined modulus does not divide domain")
    out = [a+m*t for t in range(n//m)]
    if counters is not None: counters["candidate_enumerations"] = counters.get("candidate_enumerations",0)+len(out)
    return out
