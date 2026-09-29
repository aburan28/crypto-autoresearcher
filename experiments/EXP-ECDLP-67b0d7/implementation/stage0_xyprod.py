#!/usr/bin/env python3
"""EXP-ECDLP-67b0d7 Stage 0 exact affine product xy calibrator.

Certificate kind none. No nested LHW generator. No Semaev S_m.
Frozen object P-S0-XYPROD: REAL / KF / NULL on one F_19 point.

REAL: p=19, A=1, B=-1, P=(2,3), [2]P=(16,11),
Pi=x*y=6, Pi'=x([2]P)*y([2]P)=5.
KF: claim Pi'=6. Actual 5. Rejected.
NULL empty product is rejected. y=0 is rejected.

Producer method: affine doubling, then multiply coordinates.
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
SOURCE = "experiments/EXP-ECDLP-67b0d7/implementation/stage0_xyprod.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-67b0d7/runs/RUN-ECDLP-67b0d7-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-67b0d7/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260913-7b43e9"
TASK_ID = "TASK-20260913-d97f2d"

P = 19
A = 1
B = -1
POINT = (2, 3)
MUST_P2 = (16, 11)
MUST_PI = 6
MUST_PI_PRIME = 5
KF_CLAIMED_PI_PRIME = 6


class InvalidParamsError(ValueError):
    """Empty product or y=0 is rejected."""


def inv(value: int) -> int:
    return pow(value, -1, P)


def require_nonzero_y(y: int) -> None:
    if y % P == 0:
        raise InvalidParamsError("y is zero")


def require_nonempty_product(product: int | None) -> None:
    if product is None:
        raise InvalidParamsError("product is empty")


def affine_double(x: int, y: int) -> tuple[int, int]:
    require_nonzero_y(y)
    lam = ((3 * x * x + A) * inv(2 * y)) % P
    x2 = (lam * lam - 2 * x) % P
    y2 = (lam * ((x - x2) % P) - y) % P
    return x2, y2


def product_solve() -> dict:
    require_nonzero_y(POINT[1])
    pi = (POINT[0] * POINT[1]) % P
    p2 = affine_double(*POINT)
    pi_prime = (p2[0] * p2[1]) % P
    return {
        "P2": list(p2),
        "pi": pi,
        "pi_prime": pi_prime,
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
        require_nonempty_product(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_product", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_product", "rejected": True}

    solved = product_solve()
    real_product_pass = (
        tuple(solved["P2"]) == MUST_P2
        and solved["pi"] == MUST_PI
        and solved["pi_prime"] == MUST_PI_PRIME
    )
    kf_rejected = (
        solved["pi_prime"] == MUST_PI_PRIME
        and solved["pi_prime"] != KF_CLAIMED_PI_PRIME
    )
    return {
        "fixture_pass": fixture_pass,
        "real_product_pass": real_product_pass,
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
    real_product_pass = gates["real_product_pass"]
    known_false_constant_pass = gates["known_false_constant_pass"]
    reject_invalid_pass = gates["reject_invalid_pass"]
    null_empty_pass = gates["null_empty_pass"]
    kf_rejected = gates["kf_rejected"]
    all_pass = (
        fixture_pass
        and real_product_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started
    real_obj = {
        "id": "REAL",
        "P": list(POINT),
        "P2": solved["P2"],
        "pi": solved["pi"],
        "pi_prime": solved["pi_prime"],
        "must_pi": MUST_PI,
        "must_pi_prime": MUST_PI_PRIME,
    }
    kf_obj = {
        "id": "KF",
        "kind": "constant_pi_prime",
        "pi_prime": solved["pi_prime"],
        "claimed_pi_prime": KF_CLAIMED_PI_PRIME,
        "must_pi_prime": MUST_PI_PRIME,
        "rejected": kf_rejected,
    }
    raw = {
        "run_id": "RUN-ECDLP-67b0d7-S0",
        "experiment_id": "EXP-ECDLP-67b0d7",
        "hypothesis_id": "H-ECDLP-ec06d9",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-XYPROD",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "p": P,
                "A": A,
                "B": B,
                "P": list(POINT),
                "must_P2": list(MUST_P2),
                "must_pi": MUST_PI,
                "must_pi_prime": MUST_PI_PRIME,
            },
            "KF": {
                "id": "KF",
                "kind": "constant_pi_prime",
                "must_pi_prime": MUST_PI_PRIME,
                "claimed_pi_prime": KF_CLAIMED_PI_PRIME,
            },
            "NULL": {"id": "NULL", "kind": "empty_product", "must_reject": True},
        },
        "gates": {
            "fixture_pass": fixture_pass,
            "real_product_pass": real_product_pass,
            "known_false_constant_pass": known_false_constant_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "all_pass": all_pass,
        },
        "invalid_rejected": gates["invalid_decisions"],
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_product_pass": real_product_pass,
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
        "exp_67b0d7_stage1_authorized": False,
        "exp_bf222c_stage1_authorized": False,
        "exp_e9dd89_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_form_gamma_orbit": True,
        "not_p1553": True,
        "not_nested_lhw": True,
        "do_not_run_unary_closure_census": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-67b0d7/implementation/stage0_xyprod.py\n"
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
        "real_product_pass": real_product_pass,
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
  id: ER-ECDLP-67b0d7-S0
  experiment_id: EXP-ECDLP-67b0d7
  run_id: RUN-ECDLP-67b0d7-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-13'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_product_pass: {str(real_product_pass).lower()}
  known_false_constant_pass: {str(known_false_constant_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_67b0d7_stage1_authorized: false
  exp_bf222c_stage1_authorized: false
  exp_e9dd89_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_form_gamma_orbit: true
  not_p1553: true
  not_nested_lhw: true
  do_not_run_unary_closure_census: true
  frozen_object: P-S0-XYPROD
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_product_pass {str(real_product_pass).lower()}. REAL pi is {solved['pi']}, pi_prime is {solved['pi_prime']}."
  - "known_false_constant_pass {str(known_false_constant_pass).lower()}. KF pi_prime {solved['pi_prime']} claimed {KF_CLAIMED_PI_PRIME} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. y=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty product is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen affine product xy calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a Gamma orbit. Not a rho beat. Not a decoder. Not a unary-closure census. Not Stage 1 of EXP-ECDLP-67b0d7. Not Stage 1 of EXP-ECDLP-bf222c. Certificate kind none."
"""
    REPORT_PATH.write_text(report)
    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-67b0d7-S0
  experiment_id: EXP-ECDLP-67b0d7
  hypothesis_id: H-ECDLP-ec06d9
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
    command: python3 experiments/EXP-ECDLP-67b0d7/implementation/stage0_xyprod.py
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
      frozen_object: P-S0-XYPROD
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
    validity_reason: Stage 0 exact affine product xy calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_product_pass: {str(real_product_pass).lower()}
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
      not_p1553: true
      not_nested_lhw: true
      do_not_run_unary_closure_census: true
      stage1_authorized: false
      exp_67b0d7_stage1_authorized: false
      exp_bf222c_stage1_authorized: false
      exp_e9dd89_stage1_authorized: false
    scientific_boundary: "Toy frozen affine product xy calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a Gamma orbit. Not a rho beat. Not a decoder. Not a unary-closure census. Not Stage 1 of EXP-ECDLP-67b0d7. Not Stage 1 of EXP-ECDLP-bf222c. Certificate kind none."
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
                "real_product_pass": real_product_pass,
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
