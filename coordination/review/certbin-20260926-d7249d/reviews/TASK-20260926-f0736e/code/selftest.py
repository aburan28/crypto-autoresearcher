"""BR-2 self-tests (TASK-20260926-f0736e), run BEFORE any blind input is read.

Seed: SELFTEST_SEED = 15758190 (= 0xF0736E, from this task's id); sub-streams
are PCG64(SELFTEST_SEED + i) for the item number i.  No specification seed is
used.  Every random object here is self-generated; none is a blind input.
"""
import copy
import itertools
import json
import math
import time

import numpy as np

import algebra as G
import certs as C
import checkers as K
import field as F

SELFTEST_SEED = 15758190
A_CURVE = 46693
B_CURVE = 306147


def rng(i):
    return np.random.Generator(np.random.PCG64(SELFTEST_SEED + i))


def t_irreducible():
    rep = F.irreducibility_report()
    # also: the four lexicographically smaller pentanomials (context only)
    smaller = {}
    for (a, b, c) in [(3, 2, 1), (4, 2, 1), (4, 3, 1), (4, 3, 2)]:
        f = (1 << 19) | (1 << a) | (1 << b) | (1 << c) | 1
        smaller["t^19+t^%d+t^%d+t^%d+1" % (a, b, c)] = F.irreducibility_report(f)["irreducible"]
    rep["smaller_pentanomials_irreducible"] = smaller
    return rep["irreducible"], rep


def curve_order_exact(A, B):
    x = np.arange(1, 1 << F.N, dtype=np.int64)
    val = x ^ A ^ F.vmul(np.full_like(x, B), F.vinv(F.vsq(x)))
    zeros = int(np.count_nonzero(F.vtr(val) == 0))
    return 1 + 1 + 2 * zeros


def t_s3_points(npairs=200):
    r = rng(2)
    E = F.Curve(A_CURVE, B_CURVE)

    def rand_point():
        while True:
            x = int(r.integers(1, 1 << F.N))
            P = E.lift(x)
            if P is not None:
                assert E.on_curve(P)
                return P

    fails = 0
    checked = 0
    offcurve = 0
    for _ in range(npairs):
        P1, P2 = rand_point(), rand_point()
        for P3 in (E.add(P1, P2), E.add(P1, E.neg(P2))):
            if P3 is None:
                continue
            if not E.on_curve(P3):
                offcurve += 1
            checked += 1
            if F.S3(P1[0], P2[0], P3[0], B_CURVE) != 0:
                fails += 1
    # negative control: a random third x should almost never satisfy S_3
    neg_hits = 0
    for _ in range(npairs):
        P1, P2 = rand_point(), rand_point()
        x3 = int(r.integers(0, 1 << F.N))
        true_x = {Pt[0] for Pt in (E.add(P1, P2), E.add(P1, E.neg(P2))) if Pt is not None}
        if x3 in true_x:
            continue
        if F.S3(P1[0], P2[0], x3, B_CURVE) == 0:
            neg_hits += 1
    # group-law sanity: associativity and [#E]P = O with #E counted exactly
    assoc_fail = 0
    for _ in range(30):
        P, Q, R = rand_point(), rand_point(), rand_point()
        if E.add(E.add(P, Q), R) != E.add(P, E.add(Q, R)):
            assoc_fail += 1
    order = curve_order_exact(A_CURVE, B_CURVE)
    ord_fail = sum(1 for _ in range(10) if E.smul(order, rand_point()) is not None)
    ok = fails == 0 and offcurve == 0 and assoc_fail == 0 and ord_fail == 0 and neg_hits == 0
    return ok, {"pairs": npairs, "S3_evaluations": checked, "S3_nonzero": fails,
                "sum_points_off_curve": offcurve,
                "negative_control_random_x3_hits": neg_hits,
                "associativity_failures_of_30": assoc_fail,
                "curve_order_by_exact_count": order,
                "order_times_point_nonzero_of_10": ord_fail}


