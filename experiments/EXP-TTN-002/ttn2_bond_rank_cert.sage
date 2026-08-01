# EXP-TTN-002 / ledger family TTN (DEC-20260718-008 follow-up i, handoff TASK-20260718-TTNM6)
# m=6 bond-rank certificate for the Semaev recursion tensor S_6.
# Exact F_p ranks of recursion-tree bonds of S_6 (d = 16, tensor side 17) via
# explicit Sylvester-structure factorizations (no symbolic S_6 materialization):
#   root  {x1,x2}|{x3..x6}:  S_6 = sum_M c^M(x1,x2) H_M(x3..x6), 45 terms  -> rank <= 45
#   child {x1,x2,x3}|{x4,x5,x6}: S_6 = sum_{M,N} s_{MN} a^M b^N, 70x70 sign matrix S
# Law chi(m) = C(2^{m-3}+2, 2) (exact at m=3,4,5 per EV-TTN-001) predicts chi(6) = 45.
# Rank certificate: F = sum L_l (FORM)_{l,r} R_r with sampled factor matrices; if sampled
# factor ranks equal structural counts (45/70) -> exact; else pivot-basis reduction
# rank(W_L FORM W_R^T), with a documented redraw and the syzygy witness recorded.
# CONVENTION: S_m := FORMAL-degree Sylvester resultant (EXP-TTN-001 definition). Sage's
# per-point .resultant() uses ACTUAL degrees; identity Sylv_{m,n}(f,g) =
# lead(f)^{n-deg(g)} Sylv_{m,deg(g)}(f,g) is applied and verified pointwise where needed.
# Deterministic: all randomness via seeded random.Random streams. Run from repo root:
#   sage experiments/EXP-TTN-002/ttn2_bond_rank_cert.sage
# Env TTN2_SMOKE=1: single-cell reduced smoke run writing to /tmp (not an artifact).

import json, time, platform, random, sys, signal, subprocess, itertools, os, hashlib
import numpy as np

SMOKE = os.environ.get("TTN2_SMOKE") == "1"
RUN_ID = os.environ.get("TTN2_RUN_ID", "RUN-TTN-002-a")
OUT_PATH = ("/tmp/ttn2_smoke_raw.json" if SMOKE
            else "experiments/EXP-TTN-002/runs/%s/raw.json" % RUN_ID)
PRIMES = [101, 431, 1009]
SEEDS = [20260717, 20260718, 20260719]
NPTS_ROOT = 96
NPTS_CHILD = 96
NPTS_GC = 64
NPTS_1 = 64
NPTS_REDRAW = 128
N_C1 = 2048
N_S5SAGE = 512
N_S4SAGE = 64
N_NESTED = 64
N_P2_S4 = 200
if SMOKE:
    PRIMES = [101]
    SEEDS = [20260717]
    N_C1 = 256
    N_S5SAGE = 48
    N_S4SAGE = 16
    N_NESTED = 16
    N_P2_S4 = 40

T0 = time.time()
def log(msg):
    print("[%6.1fs] %s" % (time.time() - T0, msg))
    sys.stdout.flush()

# ---------------------------------------------------------------- small helpers

def inv_table(p):
    inv = [0] * p
    for v in range(1, p):
        inv[v] = pow(v, p - 2, p)
    return inv

def sylvester_det(f, g, p, inv):
    # plain GE determinant of the formal Sylvester matrix; f,g coeff lists DESCENDING
    # (verbatim from EXP-TTN-001, used only for extraction self-check C2)
    mf, mg = len(f) - 1, len(g) - 1
    n = mf + mg
    M = []
    for i in range(mg):
        r = [0] * n
        for k, c in enumerate(f):
            r[i + k] = c % p
        M.append(r)
    for i in range(mf):
        r = [0] * n
        for k, c in enumerate(g):
            r[i + k] = c % p
        M.append(r)
    det = 1
    for col in range(n):
        piv = -1
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r
                break
        if piv < 0:
            return 0
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
            det = (-det) % p
        pv = M[col][col]
        det = det * pv % p
        ip = inv[pv]
        Mc = M[col]
        for r in range(col + 1, n):
            fac = M[r][col] * ip % p
            if fac:
                Mr = M[r]
                for cc in range(col + 1, n):
                    Mr[cc] = (Mr[cc] - fac * Mc[cc]) % p
    return det % p

def gen_curve(p, seed):
    rng = random.Random("curve-%d-%d" % (seed, p))
    while True:
        a = rng.randrange(p)
        b = rng.randrange(p)
        if (4 * a * a * a + 27 * b * b) % p != 0:
            return a, b

def perms_with_sign(k):
    out = []
    for perm in itertools.permutations(range(k)):
        inv = 0
        for i in range(k):
            pi = perm[i]
            for j in range(i + 1, k):
                if pi > perm[j]:
                    inv += 1
        out.append((perm, -1 if inv % 2 else 1))
    return out

PERMS = {k: perms_with_sign(k) for k in (4, 6)}

def det_perm(M, p):
    # M: (k,k,N) int64 mod p batched determinant via Leibniz (k <= 6)
    k = M.shape[0]
    acc = np.zeros(M.shape[2], dtype=np.int64)
    for perm, sgn in PERMS[k]:
        t = M[0, perm[0]].copy()
        for r in range(1, k):
            t = (t * M[r, perm[r]]) % p
        if sgn > 0:
            acc = (acc + t) % p
        else:
            acc = (acc - t) % p
    return acc

def vand_inv(k, p):
    # inverse (mod p) of Vandermonde V[row=xi][col=e] = xi^e, xi = 0..k-1
    V = [[pow(xi, e, p) for e in range(k)] for xi in range(k)]
    n = k
    A = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(V)]
    for col in range(n):
        piv = next(r for r in range(col, n) if A[r][col] % p != 0)
        A[col], A[piv] = A[piv], A[col]
        ipv = pow(A[col][col] % p, p - 2, p)
        A[col] = [(v * ipv) % p for v in A[col]]
        for r in range(n):
            if r != col and A[r][col] % p != 0:
                fac = A[r][col] % p
                A[r] = [(A[r][c] - fac * A[col][c]) % p for c in range(2 * n)]
    return np.array([row[n:] for row in A], dtype=np.int64)

