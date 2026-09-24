"""BR-2 self-tests for the blind re-derivation TASK-20260924-1f6a3c.

Declared seed: SELFTEST_SEED = 2058812 (= 0x1f6a3c, the task token). It is not a
seed of either specification. Sub-streams: numpy.random.default_rng([SEED, i]).
No blind input is used here except the curve coefficients (A, B), which are part
of the statement. Every test returns a dict with "pass" and its evidence.
"""
import random
import sys
import time

import numpy as np

import gf2n as F
import boolsys as BS
import closure as CL
import gf2lin as GL
import sroutes as SR
import wcert_check as WC
from brute import Brute
from ec import Curve, S3

SELFTEST_SEED = 2058812


def rng(i):
    return np.random.default_rng([SELFTEST_SEED, i])


def t_irreducible():
    rep = F.irreducibility_report()
    return {"pass": bool(rep["irreducible"]), **{k: v for k, v in rep.items() if k != "irreducible"}}


def t_field_axioms(n=2000):
    g = rng(1)
    bad = 0
    for _ in range(n):
        a, b, c = (int(x) for x in g.integers(0, 1 << 17, size=3))
        if F.mul(F.mul(a, b), c) != F.mul(a, F.mul(b, c)):
            bad += 1
        if F.mul(a, b ^ c) != F.mul(a, b) ^ F.mul(a, c):
            bad += 1
        if F.mul(a, b) != F.mul(b, a):
            bad += 1
        if a and F.mul(a, F.inv(a)) != 1:
            bad += 1
        if F.sq(F.sqrt(a)) != a:
            bad += 1
    return {"pass": bad == 0, "triples": n, "failures": bad}


def t_S3_point_addition(A, B, n=1000):
    E = Curve(A, B)
    g = rng(2)
    checked = bad = skipped = 0
    for _ in range(n):
        P1 = E.random_point(g)
        P2 = E.random_point(g)
        if P1[0] == P2[0]:
            skipped += 1
            continue
        for Q in (E.add(P1, P2), E.add(P1, E.neg(P2))):
            assert E.on_curve(Q)
            checked += 1
            if S3(P1[0], P2[0], Q[0], B) != 0:
                bad += 1
    # negative control: a random third abscissa should almost never satisfy S_3
    neg_hits = 0
    for _ in range(200):
        P1 = E.random_point(g)
        P2 = E.random_point(g)
        x3 = int(g.integers(0, 1 << 17))
        if S3(P1[0], P2[0], x3, B) == 0:
            neg_hits += 1
    return {"pass": bad == 0 and checked >= 200 and neg_hits <= 5, "pairs": n,
            "relations_checked": checked, "failures": bad, "skipped_equal_x": skipped,
            "negative_control_random_x3_hits_of_200": neg_hits}


def t_descended_vs_direct(B, n=1000):
    g = rng(3)
    bad = 0
    bad_hand = 0
    xRs = [0, 1, 5, 511, 512] + [int(x) for x in g.integers(0, 1 << 17, size=45)]
    eq_cache = {}
    hand_cache = {}
    for xR in xRs:
        eq_cache[xR] = BS.descended_equations(xR, B)
        hand_cache[xR] = [set(e) for e in WC.equations_curve(xR, B)]
        if eq_cache[xR] != hand_cache[xR]:
            bad_hand += 1
    maxdeg = max(BS.popcount(m) for eqs in eq_cache.values() for e in eqs for m in e)
    for i in range(n):
        xR = xRs[i % len(xRs)]
        v = int(g.integers(0, 1 << 18))
        x1 = v & 511
        x2 = v >> 9
        direct = S3(x1, x2, xR, B)
        desc = BS.eval_eqs(eq_cache[xR], v)
        if direct != desc:
            bad += 1
    return {"pass": bad == 0 and bad_hand == 0 and maxdeg <= 2, "points": n,
            "distinct_xR": len(xRs), "failures": bad,
            "engine_vs_checker_handformula_mismatches": bad_hand, "max_monomial_degree": maxdeg}