def t_descent(nx=120, nv_per=5):
    r = rng(3)
    bad_eval = 0
    bad_closed = 0
    bad_checker = 0
    maxdeg = 0
    n = 0
    for _ in range(nx):
        xR = int(r.integers(0, 1 << F.N))
        eqs = G.descend_S3(xR, B_CURVE)
        e2 = G.descend_S3_closed_form(xR, B_CURVE)
        e3 = K.curve_system(xR, B_CURVE)
        if not all(np.array_equal(a, b) for a, b in zip(eqs, e2)):
            bad_closed += 1
        if not all(np.array_equal(a, b) for a, b in zip(eqs, e3)):
            bad_checker += 1
        maxdeg = max(maxdeg, max(G.poly_deg(e) for e in eqs))
        for _ in range(nv_per):
            v = int(r.integers(0, 1 << 20))
            x1 = v & 0x3FF
            x2 = (v >> 10) & 0x3FF
            direct = F.S3(x1, x2, xR, B_CURVE)
            bits = G.eval_system_at(eqs, v)
            if direct != sum(b << k for k, b in enumerate(bits)):
                bad_eval += 1
            n += 1
    ok = bad_eval == 0 and bad_closed == 0 and bad_checker == 0 and maxdeg <= 2
    return ok, {"x_R_values": nx, "(v,x_R)_evaluations": n, "mismatches_vs_direct_S3": bad_eval,
                "generic_vs_closed_form_mismatch": bad_closed,
                "generic_vs_checker_closed_form_mismatch": bad_checker, "max_degree": maxdeg}


def naive_row(mu, f):
    s = set()
    for m in f:
        p = int(m) | mu
        s ^= {p}
    return s


def t_macaulay_rows(nrows=60):
    r = rng(4)
    xR = int(r.integers(1024, 1 << F.N))
    eqs = G.descend_S3(xR, B_CURVE)
    out = {}
    ok = True
    for D, expect in ((3, (399, 1351)), (4, (4009, 6196))):
        M, labels, cols = G.macaulay(eqs, G.NV, D)
        shape = (M.shape[0], cols.n)
        bad = 0
        for ri in r.choice(M.shape[0], size=nrows, replace=False):
            mu, k = labels[int(ri)]
            # check the row index convention: mu_index * neq + k
            mus = G.mu_order(D - 2, G.NV)
            assert int(ri) == mus.index(mu) * G.NEQ + k
            got = set(int(x) for x in G.packed_to_masks(M[int(ri)], cols))
            if got != naive_row(mu, eqs[k]):
                bad += 1
        out["M_%d" % D] = {"shape": list(shape), "expected": list(expect), "rows_checked": nrows,
                           "row_mismatches": bad}
        ok = ok and shape == expect and bad == 0
    # substituted fixtures (19 variables)
    rc, aux = G.rc_b(eqs, G.NV, xR)
    out["R'_3_shape"] = rc.get("R3_shape")
    out["R'_4_shape"] = rc.get("R4_shape")
    ok = ok and rc.get("R3_shape") == [380, 1160] and rc.get("R4_shape") == [3629, 5036]
    # naive rows for the substituted M_4 as well
    if aux and "sub" in aux:
        M, labels, cols = G.macaulay(aux["sub"], G.NV - 1, 4)
        bad = 0
        for ri in r.choice(M.shape[0], size=20, replace=False):
            mu, k = labels[int(ri)]
            got = set(int(x) for x in G.packed_to_masks(M[int(ri)], cols))
            if got != naive_row(mu, aux["sub"][k]):
                bad += 1
        out["R'_4_rows_checked"] = 20
        out["R'_4_row_mismatches"] = bad
        ok = ok and bad == 0
    return ok, out


