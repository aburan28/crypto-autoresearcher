#!/usr/bin/env python3
"""Blind re-derivation for TASK-20261022-65e6c1 (EXP-CZLIFT-f5e06c), phase 1 (joint J3).

Written from experiments/EXP-CZLIFT-f5e06c/specification.yaml, trial-plan.json,
ledger/hypotheses/H-CZLIFT-bd2017.yaml and general mathematics only. Imports
nothing from harness/ or any experiment implementation.

Quantity (review_plan.blind_rederivation):
  (a) anomaly #E(F_p) = p of three sampled curves by an own point count;
  (b) v_p(z([p]P^)) on the canonical and pert_p lifts of one of them.

Interpretation choices (the specification does not define them; recorded as
findings, not resolved by reading producer code):
  * sampler: class-number-one CM curves with odd fundamental discriminant
    D in {-3,-11,-19,-43,-67,-163} (the only class-number-one maximal orders
    admitting a trace-1 Frobenius of odd prime norm; -7 is excluded, see CM_J), p = (1 + |D| v^2)/4 prime in [10^4, 10^5], twist with
    trace exactly 1. Seeded by the spec's first seed.
  * canonical lift: the CM curve over Q itself (integer coefficients of the
    model, or of its integer twist), read in Z_p. By Deuring/Serre-Tate a CM
    curve over Q with ordinary good reduction at p is the canonical lift of its
    reduction. Coefficients are NOT reduced to [0,p) first.
  * pert_p: canonical lift with one coefficient moved by p
    (pertA: a -> a + p, pertB: b -> b + p). pert_p2 (a -> a + p^2) is carried as
    a positive control of the mod-p^2 rule.
  * z = -x/y; [p]P^ computed in Jacobian coordinates mod p^N, P^ = (x0, Hensel
    lift of y0) with x0 in [0,p).
Theory prediction (general mathematics): canonical lift => E^(Q_p) has a
rational p-torsion point (lift of the etale kernel), so [p]P^ lies in E_2,
v >= 2 for every P^; a lift not congruent to the canonical one mod p^2 has
E^(Q_p) torsion-free, so v = 1 exactly for every P != O.
"""
import json
import random
import sys

PMIN, PMAX = 10_000, 100_000
SEED = 20261009
N_PREC = (8, 16)

# D = -7 is excluded: (1 + 7 v^2)/4 is even for every odd v (2 splits in Q(sqrt -7)),
# so no prime p > 2 carries a trace-1 Frobenius of discriminant -7.
CM_J = {-3: 0, -11: -32768, -19: -884736, -43: -884736000,
        -67: -147197952000, -163: -262537412640768000}


def is_prime(n):
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


def sqrt_mod(a, p):
    """Tonelli-Shanks; returns r with r^2 = a mod p, or None."""
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


def count_points(p, a, b):
    """#E(F_p) for y^2 = x^3 + a x + b by a table of squares (no Euler criterion)."""
    a %= p
    b %= p
    nsq = [0] * p  # number of y with y^2 = v
    for y in range(p):
        nsq[y * y % p] += 1
    total = 1  # point at infinity
    for x in range(p):
        total += nsq[(x * x * x + a * x + b) % p]
    return total


# ---- Jacobian arithmetic mod m on y^2 = x^3 + a x + b -------------------------
INF = None


def jdbl(P, a, m):
    if P is INF:
        return INF
    X, Y, Z = P
    if Y % m == 0:
        return INF
    YY = Y * Y % m
    S = 4 * X * YY % m
    ZZ = Z * Z % m
    M = (3 * X * X + a * ZZ * ZZ) % m
    X3 = (M * M - 2 * S) % m
    Y3 = (M * (S - X3) - 8 * YY * YY) % m
    Z3 = 2 * Y * Z % m
    return (X3, Y3, Z3)


def jadd(P, Q, a, m):
    if P is INF:
        return Q
    if Q is INF:
        return P
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    Z1Z1, Z2Z2 = Z1 * Z1 % m, Z2 * Z2 % m
    U1, U2 = X1 * Z2Z2 % m, X2 * Z1Z1 % m
    S1, S2 = Y1 * Z2 * Z2Z2 % m, Y2 * Z1 * Z1Z1 % m
    H, r = (U2 - U1) % m, (S2 - S1) % m
    if H == 0:
        if r == 0:
            return jdbl(P, a, m)
        return INF
    HH = H * H % m
    HHH = H * HH % m
    V = U1 * HH % m
    X3 = (r * r - HHH - 2 * V) % m
    Y3 = (r * (V - X3) - S1 * HHH) % m
    Z3 = H * Z1 * Z2 % m
    return (X3, Y3, Z3)


def jmul(k, P, a, m):
    R = INF
    for bit in bin(k)[2:]:
        R = jdbl(R, a, m)
        if bit == '1':
            R = jadd(R, P, a, m)
    return R


def vp(n, p, cap):
    if n == 0:
        return cap
    v = 0
    while n % p == 0 and v < cap:
        n //= p
        v += 1
    return v


def vz_of(R, p, N):
    """v_p of z = -x/y = -X Z / Y for a Jacobian point known mod p^N."""
    if R is INF:
        return {"v": None, "note": "point at infinity to precision"}
    X, Y, Z = R
    vX, vY, vZ = vp(X, p, N), vp(Y, p, N), vp(Z, p, N)
    val = vX + vZ - vY
    return {"v": val, "vX": vX, "vY": vY, "vZ": vZ,
            "capped": (vZ >= N) or (vX >= N) or (vY >= N)}


