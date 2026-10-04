#!/usr/bin/env python3
"""J8 (CP-5) of TASK-20260926-f50294: try to craft certificates that pass a
frozen rule for a FALSE statement, on small systems of the comparator's own
(6 to 8 variables; search.py, seed 2026092610), and document where each
attempt fails.

Checkers used:
  * FROZEN FORMAT, exactly as used for CP-3: checks/mini.py check_wdag and
    check_ann at (D, nv, neq) = (4, 20, 19). A small system in v_0..v_{n-1}
    with neq_s equations is EMBEDDED: f_k = 0 for k >= neq_s, variables
    v_n..v_19 free. 1 in W_4 is invariant under this embedding: W_4(small) is
    contained in W_4(20); conversely the ring map v_i -> 0 (i >= n) sends
    M_4 rows to M_4 rows or 0 and v_j * g (deg g <= 3) to 0 or v_j * pi(g),
    never raises degree, fixes 1, so pi(W_4(20)) is inside W_4(small).
  * D-PARAMETRISED transcription (check_wdag_D below) for the D = 3 analogue,
    where small systems separate W_D from M_{D+1}: rules (a)-(e) with
    |mu| <= D - 2, child degree <= D - 1, node degree <= D.

Usage: python3 crafted_attempts.py <out_json>
"""
import itertools
import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "checks"))
import mini  # noqa: E402  (the CP-3 checker, unchanged)
import small_engine as se  # noqa: E402


def mask_list(m):
    return [i for i in range(20) if (m >> i) & 1]


def check_wdag_D(cert, fs, D, nv, neq):
    """Rules (a)-(e) of wdag-v1 with D generic (the frozen text at D = 4)."""
    polys = {}
    for nd in sorted(cert["nodes"], key=lambda x: x["id"]):
        i = nd["id"]
        acc = set()
        for mu, k in nd["rows"]:
            if len(mu) > D - 2 or len(set(mu)) != len(mu) or any(v < 0 or v >= nv for v in mu):
                return False, "(b) node %d |mu| = %d > %d" % (i, len(mu), D - 2)
            if not 0 <= k < neq:
                return False, "(b) k"
            acc ^= mini.mono_mul(fs[k], mini.mask_of(mu))
        for j, c in nd["prods"]:
            if c >= i or c not in polys:
                return False, "(a) node %d child %d" % (i, c)
            if not 0 <= j < nv:
                return False, "bad j"
            if mini.deg(polys[c]) > D - 1:
                return False, "(c) node %d child %d deg %d > %d" % (i, c, mini.deg(polys[c]), D - 1)
            acc ^= mini.mono_mul(polys[c], 1 << j)
        if mini.deg(acc) > D:
            return False, "(d) node %d deg %d > %d" % (i, mini.deg(acc), D)
        polys[i] = acc
    if polys.get(cert["output"]) != {0}:
        return False, "(e) poly(output) != 1"
    return True, None


def flat_identity(R, fs, D):
    """A flat identity sum mu f_k = 1 from M_D (small engine, tags)."""
    E, gens = se.rowspace(R, fs, D)
    one = R.vec({0})
    r, tag = E.reduce(one, 0)
    assert r == 0
    C = []
    g = 0
    while tag:
        if tag & 1:
            _, (kind, mu, k) = gens[g]
            C.append((mu, k))
        tag >>= 1
        g += 1
    return C


def wdag_from_tags(R, fs, D):
    """A wdag-v1 for 1 in W_D, from the literal small engine's tags."""
    W = se.literal_W(R, fs, D)
    assert W["one"]
    E, gens = W["echelon"], W["gens"]
    r, tag = E.reduce(R.vec({0}), 0)
    assert r == 0
    nodes = []
    memo = {}

    def node_for(tag):
        if tag in memo:
            return memo[tag]
        rows, prods = [], []
        g, t = 0, tag
        while t:
            if t & 1:
                desc = gens[g][1]
                if desc[0] == "row":
                    rows.append([mask_list(desc[1]), desc[2]])
                else:
                    _, j, v, sub = desc
                    prods.append([j, node_for(sub)])
            t >>= 1
            g += 1
        nid = len(nodes)
        nodes.append({"id": nid, "rows": rows, "prods": prods})
        memo[tag] = nid
        return nid

    o = node_for(tag)
    return {"D": D, "nv": R.n, "neq": len(fs), "nodes": nodes, "output": o}, W


