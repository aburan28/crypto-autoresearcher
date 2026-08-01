#!/usr/bin/env python3
"""EXP-ISADV-001 advice_transfer.py — cross-isogeny advice transport probe (toy).

Question: does a distinguished-x advice table planted on one curve help hit targets
on an isogenous classmate (same #E(F_p)) beyond the baseline rate |advice|/p?

Toy model: an "advice hit" on target point R means x(R) lies in the advice set,
i.e. the target would be recoverable from the table. Plant advice on E0 as the
x-coordinates of k*G0 for k in [1,W]. Measure:
  - positive control: targets drawn as k*G0, k in [1,W], on E0 (hit rate must be 1);
  - relabeled control: targets k*G0 with k OUTSIDE [1,W] on E0 (rate ~ |advice|/p);
  - transfer: targets k*Gi on classmate Ei (honest: rate ~ |advice|/p if no transfer);
  - negative control: uniform random x on Ei (rate ~ |advice|/p).
Exit 0 iff controls behave; the transfer delta is an observation.

Usage: python3 advice_transfer.py --primes 101 211 431 --seed 20260718 --samples 372 --window 8
"""
import argparse, json, random, time

def inv(x, p): return pow(x % p, p - 2, p)

def add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P != Q: m = (y2 - y1) * inv(x2 - x1, p) % p
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

def curve_points_count(a, b, p):
    n = 1
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        if rhs == 0: n += 1
        elif legendre(rhs, p) == 1: n += 2
    return n

def find_isogeny_class(p, min_size=3):
    """Group small curves by #E (same trace => isogenous over F_p); return a class."""
    by_order = {}
    for a in range(0, min(p, 30)):
        for b in range(1, min(p, 30)):
            if (4*a**3 + 27*b*b) % p == 0: continue
            n = curve_points_count(a, b, p)
            t = p + 1 - n
            if t % p == 0: continue          # supersingular, exclude
            if not is_prime(n): continue     # prime-order control
            by_order.setdefault(n, []).append((a, b))
    for n, members in sorted(by_order.items(), key=lambda kv: -len(kv[1])):
        if len(members) >= min_size:
            return n, members[:6]
    raise RuntimeError(f"no suitable class for p={p}")

def first_point(a, b, p):
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        if legendre(rhs, p) == 1:
            for y in range(p):
                if (y*y) % p == rhs: return (x, y)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primes", nargs="+", type=int, default=[101, 211, 431])
    ap.add_argument("--seed", type=int, default=20260718)
    ap.add_argument("--samples", type=int, default=372)
    ap.add_argument("--window", type=int, default=8)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    t0 = time.time()
    out = {"experiment": "EXP-ISADV-001", "seed": args.seed,
           "samples": args.samples, "window": args.window, "classes": []}
    for p in args.primes:
        n, members = find_isogeny_class(p)
        E0 = members[0]
        G0 = first_point(*E0, p)
        W = args.window
        advice = set()
        P = None
        for k in range(1, W + 1):
            P = add(P, G0, E0[0], p)
            advice.add(P[0])
        baseline = len(advice) / p
        rec = {"p": p, "class_order": n, "class_members": len(members),
               "advice_size": len(advice), "baseline_rate": round(baseline, 6),
               "weil_floor_abs": round(2.0 / (p ** 0.5), 6), "curves": []}
        for idx, (a, b) in enumerate(members):
            G = first_point(a, b, p)
            pos = rel = tr = neg = 0
            for _ in range(args.samples):
                k = 1 + rng.randrange(W)
                xT = mul(k, G, a, p)[0]
                if xT in advice: pos += 1                      # on-curve planted window
                k2 = W + 1 + rng.randrange(max(1, n - W - 1))
                xT2 = mul(k2, G, a, p)[0]
                if xT2 in advice: rel += 1                     # relabeled (out-of-window)
                k3 = 1 + rng.randrange(n - 1)
                xT3 = mul(k3, G, a, p)[0]
                if xT3 in advice: tr += 1                      # honest transfer sample
                xu = rng.randrange(p)
                if xu in advice: neg += 1                      # negative control
            rec["curves"].append({
                "member_index": idx, "a": a, "b": b,
                "positive_control_rate": round(pos / args.samples, 6),
                "relabeled_rate": round(rel / args.samples, 6),
                "transfer_hit_rate": round(tr / args.samples, 6),
                "transfer_delta_vs_baseline": round(tr / args.samples - baseline, 6),
                "negative_control_rate": round(neg / args.samples, 6),
            })
        out["classes"].append(rec)
    ok = True
    for rec in out["classes"]:
        c0 = rec["curves"][0]
        if c0["positive_control_rate"] != 1.0: ok = False
        for c in rec["curves"]:
            if abs(c["negative_control_rate"] - rec["baseline_rate"]) > 0.05: ok = False
    out["controls_pass"] = ok
    out["runtime_seconds"] = round(time.time() - t0, 3)
    with open("experiments/EXP-ISADV-001/smoke_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