# ---- brute-force literal fixpoint on 6-variable systems ---------------------
def bf_closure(eqs, nv=6, D=3, limit_dim=20):
    """Brute force: W held as the SET OF ALL ITS ELEMENTS.  W^(i+1) = span of
    W^(i) and v_j * w for every element w of W^(i) of degree <= D-1."""
    mons = []
    for d in range(D, -1, -1):
        for tup in itertools.combinations(range(nv), d):
            m = 0
            for x in tup:
                m |= 1 << x
            mons.append(m)
    pos = {m: i for i, m in enumerate(mons)}
    degs = [bin(m).count("1") for m in mons]
    above = {d: sum(1 << i for i, g in enumerate(degs) if g > d) for d in range(D + 1)}

    def vec(poly_masks):
        v = 0
        for m in poly_masks:
            v ^= 1 << pos[int(m)]
        return v

    def mul(v, j):
        out = 0
        i = 0
        while v:
            if v & 1:
                out ^= 1 << pos[mons[i] | (1 << j)]
            v >>= 1
            i += 1
        return out

    def span_add(W, g):
        if g in W:
            return W
        return W | {x ^ g for x in W}

    W = {0}
    for mu in G.mu_order(D - 2, nv):
        for f in eqs:
            W = span_add(W, vec(G.poly_reduce(np.asarray(f, dtype=np.int64) | mu)))
    dims = [int(round(math.log2(len(W))))]
    i = 0
    while True:
        if dims[-1] > limit_dim:
            return None
        low = [w for w in W if (w & above[D - 1]) == 0]
        W2 = W
        for w in low:
            for j in range(nv):
                W2 = span_add(W2, mul(w, j))
        dims.append(int(round(math.log2(len(W2)))))
        if len(W2) == len(W):
            fix = i
            break
        W = W2
        i += 1
    one = (1 << pos[0]) in W
    dbd = [int(round(math.log2(sum(1 for w in W if (w & above[d]) == 0)))) for d in range(D + 1)]
    return {"dims": dims, "fixpoint_index": fix, "one": one, "dims_by_deg": dbd}


def t_literal_W(nsys=12, need_deep=3):
    r = rng(6)
    mons2 = G.mu_order(2, 6)
    compared = []
    deep = 0
    tried = 0
    while (len(compared) < nsys or deep < need_deep) and tried < 20000:
        tried += 1
        neq = int(r.integers(1, 4))
        eqs = []
        for _ in range(neq):
            dens = r.uniform(0.1, 0.5)
            eqs.append(np.array(sorted(m for m in mons2 if r.random() < dens), dtype=np.int64))
        rec, bas, _, _ = G.macaulay_closure(eqs, 6, 3)
        w, _ = G.w_closure_literal(bas, 6, 3)
        if w["final_dim"] > 18:
            continue
        is_deep = w["fixpoint_index"] >= 2
        if len(compared) >= nsys and not is_deep:
            continue
        bf = bf_closure(eqs)
        if bf is None:
            continue
        same = (bf["dims"] == w["dims"] and bf["fixpoint_index"] == w["fixpoint_index"]
                and bf["one"] == w["one"] and bf["dims_by_deg"] == w["dims_by_deg"])
        compared.append({"stream_index": tried - 1, "neq": neq,
                         "equations": [[G.mask_to_tuple(int(m)) for m in e] for e in eqs],
                         "literal": {k: w[k] for k in ("dims", "fixpoint_index", "one", "dims_by_deg")},
                         "brute_force": bf, "agree": same})
        if is_deep:
            deep += 1
    ok = len(compared) >= 5 and deep >= 1 and all(c["agree"] for c in compared)
    return ok, {"seed": SELFTEST_SEED + 6, "variables": 6, "D": 3, "systems_compared": len(compared),
                "reaching_fixpoint_index_ge_2": deep, "stream_draws": tried,
                "selection": "random stream; systems with literal final_dim > 18 skipped (brute force enumerates 2^dim elements); after the first 12 comparisons, only fixpoint-index >= 2 systems are taken until three exist",
                "systems": compared}


