#!/usr/bin/env python3
"""checks.py -- PILOT #2 semantic checks, independent of the closure code.
For every labelled cell: (a) brute-force point-sum enumeration over all ordered
m-tuples of F_(2^n)-points with x in V: SAT targets must be reachable, UNSAT
targets must not; (b) chain-prefix survival: distinct u_i values after each stage
and the number of z values the chain can reach at all; (c) liftable x in V and
the cross-check of count_chain vs pilot #1's count_affu/curve_solutions at m=3."""
import glob, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pilot_lib as L, pilot2_lib as P

def point_reach(cell):
    c = json.load(open(cell)); n, k, m = c["n"], c["k"], c.get("m", 3)
    cv = L.pick_curve(n, 0); F, E = cv["F"], cv["E"]; V = L.VSpace(F, c["basis"]); xs = [int(v) for v in V.elems]
    pts = []
    for x in xs:
        Pt = E.lift_x(x)
        if Pt is not None:
            pts.append(Pt)
            if E.neg(Pt) != Pt: pts.append(E.neg(Pt))
    sums = set()
    def rec(depth, acc):
        if depth == m:
            if acc is not None: sums.add(acc[0])
            return
        for Pt in pts:
            if depth == 0: nacc = Pt
            else:
                nacc = E.add(acc, Pt)
                if nacc is None and depth < m - 1: continue   # partial sum O: u undefined
            rec(depth + 1, nacc)
    rec(0, None)
    ins = [x for x in c["instances"] if not x["dup_target"]]
    sat = {x["z"] for x in ins if x["nsol"] > 0}; uns = {x["z"] for x in ins if x["nsol"] == 0}
    # chain prefix survival
    sq = lambda v: F.vmul(v, v); b = c["b"]; xe = V.elems; nV = 1 << k
    i1 = np.repeat(np.arange(nV), nV); i2 = np.tile(np.arange(nV), nV)
    pr, _ = L._solve_quadratic_vec(F, sq(xe[i1] ^ xe[i2]), F.vmul(xe[i1], xe[i2]), sq(F.vmul(xe[i1], xe[i2])) ^ b)
    u = np.unique(np.concatenate([r for _, r in pr])) if pr else np.zeros(0, dtype=np.int64); sizes = [len(u)]
    for s in range(1, m - 1):
        Pn = len(u); rep = np.repeat(np.arange(Pn), nV); ix = np.tile(np.arange(nV), Pn); up = u[rep]; x = xe[ix]
        pr, _ = L._solve_quadratic_vec(F, sq(up ^ x), F.vmul(up, x), sq(F.vmul(up, x)) ^ b)
        u = np.unique(np.concatenate([r for _, r in pr])) if pr else np.zeros(0, dtype=np.int64); sizes.append(len(u))
    return (f"{os.path.basename(cell)[:-5]}: m={m} n={n} k={k} liftable x in V {len([x for x in xs if E.lift_x(x) is not None])}/{len(xs)} "
            f"points {len(pts)} | SAT reachable {len(sat & sums)}/{len(sat)} UNSAT reachable {len(uns & sums)}/{len(uns)} "
            f"| distinct u_i per stage {sizes[:-1]}, z reachable by the polynomial chain {sizes[-1]} of 2^{n}")

def m3_crosscheck():
    cell = json.load(open(os.path.join(HERE, "instances", "n9-poly.json"))); n, k = cell["n"], cell["k"]
    cv = L.pick_curve(n, 0); V = L.VSpace(cv["F"], cell["basis"]); ok = 0
    for x in cell["instances"][:40]:
        s = P.build_chain(n, k, 3, cell["basis"], cell["b"], x["z"], cell["modulus"])
        assert s["equations"] == L.build_chain3(n, k, cell["basis"], cell["b"], x["z"], cell["modulus"])["equations"]
        c1, b1 = L.boolean_count_chain3(s); c2, b2 = P.boolean_count_chain(s)
        c3 = P.chain_solutions(cv["F"], V, cell["b"], x["z"], 3); c4 = L.curve_solutions(cv["F"], V, cell["b"], x["z"])
        ok += (c1 == c2 == len(c3) == len(c4) and sorted(b1) == b2 == c3 == c4)
    return f"m=3 n=9: count_chain == count_affu == chain_solutions == pilot-1 curve_solutions on {ok}/40 instances"

if __name__ == "__main__":
    print(m3_crosscheck())
    for f in sorted(glob.glob(os.path.join(HERE, "instances", "m*.json"))):
        if "nulls" in f: continue
        print(point_reach(f))