def t_macaulay_naive(B, MI, n=50):
    import sympy
    vs = sympy.symbols("v0:18")
    g = rng(4)
    M4 = BS.Macaulay(4, MI)
    xR = int(g.integers(512, 1 << 17))
    eqs = BS.descended_equations(xR, B)
    rows = M4.rows(eqs)
    bad = 0
    picks = [int(x) for x in g.integers(0, M4.R, size=n)]
    for r in picks:
        mu, k = M4.row_key(r)
        f = sum((sympy.Mul(*[vs[i] for i in BS.mask_to_list(m)]) for m in eqs[k]), sympy.Integer(0))
        mono = sympy.Mul(*[vs[i] for i in mu]) if mu else sympy.Integer(1)
        P = sympy.Poly(sympy.expand(mono * f), *vs, modulus=2) if f != 0 else None
        naive = set()
        if P is not None:
            for exps, c in P.terms():
                if int(c) % 2:
                    m = 0
                    for i, e in enumerate(exps):
                        if e:
                            m |= 1 << i
                    naive ^= {m}
        eng = set(MI.masks_from_vec(rows[r]))
        if eng != naive:
            bad += 1
    return {"pass": bad == 0, "rows_checked": n, "failures": bad, "row_indices": picks}


def t_fixtures(MI):
    M3 = BS.Macaulay(3, MI)
    M4 = BS.Macaulay(4, MI)
    out = {"M3": [M3.R, M3.C], "M4": [M4.R, M4.C]}
    ok = out["M3"] == [323, 988] and out["M4"] == [2924, 4048]
    if MI.Dmax >= 5:
        M5 = BS.Macaulay(5, MI)
        out["M5"] = [M5.R, M5.C]
        ok = ok and out["M5"] == [16796, 12616]
    # column order checks: constant last, degree non-increasing, strict comparator
    cols = BS.column_order(4)
    ok_order = cols[-1] == 0 and all(BS.popcount(cols[i]) >= BS.popcount(cols[i + 1]) for i in range(len(cols) - 1))
    ok_order = ok_order and all(BS.degrevlex_greater(cols[i], cols[i + 1]) for i in range(len(cols) - 1))
    FULL = (1 << 18) - 1
    key_order = sorted(cols, key=lambda m: (-BS.popcount(m), -((~m) & FULL)))
    out["column_order_matches_complement_key"] = key_order == cols
    out["column_order_first5"] = [BS.mask_to_list(m) for m in cols[:5]]
    out["column_order_last5"] = [BS.mask_to_list(m) for m in cols[-5:]]
    mus = BS.row_mu_order(2)
    out["row_mu_first5"] = [BS.mask_to_list(m) for m in mus[:5]]
    out["pass"] = bool(ok and ok_order)
    return out


def t_multiplier(MI, n=300):
    g = rng(5)
    mult = CL.Multiplier(MI, 4)
    vecs = []
    for _ in range(n):
        v = 0
        for b in g.integers(0, MI.N[3], size=int(g.integers(1, 60))):
            v ^= 1 << int(b)
        vecs.append(v)
    prods = mult.products(vecs)
    bad = 0
    for v, row in zip(vecs, prods):
        for j in range(18):
            if row[j] != mult.product_single_naive(v, j):
                bad += 1
    return {"pass": bad == 0, "vectors": n, "failures": bad}


def _random_system(g, nv, m, dens, plant):
    mons = [x for x in BS.monomials_upto(2, nv)]
    eqs = []
    sol = int(g.integers(0, 1 << nv)) if plant else None
    for _ in range(m):
        e = set(mm for mm in mons if g.random() < dens)
        if plant:
            val = 0
            for mm in e:
                if mm & sol == mm:
                    val ^= 1
            if val:
                e ^= {0}
        eqs.append(e)
    return eqs


def _engine_closure(eqs, nv, D):
    MI = BS.MonomialIndex(D, nv)
    Mac = BS.Macaulay(D, MI, neq=len(eqs))
    rows = Mac.rows(eqs)
    mult = CL.Multiplier(MI, D)
    res = CL.literal_closure(rows, MI, D, mult)
    return res, MI, Mac, rows, mult


