#!/usr/bin/env python3
"""Phase 0 of EXP-CERTBIN-a58c63: C-SELF and C-FIX (both regimes, every cell),
before any frozen stream is drawn.

Copied from EXP-CERTBIN-4e92d7/impl/selftest.py and extended to both fields
and both regimes (see impl-provenance.json). All randomness:
numpy.random.Generator(numpy.random.PCG64(S_selftest)), S_selftest =
2026092420099, one generator consumed in the order of the items below.
Writes selftest.json; exit status 0 iff every item passes.
"""
import argparse
import datetime
import functools
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np  # noqa: E402

from gf2n import Field, TableField, MODULUS17, is_irreducible, find_pentanomial, modulus_string  # noqa: E402
from curve import Curve, s3_eval_school  # noqa: E402
from macaulay import Descent, MacaulayShape, mu_order, degrevlex_greater  # noqa: E402
from oracles import solve_quadratic, oracle_A, OracleB, OracleC, s3_coeffs  # noqa: E402
from elim import eliminate as eliminate_A, gf2_rank_rows  # noqa: E402
from regimeB import ShapeB, GFTabs, eliminate as eliminate_B, column_pass as column_pass_B, row_pass, \
    eval_linearized, replay, guided  # noqa: E402
from delta import DeltaCalc  # noqa: E402
from detmod import DetField, determinant  # noqa: E402

S_SELFTEST = 2026092420099
FIX_A = {(17, 6): {3: (221, 299), 4: (1343, 794)}, (19, 6): {3: (247, 299), 4: (1501, 794)},
         (17, 5): {3: (187, 176), 4: (952, 386)}, (19, 5): {3: (209, 176), 4: (1064, 386)}}
FIX_B = {6: (2028, 2278), 5: (3276, 2278)}
CELLS = [(17, 6), (19, 6), (17, 5), (19, 5)]


def rint(rng, lo, hi):
    return int(rng.integers(lo, hi))


def t_moduli():
    ok17, det17 = is_irreducible(MODULUS17)
    mod19, abc, ntested, rejected = find_pentanomial(19)
    ok19, det19 = is_irreducible(mod19)
    return {"id": "moduli_irreducible", "pass": bool(ok17 and ok19 and MODULUS17 == (1 << 17) | (1 << 3) | 1),
            "n17": {"modulus": modulus_string(MODULUS17), "modulus_int": MODULUS17, "irreducible": ok17,
                    "details": det17},
            "n19": {"rule": "t^19 + t^a + t^b + t^c + 1, 19 > a > b > c > 0, irreducible, lexicographically smallest (a, b, c); exhaustive test in lexicographic order",
                    "selected_abc": list(abc), "modulus": modulus_string(mod19), "modulus_int": mod19,
                    "candidates_tested": ntested, "rejected_reducible": rejected, "irreducible": ok19,
                    "details": det19}}, mod19


def t_field_axioms(F, rng, n):
    N = 10000
    fails = []
    Fs = Field(F.n, F.mod)
    for i in range(N):
        a, b, c = rint(rng, 0, F.q), rint(rng, 0, F.q), rint(rng, 0, F.q)
        m = F.mul
        s = F.mul_school
        checks = {
            "table_eq_school": m(a, b) == s(a, b),
            "commutative": m(a, b) == m(b, a),
            "associative": m(m(a, b), c) == m(a, m(b, c)),
            "distributive": m(a, b ^ c) == m(a, b) ^ m(a, c),
            "identity": m(a, 1) == a,
            "add_inverse": (a ^ a) == 0,
            "mul_inverse": a == 0 or s(a, F.inv(a)) == 1,
            "sqrt": s(F.sqrt(a), F.sqrt(a)) == a,
            "trace_linear": F.trace(a ^ b) == F.trace(a) ^ F.trace(b),
            "trace_matches_definition": F.trace(a) == Fs.trace(a) if i < 200 else True,
        }
        bad = [k for k, v in checks.items() if not v]
        if bad:
            fails.append({"a": a, "b": b, "c": c, "failed": bad})
    # vectorised helpers against scalar
    xs = rng.integers(0, F.q, size=2000)
    ys = rng.integers(0, F.q, size=2000)
    vm = F.vmul(xs, ys)
    vok = all(int(v) == F.mul(int(x), int(y)) for v, x, y in zip(vm, xs, ys))
    return {"id": f"field_axioms_n{n}", "pass": not fails and vok, "triples": N, "vectorised_mul_ok": vok,
            "failures": fails[:20], "n_failures": len(fails)}


