#!/usr/bin/env python3
"""RED-TEAM PROBE, NOT PRE-REGISTERED.

Builds ONE null object and pushes it through Section A's frozen AM-4 gate
exactly as prereg 2.2/2.5 defines it:

    X_null(B, beta) = (beta/d) * (1/d) * log|det B|          s_X = 1.0

X_null is a CLOSED-FORM FUNCTION OF (d, k, beta, q) ALONE.  It has zero
variance across the 8 frozen bases and cannot distinguish two lattices of the
same shape.  If it clears G-NUM, G-INV, G-Q and BOTH clauses of G-REL, the
frozen gate certifies as "ADMISSIBLE OBSERVABLE EXHIBITED" (R1) a statistic
that carries no information about the lattice at all.

Everything is the frozen construction of prereg 2.9 and the frozen seed TAGs
of prereg section 6.  Claim tier TOY.  No lattice claim is made.
"""
import json
import math

import numpy as np

TAU_NUM, TAU_INV, TAU_Q, TAU_REL = 1e-6, 0.01, 0.10, 0.10
Q_LADDER = [1, 2, 4, 16, 64, 256, 1009, 3329]
BETA_GRID = {100: [15, 30, 35, 50, 65], 140: [20, 40, 45, 70, 95]}
REL1_PAIR = {100: (15, 65), 140: (20, 95)}
LATTICES = [("L1", 100, 30), ("L2", 100, 70), ("L3", 100, 50),
            ("L4", 140, 40), ("L5", 140, 100)]
REL2_PAIRS = [("L1", "L2"), ("L4", "L5")]


def basis(d, k, q, i):
    """prereg 2.9, verbatim: A = rng([1,d,k,i]).integers(0,q,(k,d-k));
    B = [[I_k, A], [0, q I_{d-k}]]."""
    A = np.random.default_rng([1, d, k, i]).integers(0, q, size=(k, d - k))
    B = np.zeros((d, d), dtype=float)
    B[:k, :k] = np.eye(k)
    B[:k, k:] = A
    B[k:, k:] = q * np.eye(d - k)
    return B


def haar_orth(d, seed):
    Z = np.random.default_rng(seed).normal(size=(d, d))
    Qm, Rm = np.linalg.qr(Z)
    return Qm * np.sign(np.diag(Rm))


