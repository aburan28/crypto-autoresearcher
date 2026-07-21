# EXP-TTN-002 / ledger family TTN (DEC-20260718-008 follow-up i, handoff TASK-20260718-TTNM6)
# m=6 bond-rank certificate for the Semaev recursion tensor S_6.
# Exact F_p ranks of recursion-tree bonds of S_6 (d = 16, tensor side 17) via
# explicit Sylvester-structure factorizations (no symbolic S_6 materialization):
#   root  {x1,x2}|{x3..x6}:  S_6 = sum_M c^M(x1,x2) H_M(x3..x6), 45 terms  -> rank <= 45
#   child {x1,x2,x3}|{x4,x5,x6}: S_6 = sum_{M,N} s_{MN} a^M b^N, 70x70 sign matrix S
# Law chi(m) = C(2^{m-3}+2, 2) (exact at m=3,4,5 per EV-TTN-001) predicts chi(6) = 45.
# Deterministic: all randomness via seeded random.Random streams. Run from repo root:
#   sage experiments/EXP-TTN-002/ttn2_bond_rank_cert.sage
# Env TTN2_SMOKE=1: single-cell reduced smoke run writing to /tmp (not an artifact).

import json, time, platform, random, sys, signal, subprocess, itertools, os, hashlib
import numpy as np

SMOKE = os.environ.get("TTN2_SMOKE") == "1"
OUT_PATH = ("/tmp/ttn2_smoke_raw.json" if SMOKE
            else "experiments/EXP-TTN-002/runs/RUN-TTN-002-a/raw.json")
PRIMES = [101, 431, 1009]
SEEDS = [20260717, 20260718, 20260719]
NPTS_ROOT = 96
NPTS_CHILD = 96
NPTS_GC = 64
NPTS_1 = 64
N_C1 = 2048
N_SAGE = 512
N_P2_S4 = 200
N_P2_S5 = 64
PROBE_ALARM_S = 90
if SMOKE:
    PRIMES = [101]
    SEEDS = [20260717]
    N_C1 = 256
    N_SAGE = 24
    N_P2_S4 = 40
    N_P2_S5 = 8
    PROBE_ALARM_S = 20

T0 = time.time()

class SageCapTimeout(Exception):
    pass

def _alarm_handler(signum, frame):
    raise SageCapTimeout()

signal.signal(signal.SIGALRM, _alarm_handler)

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

PERMS = {k: perms_with_sign(k) for k in (2, 4, 6)}

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
    # inverse (mod p) of Vandermonde matrix V[row=xi][col=e] = xi^e, xi = 0..k-1
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
    return np.array([row[n:] for row in A], dtype=np.int64)  # (e, xi): coeffs = INV @ vals

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
    # structured Leibniz enumeration of the formal (m+ n)-Sylvester determinant.
    # rows 0..ndeg-1: shifts of f (deg mdeg); rows ndeg..: shifts of g.
    # returns dict[(fkey sorted tuple, gkey sorted tuple)] -> integer coefficient
    rows = []
    for r in range(ndeg):
        rows.append([(r + i, 0, mdeg - i) for i in range(mdeg + 1)])   # (col, which=0 f, power)
    for r in range(mdeg):
        rows.append([(r + i, 1, ndeg - i) for i in range(ndeg + 1)])   # g
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
    # coeffs (ascending, g0..g4) of Res_Z(S3(P1,P2,Z), S3(Z,P3,X)) as poly in X
    d = s3_coeffs(P1, P2, a, b, p)
    vals = []
    for xi in range(5):
        e = s3_coeffs(np.full_like(P3, xi), P3, a, b, p)  # S3(Z,P3,xi): coeffs in Z
        vals.append(det_perm(sylv_mat(d, e, p), p))
    V = np.stack(vals)                      # (5, N)
    return [ (V5INV[e, 0] * V[0] + V5INV[e, 1] * V[1] + V5INV[e, 2] * V[2]
              + V5INV[e, 3] * V[3] + V5INV[e, 4] * V[4]) % p for e in range(5) ]

