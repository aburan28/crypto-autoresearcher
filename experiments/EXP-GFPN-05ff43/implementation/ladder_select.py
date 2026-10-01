#!/usr/bin/env python3
"""Ladder prime + curve selection for EXP-GFPN-05ff43 (deterministic).

Primes p' are chosen as the smallest prime >= 2^k (k in TARGET_BITS) with
p' = 1 (mod 5) (needed for z^5 - c to be irreducible over F_p'), primality
proved by PARI isprime (APR-CL / ECPP proof) and re-checked here by trial
division (p' < 2^31).  The field modulus is z^5 - cmod with cmod the smallest
positive integer that is not a 5th power mod p'.

Curves over F_q = F_{p'^5}, searched deterministically from seed 2026092002:
  ecgfp5_shaped:      y^2 = x(x^2 + 2x + c z), c = 1, 2, ...; first c with
                      #E = 2 * prime is taken (order via PARI ellcard, primality
                      via PARI isprime).  Also records whether b = c z is a
                      square in F_q (FHJRV Prop. 8 condition).
  random_2torsion:    y^2 = x(x^2 + a x + b), a, b random in F_q from the seeded
                      stream; first with #E = 2 * prime.
  random_no2torsion:  y^2 = x^3 + a x + b, a, b random, x^3 + a x + b irreducible
                      over F_q (no rational 2-torsion); first with #E prime.
Bounded search (MAX_TRIES); if no 2*prime / prime order is found the smallest
cofactor seen is taken and recorded (contract allows a recorded cofactor).
"""
import json, random, sys, time
import cypari2
pari = cypari2.Pari()
pari.allocatemem(2 * 10**9)

TARGET_BITS = [12, 18, 24, 30]
MAX_TRIES = int(__import__("os").environ.get("GFPN_MAX_TRIES", "400"))
SEED_CURVES = 2026092002

def is_prime_trial(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True

def pick_prime(bits):
    p = 2 ** bits
    while True:
        p = int(pari.nextprime(p))
        if p % 5 == 1 and is_prime_trial(p) and int(pari.isprime(p)) == 1:
            return p
        p += 1

def pick_cmod(p):
    c = 2
    while pow(c, (p - 1) // 5, p) == 1:
        c += 1
    return c

def fq_setup(p, cmod):
    pari(f"gfield = ffgen(Mod(1,{p})*(z^5-{cmod}), 'z)")

def ellcard(p, a2, a4, a6):
    """Order of y^2 = x^3 + a2 x^2 + a4 x + a6 over F_q; coefficients as F_p-coefficient lists."""
    def elt(cs):
        return "(" + "+".join(f"{c}*gfield^{i}" for i, c in enumerate(cs)) + ")"
    N = pari(f"ellcard(ellinit([0, {elt(a2)}, 0, {elt(a4)}, {elt(a6)}], gfield))")
    return int(N)

def is_square_fq(cs):
    def elt(cs):
        return "(" + "+".join(f"{c}*gfield^{i}" for i, c in enumerate(cs)) + ")"
    return int(pari(f"issquare({elt(cs)})")) == 1

def cubic_irreducible(a4, a6):
    def elt(cs):
        return "(" + "+".join(f"{c}*gfield^{i}" for i, c in enumerate(cs)) + ")"
    return int(pari(f"polisirreducible(x^3 + {elt(a4)}*x + {elt(a6)})")) == 1

def factor_cofactor(N):
    """Return (cofactor, largest prime factor) using PARI factor (N < 2^160, fine)."""
    f = pari.factor(N)
    primes = [int(f[0][i]) for i in range(len(f[0]))]
    exps = [int(f[1][i]) for i in range(len(f[1]))]
    big = max(primes)
    cof = N // big
    return cof, big, [(pp, e) for pp, e in zip(primes, exps)]

def select(bits):
    p = pick_prime(bits); cmod = pick_cmod(p); fq_setup(p, cmod)
    rng = random.Random(f"{SEED_CURVES}:ladder:{p}")
    out = {"bits_target": bits, "p": p, "p_bits": p.bit_length(), "cmod": cmod,
           "field": f"F_{p}[z]/(z^5 - {cmod})", "seed_stream": f"random.Random('{SEED_CURVES}:ladder:{p}')",
           "curves": {}}
    # EcGFp5-shaped
    best = None
    for c in range(1, MAX_TRIES + 1):
        N = ellcard(p, [2], [0, c], [0])
        cof, big, fac = factor_cofactor(N)
        if best is None or cof < best["cofactor"]:
            best = {"c": c, "order": N, "cofactor": cof, "subgroup_prime": big, "factorization": fac}
        if cof == 2:
            break
    b_sq = is_square_fq([0, best["c"]])
    out["curves"]["ecgfp5_shaped"] = {"model": f"y^2 = x(x^2 + 2x + {best['c']}*z)", "a2": [2], "a4": [0, best["c"]], "a6": [0],
                                      "tries": best["c"], "b_is_square_in_Fq": b_sq, "has_rational_2torsion": True, **best}
    # random with 2-torsion: y^2 = x(x^2 + a x + b)
    best = None
    for t in range(1, MAX_TRIES + 1):
        a = [rng.randrange(p) for _ in range(5)]; b = [rng.randrange(p) for _ in range(5)]
        N = ellcard(p, a, b, [0])
        cof, big, fac = factor_cofactor(N)
        if best is None or cof < best["cofactor"]:
            best = {"a2": a, "a4": b, "a6": [0], "order": N, "cofactor": cof, "subgroup_prime": big, "factorization": fac, "tries": t}
        if cof == 2:
            break
    best["b_is_square_in_Fq"] = is_square_fq(best["a4"])
    out["curves"]["random_2torsion"] = {"model": "y^2 = x(x^2 + a x + b), a,b random in F_q", "has_rational_2torsion": True, **best}
    # random without 2-torsion: y^2 = x^3 + a x + b, cubic irreducible
    best = None
    for t in range(1, MAX_TRIES + 1):
        a = [rng.randrange(p) for _ in range(5)]; b = [rng.randrange(p) for _ in range(5)]
        if not cubic_irreducible(a, b):
            continue
        N = ellcard(p, [0], a, b)
        cof, big, fac = factor_cofactor(N)
        if best is None or cof < best["cofactor"]:
            best = {"a2": [0], "a4": a, "a6": b, "order": N, "cofactor": cof, "subgroup_prime": big, "factorization": fac, "tries": t}
        if cof == 1:
            break
    out["curves"]["random_no2torsion"] = {"model": "y^2 = x^3 + a x + b, a,b random in F_q, cubic irreducible", "has_rational_2torsion": False, **best}
    return out

if __name__ == "__main__":
    bits = [int(b) for b in sys.argv[1:]] or TARGET_BITS
    res = []
    for b in bits:
        t = time.time()
        r = select(b); r["selection_seconds"] = round(time.time() - t, 2)
        res.append(r)
        print(json.dumps(r), flush=True)
    json.dump(res, open("ladder.json", "w"), indent=1)
