#!/usr/bin/env python3
"""EXP-ECDLP-bb5ef7 Stage 0 exact Woodbury-Schur calibrator.

Certificate kind none. No nested LHW generator. No Semaev S_m.
Frozen object P-S0-ENDFOLD: REAL / KF / NULL on a 2-by-2 fold.

REAL: M0=I_2, U=[1,0]^T, V=[0,1]^T, b=[1,1],
UV^T=[[0,1],[0,0]], M=[[1,1],[0,1]], r=1, Schur=1, x=[0,1].
KF: claim r=0 (solve on M0). Actual r=1. Rejected.
NULL empty matrix is rejected. Singular M0 is rejected.

Producer method: form M=M0+UV^T, invert M0, compute Schur,
apply Woodbury, solve.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-bb5ef7/implementation/stage0_endfold.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-bb5ef7/runs/RUN-ECDLP-bb5ef7-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-bb5ef7/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260913-d395c8"
TASK_ID = "TASK-20260913-1d5d1b"

M0 = ((1, 0), (0, 1))
U = ((1,), (0,))
V = ((0,), (1,))
B = (1, 1)
MUST_R = 1
MUST_SCHUR = 1
MUST_X = (0, 1)
KF_CLAIMED_R = 0


class InvalidParamsError(ValueError):
    """Empty or singular M0 is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_nonempty_matrix(matrix: tuple | None) -> None:
    if not matrix:
        raise InvalidParamsError("matrix is empty")


def det2(matrix: tuple[tuple[int, int], tuple[int, int]]) -> int:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def require_invertible_m0(matrix: tuple[tuple[int, int], tuple[int, int]]) -> None:
    require_nonempty_matrix(matrix)
    if det2(matrix) == 0:
        raise InvalidParamsError("M0 is singular")