def embed(fs):
    return [set(f) for f in fs] + [set() for _ in range(19 - len(fs))]


def to_hex(bits):
    return format(int.from_bytes(np.packbits(bits, bitorder="little").tobytes(), "little"), "x")


def main():
    outp = sys.argv[1]
    t0 = time.time()
    found = json.load(open(os.path.join(HERE, "search_found.json")))["found"]
    rng = random.Random(2026092611)
    res = {"attempts": [], "notes": []}

    def rec(obj, statement, attempt, rule_text, passed, why, extra=None):
        d = {"object": obj, "false_statement_targeted": statement, "attempt": attempt,
             "rule_checked": rule_text, "passed": bool(passed), "first_failure": why}
        if extra:
            d.update(extra)
        res["attempts"].append(d)
        print(("PASS " if passed else "fail ") + attempt[:90], "|", why, flush=True)

    # ================================================================ X3 (D = 3)
    X = found["X3"][0]
    n, neq = X["n"], X["neq"]
    fs = [set(f) for f in X["fs"]]
    R3, R4 = se.Ring(n, 3), se.Ring(n, 4)
    W3 = se.literal_W(R3, fs, 3)
    assert not W3["one"] and not se.solutions(fs, n)
    obj = "X3: own system, n = %d, neq = %d, unsatisfiable; 1 not in W_3 (literal, dims %s), 1 in M_4" % (n, neq, W3["dims"])
    C = flat_identity(R4, fs, 4)
    maxmu = max(se.popcount(mu) for mu, k in C)
    acc = set()
    for mu, k in C:
        acc ^= mini.mono_mul(fs[k], mu)
    res["notes"].append({"X3_flat_identity": {"terms": len(C), "max_mu": maxmu, "identity_holds_in_B": acc == {0},
                                              "reading": "a valid flat-v1 with max |mu| = D - 1 = 2: certifies unsatisfiability and 1 in M_4, NOT 1 in W_3; counting it toward W_3 would count a system W_3 does not refute (the D = 3 image of the frozen rule 'never toward W_4 unless max |mu| <= 2')"}})
    # A1: flat identity as one-node wdag
    cert = {"nodes": [{"id": 0, "rows": [[mask_list(mu), k] for mu, k in C], "prods": []}], "output": 0}
    ok, why = check_wdag_D(cert, fs, 3, n, neq)
    rec(obj, "1 in W_3", "A1 flat identity (max |mu| = 2) rewritten as a one-node wdag", "(a)-(e), D = 3", ok, why)
    # A2/A3: factor one variable out of each |mu| = 2 term (every grouping choice sampled)
    best = None
    tried = 0
    passes = 0
    for trial in range(3000):
        groups = {}
        base = []
        for mu, k in C:
            vs = mask_list(mu)
            if len(vs) <= 1:
                base.append([vs, k])
            else:
                j = vs[rng.randrange(len(vs))] if trial else vs[-1]
                groups.setdefault(j, []).append([[v for v in vs if v != j], k])
        nodes = []
        prods = []
        for j, rows in sorted(groups.items()):
            nodes.append({"id": len(nodes), "rows": rows, "prods": []})
            prods.append([j, len(nodes) - 1])
        nodes.append({"id": len(nodes), "rows": base, "prods": prods})
        cert = {"nodes": nodes, "output": len(nodes) - 1}
        ok, why = check_wdag_D(cert, fs, 3, n, neq)
        tried += 1
        passes += int(ok)
        md = max(mini.deg(_poly(nd["rows"], fs)) for nd in nodes[:-1]) if len(nodes) > 1 else -1
        best = md if best is None else min(best, md)
    rec(obj, "1 in W_3", "A2/A3 degree-disciplined rewriting of the flat identity: factor v_j out of every |mu| = 2 term (%d random groupings)" % tried,
        "(a)-(e), D = 3", passes > 0, "(c) on every grouping: min over groupings of the max child degree = %s > 2" % best,
        {"groupings_tried": tried, "groupings_passing": passes})
    # A4: cancelling pair on a degree-3 child
    c3 = {"id": 0, "rows": [[[0], 0]], "prods": []}
    cert = {"nodes": [c3, {"id": 1, "rows": [[mask_list(mu), k] for mu, k in C if se.popcount(mu) <= 1],
                           "prods": [[5, 0], [5, 0]]}], "output": 1}
    ok, why = check_wdag_D(cert, fs, 3, n, neq)
    rec(obj, "1 in W_3", "A4 identical prods pair on a degree-3 child (sum unchanged)", "(a)-(e), D = 3", ok, why)
    # A6: a child whose UNREDUCED expression has degree 3 but whose poly in B has degree <= 2
    # (a fallen element of M_3 written through |mu| = 1 rows) is legal under rule (c) and stays in W_3
    E3, g3 = se.rowspace(R3, fs, 3)
    fallen = [(v, t) for lb, (v, t) in E3.rows.items() if lb < R3.low_limit]
    pick = None
    for v, t in fallen:
        rows_t = []
        g, tt = 0, t
        while tt:
            if tt & 1:
                _, mu, k = g3[g][1]
                rows_t.append([mask_list(mu), k])
            tt >>= 1
            g += 1
        if any(len(r[0]) == 1 for r in rows_t):
            pick = (v, rows_t)
            break
    if pick:
        v, rows_t = pick
        cert = {"nodes": [{"id": 0, "rows": rows_t, "prods": []}, {"id": 1, "rows": [], "prods": [[0, 0]]}], "output": 1}
        ok, why = check_wdag_D(cert, fs, 3, n, neq)
        p0 = _poly(rows_t, fs)
        prod = mini.mono_mul(p0, 1)
        inW = W3["echelon"].contains(R3.vec(prod))
        rec(obj, "1 in W_3", "A6 'degree after reduction': a fallen element of M_3 (rows of formal degree 3, poly degree %d) used as a child of v_0" % mini.deg(p0),
            "(a)-(e), D = 3", ok, why,
            {"reading": "rule (c) is met AFTER reduction (the text defines poly(c) in B); the product lies in the literal W_3: %s; the output is not 1, so (e) fails. The after-reduction reading is sound: poly(c) is a sum of M_3 rows whatever its unreduced form." % inW})
    else:
        res["notes"].append({"A6": "X3 has no fallen element of M_3 written through |mu| = 1 rows; the after-reduction reading is exercised by the Y4 positive control and by every archived wdag-v1 (children built from |mu| = 2 rows, formal degree 4, poly degree 3)"})
    # A7: random wdags; every node passing (a)-(d) must lie in the literal W_3; none may output 1
    npass = 0
    nout = 0
    notin = 0
    for trial in range(4000):
        nn = rng.randrange(1, 4)
        nodes = []
        for i in range(nn):
            rows = [[([rng.randrange(n)] if rng.random() < 0.6 else []), rng.randrange(neq)] for _ in range(rng.randrange(0, 6))]
            prods = [[rng.randrange(n), rng.randrange(i)] for _ in range(rng.randrange(0, 3))] if i else []
            nodes.append({"id": i, "rows": rows, "prods": prods})
        cert = {"nodes": nodes, "output": nn - 1}
        # evaluate (a)-(d) only, then membership of every node
        polys = {}
        good = True
        for nd in nodes:
            acc = _poly(nd["rows"], fs)
            for j, c in nd["prods"]:
                if mini.deg(polys[c]) > 2:
                    good = False
                acc ^= mini.mono_mul(polys[c], 1 << j)
            if mini.deg(acc) > 3:
                good = False
            polys[nd["id"]] = acc
        if not good:
            continue
        npass += 1
        for p in polys.values():
            if not W3["echelon"].contains(R3.vec(p)):
                notin += 1
        if polys[nn - 1] == {0}:
            nout += 1
    rec(obj, "1 in W_3", "A7 4000 random wdags; every one meeting (a)-(d) checked node by node against the literal W_3",
        "(a)-(d) then membership", nout > 0,
        "%d met (a)-(d); nodes outside W_3: %d; outputs equal to 1: %d" % (npass, notin, nout),
        {"met_a_to_d": npass, "nodes_outside_literal_W3": notin, "outputs_equal_1": nout})

    # ============================================= satisfiable system, frozen D = 4 format
    sat_fs = [set(f) for f in found["Y4"][0]["fs"][:-1]]  # the planted system minus its last equation
    nS = found["Y4"][0]["n"]
    sols = se.solutions(sat_fs, nS)
    assert sols
    E = embed(sat_fs)
    objS = "S: own satisfiable system, n = %d, neq = %d, %d solutions over v_0..v_%d, embedded in (D, nv, neq) = (4, 20, 19)" % (nS, len(sat_fs), len(sols), nS - 1)
    ok, why, _ = mini.check_wdag({"D": 4, "nv": 20, "neq": 19, "nodes": [{"id": 0, "rows": [[[], 0]], "prods": [[20, 0]]}], "output": 0}, E)
    rec(objS, "1 in W_4", "S1 self-referencing child (c = i) with an out-of-range variable j = 20", "frozen (a)-(e) (mini.check_wdag)", ok, why)
    ok, why, _ = mini.check_wdag({"D": 4, "nv": 20, "neq": 19, "nodes": [{"id": 0, "rows": [[[20], 0]], "prods": []}], "output": 0}, E)
    rec(objS, "1 in W_4", "S2 mu containing v_20 (outside B)", "frozen (a)-(e)", ok, why)
    rows = [[[], k] for k in range(len(sat_fs))]
    ok, why, _ = mini.check_wdag({"D": 4, "nv": 20, "neq": 19, "nodes": [{"id": 0, "rows": rows, "prods": []}], "output": 0}, E)
    rec(objS, "1 in W_4", "S3 output whose poly merely contains the constant term", "frozen (a)-(e)", ok, why)
    ok, why, _ = mini.check_wdag({"D": 4, "nv": 20, "neq": 19, "nodes": [{"id": 0, "rows": [[[], 18]], "prods": []}], "output": 0}, E)
    rec(objS, "1 in W_4", "S4 rows on the zero equations k >= neq_s (padding)", "frozen (a)-(e)", ok, why)
    res["notes"].append({"S_reading": "For a satisfiable system no node of ANY syntactically well-formed DAG (degree discipline or not) can equal 1: every rows term and every product lies in the ideal, which vanishes at a solution. Soundness there needs only exact B arithmetic and the exact equality of rule (e); the degree rules bind only on unsatisfiable systems where 1 is in the ideal but not in W_4 (the frozen control arms N-ELL19, N-F219, N-AFF19)."})
    # evaluation-functional ann-v1 on the satisfiable system: a valid certificate of the TRUE statement
    mini._ann_init()
    p = sols[0]
    lam = np.array([1 if (m & p) == m else 0 for m in mini.ANN], dtype=np.uint8)
    lam_S_valid = lam.copy()
    ok, why, st = mini.check_ann({"D": 4, "nv": 20, "neq": 19, "L_hex": [to_hex(lam)]}, E)
    res["notes"].append({"S_evaluation_functional_ann_v1": {"valid": ok, "why": why, "stats": st,
                         "reading": "lambda_p(g) = g(p) at a solution p (extended by 0 on v_%d..v_19): S = {g : g(p) = 0} contains every M_4 row and is closed under v_j (g(p) = 0 implies (v_j g)(p) = 0), and lambda_p(1) = 1. A one-functional ann-v1 is therefore valid on every satisfiable system; this is why the blind ann-v1 of the five S3-SAT100 pool systems can be small (2, 4 or 6 functionals). True statement, correctly accepted." % nS}})

    # ============================================= Y4 (1 in W_4, 1 not in M_4), frozen format
    Y = found["Y4"][0]
    nY, neqY = Y["n"], Y["neq"]
    fY = [set(f) for f in Y["fs"]]
    RY = se.Ring(nY, 4)
    wd, WY = wdag_from_tags(RY, fY, 4)
    EY = embed(fY)
    wd20 = dict(wd, nv=20, neq=19)
    ok, why, st = mini.check_wdag(wd20, EY)
    objY = "Y4: own system, n = %d, neq = %d; literal W_4 dims %s, 1 first at iteration %s; 1 not in M_4; embedded in (4, 20, 19)" % (nY, neqY, WY["dims"], WY["one_first_iteration"])
    res["notes"].append({"Y4_positive_control": {"wdag_nodes": len(wd["nodes"]), "valid_under_frozen_checker": ok, "why": why,
                                                 "reading": "the embedded system is W_4-refuted in the frozen format, so every ann-v1 below targets a FALSE statement"}})
    M4 = mini.m4_rows(EY)
    rk, AnnM4 = mini.gf2_rref_nullspace(M4)
    L_full = AnnM4
    const_col = 6195
    ok, why, st = mini.check_ann({"D": 4, "nv": 20, "neq": 19, "L_hex": [to_hex(x) for x in L_full]}, EY, M4=M4)
    rec(objY, "1 not in W_4", "B1 L = basis of the annihilator of rowspace(M_4) (|L| = %d)" % len(L_full), "frozen (A1)-(A3) (mini.check_ann)", ok, why,
        {"stats": st, "A3_would_hold": bool(L_full[:, const_col].any())})
    # B2: lenient (A2) readings that would be UNSOUND
    first3 = 6196 - 1351
    #  (i) filter a basis of S (free-column null-space basis of the full L) to its degree <= 3 members
    _, Sbasis = mini.gf2_rref_nullspace(L_full)
    Kf = Sbasis[~Sbasis[:, :first3].any(axis=1)]
    lenient_i = _a2_on(Kf, L_full)
    #  (ii) the literal basis of S cap B_<=3
    _, K3 = mini.gf2_rref_nullspace(L_full[:, first3:])
    Kfull = np.zeros((K3.shape[0], 6196), dtype=np.uint8)
    Kfull[:, first3:] = K3
    literal = _a2_on(Kfull, L_full)
    rank_Kf = mini.gf2_rank(Kf) if Kf.shape[0] else 0
    rec(objY, "1 not in W_4", "B2(i) LENIENT (A2): K = members of a free-column basis of S that happen to lie in B_<=3 (not a basis of S cap B_<=3)",
        "lenient variant (NOT the frozen text)", lenient_i[0], lenient_i[1],
        {"dim_S_cap_B3": int(K3.shape[0]), "lenient_K_size": int(Kf.shape[0]), "lenient_K_rank": int(rank_Kf),
         "frozen_A2_on_literal_basis": {"passes": literal[0], "first": literal[1]}})
    #  (iii) a prover-supplied K: the degree <= 3 echelon rows of rowspace(M_4) that were multiplied ONLY by v_0
    #        (checking a subset of j) -- a partial check
    part = _a2_on(Kfull, L_full, js=[0])
    rec(objY, "1 not in W_4", "B2(iii) PARTIAL (A2): the literal K but only j = 0 checked", "partial variant (NOT the frozen text)", part[0], part[1])
    # B4: a single functional of the annihilator with lambda(1) = 1
    idx1 = int(np.flatnonzero(L_full[:, const_col])[0])
    ok, why, st = mini.check_ann({"D": 4, "nv": 20, "neq": 19, "L_hex": [to_hex(L_full[idx1])]}, EY, M4=M4)
    rec(objY, "1 not in W_4", "B4 one functional of ann(M_4) with lambda(1) = 1", "frozen (A1)-(A3)", ok, why, {"stats": st})
    # B5: random sub-families of ann(M_4) that keep a lambda(1) = 1 member
    rej = {}
    for t in range(30):
        sel = [i for i in range(L_full.shape[0]) if rng.random() < rng.choice([0.2, 0.5, 0.9])]
        if idx1 not in sel:
            sel.append(idx1)
        ok, why, _ = mini.check_ann({"D": 4, "nv": 20, "neq": 19, "L_hex": [to_hex(L_full[i]) for i in sel]}, EY, M4=M4)
        key = "accepted" if ok else why.split(" ")[0]
        rej[key] = rej.get(key, 0) + 1
    rec(objY, "1 not in W_4", "B5 30 random sub-families of ann(M_4) containing a lambda(1) = 1 member", "frozen (A1)-(A3)",
        rej.get("accepted", 0) > 0, "outcomes %s" % rej, {"outcomes": rej})
    # B6: evaluation functional at a non-solution
    pY = 0
    lam = np.array([1 if (m & pY) == m else 0 for m in mini.ANN], dtype=np.uint8)
    ok, why, _ = mini.check_ann({"D": 4, "nv": 20, "neq": 19, "L_hex": [to_hex(lam)]}, EY, M4=M4)
    rec(objY, "1 not in W_4", "B6 evaluation functional at a point (no solution exists)", "frozen (A1)-(A3)", ok, why)
    # B7: the valid ann-v1 of the satisfiable system S transplanted onto Y4
    lamS = np.array([1 if (m & sols[0]) == m else 0 for m in mini.ANN], dtype=np.uint8)
    ok, why, _ = mini.check_ann({"D": 4, "nv": 20, "neq": 19, "L_hex": [to_hex(lamS)]}, EY, M4=M4)
    rec(objY, "1 not in W_4", "B7 the valid one-functional ann-v1 of S transplanted onto Y4 (S is Y4 minus one equation)", "frozen (A1)-(A3)", ok, why)
    # B8: A3-only negative: empty L, and L without its lambda(1) = 1 member on a TRUE non-refutation (S)
    try:
        ok, why, _ = mini.check_ann({"D": 4, "nv": 20, "neq": 19, "L_hex": []}, E)
    except Exception as e:  # a raise is a rejection, never an acceptance
        ok, why = False, "checker raised %s (mini.check_ann does not special-case an empty L; a raise is not an acceptance)" % type(e).__name__
    res["notes"].append({"A3_only_negative_empty_L_on_S": {"accepted": ok, "why": why}})
    # A3-only negative on a TRUE non-refutation: the valid evaluation functional with its constant coordinate cleared
    lam0 = lam_S_valid.copy()
    lam0[6195] = 0
    ok, why, _ = mini.check_ann({"D": 4, "nv": 20, "neq": 19, "L_hex": [to_hex(lam0)]}, E)
    res["notes"].append({"A3_negative_constant_cleared_on_S": {"accepted": ok, "why": why}})
    res["seconds"] = round(time.time() - t0, 1)
    json.dump(res, open(outp, "w"), indent=1, default=str)
    print("done", res["seconds"], "s")


def _poly(rows, fs):
    acc = set()
    for mu, k in rows:
        acc ^= mini.mono_mul(fs[k], mini.mask_of(mu))
    return acc


def _a2_on(K, L, js=range(20)):
    """lambda(v_j k) = 0 for every k in K (rows, full 6196 coordinates), j, lambda."""
    mini._ann_init()
    if K.shape[0] == 0:
        return True, "K empty: (A2) vacuous"
    for j in js:
        tgt = np.array([mini.ANN_POS[m | (1 << j)] if mini.popcount(m | (1 << j)) <= 4 else -1 for m in mini.ANN], dtype=np.int64)
        Pj = np.zeros((K.shape[0], 6196), dtype=np.int64)
        cols = np.flatnonzero(K.any(axis=0))
        for c in cols:
            if tgt[c] < 0:
                return False, "product leaves B_<=4 (K has degree-4 content)"
            Pj[:, tgt[c]] += K[:, c]
        Pj = (Pj & 1).astype(np.uint8)
        bad = np.argwhere(mini.matmul2(L, Pj.T))
        if bad.size:
            return False, "(A2) lambda %d nonzero on v_%d * K[%d]" % (bad[0][0], j, bad[0][1])
    return True, "passed"


if __name__ == "__main__":
    main()
