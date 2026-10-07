#!/usr/bin/env python3
"""Arm-(a) basis-swap wrapper for EXP-CERTBIN-1bfef5.

Documented copy/wrapper of EXP-CERTBIN-e94b27 descent+closure under:
  * a random F_2-basis of the polynomial subspace V (GL(9) draw), and
  * a normal field basis of F_{2^17},

then compares M_4 / W_4 labels (and W_4 iteration/dimension) to
RUN-CERTBIN-c417e0. Clears IMP-ARM-A-BASIS-SWAP.

Does not edit e94b27/impl in place. No Magma/Sage/AUXIN/Bedrock.
"""
from __future__ import annotations

import gzip
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parents[3]
E94_IMPL = REPO / "experiments/EXP-CERTBIN-e94b27/impl"
ARCHIVED_RUN = REPO / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
SEED = 2026092691
CURVE_B = 126251  # RC-1 cell; matches archived curve
L = 9
NEQ = 17
SETS = ("U62", "S62", "C20")
CLOSURES = ("M_4", "W_4")


def _ensure_e94_path() -> None:
    p = str(E94_IMPL)
    if p not in sys.path:
        sys.path.insert(0, p)


def invert_gf2(M: np.ndarray) -> Optional[np.ndarray]:
    n = M.shape[0]
    A = np.concatenate([M.astype(np.uint8).copy(), np.eye(n, dtype=np.uint8)], axis=1)
    for col in range(n):
        piv = None
        for r in range(col, n):
            if A[r, col]:
                piv = r
                break
        if piv is None:
            return None
        if piv != col:
            A[[col, piv]] = A[[piv, col]]
        for r in range(n):
            if r != col and A[r, col]:
                A[r] ^= A[col]
    return A[:, n:].astype(np.uint8)