def S4BXcoeffs(P1, P2, P3, a, b, p, V5INV):
    # coeffs of Res_Z(S3(X,P1,Z), S3(Z,P2,P3)) as poly in X  (balanced right side)
    d = s3_coeffs(P2, P3, a, b, p)
    vals = []
    for xi in range(5):
        e = s3_coeffs(P1, np.full_like(P1, xi), a, b, p)  # S3(xi,P1,Z): coeffs in Z
        vals.append(det_perm(sylv_mat(e, d, p), p))
    V = np.stack(vals)
    return [ (V5INV[e, 0] * V[0] + V5INV[e, 1] * V[1] + V5INV[e, 2] * V[2]
              + V5INV[e, 3] * V[3] + V5INV[e, 4] * V[4]) % p for e in range(5) ]

def S5Xcoeffs(T1, T2, T3, T4, a, b, p, V5INV, V9INV):
    # coeffs (h0..h8) of S5(X,T1..T4) = Res_Z(S3(X,T1,Z), S4(Z,T2,T3,T4)) as poly in X
    g = S4Xcoeffs(T2, T3, T4, a, b, p, V5INV)
    vals = []
    for xi in range(9):
        d = s3_coeffs(T1, np.full_like(T1, xi), a, b, p)  # S3(xi,T1,Z): coeffs in Z
        vals.append(det_perm(sylv_mat(d, g, p), p))
    V = np.stack(vals)                      # (9, N)
    return [ sum((V9INV[e, k] * V[k] for k in range(9)), np.zeros_like(V[0])) % p
             for e in range(9) ]

def monomial_products(coeffs, keys, p):
    # (N, len(keys)): prod of coeffs[pw] over each key tuple
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

# ---------------------------------------------------------------- sage independent nested-resultant path

def s3_sym(R, u, v, w, a, b):
    return ((u - v) ** 2 * w ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * w
            + (u * v - a) ** 2 - 4 * b * (u + v))

class SagePaths(object):
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b
        self.Fp = GF(p)
        self.Rzw = PolynomialRing(self.Fp, names=['Z', 'W'])
        self.Z, self.W = self.Rzw.gens()
        self.Rxz = PolynomialRing(self.Fp, names=['X', 'Z'])
        self.X, self.Z2 = self.Rxz.gens()

    def _lift_Z(self, f):
        # f in Rzw with W eliminated -> element of Rxz in Z2
        out = self.Rxz(0)
        for mono, c in f.dict().items():
            assert mono[1] == 0, "W survives in S4"
            out += c * self.Z2 ** int(mono[0])
        return out

    def s4_poly(self, t2, t3, t4):
        # S4(Z, t2, t3, t4) = Res_W(S3(Z,t2,W), S3(W,t3,t4)) as poly in Z
        f1 = s3_sym(self.Rzw, self.Z, self.Fp(t2), self.W, self.a, self.b)
        f2 = s3_sym(self.Rzw, self.W, self.Fp(t3), self.Fp(t4), self.a, self.b)
        return f1.resultant(f2, self.W)

    def s5_poly(self, t1, t2, t3, t4):
        # S5(X, t1..t4) = Res_Z(S3(X,t1,Z), S4(Z,t2,t3,t4)) as poly in X
        s4 = self._lift_Z(self.s4_poly(t2, t3, t4))
        g1 = s3_sym(self.Rxz, self.X, self.Fp(t1), self.Z2, self.a, self.b)
        return g1.resultant(s4, self.Z2)

    def s6_value(self, x1, x2, x3, x4, x5, x6):
        s5 = self.s5_poly(x3, x4, x5, x6)
        f = s3_sym(self.Rxz, self.Fp(x1), self.Fp(x2), self.X, self.a, self.b)
        return int(f.resultant(s5, self.X)) % self.p

# ---------------------------------------------------------------- extraction + self-check (C2)

log("extracting root 10x10 Sylvester structure ...")
ROOT_TERMS = extract_sylvester(2, 8)     # f = c (deg 2), g = h (deg 8)
log("root terms extracted: %d nonzero keys" % len(ROOT_TERMS))
log("extracting child 8x8 Sylvester structure ...")
CHILD_TERMS = extract_sylvester(4, 4)    # f = a (deg 4), g = b (deg 4)
log("child terms extracted: %d nonzero keys" % len(CHILD_TERMS))