def unimodular(d, seed):
    """prereg 2.9: random permutation, random sign flip, d/2 elementary
    R_i <- R_i + s R_j.  det = +-1 by construction."""
    rng = np.random.default_rng(seed)
    U = np.eye(d)
    U = U[rng.permutation(d)]
    U = np.diag(rng.choice([-1.0, 1.0], size=d)) @ U
    for _ in range(d // 2):
        i, j = rng.choice(d, size=2, replace=False)
        U[i] += rng.choice([-1.0, 1.0]) * U[j]
    return U


def transformed(B, d, k, beta, h, which):
    if which in ("T0", "T1"):
        H = haar_orth(d, [2, d, k, beta, h])
        return B @ H @ H.T if which == "T0" else B @ H
    if which == "T2":
        pi = np.random.default_rng([3, d, k, beta, h]).permutation(d)
        return B[pi]
    if which == "T3":
        return unimodular(d, [4, d, k, beta, h]) @ B
    raise ValueError(which)


def logabsdet(M):
    sign, la = np.linalg.slogdet(M)
    return la


def X_null(M, d, beta):
    return (beta / d) * (logabsdet(M) / d)


def X_rdet(M, d, beta):          # X8, for pipeline cross-check
    return math.exp(logabsdet(M) / d)


def rho(xt, xb, s):
    return abs(xt - xb) / max(abs(xb), s)


S_X = 1.0
OUT = {"probe": "RED-TEAM, NOT PRE-REGISTERED",
       "observable": "X_null(B,beta) = (beta/d)*(1/d)*log|det B| ; s_X = 1.0",
       "claim_tier": "TOY"}

# ---------------------------------------------------------------- G-NUM/G-INV
res = {t: [] for t in ("T0", "T1", "T2", "T3")}
res_rdet = {t: [] for t in ("T0", "T1", "T2", "T3")}
across_bases = {}
for (lat, d, k) in LATTICES:
    for beta in BETA_GRID[d]:
        for i in range(8):
            B = basis(d, k, 3329, i)
            xb = X_null(B, d, beta)
            across_bases.setdefault((lat, beta), []).append(xb)
            rb = X_rdet(B, d, beta)
            for h in range(8):
                for t in ("T0", "T1", "T2", "T3"):
                    M = transformed(B, d, k, beta, h, t)
                    res[t].append(rho(X_null(M, d, beta), xb, S_X))
                    res_rdet[t].append(rho(X_rdet(M, d, beta), rb, 1.0))

OUT["G_NUM"] = {"max_rho_T0": float(np.max(res["T0"])), "tau_num": TAU_NUM,
                "pass": bool(np.max(res["T0"]) <= TAU_NUM)}
inv = max(np.max(res[t]) for t in ("T1", "T2", "T3"))
OUT["G_INV"] = {"max_rho_T1T2T3": float(inv), "tau_inv": TAU_INV,
                "per_transform": {t: float(np.max(res[t])) for t in res},
                "n_rho": len(res["T1"]) * 3, "pass": bool(inv <= TAU_INV)}
OUT["cross_check_rdet_same_pipeline"] = {
    t: float(np.max(res_rdet[t])) for t in res_rdet}
OUT["zero_information_check"] = {
    "max_sd_of_X_null_over_the_8_frozen_bases_at_fixed_(lat,beta)":
        float(max(float(np.std(v)) for v in across_bases.values())),
    "meaning": "X_null is constant across the 8 bases: it is a closed-form "
               "function of (d,k,beta,q) and carries no information about "
               "which lattice of the family was drawn"}

# ---------------------------------------------------------------------- G-Q
gq = []
for (lat, d, k) in [("L1", 100, 30), ("L4", 140, 40)]:
    for beta in BETA_GRID[d]:
        vals = {q: X_null(basis(d, k, q, 0), d, beta) for q in Q_LADDER}
        gq.append({"lattice": lat, "beta": beta,
                   "X_q1": vals[1], "X_q3329": vals[3329],
                   "value": rho(vals[1], vals[3329], S_X)})
best = max(gq, key=lambda c: c["value"])
OUT["G_Q"] = {"max_over_cells": best["value"], "at": best, "tau_q": TAU_Q,
              "pass": bool(best["value"] >= TAU_Q)}

# ------------------------------------------------------------------- G-REL1
base = {}
for (lat, d, k) in LATTICES:
    for beta in BETA_GRID[d]:
        base[(lat, beta)] = X_null(basis(d, k, 3329, 0), d, beta)
r1 = []
for (lat, d, k) in LATTICES:
    lo, hi = REL1_PAIR[d]
    r1.append({"lattice": lat, "beta_lo": lo, "beta_hi": hi,
               "X_lo": base[(lat, lo)], "X_hi": base[(lat, hi)],
               "value": rho(base[(lat, hi)], base[(lat, lo)], S_X)})
b1 = max(r1, key=lambda c: c["value"])
OUT["G_REL1"] = {"best": b1, "all": r1, "tau_rel": TAU_REL,
                 "pass": bool(b1["value"] >= TAU_REL)}

# ------------------------------------------------------------------- G-REL2
r2 = []
for (la, lb) in REL2_PAIRS:
    d = [L[1] for L in LATTICES if L[0] == la][0]
    for beta in BETA_GRID[d]:
        r2.append({"pair": "%s/%s" % (la, lb), "d": d, "beta": beta,
                   "X_k": base[(la, beta)], "X_dmk": base[(lb, beta)],
                   "value": rho(base[(lb, beta)], base[(la, beta)], S_X)})
b2 = max(r2, key=lambda c: c["value"])
OUT["G_REL2"] = {"best": b2, "all": r2, "tau_rel": TAU_REL,
                 "pass": bool(b2["value"] >= TAU_REL)}

OUT["G_REL"] = {"pass": bool(OUT["G_REL1"]["pass"] and OUT["G_REL2"]["pass"])}
OUT["OUTCOME_UNDER_THE_FROZEN_MAP"] = (
    "R1 -- ADMISSIBLE OBSERVABLE EXHIBITED"
    if (OUT["G_NUM"]["pass"] and OUT["G_INV"]["pass"] and OUT["G_Q"]["pass"]
        and OUT["G_REL"]["pass"]) else
    "R3 or lower -- see the per-gate numbers")

print(json.dumps(OUT, indent=1))