def hensel_y(p, a, b, x0, y0, N):
    m = p ** N
    f = (x0 ** 3 + a * x0 + b) % m
    y = y0 % m
    for _ in range(N.bit_length() + 2):
        y = (y - (y * y - f) * pow(2 * y, -1, m)) % m
    assert (y * y - f) % m == 0
    return y


def vz_mult_p(p, a_lift, b_lift, x0, y0, N):
    """v_p(z([p]P^)) by two different addition chains."""
    m = p ** N
    a, b = a_lift % m, b_lift % m
    y = hensel_y(p, a, b, x0, y0, N)
    P = (x0 % m, y, 1)
    R1 = jmul(p, P, a, m)                       # left-to-right binary
    h = (p - 1) // 2
    R2 = jadd(jmul(h + 1, P, a, m), jmul(h, P, a, m), a, m)  # (p+1)/2 P + (p-1)/2 P
    return vz_of(R1, p, N), vz_of(R2, p, N)


def random_point(p, a, b, rng):
    while True:
        x = rng.randrange(p)
        y = sqrt_mod(x ** 3 + a * x + b, p)
        if y not in (None, 0):
            return x, y


def order_p_test(p, a, b, rng, trials=3):
    """Group-order evidence independent of the count: [p]P = O for random P."""
    for _ in range(trials):
        x, y = random_point(p, a % p, b % p, rng)
        if jmul(p, (x, y, 1), a % p, p) is not INF:
            return False
    return True


def model(D):
    j = CM_J[D]
    if j == 0:
        return 0, 1
    k = 1728 - j
    return 3 * j * k, 2 * j * k * k


def least_nonresidue(p):
    n = 2
    while pow(n, (p - 1) // 2, p) != p - 1:
        n += 1
    return n


def anomalous_twist(D, p, rng):
    """Integer CM model (canonical lift over Z) whose reduction has trace 1."""
    A, B = model(D)
    if D == -3:
        cands = [(0, d) for d in range(1, 64)]
    else:
        n = least_nonresidue(p)
        cands = [(A, B), (A * n * n, B * n ** 3)]
    for (a, b) in cands:
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            continue
        if not order_p_test(p, a, b, rng):
            continue
        return a, b
    return None


def sample_curves(seed, count=3):
    rng = random.Random(seed)
    Ds = rng.sample(sorted(CM_J), count)
    out = []
    for D in Ds:
        aD = -D
        lo = 1
        while (1 + aD * lo * lo) // 4 < PMIN:
            lo += 1
        hi = lo
        while (1 + aD * (hi + 1) ** 2) // 4 <= PMAX:
            hi += 1
        vs = [v for v in range(lo, hi + 1) if v % 2 == 1
              and (1 + aD * v * v) % 4 == 0
              and PMIN <= (1 + aD * v * v) // 4 <= PMAX
              and is_prime((1 + aD * v * v) // 4)]
        v = rng.choice(vs)
        p = (1 + aD * v * v) // 4
        tw = anomalous_twist(D, p, rng)
        out.append({"D": D, "j": CM_J[D], "v": v, "p": p, "a_lift": tw[0], "b_lift": tw[1]})
    return out, rng


def main():
    curves, rng = sample_curves(SEED)
    report = {"seed": SEED, "prime_range": [PMIN, PMAX], "curves": []}
    for c in curves:
        p = c["p"]
        n = count_points(p, c["a_lift"], c["b_lift"])
        c["a_mod_p"], c["b_mod_p"] = c["a_lift"] % p, c["b_lift"] % p
        c["count"] = n
        c["anomalous"] = (n == p)
        c["order_p_test"] = order_p_test(p, c["a_lift"], c["b_lift"], rng, trials=5)
        c["a_lift"], c["b_lift"] = str(c["a_lift"]), str(c["b_lift"])
        report["curves"].append(c)
    # lifts on every curve; the card asks for one, the rest are extra
    for c in report["curves"]:
        p = c["p"]
        A, B = int(c["a_lift"]), int(c["b_lift"])
        lifts = {
            "canonical": (A, B),
            "pertA_p": (A + p, B),
            "pertB_p": (A, B + p),
            "pertA_p2_control": (A + p * p, B),
            "canonical_reduced_coeffs_trap": (A % p, B % p),
        }
        pts = [random_point(p, A % p, B % p, rng) for _ in range(3)]
        c["points"] = pts
        res = {}
        for name, (a, b) in lifts.items():
            res[name] = {}
            for N in N_PREC:
                vals = []
                for (x0, y0) in pts:
                    r1, r2 = vz_mult_p(p, a, b, x0, y0, N)
                    vals.append({"chain_binary": r1, "chain_halves": r2})
                res[name][f"N={N}"] = vals
        c["v_p_z_pP"] = res
        c["v_summary"] = {name: sorted({vv["chain_binary"]["v"] for vv in res[name][f"N={N_PREC[1]}"]}
                                         | {vv["chain_halves"]["v"] for vv in res[name][f"N={N_PREC[1]}"]})
                          for name in lifts}
    json.dump(report, sys.stdout, indent=1, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