def sylv_mat(fc, gc, p):
    # fc: list of m+1 arrays (ascending coeffs of f), gc: n+1 arrays; returns (m+n,m+n,N)
    m = len(fc) - 1
    n = len(gc) - 1
    N = fc[0].shape[0]
    M = np.zeros((m + n, m + n, N), dtype=np.int64)
    for r in range(n):
        for i in range(m + 1):
            M[r, r + i] = fc[m - i]
    for r in range(m):
        for i in range(n + 1):
            M[n + r, r + i] = gc[n - i]
    return M

# ---------------------------------------------------------------- Sylvester structure extraction

def extract_sylvester(mdeg, ndeg):
    # structured Leibniz enumeration of the formal (mdeg+ndeg)-Sylvester determinant.
    mdeg = int(mdeg)
    ndeg = int(ndeg)
    rows = []
    for r in range(ndeg):
        rows.append([(r + i, 0, mdeg - i) for i in range(mdeg + 1)])
    for r in range(mdeg):
        rows.append([(r + i, 1, ndeg - i) for i in range(ndeg + 1)])
    n = mdeg + ndeg
    terms = {}
    sys.setrecursionlimit(100000)

    def rec(r, usedmask, parity, fkey, gkey):
        if r == n:
            key = (tuple(sorted(fkey)), tuple(sorted(gkey)))
            terms[key] = terms.get(key, 0) + (-1 if parity else 1)
            return
        for (col, which, pw) in rows[r]:
            if (usedmask >> col) & 1:
                continue
            add = bin(usedmask >> (col + 1)).count("1")
            if which == 0:
                rec(r + 1, usedmask | (1 << col), (parity + add) & 1, fkey + [pw], gkey)
            else:
                rec(r + 1, usedmask | (1 << col), (parity + add) & 1, fkey, gkey + [pw])

    rec(0, 0, 0, [], [])
    return terms

# ---------------------------------------------------------------- vectorized coefficient machinery

def s3_coeffs(x1, x2, a, b, p):
    # coeffs of S3(x1,x2,X) in X, ascending (c0,c1,c2); int64 arrays (or 0-d) mod p.
    # NB: sage preparser turns integer literals into sage Integer; coerce everything.
    x1 = np.asarray(x1, dtype=np.int64)
    x2 = np.asarray(x2, dtype=np.int64)
    ai = int(a)
    bi = int(b)
    pi = int(p)
    I2 = int(2)
    I4 = int(4)
    c2 = (x1 - x2) ** 2 % pi
    t = ((x1 + x2) * (x1 * x2 + ai) + I2 * bi) % pi
    c1 = (pi - (I2 * t) % pi) % pi
    c0 = ((x1 * x2 - ai) ** 2 - (I4 * bi) * (x1 + x2)) % pi
    return (c0.astype(np.int64), c1.astype(np.int64), c2.astype(np.int64))

def polyval(coeffs, x, p):
    acc = np.zeros_like(x)
    for c in reversed(coeffs):
        acc = (acc * x + c) % p
    return acc

def S4Xcoeffs(P1, P2, P3, a, b, p, V5INV):
    # coeffs (ascending g0..g4) of Res_Z(S3(P1,P2,Z), S3(Z,P3,X)) as poly in X (FORMAL deg 4)
    d = s3_coeffs(P1, P2, a, b, p)
    vals = []
    for xi in range(5):
        e = s3_coeffs(np.full_like(P3, xi), P3, a, b, p)  # coeffs of S3(Z,P3,xi) in Z
        vals.append(det_perm(sylv_mat(d, e, p), p))
    V = np.stack(vals)
    return [ (V5INV[e, 0] * V[0] + V5INV[e, 1] * V[1] + V5INV[e, 2] * V[2]
              + V5INV[e, 3] * V[3] + V5INV[e, 4] * V[4]) % p for e in range(5) ]

def S4BXcoeffs(P1, P2, P3, a, b, p, V5INV):
    # coeffs of Res_Z(S3(X,P1,Z), S3(Z,P2,P3)) as poly in X (balanced right side)
    d = s3_coeffs(P2, P3, a, b, p)
    vals = []
    for xi in range(5):
        e = s3_coeffs(P1, np.full_like(P1, xi), a, b, p)  # coeffs of S3(xi,P1,Z) in Z
        vals.append(det_perm(sylv_mat(e, d, p), p))
    V = np.stack(vals)
    return [ (V5INV[e, 0] * V[0] + V5INV[e, 1] * V[1] + V5INV[e, 2] * V[2]
              + V5INV[e, 3] * V[3] + V5INV[e, 4] * V[4]) % p for e in range(5) ]

def S5Xcoeffs(T1, T2, T3, T4, a, b, p, V5INV, V9INV):
    # coeffs (h0..h8) of S5(X,T1..T4) = Res_Z(S3(X,T1,Z), S4(Z,T2,T3,T4)) in X (FORMAL deg 8)
    g = S4Xcoeffs(T2, T3, T4, a, b, p, V5INV)
    vals = []
    for xi in range(9):
        d = s3_coeffs(T1, np.full_like(T1, xi), a, b, p)  # coeffs of S3(xi,T1,Z) in Z
        vals.append(det_perm(sylv_mat(d, g, p), p))
    V = np.stack(vals)
    return [ sum((V9INV[e, k] * V[k] for k in range(9)), np.zeros_like(V[0])) % p
             for e in range(9) ]

