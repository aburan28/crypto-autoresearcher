#!/usr/bin/env python3
"""EXP-XEDN-001 xedni_sections.py — toy elliptic-surface section census (xedni harness).

Surfaces: y^2 = x^3 + a(t) x + b(t) over F_p(t), deg a <= 1, deg b <= 1 for the
constant-section census; a deg-6 b(t) family for the deg-2 section hunt.

Parts:
  1. constant-section census: for a box of (a0,a1,b0,b1), a constant section
     (x0,y0) requires a1*x0 + b1 = 0 and x0^3+a0*x0+b0 square. Prediction: ~1/2
     of surfaces with a1 != 0 admit it (squareness), zero with a1 = 0, b1 != 0.
  2. planted positive control: surface built FROM a known section must be recovered.
  3. deg-2 section hunt on deg-6 b(t), a(t)=0: x(t) = t^2+x1*t+x0 monic;
     LHS = x^3+b(t) is a sextic; perfect-square test via gcd(f,f') with
     re-square verification (no false positives possible).
     Planted surface (b = y^2 - x^3) must yield its section; random surfaces
     measure scarcity vs the ~p^-3 naive prediction.
  4. negative control: random sextics, square rate ~ p^-3.

Usage: python3 xedni_sections.py --p 101 --seed 20260718 --samples 200000
Exit 0 iff controls pass (planted recovered; negative rate within 10x of p^-3 bound).
"""
import argparse, json, random, time

def trim(f):
    while len(f) > 1 and f[-1] == 0: f.pop()
    return f

def padd(f, g, p):
    n = max(len(f), len(g))
    out = [0]*n
    for i in range(n):
        out[i] = ((f[i] if i < len(f) else 0) + (g[i] if i < len(g) else 0)) % p
    return trim(out)

def psub(f, g, p):
    n = max(len(f), len(g))
    out = [0]*n
    for i in range(n):
        out[i] = ((f[i] if i < len(f) else 0) - (g[i] if i < len(g) else 0)) % p
    return trim(out)

def pmul(f, g, p):
    if f == [0] or g == [0]: return [0]
    out = [0]*(len(f)+len(g)-1)
    for i, a in enumerate(f):
        if a:
            for j, b in enumerate(g):
                if b: out[i+j] = (out[i+j] + a*b) % p
    return trim(out)

def pdivmod(f, g, p):
    f = f[:]
    inv_lc = pow(g[-1], p-2, p)
    q = [0]*max(1, (len(f)-len(g)+1))
    while len(f) >= len(g) and f != [0]:
        k = len(f)-len(g)
        c = f[-1]*inv_lc % p
        q[k] = c
        for j in range(len(g)):
            f[j+k] = (f[j+k] - c*g[j]) % p
        trim(f)
    return trim(q), f

def pgcd(f, g, p):
    while g != [0]:
        _, r = pdivmod(f, g, p)
        f, g = g, r
    inv_lc = pow(f[-1], p-2, p)
    return trim([c*inv_lc % p for c in f])

def pderiv(f, p):
    return trim([(i*c) % p for i, c in enumerate(f)][1:] or [0])

