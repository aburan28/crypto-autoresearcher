#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-1 -- THE DIAGNOSTIC MEASUREMENT THAT SCORES THE FIVE FALSIFIERS.

TASK-20260813-2ce014 / BATCH-6b6e78 / GOAL-MLKEM-005.  Role: executor (LEAD).
CLAIM TIER TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model.

WHAT THIS IS.  An implementation of PREREG-2
(tasks/TASK-20260813-25cb95/prereg.md, notarized at 60ac81998, sha256
6c7c0800f0fdd94f62443262e5283aadc2149bad97d377634581d7aceba405ed) exactly as
frozen: the numbered assumption A-1 and its five falsifiers FC-1, FC-2a, FC-2b,
FC-3a, FC-3b (section 1.2), the precision_degenerate rule with BOTH readings
(1.3), the frozen objects and PER-CANDIDATE declared argument sets (2), the
DERIVED exact route R7_exact_gram for X_gso_k and its P-GRAM check (2.9), the
diagnostic (3), the K-interval computation P-SEP (3.5), the X_hash calibration
(3.6), obligation (b)'s three frozen readings V6 / V7 / VX (4), the prediction
register (5), the must-pass guard P-G2 (6.1) and the outcome rows (8).

THE FROZEN TEXT IS NOT AMENDED HERE.  Where this producer believes a clause is
wrong, THE CLAUSE IS IMPLEMENTED AS WRITTEN and the objection is recorded in
report_a1.md.  In particular P-GRAM is applied exactly as frozen, including
against route RG, and the derivation of PREREG-2 2.9 is NOT patched and NO
substitute route is introduced.

THIS SCRIPT SPECIFIES NO CRITERION.  It computes statistics and scores the
frozen falsifiers.  It proposes no threshold, no gate, no K and no replacement
fibre clause.  It declares no hypothesis supported or refuted.

PROVENANCE.  The committed lead measurement measure_gvar2.py (BATCH-4ed139) is
IMPORTED, not transcribed: its Q, N_BASES, TAU_VAR, LATTICES, BETA_GRID,
FAMILIES, make_A_seed, moduli, build_basis_fam, structural_check_and_exact_absdet,
bit_identical, sd_mean, var_s_from_cells, var_f_from_cells and gvar2 are used
directly, as are probe_nullroute.py's fixed_unimodular and fixed_isometry
through it.  The committed rider measurement measure_falserefusal.py is
IMPORTED for its x_gso_k_RQ and x_gso_k_RG route definitions.  No committed file
is modified and no main() of a committed file is called.

RE-EXECUTABLE from the repository root:
    PYTHONDONTWRITEBYTECODE=1 python3 -B <this file> --out results_a1.json

WRITES exactly one file: the --out path.  No git write, no commit.
"""

import argparse
import decimal
import hashlib
import importlib.util
import json
import math
import os
import platform
import subprocess
import sys
import time
from collections import OrderedDict

sys.dont_write_bytecode = True

import numpy as np

T0 = time.time()

TASK_ID = "TASK-20260813-2ce014"
BATCH_ID = "BATCH-6b6e78"
GOAL_ID = "GOAL-MLKEM-005"
NOTARIZING_COMMIT = "60ac81998"
DEC_PREC = 60                     # PREREG-2 2.6 / 2.9: decimal, 60 sig digits
DEC_STAT_PREC = 240               # the sd/mean OF those exact values (see below)
R7_CAP_SECONDS_PER_LATTICE = 45.0  # PREREG-2 2.9, d in {100, 140}
MEASUREMENT_CAP_SECONDS = 600.0    # task card / handoff hard cap
W_WINDOW = 2.0                     # PREREG-2 2.1: the FC-3a window factor


# --------------------------------------------------------------- repo plumbing
def _repo_root():
    env = os.environ.get("A1_REPO_ROOT")
    if env:
        return os.path.abspath(env)
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        return subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return os.path.abspath(".")


REPO = _repo_root()
G5 = "coordination/goals/GOAL-MLKEM-005"
P_PREREG2 = os.path.join(REPO, G5, "batches/BATCH-6b6e78/tasks/"
                                   "TASK-20260813-25cb95/prereg.md")
P_MG = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                              "TASK-20260812-56b9da/measure_gvar2.py")
P_MF = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                              "TASK-20260812-4b8ede/measure_falserefusal.py")
P_FR = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                              "TASK-20260812-4b8ede/results_falserefusal.json")
P_GVAR2_OUT = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                                     "TASK-20260812-56b9da/results_gvar2.json")
P_PROBE_PN = os.path.join(REPO, G5, "batches/BATCH-4ed139/reviews/"
                                    "TASK-20260812-696cd4/probes/"
                                    "probe_precision_null.py")
P_PROBE_PN_OUT = os.path.join(REPO, G5, "batches/BATCH-4ed139/reviews/"
                                        "TASK-20260812-696cd4/probes/"
                                        "probe_precision_null_output.json")
P_PROBE_ARGSET = os.path.join(REPO, G5, "batches/BATCH-4ed139/reviews/"
                                        "TASK-20260812-696cd4/probes/"
                                        "probe_argset.py")
P_PREREG1 = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                                   "TASK-20260812-34b86c/prereg.md")
P_PROBE_NULLROUTE = os.path.join(REPO, G5, "batches/BATCH-9e3584/reviews/"
                                           "TASK-20260809-444fe7/probes/"
                                           "probe_nullroute.py")

INPUT_FILES = OrderedDict([
    ("prereg2 (PREREG-2, frozen)", P_PREREG2),
    ("prereg1 (PREREG-1, frozen)", P_PREREG1),
    ("measure_gvar2.py (committed lead, BATCH-4ed139)", P_MG),
    ("results_gvar2.json (committed lead, BATCH-4ed139)", P_GVAR2_OUT),
    ("measure_falserefusal.py (committed rider ii, BATCH-4ed139)", P_MF),
    ("results_falserefusal.json (committed rider ii, BATCH-4ed139)", P_FR),
    ("probe_precision_null.py (committed red team, BATCH-4ed139)", P_PROBE_PN),
    ("probe_precision_null_output.json (committed red team)", P_PROBE_PN_OUT),
    ("probe_argset.py (committed red team, BATCH-4ed139)", P_PROBE_ARGSET),
    ("probe_nullroute.py (committed, BATCH-9e3584)", P_PROBE_NULLROUTE),
])


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)          # module level only; main() NOT called
    return mod


MG = load_module(P_MG, "committed_measure_gvar2")
MF = load_module(P_MF, "committed_measure_falserefusal")

Q = MG.Q
N_BASES = MG.N_BASES
TAU_VAR = MG.TAU_VAR
LATTICES = MG.LATTICES
BETA_GRID = MG.BETA_GRID
bit_identical = MG.bit_identical
sd_mean = MG.sd_mean
var_s_from_cells = MG.var_s_from_cells
var_f_from_cells = MG.var_f_from_cells
gvar2 = MG.gvar2
PROBE_N = MG.PROBE_N

# PREREG-2 2.6 -- the six declared float routes, carried through measure_gvar2
ROUTES6 = list(MG.ROUTES6)
ROUTES_GSO = ["RQ_qr_of_BT", "RG_cholesky_of_gram"]
PRECISIONS = OrderedDict([("binary32", np.float32), ("binary64", np.float64)])
UNIT_ROUNDOFF = {"binary32": float(np.finfo(np.float32).eps) / 2.0,
                 "binary64": float(np.finfo(np.float64).eps) / 2.0}

# PREREG-2 2.7 -- the frozen grids
LAMBDA_GRID = [0.0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1.0]
C_GRID = [1e-9, 1e-3, 1e-2, 1e-1]

# PREREG-2 2.3 -- the three fibre draws and the two frozen pinnings
DRAWS = OrderedDict([("fib_s2", 2), ("fib_s3", 3), ("fib_s4", 4)])
PIN_DET = "PIN-DET"
PIN_DET_A00 = "PIN-DET+PIN-A00"


def fibre_family_label(draw, pin):
    return "F0|%s|%s" % (draw, pin)


# PREREG-2 2.4 -- the in-scope candidates and their DECLARED ARGUMENT SETS.
# `declared_arguments` and `nuisance` are transcribed from the frozen table;
# `pin` is the fibre family the frozen table assigns to that candidate.
CANDIDATE_SPECS = OrderedDict([
    ("X_null", dict(
        definition="(beta/d)(1/d) log abs(det B)",
        declared_arguments=["d", "k", "beta", "q", "abs(det B)"],
        nuisance=["abs(det B)"], pin=PIN_DET, routes=ROUTES6,
        exact_route="R6_exact", expected_exact_class="CONSTANT", param=None)),
    ("rdet", dict(
        definition="exp(log abs(det B) / d)",
        declared_arguments=["d", "abs(det B)"],
        nuisance=["abs(det B)"], pin=PIN_DET, routes=ROUTES6,
        exact_route="R6_exact", expected_exact_class="CONSTANT", param=None)),
    ("X_parfree", dict(
        definition="log abs(det B) / (d*k)",
        declared_arguments=["d", "k", "abs(det B)"],
        nuisance=["abs(det B)"], pin=PIN_DET, routes=ROUTES6,
        exact_route="R6_exact", expected_exact_class="CONSTANT", param=None)),
    ("V_evade", dict(
        definition="X_null + 1e-9 * A[0,0]/q",
        declared_arguments=["d", "k", "beta", "q", "abs(det B)", "A[0,0]"],
        nuisance=["abs(det B)", "A[0,0]"], pin=PIN_DET_A00, routes=ROUTES6,
        exact_route="R6_exact", expected_exact_class="CONSTANT", param=None)),
    ("X_lambda", dict(
        definition="X_null + lambda * A[0,0]/q",
        declared_arguments=["d", "k", "beta", "q", "abs(det B)", "A[0,0]",
                            "lambda"],
        nuisance=["abs(det B)", "A[0,0]"], pin=PIN_DET_A00, routes=ROUTES6,
        exact_route="R6_exact", expected_exact_class="CONSTANT",
        param=("lambda", LAMBDA_GRID))),
    ("X_gso_k", dict(
        definition="(1/k) sum_{j=1..k} log norm(b*_j) of the RAW basis",
        declared_arguments=["d", "k", "q", "raw GSO profile"],
        nuisance=["abs(det B)"], pin=PIN_DET, routes=ROUTES_GSO,
        exact_route="R7_exact_gram", expected_exact_class="NON-CONSTANT",
        param=None)),
    ("X_hash", dict(
        definition="X_null + c * H(B), H per PREREG-2 2.8",
        declared_arguments=["d", "k", "beta", "q", "abs(det B)",
                            "every entry of A"],
        nuisance=["abs(det B)"], pin=PIN_DET, routes=ROUTES6,
        exact_route="R6_exact", expected_exact_class="NON-CONSTANT",
        param=("c", C_GRID))),
])


def candidate_keys():
    """(key, base_candidate, param_value) for every scored candidate instance."""
    out = []
    for name, spec in CANDIDATE_SPECS.items():
        if spec["param"] is None:
            out.append((name, name, None))
        else:
            pname, grid = spec["param"]
            for v in grid:
                out.append(("%s[%s=%s]" % (name, pname, repr(v)), name, v))
    return out


# ------------------------------------------------------- basis / fibre builder
def build_A(d, k, i, seed_prefix, pin):
    """PREREG-2 2.3.  PIN-DET is the declared draw itself (modulus block held
    fixed across i, so |det B_i| = q^(d-k) by construction).  PIN-A00
    additionally sets A'_i[0,0] = A'_0[0,0] for every i, leaving every other
    entry of A' and |det B_i| untouched."""
    A = MG.make_A_seed(d, k, Q, i, seed_prefix).copy()
    if pin == PIN_DET_A00:
        A[0, 0] = MG.make_A_seed(d, k, Q, 0, seed_prefix)[0, 0]
    return A


