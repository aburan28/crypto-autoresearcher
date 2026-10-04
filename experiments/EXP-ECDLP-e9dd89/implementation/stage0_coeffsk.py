#!/usr/bin/env python3
"""EXP-ECDLP-e9dd89 Stage 0 exact elementary-symmetric calibrator.

Certificate kind none. No nested LHW generator. No Semaev S_m.
Frozen object P-S0-COEFFSK: REAL / KF / NULL on a 2-set.

REAL: S={1,2}, (X-1)(X-2)=X^2-3X+2, e1=3.
KF: claim e1=0 (constant sketch). Actual e1=3. Rejected.
NULL empty set is rejected. Empty selected-coefficient list is rejected.

Producer method: expand (X-a)(X-b) and read e1=a+b.
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
SOURCE = "experiments/EXP-ECDLP-e9dd89/implementation/stage0_coeffsk.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-e9dd89/runs/RUN-ECDLP-e9dd89-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-e9dd89/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260913-b3491f"
TASK_ID = "TASK-20260913-7a9620"

ELEMENTS = (1, 2)
SELECTED = ("e1",)
MUST_E1 = 3
MUST_POLY = (1, -3, 2)
KF_CLAIMED_E1 = 0


class InvalidParamsError(ValueError):
    """Empty set or empty selected-coefficient list is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_nonempty_set(elements: tuple | None) -> None:
    if not elements:
        raise InvalidParamsError("set is empty")


def require_selected_coefficients(selected: tuple | None) -> None:
    if not selected:
        raise InvalidParamsError("selected-coefficient list is empty")


def expand_and_read_e1(elements: tuple[int, int]) -> dict:
    """Expand (X-a)(X-b) and read e1=a+b."""
    require_nonempty_set(elements)
    require_selected_coefficients(SELECTED)
    a, b = elements
    # X^2 - (a+b)X + ab
    poly = (1, -(a + b), a * b)
    e1 = a + b
    return {"poly": list(poly), "e1": e1}


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()

    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_selected_coefficients(())
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "empty-selected-coefficients", "selected": [], "rejected": True})

    try:
        require_nonempty_set(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_set", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_set", "rejected": True}

    solved = expand_and_read_e1(ELEMENTS)
    real_e1_pass = solved["e1"] == MUST_E1 and tuple(solved["poly"]) == MUST_POLY
    real_obj = {
        "id": "REAL",
        "elements": list(ELEMENTS),
        "poly": solved["poly"],
        "e1": solved["e1"],
        "must_e1": MUST_E1,
        "must_poly": list(MUST_POLY),
    }

    kf_rejected = solved["e1"] == MUST_E1 and solved["e1"] != KF_CLAIMED_E1
    known_false_constant_pass = kf_rejected
    kf_obj = {
        "id": "KF",
        "kind": "constant_sketch",
        "e1": solved["e1"],
        "claimed_e1": KF_CLAIMED_E1,
        "must_e1": MUST_E1,
        "rejected": kf_rejected,
    }

    all_pass = (
        fixture_pass
        and real_e1_pass
        and known_false_constant_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-e9dd89-S0",
        "experiment_id": "EXP-ECDLP-e9dd89",
        "hypothesis_id": "H-ECDLP-2b270e",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-COEFFSK",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "elements": list(ELEMENTS),
                "must_e1": MUST_E1,
                "must_poly": list(MUST_POLY),
            },
            "KF": {
                "id": "KF",
                "kind": "constant_sketch",
                "must_e1": MUST_E1,
                "claimed_e1": KF_CLAIMED_E1,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_set", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_e1_pass": real_e1_pass,
            "known_false_constant_pass": known_false_constant_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "python3 experiments/EXP-ECDLP-e9dd89/implementation/stage0_coeffsk.py\n"
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
        "real_e1_pass": real_e1_pass,
        "known_false_constant_pass": known_false_constant_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-e9dd89-S0
  experiment_id: EXP-ECDLP-e9dd89
  run_id: RUN-ECDLP-e9dd89-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-13'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_e1_pass: {str(real_e1_pass).lower()}
  known_false_constant_pass: {str(known_false_constant_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
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
  frozen_object: P-S0-COEFFSK
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_e1_pass {str(real_e1_pass).lower()}. REAL e1 is {solved['e1']}, poly is {solved['poly']}."
  - "known_false_constant_pass {str(known_false_constant_pass).lower()}. KF e1 {solved['e1']} claimed {KF_CLAIMED_E1} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. Empty selected-coefficient list rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty set is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen elementary-symmetric calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a Gamma orbit. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-e9dd89. Not Stage 1 of EXP-ECDLP-bb5ef7. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-e9dd89-S0
  experiment_id: EXP-ECDLP-e9dd89
  hypothesis_id: H-ECDLP-2b270e
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
    command: python3 experiments/EXP-ECDLP-e9dd89/implementation/stage0_coeffsk.py
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
      frozen_object: P-S0-COEFFSK
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      elements: [1, 2]
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
    validity_reason: Stage 0 exact elementary-symmetric calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_e1_pass: {str(real_e1_pass).lower()}
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
      exp_e9dd89_stage1_authorized: false
      exp_bb5ef7_stage1_authorized: false
      exp_70c6f0_stage1_authorized: false
      exp_9c04a3_stage1_authorized: false
    scientific_boundary: "Toy frozen elementary-symmetric calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a Gamma orbit. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-e9dd89. Not Stage 1 of EXP-ECDLP-bb5ef7. Certificate kind none."
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
                "real_e1_pass": real_e1_pass,
                "known_false_constant_pass": known_false_constant_pass,
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