CKEYS = sorted(set(k[0] for k in ROOT_TERMS))            # 45 multisets of 8 from {0,1,2}
HKEYS = sorted(set(k[1] for k in ROOT_TERMS))            # 45 pairs from {0..8}
AKEYS = sorted(set(k[0] for k in CHILD_TERMS))           # 70 multisets of 4 from {0..4}
BKEYS = sorted(set(k[1] for k in CHILD_TERMS))           # 70
assert len(CKEYS) == 45 and len(HKEYS) == 45, (len(CKEYS), len(HKEYS))
assert len(AKEYS) == 70 and len(BKEYS) == 70, (len(AKEYS), len(BKEYS))
CKIDX = {k: i for i, k in enumerate(CKEYS)}
AKIDX = {k: i for i, k in enumerate(AKEYS)}
BKIDX = {k: i for i, k in enumerate(BKEYS)}

# root sparse structure: per c-multiset M, list of ((i,j), coeff)
S_ROOT = [[] for _ in range(45)]
for (ck, hk), coeff in ROOT_TERMS.items():
    if coeff:
        S_ROOT[CKIDX[ck]].append((hk, coeff))
# child dense 70x70 integer matrix
S_CHILD = np.zeros((70, 70), dtype=np.int64)
for (ak, bk), coeff in CHILD_TERMS.items():
    S_CHILD[AKIDX[ak], BKIDX[bk]] = coeff
S_CHILD_QQ_RANK = int(matrix(QQ, [[int(v) for v in row] for row in S_CHILD]).rank())
log("child S matrix: %d nonzero entries, rank over QQ = %d" %
    (int((S_CHILD != 0).sum()), S_CHILD_QQ_RANK))

def expansion_value_root(cvals, hvals):
    # sum_M c^M sum_(hk,coeff) coeff * h^hk ; cvals = [c0,c1,c2], hvals = [h0..h8]
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
        tot += coeff * am * bm
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
log("C2 extraction self-check: root=%s child=%s pass=%s" % (C2["root"], C2["child"], C2_PASS))

extraction_fp = hashlib.sha256(
    json.dumps({"root": sorted([list(k[0]), list(k[1]), v] for k, v in ROOT_TERMS.items()),
                "child": sorted([list(k[0]), list(k[1]), v] for k, v in CHILD_TERMS.items())},
               sort_keys=True, default=lambda o: int(o)).encode()).hexdigest()

# ---------------------------------------------------------------- main cell loop

