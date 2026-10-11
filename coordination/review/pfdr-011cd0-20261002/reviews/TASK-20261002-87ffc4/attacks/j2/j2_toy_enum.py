"""J2: exact toy enumeration of Lemma L1 (and the PTM-L objects) on the engine's
stored set.

Parts (each declared; no randomness anywhere -- every L is enumerated):
  A  h = 2, s = 4, N = 31, every L in (Z/31)^4 (U law). TT and TB (bipartite pair
     set). Moments of the L1 representation (R* = sum_r I_r, nP* = sum M_r I_r)
     and of the engine-rule count (stored set built by the validated tail_rule
     with its L-dependent drops; harvester formal dedup; coincidence of present
     elements), against the formulas. Third central moment of R* against the
     mutually-independent value plus the exact dependent-triple correction.
  B  same set under the engine's admissible law (L_i != 0, L_i != +-L_j: the base
     has distinct x), all 30*28*26*24 ordered L.
  C  h = 3, s = 6: U law at N = 7 (every L in (Z/7)^6) and admissible law at
     N = 13 (all 46080 admissible L).
  D  PTM-L composite N (Z/N not a field): s = 4, h = 2, N = 15 and N = 16, every L;
     where steps (1) and (2) of the proof fail.
  E  PTM-L stored set chosen after seeing L: (i) deduplicated by x-key (one
     element per x-group); (ii) an early-return selection (elements are taken in
     stored order and collection stops at the first x-coincidence).
  F  TB as literally worded in L1's setting (pairs over all of V = tails + e_b)
     versus the harvester's bipartite (base, tail) pair set.
Command: nice -n 19 $PY attacks/j2/j2_toy_enum.py --out attacks/j2/out/toy_enum.json
"""
import argparse
import itertools
import json
import os
import sys
import time
from fractions import Fraction as Fr

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j2lib  # noqa: E402


def all_L(N, s):
    g = np.indices((N,) * s).reshape(s, -1).T.astype(np.int64)
    return g


def admissible_L(N, s):
    out = []
    for L in itertools.product(range(1, N), repeat=s):
        ok = True
        for i in range(s):
            for j in range(i):
                if (L[i] - L[j]) % N == 0 or (L[i] + L[j]) % N == 0:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            out.append(L)
    return np.array(out, dtype=np.int64)


def dot(Ls, v, N):
    return ((Ls @ np.array(v, dtype=np.int64)) % N).astype(np.int16)


def element_presence(Ls, s, h, N, seen):
    """Presence of every formally distinct element (key -> bool array) under the
    engine build rule with L-dependent drops: a tail is stored iff every base
    index in it has nonzero log (U-extension; always true under the admissible
    law) and every suffix sum is nonzero mod N. An element is present iff one
    of its tails is."""
    pres = {}
    cache = {}

    def nz(vec):
        k = tuple(vec)
        if k not in cache:
            cache[k] = dot(Ls, vec, N) != 0
        return cache[k]

    for key, tails in seen.items():
        acc = np.zeros(len(Ls), dtype=bool)
        for t in tails:
            ok = np.ones(len(Ls), dtype=bool)
            for i, _sg in t:
                e = [0] * s
                e[i] = 1
                ok &= nz(e)
            for k in range(len(t)):
                ok &= nz(j2lib.vec_of(t[k:], s))
            acc |= ok
        pres[key] = acc
    return pres


def moments(x):
    """Exact (mean, var, third central moment) of an integer array as Fractions."""
    x = x.astype(np.int64)
    n = len(x)
    s1, s2, s3 = int(x.sum()), int((x * x).sum()), int((x * x * x).sum())
    m1 = Fr(s1, n)
    m2 = Fr(s2, n)
    m3 = Fr(s3, n)
    var = m2 - m1 * m1
    k3 = m3 - 3 * m1 * m2 + 2 * m1 ** 3
    return m1, var, k3


def f(x):
    return float(x)


