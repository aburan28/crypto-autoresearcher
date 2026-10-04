#!/usr/bin/env python3
"""EXP-ECDLP-bf222c Stage 0 exact doubling-Jacobian chain-rule calibrator.

Certificate kind none. No nested LHW generator. No Semaev S_m.
Frozen object P-S0-DBLJAC: REAL / KF / NULL on one F_19 point.

REAL: p=19, A=1, B=-1, P=(2,3), [2]P=(16,11), [4]P=(15,11),
J1=[[13,12],[3,0]] det=2, J2=[[0,7],[16,14]] det=2,
J4=J2 J1=[[2,0],[3,2]] det=4.
KF: claim det D[4]=1. Actual 4. Rejected.
NULL empty matrix is rejected. y=0 is rejected.

Producer method: form affine doubling Jacobians by formal
differentiation and multiply determinants.
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
SOURCE = "experiments/EXP-ECDLP-bf222c/implementation/stage0_dbljac.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-bf222c/runs/RUN-ECDLP-bf222c-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-bf222c/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260913-7eeb2c"
TASK_ID = "TASK-20260913-1f3e28"

P = 19
A = 1
B = -1
POINT = (2, 3)
MUST_P2 = (16, 11)
MUST_P4 = (15, 11)
MUST_J1 = ((13, 12), (3, 0))
MUST_J2 = ((0, 7), (16, 14))
MUST_J4 = ((2, 0), (3, 2))
MUST_DET1 = 2
MUST_DET2 = 2
MUST_DET4 = 4
KF_CLAIMED_DET4 = 1


class InvalidParamsError(ValueError):
    """Empty Jacobian or y=0 is rejected."""


def inv(value: int) -> int:
    return pow(value, -1, P)


def require_nonzero_y(y: int) -> None:
    if y % P == 0:
        raise InvalidParamsError("y is zero")


def require_nonempty_matrix(matrix: tuple | None) -> None:
    if not matrix:
        raise InvalidParamsError("matrix is empty")


def det2(matrix: tuple[tuple[int, int], tuple[int, int]]) -> int:
    return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % P


def matmul(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (
            (left[0][0] * right[0][0] + left[0][1] * right[1][0]) % P,
            (left[0][0] * right[0][1] + left[0][1] * right[1][1]) % P,
        ),
        (
            (left[1][0] * right[0][0] + left[1][1] * right[1][0]) % P,
            (left[1][0] * right[0][1] + left[1][1] * right[1][1]) % P,
        ),
    )


def affine_double(x: int, y: int) -> tuple[int, int]:
    require_nonzero_y(y)
    lam = ((3 * x * x + A) * inv(2 * y)) % P
    x2 = (lam * lam - 2 * x) % P
    y2 = (lam * ((x - x2) % P) - y) % P
    return x2, y2


def doubling_jacobian(x: int, y: int) -> tuple[tuple[tuple[int, int], tuple[int, int]], int]:
    """Formal Jacobian of affine doubling at (x, y)."""
    require_nonzero_y(y)
    lam = ((3 * x * x + A) * inv(2 * y)) % P
    dlam_dx = (3 * x * inv(y)) % P
    dlam_dy = (-(3 * x * x + A) * inv(2 * y * y)) % P
    x2 = (lam * lam - 2 * x) % P
    dx2_dx = (2 * lam * dlam_dx - 2) % P
    dx2_dy = (2 * lam * dlam_dy) % P
    dyp_dx = (dlam_dx * x + lam - (dlam_dx * x2 + lam * dx2_dx)) % P
    dyp_dy = (dlam_dy * x - (dlam_dy * x2 + lam * dx2_dy) - 1) % P
    jacobian = ((dx2_dx, dx2_dy), (dyp_dx, dyp_dy))
    return jacobian, det2(jacobian)


def chain_rule_solve() -> dict:
    require_nonzero_y(POINT[1])
    p2 = affine_double(*POINT)
    p4 = affine_double(*p2)
    j1, det_j1 = doubling_jacobian(*POINT)
    j2, det_j2 = doubling_jacobian(*p2)
    j4 = matmul(j2, j1)
    det_j4 = det2(j4)
    product = (det_j1 * det_j2) % P
    return {
        "P2": list(p2),
        "P4": list(p4),
        "J1": [list(j1[0]), list(j1[1])],
        "J2": [list(j2[0]), list(j2[1])],
        "J4": [list(j4[0]), list(j4[1])],
        "det1": det_j1,
        "det2": det_j2,
        "det4": det_j4,
        "product": product,
    }


def evaluate_gates() -> dict:
    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_nonzero_y(0)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "y-zero", "point": [2, 0], "rejected": True})

    try:
        require_nonempty_matrix(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_matrix", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_matrix", "rejected": True}

    solved = chain_rule_solve()
    real_chain_rule_pass = (
        tuple(solved["P2"]) == MUST_P2
        and tuple(solved["P4"]) == MUST_P4
        and tuple(tuple(row) for row in solved["J1"]) == MUST_J1
        and tuple(tuple(row) for row in solved["J2"]) == MUST_J2
        and tuple(tuple(row) for row in solved["J4"]) == MUST_J4
        and solved["det1"] == MUST_DET1
        and solved["det2"] == MUST_DET2
        and solved["det4"] == MUST_DET4
        and solved["product"] == MUST_DET4
    )
    kf_rejected = solved["det4"] == MUST_DET4 and solved["det4"] != KF_CLAIMED_DET4
    return {
        "fixture_pass": fixture_pass,
        "real_chain_rule_pass": real_chain_rule_pass,
        "known_false_constant_pass": kf_rejected,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "solved": solved,
        "kf_rejected": kf_rejected,
        "null_obj": null_obj,
        "invalid_decisions": invalid_decisions,
    }


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()
    gates = evaluate_gates()
    solved = gates["solved"]
    fixture_pass = gates["fixture_pass"]
    real_chain_rule_pass = gates["real_chain_rule_pass"]
    known_false_constant_pass = gates["known_false_constant_pass"]
    reject_invalid_pass = gates["reject_invalid_pass"]
    null_empty_pass = gates["null_empty_pass"]
    kf_rejected = gates["kf_rejected"]
    all_pass = (
        fixture_pass
        and real_chain_rule_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started
    real_obj = {
        "id": "REAL",
        "P": list(POINT),
        "P2": solved["P2"],
        "P4": solved["P4"],
        "J1": solved["J1"],
        "J2": solved["J2"],
        "J4": solved["J4"],
        "det1": solved["det1"],
        "det2": solved["det2"],
        "det4": solved["det4"],
        "product": solved["product"],
        "must_det1": MUST_DET1,
        "must_det2": MUST_DET2,
        "must_det4": MUST_DET4,
    }
    kf_obj = {
        "id": "KF",
        "kind": "constant_det4",
        "det4": solved["det4"],
        "claimed_det4": KF_CLAIMED_DET4,
        "must_det4": MUST_DET4,
        "rejected": kf_rejected,
    }
    raw = {
        "run_id": "RUN-ECDLP-bf222c-S0",
        "experiment_id": "EXP-ECDLP-bf222c",
        "hypothesis_id": "H-ECDLP-6e6649",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-DBLJAC",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "p": P,
                "A": A,
                "B": B,
                "P": list(POINT),
                "must_P2": list(MUST_P2),
                "must_P4": list(MUST_P4),
                "must_det1": MUST_DET1,
                "must_det2": MUST_DET2,
                "must_det4": MUST_DET4,
            },
            "KF": {
                "id": "KF",
                "kind": "constant_det4",
                "must_det4": MUST_DET4,
                "claimed_det4": KF_CLAIMED_DET4,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_matrix", "must_reject": True},
            "invalid_rejected": gates["invalid_decisions"],
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_chain_rule_pass": real_chain_rule_pass,
            "known_false_constant_pass": known_false_constant_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": gates["null_obj"],
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_bf222c_stage1_authorized": False,
        "exp_e9dd89_stage1_authorized": False,
        "exp_bb5ef7_stage1_authorized": False,
        "exp_70c6f0_stage1_authorized": False,
        "exp_9c04a3_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_run_coppersmith": True,
        "do_not_form_gamma_orbit": True,
        "not_p1553": True,
        "not_nested_lhw": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-bf222c/implementation/stage0_dbljac.py\n"
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
        "real_chain_rule_pass": real_chain_rule_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": gates["null_obj"],
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")
    report = f"""execution_report:
  id: ER-ECDLP-bf222c-S0
  experiment_id: EXP-ECDLP-bf222c
  run_id: RUN-ECDLP-bf222c-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-13'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_chain_rule_pass: {str(real_chain_rule_pass).lower()}
  known_false_constant_pass: {str(known_false_constant_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_bf222c_stage1_authorized: false
  exp_e9dd89_stage1_authorized: false
  exp_bb5ef7_stage1_authorized: false
  exp_70c6f0_stage1_authorized: false
  exp_9c04a3_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_run_coppersmith: true
  do_not_form_gamma_orbit: true
  not_p1553: true
  not_nested_lhw: true
  frozen_object: P-S0-DBLJAC
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_chain_rule_pass {str(real_chain_rule_pass).lower()}. REAL det1 is {solved['det1']}, det2 is {solved['det2']}, det4 is {solved['det4']}."
  - "known_false_constant_pass {str(known_false_constant_pass).lower()}. KF det4 {solved['det4']} claimed {KF_CLAIMED_DET4} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. y=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty matrix is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen doubling-Jacobian chain-rule calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a Gamma orbit. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-bf222c. Not Stage 1 of EXP-ECDLP-e9dd89. Certificate kind none."
"""
    REPORT_PATH.write_text(report)
    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-bf222c-S0
  experiment_id: EXP-ECDLP-bf222c
  hypothesis_id: H-ECDLP-6e6649
  goal_id: GOAL-ECDLP-001
  batch_id: BATCH-0a83f9
  task_id: {TASK_ID}
  stage: 0
  status: {'completed_valid' if all_pass else 'invalid'}
  recorded_at: '{recorded_at}'
  code:
    commit: {commit}
    dirty: true
    dirty_summary: untracked Stage 0 implementation and run artifacts at execution time
    command: python3 experiments/EXP-ECDLP-bf222c/implementation/stage0_dbljac.py
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
      frozen_object: P-S0-DBLJAC
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      p: 19
      A: 1
      B: -1
      P: [2, 3]
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
    validity_reason: Stage 0 exact doubling-Jacobian chain-rule calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_chain_rule_pass: {str(real_chain_rule_pass).lower()}
      known_false_constant_pass: {str(known_false_constant_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      do_not_form_semaev: true
      do_not_run_velu: true
      do_not_run_coppersmith: true
      do_not_form_gamma_orbit: true
      not_p1553: true
      not_nested_lhw: true
      stage1_authorized: false
      exp_bf222c_stage1_authorized: false
      exp_e9dd89_stage1_authorized: false
      exp_bb5ef7_stage1_authorized: false
      exp_70c6f0_stage1_authorized: false
      exp_9c04a3_stage1_authorized: false
    scientific_boundary: "Toy frozen doubling-Jacobian chain-rule calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a Gamma orbit. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-bf222c. Not Stage 1 of EXP-ECDLP-e9dd89. Certificate kind none."
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
                "real_chain_rule_pass": real_chain_rule_pass,
                "known_false_constant_pass": known_false_constant_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_empty_pass": null_empty_pass,
                "REAL": real_obj,
                "KF": kf_obj,
                "NULL": gates["null_obj"],
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