def t_literal_W_int(nsys=80):
    """Extra: literal W_D against an independent Python-int elimination
    (no enumeration; also covers refuted and larger systems)."""
    r = rng(7)
    mons2 = G.mu_order(2, 6)
    D = 3
    nv = 6
    mons = []
    for d in range(D, -1, -1):
        for tup in itertools.combinations(range(nv), d):
            mons.append(sum(1 << x for x in tup))
    pos = {m: i for i, m in enumerate(mons)}
    deg = [bin(m).count("1") for m in mons]

    def vec(ms):
        v = 0
        for m in ms:
            v ^= 1 << pos[int(m)]
        return v

    def lead(v):
        return (v & -v).bit_length() - 1

    def insert(basis, v):
        for p in sorted(basis):
            if (v >> p) & 1:
                v ^= basis[p]
        if v:
            basis[lead(v)] = v
            return True
        return False

    def mul(v, j):
        out = 0
        i = 0
        while v:
            if v & 1:
                out ^= 1 << pos[mons[i] | (1 << j)]
            v >>= 1
            i += 1
        return out

    agree = 0
    total = 0
    refuted = 0
    for _ in range(nsys):
        neq = int(r.integers(1, 9))
        eqs = [np.array(sorted(m for m in mons2 if r.random() < r.uniform(0.1, 0.6)), dtype=np.int64)
               for _ in range(neq)]
        basis = {}
        for mu in G.mu_order(D - 2, nv):
            for f in eqs:
                insert(basis, vec(G.poly_reduce(np.asarray(f, dtype=np.int64) | mu)))
        dims = [len(basis)]
        i = 0
        while True:
            low = [b for p, b in basis.items() if deg[p] <= D - 1]
            for b in low:
                for j in range(nv):
                    insert(basis, mul(b, j))
            dims.append(len(basis))
            if dims[-1] == dims[-2]:
                fix = i
                break
            i += 1
        one = pos[0] in basis
        rec, bas, _, _ = G.macaulay_closure(eqs, nv, D)
        w, _ = G.w_closure_literal(bas, nv, D)
        total += 1
        refuted += int(one)
        if w["dims"] == dims and w["fixpoint_index"] == fix and w["one"] == one:
            agree += 1
    return agree == total and refuted > 0, {"systems": total, "agree": agree, "refuted_among_them": refuted}


def t_kernel_rank(ntests=30):
    """Extra: C semi-echelon rank against the checker's numpy elimination."""
    r = rng(8)
    bad = 0
    for _ in range(ntests):
        rows = int(r.integers(5, 400))
        ncols_choice = [(6, 3), (7, 3), (8, 4)][int(r.integers(0, 3))]
        cols = G.Cols(*ncols_choice)
        dens = r.uniform(0.01, 0.5)
        A = (r.random((rows, cols.n)) < dens).astype(np.uint8)
        # plant dependencies
        if rows > 4:
            A[-1] = A[0] ^ A[1]
        b = G.Basis(cols, cap=cols.n)
        b.insert(G.pack_dense(A))
        Kn, rk = K.nullspace(A.T.copy())  # rank of A^T == rank of A
        if b.rank != rk:
            bad += 1
    return bad == 0, {"random_matrices": ntests, "rank_mismatches": bad}