SMALL_FIELDS = [(5, (1 << 5) | (1 << 2) | 1), (7, (1 << 7) | (1 << 1) | 1), (9, (1 << 9) | (1 << 4) | 1)]


def t_point_count(rng):
    out = []
    ok_all = True
    for n, mod in SMALL_FIELDS:
        irr, _ = is_irreducible(mod)
        Fs = Field(n, mod)
        A = rint(rng, 0, Fs.q)
        B = rint(rng, 1, Fs.q)
        E = Curve(Fs, A, B)
        c1 = E.count_by_trace()
        c2 = E.count_naive()
        ok = irr and c1 == c2
        ok_all &= ok
        out.append({"n": n, "modulus_int": mod, "irreducible": irr, "A": A, "B": B,
                    "count_by_trace": c1, "count_naive": c2, "pass": ok})
    return {"id": "point_count_small_curves", "pass": ok_all, "curves": out}


def random_point(E, rng):
    while True:
        x = rint(rng, 0, E.F.q)
        P = E.lift_x(x)
        if P is not None:
            if rint(rng, 0, 2):
                P = E.neg(P)
            return P


def t_s3_addition(F, rng, n):
    E = Curve(F, rint(rng, 0, F.q), rint(rng, 1, F.q))
    N = 1000
    fails = []
    skipped = 0
    oncurve_fail = 0
    for _ in range(N):
        P1 = random_point(E, rng)
        P2 = random_point(E, rng)
        if not (E.on_curve(P1) and E.on_curve(P2)):
            oncurve_fail += 1
        for lab, R in (("sum", E.add(P1, P2)), ("diff", E.sub(P1, P2))):
            if R is None:
                skipped += 1
                continue
            if not E.on_curve(R):
                oncurve_fail += 1
            if s3_eval_school(F, E.B, P1[0], P2[0], R[0]) != 0:
                fails.append({"P1": P1, "P2": P2, "which": lab})
    return {"id": f"s3_vs_point_addition_n{n}", "pass": not fails and oncurve_fail == 0,
            "curve": {"A": E.A, "B": E.B}, "pairs": N, "skipped_infinity": skipped,
            "on_curve_failures": oncurve_fail, "failures": fails[:20], "n_failures": len(fails)}


def t_LV(F, n):
    out = []
    ok_all = True
    for l in (5, 6):
        S = ShapeB(F, l)
        lam = S.lam
        xs = np.arange(F.q, dtype=np.int64)
        # vectorised evaluation of L_V on all of F_{2^n}
        acc = np.zeros_like(xs)
        p = xs.copy()
        for li in lam:
            acc ^= F.vmul(p, np.full_like(p, li))
            p = F.vmul(p, p)
        roots = np.flatnonzero(acc == 0)
        exact = roots.tolist() == list(range(1 << l))
        # independent: the product definition prod_{v in V} (X - v) by polynomial multiplication
        poly = [1]
        for v in range(1 << l):
            new = [0] * (len(poly) + 1)
            for i, c in enumerate(poly):
                new[i + 1] ^= c
                new[i] ^= F.mul_school(c, v)
            poly = new
        lin_from_prod = [poly[1 << i] for i in range(l + 1)]
        others_zero = all(c == 0 for e, c in enumerate(poly) if e & (e - 1) != 0 or e == 0)
        ok = exact and lam[0] != 0 and lin_from_prod == lam and others_zero and eval_linearized(F, lam, 5) == int(acc[5])
        ok_all &= ok
        out.append({"l": l, "lambda": lam, "roots_exactly_V": exact, "lambda0_nonzero": lam[0] != 0,
                    "matches_product_definition": lin_from_prod == lam, "non_2power_coeffs_zero": others_zero,
                    "pass": ok})
    return {"id": f"L_V_roots_n{n}", "pass": ok_all, "per_l": out}