result = {
    "experiment_id": "EXP-TTN-002",
    "run_id": "RUN-TTN-002-a",
    "smoke": SMOKE,
    "parameters": {
        "primes": PRIMES, "seeds": SEEDS, "m": 6, "degree_d": 16, "tensor_side": 17,
        "points": {"root": NPTS_ROOT, "child": NPTS_CHILD, "grandchild": NPTS_GC,
                   "singlevar": NPTS_1, "C1": N_C1, "sage": N_SAGE,
                   "P2_S4": N_P2_S4, "P2_S5": N_P2_S5},
        "bonds": {"root": "{x1,x2}|{x3,x4,x5,x6}", "child": "{x1,x2,x3}|{x4,x5,x6}",
                  "grandchild": "{x1,x2,x3,x4}|{x5,x6}", "singlevar": "{x1}|rest"},
        "predictions": {"root": 45, "child_law_facevalue": 45, "child_balanced_multiset": 70,
                        "grandchild": 45, "singlevar": 17},
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
        json.dump(result, fh, indent=1)
    log("C2 failed; aborting")
    sys.exit(1)

started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

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
        U = sample(NPTS_ROOT, 2)
        V = sample(NPTS_ROOT, 4)
        cU = s3_coeffs(U[:, 0], U[:, 1], a, b, p)
        CM = monomial_products(cU, CKEYS, p)                       # (96,45)
        hV = S5Xcoeffs(V[:, 0], V[:, 1], V[:, 2], V[:, 3], a, b, p, V5INV, V9INV)
        HM = np.zeros((NPTS_ROOT, 45), dtype=np.int64)
        for mi in range(45):
            acc = np.zeros(NPTS_ROOT, dtype=np.int64)
            for (hk, coeff) in S_ROOT[mi]:
                acc = (acc + coeff * ((hV[hk[0]] * hV[hk[1]]) % p)) % p
            HM[:, mi] = acc
        E_root = (CM @ HM.T) % p
        rank_CM = sage_rank(CM, p)
        rank_HM = sage_rank(HM, p)
        rank_E_root = sage_rank(E_root, p)
        cell["root"] = {"rank_CM": rank_CM, "rank_HM": rank_HM, "rank_E": rank_E_root,
                        "certified_rank": (45 if (rank_CM == 45 and rank_HM == 45) else None)}
        log("  root: rank(CM)=%d rank(HM)=%d rank(E)=%d" % (rank_CM, rank_HM, rank_E_root))

        # ================= CHILD bond {x1,x2,x3}|{x4,x5,x6}
        U3 = sample(NPTS_CHILD, 3)
        V3 = sample(NPTS_CHILD, 3)
        aU = S4Xcoeffs(U3[:, 0], U3[:, 1], U3[:, 2], a, b, p, V5INV)
        AM = monomial_products(aU, AKEYS, p)                       # (96,70)
        bV = S4BXcoeffs(V3[:, 0], V3[:, 1], V3[:, 2], a, b, p, V5INV)
        BM = monomial_products(bV, BKEYS, p)                       # (96,70)
        E_child = ((AM @ S_CHILD_MOD) % p @ BM.T) % p
        rank_AM = sage_rank(AM, p)
        rank_BM = sage_rank(BM, p)
        rank_E_child = sage_rank(E_child, p)
        cell["child"] = {"rank_AM": rank_AM, "rank_BM": rank_BM, "rank_E": rank_E_child,
                         "rank_S_mod_p": S_child_rank_p,
                         "certified_rank": (S_child_rank_p if (rank_AM == 70 and rank_BM == 70)
                                            else None)}
        log("  child: rank(AM)=%d rank(BM)=%d rank(E)=%d rank(S)=%d" %
            (rank_AM, rank_BM, rank_E_child, S_child_rank_p))

        # ================= GRANDCHILD {x1..x4}|{x5,x6} (symmetry probe)
        U4 = sample(NPTS_GC, 4)
        V2 = sample(NPTS_GC, 2)
        # E_gc[i,j] = sum_M c^M(u_i1,u_i2) * H_M(u_i3,u_i4,v_j1,v_j2)
        cU4 = s3_coeffs(U4[:, 0], U4[:, 1], a, b, p)
        CM4 = monomial_products(cU4, CKEYS, p)                     # (64,45)
        P3a = np.repeat(U4[:, 2], NPTS_GC)
        P4a = np.repeat(U4[:, 3], NPTS_GC)
        P5a = np.tile(V2[:, 0], NPTS_GC)
        P6a = np.tile(V2[:, 1], NPTS_GC)
        hpair = S5Xcoeffs(P3a, P4a, P5a, P6a, a, b, p, V5INV, V9INV)  # lists of (64*64,)
        HMpair = np.zeros((NPTS_GC * NPTS_GC, 45), dtype=np.int64)
        for mi in range(45):
            acc = np.zeros(NPTS_GC * NPTS_GC, dtype=np.int64)
            for (hk, coeff) in S_ROOT[mi]:
                acc = (acc + coeff * ((hpair[hk[0]] * hpair[hk[1]]) % p)) % p
            HMpair[:, mi] = acc
        HMpair = HMpair.reshape(NPTS_GC, NPTS_GC, 45)
        E_gc = np.einsum('im,ijm->ij', CM4, HMpair) % p
        rank_E_gc = sage_rank(E_gc, p)
        cell["grandchild"] = {"rank_E": rank_E_gc}
        log("  grandchild: rank(E)=%d" % rank_E_gc)

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
                acc = (acc + coeff * ((hV5[hk[0]] * hV5[hk[1]]) % p)) % p
            HM1[:, mi] = acc
        E_1 = np.einsum('ijm,jm->ij', CM1, HM1) % p
        rank_E_1 = sage_rank(E_1, p)
        cell["singlevar"] = {"rank_E": rank_E_1}
        log("  singlevar: rank(E)=%d" % rank_E_1)

        # ================= P2: coefficient-path cross-checks
        rng2 = random.Random("p2-%d-%d" % (seed, p))
        T = np.array([[rng2.randrange(p) for _ in range(4)] for _ in range(N_P2_S4)], dtype=np.int64)
        g = S4Xcoeffs(T[:, 0], T[:, 1], T[:, 2], a, b, p, V5INV)
        val_interp = polyval(g, T[:, 3], p)
        dA = s3_coeffs(T[:, 0], T[:, 1], a, b, p)
        dB = s3_coeffs(T[:, 2], T[:, 3], a, b, p)
        val_direct = det_perm(sylv_mat(dA, dB, p), p)
        cell["P2_S4_path"] = bool((val_interp == val_direct).all())
        ok5 = 0
        sp = SagePaths(p, a, b)
        rng5 = random.Random("p2s5-%d-%d" % (seed, p))
        for _ in range(N_P2_S5):
            t0, t1, t2, t3, t4 = [rng5.randrange(p) for _ in range(5)]
            h = S5Xcoeffs(np.array([t1]), np.array([t2]), np.array([t3]), np.array([t4]),
                          a, b, p, V5INV, V9INV)
            v_num = int(polyval([hh for hh in h], np.array([t0]), p)[0])
            s5p = sp.s5_poly(t1, t2, t3, t4)
            v_sage = int(s5p.subs({sp.X: sp.Fp(t0)})) % p
            ok5 += (v_num == v_sage)
        cell["P2_S5_path"] = (ok5 == N_P2_S5)
        cell["P2_S5_agreements"] = ok5

        # ================= C1: three evaluation paths agree
        rngc = random.Random("c1-%d-%d" % (seed, p))
        PC = np.array([[rngc.randrange(p) for _ in range(6)] for _ in range(N_C1)], dtype=np.int64)
        # comb path
        cC = s3_coeffs(PC[:, 0], PC[:, 1], a, b, p)
        CMC = monomial_products(cC, CKEYS, p)
        hC = S5Xcoeffs(PC[:, 2], PC[:, 3], PC[:, 4], PC[:, 5], a, b, p, V5INV, V9INV)
        HMC = np.zeros((N_C1, 45), dtype=np.int64)
        for mi in range(45):
            acc = np.zeros(N_C1, dtype=np.int64)
            for (hk, coeff) in S_ROOT[mi]:
                acc = (acc + coeff * ((hC[hk[0]] * hC[hk[1]]) % p)) % p
            HMC[:, mi] = acc
        val_comb = (CMC * HMC).sum(axis=1) % p
        # balanced path
        aC = S4Xcoeffs(PC[:, 0], PC[:, 1], PC[:, 2], a, b, p, V5INV)
        AMC = monomial_products(aC, AKEYS, p)
        bC = S4BXcoeffs(PC[:, 3], PC[:, 4], PC[:, 5], a, b, p, V5INV)
        BMC = monomial_products(bC, BKEYS, p)
        val_bal = ((AMC @ S_CHILD_MOD) % p * BMC).sum(axis=1) % p
        mism_cb = int((val_comb != val_bal).sum())
        cell["C1_comb_vs_balanced"] = {"points": N_C1, "mismatches": mism_cb}
        # sage path on seeded subset
        rngs = random.Random("c1sage-%d-%d" % (seed, p))
        sage_idx = [rngs.randrange(N_C1) for _ in range(N_SAGE)]
        mism_sage = 0
        sage_examples = []
        for idx in sage_idx:
            row = PC[idx]
            v_sage = sp.s6_value(*[int(v) for v in row])
            if v_sage != int(val_comb[idx]):
                mism_sage += 1
                if len(sage_examples) < 3:
                    sage_examples.append({"point": [int(v) for v in row],
                                          "comb": int(val_comb[idx]), "sage": v_sage})
        cell["C1_comb_vs_sage"] = {"points": N_SAGE, "mismatches": mism_sage,
                                   "examples": sage_examples}
        log("  C1: comb-vs-bal %d/%d mism, comb-vs-sage %d/%d mism; P2 S4=%s S5=%d/%d" %
            (mism_cb, N_C1, mism_sage, N_SAGE, cell["P2_S4_path"], ok5, N_P2_S5))

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
summary = {
    "root_ranks_E": sorted(set(c["root"]["rank_E"] for c in cells)),
    "root_ranks_CM": sorted(set(c["root"]["rank_CM"] for c in cells)),
    "root_ranks_HM": sorted(set(c["root"]["rank_HM"] for c in cells)),
    "root_certified_45_all": all(c["root"]["certified_rank"] == 45 for c in cells),
    "child_ranks_E": sorted(set(c["child"]["rank_E"] for c in cells)),
    "child_ranks_AM": sorted(set(c["child"]["rank_AM"] for c in cells)),
    "child_ranks_BM": sorted(set(c["child"]["rank_BM"] for c in cells)),
    "child_S_rank_mod_p": sorted(set(c["child"]["rank_S_mod_p"] for c in cells)),
    "child_S_rank_QQ": S_CHILD_QQ_RANK,
    "grandchild_ranks_E": sorted(set(c["grandchild"]["rank_E"] for c in cells)),
    "singlevar_ranks_E": sorted(set(c["singlevar"]["rank_E"] for c in cells)),
    "field_independence_all_bonds": None,
    "controls": {
        "P1_S3_baseline_all": all(c["P1_S3_baseline"] for c in cells),
        "P2_S4_path_all": all(c["P2_S4_path"] for c in cells),
        "P2_S5_path_all": all(c["P2_S5_path"] for c in cells),
        "C1_comb_vs_balanced_all": all(c["C1_comb_vs_balanced"]["mismatches"] == 0 for c in cells),
        "C1_comb_vs_sage_all": all(c["C1_comb_vs_sage"]["mismatches"] == 0 for c in cells),
        "P3_CUR_exact_all": all(c["P3_CUR_exact_Eroot"] for c in cells),
        "N1_random_full_rank_all": all(c["N1_random_96_rank"] == NPTS_ROOT for c in cells),
        "N2_planted_rank45_all": all(c["N2_planted_rank45"] == 45 for c in cells),
        "C2_extraction_selfcheck": C2_PASS,
    },
    "n_cells": len(cells),
    "wall_seconds_script_preprobe": time.time() - T0,
    "sage_version": str(sage.version.version),
    "python_version": platform.python_version(),
    "numpy_version": np.__version__,
    "platform": platform.platform(),
    "started_at_utc": started_utc,
}
fi = (len(summary["root_ranks_E"]) == 1 and len(summary["child_ranks_E"]) == 1
      and len(summary["grandchild_ranks_E"]) == 1 and len(summary["singlevar_ranks_E"]) == 1
      and len(summary["root_ranks_CM"]) == 1 and len(summary["root_ranks_HM"]) == 1)
summary["field_independence_all_bonds"] = fi
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
log("WROTE %s (pre-probe) cells=%d" % (OUT_PATH, len(cells)))

# ---------------------------------------------------------------- dense symbolic S6 probe (infrastructure note only, NOT evidence)
probe = {"attempted": True, "p": 101, "seed": 20260717, "alarm_s": PROBE_ALARM_S}
try:
    pa, pb = gen_curve(101, 20260717)
    Fp101 = GF(101)
    R = PolynomialRing(Fp101, names=['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'X', 'Z', 'W'])
    x1, x2, x3, x4, x5, x6, X, Z, W = R.gens()
    tp0 = time.time()
    S4p = s3_sym(R, Z, x4, W, pa, pb).resultant(s3_sym(R, W, x5, x6, pa, pb), W)
    probe["t_S4_symbolic_s"] = time.time() - tp0
    tp1 = time.time()
    S5p = s3_sym(R, X, x3, Z, pa, pb).resultant(S4p, Z)
    probe["t_S5_symbolic_s"] = time.time() - tp1
    probe["S5_terms"] = len(S5p.monomials())
    tp2 = time.time()
    signal.alarm(PROBE_ALARM_S)
    try:
        S6p = s3_sym(R, x1, x2, X, pa, pb).resultant(S5p, X)
        signal.alarm(0)
        probe["t_S6_symbolic_s"] = time.time() - tp2
        probe["S6_terms"] = len(S6p.monomials())
        probe["status"] = "completed"
    except SageCapTimeout:
        signal.alarm(0)
        probe["status"] = "censored_infrastructure_%ds" % PROBE_ALARM_S
        probe["t_S6_symbolic_s"] = time.time() - tp2
except Exception as e:
    probe["status"] = "failed_infrastructure_exception"
    probe["exception"] = repr(e)
result["dense_S6_probe"] = probe
result["summary"]["wall_seconds_script"] = time.time() - T0
with open(OUT_PATH, "w") as fh:
    json.dump(sanitize(result), fh, indent=1)
log("WROTE %s (final); probe status=%s; total wall %.1fs" %
    (OUT_PATH, probe.get("status"), result["summary"]["wall_seconds_script"]))