def monomial_products(coeffs, keys, p):
    N = coeffs[0].shape[0]
    out = np.ones((N, len(keys)), dtype=np.int64)
    for j, key in enumerate(keys):
        t = out[:, j]
        for pw in key:
            t = (t * coeffs[pw]) % p
        out[:, j] = t
    return out

def sage_rank(arr, p):
    return int(matrix(GF(p), [[int(v) % p for v in row] for row in arr]).rank())

def factor_basis(Fmat, p):
    # Fmat (N,K): sampled factor matrix, columns = evals of a polynomial family.
    # returns (rank, pivot_columns, W (r,K)): family members expressed in pivot basis.
    Ms = matrix(GF(p), [[int(v) % p for v in row] for row in Fmat])
    r = int(Ms.rank())
    piv = list(Ms.pivots())
    U = Ms.matrix_from_columns(piv)
    W = U.solve_right(Ms)
    Wnp = np.array([[int(v) for v in row] for row in W.rows()], dtype=np.int64)
    return r, piv, Wnp

def kernel_witness(Fmat, p):
    # right kernel of Fmat: relations among the family members (syzygy witnesses)
    Ms = matrix(GF(p), [[int(v) % p for v in row] for row in Fmat])
    K = Ms.right_kernel()
    return [[int(v) for v in vec] for vec in K.basis()]

# ---------------------------------------------------------------- CUR (verbatim semantics from EXP-TTN-001)

def cur_pivots(M):
    A, B = M.nrows(), M.ncols()
    Mc = copy(M)
    pr, pc = [], []
    used = set()
    for j in range(B):
        piv = None
        for i in range(A):
            if i not in used and Mc[i, j] != 0:
                piv = i
                break
        if piv is None:
            continue
        pr.append(piv)
        pc.append(j)
        used.add(piv)
        invv = Mc[piv, j] ** -1
        for r in range(A):
            if r != piv and Mc[r, j] != 0:
                Mc[r, :] -= Mc[r, j] * invv * Mc[piv, :]
    return pr, pc

def cur_truncate(M, pr, pc, chi):
    R = pr[:chi]
    C = pc[:chi]
    Mhat = M.matrix_from_columns(C) * M.matrix_from_rows_and_columns(R, C).inverse() * M.matrix_from_rows(R)
    return np.array([[int(v) for v in row] for row in Mhat.rows()], dtype=np.int64)

# ---------------------------------------------------------------- extraction + self-check (C2)

log("extracting root 10x10 Sylvester structure ...")
ROOT_TERMS = extract_sylvester(2, 8)
log("root terms extracted: %d nonzero keys" % len(ROOT_TERMS))
log("extracting child 8x8 Sylvester structure ...")
CHILD_TERMS = extract_sylvester(4, 4)
log("child terms extracted: %d nonzero keys" % len(CHILD_TERMS))

CKEYS = sorted(set(k[0] for k in ROOT_TERMS))
HKEYS = sorted(set(k[1] for k in ROOT_TERMS))
AKEYS = sorted(set(k[0] for k in CHILD_TERMS))
BKEYS = sorted(set(k[1] for k in CHILD_TERMS))
assert len(CKEYS) == 45 and len(HKEYS) == 45, (len(CKEYS), len(HKEYS))
assert len(AKEYS) == 70 and len(BKEYS) == 70, (len(AKEYS), len(BKEYS))
CKIDX = {k: i for i, k in enumerate(CKEYS)}
AKIDX = {k: i for i, k in enumerate(AKEYS)}
BKIDX = {k: i for i, k in enumerate(BKEYS)}

S_ROOT = [[] for _ in range(45)]
for (ck, hk), coeff in ROOT_TERMS.items():
    if coeff:
        S_ROOT[CKIDX[ck]].append((hk, coeff))
S_CHILD = np.zeros((70, 70), dtype=np.int64)
for (ak, bk), coeff in CHILD_TERMS.items():
    S_CHILD[AKIDX[ak], BKIDX[bk]] = int(coeff)
S_CHILD_QQ_RANK = int(matrix(QQ, [[int(v) for v in row] for row in S_CHILD]).rank())
log("child S matrix: %d nonzero entries, rank over QQ = %d" %
    (int((S_CHILD != 0).sum()), S_CHILD_QQ_RANK))

def expansion_value_root(cvals, hvals):
    tot = 0
    for mi, ck in enumerate(CKEYS):
        cm = 1
        for pw in ck:
            cm *= cvals[pw]
        hv = 0
        for (hk, coeff) in S_ROOT[mi]:
            hv += coeff * hvals[hk[0]] * hvals[hk[1]]
        tot += cm * hv
    return tot

def expansion_value_child(avals, bvals):
    tot = 0
    for (ak, bk), coeff in CHILD_TERMS.items():
        if not coeff:
            continue
        am = 1
        for pw in ak:
            am *= avals[pw]
        bm = 1
        for pw in bk:
            bm *= bvals[pw]
        tot += int(coeff) * am * bm
    return tot

C2 = {"root": [], "child": []}
rngc2 = random.Random("c2-selfcheck")
for p in PRIMES:
    inv = inv_table(p)
    ok_r = ok_c = 0
    for _ in range(3):
        cvals = [rngc2.randrange(p) for _ in range(3)]
        hvals = [rngc2.randrange(p) for _ in range(9)]
        avals = [rngc2.randrange(p) for _ in range(5)]
        bvals = [rngc2.randrange(p) for _ in range(5)]
        v1 = expansion_value_root(cvals, hvals) % p
        v2 = sylvester_det([cvals[2], cvals[1], cvals[0]], list(reversed(hvals)), p, inv)
        w1 = expansion_value_child(avals, bvals) % p
        w2 = sylvester_det(list(reversed(avals)), list(reversed(bvals)), p, inv)
        ok_r += (v1 == v2)
        ok_c += (w1 == w2)
    C2["root"].append({"p": p, "agreements": ok_r, "of": 3})
    C2["child"].append({"p": p, "agreements": ok_c, "of": 3})
