#!/usr/bin/env python3
"""Sampled first-principles replay for J2 (TASK-20261022-3aca4b), sharing no code with the
producer. Re-enumerates every rational point of naive height <= HR on all eight ladder
curves (a-invariants as recorded in raw-result.json, which my blind phase could not see),
and compares counts and distinct residues mod each recorded prime with the coverage rows at
every grid height <= HR. For the four twist curves it enumerates the quadratic-twist points
(x rational, D * R(x) a square) of height <= 30000 and replays every twist row.

The raw-result.json does not carry the full point lists, so this replay, not the raw file,
is the only way to check `distinct`, `distinct_twist` and `distinct_union`. Cells at
H = 10^5 and 3 x 10^5 are NOT replayed (compute budget; see validation report).

Usage: python3 -I j2_replay.py <repo-root> [HR]
"""
import json
import math
import sys

ROOT = sys.argv[1]
HR = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
EXP = ROOT + "/experiments/EXP-CZLIFT-a255fc"
TW_H = 30000


def binv(a1, a2, a3, a4, a6):
    return a1 * a1 + 4 * a2, 2 * a4 + a1 * a3, a3 * a3 + 4 * a6


def search(ainv, H, D=1):
    """All (a, d, u) with gcd(a,d)=1, max(|a|,d^2)<=H and R(a,d) = D*u^2, R the
    completed-square sextic; u>=0 listed once, the caller expands +-u."""
    b2, b4, b6 = binv(*ainv)
    res = []
    isqrt = math.isqrt
    gcd = math.gcd
    for d in range(1, isqrt(H) + 1):
        d2 = d * d
        c2 = b2 * d2
        c1 = 2 * b4 * d2 * d2
        c0 = b6 * d2 * d2 * d2
        for a in range(-H, H + 1):
            R = ((4 * a + c2) * a + c1) * a + c0
            if D == 1:
                if R < 0:
                    continue
                s = isqrt(R)
                if s * s != R:
                    continue
                if gcd(a, d) != 1:
                    continue
                res.append((a, d, s))
            else:
                V = D * R
                if V < 0:
                    continue
                v = isqrt(V)
                if v * v != V:
                    continue
                if gcd(a, d) != 1:
                    continue
                assert v % abs(D) == 0
                res.append((a, d, v // abs(D)))
    return res


def expand(triples):
    pts = []
    for a, d, s in triples:
        pts.append((a, d, s))
        if s != 0:
            pts.append((a, d, -s))
    return pts


def height(t):
    return max(abs(t[0]), t[1] * t[1])


def residues(pts, p, w=1):
    """Residues in E(F_p) as (x, Y) with Y = 2y + a1 x + a3 (bijective in y for odd p);
    twist points carry Y = u*sqrt(D)/d^3 and w is a square root of D mod p."""
    out = set()
    for a, d, s in pts:
        if d % p == 0:
            out.add("O")
            continue
        di = pow(d, -1, p)
        out.add((a * di * di % p, s * w * di * di * di % p))
    return out


def sqrt_mod(D, p):
    D %= p
    for w in range(1, p):
        if w * w % p == D:
            return w
    raise ValueError


def main():
    out = {"HR": HR, "twist_H": TW_H, "runs": {}}
    raws = {r: json.load(open(f"{EXP}/runs/{r}/raw-result.json")) for r in
            ("RUN-CZLIFT-74f172", "RUN-CZLIFT-490b33")}
    main_raw = raws["RUN-CZLIFT-74f172"]
    base_pts = {}
    for c in main_raw["raw"]["curves"]:
        ainv = tuple(c["ainvs"])
        base_pts[c["label"]] = expand(search(ainv, HR))
    for run, raw in raws.items():
        R = {"count_mismatches": [], "distinct_mismatches": [], "cells_replayed": 0,
             "counts_replayed": 0, "sample_points_found": True}
        for c in raw["raw"]["curves"]:
            pts = base_pts[c["label"]]
            for h, n in c["counts"].items():
                if int(h) <= HR:
                    R["counts_replayed"] += 1
                    mine = 1 + sum(1 for t in pts if height(t) <= int(h))
                    if mine != n:
                        R["count_mismatches"].append((c["label"], int(h), n, mine))
            sset = set(map(tuple, pts))
            for t in c["points_sample"]:
                if height(t) <= HR and tuple(t) not in sset:
                    R["sample_points_found"] = False
            for row in c["coverage"]:
                if row["H"] > HR:
                    continue
                sub = [t for t in pts if height(t) <= row["H"]]
                mine = len(residues(sub, row["p"]) | {"O"})
                R["cells_replayed"] += 1
                if mine != row["distinct"]:
                    R["distinct_mismatches"].append((c["label"], row["p"], row["H"], row["distinct"], mine))
        out["runs"][run] = R
    # twists (main run only)
    tw = {"rows_replayed": 0, "mismatches": [], "n_twist_points_by_curve_D": {}}
    for c in main_raw["raw"]["curves"]:
        if not c.get("twists"):
            continue
        ainv = tuple(c["ainvs"])
        base = [t for t in base_pts[c["label"]] if height(t) <= TW_H] if HR >= TW_H else \
            expand(search(ainv, TW_H))
        for D in (-1, 2, -3, 5, -7, 13):
            tpts = expand(search(ainv, TW_H, D))
            n_tw_incl_O = 1 + len(tpts)
            tw["n_twist_points_by_curve_D"]["%s,D=%d" % (c["label"], D)] = {
                "mine_incl_O": n_tw_incl_O,
                "nontrivial": [list(t) for t in tpts][:12],
            }
            for row in c["twists"]:
                if row["D"] != D:
                    continue
                p = row["p"]
                w = sqrt_mod(D, p)
                rb = residues(base, p) | {"O"}
                rt = residues(tpts, p, w) | {"O"}
                mine = {"n_base_points": 1 + len(base), "n_twist_points": n_tw_incl_O,
                        "distinct_base": len(rb), "distinct_twist": len(rt),
                        "distinct_union": len(rb | rt)}
                tw["rows_replayed"] += 1
                diff = {k: (row[k], v) for k, v in mine.items() if row[k] != v}
                if diff:
                    tw["mismatches"].append((c["label"], D, p, diff))
    out["twists_main_run"] = tw
    json.dump(out, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