def build_basis(d, k, i, seed_prefix, pin):
    A = build_A(d, k, i, seed_prefix, pin)
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = np.diag(MG.moduli(d, k, i, "const_q"))
    return B, A


def hash_H_int(B):
    """PREREG-2 2.8, frozen to the bit.  Returns the INTEGER numerator; the
    value H(B) is that integer divided by 2**256, taken exactly in `decimal`
    for the exact route and in the working precision for the float routes."""
    payload = b"|".join(str(int(x)).encode() for x in B.flatten(order="C"))
    return int(hashlib.sha256(payload).hexdigest(), 16)


# ------------------------------------------------------------- float routes
def logdet_routes_prec(B, d, k, dt):
    """PREREG-2 2.6 routes R0..R5 evaluated at working precision `dt`.  The
    expressions are the committed measure_gvar2.logdet_routes_fam ones with the
    float64 cast replaced by a cast to `dt`; R0 is this family's exact closed
    form (d-k) log q, evaluated in `dt`."""
    out = OrderedDict()
    err = OrderedDict()

    def _try(name, fn):
        try:
            out[name] = float(fn())
        except Exception as e:
            err[name] = "%s: %s" % (e.__class__.__name__, e)

    _try("R0_closed_form", lambda: dt(d - k) * np.log(dt(Q)))
    Bf = B.astype(dt)
    _try("R1_slogdet", lambda: np.linalg.slogdet(Bf)[1])
    _try("R2_QR_of_BT",
         lambda: np.sum(np.log(np.abs(np.diag(np.linalg.qr(Bf.T)[1])))))
    U = PROBE_N.fixed_unimodular(d)
    _try("R3_slogdet_of_UB",
         lambda: np.linalg.slogdet((U @ B).astype(dt))[1])
    _try("R4_gram_half_slogdet",
         lambda: dt(0.5) * np.linalg.slogdet(Bf @ Bf.T)[1])
    H = PROBE_N.fixed_isometry(d).astype(dt)
    _try("R5_slogdet_of_BH_ambient_isometry",
         lambda: np.linalg.slogdet(Bf @ H)[1])
    return out, err


def gso_routes_prec(B, k, dt):
    """PREREG-2 2.6 routes RQ and RG for X_gso_k, at working precision `dt`.
    The expressions are the committed measure_falserefusal.x_gso_k_RQ /
    x_gso_k_RG with the float64 cast replaced by a cast to `dt`."""
    out, err = OrderedDict(), OrderedDict()
    try:
        _, Rm = np.linalg.qr(B.astype(dt).T)
        dg = np.abs(np.diag(Rm))[:k]
        out["RQ_qr_of_BT"] = float(np.mean(np.log(dg)))
    except Exception as e:
        err["RQ_qr_of_BT"] = "%s: %s" % (e.__class__.__name__, e)
    try:
        G = (B.astype(np.int64) @ B.astype(np.int64).T).astype(dt)
        L = np.linalg.cholesky(G)
        dg = np.abs(np.diag(L))[:k]
        out["RG_cholesky_of_gram"] = float(np.mean(np.log(dg)))
    except Exception as e:
        err["RG_cholesky_of_gram"] = "%s: %s" % (e.__class__.__name__, e)
    return out, err


def cand_value_prec(base, ld, a00, hnum, d, k, beta, dt, param):
    """The candidate observable at working precision `dt` from the route's
    log abs(det B) value `ld` (itself computed at `dt`)."""
    ldt = dt(ld)
    xn = (dt(beta) / dt(d)) * (dt(1.0) / dt(d)) * ldt
    if base == "X_null":
        return float(xn)
    if base == "rdet":
        return float(np.exp(ldt / dt(d)))
    if base == "X_parfree":
        return float(ldt / (dt(d) * dt(k)))
    if base == "V_evade":
        return float(xn + dt(1e-9) * dt(a00) / dt(Q))
    if base == "X_lambda":
        return float(xn + dt(param) * dt(a00) / dt(Q))
    if base == "X_hash":
        return float(xn + dt(param) * dt(hnum / float(1 << 256)))
    raise KeyError(base)


# ------------------------------------------------------------- exact routes
def exact_logabsdet(absdet):
    with decimal.localcontext() as ctx:
        ctx.prec = DEC_PREC
        return decimal.Decimal(absdet).ln()


def cand_value_exact(base, logabsdet, a00, hnum, d, k, beta, param):
    """R6_exact (PREREG-2 2.6): the candidate from the EXACT integer
    determinant through `decimal` at 60 significant digits.  No float
    representation of the determinant is read anywhere."""
    with decimal.localcontext() as ctx:
        ctx.prec = DEC_PREC
        D = decimal.Decimal
        xn = (D(beta) / D(d)) * (D(1) / D(d)) * logabsdet
        if base == "X_null":
            return +xn
        if base == "rdet":
            return (logabsdet / D(d)).exp()
        if base == "X_parfree":
            return logabsdet / (D(d) * D(k))
        if base == "V_evade":
            return xn + D("1e-9") * D(a00) / D(Q)
        if base == "X_lambda":
            return xn + D(repr(param)) * D(a00) / D(Q)
        if base == "X_hash":
            return xn + D(repr(param)) * (D(hnum) / D(1 << 256))
        raise KeyError(base)


_PRIME_CURSOR = [(1 << 30) - 1]
_PRIMES = []


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


def primes_needed(n):
    """n DISTINCT primes just below 2^30, generated once and cached.  The search
    cursor is global, so a later call never re-emits an earlier prime."""
    while len(_PRIMES) < n:
        c = _PRIME_CURSOR[0]
        while not _is_prime(c):
            c -= 2
        _PRIMES.append(c)
        _PRIME_CURSOR[0] = c - 2
    return _PRIMES[:n]


def _det_mod_p(M, p):
    M = np.mod(M, p).astype(np.int64)
    n = M.shape[0]
    det = 1
    for c in range(n):
        piv = -1
        for r in range(c, n):
            if M[r, c]:
                piv = r
                break
        if piv < 0:
            return 0
        if piv != c:
            M[[c, piv]] = M[[piv, c]]
            det = (-det) % p
        pv = int(M[c, c])
        det = det * pv % p
        inv = pow(pv, p - 2, p)
        col = M[c + 1:, c]
        if col.size:
            f = (col * inv) % p
            M[c + 1:, c:] = (M[c + 1:, c:] - f[:, None] * M[c, c:][None, :]) % p
    return det


def exact_gram_det(A):
    """det(I_k + A A^T) as an EXACT Python integer, by multi-modular
    elimination over distinct 30-bit primes with CRT, sized by the Hadamard
    bound of the actual matrix.  Fraction-free / exact throughout; no float
    representation of the Gram determinant is read anywhere (the float array is
    used ONLY to size the prime set)."""
    k = A.shape[0]
    Ao = A.astype(object)
    Gobj = Ao @ Ao.T + np.eye(k, dtype=np.int64).astype(object)
    Gf = np.array([[float(x) for x in row] for row in Gobj], dtype=np.float64)
    logb = float(np.sum(0.5 * np.log(np.sum(Gf * Gf, axis=1))))
    nbits = logb / math.log(2.0) + 8.0
    nprimes = max(1, int(nbits / 29.0) + 1)
    ps = primes_needed(nprimes)
    res, M = 0, 1
    for p in ps:
        Mp = np.array([[int(x) % p for x in row] for row in Gobj],
                      dtype=np.int64)
        dp = _det_mod_p(Mp, p)
        if M == 1:
            res, M = dp % p, p
        else:
            t = ((dp - res) % p) * pow(M % p, p - 2, p) % p
            res = res + M * t
            M *= p
    return res, nprimes


def x_gso_k_exact(A, k):
    """R7_exact_gram, PREREG-2 2.9 (the Coordinator's own derivation, quoted):
        X_gso_k = (1/(2k)) * log det(I_k + A A^T).
    det by exact integer arithmetic; the logarithm through `decimal` at 60
    significant digits."""
    det, nprimes = exact_gram_det(A)
    with decimal.localcontext() as ctx:
        ctx.prec = DEC_PREC
        return decimal.Decimal(det).ln() / (2 * k), det, nprimes


# --------------------------------------------------------------- statistics
def dec_sd_mean(vals):
    """sd (ddof = 1) and mean of exact Decimal values, in Decimal.

    The STATISTIC is taken at 4x the route's declared 60 significant digits so
    that the mean and the deviations of eight EQUAL exact values are exact and
    the sd of a constant fibre is EXACTLY 0.  FC-2b is an existence test with
    no threshold, so a rounding residue in the statistic would fire it
    spuriously; at DEC_STAT_PREC digits the sum of eight <=60-digit values and
    its division by 8 are both exact.  This raises the precision of the
    STATISTIC only and does not change the declared route precision."""
    with decimal.localcontext() as ctx:
        ctx.prec = DEC_STAT_PREC
        n = len(vals)
        m = sum(vals) / n
        if n < 2:
            return decimal.Decimal(0), m
        var = sum((v - m) ** 2 for v in vals) / (n - 1)
        return var.sqrt(), m


def rho_of(s, m):
    return (float(s) / abs(float(m))) if float(m) != 0.0 else None