C2_PASS = all(x["agreements"] == 3 for x in C2["root"]) and all(x["agreements"] == 3 for x in C2["child"])
log("C2 extraction self-check: %s pass=%s" % (C2, C2_PASS))

extraction_fp = hashlib.sha256(
    json.dumps({"root": sorted([list(k[0]), list(k[1]), v] for k, v in ROOT_TERMS.items()),
                "child": sorted([list(k[0]), list(k[1]), v] for k, v in CHILD_TERMS.items())},
               sort_keys=True, default=lambda o: int(o)).encode()).hexdigest()

# ---------------------------------------------------------------- main structures

result = {
    "experiment_id": "EXP-TTN-002",
    "run_id": RUN_ID,
    "smoke": SMOKE,
    "parameters": {
        "primes": PRIMES, "seeds": SEEDS, "m": 6, "degree_d": 16, "tensor_side": 17,
        "points": {"root": NPTS_ROOT, "child": NPTS_CHILD, "grandchild": NPTS_GC,
                   "singlevar": NPTS_1, "redraw": NPTS_REDRAW, "C1": N_C1,
                   "S5_sage": N_S5SAGE, "S4_sage": N_S4SAGE, "nested_sage": N_NESTED,
                   "P2_S4": N_P2_S4},
        "bonds": {"root": "{x1,x2}|{x3,x4,x5,x6}", "child": "{x1,x2,x3}|{x4,x5,x6}",
                  "grandchild": "{x1,x2,x3,x4}|{x5,x6}", "singlevar": "{x1}|rest"},
        "predictions": {"root": 45, "child_law_facevalue": 45, "child_balanced_multiset": 70,
                        "grandchild": 45, "singlevar": 17},
        "convention": "formal-degree Sylvester resultant; sage per-point actual-degree resultants corrected via lead(f)^{drop} identity where used",
    },
    "extraction": {"root_nonzero_terms": len(ROOT_TERMS), "child_nonzero_terms": len(CHILD_TERMS),
                   "child_S_nonzero": int((S_CHILD != 0).sum()),
                   "child_S_rank_QQ": S_CHILD_QQ_RANK, "sha256": extraction_fp,
                   "C2_selfcheck": C2, "C2_pass": C2_PASS},
    "cells": [],
    "deviations": [],
}

if not C2_PASS:
    result["deviations"].append("C2 extraction self-check FAILED - run invalid")
    with open(OUT_PATH, "w") as fh:
        json.dump(result, fh, indent=1, default=str)
    log("C2 failed; aborting")
    sys.exit(1)

started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def s3_sym(R, u, v, w, a, b):
    return ((u - v) ** 2 * w ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * w
            + (u * v - a) ** 2 - 4 * b * (u + v))

def build_symbolic_S4_S5(p, a, b):
    # formal-degree nested resultants on multivariate rings (EXP-TTN-001 build convention)
    Fp = GF(p)
    R4 = PolynomialRing(Fp, names=['u1', 'u2', 'u3', 'X', 'Z'])
    u1, u2, u3, X4, Z4 = R4.gens()
    S4sym = s3_sym(R4, u1, u2, Z4, a, b).resultant(s3_sym(R4, Z4, u3, X4, a, b), Z4)
    R5 = PolynomialRing(Fp, names=['v1', 'v2', 'v3', 'v4', 'X', 'Z', 'W'])
    v1, v2, v3, v4, X5, Z5, W5 = R5.gens()
    S4inner = s3_sym(R5, Z5, v2, W5, a, b).resultant(s3_sym(R5, W5, v3, v4, a, b), W5)
    S5sym = s3_sym(R5, X5, v1, Z5, a, b).resultant(S4inner, Z5)
    return S4sym, R4, S5sym, R5

def sym_to_coeff_tensor(S, var_names, side, p):
    # S: sage multivariate poly; var_names: axis-ordered variable names;
    # side: per-axis size (exponents 0..side-1). Returns numpy int64 array.
    R = S.parent()
    gens = {str(g): i for i, g in enumerate(R.gens())}
    idx = [gens[nm] for nm in var_names]
    zpos = [i for i in range(len(R.gens())) if i not in idx]
    T = np.zeros((side,) * len(var_names), dtype=np.int64)
    for mono, coeff in S.dict().items():
        for zp in zpos:
            assert int(mono[zp]) == 0, "eliminated variable survives in S5sym"
        key = tuple(int(mono[idx[k]]) for k in range(len(var_names)))
        if all(e < side for e in key):
            T[key] = int(coeff) % p
    return T

def diag_eval(T, Vlist, p):
    # staged diagonal contraction with per-stage mod-p reduction (int64-safe):
    # returns vals[i] = sum_e T[e0..ek] prod_k Vlist[k][i, e_k], WITHOUT materializing grids
    E = T
    N = Vlist[0].shape[0]
    G = np.tensordot(Vlist[0], E, axes=([1], [0])) % p      # (N, 9,9,9,9)
    for k in range(1, len(Vlist)):
        letters_in = ''.join(chr(ord('j') + t) for t in range(G.ndim - 1))
        G = np.einsum('i' + letters_in + ',i' + letters_in[0] + '->i' + letters_in[1:],
                      G, Vlist[k], optimize=True) % p
    return G

def vandermonde(X, n, p):
    X = np.asarray(X, dtype=np.int64)
    V = np.zeros((X.shape[0], n), dtype=np.int64)
    V[:, 0] = 1 % p
    for e in range(1, n):
        V[:, e] = (V[:, e - 1] * X) % p
    return V

# ---------------------------------------------------------------- cell loop