def naive_rowB(S, r):
    """Literal polynomial multiplication for row r of M_66 (dict monomial -> coeff)."""
    F = S.F
    info = S.row_order()[r]
    a, b = info["mult"]
    if info["block"] == 0:
        return None  # built by the caller with the instance's g_0
    lam = S.lam
    out = {}
    for i, li in enumerate(lam):
        m = (a + (1 << i), b) if info["block"] == 1 else (a, b + (1 << i))
        out[m] = out.get(m, 0) ^ li
    return {k: v for k, v in out.items() if v}


def t_rowsB(F, rng, n):
    out = []
    ok_all = True
    for l in (5, 6):
        S = ShapeB(F, l)
        B = rint(rng, 1, F.q)
        xR = rint(rng, 0, F.q)
        co = s3_coeffs(F, B, xR)
        M = S.build(co)
        g0 = {(2, 2): co[0], (2, 0): co[1], (0, 2): co[2], (1, 1): co[3], (0, 0): co[4]}
        bad = 0
        # columns: literal descending degrevlex comparison
        def gt(u, v):
            du, dv = u[0] + u[1], v[0] + v[1]
            if du != dv:
                return du > dv
            return u[0] > v[0]
        lit = sorted([(a, e - a) for e in range(67) for a in range(e + 1)],
                     key=functools.cmp_to_key(lambda u, v: -1 if gt(u, v) else (1 if gt(v, u) else 0)))
        cols_ok = lit == S.cols and S.cols[-1] == (0, 0)
        ro = S.row_order()
        rows_ok = [x["mult"] for x in ro[:S.n0]] == [list(m) for m in sorted(
            [(a, e - a) for e in range(63) for a in range(e + 1)], key=lambda m: (m[0] + m[1], -m[0]))]
        for _ in range(50):
            r = rint(rng, 0, S.R)
            info = ro[r]
            if info["block"] == 0:
                a, b = info["mult"]
                want = {}
                for (i, j), c in g0.items():
                    want[(a + i, b + j)] = want.get((a + i, b + j), 0) ^ c
                want = {k: v for k, v in want.items() if v}
            else:
                want = naive_rowB(S, r)
            got = {S.cols[c]: int(M[r, c]) for c in np.flatnonzero(M[r])}
            if want != got:
                bad += 1
        fix = (S.R, S.C) == FIX_B[l] and S.n0 == 2016 and (S.n1 == (6 if l == 6 else 630))
        ok = bad == 0 and cols_ok and rows_ok and fix
        ok_all &= ok
        out.append({"l": l, "rows_checked": 50, "row_mismatches": bad, "column_order_literal_ok": cols_ok,
                    "block0_order_ok": rows_ok, "shape": [S.R, S.C], "pass": ok})
    return {"id": f"regimeB_rows_vs_naive_n{n}", "pass": ok_all, "per_l": out}


def naive_rowA(mu, fk_monos):
    acc = {}
    for m in fk_monos:
        prod = tuple(sorted(set(mu) | set(m)))
        acc[prod] = acc.get(prod, 0) ^ 1
    return {m for m, v in acc.items() if v}


