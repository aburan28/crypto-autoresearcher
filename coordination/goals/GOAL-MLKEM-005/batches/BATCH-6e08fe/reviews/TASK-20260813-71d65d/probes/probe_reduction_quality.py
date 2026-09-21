#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260813-71d65d (Validator) -- probe_reduction_quality.py

DIRECT EMPIRICAL TEST of the central question this validation exists to
answer: how much of the lead's reported hkz D_route' disagreement
(0.015-0.223) is explained by reduction QUALITY (LLL delta=0.99 vs a
stronger/near-HKZ reduction) rather than by any code-sharing question?

METHOD (deliberately simple and provably correct -- no risky basis-surgery):
Build the SAME frozen basis at L7/L9/L11 (from the published seed formula,
independently), LLL(0.99)-reduce it exactly as the producer's declared
choice does, and for each tail index j relevant to a beta window, compute
lambda_1(pi_j(L)) -- the EXACT minimum of the trailing PROJECTED lattice
pi_j(L) -- via full enumeration on the (already-computed) GSO submatrix
mu[j:,j:]/sqn[j:]. This is a mathematically well-defined quantity: for ANY
basis sharing the SAME first-j subspace decomposition as our LLL basis,
b*_j can be no shorter than sqrt(lambda_1(pi_j(L))) -- this is the
DEFINITION of the projected lattice minimum. A genuinely HKZ-reduced basis
satisfies b*_j = sqrt(lambda_1(pi_j(L))) EXACTLY at every index (for ITS
OWN subspace decomposition, which may differ from LLL's -- so this is a
"tail-only-improvement, given the LLL head" LOWER BOUND on what any
stronger reduction could achieve at that specific index, not a full
self-consistent HKZ re-derivation). No basis modification, no insertion, no
rank-preservation risk: this only does enumeration on GSO submatrices that
already exist.

If this cheap, rigorous per-index LOWER BOUND already reaches or exceeds
route_p's actual reported HKZ value, that is strong, direct evidence that
the LLL-vs-HKZ reduction-quality gap alone is large enough to explain the
observed hkz D_route' disagreement, independent of any code-sharing
question. If it falls well short, reduction quality alone would not fully
explain the gap.

