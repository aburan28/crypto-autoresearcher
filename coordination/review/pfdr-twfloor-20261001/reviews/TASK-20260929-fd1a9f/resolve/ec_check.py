"""Disjoint kP = Q checker for joint F1 (VF-3), TASK-20260929-fd1a9f.

Imports NOTHING from crypto_autoresearcher and no elliptic-curve or number
theory library: only the Python standard library modules json, math, random
(for the target-log RULE, which is defined by Python's random.Random) and sys.
Everything else is implemented here: modular inverse (extended Euclid), affine
short-Weierstrass arithmetic over F_p with None as the point at infinity,
double-and-add scalar multiplication, a deterministic primality test (trial
division to isqrt(n), cross-checked by Miller-Rabin with the first twelve
prime bases), and baby-step giant-step.

usage: python3 ec_check.py <captures.jsonl> <archived-keys.json> <out k-table.jsonl>
"""
from __future__ import annotations

import json
import math
import random
import sys


# -- arithmetic --------------------------------------------------------------------------
def egcd_inv(x: int, p: int) -> int:
    """Inverse of x mod p by the extended Euclidean algorithm (x != 0 mod p)."""
    a, b = x % p, p
    if a == 0:
        raise ZeroDivisionError("no inverse of 0")
    u0, u1 = 1, 0
    while b:
        q = a // b
        a, b = b, a - q * b
        u0, u1 = u1, u0 - q * u1
    if a != 1:
        raise ZeroDivisionError("not invertible")
    return u0 % p


class Curve:
    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a % p, b % p

    def on(self, P) -> bool:
        if P is None:
            return True
        x, y = P
        p = self.p
        return 0 <= x < p and 0 <= y < p and (y * y - (x * x * x + self.a * x + self.b)) % p == 0

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            lam = (3 * x1 * x1 + self.a) * egcd_inv(2 * y1, p) % p
        else:
            lam = (y2 - y1) * egcd_inv(x2 - x1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    def mul(self, k: int, P):
        if k < 0:
            return self.mul(-k, self.neg(P))
        R, A = None, P
        while k:
            if k & 1:
                R = self.add(R, A)
            A = self.add(A, A)
            k >>= 1
        return R


# -- primality --------------------------------------------------------------------------
def is_prime_trial(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r = math.isqrt(n)
    f = 3
    while f <= r:
        if n % f == 0:
            return False
        f += 2
    return True


def is_prime_mr(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for q in small:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def is_prime(n: int) -> tuple[bool, bool]:
    """(trial-division verdict, Miller-Rabin verdict); both must agree."""
    return is_prime_trial(n), is_prime_mr(n)


# -- logarithm ---------------------------------------------------------------------------
def bsgs(E: Curve, P, Q, N: int) -> int | None:
    """k in [0, N) with k P = Q, by baby-step giant-step (full-point table)."""
    m = math.isqrt(N) + 1
    table = {}
    R = None
    for j in range(m):
        if R not in table:
            table[R] = j
        R = E.add(R, P)
    step = E.neg(E.mul(m, P))
    G = Q
    for i in range(m + 1):
        j = table.get(G)
        if j is not None:
            return (i * m + j) % N
        G = E.add(G, step)
    return None


def k_rule(bits: int, c: int, N: int) -> int:
    """__main__._instance / _instance_j0 rule as stated on the card and in
    AMD-20260929-1de84f C-5: random.Random(f"target|{bits}|{c}|0").randrange(1, N)."""
    return random.Random(f"target|{bits}|{c}|0").randrange(1, N)


def check(cap: dict, arch: dict | None) -> dict:
    p, a, b, N = cap["p"], cap["a"], cap["b"], cap["N"]
    E = Curve(p, a, b)
    P = tuple(cap["P"]) if cap["P"] is not None else None
    Q = tuple(cap["Q"]) if cap["Q"] is not None else None
    out = {"curve_params_equal_archived_row": (arch is not None and
                                               [arch["p"], arch["a"], arch["b"], arch["N"]] == [p, a, b, N])}
    out["discriminant_nonzero"] = (4 * a ** 3 + 27 * b ** 2) % p != 0
    pt, pm = is_prime(p)
    nt, nm = is_prime(N)
    out["p_prime"] = pt and pm
    out["N_prime"] = nt and nm
    out["primality_tests_agree"] = (pt == pm) and (nt == nm)
    out["hasse_bound"] = abs(p + 1 - N) <= 2 * math.isqrt(p) + 2
    out["P_on_curve"] = P is not None and E.on(P)
    out["Q_on_curve"] = Q is not None and E.on(Q)
    out["N_P_is_O"] = E.mul(N, P) is None
    kr = k_rule(cap["bits"], cap["curve"], N)
    out["k_rule"] = kr
    out["k_rule_P_eq_Q"] = E.mul(kr, P) == Q
    ks = cap.get("k_solver")
    out["k_solver"] = ks
    if ks is None:
        out["k_solver_eq_k_rule_mod_N"] = None
        out["k_solver_P_eq_Q"] = None
    else:
        out["k_solver_eq_k_rule_mod_N"] = (ks - kr) % N == 0
        out["k_solver_P_eq_Q"] = E.mul(ks, P) == Q
    return out


def main():
    caps = [json.loads(l) for l in open(sys.argv[1])]
    arch = json.load(open(sys.argv[2]))  # {"bits|curve|panel": {"p","a","b","N"}}
    bs_cache = {}
    with open(sys.argv[3], "w") as f:
        for cap in caps:
            key = f"{cap['bits']}|{cap['curve']}|{cap['panel']}"
            res = check(cap, arch.get(key))
            ck = (cap["p"], cap["a"], cap["b"], tuple(cap["P"]), tuple(cap["Q"]))
            if ck not in bs_cache:
                bs_cache[ck] = bsgs(Curve(cap["p"], cap["a"], cap["b"]), tuple(cap["P"]), tuple(cap["Q"]), cap["N"])
            res["k_bsgs"] = bs_cache[ck]
            res["k_bsgs_eq_k_rule"] = res["k_bsgs"] == res["k_rule"]
            rec = {k: cap[k] for k in ("job", "panel", "bits", "curve", "m", "arm", "mode", "p", "a", "b", "N", "P", "Q",
                                       "terminated_by", "verified_flag")}
            rec["k_solver"] = cap.get("k_solver")
            rec |= {"k_rule": res.pop("k_rule"), "k_bsgs": res.pop("k_bsgs")}
            rec.pop("k_solver", None)
            rec["k_solver"] = res.pop("k_solver")
            rec["checks"] = res
            f.write(json.dumps(rec, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
