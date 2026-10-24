#!/usr/bin/env python3
"""Sampled independent replay of the attack outcome on producer curves, using only the sealed
blind primitives (hash-checked) plus a leading-digit helper written here.

Anomalous arm (6 curves per seed, 8 samples per lift class):
  canonical (producer's integral A, B), pertA_p (A + p r), pertA_p2 (A + p^2 r):
  v_p(z([p]P^)), v_p(z([p]Q^)), Smart ratio = leading digit of z([p]Q^)/z([p]P^), success = ratio == d.
Torsion arm (4 curves per arm per seed, 12 samples): naive and x-randomised Hensel sections,
  v_p(z([n]s(P))), ratio vs d mod p (the producer's success definition), at precision 4.
Validator seed 6565; d drawn from [2, order-2] as in the frozen drivers.
"""
import hashlib
import importlib.util
import json
import os
import random
import sys

ROOT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
seal = {l.split()[1]: l.split()[0] for l in open(os.path.join(HERE, "blind", "SEAL.sha256")) if len(l.split()) == 2}
src = os.path.join(HERE, "blind", "blind_rederive.py")
assert hashlib.sha256(open(src, "rb").read()).hexdigest() == seal["blind_rederive.py"]
spec = importlib.util.spec_from_file_location("blind", src)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
EXP = "experiments/EXP-CZLIFT-f5e06c"


def z_lead(R, p, N):
    """(v, leading unit digit) of z = -X Z / Y for a Jacobian point in the formal group."""
    X, Y, Z = R
    m = p ** N
    z = (-X * Z * pow(Y, -1, m)) % m  # Y is a unit for points of E_1 in this representation
    v = B.vp(z, p, N)
    return v, (z // p ** v) % p if v < N else None


def lift(p, a, b, x0, y0, N, eps):
    x = (x0 + p * eps) % p ** N
    m = p ** N
    f = (x ** 3 + a * x + b) % m
    y = y0 % m
    for _ in range(N + 2):
        y = (y - (y * y - f) * pow(2 * y, -1, m)) % m
    assert (y * y - f) % m == 0
    return (x, y, 1)


def ratio_trial(p, a, b, P, Q, k, N, eps_P, eps_Q):
    m = p ** N
    Ph = lift(p, a % m, b % m, P[0], P[1], N, eps_P)
    Qh = lift(p, a % m, b % m, Q[0], Q[1], N, eps_Q)
    RP, RQ = B.jmul(k, Ph, a % m, m), B.jmul(k, Qh, a % m, m)
    vP, uP = z_lead(RP, p, N)
    vQ, uQ = z_lead(RQ, p, N)
    if uP is None or vQ < vP:
        return vP, vQ, None
    if vQ > vP:
        return vP, vQ, 0
    return vP, vQ, uQ * pow(uP, -1, p) % p


def fp_mul(k, P, a, p):
    R = B.jmul(k, (P[0], P[1], 1), a % p, p)
    if R is None:
        return None
    X, Y, Z = R
    zi = pow(Z, -1, p)
    return (X * zi * zi % p, Y * zi * zi * zi % p)


rng = random.Random(6565)
out = {}
for run in ("RUN-CZLIFT-032a92", "RUN-CZLIFT-6447f0"):
    raw = json.load(open(os.path.join(ROOT, EXP, "runs", run, "raw-result.json")))["raw"]
    an = rng.sample(raw["curves_anomalous"], 6)
    res_a = {}
    for c in an:
        p, A, Bc = c["p"], c["A"], c["B"]
        for cls in ("canonical", "pertA_p", "pertA_p2"):
            r = rng.randrange(1, p)
            a2 = A if cls == "canonical" else A + (p if cls == "pertA_p" else p * p) * r
            s = res_a.setdefault(cls, {"n": 0, "success": 0, "v": {}, "undefined": 0})
            for _ in range(8):
                P = B.random_point(p, A % p, Bc % p, rng)
                d = rng.randrange(2, p - 1)
                Q = fp_mul(d, P, A, p)
                vP, vQ, ratio = ratio_trial(p, a2, Bc, P, Q, p, 8, rng.randrange(p), rng.randrange(p))
                s["n"] += 1
                s["v"][f"{vP},{vQ}"] = s["v"].get(f"{vP},{vQ}", 0) + 1
                s["undefined"] += ratio is None
                s["success"] += ratio == d
    res_t = {}
    for arm in ("cm_canonical", "random_naive"):
        cs = rng.sample([c for c in raw["curves_torsion"] if c["arm"] == arm], 4)
        for c in cs:
            p, A, Bc, N_, n = c["p"], c["A"], c["B"], c["N"], c["n"]
            h = N_ // n
            for sec in ("naive", "hensel_random"):
                s = res_t.setdefault(f"{arm}/{sec}", {"n": 0, "success": 0, "v": {}, "undefined": 0})
                for _ in range(12):
                    while True:
                        P = fp_mul(h, B.random_point(p, A % p, Bc % p, rng), A, p)
                        if P is not None and P[1] != 0:
                            break
                    d = rng.randrange(2, n - 1)
                    Q = fp_mul(d, P, A, p)
                    e1, e2 = (0, 0) if sec == "naive" else (rng.randrange(p), rng.randrange(p))
                    vP, vQ, ratio = ratio_trial(p, A, Bc, P, Q, n, 4, e1, e2)
                    s["n"] += 1
                    s["v"][f"{vP},{vQ}"] = s["v"].get(f"{vP},{vQ}", 0) + 1
                    s["undefined"] += ratio is None
                    s["success"] += ratio == d % p
    out[run] = {"anomalous_sampled_curves": [(c["D"], c["p"]) for c in an], "anomalous": res_a,
                "torsion": res_t}
json.dump(out, sys.stdout, indent=1)
print()