def random_gl(n: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    while True:
        M = rng.integers(0, 2, size=(n, n), dtype=np.uint8)
        inv = invert_gf2(M)
        if inv is not None:
            return M, inv


def find_normal_element(F) -> Tuple[int, np.ndarray, np.ndarray]:
    """Return (alpha, M, M_inv) where columns of M are alpha^{2^i} in poly basis."""
    for a in range(1, F.q):
        mat = np.zeros((F.n, F.n), dtype=np.uint8)
        x = a
        for i in range(F.n):
            for j in range(F.n):
                mat[j, i] = (x >> j) & 1
            x = F.sqr(x)
        inv = invert_gf2(mat)
        if inv is not None:
            return a, mat, inv
    raise RuntimeError("no normal element found in F_{2^17}")


def v_basis_from_T(T: np.ndarray) -> List[int]:
    """Columns of T (GL(l,F_2)) as degree-<l polynomial-subspace elements."""
    out: List[int] = []
    for j in range(L):
        b = 0
        for i in range(L):
            if T[i, j]:
                b |= 1 << i
        out.append(b)
    return out


def s3_multilinear_general(F, B: int, xR: int, V_basis: List[int]):
    from macaulay import _padd, _pmul, _pscal, _psq  # type: ignore

    X1 = {(j,): int(V_basis[j]) for j in range(L)}
    X2 = {(L + j,): int(V_basis[j]) for j in range(L)}
    s12 = _pmul(F, X1, X2)
    e1 = _padd(s12, _pscal(F, X1, xR), _pscal(F, X2, xR))
    return _padd(_psq(F, e1), _pscal(F, s12, xR), {(): B})


def descended_E_general(F, B: int, xR: int, V_basis: List[int], field_inv: np.ndarray):
    """17 x 172 E(r) with arbitrary V-basis and field-basis recombination."""
    from macaulay import EQ_INDEX, EQ_MONS, NEQ as NEQ_M  # type: ignore

    assert NEQ_M == NEQ
    S = s3_multilinear_general(F, B, xR, V_basis)
    E = np.zeros((NEQ, len(EQ_MONS)), dtype=np.uint8)
    for m, c in S.items():
        if c == 0:
            continue
        j = EQ_INDEX[m]
        vec = np.array([(c >> k) & 1 for k in range(NEQ)], dtype=np.uint8)
        coords = (field_inv @ vec) % 2
        for k in range(NEQ):
            if coords[k]:
                E[k, j] = 1
    return E


def load_archived_labels() -> Dict[str, Dict[str, Any]]:
    path = ARCHIVED_RUN / "closures.jsonl.gz"
    out: Dict[str, Dict[str, Any]] = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("set") not in SETS or row.get("closure") not in CLOSURES:
                continue
            key = f"{row['set']}:{row['idx']}:{row['closure']}"
            out[key] = row
    return out


def load_targets() -> List[Dict[str, Any]]:
    inst = json.loads((ARCHIVED_RUN / "instance-sets.json").read_text(encoding="utf-8"))
    targets: List[Dict[str, Any]] = []
    for sname in SETS:
        for row in inst["sets"][sname]:
            targets.append(
                {
                    "set": sname,
                    "idx": row["idx"],
                    "key": row["key"],
                    "x_R": row["archived"]["x_R"],
                }
            )
    return targets


def run_arm_a(progress_every: int = 16) -> Dict[str, Any]:
    """Execute arm-(a): random poly-V basis + normal field basis vs archive."""
    _ensure_e94_path()
    from gf2n import TableField  # type: ignore
    from instances import eqs_of  # type: ignore
    from closure import Closure  # type: ignore

    t0 = time.monotonic()
    F = TableField()
    rng = np.random.Generator(np.random.PCG64(SEED))
    T, T_inv = random_gl(L, rng)
    V_basis = v_basis_from_T(T)
    alpha, M_normal, M_inv = find_normal_element(F)

    # Self-check: identity bases reproduce stock descended_E on one target.
    from macaulay import descended_E  # type: ignore

    x_check = 4418
    V_id = [1 << j for j in range(L)]
    I = np.eye(NEQ, dtype=np.uint8)
    E_stock = descended_E(F, CURVE_B, x_check)
    E_gen = descended_E_general(F, CURVE_B, x_check, V_id, I)
    identity_ok = bool(np.array_equal(E_stock, E_gen))

    archived = load_archived_labels()
    targets = load_targets()
    if len(targets) != 144 or len(archived) != 288:
        return {
            "ok": False,
            "arm_a_executed": False,
            "reason": (
                f"archived surface size mismatch: targets={len(targets)} "
                f"labels={len(archived)} (need 144/288)"
            ),
            "amazon_bedrock": "NOT SELECTED",
        }

    cl = Closure(18, 4, 17)
    comparisons: List[Dict[str, Any]] = []
    n_agree = 0
    n_disagree = 0

    for i, tgt in enumerate(targets):
        E = descended_E_general(F, CURVE_B, int(tgt["x_R"]), V_basis, M_inv)
        eqs = eqs_of(E)

        rec_m, _ = cl.macaulay_closure(eqs, want_cert=False)
        label_m = "refuted" if rec_m["one"] else "not_refuted"
        key_m = f"{tgt['set']}:{tgt['idx']}:M_4"
        arch_m = archived[key_m]
        agree_m = (
            label_m == arch_m.get("label")
            and bool(rec_m["one"]) == bool(arch_m.get("one"))
            and int(rec_m["rank"]) == int(arch_m.get("rank"))
        )
        comparisons.append(
            {
                "key": key_m,
                "closure": "M_4",
                "agree": agree_m,
                "live": {"label": label_m, "one": bool(rec_m["one"]), "rank": int(rec_m["rank"])},
                "archived": {
                    "label": arch_m.get("label"),
                    "one": arch_m.get("one"),
                    "rank": arch_m.get("rank"),
                },
            }
        )
        n_agree += int(agree_m)
        n_disagree += int(not agree_m)

        rec_w, _ = cl.w_closure(eqs, want_cert=False)
        label_w = "refuted" if rec_w["one"] else "not_refuted"
        key_w = f"{tgt['set']}:{tgt['idx']}:W_4"
        arch_w = archived[key_w]
        agree_w = (
            label_w == arch_w.get("label")
            and bool(rec_w["one"]) == bool(arch_w.get("one"))
            and int(rec_w["final_dim"]) == int(arch_w.get("final_dim"))
            and int(rec_w["iterations_to_fixpoint"])
            == int(arch_w.get("iterations_to_fixpoint"))
        )
        comparisons.append(
            {
                "key": key_w,
                "closure": "W_4",
                "agree": agree_w,
                "live": {
                    "label": label_w,
                    "one": bool(rec_w["one"]),
                    "final_dim": int(rec_w["final_dim"]),
                    "iterations_to_fixpoint": int(rec_w["iterations_to_fixpoint"]),
                    "one_first_iteration": rec_w.get("one_first_iteration"),
                },
                "archived": {
                    "label": arch_w.get("label"),
                    "one": arch_w.get("one"),
                    "final_dim": arch_w.get("final_dim"),
                    "iterations_to_fixpoint": arch_w.get("iterations_to_fixpoint"),
                    "one_first_iteration": arch_w.get("one_first_iteration"),
                },
            }
        )
        n_agree += int(agree_w)
        n_disagree += int(not agree_w)

        if progress_every and (i + 1) % progress_every == 0:
            print(
                f"arm-a progress {i+1}/144 targets; agree={n_agree} disagree={n_disagree}",
                flush=True,
            )

    agreement = f"{n_agree}/288"
    exact = n_agree == 288 and n_disagree == 0 and identity_ok
    if not identity_ok:
        outcome_hint = "O-ARTIFACT"
        reason = "General-descent identity self-check failed against stock descended_E"
    elif exact:
        outcome_hint = "O-ARM-A-EXACT"  # Stage-1 identity gate; Stage-2 assigns E-SET/E-POLY
        reason = "Arm-(a) exact 288/288 label/iteration/dimension agreement with RUN-CERTBIN-c417e0"
    else:
        outcome_hint = "O-ARTIFACT"
        reason = (
            f"Arm-(a) disagreement {agreement} after instrument gates; "
            "Proposition B / instrument defect pending localisation"
        )

    return {
        "ok": True,
        "arm_a_executed": True,
        "arm_a_agreement": agreement,
        "arm_a_exact": exact,
        "n_agree": n_agree,
        "n_disagree": n_disagree,
        "identity_selfcheck_ok": identity_ok,
        "outcome_hint": outcome_hint,
        "reason": reason,
        "seed": SEED,
        "curve_B": CURVE_B,
        "V_basis_T": T.astype(int).tolist(),
        "V_basis_elements": V_basis,
        "normal_alpha": alpha,
        "normal_basis_M": M_normal.astype(int).tolist(),
        "archived_run": str(ARCHIVED_RUN.relative_to(REPO)),
        "n_targets": len(targets),
        "comparisons_disagree": [c for c in comparisons if not c["agree"]],
        "elapsed_s": time.monotonic() - t0,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False},
        # Full per-row table is large; keep summary + disagreements only in primary JSON.
        "comparisons_sha256_note": "full row table omitted from primary summary; n=288",
    }
