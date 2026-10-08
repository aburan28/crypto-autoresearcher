"""Ordinary binary curve Y^2 + XY = X^3 + A X^2 + B and Hasse-BSGS order."""
from __future__ import annotations

import math
import random
from typing import Optional

from gf2n import Field


Point = Optional[tuple[int, int]]  # None = infinity


class Curve:
    def __init__(self, F: Field, A: int, B: int):
        if B == 0:
            raise ValueError("B must be nonzero")
        self.F, self.A, self.B = F, A, B

    def on_curve(self, P: Point) -> bool:
        if P is None:
            return True
        F = self.F
        x, y = P
        lhs = F.mul(y, y) ^ F.mul(x, y)
        x2 = F.mul(x, x)
        rhs = F.mul(x2, x) ^ F.mul(self.A, x2) ^ self.B
        return lhs == rhs

    def neg(self, P: Point) -> Point:
        if P is None:
            return None
        return (P[0], P[0] ^ P[1])

    def double(self, P: Point) -> Point:
        F = self.F
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.mul(lam, lam) ^ lam ^ self.A
        y3 = F.mul(x1, x1) ^ F.mul(lam ^ 1, x3)
        return (x3, y3)

    def add(self, P: Point, Q: Point) -> Point:
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == (x1 ^ y1):
                return None
            return self.double(P)
        dx = x1 ^ x2
        lam = F.mul(y1 ^ y2, F.inv(dx))
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def mul(self, k: int, P: Point) -> Point:
        if k < 0:
            return self.mul(-k, self.neg(P))
        R: Point = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.double(Q)
            k >>= 1
        return R

    def rhs_c(self, x: int) -> int:
        F = self.F
        return x ^ self.A ^ F.mul(self.B, F.inv(F.mul(x, x)))

    def lift_x(self, x: int) -> Point:
        F = self.F
        if x == 0:
            return (0, F.sqrt(self.B))
        c = self.rhs_c(x)
        if F.trace(c) != 0:
            return None
        if F.n % 2 == 1:
            z = F.half_trace(c)
        else:
            z = F.solve_artin_schreier(c)
            if z is None:
                return None
        return (x, F.mul(x, z))

    def random_point(self, rng: random.Random) -> Point:
        F = self.F
        for _ in range(10000):
            x = rng.randrange(0, F.q)
            P = self.lift_x(x)
            if P is not None:
                assert self.on_curve(P)
                return P
        raise RuntimeError("failed to sample a curve point")


def hasse_bound(q: int) -> int:
    # |#E - (q+1)| <= floor(2*sqrt(q)) = isqrt(4*q)
    return math.isqrt(4 * q)