def t_s_routes(nsys=12):
    r = rng(9)
    bad = 0
    recs = []
    xs = [0, 5, 1023] + [int(r.integers(1024, 1 << F.N)) for _ in range(nsys)]
    for xR in xs:
        eqs = G.descend_S3(xR, B_CURVE)
        s1 = G.exhaustive_s(eqs)
        s2, nroots = G.s_route_quadratic(xR, B_CURVE)
        s3 = G.exhaustive_s_unpacked(eqs)
        # direct F_{2^19} count over V x V (third route, vectorised)
        x1 = np.repeat(np.arange(1024, dtype=np.int64), 1024)
        x2 = np.tile(np.arange(1024, dtype=np.int64), 1024)
        xr = np.full_like(x1, xR)
        u = F.vmul(x1, x2) ^ F.vmul(x1, xr) ^ F.vmul(x2, xr)
        val = F.vsq(u) ^ F.vmul(F.vmul(x1, x2), xr) ^ B_CURVE
        s4 = int(np.count_nonzero(val == 0))
        recs.append({"x_R": xR, "exhaustive_packed": s1, "quadratic_route": s2,
                     "exhaustive_unpacked": s3, "direct_VxV": s4})
        if not (s1 == s2 == s3 == s4):
            bad += 1
    # random (non-curve) systems with a planted solution
    planted_bad = 0
    for _ in range(6):
        eqs = [np.array(sorted(m for m in G.mu_order(2, 20) if r.random() < 0.3), dtype=np.int64)
               for _ in range(19)]
        v0 = int(r.integers(0, 1 << 20))
        # force f_k(v0) = 0 by toggling the constant term
        eqs2 = []
        for e in eqs:
            if G.poly_eval(e, v0):
                e = G.poly_reduce(np.concatenate([e, np.array([0], dtype=np.int64)]))
            eqs2.append(e)
        s1, sols = G.exhaustive_s(eqs2, return_solutions=True)
        s3 = G.exhaustive_s_unpacked(eqs2)
        if s1 != s3 or v0 not in set(sols.tolist()) or any(any(G.eval_system_at(eqs2, int(v))) for v in sols[:50]):
            planted_bad += 1
    # root finder against brute force over the whole field
    qa_bad = 0
    allx = np.arange(1 << F.N, dtype=np.int64)
    for _ in range(40):
        a, b, c = (int(r.integers(1, 1 << F.N)) for _ in range(3))
        vals = F.vmul(np.full_like(allx, a), F.vsq(allx)) ^ F.vmul(np.full_like(allx, b), allx) ^ c
        brute = set(np.flatnonzero(vals == 0).tolist())
        y = F.mul(F.mul(c, a), F.inv(F.sq(b)))
        roots = set()
        if F.tr(y) == 0:
            z = F.half_trace(y)
            sc = F.mul(b, F.inv(a))
            roots = {F.mul(sc, z), F.mul(sc, z ^ 1)}
        if roots != brute:
            qa_bad += 1
    ok = bad == 0 and planted_bad == 0 and qa_bad == 0
    return ok, {"curve_systems": recs, "route_disagreements": bad,
                "planted_solution_failures": planted_bad,
                "quadratic_root_finder_vs_full_field_bruteforce": {"quadratics": 40, "mismatches": qa_bad}}