def t_descentA(F, rng, n):
    out = []
    ok_all = True
    for l in (5, 6):
        desc = Descent(F, l)
        B = rint(rng, 1, F.q)
        E0, Ej = desc.affine_basis(B)
        fails = 0
        aff_fails = 0
        for _ in range(1000):
            xR = rint(rng, 0, F.q)
            u = rint(rng, 0, 1 << (2 * l))
            E = desc.descended_E(B, xR)
            if not np.array_equal(E, desc.affine_combine(E0, Ej, xR)):
                aff_fails += 1
            x1, x2 = u & ((1 << l) - 1), u >> l
            direct = s3_eval_school(F, B, x1, x2, xR)
            vals = desc.eval_equations_scalar(E, u)
            if sum(v << k for k, v in enumerate(vals)) != direct:
                fails += 1
        # Macaulay rows vs naive, both D
        mrows = []
        for D in (3, 4):
            S = MacaulayShape(D, desc)
            mons = mu_order(D, desc.nv)
            cmp = functools.cmp_to_key(lambda a, b: -1 if degrevlex_greater(a, b) else (1 if degrevlex_greater(b, a) else 0))
            order_ok = sorted(mons, key=cmp) == S.cols and S.cols[-1] == ()
            row_ok = sorted(mu_order(D - 2, desc.nv), key=lambda m: (len(m), m)) == S.mus
            E = desc.descended_E(B, rint(rng, 0, F.q))
            Md = S.build_dense(E)
            unpack_ok = np.array_equal(S.unpack(S.build(E)), Md)
            bad = 0
            for _ in range(50):
                row = rint(rng, 0, S.R)
                a, k = divmod(row, desc.neq)
                fk = [desc.eq_mons[j] for j in np.flatnonzero(E[k])]
                if naive_rowA(S.mus[a], fk) != {S.cols[c] for c in np.flatnonzero(Md[row])}:
                    bad += 1
            fix = (S.R, S.C) == FIX_A[(n, l)][D]
            mrows.append({"D": D, "column_order_literal_ok": order_ok, "row_order_literal_ok": row_ok,
                          "pack_roundtrip_ok": unpack_ok, "row_mismatches": bad, "fixture_ok": fix})
            ok_all &= order_ok and row_ok and unpack_ok and bad == 0 and fix
        ok = fails == 0 and aff_fails == 0
        ok_all &= ok
        out.append({"l": l, "points": 1000, "descended_vs_direct_failures": fails,
                    "affine_identity_failures": aff_fails, "macaulay": mrows})
    return {"id": f"regimeA_descent_and_rows_n{n}", "pass": ok_all, "per_l": out}


def t_half_trace(F, rng, n):
    N = 10000
    fails = []
    for i in range(N):
        c0 = rint(rng, 0, F.q)
        h = F.half_trace(c0)
        if F.mul(h, h) ^ h != c0 ^ F.trace(c0):
            fails.append({"i": i, "check": "H^2+H=c+Tr(c)"})
        a = rint(rng, 0, F.q) if i % 4 != 1 else 0
        b = rint(rng, 0, F.q) if i % 4 != 2 else 0
        if i % 2 == 0:
            x0 = rint(rng, 0, F.q)
            c = F.mul_school(a, F.mul_school(x0, x0)) ^ F.mul_school(b, x0)
        else:
            x0 = None
            c = rint(rng, 0, F.q)
        kind, roots = solve_quadratic(F, a, b, c)
        if kind == "all":
            if not (a == 0 and b == 0 and c == 0):
                fails.append({"i": i, "check": "all_kind"})
            continue
        for r in roots:
            if F.mul_school(a, F.mul_school(r, r)) ^ F.mul_school(b, r) ^ c != 0:
                fails.append({"i": i, "check": "root_invalid"})
        if len(set(roots)) != len(roots):
            fails.append({"i": i, "check": "duplicate_roots"})
        if x0 is not None and x0 not in roots:
            fails.append({"i": i, "check": "planted_root_missing"})
    ab = []
    for l in (5, 6):
        desc = Descent(F, l)
        oB, oC = OracleB(desc), OracleC(F, l)
        for _ in range(3):
            B = rint(rng, 1, F.q)
            xR = rint(rng, 0, F.q)
            sa = oracle_A(F, B, xR, l)
            sb = oB(desc.descended_E(B, xR))
            sc = oC(s3_coeffs(F, B, xR))
            ab.append({"l": l, "B": B, "xR": xR, "s_A": len(sa), "s_B": len(sb), "s_C": len(sc),
                       "equal_sets": sa == sb == sc})
            if not sa == sb == sc:
                fails.append({"check": "oracle_cross_check", "l": l, "B": B, "xR": xR})
        # planted: a target with a known solution in V x V must be found by all three
        for _ in range(3):
            B = rint(rng, 1, F.q)
            x1, x2 = rint(rng, 0, 1 << l), rint(rng, 0, 1 << l)
            s = x1 ^ x2
            kind, roots = solve_quadratic(F, F.mul(s, s), F.mul(x1, x2), F.mul(F.mul(x1, x2), F.mul(x1, x2)) ^ B)
            if kind != "roots" or not roots:
                continue
            xR = roots[0]
            u = x1 | (x2 << l)
            sa = oracle_A(F, B, xR, l)
            sb = oB(desc.descended_E(B, xR))
            sc = oC(s3_coeffs(F, B, xR))
            ok = u in sa and sa == sb == sc
            ab.append({"l": l, "planted": True, "B": B, "xR": xR, "u": u, "found_and_equal": ok})
            if not ok:
                fails.append({"check": "planted_oracle", "l": l})
    return {"id": f"half_trace_root_finding_and_oracles_n{n}", "pass": not fails, "quadratics": N,
            "oracle_cross_check": ab, "failures": fails[:20], "n_failures": len(fails)}


