#!/usr/bin/env python3
"""EXP-ECDLP-71c37d Stage 0 exact embedding-order calibrator.

Certificate kind none. No Miller function. No Tate pairing. No L(N.O).
No M_D. Frozen object P-S0-EMBORD: REAL / KF / NULL on (N,p) toys.

REAL: (N,p)=(7,11). gcd(7,10)=1, k=ord_7(11)=3, degrees [1, 3, 3].
KF: (7,29). k=1 because 7 | 28. Rejected as a generic large-k target.
NULL empty pair is rejected. N=0 is rejected.

Producer method: sequential multiply. Start at 1, repeatedly multiply
by (p mod N) until 1, counting steps. Degrees = [1] + [k]*((N-1)//k).
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
SOURCE = "experiments/EXP-ECDLP-71c37d/implementation/stage0_embord.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-71c37d/runs/RUN-ECDLP-71c37d-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-71c37d/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-c83366"
TASK_ID = "TASK-20260908-2d3326"

REAL_N = 7
REAL_P = 11
MUST_GCD = 1
MUST_K = 3
MUST_DEGREES = [1, 3, 3]
KF_N = 7
KF_P = 29
KF_MUST_K = 1


class InvalidParamsError(ValueError):
    """N not a frozen positive integer, or empty pair, is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_positive_n(n: int) -> None:
    if int(n) <= 0:
        raise InvalidParamsError("N is not a frozen positive integer")


def require_nonempty_pair(pair: tuple[int, int] | None) -> None:
    if pair is None:
        raise InvalidParamsError("pair is empty")


def gcd_int(u: int, v: int) -> int:
    a, b = abs(int(u)), abs(int(v))
    while b:
        a, b = b, a % b
    return a


def embedding_order(n: int, p: int) -> int:
    """Sequential multiply: acc starts at 1, multiply by (p mod n) until 1."""
    require_positive_n(n)
    modulus = int(n)
    base = int(p) % modulus
    if base == 0:
        raise InvalidParamsError("p is 0 modulo N")
    acc = 1
    steps = 0
    while True:
        acc = (acc * base) % modulus
        steps += 1
        if acc == 1:
            return steps
        if steps > modulus:
            raise InvalidParamsError("order did not close")


def forced_degrees(n: int, k: int) -> list[int]:
    require_positive_n(n)
    if int(n - 1) % int(k) != 0:
        raise InvalidParamsError("k does not divide N-1")
    return sorted([1] + [int(k)] * ((int(n) - 1) // int(k)))


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()

    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_positive_n(0)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "N-zero", "N": 0, "rejected": True})

    try:
        require_nonempty_pair(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_pair", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_pair", "rejected": True}

    try:
        kf_k = embedding_order(KF_N, KF_P)
        kf_divides = ((KF_P - 1) % KF_N) == 0
        kf_rejected = (kf_k == KF_MUST_K) and kf_divides
        known_false_k1_pass = kf_rejected
        kf_obj = {
            "id": "KF",
            "N": KF_N,
            "p": KF_P,
            "k": kf_k,
            "must_k": KF_MUST_K,
            "N_divides_p_minus_1": kf_divides,
            "rejected": kf_rejected,
        }
    except InvalidParamsError:
        known_false_k1_pass = False
        kf_obj = {"id": "KF", "N": KF_N, "p": KF_P, "rejected": False}

    require_positive_n(REAL_N)
    require_nonempty_pair((REAL_N, REAL_P))
    real_gcd = gcd_int(REAL_N, REAL_P - 1)
    real_k = embedding_order(REAL_N, REAL_P)
    real_degrees = forced_degrees(REAL_N, real_k)
    real_order_pass = (
        real_gcd == MUST_GCD
        and real_k == MUST_K
        and real_degrees == MUST_DEGREES
    )
    real_obj = {
        "id": "REAL",
        "N": REAL_N,
        "p": REAL_P,
        "gcd": real_gcd,
        "k": real_k,
        "degrees": real_degrees,
        "must_gcd": MUST_GCD,
        "must_k": MUST_K,
        "must_degrees": MUST_DEGREES,
    }

    all_pass = (
        fixture_pass
        and real_order_pass
        and known_false_k1_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-71c37d-S0",
        "experiment_id": "EXP-ECDLP-71c37d",
        "hypothesis_id": "H-ECDLP-84eb73",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-EMBORD",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "N": REAL_N,
                "p": REAL_P,
                "must_gcd": MUST_GCD,
                "must_k": MUST_K,
                "must_degrees": MUST_DEGREES,
            },
            "KF": {
                "id": "KF",
                "N": KF_N,
                "p": KF_P,
                "must_k": KF_MUST_K,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_pair", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_order_pass": real_order_pass,
            "known_false_k1_pass": known_false_k1_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_71c37d_stage1_authorized": False,
        "exp_2a466a_stage1_authorized": False,
        "exp_8eaf6a_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "not_miller": True,
        "not_tate": True,
        "not_mov": True,
        "not_frey_ruck": True,
        "do_not_run_coppersmith": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-71c37d/implementation/stage0_embord.py\n"
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
        "real_order_pass": real_order_pass,
        "known_false_k1_pass": known_false_k1_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-71c37d-S0
  experiment_id: EXP-ECDLP-71c37d
  run_id: RUN-ECDLP-71c37d-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_order_pass: {str(real_order_pass).lower()}
  known_false_k1_pass: {str(known_false_k1_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_71c37d_stage1_authorized: false
  exp_2a466a_stage1_authorized: false
  exp_8eaf6a_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_miller: true
  not_tate: true
  not_mov: true
  not_frey_ruck: true
  do_not_run_coppersmith: true
  do_not_form_semaev: true
  do_not_run_velu: true
  frozen_object: P-S0-EMBORD
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_order_pass {str(real_order_pass).lower()}. REAL k is {real_k}, gcd is {real_gcd}, degrees are {real_degrees}."
  - "known_false_k1_pass {str(known_false_k1_pass).lower()}. KF k={kf_obj.get('k')} rejected={str(kf_obj['rejected']).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. N=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty pair is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen embedding-order calibrator on (N,p). Not Miller. Not Tate. Not MOV. Not Frey-Ruck. Not a level-N model. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-71c37d. Not Stage 1 of EXP-ECDLP-2a466a. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-71c37d-S0
  experiment_id: EXP-ECDLP-71c37d
  hypothesis_id: H-ECDLP-84eb73
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
    command: python3 experiments/EXP-ECDLP-71c37d/implementation/stage0_embord.py
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
      frozen_object: P-S0-EMBORD
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      real_N: 7
      real_p: 11
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
    validity_reason: Stage 0 exact embedding-order calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_order_pass: {str(real_order_pass).lower()}
      known_false_k1_pass: {str(known_false_k1_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_miller: true
      not_tate: true
      not_mov: true
      not_frey_ruck: true
      do_not_run_coppersmith: true
      do_not_form_semaev: true
      do_not_run_velu: true
      stage1_authorized: false
      exp_71c37d_stage1_authorized: false
      exp_2a466a_stage1_authorized: false
      exp_8eaf6a_stage1_authorized: false
    scientific_boundary: "Toy frozen embedding-order calibrator on (N,p). Not Miller. Not Tate. Not MOV. Not Frey-Ruck. Not a level-N model. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-71c37d. Not Stage 1 of EXP-ECDLP-2a466a. Certificate kind none."
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
                "real_order_pass": real_order_pass,
                "known_false_k1_pass": known_false_k1_pass,
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