for p in PRIMES:
    Fp = GF(p)
    V5INV = vand_inv(5, p)
    V9INV = vand_inv(9, p)
    S_CHILD_MOD = S_CHILD % p
    S_child_rank_p = sage_rank(S_CHILD, p)
    for seed in SEEDS:
        tcell = time.time()
        a, b = gen_curve(p, seed)
        cell = {"p": p, "seed": seed, "curve": {"a": a, "b": b},
                "S_child_rank_mod_p": S_child_rank_p}
        log("cell p=%d seed=%d curve a=%d b=%d" % (p, seed, a, b))

        # ---- P1: S3 baseline on curve points
        E_curve = EllipticCurve(Fp, [a, b])
        rng1 = random.Random("p1-%d-%d" % (seed, p))
        ok1 = 0
        tries = 0
        while ok1 < 20 and tries < 400:
            tries += 1
            def rand_pt():
                while True:
                    x = rng1.randrange(p)
                    rhs = (x * x * x + a * x + b) % p
                    if Fp(rhs).is_square():
                        return E_curve(x, Fp(rhs).sqrt())
            P = rand_pt()
            Q = rand_pt()
            Rpt = -(P + Q)
            c0, c1, c2 = s3_coeffs(np.int64(P[0]), np.int64(Q[0]), a, b, p)
            val = (int(c2) * pow(int(Rpt[0]), 2, p) + int(c1) * int(Rpt[0]) + int(c0)) % p
            if val == 0:
                ok1 += 1
        cell["P1_S3_baseline"] = (ok1 == 20)

        # ---- point samplers
        rng = random.Random("pts-%d-%d" % (seed, p))
        def sample(n, dim):
            return np.array([[rng.randrange(p) for _ in range(dim)] for _ in range(n)],
                            dtype=np.int64)

        # ================= ROOT bond {x1,x2}|{x3..x6}
        def root_factors(U, V):
            cU = s3_coeffs(U[:, 0], U[:, 1], a, b, p)
            CM = monomial_products(cU, CKEYS, p)
            hV = S5Xcoeffs(V[:, 0], V[:, 1], V[:, 2], V[:, 3], a, b, p, V5INV, V9INV)
            HM = np.zeros((V.shape[0], 45), dtype=np.int64)
            for mi in range(45):
                acc = np.zeros(V.shape[0], dtype=np.int64)
                for (hk, coeff) in S_ROOT[mi]:
                    acc = (acc + int(coeff) * ((hV[hk[0]] * hV[hk[1]]) % p)) % p
                HM[:, mi] = acc
            return CM, HM

        U = sample(NPTS_ROOT, 2)
        V = sample(NPTS_ROOT, 4)
        CM, HM = root_factors(U, V)
        E_root = (CM @ HM.T) % p
        rC, pivC, WC = factor_basis(CM, p)
        rH, pivH, WH = factor_basis(HM, p)
        rank_root_form = sage_rank((WC @ WH.T) % p, p)
        rank_E_root = sage_rank(E_root, p)
        cell["root"] = {"rank_CM": rC, "rank_HM": rH, "rank_E": rank_E_root,
                        "rank_form": rank_root_form,
                        "certified_rank": (45 if (rC == 45 and rH == 45) else None),
                        "C3_E_eq_form": bool(rank_E_root == rank_root_form)}
        if rC < 45 or rH < 45:
            cell["root"]["syzygy_CM"] = kernel_witness(CM, p)
            cell["root"]["syzygy_HM"] = kernel_witness(HM, p)
        log("  root: rank(CM)=%d rank(HM)=%d rank(E)=%d form=%d" % (rC, rH, rank_E_root, rank_root_form))

        # ================= CHILD bond {x1,x2,x3}|{x4,x5,x6}
        def child_factors(U3, V3):
            aU = S4Xcoeffs(U3[:, 0], U3[:, 1], U3[:, 2], a, b, p, V5INV)
            AM = monomial_products(aU, AKEYS, p)
            bV = S4BXcoeffs(V3[:, 0], V3[:, 1], V3[:, 2], a, b, p, V5INV)
            BM = monomial_products(bV, BKEYS, p)
            return AM, BM

        U3 = sample(NPTS_CHILD, 3)
        V3 = sample(NPTS_CHILD, 3)
        AM, BM = child_factors(U3, V3)
        E_child = ((AM @ S_CHILD_MOD) % p @ BM.T) % p
        rA, pivA, WA = factor_basis(AM, p)
        rB, pivB, WB = factor_basis(BM, p)
        rank_child_form = sage_rank(((WA @ S_CHILD_MOD) % p @ WB.T) % p, p)
        rank_E_child = sage_rank(E_child, p)
        cell["child"] = {"rank_AM": rA, "rank_BM": rB, "rank_E": rank_E_child,
                         "rank_form": rank_child_form, "rank_S_mod_p": S_child_rank_p,
                         "certified_rank": (S_child_rank_p if (rA == 70 and rB == 70) else None),
                         "C3_E_eq_form": bool(rank_E_child == rank_child_form)}
        if rA < 70 or rB < 70:
            cell["child"]["syzygy_AM"] = kernel_witness(AM, p)
            cell["child"]["syzygy_BM"] = kernel_witness(BM, p)
        log("  child: rank(AM)=%d rank(BM)=%d rank(E)=%d form=%d rank(S)=%d" %
            (rA, rB, rank_E_child, rank_child_form, S_child_rank_p))

        # ---- redraw (documented stopping rule) if any factor rank deficient
        if rC < 45 or rH < 45 or rA < 70 or rB < 70:
            rng_r = random.Random("pts2-%d-%d" % (seed, p))
            def sample2(n, dim):
                return np.array([[rng_r.randrange(p) for _ in range(dim)] for _ in range(n)],
                                dtype=np.int64)
            U2 = sample2(NPTS_REDRAW, 2)
            V2 = sample2(NPTS_REDRAW, 4)
            CM2, HM2 = root_factors(U2, V2)
            U32 = sample2(NPTS_REDRAW, 3)
            V32 = sample2(NPTS_REDRAW, 3)
            AM2, BM2 = child_factors(U32, V32)
            rC2, _, WC2 = factor_basis(CM2, p)
            rH2, _, WH2 = factor_basis(HM2, p)
            rA2, _, WA2 = factor_basis(AM2, p)
            rB2, _, WB2 = factor_basis(BM2, p)
            cell["redraw"] = {"points": NPTS_REDRAW, "rank_CM": rC2, "rank_HM": rH2,
                              "rank_AM": rA2, "rank_BM": rB2,
                              "rank_root_form": sage_rank((WC2 @ WH2.T) % p, p),
                              "rank_child_form": sage_rank(((WA2 @ S_CHILD_MOD) % p @ WB2.T) % p, p)}
            if rA2 < 70:
                cell["redraw"]["syzygy_AM"] = kernel_witness(AM2, p)
            if rB2 < 70:
                cell["redraw"]["syzygy_BM"] = kernel_witness(BM2, p)
            if rC2 < 45:
                cell["redraw"]["syzygy_CM"] = kernel_witness(CM2, p)
            if rH2 < 45:
                cell["redraw"]["syzygy_HM"] = kernel_witness(HM2, p)
            log("  redraw: CM=%d HM=%d AM=%d BM=%d rootform=%d childform=%d" %
                (rC2, rH2, rA2, rB2, cell["redraw"]["rank_root_form"], cell["redraw"]["rank_child_form"]))

        # ================= GRANDCHILD {x1..x4}|{x5,x6} (symmetry probe)
        U4 = sample(NPTS_GC, 4)
        V2b = sample(NPTS_GC, 2)
        cU4 = s3_coeffs(U4[:, 0], U4[:, 1], a, b, p)
        CM4 = monomial_products(cU4, CKEYS, p)
        P3a = np.repeat(U4[:, 2], NPTS_GC)
        P4a = np.repeat(U4[:, 3], NPTS_GC)
        P5a = np.tile(V2b[:, 0], NPTS_GC)
        P6a = np.tile(V2b[:, 1], NPTS_GC)
        hpair = S5Xcoeffs(P3a, P4a, P5a, P6a, a, b, p, V5INV, V9INV)
        HMpair = np.zeros((NPTS_GC * NPTS_GC, 45), dtype=np.int64)
        for mi in range(45):
            acc = np.zeros(NPTS_GC * NPTS_GC, dtype=np.int64)
            for (hk, coeff) in S_ROOT[mi]:
                acc = (acc + int(coeff) * ((hpair[hk[0]] * hpair[hk[1]]) % p)) % p
            HMpair[:, mi] = acc
        HMpair = HMpair.reshape(NPTS_GC, NPTS_GC, 45)
        E_gc = np.einsum('im,ijm->ij', CM4, HMpair) % p
        cell["grandchild"] = {"rank_E": sage_rank(E_gc, p)}
        log("  grandchild: rank(E)=%d" % cell["grandchild"]["rank_E"])

        # ================= SINGLE-VAR {x1}|rest (context)
        U1 = sample(NPTS_1, 1)
        V5 = sample(NPTS_1, 5)
        cU1 = s3_coeffs(np.repeat(U1[:, 0], NPTS_1), np.tile(V5[:, 0], NPTS_1), a, b, p)
        CM1 = monomial_products(cU1, CKEYS, p).reshape(NPTS_1, NPTS_1, 45)
        hV5 = S5Xcoeffs(V5[:, 1], V5[:, 2], V5[:, 3], V5[:, 4], a, b, p, V5INV, V9INV)
        HM1 = np.zeros((NPTS_1, 45), dtype=np.int64)
        for mi in range(45):
            acc = np.zeros(NPTS_1, dtype=np.int64)
            for (hk, coeff) in S_ROOT[mi]:
                acc = (acc + int(coeff) * ((hV5[hk[0]] * hV5[hk[1]]) % p)) % p
            HM1[:, mi] = acc
        E_1 = np.einsum('ijm,jm->ij', CM1, HM1) % p
        cell["singlevar"] = {"rank_E": sage_rank(E_1, p)}
        log("  singlevar: rank(E)=%d" % cell["singlevar"]["rank_E"])

        # ================= symbolic S4/S5 (sage, independent construction)
        tsym = time.time()
        S4sym, R4, S5sym, R5 = build_symbolic_S4_S5(p, a, b)
        cell["t_symbolic_S4S5_s"] = time.time() - tsym
        cell["S4sym_terms"] = len(S4sym.monomials())
        cell["S5sym_terms"] = len(S5sym.monomials())
        T5sym = sym_to_coeff_tensor(S5sym, ['v1', 'v2', 'v3', 'v4', 'X'], 9, p)

        # ---- P2-S4: my S4Xcoeffs vs direct per-point dets (200) and vs S4sym evals (64)
        rng2 = random.Random("p2-%d-%d" % (seed, p))
        T = np.array([[rng2.randrange(p) for _ in range(4)] for _ in range(N_P2_S4)], dtype=np.int64)
        g = S4Xcoeffs(T[:, 0], T[:, 1], T[:, 2], a, b, p, V5INV)
        val_interp = polyval(g, T[:, 3], p)
        dA = s3_coeffs(T[:, 0], T[:, 1], a, b, p)
        dB = s3_coeffs(T[:, 2], T[:, 3], a, b, p)
        val_direct = det_perm(sylv_mat(dA, dB, p), p)
        cell["P2_S4_path"] = bool((val_interp == val_direct).all())
        ok4s = 0
        R4gens = R4.gens()
        for i in range(min(N_S4SAGE, N_P2_S4)):
            t1, t2, t3, t4 = [int(v) for v in T[i]]
            v_sym = int(S4sym.subs({R4gens[0]: t1, R4gens[1]: t2, R4gens[2]: t3,
                                    R4gens[3]: t4})) % p
            ok4s += (v_sym == int(val_interp[i]))
        cell["P2_S4_vs_sageSym"] = {"agreements": ok4s, "of": min(N_S4SAGE, N_P2_S4)}

        # ---- P2-S5 + C1-sage: my S5Xcoeffs vs symbolic S5 (diagonal contraction, no grid)
        rng5 = random.Random("p2s5-%d-%d" % (seed, p))
        PS5 = np.array([[rng5.randrange(p) for _ in range(5)] for _ in range(N_S5SAGE)],
                       dtype=np.int64)
        # point i: (X = PS5[i,0], v1..v4 = PS5[i,1..4]); T5sym axes are (v1,v2,v3,v4,X)
        Vv = [vandermonde(PS5[:, k], 9, p) for k in (1, 2, 3, 4)]
        Vx = vandermonde(PS5[:, 0], 9, p)
        v_sym5 = diag_eval(T5sym, [Vv[0], Vv[1], Vv[2], Vv[3], Vx], p) % p
        hM = S5Xcoeffs(PS5[:, 1], PS5[:, 2], PS5[:, 3], PS5[:, 4], a, b, p, V5INV, V9INV)
        val_my5 = polyval(hM, PS5[:, 0], p)
        mism5 = int((val_my5 != v_sym5).sum())
        cell["P2_S5_vs_sageSym"] = {"points": N_S5SAGE, "mismatches": mism5}

        # ---- C1 part 1: comb vs balanced expansions (identity S6_comb == S6_bal)
        rngc = random.Random("c1-%d-%d" % (seed, p))
        PC = np.array([[rngc.randrange(p) for _ in range(6)] for _ in range(N_C1)], dtype=np.int64)
        cC = s3_coeffs(PC[:, 0], PC[:, 1], a, b, p)
        CMC = monomial_products(cC, CKEYS, p)
        hC = S5Xcoeffs(PC[:, 2], PC[:, 3], PC[:, 4], PC[:, 5], a, b, p, V5INV, V9INV)
        HMC = np.zeros((N_C1, 45), dtype=np.int64)
        for mi in range(45):
            acc = np.zeros(N_C1, dtype=np.int64)
            for (hk, coeff) in S_ROOT[mi]:
                acc = (acc + int(coeff) * ((hC[hk[0]] * hC[hk[1]]) % p)) % p
            HMC[:, mi] = acc
        val_comb = (CMC * HMC).sum(axis=1) % p
        aC = S4Xcoeffs(PC[:, 0], PC[:, 1], PC[:, 2], a, b, p, V5INV)
        AMC = monomial_products(aC, AKEYS, p)
        bC = S4BXcoeffs(PC[:, 3], PC[:, 4], PC[:, 5], a, b, p, V5INV)
        BMC = monomial_products(bC, BKEYS, p)
        val_bal = ((AMC @ S_CHILD_MOD) % p * BMC).sum(axis=1) % p
        cell["C1_comb_vs_balanced"] = {"points": N_C1,
                                       "mismatches": int((val_comb != val_bal).sum())}

        # ---- C1 part 2: comb vs fully-nested per-point sage resultants, with the sage side
        #      padded to FORMAL degree at every level via Sylv_{m,n}(f,g) =
        #      lead(f)^{n-deg(g)} Sylv_{m,deg(g)}(f,g) (exact polynomial identity).
        R5gens = R5.gens()
        v1g, v2g, v3g, v4g, Xg, Zg, Wg = R5gens
        nested = {"points": N_NESTED, "checked_exact": 0, "padded_points": 0,
                  "degf_dropped_recorded": 0, "mismatches": 0, "examples": []}
        rngn2 = random.Random("c1nested-%d-%d" % (seed, p))
        for _ in range(N_NESTED):
            x1, x2, x3, x4, x5, x6 = [rngn2.randrange(p) for _ in range(6)]
            # level S4: sage actual-degree resultant, then pad to formal (deg W = 2+2)
            f1 = s3_sym(R5, Zg, Fp(x4), Wg, a, b)
            f2 = s3_sym(R5, Wg, Fp(x5), Fp(x6), a, b)
            deg_f2 = int(f2.degree(Wg))
            s4_actual = f1.resultant(f2, Wg)
            s4_formal = (Zg - Fp(x4)) ** (2 * (2 - deg_f2)) * s4_actual
            # level S5: pad to formal (deg Z = 2+4)
            deg_s4f = int(s4_formal.degree(Zg))
            g1 = s3_sym(R5, Xg, Fp(x3), Zg, a, b)
            s5_actual = g1.resultant(s4_formal, Zg)
            s5_formal = (Xg - Fp(x3)) ** (2 * (4 - deg_s4f)) * s5_actual
            # level S6: pad to formal (deg X = 2+8)
            deg_s5f = int(s5_formal.degree(Xg))
            fs = s3_sym(R5, Fp(x1), Fp(x2), Xg, a, b)
            c2v = (x1 - x2) ** 2 % p
            s6_actual = fs.resultant(s5_formal, Xg)
            sage_val = int(Fp(c2v) ** (8 - deg_s5f) * s6_actual) % p
            # my comb value at the point
            cc = s3_coeffs(np.array([x1]), np.array([x2]), a, b, p)
            hh = S5Xcoeffs(np.array([x3]), np.array([x4]), np.array([x5]), np.array([x6]),
                           a, b, p, V5INV, V9INV)
            cmv = monomial_products(cc, CKEYS, p)
            hmv = np.zeros((1, 45), dtype=np.int64)
            for mi in range(45):
                acc = np.zeros(1, dtype=np.int64)
                for (hk, coeff) in S_ROOT[mi]:
                    acc = (acc + int(coeff) * ((hh[hk[0]] * hh[hk[1]]) % p)) % p
                hmv[0, mi] = int(acc[0])
            my_val = int((cmv * hmv).sum()) % p
            if c2v == 0:
                # lead of fs itself dropped: padding direction changes; record only
                nested["degf_dropped_recorded"] += 1
                continue
            if my_val == sage_val:
                if deg_f2 < 2 or deg_s4f < 4 or deg_s5f < 8:
                    nested["padded_points"] += 1
                else:
                    nested["checked_exact"] += 1
            else:
                nested["mismatches"] += 1
                if len(nested["examples"]) < 3:
                    nested["examples"].append({"point": [x1, x2, x3, x4, x5, x6],
                                               "my": my_val, "sage_formal": sage_val,
                                               "drops": [2 - deg_f2, 4 - deg_s4f, 8 - deg_s5f]})
        cell["C1_comb_vs_sageNested"] = nested
        log("  C1: comb-vs-bal %d/%d mism; nested sage: exact=%d padded=%d degf0=%d mism=%d; P2 S5 mism=%d" %
            (cell["C1_comb_vs_balanced"]["mismatches"], N_C1, nested["checked_exact"],
             nested["padded_points"], nested["degf_dropped_recorded"],
             nested["mismatches"], mism5))

        # ================= P3: CUR exactness at full rank on E_root
        Msage = matrix(GF(p), [[int(v) % p for v in row] for row in E_root])
        pr, pc = cur_pivots(Msage)
        assert len(pr) == rank_E_root, "pivot count != rank"
        That = cur_truncate(Msage, pr, pc, rank_E_root)
        cell["P3_CUR_exact_Eroot"] = bool(np.array_equal(That % p, E_root % p))

        # ================= N1, N2 negative controls
        rngn = random.Random("neg-%d-%d" % (seed, p))
        RND = np.array([[rngn.randrange(p) for _ in range(NPTS_ROOT)] for _ in range(NPTS_ROOT)],
                       dtype=np.int64)
        cell["N1_random_96_rank"] = sage_rank(RND, p)
        Fp45 = np.array([[rngn.randrange(p) for _ in range(45)] for _ in range(NPTS_ROOT)],
                        dtype=np.int64)
        Gp45 = np.array([[rngn.randrange(p) for _ in range(45)] for _ in range(NPTS_ROOT)],
                        dtype=np.int64)
        cell["N2_planted_rank45"] = sage_rank((Fp45 @ Gp45.T) % p, p)

        cell["t_cell_s"] = time.time() - tcell
        result["cells"].append(cell)
        log("cell done: p=%d seed=%d t=%.1fs" % (p, seed, cell["t_cell_s"]))