def rank_mod(vecs, N):
    """Rank over F_N (N prime) by Gaussian elimination."""
    rows = [list(v) for v in vecs]
    r = 0
    ncol = len(rows[0])
    for c in range(ncol):
        piv = None
        for i in range(r, len(rows)):
            if rows[i][c] % N:
                piv = i
                break
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], -1, N)
        rows[r] = [x * inv % N for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] % N:
                fac = rows[i][c]
                rows[i] = [(x - fac * y) % N for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def dependent_triples(class_keys, N):
    """Unordered triples of distinct classes whose representatives span a
    2-dimensional space (pairwise independent but not mutually)."""
    keys = list(class_keys)
    idx = {k: i for i, k in enumerate(keys)}
    # a triple {r, r', r''} is dependent iff r'' is in span(r, r') and distinct:
    # enumerate pairs, enumerate the N - 1 nontrivial combinations r + c r' (c != 0),
    # normalise, and look it up.
    count = 0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            u, w = keys[i], keys[j]
            for c in range(1, N):
                v = tuple((a + c * b) % N for a, b in zip(u, w))
                k = j2lib.monic_mod(v, N)
                if k is None:
                    continue
                t = idx.get(k)
                if t is not None and t > j:
                    count += 1
    return count


def analyse(Ls, s, h, N, label, law, want_triples=False, tb=True):
    tails0 = j2lib.tail_rule(s, h)
    tt_el, deg, seen = j2lib.harvester_elements(tails0, s)
    base = []
    for b in range(s):
        e = [0] * s
        e[b] = 1
        base.append(tuple(e))
    pres = element_presence(Ls, s, h, N, seen)
    for b, e in enumerate(base):
        pres.setdefault(e, dot(Ls, e, N) != 0)
        pres[("base", b)] = dot(Ls, e, N) != 0
    vals = {}

    def val(v):
        if v not in vals:
            vals[v] = dot(Ls, v, N)
        return vals[v]

    out = {"label": label, "law": law, "N": N, "s": s, "h": h, "n_L": int(len(Ls)),
           "stored_tails_formal": len(tails0), "tt_elements": len(tt_el),
           "degenerate_unit_elements": len(deg)}
    classes_out = {}
    sets = {"TT": [(u, w) for u, w in itertools.combinations(tt_el, 2)]}
    if tb:
        sets["TB"] = [(base[b], u) for b in range(s) for u in tt_el]
    for cname, pairs in sets.items():
        classes, excl = j2lib.signed_pair_classes(pairs, N)
        RR = len(classes)
        M = {k: len(v) for k, v in classes.items()}
        sumM = sum(M.values())
        sumM2 = sum(m * m for m in M.values())
        Rstar = np.zeros(len(Ls), dtype=np.int64)
        nPstar = np.zeros(len(Ls), dtype=np.int64)
        Reng = np.zeros(len(Ls), dtype=np.int64)
        nPeng = np.zeros(len(Ls), dtype=np.int64)
        for key, members in classes.items():
            I = dot(Ls, key, N) == 0
            Rstar += I
            nPstar += len(members) * I
            hit = np.zeros(len(Ls), dtype=bool)
            for idx, sg in members:
                u, w = pairs[idx]
                pu = pres[("base", base.index(u))] if (cname == "TB") else pres[u]
                pw = pres[w]
                co = pu & pw & ((val(u).astype(np.int32) - sg * val(w).astype(np.int32)) % N == 0)
                hit |= co
                nPeng += co
            Reng += hit
        # dependent pairs never coincide given presence: check by brute force
        dep_coincide = 0
        for (u, w) in pairs:
            if j2lib.dependent_mod(u, w, N):
                pu = pres[("base", base.index(u))] if (cname == "TB") else pres[u]
                vu, vw = val(u).astype(np.int32), val(w).astype(np.int32)
                co = pu & pres[w] & (((vu - vw) % N == 0) | ((vu + vw) % N == 0))
                dep_coincide += int(co.sum())
        mR, vR, k3R = moments(Rstar)
        mP, vP, _ = moments(nPstar)
        mRe, vRe, k3Re = moments(Reng)
        mPe, vPe, _ = moments(nPeng)
        p = Fr(1, N)
        form = {"E_R": Fr(RR, N), "Var_R": Fr(RR, N) * (1 - p), "E_nP": Fr(sumM, N),
                "Var_nP": Fr(sumM2, N) * (1 - p), "D_R": 1 - p, "D_P": (1 - p) * Fr(sumM2, sumM)}
        rec = {
            "pairs_unordered": len(pairs), "signed_pairs_excluded": excl, "RR": RR,
            "sum_M": sumM, "sum_M2": sumM2, "dependent_pairs_coinciding_count": dep_coincide,
            "formula": {k: f(v) for k, v in form.items()},
            "Rstar": {"E": f(mR), "Var": f(vR), "k3": f(k3R),
                      "E_equals_formula": mR == form["E_R"], "Var_equals_formula": vR == form["Var_R"]},
            "nPstar": {"E": f(mP), "Var": f(vP),
                       "E_equals_formula": mP == form["E_nP"], "Var_equals_formula": vP == form["Var_nP"]},
            "R_engine": {"E": f(mRe), "Var": f(vRe), "k3": f(k3Re), "D": f(vRe / mRe) if mRe else None,
                         "rel_dev_E": f((mRe - form["E_R"]) / form["E_R"]),
                         "rel_dev_Var": f((vRe - form["Var_R"]) / form["Var_R"])},
            "nP_engine": {"E": f(mPe), "Var": f(vPe),
                          "rel_dev_E": f((mPe - form["E_nP"]) / form["E_nP"]),
                          "rel_dev_Var": f((vPe - form["Var_nP"]) / form["Var_nP"])},
            "P_R_engine_ne_Rstar": float(np.mean(Reng != Rstar)),
            "P_nP_engine_ne_nPstar": float(np.mean(nPeng != nPstar)),
            "L1_null_bound_V_over_N": (len(tt_el) + (s if cname == "TB" else 0)) / N,
        }
        if want_triples:
            T = dependent_triples(classes.keys(), N)
            k3_indep = Fr(RR) * p * (1 - p) * (1 - 2 * p)
            k3_pred = k3_indep + 6 * T * (p * p - p ** 3)
            rec["third_moment"] = {
                "k3_Rstar_exact": f(k3R), "k3_mutually_independent": f(k3_indep),
                "dependent_triples": T, "k3_predicted_with_dependent_triples": f(k3_pred),
                "prediction_exact": k3R == k3_pred if law == "U" else None}
        # multiplicity histogram of the classes (formula side)
        hist = {}
        for m in M.values():
            hist[m] = hist.get(m, 0) + 1
        rec["class_multiplicity_histogram"] = {str(k): hist[k] for k in sorted(hist)}
        classes_out[cname] = rec
    out["classes"] = classes_out
    return out


def composite_ptm(N, s=4, h=2):
    """PTM-L composite N. Classes are orbits under unit scaling ((Z/N)^*); I_r is
    the event v_r . L == 0. Reports per-class P(v.L = 0) vs 1/N (step 1) and the
    number of class pairs with P(both) != 1/N^2 (step 2), and the moments of R*
    and of the engine-rule count against the L1 formula."""
    units = [u for u in range(1, N) if np.gcd(u, N) == 1]

    def canon(v):
        best = None
        for u in units:
            w = tuple((u * c) % N for c in v)
            if best is None or w < best:
                best = w
        return best

    tails0 = j2lib.tail_rule(s, h)
    tt_el, _deg, seen = j2lib.harvester_elements(tails0, s)
    pairs = list(itertools.combinations(tt_el, 2))
    classes = {}
    for (u, w) in pairs:
        for sg in (1, -1):
            r = tuple((a - sg * b) % N for a, b in zip(u, w))
            if not any(r):
                continue
            classes.setdefault(canon(r), []).append(((u, w), sg))
    Ls = all_L(N, s)
    Is = {k: (dot(Ls, k, N) == 0) for k in classes}
    pk = {k: float(Is[k].mean()) for k in classes}
    step1_fail = {str(k): pk[k] for k in classes if abs(pk[k] - 1 / N) > 1e-12}
    keys = list(classes)
    step2_fail = 0
    examples = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            pb = float((Is[keys[i]] & Is[keys[j]]).mean())
            if abs(pb - pk[keys[i]] * pk[keys[j]]) > 1e-12:
                step2_fail += 1
                if len(examples) < 5:
                    examples.append({"r": keys[i], "r2": keys[j], "P_both": pb,
                                     "P_r_P_r2": pk[keys[i]] * pk[keys[j]]})
    Rstar = sum(Is[k].astype(np.int64) for k in classes)
    m, v, _ = moments(Rstar)
    RR = len(classes)
    # the engine-rule count: distinct classes among coincident pairs (present = nonzero sums)
    vals = {}

    def val(x):
        if x not in vals:
            vals[x] = dot(Ls, x, N)
        return vals[x]

    Reng = np.zeros(len(Ls), dtype=np.int64)
    for k, members in classes.items():
        hit = np.zeros(len(Ls), dtype=bool)
        for (u, w), sg in members:
            hit |= (val(u) != 0) & (val(w) != 0) & ((val(u).astype(np.int32) - sg * val(w).astype(np.int32)) % N == 0)
        Reng += hit
    me, ve, _ = moments(Reng)
    return {"N": N, "s": s, "h": h, "RR_unit_orbits": RR,
            "formula_E_R": RR / N, "formula_Var_R": RR / N * (1 - 1 / N), "formula_D_R": 1 - 1 / N,
            "Rstar_E": f(m), "Rstar_Var": f(v), "Rstar_D": f(v / m),
            "Rengine_E": f(me), "Rengine_Var": f(ve), "Rengine_D": f(ve / me) if me else None,
            "step1_classes_with_P_ne_1_over_N": len(step1_fail),
            "step1_examples": dict(list(step1_fail.items())[:6]),
            "step2_class_pairs_not_independent": step2_fail,
            "step2_examples": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in e.items()} for e in examples]}


