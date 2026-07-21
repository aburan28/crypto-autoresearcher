#!/usr/bin/env python3
"""EXP-IMON-001 imon_group.py — monodromy census harness (two-sided: C2 attack / D2 barrier).

Parts:
  1. m=2 decomposition cover census: exact counts of split / inert / ramified
     factorization types of T^2 - (x1^3+a*x1+b) over all x1 in F_p, on a
     prime-order ordinary curve. Chebotarev(S2) prediction: 1/2 split, 1/2 inert,
     up to Weil error 2/sqrt(p).
  2. joint census: split-type independence over all pairs (x1,x2) — the
     quasirandomness test relevant to relation events.
  3. positive control (imprimitivity detection): product cover f = g2*g3 with
     random deg-2, deg-3 factors. Its factorization types can never include a
     5-cycle or a 4+1 type, unlike full S5 — the harness must flag it NON-FULL.
  4. negative control: random deg-5 polynomials; Chebotarev(S5) predicts 5-cycles
     at rate 1/5 and 4+1 at 1/4 — the harness must flag FULL-consistent.

Usage: python3 imon_group.py --p 101 --seed 20260718 --samples 20000
Exit 0 iff: control 3 flagged non-full AND control 4 not flagged non-full.
"""
import argparse, json, random, time
from collections import Counter