def literal_elimination_GF(F, rows):
    """Literal transcription of the regime-B rule on Python dict rows
    (column -> element): smallest-original-index unused nonzero row is the
    pivot; row_i <- row_i + (M[i,c]/M[p,c]) row_p for every other unused
    nonzero row; rows never move, pivot rows not rescaled."""
    rows = [dict(r) for r in rows]
    C = 1 + max([c for r in rows for c in r] + [0])
    used = set()
    ops = []
    for c in range(C):
        cand = [i for i in range(len(rows)) if i not in used and rows[i].get(c, 0) != 0]
        if not cand:
            continue
        p = cand[0]
        X = cand[1:]
        for i in X:
            f = F.mul_school(rows[i][c], F.inv(rows[p][c]))
            for cc, v in rows[p].items():
                nv = rows[i].get(cc, 0) ^ F.mul_school(f, v)
                if nv:
                    rows[i][cc] = nv
                else:
                    rows[i].pop(cc, None)
        used.add(p)
        ops.append((p, c, X))
    return ops


def naive_Z(F, Md):
    """Z by prefix ranks (independent: Gaussian elimination from scratch per prefix)."""
    R = Md.shape[0]
    Z = []
    basis = []
    for i in range(R):
        rows = basis + [list(map(int, Md[i]))]
        if rank_GF(F, rows) == len(basis):
            Z.append(i)
        else:
            basis.append(list(map(int, Md[i])))
    return Z


def rank_GF(F, rows):
    A = [list(r) for r in rows]
    rk = 0
    ncol = len(A[0]) if A else 0
    for c in range(ncol):
        piv = next((i for i in range(rk, len(A)) if A[i][c]), None)
        if piv is None:
            continue
        A[rk], A[piv] = A[piv], A[rk]
        iv = F.inv(A[rk][c])
        for i in range(len(A)):
            if i != rk and A[i][c]:
                f = F.mul(A[i][c], iv)
                A[i] = [x ^ F.mul(f, y) for x, y in zip(A[i], A[rk])]
        rk += 1
    return rk


def t_elimB(F, rng, n):
    T = GFTabs(F)
    fails = []
    for m in range(20):
        R = rint(rng, 4, 30)
        C = rint(rng, 4, 40)
        dens = 0.15 + 0.7 * rng.random()
        Md = np.where(rng.random((R, C)) < dens, rng.integers(1, F.q, size=(R, C)), 0).astype(np.uint32)
        if rint(rng, 0, 2) and R > 3:   # plant a dependency
            i, j, k = rint(rng, 0, R), rint(rng, 0, R), rint(rng, 0, R)
            f = rint(rng, 1, F.q)
            Md[k] = Md[i] ^ F.vmul(Md[j].astype(np.int64), np.full(C, f)).astype(np.uint32)
        res, cpass, leads = eliminate_B(Md, T)
        lit = literal_elimination_GF(F, [{c: int(v) for c, v in enumerate(row) if v} for row in Md])
        got = [(p, c, X.tolist()) for p, c, X in zip(res.p, res.c, res.X)]
        Zn = naive_Z(F, Md)
        rk = rank_GF(F, [list(map(int, r)) for r in Md])
        nonpiv = sorted(set(range(R)) - set(res.p))
        # the fixed-schedule replay of a matrix's own op log reproduces its pivots
        rp = replay(Md, T, np.array(res.p), np.array(res.c), res.X)
        ok = (lit == got and cpass and res.Z == Zn and res.rank == rk and nonpiv == res.Z
              and rp["survived"] and rp["first_invalid"] is None and rp["e"] == res.pivot_vals)
        if not ok:
            fails.append({"matrix": m, "R": R, "C": C, "oplog_equal": lit == got, "cpass": cpass,
                          "Z_equal_naive": res.Z == Zn, "rank_equal": res.rank == rk})
    # also: a real M_66 at l = 6, row pass Z vs column-pass non-pivot rows (C-PASS path)
    return {"id": f"regimeB_elimination_vs_literal_n{n}", "pass": not fails, "matrices": 20,
            "checks": "op log (p, c, X) == literal transcription; C-PASS; Z == naive prefix-rank Z; rank == independent rank; own-op-log replay reproduces the pivot entries",
            "failures": fails}