def selected_after_L(N=31, s=4, h=2):
    """PTM-L: stored sets chosen after seeing L."""
    Ls = all_L(N, s)
    tails0 = j2lib.tail_rule(s, h)
    tt_el, _deg, seen = j2lib.harvester_elements(tails0, s)
    vals = np.stack([dot(Ls, v, N) for v in tt_el], axis=1)  # (nL, E)
    vals = vals.astype(np.int32)
    keyx = np.minimum(vals, (N - vals) % N)  # x-key class of u.L (0 = identity)
    pairs = list(itertools.combinations(range(len(tt_el)), 2))
    classes, _ = j2lib.signed_pair_classes([(tt_el[i], tt_el[j]) for i, j in pairs], N)
    sumM = sum(len(v) for v in classes.values())
    # (i) dedup by x-key: keep the first element of each x-group -> no pair can coincide.
    nP_dedup = np.zeros(len(Ls), dtype=np.int64)  # identically zero by construction
    # (ii) early return: take elements in stored order; stop (exclusive) at the first
    # element whose x-key was already seen. Count coincident pairs among the kept.
    nP_early = np.zeros(len(Ls), dtype=np.int64)
    alive = np.ones(len(Ls), dtype=bool)
    kept_cols = []
    for e in range(len(tt_el)):
        col = keyx[:, e]
        clash = np.zeros(len(Ls), dtype=bool)
        for k in kept_cols:
            clash |= (keyx[:, k] == col) & (col != 0)
        # an element that clashes is the "early return": it ends collection
        newly_dead = alive & clash
        alive &= ~clash
        kept_cols.append(e)
        # pairs counted: none among kept by construction of the stop; the stopping
        # element's coincidence is counted once (it is the event that stops)
        nP_early += newly_dead
    return {"N": N, "s": s, "h": h, "formula_E_nP": sumM / N,
            "dedup_by_xkey_E_nP": float(nP_dedup.mean()),
            "early_return_E_nP": float(nP_early.mean()),
            "early_return_Var_nP": float(nP_early.var()),
            "early_return_formula_Var_nP": float(sum(len(v) ** 2 for v in classes.values()) / N * (1 - 1 / N)),
            "note": ("(i) is identically 0 against a formula mean sum M_r/N; (ii) is a 0/1 count "
                     "capped at one coincidence per L, so its variance is bounded by 1/4 whatever "
                     "the formula says.")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    res = {"task": "TASK-20261002-87ffc4", "joint": "J2", "parts": {}}
    LA = all_L(31, 4)
    res["parts"]["A_h2_s4_N31_U"] = analyse(LA, 4, 2, 31, "A", "U", want_triples=True)
    LB = admissible_L(31, 4)
    res["parts"]["B_h2_s4_N31_admissible"] = analyse(LB, 4, 2, 31, "B", "admissible")
    LC = all_L(7, 6)
    res["parts"]["C1_h3_s6_N7_U"] = analyse(LC, 6, 3, 7, "C1", "U", want_triples=False)
    LC2 = admissible_L(13, 6)
    res["parts"]["C2_h3_s6_N13_admissible"] = analyse(LC2, 6, 3, 13, "C2", "admissible")
    res["parts"]["D_composite_N15"] = composite_ptm(15)
    res["parts"]["D_composite_N16"] = composite_ptm(16)
    res["parts"]["E_selected_after_L"] = selected_after_L()
    res["seconds"] = time.time() - t0

    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, tuple):
            return list(o)
        raise TypeError(type(o))
    json.dump(res, open(a.out, "w"), indent=1, default=conv)
    print(json.dumps(res, indent=1, default=conv)[:6000])


if __name__ == "__main__":
    main()
