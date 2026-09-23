#!/usr/bin/env python3
"""TASK-20260923-b8f163, joint J1 (object fidelity) of REVIEW-CERTBIN-20260923-c51f07.

Spec-literal constructions for EXP-CERTBIN-4e92d7, written by the validator from
experiments/EXP-CERTBIN-4e92d7/specification.yaml ("object" block) ONLY.

Everything below the line "INDEPENDENT" uses no impl/ code. impl/ modules are
imported ONLY in the block marked "IMPL (comparison only)", to construct the
SAME instance with the producer's constructor for a bit-level diff (allowed by
RV-3). analysis.py and report.py are never imported or run.

Zero trials: this is a verification computation (RV-7), no RUN-id.

Instance set (pre-declared, outcome-independent): the five F-S3 references
U1, U2, U3, S1, S2, the F-S3 modal reference instance, and F-S3 test targets
idx 1..10 in draw order. At most 16 distinct archived instances (<= 20).

Usage: python3 j1_spec_literal.py            (run from anywhere)
Writes j1_results.json and j1_diffs.txt next to this file.
"""
import gzip
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
EXP = os.path.join(REPO, "experiments", "EXP-CERTBIN-4e92d7")
RUN = os.path.join(EXP, "runs", "RUN-CERTBIN-3b7e05")
IMPL = os.path.join(EXP, "impl")

T0 = time.time()
LOG = []


def log(msg):
    line = f"[{time.time() - T0:8.1f}s] {msg}"
    print(line, flush=True)
    LOG.append(line)


# =============================================================================
# INDEPENDENT: field F_2[t]/(t^17 + t^3 + 1), bit j = coefficient of t^j
# (interleaved shift-and-reduce; the impl uses clmul-then-reduce and log tables)
# =============================================================================
NBITS = 17
FPOLY = (1 << 17) | (1 << 3) | 1


def gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if (a >> NBITS) & 1:
            a ^= FPOLY
    return r


def gpow(a, e):
    r = 1
    while e:
        if e & 1:
            r = gmul(r, a)
        a = gmul(a, a)
        e >>= 1
    return r


def modulus_check():
    """17 is prime, so f is irreducible iff f has no root in F_2 and
    t^(2^17) = t mod f (every irreducible factor then has degree 1 or 17)."""
    f0 = FPOLY & 1                                  # f(0)
    f1 = bin(FPOLY).count("1") & 1                  # f(1)
    x = 2
    for _ in range(NBITS):
        x = gmul(x, x)
    return {"f(0)": f0, "f(1)": f1, "t^(2^17)==t": x == 2, "irreducible": f0 == 1 and f1 == 1 and x == 2}


# log tables for the brute-force oracle (built with gmul; generator t because
# 2^17 - 1 is prime, so every element != 0, 1 generates)
EXPT = [0] * (2 * ((1 << NBITS) - 1))
LOGT = [0] * (1 << NBITS)
_x = 1
for _i in range((1 << NBITS) - 1):
    EXPT[_i] = _x
    LOGT[_x] = _i
    _x = gmul(_x, 2)
assert _x == 1
for _i in range((1 << NBITS) - 1, 2 * ((1 << NBITS) - 1)):
    EXPT[_i] = EXPT[_i - ((1 << NBITS) - 1)]


def tmul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXPT[LOGT[a] + LOGT[b]]


def s3(x1, x2, x3, B, mul=gmul):
    """S_3 = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B (spec summation_polynomial)."""
    e = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
    return mul(e, e) ^ mul(mul(x1, x2), x3) ^ B


# ---- curve law, only to sanity-check that S_3 is the summation polynomial of
# Y^2 + XY = X^3 + A X^2 + B (not a J1 item of the plan; cheap context)
def ginv(a):
    return gpow(a, (1 << NBITS) - 2)


def gtrace(a):
    s, x = 0, a
    for _ in range(NBITS):
        s ^= x
        x = gmul(x, x)
    return s