def literal_state(F, rows, steps):
    """Literal transcription of the regime-B rule run for `steps` pivot steps;
    returns (rows, used set, trace list, next column pointer)."""
    rows = [dict(r) for r in rows]
    C = 1 + max([c for r in rows for c in r] + [0])
    used = set()
    trace = []
    for c in range(C):
        if len(trace) >= steps:
            break
        cand = [i for i in range(len(rows)) if i not in used and rows[i].get(c, 0) != 0]
        if not cand:
            continue
        p = cand[0]
        for i in cand[1:]:
            f = F.mul_school(rows[i][c], F.inv(rows[p][c]))
            for cc, v in rows[p].items():
                nv = rows[i].get(cc, 0) ^ F.mul_school(f, v)
                if nv:
                    rows[i][cc] = nv
                else:
                    rows[i].pop(cc, None)
        used.add(p)
        trace.append((p, c))
    return rows, used, trace


def literal_classify(F, rows_t, tr_t, tr_r):
    """AMD-20260924-3a9f06 R0-R6, literally, from the two full traces and the
    target's literal state after k steps."""
    if tr_t == tr_r:
        return "MATCH", False
    k = 0
    while k < min(len(tr_t), len(tr_r)) and tr_t[k] == tr_r[k]:
        k += 1
    if len(tr_r) == k:
        return "PREFIX", False
    if len(tr_t) > k and tr_t[k][1] < tr_r[k][1]:
        return "EXTRA-PIVOT", False
    st, used, _ = literal_state(F, rows_t, k)
    pr, cr = tr_r[k]
    nz = [i for i in range(len(st)) if i not in used and st[i].get(cr, 0) != 0]
    if not nz:
        return "COLUMN", len(tr_t) == k
    if st[pr].get(cr, 0) == 0:
        return "ZERO-PIVOT", False
    if nz[0] < pr:
        return "ROW-ORDER", False
    return "UNCLASSIFIED", False


def t_classify(F, rng, n):
    """The in-pass R0-R6 classifier against the literal transcription, on
    target/reference pairs built to share a trace prefix; and guided = own."""
    T = GFTabs(F)
    fails = []
    seen = {}
    for m in range(200):
        R = rint(rng, 5, 14)
        C = rint(rng, 5, 16)
        dens = 0.25 + 0.5 * rng.random()
        Mr = np.where(rng.random((R, C)) < dens, rng.integers(1, F.q, size=(R, C)), 0).astype(np.uint32)
        Mt = Mr.copy()
        for _ in range(rint(rng, 0, 3)):
            i, j = rint(rng, 0, R), rint(rng, 0, C)
            Mt[i, j] = 0 if rint(rng, 0, 2) else rint(rng, 1, F.q)
        if rint(rng, 0, 4) == 0:   # force a sat-like prefix: zero out the last columns of the target
            Mt[:, C - rint(rng, 1, 3):] = 0
        rres, _, _ = eliminate_B(Mr, T)
        tres, _, _ = eliminate_B(Mt, T, refs=[("r", np.array(rres.p), np.array(rres.c))])
        rows_t = [{c: int(v) for c, v in enumerate(row) if v} for row in Mt]
        want, want_pf = literal_classify(F, rows_t, list(zip(tres.p, tres.c)), list(zip(rres.p, rres.c)))
        got = tres.classif.get("r")
        got_t = got["type"] if got else "MATCH"
        got_pf = got["prefix_flag"] if got else False
        seen[want] = seen.get(want, 0) + 1
        if got_t != want or got_pf != want_pf:
            fails.append({"pair": m, "want": [want, want_pf], "got": [got_t, got_pf]})
        # guided = own on the target's own trace
        g = guided(Mt, T, np.array(tres.p), np.array(tres.c))
        if not (g["broke_at"] is None and g["e"] == list(tres.pivot_vals)
                and all(np.array_equal(a, b) for a, b in zip(g["cleared"], tres.X))):
            fails.append({"pair": m, "guided_equals_own": False})
    return {"id": f"regimeB_classifier_vs_literal_n{n}", "pass": not fails, "pairs": 200,
            "types_exercised": seen, "failures": fails[:20],
            "note": "AMD-20260924-3a9f06 R0-R6 and C-6 (additional item)"}


