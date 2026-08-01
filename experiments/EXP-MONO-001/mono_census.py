#!/usr/bin/env python3
"""EXP-MONO-001 mono_census.py — Chebotarev census of the toy 2-decomposition cover.

For each toy prime p, search small (a,b) for an ordinary curve E/F_p whose group
order #E(F_p) is itself prime (cofactor 1, so every non-identity point generates;
this is the lab's prime-order control). Then census the toy factor-base hit event:

  relation(x1) := [ x1 splits, i.e. x1^3+a*x1+b is a square in F_p ]
                  AND [ x1 in FB_W := { x(r*G) : 1 <= r <= W } ]   (toy factor base)

This is the m=2 shadow of the summation-decomposition event: split-ness is the
Chebotarev/Frobenius condition, orbit membership is the relation condition.
We measure the joint rate against the quasirandom prediction
  P(split) * P(orbit) with Weil error floor ~ 2/sqrt(p),
on random curves where the full-symmetric-group hypothesis predicts delta ~ 0.

Controls:
  positive: x1 forced = x(r*G), r in [1,W]  => relation must fire with rate 1.
  negative: x1 uniform in F_p (no split condition forced) =>
            rate must be ~ |FB_W|/p.
  negative: x1 uniform among splitting x's but orbit window replaced by W random
            x-coordinates => rate must match quasirandom within floor.

Exit 0 iff all controls pass on all curves; deltas are observations, not pass/fail.

Usage: python3 mono_census.py --primes 101 211 431 --seed 20260718 --samples 30000 --window 4
"""
import argparse, json, random, time

def inv(x, p):
    return pow(x % p, p - 2, p)

def add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P != Q:
        m = (y2 - y1) * inv(x2 - x1, p) % p
    else:
        if y1 == 0: return None
        m = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    x3 = (m * m - x1 - x2) % p
    return (x3, (m * (x1 - x3) - y1) % p)

def mul(k, P, a, p):
    R = None
    while k:
        if k & 1: R = add(R, P, a, p)
        P = add(P, P, a, p); k >>= 1
    return R

def legendre(x, p):
    r = pow(x % p, (p - 1) // 2, p)
    return -1 if r == p - 1 else r

def is_prime(n):
    if n < 2: return False
    d = 2
    while d * d <= n:
        if n % d == 0: return False
        d += 1
    return True

def curve_data(a, b, p):
    """Return (#E(F_p), {x: y}, count of rhs==0 x's) by exact enumeration."""
    xs = {}
    n = 1  # point at infinity
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        if rhs == 0:
            n += 1
            xs[x] = 0
        elif legendre(rhs, p) == 1:
            for y in range(p):
                if (y * y) % p == rhs:
                    xs[x] = y
                    break
            n += 2
    return n, xs

def find_prime_order_curve(p, rng):
    for a in range(0, min(p, 12)):
        for b in range(1, min(p, 12)):
            if (4 * a**3 + 27 * b * b) % p == 0:
                continue
            n, xs = curve_data(a, b, p)
            if is_prime(n) and xs:
                x0 = sorted(xs)[0]
                return a, b, n, (x0, xs[x0]), xs
    raise RuntimeError(f"no prime-order curve found for p={p}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primes", nargs="+", type=int, default=[101, 211, 431])
    ap.add_argument("--seed", type=int, default=20260718)
    ap.add_argument("--samples", type=int, default=30000)
    ap.add_argument("--window", type=int, default=4)
    args = ap.parse_args()
    t0 = time.time()
    rng = random.Random(args.seed)
    out = {"experiment": "EXP-MONO-001", "seed": args.seed,
           "samples": args.samples, "window": args.window, "curves": []}
    for p in args.primes:
        a, b, n, G, xs = find_prime_order_curve(p, rng)
        W = args.window
        FB = set()
        P = None
        for r in range(1, W + 1):
            P = add(P, G, a, p)
            FB.add(P[0])
        W_eff = len(FB)  # distinct x's (x(rG)=x(-rG) collisions make it <= W)
        split_xs = sorted(xs)
        N = float(args.samples)
        c_split = c_rel = c_pos = c_neg = c_negshuf = 0
        for _ in range(args.samples):
            x1 = rng.randrange(p)
            s1 = legendre(x1**3 + a*x1 + b, p) == 1
            if s1: c_split += 1
            if s1 and x1 in FB: c_rel += 1
            # positive control: planted orbit member
            r = 1 + rng.randrange(W)
            xp = mul(r, G, a, p)[0]
            if legendre(xp**3 + a*xp + b, p) == 1 and xp in FB: c_pos += 1
            # negative control: uniform x, no split condition
            xu = rng.randrange(p)
            if xu in FB: c_neg += 1
            # negative control: splitting x vs random fake window
            xs_r = split_xs[rng.randrange(len(split_xs))]
            fake_FB = set(rng.sample(range(p), W_eff))
            if xs_r in fake_FB: c_negshuf += 1
        p_split = c_split / N
        pred = p_split * (W_eff / n)
        rec = {
            "p": p, "a": a, "b": b, "group_order": n, "order_is_prime": True,
            "window_W": W, "distinct_window_xs": W_eff,
            "x_split_rate": round(p_split, 6),
            "weil_floor_abs": round(2.0 / (p ** 0.5), 6),
            "relation_rate": round(c_rel / N, 6),
            "quasirandom_prediction": round(pred, 6),
            "delta_vs_quasirandom": round(c_rel / N - pred, 6),
            "positive_control_rate": round(c_pos / N, 6),
            "negative_control_uniform_rate": round(c_neg / N, 6),
            "negative_control_uniform_expected": round(W_eff / p, 6),
            "negative_control_shuffled_rate": round(c_negshuf / N, 6),
        }
        out["curves"].append(rec)
    ok = True
    for rec in out["curves"]:
        if rec["positive_control_rate"] != 1.0: ok = False
        if abs(rec["negative_control_uniform_rate"] - rec["negative_control_uniform_expected"]) > 0.02: ok = False
        if abs(rec["negative_control_shuffled_rate"] - rec["window_W"] / rec["p"]) > 0.03: ok = False
    out["controls_pass"] = ok
    out["runtime_seconds"] = round(time.time() - t0, 3)
    with open("experiments/EXP-MONO-001/smoke_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