def order_via_hasse_bsgs(E: Curve, seed: int = 20261001, max_trials: int = 128) -> dict:
    """Determine #E(F_q) via point-order LCMs + Weil-compatible filter.

    1. BSGS: for random P, collect Hasse-interval annihilators N with N*P=O;
       gcd of those equals ord(P).
    2. Running LCM L of point orders.
    3. Candidate cardinalities = multiples of L in the Hasse interval.
    4. Filter by the elliptic-curve structure theorem: E(F_q) ≅ Z/n × Z/m
       with n|m, nm=#E, and n|(q-1). Taking m=L (once L is the exponent,
       approximated by the running LCM), require (N/L)|L and (N/L)|(q-1).
    """
    F = E.F
    q = F.q
    Bnd = hasse_bound(q)
    lo, hi = q + 1 - Bnd, q + 1 + Bnd
    rng = random.Random(seed)
    m_step = math.isqrt(2 * Bnd) + 1

    def annihilator_candidates(P) -> list[int]:
        Q = E.mul(q + 1, P)
        baby = {}
        R: Point = None
        for j in range(m_step):
            key = ("O",) if R is None else (R[0], R[1])
            baby.setdefault(key, j)
            R = E.add(R, P)
        step = E.mul(m_step, P)
        i_max = Bnd // m_step + 2
        Ns = []
        for i in range(-i_max, i_max + 1):
            left = E.add(Q, E.mul(-i, step))
            key = ("O",) if left is None else (left[0], left[1])
            if key in baby:
                j = baby[key]
                t = i * m_step + j
                if abs(t) <= Bnd:
                    N = q + 1 - t
                    if lo <= N <= hi and E.mul(N, P) is None:
                        Ns.append(N)
        return sorted(set(Ns))

    def gcd_list(vals: list[int]) -> int:
        g = 0
        for v in vals:
            g = math.gcd(g, v)
        return g

    def lcm(a: int, b: int) -> int:
        return a // math.gcd(a, b) * b

    L = 1
    details = []
    stagnant = 0
    for trial in range(max_trials):
        P = E.random_point(rng)
        Ns = annihilator_candidates(P)
        if not Ns:
            details.append({"trial": trial, "point_x": P[0], "Ns": [], "ord": None})
            continue
        ord_P = gcd_list(Ns)
        details.append({"trial": trial, "point_x": P[0], "Ns": Ns, "ord": ord_P})
        if ord_P <= 0:
            continue
        new_L = lcm(L, ord_P)
        if new_L == L:
            stagnant += 1
        else:
            stagnant = 0
            L = new_L
        multiples = [N for N in range(lo, hi + 1) if L > 0 and N % L == 0]
        # Weil/structure filter: n = N/L must divide L and (q-1)
        filtered = [
            N
            for N in multiples
            if (N // L) > 0
            and (L % (N // L) == 0)
            and ((q - 1) % (N // L) == 0)
        ]
        # Accept when unique after filter, and L has stabilized enough
        # (or uniquely determined regardless).
        if len(filtered) == 1 and (stagnant >= 2 or len(multiples) == 1):
            N = filtered[0]
            P2 = E.random_point(rng)
            if E.mul(N, P2) is not None:
                continue
            return {
                "ok": True,
                "group_order": N,
                "trace_t": q + 1 - N,
                "hasse_bound": Bnd,
                "q": q,
                "lcm_point_orders": L,
                "structure_n": N // L,
                "trials_used": trial + 1,
                "details": details,
            }
        if len(multiples) == 1 and stagnant >= 1:
            N = multiples[0]
            P2 = E.random_point(rng)
            if E.mul(N, P2) is not None:
                continue
            return {
                "ok": True,
                "group_order": N,
                "trace_t": q + 1 - N,
                "hasse_bound": Bnd,
                "q": q,
                "lcm_point_orders": L,
                "structure_n": N // L if L else None,
                "trials_used": trial + 1,
                "details": details,
            }
    return {
        "ok": False,
        "group_order": None,
        "trace_t": None,
        "hasse_bound": Bnd,
        "q": q,
        "lcm_point_orders": L,
        "trials_used": max_trials,
        "details": details,
        "error": "failed to uniquely determine group order within trial budget",
    }


def factor_group_order(N: int) -> dict:
    """Trial-factor N; identify a large prime-order subgroup if present."""
    n = N
    factors = []
    p = 2
    while p * p <= n:
        while n % p == 0:
            factors.append(p)
            n //= p
        p = 3 if p == 2 else p + 2
        if p > 1000000 and p * p <= n:
            # give up on huge remaining cofactor trial; break to append
            break
    if n > 1:
        factors.append(n)
    odd_primes = [f for f in factors if f > 2]
    l_order = max(odd_primes) if odd_primes else None
    cofactor = N // l_order if l_order else None
    l_prime = l_order is not None and _is_probable_prime(l_order)
    return {
        "N": N,
        "factors": factors,
        "l_order": l_order,
        "cofactor_h": cofactor,
        "l_order_probable_prime": l_prime,
    }


def _is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
        if a >= n:
            continue
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


def verify_subgroup_order(E: Curve, N: int, l_order: int, seed: int = 20261001) -> dict:
    """Check N*P=O for random P, and that some point has order dividing l_order with P!=O."""
    rng = random.Random(seed + 7)
    checks = []
    ok = True
    for i in range(3):
        P = E.random_point(rng)
        NP = E.mul(N, P)
        checks.append({"i": i, "N_P_is_O": NP is None})
        if NP is not None:
            ok = False
    found = False
    gen_x = None
    h = N // l_order
    for _ in range(64):
        Q = E.random_point(rng)
        P = E.mul(h, Q)
        if P is None:
            continue
        if E.mul(l_order, P) is None:
            found = True
            gen_x = P[0]
            break
    return {
        "N_annihilates_sample_points": ok,
        "found_point_of_order_l": found,
        "sample_generator_x": gen_x,
        "checks": checks,
        "verified": ok and found,
    }