# ---------------------------------------------------------------- summary

cells = result["cells"]

def ranks_of(key1, key2):
    return sorted(set(c[key1][key2] for c in cells))

summary = {
    "root_ranks_E": ranks_of("root", "rank_E"),
    "root_ranks_CM": ranks_of("root", "rank_CM"),
    "root_ranks_HM": ranks_of("root", "rank_HM"),
    "root_ranks_form": ranks_of("root", "rank_form"),
    "root_certified_45_all": all(c["root"]["certified_rank"] == 45 for c in cells),
    "child_ranks_E": ranks_of("child", "rank_E"),
    "child_ranks_AM": ranks_of("child", "rank_AM"),
    "child_ranks_BM": ranks_of("child", "rank_BM"),
    "child_ranks_form": ranks_of("child", "rank_form"),
    "child_S_rank_mod_p": sorted(set(c["child"]["rank_S_mod_p"] for c in cells)),
    "child_S_rank_QQ": S_CHILD_QQ_RANK,
    "grandchild_ranks_E": ranks_of("grandchild", "rank_E"),
    "singlevar_ranks_E": ranks_of("singlevar", "rank_E"),
    "controls": {
        "P1_S3_baseline_all": all(c["P1_S3_baseline"] for c in cells),
        "P2_S4_path_all": all(c["P2_S4_path"] for c in cells),
        "P2_S4_vs_sageSym_all": all(c["P2_S4_vs_sageSym"]["agreements"] == c["P2_S4_vs_sageSym"]["of"]
                                    for c in cells),
        "P2_S5_vs_sageSym_all": all(c["P2_S5_vs_sageSym"]["mismatches"] == 0 for c in cells),
        "C1_comb_vs_balanced_all": all(c["C1_comb_vs_balanced"]["mismatches"] == 0 for c in cells),
        "C1_comb_vs_sageNested_all": all(c["C1_comb_vs_sageNested"]["mismatches"] == 0 for c in cells),
        "C3_E_eq_form_all": all(c["root"]["C3_E_eq_form"] and c["child"]["C3_E_eq_form"]
                                for c in cells),
        "P3_CUR_exact_all": all(c["P3_CUR_exact_Eroot"] for c in cells),
        "N1_random_full_rank_all": all(c["N1_random_96_rank"] == NPTS_ROOT for c in cells),
        "N2_planted_rank45_all": all(c["N2_planted_rank45"] == 45 for c in cells),
        "C2_extraction_selfcheck": C2_PASS,
    },
    "n_cells": len(cells),
    "wall_seconds_script": time.time() - T0,
    "sage_version": str(sage.version.version),
    "python_version": platform.python_version(),
    "numpy_version": np.__version__,
    "platform": platform.platform(),
    "started_at_utc": started_utc,
}
fi_keys = ["root_ranks_E", "root_ranks_CM", "root_ranks_HM", "child_ranks_E",
           "child_ranks_form", "grandchild_ranks_E", "singlevar_ranks_E"]
summary["field_independence_all_bonds"] = all(len(summary[k]) == 1 for k in fi_keys)
result["summary"] = summary

def sanitize(o):
    if isinstance(o, dict):
        return {str(k): sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if o is None or isinstance(o, (int, float, str)):
        return o
    try:
        f = float(o)
        i = int(o)
        return i if f == i else f
    except Exception:
        return str(o)

with open(OUT_PATH, "w") as fh:
    json.dump(sanitize(result), fh, indent=1)
log("WROTE %s cells=%d wall=%.1fs" % (OUT_PATH, len(cells), summary["wall_seconds_script"]))
