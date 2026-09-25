#!/usr/bin/env python3
"""C-SELF and C-FIX (specification controls), seed S_selftest = 2026092450199.

Checks: modulus irreducibility; field axioms on 10^4 triples; own E_S3 against
direct F_{2^17} evaluation of S_3 on 10^3 (v, x_R); the exhaustive-s routine
against naive direct evaluation on 200 random systems; own substitution
against direct evaluation on 10^3 cases; the engine's W_D on 30 random small
systems (6 variables, D in {3, 4}) against a brute-force literal fixpoint
(>= 3 of them reaching the fixpoint at iteration index >= 2); the wdag
extractor on the refuted small systems, checked in-process by the verifier's
rules (a)-(e) (verifier/verify_nconv.py check_wdag, imported read-only);
C-FIX dimensions.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

import common  # noqa: E402
import construct  # noqa: E402
import gf2n  # noqa: E402
import rcb  # noqa: E402
import satcount  # noqa: E402
from common import COLS, NCOL, NEQ, NV, SEED_SELFTEST, now, write_json  # noqa: E402

from crypto_autoresearcher.gf2 import closure, kernels  # noqa: E402

sys.path.insert(0, str(HERE.parent / "verifier"))
import verify_nconv as VER  # noqa: E402
import wdag  # noqa: E402


def field_axioms(g, n=10000):
    bad = 0
    a = g.integers(0, 1 << 17, size=n).tolist()
    b = g.integers(0, 1 << 17, size=n).tolist()
    c = g.integers(0, 1 << 17, size=n).tolist()
    m = gf2n.mul
    for x, y, z in zip(a, b, c):
        ok = (m(x, y) == m(y, x) and m(m(x, y), z) == m(x, m(y, z))
              and m(x, y ^ z) == m(x, y) ^ m(x, z) and m(x, 1) == x)
        if x:
            ok = ok and m(x, gf2n.inv(x)) == 1
        bad += not ok
    return {"n": n, "failures": bad, "pass": bad == 0}


def construction_check(g, B, n=1000):
    bad = []
    for i in range(n):
        v = int(g.integers(0, 1 << 18))
        xR = int(g.integers(0, 1 << 17))
        rows = construct.e_s3(xR, B)
        if construct.eval_rows(rows, v) != construct.eval_s3_direct(v, xR, B):
            bad.append([v, xR])
    return {"n": n, "failures": len(bad), "examples": bad[:5], "pass": not bad}


def naive_solutions(rows):
    """Direct evaluation of every monomial on every assignment (uint8 arrays)."""
    u = np.arange(1 << NV, dtype=np.int64)
    bits = [((u >> i) & 1).astype(np.uint8) for i in range(NV)]
    one = np.ones(1 << NV, dtype=np.uint8)
    mon = []
    for m in COLS:
        if len(m) == 0:
            mon.append(one)
        elif len(m) == 1:
            mon.append(bits[m[0]])
        else:
            mon.append(bits[m[0]] & bits[m[1]])
    ok = np.ones(1 << NV, dtype=bool)
    for r in rows:
        val = np.zeros(1 << NV, dtype=np.uint8)
        for j in range(NCOL):
            if (r >> j) & 1:
                val ^= mon[j]
        ok &= val == 0
    return np.flatnonzero(ok).tolist()


def satcount_check(g, n=200):
    bad = []
    hist = {}
    for i in range(n):
        dens = [0.5, 0.1, 0.03][i % 3]
        rows = []
        for k in range(NEQ):
            r = 0
            for j in np.flatnonzero(g.random(NCOL) < dens).tolist():
                r |= 1 << j
            rows.append(r)
        s, sols = satcount.count_solutions(rows)
        ns = naive_solutions(rows)
        hist[s] = hist.get(s, 0) + 1
        agree = (s == len(ns) and sols == ns)
        # per-assignment pure-Python spot checks
        for u in sols[:8]:
            agree = agree and construct.eval_rows(rows, u) == 0
        for u in g.integers(0, 1 << NV, size=16).tolist():
            agree = agree and ((construct.eval_rows(rows, u) == 0) == (u in set(sols)))
        if not agree:
            bad.append(i)
    return {"n": n, "failures": len(bad), "failing": bad[:10],
            "s_histogram": {str(k): v for k, v in sorted(hist.items())}, "pass": not bad}


def eval_masks(ms, u):
    acc = 0
    for m in ms:
        acc ^= int((u & m) == m)
    return acc


def substitution_check(g, B, n_sys=100, per=10):
    bad = []
    cases = 0
    labels = {}
    for i in range(n_sys):
        if i % 4 == 0:
            xR = int(g.integers(1, 1 << 17))
            rows = construct.e_s3(xR, B)
            # random lower-degree part (N-CONV-like) on half of these
            if i % 8 == 0:
                rows = [(r & common.QUAD_MASK) | (int(g.integers(0, 1 << 19)) & common.LOW_MASK)
                        for r in rows]
        else:
            rows = []
            for k in range(NEQ - 1):
                r = 0
                for j in np.flatnonzero(g.random(NCOL) < 0.5).tolist():
                    r |= 1 << j
                rows.append(r)
            sub = int(g.integers(1, 1 << (NEQ - 1)))
            q = 0
            for k in range(NEQ - 1):
                if (sub >> k) & 1:
                    q ^= rows[k] & common.QUAD_MASK
            rows.append(q | (int(g.integers(0, 1 << 19)) & common.LOW_MASK))
        info = rcb.ell_info(rows)
        labels[info["label"]] = labels.get(info["label"], 0) + 1
        if not info["substituted"]:
            continue
        eqs17, eqs18 = rcb.substitute(rows, info)
        js = info["j_star"]
        keep = [v for v in range(NV) if v != js]
        Lterms = [0] if info["ell_const"] else []
        Lterms += [1 << v for v in info["ell_linear_support"] if v != js]
        for _ in range(per):
            up = int(g.integers(0, 1 << 17))
            u = 0
            for nidx, v in enumerate(keep):
                if (up >> nidx) & 1:
                    u |= 1 << v
            lv = eval_masks(Lterms, u)  # v_{j*} := ell + v_{j*} = L(u)
            u |= lv << js
            fu = construct.eval_rows(rows, u)
            ok = True
            for k in range(NEQ):
                if eval_masks(eqs17[k], up) != (fu >> k) & 1:
                    ok = False
                if eval_masks(eqs18[k], u) != (fu >> k) & 1:
                    ok = False
            # ell vanishes at u
            ok = ok and eval_masks([common.COL_MASK[j] for j in range(19)
                                    if (info["ell"] >> j) & 1], u) == 0
            cases += 1
            if not ok:
                bad.append([i, up])
    return {"cases": cases, "failures": len(bad), "labels": labels,
            "pass": not bad and cases >= 1000}


# ---------------------------------------------------------------------------
# literal W_D on small systems
# ---------------------------------------------------------------------------
def literal_WD(eqs, nv, D):
    mons = [0]
    for d in range(1, D + 1):
        for c in combinations(range(nv), d):
            s = 0
            for i in c:
                s |= 1 << i
            mons.append(s)
    idx = {m: i for i, m in enumerate(mons)}
    deg = [bin(m).count("1") for m in mons]

    def vec(ms):
        v = 0
        for m in ms:
            v ^= 1 << idx[m]
        return v

    def mulmon(m, v):
        out = 0
        x = v
        while x:
            b = (x & -x).bit_length() - 1
            x &= x - 1
            out ^= 1 << idx[mons[b] | m]
        return out

    def basis_of(vs):
        piv = {}
        for v in vs:
            while v:
                h = v.bit_length() - 1
                if h in piv:
                    v ^= piv[h]
                else:
                    piv[h] = v
                    break
        return list(piv.values())

    def in_span(basis, v):
        piv = {b.bit_length() - 1: b for b in basis}
        # basis is echelon by highest bit (from basis_of)
        while v:
            h = v.bit_length() - 1
            if h not in piv:
                return False
            v ^= piv[h]
        return True

    def low_part(basis, dmax):
        """basis of span(basis) cap B_{<=dmax} by eliminating on the >dmax part."""
        hi_mask = 0
        for i, m in enumerate(mons):
            if deg[i] > dmax:
                hi_mask |= 1 << i
        piv = {}
        low = []
        for b in basis:
            v, comb = b & hi_mask, b
            while v:
                h = v.bit_length() - 1
                if h in piv:
                    pv, pc = piv[h]
                    v ^= pv
                    comb ^= pc
                else:
                    piv[h] = (v, comb)
                    break
            if not v:
                low.append(comb)
        return low

    mus = [m for m in mons if bin(m).count("1") <= D - 2]
    rows = [mulmon(mu, vec(f)) for mu in mus for f in eqs]
    W = basis_of(rows)
    dims = [len(W)]
    one = 1 << idx[0]
    one_first = 0 if in_span(W, one) else None
    it = 0
    while True:
        low = low_part(W, D - 1)
        prods = [mulmon(1 << j, g) for g in low for j in range(nv)]
        W2 = basis_of(W + prods)
        if len(W2) == len(W):
            break
        it += 1
        W = W2
        dims.append(len(W))
        if one_first is None and in_span(W, one):
            one_first = it
    dbd = [len(low_part(W, d)) for d in range(D + 1)]
    return {"dims": dims, "iterations_to_fixpoint": it, "final_dim": len(W),
            "one": one_first is not None, "one_first_iteration": one_first,
            "dims_by_deg": dbd}, W, mons


def small_wd_check(g, n=30):
    mons6 = [0] + [1 << i for i in range(6)] + [(1 << a) | (1 << b) for a, b in combinations(range(6), 2)]
    systems = []
    per = []

    def draw(i):
        D = 3 if i % 2 == 0 else 4
        neq = [3, 5, 2, 6, 4][(i // 2) % 5]
        dens = 0.2 if (i // 10) % 2 == 0 else 0.3
        eqs = [[m for m in mons6 if g.random() < dens] for _ in range(neq)]
        return D, neq, eqs

    for i in range(n):
        systems.append(draw(i) + ("random",))
    deep = sum(1 for (D, neq, eqs, _) in systems
               if closure.Closure(6, D, neq).w_closure(eqs, want_cert=False)[0]["iterations_to_fixpoint"] >= 2)
    constructed = []
    j = n
    # F-J2-1: if fewer than 3 reach index >= 2, continue the same seeded stream
    # and replace the last random systems by the first deep ones found (listed).
    while deep < 3:
        D, neq, eqs = draw(j)
        j += 1
        if closure.Closure(6, D, neq).w_closure(eqs, want_cert=False)[0]["iterations_to_fixpoint"] >= 2:
            pos = n - 1 - len(constructed)
            systems[pos] = (D, neq, eqs, f"constructed (stream draw {j - 1})")
            constructed.append(pos)
            deep = sum(1 for (D2, n2, e2, _) in systems
                       if closure.Closure(6, D2, n2).w_closure(e2, want_cert=False)[0]["iterations_to_fixpoint"] >= 2)
    fails = 0
    wdag_checked = 0
    wdag_fail = 0
    for i, (D, neq, eqs, origin) in enumerate(systems):
        Cl = closure.Closure(6, D, neq)
        rec, cert = Cl.w_closure(eqs, want_cert=True)
        lit, Wlit, mons = literal_WD(eqs, 6, D)
        keys = ["dims", "iterations_to_fixpoint", "final_dim", "one", "one_first_iteration", "dims_by_deg"]
        agree = all(rec[k] == lit[k] for k in keys)
        # same space: every literal basis vector is in the engine's W_D
        same = True
        for v in Wlit:
            ms = [mons[b] for b in range(len(mons)) if (v >> b) & 1]
            if not Cl.member(ms):
                same = False
                break
        ent = {"i": i, "origin": origin, "D": D, "neq": neq, "eqs": eqs, "engine": {k: rec[k] for k in keys},
               "literal": lit, "agree": agree, "same_space": same}
        if rec["one"]:
            X = wdag.WDagClosure(6, D, neq)
            dims, of, levels = X.iterate(eqs)
            body = X.extract(levels)
            F = [np.array(f, dtype=np.int64) for f in eqs]
            vr = VER.check_wdag(body, F, D=D, nv=6)
            ent["wdag"] = {"dims_equal_engine": dims == rec["dims"], "depth": of,
                           "nodes": len(body["nodes"]), "verified": vr["verified"],
                           "reason": vr.get("reason")}
            wdag_checked += 1
            if not (vr["verified"] and dims == rec["dims"] and of == rec["one_first_iteration"]):
                wdag_fail += 1
        if not (agree and same):
            fails += 1
        per.append(ent)
    n_deep = sum(1 for e in per if e["engine"]["iterations_to_fixpoint"] >= 2)
    n_deep_refuted = sum(1 for e in per if e["engine"]["iterations_to_fixpoint"] >= 2 and e["engine"]["one"])
    return {"n": len(per), "failures": fails, "n_fixpoint_index_ge2": n_deep,
            "fixpoint_index_ge2": [e["i"] for e in per if e["engine"]["iterations_to_fixpoint"] >= 2],
            "n_deep_and_refuted": n_deep_refuted,
            "constructed_positions": constructed,
            "wdag_checked": wdag_checked, "wdag_failures": wdag_fail,
            "wdag_depths": sorted({e["wdag"]["depth"] for e in per if "wdag" in e}),
            "systems": per,
            "pass": fails == 0 and n_deep >= 3 and wdag_fail == 0 and wdag_checked >= 1}


def extractor_deep_check(g, want=5, max_draws=20000):
    """Additional extractor check (not required by the specification): refuted
    systems whose 1 first appears at iteration >= 2 (8 variables, D = 3,
    7 equations, density 0.2; the same seeded stream), extracted and checked
    by the verifier's rules in-process."""
    nv, D, neq = 8, 3, 7
    mons = [0] + [1 << i for i in range(nv)] + [(1 << a) | (1 << b) for a, b in combinations(range(nv), 2)]
    Cl = closure.Closure(nv, D, neq)
    X = wdag.WDagClosure(nv, D, neq)
    found = []
    draws = 0
    while len(found) < want and draws < max_draws:
        eqs = [[m for m in mons if g.random() < 0.2] for _ in range(neq)]
        draws += 1
        rec, _ = Cl.w_closure(eqs, want_cert=False)
        if rec["one"] and rec["one_first_iteration"] >= 2:
            dims, of, levels = X.iterate(eqs)
            body = X.extract(levels)
            F = [np.array(f, dtype=np.int64) for f in eqs]
            vr = VER.check_wdag(body, F, D=D, nv=nv)
            lit, _, _ = literal_WD(eqs, nv, D)
            found.append({"draw": draws, "depth": of, "engine_dims": rec["dims"], "extractor_dims": dims,
                          "literal_dims": lit["dims"], "nodes": len(body["nodes"]),
                          "verified": vr["verified"], "reason": vr.get("reason"),
                          "ok": vr["verified"] and dims == rec["dims"] and of == rec["one_first_iteration"]
                          and lit["dims"] == rec["dims"]})
    return {"nv": nv, "D": D, "neq": neq, "draws": draws, "found": found,
            "pass": len(found) >= 1 and all(f["ok"] for f in found)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    t0 = time.time()
    started = now()
    B = json.load(open(common.P_CURVE))["B"]
    g = np.random.Generator(np.random.PCG64(SEED_SELFTEST))
    res = {"control": "C-SELF + C-FIX", "seed": SEED_SELFTEST, "started": started,
           "engine_backend": kernels.backend()}
    irr = gf2n.irreducible_check()
    res["modulus_irreducible"] = dict(irr, **{"pass": irr["irreducible"]})
    for name, fn in [("field_axioms", lambda: field_axioms(g)),
                     ("E_S3_vs_direct", lambda: construction_check(g, B)),
                     ("exhaustive_s_vs_naive", lambda: satcount_check(g)),
                     ("substitution_vs_direct", lambda: substitution_check(g, B)),
                     ("engine_WD_vs_literal_small", lambda: small_wd_check(g)),
                     ("extractor_depth_ge2_extra", lambda: extractor_deep_check(g))]:
        t = time.time()
        res[name] = fn()
        res[name]["seconds"] = round(time.time() - t, 2)
        print(f"[selftest] {name}: pass={res[name]['pass']} ({res[name]['seconds']}s)", flush=True)
    import closures
    fix = {k: {"shape": list(v), "expected": list(closures.FIX_EXPECTED[k]),
               "pass": tuple(v) == closures.FIX_EXPECTED[k]} for k, v in closures.FIX.items()}
    res["C-FIX"] = {"dims": fix, "pass": all(x["pass"] for x in fix.values())}
    c_self = all(res[k]["pass"] for k in ["modulus_irreducible", "field_axioms", "E_S3_vs_direct",
                                          "exhaustive_s_vs_naive", "substitution_vs_direct",
                                          "engine_WD_vs_literal_small", "extractor_depth_ge2_extra"])
    res["C-SELF_pass"] = c_self
    res["C-FIX_pass"] = res["C-FIX"]["pass"]
    res["pass"] = c_self and res["C-FIX"]["pass"]
    res["finished"] = now()
    res["seconds"] = round(time.time() - t0, 2)
    write_json(args.out, res)
    print(f"[selftest] C-SELF {c_self} C-FIX {res['C-FIX']['pass']} ({res['seconds']}s)", flush=True)
    return 0 if res["pass"] else 3


if __name__ == "__main__":
    sys.exit(main())