def legendre(x, p):
    r = pow(x % p, (p-1)//2, p)
    return -1 if r == p-1 else r

def is_prime(n):
    if n < 2: return False
    d = 2
    while d*d <= n:
        if n % d == 0: return False
        d += 1
    return True

def curve_prime_order(p):
    for a in range(0, min(p, 12)):
        for b in range(1, min(p, 12)):
            if (4*a**3 + 27*b*b) % p == 0: continue
            n = 1
            for x in range(p):
                rhs = (x**3 + a*x + b) % p
                if rhs == 0: n += 1
                elif legendre(rhs, p) == 1: n += 2
            if is_prime(n): return a, b, n
    raise RuntimeError("no prime-order curve")

def factor_degrees_monic(f, p):
    """Factorization degree pattern of monic poly f over F_p (toy: root scan + recursion)."""
    f = f[:]
    degs = []
    # strip linear factors
    while True:
        root = None
        for r in range(p):
            if evalpoly(f, r, p) == 0:
                root = r; break
        if root is None: break
        degs.append(1)
        f = pdiv(f, [(-root) % p, 1], p)
    d = len(f) - 1
    if d >= 2:
        if d == 2:
            # irreducible iff no root (roots already stripped)
            degs.append(2)
        elif d == 3:
            degs.append(3)  # no roots => irreducible cubic
        elif d == 4:
            # could be 4, or 2+2: test irreducible-quadratic factor by brute force
            found = False
            for c0 in range(p):
                for c1 in range(p):
                    q = [c0, c1, 1]
                    r = pmod(f, q, p)
                    if r == [0]:
                        degs.extend([2, 2]); found = True; break
                if found: break
            if not found: degs.append(4)
        elif d == 5:
            # no linear roots; could be 5 or 2+3
            found = False
            for c0 in range(p):
                for c1 in range(p):
                    q = [c0, c1, 1]
                    if pmod(f, q, p) == [0]:
                        degs.extend([2, 3]); found = True; break
                if found: break
            if not found: degs.append(5)
    return tuple(sorted(degs))

def evalpoly(f, x, p):
    v = 0
    for c in reversed(f): v = (v*x + c) % p
    return v

def pdiv(f, g, p):
    f = f[:]
    inv_lc = pow(g[-1], p-2, p)
    q = [0]*max(1, (len(f)-len(g)+1))
    while len(f) >= len(g) and f != [0]:
        k = len(f)-len(g)
        c = f[-1]*inv_lc % p
        q[k] = c
        for j in range(len(g)):
            f[j+k] = (f[j+k] - c*g[j]) % p
        while len(f) > 1 and f[-1] == 0: f.pop()
    return q

def pmod(f, g, p):
    f = f[:]
    inv_lc = pow(g[-1], p-2, p)
    while len(f) >= len(g) and f != [0]:
        k = len(f)-len(g)
        c = f[-1]*inv_lc % p
        for j in range(len(g)):
            f[j+k] = (f[j+k] - c*g[j]) % p
        while len(f) > 1 and f[-1] == 0: f.pop()
    return f

def pmul(f, g, p):
    out = [0]*(len(f)+len(g)-1)
    for i, a in enumerate(f):
        if a:
            for j, b in enumerate(g):
                if b: out[i+j] = (out[i+j] + a*b) % p
    while len(out) > 1 and out[-1] == 0: out.pop()
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=101)
    ap.add_argument("--seed", type=int, default=20260718)
    ap.add_argument("--samples", type=int, default=20000)
    args = ap.parse_args()
    p = args.p
    rng = random.Random(args.seed)
    t0 = time.time()
    out = {"experiment": "EXP-IMON-001", "p": p, "seed": args.seed}

    # --- parts 1+2: curve census ---
    a, b, n = curve_prime_order(p)
    split = inert = ram = 0
    for x1 in range(p):
        rhs = (x1**3 + a*x1 + b) % p
        l = legendre(rhs, p)
        if l == 1: split += 1
        elif l == -1: inert += 1
        else: ram += 1
    joint = 0
    for x1 in range(p):
        s1 = legendre((x1**3 + a*x1 + b) % p, p) == 1
        if not s1: continue
        for x2 in range(p):
            if legendre((x2**3 + a*x2 + b) % p, p) == 1:
                joint += 1
    sr = split/p
    out["curve_cover"] = {
        "a": a, "b": b, "group_order": n, "order_is_prime": True,
        "split": split, "inert": inert, "ramified": ram,
        "split_rate": round(sr, 6),
        "chebotarev_S2_prediction": 0.5,
        "delta_vs_S2": round(sr - 0.5, 6),
        "weil_floor_abs": round(2.0/(p**0.5), 6),
        "joint_split_rate": round(joint/(p*p), 6),
        "independence_prediction": round(sr*sr, 6),
        "joint_delta": round(joint/(p*p) - sr*sr, 6),
    }

    # --- part 3: product-cover positive control ---
    g2 = [rng.randrange(p), rng.randrange(p), 1]
    g3 = [rng.randrange(p), rng.randrange(p), rng.randrange(p), 1]
    fprod = pmul(g2, g3, p)
    prod_types = Counter()
    NS = 400
    for _ in range(NS):
        g2 = [rng.randrange(p), rng.randrange(p), 1]
        g3 = [rng.randrange(p), rng.randrange(p), rng.randrange(p), 1]
        prod_types[factor_degrees_monic(pmul(g2, g3, p), p)] += 1
    nonfull_flag_control = ((5,) not in prod_types) and ((1, 4) not in prod_types)
    out["product_cover_control"] = {
        "samples": NS,
        "observed_types": {str(k): v for k, v in sorted(prod_types.items())},
        "flagged_non_full": nonfull_flag_control,
    }

    # --- part 4: random deg-5 negative control ---
    rand_types = Counter()
    for _ in range(args.samples):
        f = [rng.randrange(p) for _ in range(5)] + [1]
        rand_types[factor_degrees_monic(f, p)] += 1
    tot = args.samples
    five = rand_types.get((5,), 0)/tot
    four1 = rand_types.get((1, 4), 0)/tot
    out["random_deg5_control"] = {
        "samples": tot,
        "observed_types": {str(k): v for k, v in sorted(rand_types.items())},
        "five_cycle_rate": round(five, 6), "chebotarev_S5_5cycle": 0.2,
        "four_plus_one_rate": round(four1, 6), "chebotarev_S5_4plus1": 0.25,
        "flagged_full_consistent": abs(five - 0.2) < 0.05 and abs(four1 - 0.25) < 0.06,
    }

    ok = (nonfull_flag_control and out["random_deg5_control"]["flagged_full_consistent"])
    out["controls_pass"] = ok
    out["runtime_seconds"] = round(time.time()-t0, 3)
    with open("experiments/EXP-IMON-001/smoke_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
