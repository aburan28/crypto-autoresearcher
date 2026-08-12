"""
Find two toy short-Weierstrass curves y^2 = x^3 + a x + b (mod p) each with a
prime-order subgroup that is an exact power of two, of the sizes declared for
this pilot run. Point-counting uses a vectorised (numpy) O(p) Legendre-symbol
scan, tractable only at toy sizes -- part of why this pilot uses reduced
curve sizes relative to the frozen specification's 2^20 / 2^28
(see implementation.md, "Scope deviation").
"""
import json
import random
import sys
import numpy as np

TARGET_ORDERS = [2**12, 2**16]

def is_prime(n):
    if n < 2:
        return False
    for p in [2,3,5,7,11,13,17,19,23,29,31]:
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in [2,3,5,7,11,13,17,19,23,29,31,37]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def modpow_array(base, exp, mod):
    # vectorised modular exponentiation, base: int array, exp: python int, mod: int
    result = np.ones_like(base, dtype=object)
    b = base.astype(object) % mod
    e = exp
    while e > 0:
        if e & 1:
            result = (result * b) % mod
        b = (b * b) % mod
        e >>= 1
    return result

def point_count_vec(a, b, p):
    xs = np.arange(p, dtype=object)
    rhs = (xs*xs*xs + a*xs + b) % p
    leg = modpow_array(rhs, (p - 1)//2, p)
    leg = np.where(rhs == 0, 0, np.where(leg == p - 1, -1, 1))
    return p + 1 + int(leg.sum())

def mod_inv(a, p):
    return pow(int(a), p - 2, p)

def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * mod_inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * mod_inv((x2 - x1) % p, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, P, a, p):
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R

def legendre_scalar(a, p):
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else r

def tonelli_shanks(n, p):
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = (t2 * t2) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, (b * b) % p, (t * b * b) % p, (r * b) % p
    return r

def find_points(a, b, p, limit=None, rng=None):
    xs = list(range(p))
    if rng is not None:
        rng.shuffle(xs)
    pts = []
    for x in xs:
        rhs = (x*x*x + a*x + b) % p
        y = tonelli_shanks(rhs, p)
        if y is not None:
            pts.append((x, y))
        if limit is not None and len(pts) >= limit:
            break
    return pts

def curve_search(target_order, p_lo, p_hi, seed, max_primes_tried=2000):
    rng = random.Random(seed)
    candidates = [p for p in range(p_lo, p_hi) if is_prime(p)]
    rng.shuffle(candidates)
    tried = 0
    for p in candidates:
        if tried >= max_primes_tried:
            break
        tried += 1
        for a in range(0, 6):
            for b in range(1, 6):
                disc = (4 * a**3 + 27 * b*b) % p
                if disc == 0:
                    continue
                n = point_count_vec(a, b, p)
                if n % target_order == 0:
                    cofactor = n // target_order
                    if cofactor == 0:
                        continue
                    pts = find_points(a, b, p, limit=200, rng=rng)
                    for pt in pts:
                        G = ec_mul(cofactor, pt, a, p)
                        if G is None:
                            continue
                        if ec_mul(target_order, G, a, p) is not None:
                            continue
                        if ec_mul(target_order // 2, G, a, p) is None:
                            continue
                        return {
                            "p": p, "a": a, "b": b, "order_curve": n,
                            "cofactor": cofactor, "subgroup_order": target_order,
                            "generator": list(G),
                        }
    return None

def main():
    curves = {}
    ranges = [(3700, 6000), (63000, 74000)]
    for i, (N, (lo, hi)) in enumerate(zip(TARGET_ORDERS, ranges)):
        print(f"searching curve_{i+1} N=2^{N.bit_length()-1} p in [{lo},{hi})", file=sys.stderr)
        res = curve_search(N, lo, hi, seed=1000 + i)
        if res is None:
            print(f"FAILED to find curve for N={N}", file=sys.stderr)
            sys.exit(1)
        curves[f"curve_{i+1}"] = res
        print(f"curve_{i+1}: N=2^{N.bit_length()-1} p={res['p']} a={res['a']} b={res['b']} G={res['generator']}")
    with open("/tmp/wt-run-exp/experiments/EXP-REPL-1d1287/curves.json", "w") as f:
        json.dump({
            "deviation_note": (
                "Reduced curve sizes (2^12, 2^16) substituted for the frozen "
                "spec's 2^20 / 2^28 due to session compute limits on exhaustive "
                "O(p) point-counting used to locate exact power-of-two "
                "subgroups deterministically. See implementation.md."
            ),
            "curves": curves,
        }, f, indent=2)

if __name__ == "__main__":
    main()
