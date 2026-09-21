#!/usr/bin/env python3
"""
SECTION A of the notarized BATCH-a44d08 pre-registration: `k != d/2`, the
discriminating test between the two spill mechanisms.

TASK-20260806-3084bc / BATCH-a44d08 / GOAL-MLKEM-005.
CLAIM TIER: TOY. Nothing this script can produce bears on ML-KEM security, on
any FIPS 203 parameter set, on any attack cost, or on any cost model.

This script implements Section A of

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/
      TASK-20260806-843c40/prereg.md
    sha256 = 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80

EXACTLY AS FROZEN.  It re-hashes that file and ABORTS on mismatch (prereg
section 7).  It asserts `git merge-base --is-ancestor <notarizing commit> HEAD`
against the NOTARIZING COMMIT ITSELF and not its parent (prereg section 0.2,
correction V-7).  It does not modify the pre-registration and does not
re-derive, improve or substitute any threshold, grid, observable, estimator or
falsifier declared there.

Wording rule carried from prereg section 2.5 / section 5.4: no arm is described
as "absent", "no departure", "vanishes", "consistent with zero" or any synonym.
Every negative is an upper bound stated with its detection floor.  A self-scan
for those tokens runs at the end and its hits are recorded for review.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from typing import Any

import numpy as np
import scipy

# --------------------------------------------------------------------------
# 0.  Frozen identifiers and the abort-on-mismatch gate
# --------------------------------------------------------------------------

PREREG_PATH = (
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/tasks/"
    "TASK-20260806-843c40/prereg.md"
)
PREREG_SHA256_EXPECTED = (
    "8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80"
)
NOTARIZING_COMMIT = "9cb2d3e28ae7a474edbb116d694969470829e112"

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 7)))
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Hard budget (task card): wall clock 10800 s, memory 8 GB, maximum_runs 1.
WALL_CLOCK_BUDGET_S = 10800.0
# Sub-budget for the SECONDARY A-lll arm.  Prereg section 2.6: "If LLL exceeds
# its share of the budget the A-lll arm is reported as not measured, as
# infrastructure."  Declared here, before the arm runs.
LLL_BUDGET_S = 6000.0

T0 = time.time()


def elapsed() -> float:
    return time.time() - T0


def sh(cmd: list[str]) -> str:
    return subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def preflight() -> dict[str, Any]:
    """Re-hash the pre-registration, abort on mismatch, assert ancestry."""
    abs_prereg = os.path.join(REPO_ROOT, PREREG_PATH)
    digest = sha256_file(abs_prereg)
    if digest != PREREG_SHA256_EXPECTED:
        sys.stderr.write(
            "ABORT: pre-registration sha256 mismatch.\n"
            f"  expected {PREREG_SHA256_EXPECTED}\n"
            f"  observed {digest}\n"
            "This is a harness failure, not a result (prereg section 7).\n"
        )
        raise SystemExit(2)

    # The receipt carrier, checked independently of the constant above.
    receipt_path = os.path.join(os.path.dirname(abs_prereg), "prereg_sha256.txt")
    receipt = open(receipt_path).read().strip().split()[0]
    if receipt != digest:
        sys.stderr.write("ABORT: notarized receipt disagrees with the file.\n")
        raise SystemExit(2)

    rc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", NOTARIZING_COMMIT, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
    ).returncode
    if rc != 0:
        sys.stderr.write(
            "ABORT: the notarizing commit is not an ancestor of HEAD.\n"
        )
        raise SystemExit(2)

    return {
        "prereg_path": PREREG_PATH,
        "prereg_sha256_expected": PREREG_SHA256_EXPECTED,
        "prereg_sha256_observed": digest,
        "prereg_sha256_match": True,
        "prereg_sha256_receipt_file": receipt,
        "notarizing_commit_asserted": NOTARIZING_COMMIT,
        "ancestry_check": "git merge-base --is-ancestor "
        f"{NOTARIZING_COMMIT} HEAD",
        "ancestry_is_ancestor": True,
        "ancestry_asserted_against": "the notarizing commit itself, not its "
        "parent (prereg section 0.2, correction V-7)",
        "head_commit": sh(["git", "rev-parse", "HEAD"]),
        "head_commit_subject": sh(["git", "log", "-1", "--format=%s"]),
        "dirty_tree": bool(sh(["git", "status", "--porcelain"])),
        "dirty_tree_paths": sh(["git", "status", "--porcelain"]).splitlines(),
    }


# --------------------------------------------------------------------------
# 1.  Frozen constants (prereg sections 1, 2.1, 2.2, 2.5, 2.6)
# --------------------------------------------------------------------------

Q = 3329                      # [carried]
N_BASES = 8                   # draws per arm [carried]
GATE_FACTOR = 4.0             # [carried]
TOL_E_ABS = 0.02              # [set here, prereg section 2.5]
TOL_V_REL = 0.02              # [set here, prereg section 2.5]

CELLS = [(100, 30), (100, 70), (140, 40), (140, 100)]

BETA_GRID = {
    100: [15, 25, 30, 35, 50, 65, 70, 75, 85],
    140: [20, 35, 40, 45, 70, 95, 100, 105, 120],
}


def seed_basis_k(d: int, k: int, i: int) -> int:
    return 810000 + d * 1000 + k * 10 + i


def seed_haar_k(d: int, k: int, j: int) -> int:
    return 910000 + d * 1000 + k * 10 + j


def seed_perm(d: int, k: int, i: int) -> int:
    return 920000 + d * 1000 + k * 10 + i


# --------------------------------------------------------------------------
# 2.  Closed-form predictions (prereg section 2.1) -- verified against the
#     frozen tables of section 2.3 before any object is built.
# --------------------------------------------------------------------------

def E_I_MK(beta: int, k: int) -> float:
    return min(1.0, k / beta)


def E_I_MD(beta: int, d: int, k: int) -> float:
    return max(0.0, 1.0 - (d - k) / beta)


def V_c(beta: int, c: int, d: int) -> float:
    if beta <= c:
        return beta * beta * (d - c) / (c * d)
    return c * (1 - beta / d) ** 2 + (d - c) * ((beta - c) / (d - c) - beta / d) ** 2


def V_haar(beta: int, d: int) -> float:
    return 2.0 * beta * (d - beta) / (d * (d + 2))


# The section 2.3 tables, transcribed verbatim from the notarized document, so
# that the implementation is checked against the FROZEN prediction rather than
# against a re-derivation of it.  Columns: beta, E_I MK, E_I MD, V MK, V MD,
# V Haar, ratio MK/MD.
FROZEN_TABLES: dict[tuple[int, int], list[tuple]] = {
    (100, 30): [
        (15, 1.0000, 0.0000, 5.2500, 0.9643, 0.2500, 5.444),
        (25, 1.0000, 0.0000, 14.5833, 2.6786, 0.3676, 5.444),
        (30, 1.0000, 0.0000, 21.0000, 3.8571, 0.4118, 5.444),
        (35, 0.8571, 0.0000, 18.1071, 5.2500, 0.4461, 3.449),
        (50, 0.6000, 0.0000, 10.7143, 10.7143, 0.4902, 1.000),
        (65, 0.4615, 0.0000, 5.2500, 18.1071, 0.4461, 0.290),
        (70, 0.4286, 0.0000, 3.8571, 21.0000, 0.4118, 0.184),
        (75, 0.4000, 0.0667, 2.6786, 14.5833, 0.3676, 0.184),
        (85, 0.3529, 0.1765, 0.9643, 5.2500, 0.2500, 0.184),
    ],
    (100, 70): [
        (15, 1.0000, 0.0000, 0.9643, 5.2500, 0.2500, 0.184),
        (25, 1.0000, 0.0000, 2.6786, 14.5833, 0.3676, 0.184),
        (30, 1.0000, 0.0000, 3.8571, 21.0000, 0.4118, 0.184),
        (35, 1.0000, 0.1429, 5.2500, 18.1071, 0.4461, 0.290),
        (50, 1.0000, 0.4000, 10.7143, 10.7143, 0.4902, 1.000),
        (65, 1.0000, 0.5385, 18.1071, 5.2500, 0.4461, 3.449),
        (70, 1.0000, 0.5714, 21.0000, 3.8571, 0.4118, 5.444),
        (75, 0.9333, 0.6000, 14.5833, 2.6786, 0.3676, 5.444),
        (85, 0.8235, 0.6471, 5.2500, 0.9643, 0.2500, 5.444),
    ],
    (140, 40): [
        (20, 1.0000, 0.0000, 7.1429, 1.1429, 0.2414, 6.250),
        (35, 1.0000, 0.0000, 21.8750, 3.5000, 0.3697, 6.250),
        (40, 1.0000, 0.0000, 28.5714, 4.5714, 0.4024, 6.250),
        (45, 0.8889, 0.0000, 25.7857, 5.7857, 0.4301, 4.457),
        (70, 0.5714, 0.0000, 14.0000, 14.0000, 0.4930, 1.000),
        (95, 0.4211, 0.0000, 5.7857, 25.7857, 0.4301, 0.224),
        (100, 0.4000, 0.0000, 4.5714, 28.5714, 0.4024, 0.160),
        (105, 0.3810, 0.0476, 3.5000, 21.8750, 0.3697, 0.160),
        (120, 0.3333, 0.1667, 1.1429, 7.1429, 0.2414, 0.160),
    ],
    (140, 100): [
        (20, 1.0000, 0.0000, 1.1429, 7.1429, 0.2414, 0.160),
        (35, 1.0000, 0.0000, 3.5000, 21.8750, 0.3697, 0.160),
        (40, 1.0000, 0.0000, 4.5714, 28.5714, 0.4024, 0.160),
        (45, 1.0000, 0.1111, 5.7857, 25.7857, 0.4301, 0.224),
        (70, 1.0000, 0.4286, 14.0000, 14.0000, 0.4930, 1.000),
        (95, 1.0000, 0.5789, 25.7857, 5.7857, 0.4301, 4.457),
        (100, 1.0000, 0.6000, 28.5714, 4.5714, 0.4024, 6.250),
        (105, 0.9524, 0.6190, 21.8750, 3.5000, 0.3697, 6.250),
        (120, 0.8333, 0.6667, 7.1429, 1.1429, 0.2414, 6.250),
    ],
}


def check_frozen_tables() -> dict[str, Any]:
    """Recompute every entry of the frozen section 2.3 tables from the closed
    forms of section 2.1 and compare.  A mismatch means this script does not
    implement the frozen prediction and the run must not proceed."""
    worst = 0.0
    rows = []
    for (d, k), table in FROZEN_TABLES.items():
        if [r[0] for r in table] != BETA_GRID[d]:
            raise SystemExit("ABORT: beta grid disagrees with the frozen table.")
        for beta, eik, eid, vk, vd, vh, ratio in table:
            got = (
                E_I_MK(beta, k),
                E_I_MD(beta, d, k),
                V_c(beta, k, d),
                V_c(beta, d - k, d),
                V_haar(beta, d),
                V_c(beta, k, d) / V_c(beta, d - k, d),
            )
            exp = (eik, eid, vk, vd, vh, ratio)
            devs = [abs(a - b) for a, b in zip(got, exp)]
            worst = max(worst, max(devs[:5]), devs[5] / 1000.0)
            rows.append(
                {
                    "d": d, "k": k, "beta": beta,
                    "max_abs_dev_first_five": max(devs[:5]),
                    "ratio_abs_dev": devs[5],
                }
            )
    ok = all(r["max_abs_dev_first_five"] <= 1e-4 for r in rows) and all(
        r["ratio_abs_dev"] <= 1e-3 for r in rows
    )
    if not ok:
        raise SystemExit("ABORT: closed forms do not reproduce the frozen tables.")
    return {
        "checked_entries": len(rows) * 6,
        "max_abs_deviation_values": max(r["max_abs_dev_first_five"] for r in rows),
        "max_abs_deviation_ratio_column": max(r["ratio_abs_dev"] for r in rows),
        "tolerance_values": 1e-4,
        "tolerance_ratio_column": 1e-3,
        "result": "PASS -- the closed forms of prereg section 2.1 reproduce "
        "every entry of the frozen section 2.3 tables to the printed precision",
    }


# --------------------------------------------------------------------------
# 3.  Frame construction (prereg section 2.6), exact integer basis -> float64 QR
# --------------------------------------------------------------------------

def build_B(d: int, k: int, i: int) -> np.ndarray:
    """B = [[ I_k , A ], [ 0 , q I_{d-k} ]];  K_I = coords 1..k, K_q = k+1..d."""
    rng = np.random.default_rng(seed_basis_k(d, k, i))
    A = rng.integers(0, Q, size=(k, d - k))
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = Q * np.eye(d - k, dtype=np.int64)
    return B


def build_B_swap(d: int, k: int, i: int) -> np.ndarray:
    """N-A3 block swap: B' = [[ q I_{d-k} , 0 ], [ A , I_k ]] with the SAME A,
    so K_q = coords 1..d-k and K_I = coords d-k+1..d.

    DISCLOSED TRANSCRIPTION RESOLUTION: prereg section 2.6 writes the (2,1)
    block as `A^T`.  With A of shape (k, d-k) as that same section fixes, A^T
    has shape (d-k, k) and CANNOT occupy a block of shape (k, d-k); the frozen
    text is dimensionally inadmissible as literally written.  The unique
    shape-consistent object that "the same A" can denote there is A itself,
    which is what is used.  Recorded as a deviation in the run manifest and the
    report rather than silently resolved.
    """
    rng = np.random.default_rng(seed_basis_k(d, k, i))
    A = rng.integers(0, Q, size=(k, d - k))
    B = np.zeros((d, d), dtype=np.int64)
    B[: d - k, : d - k] = Q * np.eye(d - k, dtype=np.int64)
    B[d - k:, : d - k] = A
    B[d - k:, d - k:] = np.eye(k, dtype=np.int64)
    return B


def frame_Q(B: np.ndarray) -> np.ndarray:
    """Orthonormal GSO frame: Q from QR(B^T), float64.  Column j of Q spans the
    j-th Gram-Schmidt direction of the rows of B in order."""
    Qm, _ = np.linalg.qr(np.asarray(B, dtype=np.float64).T)
    return Qm


def haar_Q(d: int, seed: int) -> np.ndarray:
    """N-A1: Haar orthogonal, QR of a standard normal d x d, columns
    sign-fixed by sign(diag(R))."""
    rng = np.random.default_rng(seed)
    G = rng.standard_normal((d, d))
    Qm, R = np.linalg.qr(G)
    s = np.sign(np.diag(R))
    s[s == 0] = 1.0
    return Qm * s


def diag_P(Qm: np.ndarray, beta: int) -> np.ndarray:
    """diag(P) for P = Q_tail Q_tail^T, Q_tail = last beta columns of Q."""
    tail = Qm[:, -beta:]
    return np.einsum("ij,ij->i", tail, tail)


def observables(dg: np.ndarray, d: int, k: int, beta: int) -> dict[str, float]:
    """E_I, E_q, V and the capacity bounds, all exact scalars of the frame."""
    s_I = float(dg[:k].sum())
    return {
        "E_I": s_I / beta,
        "E_q": 1.0 - s_I / beta,
        "V": float((dg ** 2).sum()) - beta * beta / d,
        "sum_Paa": float(dg.sum()),
        "sum_Paa2": float((dg ** 2).sum()),
        "m3": float(((dg - beta / d) ** 3).sum()),
    }


# --------------------------------------------------------------------------
# 4.  Aggregation and the frozen scoring rule (prereg section 2.5)
# --------------------------------------------------------------------------

def agg(values: list[float]) -> dict[str, Any]:
    a = np.asarray(values, dtype=np.float64)
    sd = float(a.std(ddof=1)) if a.size > 1 else 0.0
    se = sd / np.sqrt(a.size)
    return {
        "n": int(a.size),
        "mean": float(a.mean()),
        "sd_ddof1": sd,
        "SE": float(se),
        "min": float(a.min()),
        "max": float(a.max()),
        "per_instance": [float(x) for x in a],
        "degenerate_exact": bool(se == 0.0),
    }


def z_or_none(meas: float, pred: float, se: float) -> float | None:
    """Departure in SE units.  None when SE == 0 exactly: prereg section 2.5
    forbids the division and the absolute tolerance component governs."""
    if se == 0.0:
        return None
    return (meas - pred) / se


def score_point(d: int, k: int, beta: int,
                aE: dict[str, Any], aV: dict[str, Any]) -> dict[str, Any]:
    """Apply the FROZEN falsification rule of prereg section 2.5 at one point."""
    eik, eid = E_I_MK(beta, k), E_I_MD(beta, d, k)
    vk, vd = V_c(beta, k, d), V_c(beta, d - k, d)

    tol_E = max(GATE_FACTOR * aE["SE"], TOL_E_ABS)
    tol_V_MK = max(GATE_FACTOR * aV["SE"], TOL_V_REL * vk)
    tol_V_MD = max(GATE_FACTOR * aV["SE"], TOL_V_REL * vd)

    v_excluded = (2 * beta == d)     # prereg section 2.4

    out = {
        "d": d, "k": k, "beta": beta,
        "pred": {"E_I_MK": eik, "E_I_MD": eid, "V_MK": vk, "V_MD": vd,
                 "E_I_haar": k / d, "V_haar": V_haar(beta, d)},
        "meas": {"E_I": aE, "V": aV},
        "tolerances": {"tol_E": tol_E, "tol_V_MK": tol_V_MK,
                       "tol_V_MD": tol_V_MD,
                       "note": "tol_E = max(4*SE_EI, 0.02); "
                               "tol_V(m) = max(4*SE_V, 0.02*V_pred(m)) "
                               "[prereg section 2.5, frozen]"},
        "E_arm": {
            "resid_MK": aE["mean"] - eik,
            "resid_MD": aE["mean"] - eid,
            "z_MK": z_or_none(aE["mean"], eik, aE["SE"]),
            "z_MD": z_or_none(aE["mean"], eid, aE["SE"]),
            "separation_of_predictions_SE": (
                None if aE["SE"] == 0.0 else abs(eik - eid) / aE["SE"]
            ),
            "separation_of_predictions_abs": abs(eik - eid),
            "falsifies_MK": abs(aE["mean"] - eik) > tol_E,
            "falsifies_MD": abs(aE["mean"] - eid) > tol_E,
            "discriminating": True,
            "degenerate_exact": aE["degenerate_exact"],
        },
        "V_arm": {
            "excluded_beta_eq_d_over_2": v_excluded,
            "resid_MK": aV["mean"] - vk,
            "resid_MD": aV["mean"] - vd,
            "z_MK": z_or_none(aV["mean"], vk, aV["SE"]),
            "z_MD": z_or_none(aV["mean"], vd, aV["SE"]),
            "separation_of_predictions_SE": (
                None if aV["SE"] == 0.0 else abs(vk - vd) / aV["SE"]
            ),
            "separation_of_predictions_abs": abs(vk - vd),
            "falsifies_MK": (not v_excluded)
                            and abs(aV["mean"] - vk) > tol_V_MK,
            "falsifies_MD": (not v_excluded)
                            and abs(aV["mean"] - vd) > tol_V_MD,
            "discriminating": not v_excluded,
            "degenerate_exact": aV["degenerate_exact"],
        },
        # Structural annotations -- NOT part of the frozen rule, disclosed so a
        # reviewer can see where a prediction coincides with an algebraic bound.
        "bound_annotations": {
            "E_I_upper_capacity_bound": min(1.0, k / beta),
            "E_I_lower_capacity_bound": max(0.0, 1.0 - (d - k) / beta),
            "MK_E_saturates_upper_bound": abs(eik - min(1.0, k / beta)) < 1e-12,
            "MD_E_saturates_lower_bound": abs(eid - max(0.0, 1.0 - (d - k) / beta))
                                          < 1e-12,
            "V_global_max": beta * (1 - beta / d),
            "MK_V_saturates_global_max": abs(vk - beta * (1 - beta / d)) < 1e-9,
            "MD_V_saturates_global_max": abs(vd - beta * (1 - beta / d)) < 1e-9,
            "both_E_predictions_free_of_bound_conflict": beta <= min(k, d - k),
        },
    }
    return out


def cell_verdict(points: list[dict[str, Any]]) -> dict[str, Any]:
    mk_f = [p for p in points
            if p["E_arm"]["falsifies_MK"] or p["V_arm"]["falsifies_MK"]]
    md_f = [p for p in points
            if p["E_arm"]["falsifies_MD"] or p["V_arm"]["falsifies_MD"]]
    mk_any, md_any = bool(mk_f), bool(md_f)
    if not mk_any and md_any:
        v = "SUPPORTS M-K"
    elif mk_any and not md_any:
        v = "SUPPORTS M-D"
    elif mk_any and md_any:
        v = "NEITHER"
    else:
        v = "NOT SEPARATED"
    floors = {
        "max_tol_E": max(p["tolerances"]["tol_E"] for p in points),
        "min_tol_E": min(p["tolerances"]["tol_E"] for p in points),
        "max_tol_V_MK": max(p["tolerances"]["tol_V_MK"] for p in points),
        "max_tol_V_MD": max(p["tolerances"]["tol_V_MD"] for p in points),
    }
    return {
        "verdict": v,
        "MK_falsified_at": [
            {"beta": p["beta"],
             "arms": [a for a in ("E", "V") if p[f"{a}_arm"]["falsifies_MK"]]}
            for p in mk_f
        ],
        "MD_falsified_at": [
            {"beta": p["beta"],
             "arms": [a for a in ("E", "V") if p[f"{a}_arm"]["falsifies_MD"]]}
            for p in md_f
        ],
        "detection_floors": floors,
        "upper_bound_wording": (
            "Any point at which a mechanism is NOT falsified is an upper bound "
            "at that point's own floor: the measured statistic lies within "
            "tol_E (E_I units) / tol_V(m) (V units) of that mechanism's "
            "prediction at n = 8 bases. It is not a statement that the "
            "mechanism is correct."
        ),
    }


# --------------------------------------------------------------------------
# 5.  Arms
# --------------------------------------------------------------------------

def numeric_integrity(Qm: np.ndarray, d: int, k: int, beta: int
                      ) -> dict[str, float]:
    """Independent recomputation of the two observables by a DIFFERENT code
    path (explicit P = Q_tail Q_tail^T and explicit projector traces), plus an
    orthonormality residual.  Guards against a QR or slicing defect producing
    a plausible-looking but wrong frame."""
    tail = Qm[:, -beta:]
    orth = float(np.abs(tail.T @ tail - np.eye(beta)).max())
    P = tail @ tail.T
    dg_fast = np.einsum("ij,ij->i", tail, tail)
    dg_slow = np.diag(P)
    Pi_I = np.zeros(d)
    Pi_I[:k] = 1.0
    E_I_trace = float(np.trace(P * Pi_I[None, :])) / beta      # tr(P Pi_I)/beta
    V_trace = float(np.sum(dg_slow ** 2)) - beta * beta / d
    return {
        "orthonormality_residual_max": orth,
        "diag_path_agreement_max": float(np.abs(dg_fast - dg_slow).max()),
        "trace_P_minus_beta": float(dg_slow.sum() - beta),
        "E_I_two_paths_agreement": abs(
            E_I_trace - float(dg_fast[:k].sum()) / beta),
        "V_two_paths_agreement": abs(
            V_trace - (float((dg_fast ** 2).sum()) - beta * beta / d)),
        "capacity_bound_upper_respected": bool(
            float(dg_fast[:k].sum()) / beta <= min(1.0, k / beta) + 1e-9),
        "capacity_bound_lower_respected": bool(
            float(dg_fast[:k].sum()) / beta
            >= max(0.0, 1.0 - (d - k) / beta) - 1e-9),
    }


def run_frame_arm(d: int, k: int, builder, index_range: str = "low_k",
                  n: int = N_BASES) -> tuple[dict[int, dict], float]:
    """Build n frames with `builder(i)` and score every beta on the shared Q.

    index_range: which coordinate range is treated as K_I when forming E_I.
      "low_k"      -> coords 1..k          (the frozen scoring of the real arm)
      "high_k"     -> coords d-k+1..d      (N-A3, scored against the RELOCATED
                                            I-block)
    """
    t = time.time()
    per_beta: dict[int, dict[str, list[float]]] = {
        b: {"E_I": [], "V": [], "m3": []} for b in BETA_GRID[d]
    }
    for i in range(n):
        Qm = frame_Q(builder(i))
        for beta in BETA_GRID[d]:
            dg = diag_P(Qm, beta)
            if index_range == "high_k":
                dg = np.concatenate([dg[d - k:], dg[: d - k]])
            o = observables(dg, d, k, beta)
            per_beta[beta]["E_I"].append(o["E_I"])
            per_beta[beta]["V"].append(o["V"])
            per_beta[beta]["m3"].append(o["m3"])
    out = {
        b: {"E_I": agg(v["E_I"]), "V": agg(v["V"]), "m3": agg(v["m3"])}
        for b, v in per_beta.items()
    }
    return out, time.time() - t


def run_haar_arm(d: int, k: int) -> tuple[dict[int, dict], float]:
    t = time.time()
    per_beta: dict[int, dict[str, list[float]]] = {
        b: {"E_I": [], "V": []} for b in BETA_GRID[d]
    }
    for j in range(N_BASES):
        Qm = haar_Q(d, seed_haar_k(d, k, j))
        for beta in BETA_GRID[d]:
            dg = diag_P(Qm, beta)
            o = observables(dg, d, k, beta)
            per_beta[beta]["E_I"].append(o["E_I"])
            per_beta[beta]["V"].append(o["V"])
    out = {b: {"E_I": agg(v["E_I"]), "V": agg(v["V"])}
           for b, v in per_beta.items()}
    return out, time.time() - t


def run_perm_arm(d: int, k: int) -> tuple[dict[int, dict], float]:
    """N-A2: the SAME B with a random ambient coordinate permutation applied,
    scored against the UNPERMUTED index ranges 1..k and k+1..d."""
    def builder(i: int) -> np.ndarray:
        B = build_B(d, k, i)
        pi = np.random.default_rng(seed_perm(d, k, i)).permutation(d)
        return B[:, pi]
    return run_frame_arm(d, k, builder, index_range="low_k")


def lll_reduce(B: np.ndarray):
    from fpylll import IntegerMatrix, LLL
    M = IntegerMatrix.from_matrix([[int(x) for x in row] for row in B])
    LLL.reduction(M)
    d = B.shape[0]
    return np.array([[M[i, j] for j in range(d)] for i in range(d)],
                    dtype=np.float64)


# --------------------------------------------------------------------------
# 6.  fpylll convention disclosure (prereg section 2.6) -- a read of integer
#     entries, not a statistic, not a scored arm.
# --------------------------------------------------------------------------

def classify_qary(M, d: int, q: int) -> dict[str, Any]:
    """Describe an integer q-ary basis structurally: which rows are q times a
    unit vector, which columns those q's sit in, and where the identity part
    lives."""
    rows = np.array([[M[i, j] for j in range(d)] for i in range(d)],
                    dtype=np.int64)
    q_rows, q_cols, id_rows, id_cols = [], [], [], []
    for i in range(d):
        nz = np.nonzero(rows[i])[0]
        if nz.size == 1 and abs(rows[i, nz[0]]) == q:
            q_rows.append(i)
            q_cols.append(int(nz[0]))
        ones = np.nonzero(rows[i] == 1)[0]
        if ones.size >= 1:
            for c in ones:
                if np.count_nonzero(rows[:, c]) == 1:
                    id_rows.append(i)
                    id_cols.append(int(c))
                    break
    return {
        "n_rows_that_are_q_times_a_unit_vector": len(q_rows),
        "row_indices_of_q_rows_0based": [int(x) for x in q_rows],
        "row_index_range_of_q_rows": (
            f"{min(q_rows)}..{max(q_rows)}" if q_rows else None
        ),
        "column_indices_carrying_q_0based": sorted(int(x) for x in q_cols),
        "column_index_range_carrying_q": (
            f"{min(q_cols)}..{max(q_cols)}" if q_cols else None
        ),
        "row_index_range_carrying_identity_part": (
            f"{min(id_rows)}..{max(id_rows)}" if id_rows else None
        ),
        "column_index_range_carrying_identity_part": (
            f"{min(id_cols)}..{max(id_cols)}" if id_cols else None
        ),
        "first_row_head": [int(x) for x in rows[0, :6]],
        "last_row_head": [int(x) for x in rows[-1, :6]],
        "row_norms_first_and_last": [
            float(np.linalg.norm(rows[0])), float(np.linalg.norm(rows[-1]))
        ],
    }


def fpylll_disclosure() -> dict[str, Any]:
    out: dict[str, Any] = {"available": False}
    try:
        import fpylll
        from fpylll import IntegerMatrix
    except Exception as exc:                                    # pragma: no cover
        out["not_obtained_reason"] = (
            f"fpylll unavailable: {exc!r}. Recorded as INFRASTRUCTURE, not a "
            "result (prereg section 2.6, AGENTS.md rule 3)."
        )
        return out
    out["available"] = True
    out["fpylll_version"] = fpylll.__version__
    d = 100
    # The frozen call, verbatim.
    M = IntegerMatrix.random(d, "qary", k=d // 2, q=Q)
    out["frozen_call"] = 'IntegerMatrix.random(100, "qary", k=50, q=3329)'
    out["frozen_call_structure"] = classify_qary(M, d, Q)
    # ADDITIONAL structural read (NOT the frozen disclosure, NOT a scored arm,
    # NOT a statistic): the frozen call has k = d/2, at which "k counts the
    # identity rows" and "k counts the q rows" are indistinguishable. One
    # asymmetric call settles the parameter's semantics by inspecting integers.
    M2 = IntegerMatrix.random(d, "qary", k=30, q=Q)
    out["additional_asymmetric_read"] = {
        "call": 'IntegerMatrix.random(100, "qary", k=30, q=3329)',
        "purpose": "disambiguate whether the generator's k counts identity "
                   "rows or q-scaled rows; indistinguishable at k = d/2",
        "structure": classify_qary(M2, d, Q),
    }
    return out


def instrument_check_kd2() -> dict[str, Any]:
    """Reproduce the committed k = d/2 anchors on THIS code path.

    Not a scored arm and not part of any verdict. Committed anchors
    [quoted: EV-MLKEM-94c773; BATCH-436ddd red_team_report.md section 2]:
    V(100, beta=30) = 9.3628, V(100, beta=60) = 16.269, V(140, beta=30) =
    6.7504, V(140, beta=40) = 11.8075, and window energy fraction in the q*I
    block = 0.00000 with beta=60 energy fraction 0.83333 = k/beta at d=100.
    """
    anchors = {
        (100, 30): 9.3628, (100, 60): 16.269,
        (140, 30): 6.7504, (140, 40): 11.8075,
    }
    rows = []
    for d in (100, 140):
        k = d // 2
        Vs: dict[int, list[float]] = {}
        EIs: dict[int, list[float]] = {}
        betas = [b for (dd, b) in anchors if dd == d]
        for i in range(N_BASES):
            Qm = frame_Q(build_B(d, k, i))
            for beta in betas:
                o = observables(diag_P(Qm, beta), d, k, beta)
                Vs.setdefault(beta, []).append(o["V"])
                EIs.setdefault(beta, []).append(o["E_I"])
        for beta in betas:
            a = agg(Vs[beta])
            e = agg(EIs[beta])
            ref = anchors[(d, beta)]
            rows.append({
                "d": d, "k_equals_d_over_2": k, "beta": beta,
                "V_mean_this_code_path": a["mean"],
                "V_SE": a["SE"],
                "committed_anchor_V": ref,
                "relative_deviation_percent": 100.0 * (a["mean"] - ref) / ref,
                "E_I_mean_this_code_path": e["mean"],
                "E_q_mean_this_code_path": 1.0 - e["mean"],
                "E_I_MK_equals_MD_prediction_at_k_eq_d_over_2":
                    E_I_MK(beta, k),
            })
    return {
        "purpose": "verify that the explicitly built basis of prereg section "
                   "2.6 reproduces the committed k = d/2 values on this code "
                   "path; k = d/2 is NON-DISCRIMINATING between M-K and M-D "
                   "and no row here is scored as evidence for either",
        "rows": rows,
    }


# --------------------------------------------------------------------------
# 7.  Main
# --------------------------------------------------------------------------

def main() -> int:
    pre = preflight()
    tables = check_frozen_tables()

    env = {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "loadavg_at_start": list(os.getloadavg()),
        "blas_threads_env": {
            v: os.environ.get(v)
            for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                      "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                      "NUMEXPR_NUM_THREADS")
        },
    }
    try:
        import fpylll
        env["fpylll"] = fpylll.__version__
    except Exception:
        env["fpylll"] = None

    print(f"[{elapsed():7.1f}s] preflight OK, prereg sha256 verified")
    print(f"[{elapsed():7.1f}s] frozen table check: {tables['result']}")

    disclosure = fpylll_disclosure()
    print(f"[{elapsed():7.1f}s] fpylll convention disclosure done")

    icheck = instrument_check_kd2()
    print(f"[{elapsed():7.1f}s] k = d/2 instrument check done")

    results: dict[str, Any] = {}
    timings: dict[str, Any] = {}
    lll_spent = 0.0
    lll_status: dict[str, Any] = {}

    for d, k in CELLS:
        key = f"d{d}_k{k}"
        print(f"[{elapsed():7.1f}s] === cell d={d} k={k} ===")
        t_cell = time.time()

        integ = {
            str(b): numeric_integrity(frame_Q(build_B(d, k, 0)), d, k, b)
            for b in BETA_GRID[d]
        }

        unred, t_u = run_frame_arm(d, k, lambda i: build_B(d, k, i))
        haar, t_h = run_haar_arm(d, k)
        perm, t_p = run_perm_arm(d, k)
        swap_hi, t_s1 = run_frame_arm(
            d, k, lambda i: build_B_swap(d, k, i), index_range="high_k")
        swap_lo, t_s2 = run_frame_arm(
            d, k, lambda i: build_B_swap(d, k, i), index_range="low_k")

        # --- SECONDARY arm A-lll, under its own declared budget -------------
        lll_arm = None
        lll_note = None
        t_l = 0.0
        if env["fpylll"] is None:
            lll_note = ("A-lll NOT MEASURED: fpylll unavailable. "
                        "INFRASTRUCTURE, not a result (AGENTS.md rule 3).")
        elif lll_spent >= LLL_BUDGET_S or elapsed() > WALL_CLOCK_BUDGET_S * 0.8:
            lll_note = (f"A-lll NOT MEASURED for this cell: the declared LLL "
                        f"sub-budget of {LLL_BUDGET_S:.0f} s was already spent "
                        f"({lll_spent:.1f} s) or the wall-clock budget is near. "
                        "INFRASTRUCTURE, not a result (prereg section 2.6).")
        else:
            t_l0 = time.time()
            reduced: list[np.ndarray] = []
            per_basis_s = []
            aborted = None
            for i in range(N_BASES):
                if lll_spent + (time.time() - t_l0) > LLL_BUDGET_S:
                    aborted = i
                    break
                tb = time.time()
                reduced.append(lll_reduce(build_B(d, k, i)))
                per_basis_s.append(time.time() - tb)
            t_l = time.time() - t_l0
            lll_spent += t_l
            if len(reduced) == N_BASES:
                lll_arm, _ = run_frame_arm(
                    d, k, lambda i: reduced[i], index_range="low_k",
                    n=N_BASES)
                lll_status[key] = {
                    "measured": True, "n_bases": N_BASES,
                    "per_basis_seconds": per_basis_s,
                    "total_seconds": t_l,
                }
            else:
                lll_note = (f"A-lll NOT MEASURED for this cell: the LLL "
                            f"sub-budget bound after {len(reduced)} of "
                            f"{N_BASES} bases. INFRASTRUCTURE, not a result.")
                lll_status[key] = {
                    "measured": False, "n_bases_completed": len(reduced),
                    "aborted_at_basis": aborted,
                    "per_basis_seconds": per_basis_s,
                    "total_seconds": t_l,
                }

        pts_u = [score_point(d, k, b, unred[b]["E_I"], unred[b]["V"])
                 for b in BETA_GRID[d]]
        verdict_u = cell_verdict(pts_u)

        pts_l, verdict_l = None, None
        if lll_arm is not None:
            pts_l = [score_point(d, k, b, lll_arm[b]["E_I"], lll_arm[b]["V"])
                     for b in BETA_GRID[d]]
            verdict_l = cell_verdict(pts_l)

        # Null-object scoring, on the identical code path.
        nulls = []
        for b in BETA_GRID[d]:
            h, pm, sh_, sl = haar[b], perm[b], swap_hi[b], swap_lo[b]
            nulls.append({
                "beta": b,
                "N_A1_haar": {
                    "E_I_mean": h["E_I"]["mean"], "E_I_SE": h["E_I"]["SE"],
                    "E_I_pred_k_over_d": k / d,
                    "E_I_z_vs_pred": z_or_none(h["E_I"]["mean"], k / d,
                                               h["E_I"]["SE"]),
                    "V_mean": h["V"]["mean"], "V_SE": h["V"]["SE"],
                    "V_pred_exact": V_haar(b, d),
                    "V_z_vs_pred": z_or_none(h["V"]["mean"], V_haar(b, d),
                                             h["V"]["SE"]),
                    "E_I_z_vs_MK": z_or_none(h["E_I"]["mean"], E_I_MK(b, k),
                                             h["E_I"]["SE"]),
                    "E_I_z_vs_MD": z_or_none(h["E_I"]["mean"], E_I_MD(b, d, k),
                                             h["E_I"]["SE"]),
                },
                "N_A2_ambient_permutation": {
                    "E_I_mean": pm["E_I"]["mean"], "E_I_SE": pm["E_I"]["SE"],
                    "E_I_pred_k_over_d": k / d,
                    "E_I_z_vs_pred": z_or_none(pm["E_I"]["mean"], k / d,
                                               pm["E_I"]["SE"]),
                    "E_I_z_vs_MK": z_or_none(pm["E_I"]["mean"], E_I_MK(b, k),
                                             pm["E_I"]["SE"]),
                    "V_mean": pm["V"]["mean"], "V_SE": pm["V"]["SE"],
                    "V_of_unpermuted_arm": unred[b]["V"]["mean"],
                },
                "N_A3_block_swap": {
                    "E_I_scored_against_RELOCATED_I_block": {
                        "mean": sh_["E_I"]["mean"], "SE": sh_["E_I"]["SE"],
                        "z_vs_MK": z_or_none(sh_["E_I"]["mean"], E_I_MK(b, k),
                                             sh_["E_I"]["SE"]),
                        "z_vs_MD": z_or_none(sh_["E_I"]["mean"],
                                             E_I_MD(b, d, k),
                                             sh_["E_I"]["SE"]),
                    },
                    "E_I_scored_against_OLD_index_range_1_to_k": {
                        "mean": sl["E_I"]["mean"], "SE": sl["E_I"]["SE"],
                        "z_vs_MK": z_or_none(sl["E_I"]["mean"], E_I_MK(b, k),
                                             sl["E_I"]["SE"]),
                    },
                    "V_mean": sh_["V"]["mean"],
                    "V_of_unswapped_arm": unred[b]["V"]["mean"],
                    "admissibility_note":
                        "prereg section 2.6: if the measured quantity follows "
                        "the coordinate RANGE rather than the relocated "
                        "I-block, the observable measures index position and "
                        "Section A is INADMISSIBLE.",
                },
            })

        results[key] = {
            "d": d, "k": k, "d_minus_k": d - k,
            "beta_grid": BETA_GRID[d],
            "seeds": {
                "seed_basis_k": [seed_basis_k(d, k, i) for i in range(N_BASES)],
                "seed_haar_k": [seed_haar_k(d, k, j) for j in range(N_BASES)],
                "seed_perm": [seed_perm(d, k, i) for i in range(N_BASES)],
            },
            "arm_A_unreduced_PRIMARY": {"points": pts_u, "cell": verdict_u},
            "arm_A_lll_SECONDARY": (
                {"points": pts_l, "cell": verdict_l}
                if pts_l is not None else {"not_measured": lll_note}
            ),
            "nulls": nulls,
            "numeric_integrity_basis_i0": integ,
        }
        timings[key] = {
            "unreduced_s": t_u, "haar_s": t_h, "perm_s": t_p,
            "block_swap_hi_s": t_s1, "block_swap_lo_s": t_s2,
            "lll_s": t_l, "cell_total_s": time.time() - t_cell,
        }
        print(f"[{elapsed():7.1f}s]   verdict (A-unreduced): "
              f"{verdict_u['verdict']}   cell {time.time()-t_cell:.1f}s")

    payload = {
        "task": "TASK-20260806-3084bc",
        "batch": "BATCH-a44d08",
        "goal": "GOAL-MLKEM-005",
        "section": "A",
        "claim_tier": "TOY",
        "claim_tier_note": (
            "Nothing here bears on ML-KEM security, on any FIPS 203 parameter "
            "set, on any attack cost, or on any cost model. No result is "
            "transported beyond the tested d, k and beta."
        ),
        "certificate": {
            "kind": "none",
            "reason": "pure measurement run: no discrete-log solve and no "
                      "factor-base relation is claimed.",
        },
        "preflight": pre,
        "frozen_table_check": tables,
        "environment": env,
        "budget": {
            "wall_clock_budget_s": WALL_CLOCK_BUDGET_S,
            "lll_sub_budget_s": LLL_BUDGET_S,
            "maximum_runs": 1,
            "memory_gb": 8,
        },
        "fpylll_convention_disclosure": disclosure,
        "instrument_check_k_eq_d_over_2": icheck,
        "cells": results,
        "timings_s": timings,
        "wall_clock_total_s": elapsed(),
        "loadavg_at_end": list(os.getloadavg()),
        "peak_rss_bytes": None,
    }
    try:
        import resource
        payload["peak_rss_bytes"] = (
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        )
    except Exception:
        pass

    out_path = os.path.join(OUT_DIR, "results_k.json")
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
    print(f"[{elapsed():7.1f}s] wrote {out_path}")

    return 0


def wording_scan() -> int:
    """Frozen completion-gate scan (prereg section 5.4), run as a separate mode
    AFTER the report exists.  Every hit is printed so a reviewer checks it is a
    quotation of the prohibition itself and not a description of a measured
    arm.  Nothing is enforced silently and no file is written."""
    banned = ["absent", "no departure", "vanish", "consistent with zero"]
    for f in ("measure_k.py", "results_k.json", "report_k.md",
              "run_manifest.yaml"):
        p = os.path.join(OUT_DIR, f)
        if not os.path.exists(p):
            print(f"{f}: NOT PRESENT")
            continue
        hits = 0
        for n_, line in enumerate(
                open(p, errors="replace").read().splitlines(), 1):
            for w in banned:
                if re.search(w, line, re.I):
                    hits += 1
                    print(f"{f}:{n_}: [{w}] {line.strip()[:180]}")
        print(f"{f}: {hits} hit(s)")
    return 0


if __name__ == "__main__":
    if "--wording-scan" in sys.argv:
        raise SystemExit(wording_scan())
    raise SystemExit(main())
