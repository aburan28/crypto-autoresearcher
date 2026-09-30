#!/usr/bin/env python3
"""J8(ii) (TASK-20260923-29e7af): EXPLICIT degree-4 refutation certificates,
built WITHOUT the archived impl/ (own GF(2^17) arithmetic, own S_3 expansion,
own multilinear products, own GF(2) elimination with row tracking).

Object (spec text): f_k = coefficient of t^k of S_3(x_1, x_2, x_R) after
Weil descent with x_1 = sum_{j<9} v_j t^j, x_2 = sum_{j<9} v_{9+j} t^j and
v^2 = v; S_3 = x1^2 x2^2 + x_R^2 (x1^2 + x2^2) + x1 x2 x_R + B (char 2 form of
(x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B). Rows: mu * f_k, deg mu <= 2 (D = 4).

For each sampled instance: decide whether the constant 1 is in the row space,
and if so extract lambda with sum_{i in lambda} mu_i f_{k_i} = 1, then RE-VERIFY
that sum from scratch by XOR of the explicit multilinear row polynomials.
A verified lambda is a proof that the Boolean system has no solution.
Instances: F-S3 references U1..S2 and F-S3 targets sampled by a declared rule
(first 6 unsat with one_in_R at D=4, first 3 unsat without, first 3 sat, by idx),
compared with the pipeline's per-instance one_in_R flag.
"""
import gzip
import json
import os
import time
from itertools import combinations

RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
HERE = os.path.dirname(os.path.abspath(__file__))
N = 17
MOD = (1 << 17) | (1 << 3) | 1
NV = 18


def mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> N:
            a ^= MOD
    return r


def tpow(e):
    r = 1
    for _ in range(e):
        r = mul(r, 2)
    return r


def equations(B, xR):
    """17 Boolean polynomials, each a frozenset of monomials (frozensets of var indices)."""
    coef = {}
    xR2 = mul(xR, xR)

    def add(m, c):
        coef[m] = coef.get(m, 0) ^ c
    for i in range(9):
        for j in range(9):
            m = frozenset((i, 9 + j))
            add(m, tpow(2 * (i + j)) ^ mul(xR, tpow(i + j)))
    for j in range(9):
        add(frozenset((j,)), mul(xR2, tpow(2 * j)))
        add(frozenset((9 + j,)), mul(xR2, tpow(2 * j)))
    add(frozenset(), B)
    return [frozenset(m for m, c in coef.items() if (c >> k) & 1) for k in range(N)]


def times(mu, poly):
    out = set()
    for m in poly:
        out ^= {m | mu}
    return frozenset(out)


def certificate(B, xR, D=4):
    eqs = equations(B, xR)
    mus = [frozenset(c) for d in range(D - 1) for c in combinations(range(NV), d)]
    rows = [(mu, k, times(mu, eqs[k])) for mu in mus for k in range(N)]
    mons = sorted({m for _, _, p in rows for m in p} | {frozenset()}, key=lambda m: (-len(m), sorted(m)))
    idx = {m: i for i, m in enumerate(mons)}   # constant monomial gets the LAST (lowest-significance) index
    C = len(mons)

    def vec(p):
        v = 0
        for m in p:
            v |= 1 << (C - 1 - idx[m])
        return v
    piv = {}
    for i, (_, _, p) in enumerate(rows):
        v, t = vec(p), 1 << i
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h][0]
                t ^= piv[h][1]
            else:
                piv[h] = (v, t)
                break
    target = 1 << (C - 1 - idx[frozenset()])
    v, t = target, 0
    while v:
        h = v.bit_length() - 1
        if h not in piv:
            return {"one_in_R4": False, "rank": len(piv), "rows": len(rows), "cols_used": C}
        v ^= piv[h][0]
        t ^= piv[h][1]
    lam = [i for i in range(len(rows)) if (t >> i) & 1]
    acc = set()
    for i in lam:
        acc ^= set(rows[i][2])
    ok = (acc == {frozenset()})
    maxdeg_mu = max(len(rows[i][0]) for i in lam)
    return {"one_in_R4": True, "certificate_verified": ok, "lambda_size": len(lam),
            "max_deg_mu": maxdeg_mu, "rank": len(piv), "rows": len(rows), "cols_used": C,
            "lambda_rows_first20": [[sorted(rows[i][0]), rows[i][1]] for i in lam[:20]]}


def main():
    t0 = time.time()
    B = json.load(open(os.path.join(RUN, "curve.json")))["B"]
    refs = json.load(open(os.path.join(RUN, "references.json")))["F-S3"]["references"]
    recs = [json.loads(l) for l in gzip.open(os.path.join(RUN, "targets-F-S3.jsonl.gz"), "rt")]
    R4 = sorted([r for r in recs if r["D"] == 4 and r["stratum"] != "degenerate"], key=lambda r: r["idx"])
    pick = ([r for r in R4 if r["stratum"] == "unsat" and r["one_in_R"]][:6]
            + [r for r in R4 if r["stratum"] == "unsat" and not r["one_in_R"]][:3]
            + [r for r in R4 if r["stratum"] == "sat"][:3])
    items = [(f"ref {k}", v["x_R"], v["D4"]["one_in_R"], v["arm"], v["D4"]["rank"]) for k, v in refs.items() if "x_R" in v]
    items += [(f"target {r['idx']}", r["x_R"], r["one_in_R"], r["stratum"], r["rank"]) for r in pick]
    out = []
    for name, xR, flag, arm, prank in items:
        c = certificate(B, xR)
        c.update({"instance": name, "x_R": xR, "arm": arm, "pipeline_one_in_R4": flag,
                  "agrees_with_pipeline": c["one_in_R4"] == flag,
                  "pipeline_rank4": prank, "rank_agrees": c["rank"] == prank})
        out.append(c)
        print(name, arm, "pipeline", flag, "mine", c["one_in_R4"], "verified", c.get("certificate_verified"),
              "|lambda|", c.get("lambda_size"), "rank", c["rank"], "pipeline_rank", prank, f"{time.time() - t0:.0f}s", flush=True)
    json.dump({"results": out, "wall_seconds": round(time.time() - t0, 1)},
              open(os.path.join(HERE, "j8-certificates.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