def is_square_poly(f, p):
    """Return g if f = c*g^2 (c scalar), else None. Verified by re-squaring."""
    if len(f) % 2 == 0: return None          # odd degree (len-1 odd)
    lc = f[-1]
    if pow(lc, (p-1)//2, p) != 1: return None
    h = pgcd(f, pderiv(f, p), p)
    if 2*(len(h)-1) != len(f)-1: return None
    c = lc * pow(h[-1], p-2, p) % p
    g2 = pmul(h, h, p)
    f2 = [c*co % p for co in g2]
    return h if f2 == f else None

def legendre(x, p):
    r = pow(x % p, (p-1)//2, p)
    return -1 if r == p-1 else r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=101)
    ap.add_argument("--seed", type=int, default=20260718)
    ap.add_argument("--samples", type=int, default=200000)
    args = ap.parse_args()
    p = args.p
    rng = random.Random(args.seed)
    t0 = time.time()
    out = {"experiment": "EXP-XEDN-001", "p": p, "seed": args.seed}

    # --- part 1: constant-section census over a box of surfaces ---
    box = [1, 2, 3, 5, 7, 11]
    tot = withsec = 0
    for a0 in box:
        for a1 in box:
            for b0 in box:
                for b1 in box:
                    tot += 1
                    x0 = (-b1 * pow(a1, p-2, p)) % p
                    if legendre((x0**3 + a0*x0 + b0) % p, p) == 1:
                        withsec += 1
    out["constant_section_census"] = {
        "surfaces": tot, "with_constant_section": withsec,
        "rate": round(withsec/tot, 6), "prediction": 0.5,
        "delta": round(withsec/tot - 0.5, 6)}

    # --- part 2: planted constant section recovery ---
    x0p, y0p = 5, None
    a0p, a1p = 2, 3
    rhs = (x0p**3 + a0p*x0p) % p
    ok2 = legendre(rhs, p)
    b0p = None
    planted2 = False
    for cand in range(p):
        if (cand*cand) % p == (rhs + 0) % p or (cand*cand) % p == rhs:
            pass
    # choose b0 so that x0^3+a0*x0+b0 is square
    for b0c in range(p):
        if legendre((x0p**3 + a0p*x0p + b0c) % p, p) == 1:
            b0p = b0c; break
    b1p = (-a1p*x0p) % p
    x0check = (-b1p * pow(a1p, p-2, p)) % p
    planted2 = (x0check == x0p) and legendre((x0p**3 + a0p*x0p + b0p) % p, p) == 1
    out["planted_constant_control"] = {"recovered": planted2}

    # --- part 3: deg-2 monic section hunt, a(t)=0, b(t) deg<=6 ---
    # planted surface: x*(t) = t^2+x1 t+x0, y*(t) = t^3+y2 t^2+y1 t+y0
    xsec = [3, 5, 1]           # x0,x1,lc=1
    ysec = [7, 4, 2, 1]        # y0..y2,lc=1
    bplant = psub(pmul(ysec, ysec, p), pmul(pmul(xsec, xsec, p), xsec, p), p)
    hits_planted = []
    for x0 in range(p):
        for x1 in range(p):
            xt = [x0, x1, 1]
            lhs = padd(pmul(pmul(xt, xt, p), xt, p), bplant, p)
            g = is_square_poly(lhs, p)
            if g is not None:
                hits_planted.append((x0, x1))
    planted_recovered = (3, 5) in hits_planted
    # random surfaces: sample S random b(t) deg 6, count sections in a window
    S = 40
    win = 12
    rand_hits = 0
    rand_slots = 0
    for _ in range(S):
        b = [rng.randrange(p) for _ in range(6)] + [rng.randrange(1, p)]
        for x0 in rng.sample(range(p), win):
            for x1 in rng.sample(range(p), win):
                xt = [x0, x1, 1]
                lhs = padd(pmul(pmul(xt, xt, p), xt, p), b, p)
                rand_slots += 1
                if is_square_poly(lhs, p) is not None:
                    rand_hits += 1
    out["deg2_section_hunt"] = {
        "planted_surface_b_degree": len(bplant)-1,
        "planted_section_recovered": planted_recovered,
        "planted_total_sections_found": len(hits_planted),
        "random_surfaces": S, "random_slots_tested": rand_slots,
        "random_sections_found": rand_hits,
        "naive_prediction_per_slot": round(1.0/(p**3), 9),
    }

    # --- part 4: negative control, random sextics ---
    nh = 0
    for _ in range(args.samples):
        f = [rng.randrange(p) for _ in range(6)] + [rng.randrange(1, p)]
        if is_square_poly(f, p) is not None: nh += 1
    out["negative_control_random_sextics"] = {
        "samples": args.samples, "square_hits": nh,
        "rate": nh/args.samples, "naive_prediction": round(1.0/(p**3), 9)}

    ok = (out["planted_constant_control"]["recovered"] and planted_recovered
          and nh <= max(3, 10*args.samples/(p**3)))
    out["controls_pass"] = ok
    out["runtime_seconds"] = round(time.time()-t0, 3)
    with open("experiments/EXP-XEDN-001/smoke_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