def t_substitution(ncases=300):
    r = rng(10)
    bad = 0
    n = 0
    for _ in range(ncases // 30):
        xR = int(r.integers(1024, 1 << F.N))
        eqs = G.descend_S3(xR, B_CURVE)
        rc, aux = G.rc_b(eqs, G.NV, xR)
        if not rc.get("applicable"):
            continue
        ell = aux["ell"]
        jstar = rc["jstar"]
        a_poly = G.poly_reduce(np.concatenate([ell, np.array([1 << jstar], dtype=np.int64)]))
        for _ in range(30):
            u = int(r.integers(0, 1 << 19))
            full = G.unsubstitute_point(u, jstar, a_poly)
            assert G.poly_eval(ell, full) == 0
            if G.eval_system_at(aux["sub"], u) != G.eval_system_at(eqs, full):
                bad += 1
            n += 1
    return bad == 0 and n >= 100, {"cases": n, "mismatches": bad}


def _synthetic_refuted_curve_system(r):
    E = F.Curve(A_CURVE, B_CURVE)
    while True:
        x = int(r.integers(1, 1 << F.N))
        P = E.lift(x)
        if P is None:
            continue
        R = E.dbl(P)
        if R is None or R[0] < 1024:
            continue
        eqs = G.descend_S3(R[0], B_CURVE)
        if G.exhaustive_s(eqs) != 0:
            continue
        r4, bas4, M4, lab = G.macaulay_closure(eqs, G.NV, 4)
        w, basw = G.w_closure_literal(bas4, G.NV, 4)
        if w["one"] and w["one_first_iteration"] >= 1:
            return R[0], eqs, M4, lab, bas4, w


def t_wdag_checker():
    r = rng(11)
    xR, eqs, M4, lab, bas4, w = _synthetic_refuted_curve_system(r)
    cert, st = C.build_wdag("SELFTEST", eqs, M4, lab, bas4.cols, w)
    eqsK = K.curve_system(xR, B_CURVE)
    res = {"synthetic_x_R": xR, "W_one_first_iteration": w["one_first_iteration"], "cert_stats": st}
    ok_valid, why = K.check_wdag(cert, eqsK, "SELFTEST")
    res["valid_accepted"] = [ok_valid, why]
    corrupt = {}
    out = cert["output"]
    onode = [n for n in cert["nodes"] if n["id"] == out][0]
    # (1) one row removed
    c1 = copy.deepcopy(cert)
    n1 = [n for n in c1["nodes"] if n["rows"]][0]
    n1["rows"].pop(len(n1["rows"]) // 2)
    corrupt["one_row_removed"] = K.check_wdag(c1, eqsK, "SELFTEST")
    # (2) one k changed
    c2 = copy.deepcopy(cert)
    n2 = [n for n in c2["nodes"] if n["rows"]][0]
    n2["rows"][0][1] = (n2["rows"][0][1] + 1) % 19
    corrupt["one_k_changed"] = K.check_wdag(c2, eqsK, "SELFTEST")
    # (3) degree violation: a degree-4 node used twice as a child (sum unchanged)
    c3 = copy.deepcopy(cert)
    deg4_row = None
    for mu in G.mu_order(2, G.NV):
        if bin(mu).count("1") == 2:
            for k in range(19):
                p = G.poly_reduce(eqs[k] | mu)
                if G.poly_deg(p) == 4:
                    deg4_row = [G.mask_to_tuple(mu), k]
                    break
        if deg4_row:
            break
    newid = max(n["id"] for n in c3["nodes"]) + 1
    c3["nodes"].append({"id": newid, "rows": [deg4_row], "prods": []})
    newout = newid + 1
    o3 = copy.deepcopy(onode)
    o3["id"] = newout
    o3["prods"] = o3["prods"] + [[3, newid], [3, newid]]
    c3["nodes"].append(o3)
    c3["output"] = newout
    corrupt["pair_of_identical_prods_on_degree4_child"] = K.check_wdag(c3, eqsK, "SELFTEST")
    # (4) a row with |mu| = 3
    c4 = copy.deepcopy(cert)
    n4 = [n for n in c4["nodes"] if n["rows"]][0]
    n4["rows"].append([[0, 1, 2], 0])
    n4["rows"].append([[0, 1, 2], 0])  # cancels algebraically; only (b) can reject
    corrupt["mu_of_size_3_(cancelling_pair)"] = K.check_wdag(c4, eqsK, "SELFTEST")
    # (5) child id not smaller than parent
    c5 = copy.deepcopy(cert)
    if onode["prods"]:
        for n in c5["nodes"]:
            if n["id"] == out:
                n["id"] = -1
        c5["output"] = -1
        corrupt["child_id_not_smaller"] = K.check_wdag(c5, eqsK, "SELFTEST")
    # (6) re-keyed to another system
    xR2 = xR ^ 0x40000
    corrupt["rekeyed_to_other_system"] = K.check_wdag(cert, K.curve_system(xR2, B_CURVE), "SELFTEST")
    res["corrupted"] = {k: list(v) for k, v in corrupt.items()}
    ok = ok_valid and all(not v[0] for v in corrupt.values()) and len(corrupt) >= 3
    return ok, res


def t_ann_checker():
    r = rng(12)
    # a synthetic non-refuted system with W_4 != M_4: 18 random rows on the
    # bilinear+linear+constant columns plus a linear row v_0 + v_10 + c
    Ecols = G.E_columns(G.NV)
    bil = [i for i, m in enumerate(Ecols) if bin(m).count("1") == 2 and (m & 0x3FF) and (m >> 10)]
    lincon = list(range(0, 21))
    while True:
        eqs = []
        for k in range(18):
            sel = [Ecols[c] for c in bil + lincon if r.random() < 0.5]
            eqs.append(np.array(sorted(sel), dtype=np.int64))
        eqs.append(np.array(sorted([1 << 0, 1 << 10] + ([0] if r.random() < 0.5 else [])), dtype=np.int64))
        if G.exhaustive_s(eqs) != 0:
            continue
        r4, bas4, M4, lab = G.macaulay_closure(eqs, G.NV, 4)
        w, basw = G.w_closure_literal(bas4, G.NV, 4)
        if not w["one"] and w["final_dim"] != r4["rank"]:
            break
    cert, st, Lm = C.build_ann("SELFTEST", basw)
    m4 = K.m4_rows_dense(eqs)
    res = {"W_dims": w["dims"], "M4_rank": r4["rank"], "cert_stats": st}
    v = K.check_ann(cert, eqs, "SELFTEST", m4=m4)
    res["valid_accepted"] = [v[0], v[1]]
    corrupt = {}
    # (e1) a functional nonzero on a named M_4 row
    row_idx = int(np.flatnonzero(m4.any(axis=1))[5])
    lam = m4[row_idx].copy()
    lam[:] = 0
    lam[int(np.flatnonzero(m4[row_idx])[0])] = 1
    c1 = copy.deepcopy(cert)
    c1["L_hex"].append(C.hex_rows(lam[None, :])[0])
    corrupt["e1_functional_nonzero_on_M4_row_%d" % row_idx] = K.check_ann(c1, eqs, "SELFTEST", m4=m4)[:2]
    # (e2) the annihilator of M_4 alone (W_4 != M_4 here)
    c2 = {"label": "SELFTEST", "D": 4, "nv": 20, "neq": 19, "L_hex": C.hex_rows(C.annihilator(bas4))}
    corrupt["e2_annihilator_of_M4_alone"] = K.check_ann(c2, eqs, "SELFTEST", m4=m4)[:2]
    # (e3) every functional's constant coordinate cleared
    L3 = Lm.copy()
    L3[:, -1] = 0
    c3 = copy.deepcopy(cert)
    c3["L_hex"] = C.hex_rows(L3)
    corrupt["e3_constant_coordinate_cleared"] = K.check_ann(c3, eqs, "SELFTEST", m4=m4)[:2]
    # (e4) re-keyed to another system (the row-18 constant flipped)
    eqs4 = [e.copy() for e in eqs]
    eqs4[18] = G.poly_reduce(np.concatenate([eqs4[18], np.array([0], dtype=np.int64)]))
    corrupt["e4_rekeyed_to_other_system"] = K.check_ann(cert, eqs4, "SELFTEST")[:2]
    res["corrupted"] = {k: list(v) for k, v in corrupt.items()}
    ok = v[0] and all(not x[0] for x in corrupt.values())
    return ok, res


def t_wdag_multilevel(want_deep=3, want_one=3, want_zero=1, max_draws=20000):
    """Extra: the multi-level (collapse-per-variable) wdag construction and
    the checker on small systems whose first refutation is at iteration 0, 1
    and >= 2.  Run at D = 3 in 7 variables because no 20-variable (or small
    D = 4) system met in development first refutes at an iteration >= 2; the
    checker applies the same rules with |mu| <= D-2, child degree <= D-1 and
    node degree <= D (identical to the frozen rules at D = 4)."""
    r = rng(14)
    nv, D = 7, 3
    mons2 = G.mu_order(2, nv)
    got = {0: 0, 1: 0, "deep": 0}
    recs = []
    draws = 0
    while (got["deep"] < want_deep or got[1] < want_one or got[0] < want_zero) and draws < max_draws:
        draws += 1
        neq = int(r.integers(2, 7))
        eqs = [np.array(sorted(m for m in mons2 if r.random() < r.uniform(0.1, 0.5)), dtype=np.int64)
               for _ in range(neq)]
        rec, bas, M, labels = G.macaulay_closure(eqs, nv, D)
        w, _ = G.w_closure_literal(bas, nv, D)
        L = w["one_first_iteration"]
        if L is None:
            continue
        key = "deep" if L >= 2 else L
        need = {"deep": want_deep, 1: want_one, 0: want_zero}[key]
        if got[key] >= need:
            continue
        got[key] += 1
        cert, st = C.build_wdag("ML", eqs, M, labels, bas.cols, w, nv=nv, neq=neq, D=D)
        ok, why = K.check_wdag(cert, eqs, "ML", nv=nv, neq=neq, D=D)
        # corruption: drop one prods entry (or one row if there are no prods)
        bad = copy.deepcopy(cert)
        with_prods = [n for n in bad["nodes"] if n["prods"]]
        if with_prods:
            with_prods[-1]["prods"].pop(0)
            kind = "one_prod_removed"
        else:
            [n for n in bad["nodes"] if n["rows"]][0]["rows"].pop(0)
            kind = "one_row_removed"
        okb, whyb = K.check_wdag(bad, eqs, "ML", nv=nv, neq=neq, D=D)
        recs.append({"draw": draws - 1, "neq": neq, "one_first_iteration": L, "dims": w["dims"],
                     "cert_stats": st, "valid_accepted": [ok, why], "corrupted_" + kind: [okb, whyb]})
    ok_all = (got["deep"] >= want_deep and got[1] >= want_one and got[0] >= want_zero
              and all(x["valid_accepted"][0] for x in recs)
              and all(not [v for k, v in x.items() if k.startswith("corrupted_")][0][0] for x in recs))
    return ok_all, {"variables": nv, "D": D, "draws": draws, "counts": {str(k): v for k, v in got.items()},
                    "systems": recs}


TESTS = [
    ("irreducibility_of_modulus", t_irreducible),
    ("S3_vanishes_on_point_sums_and_differences", t_s3_points),
    ("descended_equations_vs_direct_F2^19_evaluation", t_descent),
    ("macaulay_rows_vs_naive_multiply_and_fixture_dimensions", t_macaulay_rows),
    ("literal_W_D_vs_bruteforce_fixpoint_6vars_D3", t_literal_W),
    ("literal_W_D_vs_independent_int_elimination_6vars_D3", t_literal_W_int),
    ("C_kernel_rank_vs_numpy_elimination", t_kernel_rank),
    ("s_routes_and_root_finder", t_s_routes),
    ("substitution_vs_direct_evaluation", t_substitution),
    ("wdag_v1_checker_accepts_valid_rejects_corrupted", t_wdag_checker),
    ("ann_v1_checker_accepts_valid_rejects_corrupted", t_ann_checker),
    ("wdag_multilevel_construction_small_D3", t_wdag_multilevel),
]


def run_all():
    results = {}
    all_ok = True
    for name, fn in TESTS:
        t0 = time.time()
        ok, detail = fn()
        results[name] = {"passed": bool(ok), "seconds": round(time.time() - t0, 2), "detail": detail}
        all_ok = all_ok and ok
        print("[selftest] %-60s %s (%.1fs)" % (name, "PASS" if ok else "FAIL", time.time() - t0), flush=True)
    return all_ok, results


if __name__ == "__main__":
    ok, res = run_all()
    print(json.dumps({"all_passed": ok}, indent=1))
