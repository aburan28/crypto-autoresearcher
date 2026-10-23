"""Red-team probes for EXP-CZLIFT-ae0a13 (TASK-20261023-1d45b5). Own arithmetic (rt_lib.py).

A  readout-breadth mutation (R2, PTM-1): planted sections s_tor + [f(log_P R)]T with
   f = id (the validator's s_leak, positive control), f = n - x and f = x^2 mod n.
   Each is a DL oracle; the frozen success test scores whether ratio == d mod p.
B  equivariance spectrum and exhaustive success (R2): for naive and Teichmuller,
   g(R) = (v, lead digit) of z([n]s(R)) over all R in <P>; the multiplier set
   E_s = {d : g(dR)/g(R) is the same for every R}; the exhaustive success count over
   all (base m, d) against a random odd-function null of the same shape; on the
   recorded integer lift AND on a perturbed lift (A + p a1, B + p b1) of the SAME
   reduction (the matched arm comparison the frozen design lacks).
C  Frobenius-lift iteration on the canonical lift of j = 0 curves (R1): pi = a + b rho
   with rho(x, y) = (zeta x, y); iterate X -> pi(X) from the naive lift and compare
   with the torsion section.
D  precision sweep: v(z([n] s_tor(P))) should track K; v(z([n] naive(P))) should not.
Reads only (arm, label, p, A, B, N, n) of each curve from the runs' raw-result.json.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rt_lib import (ZpCurve, aff_add, aff_mul, aff_neg, count_points,  # noqa: E402
                    point_of_order, random_point)

RUNS = os.path.join(HERE, "..", "..", "runs")
RUN_IDS = ["RUN-CZLIFT-dab752", "RUN-CZLIFT-5b2581"]
K = 4
SEED = 20261023


def curves_of(run_id):
    raw = json.load(open(os.path.join(RUNS, run_id, "raw-result.json")))
    return [{k: c[k] for k in ("arm", "label", "p", "A", "B", "N", "n")} for c in raw["raw"]["curves"]]


def zscore(succ, n, ref):
    s = (ref * (1 - ref) / n) ** 0.5
    return (succ / n - ref) / s


# ------------------------------------------------------------------ A
def part_A(curves_by_run, samples=16):
    rng = random.Random(SEED)
    res = {}
    for run_id, curves in curves_by_run.items():
        acc = {}
        for c in curves:
            p, A, B, N, n = c["p"], c["A"], c["B"], c["N"], c["n"]
            Ap, Bp = A % p, B % p
            assert count_points(p, Ap, Bp) == N
            E = ZpCurve(p, K, A, B)
            G = point_of_order(p, Ap, Bp, N, n, rng)
            while True:
                T = E.mul(n, E.hensel_random(G, rng))
                if E.val(E.z_param(T)) == 1:
                    break
            for _ in range(samples):
                P = point_of_order(p, Ap, Bp, N, n, rng)
                d = rng.randrange(2, n - 1)
                Q = aff_mul(d, P, p, Ap)
                tP = E.torsion_F1(E.hensel_random(P, rng), n)
                tQ = E.torsion_F1(E.hensel_random(Q, rng), n)
                plans = {"leak_id": (1, d), "leak_neg": (n - 1, n - d), "leak_sq": (1, d * d % n)}
                for name, (fP, fQ) in plans.items():
                    sP = E.add(tP, E.mul(fP, T))
                    sQ = E.add(tQ, E.mul(fQ, T))
                    ratio, vP, vQ = E.smart_ratio(sP, sQ, n)
                    success = ratio is not None and ratio == d % p
                    # attacker who knows the rule f but not d
                    cands = []
                    if ratio is not None:
                        for dd in range(2, n - 1):
                            fq = {"leak_id": dd, "leak_neg": n - dd, "leak_sq": dd * dd % n}[name]
                            fp = {"leak_id": 1, "leak_neg": n - 1, "leak_sq": 1}[name]
                            if fq % p == ratio * fp % p and fq % p != 0:
                                cands.append(dd)
                    recovered = any(aff_mul(dd, P, p, Ap) == Q for dd in cands)
                    t = acc.setdefault(name, {}).setdefault(c["arm"], {"n": 0, "succ": 0, "inv_p": 0.0,
                                                                        "recovered": 0, "cand_max": 0})
                    t["n"] += 1
                    t["succ"] += int(success)
                    t["inv_p"] += 1 / p
                    t["recovered"] += int(recovered)
                    t["cand_max"] = max(t["cand_max"], len(cands))
        for name, arms in acc.items():
            for arm, t in arms.items():
                ref = t["inv_p"] / t["n"]
                t["success_rate"] = t["succ"] / t["n"]
                t["frozen_z"] = zscore(t["succ"], t["n"], ref)
                t["passes_frozen_|z|<=4"] = abs(t["frozen_z"]) <= 4
                t["recovery_rate"] = t["recovered"] / t["n"]
                del t["inv_p"]
        res[run_id] = acc
    return res


# ------------------------------------------------------------------ B
def g_table(E, P, n, section, Ap):
    """(v, u) of z([n] s(mP)) for m = 1..n-1 (index m)."""
    v = np.zeros(n, dtype=np.int64)
    u = np.zeros(n, dtype=np.int64)
    R = None
    for m in range(1, n):
        R = aff_add(R, P, E.p, Ap)
        s = E.naive(R) if section == "naive" else E.teichmuller(R)
        vv, uu = E.lead(E.z_param(E.mul(n, s)))
        v[m], u[m] = vv, uu
    return v, u


def success_count(v, u, n, p, Kp):
    """Exhaustive count over m in [1,n-1], d in [2,n-2] of ratio(mP, d) == d mod p (run.py conventions)."""
    m = np.arange(1, n)[:, None]
    d = np.arange(2, n - 1)[None, :]
    idx = (m * d) % n
    vP, uP = v[m], u[m]
    vQ, uQ = v[idx], u[idx]
    defined = (vP < Kp) & (vQ >= vP)
    inv = np.zeros(p, dtype=np.int64)
    inv[1:] = [pow(int(x), -1, p) for x in range(1, p)]
    ratio = np.where(vQ > vP, 0, (uQ * inv[uP % p]) % p)
    hit = defined & (ratio == (d % p))
    return int(hit.sum()), int(defined.size)


def multiplier_set(v, u, n, p, Kp):
    out = []
    inv = {x: pow(x, -1, p) for x in range(1, p)}
    for d in range(2, n):
        cs = set()
        ok = True
        for m in range(1, n):
            dm = d * m % n
            if v[dm] != v[m]:
                ok = False
                break
            if v[m] < Kp:
                cs.add(int(u[dm]) * inv[int(u[m])] % p)
                if len(cs) > 1:
                    ok = False
                    break
        if ok:
            out.append((d, sorted(cs)[0] if cs else None))
    return out


def null_counts(n, p, draws, rng_np):
    """Random odd function g: <P>\\{O} -> (v, u), v = 2 w.p. 1/p else 1, u uniform in F_p^*."""
    res = []
    half = list(range(1, (n - 1) // 2 + 1))
    for _ in range(draws):
        v = np.zeros(n, dtype=np.int64)
        u = np.zeros(n, dtype=np.int64)
        vh = np.where(rng_np.random(len(half)) < 1 / p, 2, 1)
        uh = rng_np.integers(1, p, len(half))
        for i, m in enumerate(half):
            v[m], u[m] = vh[i], uh[i]
            v[n - m], u[n - m] = vh[i], (-uh[i]) % p
        res.append(success_count(v, u, n, p, K)[0])
    return res


def cube_root_unity(p):
    for g in range(2, p):
        z = pow(g, (p - 1) // 3, p)
        if z != 1:
            return z
    raise ValueError


def part_B(curves_by_run, draws=60):
    rng = random.Random(SEED + 1)
    rng_np = np.random.default_rng(SEED + 2)
    seen = {}
    for run_id, curves in curves_by_run.items():
        for c in curves:
            key = (c["p"], c["A"], c["B"])
            seen.setdefault(key, dict(c, runs=[]))["runs"].append(run_id)
    rows = []
    for key, c in sorted(seen.items()):
        p, A, B, N, n = c["p"], c["A"], c["B"], c["N"], c["n"]
        Ap, Bp = A % p, B % p
        P = point_of_order(p, Ap, Bp, N, n, rng)
        a1, b1 = rng.randrange(1, p), rng.randrange(1, p)
        lifts = {"recorded": (A, B), "perturbed": (A + p * a1, B + p * b1)}
        nulls = null_counts(n, p, draws, rng_np)
        row = {"arm": c["arm"], "label": c["label"], "p": p, "n": n, "N": N, "A": A, "B": B,
               "runs": c["runs"], "perturbation": [a1, b1], "null_mean": float(np.mean(nulls)),
               "null_counts": nulls, "lifts": {}}
        lam = None
        if A == 0:
            zeta = cube_root_unity(p)
            rhoP = ((zeta * P[0]) % p, P[1])
            lam = next((l for l in range(2, n) if aff_mul(l, P, p, Ap) == rhoP), None)
            row["j0_lambda"] = lam  # None: <P> not rho-stable (E(F_p)[n] not cyclic)
            row["j0_zeta_teich_mod_p"] = zeta
        for lname, (AL, BL) in lifts.items():
            E = ZpCurve(p, K, AL, BL)
            for sec in ("naive", "teichmuller"):
                v, u = g_table(E, P, n, sec, Ap)
                S, cells = success_count(v, u, n, p, K)
                mult = multiplier_set(v, u, n, p, K)
                row["lifts"].setdefault(lname, {})[sec] = {
                    "exhaustive_success": S, "cells": cells,
                    "multiplier_set": mult}
        rows.append(row)
    # pooled summaries
    summ = {}
    for arm in ("cm_canonical", "random_naive", "all"):
        sel = [r for r in rows if arm == "all" or r["arm"] == arm]
        nulltot = np.sum([r["null_counts"] for r in sel], axis=0)
        for lname in ("recorded", "perturbed"):
            for sec in ("naive", "teichmuller"):
                S = sum(r["lifts"][lname][sec]["exhaustive_success"] for r in sel)
                cells = sum(r["lifts"][lname][sec]["cells"] for r in sel)
                summ[f"{arm}/{lname}/{sec}"] = {
                    "curves": len(sel), "cells": cells, "success": S,
                    "null_mean": float(nulltot.mean()), "null_sd": float(nulltot.std(ddof=1)),
                    "z_vs_null": float((S - nulltot.mean()) / nulltot.std(ddof=1)),
                    "ratio_to_null": float(S / nulltot.mean())}
    # p-binned (the parameter that should drive the rate down as 1/p)
    bins = [(50, 150), (150, 300), (300, 450), (450, 620)]
    pb = {}
    for lo, hi in bins:
        sel = [r for r in rows if lo <= r["p"] < hi]
        if not sel:
            continue
        nulltot = np.sum([r["null_counts"] for r in sel], axis=0)
        for sec in ("naive", "teichmuller"):
            S = sum(r["lifts"]["recorded"][sec]["exhaustive_success"] for r in sel)
            pb[f"p in [{lo},{hi}) {sec}"] = {"curves": len(sel), "success": S,
                                              "null_mean": float(nulltot.mean()),
                                              "ratio_to_null": float(S / nulltot.mean())}
    return rows, summ, pb


# ------------------------------------------------------------------ C
def part_C(curves_by_run):
    rng = random.Random(SEED + 3)
    seen = {}
    for curves in curves_by_run.values():
        for c in curves:
            if c["A"] == 0:
                seen[(c["p"], c["B"])] = c
    out = []
    for (p, B), c in sorted(seen.items()):
        N, n = c["N"], c["n"]
        t = p + 1 - N
        E = ZpCurve(p, K, 0, B)
        z0 = cube_root_unity(p)
        zeta = pow(z0, p ** (K - 1), E.M)  # Teichmuller cube root of unity in Z/p^K
        assert (zeta ** 3 - 1) % E.M == 0

        def rho(X):
            return (zeta * X[0] % E.M, X[1], X[2])

        def rho_aff(R):
            return None if R is None else ((z0 * R[0]) % p, R[1])
        pts = [random_point(p, 0, B % p, rng) for _ in range(6)]
        found = []
        lim = int(2 * p ** 0.5) + 2
        for a in range(-lim, lim + 1):
            for b in range(-lim, lim + 1):
                if a * a - a * b + b * b != p or 2 * a - b != t:
                    continue
                if all(aff_add(aff_mul(a, R, p, 0), aff_mul(b, rho_aff(R), p, 0), p, 0) == R for R in pts):
                    found.append((a, b, (a + b * z0) % p))
        rec = {"p": p, "B": B, "N": N, "n": n, "t": t, "pi_candidates(a,b,tangent mod p)": found}
        P = point_of_order(p, 0, B % p, N, n, rng)
        tor = E.torsion_F1(E.hensel_random(P, rng), n)
        insep = [f for f in found if f[2] == 0]
        if insep:
            a, b, _ = insep[0]

            def pi(X):
                return E.add(E.mul(a, X), E.mul(b, rho(X)))
            rec["pi_fixes_s_tor"] = E.eq(pi(tor), tor)
            X = E.naive(P)
            rec["pi_fixes_naive"] = E.eq(pi(X), X)
            agree = []
            for j in range(1, K + 2):
                X = pi(X)
                diff = E.sub(X, tor)
                agree.append(E.val(E.z_param(diff)) if E.reduce(diff) is None else 0)
            rec["v_z(pi^j(naive P) - s_tor P), j=1..K+1"] = agree
            rec["pi^(K)(naive P) == s_tor(P) mod p^K"] = agree[K - 1] >= K
            # separable conjugate: a + b zeta^2 = (a - b) - b zeta
            ac, bc = a - b, -b
            Xc = E.naive(P)
            Xc2 = E.add(E.mul(ac, Xc), E.mul(bc, rho(Xc)))
            rec["conjugate_pi_bar_maps_P_to"] = "P" if E.reduce(Xc2) == P else "a different residue class"
        out.append(rec)
    return out


# ------------------------------------------------------------------ D
def part_D():
    rng = random.Random(SEED + 4)
    out = []
    for p, A, B in ((67, 0, 2), (157, -9504, 365904), (557, 312, 427)):
        N = count_points(p, A % p, B % p)
        n = max(q for q in range(3, N + 1) if N % q == 0 and all(q % r for r in range(2, int(q ** 0.5) + 1)))
        P = point_of_order(p, A % p, B % p, N, n, rng)
        rec = {"p": p, "A": A, "B": B, "n": n, "K": [], "v_tor": [], "v_naive": []}
        for Kp in (2, 3, 4, 6, 8):
            E = ZpCurve(p, Kp, A, B)
            tor = E.torsion_F1(E.hensel_random(P, rng), n)
            rec["K"].append(Kp)
            rec["v_tor"].append(E.val(E.z_param(E.mul(n, tor))))
            rec["v_naive"].append(E.val(E.z_param(E.mul(n, E.naive(P)))))
        out.append(rec)
    return out


def main():
    t0 = time.time()
    cbr = {r: curves_of(r) for r in RUN_IDS}
    out = {"seed": SEED, "precision": K}
    out["A_readout_mutation"] = part_A(cbr)
    tA = time.time()
    rowsB, summB, pbB = part_B(cbr)
    tB = time.time()
    out["B_rows"] = rowsB
    out["B_summary"] = summB
    out["B_p_bins"] = pbB
    out["C_frobenius_iteration"] = part_C(cbr)
    out["D_precision_sweep"] = part_D()
    out["timing_s"] = {"A": tA - t0, "B": tB - tA, "total": time.time() - t0}
    json.dump(out, open(os.path.join(HERE, "rt_probe_output.json"), "w"), indent=1, default=int)

    print("== A readout mutation (planted DL-oracle sections; frozen success test vs recovery)")
    for run_id, acc in out["A_readout_mutation"].items():
        for name, arms in acc.items():
            for arm, t in arms.items():
                print(f"  {run_id} {name:9s} {arm:13s} n={t['n']} success={t['success_rate']:.4f} "
                      f"frozen_z={t['frozen_z']:+.2f} passes={t['passes_frozen_|z|<=4']} "
                      f"recovery={t['recovery_rate']:.4f} max_candidates={t['cand_max']}")
    print("== B exhaustive success vs random-odd-function null (pooled over curves)")
    for k, s in summB.items():
        print(f"  {k:40s} curves={s['curves']} cells={s['cells']} success={s['success']} "
              f"null={s['null_mean']:.1f}+-{s['null_sd']:.1f} z={s['z_vs_null']:+.2f} ratio={s['ratio_to_null']:.3f}")
    for k, s in pbB.items():
        print(f"  {k:28s} curves={s['curves']} success={s['success']} null={s['null_mean']:.1f} ratio={s['ratio_to_null']:.3f}")
    print("== B multiplier sets E_s (d with g(dR)/g(R) constant over all R); expected {n-1} unless a lift symmetry")
    for r in rowsB:
        tag = f"{r['arm']:12s} {r['label']:7s} p={r['p']:3d} n={r['n']:3d}"
        ms = {f"{l}/{s}": [d for d, _ in r['lifts'][l][s]['multiplier_set']] for l in r['lifts'] for s in r['lifts'][l]}
        nontriv = {k: v for k, v in ms.items() if v != [r['n'] - 1]}
        extra = ""
        if r.get("j0_lambda") is not None:
            lam = r["j0_lambda"]
            mt = dict(r["lifts"]["recorded"]["teichmuller"]["multiplier_set"])
            extra = (f" | j0 lambda={lam} lambda^2={lam*lam % r['n']} zeta_p={r['j0_zeta_teich_mod_p']} "
                     f"ratio(lambda)={mt.get(lam)} ratio(lambda^2)={mt.get(lam*lam % r['n'])}")
        print(f"  {tag} nontrivial={nontriv if nontriv else 'none'}{extra}")
    print("== C Frobenius-lift iteration on the canonical j=0 lift")
    for rec in out["C_frobenius_iteration"]:
        print("  " + json.dumps(rec, default=int))
    print("== D precision sweep")
    for rec in out["D_precision_sweep"]:
        print("  " + json.dumps(rec))
    print(f"timing {out['timing_s']}")


if __name__ == "__main__":
    main()