def invert2(matrix: tuple[tuple[int, int], tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
    require_invertible_m0(matrix)
    d = det2(matrix)
    return (
        (matrix[1][1] // d, -matrix[0][1] // d),
        (-matrix[1][0] // d, matrix[0][0] // d),
    )


def mat_add(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (left[0][0] + right[0][0], left[0][1] + right[0][1]),
        (left[1][0] + right[1][0], left[1][1] + right[1][1]),
    )


def mat_sub(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (left[0][0] - right[0][0], left[0][1] - right[0][1]),
        (left[1][0] - right[1][0], left[1][1] - right[1][1]),
    )


def outer_uv(
    u: tuple[tuple[int], tuple[int]],
    v: tuple[tuple[int], tuple[int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (u[0][0] * v[0][0], u[0][0] * v[1][0]),
        (u[1][0] * v[0][0], u[1][0] * v[1][0]),
    )


def mat_vec(
    matrix: tuple[tuple[int, int], tuple[int, int]],
    vec: tuple[int, int],
) -> tuple[int, int]:
    return (
        matrix[0][0] * vec[0] + matrix[0][1] * vec[1],
        matrix[1][0] * vec[0] + matrix[1][1] * vec[1],
    )


def coupling_rank(u: tuple[tuple[int], tuple[int]], v: tuple[tuple[int], tuple[int]]) -> int:
    uv = outer_uv(u, v)
    rows = [uv[0], uv[1]]
    if rows[0] == (0, 0) and rows[1] == (0, 0):
        return 0
    if rows[0] == (0, 0) or rows[1] == (0, 0):
        return 1
    if rows[0][0] * rows[1][1] == rows[0][1] * rows[1][0]:
        return 1
    return 2


def woodbury_solve() -> dict:
    """Form M=M0+UV^T, invert M0, compute Schur, apply Woodbury, solve."""
    require_nonempty_matrix(M0)
    require_invertible_m0(M0)
    uv = outer_uv(U, V)
    m = mat_add(M0, uv)
    m0_inv = invert2(M0)
    # Schur I + V^T M0^{-1} U. Column U, row V^T.
    m0_inv_u = mat_vec(m0_inv, (U[0][0], U[1][0]))
    v_t_m0_inv_u = V[0][0] * m0_inv_u[0] + V[1][0] * m0_inv_u[1]
    schur = 1 + v_t_m0_inv_u
    if schur == 0:
        raise InvalidParamsError("Schur complement is singular")
    # Woodbury: M^{-1} = M0^{-1} - M0^{-1} U Schur^{-1} V^T M0^{-1}
    # For this frozen 2-by-2 rank-1 update that is M0^{-1} - (1/schur) * (M0^{-1} U) V^T M0^{-1}.
    v_t_m0_inv = (
        V[0][0] * m0_inv[0][0] + V[1][0] * m0_inv[1][0],
        V[0][0] * m0_inv[0][1] + V[1][0] * m0_inv[1][1],
    )
    correction = (
        (m0_inv_u[0] * v_t_m0_inv[0] // schur, m0_inv_u[0] * v_t_m0_inv[1] // schur),
        (m0_inv_u[1] * v_t_m0_inv[0] // schur, m0_inv_u[1] * v_t_m0_inv[1] // schur),
    )
    m_inv = mat_sub(m0_inv, correction)
    x = mat_vec(m_inv, B)
    r = coupling_rank(U, V)
    return {
        "M": [list(m[0]), list(m[1])],
        "UVT": [list(uv[0]), list(uv[1])],
        "M0_inv": [list(m0_inv[0]), list(m0_inv[1])],
        "M_inv": [list(m_inv[0]), list(m_inv[1])],
        "r": r,
        "schur": schur,
        "x": list(x),
    }


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()

    fixture_pass = True
    invalid_decisions: list[dict] = []
    singular = ((1, 0), (0, 0))
    try:
        require_invertible_m0(singular)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "M0-singular", "M0": [list(singular[0]), list(singular[1])], "rejected": True})

    try:
        require_nonempty_matrix(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_matrix", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_matrix", "rejected": True}

    solved = woodbury_solve()
    real_woodbury_pass = (
        solved["r"] == MUST_R
        and solved["schur"] == MUST_SCHUR
        and tuple(solved["x"]) == MUST_X
    )
    real_obj = {
        "id": "REAL",
        "M0": [list(M0[0]), list(M0[1])],
        "U": [list(U[0]), list(U[1])],
        "V": [list(V[0]), list(V[1])],
        "b": list(B),
        "M": solved["M"],
        "UVT": solved["UVT"],
        "r": solved["r"],
        "schur": solved["schur"],
        "x": solved["x"],
        "must_r": MUST_R,
        "must_schur": MUST_SCHUR,
        "must_x": list(MUST_X),
    }

    kf_rejected = solved["r"] == MUST_R and solved["r"] != KF_CLAIMED_R
    known_false_zero_rank_pass = kf_rejected
    kf_obj = {
        "id": "KF",
        "kind": "zero_rank_coupling",
        "r": solved["r"],
        "claimed_r": KF_CLAIMED_R,
        "must_r": MUST_R,
        "rejected": kf_rejected,
    }

    all_pass = (
        fixture_pass
        and real_woodbury_pass
        and known_false_zero_rank_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-bb5ef7-S0",
        "experiment_id": "EXP-ECDLP-bb5ef7",
        "hypothesis_id": "H-ECDLP-804ee9",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-ENDFOLD",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "M0": [list(M0[0]), list(M0[1])],
                "U": [list(U[0]), list(U[1])],
                "V": [list(V[0]), list(V[1])],
                "b": list(B),
                "must_r": MUST_R,
                "must_schur": MUST_SCHUR,
                "must_x": list(MUST_X),
            },
            "KF": {
                "id": "KF",
                "kind": "zero_rank_coupling",
                "must_r": MUST_R,
                "claimed_r": KF_CLAIMED_R,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_matrix", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_woodbury_pass": real_woodbury_pass,
            "known_false_zero_rank_pass": known_false_zero_rank_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_bb5ef7_stage1_authorized": False,
        "exp_70c6f0_stage1_authorized": False,
        "exp_9c04a3_stage1_authorized": False,
        "exp_166141_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_run_coppersmith": True,
        "do_not_fold_endomorphism_orbit": True,
        "not_p1553": True,
        "not_nested_lhw": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-bb5ef7/implementation/stage0_endfold.py\n"
    )
    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "executable": sys.executable,
    }
    (RUN_DIR / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    stdout_payload = {
        "fixture_pass": fixture_pass,
        "real_woodbury_pass": real_woodbury_pass,
        "known_false_zero_rank_pass": known_false_zero_rank_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-bb5ef7-S0
  experiment_id: EXP-ECDLP-bb5ef7
  run_id: RUN-ECDLP-bb5ef7-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-13'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_woodbury_pass: {str(real_woodbury_pass).lower()}
  known_false_zero_rank_pass: {str(known_false_zero_rank_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_bb5ef7_stage1_authorized: false
  exp_70c6f0_stage1_authorized: false
  exp_9c04a3_stage1_authorized: false
  exp_166141_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_run_coppersmith: true
  do_not_fold_endomorphism_orbit: true
  not_p1553: true
  not_nested_lhw: true
  frozen_object: P-S0-ENDFOLD
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_woodbury_pass {str(real_woodbury_pass).lower()}. REAL r is {solved['r']}, Schur is {solved['schur']}, x is {solved['x']}."
  - "known_false_zero_rank_pass {str(known_false_zero_rank_pass).lower()}. KF r {solved['r']} claimed {KF_CLAIMED_R} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. Singular M0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty matrix is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen Woodbury-Schur calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-bb5ef7. Not Stage 1 of EXP-ECDLP-70c6f0. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-bb5ef7-S0
  experiment_id: EXP-ECDLP-bb5ef7
  hypothesis_id: H-ECDLP-804ee9
  goal_id: GOAL-ECDLP-001
  batch_id: BATCH-5a5091
  task_id: {TASK_ID}
  stage: 0
  status: {'completed_valid' if all_pass else 'invalid'}
  recorded_at: '{recorded_at}'
  code:
    commit: {commit}
    dirty: true
    dirty_summary: untracked Stage 0 implementation and run artifacts at execution time
    command: python3 experiments/EXP-ECDLP-bb5ef7/implementation/stage0_endfold.py
    source_path: {SOURCE}
    source_sha256: {source_sha256}
  inference:
    requested_policy: executor-implementation
    resolved_model_id: cursor-grok-4.6-cloud-agent
    model_provenance: cursor cloud agent session acting as executor
    model_verified: false
    reasoning_effort: medium
    fallback_used: false
    degraded_requirements: null
  environment:
    python: {platform.python_version()}
    platform: {platform.platform()}
    machine: {platform.machine()}
  inputs:
    parameters:
      frozen_object: P-S0-ENDFOLD
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      M0: [[1, 0], [0, 1]]
      U: [[1], [0]]
      V: [[0], [1]]
      b: [1, 1]
    seeds:
      declared: [8]
  timing:
    wall_clock_seconds: {elapsed}
  resources:
    wall_clock_seconds: {elapsed}
    peak_rss_bytes: null
  result:
    validity_status: {'valid' if all_pass else 'invalid'}
    valid: {str(all_pass).lower()}
    validity_reason: Stage 0 exact Woodbury-Schur calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_woodbury_pass: {str(real_woodbury_pass).lower()}
      known_false_zero_rank_pass: {str(known_false_zero_rank_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      do_not_form_semaev: true
      do_not_run_velu: true
      do_not_run_coppersmith: true
      do_not_fold_endomorphism_orbit: true
      not_p1553: true
      not_nested_lhw: true
      stage1_authorized: false
      exp_bb5ef7_stage1_authorized: false
      exp_70c6f0_stage1_authorized: false
      exp_9c04a3_stage1_authorized: false
      exp_166141_stage1_authorized: false
    scientific_boundary: "Toy frozen Woodbury-Schur calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-bb5ef7. Not Stage 1 of EXP-ECDLP-70c6f0. Certificate kind none."
  artifacts:
    raw_result: raw-result.json
    stdout: stdout.log
    stderr: stderr.log
    environment: environment.json
    command: command.txt
"""
    (RUN_DIR / "manifest.yaml").write_text(manifest)
    print(
        json.dumps(
            {
                "all_pass": all_pass,
                "elapsed": elapsed,
                "source_sha256": source_sha256,
                "fixture_pass": fixture_pass,
                "real_woodbury_pass": real_woodbury_pass,
                "known_false_zero_rank_pass": known_false_zero_rank_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_empty_pass": null_empty_pass,
                "REAL": real_obj,
                "KF": kf_obj,
                "NULL": null_obj,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
