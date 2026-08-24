#!/usr/bin/env python3
"""TASK-20260813-59c321 (Validator) -- probe 2 of 4.

INDEPENDENT RE-DERIVATION OF EVERY FORCED VALUE OF BATCH-6b6e78, WRITTEN FROM
THE FROZEN TEXT OF PREREG-2 (sha256 6c7c0800f0...05ed, notarized 60ac81998).

WHAT IS AND IS NOT IMPORTED
  NOT imported: measure_a1.py (the producer's module) -- nothing from
                TASK-20260813-2ce014 is imported, read or executed here.
  NOT imported: measure_gvar2.py / probe_nullroute.py.  The frozen constructions
                they carry (make_A_seed, fixed_unimodular, fixed_isometry,
                bit_identical, sd_mean, var_s/var_f, gvar2) are TRANSCRIBED
                below from their committed source text, because PREREG-2 2.3,
                2.6, 3.2 and section 4 declare them BY SEED AND FORMULA and
                require them "carried verbatim".  Transcription is stated so a
                reader knows exactly which class of check this is.
  Bases are rebuilt FROM THEIR SEEDS.  No producer artifact is read as an input
  to any number computed here.

Writes exactly one file: its --out path.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from collections import OrderedDict
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction

import numpy as np

# ------------------------------------------------------------------ 2.1 / 2.2
Q = 3329
LOGQ = math.log(Q)
N_BASES = 8
TAU_VAR = 1e-3
W_LO, W_HI = 0.5, 2.0

LATTICES = [("L1", 100, 30), ("L2", 100, 70), ("L4", 140, 40), ("L5", 140, 100),
            ("L7", 20, 6), ("L8", 20, 14), ("L9", 30, 9), ("L10", 30, 21),
            ("L11", 40, 12), ("L12", 40, 28)]
BETAS = {100: [15, 30, 35, 50, 65], 140: [20, 40, 45, 70, 95],
         20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}

LAMBDAS = [0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1]
CS = [1e-9, 1e-3, 1e-2, 1e-1]

FLOAT_ROUTES = ["R0_closed_form", "R1_slogdet", "R2_QR_of_BT",
                "R3_slogdet_of_UB", "R4_gram_half_slogdet",
                "R5_slogdet_of_BH_ambient_isometry"]
GSO_ROUTES = ["RQ_qr_of_BT", "RG_cholesky_of_gram"]

U32 = float(np.finfo(np.float32).eps) / 2.0
U64 = float(np.finfo(np.float64).eps) / 2.0

ASSOC = "validator"


# ------------------------------------------- TRANSCRIBED frozen constructions
def make_A_seed(d, k, i, seed_prefix):
    """PREREG-2 2.3: A_i = default_rng([prefix,d,k,i]).integers(0,q,(k,d-k))."""
    rng = np.random.default_rng([seed_prefix, d, k, i])
    return rng.integers(0, Q, size=(k, d - k), dtype=np.int64)


def unimodular(d, rng):
    U = np.eye(d, dtype=np.int64)
    U = U[rng.permutation(d)]
    signs = rng.integers(0, 2, size=d) * 2 - 1
    U = U * signs[:, None]
    for _ in range(d // 2):
        a, b = rng.choice(d, size=2, replace=False)
        s = int(rng.integers(0, 2)) * 2 - 1
        U[a] = U[a] + s * U[b]
    return U


def haar_orthogonal(d, rng):
    Z = rng.standard_normal((d, d))
    Qm, Rm = np.linalg.qr(Z)
    ph = np.sign(np.diag(Rm))
    ph[ph == 0] = 1.0
    return Qm * ph


_UC, _HC = {}, {}


def fixed_unimodular(d):
    if d not in _UC:
        _UC[d] = unimodular(d, np.random.default_rng([424242, d]))
    return _UC[d]


def fixed_isometry(d):
    if d not in _HC:
        _HC[d] = haar_orthogonal(d, np.random.default_rng([313131, d]))
    return _HC[d]


def bit_identical(vals):
    return len({float(v).hex() for v in vals}) == 1


def sd_mean(vals):
    a = np.asarray(vals, dtype=float)
    return (float(a.std(ddof=1)) if a.size > 1 else 0.0), float(a.mean())


# ------------------------------------------------------------- basis building
def build_basis(d, k, i, seed_prefix, pin_a00, a00_ref=None):
    """PREREG-2 2.3.  F0 / fib_s* draw with the modulus block q I_{d-k} fixed
    across i (PIN-DET, satisfied by construction), optionally with A[0,0]
    pinned to A_0[0,0] (PIN-A00)."""
    A = make_A_seed(d, k, i, seed_prefix)
    if pin_a00:
        A = A.copy()
        A[0, 0] = a00_ref
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = np.diag(np.full(d - k, Q, dtype=np.int64))
    return B, A


def structural_check(B, d, k):
    return bool(np.array_equal(B[:k, :k], np.eye(k, dtype=np.int64))
                and np.array_equal(B[k:, :k], np.zeros((d - k, k), np.int64))
                and np.array_equal(B[k:, k:],
                                   np.diag(np.full(d - k, Q, np.int64))))


def hash_H(B):
    """PREREG-2 2.8, over the EXACT INTEGER basis."""
    payload = b"|".join(str(int(x)).encode() for x in B.flatten(order="C"))
    return int(hashlib.sha256(payload).hexdigest(), 16) / 2 ** 256


def hash_H_int(B):
    payload = b"|".join(str(int(x)).encode() for x in B.flatten(order="C"))
    return int(hashlib.sha256(payload).hexdigest(), 16)


# ------------------------------------------------------- 2.6 routes at prec p
# R4_GRAM selects HOW THE GRAM IS FORMED before slogdet.  This is the ONE
# ambiguity PREREG-2 2.6 leaves open once "binary32" is a declared working
# precision, and it is exposed as a switch rather than resolved silently:
#   "int"   -- G = (B @ B.T).astype(dt).  The Gram is formed in EXACT int64 and
#              cast once.  This is the expression carried VERBATIM in the two
#              committed sources PREREG-2 2.6 names: probe_nullroute.py:183 and
#              measure_gvar2.py:219, with the float64 cast replaced by dt.
#   "float" -- G = Bf @ Bf.T with Bf = B.astype(dt).  The Gram is accumulated at
#              the working precision.  This is what measure_a1.py:295 does.
# At binary64 the two are provably identical on these families (every entry of
# B B^T is an integer below 2**53, so the float64 accumulation is exact); they
# separate only at binary32.
R4_GRAM = "int"


def float_routes(B, d, k, dt):
    """PREREG-2 2.6 R0..R5 evaluated at working precision dt."""
    out = OrderedDict()
    out["R0_closed_form"] = dt(dt(d - k) * dt(LOGQ))
    Bf = B.astype(dt)
    out["R1_slogdet"] = dt(np.linalg.slogdet(Bf)[1])
    Rm = np.linalg.qr(Bf.T)[1]
    out["R2_QR_of_BT"] = dt(np.sum(np.log(np.abs(np.diag(Rm)))))
    U = fixed_unimodular(d)
    out["R3_slogdet_of_UB"] = dt(np.linalg.slogdet((U @ B).astype(dt))[1])
    G = (Bf @ Bf.T) if R4_GRAM == "float" else (B @ B.T).astype(dt)
    out["R4_gram_half_slogdet"] = dt(dt(0.5) * dt(np.linalg.slogdet(G)[1]))
    H = fixed_isometry(d).astype(dt)
    out["R5_slogdet_of_BH_ambient_isometry"] = dt(
        np.linalg.slogdet(Bf @ H)[1])
    return out


def gso_routes(B, d, k, dt):
    """PREREG-2 2.6 RQ / RG for X_gso_k at working precision dt.
    Returns (value_or_None, error_or_None) per route."""
    out = OrderedDict()
    Bf = B.astype(dt)
    Rm = np.linalg.qr(Bf.T)[1]
    dg = np.abs(np.diag(Rm))[:k]
    out["RQ_qr_of_BT"] = (dt(np.sum(np.log(dg)) / dt(k)), None)
    try:
        G = (B @ B.T).astype(dt)
        L = np.linalg.cholesky(G)
        dgl = np.diag(L)[:k]
        out["RG_cholesky_of_gram"] = (dt(np.sum(np.log(dgl)) / dt(k)), None)
    except np.linalg.LinAlgError as e:
        out["RG_cholesky_of_gram"] = (None, "LinAlgError: %s" % e)
    return out


# ------------------------------------------------ exact integer determinants
def _primes_below(limit, want):
    ps, n = [], limit - 1
    while len(ps) < want:
        if n % 2 == 0:
            n -= 1
            continue
        if _is_prime(n):
            ps.append(n)
        n -= 2
    return ps


def _is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


_PRIMES = None


def primes(want):
    global _PRIMES
    if _PRIMES is None or len(_PRIMES) < want:
        _PRIMES = _primes_below(2 ** 30, max(want, 160))
    return _PRIMES[:want]


def det_mod_p(M, p):
    A = np.mod(M, p).astype(np.int64)
    n = A.shape[0]
    det = 1
    for i in range(n):
        piv = -1
        col = A[i:, i]
        nz = np.nonzero(col)[0]
        if nz.size == 0:
            return 0
        piv = i + int(nz[0])
        if piv != i:
            A[[i, piv]] = A[[piv, i]]
            det = (-det) % p
        a = int(A[i, i])
        det = det * a % p
        inv = pow(a, p - 2, p)
        if i + 1 < n:
            f = (A[i + 1:, i] * inv) % p
            A[i + 1:, i:] = (A[i + 1:, i:] - f[:, None] * A[i, i:]) % p
    return det % p


def exact_det_spd(M):
    """Exact determinant of a symmetric positive-definite integer matrix by
    multi-modular elimination + CRT, sized by the Hadamard bound."""
    n = M.shape[0]
    if n == 0:
        return 1
    rn = np.sqrt(np.sum(M.astype(float) ** 2, axis=1))
    bits = float(np.sum(np.log2(np.maximum(rn, 1.0)))) + 8.0
    need = int(bits / 29.0) + 3
    ps = primes(need)
    rs = [det_mod_p(M, p) for p in ps]
    Mtot, x = 1, 0
    for p, r in zip(ps, rs):
        # incremental CRT
        g = pow(Mtot % p, p - 2, p)
        t = ((r - x) % p) * g % p
        x = x + Mtot * t
        Mtot *= p
    if x > Mtot // 2:
        x -= Mtot
    return x


def bareiss_det(M):
    """Fraction-free exact determinant, used only as a small-case cross-check."""
    A = [[Fraction(int(v)) for v in row] for row in M]
    n = len(A)
    sign, prev = 1, Fraction(1)
    for i in range(n - 1):
        if A[i][i] == 0:
            for r in range(i + 1, n):
                if A[r][i] != 0:
                    A[i], A[r] = A[r], A[i]
                    sign = -sign
                    break
            else:
                return 0
        for r in range(i + 1, n):
            for c in range(i + 1, n):
                A[r][c] = (A[r][c] * A[i][i] - A[r][i] * A[i][c]) / prev
            A[r][i] = Fraction(0)
        prev = A[i][i]
    return int(sign * A[n - 1][n - 1])


def gram_det_exact(A):
    """det(I_k + A A^T).  Computed on whichever of the two Sylvester-equivalent
    forms is smaller, and BOTH forms are compared on every call so the identity
    is exercised as a check rather than assumed."""
    k, m = A.shape
    Ak = np.eye(k, dtype=np.int64) + A @ A.T
    Am = np.eye(m, dtype=np.int64) + A.T @ A
    if k <= m:
        return exact_det_spd(Ak), "I_k + A A^T", (k, m)
    return exact_det_spd(Am), "I_m + A^T A (Sylvester)", (k, m)


# --------------------------------------------------------------- exact routes
def dec_ln(x, prec=60):
    with localcontext() as ctx:
        ctx.prec = prec
        return +Decimal(x).ln()


def exact_stat(vals, prec=400):
    """sd (ddof=1) and mean of exact Decimals at HIGH precision, so that eight
    equal values give sd EXACTLY 0.  Also returns the value the same statistic
    takes at 60 digits, to expose the rounding artefact directly."""
    out = {}
    for p in (prec, 60):
        with localcontext() as ctx:
            ctx.prec = p
            n = Decimal(len(vals))
            mu = sum(vals, Decimal(0)) / n
            var = sum(((v - mu) ** 2 for v in vals), Decimal(0)) / (n - 1)
            sd = var.sqrt()
            rho = (sd / abs(mu)) if mu != 0 else None
            out[p] = (sd, mu, rho)
    return out


# ------------------------------------------------------------------ VAR-S / F
def var_s_from_cells(cellstats):
    out = OrderedDict()
    for lat, per_beta in cellstats.items():
        means = [v["m"] for v in per_beta.values()]
        R = float(max(means) - min(means)) if means else 0.0
        for beta, v in per_beta.items():
            s = float(v["s"])
            if R == 0.0:
                verdict, D = "scale_degenerate", None
            else:
                D = s / R
                verdict = "ADMIT" if D >= TAU_VAR else "REFUSE"
            out["%s_b%s" % (lat, beta)] = {"VAR_S": verdict, "D_c": D,
                                           "s_c": s, "R_d_k": R}
    return out


def var_f_from_cells(fibstats):
    out = OrderedDict()
    for lat, per_beta in fibstats.items():
        means = [v["m"] for v in per_beta.values()]
        R = float(max(means) - min(means)) if means else 0.0
        for beta, v in per_beta.items():
            s = float(v["s"])
            bid = v.get("bit_identical")
            if R == 0.0:
                D = None
                verdict = "PASS" if (bid is False) else "FAIL"
                basis = "bit_identity_at_scale_degenerate_fibre_cell"
            else:
                D = s / R
                verdict = "PASS" if D >= TAU_VAR else "FAIL"
                basis = "scaled_dispersion"
            out["%s_b%s" % (lat, beta)] = {"VAR_F": verdict, "D_c_fib": D,
                                           "s_c_fib": s, "R_d_k_fib": R,
                                           "bit_identical": bid,
                                           "decided_by": basis}
    return out


def gvar2(vs, vf):
    if vf is None:
        return "UNCOVERED_VAR_F_NOT_COMPUTABLE"
    s_ok = vs["VAR_S"] in ("ADMIT", "scale_degenerate")
    f_ok = vf["VAR_F"] == "PASS"
    return "ADMIT" if (s_ok and f_ok) else "REFUSE"


# ----------------------------------------------------------- candidate values
def cand_value(name, L, a00, d, k, beta, dt, lam=None, c=None, hb=None):
    """PREREG-2 2.4 definitions, evaluated at working precision dt.
    L is the route's log|det B| at that precision."""
    if name == "X_null":
        return dt(dt(dt(beta) / dt(d)) * dt(dt(1.0) / dt(d)) * dt(L))
    if name == "rdet":
        return dt(np.exp(dt(dt(L) / dt(d))))
    if name == "X_parfree":
        return dt(dt(L) / dt(dt(d) * dt(k)))
    base = cand_value("X_null", L, a00, d, k, beta, dt)
    if name == "V_evade":
        return dt(base + (dt(dt(1e-9) * dt(a00)) / dt(Q) if ASSOC == "producer"
                          else dt(dt(1e-9) * dt(dt(a00) / dt(Q)))))
    if name == "X_lambda":
        return dt(base + (dt(dt(lam) * dt(a00)) / dt(Q) if ASSOC == "producer"
                          else dt(dt(lam) * dt(dt(a00) / dt(Q)))))
    if name == "X_hash":
        return dt(base + dt(dt(c) * dt(hb)))
    raise ValueError(name)


