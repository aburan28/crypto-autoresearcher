#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260808-2a9085 / BATCH-cbe023 / GOAL-MLKEM-005
SECTION A of the notarized pre-registration
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-35efa3/prereg.md
  sha256 2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8
  notarized in commit 4f7c63703.

THE AM-4 ADMISSIBILITY GATE over the ten frozen candidate observables X1..X10.

CLAIM TIER: TOY. Nothing this script computes bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model.

certificate.kind: none  -- no discrete-log solve and no factor-base relation is
claimed or produced, so docs/claims-and-verification.md requires no solution
certificate. The independent re-verifications carried here (exact-SVP vs Gram
enumeration cross-check, sympy det(U) check, the OD identity) are INSTRUMENT
CHECKS and are labelled as such, never as certificates.

Budget: 1 run, 8 GB, 10800 s. BLAS threads pinned to 1 by the caller.
"""

import os
import sys
import json
import time
import math
import socket
import hashlib
import platform
import subprocess
import argparse
from collections import OrderedDict

import numpy as np
import scipy
from scipy.special import betaincinv

T_START = time.time()

# ----------------------------------------------------------------------------
# 0. FROZEN CONSTANTS, transcribed from the pre-registration. Nothing here is
#    computed from a measurement.
# ----------------------------------------------------------------------------

PREREG_REL = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
              "TASK-20260808-35efa3/prereg.md")
PREREG_SHA256_EXPECTED = "2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8"
NOTARIZING_COMMIT = "4f7c63703"

TAU_NUM = 1e-6      # prereg 2.2 / 2.5  G-NUM
TAU_INV = 0.01      # prereg 2.2 / 2.5  G-INV
TAU_Q   = 0.10      # prereg 2.2 / 2.5  G-Q
TAU_REL = 0.10      # prereg 2.2 / 2.5  G-REL
OD_IDENTITY_TOL = 1e-10   # prereg 2.4

Q_MAIN = 3329
Q_LADDER = [1, 2, 4, 16, 64, 256, 1009, 3329]          # prereg 2.1
RANK_LADDER = [1, 5, 10, 20, "k"]                      # prereg 2.1
N_BASES = 8                                            # prereg 2.9
N_REPL = 8                                             # prereg 2.9

# Section 2.9 lattices.  (name, d, k, role)
LATTICES = [
    ("L1", 100,  30, "qary"),
    ("L2", 100,  70, "qary"),    # L1 mirror, for REL-2
    ("L3", 100,  50, "qary"),    # the cell AM4-OBS-1's table was measured at
    ("L4", 140,  40, "qary"),
    ("L5", 140, 100, "qary"),    # L4 mirror, for REL-2
    ("L6", 100,  50, "Zd_identity"),   # Z^100 in the identity basis, B = I_d
]
SMALL_LATTICES = [
    ("L7",  20,  6, "qary"),
    ("L8",  20, 14, "qary"),
    ("L9",  30,  9, "qary"),
    ("L10", 30, 21, "qary"),
    ("L11", 40, 12, "qary"),
    ("L12", 40, 28, "qary"),
]
BETA_GRID = {100: [15, 30, 35, 50, 65], 140: [20, 40, 45, 70, 95]}
for _d in (20, 30, 40):
    BETA_GRID[_d] = [int(_d // 4), int(_d // 2), int(3 * _d // 4)]

# prereg 2.5 REL-1 endpoints
REL1_PAIR = {100: (15, 65), 140: (20, 95)}
for _d in (20, 30, 40):
    # NOT pinned by the prereg, which names REL-1 endpoints only for d=100/140.
    # The small-d family exists solely for X9/X10 (prereg 2.3, 2.9), so REL-1 is
    # taken at the endpoints of that family's own declared beta grid. Recorded as
    # an INTERPRETATION in the deviations list; the full ladder is reported so a
    # reviewer can rescore under any other reading.
    REL1_PAIR[_d] = (BETA_GRID[_d][0], BETA_GRID[_d][-1])

# prereg 2.5 REL-2 mirrored cell pairs
REL2_PAIRS = [("L1", "L2"), ("L4", "L5"), ("L7", "L8"), ("L9", "L10"), ("L11", "L12")]

# prereg 2.9: the D arm runs at L3 beta=40 and L4 beta=45 only
D_CELLS = [("L3", 100, 50, 40), ("L4", 140, 40, 45)]
D_N = 2 ** 20
D_CHUNK = 2 ** 16
D_TAIL_INDEX = 1023          # sort(R)[round(2^-10 * 2^20) - 1]
D_POOLS = 3                  # prereg 2.9 E = 3
D_BASES = 4                  # prereg 2.9
D_REPL = 3                   # prereg 2.9

# Budget ladder, prereg 2.9
CAP_TOTAL = 10800.0
CKPT_STAGE1 = 3600.0         # drop mirrors L2/L5 past this
CAP_D_ARM = 3000.0
CAP_X9_PER_LATTICE = 300.0
CAP_X10_PER_PRES = 300.0
CAP_X10_TOTAL = 3600.0

CANDIDATES = ["E_I", "V", "m3", "D", "W", "OD", "TRIV", "rdet", "lam1n", "hkz"]
CAND_XID = {"E_I": "X1", "V": "X2", "m3": "X3", "D": "X4", "W": "X5",
            "OD": "X6", "TRIV": "X7", "rdet": "X8", "lam1n": "X9", "hkz": "X10"}
FP_CLASS = ["E_I", "V", "m3", "W", "OD", "TRIV"]     # declared f(P); confirmed by probe
NON_FP_CLASS = ["rdet", "lam1n", "hkz"]              # declared non-f(P); confirmed by PROBE-L
FRAME_CHEAP = ["E_I", "V", "m3", "W", "OD", "TRIV"]  # computable from one QR

DEVIATIONS = []


def dev(tag, text):
    DEVIATIONS.append({"tag": tag, "note": text})


# ----------------------------------------------------------------------------
# 1. Notarization check -- ABORT ON MISMATCH (prereg 0.3, 7; correction V-7)
# ----------------------------------------------------------------------------

def repo_root():
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def verify_notarization(root):
    p = os.path.join(root, PREREG_REL)
    if not os.path.exists(p):
        raise SystemExit("ABORT: pre-registration not found at %s" % p)
    got = sha256_file(p)
    receipt_path = os.path.join(os.path.dirname(p), "prereg_sha256.txt")
    receipt = open(receipt_path).read().strip().split()[0] if os.path.exists(receipt_path) else None
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                          capture_output=True, text=True, check=True).stdout.strip()
    anc = subprocess.run(["git", "merge-base", "--is-ancestor", NOTARIZING_COMMIT, "HEAD"],
                         cwd=root, capture_output=True, text=True)
    notar_full = subprocess.run(["git", "rev-parse", NOTARIZING_COMMIT], cwd=root,
                                capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                           capture_output=True, text=True, check=True).stdout
    rec = OrderedDict()
    rec["prereg_path"] = PREREG_REL
    rec["sha256_measured"] = got
    rec["sha256_expected_task_card"] = PREREG_SHA256_EXPECTED
    rec["sha256_expected_receipt_file"] = receipt
    rec["sha256_match"] = (got == PREREG_SHA256_EXPECTED)
    rec["receipt_match"] = (receipt == got) if receipt else None
    rec["notarizing_commit"] = NOTARIZING_COMMIT
    rec["notarizing_commit_full"] = notar_full
    rec["assertion"] = "git merge-base --is-ancestor <NOTARIZING COMMIT ITSELF> HEAD"
    rec["notarizing_commit_is_ancestor_of_HEAD"] = (anc.returncode == 0)
    rec["head_commit"] = head
    rec["worktree_dirty"] = bool(dirty.strip())
    rec["worktree_dirty_paths"] = [l[3:] for l in dirty.splitlines()]
    if not rec["sha256_match"]:
        raise SystemExit("ABORT: prereg sha256 mismatch -- harness failure, not a result.")
    if not rec["notarizing_commit_is_ancestor_of_HEAD"]:
        raise SystemExit("ABORT: notarizing commit is not an ancestor of HEAD.")
    return rec


# ----------------------------------------------------------------------------
# 2. Construction: bases, transforms, frames (prereg 2.1, 2.9)
# ----------------------------------------------------------------------------

def make_A(d, k, q, i, rank=None):
    """A = default_rng([1, d, k, i]).integers(0, q, size=(k, d-k))   [prereg 2.9]
    rank-r variant: A = A1 @ A2 mod q with inner dimension r, entries uniform [0,q)."""
    m = d - k
    if rank is None:
        rng = np.random.default_rng([1, d, k, i])
        return rng.integers(0, q, size=(k, m), dtype=np.int64)
    r = int(rank)
    rng = np.random.default_rng([1, d, k, i, r])
    A1 = rng.integers(0, q, size=(k, r), dtype=np.int64)
    A2 = rng.integers(0, q, size=(r, m), dtype=np.int64)
    return (A1 @ A2) % q if q > 1 else np.zeros((k, m), dtype=np.int64)


def build_basis(d, k, q, i, kind="qary", rank=None):
    """B = [[I_k, A], [0, q*I_{d-k}]]  -- built EXPLICITLY in exact integer
    arithmetic, never by a generator (prereg 1.1 / 2.9). K_I = coords 0..k-1,
    K_q = coords k..d-1.  AM-9: k = |K_I|; fpylll's k would be k_fpylll = d-k."""
    if kind == "Zd_identity":
        return np.eye(d, dtype=np.int64)
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, q, i, rank=rank)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def haar_orthogonal(d, rng):
    """Haar-distributed orthogonal matrix (Mezzadri sign correction)."""
    Z = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(Z)
    ph = np.sign(np.diag(R))
    ph[ph == 0] = 1.0
    return Q * ph


def perm_matrix(d, rng):
    p = rng.permutation(d)
    P = np.zeros((d, d), dtype=np.int64)
    P[np.arange(d), p] = 1
    return P


