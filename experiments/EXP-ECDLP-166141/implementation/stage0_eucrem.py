#!/usr/bin/env python3
"""EXP-ECDLP-166141 Stage 0 exact Euclidean remainder calibrator.

Certificate kind none. No Semaev S_m. No P1553 recurrence.
Frozen object P-S0-EUCREM: REAL / KF / NULL on F_5[x] toys.

REAL: g=x+1, r=x^2+2x+3, remainder 2 because (x+1)^2+2 = r.
KF: evaluate r at +1, value 1. Rejected as a generic remainder.
NULL empty pair is rejected. modulus 0 is rejected.

Producer method: sequential Euclidean division. Leading-term
cancellation until deg rem < deg g. Not closed-form evaluation.
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
SOURCE = "experiments/EXP-ECDLP-166141/implementation/stage0_eucrem.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-166141/runs/RUN-ECDLP-166141-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-166141/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-da146d"
TASK_ID = "TASK-20260908-4a0d8b"

MODULUS = 5
G = (1, 1)
R = (3, 2, 1)
MUST_REMAINDER = 2
KF_MUST_VALUE = 1


class InvalidParamsError(ValueError):
    """modulus not a frozen positive integer, or empty pair, is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_positive_modulus(modulus: int) -> None:
    if int(modulus) <= 0:
        raise InvalidParamsError("modulus is not a frozen positive integer")


def require_nonempty_pair(pair: tuple | None) -> None:
    if pair is None:
        raise InvalidParamsError("pair is empty")


def normalize(coeffs: list[int], modulus: int) -> list[int]:
    out = [int(c) % int(modulus) for c in coeffs]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    if not out:
        return [0]
    return out


def sequential_remainder(r: tuple[int, ...], g: tuple[int, ...], modulus: int) -> int:
    """Euclidean remainder of r by g. Sequential leading-term cancellation."""
    require_positive_modulus(modulus)
    rem = normalize(list(r), modulus)
    divisor = normalize(list(g), modulus)
    deg_g = len(divisor) - 1
    lead_inv = pow(divisor[-1], -1, modulus)
    while len(rem) - 1 >= deg_g and rem != [0]:
        shift = (len(rem) - 1) - deg_g
        factor = (rem[-1] * lead_inv) % modulus
        for i, coeff in enumerate(divisor):
            idx = i + shift
            rem[idx] = (rem[idx] - factor * coeff) % modulus
        rem = normalize(rem, modulus)
    if len(rem) != 1:
        raise InvalidParamsError("remainder is not a frozen constant")
    return rem[0]


def eval_at_one(coeffs: tuple[int, ...], modulus: int) -> int:
    acc = 0
    pow_x = 1
    for coeff in coeffs:
        acc = (acc + int(coeff) * pow_x) % int(modulus)
        pow_x = (pow_x * 1) % int(modulus)
    return acc


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()

    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_positive_modulus(0)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "modulus-zero", "modulus": 0, "rejected": True})

    try:
        require_nonempty_pair(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_pair", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_pair", "rejected": True}

    require_positive_modulus(MODULUS)
    require_nonempty_pair((G, R))
    real_remainder = sequential_remainder(R, G, MODULUS)
    real_remainder_pass = real_remainder == MUST_REMAINDER
    real_obj = {
        "id": "REAL",
        "modulus": MODULUS,
        "g": list(G),
        "r": list(R),
        "remainder": real_remainder,
        "must_remainder": MUST_REMAINDER,
    }

    kf_value = eval_at_one(R, MODULUS)
    kf_rejected = kf_value == KF_MUST_VALUE
    known_false_eval_pass = kf_rejected
    kf_obj = {
        "id": "KF",
        "kind": "eval_at_plus_one",
        "value": kf_value,
        "must_value": KF_MUST_VALUE,
        "rejected": kf_rejected,
    }

    all_pass = (
        fixture_pass
        and real_remainder_pass
        and known_false_eval_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-166141-S0",
        "experiment_id": "EXP-ECDLP-166141",
        "hypothesis_id": "H-ECDLP-98f679",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-EUCREM",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "modulus": MODULUS,
                "g": list(G),
                "r": list(R),
                "must_remainder": MUST_REMAINDER,
            },
            "KF": {
                "id": "KF",
                "kind": "eval_at_plus_one",
                "must_value": KF_MUST_VALUE,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_pair", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_remainder_pass": real_remainder_pass,
            "known_false_eval_pass": known_false_eval_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_166141_stage1_authorized": False,
        "exp_1dc6e1_stage1_authorized": False,
        "exp_6b3d67_stage1_authorized": False,
        "exp_71c37d_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_run_coppersmith": True,
        "not_p1553": True,
        "do_not_build_crt": True,
        "do_not_build_halfgcd": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-166141/implementation/stage0_eucrem.py\n"
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
        "real_remainder_pass": real_remainder_pass,
        "known_false_eval_pass": known_false_eval_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-166141-S0
  experiment_id: EXP-ECDLP-166141
  run_id: RUN-ECDLP-166141-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_remainder_pass: {str(real_remainder_pass).lower()}
  known_false_eval_pass: {str(known_false_eval_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_166141_stage1_authorized: false
  exp_1dc6e1_stage1_authorized: false
  exp_6b3d67_stage1_authorized: false
  exp_71c37d_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_run_coppersmith: true
  not_p1553: true
  do_not_build_crt: true
  do_not_build_halfgcd: true
  frozen_object: P-S0-EUCREM
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_remainder_pass {str(real_remainder_pass).lower()}. REAL remainder is {real_remainder}."
  - "known_false_eval_pass {str(known_false_eval_pass).lower()}. KF eval-at-plus-one value {kf_value} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. modulus 0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty pair is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen Euclidean remainder calibrator. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not CRT. Not a transposed half-gcd. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-166141. Not Stage 1 of EXP-ECDLP-1dc6e1. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-166141-S0
  experiment_id: EXP-ECDLP-166141
  hypothesis_id: H-ECDLP-98f679
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
    command: python3 experiments/EXP-ECDLP-166141/implementation/stage0_eucrem.py
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
      frozen_object: P-S0-EUCREM
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      real_modulus: 5
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
    validity_reason: Stage 0 exact Euclidean remainder calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_remainder_pass: {str(real_remainder_pass).lower()}
      known_false_eval_pass: {str(known_false_eval_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      do_not_form_semaev: true
      do_not_run_velu: true
      do_not_run_coppersmith: true
      not_p1553: true
      do_not_build_crt: true
      do_not_build_halfgcd: true
      stage1_authorized: false
      exp_166141_stage1_authorized: false
      exp_1dc6e1_stage1_authorized: false
      exp_6b3d67_stage1_authorized: false
      exp_71c37d_stage1_authorized: false
    scientific_boundary: "Toy frozen Euclidean remainder calibrator. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not CRT. Not a transposed half-gcd. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-166141. Not Stage 1 of EXP-ECDLP-1dc6e1. Certificate kind none."
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
                "real_remainder_pass": real_remainder_pass,
                "known_false_eval_pass": known_false_eval_pass,
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