def ghalftrace(c):
    """H(c) = sum_{i=0}^{(n-1)/2} c^(4^i), n odd."""
    s, x = 0, c
    for _ in range((NBITS - 1) // 2 + 1):
        s ^= x
        x = gmul(x, x)
        x = gmul(x, x)
    return s


def lift(A, B, x):
    if x == 0:
        return None
    c = x ^ A ^ gmul(B, ginv(gmul(x, x)))
    if gtrace(c) != 0:
        return None
    z = ghalftrace(c)
    y = gmul(x, z)
    assert gmul(y, y) ^ gmul(x, y) == gmul(gmul(x, x), x) ^ gmul(A, gmul(x, x)) ^ B
    return (x, y)


def padd(A, P, Q):
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2:
        return None
    lam = gmul(y1 ^ y2, ginv(x1 ^ x2))
    x3 = gmul(lam, lam) ^ lam ^ x1 ^ x2 ^ A
    y3 = gmul(lam, x1 ^ x3) ^ x3 ^ y1
    return (x3, y3)


# =============================================================================
# INDEPENDENT: monomials, orders
# =============================================================================
NV = 18   # v_0 > v_1 > ... > v_17
L = 9
NEQ = 17


def spec_greater(a, b):
    """spec: a > b iff deg a > deg b; or deg a = deg b and, at the largest
    variable index i where a and b differ, a does NOT contain v_i."""
    if len(a) != len(b):
        return len(a) > len(b)
    d = set(a).symmetric_difference(b)
    if not d:
        return False
    return max(d) not in set(a)


_MON_CACHE = {}


def monomials_upto(dmax):
    """All multilinear monomials of degree <= dmax, by bitmask enumeration."""
    if dmax not in _MON_CACHE:
        out = []
        for mask in range(1 << NV):
            w = bin(mask).count("1")
            if w <= dmax:
                out.append(tuple(i for i in range(NV) if (mask >> i) & 1))
        _MON_CACHE[dmax] = out
    return list(_MON_CACHE[dmax])


def column_order_literal(D):
    """DESCENDING order under spec_greater, computed by counting, for each
    monomial, how many monomials are strictly greater (O(n^2) within a degree).
    A strict total order gives a permutation of ranks; that is asserted."""
    mons = monomials_upto(D)
    bydeg = {}
    for m in mons:
        bydeg.setdefault(len(m), []).append(m)
    order = []
    total_checks = 0
    for d in sorted(bydeg, reverse=True):          # higher degree is greater
        grp = bydeg[d]
        rank = {}
        for a in grp:
            g = 0
            for b in grp:
                if a is not b and spec_greater(b, a):
                    g += 1
            rank[a] = g
            total_checks += len(grp)
        # antisymmetry/totality: ranks must be exactly 0..len-1
        assert sorted(rank.values()) == list(range(len(grp))), f"not a strict total order at degree {d}"
        order.extend(sorted(grp, key=lambda m: rank[m]))
    assert order[-1] == ()
    return order, total_checks


def row_order_literal(D):
    mus = sorted(monomials_upto(D - 2), key=lambda m: (len(m), m))
    rows = []
    for a, mu in enumerate(mus):
        for k in range(NEQ):
            rows.append({"row": a * NEQ + k, "mu": list(mu), "k": k})
    return mus, rows


# =============================================================================
# INDEPENDENT: Weil descent, two ways
# =============================================================================
def x_of(u_bits, off):
    """x = sum_{j<9} v_{off+j} t^j evaluated at the Boolean point u_bits."""
    x = 0
    for j in range(L):
        if (u_bits >> (off + j)) & 1:
            x |= 1 << j
    return x


def descent_symbolic(B, xR):
    """Literal expansion: polynomials in v with F_{2^17} coefficients as dict
    frozenset(monomial) -> element; products multilinearize by set union
    (v^2 = v). e*e is formed as a FULL product (no char-2 squaring shortcut)."""
    def pm(P, Q):
        out = {}
        for m1, c1 in P.items():
            for m2, c2 in Q.items():
                m = m1 | m2
                out[m] = out.get(m, 0) ^ gmul(c1, c2)
        return out

    def pa(*Ps):
        out = {}
        for P in Ps:
            for m, c in P.items():
                out[m] = out.get(m, 0) ^ c
        return out

    X1 = {frozenset([j]): 1 << j for j in range(L)}
    X2 = {frozenset([L + j]): 1 << j for j in range(L)}
    X3 = {frozenset(): xR}
    e = pa(pm(X1, X2), pm(X1, X3), pm(X2, X3))
    S = pa(pm(e, e), pm(pm(X1, X2), X3), {frozenset(): B})
    return {tuple(sorted(m)): c for m, c in S.items() if c}


def descent_mobius(B, xR, dmax=4):
    """Multilinear coefficients by Moebius inversion of direct evaluations:
    c_m = XOR_{u subset m} S_3(x_1(u), x_2(u), x_R). Unique multilinear
    representation, so it must equal the multilinearized expansion."""
    cache = {}

    def P(mask):
        if mask not in cache:
            cache[mask] = s3(x_of(mask, 0), x_of(mask, L), xR, B)
        return cache[mask]

    coef = {}
    for m in monomials_upto(dmax):
        mm = 0
        for i in m:
            mm |= 1 << i
        acc = 0
        sub = mm
        while True:
            acc ^= P(sub)
            if sub == 0:
                break
            sub = (sub - 1) & mm
        if acc:
            coef[m] = acc
    return coef


def equations_from_coef(coef):
    """f_k = set of monomials whose coefficient has bit k set (coefficient of t^k)."""
    f = [set() for _ in range(NEQ)]
    for m, c in coef.items():
        for k in range(NEQ):
            if (c >> k) & 1:
                f[k].add(m)
    return f


def macaulay_rows(f, mus, colidx):
    """Row (mu, k) = multilinear reduction of mu * f_k, zero rows retained.
    Returned as Python ints: bit c set iff column c (declared order) is 1."""
    rows = []
    for mu in mus:
        smu = set(mu)
        for k in range(NEQ):
            acc = set()
            for m in f[k]:
                prod = tuple(sorted(smu.union(m)))
                if prod in acc:
                    acc.remove(prod)
                else:
                    acc.add(prod)
            v = 0
            for prod in acc:
                v |= 1 << colidx[prod]
            rows.append(v)
    return rows


def rows_to_dense(rows, C):
    M = np.zeros((len(rows), C), dtype=np.uint8)
    for i, v in enumerate(rows):
        while v:
            lb = v & -v
            M[i, lb.bit_length() - 1] = 1
            v ^= lb
    return M


# =============================================================================
# INDEPENDENT: the solver, Z_D, traces, replay
# =============================================================================
def literal_solver(rows_in, C):
    """spec elimination, literally: for each column c in order, among rows not
    yet used as pivot rows pick the smallest ORIGINAL row index with a 1 in
    column c of the CURRENT matrix; record (p, c); XOR row p into every other
    unused row with a 1 in column c, recording X. Rows never move."""
    rows = list(rows_in)
    R = len(rows)
    used = [False] * R
    ops = []
    for c in range(C):
        bit = 1 << c
        cand = [i for i in range(R) if (not used[i]) and (rows[i] & bit)]
        if not cand:
            continue
        p = min(cand)
        X = sorted(i for i in cand if i != p)
        for x in X:
            rows[x] ^= rows[p]
        used[p] = True
        ops.append((p, c, X))
    return ops


def zero_reduction_set(rows):
    """Z_D = {i : row i lies in span(rows 0..i-1)}, incremental basis keyed by
    the leading (smallest-index) column. Returns (Z, sorted leading columns)."""
    basis = {}
    Z = []
    for i, v in enumerate(rows):
        while v:
            lc = (v & -v).bit_length() - 1
            if lc in basis:
                v ^= basis[lc]
            else:
                basis[lc] = v
                break
        if v == 0:
            Z.append(i)
    return Z, sorted(basis)


def cjson(o):
    """canonical JSON: no whitespace, integer lists (own serializer)."""
    if isinstance(o, (list, tuple)):
        return "[" + ",".join(cjson(x) for x in o) + "]"
    if isinstance(o, (int, np.integer)) and not isinstance(o, bool):
        return str(int(o))
    raise TypeError(type(o))


def h(o):
    return hashlib.sha256(cjson(o).encode("utf-8")).hexdigest()


def traces(rows, C):
    ops = literal_solver(rows, C)
    Z, leads = zero_reduction_set(rows)
    rank = len(ops)
    pivcols = sorted(c for _, c, _ in ops)
    T = {
        "rank": rank,
        "set": [pivcols, Z],
        "strict": [[p, c] for p, c, _ in ops],
        "ops": [[p, c, X] for p, c, X in ops],
    }
    H = {g: h(T[g]) for g in T}
    cpass = (leads == pivcols) and (len(Z) == len(rows) - rank)
    return ops, Z, T, H, cpass, leads


def replay(rows_in, oplog, full=True):
    """Fixed-schedule replay: e_k = entry (p_k, c_k) immediately BEFORE step
    k's XORs; then XOR row p_k into every row of X_k (full rows, no shortcut,
    no data-dependent choice)."""
    rows = list(rows_in)
    e = []
    for p, c, X in oplog:
        e.append((rows[p] >> c) & 1)
        for x in X:
            rows[x] ^= rows[p]
    return e


def own_oracle_s(B, xR):
    """Third oracle: brute force over (x_1, x_2) in V x V of S_3 = 0 with the
    validator's own field arithmetic (log tables built from gmul)."""
    cnt = 0
    for x1 in range(1 << L):
        for x2 in range(1 << L):
            if s3(x1, x2, xR, B, mul=tmul) == 0:
                cnt += 1
    return cnt


# =============================================================================
# load archived inputs (committed bytes)
# =============================================================================
def load_inputs():
    curve = json.load(open(os.path.join(RUN, "curve.json")))
    refs = json.load(open(os.path.join(RUN, "references.json")))["F-S3"]["references"]
    tgt = {}
    with gzip.open(os.path.join(RUN, "targets-F-S3.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r["idx"] <= 10:
                tgt[(r["idx"], r["D"])] = r
    oplogs = {}
    for D in (3, 4):
        oplogs[D] = {}
        with gzip.open(os.path.join(RUN, f"F-S3-reference-oplogs-D{D}.jsonl.gz"), "rt") as fh:
            for line in fh:
                r = json.loads(line)
                oplogs[D].setdefault(r["ref"], []).append(r)
        for lab in oplogs[D]:
            lst = sorted(oplogs[D][lab], key=lambda r: r["k"])
            assert [r["k"] for r in lst] == list(range(len(lst)))
            oplogs[D][lab] = [(r["p"], r["c"], r["X"]) for r in lst]
    return curve, refs, tgt, oplogs


def main():
    results = {"task": "TASK-20260923-b8f163", "joint": "J1", "checks": {}}
    diffs = []
    curve, refs, tgt, oplogs = load_inputs()
    A, B = curve["A"], curve["B"]
    log(f"curve A={A} B={B} (from curve.json)")

    # ---- modulus + encoding
    mc = modulus_check()
    results["checks"]["modulus"] = mc
    log(f"modulus: {mc}")

    # ---- S_3 is the summation polynomial of this curve form (context check)
    rngp = np.random.Generator(np.random.PCG64(20260923))  # validator's own seed, declared
    ok_s3, n_s3 = 0, 0
    while n_s3 < 100:
        P1 = lift(A, B, int(rngp.integers(1, 1 << NBITS)))
        P2 = lift(A, B, int(rngp.integers(1, 1 << NBITS)))
        if P1 is None or P2 is None:
            continue
        Sm = padd(A, P1, P2)
        Dm = padd(A, P1, (P2[0], P2[0] ^ P2[1]))
        if Sm is None or Dm is None:
            continue
        n_s3 += 1
        ok_s3 += (s3(P1[0], P2[0], Sm[0], B) == 0 and s3(P1[0], P2[0], Dm[0], B) == 0)
    results["checks"]["s3_is_summation_polynomial_on_curve"] = {"pairs": n_s3, "vanish_at_sum_and_difference": ok_s3,
                                                               "seed": 20260923, "note": "validator's own curve law; context only"}
    log(f"S_3 on-curve check: {ok_s3}/{n_s3}")

    # ---- (1) column and row orders
    ordchk = {}
    my_cols, my_mus = {}, {}
    for D in (3, 4):
        cols, ncmp = column_order_literal(D)
        my_cols[D] = cols
        arch = json.load(open(os.path.join(RUN, f"column-order-D{D}.json")))
        arch_cols = [tuple(c["monomial"]) for c in sorted(arch["columns"], key=lambda c: c["col"])]
        col_idx_ok = [c["col"] for c in arch["columns"]] == list(range(len(arch["columns"])))
        deg_ok = all(c["degree"] == len(c["monomial"]) for c in arch["columns"])
        ndiff = sum(1 for a, b in zip(cols, arch_cols) if a != b) + abs(len(cols) - len(arch_cols))
        first = next((i for i, (a, b) in enumerate(zip(cols, arch_cols)) if a != b), None)
        mus, rows = row_order_literal(D)
        my_mus[D] = mus
        archr = json.load(open(os.path.join(RUN, f"row-order-D{D}.json")))
        rdiff = sum(1 for a, b in zip(rows, archr["rows"]) if a != b) + abs(len(rows) - len(archr["rows"]))
        ordchk[f"D{D}"] = {
            "C_D_literal": len(cols), "C_D_archived": arch["C_D"], "column_positions_differing": ndiff,
            "first_column_difference": first, "archived_col_field_is_position": col_idx_ok,
            "archived_degree_field_consistent": deg_ok, "pairwise_comparisons": ncmp,
            "R_D_literal": len(rows), "R_D_archived": archr["R_D"], "row_entries_differing": rdiff,
            "fixture_literal": [len(rows), len(cols)],
        }
        diffs.append(f"column-order-D{D}.json vs literal: {ndiff} differing positions (first: {first})")
        diffs.append(f"row-order-D{D}.json vs literal: {rdiff} differing entries")
        log(f"orders D={D}: {ordchk[f'D{D}']}")
    results["checks"]["orders"] = ordchk

    # ---- instances
    insts = []
    for lab in ("U1", "U2", "U3", "S1", "S2"):
        insts.append(("ref", lab, refs[lab]["x_R"]))
    # the modal reference is a test target; references.json records its index per D
    midx = refs["modal"]["instance_idx_per_D"]
    assert midx["D3"] == midx["D4"], "modal instance differs by D; handle per D"
    refs["modal"]["x_R"] = tgt[(midx["D4"], 4)]["x_R"] if midx["D4"] <= 10 else None
    assert refs["modal"]["x_R"] is not None, "modal instance outside loaded targets"
    refs["modal"]["s"] = tgt[(midx["D4"], 4)]["s"]
    refs["modal"]["arm"] = tgt[(midx["D4"], 4)]["stratum"]
    results["modal_instance_idx"] = midx
    insts.append(("ref", "modal", refs["modal"]["x_R"]))
    for i in range(1, 11):
        insts.append(("target", i, tgt[(i, 4)]["x_R"]))
    distinct = sorted({x for _, _, x in insts})
    results["instances"] = [{"kind": k, "id": i, "x_R": x} for k, i, x in insts]
    results["distinct_instances"] = len(distinct)
    log(f"{len(insts)} instance slots, {len(distinct)} distinct x_R")

    # ---- IMPL (comparison only): producer constructor on the same x_R
    sys.path.insert(0, IMPL)
    from gf2n import TableField                     # noqa: E402  (IMPL)
    from macaulay import MacaulayShape, descended_E, affine_basis   # noqa: E402  (IMPL)
    from elim import eliminate                      # noqa: E402  (IMPL)
    TF = TableField()
    shapes = {D: MacaulayShape(D) for D in (3, 4)}
    for D in (3, 4):
        impl_cols = [tuple(m) for m in shapes[D].cols]
        ordchk[f"D{D}"]["impl_MacaulayShape_cols_equal_literal"] = impl_cols == my_cols[D]
        ordchk[f"D{D}"]["impl_MacaulayShape_mus_equal_literal"] = [tuple(m) for m in shapes[D].mus] == my_mus[D]

    # ---- affine basis (own descent)
    E0c = descent_mobius(B, 0)
    Ejc = [descent_mobius(B, 1 << j) for j in range(NEQ)]
    f0 = equations_from_coef(E0c)
    fj = []
    for j in range(NEQ):
        fx = equations_from_coef(Ejc[j])
        fj.append([fx[k].symmetric_difference(f0[k]) for k in range(NEQ)])

    per_inst = []
    for kind, ident, xR in insts:
        rec = {"kind": kind, "id": ident, "x_R": xR}
        # descent two ways + degree <= 2 + affine identity
        cs = descent_symbolic(B, xR)
        cm = descent_mobius(B, xR, dmax=4)
        rec["descent_symbolic_eq_mobius"] = cs == cm
        rec["max_degree_nonzero_coef"] = max(len(m) for m in cm)
        f = equations_from_coef(cm)
        faff = [set(f0[k]) for k in range(NEQ)]
        for j in range(NEQ):
            if (xR >> j) & 1:
                for k in range(NEQ):
                    faff[k] ^= fj[j][k]
        rec["affine_identity_E_eq_E0_plus_sum_rjEj"] = all(faff[k] == f[k] for k in range(NEQ))
        # impl descended_E vs own
        Eimpl = descended_E(TF, B, xR)
        from macaulay import EQ_MONS as IMPL_EQ_MONS  # noqa: E402 (IMPL)
        fimpl = [set(tuple(IMPL_EQ_MONS[j]) for j in np.flatnonzero(Eimpl[k])) for k in range(NEQ)]
        rec["impl_descended_E_equal_own"] = all(fimpl[k] == f[k] for k in range(NEQ))
        # own oracle s
        s_own = own_oracle_s(B, xR)
        rec["s_own_oracle"] = s_own
        rec["degenerate_own"] = xR < (1 << L)
        per_D = {}
        for D in (3, 4):
            cols = my_cols[D]
            colidx = {m: i for i, m in enumerate(cols)}
            rows = macaulay_rows(f, my_mus[D], colidx)
            C = len(cols)
            Md_own = rows_to_dense(rows, C)
            Mp_impl = shapes[D].build(Eimpl)
            Md_impl = shapes[D].unpack(Mp_impl)
            nbits_diff = int((Md_own != Md_impl).sum())
            d = {"matrix_bits_differing_vs_impl_constructor": nbits_diff,
                 "zero_rows": int(sum(1 for v in rows if v == 0))}
            t1 = time.time()
            ops, Z, T, H, cpass, leads = traces(rows, C)
            d["literal_solver_seconds"] = round(time.time() - t1, 2)
            d["rank"] = T["rank"]
            d["Z_size"] = len(Z)
            d["own_C_PASS"] = cpass
            d["one_in_R_own"] = (C - 1) in set(T["set"][0])
            # impl elimination on impl matrix, op-log level
            ires, icpass, ileads = eliminate(Mp_impl, C, keep_ops=True)
            iops = [(int(p), int(c), [int(x) for x in X]) for p, c, X in zip(ires.p, ires.c, ires.X)]
            d["impl_eliminate_oplog_equal_literal"] = iops == [(p, c, X) for p, c, X in ops]
            d["impl_rowpass_Z_equal_own"] = [int(z) for z in ires.Z] == Z
            d["impl_hashes_equal_own"] = {"rank": ires.h_rank == H["rank"], "set": ires.h_set == H["set"],
                                          "strict": ires.h_strict == H["strict"], "ops": ires.h_ops == H["ops"]}
            # archived records
            if kind == "ref":
                ar = refs[ident][f"D{D}"]
                d["archived_hashes_equal_own"] = {g: ar[f"h_{g}"] == H[g] for g in ("rank", "set", "strict", "ops")}
                d["archived_T_strict_equal_own"] = ar["T_strict"] == T["strict"]
                d["archived_rank_Zsize_oneinR_equal_own"] = (ar["rank"] == T["rank"] and ar["Z_size"] == len(Z)
                                                             and ar["one_in_R"] == d["one_in_R_own"])
                ol = oplogs[D][ident]
                d["archived_oplog_equal_own"] = [(p, c, list(X)) for p, c, X in ol] == [(p, c, X) for p, c, X in ops]
                # exact affine forms: replay the ARCHIVED op log on own M(E^0), M(E^j)
                rows0 = macaulay_rows(f0, my_mus[D], colidx)
                a0 = replay(rows0, ol)
                a = [0] * len(ol)
                for j in range(NEQ):
                    rj = macaulay_rows(fj[j], my_mus[D], colidx)
                    ej = replay(rj, ol)
                    for k in range(len(ol)):
                        a[k] |= ej[k] << j
                nz = [x for x in a if x]
                # F_2 rank of nonzero a_k
                basis = {}
                for v in nz:
                    while v:
                        hb = v.bit_length() - 1
                        if hb in basis:
                            v ^= basis[hb]
                        else:
                            basis[hb] = v
                            break
                d["K_exact_own"] = len(nz)
                d["K_rank_own"] = len(basis)
                d["archived_K_exact_K_rank_equal_own"] = (ar.get("K_exact") == len(nz) and ar.get("K_rank") == len(basis))
                # self replay: all e_k = 1 on the reference itself
                e_self = replay(rows, ol)
                d["self_replay_all_ones"] = all(x == 1 for x in e_self)
                d["affine_forms_reproduce_self_replay"] = all(
                    (a0[k] ^ (bin(a[k] & xR).count("1") & 1)) == e_self[k] for k in range(len(ol)))
                rec.setdefault("_forms", {})[D] = (a0, a)
            else:
                ar = tgt[(ident, D)]
                d["archived_hashes_equal_own"] = {g: ar[f"h_{g}"] == H[g] for g in ("rank", "set", "strict", "ops")}
                d["archived_fields_equal_own"] = {
                    "rank": ar["rank"] == T["rank"], "Z_size": ar["Z_size"] == len(Z),
                    "one_in_R": ar["one_in_R"] == d["one_in_R_own"], "len_strict": ar["len_strict"] == len(ops),
                    "ops_strict": ar["ops_strict"] == sum(len(X) for _, _, X in ops),
                    "s": ar["s"] == s_own, "degenerate": ar["degenerate"] == rec["degenerate_own"],
                    "stratum": ar["stratum"] == ("degenerate" if rec["degenerate_own"] else ("sat" if s_own >= 1 else "unsat")),
                }
                # direct replay of every reference op log on this target
                rz = {}
                for lab in ("U1", "U2", "U3", "S1", "S2"):
                    e = replay(rows, oplogs[D][lab])
                    fz = next((k for k, v in enumerate(e) if v == 0), len(e))
                    arch_fz = ar["refs"][lab].get("replay_first_zero")
                    # own affine prediction of the whole e vector
                    rz[lab] = {"first_zero_own": fz, "first_zero_archived": arch_fz, "equal": fz == arch_fz}
                    # own match flags vs archived
                    refT = refs[lab][f"D{D}"]
                    own_match = {"rank": T["rank"] == refs[lab][f"D{D}"]["rank"],
                                 "strict": T["strict"] == refT["T_strict"],
                                 "set": H["set"] == refT["h_set"], "ops": H["ops"] == refT["h_ops"]}
                    rz[lab]["match_flags_equal_archived"] = own_match == ar["refs"][lab]["match"]
                    rz[lab]["_e"] = e
                d["replay_vs_archived"] = {k: {kk: vv for kk, vv in v.items() if kk != "_e"} for k, v in rz.items()}
                d["_replays"] = {k: v["_e"] for k, v in rz.items()}
            per_D[f"D{D}"] = d
            log(f"{kind} {ident} D={D}: bits_diff={nbits_diff} rank={T['rank']} Z={len(Z)} "
                f"impl_oplog_eq={d['impl_eliminate_oplog_equal_literal']} arch_hash_eq={d['archived_hashes_equal_own']}")
        rec["per_D"] = per_D
        if kind == "ref":
            s_arch = refs[ident]["s"]
            rec["archived_s_equal_own"] = s_arch == s_own
            rec["archived_arm_equal_own"] = refs[ident]["arm"] == ("sat" if s_own >= 1 else "unsat")
        per_inst.append(rec)

    # affine forms of each reference predict the direct replay on every target
    forms = {r["id"]: r["_forms"] for r in per_inst if r["kind"] == "ref"}
    aff_vs_direct = {"pairs": 0, "pairs_all_entries_equal": 0}
    for r in per_inst:
        if r["kind"] != "target":
            continue
        for D in (3, 4):
            for lab, e in r["per_D"][f"D{D}"]["_replays"].items():
                a0, a = forms[lab][D]
                pred = [a0[k] ^ (bin(a[k] & r["x_R"]).count("1") & 1) for k in range(len(a))]
                aff_vs_direct["pairs"] += 1
                aff_vs_direct["pairs_all_entries_equal"] += int(pred == e)
    results["checks"]["affine_forms_vs_direct_replay"] = aff_vs_direct
    log(f"affine vs direct replay: {aff_vs_direct}")

    # F-S3-REV spot check (row index i -> R_D - 1 - i) on U1 and target 1
    rev = {}
    revrecs = {}
    with gzip.open(os.path.join(RUN, "targets-F-S3-REV.jsonl.gz"), "rt") as fh:
        for line in fh:
            q = json.loads(line)
            if q["idx"] == 1:
                revrecs[q["D"]] = q
    refs_rev = json.load(open(os.path.join(RUN, "references.json")))["F-S3-REV"]["references"]
    for kind, ident, xR in (("ref", "U1", refs["U1"]["x_R"]), ("target", 1, tgt[(1, 4)]["x_R"])):
        f = equations_from_coef(descent_mobius(B, xR))
        for D in (3, 4):
            colidx = {m: i for i, m in enumerate(my_cols[D])}
            rows = macaulay_rows(f, my_mus[D], colidx)[::-1]
            _, _, T, H, cpass, _ = traces(rows, len(my_cols[D]))
            arch = refs_rev["U1"][f"D{D}"] if kind == "ref" else revrecs[D]
            rev[f"{kind}-{ident}-D{D}"] = {g: arch[f"h_{g}"] == H[g] for g in ("rank", "set", "strict", "ops")}
    results["checks"]["F-S3-REV_spot"] = rev
    log(f"REV spot: {rev}")

    for r in per_inst:
        r.pop("_forms", None)
        for D in (3, 4):
            r["per_D"][f"D{D}"].pop("_replays", None)
    results["per_instance"] = per_inst
    results["wall_seconds"] = round(time.time() - T0, 1)
    results["log"] = LOG
    with open(os.path.join(HERE, "j1_results.json"), "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else int(o))
    with open(os.path.join(HERE, "j1_diffs.txt"), "w") as fh:
        fh.write("\n".join(diffs) + "\n")
    log("done")


if __name__ == "__main__":
    main()