def unimodular(d, rng):
    """random permutation, random sign flip, d/2 elementary R_i <- R_i + s R_j.
    Each factor has determinant +-1 by construction (prereg 2.9)."""
    U = np.eye(d, dtype=np.int64)
    U = U[rng.permutation(d)]
    signs = rng.integers(0, 2, size=d) * 2 - 1
    U = U * signs[:, None]
    for _ in range(d // 2):
        i, j = rng.choice(d, size=2, replace=False)
        s = int(rng.integers(0, 2)) * 2 - 1
        U[i] = U[i] + s * U[j]
    return U


def transformed(B, d, k, beta, h, which):
    """Return (M, aux). T0 uses the SAME H as T1 for replicate h, so its residual
    measures the float64 noise of the identical QR path and nothing else."""
    if which == "id":
        return B.astype(np.float64), {}
    if which in ("T0", "T1"):
        H = haar_orthogonal(d, np.random.default_rng([2, d, k, beta, h]))
        M = B.astype(np.float64) @ H
        if which == "T0":
            M = M @ H.T
        return M, {"H": H}
    if which == "T2":
        Pi = perm_matrix(d, np.random.default_rng([3, d, k, beta, h]))
        return (Pi @ B).astype(np.float64), {"int": Pi @ B}
    if which == "T3":
        U = unimodular(d, np.random.default_rng([4, d, k, beta, h]))
        UB = U @ B
        return UB.astype(np.float64), {"int": UB, "U": U, "maxUB": int(np.max(np.abs(UB))),
                                       "maxU": int(np.max(np.abs(U)))}
    raise ValueError(which)


def frame_Q(M, beta):
    """orthonormal tail-beta GSO frame = last beta columns of Q from QR(M^T)."""
    Q, _ = np.linalg.qr(M.T)
    return np.ascontiguousarray(Q[:, -beta:])


# ----------------------------------------------------------------------------
# 3. The observables (prereg 1, 2.3)
# ----------------------------------------------------------------------------

def E_V_haar(d, beta):
    return 2.0 * beta * (d - beta) / (d * (d + 2.0))


def scale_floor(name, d, beta, k):
    """s_X, prereg 2.2 -- a function of (d, beta, k) alone."""
    if name == "E_I":
        return 1.0
    if name == "V":
        return E_V_haar(d, beta)
    if name == "m3":
        return E_V_haar(d, beta) ** 1.5
    if name == "D":
        return 0.01
    if name == "W":
        return math.sqrt(k * 2.0 * beta * (d - beta) / (d * d * (d + 2.0)))
    if name == "OD":
        return E_V_haar(d, beta)
    if name == "TRIV":
        return float(beta)
    if name in ("rdet", "lam1n", "hkz"):
        return 1.0
    raise ValueError(name)


def frame_observables(Qb, d, k, beta):
    """The six f(P)-class candidates from one frame."""
    diagP = np.einsum("ij,ij->i", Qb, Qb)
    P = Qb @ Qb.T
    sum_d2 = float(np.dot(diagP, diagP))
    triv = float(np.sum(P * P))                       # tr(P^2) = ||P||_F^2
    od = triv - sum_d2                                # sum_{a!=b} P_ab^2
    out = {
        "E_I": float(diagP[:k].sum() / beta),
        "V": sum_d2 - beta * beta / d,
        "m3": float(np.sum((diagP - beta / d) ** 3)),
        "W": float(diagP[:k].sum() - beta * k / d),
        "OD": od,
        "TRIV": triv,
    }
    out["_od_identity_residual"] = abs(od + out["V"] + beta * beta / d - beta)
    return out


def rdet_of(M, d):
    sign, logabs = np.linalg.slogdet(M)
    return float(np.exp(logabs / d)), float(logabs)


# --- X9 / X10 via the integer Gram matrix -----------------------------------
try:
    from fpylll import IntegerMatrix, GSO, LLL, BKZ, Enumeration, EnumerationError
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz import BKZReduction
    HAVE_FPYLLL = True
    import fpylll as _fp
    FPYLLL_VERSION = _fp.__version__
except Exception as _e:                                  # pragma: no cover
    HAVE_FPYLLL = False
    FPYLLL_VERSION = "IMPORT FAILED: %s" % _e


def _to_im(Mi):
    A = IntegerMatrix(Mi.shape[0], Mi.shape[1])
    for i in range(Mi.shape[0]):
        for j in range(Mi.shape[1]):
            A[i, j] = int(Mi[i, j])
    return A


def gram_int(M):
    """Integer Gram matrix of the row lattice of M, with the float integrality
    deviation reported.  G = M M^T is integral whenever the underlying basis is
    integral, and an ambient isometry preserves it EXACTLY in exact arithmetic --
    so for T0/T1 this pipeline is structurally invariant and its residual measures
    only Gram-formation float noise.  Disclosed in the report; not a hidden pass."""
    G = M @ M.T
    Gr = np.rint(G)
    devmax = float(np.max(np.abs(G - Gr))) if G.size else 0.0
    return Gr.astype(object), devmax, float(np.max(np.abs(Gr)))


HKZ_MAX_SWEEP = 30


def hkz_profile(M, d, verify=True):
    """HKZ-reduce the row lattice of M and return its GSO profile.

    Reduction: one BKZ pass at block_size = d, then repeated sweeps in which each
    index i is enumerated over the projected block [i, d) and any STRICTLY shorter
    projected vector is inserted.  The explicit sweep is necessary: fpylll's
    BKZReduction.svp_call discards any improvement not better than lll_delta =
    0.99 * r_i, which leaves a basis that is NOT HKZ by up to ~0.8% at some
    indices (observed at d = 30 before this pass was added).

    verify=True then re-runs an INDEPENDENT enumeration at every index and reports
    hkz_violation = max_i (r_i - lambda_1(pi_i(L))^2)/r_i.  A run with
    hkz_violation > 0 has NOT achieved HKZ, the arm is labelled NON-CANONICAL for
    that presentation, and per prereg 2.9 step 4 its residual is UNINFORMATIVE for
    G-INV.  This is an INSTRUMENT CHECK, not a certificate.

    One reduction yields BOTH X9 (lam1n, from r_0 = lambda_1^2) and X10 (hkz, the
    tail-beta window of the profile) at every beta.
    """
    if not HAVE_FPYLLL:
        return {"status": "NOT MEASURED -- INFRASTRUCTURE (fpylll unavailable)"}
    t0 = time.time()
    Gr, devmax, gmax = gram_int(M)
    if devmax >= 0.5:
        return {"status": "NOT ADJUDICATED -- Gram integrality deviation %.3e >= 0.5" % devmax,
                "gram_int_dev": devmax}
    Gnp = np.array(Gr.tolist(), dtype=object)
    try:
        A = IntegerMatrix(d, d)
        for i in range(d):
            for j in range(d):
                A[i, j] = int(Gnp[i, j])
        Mg = GSO.Mat(A, gram=True)
        Mg.update_gso()
        LLL.Reduction(Mg)()
        strat = [Strategy(b) for b in range(d + 1)]
        bk = BKZReduction(Mg)
        bk(BKZ.Param(block_size=d, strategies=strat, max_loops=1, flags=BKZ.MAX_LOOPS))
        sweeps = 0
        for sweeps in range(HKZ_MAX_SWEEP):
            changed = False
            for i in range(d - 1):
                ri = Mg.get_r(i, i)
                try:
                    nd, sol = Enumeration(Mg).enumerate(i, d, ri, 0)[0]
                except EnumerationError:
                    continue
                if nd < ri * (1 - 1e-12):
                    bk.svp_postprocessing(i, d - i, sol)
                    Mg.update_gso()
                    changed = True
            if not changed:
                break
        r = np.array([Mg.get_r(i, i) for i in range(d)], dtype=float)
        viol = None
        if verify:
            viol = 0.0
            for i in range(d - 1):
                try:
                    mn = Enumeration(Mg).enumerate(i, d, r[i] * 1.0000001, 0)[0][0]
                except EnumerationError:
                    mn = r[i]
                viol = max(viol, (r[i] - mn) / r[i])
    except Exception as ex:
        return {"status": "NOT MEASURED -- INFRASTRUCTURE (%s: %s)" % (type(ex).__name__, ex)}
    logdet = 0.5 * float(np.sum(np.log(r)))
    return {"status": "ok", "r": r, "lam1sq": float(r[0]), "logdet": logdet,
            "gram_int_dev": devmax, "gram_max": gmax, "hkz_violation": viol,
            "sweeps": sweeps, "secs": time.time() - t0}


def x9_x10_from_profile(prof, d, beta):
    if prof.get("status") != "ok":
        return None, None
    r = prof["r"]
    logdet = prof["logdet"]
    lam1n = math.exp(0.5 * math.log(prof["lam1sq"]) - logdet / d)
    logb = 0.5 * np.log(r)
    hkz = float(np.mean(logb[d - beta:]) - logdet / d)
    return lam1n, hkz


# --- X4 = D ------------------------------------------------------------------

def cbd2_pool(d, p, n=D_N, chunk=D_CHUNK):
    """E = 3 independent pools of N = 2^20 CBD_{eta=2} vectors, rng seed
    default_rng([7, d, p]) (prereg 2.9, TAG 7). Stored int8, generated in chunks."""
    rng = np.random.default_rng([7, d, p])
    out = np.empty((n, d), dtype=np.int8)
    for s in range(0, n, chunk):
        e = min(chunk, n - s)
        a = rng.binomial(2, 0.5, size=(e, d))
        b = rng.binomial(2, 0.5, size=(e, d))
        out[s:s + e] = (a - b).astype(np.int8)
    return out


def D_from_frame(Qb, pool, sqn, d, beta, qbeta, chunk=D_CHUNK):
    """D = q_emp(2^-10)/q_Beta(2^-10) - 1, q_emp = sort(R)[1023] at N = 2^20."""
    n = pool.shape[0]
    R = np.empty(n, dtype=np.float64)
    for s in range(0, n, chunk):
        e = min(chunk, n - s)
        Ec = pool[s:s + e].astype(np.float64)
        Y = Ec @ Qb
        R[s:s + e] = np.einsum("ij,ij->i", Y, Y) / sqn[s:s + e]
    q_emp = float(np.partition(R, D_TAIL_INDEX)[D_TAIL_INDEX])
    return q_emp / qbeta - 1.0, q_emp


# ----------------------------------------------------------------------------
# 4. residual
# ----------------------------------------------------------------------------

def rho(xt, xb, s):
    return abs(xt - xb) / max(abs(xb), s)


def agg(vals):
    if not vals:
        return None
    a = np.asarray(vals, dtype=float)
    return {"min": float(a.min()), "median": float(np.median(a)),
            "max": float(a.max()), "n": int(a.size)}


# ============================================================================
# MAIN
# ============================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    root = repo_root()
    notar = verify_notarization(root)
    print("[notarization] prereg sha256 = %s  MATCH=%s" % (notar["sha256_measured"], notar["sha256_match"]))
    print("[notarization] %s ancestor-of-HEAD = %s (HEAD %s)"
          % (NOTARIZING_COMMIT, notar["notarizing_commit_is_ancestor_of_HEAD"], notar["head_commit"][:9]))

    # Protocol interpretations and additions, DECLARED BEFORE ANY RESULT IS COMPUTED.
    dev("INTERPRETATION",
        "REL-1 endpoints are pinned by prereg 2.5 only for d = 100 and d = 140. X9/X10 are 'small d only' "
        "(prereg 2.3) on the family L7..L12 whose beta grid is {d/4, d/2, 3d/4} (prereg 2.9). REL-1 for those "
        "candidates is therefore taken at the endpoints of that declared grid, (d/4, 3d/4). The full ladder is "
        "reported so a reviewer can rescore under any other reading.")
    dev("INTERPRETATION",
        "L6 = Z^100 in the identity basis carries no k in prereg 2.9, but E_I and W need K_I. k = 50 (= d/2) is "
        "used, which is L3's value; disclosed rather than silently chosen.")
    dev("INTERPRETATION",
        "The q-ladder is run on the FROZEN construction of prereg 2.9, A = default_rng([1,d,k,i]).integers(0,q), "
        "under which A = 0 at q = 1 and the q = 1 basis is exactly I_d. A SUPPLEMENTARY ladder-B (A held at "
        "q = 3329 while only the lower block is scaled by q, so that q = 1 is Z^d in a NON-identity basis, which "
        "is the object the BATCH-a44d08 red team's ladder used) is reported separately, labelled POST-HOC and "
        "UNCITABLE AS A RESULT per prereg section 5 rule 6.")
    dev("ADDITION",
        "PROBE-L, a SUPPLEMENTARY frame-collision, is added and labelled as such. GEN-2 requires each "
        "candidate's class to be decided by measurement rather than assertion, and the frozen "
        "diagonal-collision probe is undefined on X8/X9/X10 because those are not functions of a projector at "
        "all. PROBE-L scales rows 1..d-beta of B, which leaves span(rows 1..d-beta) and hence the tail-beta "
        "frame EXACTLY unchanged while changing the lattice. It does not replace the frozen probe, which is "
        "run exactly as specified.")
    dev("DISCLOSURE",
        "X9/X10 are computed through the integer Gram matrix G = M M^T (fpylll GSO.Mat(gram=True)), which is "
        "the only route this environment offers for a non-integer presentation. G is EXACTLY preserved by an "
        "ambient isometry in exact arithmetic, so the T0/T1 residuals for X9/X10 are structurally near-zero and "
        "measure only Gram-formation float noise -- they are a WEAK test. The T2 and T3 residuals ARE genuine: "
        "the Gram matrix genuinely changes (Pi G Pi^T, U G U^T) and the reduction must recover the same "
        "invariant from a different starting basis. gram_int_dev, the pre-rounding integrality deviation, is "
        "reported per presentation.")
    dev("DISCLOSURE",
        "The X9/X10 reduction is one BKZ pass at block_size = d followed by explicit HKZ sweeps, because "
        "fpylll's BKZReduction.svp_call discards improvements below lll_delta = 0.99 * r_i and therefore does "
        "NOT reach HKZ (violations up to 7.6e-3 observed at d = 30 before the sweep was added). Every reduction "
        "is verified by an independent per-index enumeration; a presentation with hkz_violation > 0 is "
        "NON-CANONICAL and its residual is reported as uninformative for G-INV per prereg 2.9 step 4.")
    dev("DISCLOSURE",
        "The transform seed formula default_rng([TAG,d,k,beta,h]) includes beta. For X9/X10 the HKZ-reduced "
        "basis does not depend on beta (only the readout window does), so ONE reduction per presentation "
        "serves every beta and the transform seed uses beta = d/2 for those arms.")
    dev("DISCLOSURE",
        "The rank-r factors use default_rng([1,d,k,i,r]); prereg 2.9 pins TAG 1 for 'the basis matrix A (and "
        "its rank-r factors)' and gives the un-ranked form default_rng([1,d,k,i]) explicitly, so r is appended.")
    dev("ADDITION",
        "The rank sweep is reported on the frozen beta grid AND on a finer grid beta = 1..min(k+5, d-k), "
        "because the departure index b*(X) of G-RANK is resolved only to the grid it is read on. Both are in "
        "the JSON; b* is computed on the union.")

    smoke = args.smoke
    lattices = LATTICES[:2] if smoke else LATTICES
    small = SMALL_LATTICES[:2] if smoke else SMALL_LATTICES
    nb = 2 if smoke else N_BASES
    nr = 2 if smoke else N_REPL

    RES = OrderedDict()
    RES["task"] = "TASK-20260808-2a9085"
    RES["batch"] = "BATCH-cbe023"
    RES["goal"] = "GOAL-MLKEM-005"
    RES["section"] = "A -- the AM-4 admissibility gate"
    RES["claim_tier"] = "TOY"
    RES["certificate"] = {"kind": "none",
                          "reason": "no discrete-log solve and no factor-base relation is claimed or produced"}
    RES["notarization"] = notar
    RES["thresholds"] = {"tau_num": TAU_NUM, "tau_inv": TAU_INV, "tau_q": TAU_Q,
                         "tau_rel": TAU_REL, "od_identity_tol": OD_IDENTITY_TOL}
    RES["k_convention_AM9"] = ("k = |K_I| = size of the IDENTITY block throughout. "
                               "fpylll's k counts the q-scaled rows: k_fpylll = d - k. "
                               "Every basis here is BUILT EXPLICITLY as [[I_k, A],[0, q I_{d-k}]]; "
                               "no fpylll basis generator is called anywhere in this script.")
    RES["environment"] = {
        "python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
        "fpylll": FPYLLL_VERSION, "platform": platform.platform(), "host": socket.gethostname(),
        "blas_threads_env": {k: os.environ.get(k) for k in
                             ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"]},
        "gmpy2": "ABSENT (verified: nothing here depends on it)",
    }
    RES["smoke"] = smoke

    # ------------------------------------------------------------------
    # 4.1  INSTRUMENT CHECKS run before any candidate is judged
    # ------------------------------------------------------------------
    print("\n[instrument checks]")
    ic = OrderedDict()

    # (a) det(U) = +-1, exactly, with sympy at d <= 40 (prereg 2.9)
    import sympy
    detU = []
    for d in (20, 30, 40):
        for h in range(4):
            U = unimodular(d, np.random.default_rng([4, d, d // 3, d // 2, h]))
            detU.append(int(sympy.Matrix(U.tolist()).det()))
    ic["detU_exact_sympy_d_le_40"] = {"values": detU, "all_pm1": all(abs(v) == 1 for v in detU)}
    print("  det(U) exact (sympy, d<=40): all +-1 = %s" % ic["detU_exact_sympy_d_le_40"]["all_pm1"])

    # (b) Gram-path enumeration vs exact-basis enumeration (independent of the
    #     solver used for X9/X10): a genuine cross-check of the X9/X10 pipeline.
    if HAVE_FPYLLL:
        xchk = []
        for (nm, d, k, kind) in SMALL_LATTICES:
            B = build_basis(d, k, Q_MAIN, 0, kind)
            Mb = GSO.Mat(_to_im(B)); Mb.update_gso(); LLL.Reduction(Mb)()
            lam_basis = Enumeration(Mb).enumerate(0, d, Mb.get_r(0, 0), 0)[0][0]
            prof = hkz_profile(B.astype(np.float64), d)
            xchk.append({"lattice": nm, "d": d, "k_identity_block": k,
                         "lam1sq_basis_LLL_enum": float(lam_basis),
                         "lam1sq_gram_HKZ_r0": prof.get("lam1sq"),
                         "match": abs(float(lam_basis) - float(prof.get("lam1sq", -1))) < 1e-6})
        ic["x9_pipeline_crosscheck"] = xchk
        print("  X9 Gram-HKZ r0 vs independent basis-LLL+enum lambda_1^2: %d/%d match"
              % (sum(1 for c in xchk if c["match"]), len(xchk)))
    else:
        ic["x9_pipeline_crosscheck"] = "NOT MEASURED -- INFRASTRUCTURE (fpylll unavailable)"

    RES["instrument_checks"] = ic

    # ------------------------------------------------------------------
    # 4.2  OBS-GEN numerical corollaries (prereg 2.4 / GEN-1)
    #      OD + V + beta^2/d = beta  at EVERY frame, to <= 1e-10
    # ------------------------------------------------------------------
    od_res = []

    # ------------------------------------------------------------------
    # 4.3  THE DIAGONAL-COLLISION PROBE (prereg 2.4) -- the test that could
    #      REFUTE AM4-OBS-1's premise.  Frozen construction.
    # ------------------------------------------------------------------
    print("\n[collision probe -- pre-registered, could refute AM4-OBS-1's premise]")
    cp_d, cp_k, cp_beta = 100, 50, 40
    u_lo, u_hi = 0.25, 0.75
    a_idx = np.arange(cp_beta) * 2
    b_idx = np.arange(cp_beta) * 2 + 1
    u = np.where(np.arange(cp_beta) < cp_beta // 2, u_lo, u_hi)
    # sigma permutes the a-indices among themselves, WITHIN each u-level set (a
    # cyclic shift), so diag(P2) = diag(P1) exactly while P2 != P1 off-diagonal.
    sigma = np.arange(cp_beta)
    g1 = np.arange(0, cp_beta // 2); g2 = np.arange(cp_beta // 2, cp_beta)
    sigma[g1] = np.roll(g1, 1)
    sigma[g2] = np.roll(g2, 1)
    V1 = np.zeros((cp_d, cp_beta)); V2 = np.zeros((cp_d, cp_beta))
    for m in range(cp_beta):
        V1[a_idx[m], m] = math.sqrt(u[m]);      V1[b_idx[m], m] = math.sqrt(1 - u[m])
        V2[a_idx[sigma[m]], m] = math.sqrt(u[m]); V2[b_idx[m], m] = math.sqrt(1 - u[m])
    P1 = V1 @ V1.T; P2 = V2 @ V2.T
    coll_rec = OrderedDict()
    coll_rec["construction"] = ("two-level frame on 2*beta coordinates paired (a_m,b_m) with diagonal "
                                "(u,1-u), u in {0.25,0.75}; P2 is the same construction with the "
                                "a-indices cyclically permuted WITHIN each u-level set")
    coll_rec["d"], coll_rec["k"], coll_rec["beta"] = cp_d, cp_k, cp_beta
    coll_rec["sigma_is_identity"] = bool(np.array_equal(sigma, np.arange(cp_beta)))
    coll_rec["orthonormality_V1"] = float(np.max(np.abs(V1.T @ V1 - np.eye(cp_beta))))
    coll_rec["orthonormality_V2"] = float(np.max(np.abs(V2.T @ V2 - np.eye(cp_beta))))
    coll_rec["diag_collision_max_abs_diff"] = float(np.max(np.abs(np.diag(P1) - np.diag(P2))))
    coll_rec["offdiag_max_abs_diff"] = float(np.max(np.abs(P1 - P2)))
    coll_rec["rank_P1"] = int(round(np.trace(P1))); coll_rec["rank_P2"] = int(round(np.trace(P2)))
    o1 = frame_observables(V1, cp_d, cp_k, cp_beta)
    o2 = frame_observables(V2, cp_d, cp_k, cp_beta)
    coll_rec["per_candidate"] = OrderedDict()
    for nm in FRAME_CHEAP:
        s = scale_floor(nm, cp_d, cp_beta, cp_k)
        c = rho(o2[nm], o1[nm], s)
        verdict = ("DIAGONAL-DETERMINED on this probe (AM4-OBS-1 premise holds for X)" if c <= TAU_NUM
                   else ("NOT a function of diag alone (AM4-OBS-1 premise REFUTED for X)" if c > TAU_INV
                         else "INDETERMINATE at the probe's resolution"))
        coll_rec["per_candidate"][nm] = {"xid": CAND_XID[nm], "X_P1": o1[nm], "X_P2": o2[nm],
                                         "s_X": s, "coll": c, "verdict": verdict}
        print("  coll(%-5s) = %.3e  -> %s" % (nm, c, verdict.split("(")[0].strip()))
    RES["collision_probe"] = coll_rec

    # ------------------------------------------------------------------
    # 4.4  SUPPLEMENTARY frame-collision for the lattice candidates (PROBE-L).
    #      NOT pre-registered. GEN-2 requires each candidate's class to be
    #      decided BY MEASUREMENT rather than by assertion, and the frozen
    #      diagonal-collision probe is undefined on X8/X9/X10 (they are not
    #      functions of a projector at all). PROBE-L supplies the measurement:
    #      scaling rows 1..d-beta of B leaves span(rows 1..d-beta) unchanged,
    #      hence leaves the tail-beta frame P EXACTLY unchanged, while changing
    #      the lattice.  Labelled SUPPLEMENTARY throughout.
    # ------------------------------------------------------------------
    print("\n[PROBE-L -- SUPPLEMENTARY frame-collision for the lattice candidates]")
    pl_d, pl_k, pl_beta = 40, 12, 30
    Bl = build_basis(pl_d, pl_k, Q_MAIN, 0, "qary")
    C = np.ones(pl_d, dtype=np.int64); C[: pl_d - pl_beta] = 3      # scale rows 1..d-beta by 3
    Bl2 = (np.diag(C) @ Bl)
    Qa = frame_Q(Bl.astype(np.float64), pl_beta)
    Qb2 = frame_Q(Bl2.astype(np.float64), pl_beta)
    Pa = Qa @ Qa.T; Pb = Qb2 @ Qb2.T
    pl = OrderedDict()
    pl["status"] = "SUPPLEMENTARY -- not pre-registered; used only to discharge GEN-2's class determination"
    pl["construction"] = ("B' = diag(3,...,3,1,...,1) B scaling rows 1..d-beta only; span(rows 1..d-beta) "
                          "is unchanged so the tail-beta frame is unchanged, but the lattice is a proper sublattice")
    pl["d"], pl["k"], pl["beta"] = pl_d, pl_k, pl_beta
    pl["frame_collision_max_abs_P_diff"] = float(np.max(np.abs(Pa - Pb)))
    oa = frame_observables(Qa, pl_d, pl_k, pl_beta); ob = frame_observables(Qb2, pl_d, pl_k, pl_beta)
    pl["per_candidate"] = OrderedDict()
    for nm in FRAME_CHEAP:
        s = scale_floor(nm, pl_d, pl_beta, pl_k)
        pl["per_candidate"][nm] = {"xid": CAND_XID[nm], "X_B": oa[nm], "X_Bprime": ob[nm],
                                   "s_X": s, "collL": rho(ob[nm], oa[nm], s),
                                   "class": "f(P): constant on the frame collision"}
    ra, _ = rdet_of(Bl.astype(np.float64), pl_d); rb, _ = rdet_of(Bl2.astype(np.float64), pl_d)
    pl["per_candidate"]["rdet"] = {"xid": "X8", "X_B": ra, "X_Bprime": rb, "s_X": 1.0,
                                   "collL": rho(rb, ra, 1.0),
                                   "class": "NOT f(P): separates two lattices with the identical tail frame"}
    prof_a = hkz_profile(Bl.astype(np.float64), pl_d); prof_b = hkz_profile(Bl2.astype(np.float64), pl_d)
    l9a, l10a = x9_x10_from_profile(prof_a, pl_d, pl_beta)
    l9b, l10b = x9_x10_from_profile(prof_b, pl_d, pl_beta)
    for nm, va, vb in (("lam1n", l9a, l9b), ("hkz", l10a, l10b)):
        if va is None:
            pl["per_candidate"][nm] = {"xid": CAND_XID[nm], "status": "NOT MEASURED -- INFRASTRUCTURE"}
        else:
            pl["per_candidate"][nm] = {"xid": CAND_XID[nm], "X_B": va, "X_Bprime": vb, "s_X": 1.0,
                                       "collL": rho(vb, va, 1.0),
                                       "class": "NOT f(P): separates two lattices with the identical tail frame"}
    RES["probe_L_supplementary"] = pl
    for nm, v in pl["per_candidate"].items():
        if "collL" in v:
            print("  collL(%-5s) = %.4e" % (nm, v["collL"]))

    # ------------------------------------------------------------------
    # 4.5  STAGE 1 -- the AM-4 triple over X1,X2,X3,X5,X6,X7,X8 on L1..L6
    # ------------------------------------------------------------------
    print("\n[stage 1: AM-4 triple, X1 X2 X3 X5 X6 X7 X8 on L1..L6]")
    inv = OrderedDict()          # name -> lattice -> beta -> transform -> agg
    base_vals = OrderedDict()    # (lattice,beta,i) -> {name: value}
    t3_growth = []
    dropped_mirrors = False
    stage1_notes = []

    for (nm_lat, d, k, kind) in lattices:
        if dropped_mirrors and nm_lat in ("L2", "L5"):
            stage1_notes.append("%s DROPPED at the 3600 s checkpoint; REL-2 recorded NOT MEASURED for it" % nm_lat)
            continue
        if time.time() - T_START > CKPT_STAGE1 and not dropped_mirrors:
            dropped_mirrors = True
            dev("BUDGET", "3600 s stage-1 checkpoint bound; mirrors L2/L5 dropped per prereg 2.9 ladder")
            if nm_lat in ("L2", "L5"):
                stage1_notes.append("%s DROPPED at the 3600 s checkpoint" % nm_lat)
                continue
        nbi = 1 if kind == "Zd_identity" else nb
        for beta in BETA_GRID[d]:
            for i in range(nbi):
                B = build_basis(d, k, Q_MAIN, i, kind)
                Qb0 = frame_Q(B.astype(np.float64), beta)
                base = frame_observables(Qb0, d, k, beta)
                od_res.append(base.pop("_od_identity_residual"))
                base["rdet"], _ = rdet_of(B.astype(np.float64), d)
                base_vals[(nm_lat, beta, i)] = base
                for which in ("T0", "T1", "T2", "T3"):
                    for h in range(nr):
                        M, aux = transformed(B, d, k, beta, h, which)
                        Qt = frame_Q(M, beta)
                        ov = frame_observables(Qt, d, k, beta)
                        od_res.append(ov.pop("_od_identity_residual"))
                        ov["rdet"], _ = rdet_of(M, d)
                        if which == "T3":
                            t3_growth.append({"lattice": nm_lat, "d": d, "beta": beta, "basis": i,
                                              "repl": h, "max_abs_UB": aux["maxUB"], "max_abs_U": aux["maxU"]})
                        for nmv in FRAME_CHEAP + ["rdet"]:
                            s = scale_floor(nmv, d, beta, k)
                            r = rho(ov[nmv], base[nmv], s)
                            inv.setdefault(nmv, OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                               .setdefault(str(beta), OrderedDict()).setdefault(which, []).append(r)
        print("  %s (d=%d,k=%d,%s) done  t=%.0fs" % (nm_lat, d, k, kind, time.time() - T_START))

    # PRED-A1: T1 means against the exact Haar targets
    print("\n[PRED-A1: T1 means vs exact Haar targets]")
    preda1 = []
    for (nm_lat, d, k, kind) in lattices:
        if kind == "Zd_identity":
            continue
        if (nm_lat, BETA_GRID[d][0], 0) not in base_vals:
            continue
        for beta in BETA_GRID[d]:
            eis, vs = [], []
            B = build_basis(d, k, Q_MAIN, 0, kind)
            for h in range(nr):
                M, _ = transformed(B, d, k, beta, h, "T1")
                o = frame_observables(frame_Q(M, beta), d, k, beta)
                eis.append(o["E_I"]); vs.append(o["V"])
            eis = np.array(eis); vs = np.array(vs)
            se_e = float(eis.std(ddof=1) / math.sqrt(len(eis))); se_v = float(vs.std(ddof=1) / math.sqrt(len(vs)))
            tol_e = max(4 * se_e, 0.02); tol_v = max(4 * se_v, 0.02 * E_V_haar(d, beta))
            preda1.append({
                "lattice": nm_lat, "d": d, "k": k, "beta": beta,
                "mean_E_I_T1": float(eis.mean()), "target_k_over_d": k / d,
                "abs_dev_E_I": abs(float(eis.mean()) - k / d), "tol_E_I": tol_e,
                "E_I_within": abs(float(eis.mean()) - k / d) <= tol_e,
                "mean_V_T1": float(vs.mean()), "target_EV_haar": E_V_haar(d, beta),
                "abs_dev_V": abs(float(vs.mean()) - E_V_haar(d, beta)), "tol_V": tol_v,
                "V_within": abs(float(vs.mean()) - E_V_haar(d, beta)) <= tol_v})
    RES["PRED_A1"] = {"statement": "under T1, mean E_I within max(4 SE, 0.02) of k/d and mean V within "
                                   "max(4 SE, 0.02*E[V]_haar) of E[V]_haar",
                      "rows": preda1,
                      "E_I_pass_frac": (sum(1 for r in preda1 if r["E_I_within"]), len(preda1)),
                      "V_pass_frac": (sum(1 for r in preda1 if r["V_within"]), len(preda1))}
    print("  E_I within tol at %d/%d cells; V within tol at %d/%d cells"
          % (RES["PRED_A1"]["E_I_pass_frac"] + RES["PRED_A1"]["V_pass_frac"]))

    # ------------------------------------------------------------------
    # 4.6  q-SWEEP and RANK-SWEEP for the frame + rdet candidates
    # ------------------------------------------------------------------
    print("\n[q-sweep to q=1 and rank sweep]")
    SWEEP_CELLS = [("L1", 100, 30), ("L4", 140, 40)]
    qsweep = OrderedDict()
    qsweep_supp = OrderedDict()
    for (nm_lat, d, k) in SWEEP_CELLS:
        if (nm_lat, BETA_GRID[d][0], 0) not in base_vals:
            continue
        for beta in BETA_GRID[d]:
            for q in Q_LADDER:
                # FROZEN reading: A = default_rng([1,d,k,i]).integers(0,q) (prereg 2.9)
                B = build_basis(d, k, q, 0, "qary")
                o = frame_observables(frame_Q(B.astype(np.float64), beta), d, k, beta)
                o.pop("_od_identity_residual")
                o["rdet"], _ = rdet_of(B.astype(np.float64), d)
                for nmv in FRAME_CHEAP + ["rdet"]:
                    qsweep.setdefault(nmv, OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                          .setdefault(str(beta), OrderedDict())[str(q)] = o[nmv]
                # SUPPLEMENTARY / POST-HOC ladder-B: A drawn once at q=3329 and held
                # fixed while only the lower block is scaled by q. At q=1 this is Z^d
                # in a NON-identity basis, which is the object the BATCH-a44d08 red
                # team's q-ladder used. Labelled POST-HOC and uncitable as a result.
                Bs = build_basis(d, k, Q_MAIN, 0, "qary").copy()
                Bs[k:, k:] = q * np.eye(d - k, dtype=np.int64)
                os_ = frame_observables(frame_Q(Bs.astype(np.float64), beta), d, k, beta)
                os_.pop("_od_identity_residual")
                os_["rdet"], _ = rdet_of(Bs.astype(np.float64), d)
                for nmv in FRAME_CHEAP + ["rdet"]:
                    qsweep_supp.setdefault(nmv, OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                               .setdefault(str(beta), OrderedDict())[str(q)] = os_[nmv]

    ranksweep = OrderedDict()
    for (nm_lat, d, k) in SWEEP_CELLS:
        if (nm_lat, BETA_GRID[d][0], 0) not in base_vals:
            continue
        ranks = [r for r in RANK_LADDER[:-1] if r <= k] + [k]
        for r in ranks:
            B = build_basis(d, k, Q_MAIN, 0, "qary", rank=r)
            Ablk = B[:k, k:]
            rk = int(np.linalg.matrix_rank(Ablk.astype(np.float64)))
            fine = sorted(set(BETA_GRID[d] + list(range(1, min(k + 6, d - k + 1)))))
            Qfull, _ = np.linalg.qr(B.astype(np.float64).T)
            for beta in fine:
                Qb = np.ascontiguousarray(Qfull[:, -beta:])
                o = frame_observables(Qb, d, k, beta); o.pop("_od_identity_residual")
                o["rdet"], _ = rdet_of(B.astype(np.float64), d)
                for nmv in FRAME_CHEAP + ["rdet"]:
                    ranksweep.setdefault(nmv, OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                             .setdefault(str(r), OrderedDict())[str(beta)] = o[nmv]
            ranksweep.setdefault("_rank_realized", OrderedDict()).setdefault(nm_lat, OrderedDict())[str(r)] = rk

    # ------------------------------------------------------------------
    # 4.7  X9 / X10 on the small-d family, all transforms
    # ------------------------------------------------------------------
    print("\n[X9 lam1n and X10 hkz on the small-d family L7..L12]")
    x9_status = OrderedDict(); x10_status = OrderedDict()
    t_x10_total = 0.0
    small_base = OrderedDict()
    canon = {"informative": 0, "noncanonical": 0, "violations": [], "sweeps_max": 0}
    inv_canon = OrderedDict()     # canonical-subset residuals for X9/X10
    for (nm_lat, d, k, kind) in small:
        t_lat0 = time.time()
        capped = False
        for i in range(nb):
            B = build_basis(d, k, Q_MAIN, i, kind)
            prof0 = hkz_profile(B.astype(np.float64), d)
            if prof0.get("status") != "ok":
                x9_status[nm_lat] = prof0.get("status"); capped = True; break
            canon["violations"].append(prof0["hkz_violation"])
            canon["sweeps_max"] = max(canon["sweeps_max"], prof0["sweeps"])
            for beta in BETA_GRID[d]:
                l9, l10 = x9_x10_from_profile(prof0, d, beta)
                small_base[(nm_lat, beta, i)] = {"lam1n": l9, "hkz": l10}
            for which in ("T0", "T1", "T2", "T3"):
                for h in range(nr):
                    if time.time() - t_lat0 > CAP_X9_PER_LATTICE or t_x10_total > CAP_X10_TOTAL:
                        capped = True; break
                    beta_seed = BETA_GRID[d][1]
                    M, aux = transformed(B, d, k, beta_seed, h, which)
                    tt = time.time()
                    prof = hkz_profile(M, d)
                    t_x10_total += time.time() - tt
                    if prof.get("status") != "ok":
                        x10_status.setdefault(nm_lat, []).append(prof.get("status")); continue
                    canon["violations"].append(prof["hkz_violation"])
                    canon["sweeps_max"] = max(canon["sweeps_max"], prof["sweeps"])
                    # A pair is CANONICAL, hence informative for G-INV, only if BOTH
                    # the baseline and the transformed presentation reached verified
                    # HKZ. Otherwise prereg 2.9 step 4 makes its residual uninformative.
                    pair_canon = (prof0["hkz_violation"] == 0.0 and prof["hkz_violation"] == 0.0)
                    canon["informative" if pair_canon else "noncanonical"] += 1
                    for beta in BETA_GRID[d]:
                        l9, l10 = x9_x10_from_profile(prof, d, beta)
                        b9, b10 = small_base[(nm_lat, beta, i)]["lam1n"], small_base[(nm_lat, beta, i)]["hkz"]
                        for nmv, tv, bv in (("lam1n", l9, b9), ("hkz", l10, b10)):
                            rv = rho(tv, bv, 1.0)
                            inv.setdefault(nmv, OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                               .setdefault(str(beta), OrderedDict()).setdefault(which, []).append(rv)
                            if pair_canon:
                                inv_canon.setdefault(nmv, OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                                    .setdefault(str(beta), OrderedDict()).setdefault(which, []).append(rv)
                    inv.setdefault("_gram_int_dev", OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                       .setdefault(which, []).append(prof["gram_int_dev"])
                if capped:
                    break
            if capped:
                break
        if capped:
            dev("BUDGET", "%s: X9/X10 cap bound (300 s per lattice / 3600 s total) -- arm NOT MEASURED beyond "
                          "what is recorded; INFRASTRUCTURE, never a refusal" % nm_lat)
        print("  %s (d=%d,k=%d) t=%.1fs capped=%s" % (nm_lat, d, k, time.time() - t_lat0, capped))
    canon["max_hkz_violation"] = max(canon["violations"]) if canon["violations"] else None
    canon["n_reductions"] = len(canon["violations"])
    canon["all_verified_HKZ"] = bool(canon["violations"]) and max(canon["violations"]) == 0.0
    canon.pop("violations")
    RES["hkz_canonicality"] = canon
    print("  HKZ verification: %d reductions, max violation %s, all verified HKZ = %s; "
          "%d informative / %d non-canonical transform pairs"
          % (canon["n_reductions"], canon["max_hkz_violation"], canon["all_verified_HKZ"],
             canon["informative"], canon["noncanonical"]))

    # q-sweep and rank sweep for X9/X10 at a small-d cell
    sm_cell = ("L11", 40, 12) if not smoke else ("L7", 20, 6)
    nm_lat, d, k = sm_cell
    for q in Q_LADDER:
        B = build_basis(d, k, q, 0, "qary")
        prof = hkz_profile(B.astype(np.float64), d)
        for beta in BETA_GRID[d]:
            l9, l10 = x9_x10_from_profile(prof, d, beta)
            for nmv, val in (("lam1n", l9), ("hkz", l10)):
                qsweep.setdefault(nmv, OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                      .setdefault(str(beta), OrderedDict())[str(q)] = val
    for (nm_lat2, d2, k2) in [sm_cell]:
        ranks = [r for r in RANK_LADDER[:-1] if r <= k2] + [k2]
        for r in ranks:
            B = build_basis(d2, k2, Q_MAIN, 0, "qary", rank=r)
            prof = hkz_profile(B.astype(np.float64), d2)
            for beta in sorted(set(BETA_GRID[d2] + list(range(1, min(k2 + 6, d2 - k2 + 1))))):
                l9, l10 = x9_x10_from_profile(prof, d2, beta)
                for nmv, val in (("lam1n", l9), ("hkz", l10)):
                    ranksweep.setdefault(nmv, OrderedDict()).setdefault(nm_lat2, OrderedDict()) \
                             .setdefault(str(r), OrderedDict())[str(beta)] = val
    # mirrored small-d cells for REL-2 of X9/X10 already covered by small_base

    # ------------------------------------------------------------------
    # 4.8  X4 = D
    # ------------------------------------------------------------------
    print("\n[X4 = D arm]")
    t_d0 = time.time()
    d_arm = OrderedDict()
    d_arm["status"] = "ok"
    d_pools_used = D_POOLS
    d_evals = 0
    for (nm_lat, d, k, beta) in (D_CELLS if not smoke else D_CELLS[:1]):
        if time.time() - t_d0 > CAP_D_ARM:
            d_arm.setdefault("not_measured", []).append("%s beta=%d: 3000 s D-arm cap bound" % (nm_lat, beta))
            dev("BUDGET", "D arm cap bound before %s" % nm_lat)
            continue
        qbeta = float(betaincinv(beta / 2.0, (d - beta) / 2.0, 2.0 ** -10))
        pools = []
        for p in range(d_pools_used):
            pools.append(cbd2_pool(d, p))
        sqns = []
        for pl_ in pools:
            s = np.empty(D_N)
            for st in range(0, D_N, D_CHUNK):
                e = min(D_CHUNK, D_N - st)
                c = pl_[st:st + e].astype(np.float64)
                s[st:st + e] = np.einsum("ij,ij->i", c, c)
            sqns.append(s)
        cell = OrderedDict(); cell["q_Beta_2^-10"] = qbeta
        cell["base"] = OrderedDict(); cell["rho"] = OrderedDict()
        nbD = 1 if smoke else D_BASES
        nrD = 1 if smoke else D_REPL
        for i in range(nbD):
            B = build_basis(d, k, Q_MAIN, i, "qary")
            Qb0 = frame_Q(B.astype(np.float64), beta)
            b_by_pool = []
            for p in range(d_pools_used):
                Dv, qe = D_from_frame(Qb0, pools[p], sqns[p], d, beta, qbeta); d_evals += 1
                b_by_pool.append(Dv)
            cell["base"][str(i)] = b_by_pool
            for which in ("T0", "T1", "T2", "T3"):
                for h in range(nrD):
                    if time.time() - t_d0 > CAP_D_ARM:
                        d_arm.setdefault("not_measured", []).append(
                            "%s beta=%d basis %d %s repl %d: 3000 s cap" % (nm_lat, beta, i, which, h))
                        break
                    M, _ = transformed(B, d, k, beta, h, which)
                    Qt = frame_Q(M, beta)
                    for p in range(d_pools_used):
                        Dv, _ = D_from_frame(Qt, pools[p], sqns[p], d, beta, qbeta); d_evals += 1
                        r = rho(Dv, b_by_pool[p], scale_floor("D", d, beta, k))
                        cell["rho"].setdefault(which, []).append(r)
                        inv.setdefault("D", OrderedDict()).setdefault(nm_lat, OrderedDict()) \
                           .setdefault(str(beta), OrderedDict()).setdefault(which, []).append(r)
                        cell.setdefault("values", OrderedDict()).setdefault(which, []).append(Dv)
        # pooled SE of D across pools and bases (the floor the collision probe is read against)
        allb = [v for lst in cell["base"].values() for v in lst]
        cell["base_mean"] = float(np.mean(allb)); cell["base_sd"] = float(np.std(allb, ddof=1))
        cell["base_pooled_SE"] = float(np.std(allb, ddof=1) / math.sqrt(len(allb)))
        # q-sweep and rank sweep for D at this cell (pool-averaged, basis i=0)
        cell["q_sweep"] = OrderedDict()
        for q in Q_LADDER:
            Bq = build_basis(d, k, q, 0, "qary")
            Qq = frame_Q(Bq.astype(np.float64), beta)
            vals = []
            for p in range(d_pools_used):
                Dv, _ = D_from_frame(Qq, pools[p], sqns[p], d, beta, qbeta); d_evals += 1
                vals.append(Dv)
            cell["q_sweep"][str(q)] = float(np.mean(vals))
        cell["rank_sweep"] = OrderedDict()
        for r in [x for x in RANK_LADDER[:-1] if x <= k] + [k]:
            Br = build_basis(d, k, Q_MAIN, 0, "qary", rank=r)
            Qr = frame_Q(Br.astype(np.float64), beta)
            vals = []
            for p in range(d_pools_used):
                Dv, _ = D_from_frame(Qr, pools[p], sqns[p], d, beta, qbeta); d_evals += 1
                vals.append(Dv)
            cell["rank_sweep"][str(r)] = float(np.mean(vals))
        # collision probe for D at this cell's d (only where 2*beta <= d)
        if 2 * beta <= d:
            cb = beta
            ai = np.arange(cb) * 2; bi = np.arange(cb) * 2 + 1
            uu = np.where(np.arange(cb) < cb // 2, u_lo, u_hi)
            sg = np.arange(cb); h1 = np.arange(0, cb // 2); h2 = np.arange(cb // 2, cb)
            sg[h1] = np.roll(h1, 1); sg[h2] = np.roll(h2, 1)
            W1 = np.zeros((d, cb)); W2 = np.zeros((d, cb))
            for m in range(cb):
                W1[ai[m], m] = math.sqrt(uu[m]); W1[bi[m], m] = math.sqrt(1 - uu[m])
                W2[ai[sg[m]], m] = math.sqrt(uu[m]); W2[bi[m], m] = math.sqrt(1 - uu[m])
            v1, v2 = [], []
            for p in range(d_pools_used):
                a, _ = D_from_frame(W1, pools[p], sqns[p], d, cb, qbeta); d_evals += 1
                b, _ = D_from_frame(W2, pools[p], sqns[p], d, cb, qbeta); d_evals += 1
                v1.append(a); v2.append(b)
            collD = rho(float(np.mean(v2)), float(np.mean(v1)), scale_floor("D", d, cb, k))
            floor = cell["base_pooled_SE"] / max(abs(float(np.mean(v1))), scale_floor("D", d, cb, k))
            cell["collision_probe_D"] = {
                "D_P1_by_pool": v1, "D_P2_by_pool": v2, "coll": collD,
                "pooled_SE_floor_in_rho_units": floor,
                "diag_max_abs_diff": float(np.max(np.abs(np.diag(W1 @ W1.T) - np.diag(W2 @ W2.T)))),
                "offdiag_max_abs_diff": float(np.max(np.abs(W1 @ W1.T - W2 @ W2.T))),
                "reading": ("UPPER BOUND: D is diagonal-determined on this probe to within %.4g of scale, "
                            "which is %s the pooled SE floor %.4g"
                            % (collD, "below" if collD < floor else "above", floor))}
            coll_rec.setdefault("per_candidate_D_by_cell", OrderedDict())[nm_lat] = {
                "xid": "X4", "coll": collD, "s_X": scale_floor("D", d, cb, k),
                "pooled_SE_floor_in_rho_units": floor}
            coll_rec["per_candidate"]["D_at_%s" % nm_lat] = {
                "xid": "X4", "coll": collD, "s_X": scale_floor("D", d, cb, k),
                "pooled_SE_floor_in_rho_units": floor,
                "verdict": ("DIAGONAL-DETERMINED on this probe (AM4-OBS-1 premise holds for X)" if collD <= TAU_NUM
                            else ("NOT a function of diag alone (AM4-OBS-1 premise REFUTED for X)" if collD > TAU_INV
                                  else "INDETERMINATE at the probe's resolution")),
                "cell": nm_lat}
        d_arm[nm_lat] = cell
        del pools, sqns
        print("  %s beta=%d done, %d D-evaluations, t=%.0fs" % (nm_lat, beta, d_evals, time.time() - t_d0))
    d_arm["pools_used_E"] = d_pools_used
    d_arm["total_D_evaluations"] = d_evals
    d_arm["wall_secs"] = time.time() - t_d0
    RES["D_arm"] = d_arm

    # ------------------------------------------------------------------
    # 4.9  AGGREGATE, and apply the five gate criteria
    # ------------------------------------------------------------------
    print("\n[gates]")
    RES["od_identity"] = {"n_frames": len(od_res),
                          "max_abs_residual": float(np.max(od_res)) if od_res else None,
                          "tol": OD_IDENTITY_TOL,
                          "holds": bool(od_res and float(np.max(od_res)) <= OD_IDENTITY_TOL)}
    print("  OD + V + beta^2/d = beta : max residual %.3e over %d frames (tol %.0e) -> %s"
          % (RES["od_identity"]["max_abs_residual"], RES["od_identity"]["n_frames"],
             OD_IDENTITY_TOL, RES["od_identity"]["holds"]))

    inv_agg = OrderedDict()
    for nmv, per_lat in inv.items():
        if nmv.startswith("_"):
            continue
        inv_agg[nmv] = OrderedDict()
        for lat, per_beta in per_lat.items():
            inv_agg[nmv][lat] = OrderedDict()
            for beta, per_t in per_beta.items():
                inv_agg[nmv][lat][beta] = {t: agg(v) for t, v in per_t.items()}
    RES["invariance_residuals"] = inv_agg
    RES["invariance_raw_counts"] = {nmv: sum(len(v) for lat in per_lat.values()
                                             for bb in lat.values() for v in bb.values())
                                    for nmv, per_lat in inv.items() if not nmv.startswith("_")}
    RES["T3_growth_diagnostic"] = {"n": len(t3_growth),
                                   "max_abs_UB": max((r["max_abs_UB"] for r in t3_growth), default=None),
                                   "max_abs_U": max((r["max_abs_U"] for r in t3_growth), default=None),
                                   "rows_sample": t3_growth[:12]}
    RES["gram_int_dev"] = {lat: {t: agg(v) for t, v in per.items()}
                           for lat, per in inv.get("_gram_int_dev", {}).items()}
    RES["q_sweep_frozen"] = qsweep
    RES["q_sweep_supplementary_POSTHOC_uncitable"] = qsweep_supp
    RES["rank_sweep"] = ranksweep
    RES["stage1_notes"] = stage1_notes

    gates = OrderedDict()
    for nmv in CANDIDATES:
        g = OrderedDict(); g["xid"] = CAND_XID[nmv]
        per_lat = inv.get(nmv)
        if not per_lat:
            g["status"] = "NOT ADJUDICATED -- arm not reached (INFRASTRUCTURE / budget)"
            gates[nmv] = g
            continue
        t0v, tinv = [], []
        for lat, pb in per_lat.items():
            for beta, pt in pb.items():
                t0v += pt.get("T0", [])
                for t in ("T1", "T2", "T3"):
                    tinv += pt.get(t, [])
        g["G_NUM"] = {"max_rho_T0": float(np.max(t0v)) if t0v else None, "tau_num": TAU_NUM,
                      "pass": bool(t0v) and float(np.max(t0v)) <= TAU_NUM, "n": len(t0v)}
        g["G_INV"] = {"max_rho_T1T2T3": float(np.max(tinv)) if tinv else None, "tau_inv": TAU_INV,
                      "pass": bool(tinv) and float(np.max(tinv)) <= TAU_INV, "n": len(tinv)}
        g["G_INV_by_transform"] = {}
        for t in ("T1", "T2", "T3"):
            vv = [x for lat, pb in per_lat.items() for beta, pt in pb.items() for x in pt.get(t, [])]
            g["G_INV_by_transform"][t] = agg(vv)
        if nmv in ("lam1n", "hkz"):
            pc = inv_canon.get(nmv, {})
            ct = [x for lat, pb in pc.items() for beta, pt in pb.items()
                  for t in ("T1", "T2", "T3") for x in pt.get(t, [])]
            g["G_INV_canonical_subset"] = {
                "max_rho_T1T2T3": float(np.max(ct)) if ct else None, "n": len(ct),
                "pass": bool(ct) and float(np.max(ct)) <= TAU_INV,
                "note": ("prereg 2.9 step 4: a residual from a NON-CANONICAL reduction is uninformative for "
                         "G-INV. This is the residual over the transform pairs where BOTH presentations "
                         "reached VERIFIED HKZ (hkz_violation = 0). All-pairs figure reported beside it.")}
            if ct:
                g["G_INV"]["pass_all_pairs"] = g["G_INV"]["pass"]
                g["G_INV"]["pass"] = g["G_INV_canonical_subset"]["pass"]
                g["G_INV"]["reading_used"] = "canonical subset (frozen clause prereg 2.9 step 4)"
        # G-Q
        qs = qsweep.get(nmv)
        if qs:
            best = None
            for lat, pb in qs.items():
                for beta, lad in pb.items():
                    if "1" in lad and "3329" in lad and lad["1"] is not None and lad["3329"] is not None:
                        s = scale_floor(nmv, int([L for L in LATTICES + SMALL_LATTICES if L[0] == lat][0][1]),
                                        int(beta), int([L for L in LATTICES + SMALL_LATTICES if L[0] == lat][0][2]))
                        val = abs(lad["3329"] - lad["1"]) / max(abs(lad["3329"]), s)
                        if best is None or val > best[0]:
                            best = (val, lat, beta)
            g["G_Q"] = {"max_over_cells": best[0] if best else None,
                        "at": {"lattice": best[1], "beta": best[2]} if best else None,
                        "tau_q": TAU_Q, "pass": bool(best) and best[0] >= TAU_Q}
        elif nmv == "D":
            best = None
            for lat, cell in d_arm.items():
                if isinstance(cell, dict) and "q_sweep" in cell:
                    lad = cell["q_sweep"]
                    dd = [L for L in LATTICES if L[0] == lat][0]
                    bb = [c[3] for c in D_CELLS if c[0] == lat][0]
                    s = scale_floor("D", dd[1], bb, dd[2])
                    val = abs(lad["3329"] - lad["1"]) / max(abs(lad["3329"]), s)
                    if best is None or val > best[0]:
                        best = (val, lat, bb)
            g["G_Q"] = {"max_over_cells": best[0] if best else None,
                        "at": {"lattice": best[1], "beta": best[2]} if best else None,
                        "tau_q": TAU_Q, "pass": bool(best) and best[0] >= TAU_Q}
        else:
            g["G_Q"] = {"status": "NOT MEASURED"}
        # G-REL1
        src = base_vals if nmv in FRAME_CHEAP + ["rdet"] else small_base
        cands = []
        latset = lattices if nmv in FRAME_CHEAP + ["rdet"] else small
        for (lat, d, k, kind) in latset:
            lo, hi = REL1_PAIR[d]
            a = src.get((lat, lo, 0)); b = src.get((lat, hi, 0))
            if a is None or b is None or a.get(nmv) is None or b.get(nmv) is None:
                continue
            s = scale_floor(nmv, d, lo, k)
            cands.append({"lattice": lat, "beta_lo": lo, "beta_hi": hi, "X_lo": a[nmv],
                          "X_hi": b[nmv], "s_X": s, "value": rho(b[nmv], a[nmv], s)})
        if nmv == "D":
            g["G_REL1"] = {"status": "NOT MEASURED -- the frozen D arm runs at one beta per cell "
                                     "(prereg 2.9: L3 beta=40 and L4 beta=45 only)"}
        elif cands:
            bestc = max(cands, key=lambda c: c["value"])
            g["G_REL1"] = {"best": bestc, "all": cands, "tau_rel": TAU_REL,
                           "pass": bestc["value"] >= TAU_REL}
        else:
            g["G_REL1"] = {"status": "NOT MEASURED"}
        # G-REL2 on mirrored cells
        rel2 = []
        for (la, lb) in REL2_PAIRS:
            La = [L for L in LATTICES + SMALL_LATTICES if L[0] == la]
            Lb = [L for L in LATTICES + SMALL_LATTICES if L[0] == lb]
            if not La or not Lb:
                continue
            d, ka = La[0][1], La[0][2]
            for beta in BETA_GRID[d]:
                a = src.get((la, beta, 0)); b = src.get((lb, beta, 0))
                if a is None or b is None or a.get(nmv) is None or b.get(nmv) is None:
                    continue
                s = scale_floor(nmv, d, beta, ka)
                rel2.append({"pair": "%s/%s" % (la, lb), "d": d, "beta": beta,
                             "X_k": a[nmv], "X_dmk": b[nmv], "s_X": s,
                             "value": rho(b[nmv], a[nmv], s)})
        if nmv == "D":
            g["G_REL2"] = {"status": "NOT MEASURED -- the frozen D arm runs at L3 and L4 only, which are "
                                     "not a mirrored pair"}
        elif rel2:
            bestr = max(rel2, key=lambda c: c["value"])
            g["G_REL2"] = {"best": bestr, "all": rel2, "tau_rel": TAU_REL, "pass": bestr["value"] >= TAU_REL}
        else:
            g["G_REL2"] = {"status": "NOT MEASURED"}
        g["G_REL"] = {"pass": bool(g["G_REL1"].get("pass")) and bool(g["G_REL2"].get("pass"))}
        # G-RANK: departure index b*(X) per forced rank
        rs = ranksweep.get(nmv)
        if rs:
            gr = OrderedDict()
            for lat, per_r in rs.items():
                dd = [L for L in LATTICES + SMALL_LATTICES if L[0] == lat][0]
                gr[lat] = OrderedDict()
                for r, lad in per_r.items():
                    betas = sorted(int(x) for x in lad)
                    b0 = betas[0]; x0 = lad[str(b0)]
                    s = scale_floor(nmv, dd[1], b0, dd[2])
                    bstar = None
                    for bb in betas[1:]:
                        if lad[str(bb)] is None or x0 is None:
                            continue
                        if abs(lad[str(bb)] - x0) > TAU_INV * s:
                            bstar = bb; break
                    gr[lat][r] = {"b_star": bstar, "beta_min": b0,
                                  "realized_rank": ranksweep.get("_rank_realized", {}).get(lat, {}).get(r)}
            g["G_RANK"] = {"b_star_by_rank": gr,
                           "note": "REFUSED as a block-content adjudicator iff b*(X) tracks min(rank(A_S),beta) "
                                   "rather than min(k,beta); b* is resolved only to the reported beta grid"}
            # tracking verdict
            verdicts = {}
            for lat, per_r in gr.items():
                ks = [L for L in LATTICES + SMALL_LATTICES if L[0] == lat][0][2]
                bs = {r: v["b_star"] for r, v in per_r.items()}
                distinct = len(set(v for v in bs.values() if v is not None))
                verdicts[lat] = {"b_star_by_rank": bs, "k": ks,
                                 "moves_with_rank": distinct > 1,
                                 "verdict": ("REFUSED as a block-content adjudicator -- b* tracks rank(A_S)"
                                             if distinct > 1 else
                                             "b* does not move across the rank ladder at this grid resolution")}
            g["G_RANK"]["verdict_by_lattice"] = verdicts
        else:
            g["G_RANK"] = {"status": "NOT MEASURED"}
        g["ADMISSIBLE"] = bool(g["G_NUM"].get("pass") and g["G_INV"].get("pass")
                               and g["G_Q"].get("pass") and g["G_REL"].get("pass"))
        g["ADMISSIBLE_NOT_RELEVANT"] = bool(g["G_NUM"].get("pass") and g["G_INV"].get("pass")
                                            and g["G_Q"].get("pass") and not g["G_REL"].get("pass"))
        gates[nmv] = g
        fmt = lambda v: ("%.3e" % v) if isinstance(v, float) else "n/a"
        print("  %-4s %-5s G-NUM %-5s (%s)  G-INV %-5s (%s)  G-Q %-5s (%s)  G-REL1 %-5s  G-REL2 %-5s"
              % (CAND_XID[nmv], nmv, g["G_NUM"].get("pass"), fmt(g["G_NUM"].get("max_rho_T0")),
                 g["G_INV"].get("pass"), fmt(g["G_INV"].get("max_rho_T1T2T3")),
                 g["G_Q"].get("pass"), fmt(g["G_Q"].get("max_over_cells")),
                 g["G_REL1"].get("pass", "n/m"), g["G_REL2"].get("pass", "n/m")))
    RES["gates"] = gates

    # ------------------------------------------------------------------
    # 4.10  frozen predictions
    # ------------------------------------------------------------------
    preds = OrderedDict()
    preds["PRED_A2"] = {"statement": "every f(P)-class candidate fails G-INV or G-Q",
                        "per_candidate": {n: {"G_INV_pass": gates[n]["G_INV"].get("pass"),
                                              "G_Q_pass": gates[n]["G_Q"].get("pass"),
                                              "fails_one": not (gates[n]["G_INV"].get("pass")
                                                                and gates[n]["G_Q"].get("pass"))}
                                          for n in FP_CLASS if n in gates and "G_INV" in gates[n]},
                        }
    preds["PRED_A2"]["holds"] = all(v["fails_one"] for v in preds["PRED_A2"]["per_candidate"].values())
    if "TRIV" in gates and "G_INV" in gates["TRIV"]:
        preds["PRED_A3"] = {"statement": "X7 = tr(P^2) passes G-INV at <= tau_num and FAILS G-Q",
                            "max_rho_T1T2T3": gates["TRIV"]["G_INV"]["max_rho_T1T2T3"],
                            "passes_G_INV_at_tau_num": gates["TRIV"]["G_INV"]["max_rho_T1T2T3"] <= TAU_NUM,
                            "G_Q_value": gates["TRIV"]["G_Q"].get("max_over_cells"),
                            "G_Q_refuses_TRIV": not gates["TRIV"]["G_Q"].get("pass"),
                            "FROZEN_CLAUSE": ("prereg 2.8 PRED-A3 / 2.10 Form 1: if X7 PASSES G-Q the gate is "
                                              "declared INADMISSIBLE and no admissibility claim may be reported")}
        preds["PRED_A3"]["holds"] = bool(preds["PRED_A3"]["passes_G_INV_at_tau_num"]
                                         and preds["PRED_A3"]["G_Q_refuses_TRIV"])
    if "rdet" in gates and "G_INV" in gates["rdet"]:
        bt = gates["rdet"]["G_INV_by_transform"]
        preds["PRED_A4"] = {"statement": "X8 = rdet passes G-INV at <= tau_num under T1 and T2, and at "
                                         "<= tau_inv under T3",
                            "T1_max": bt["T1"]["max"] if bt.get("T1") else None,
                            "T2_max": bt["T2"]["max"] if bt.get("T2") else None,
                            "T3_max": bt["T3"]["max"] if bt.get("T3") else None,
                            "FROZEN_CLAUSE": ("prereg 2.10 (b): if X8 FAILS G-INV the gate is INSTRUMENT-LIMITED "
                                              "and NO REFUSAL OF ANY CANDIDATE MAY BE REPORTED")}
        preds["PRED_A4"]["holds"] = bool(bt.get("T1") and bt["T1"]["max"] <= TAU_NUM
                                         and bt.get("T2") and bt["T2"]["max"] <= TAU_NUM
                                         and bt.get("T3") and bt["T3"]["max"] <= TAU_INV)
        preds["PRED_A4"]["rdet_passes_G_INV"] = gates["rdet"]["G_INV"].get("pass")
        preds["PRED_A4"]["rdet_passes_G_Q"] = gates["rdet"]["G_Q"].get("pass")
    if "E_I" in qsweep:
        lad = {}
        for lat, pb in qsweep["E_I"].items():
            for beta, l in pb.items():
                lad["%s_beta%s" % (lat, beta)] = {q: 1.0 - v for q, v in l.items()}
        preds["PRED_A5"] = {"statement": "the q-ladder for E_I is monotone in q and 1 - E_I ~ q^-2",
                            "one_minus_E_I_frozen_construction": lad,
                            "note": "scored on the FROZEN construction A = integers(0,q), under which A = 0 "
                                    "at q = 1 and the q=1 basis is I_d. The supplementary POST-HOC ladder-B "
                                    "(A held at q=3329, only the lower block scaled) is reported separately."}
        supl = {}
        for lat, pb in qsweep_supp.get("E_I", {}).items():
            for beta, l in pb.items():
                supl["%s_beta%s" % (lat, beta)] = {q: 1.0 - v for q, v in l.items()}
        preds["PRED_A5"]["one_minus_E_I_supplementary_POSTHOC"] = supl
    RES["predictions"] = preds

    # ------------------------------------------------------------------
    # 4.11  GEN-1/2/3 and the outcome map, applied IN ORDER
    # ------------------------------------------------------------------
    scored = [n for n in CANDIDATES if n in gates and "G_INV" in gates[n]]
    fp_scored = [n for n in scored if n in FP_CLASS]
    nonfp_scored = [n for n in scored if n in NON_FP_CLASS]

    gen = OrderedDict()
    gen["GEN_1"] = {
        "OBS_GEN_stated_in_report": True,
        "X7_invariant_to_tau_num": (gates.get("TRIV", {}).get("G_INV", {}).get("max_rho_T1T2T3") is not None
                                    and gates["TRIV"]["G_INV"]["max_rho_T1T2T3"] <= TAU_NUM),
        "OD_identity_holds": RES["od_identity"]["holds"],
        "every_fP_fails_G_INV_or_G_Q": all(not (gates[n]["G_INV"].get("pass") and gates[n]["G_Q"].get("pass"))
                                           for n in fp_scored),
        "fP_scored": fp_scored,
    }
    gen["GEN_1"]["holds"] = all([gen["GEN_1"]["X7_invariant_to_tau_num"],
                                 gen["GEN_1"]["OD_identity_holds"],
                                 gen["GEN_1"]["every_fP_fails_G_INV_or_G_Q"]])
    gen["GEN_2"] = {"n_fP_scored": len(fp_scored), "n_nonfP_scored": len(nonfp_scored),
                    "fP": fp_scored, "nonfP": nonfp_scored,
                    "requirement": ">= 3 f(P)-class and >= 2 non-f(P)-class actually scored, class decided "
                                   "by measurement (frozen collision probe + supplementary PROBE-L) not assertion",
                    "holds": len(fp_scored) >= 3 and len(nonfp_scored) >= 2}
    gen["GEN_3"] = {"holds": True,
                    "scope": "observables that are functions of the tail-beta frame projector alone, at the "
                             "tested (d,k,beta,q) grid, at n = 8 bases; NOT a theorem that no admissible "
                             "statistic exists",
                    "forward_guidance": ["(i) weaken AM-4 to the basis-change subgroup {T2,T3} only, retaining "
                                         "the standard coordinate frame",
                                         "(ii) restate the target question in isometry-invariant terms (e.g. the "
                                         "GSO profile of a canonical reduction, X10) -- a DIFFERENT question, "
                                         "and it must be labelled as one"]}
    RES["GEN"] = gen

    # OUTCOME MAP, evaluated IN ORDER (prereg 2.7)
    outcome = OrderedDict()
    notes = []

    # frozen clause checks first
    inadmissible_gate = bool(gates.get("TRIV", {}).get("G_Q", {}).get("pass"))
    instrument_limited = ("rdet" in gates and "G_INV" in gates["rdet"]
                          and not gates["rdet"]["G_INV"].get("pass"))
    outcome["frozen_clause_TRIV_passes_G_Q_gate_INADMISSIBLE"] = inadmissible_gate
    outcome["frozen_clause_rdet_fails_G_INV_no_refusal_may_be_reported"] = instrument_limited

    r5 = [n for n in CANDIDATES if n not in scored or not gates[n]["G_NUM"].get("pass")]
    outcome["R5_not_adjudicated"] = {n: (gates[n]["G_NUM"] if n in gates and "G_NUM" in gates[n]
                                         else gates.get(n, {}).get("status", "not reached")) for n in r5}

    r4_premise = [n for n in ("E_I", "V", "m3", "W")
                  if coll_rec["per_candidate"].get(n, {}).get("coll", 0.0) > TAU_INV]
    r4_conclusion = [n for n in ("E_I", "V", "m3", "D", "W")
                     if n in gates and "G_INV_by_transform" in gates[n]
                     and gates[n]["G_INV_by_transform"].get("T1")
                     and gates[n]["G_INV_by_transform"]["T1"]["max"] <= TAU_INV]
    outcome["R4"] = {"fired": bool(r4_premise or r4_conclusion),
                     "premise_refuted_for": r4_premise,
                     "measured_conclusion_refuted_for": r4_conclusion,
                     "note": "prereg 2.7 R4 lists X1,X2,X3,X5 for the premise clause and X1..X5 for the "
                             "measured-conclusion clause; X4 = D's collision result is reported as an upper "
                             "bound against the pooled SE floor and is not used to fire the premise clause"}

    r1 = [n for n in scored if gates[n]["ADMISSIBLE"]]
    r3 = [n for n in scored if gates[n]["ADMISSIBLE_NOT_RELEVANT"]]
    outcome["R1_admissible"] = r1
    outcome["R3_admissible_not_relevant"] = r3

    if inadmissible_gate:
        head = "GATE DECLARED INADMISSIBLE"
        notes.append("X7 = tr(P^2) PASSED G-Q. Frozen clause prereg 2.8 PRED-A3 / 2.10 Form 1 applies: the "
                     "sensitivity criterion does not discriminate and NO admissibility claim may be reported.")
    elif instrument_limited:
        head = "R5 -- INSTRUMENT-LIMITED"
        notes.append("X8 = rdet FAILED G-INV. Frozen clause prereg 2.10 (b) applies: NO REFUSAL OF ANY "
                     "CANDIDATE MAY BE REPORTED.")
    elif r1:
        head = "R1 -- ADMISSIBLE OBSERVABLE EXHIBITED"
    elif r3:
        head = "R3 -- ADMISSIBLE BUT NOT RELEVANT (the obstruction is relocated, not removed)"
    elif gen["GEN_1"]["holds"] and gen["GEN_2"]["holds"] and gen["GEN_3"]["holds"]:
        head = "R2 -- OBSTRUCTION ARCHIVED"
    else:
        head = "R2' -- OBSTRUCTION NOT ESTABLISHED (artifact of the observables actually tested)"
    if outcome["R4"]["fired"]:
        notes.append("R4 also fired and is reported FIRST per prereg 2.7: AM4-OBS-1 REFUTED IN PART.")
    outcome["headline"] = head
    outcome["notes"] = notes
    outcome["map_note"] = ("evaluated IN ORDER R5 -> R4 -> R1 -> R3 -> R2 -> R2'; R1 and R3 are not exclusive "
                           "of each other across candidates and both are reported")
    RES["outcome"] = outcome

    RES["deviations"] = DEVIATIONS
    RES["wall_secs_total"] = time.time() - T_START
    RES["budget"] = {"cap_total_s": CAP_TOTAL, "used_s": time.time() - T_START,
                     "cap_D_arm_s": CAP_D_ARM, "D_arm_used_s": d_arm.get("wall_secs"),
                     "mirrors_dropped": dropped_mirrors}

    def enc(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        raise TypeError(str(type(o)))

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1, default=enc)
    print("\n[outcome] %s" % head)
    for n in notes:
        print("          %s" % n)
    print("[wrote] %s  (%.0f s total)" % (args.out, time.time() - T_START))


if __name__ == "__main__":
    main()
