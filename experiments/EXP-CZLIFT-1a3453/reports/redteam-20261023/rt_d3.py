#!/usr/bin/env python3
"""Red team TASK-20261023-792040, joint R2: is the shuffled control contaminated by the D = -3 structure?

Own arithmetic, independent of the producer and of the validator's lift:
  * projective complete addition (Renes-Costello-Batina 2016, Alg. 1, general a)
    over Z/p^5, tested against affine F_p addition before use;
  * the torsion lift by the group-order route T1 = [c] P^, c = 1 mod n,
    c = 0 mod p^4 (E(Z/p^5) = E(F_p) x formal part of order p^4), for any Hensel
    lift P^; certified by T1 = P mod p and [n] T1 = O, then compared with the
    validator's recorded T1 (j2_replay_output.json) so the series is the
    producer's series (same generator P);
  * T_k = [k] T1 by successive addition; digits of y(T_k) mod p^5.
Then, on every power-bearing D = -3 record, for y digits 1..4:
  (a) the automorphism identity y(T_{lambda k}) = y(T_k), lambda^2 + lambda + 1 = 0 mod n;
  (b) real series: DC (trivial chi) maximum and non-DC maximum over psi;
  (c) producer-style shuffled control (permutation of all n indices incl. the
      k = 0 placeholder, half range read), 60 draws: DC and non-DC maxima, and
      the rate of a spike at margins 12, 10, 9, 8;
  (d) symmetry-matched null: a random function with the same mu_6 structure
      (uniform Y in Z/p^5 per orbit {+-k, +-lambda k, +-lambda^2 k}, y(-k) = -Y),
      60 draws, the same maxima.
Usage: rt_d3.py OUT.json
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
import sys

import numpy as np

BASE = "experiments/EXP-CZLIFT-1a3453"
RUNS = ["RUN-CZLIFT-037e5f", "RUN-CZLIFT-d37ca4"]
REPLAY = f"{BASE}/reports/validation-20261022/j2_replay_output.json"
K = 5
DRAWS = 60


# ---------- complete projective addition (RCB 2016, Algorithm 1) ----------
def rcb_add(P, Q, a, b3, M):
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    t0 = X1 * X2 % M; t1 = Y1 * Y2 % M; t2 = Z1 * Z2 % M
    t3 = (X1 + Y1) * (X2 + Y2) % M; t4 = (t0 + t1) % M; t3 = (t3 - t4) % M
    t4 = (X1 + Z1) * (X2 + Z2) % M; t5 = (t0 + t2) % M; t4 = (t4 - t5) % M
    t5 = (Y1 + Z1) * (Y2 + Z2) % M; X3 = (t1 + t2) % M; t5 = (t5 - X3) % M
    Z3 = a * t4 % M; X3 = b3 * t2 % M; Z3 = (X3 + Z3) % M
    X3 = (t1 - Z3) % M; Z3 = (t1 + Z3) % M; Y3 = X3 * Z3 % M
    t1 = 3 * t0 % M; t2 = a * t2 % M; t4 = b3 * t4 % M
    t1 = (t1 + t2) % M; t2 = (t0 - t2) % M; t2 = a * t2 % M; t4 = (t4 + t2) % M
    t2 = t1 * t4 % M; Y3 = (Y3 + t2) % M; t2 = t5 * t4 % M
    X3 = (X3 * t3 - t2) % M; t2 = t3 * t1 % M; Z3 = (Z3 * t5 + t2) % M
    return (X3, Y3, Z3)


def rcb_mul(k, P, a, b3, M):
    R = (0, 1, 0)
    D = P
    while k:
        if k & 1:
            R = rcb_add(R, D, a, b3, M)
        D = rcb_add(D, D, a, b3, M)
        k >>= 1
    return R


def affine(P, M):
    X, Y, Z = P
    zi = pow(Z, -1, M)
    return (X * zi % M, Y * zi % M)


def fp_affine_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    lam = ((3 * x1 * x1 + a) * pow(2 * y1, -1, p) if P == Q else (y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def self_test(p, a, b, rng):
    pts = []
    for x in range(p):
        r = (x ** 3 + a * x + b) % p
        for y in range(p):
            if y * y % p == r:
                pts.append((x, y))
        if len(pts) > 40:
            break
    for _ in range(200):
        P, Q = rng.choice(pts), rng.choice(pts + [None])
        exp = fp_affine_add(P, Q, a, p)
        R = rcb_add((P[0], P[1], 1), (0, 1, 0) if Q is None else (Q[0], Q[1], 1), a % p, 3 * b % p, p)
        got = None if R[2] % p == 0 else affine(R, p)
        assert got == exp, (P, Q, exp, got)


def hensel_y(x, y0, A, B, M):
    f = (x ** 3 + A * x + B) % M
    y = y0
    for _ in range(K + 2):
        y = (y - (y * y - f) * pow(2 * y, -1, M)) % M
    assert (y * y - f) % M == 0
    return y


def spec(d, p, n):
    """X(a, t) over psi_a (a = 1..p-1) and chi_t on the half range; returns (dc_max, nondc_max)."""
    h = (n - 1) // 2
    a = np.arange(1, p, dtype=np.int64)[:, None]
    z = np.zeros((p - 1, n), dtype=np.complex128)
    z[:, 1:h + 1] = np.exp(2j * np.pi * ((a * d[None, 1:h + 1]) % p) / p)
    X = np.abs(np.fft.fft(z, axis=1)) ** 2 / h
    return float(X[:, 0].max()), float(X[:, 1:].max())


def digit(v, p, i):
    return (v // p ** i) % p


def main(out_path):
    replay = json.load(open(REPLAY))
    rng = random.Random("rt-d3")
    results = []
    for e in replay:
        if e["label"] != "D=-3":
            continue
        p, n = e["p"], e["n"]
        h = (n - 1) // 2
        T = math.log((p - 1) * n) + 12.0
        if h <= T:
            continue
        raw = json.load(open(f"{BASE}/runs/{e['run']}/raw-result.json"))["raw"]["curves"][e["index"]]
        A, B = raw["A"], raw["B"]
        M = p ** K
        a, b3 = A % M, 3 * B % M
        self_test(p, A % p, B % p, rng)
        P = tuple(e["replay"]["P"])
        # own torsion lift via the group-order route
        x0, y0 = P
        Ph = (x0, hensel_y(x0, y0, A % M, B % M, M), 1)
        c = (pow(p ** (K - 1), -1, n) * p ** (K - 1)) % (n * p ** (K - 1))  # c = 1 mod n, 0 mod p^4
        T1p = rcb_mul(c, Ph, a, b3, M)
        T1 = affine(T1p, M)
        assert (T1[0] % p, T1[1] % p) == P
        Tn = rcb_mul(n, (T1[0], T1[1], 1), a, b3, M)
        assert Tn[0] % M == 0 and Tn[2] % M == 0 and Tn[1] % p != 0, "T1 is not n-torsion"
        agree = tuple(T1) == tuple(e["replay"]["T1"])
        # chain
        ys = np.zeros(n, dtype=object)
        cur = (T1[0], T1[1], 1)
        ys[1] = T1[1]
        for k in range(2, n):
            cur = rcb_add(cur, (T1[0], T1[1], 1), a, b3, M)
            ys[k] = affine(cur, M)[1]
        # automorphism
        lam = next(l for l in range(2, n) if (l * l + l + 1) % n == 0)
        auto_ok = all(ys[(lam * k) % n] == ys[k] for k in range(1, n))
        # mu_6 orbits on Z/n \ {0}
        orbit_of = {}
        reps = []
        for k in range(1, n):
            if k in orbit_of:
                continue
            reps.append(k)
            for s in (1, lam, lam * lam % n):
                orbit_of[s * k % n] = (k, 1)
                orbit_of[(-s * k) % n] = (k, -1)
        rec = {"run": e["run"], "p": p, "n": n, "h": h, "T": T, "T1_agrees_with_validator": agree,
               "automorphism_y_invariant": auto_ok, "lambda": lam, "digits": {}}
        for i in range(1, K):
            d = np.array([0] + [digit(int(ys[k]), p, i) for k in range(1, n)], dtype=np.int64)
            r_dc, r_ndc = spec(d, p, n)
            sh_dc, sh_ndc, mt_dc, mt_ndc = [], [], [], []
            for _ in range(DRAWS):
                perm = np.array(rng.sample(range(n), n))
                x, y = spec(d[perm], p, n)
                sh_dc.append(x); sh_ndc.append(y)
                vals = {r: rng.randrange(M) for r in reps}
                dm = np.array([0] + [digit((orbit_of[k][1] * vals[orbit_of[k][0]]) % M, p, i) for k in range(1, n)],
                              dtype=np.int64)
                x, y = spec(dm, p, n)
                mt_dc.append(x); mt_ndc.append(y)
            sh_max = [max(x, y) for x, y in zip(sh_dc, sh_ndc)]
            base = T - 12.0
            rec["digits"][f"y{i}"] = {
                "real_dc": r_dc, "real_nondc": r_ndc,
                "shuffled_dc_mean": st.mean(sh_dc), "shuffled_dc_max": max(sh_dc), "shuffled_nondc_mean": st.mean(sh_ndc),
                "matched_dc_mean": st.mean(mt_dc), "matched_dc_max": max(mt_dc), "matched_nondc_mean": st.mean(mt_ndc),
                "matched_dc_rank_of_real": sum(x >= r_dc for x in mt_dc) / DRAWS,
                "shuffled_spike_rate": {str(m): sum(v > base + m for v in sh_max) / DRAWS for m in (12, 10, 9, 8, 7)},
                "real_spike_at_margin": {str(m): int(max(r_dc, r_ndc) > base + m) for m in (12, 10, 9, 8, 7)},
            }
        results.append(rec)
        print(json.dumps({k: v for k, v in rec.items() if k != "digits"}))
        for k, v in rec["digits"].items():
            print("  ", k, {kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in v.items()})
    json.dump(results, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