def n_distinct(vals):
    return len({float(v).hex() for v in vals})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["task_id"] = TASK_ID
    R["batch_id"] = BATCH_ID
    R["goal_id"] = GOAL_ID
    R["role"] = "executor"
    R["object"] = ("A-1, the finite-precision fibre assumption, as frozen by "
                   "PREREG-2 section 1, and its five falsifiers FC-1, FC-2a, "
                   "FC-2b, FC-3a, FC-3b")
    R["claim_tier"] = "toy"
    R["status_of_this_measurement"] = (
        "PRODUCER MEASUREMENT under the frozen PREREG-2. OBSERVATIONS ONLY. It "
        "declares no hypothesis supported or refuted, validates no heuristic, "
        "specifies no dispersion criterion, fibre clause, gate, threshold or K, "
        "and changes no research status. It rescores no frozen verdict of any "
        "prior batch: BATCH-4ed139's F0 verdict is immutable and section 4 "
        "below is A NEW MEASUREMENT IN THIS BATCH, not a rescoring of it. "
        "CLAIM TIER TOY: nothing here bears on ML-KEM security, any FIPS 203 "
        "parameter set, any attack cost or any cost model.")
    R["certificate"] = {
        "kind": "none",
        "reason": "pure measurement run: no discrete-log solve and no "
                  "factor-base relation is claimed or produced. The run's own "
                  "internal re-verifications (block-structure check, exact "
                  "integer determinant guard, P-GRAM, import agreement) are "
                  "INSTRUMENT CHECKS, not certificates."}
    R["environment"] = {
        "python": platform.python_version(), "numpy": np.__version__,
        "platform": platform.platform(), "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "thread_caps_in_force": {v: os.environ.get(v) for v in
                                 ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                  "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                                  "VECLIB_MAXIMUM_THREADS")}}
    try:
        import fpylll                                            # noqa: F401
        R["environment"]["fpylll"] = fpylll.__version__
    except Exception as e:
        R["environment"]["fpylll"] = (
            "ABSENT (%s). NOT USED AND NOT NEEDED: this batch performs NO "
            "reduction of any kind (PREREG-2 11) and every route here is "
            "reduction-free." % e.__class__.__name__)
    try:
        R["git_revision"] = subprocess.run(
            ["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True,
            text=True, check=True).stdout.strip()
        R["git_dirty_paths"] = subprocess.run(
            ["git", "-C", REPO, "status", "--porcelain"], capture_output=True,
            text=True, check=True).stdout.strip().splitlines()
    except Exception as e:
        R["git_revision"] = "UNAVAILABLE: %s" % e
        R["git_dirty_paths"] = None

    # ---- the notarized contract, VERIFIED rather than asserted
    pv = OrderedDict()
    rel = os.path.relpath(P_PREREG2, REPO)
    try:
        pv["sha256_working_tree"] = sha256_file(P_PREREG2)
        side = os.path.join(os.path.dirname(P_PREREG2), "prereg_sha256.txt")
        pv["sidecar_text"] = (open(side).read().strip()
                              if os.path.exists(side) else None)
        blob = subprocess.run(["git", "-C", REPO, "show",
                               "%s:%s" % (NOTARIZING_COMMIT, rel)],
                              capture_output=True, check=True).stdout
        pv["sha256_notarized_blob"] = hashlib.sha256(blob).hexdigest()
        pv["working_tree_equals_notarized_blob"] = (
            pv["sha256_working_tree"] == pv["sha256_notarized_blob"])
        pv["notarizing_commit"] = subprocess.run(
            ["git", "-C", REPO, "rev-parse", NOTARIZING_COMMIT],
            capture_output=True, text=True, check=True).stdout.strip()
        pv["is_ancestor_of_HEAD"] = subprocess.run(
            ["git", "-C", REPO, "merge-base", "--is-ancestor",
             NOTARIZING_COMMIT, "HEAD"], capture_output=True).returncode == 0
        pv["files_changed_by_the_notarizing_commit"] = subprocess.run(
            ["git", "-C", REPO, "show", "--name-only", "--format=",
             NOTARIZING_COMMIT], capture_output=True, text=True,
            check=True).stdout.strip().splitlines()
    except Exception as e:
        pv["ERROR"] = "%s: %s" % (e.__class__.__name__, e)
    R["prereg_verification"] = pv
    R["inputs_sha256"] = OrderedDict(
        (k, sha256_file(v)) for k, v in INPUT_FILES.items())
    R["input_paths"] = OrderedDict(
        (k, os.path.relpath(v, REPO)) for k, v in INPUT_FILES.items())
    R["frozen_constants"] = {
        "q": Q, "N_BASES": N_BASES, "tau_var": TAU_VAR, "W_FC3a_window": W_WINDOW,
        "lambda_grid": LAMBDA_GRID, "c_grid": C_GRID,
        "decimal_significant_digits": DEC_PREC,
        "implementation_statistic_significant_digits_NOT_A_FROZEN_CONSTANT":
            DEC_STAT_PREC,
        "declared_precisions": list(PRECISIONS),
        "unit_roundoff_u_p": UNIT_ROUNDOFF,
        "R7_cap_seconds_per_lattice_at_d_in_100_140":
            R7_CAP_SECONDS_PER_LATTICE}
    R["seeds"] = {
        "A_draws": "np.random.default_rng([seed_prefix, d, k, i]).integers"
                   "(0, q, size=(k, d-k)) via the IMPORTED committed "
                   "measure_gvar2.make_A_seed; seed_prefix 1 = F0 (the scored "
                   "family), 2 / 3 / 4 = the three declared fibre draws "
                   "fib_s2 / fib_s3 / fib_s4",
        "fixed_unimodular_U": "np.random.default_rng([424242, d]) via the "
                              "IMPORTED probe_nullroute.fixed_unimodular",
        "fixed_isometry_H": "np.random.default_rng([313131, d]) via the "
                            "IMPORTED probe_nullroute.fixed_isometry",
        "H(B) hash": "sha256, deterministic, no seed (PREREG-2 2.8)",
        "multimodular primes": "the largest distinct primes below 2^30, "
                               "enumerated downward; deterministic, no seed",
        "other_randomness": "none; no sampling, no shuffling, no reduction, no "
                            "timing-dependent branch"}
    R["route_provenance"] = {
        "measure_gvar2.py": "IMPORTED as a module (not transcribed): Q, "
                            "N_BASES, TAU_VAR, LATTICES, BETA_GRID, ROUTES6, "
                            "FAMILIES, make_A_seed, moduli, build_basis_fam, "
                            "structural_check_and_exact_absdet, bit_identical, "
                            "sd_mean, var_s_from_cells, var_f_from_cells, "
                            "gvar2, and PROBE_N (probe_nullroute) through it",
        "measure_falserefusal.py": "IMPORTED as a module: the RQ and RG route "
                                   "definitions for X_gso_k",
        "routes at binary32": "the committed float64 expressions with the cast "
                              "to np.float64 replaced by a cast to np.float32 "
                              "and nothing else changed; float32 is a knob used "
                              "to move machine epsilon and is NOT a claim about "
                              "any deployment (framing carried verbatim from "
                              "the archived probe_precision_null.py)"}

    # ============================================================ 0. bases
    print("[0] building F0 and the six per-candidate fibre families ...")
    FAMS = OrderedDict()
    FAMS["F0"] = ("F0", 1, PIN_DET)          # the scored family, seed prefix 1
    for draw, sp in DRAWS.items():
        for pin in (PIN_DET, PIN_DET_A00):
            FAMS[fibre_family_label(draw, pin)] = (draw, sp, pin)

    BAS = {}        # (fam, lat, i) -> dict
    STRUCT_OK = True
    for fam, (draw, sp, pin) in FAMS.items():
        for lat, (d, k) in LATTICES.items():
            for i in range(N_BASES):
                B, A = build_basis(d, k, i, sp, pin)
                m = MG.moduli(d, k, i, "const_q")
                ok, ad = MG.structural_check_and_exact_absdet(B, d, k, m)
                STRUCT_OK = STRUCT_OK and ok
                BAS[(fam, lat, i)] = {
                    "B": B, "A": A, "absdet": ad, "A00": int(A[0, 0]),
                    "hnum": hash_H_int(B), "struct_ok": bool(ok)}
    R["block_structure_verified_entrywise_everywhere"] = bool(STRUCT_OK)

    # cross-check: the PIN-DET draws must be the committed builder's families
    xcheck = True
    for draw, sp in DRAWS.items():
        fam = fibre_family_label(draw, PIN_DET)
        for lat, (d, k) in LATTICES.items():
            for i in range(N_BASES):
                xcheck = xcheck and np.array_equal(
                    BAS[(fam, lat, i)]["B"],
                    MG.build_basis_fam(d, k, i, "F0|%s" % draw))
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            xcheck = xcheck and np.array_equal(
                BAS[("F0", lat, i)]["B"], MG.build_basis_fam(d, k, i, "F0"))
    R["PIN_DET_families_bit_identical_to_the_committed_builder"] = bool(xcheck)

    # ================================ 1. R3-OUT-4 -- obligation (d), the guard
    print("[1] R3-OUT-4: the per-candidate fibre guard (obligation (d))")
    print("    ASSERTING AND PRINTING, per candidate, per fibre family and per")
    print("    lattice, WHICH DECLARED ARGUMENTS WERE VERIFIED CONSTANT across")
    print("    the basis index i = 0..%d." % (N_BASES - 1))
    guard = OrderedDict()
    GUARD_VIOLATIONS = []
    GSOPROF = {}
    for key, base, param in candidate_keys():
        spec = CANDIDATE_SPECS[base]
        pin = spec["pin"]
        per_fam = OrderedDict()
        for draw in DRAWS:
            fam = fibre_family_label(draw, pin)
            per_lat = OrderedDict()
            for lat, (d, k) in LATTICES.items():
                recs = [BAS[(fam, lat, i)] for i in range(N_BASES)]
                dets = [r["absdet"] for r in recs]
                a00s = [r["A00"] for r in recs]
                As = [r["A"] for r in recs]

                def _gsos():
                    key_ = (fam, lat)
                    if key_ not in GSOPROF:
                        GSOPROF[key_] = [tuple(np.abs(np.diag(np.linalg.qr(
                            r["B"].astype(np.float64).T)[1]))[:k].tolist())
                            for r in recs]
                    return GSOPROF[key_]

                stat = OrderedDict()
                # PREREG-2 2.4 gives a candidate's declared ARGUMENT set and,
                # separately, the nuisance argument held fixed on its own
                # fibre. For X_gso_k the latter (abs(det B)) is not itself a
                # member of the former, so the guard ranges over the UNION and
                # never over the argument list alone.
                checked_args = list(spec["declared_arguments"]) + [
                    a for a in spec["nuisance"]
                    if a not in spec["declared_arguments"]]
                for arg in checked_args:
                    if arg in ("d", "k", "q", "beta", "lambda", "c"):
                        stat[arg] = {
                            "role": "cell parameter",
                            "verified_constant_across_i": True,
                            "comparison": "identical by construction of the "
                                          "cell; the same value is used at "
                                          "every basis index",
                            "in_declared_nuisance_set": arg in spec["nuisance"]}
                    elif arg == "abs(det B)":
                        c = len(set(dets)) == 1
                        stat[arg] = {
                            "role": "declared NUISANCE argument",
                            "verified_constant_across_i": bool(c),
                            "comparison": "EXACT INTEGER equality of |det B_i| "
                                          "over the 8 bases",
                            "n_distinct": len(set(dets)),
                            "value_decimal_digits": len(str(dets[0])),
                            "in_declared_nuisance_set": True}
                    elif arg == "A[0,0]":
                        c = len(set(a00s)) == 1
                        stat[arg] = {
                            "role": "declared NUISANCE argument",
                            "verified_constant_across_i": bool(c),
                            "comparison": "INTEGER equality of A_i[0,0] over "
                                          "the 8 bases",
                            "n_distinct": len(set(a00s)),
                            "values_over_8_bases": a00s,
                            "in_declared_nuisance_set": True}
                    elif arg == "every entry of A":
                        c = all(np.array_equal(As[0], a) for a in As[1:])
                        stat[arg] = {
                            "role": "declared FREE argument (NOT in the "
                                    "nuisance set): the free content of A is "
                                    "what varies across the fibre",
                            "verified_constant_across_i": bool(c),
                            "comparison": "entrywise integer equality of A_i",
                            "in_declared_nuisance_set": False}
                    elif arg == "raw GSO profile":
                        gsos = _gsos()
                        c = all(g == gsos[0] for g in gsos[1:])
                        stat[arg] = {
                            "role": "declared FREE argument (NOT in the "
                                    "nuisance set)",
                            "verified_constant_across_i": bool(c),
                            "comparison": "bitwise equality of the float64 "
                                          "|R_jj|, j = 1..k, from route RQ",
                            "in_declared_nuisance_set": False}
                    else:
                        stat[arg] = {"role": "UNRECOGNISED DECLARED ARGUMENT",
                                     "verified_constant_across_i": None,
                                     "comparison": "NOT CHECKED",
                                     "in_declared_nuisance_set":
                                         arg in spec["nuisance"]}
                bad = [a for a in spec["nuisance"]
                       if stat.get(a, {}).get("verified_constant_across_i")
                       is not True]
                if bad:
                    GUARD_VIOLATIONS.append(
                        {"candidate": key, "fibre_family": fam, "lattice": lat,
                         "declared_nuisance_arguments_not_constant": bad})
                per_lat[lat] = OrderedDict([
                    ("declared_arguments_VERIFIED_CONSTANT",
                     [a for a, v in stat.items()
                      if v["verified_constant_across_i"] is True]),
                    ("declared_arguments_observed_to_VARY",
                     [a for a, v in stat.items()
                      if v["verified_constant_across_i"] is False]),
                    ("declared_nuisance_set", list(spec["nuisance"])),
                    ("NUISANCE_SET_FULLY_CONSTANT", not bad),
                    ("per_argument", stat)])
                print("    %-22s %-24s %-4s  const=%s  vary=%s  nuisance_ok=%s"
                      % (key, fam, lat,
                         ",".join(per_lat[lat][
                             "declared_arguments_VERIFIED_CONSTANT"]) or "-",
                         ",".join(per_lat[lat][
                             "declared_arguments_observed_to_VARY"]) or "-",
                         not bad))
            per_fam[fam] = per_lat
        guard[key] = OrderedDict([
            ("definition", spec["definition"]),
            ("declared_arguments", list(spec["declared_arguments"])),
            ("declared_nuisance_set", list(spec["nuisance"])),
            ("fibre_pinning", pin),
            ("per_fibre_family", per_fam)])
    R["R3_OUT_4_per_candidate_fibre_guard"] = guard
    R["R3_OUT_V_VOID"] = OrderedDict([
        ("fires", bool(GUARD_VIOLATIONS or not STRUCT_OK)),
        ("violations", GUARD_VIOLATIONS),
        ("block_structure_ok", bool(STRUCT_OK)),
        ("rule", "PREREG-2 3.1 / 6.1: if any declared nuisance argument of any "
                 "scored candidate is not constant across i on that "
                 "candidate's own fibre family, every fibre-constancy quantity "
                 "in this batch is VOID and the batch reports the instrument "
                 "defect and nothing else."),
        ("reachability_disclosure_carried_from_PREREG-2 6.1",
         "Under THIS batch's PIN-A00 construction the void row is reachable "
         "ONLY through an implementation error, because the pinning is by "
         "construction. Its non-firing is therefore evidence about the "
         "IMPLEMENTATION and about nothing else, and it may NOT be cited as a "
         "control, as a validation of the fibre clause, or as evidence about "
         "any object.")])
    print("    R3-OUT-V fires: %s" % R["R3_OUT_V_VOID"]["fires"])
    if R["R3_OUT_V_VOID"]["fires"]:
        R["TERMINATION_BRANCH"] = "T-VOID"
        R["wall_clock_seconds"] = round(time.time() - T0, 3)
        with open(args.out, "w") as fh:
            json.dump(R, fh, indent=1)
            fh.write("\n")
        print("R3-OUT-V FIRED -- instrument defect reported, and nothing else.")
        return 3

    # =========================================== 2. float routes at both prec
    print("[2] evaluating the declared routes at binary32 and binary64 ...")
    LDV = {}     # (fam, lat, i, prec) -> {route: logdet}
    GSOV = {}    # (fam, lat, i, prec) -> {route: X_gso_k}
    ROUTE_ERRORS = OrderedDict()
    for fam in FAMS:
        for lat, (d, k) in LATTICES.items():
            for i in range(N_BASES):
                B = BAS[(fam, lat, i)]["B"]
                for pname, dt in PRECISIONS.items():
                    o, e = logdet_routes_prec(B, d, k, dt)
                    LDV[(fam, lat, i, pname)] = o
                    if e:
                        ROUTE_ERRORS["%s|%s|i%d|%s|logdet" %
                                     (fam, lat, i, pname)] = e
                    if FAMS[fam][2] == PIN_DET:
                        g, ge = gso_routes_prec(B, k, dt)
                        GSOV[(fam, lat, i, pname)] = g
                        if ge:
                            ROUTE_ERRORS["%s|%s|i%d|%s|gso" %
                                         (fam, lat, i, pname)] = ge
    R["route_evaluation_errors"] = ROUTE_ERRORS
    R["route_evaluation_errors_note"] = (
        "A numerical failure of a declared route at a declared precision is "
        "INFRASTRUCTURE / NUMERICAL SIGNAL: the affected cells are reported "
        "UNCOVERED and force PREREG-2 7.6's -PARTIAL suffix. It is NEVER a "
        "falsifier of A-1 and never negative mathematical evidence.")

    # agreement of this file's float64 routes with the committed lead's
    agree = {"n_compared": 0, "n_bit_identical": 0, "max_abs_diff": 0.0}
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            B = MG.build_basis_fam(d, k, i, "F0")
            m = MG.moduli(d, k, i, "const_q")
            ref, _ = MG.logdet_routes_fam(B, d, k, m, "F0")
            mine = LDV[("F0", lat, i, "binary64")]
            for r in ROUTES6:
                agree["n_compared"] += 1
                if float(ref[r]).hex() == float(mine[r]).hex():
                    agree["n_bit_identical"] += 1
                agree["max_abs_diff"] = max(agree["max_abs_diff"],
                                            abs(ref[r] - mine[r]))
    R["binary64_routes_agree_with_the_committed_measure_gvar2"] = agree

    # =============================================== 3. exact routes (A-1.1)
    print("[3] R3-OUT-1: exact-route certification (A-1.1) ...")
    t_exact0 = time.time()
    LOGDET_EXACT = {}
    for fam in FAMS:
        for lat in LATTICES:
            for i in range(N_BASES):
                LOGDET_EXACT[(fam, lat, i)] = exact_logabsdet(
                    BAS[(fam, lat, i)]["absdet"])

    # ---- R7_exact_gram, with the declared per-lattice cap
    GSO_EXACT = {}
    r7 = OrderedDict()
    R7_UNCOVERED = []
    for fam in [f for f in FAMS if FAMS[f][2] == PIN_DET]:
        per_lat = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            ts = time.time()
            vals, dets, npr = [], [], None
            try:
                for i in range(N_BASES):
                    v, det, npr = x_gso_k_exact(BAS[(fam, lat, i)]["A"], k)
                    vals.append(v)
                    dets.append(det)
                el = time.time() - ts
                capped = (d in (100, 140)) and (el > R7_CAP_SECONDS_PER_LATTICE)
                if capped:
                    R7_UNCOVERED.append({"family": fam, "lattice": lat,
                                         "seconds": el,
                                         "reason": "exceeded the declared 45 s "
                                                   "per-lattice cap at d in "
                                                   "{100,140}"})
                    per_lat[lat] = {"terminated_within_cap": False,
                                    "seconds": el, "n_primes": npr}
                    continue
                for i in range(N_BASES):
                    GSO_EXACT[(fam, lat, i)] = vals[i]
                per_lat[lat] = {
                    "terminated_within_cap": True, "seconds": el,
                    "n_primes": npr,
                    "cap_applies": d in (100, 140),
                    "det_decimal_digits": len(str(dets[0])),
                    "n_distinct_exact_values_over_8_bases": len(set(vals)),
                    "exact_values_over_8_bases": [str(v) for v in vals]}
            except Exception as e:
                el = time.time() - ts
                R7_UNCOVERED.append({"family": fam, "lattice": lat,
                                     "seconds": el,
                                     "reason": "%s: %s" % (e.__class__.__name__, e)})
                per_lat[lat] = {"terminated_within_cap": False, "seconds": el,
                                "error": "%s: %s" % (e.__class__.__name__, e)}
            print("    R7_exact_gram %-24s %-4s d=%3d k=%3d  %.2fs  %s"
                  % (fam, lat, d, k, time.time() - ts,
                     "ok" if per_lat[lat].get("terminated_within_cap") else
                     "UNCOVERED"))
        r7[fam] = per_lat
    R["R7_exact_gram_execution"] = r7
    R["R7_exact_gram_uncovered"] = R7_UNCOVERED

    # ---- P-GRAM, APPLIED EXACTLY AS FROZEN (PREREG-2 2.9)
    print("[4] R3-OUT-8: P-GRAM (CONSISTENCY CHECK, applied as frozen) ...")
    FR = json.load(open(P_FR))
    committed_f0 = FR["informativeness_F0"]["per_lattice"]
    pgram = OrderedDict()
    worst = {"RQ_qr_of_BT": 0.0, "RG_cholesky_of_gram": 0.0}
    worst_where = {"RQ_qr_of_BT": None, "RG_cholesky_of_gram": None}
    n_cmp = 0
    for fam in [f for f in FAMS if FAMS[f][2] == PIN_DET]:
        per_lat = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            rows = OrderedDict()
            for route in ROUTES_GSO:
                devs = []
                for i in range(N_BASES):
                    if (fam, lat, i) not in GSO_EXACT:
                        continue
                    fl = GSOV[(fam, lat, i, "binary64")].get(route)
                    if fl is None:
                        continue
                    dev = abs(float(GSO_EXACT[(fam, lat, i)]) - fl)
                    devs.append(dev)
                    n_cmp += 1
                    if dev > worst[route]:
                        worst[route] = dev
                        worst_where[route] = "%s|%s|i%d (in-run float64)" % (
                            fam, lat, i)
                # the COMMITTED float64 values, for the scored family F0
                cdevs = []
                if fam == "F0":
                    cv = committed_f0[lat]["per_route"][route][
                        "values_over_8_bases"]
                    for i in range(N_BASES):
                        if (fam, lat, i) not in GSO_EXACT:
                            continue
                        dev = abs(float(GSO_EXACT[(fam, lat, i)]) - cv[i])
                        cdevs.append(dev)
                        n_cmp += 1
                        if dev > worst[route]:
                            worst[route] = dev
                            worst_where[route] = ("%s|%s|i%d (COMMITTED "
                                                  "results_falserefusal.json)"
                                                  % (fam, lat, i))
                rows[route] = {
                    "max_abs_dev_vs_in_run_float64": max(devs) if devs else None,
                    "max_abs_dev_vs_committed_float64":
                        max(cdevs) if cdevs else None,
                    "n_bases_compared": len(devs) + len(cdevs)}
            per_lat[lat] = rows
        pgram[fam] = per_lat
    tol = 1e-10
    per_route_pass = {r: (worst[r] <= tol) for r in ROUTES_GSO}
    pgram_holds = all(per_route_pass.values()) and n_cmp > 0
    R["R3_OUT_8_P_GRAM"] = OrderedDict([
        ("frozen_statement",
         "PREREG-2 2.9: R7_exact_gram must reproduce the committed RQ and RG "
         "float64 values of X_gso_k to 1e-10 absolute at every basis and "
         "lattice where both are computed. If it does not, the derivation is "
         "wrong, R7_exact_gram is reported as UNAVAILABLE -- which fires FC-1 "
         "-- and the disagreement is reported as a finding. It is never "
         "patched."),
        ("class", "CONSISTENCY CHECK (PREREG-2 5)"),
        ("tolerance_absolute", tol),
        ("n_comparisons", n_cmp),
        ("max_abs_deviation_per_route", worst),
        ("worst_cell_per_route", worst_where),
        ("PASSES_per_route", per_route_pass),
        ("P_GRAM_HOLDS", bool(pgram_holds)),
        ("per_family_per_lattice", pgram)])
    R7_AVAILABLE = bool(pgram_holds)
    R["R7_exact_gram_availability"] = {
        "AVAILABLE": R7_AVAILABLE,
        "rule_applied": "PREREG-2 2.9 as frozen: P-GRAM failing at any "
                        "comparison makes R7_exact_gram UNAVAILABLE for "
                        "X_gso_k, which fires FC-1. THE DERIVATION IS NOT "
                        "PATCHED AND NO SUBSTITUTE ROUTE IS INTRODUCED."}
    print("    P-GRAM holds: %s (max dev RQ %.3e, RG %.3e over %d comparisons)"
          % (pgram_holds, worst["RQ_qr_of_BT"], worst["RG_cholesky_of_gram"],
             n_cmp))

    # ---- R3-OUT-1: the certification, per candidate / fibre family / cell
    CERT = {}          # (key, fam, cell) -> dict
    cert_rows = OrderedDict()
    for key, base, param in candidate_keys():
        spec = CANDIDATE_SPECS[base]
        pin = spec["pin"]
        per_fam = OrderedDict()
        for draw in DRAWS:
            fam = fibre_family_label(draw, pin)
            per_cell = OrderedDict()
            for lat, (d, k) in LATTICES.items():
                for beta in BETA_GRID[d]:
                    cell = "%s_b%s" % (lat, beta)
                    if base == "X_gso_k":
                        if not R7_AVAILABLE:
                            rec = {"certified_class": "UNCERTIFIED",
                                   "exact_route": "R7_exact_gram",
                                   "reason": "R7_exact_gram is UNAVAILABLE: "
                                             "P-GRAM failed (PREREG-2 2.9)"}
                            per_cell[cell] = rec
                            CERT[(key, fam, cell)] = rec
                            continue
                        if (fam, lat, 0) not in GSO_EXACT:
                            rec = {"certified_class": "UNCERTIFIED",
                                   "exact_route": "R7_exact_gram",
                                   "reason": "route did not terminate within "
                                             "the declared cap at this lattice"}
                            per_cell[cell] = rec
                            CERT[(key, fam, cell)] = rec
                            continue
                        vals = [GSO_EXACT[(fam, lat, i)] for i in range(N_BASES)]
                        eroute = "R7_exact_gram"
                    else:
                        vals = [cand_value_exact(
                            base, LOGDET_EXACT[(fam, lat, i)],
                            BAS[(fam, lat, i)]["A00"],
                            BAS[(fam, lat, i)]["hnum"], d, k, beta, param)
                            for i in range(N_BASES)]
                        eroute = "R6_exact"
                    s, m = dec_sd_mean(vals)
                    rho = rho_of(s, m)
                    rec = {
                        "certified_class": ("CONSTANT" if len(set(vals)) == 1
                                            else "NON-CONSTANT"),
                        "exact_route": eroute,
                        "n_distinct_exact_values_over_8_bases": len(set(vals)),
                        "rho_exact": rho,
                        "exact_mean": str(m)}
                    per_cell[cell] = rec
                    CERT[(key, fam, cell)] = rec
            per_fam[fam] = per_cell
        classes = {v["certified_class"] for f in per_fam
                   for v in per_fam[f].values()}
        cert_rows[key] = OrderedDict([
            ("expected_exact_class_PREREG2_2_4", spec["expected_exact_class"]),
            ("exact_route", spec["exact_route"]),
            ("CERTIFIED_CLASS", (list(classes)[0] if len(classes) == 1
                                 else "MIXED:" + "/".join(sorted(classes)))),
            ("certification_agrees_with_the_expectation",
             (len(classes) == 1 and
              list(classes)[0] == spec["expected_exact_class"])),
            ("n_cells_per_fibre_family", len(per_fam[list(per_fam)[0]])),
            ("per_fibre_family", per_fam)])
    R["R3_OUT_1_exact_route_certification"] = OrderedDict([
        ("rule", "PREREG-2 3.3: CERTIFIED CLASS = CONSTANT if all 8 exact "
                 "values are equal, NON-CONSTANT otherwise, UNCERTIFIED if the "
                 "route did not terminate or is undefined. THE CERTIFIED "
                 "CLASS, NOT PREREG-2 2.4's EXPECTATION, IS WHAT THE "
                 "FALSIFIERS ARE EVALUATED AGAINST."),
        ("exact_route_wall_clock_seconds_total", round(time.time() - t_exact0, 3)),
        ("per_candidate", cert_rows)])
    R["certification_vs_expectation_disagreements"] = [
        k for k, v in cert_rows.items()
        if not v["certification_agrees_with_the_expectation"]]

    # =============== 4. R3-OUT-2 -- the two-precision table and the falsifiers
    print("[5] R3-OUT-2: the two-precision table and the falsifiers ...")
    two_prec = OrderedDict()
    FC = {n: [] for n in ("FC-1", "FC-2a", "FC-2b", "FC-3a", "FC-3b")}
    PDEG = []
    VERDICT_CHANGES = OrderedDict()
    rho_by_route_prec = {}      # (route, prec) -> {"CONSTANT": [], "NON": []}
    covered_cells = 0
    uncovered_cells = []

    for key, base, param in candidate_keys():
        spec = CANDIDATE_SPECS[base]
        pin = spec["pin"]
        for draw in DRAWS:
            fam = fibre_family_label(draw, pin)
            sp = FAMS[fam][1]
            for route in spec["routes"]:
                # build the per-precision cellstats, then the committed VAR-F
                cs = {p: OrderedDict() for p in PRECISIONS}
                missing = []
                for lat, (d, k) in LATTICES.items():
                    for p in PRECISIONS:
                        cs[p].setdefault(lat, OrderedDict())
                    for beta in BETA_GRID[d]:
                        for p in PRECISIONS:
                            vals = []
                            bad = False
                            for i in range(N_BASES):
                                if base == "X_gso_k":
                                    src = GSOV[(fam, lat, i, p)]
                                    if route not in src:
                                        bad = True
                                        break
                                    vals.append(src[route])
                                else:
                                    src = LDV[(fam, lat, i, p)]
                                    if route not in src:
                                        bad = True
                                        break
                                    vals.append(cand_value_prec(
                                        base, src[route],
                                        BAS[(fam, lat, i)]["A00"],
                                        BAS[(fam, lat, i)]["hnum"],
                                        d, k, beta, PRECISIONS[p], param))
                            if bad:
                                missing.append("%s_b%s|%s" % (lat, beta, p))
                                continue
                            s, m = sd_mean(vals)
                            cs[p][lat][beta] = {
                                "s": s, "m": m,
                                "spread": float(max(vals) - min(vals)),
                                "bit_identical": bool(bit_identical(vals)),
                                "n_distinct": n_distinct(vals),
                                "seed_prefix": sp}
                vf = {p: var_f_from_cells(cs[p]) for p in PRECISIONS}
                blockkey = "%s|%s|%s" % (key, route, fam)
                missing_cells = {x.split("|")[0] for x in missing}
                cells = OrderedDict()
                n_changed = 0
                for lat, (d, k) in LATTICES.items():
                    for beta in BETA_GRID[d]:
                        cell = "%s_b%s" % (lat, beta)
                        if any(cell not in vf[p] for p in PRECISIONS):
                            # already enumerated in `missing` with its precision
                            if cell not in missing_cells:
                                uncovered_cells.append(blockkey + "|" + cell)
                            continue
                        rec = OrderedDict()
                        rec["certified_class"] = CERT[(key, fam, cell)][
                            "certified_class"]
                        rec["rho_exact"] = CERT[(key, fam, cell)].get("rho_exact")
                        for p in PRECISIONS:
                            v = vf[p][cell]
                            rho = rho_of(v["s_c_fib"], v["m_c_fib"])
                            rec[p] = OrderedDict([
                                ("s_c_fib", v["s_c_fib"]),
                                ("m_c_fib", v["m_c_fib"]),
                                ("rho", rho),
                                ("bit_identical", v["bit_identical"]),
                                ("n_distinct_ieee754_values_over_8_bases",
                                 v["n_distinct_ieee754_values_over_8_bases"]),
                                ("VAR_F", v["VAR_F"]),
                                ("VAR_F_decided_by", v["decided_by"]),
                                ("D_c_fib", v["D_c_fib"])])
                        r32 = rec["binary32"]["rho"]
                        r64 = rec["binary64"]["rho"]
                        rec["ratio_rho32_over_rho64"] = (
                            (r32 / r64) if (r32 is not None and r64) else None)
                        rec["VAR_F_verdict_changes_with_precision"] = (
                            rec["binary32"]["VAR_F"] != rec["binary64"]["VAR_F"])
                        if rec["VAR_F_verdict_changes_with_precision"]:
                            n_changed += 1
                        rec["fibre_family"] = fam
                        rec["fibre_seed_prefix"] = sp
                        # --- precision_degenerate (PREREG-2 1.3)
                        pdeg = (r64 == 0.0)
                        rec["precision_degenerate"] = bool(pdeg)
                        if pdeg:
                            strict = ("A-1.2 SATISFIED under the strict reading"
                                      if (r32 or 0.0) > 0.0 else
                                      "A-1.2 FALSIFIED under the strict "
                                      "reading (nothing decreased)")
                            rec["frozen_reading"] = ("EXEMPT from FC-2a: not a "
                                                     "falsification and not a "
                                                     "confirmation")
                            rec["strict_reading"] = strict
                            PDEG.append({"block": blockkey, "cell": cell,
                                         "certified_class": rec["certified_class"],
                                         "rho32": r32, "rho64": r64,
                                         "frozen_reading": rec["frozen_reading"],
                                         "strict_reading": strict})
                        covered_cells += 1
                        cls = rec["certified_class"]
                        # --- falsifier scoring, PREREG-2 1.2, verbatim
                        fired = []
                        if cls == "CONSTANT":
                            if (not pdeg) and r32 is not None and r64 is not None \
                                    and r32 <= r64:
                                fired.append("FC-2a")
                                FC["FC-2a"].append(
                                    {"block": blockkey, "cell": cell,
                                     "rho32": r32, "rho64": r64})
                        elif cls == "NON-CONSTANT":
                            if r32 == 0.0 or r64 == 0.0:
                                fired.append("FC-3b")
                                FC["FC-3b"].append(
                                    {"block": blockkey, "cell": cell,
                                     "rho32": r32, "rho64": r64})
                            ratio = rec["ratio_rho32_over_rho64"]
                            if ratio is not None and not (
                                    1.0 / W_WINDOW <= ratio <= W_WINDOW):
                                fired.append("FC-3a")
                                FC["FC-3a"].append(
                                    {"block": blockkey, "cell": cell,
                                     "ratio": ratio, "rho32": r32, "rho64": r64})
                        rec["falsifiers_fired_at_this_cell"] = fired
                        cells[cell] = rec
                        # P-SEP accumulation
                        for p in PRECISIONS:
                            rr = rec[p]["rho"]
                            if rr is None:
                                continue
                            b = rho_by_route_prec.setdefault(
                                (route, p), {"CONSTANT": [], "NON-CONSTANT": []})
                            if cls in b:
                                b[cls].append((rr, key, cell, fam))
                if missing:
                    uncovered_cells.extend(
                        [blockkey + "|" + x for x in missing])
                two_prec[blockkey] = OrderedDict([
                    ("candidate", key), ("route", route), ("fibre_family", fam),
                    ("certified_class",
                     cert_rows[key]["CERTIFIED_CLASS"]),
                    ("n_cells", len(cells)),
                    ("n_cells_where_the_committed_VAR_F_verdict_CHANGES_with_"
                     "precision", n_changed),
                    ("n_precision_degenerate_cells",
                     sum(1 for c in cells.values() if c["precision_degenerate"])),
                    ("per_cell", cells)])
                VERDICT_CHANGES[blockkey] = n_changed

    # FC-2b: existence, scored once per (candidate, fibre family, cell)
    for (key, fam, cell), rec in CERT.items():
        if rec["certified_class"] == "CONSTANT" and rec.get("rho_exact"):
            FC["FC-2b"].append({"candidate": key, "fibre_family": fam,
                                "cell": cell, "rho_exact": rec["rho_exact"]})

    # FC-1: per CANDIDATE CLASS (PREREG-2 1.2)
    det_class = [k for k, b, p in candidate_keys() if b != "X_gso_k"]
    gso_class = [k for k, b, p in candidate_keys() if b == "X_gso_k"]
    fc1 = OrderedDict()
    fc1["determinant_only_class"] = {
        "candidates": det_class, "exact_route": "R6_exact",
        "exists_defined_and_terminates": True,
        "FC_1_fires": False,
        "evidence": "R6_exact evaluated at every candidate, fibre family and "
                    "cell in this run"}
    fc1["raw_GSO_class"] = {
        "candidates": gso_class, "exact_route": "R7_exact_gram",
        "exists_defined_and_terminates": bool(R7_AVAILABLE and not R7_UNCOVERED),
        "FC_1_fires": bool(not R7_AVAILABLE or bool(R7_UNCOVERED)),
        "evidence": ("P-GRAM verdict %s; %d lattice(s) over the declared cap"
                     % (pgram_holds, len(R7_UNCOVERED)))}
    if fc1["raw_GSO_class"]["FC_1_fires"]:
        FC["FC-1"].append(fc1["raw_GSO_class"])
    R["FC_1_per_candidate_class"] = fc1

    R["R3_OUT_2_two_precision_table"] = OrderedDict([
        ("rule", "PREREG-2 3.2 / 3.4"),
        ("n_blocks", len(two_prec)),
        ("n_covered_cell_evaluations", covered_cells),
        ("uncovered", uncovered_cells),
        ("falsifiers", OrderedDict([
            (n, {"fired": bool(FC[n]),
                 "n_cells_fired": len(FC[n]),
                 "instances": FC[n][:200],
                 "n_instances_truncated_in_this_summary":
                     max(0, len(FC[n]) - 200)})
            for n in ("FC-1", "FC-2a", "FC-2b", "FC-3a", "FC-3b")])),
        ("A_1_HOLDS_IN_THIS_BATCH",
         not any(FC[n] for n in ("FC-1", "FC-2a", "FC-2b", "FC-3a", "FC-3b"))),
        ("diagnostic_X_gso_k_rho_margin_over_u_64",
         "reported in R3-OUT-5 as a MEASUREMENT and never as a control "
         "(PREREG-2 6.1)"),
        ("per_block", two_prec)])
    R["R3_OUT_7_precision_degenerate_disclosure"] = OrderedDict([
        ("rule", "PREREG-2 1.3: the FROZEN reading is binding (a cell with "
                 "rho(binary64) == 0 exactly is precision_degenerate and EXEMPT "
                 "from FC-2a -- not a falsification and not a confirmation; "
                 "FC-2b still binds there). The STRICT reading's verdict is "
                 "reported beside it at every such cell."),
        ("n_precision_degenerate_cells", len(PDEG)),
        ("n_strict_reading_FALSIFIED", sum(
            1 for x in PDEG if x["strict_reading"].startswith(
                "A-1.2 FALSIFIED"))),
        ("n_strict_reading_SATISFIED", sum(
            1 for x in PDEG if x["strict_reading"].startswith(
                "A-1.2 SATISFIED"))),
        ("per_certified_class", {
            cl: sum(1 for x in PDEG if x["certified_class"] == cl)
            for cl in ("CONSTANT", "NON-CONSTANT", "UNCERTIFIED")}),
        ("cells", PDEG)])
    R["obligation_c_VAR_F_verdict_changes_with_precision"] = OrderedDict([
        ("rule", "PREREG-2 3.2 / AM-18(b)"),
        ("n_blocks_with_at_least_one_changing_cell",
         sum(1 for v in VERDICT_CHANGES.values() if v)),
        ("n_blocks_total", len(VERDICT_CHANGES)),
        ("total_cells_whose_committed_VAR_F_verdict_changes",
         sum(VERDICT_CHANGES.values())),
        ("per_block_cell_counts", VERDICT_CHANGES)])

    # ==================================================== 5. R3-OUT-5 -- P-SEP
    print("[6] R3-OUT-5: P-SEP, the K-intervals (SOLVED, not gridded) ...")
    psep = OrderedDict()
    for (route, p), b in sorted(rho_by_route_prec.items()):
        u = UNIT_ROUNDOFF[p]
        cons = [(x[0] / u, x[1], x[2]) for x in b["CONSTANT"]]
        noncons = [(x[0] / u, x[1], x[2]) for x in b["NON-CONSTANT"]]
        kmin = max(cons)[0] if cons else None
        kmax = min(noncons)[0] if noncons else None
        empty = (None if (kmin is None or kmax is None) else kmin >= kmax)
        psep["%s|%s" % (route, p)] = OrderedDict([
            ("route", route), ("precision", p), ("unit_roundoff_u_p", u),
            ("K_min", kmin),
            ("K_min_witness", (max(cons)[1:] if cons else None)),
            ("K_max", kmax),
            ("K_max_witness", (min(noncons)[1:] if noncons else None)),
            ("n_constant_cells", len(cons)),
            ("n_nonconstant_cells", len(noncons)),
            ("interval_EMPTY", empty),
            ("note", (None if (kmin is not None and kmax is not None) else
                      "one side undefined: no certified candidate of that "
                      "class supplies a rho on this (route, precision); the "
                      "interval is unbounded on that side"))])
    def _inter(keys):
        mins = [psep[k]["K_min"] for k in keys if psep[k]["K_min"] is not None]
        maxs = [psep[k]["K_max"] for k in keys if psep[k]["K_max"] is not None]
        lo = max(mins) if mins else None
        hi = min(maxs) if maxs else None
        return OrderedDict([("K_min", lo), ("K_max", hi),
                            ("EMPTY", (None if (lo is None or hi is None)
                                       else lo >= hi))])
    per_route_inter = OrderedDict()
    for route in sorted({psep[k]["route"] for k in psep}):
        ks = [k for k in psep if psep[k]["route"] == route]
        per_route_inter[route] = _inter(ks)
    R["R3_OUT_5_P_SEP"] = OrderedDict([
        ("what_this_is", "PREREG-2 3.5. A MEASUREMENT of whether an admissible "
                         "precision-relative interval exists. IT SPECIFIES NO "
                         "CRITERION AND PROPOSES NO K."),
        ("definition", "K_min(r,p) = max over CERTIFIED-CONSTANT candidates and "
                       "covered cells of rho/u_p; K_max(r,p) = min over "
                       "CERTIFIED-NON-CONSTANT candidates and covered cells of "
                       "rho/u_p; the interval is EMPTY if K_min >= K_max"),
        ("per_route_per_precision", psep),
        ("intersection_over_precisions_at_fixed_route", per_route_inter),
        ("joint_intersection_over_routes_and_precisions", _inter(list(psep))),
        ("P_SEP_prediction", "the joint intersection over both declared "
                             "precisions is EMPTY"),
        ("P_SEP_falsifier", "the producer exhibits a non-empty joint "
                            "intersection")])

    # ================================================= 6. R3-OUT-6 -- X_hash
    print("[7] R3-OUT-6: X_hash at every declared amplitude, all three draws")
    xhash = OrderedDict()
    for key, base, param in candidate_keys():
        if base != "X_hash":
            continue
        per_draw = OrderedDict()
        for draw in DRAWS:
            fam = fibre_family_label(draw, PIN_DET)
            rows = OrderedDict()
            for route in ROUTES6:
                bk = "%s|%s|%s" % (key, route, fam)
                blk = two_prec[bk]
                rows[route] = {
                    "n_cells": blk["n_cells"],
                    "rho_binary32_min": min(
                        [c["binary32"]["rho"] for c in blk["per_cell"].values()
                         if c["binary32"]["rho"] is not None] or [None]),
                    "rho_binary32_max": max(
                        [c["binary32"]["rho"] for c in blk["per_cell"].values()
                         if c["binary32"]["rho"] is not None] or [None]),
                    "rho_binary64_min": min(
                        [c["binary64"]["rho"] for c in blk["per_cell"].values()
                         if c["binary64"]["rho"] is not None] or [None]),
                    "rho_binary64_max": max(
                        [c["binary64"]["rho"] for c in blk["per_cell"].values()
                         if c["binary64"]["rho"] is not None] or [None]),
                    "n_cells_rho32_zero": sum(
                        1 for c in blk["per_cell"].values()
                        if c["binary32"]["rho"] == 0.0),
                    "n_cells_rho64_zero": sum(
                        1 for c in blk["per_cell"].values()
                        if c["binary64"]["rho"] == 0.0),
                    "n_cells_FC_3a": sum(
                        1 for c in blk["per_cell"].values()
                        if "FC-3a" in c["falsifiers_fired_at_this_cell"]),
                    "n_cells_FC_3b": sum(
                        1 for c in blk["per_cell"].values()
                        if "FC-3b" in c["falsifiers_fired_at_this_cell"]),
                    "n_cells_VAR_F_verdict_changes":
                        blk["n_cells_where_the_committed_VAR_F_verdict_CHANGES"
                            "_with_precision"]}
            per_draw[fam] = rows
        xhash[key] = per_draw
    R["R3_OUT_6_X_hash_null_object_calibration"] = OrderedDict([
        ("status", "RE-EXECUTION AND EXTENSION OF AN ARCHIVED CONSTRUCTION, "
                   "NEVER A NEW FINDING. That X_hash is admitted at 38 of 38 "
                   "cells at the top amplitude by the BATCH-4ed139 code path is "
                   "ARCHIVED, n = 1, and ATTRIBUTED to the BATCH-4ed139 Red "
                   "Team's probe_argset.py section Q3 and to KN-FIND-9d44b4 "
                   "section 6 item 5. What is new here is only its behaviour "
                   "ACROSS PRECISIONS and on the PER-CANDIDATE fibre."),
        ("H_definition", "H(B) = int(sha256(payload).hexdigest(), 16) / 2**256 "
                         "with payload = b'|'.join(str(int(x)).encode() for x "
                         "in B.flatten(order='C')); B the EXACT INTEGER basis. "
                         "H reads EVERY ENTRY OF A and carries NO LATTICE "
                         "INFORMATION WHATEVER (PREREG-2 2.8)."),
        ("per_amplitude_per_draw", xhash)])

    # ======================= 7. R3-OUT-3 -- obligation (b): V6 / V7 / VX on F0
    print("[8] R3-OUT-3: obligation (b), F0's refusal half under V6 / V7 / VX")
    OBL_B = OrderedDict()
    fib_primary = fibre_family_label("fib_s2", PIN_DET)

    def _cellstats_scored(base, route, prec):
        out = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            per = OrderedDict()
            for beta in BETA_GRID[d]:
                vals = [cand_value_prec(base, LDV[("F0", lat, i, prec)][route],
                                        BAS[("F0", lat, i)]["A00"],
                                        BAS[("F0", lat, i)]["hnum"],
                                        d, k, beta, PRECISIONS[prec], None)
                        for i in range(N_BASES)]
                s, m = sd_mean(vals)
                per[beta] = {"s": s, "m": m,
                             "spread": float(max(vals) - min(vals)),
                             "bit_identical": bool(bit_identical(vals)),
                             "n_distinct": n_distinct(vals), "seed_prefix": 1}
            out[lat] = per
        return out

    def _cellstats_fibre(base, route, prec, fam):
        out = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            per = OrderedDict()
            for beta in BETA_GRID[d]:
                vals = [cand_value_prec(base, LDV[(fam, lat, i, prec)][route],
                                        BAS[(fam, lat, i)]["A00"],
                                        BAS[(fam, lat, i)]["hnum"],
                                        d, k, beta, PRECISIONS[prec], None)
                        for i in range(N_BASES)]
                s, m = sd_mean(vals)
                per[beta] = {"s": s, "m": m,
                             "spread": float(max(vals) - min(vals)),
                             "bit_identical": bool(bit_identical(vals)),
                             "n_distinct": n_distinct(vals),
                             "seed_prefix": FAMS[fam][1]}
            out[lat] = per
        return out

    def _cellstats_exact(base, fam, sp):
        out = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            per = OrderedDict()
            for beta in BETA_GRID[d]:
                vals = [float(cand_value_exact(
                    base, LOGDET_EXACT[(fam, lat, i)],
                    BAS[(fam, lat, i)]["A00"], BAS[(fam, lat, i)]["hnum"],
                    d, k, beta, None)) for i in range(N_BASES)]
                s, m = sd_mean(vals)
                per[beta] = {"s": s, "m": m,
                             "spread": float(max(vals) - min(vals)),
                             "bit_identical": bool(bit_identical(vals)),
                             "n_distinct": n_distinct(vals), "seed_prefix": sp}
            out[lat] = per
        return out

    for prec_label, prec in (("binary64_FROZEN_READING", "binary64"),
                             ("binary32_DIAGNOSTIC_not_a_frozen_reading",
                              "binary32")):
        per_cand = OrderedDict()
        for base in ("X_null", "rdet"):
            rows = OrderedDict()
            for route in ROUTES6:
                vs = var_s_from_cells(_cellstats_scored(base, route, prec))
                vf = var_f_from_cells(
                    _cellstats_fibre(base, route, prec, fib_primary))
                cells = OrderedDict(
                    (ck, {"VAR_S": vs[ck]["VAR_S"], "VAR_F": vf[ck]["VAR_F"],
                          "G_VAR2": gvar2(vs[ck], vf[ck]),
                          "s_c": vs[ck]["s_c"], "D_c": vs[ck]["D_c"],
                          "s_c_fib": vf[ck]["s_c_fib"],
                          "bit_identical_fib": vf[ck]["bit_identical"]})
                    for ck in vs)
                verds = [c["G_VAR2"] for c in cells.values()]
                rows[route] = OrderedDict([
                    ("target", "REFUSED"),
                    ("n_cells_covered", len(verds)), ("n_cells_declared", 38),
                    ("coverage", "%d/38" % len(verds)),
                    ("n_REFUSE", sum(1 for v in verds if v == "REFUSE")),
                    ("n_ADMIT", sum(1 for v in verds if v == "ADMIT")),
                    ("TARGET_MET_AT_EVERY_COVERED_CELL",
                     all(v == "REFUSE" for v in verds)),
                    ("per_cell", cells)])
            # the exact route
            vs = var_s_from_cells(_cellstats_exact(base, "F0", 1))
            vf = var_f_from_cells(_cellstats_exact(base, fib_primary, 2))
            cells = OrderedDict(
                (ck, {"VAR_S": vs[ck]["VAR_S"], "VAR_F": vf[ck]["VAR_F"],
                      "G_VAR2": gvar2(vs[ck], vf[ck]),
                      "s_c": vs[ck]["s_c"], "D_c": vs[ck]["D_c"],
                      "s_c_fib": vf[ck]["s_c_fib"],
                      "bit_identical_fib": vf[ck]["bit_identical"]})
                for ck in vs)
            verds = [c["G_VAR2"] for c in cells.values()]
            rows["R6_exact"] = OrderedDict([
                ("target", "REFUSED"),
                ("n_cells_covered", len(verds)), ("n_cells_declared", 38),
                ("coverage", "%d/38" % len(verds)),
                ("n_REFUSE", sum(1 for v in verds if v == "REFUSE")),
                ("n_ADMIT", sum(1 for v in verds if v == "ADMIT")),
                ("TARGET_MET_AT_EVERY_COVERED_CELL",
                 all(v == "REFUSE" for v in verds)),
                ("precision_free", True),
                ("per_cell", cells)])
            per_cand[base] = rows
        v6 = all(per_cand[c][r]["TARGET_MET_AT_EVERY_COVERED_CELL"]
                 for c in per_cand for r in ROUTES6)
        v7 = v6 and all(per_cand[c]["R6_exact"][
            "TARGET_MET_AT_EVERY_COVERED_CELL"] for c in per_cand)
        vx = all(per_cand[c]["R6_exact"]["TARGET_MET_AT_EVERY_COVERED_CELL"]
                 for c in per_cand)
        OBL_B[prec_label] = OrderedDict([
            ("scope", "F0's REFUSAL HALF ONLY -- X_null and rdet, both "
                      "determinant-only, no reduction. The lam1n / hkz / "
                      "rawtail ADMITTED half is NOT IN SCOPE (PREREG-2 2.5)."),
            ("V6_route_set", ROUTES6),
            ("V6_verdict_over_the_SIX_FLOAT_ROUTES_R0_to_R5",
             "PASS" if v6 else "FAIL"),
            ("V7_route_set", ROUTES6 + ["R6_exact"]),
            ("V7_verdict_over_the_SEVEN_ROUTES_R0_to_R5_plus_R6_exact",
             "PASS" if v7 else "FAIL"),
            ("VX_route_set", ["R6_exact"]),
            ("VX_verdict_over_the_EXACT_ROUTE_ALONE_R6_exact",
             "PASS" if vx else "FAIL"),
            ("per_candidate_per_route", per_cand)])
    R["R3_OUT_3_obligation_b"] = OrderedDict([
        ("status", "A NEW MEASUREMENT IN THIS BATCH. The BATCH-4ed139 frozen "
                   "verdict is IMMUTABLE AND IS NOT RESCORED: F0 FAILED, the "
                   "branch was T-F0FAIL reported as T-F0FAIL-PARTIAL, and "
                   "DEC-20260812-781961 closed it. This section adds a route "
                   "and computes THIS batch's own answer."),
        ("naming_rule", "NO ONE OF V6, V7, VX MAY BE REPORTED WITHOUT NAMING "
                        "ITS ROUTE SET IN THE SAME SENTENCE (PREREG-2 4)."),
        ("fibre_family_used_for_VAR_F", fib_primary),
        ("scored_family_used_for_VAR_S", "F0 (seed prefix 1)"),
        ("readings", OBL_B)])

    # ============================================ 8. the prediction register
    fro = OBL_B["binary64_FROZEN_READING"]
    preds = OrderedDict()
    preds["P-A11"] = {
        "statement": "an exact route exists and terminates within the declared "
                     "cap for every in-scope candidate (mandatory at d <= 40)",
        "class": "PREDICTION", "open_at_notarization": True,
        "falsifier": "FC-1",
        "OUTCOME": ("HELD" if not FC["FC-1"] else "FALSIFIED"),
        "detail": fc1}
    preds["P-A12a"] = {
        "statement": "X_null and rdet: rho(f32) > rho(f64) at every "
                     "non-degenerate covered cell, rho(exact) = 0",
        "class": "CONSISTENCY CHECK", "open_at_notarization": True,
        "falsifier": "FC-2a / FC-2b",
        "OUTCOME": ("HELD" if not [x for x in FC["FC-2a"] + FC["FC-2b"]
                                   if x.get("block", x.get("candidate", ""))
                                   .split("|")[0] in ("X_null", "rdet")]
                    else "FALSIFIED")}
    preds["P-A12b"] = {
        "statement": "X_parfree, V_evade, X_lambda (every lambda): same, on "
                     "their OWN fibre",
        "class": "PREDICTION", "open_at_notarization": True,
        "falsifier": "FC-2a / FC-2b",
        "OUTCOME": ("HELD" if not [
            x for x in FC["FC-2a"] + FC["FC-2b"]
            if x.get("block", x.get("candidate", "")).split("|")[0].split("[")[0]
            in ("X_parfree", "V_evade", "X_lambda")] else "FALSIFIED")}
    preds["P-A13a"] = {
        "statement": "X_gso_k: rho(f32)/rho(f64) in [1/2, 2] and rho > 0 at "
                     "both precisions",
        "class": "CONSISTENCY CHECK", "open_at_notarization": True,
        "falsifier": "FC-3a / FC-3b",
        "OUTCOME": ("NOT SCORABLE: X_gso_k is UNCERTIFIED because "
                    "R7_exact_gram is UNAVAILABLE (P-GRAM)" if not R7_AVAILABLE
                    else ("HELD" if not [
                        x for x in FC["FC-3a"] + FC["FC-3b"]
                        if x["block"].split("|")[0] == "X_gso_k"]
                        else "FALSIFIED"))}
    preds["P-HASH"] = {
        "statement": "X_hash: rho(f32)/rho(f64) in [1/2, 2] and rho > 0, at "
                     "every declared amplitude and fibre draw",
        "class": "PREDICTION", "open_at_notarization": True,
        "falsifier": "FC-3a / FC-3b",
        "OUTCOME": ("HELD" if not [x for x in FC["FC-3a"] + FC["FC-3b"]
                                   if x["block"].split("|")[0].startswith(
                                       "X_hash")] else "FALSIFIED"),
        "frozen_consequence_carried": (
            "P-HASH HOLDING CANNOT FALSIFY A-1 and may not be reported as "
            "falsifying it (X_hash is certified non-constant, so A-1.3 "
            "predicts exactly this). What it bounds is A-1's usable content: "
            "if P-HASH holds, precision-invariance of the fibre dispersion is "
            "NECESSARY BUT NOT SUFFICIENT for 'reads the instance', and A-1 "
            "buys strictly less than a separator.")}
    preds["P-SEP"] = {
        "statement": "the joint K-interval over both precisions is EMPTY",
        "class": "PREDICTION", "open_at_notarization": True,
        "falsifier": "a non-empty joint intersection",
        "OUTCOME": R["R3_OUT_5_P_SEP"][
            "joint_intersection_over_routes_and_precisions"]}
    preds["P-F0Xa"] = {
        "statement": "V6 = FAIL", "class": "CONSISTENCY CHECK",
        "open_at_notarization": True, "falsifier": "V6 != FAIL",
        "OUTCOME": ("HELD" if fro[
            "V6_verdict_over_the_SIX_FLOAT_ROUTES_R0_to_R5"] == "FAIL"
            else "FALSIFIED")}
    preds["P-F0Xb"] = {
        "statement": "V7 = FAIL and VX = PASS at 38/38",
        "class": "PREDICTION", "open_at_notarization": True,
        "falsifier": "either disagreeing at any covered cell",
        "OUTCOME": ("HELD" if (fro[
            "V7_verdict_over_the_SEVEN_ROUTES_R0_to_R5_plus_R6_exact"] == "FAIL"
            and fro["VX_verdict_over_the_EXACT_ROUTE_ALONE_R6_exact"] == "PASS")
            else "FALSIFIED")}
    preds["P-GRAM"] = {
        "statement": "R7_exact_gram reproduces committed RQ/RG X_gso_k to 1e-10",
        "class": "CONSISTENCY CHECK", "open_at_notarization": True,
        "falsifier": "any disagreement above 1e-10",
        "OUTCOME": ("HELD" if pgram_holds else "FALSIFIED")}
    preds["P-G2"] = {
        "statement": "every declared nuisance argument of every scored "
                     "candidate is constant across i on that candidate's own "
                     "fibre family",
        "class": "MUST-PASS GUARD", "open_at_notarization": True,
        "falsifier": "any declared argument varying anywhere",
        "OUTCOME": ("HELD" if not GUARD_VIOLATIONS else "FAILED")}
    R["PREDICTION_REGISTER"] = OrderedDict([
        ("source", "PREREG-2 section 5, frozen at notarization; all ten items "
                   "were OPEN at the moment of notarization"),
        ("empirical_content_of_this_batch",
         "FIVE predictions (P-A11, P-A12b, P-HASH, P-SEP, P-F0Xb); FOUR "
         "consistency checks (P-A12a, P-A13a, P-F0Xa, P-GRAM) -- reported, "
         "valuable and NOT counted; ONE must-pass guard (P-G2)"),
        ("items", preds)])

    # =============================================== 9. termination branch
    any_fc = any(FC[n] for n in ("FC-1", "FC-2a", "FC-2b", "FC-3a", "FC-3b"))
    all_classes_fc1 = (fc1["determinant_only_class"]["FC_1_fires"] and
                       fc1["raw_GSO_class"]["FC_1_fires"])
    partial = bool(uncovered_cells or R7_UNCOVERED or ROUTE_ERRORS)
    if GUARD_VIOLATIONS:
        branch = "T-VOID"
    elif all_classes_fc1:
        branch = "T-UNSTATABLE"
    elif any_fc:
        branch = "T-A1-FALSIFIED"
    else:
        branch = "T-A1-HELD"
    R["TERMINATION_BRANCH"] = branch + ("-PARTIAL" if partial else "")
    R["TERMINATION_BRANCH_BASIS"] = OrderedDict([
        ("rule", "PREREG-2 7: exactly one of T-VOID, T-UNSTATABLE, "
                 "T-A1-FALSIFIED, T-A1-HELD fires; the branch is read off "
                 "R3-OUT-1 and R3-OUT-2 under R3-OUT-V's precedence and "
                 "NOWHERE ELSE. Section 7.6 is the infrastructure/coverage "
                 "branch and is NOT a fifth science branch."),
        ("R3_OUT_V_fires", bool(GUARD_VIOLATIONS)),
        ("FC_1_fires_for_EVERY_class", bool(all_classes_fc1)),
        ("falsifiers_fired", {n: bool(FC[n]) for n in FC}),
        ("partial_suffix_applied", partial),
        ("partial_reason", {"uncovered_cell_evaluations": len(uncovered_cells),
                            "R7_uncovered_lattices": len(R7_UNCOVERED),
                            "route_evaluation_errors": len(ROUTE_ERRORS)})])

    R["scope"] = (
        "q = 3329; d in {20, 30, 40, 100, 140}; the frozen k and beta grids; 8 "
        "bases per lattice per fibre family; one scored family F0 and three "
        "fibre draws under two frozen pinnings; six float routes plus one "
        "exact route for the determinant-only candidates, two float routes "
        "plus one exact route for X_gso_k; two working precisions, binary32 "
        "and binary64; NO REDUCTION OF ANY KIND and nothing reduction-"
        "dependent above d = 40. lam1n, hkz and rawtail are OUT OF SCOPE "
        "(PREREG-2 2.5) -- a declared scope limit, NEVER an FC-1 firing. "
        "Every observation is scoped to exactly that and transports nowhere.")
    R["wall_clock_seconds"] = round(time.time() - T0, 3)
    R["measurement_cap_seconds"] = MEASUREMENT_CAP_SECONDS
    R["measurement_within_cap"] = R["wall_clock_seconds"] <= MEASUREMENT_CAP_SECONDS

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=1)
        fh.write("\n")

    print("=" * 78)
    print("A-1 DIAGNOSTIC -- BATCH-6b6e78 -- TOY")
    print("=" * 78)
    print("R3-OUT-V (guard P-G2) fires        : %s" % bool(GUARD_VIOLATIONS))
    print("R3-OUT-8 P-GRAM holds              : %s" % pgram_holds)
    print("    max abs dev vs RQ float64      : %.3e" % worst["RQ_qr_of_BT"])
    print("    max abs dev vs RG float64      : %.3e" % worst["RG_cholesky_of_gram"])
    print("R7_exact_gram AVAILABLE            : %s" % R7_AVAILABLE)
    for n in ("FC-1", "FC-2a", "FC-2b", "FC-3a", "FC-3b"):
        print("%-6s fired: %-5s  n = %d" % (n, bool(FC[n]), len(FC[n])))
    print("precision_degenerate cells         : %d "
          "(strict reading FALSIFIED at %d)"
          % (len(PDEG), R["R3_OUT_7_precision_degenerate_disclosure"][
              "n_strict_reading_FALSIFIED"]))
    print("cells whose committed VAR-F verdict changes with precision: %d "
          "of %d covered" % (sum(VERDICT_CHANGES.values()), covered_cells))
    for lab in OBL_B:
        b = OBL_B[lab]
        print("obligation (b) [%s]: V6{R0..R5} = %s, "
              "V7{R0..R5,R6_exact} = %s, VX{R6_exact} = %s"
              % (lab, b["V6_verdict_over_the_SIX_FLOAT_ROUTES_R0_to_R5"],
                 b["V7_verdict_over_the_SEVEN_ROUTES_R0_to_R5_plus_R6_exact"],
                 b["VX_verdict_over_the_EXACT_ROUTE_ALONE_R6_exact"]))
    print("P-SEP joint intersection           : %s"
          % json.dumps(R["R3_OUT_5_P_SEP"][
              "joint_intersection_over_routes_and_precisions"]))
    print("TERMINATION BRANCH                 : %s" % R["TERMINATION_BRANCH"])
    print("\nwrote %s in %.2f s" % (args.out, R["wall_clock_seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