def t_wd_bruteforce(n_required=5):
    """6 variables, D = 3 (the card's requirement), plus 4-variable systems at D = 3, 4.
    Three implementations: the engine (literal rule), brute-force enumeration of every
    element (brute.py; exact while under its cap, otherwise compared on the prefix it
    completed, including the first-one iteration if reached), and a dense kernel-based
    implementation (dense.py) compared on everything."""
    from dense import Dense
    g = rng(6)
    records = []
    plan = ([("sparse", m) for m in (1, 2, 3) for _ in range(6)]
            + [("overdet", m) for m in (4, 5, 6, 7, 8) for _ in range(6)])
    for kind, m in plan:
        if kind == "sparse":
            dens = float(g.choice([0.15, 0.25, 0.4]))
            plant = bool(g.integers(0, 4) != 0)
        else:
            dens = 0.35
            plant = bool(g.integers(0, 3) == 0)
        eqs = _random_system(g, 6, m, dens, plant)
        res, MI, _, _, _ = _engine_closure(eqs, 6, 3)
        dn = Dense(6, 3).closure(eqs)
        bru = Brute(6, 3)
        br = bru.closure(eqs)
        rec = {"nv": 6, "D": 3, "m": m, "planted": plant, "engine_dims": res["dims"],
               "engine_first_one": res["first_one_iteration"], "dense_dims": dn["dims"],
               "dense_first_one": dn["first_one_iteration"], "brute_completed": br["completed"]}
        agree_dense = (res["dims"] == dn["dims"] and res["first_one_iteration"] == dn["first_one_iteration"]
                       and res["fixpoint_index"] == dn["fixpoint_index"])
        if br["completed"]:
            same_space = res["final_dim"] == br["dims"][-1] and all(
                bru.vec(MI.masks_from_vec(b)) in br["elements"] for b in res["space"].basis.values())
            agree_brute = (res["dims"] == br["dims"] and res["fixpoint_index"] == br["fixpoint_index"]
                           and res["first_one_iteration"] == br["first_one_iteration"] and same_space)
            rec["brute_dims"] = br["dims"]
            rec["brute_first_one"] = br["first_one_iteration"]
        else:
            pre = br["dims_prefix"]
            fo = br["first_one_iteration_prefix"]
            agree_brute = (res["dims"][:len(pre)] == pre
                           and (fo is None or fo == res["first_one_iteration"])
                           and (fo is not None or res["first_one_iteration"] is None
                                or res["first_one_iteration"] >= len(pre)))
            rec["brute_dims_prefix"] = pre
            rec["brute_first_one_prefix"] = fo
        rec["agree_dense"] = agree_dense
        rec["agree_brute"] = agree_brute
        records.append(rec)
    extra = []
    for D in (3, 4):
        for _ in range(12):
            m = int(g.integers(1, 7))
            plant = bool(g.integers(0, 2))
            eqs = _random_system(g, 4, m, 0.35, plant)
            br = Brute(4, D).closure(eqs)
            res, MI, _, _, _ = _engine_closure(eqs, 4, D)
            dn = Dense(4, D).closure(eqs)
            bru = Brute(4, D)
            same_space = res["final_dim"] == br["dims"][-1] and all(
                bru.vec(MI.masks_from_vec(b)) in br["elements"] for b in res["space"].basis.values())
            agree = (br["completed"] and res["dims"] == br["dims"] == dn["dims"]
                     and res["first_one_iteration"] == br["first_one_iteration"] == dn["first_one_iteration"]
                     and same_space)
            extra.append({"nv": 4, "D": D, "m": m, "planted": plant, "engine_dims": res["dims"],
                          "brute_dims": br.get("dims"), "dense_dims": dn["dims"],
                          "first_one": [res["first_one_iteration"], br.get("first_one_iteration"), dn["first_one_iteration"]],
                          "agree": agree})
    full6 = [r for r in records if r["brute_completed"]]
    passed = (len(full6) >= n_required and all(r["agree_brute"] and r["agree_dense"] for r in records)
              and all(r["agree"] for r in extra))
    return {"pass": passed, "seed": [SELFTEST_SEED, 6],
            "six_var_D3_systems": len(records),
            "six_var_D3_fully_enumerated": len(full6),
            "six_var_D3_fully_enumerated_with_growth_beyond_W0": sum(1 for r in full6 if len(r["brute_dims"]) > 2),
            "six_var_D3_with_one_in_W": sum(1 for r in records if r["engine_first_one"] is not None),
            "six_var_D3_with_one_first_at_iteration_ge_1": sum(1 for r in records if (r["engine_first_one"] or 0) >= 1),
            "six_var_D3_brute_prefix_reached_first_one_ge_1": sum(1 for r in records if not r["brute_completed"] and (r.get("brute_first_one_prefix") or 0) >= 1),
            "six_var_D3_with_two_or_more_growth_steps": sum(1 for r in records if len(r["engine_dims"]) > 3),
            "four_var_systems": len(extra),
            "four_var_with_one_in_W": sum(1 for r in extra if r["first_one"][0] is not None),
            "records": records, "four_var_records": extra}


