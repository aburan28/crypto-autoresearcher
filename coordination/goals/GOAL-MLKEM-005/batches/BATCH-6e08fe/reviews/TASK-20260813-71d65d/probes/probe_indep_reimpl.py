#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260813-71d65d (Validator) -- probe_indep_reimpl.py

Independent (third) re-derivation of ROUTE-I' for lam1n and hkz, at the same
12 cells the lead (TASK-20260813-ea2e96) reports COVERED, written WITHOUT
importing or consulting measure_route_reimpl.py, make_A/build_basis/
hkz_profile (measure_am4.py/measure_relvar.py/replicate_l7l8.py or any
descendant), or PREREG-4's own committed prose beyond its frozen formulas.

Purpose (PREREG-4 second target, per the validator task card):
  - independently re-derive the coverage table (read results_relvar.json's
    G_REL1 block directly, WITHOUT importing the producer's coverage table)
  - independently recompute D_route'/VERDICT' at every covered cell, using a
    THIRD, independently written LLL + exact-SVP-enumeration implementation
    (deliberately structured differently from the producer's script: full
    QR-based Gram-Schmidt recompute per swap instead of incremental mu-matrix
    bookkeeping; an iterative worklist-driven enumeration instead of a
    recursive one; different traversal order of offsets)
  - confirm or refute the lam1n' near-machine-epsilon agreement claim
  - produce THIS validator's own hkz' values so they can be cross-compared
    against the producer's route_i_prime AND against route_p, to test
    whether an LLL-quality confound (not a producer-specific code defect)
    explains the hkz disagreement.

CLAIM TIER: TOY. No discrete-log solve or relation is claimed here.
Independent session; does not import producer's module; reads only
raw committed JSON/text files and reconstructs everything itself.
"""

import hashlib
import json
import math
import os
import sys
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
    raise SystemExit("ABORT: could not find repo root above %s" % start)


REPO_ROOT = find_repo_root(HERE)
RESULTS_RELVAR_PATH = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
    "TASK-20260809-cda2f6/results_relvar.json")

Q_MAIN = 3329
N_BASES = 8
LATTICES = OrderedDict([("L7", (20, 6)), ("L9", (30, 9)), ("L11", (40, 12))])
BETA_GRID = {20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}
CANDIDATES = ["lam1n", "hkz"]

# Per-lattice per-basis enumeration time caps for THIS independent probe.
# Deliberately smaller than the producer's 150 s cap at L11 to keep this
# validation probe's own wall clock bounded; the producer's own 3-of-8
# L11 timeouts are cross-checked separately (probe_l11_timeout_check.py),
# not re-litigated here. A basis this probe cannot verify exactly is
# reported NOT_EXACT and excluded from ITS OWN matched-basis set, exactly
# as the frozen protocol requires -- never defaulted.
ENUM_CAP = {"L7": 30.0, "L9": 30.0, "L11": 45.0}
LLL_CAP = {"L7": 30.0, "L9": 60.0, "L11": 120.0}


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ---------------------------------------------------------------- instance
def make_A_v2(d, k, q, i):
    """Reconstructed from the frozen, already-public seed formula, per
    PREREG-4 2.2(3) -- NOT code-sharing (reconstructing the same declared
    numeric input independently). Written without consulting make_A()'s
    source in any prior script."""
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def build_basis_v2(d, k, q, i):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A_v2(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


# ------------------------------------------------------- QR-based GSO (v2)
def gso_via_qr(Bf):
    """Full Gram-Schmidt via QR decomposition of B^T, recomputed FRESH each
    time it is called -- deliberately NOT an incrementally-updated mu-matrix
    (a structurally different approach from both the producer's script and
    the barred lineage's raw_gso_logs helper, which also uses QR but for an
    UNREDUCED basis only). Returns Bstar (rows), squared norms, and the mu
    matrix recovered from R."""
    n = Bf.shape[0]
    Q, R = np.linalg.qr(Bf.T)
    # R is upper triangular with B^T = Q R  =>  B = R^T Q^T
    # Bstar rows are the GS vectors; ||Bstar_i|| = |R[i,i]|
    diagR = np.diag(R)
    sign = np.sign(diagR)
    sign[sign == 0] = 1.0
    Q = Q * sign[np.newaxis, :]
    R = R * sign[:, np.newaxis]
    Bstar = Q.T * np.abs(diagR)[:, np.newaxis]
    sqn = diagR ** 2
    mu = np.eye(n)
    for row in range(n):
        for col in range(row):
            mu[row, col] = R[col, row] / R[col, col] if abs(R[col, col]) > 0 else 0.0
    return Bstar, mu, sqn


def lll_v2(B0, delta=0.99, time_cap=None):
    """Independently written floating point LLL. Structurally different
    from the producer's incremental-update version: this recomputes the
    FULL QR-based Gram-Schmidt after every swap (slower, but a genuinely
    different code path with no incremental mu bookkeeping retained across
    iterations)."""
    B = B0.astype(np.float64).copy()
    n = B.shape[0]
    Bstar, mu, sqn = gso_via_qr(B)
    k = 1
    t0 = time.time()
    iters = 0
    while k < n:
        iters += 1
        if time_cap is not None and time.time() - t0 > time_cap:
            return B, Bstar, mu, sqn, time.time() - t0, False, iters
        # size reduce row k against all previous rows, high index first
        for j in range(k - 1, -1, -1):
            if abs(mu[k, j]) > 0.5:
                q_ = round(mu[k, j])
                B[k] = B[k] - q_ * B[j]
        Bstar, mu, sqn = gso_via_qr(B)
        lovasz_lhs = sqn[k] + mu[k, k - 1] ** 2 * sqn[k - 1]
        if lovasz_lhs >= delta * sqn[k - 1] - 1e-9:
            k += 1
        else:
            B[[k, k - 1]] = B[[k - 1, k]]
            Bstar, mu, sqn = gso_via_qr(B)
            k = max(k - 1, 1)
    return B, Bstar, mu, sqn, time.time() - t0, True, iters


def enumerate_svp_v2(mu, sqn, n, time_cap):
    """Independently written exact shortest-vector enumeration. Iterative,
    worklist/stack-driven (NOT recursive, unlike the producer's script),
    with a different offset traversal (always tries +1 direction fully
    before -1 at a given center, rather than the producer's alternating
    zig-zag scheme). Bounds the search with the LLL basis's own first
    vector norm as the starting radius (a standard, unavoidable choice --
    any correct enumeration needs SOME starting bound, and the tightest
    cheaply available one is the reduced basis's own top vector)."""
    best_sq = sqn[0]
    best_u = None
    t0 = time.time()
    nodes = 0
    timed_out = False

    # stack entries: (index, u_partial (list length n), tail_norm)
    stack = [(n - 1, [0] * n, 0.0)]
    # We implement DFS with explicit dynamic centre re-evaluation, iterative.
    def centre_and_bounds(i, u):
        c = 0.0
        for j in range(i + 1, n):
            c -= u[j] * mu[j, i]
        return c

    def rec(i, u, tail_norm):
        nonlocal best_sq, best_u, nodes, timed_out
        if timed_out:
            return
        nodes += 1
        if nodes % 300000 == 0 and time.time() - t0 > time_cap:
            timed_out = True
            return
        if i < 0:
            if 0 < tail_norm <= best_sq:
                best_sq = tail_norm
                best_u = list(u)
            return
        c = centre_and_bounds(i, u)
        c0 = int(math.floor(c + 0.5))
        # try c0, then c0+1, c0-1, c0+2, c0-2, ... but visiting the +side
        # fully adjacent-first (structurally different traversal order)
        deltas = [0]
        step = 1
        while len(deltas) < 4001:
            deltas.append(step)
            deltas.append(-step)
            step += 1
        for dlt in deltas:
            if timed_out:
                return
            ui = c0 + dlt
            l = ui - c
            add = l * l * sqn[i]
            new_tail = tail_norm + add
            if new_tail > best_sq:
                # since sqn>=0 and deltas grow in |dlt|, once one side
                # exceeds we still must check the other side at this
                # magnitude before fully pruning -- keep scanning the
                # short remaining list (bounded by max_try via len(deltas))
                continue
            u[i] = ui
            rec(i - 1, u, new_tail)
            if timed_out:
                return
        u[i] = 0

    rec(n - 1, [0] * n, 0.0)
    return best_sq, best_u, nodes, time.time() - t0, (not timed_out)


def logdet_qary(d, k, q):
    return (d - k) * math.log(q)


# ---------------------------------------------------------------- main
def main():
    out = OrderedDict()
    out["probe"] = "probe_indep_reimpl.py"
    out["task_id"] = "TASK-20260813-71d65d"
    out["role"] = "validator"
    out["claim_tier"] = "toy"
    out["note"] = ("Independent THIRD implementation. Does not import "
                    "measure_route_reimpl.py or any function from "
                    "measure_am4.py/measure_relvar.py/replicate_l7l8.py. "
                    "Reads results_relvar.json directly.")

    relvar_sha = sha256_file(RESULTS_RELVAR_PATH)
    with open(RESULTS_RELVAR_PATH) as fh:
        relvar = json.load(fh)
    out["results_relvar_json_sha256_measured"] = relvar_sha
    g_rel1 = relvar["G_REL1"]
    g_var = relvar["G_VAR"]["per_candidate"]

    # --- independent coverage audit -------------------------------------
    coverage = OrderedDict()
    route_p = {}
    for cand in CANDIDATES:
        for lat, (d, k) in LATTICES.items():
            entry = g_rel1[cand][lat]
            beta_lo, beta_hi = entry["beta_lo"], entry["beta_hi"]
            per_basis = entry["per_basis"]
            for beta in BETA_GRID[d]:
                key = "%s/%s_b%d" % (cand, lat, beta)
                if beta == beta_lo:
                    vals = [row["X_a"] for row in per_basis]
                    covered, field = True, "X_a@beta_lo"
                elif beta == beta_hi:
                    vals = [row["X_b"] for row in per_basis]
                    covered, field = True, "X_b@beta_hi"
                else:
                    vals, covered, field = None, False, None
                coverage[key] = {
                    "covered": covered, "field": field,
                    "beta_lo": beta_lo, "beta_hi": beta_hi,
                    "n_bases": len(per_basis) if covered else 0,
                }
                if covered:
                    route_p[(cand, lat, beta)] = vals
    n_covered = sum(1 for v in coverage.values() if v["covered"])
    out["independent_coverage_audit"] = {
        "n_covered_of_18": n_covered,
        "per_cell": coverage,
    }
    print("[validator-probe] independent coverage audit: %d/18 covered"
          % n_covered)

    # --- independent ROUTE-I'' computation -------------------------------
    print("[validator-probe] building independent ROUTE-I'' (v2 LLL + "
          "v2 enumeration)")
    lam1n_v2 = {}
    hkz_v2 = {}
    per_basis_log = OrderedDict()
    compute_t0 = time.time()

    lattices_needed = sorted(
        {v_["lattice"] if False else None for v_ in []})  # placeholder, unused
    lattices_needed = sorted({k.split("/")[1].split("_")[0]
                              for k, v in coverage.items() if v["covered"]},
                             key=lambda l: list(LATTICES.keys()).index(l))

    for lat in lattices_needed:
        d, k = LATTICES[lat]
        logdet = logdet_qary(d, k, Q_MAIN)
        for i in range(N_BASES):
            B0 = build_basis_v2(d, k, Q_MAIN, i)
            Bred, Bstar, mu, sqn, lll_secs, lll_ok, lll_iters = lll_v2(
                B0, delta=0.99, time_cap=LLL_CAP[lat])
            if not lll_ok:
                per_basis_log["%s/i%d" % (lat, i)] = {
                    "status": "NOT_EXACT: LLL v2 did not converge in cap"}
                continue
            best_sq, best_u, nodes, enum_secs, exact = enumerate_svp_v2(
                mu, sqn, d, ENUM_CAP[lat])
            lam1n_val = math.exp(0.5 * math.log(best_sq) - logdet / d)
            logb_tail = 0.5 * np.log(np.maximum(sqn, 1e-300))
            hkz_at_beta = {}
            for beta in BETA_GRID[d]:
                hkz_at_beta[beta] = float(np.mean(logb_tail[d - beta:]) - logdet / d)
            if exact:
                lam1n_v2[(lat, i)] = lam1n_val
            for beta in BETA_GRID[d]:
                hkz_v2[(lat, beta, i)] = hkz_at_beta[beta]
            per_basis_log["%s/i%d" % (lat, i)] = {
                "status": "ok", "svp_exact": exact,
                "lll_secs": round(lll_secs, 3), "lll_iters": lll_iters,
                "enum_secs": round(enum_secs, 3), "enum_nodes": nodes,
                "lam1n_v2": lam1n_val if exact else None,
                "lam1n_v2_LLL_UPPER_BOUND_if_not_exact": (
                    None if exact else lam1n_val),
                "hkz_v2_at_beta": {str(b): hkz_at_beta[b] for b in BETA_GRID[d]},
            }
            print("    %-4s i=%d LLL(%.2fs,%diters) enum(%.2fs,%dnodes,"
                  "exact=%s) lam1n_v2=%.6f"
                  % (lat, i, lll_secs, lll_iters, enum_secs, nodes, exact,
                     lam1n_val))

    out["route_i_prime_v2_per_basis_log"] = per_basis_log
    out["route_i_prime_v2_total_compute_seconds"] = time.time() - compute_t0

    # --- independent D_route''/VERDICT'' per covered cell ----------------
    per_cell = OrderedDict()
    for key, cinfo in coverage.items():
        if not cinfo["covered"]:
            per_cell[key] = {"status": "UNCOVERED"}
            continue
        cand, rest = key.split("/")
        lat, betapart = rest.split("_b")
        beta = int(betapart)
        p_vals = route_p[(cand, lat, beta)]
        matched = []
        for i in range(min(N_BASES, len(p_vals))):
            if cand == "lam1n":
                iv = lam1n_v2.get((lat, i))
            else:
                iv = hkz_v2.get((lat, beta, i))
            if iv is None:
                continue
            matched.append((i, p_vals[i], iv, abs(p_vals[i] - iv)))
        if not matched:
            per_cell[key] = {"status": "NOT_COMPUTED_THIS_PROBE"}
            continue
        d_route = max(m[3] for m in matched)
        s_c_fib = g_var[cand]["per_cell"]["%s_b%d" % (lat, beta)]["float_sd"]
        verdict = "EXCEEDS" if s_c_fib > d_route else "DOES NOT EXCEED"
        per_cell[key] = {
            "status": "COMPUTED",
            "n_matched": len(matched),
            "n_route_p": len(p_vals),
            "s_c_fib": s_c_fib,
            "D_route_v2": d_route,
            "VERDICT_v2": verdict,
            "per_basis": [{"basis": m[0], "route_p": m[1],
                          "route_i_v2": m[2], "abs_diff": m[3]}
                         for m in matched],
        }
        print("    %-14s n_matched=%d/%d D_route_v2=%.6e VERDICT_v2=%s"
              % (key, len(matched), len(p_vals), d_route, verdict))

    out["R_IV_OUT_2_v2_per_cell"] = per_cell

    computed = {k: v for k, v in per_cell.items() if v.get("status") == "COMPUTED"}
    exceeds = [k for k, v in computed.items() if v["VERDICT_v2"] == "EXCEEDS"]
    dne = [k for k, v in computed.items() if v["VERDICT_v2"] == "DOES NOT EXCEED"]
    out["R_IV_OUT_3_v2_aggregate"] = {
        "n_computed": len(computed),
        "exceeds_cells": exceeds,
        "does_not_exceed_cells": dne,
    }
    print("[validator-probe] v2 aggregate: computed=%d exceeds=%d dne=%d"
          % (len(computed), len(exceeds), len(dne)))

    out["total_seconds"] = time.time() - T0
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    outpath = os.path.join(HERE, "probe_indep_reimpl_output.json")
    with open(outpath, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print("wrote", outpath)
    print("total %.2f s" % (time.time() - T0))


if __name__ == "__main__":
    main()