def t_elimA_sanity(rng):
    from selftest_gf2 import literal_elimination_gf2
    fails = 0
    for _ in range(40):
        R = rint(rng, 5, 60)
        C = rint(rng, 5, 130)
        W = (C + 63) // 64
        Md = (rng.random((R, C)) < rng.random()).astype(np.uint8)
        if rint(rng, 0, 2):
            Md[rint(rng, 0, R)] = Md[rint(rng, 0, R)] ^ Md[rint(rng, 0, R)]
        pad = np.zeros((R, W * 64 - C), dtype=np.uint8)
        Mp = np.packbits(np.concatenate([Md, pad], axis=1), axis=1, bitorder="little").view(np.uint64).reshape(R, W).copy()
        res, cpass, _ = eliminate_A(Mp, C)
        rk = gf2_rank_rows(Mp)
        nonpiv = sorted(set(range(R)) - set(res.p))
        lit = literal_elimination_gf2(Md)
        got = [(p, c, X.tolist()) for p, c, X in zip(res.p, res.c, res.X)]
        if res.rank != rk or not cpass or nonpiv != res.Z or lit != got:
            fails += 1
    return {"id": "regimeA_elimination_vs_literal", "pass": fails == 0, "matrices": 40, "failures": fails}


def lagrange_coeffs(F, vals, l):
    """Direct Lagrange interpolation: sum_i f(v_i) prod_{j != i} (X - v_j)/(v_i - v_j)."""
    V = list(range(1 << l))
    out = [0] * len(V)
    for i, vi in enumerate(V):
        if vals[i] == 0:
            continue
        poly = [1]
        den = 1
        for j, vj in enumerate(V):
            if j == i:
                continue
            new = [0] * (len(poly) + 1)
            for e, c in enumerate(poly):
                new[e + 1] ^= c
                new[e] ^= F.mul_school(c, vj)
            poly = new
            den = F.mul_school(den, vi ^ vj)
        sc = F.mul_school(vals[i], F.inv(den))
        for e, c in enumerate(poly):
            out[e] ^= F.mul_school(c, sc)
    return out


def t_phi(F, rng, n):
    out = []
    ok_all = True
    for l in (5, 6):
        S = ShapeB(F, l)
        dc = DeltaCalc(F, l, S.lam[0])
        bad = 0
        for _ in range(5):
            vals = [rint(rng, 0, F.q) for _ in range(1 << l)]
            want = lagrange_coeffs(F, vals, l)
            got = dc.mg.mul(dc.Phi, np.array(vals, dtype=np.int64)[:, None])[:, 0].tolist()
            if want != got:
                bad += 1
        # top-coefficient identity on random nonzero 2-D functions
        idf = 0
        for _ in range(5):
            g = rng.integers(1, F.q, size=(1 << l, 1 << l))
            d = dc.compute(g)
            if not d["top_identity_ok"]:
                idf += 1
        ok = bad == 0 and idf == 0
        ok_all &= ok
        out.append({"l": l, "functions": 5, "phi_vs_lagrange_mismatches": bad,
                    "top_identity_failures_on_5_random_functions": idf, "pass": ok})
    return {"id": f"Phi_vs_Lagrange_n{n}", "pass": ok_all, "per_l": out}


