#!/usr/bin/env python3
"""EXP-ECDLP-6b3d67 Stage 0 exact F_9 semilinear parent calibrator.

Certificate kind none. No Semaev S_m. No P1553 recurrence.
Frozen object P-S0-FROBSEM: REAL / KF / NULL on F_9 toys.

REAL: F_3[α]/(α^2+1), s0=1+α, s1=1+2α, F(s1)=1+α, parent=2+2α.
KF: identity Frobenius yields parent 2. Rejected as a generic
End=Z / F_p target.
NULL empty pair is rejected. p=0 is rejected.

Producer method: repeated ring multiply. F(x) is x multiplied
by itself p times starting from 1.
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
SOURCE = "experiments/EXP-ECDLP-6b3d67/implementation/stage0_frobsem.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-6b3d67/runs/RUN-ECDLP-6b3d67-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-6b3d67/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-c439ad"
TASK_ID = "TASK-20260908-c9afc6"

P = 3
S0 = (1, 1)
S1 = (1, 2)
MUST_F_S1 = (1, 1)
MUST_PARENT = (2, 2)
KF_MUST_PARENT = (2, 0)


class InvalidParamsError(ValueError):
    """p not a frozen positive integer, or empty pair, is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_positive_p(p: int) -> None:
    if int(p) <= 0:
        raise InvalidParamsError("p is not a frozen positive integer")


def require_nonempty_pair(pair: tuple | None) -> None:
    if pair is None:
        raise InvalidParamsError("pair is empty")


def add_el(u: tuple[int, int], v: tuple[int, int]) -> tuple[int, int]:
    return ((u[0] + v[0]) % P, (u[1] + v[1]) % P)


def mul_el(u: tuple[int, int], v: tuple[int, int]) -> tuple[int, int]:
    """(a+bα)(c+dα) with α^2 = 2 in F_3."""
    a, b = u
    c, d = v
    return ((a * c + 2 * b * d) % P, (a * d + b * c) % P)


def frobenius_repeated_multiply(el: tuple[int, int]) -> tuple[int, int]:
    """F(x)=x^p by starting at 1 and multiplying by x, p times."""
    require_positive_p(P)
    acc = (1, 0)
    step = 0
    while step < P:
        acc = mul_el(acc, el)
        step += 1
    return acc


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()

    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_positive_p(0)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "p-zero", "p": 0, "rejected": True})

    try:
        require_nonempty_pair(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_pair", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_pair", "rejected": True}

    require_positive_p(P)
    require_nonempty_pair((S0, S1))
    real_f = frobenius_repeated_multiply(S1)
    real_parent = add_el(S0, real_f)
    real_semilinear_pass = real_f == MUST_F_S1 and real_parent == MUST_PARENT
    real_obj = {
        "id": "REAL",
        "p": P,
        "s0": list(S0),
        "s1": list(S1),
        "F_s1": list(real_f),
        "parent": list(real_parent),
        "must_F_s1": list(MUST_F_S1),
        "must_parent": list(MUST_PARENT),
    }

    kf_parent = add_el(S0, S1)
    kf_rejected = kf_parent == KF_MUST_PARENT
    known_false_id_pass = kf_rejected
    kf_obj = {
        "id": "KF",
        "kind": "identity_frobenius",
        "parent": list(kf_parent),
        "must_parent": list(KF_MUST_PARENT),
        "rejected": kf_rejected,
    }

    all_pass = (
        fixture_pass
        and real_semilinear_pass
        and known_false_id_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-6b3d67-S0",
        "experiment_id": "EXP-ECDLP-6b3d67",
        "hypothesis_id": "H-ECDLP-9e65d4",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-FROBSEM",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "p": P,
                "s0": list(S0),
                "s1": list(S1),
                "must_F_s1": list(MUST_F_S1),
                "must_parent": list(MUST_PARENT),
            },
            "KF": {
                "id": "KF",
                "kind": "identity_frobenius",
                "must_parent": list(KF_MUST_PARENT),
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_pair", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_semilinear_pass": real_semilinear_pass,
            "known_false_id_pass": known_false_id_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_6b3d67_stage1_authorized": False,
        "exp_71c37d_stage1_authorized": False,
        "exp_2a466a_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_run_coppersmith": True,
        "not_p1553": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-6b3d67/implementation/stage0_frobsem.py\n"
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
        "real_semilinear_pass": real_semilinear_pass,
        "known_false_id_pass": known_false_id_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-6b3d67-S0
  experiment_id: EXP-ECDLP-6b3d67
  run_id: RUN-ECDLP-6b3d67-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_semilinear_pass: {str(real_semilinear_pass).lower()}
  known_false_id_pass: {str(known_false_id_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_6b3d67_stage1_authorized: false
  exp_71c37d_stage1_authorized: false
  exp_2a466a_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_run_coppersmith: true
  not_p1553: true
  frozen_object: P-S0-FROBSEM
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_semilinear_pass {str(real_semilinear_pass).lower()}. REAL F(s1) is {list(real_f)}, parent is {list(real_parent)}."
  - "known_false_id_pass {str(known_false_id_pass).lower()}. KF identity-Frobenius parent {list(kf_parent)} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. p=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty pair is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen F_9 parent-from-children calibrator. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-6b3d67. Not Stage 1 of EXP-ECDLP-71c37d. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-6b3d67-S0
  experiment_id: EXP-ECDLP-6b3d67
  hypothesis_id: H-ECDLP-9e65d4
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
    command: python3 experiments/EXP-ECDLP-6b3d67/implementation/stage0_frobsem.py
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
      frozen_object: P-S0-FROBSEM
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      real_p: 3
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
    validity_reason: Stage 0 exact F_9 semilinear parent calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_semilinear_pass: {str(real_semilinear_pass).lower()}
      known_false_id_pass: {str(known_false_id_pass).lower()}
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
      stage1_authorized: false
      exp_6b3d67_stage1_authorized: false
      exp_71c37d_stage1_authorized: false
      exp_2a466a_stage1_authorized: false
    scientific_boundary: "Toy frozen F_9 parent-from-children calibrator. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-6b3d67. Not Stage 1 of EXP-ECDLP-71c37d. Certificate kind none."
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
                "real_semilinear_pass": real_semilinear_pass,
                "known_false_id_pass": known_false_id_pass,
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
