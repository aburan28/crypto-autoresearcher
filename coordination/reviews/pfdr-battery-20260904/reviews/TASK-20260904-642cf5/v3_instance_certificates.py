#!/usr/bin/env python3
"""V3: instance and certificate checks on the 12 declared deciding-cell instances.

My own F_p and elliptic-curve arithmetic; no producer code, no summand read from
any raw record.  For each declared (p, a, b, x_R):
  * 4a^3 + 27b^2 != 0 mod p (non-singular) and a, b != 0 (j not in {0, 1728});
  * enumerate on-curve x in the planting window [0, 4);
  * over every pair of window points and every sign choice, compute x(P1 + P2)
    and test whether x_R is among the values -- an independent decomposition
    certificate that needs no summand from the producer's record.
"""
import json, sys, itertools

def legendre(n, p):
    n %= p
    if n == 0: return 0
    return 1 if pow(n, (p - 1) // 2, p) == 1 else -1

def sqrts(n, p):
    n %= p
    if n == 0: return [0]
    if legendre(n, p) != 1: return []
    if p % 4 == 3:
        r = pow(n, (p + 1) // 4, p)
    else:                                  # Tonelli-Shanks
        q, s = p - 1, 0
        while q % 2 == 0: q //= 2; s += 1
        z = 2
        while legendre(z, p) != -1: z += 1
        m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
        while t != 1:
            i, t2 = 0, t
            while t2 != 1: t2 = t2 * t2 % p; i += 1
            bb = pow(c, 1 << (m - i - 1), p)
            m, c = i, bb * bb % p
            t = t * c % p
            r = r * bb % p
    assert r * r % p == n
    return sorted({r, (-r) % p})

def add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q:
        if y1 == 0: return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

INSTANCES = [
    (4099, 1101, 527, 72, 1, 2374), (4099, 1101, 527, 72, 2, 934),
    (4099, 1102, 1592, 55, 1, 1885), (4099, 1102, 1592, 55, 2, 3861),
    (4099, 1103, 3191, 1819, 1, 3717), (4099, 1103, 3191, 1819, 2, 2737),
    (65537, 1101, 5623, 46432, 1, 42063), (65537, 1101, 5623, 46432, 2, 3344),
    (65537, 1102, 703, 52025, 1, 47098), (65537, 1102, 703, 52025, 2, 35614),
    (65537, 1103, 61835, 65393, 1, 47685), (65537, 1103, 61835, 65393, 2, 47685),
]
WINDOW = range(0, 4)
out = []
for (p, cseed, a, b, tseed, xR) in INSTANCES:
    disc = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    pts = []
    for x in WINDOW:
        rhs = (pow(x, 3, p) + a * x + b) % p
        for y in sqrts(rhs, p):
            pts.append((x % p, y))
    sums = {}
    for i in range(len(pts)):
        for j in range(i, len(pts)):
            S = add(pts[i], pts[j], a, p)
            if S is not None:
                sums.setdefault(S[0], []).append((pts[i], pts[j]))
    witness = sums.get(xR % p, [])
    # also: is x_R itself in the window (a degenerate "decomposition")?
    out.append({
        "p": p, "curve_seed": cseed, "a": a, "b": b, "target_seed": tseed, "x_R": xR,
        "discriminant_4a3_27b2_mod_p": disc, "non_singular": disc != 0,
        "a_nonzero": a % p != 0, "b_nonzero": b % p != 0,
        "j_not_0_or_1728": (a % p != 0 and b % p != 0),
        "window_x_on_curve": sorted({x for x, _ in pts}),
        "n_window_points_with_sign": len(pts),
        "at_least_two_window_x": len({x for x, _ in pts}) >= 2,
        "n_distinct_pair_sum_x": len(sums),
        "x_R_is_a_window_pair_sum": bool(witness),
        "witness_pair": [[list(P), list(Q)] for P, Q in witness[:2]],
    })

print(f"{'p':>6} {'cseed':>5} {'t':>2} {'x_R':>6}  nonsing  a,b!=0  window_x        #pts  #sums  x_R is pair sum  witness")
for r in out:
    w = r["witness_pair"][0] if r["witness_pair"] else None
    print(f"{r['p']:6d} {r['curve_seed']:5d} {r['target_seed']:2d} {r['x_R']:6d}  "
          f"{str(r['non_singular']):7s} {str(r['j_not_0_or_1728']):6s} {str(r['window_x_on_curve']):15s} "
          f"{r['n_window_points_with_sign']:4d} {r['n_distinct_pair_sum_x']:6d}  {str(r['x_R_is_a_window_pair_sum']):15s} {w}")
print()
print("all non-singular:", all(r["non_singular"] for r in out))
print("all a,b nonzero (j not 0 or 1728):", all(r["j_not_0_or_1728"] for r in out))
print("all have >= 2 distinct on-curve window x:", all(r["at_least_two_window_x"] for r in out))
print("all x_R are window-pair sums (decomposition certificate):", all(r["x_R_is_a_window_pair_sum"] for r in out))
for p in (4099, 65537):
    xs = [r["x_R"] for r in out if r["p"] == p]
    print(f"p={p}: {len(xs)} declared instances, {len(set(zip([r['curve_seed'] for r in out if r['p']==p], xs)))} distinct (curve, x_R) pairs, x_R values {xs}")
allpairs = {(r["p"], r["a"], r["b"], r["x_R"]) for r in out}
print("distinct (p, a, b, x_R) instances among the 12 declared:", len(allpairs))
json.dump(out, open("/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5/v3_instance_table.json", "w"), indent=1)