def t_det(F, rng, n):
    DF = DetField(F.n, F.mod)
    fails = 0
    for _ in range(20):
        k = rint(rng, 1, 9)
        A = np.where(rng.random((k, k)) < 0.6, rng.integers(1, F.q, size=(k, k)), 0)
        if rint(rng, 0, 3) == 0 and k > 1:
            A[rint(rng, 0, k)] = A[rint(rng, 0, k)]
        # Leibniz expansion (characteristic 2: no signs)
        import itertools
        ref = 0
        for perm in itertools.permutations(range(k)):
            t = 1
            for i, j in enumerate(perm):
                t = F.mul_school(t, int(A[i, j]))
                if t == 0:
                    break
            ref ^= t
        if determinant(A, DF) != ref:
            fails += 1
    return {"id": f"determinant_vs_leibniz_n{n}", "pass": fails == 0, "matrices": 20, "failures": fails,
            "note": "C-BREAK instrument check (additional item)"}


def t_fixture(mod19):
    got = {}
    ok = True
    for (n, l) in CELLS:
        F = TableField(n, MODULUS17 if n == 17 else mod19)
        desc = Descent(F, l)
        for D in (3, 4):
            S = MacaulayShape(D, desc)
            got[f"A_n{n}_l{l}_D{D}"] = [S.R, S.C]
            ok &= (S.R, S.C) == FIX_A[(n, l)][D]
        SB = ShapeB(F, l)
        got[f"B_n{n}_l{l}_D66"] = [SB.R, SB.C]
        ok &= (SB.R, SB.C) == FIX_B[l]
    exp = {f"A_n{n}_l{l}_D{D}": list(FIX_A[(n, l)][D]) for (n, l) in CELLS for D in (3, 4)}
    exp.update({f"B_n{n}_l{l}_D66": list(FIX_B[l]) for (n, l) in CELLS})
    return {"id": "C-FIX", "pass": bool(ok), "expected": exp, "observed": got}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if os.path.exists(args.out):
        print(f"refusing to overwrite existing {args.out}", file=sys.stderr)
        return 2
    t0 = time.time()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rng = np.random.Generator(np.random.PCG64(S_SELFTEST))
    items = []
    it, mod19 = t_moduli()
    items.append(it)
    if not it["pass"]:
        res = {"started_at": started, "all_pass": False, "stopped": "modulus not irreducible", "items": items}
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        json.dump(res, open(args.out, "w"), indent=1)
        return 1
    fields = {17: TableField(17, MODULUS17), 19: TableField(19, mod19)}
    for n in (17, 19):
        items.append(t_field_axioms(fields[n], rng, n))
    items.append(t_point_count(rng))
    for n in (17, 19):
        F = fields[n]
        items.append(t_s3_addition(F, rng, n))
        items.append(t_LV(F, n))
        items.append(t_rowsB(F, rng, n))
        items.append(t_descentA(F, rng, n))
        items.append(t_elimB(F, rng, n))
        items.append(t_classify(F, rng, n))
        items.append(t_phi(F, rng, n))
        items.append(t_half_trace(F, rng, n))
        items.append(t_det(F, rng, n))
    items.append(t_elimA_sanity(rng))
    items.append(t_fixture(mod19))
    all_pass = all(i["pass"] for i in items)
    res = {
        "experiment_id": "EXP-CERTBIN-a58c63", "phase": 0,
        "seed": {"S_selftest": S_SELFTEST, "generator": "numpy.random.Generator(numpy.random.PCG64(seed))"},
        "numpy_version": np.__version__, "argv": sys.argv, "cwd": os.getcwd(),
        "started_at": started, "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "wall_seconds": time.time() - t0, "all_pass": all_pass,
        "C-SELF_pass": all(i["pass"] for i in items if i["id"] != "C-FIX"),
        "C-FIX_pass": items[-1]["pass"],
        "n19_modulus": items[0]["n19"],
        "items": items,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(res, f, indent=1, default=int)
    print(json.dumps({"selftest_all_pass": all_pass, "items": {i["id"]: i["pass"] for i in items}}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