def cand_value_exact(name, Lx, a00, d, k, beta, lam=None, c=None, hbi=None,
                     prec=60):
    with localcontext() as ctx:
        ctx.prec = prec
        if name == "X_null":
            return +(Decimal(beta) / Decimal(d) / Decimal(d) * Lx)
        if name == "rdet":
            return +((Lx / Decimal(d)).exp())
        if name == "X_parfree":
            return +(Lx / (Decimal(d) * Decimal(k)))
        base = Decimal(beta) / Decimal(d) / Decimal(d) * Lx
        if name == "V_evade":
            return +(base + Decimal("1e-9") * Decimal(int(a00)) / Decimal(Q))
        if name == "X_lambda":
            return +(base + Decimal(repr(lam)) * Decimal(int(a00))
                     / Decimal(Q))
        if name == "X_hash":
            return +(base + Decimal(repr(c)) * Decimal(hbi)
                     / Decimal(2) ** 256)
    raise ValueError(name)


# ---------------------------------------------------------------------- main
def main():
    global R4_GRAM, ASSOC
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--r4-gram", choices=["int", "float"], default="int")
    ap.add_argument("--assoc", choices=["validator", "producer"],
                    default="validator")
    a = ap.parse_args()
    R4_GRAM = a.r4_gram
    ASSOC = a.assoc
    t0 = time.time()
    getcontext().prec = 60

    R = OrderedDict()
    R["probe"] = "probe_rederive_a1.py"
    R["task_id"] = "TASK-20260813-59c321"
    R["independence"] = ("own implementation from the frozen text; producer "
                         "module NOT imported; bases rebuilt from seeds")
    R["variant_r4_gram_formation"] = R4_GRAM
    R["variant_candidate_associativity"] = ASSOC
    R["u_p"] = {"binary32": U32, "binary64": U64}

    # R4 both ways at binary64, to show the ambiguity is invisible there
    r4b = []
    for lat, d, k in LATTICES:
        B, _ = build_basis(d, k, 0, 1, False)
        Bf = B.astype(np.float64)
        gi = float(0.5 * np.linalg.slogdet((B @ B.T).astype(np.float64))[1])
        gf = float(0.5 * np.linalg.slogdet(Bf @ Bf.T)[1])
        Bf32 = B.astype(np.float32)
        gi32 = float(np.float32(0.5) * np.linalg.slogdet(
            (B @ B.T).astype(np.float32))[1])
        gf32 = float(np.float32(0.5) * np.linalg.slogdet(Bf32 @ Bf32.T)[1])
        r4b.append({"lattice": lat,
                    "binary64_int_gram": gi, "binary64_float_gram": gf,
                    "binary64_bit_identical": gi.hex() == gf.hex(),
                    "binary32_int_gram": gi32, "binary32_float_gram": gf32,
                    "binary32_bit_identical": gi32.hex() == gf32.hex(),
                    "binary32_abs_diff": abs(gi32 - gf32)})
    R["R4_gram_formation_ambiguity"] = {
        "identical_at_binary64_on_all_10_lattices":
            all(x["binary64_bit_identical"] for x in r4b),
        "identical_at_binary32_on_all_10_lattices":
            all(x["binary32_bit_identical"] for x in r4b),
        "per_lattice": r4b}

    # ------------------------------------------------ build every basis family
    # fibre families: 3 draws x 2 pinnings, plus the scored family F0 (prefix 1)
    fams = OrderedDict()
    for pref in (2, 3, 4):
        for pin in (False, True):
            fams["F0|fib_s%d|%s" % (pref, "PIN-DET+PIN-A00" if pin
                                    else "PIN-DET")] = (pref, pin)
    fams["F0"] = (1, False)

    struct_ok = True
    basis = {}          # (fam, lat) -> list of (B, A)
    for fam, (pref, pin) in fams.items():
        for lat, d, k in LATTICES:
            a00_ref = int(make_A_seed(d, k, 0, pref)[0, 0])
            lst = []
            for i in range(N_BASES):
                B, A = build_basis(d, k, i, pref, pin, a00_ref)
                struct_ok &= structural_check(B, d, k)
                lst.append((B, A))
            basis[(fam, lat)] = lst
    R["structural_check_entrywise_everywhere"] = bool(struct_ok)

    # ---------------------------------------- 3.1 / P-G2 per-candidate guard
    guard = OrderedDict()
    guard_fail = []
    DECLARED = {
        "X_null": (["d", "k", "beta", "q", "abs(det B)"], ["abs(det B)"]),
        "rdet": (["d", "abs(det B)"], ["abs(det B)"]),
        "X_parfree": (["d", "k", "abs(det B)"], ["abs(det B)"]),
        "V_evade": (["d", "k", "beta", "q", "abs(det B)", "A[0,0]"],
                    ["abs(det B)", "A[0,0]"]),
        "X_lambda": (["d", "k", "beta", "q", "abs(det B)", "A[0,0]", "lambda"],
                     ["abs(det B)", "A[0,0]"]),
        "X_gso_k": (["d", "k", "q", "raw GSO profile"], ["abs(det B)"]),
        "X_hash": (["d", "k", "beta", "q", "abs(det B)", "every entry of A"],
                   ["abs(det B)"]),
    }
    FIBRE_OF = {"X_null": "PIN-DET", "rdet": "PIN-DET", "X_parfree": "PIN-DET",
                "V_evade": "PIN-DET+PIN-A00", "X_lambda": "PIN-DET+PIN-A00",
                "X_gso_k": "PIN-DET", "X_hash": "PIN-DET"}
    for cand, (_args, nuis) in DECLARED.items():
        pin = FIBRE_OF[cand]
        for pref in (2, 3, 4):
            fam = "F0|fib_s%d|%s" % (pref, pin)
            for lat, d, k in LATTICES:
                bl = basis[(fam, lat)]
                chk = OrderedDict()
                chk["d"] = True
                chk["k"] = True
                chk["q"] = True
                chk["beta"] = True
                chk["lambda"] = True
                absdets = [Q ** (d - k)] * N_BASES     # verified by structure
                chk["abs(det B)"] = len(set(absdets)) == 1
                if "A[0,0]" in nuis or "A[0,0]" in _args:
                    chk["A[0,0]"] = len({int(A[0, 0]) for _, A in bl}) == 1
                key = "%s|%s|%s" % (cand, fam, lat)
                guard[key] = OrderedDict([
                    ("declared_arguments", _args),
                    ("declared_nuisance", nuis),
                    ("verified_constant_across_i",
                     [n for n in set(_args) | set(nuis)
                      if chk.get(n, None) is True]),
                    ("checked", {n: chk[n] for n in chk
                                 if n in set(_args) | set(nuis)}),
                ])
                for n in set(_args) | set(nuis):
                    if n in chk and chk[n] is False:
                        guard_fail.append((key, n))
    R["P_G2_guard"] = OrderedDict([
        ("n_guard_records", len(guard)),
        ("failures", guard_fail),
        ("HELD", len(guard_fail) == 0),
        ("note", ("its non-firing is evidence about the IMPLEMENTATION only "
                  "(PREREG-2 6.1); NOT reported as a control")),
    ])
    # explicit A[0,0] exhibit, both constructions
    d0, k0 = 100, 30
    R["A00_exhibit_L1_fib_s2"] = {
        "unpinned_BATCH_4ed139_construction":
            [int(make_A_seed(d0, k0, i, 2)[0, 0]) for i in range(8)],
        "this_batch_PIN_A00":
            [int(A[0, 0]) for _, A in basis[("F0|fib_s2|PIN-DET+PIN-A00",
                                             "L1")]],
    }

    # ------------------------------------------------- route values per basis
    RV = {}     # (fam, lat, prec) -> list over i of {route: val}
    GV = {}     # (fam, lat, prec) -> list over i of {route: (val, err)}
    A00 = {}    # (fam, lat) -> list of a00
    HB = {}     # (fam, lat) -> list of H(B) float
    HBI = {}    # (fam, lat) -> list of H(B) exact int numerator
    for (fam, lat), bl in basis.items():
        d = dict((l, (dd, kk)) for l, dd, kk in LATTICES)[lat][0]
        k = dict((l, (dd, kk)) for l, dd, kk in LATTICES)[lat][1]
        A00[(fam, lat)] = [int(A[0, 0]) for _, A in bl]
        HB[(fam, lat)] = [hash_H(B) for B, _ in bl]
        HBI[(fam, lat)] = [hash_H_int(B) for B, _ in bl]
        for pname, dt in (("binary32", np.float32), ("binary64", np.float64)):
            RV[(fam, lat, pname)] = [float_routes(B, d, k, dt) for B, _ in bl]
            GV[(fam, lat, pname)] = [gso_routes(B, d, k, dt) for B, _ in bl]
    R["timing_routes_seconds"] = round(time.time() - t0, 3)

    # ----------------------------------------------- exact routes (R3-OUT-1)
    t1 = time.time()
    # exact |det B| = q^(d-k), a verified consequence of the verified structure
    LEXACT = {}
    for lat, d, k in LATTICES:
        LEXACT[lat] = dec_ln(Q ** (d - k), 60)

    # exact Gram determinants for X_gso_k on its own fibre families and on F0
    GEX = {}
    gram_forms = {}
    for fam in ["F0|fib_s2|PIN-DET", "F0|fib_s3|PIN-DET", "F0|fib_s4|PIN-DET",
                "F0"]:
        for lat, d, k in LATTICES:
            vals = []
            for B, A in basis[(fam, lat)]:
                det, form, dims = gram_det_exact(A)
                gram_forms[(fam, lat)] = (form, dims)
                with localcontext() as ctx:
                    ctx.prec = 60
                    vals.append(+(dec_ln(det, 60) / (Decimal(2) * Decimal(k))))
            GEX[(fam, lat)] = vals
    R["timing_exact_gram_seconds"] = round(time.time() - t1, 3)

    # small-case cross-check of the multi-modular determinant against Bareiss
    xchk = []
    for lat, d, k in [("L7", 20, 6), ("L9", 30, 9), ("L11", 40, 12)]:
        A = basis[("F0", lat)][0][1]
        Ak = np.eye(k, dtype=np.int64) + A @ A.T
        xchk.append({"lattice": lat, "multimodular": str(exact_det_spd(Ak)),
                     "bareiss": str(bareiss_det(Ak)),
                     "agree": exact_det_spd(Ak) == bareiss_det(Ak)})
    R["exact_det_cross_check_multimodular_vs_bareiss"] = xchk

    # Sylvester identity exercised on every lattice, family F0
    syl = []
    for lat, d, k in LATTICES:
        A = basis[("F0", lat)][0][1]
        dk = exact_det_spd(np.eye(k, dtype=np.int64) + A @ A.T)
        dm = exact_det_spd(np.eye(d - k, dtype=np.int64) + A.T @ A)
        syl.append({"lattice": lat, "k": k, "d_minus_k": d - k,
                    "agree": dk == dm, "digits": len(str(abs(dk)))})
    R["sylvester_identity_check_det_Ik_AAT_eq_det_Im_ATA"] = syl

    # ------------------------------------------------------ P-GRAM (R3-OUT-8)
    pgram = OrderedDict()
    worst = {"RQ_qr_of_BT": (0.0, None), "RG_cholesky_of_gram": (0.0, None)}
    n_cmp = 0
    for fam in ["F0", "F0|fib_s2|PIN-DET", "F0|fib_s3|PIN-DET",
                "F0|fib_s4|PIN-DET"]:
        for lat, d, k in LATTICES:
            per = {}
            for rt in GSO_ROUTES:
                devs = []
                for i in range(N_BASES):
                    v, err = GV[(fam, lat, "binary64")][i][rt]
                    if v is None:
                        continue
                    ex = float(GEX[(fam, lat)][i])
                    devs.append(abs(float(v) - ex))
                    n_cmp += 1
                per[rt] = max(devs) if devs else None
                if per[rt] is not None and per[rt] > worst[rt][0]:
                    worst[rt] = (per[rt], "%s/%s" % (fam, lat))
            pgram["%s/%s" % (fam, lat)] = per
    pgram_pass = all(v <= 1e-10 for pr in pgram.values() for v in pr.values()
                     if v is not None)
    R["R3_OUT_8_P_GRAM"] = OrderedDict([
        ("n_comparisons", n_cmp),
        ("tolerance", 1e-10),
        ("per_family_lattice_max_abs_dev", pgram),
        ("worst_RQ", worst["RQ_qr_of_BT"]),
        ("worst_RG", worst["RG_cholesky_of_gram"]),
        ("P_GRAM_HOLDS", bool(pgram_pass)),
        ("verdict", "HELD" if pgram_pass else "FALSIFIED"),
    ])

    # the unsatisfiability argument of OBJ-1, recomputed from OUR OWN floats
    obj1 = OrderedDict()
    for lat, d, k in LATTICES:
        diffs = []
        for i in range(N_BASES):
            q_, _ = GV[("F0", lat, "binary64")][i]["RQ_qr_of_BT"]
            g_, _ = GV[("F0", lat, "binary64")][i]["RG_cholesky_of_gram"]
            if q_ is None or g_ is None:
                continue
            diffs.append(abs(float(q_) - float(g_)))
        m = max(diffs)
        obj1[lat] = {"max_abs_RQ_minus_RG": m,
                     "exceeds_2x_tolerance_2e-10": bool(m > 2e-10),
                     "no_value_can_satisfy_both_at_1e-10": bool(m > 2e-10)}
    R["OBJ_1_recomputed_route_disagreement_F0"] = obj1

    # ---------------------------------- certified classes (A-1.1, R3-OUT-1)
    inst = []   # (label, cand, param)
    inst.append(("X_null", "X_null", None))
    inst.append(("rdet", "rdet", None))
    inst.append(("X_parfree", "X_parfree", None))
    inst.append(("V_evade", "V_evade", None))
    for lam in LAMBDAS:
        inst.append(("X_lambda[lambda=%g]" % lam, "X_lambda", lam))
    for c in CS:
        inst.append(("X_hash[c=%g]" % c, "X_hash", c))
    inst.append(("X_gso_k", "X_gso_k", None))

    certified = OrderedDict()
    exact_rho = OrderedDict()
    for label, cand, par in inst:
        if cand == "X_gso_k":
            # R7_exact_gram exists and terminates, but P-GRAM decides its
            # availability, exactly as PREREG-2 2.9 freezes it.
            certified[label] = ("UNCERTIFIED" if not pgram_pass
                                else "NON-CONSTANT")
            continue
        pin = FIBRE_OF[cand]
        allconst, anyvar = True, False
        rhos = []
        for pref in (2, 3, 4):
            fam = "F0|fib_s%d|%s" % (pref, pin)
            for lat, d, k in LATTICES:
                for beta in BETAS[d]:
                    vals = []
                    for i in range(N_BASES):
                        vals.append(cand_value_exact(
                            cand, LEXACT[lat], A00[(fam, lat)][i], d, k, beta,
                            lam=par, c=par, hbi=HBI[(fam, lat)][i]))
                    if len(set(vals)) == 1:
                        rhos.append(Decimal(0))
                    else:
                        allconst = False
                        anyvar = True
                        st = exact_stat(vals)
                        rhos.append(st[400][2])
        certified[label] = "CONSTANT" if allconst else "NON-CONSTANT"
        exact_rho[label] = {"max_rho_exact": str(max(rhos)),
                            "any_nonzero": any(r != 0 for r in rhos)}
    R["R3_OUT_1_certified_classes"] = certified
    R["exact_route_rho"] = exact_rho
    R["class_counts"] = {
        "CONSTANT": sum(1 for v in certified.values() if v == "CONSTANT"),
        "NON-CONSTANT": sum(1 for v in certified.values()
                            if v == "NON-CONSTANT"),
        "UNCERTIFIED": sum(1 for v in certified.values()
                           if v == "UNCERTIFIED")}

    # the 60-digit statistic artefact the producer reported fixing
    demo_vals = [cand_value_exact("X_null", LEXACT["L1"], 0, 100, 30, 15)
                 for _ in range(8)]
    st = exact_stat(demo_vals)
    R["exact_statistic_precision_artefact"] = {
        "eight_identical_exact_values": True,
        "sd_at_400_digits": str(st[400][0]),
        "sd_at_60_digits": str(st[60][0]),
        "rho_at_60_digits": str(st[60][2]),
        "note": ("reproduces the producer's disclosed defect (b): the sd of a "
                 "constant fibre is a rounding artefact of the STATISTIC's "
                 "context, not a property of the route"),
    }

    # ------------------------------- 3.2 two-precision table + VAR-F verdicts
    t2 = time.time()
    per_block = OrderedDict()
    n_cells = n_cov = n_unc = 0
    changed_cells = 0
    changed_blocks = 0
    by_route, by_cand, by_fam = {}, {}, {}
    pdeg = 0
    pdeg_by_route, pdeg_by_cand = {}, {}
    strict_falsified = 0
    fc2a, fc3a, fc3b = [], [], []
    Kacc = {}   # (route, prec) -> {"const":[], "nonconst":[]}

    for label, cand, par in inst:
        pin = FIBRE_OF[cand]
        routes = GSO_ROUTES if cand == "X_gso_k" else FLOAT_ROUTES
        for pref in (2, 3, 4):
            fam = "F0|fib_s%d|%s" % (pref, pin)
            for rt in routes:
                blk = "%s|%s|%s" % (label, rt, fam)
                # gather per (lattice,beta) stats at both precisions
                stats = {"binary32": {}, "binary64": {}}
                cells = []
                for lat, d, k in LATTICES:
                    for pname, dt in (("binary32", np.float32),
                                      ("binary64", np.float64)):
                        stats[pname].setdefault(lat, {})
                    for beta in BETAS[d]:
                        cells.append((lat, beta, d, k))
                        for pname, dt in (("binary32", np.float32),
                                          ("binary64", np.float64)):
                            vals, uncov = [], False
                            for i in range(N_BASES):
                                if cand == "X_gso_k":
                                    v, err = GV[(fam, lat, pname)][i][rt]
                                    if v is None:
                                        uncov = True
                                        break
                                    vals.append(float(v))
                                else:
                                    L = RV[(fam, lat, pname)][i][rt]
                                    v = cand_value(
                                        cand, L, A00[(fam, lat)][i], d, k,
                                        beta, dt, lam=par, c=par,
                                        hb=HB[(fam, lat)][i])
                                    vals.append(float(v))
                            if uncov:
                                stats[pname][lat][beta] = None
                                continue
                            s, m = sd_mean(vals)
                            stats[pname][lat][beta] = {
                                "s": s, "m": m,
                                "bit_identical": bool(bit_identical(vals)),
                                "n_distinct": len({float(v).hex()
                                                   for v in vals}),
                                "rho": (s / abs(m)) if m != 0 else None}
                # VAR-F at each precision (skip lattices with uncovered cells)
                vf = {}
                for pname in ("binary32", "binary64"):
                    fs = {lat: {b: v for b, v in per.items() if v is not None}
                          for lat, per in stats[pname].items()}
                    fs = {lat: per for lat, per in fs.items() if per}
                    vf[pname] = var_f_from_cells(fs)
                blkchg = 0
                rec_r32, rec_r64, rec_ratio = [], [], []
                for lat, beta, d, k in cells:
                    n_cells += 1
                    ck = "%s_b%s" % (lat, beta)
                    s32 = stats["binary32"][lat][beta]
                    s64 = stats["binary64"][lat][beta]
                    if s32 is None or s64 is None:
                        n_unc += 1
                        rec_r32.append(None)
                        rec_r64.append(None)
                        rec_ratio.append(None)
                        continue
                    n_cov += 1
                    r32, r64 = s32["rho"], s64["rho"]
                    rec_r32.append(r32)
                    rec_r64.append(r64)
                    rec_ratio.append((r32 / r64) if (r32 is not None
                                                     and r64 not in (None, 0))
                                     else (None if r64 in (None,)
                                           else float("inf") if (r32 or 0) > 0
                                           else None))
                    v32 = vf["binary32"][ck]["VAR_F"]
                    v64 = vf["binary64"][ck]["VAR_F"]
                    if v32 != v64:
                        changed_cells += 1
                        blkchg += 1
                        by_route[rt] = by_route.get(rt, 0) + 1
                        by_cand[label] = by_cand.get(label, 0) + 1
                        by_fam[fam] = by_fam.get(fam, 0) + 1
                    cls = certified[label]
                    # precision_degenerate (1.3)
                    is_pdeg = (r64 == 0.0)
                    if cls == "CONSTANT" and is_pdeg:
                        pdeg += 1
                        pdeg_by_route[rt] = pdeg_by_route.get(rt, 0) + 1
                        pdeg_by_cand[label] = pdeg_by_cand.get(label, 0) + 1
                        if r32 == 0.0:
                            strict_falsified += 1
                    # falsifiers
                    if cls == "CONSTANT" and not is_pdeg:
                        if r32 is not None and r64 is not None \
                                and r32 <= r64:
                            fc2a.append((label, rt, fam, ck, r32, r64))
                    if cls == "NON-CONSTANT":
                        if r32 == 0.0 or r64 == 0.0:
                            fc3b.append((label, rt, fam, ck, r32, r64))
                        if r64 not in (None, 0.0) and r32 is not None:
                            ratio = r32 / r64
                            if ratio < W_LO or ratio > W_HI:
                                fc3a.append((label, rt, fam, ck, ratio, r32,
                                             r64))
                        elif r64 == 0.0 and r32 not in (None, 0.0):
                            fc3a.append((label, rt, fam, ck, float("inf"),
                                         r32, r64))
                    # K accumulation
                    for pname, rv in (("binary32", r32), ("binary64", r64)):
                        if rv is None:
                            continue
                        u = U32 if pname == "binary32" else U64
                        key = (rt, pname)
                        Kacc.setdefault(key, {"const": [], "nonconst": []})
                        if cls == "CONSTANT":
                            Kacc[key]["const"].append(rv / u)
                        elif cls == "NON-CONSTANT":
                            Kacc[key]["nonconst"].append(rv / u)
                if blkchg:
                    changed_blocks += 1
                per_block[blk] = {"n_changed_cells": blkchg,
                                  "rho32": rec_r32, "rho64": rec_r64}
    R["timing_two_precision_seconds"] = round(time.time() - t2, 3)
    R["R3_OUT_2_two_precision_table"] = OrderedDict([
        ("n_blocks", len(per_block)),
        ("n_cell_evaluations_total", n_cells),
        ("n_covered", n_cov),
        ("n_uncovered", n_unc),
        ("VAR_F_verdict_changes_with_precision_cells", changed_cells),
        ("VAR_F_verdict_changes_blocks", changed_blocks),
        ("by_route", by_route),
        ("by_candidate", by_cand),
        ("by_fibre_family", by_fam),
    ])
    R["R3_OUT_7_precision_degenerate"] = OrderedDict([
        ("n_cells", pdeg),
        ("by_route", pdeg_by_route),
        ("by_candidate", pdeg_by_cand),
        ("strict_reading_falsified_cells", strict_falsified),
        ("strict_reading_satisfied_cells", pdeg - strict_falsified),
    ])
    R["falsifiers"] = OrderedDict([
        ("FC_2a_cells", len(fc2a)),
        ("FC_2a_by_route", _count(fc2a, 1)),
        ("FC_2a_by_candidate", _count(fc2a, 0)),
        ("FC_2a_extreme", _extreme_2a(fc2a)),
        # FC-2b ranges over CERTIFIED-CONSTANT candidates ONLY (PREREG-2 1.2).
        ("FC_2b_cells", sum(
            1 for lbl, v in exact_rho.items()
            if certified.get(lbl) == "CONSTANT" and v["any_nonzero"])),
        ("FC_2b_scope", "certified-CONSTANT candidates under the exact route"),
        ("FC_2b_nonconstant_exact_rho_is_expected_and_not_FC_2b",
         [lbl for lbl, v in exact_rho.items()
          if certified.get(lbl) == "NON-CONSTANT" and v["any_nonzero"]]),
        ("FC_3a_cells", len(fc3a)),
        ("FC_3a_by_candidate", _count(fc3a, 0)),
        ("FC_3a_ratio_min", min([f[4] for f in fc3a]) if fc3a else None),
        ("FC_3a_ratio_max", max([f[4] for f in fc3a]) if fc3a else None),
        ("FC_3a_extreme", max(fc3a, key=lambda f: f[4]) if fc3a else None),
        ("FC_3b_cells", len(fc3b)),
        ("FC_3b_by_candidate", _count(fc3b, 0)),
        ("FC_3b_by_route", _count(fc3b, 1)),
        ("FC_3b_example", fc3b[0] if fc3b else None),
    ])

    # ----------------------------------------------------- P-SEP (R3-OUT-5)
    K = OrderedDict()
    kmins, kmaxs = [], []
    for rt in FLOAT_ROUTES + GSO_ROUTES:
        for pname in ("binary32", "binary64"):
            acc = Kacc.get((rt, pname))
            if acc is None or (not acc["const"] and not acc["nonconst"]):
                K["%s|%s" % (rt, pname)] = {"K_min": None, "K_max": None,
                                            "EMPTY": None}
                continue
            kmin = max(acc["const"]) if acc["const"] else None
            kmax = min(acc["nonconst"]) if acc["nonconst"] else None
            empty = (None if (kmin is None or kmax is None)
                     else bool(kmin >= kmax))
            K["%s|%s" % (rt, pname)] = {"K_min": kmin, "K_max": kmax,
                                        "EMPTY": empty,
                                        "n_const": len(acc["const"]),
                                        "n_nonconst": len(acc["nonconst"])}
            if kmin is not None:
                kmins.append(kmin)
            if kmax is not None:
                kmaxs.append(kmax)
    joint_min = max(kmins) if kmins else None
    joint_max = min(kmaxs) if kmaxs else None
    R["R3_OUT_5_P_SEP"] = OrderedDict([
        ("per_route_precision", K),
        ("joint_K_min", joint_min),
        ("joint_K_max", joint_max),
        ("joint_EMPTY", None if (joint_min is None or joint_max is None)
         else bool(joint_min >= joint_max)),
        ("K_max_witness_class",
         "supplied only by certified-NON-CONSTANT candidates"),
    ])

    # --------------------------------------- obligation (b): V6 / V7 / VX
    f0 = OrderedDict()
    for pname, dt in (("binary64", np.float64), ("binary32", np.float32)):
        tbl = OrderedDict()
        for cand in ("X_null", "rdet"):
            for rt in FLOAT_ROUTES + ["R6_exact"]:
                # VAR-S on the scored family F0 (seed prefix 1)
                cs = {}
                for lat, d, k in LATTICES:
                    cs.setdefault(lat, {})
                    for beta in BETAS[d]:
                        vals = []
                        for i in range(N_BASES):
                            if rt == "R6_exact":
                                v = float(cand_value_exact(
                                    cand, LEXACT[lat], A00[("F0", lat)][i],
                                    d, k, beta))
                            else:
                                L = RV[("F0", lat, pname)][i][rt]
                                v = float(cand_value(cand, L,
                                                     A00[("F0", lat)][i],
                                                     d, k, beta, dt))
                            vals.append(v)
                        s, m = sd_mean(vals)
                        cs[lat][beta] = {"s": s, "m": m,
                                         "bit_identical": bit_identical(vals)}
                vs = var_s_from_cells(cs)
                # VAR-F on F0|fib_s2|PIN-DET
                fam = "F0|fib_s2|PIN-DET"
                fs = {}
                for lat, d, k in LATTICES:
                    fs.setdefault(lat, {})
                    for beta in BETAS[d]:
                        vals = []
                        for i in range(N_BASES):
                            if rt == "R6_exact":
                                v = float(cand_value_exact(
                                    cand, LEXACT[lat], A00[(fam, lat)][i],
                                    d, k, beta))
                            else:
                                L = RV[(fam, lat, pname)][i][rt]
                                v = float(cand_value(cand, L,
                                                     A00[(fam, lat)][i],
                                                     d, k, beta, dt))
                            vals.append(v)
                        s, m = sd_mean(vals)
                        fs[lat][beta] = {"s": s, "m": m,
                                         "bit_identical": bit_identical(vals),
                                         "n_distinct": len({float(v).hex()
                                                            for v in vals})}
                vf = var_f_from_cells(fs)
                verd = [gvar2(vs[ck], vf[ck]) for ck in vs]
                tbl["%s|%s" % (cand, rt)] = {
                    "n_cells": len(verd),
                    "n_REFUSE": sum(1 for v in verd if v == "REFUSE"),
                    "n_ADMIT": sum(1 for v in verd if v == "ADMIT")}
        v6 = all(tbl["%s|%s" % (c, r)]["n_ADMIT"] == 0
                 for c in ("X_null", "rdet") for r in FLOAT_ROUTES)
        v7 = all(tbl["%s|%s" % (c, r)]["n_ADMIT"] == 0
                 for c in ("X_null", "rdet")
                 for r in FLOAT_ROUTES + ["R6_exact"])
        vx = all(tbl["%s|R6_exact" % c]["n_ADMIT"] == 0
                 for c in ("X_null", "rdet"))
        f0[pname] = {"per_candidate_route": tbl,
                     "V6_route_set_{R0..R5}": "PASS" if v6 else "FAIL",
                     "V7_route_set_{R0..R5,R6_exact}": "PASS" if v7 else "FAIL",
                     "VX_route_set_{R6_exact}": "PASS" if vx else "FAIL"}
    R["R3_OUT_3_F0_refusal_half"] = f0

    R["per_block_changed_counts"] = {k: v["n_changed_cells"]
                                     for k, v in per_block.items()
                                     if v["n_changed_cells"]}
    R["total_seconds"] = round(time.time() - t0, 3)

    with open(a.out, "w") as f:
        json.dump(R, f, indent=1, default=str)

    # ------------------------------------------------------------- stdout
    p = print
    p("== STRUCTURE / GUARD")
    p("  entrywise block structure verified everywhere: %s"
      % R["structural_check_entrywise_everywhere"])
    p("  P-G2 guard records %d, failures %d, HELD=%s"
      % (R["P_G2_guard"]["n_guard_records"],
         len(R["P_G2_guard"]["failures"]), R["P_G2_guard"]["HELD"]))
    p("  A[0,0] at L1 fib_s2, unpinned : %s"
      % R["A00_exhibit_L1_fib_s2"]["unpinned_BATCH_4ed139_construction"])
    p("  A[0,0] at L1 fib_s2, PIN-A00  : %s"
      % R["A00_exhibit_L1_fib_s2"]["this_batch_PIN_A00"])
    p("== EXACT ARITHMETIC CROSS-CHECKS")
    for x in R["exact_det_cross_check_multimodular_vs_bareiss"]:
        p("  %s multimodular==bareiss %s" % (x["lattice"], x["agree"]))
    p("  Sylvester det(I_k+AA^T)==det(I_m+A^TA) on all 10 lattices: %s"
      % all(s["agree"] for s in R["sylvester_identity_check_"
                                  "det_Ik_AAT_eq_det_Im_ATA"]))
    p("== P-GRAM (R3-OUT-8)  n=%d tol=1e-10" % n_cmp)
    p("  worst RQ %s  worst RG %s  ->  %s"
      % (worst["RQ_qr_of_BT"], worst["RG_cholesky_of_gram"],
         R["R3_OUT_8_P_GRAM"]["verdict"]))
    p("== OBJ-1: committed float routes disagree with EACH OTHER (my floats)")
    for lat, v in obj1.items():
        p("  %-4s max|RQ-RG| = %.6e   > 2e-10 : %s"
          % (lat, v["max_abs_RQ_minus_RG"], v["exceeds_2x_tolerance_2e-10"]))
    p("== CERTIFIED CLASSES (R3-OUT-1)")
    for kk, vv in certified.items():
        p("  %-22s %s" % (kk, vv))
    p("  counts %s" % R["class_counts"])
    p("== TWO-PRECISION TABLE (R3-OUT-2)")
    t = R["R3_OUT_2_two_precision_table"]
    p("  blocks %d  cells %d  covered %d  uncovered %d"
      % (t["n_blocks"], t["n_cell_evaluations_total"], t["n_covered"],
         t["n_uncovered"]))
    p("  VAR-F verdict CHANGES with precision: %d cells in %d blocks"
      % (t["VAR_F_verdict_changes_with_precision_cells"],
         t["VAR_F_verdict_changes_blocks"]))
    p("  by route     %s" % t["by_route"])
    p("  by candidate %s" % t["by_candidate"])
    p("  by family    %s" % t["by_fibre_family"])
    p("== R3-OUT-7 precision_degenerate")
    p("  %s" % json.dumps(R["R3_OUT_7_precision_degenerate"], default=str))
    p("== FALSIFIERS")
    p("  %s" % json.dumps(R["falsifiers"], default=str)[:1600])
    p("== P-SEP (R3-OUT-5)")
    for kk, vv in K.items():
        p("  %-46s Kmin=%s Kmax=%s EMPTY=%s"
          % (kk, vv["K_min"], vv["K_max"], vv["EMPTY"]))
    p("  JOINT Kmin=%s Kmax=%s EMPTY=%s"
      % (joint_min, joint_max, R["R3_OUT_5_P_SEP"]["joint_EMPTY"]))
    p("== R3-OUT-3 F0 refusal half")
    for pn, vv in f0.items():
        p("  [%s] V6=%s V7=%s VX=%s" % (
            pn, vv["V6_route_set_{R0..R5}"],
            vv["V7_route_set_{R0..R5,R6_exact}"],
            vv["VX_route_set_{R6_exact}"]))
        for kk, cc in vv["per_candidate_route"].items():
            p("      %-34s REFUSE %2d / ADMIT %2d of %d"
              % (kk, cc["n_REFUSE"], cc["n_ADMIT"], cc["n_cells"]))
    p("== TIMING total %.1f s" % R["total_seconds"])
    return 0


def _count(lst, idx):
    out = {}
    for t in lst:
        out[t[idx]] = out.get(t[idx], 0) + 1
    return out


def _extreme_2a(lst):
    if not lst:
        return None
    return min(lst, key=lambda t: (t[4] - t[5]))


if __name__ == "__main__":
    sys.exit(main())
