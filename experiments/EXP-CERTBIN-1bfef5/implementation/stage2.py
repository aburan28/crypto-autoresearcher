#!/usr/bin/env python3
"""Stage-2 arms (b)–(d) for EXP-CERTBIN-1bfef5.

Precondition: Stage-1 O-ARM-A-PASS (288/288) under AMD-20261003-9ef431 /
EV-CERTBIN-f218ae / DEC-20261003-b8f938.

Arms:
  (b) V_N  — span of nine conjugates of a normal element
  (c) V_S  — F_2 + ker g(σ) for both irreducible octic factors of Phi_17
  (d) V_R  — one random 9-dimensional V (shape-matched null)

Per set: oracle-A sat/unsat under the *current* V; M_4 and W_4 on all 144
archived targets; CP95 W_4/M_4 rates on archived U62; on each V_S,
Frobenius-orbit certificate verification (engine-side eval_cert on all 17
conjugates).

Control policy (AMD-20261003-894083, after EV-CERTBIN-383c07 localization):
  - Archive U62/S62/C20 labels are relative to the polynomial-V oracle of
    RUN-CERTBIN-c417e0 / oracles_rc1.oracle_A. They do NOT transfer as
    sat/unsat obligations under a new V.
  - Instrument void (O-ARTIFACT) only on soundness failure: oracle-A-sat
    under the current V AND (M_4 or W_4) one. Archive-S62 becoming unsat
    / W_4-one under a new V is a transfer observation, not an artifact.
  - Prop F orbit failure on a stable V remains O-ARTIFACT.

No Magma/Sage/AUXIN/Bedrock. No break / exponent / ECC2K-130.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parents[3]
E94_IMPL = REPO / "experiments/EXP-CERTBIN-e94b27/impl"
ARCHIVED_RUN = REPO / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
SEED = 2026092691
CURVE_B = 126251
L = 9
NEQ = 17
N = 17
# Irreducible octic factors of Phi_17 = 1+x+...+x^16 over F_2.
PHI17_OCTICS = (
    0b100111001,  # x^8 + x^5 + x^4 + x^3 + 1
    0b111010111,  # x^8 + x^7 + x^6 + x^4 + x^2 + x + 1
)
E_SET_MIN = 0.90
E_POLY_MAX = 0.50


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


def find_normal_element(F) -> Tuple[int, np.ndarray, np.ndarray]:
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


def frobenius_matrix(F) -> np.ndarray:
    """Linear map of x |-> x^2 on the polynomial basis of F_{2^n}."""
    M = np.zeros((F.n, F.n), dtype=np.uint8)
    for j in range(F.n):
        y = F.sqr(1 << j)
        for i in range(F.n):
            M[i, j] = (y >> i) & 1
    return M


def mat_poly_apply(poly: int, M: np.ndarray) -> np.ndarray:
    """Evaluate poly(M) over F_2 for a bit-polynomial poly."""
    n = M.shape[0]
    acc = np.zeros((n, n), dtype=np.uint8)
    pwr = np.eye(n, dtype=np.uint8)
    p = poly
    while p:
        if p & 1:
            acc ^= pwr
        pwr = (pwr @ M) % 2
        p >>= 1
    return acc.astype(np.uint8)


def nullspace_gf2(A: np.ndarray) -> List[np.ndarray]:
    """Right nullspace basis of A over F_2 (columns)."""
    A = A.astype(np.uint8).copy()
    m, n = A.shape
    # Row-reduce [A | I_n]^T style via column tracking on rows
    mat = A.copy()
    pivots = [-1] * m
    row = 0
    col_used = []
    for col in range(n):
        piv = None
        for r in range(row, m):
            if mat[r, col]:
                piv = r
                break
        if piv is None:
            continue
        if piv != row:
            mat[[row, piv]] = mat[[piv, row]]
        for r in range(m):
            if r != row and mat[r, col]:
                mat[r] ^= mat[row]
        pivots[row] = col
        col_used.append(col)
        row += 1
        if row == m:
            break
    free = [c for c in range(n) if c not in col_used]
    basis = []
    for f in free:
        v = np.zeros(n, dtype=np.uint8)
        v[f] = 1
        for r, pc in enumerate(pivots):
            if pc >= 0 and mat[r, f]:
                v[pc] ^= 1
        # Recover pivot contributions from RREF: for each pivot row, v[pc] = mat[r,f]
        # Recompute properly from RREF
        v = np.zeros(n, dtype=np.uint8)
        v[f] = 1
        for r in range(row - 1, -1, -1):
            pc = pivots[r]
            s = 0
            for c in range(n):
                if c != pc:
                    s ^= int(mat[r, c]) & int(v[c])
            v[pc] = s
        basis.append(v)
    return basis


def vec_to_field(v: np.ndarray) -> int:
    x = 0
    for i, b in enumerate(v):
        if b:
            x |= 1 << i
    return x


def field_to_vec(x: int, n: int = N) -> np.ndarray:
    return np.array([(x >> i) & 1 for i in range(n)], dtype=np.uint8)


def span_basis(vectors: Sequence[int], dim: int = L) -> List[int]:
    """Gaussian-eliminate field elements to a basis of size <= dim."""
    rows = [field_to_vec(v) for v in vectors if v != 0]
    if not rows:
        return []
    M = np.stack(rows, axis=0).astype(np.uint8)
    r = 0
    chosen: List[int] = []
    for col in range(M.shape[1]):
        piv = None
        for i in range(r, M.shape[0]):
            if M[i, col]:
                piv = i
                break
        if piv is None:
            continue
        if piv != r:
            M[[r, piv]] = M[[piv, r]]
        for i in range(M.shape[0]):
            if i != r and M[i, col]:
                M[i] ^= M[r]
        chosen.append(vec_to_field(M[r]))
        r += 1
        if r == dim:
            break
    return chosen


def build_V_N(F, alpha: int) -> List[int]:
    """Arm (b): span of nine consecutive conjugates of a normal element."""
    conj = []
    x = alpha
    for _ in range(N):
        conj.append(x)
        x = F.sqr(x)
    # Prefer first 9 conjugates; fall back to any 9 independent.
    basis = span_basis(conj[:9], L)
    if len(basis) < L:
        basis = span_basis(conj, L)
    if len(basis) != L:
        raise RuntimeError(f"V_N basis dim {len(basis)} != {L}")
    return basis


def build_V_S(F, octic: int) -> List[int]:
    """Arm (c): V_S = F_2 + ker g(σ) for octic g | Phi_17."""
    M = frobenius_matrix(F)
    gM = mat_poly_apply(octic, M)
    ker = nullspace_gf2(gM)
    elems = [vec_to_field(v) for v in ker]
    elems.append(1)  # F_2 = {0,1}
    basis = span_basis(elems, L)
    if len(basis) != L:
        raise RuntimeError(
            f"V_S basis dim {len(basis)} != {L} for octic={bin(octic)}"
        )
    # Frobenius-stability check: σ(b) ∈ span(basis) for each basis vector.
    Bmat = np.stack([field_to_vec(b) for b in basis], axis=1).astype(np.uint8)
    for b in basis:
        sb = F.sqr(b)
        if not _in_span(Bmat, field_to_vec(sb)):
            raise RuntimeError("V_S not Frobenius-stable under constructed basis")
    return basis


def _in_span(Bmat: np.ndarray, target: np.ndarray) -> bool:
    """Return True iff target ∈ column-span(Bmat) over F_2."""
    A = np.concatenate(
        [Bmat.astype(np.uint8).copy(), target.astype(np.uint8).reshape(-1, 1)],
        axis=1,
    )
    m, n = A.shape
    r = 0
    for col in range(n - 1):
        piv = None
        for i in range(r, m):
            if A[i, col]:
                piv = i
                break
        if piv is None:
            continue
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        for i in range(m):
            if i != r and A[i, col]:
                A[i] ^= A[r]
        r += 1
    for i in range(r, m):
        if A[i, n - 1]:
            return False
    return True


def build_V_R(F, rng: np.random.Generator) -> List[int]:
    """Arm (d): random 9-dimensional subspace of F_{2^17}."""
    while True:
        vecs = [int(rng.integers(1, F.q)) for _ in range(L + 4)]
        basis = span_basis(vecs, L)
        if len(basis) == L:
            return basis


def all_V_elements(basis: Sequence[int]) -> List[int]:
    out = []
    for mask in range(1 << L):
        x = 0
        for j in range(L):
            if (mask >> j) & 1:
                x ^= basis[j]
        out.append(x)
    return out


def oracle_A_general(F, B: int, xR: int, V_basis: Sequence[int]) -> List[int]:
    """Oracle A over arbitrary 9-dim V: roots of S_3 in V×V."""
    _ensure_e94_path()
    from oracles_rc1 import _roots_quadratic  # type: ignore

    V = all_V_elements(V_basis)
    Vset = set(V)
    out = []
    xR2 = F.mul(xR, xR)
    for x1 in V:
        x12 = F.mul(x1, x1)
        roots = _roots_quadratic(
            F, x12 ^ xR2, F.mul(x1, xR), F.mul(x12, xR2) ^ B
        )
        if roots is None:
            roots = V
        for x2 in roots:
            if x2 in Vset:
                # Encode as 18-bit coord pair in the V-basis later if needed;
                # for sat/unsat we only need existence.
                out.append((x1, x2))
    return out


def saturation_count(F, V_basis: Sequence[int]) -> Dict[str, Any]:
    """Pre-data predictor: dim of products V·V inside the ambient field.

    Reports dim(span{u*v : u,v in V}) over F_2 (as bit-vectors). This is the
    multiplication-tensor image dimension used as a cheap H1 predictor; not a
    full Macaulay saturation count.
    """
    V = all_V_elements(V_basis)
    prods = []
    for i, u in enumerate(V):
        for v in V[i:]:
            prods.append(F.mul(u, v))
    basis = span_basis(prods, N)
    return {
        "dim_V": L,
        "dim_VV": len(basis),
        "n_products_enumerated": len(prods),
        "note": "dim span{u*v : u,v in V} over F_2; H1 predictor proxy",
    }


def load_targets() -> List[Dict[str, Any]]:
    inst = json.loads((ARCHIVED_RUN / "instance-sets.json").read_text(encoding="utf-8"))
    targets: List[Dict[str, Any]] = []
    for sname in ("U62", "S62", "C20"):
        for row in inst["sets"][sname]:
            targets.append(
                {
                    "set": sname,
                    "idx": row["idx"],
                    "key": row["key"],
                    "x_R": int(row["archived"]["x_R"]),
                }
            )
    return targets


def cp95(x: int, n: int) -> Dict[str, Any]:
    _ensure_e94_path()
    from stats_exact import clopper_pearson, public  # type: ignore

    return public(clopper_pearson(x, n))


def engine_cert_ok(cert, eqs) -> bool:
    _ensure_e94_path()
    from closure import eval_cert  # type: ignore

    return eval_cert(cert, eqs) == [0]


def verify_orbit_certs(
    F,
    V_basis: List[int],
    xR: int,
    field_inv: np.ndarray,
) -> Dict[str, Any]:
    """Proposition F observational check on a Frobenius-stable V.

    For i = 0..16, descend at the co-conjugated parameters
    (B^{2^i}, x_R^{2^i}), require oracle-A unsat and W_4 refutation, and
    accept an engine-side eval_cert certificate. (Stock verify_cert.py is
    polynomial-V-specific and is not the success path under this card.)

    Holding B fixed while conjugating only x_R is incorrect for Semaev
    descent: the curve constant must be Frobenius-conjugated with x_R.
    """
    from basis_swap import descended_E_general  # noqa: WPS433
    from instances import eqs_of  # type: ignore
    from closure import Closure  # type: ignore

    cl = Closure(18, 4, 17)
    ok = 0
    details = []
    x = xR
    B = CURVE_B
    for i in range(N):
        roots = oracle_A_general(F, B, x, V_basis)
        E = descended_E_general(F, B, x, V_basis, field_inv)
        eqs = eqs_of(E)
        rec, cert = cl.w_closure(eqs, want_cert=True)
        w_one = bool(rec["one"])
        cert_ok = bool(cert is not None and engine_cert_ok(cert, eqs))
        good = (len(roots) == 0) and w_one and cert_ok
        ok += int(good)
        details.append(
            {
                "i": i,
                "B": B,
                "x_R": x,
                "oracle_A_sat": len(roots) > 0,
                "W4_one": w_one,
                "eval_cert_ok": cert_ok,
                "ok": good,
            }
        )
        x = F.sqr(x)
        B = F.sqr(B)
    return {
        "n_verify": ok,
        "n_orbit": N,
        "agreement": f"{ok}/{N}",
        "exact": ok == N,
        "mode": "reclose_W4_on_Frobenius_conjugates_B_and_xR_engine_cert",
        "details": details,
    }


def run_stage2(progress_every: int = 8) -> Dict[str, Any]:
    _ensure_e94_path()
    from gf2n import TableField  # type: ignore
    from instances import eqs_of  # type: ignore
    from closure import Closure  # type: ignore
    from basis_swap import descended_E_general  # noqa: WPS433

    t0 = time.monotonic()
    F = TableField()
    rng = np.random.Generator(np.random.PCG64(SEED))
    # Deterministic stream: burn the Stage-1 GL(9) draw so arm-(d) is independent
    # of the arm-(a) matrix while remaining seed-bound.
    _ = rng.integers(0, 2, size=(L, L), dtype=np.uint8)

    alpha, _M_normal, _M_inv = find_normal_element(F)
    field_inv = np.eye(NEQ, dtype=np.uint8)

    sets_spec = [
        {"id": "V_N", "arm": "b", "basis": build_V_N(F, alpha), "stable": False},
    ]
    for gi, g in enumerate(PHI17_OCTICS):
        sets_spec.append(
            {
                "id": f"V_S_octic{gi+1}",
                "arm": "c",
                "octic": g,
                "octic_bin": bin(g),
                "basis": build_V_S(F, g),
                "stable": True,
            }
        )
    sets_spec.append(
        {"id": "V_R", "arm": "d", "basis": build_V_R(F, rng), "stable": False}
    )

    targets = load_targets()
    if len(targets) != 144:
        return {
            "ok": False,
            "outcome": "O-IMPEDIMENT",
            "reason": f"expected 144 targets, got {len(targets)}",
            "amazon_bedrock": "NOT SELECTED",
        }

    cl = Closure(18, 4, 17)
    per_set: Dict[str, Any] = {}
    artifact = False
    artifact_reason = ""

    for spec in sets_spec:
        sid = spec["id"]
        V_basis = spec["basis"]
        sat = saturation_count(F, V_basis)
        rows: List[Dict[str, Any]] = []
        u62_w4 = u62_m4 = 0
        u62_n = 0
        s62_refuted = 0
        orbit_records: List[Dict[str, Any]] = []

        archive_s62_unsat = 0
        archive_s62_sat = 0
        soundness_violations = 0
        for i, tgt in enumerate(targets):
            # Oracle A under the *current* V. Archive S62/U62 labels are
            # poly-V-relative (e94b27 oracles_rc1.oracle_A) and do not bind
            # sat/unsat under a new V (AMD-20261003-894083 / EV-CERTBIN-383c07).
            roots = oracle_A_general(F, CURVE_B, tgt["x_R"], V_basis)
            sat_flag = len(roots) > 0
            if tgt["set"] == "S62":
                if sat_flag:
                    archive_s62_sat += 1
                else:
                    archive_s62_unsat += 1

            E = descended_E_general(F, CURVE_B, tgt["x_R"], V_basis, field_inv)
            eqs = eqs_of(E)
            rec_m, _ = cl.macaulay_closure(eqs, want_cert=False)
            rec_w, _ = cl.w_closure(eqs, want_cert=False)
            m_one = bool(rec_m["one"])
            w_one = bool(rec_w["one"])
            # Soundness only: current-V oracle-A-sat must not be refuted.
            if sat_flag and (m_one or w_one):
                soundness_violations += 1
                artifact = True
                artifact_reason = (
                    f"closure refuted oracle-A-satisfiable (current-V) target "
                    f"{tgt['key']} under {sid} (M_4={m_one}, W_4={w_one})"
                )
            # Observational transfer count (not an artifact under AMD-894083).
            if tgt["set"] == "S62" and (m_one or w_one):
                s62_refuted += 1

            if tgt["set"] == "U62":
                u62_n += 1
                u62_m4 += int(m_one)
                u62_w4 += int(w_one)
                # Prop F orbit check once per stable set on the first W_4-refuted
                # U62 target (17 conjugate reclosures); full 62×17 would dominate
                # the Stage-2 budget without changing the per-orbit predicate.
                if (
                    spec["stable"]
                    and w_one
                    and not sat_flag
                    and not orbit_records
                ):
                    orb = verify_orbit_certs(F, V_basis, tgt["x_R"], field_inv)
                    orbit_records.append(
                        {
                            "key": tgt["key"],
                            "x_R": tgt["x_R"],
                            "orbit": {
                                "n_verify": orb["n_verify"],
                                "n_orbit": orb["n_orbit"],
                                "agreement": orb["agreement"],
                                "exact": orb["exact"],
                                "mode": orb["mode"],
                            },
                        }
                    )
                    if not orb["exact"]:
                        artifact = True
                        artifact_reason = (
                            f"Prop F orbit reclose/cert verify {orb['agreement']} "
                            f"on {sid} target {tgt['key']} "
                            f"(conjugated B and x_R)"
                        )

            rows.append(
                {
                    "key": tgt["key"],
                    "set": tgt["set"],
                    "idx": tgt["idx"],
                    "x_R": tgt["x_R"],
                    "oracle_A_sat": sat_flag,
                    "oracle_A_n_roots": len(roots),
                    "M_4": {
                        "one": m_one,
                        "label": "refuted" if m_one else "not_refuted",
                        "rank": int(rec_m["rank"]),
                    },
                    "W_4": {
                        "one": w_one,
                        "label": "refuted" if w_one else "not_refuted",
                        "final_dim": int(rec_w["final_dim"]),
                        "iterations_to_fixpoint": int(rec_w["iterations_to_fixpoint"]),
                        "one_first_iteration": rec_w.get("one_first_iteration"),
                    },
                }
            )
            if progress_every and (i + 1) % progress_every == 0:
                print(
                    f"stage2 {sid} progress {i+1}/144; "
                    f"U62 W4={u62_w4}/{u62_n}",
                    flush=True,
                )

        w4_ci = cp95(u62_w4, u62_n)
        m4_ci = cp95(u62_m4, u62_n)
        per_set[sid] = {
            "arm": spec["arm"],
            "octic_bin": spec.get("octic_bin"),
            "frobenius_stable": spec["stable"],
            "V_basis": V_basis,
            "saturation": sat,
            "U62": {
                "n": u62_n,
                "W4_refuted": u62_w4,
                "M4_refuted": u62_m4,
                "W4_rate_cp95": w4_ci,
                "M4_rate_cp95": m4_ci,
            },
            "S62_refuted_count": s62_refuted,
            "S62_refuted_count_note": (
                "Observational: archive-S62 rows with M_4 or W_4 one under "
                "this V. Not an O-ARTIFACT trigger under AMD-20261003-894083 "
                "(archive labels are poly-V-relative)."
            ),
            "archive_S62_transfer": {
                "sat_under_current_V": archive_s62_sat,
                "unsat_under_current_V": archive_s62_unsat,
                "n_archive_S62": archive_s62_sat + archive_s62_unsat,
            },
            "soundness_violations": soundness_violations,
            "orbit_cert_verifications": orbit_records,
            "n_rows": len(rows),
            # Compact: keep full rows out of primary return; caller may persist.
            "rows": rows,
        }

    # Decision thresholds on structured sets: V_N and both V_S octics.
    def rate_of(sid: str) -> float:
        return float(per_set[sid]["U62"]["W4_rate_cp95"]["rate"])

    r_vn = rate_of("V_N")
    r_vs1 = rate_of("V_S_octic1")
    r_vs2 = rate_of("V_S_octic2")
    r_vs = min(r_vs1, r_vs2)
    structured = {"V_N": r_vn, "V_S_octic1": r_vs1, "V_S_octic2": r_vs2, "V_S_min": r_vs}

    if artifact:
        outcome = "O-ARTIFACT"
        reason = artifact_reason
    elif r_vn >= E_SET_MIN and r_vs >= E_SET_MIN:
        outcome = "O-E-SET"
        reason = (
            f"Arm-(a) precondition cleared; structured W_4 rates "
            f"V_N={r_vn:.4f}, V_S_min={r_vs:.4f} both >= {E_SET_MIN}"
        )
    elif r_vn <= E_POLY_MAX or r_vs <= E_POLY_MAX:
        outcome = "O-E-POLY"
        reason = (
            f"Structured W_4 rate <= {E_POLY_MAX}: "
            f"V_N={r_vn:.4f}, V_S_min={r_vs:.4f}"
        )
    else:
        outcome = "O-MIXED"
        reason = (
            f"Structured W_4 rates between thresholds: "
            f"V_N={r_vn:.4f}, V_S_min={r_vs:.4f}"
        )

    # Strip bulky rows from summary; persist separately by caller.
    summary_sets = {}
    full_rows = {}
    for sid, payload in per_set.items():
        full_rows[sid] = payload["rows"]
        slim = dict(payload)
        del slim["rows"]
        summary_sets[sid] = slim

    return {
        "ok": True,
        "outcome": outcome,
        "reason": reason,
        "structured_w4_rates": structured,
        "thresholds": {"E_SET_min": E_SET_MIN, "E_POLY_max": E_POLY_MAX},
        "normal_alpha": alpha,
        "seed": SEED,
        "curve_B": CURVE_B,
        "n_targets": len(targets),
        "per_set": summary_sets,
        "per_set_rows": full_rows,
        "control_policy": {
            "amendment_id": "AMD-20261003-d292c9",
            "prior_void_evidence": "EV-CERTBIN-383c07",
            "soundness_void": "oracle_A_sat(current V) and (M_4 or W_4) one",
            "archive_S62_transfer_is_artifact": False,
            "archive_label_scope": (
                "U62/S62/C20 labels relative to polynomial-V oracle_A "
                "of RUN-CERTBIN-c417e0; non-transfer under new V is "
                "observed, not O-ARTIFACT"
            ),
            "rate_scope": (
                "CP95 W_4/M_4 on archived U62 under current V; when W_4 "
                "matches current-V unsat (sound+complete), the rate equals "
                "the fraction of archive-U62 remaining unsat under that V"
            ),
        },
        "precondition": {
            "stage1_outcome": "O-ARM-A-PASS",
            "arm_a_agreement": "288/288",
            "evidence": "EV-CERTBIN-f218ae",
            "decision": "DEC-20261003-b8f938",
        },
        "elapsed_s": time.monotonic() - t0,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False},
        "certificate": {
            "kind": "engine_eval_orbit",
            "note": (
                "Prop F orbit checks use closure.eval_cert on conjugate eqs; "
                "e94b27 verify_cert.py is polynomial-V-specific and is not the "
                "success path under this card."
            ),
        },
    }
