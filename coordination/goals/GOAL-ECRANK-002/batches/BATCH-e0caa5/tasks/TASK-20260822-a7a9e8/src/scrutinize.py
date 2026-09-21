#!/usr/bin/env python3
"""
High-scrutiny re-verification of the top curves (TASK-20260822-a7a9e8).

For each supplied curve record it redoes, from scratch and at higher cost than
the search did:

  * exact on-curve check of every exhibited independent point (own Fraction
    code, PARI never consulted);
  * pairwise distinctness and non-identity;
  * exact nonsingularity of the reported minimal model;
  * the Neron-Tate height pairing matrix at THREE real precisions
    (60 / 120 / 250 digits), its determinant, its Hadamard ratio, and its
    smallest eigenvalue (numpy, symmetric eigensolver).  A genuine relation
    among the points forces a zero eigenvalue, so a smallest eigenvalue that is
    stable and bounded away from 0 across three precisions is the independence
    evidence;
  * PARI ellisoncurve as a redundant (not load-bearing) cross-check.

usage: python3 scrutinize.py <pool.json> <out.json> [min_rank]
"""
import json
import sys
from fractions import Fraction as Fr

import numpy as np
import cypari

pari = cypari.pari
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from construct_highrank import verify_on_curve, disc_from_ainv, ptlist  # noqa


def hmatrix(ainv, P, prec):
    gp = ("default(realprecision,%d); E=ellinit(%s); PL=%s;"
          "[ellheightmatrix(E,PL), vector(#PL,i,ellisoncurve(E,PL[i]))]") % (
        prec, str([int(z) for z in ainv]), ptlist(P))
    res = pari(gp)
    n = len(P)
    M = np.array([[float(res[0][i][j]) for j in range(n)] for i in range(n)])
    onc = [int(res[1][i]) for i in range(n)]
    return M, onc


def scrutinize(rec):
    ainv = [Fr(z) for z in rec["min_ainv"]]
    P = [(Fr(x), Fr(y)) for x, y in rec["independent_points"]]
    out = dict(curve_id=rec.get("curve_id"), A=rec["A"], kind=rec["kind"],
               min_ainv=rec["min_ainv"], claimed_rank=rec["certified_rank"],
               n_points=len(P))
    out["exact_on_curve_all"] = all(verify_on_curve(ainv, x, y) for x, y in P)
    out["points_distinct"] = len(set(P)) == len(P)
    out["nonsingular"] = disc_from_ainv(ainv) != 0
    out["rank_equals_points"] = rec["certified_rank"] == len(P)
    dets, mins, oncs = {}, {}, {}
    for prec in (60, 120, 250):
        M, onc = hmatrix(ainv, P, prec)
        dets[prec] = float(np.linalg.det(M))
        ev = np.linalg.eigvalsh(M)
        mins[prec] = float(ev.min())
        oncs[prec] = all(o == 1 for o in onc)
        if prec == 250:
            out["height_matrix"] = [[float(v) for v in row] for row in M]
            out["eigenvalues"] = [float(v) for v in ev]
            diag = [float(M[i][i]) for i in range(len(P))]
            pr = 1.0
            for d in diag:
                pr *= d
            out["hadamard_ratio"] = abs(dets[prec]) / pr if pr else 0.0
    out["regulator_det_by_precision"] = dets
    out["min_eigenvalue_by_precision"] = mins
    out["pari_ellisoncurve_all"] = all(oncs.values())
    ref = dets[250]
    out["det_stable_across_precision"] = all(
        abs(dets[p] - ref) <= 1e-6 * max(1.0, abs(ref)) for p in dets)
    out["min_eigenvalue_positive_all_prec"] = all(v > 1e-6 for v in mins.values())
    out["independence_certified"] = bool(
        out["exact_on_curve_all"] and out["points_distinct"]
        and out["nonsingular"] and out["rank_equals_points"]
        and out["det_stable_across_precision"]
        and out["min_eigenvalue_positive_all_prec"])
    out["certified_rank_lower_bound"] = (
        len(P) if out["independence_certified"] else None)
    return out


def main():
    pool = json.load(open(sys.argv[1]))
    minr = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    res = []
    for c in pool["curves"]:
        if c["certified_rank"] < minr:
            continue
        r = scrutinize(c)
        res.append(r)
        print("%s rank=%s certified=%s det250=%.6g mineig=%.6g" % (
            r["curve_id"], r["claimed_rank"], r["independence_certified"],
            r["regulator_det_by_precision"][250],
            r["min_eigenvalue_by_precision"][250]), flush=True)
    json.dump(dict(min_rank=minr, results=res), open(sys.argv[2], "w"), indent=1)
    ok = sum(1 for r in res if r["independence_certified"])
    print("scrutinized=%d certified=%d max_rank=%d" % (
        len(res), ok,
        max([r["certified_rank_lower_bound"] or 0 for r in res], default=0)))


if __name__ == "__main__":
    main()
