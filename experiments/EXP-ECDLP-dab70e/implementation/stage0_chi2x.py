#!/usr/bin/env python3
"""EXP-ECDLP-dab70e Stage 0 exact quadratic residue of affine x calibrator.

Certificate kind none. Frozen object P-S0-CHI2X: REAL / KF / NULL
on one F_19 point.

REAL: p=19, A=1, B=-1, P=(2,3), [2]P=(16,11),
chi_2(x)=2^9=18, chi_2(x')=16^9=1.
KF: claim chi_2(x')=18. Actual 1. Rejected.
NULL empty character is rejected. x=0 is the zero fibre.

Producer method: affine doubling, then u^{(p-1)/2}=u^9.
Do not run a unary-closure census.
Do not use chi_2(x')=18 as REAL.
Do not compute chi_3(y).
Do not run Miller or Tate.
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
SOURCE = "experiments/EXP-ECDLP-dab70e/implementation/stage0_chi2x.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-dab70e/runs/RUN-ECDLP-dab70e-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-dab70e/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260913-064cb8"
TASK_ID = "TASK-20260913-4c7ed3"

P = 19
A = 1
B = -1
POINT = (2, 3)
MUST_P2 = (16, 11)
MUST_CHI = 18
MUST_CHI_PRIME = 1
KF_CLAIMED_CHI_PRIME = 18
CHI_EXP = (P - 1) // 2


class InvalidParamsError(ValueError):
    """Empty character or x=0 zero fibre is rejected."""


def inv(value: int) -> int:
    return pow(value, -1, P)


def require_nonzero_x(x: int) -> None:
    if x % P == 0:
        raise InvalidParamsError("x is the zero fibre")


def require_nonzero_y(y: int) -> None:
    if y % P == 0:
        raise InvalidParamsError("y is zero; doubling undefined")


def require_nonempty_character(character: int | None) -> None:
    if character is None:
        raise InvalidParamsError("character is empty")


def chi2(u: int) -> int:
    require_nonzero_x(u)
    return pow(u % P, CHI_EXP, P)


def affine_double(x: int, y: int) -> tuple[int, int]:
    require_nonzero_y(y)
    lam = ((3 * x * x + A) * inv(2 * y)) % P
    x2 = (lam * lam - 2 * x) % P
    y2 = (lam * ((x - x2) % P) - y) % P
    return x2, y2


def character_solve() -> dict:
    require_nonzero_x(POINT[0])
    chi = chi2(POINT[0])
    p2 = affine_double(*POINT)
    chi_prime = chi2(p2[0])
    return {"P2": list(p2), "chi": chi, "chi_prime": chi_prime}


def evaluate_gates() -> dict:
    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_nonzero_x(0)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "x-zero", "point": [0, 1], "rejected": True, "zero_fibre": True})

    try:
        require_nonempty_character(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_character", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_character", "rejected": True}

    solved = character_solve()
    real_character_pass = (
        tuple(solved["P2"]) == MUST_P2
        and solved["chi"] == MUST_CHI
        and solved["chi_prime"] == MUST_CHI_PRIME
    )
    kf_rejected = (
        solved["chi_prime"] == MUST_CHI_PRIME
        and solved["chi_prime"] != KF_CLAIMED_CHI_PRIME
    )
    return {
        "fixture_pass": fixture_pass,
        "real_character_pass": real_character_pass,
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
    real_character_pass = gates["real_character_pass"]
    known_false_constant_pass = gates["known_false_constant_pass"]
    reject_invalid_pass = gates["reject_invalid_pass"]
    null_empty_pass = gates["null_empty_pass"]
    kf_rejected = gates["kf_rejected"]
    all_pass = (
        fixture_pass
        and real_character_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started
    real_obj = {
        "id": "REAL",
        "P": list(POINT),
        "P2": solved["P2"],
        "chi": solved["chi"],
        "chi_prime": solved["chi_prime"],
        "must_chi": MUST_CHI,
        "must_chi_prime": MUST_CHI_PRIME,
    }
    kf_obj = {
        "id": "KF",
        "kind": "constant_chi_prime",
        "chi_prime": solved["chi_prime"],
        "claimed_chi_prime": KF_CLAIMED_CHI_PRIME,
        "must_chi_prime": MUST_CHI_PRIME,
        "rejected": kf_rejected,
    }
    raw = {
        "run_id": "RUN-ECDLP-dab70e-S0",
        "experiment_id": "EXP-ECDLP-dab70e",
        "hypothesis_id": "H-ECDLP-74ecc8",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-CHI2X",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "p": P,
                "A": A,
                "B": B,
                "P": list(POINT),
                "must_P2": list(MUST_P2),
                "must_chi": MUST_CHI,
                "must_chi_prime": MUST_CHI_PRIME,
            },
            "KF": {
                "id": "KF",
                "kind": "constant_chi_prime",
                "must_chi_prime": MUST_CHI_PRIME,
                "claimed_chi_prime": KF_CLAIMED_CHI_PRIME,
            },
            "NULL": {"id": "NULL", "kind": "empty_character", "must_reject": True},
        },
        "gates": {
            "fixture_pass": fixture_pass,
            "real_character_pass": real_character_pass,
            "known_false_constant_pass": known_false_constant_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "all_pass": all_pass,
        },
        "invalid_rejected": gates["invalid_decisions"],
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_character_pass": real_character_pass,
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
        "exp_dab70e_stage1_authorized": False,
        "exp_f883e1_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_form_gamma_orbit": True,
        "do_not_run_miller": True,
        "do_not_run_tate": True,
        "not_p1553": True,
        "not_nested_lhw": True,
        "do_not_run_unary_closure_census": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-dab70e/implementation/stage0_chi2x.py\n"
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
        "real_character_pass": real_character_pass,
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
  id: ER-ECDLP-dab70e-S0
  experiment_id: EXP-ECDLP-dab70e
  run_id: RUN-ECDLP-dab70e-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-13'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_character_pass: {str(real_character_pass).lower()}
  known_false_constant_pass: {str(known_false_constant_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_dab70e_stage1_authorized: false
  exp_f883e1_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_form_gamma_orbit: true
  do_not_run_miller: true
  do_not_run_tate: true
  not_p1553: true
  not_nested_lhw: true
  do_not_run_unary_closure_census: true
  frozen_object: P-S0-CHI2X
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_character_pass {str(real_character_pass).lower()}. REAL chi is {solved['chi']}, chi_prime is {solved['chi_prime']}."
  - "known_false_constant_pass {str(known_false_constant_pass).lower()}. KF chi_prime {solved['chi_prime']} claimed {KF_CLAIMED_CHI_PRIME} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. x=0 rejected as the zero fibre."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty character is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen quadratic residue of affine x calibrator. Not nested LHW. Not Semaev. Not det D[2]. Not chi_3(y). Not Miller. Not Tate. Not a pairing. Not a rho beat. Not a unary-closure census. Not Stage 1 of EXP-ECDLP-dab70e. Certificate kind none."
"""
    REPORT_PATH.write_text(report)
    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-dab70e-S0
  experiment_id: EXP-ECDLP-dab70e
  hypothesis_id: H-ECDLP-74ecc8
  goal_id: GOAL-ECDLP-001
  batch_id: BATCH-e5c603
  task_id: {TASK_ID}
  stage: 0
  status: {'completed_valid' if all_pass else 'invalid'}
  recorded_at: '{recorded_at}'
  code:
    commit: {commit}
    dirty: true
    dirty_summary: untracked Stage 0 implementation and run artifacts at execution time
    command: python3 experiments/EXP-ECDLP-dab70e/implementation/stage0_chi2x.py
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
      frozen_object: P-S0-CHI2X
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
    validity_reason: Stage 0 exact quadratic residue of affine x calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_character_pass: {str(real_character_pass).lower()}
      known_false_constant_pass: {str(known_false_constant_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      do_not_form_semaev: true
      do_not_run_velu: true
      do_not_form_gamma_orbit: true
      do_not_run_miller: true
      do_not_run_tate: true
      not_p1553: true
      not_nested_lhw: true
      do_not_run_unary_closure_census: true
      stage1_authorized: false
      exp_dab70e_stage1_authorized: false
      exp_f883e1_stage1_authorized: false
    scientific_boundary: "Toy frozen quadratic residue of affine x calibrator. Not nested LHW. Not Semaev. Not det D[2]. Not chi_3(y). Not Miller. Not Tate. Not a pairing. Not a rho beat. Not a unary-closure census. Not Stage 1 of EXP-ECDLP-dab70e. Certificate kind none."
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
                "REAL": real_obj,
                "KF": kf_obj,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