CLAIM TIER: TOY. No discrete-log solve or relation. Reduction-quality
calibration probe only; not a certificate of any kind.
"""

import hashlib
import json
import math
import os
import time
from collections import OrderedDict

import numpy as np

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))


def find_repo_root(start):
    cur = start
    for _ in range(20):
        if os.path.isdir(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    raise SystemExit("no repo root found")


REPO_ROOT = find_repo_root(HERE)
RESULTS_RELVAR_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
    "tasks/TASK-20260809-cda2f6/results_relvar.json")

Q_MAIN = 3329
LATTICES = OrderedDict([("L7", (20, 6)), ("L9", (30, 9)), ("L11", (40, 12))])
BETA_GRID = {20: [5, 15], 30: [7, 22], 40: [10, 30]}   # beta_lo/beta_hi only
BASES_TO_TEST = {"L7": [0, 1, 2, 3], "L9": [0, 1, 2], "L11": [0, 2]}
PROJECTED_ENUM_TIME_CAP = 25.0
LLL_TIME_CAP = {"L7": 30.0, "L9": 60.0, "L11": 90.0}


def make_A(d, k, q, i):
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def build_basis(d, k, q, i):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def gso_full(Bf):
    n = Bf.shape[0]
    Bstar = Bf.copy()
    mu = np.eye(n)
    sqn = np.zeros(n)
    for i in range(n):
        for j in range(i):
            mu[i, j] = np.dot(Bf[i], Bstar[j]) / sqn[j]
            Bstar[i] = Bstar[i] - mu[i, j] * Bstar[j]
        sqn[i] = np.dot(Bstar[i], Bstar[i])
    return Bstar, mu, sqn


def lll_reduce(B0, delta=0.99, time_cap=60.0):
    B = B0.astype(np.float64).copy()
    n = B.shape[0]
    Bstar, mu, sqn = gso_full(B)
    k = 1
    t0 = time.time()
    while k < n:
        if time.time() - t0 > time_cap:
            return B, mu, sqn, False
        for j in range(k - 1, -1, -1):
            if abs(mu[k, j]) > 0.5:
                qz = round(mu[k, j])
                B[k] = B[k] - qz * B[j]
        Bstar, mu, sqn = gso_full(B)
        if sqn[k] + mu[k, k - 1] ** 2 * sqn[k - 1] >= delta * sqn[k - 1] - 1e-9:
            k += 1
        else:
            B[[k, k - 1]] = B[[k - 1, k]]
            Bstar, mu, sqn = gso_full(B)
            k = max(k - 1, 1)
    return B, mu, sqn, True


def lambda1_of_projected_block(mu_full, sqn_full, j, n, time_cap):
    """Exact shortest nonzero vector of the projected lattice pi_j(L), using
    the GSO submatrix mu_full[j:, j:] / sqn_full[j:] of an ALREADY-COMPUTED
    Gram-Schmidt (no basis modification). w = n - j. Returns (best_sq,
    exact_flag, nodes)."""
    w = n - j
    mu = mu_full[j:, j:]
    sqn = sqn_full[j:]
    best = [sqn[0], None]
    t0 = time.time()
    state = {"nodes": 0, "timeout": False}
    u = [0] * w

    def rec(i, tail):
        if state["timeout"]:
            return
        state["nodes"] += 1
        if state["nodes"] % 200000 == 0 and time.time() - t0 > time_cap:
            state["timeout"] = True
            return
        if i < 0:
            if 0 < tail <= best[0]:
                best[0] = tail
            return
        c = 0.0
        for jj in range(i + 1, w):
            c -= u[jj] * mu[jj, i]
        c0 = round(c)
        tried = 0
        off = 0
        while tried < 4000:
            ui = c0 + off
            l = ui - c
            add = l * l * sqn[i]
            nt = tail + add
            if nt <= best[0]:
                u[i] = ui
                rec(i - 1, nt)
                if state["timeout"]:
                    return
            if off >= 0:
                off = -(off + 1)
            else:
                off = -off
            tried += 1

    rec(w - 1, 0.0)
    return best[0], (not state["timeout"]), state["nodes"]


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    out = OrderedDict()
    out["probe"] = "probe_reduction_quality.py"
    out["method"] = ("Per-tail-index projected-lattice minimum (lambda_1 of "
                      "pi_j(L)) computed via enumeration on the LLL basis's "
                      "OWN Gram-Schmidt submatrix -- a rigorous lower bound "
                      "on the tail GSO norms achievable by ANY reduction "
                      "sharing the same LLL-determined subspace "
                      "decomposition. No basis modification performed.")
    out["bases_tested"] = BASES_TO_TEST

    relvar_sha = sha256_file(RESULTS_RELVAR_PATH)
    with open(RESULTS_RELVAR_PATH) as fh:
        relvar = json.load(fh)
    out["results_relvar_json_sha256_measured"] = relvar_sha

    per_lattice = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        g = relvar["G_REL1"]["hkz"][lat]
        beta_lo, beta_hi = g["beta_lo"], g["beta_hi"]
        route_p_lo = [row["X_a"] for row in g["per_basis"]]
        route_p_hi = [row["X_b"] for row in g["per_basis"]]
        logdet = (d - k) * math.log(Q_MAIN)

        rows = []
        for i in BASES_TO_TEST[lat]:
            B0 = build_basis(d, k, Q_MAIN, i)
            Blll, mu, sqn, ok = lll_reduce(B0, delta=0.99,
                                           time_cap=LLL_TIME_CAP[lat])
            if not ok:
                rows.append({"basis": i, "status": "LLL_TIMEOUT"})
                continue
            logb_lll = 0.5 * np.log(np.maximum(sqn, 1e-300))

            row = {"basis": i}
            for beta, rp in ((beta_lo, route_p_lo[i]), (beta_hi, route_p_hi[i])):
                hkz_lll = float(np.mean(logb_lll[d - beta:]) - logdet / d)
                # per-index projected minimum (lower bound), one enumeration
                # call per tail index in this beta window
                floor_logb = []
                any_timeout = False
                for j in range(d - beta, d):
                    best_sq, exact, nodes = lambda1_of_projected_block(
                        mu, sqn, j, d, PROJECTED_ENUM_TIME_CAP)
                    if not exact:
                        any_timeout = True
                        floor_logb.append(logb_lll[j])  # fall back to LLL's own value (conservative: does NOT overstate the bound)
                    else:
                        floor_logb.append(0.5 * math.log(max(best_sq, 1e-300)))
                hkz_floor = float(np.mean(floor_logb) - logdet / d)
                gap_lll = abs(rp - hkz_lll)
                gap_floor = abs(rp - hkz_floor)
                row["beta_%d" % beta] = {
                    "route_p": rp,
                    "hkz_prime_LLL_only": hkz_lll,
                    "hkz_prime_projected_min_floor": hkz_floor,
                    "any_projected_enum_timeout": any_timeout,
                    "abs_gap_route_p_vs_LLL": gap_lll,
                    "abs_gap_route_p_vs_floor": gap_floor,
                    "fraction_of_LLL_gap_explained_by_floor": (
                        None if gap_lll == 0 else
                        max(0.0, 1.0 - gap_floor / gap_lll)),
                    "floor_overshoots_route_p": (
                        (hkz_floor <= rp) if hkz_lll < rp else (hkz_floor >= rp)),
                }
            rows.append(row)
            print("%s i=%d  b%d: LLL_gap=%.5f floor_gap=%.5f frac_explained=%s | "
                  "b%d: LLL_gap=%.5f floor_gap=%.5f frac_explained=%s"
                  % (lat, i, beta_lo,
                     row["beta_%d" % beta_lo]["abs_gap_route_p_vs_LLL"],
                     row["beta_%d" % beta_lo]["abs_gap_route_p_vs_floor"],
                     row["beta_%d" % beta_lo]["fraction_of_LLL_gap_explained_by_floor"],
                     beta_hi,
                     row["beta_%d" % beta_hi]["abs_gap_route_p_vs_LLL"],
                     row["beta_%d" % beta_hi]["abs_gap_route_p_vs_floor"],
                     row["beta_%d" % beta_hi]["fraction_of_LLL_gap_explained_by_floor"]))
        per_lattice[lat] = rows

    out["per_lattice"] = per_lattice
    out["total_seconds"] = time.time() - T0
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    outpath = os.path.join(HERE, "probe_reduction_quality_output.json")
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print("wrote", outpath)
    print("total %.2f s" % (time.time() - T0))


if __name__ == "__main__":
    main()