def _corruptions(cert):
    import copy
    out = []
    els = cert["elements"]
    oid = cert["output_id"]
    # 1. remove one row from the output element
    c = copy.deepcopy(cert)
    o = [e for e in c["elements"] if e["id"] == oid][0]
    if o["rows"]:
        o["rows"].pop(len(o["rows"]) // 2)
        out.append(("drop_one_row_from_output", c))
    # 2. change k of one row in the first element that has rows
    c = copy.deepcopy(cert)
    for e in c["elements"]:
        if e["rows"]:
            mu, k = e["rows"][0]
            e["rows"][0] = [mu, (k + 1) % 17]
            break
    out.append(("change_k_of_one_row", c))
    # 3. change j of one product
    c = copy.deepcopy(cert)
    for e in c["elements"]:
        if e["products"]:
            j, p = e["products"][0]
            e["products"][0] = [(j + 1) % 18, p]
            break
    out.append(("change_j_of_one_product", c))
    # 4. output element moved first (parents no longer earlier)
    c = copy.deepcopy(cert)
    c["elements"] = [e for e in c["elements"] if e["id"] == oid] + [e for e in c["elements"] if e["id"] != oid]
    out.append(("output_moved_before_parents", c))
    # 5. a degree-3 mu in a row
    c = copy.deepcopy(cert)
    for e in c["elements"]:
        if e["rows"]:
            mu, k = e["rows"][0]
            e["rows"][0] = [[0, 1, 2], k]
            break
    out.append(("degree3_mu", c))
    # 6. output_id points to a parent
    c = copy.deepcopy(cert)
    if len(els) > 1:
        c["output_id"] = els[0]["id"]
        out.append(("output_id_points_to_parent", c))
    return out


def t_certificate_checker(A, B, MI, max_tries=200):
    """Find (own seed) a synthetic curve target with s = 0, 1 not in R_4 and 1 in W_4,
    so the witness needs products; extract its certificate; the checker must accept
    it and reject every corruption. Also: 4-variable D = 4 systems padded to 17
    equations, certificates extracted and checked."""
    g = rng(7)
    M4 = BS.Macaulay(4, MI)
    mult = CL.Multiplier(MI, 4)
    found = None
    tries = 0
    for _ in range(max_tries):
        tries += 1
        xR = int(g.integers(512, 1 << 17))
        eqs = BS.descended_equations(xR, B)
        s1, _ = SR.route1_exhaustive(eqs)
        if s1:
            continue
        rows = M4.rows(eqs)
        if GL.rank_of(rows).has_one():
            continue
        res = CL.literal_closure(rows, MI, 4, mult)
        if res["one_in_W"]:
            found = (xR, eqs, rows, res)
            break
    out = {"tries": tries}
    if found is None:
        out["pass"] = False
        out["note"] = "no synthetic witness found"
        return out
    xR, eqs, rows, res = found
    ext = CL.extract_certificate(rows, M4, MI, 4, mult)
    cert = {"schema": "certbin.wcert.v1", "label": "SELFTEST", **ext["certificate"]}
    heqs = WC.equations_curve(xR, B)
    ok, reason, stats = WC.check(cert, heqs)
    out["valid_witness"] = {"accepted": ok, "reason": reason, **stats,
                            "uses_products": stats["n_product_refs"] > 0}
    rej = []
    for name, c in _corruptions(cert):
        ok2, reason2, _ = WC.check(c, heqs)
        rej.append({"corruption": name, "accepted": ok2, "reason": reason2})
    out["corrupted"] = rej
    # 4-variable systems at D = 4, padded to 17 equations
    small = []
    for _ in range(10):
        m = int(g.integers(2, 6))
        eqs4 = _random_system(g, 4, m, 0.35, False) + [set() for _ in range(17 - m)]
        res4, MI4, Mac4, rows4, mult4 = _engine_closure(eqs4, 4, 4)
        if not res4["one_in_W"]:
            small.append({"m": m, "one_in_W": False})
            continue
        ext4 = CL.extract_certificate(rows4, Mac4, MI4, 4, mult4)
        c4 = {"schema": "certbin.wcert.v1", "label": "SELFTEST4", **ext4["certificate"]}
        ok4, reason4, st4 = WC.check(c4, [frozenset(e) for e in eqs4])
        small.append({"m": m, "one_in_W": True, "first_one": res4["first_one_iteration"],
                      "cert_levels": ext4["levels_used"], "accepted": ok4, "reason": reason4})
    out["four_var_padded"] = small
    out["pass"] = bool(ok and len(rej) >= 3 and not any(r["accepted"] for r in rej)
                       and all(s["accepted"] for s in small if s["one_in_W"])
                       and all(s["cert_levels"] == s["first_one"] for s in small if s["one_in_W"]))
    return out


def t_sroutes(B, n=12):
    g = rng(8)
    xRs = [0, 1, 300, 511] + [int(x) for x in g.integers(512, 1 << 17, size=n)]
    recs = []
    ok = True
    for xR in xRs:
        eqs = BS.descended_equations(xR, B)
        s1, sol1 = SR.route1_exhaustive(eqs)
        s2, sol2, bad = SR.route2_rootfinding(xR, B)
        agree = s1 == s2 and sol1 == sol2 and bad == 0
        ok = ok and agree
        recs.append({"xR": xR, "agree": agree, "bad_roots": bad})
    return {"pass": ok, "targets": len(xRs), "records": recs}


def run_all(A, B, MI):
    tests = [
        ("irreducibility", lambda: t_irreducible()),
        ("field_axioms", lambda: t_field_axioms()),
        ("S3_vs_point_addition", lambda: t_S3_point_addition(A, B)),
        ("descended_vs_direct_F2_17", lambda: t_descended_vs_direct(B)),
        ("macaulay_rows_vs_naive_sympy", lambda: t_macaulay_naive(B, MI)),
        ("fixture_dimensions_and_orders", lambda: t_fixtures(MI)),
        ("multiplier_vs_naive", lambda: t_multiplier(MI)),
        ("WD_literal_vs_bruteforce", lambda: t_wd_bruteforce()),
        ("wcert_checker", lambda: t_certificate_checker(A, B, MI)),
        ("s_routes_agree_synthetic", lambda: t_sroutes(B)),
    ]
    results = {}
    for name, fn in tests:
        t0 = time.time()
        r = fn()
        r["seconds"] = round(time.time() - t0, 3)
        results[name] = r
        print("selftest %-32s %s (%.1fs)" % (name, "PASS" if r["pass"] else "FAIL", r["seconds"]), flush=True)
    results["all_pass"] = all(r["pass"] for r in results.values() if isinstance(r, dict))
    results["seed"] = SELFTEST_SEED
    return results


if __name__ == "__main__":
    import json
    A, B = 97044, 126251
    MI = BS.MonomialIndex(5 if "--d5" in sys.argv else 4)
    res = run_all(A, B, MI)
    print(json.dumps({k: (v["pass"] if isinstance(v, dict) else v) for k, v in res.items()}))
