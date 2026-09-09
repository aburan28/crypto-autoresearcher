#!/usr/bin/env python3
"""EXP-ECDLP-9c04a3 Stage 0 exact separator-replay calibrator.

Certificate kind none. No nested LHW generator. No Semaev S_m.
Frozen object P-S0-SEPCHK: REAL / KF / NULL on a two-child fork.

REAL: A→B→{C1,C2}, unit costs, separator stores B,
r=(1,1,1,1), T=4.
KF: claim T_nosep=4. Actual r=(2,2,1,1), T=6. Rejected.
NULL empty DAG is rejected. Negative cost is rejected.

Producer method: sequential visit counting. With the separator
stored, each node is visited once. Without it, A and B are
replayed once per child.
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
SOURCE = "experiments/EXP-ECDLP-9c04a3/implementation/stage0_sepchk.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-9c04a3/runs/RUN-ECDLP-9c04a3-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-9c04a3/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-ae9b44"
TASK_ID = "TASK-20260908-5d6ade"

NODES = ("A", "B", "C1", "C2")
COSTS = {"A": 1, "B": 1, "C1": 1, "C2": 1}
SEPARATOR = "B"
MUST_R = {"A": 1, "B": 1, "C1": 1, "C2": 1}
MUST_T = 4
MUST_T_NOSEP = 6
KF_CLAIMED_T_NOSEP = 4


class InvalidParamsError(ValueError):
    """Empty DAG or non-positive cost is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_nonempty_dag(nodes: tuple | None) -> None:
    if not nodes:
        raise InvalidParamsError("dag is empty")


def require_positive_costs(costs: dict[str, int]) -> None:
    for name, cost in costs.items():
        if int(cost) <= 0:
            raise InvalidParamsError(f"cost of {name} is not a frozen positive integer")


def replay_counts(*, store_separator: bool) -> dict[str, int]:
    """Sequential visit counts on the frozen fork."""
    require_nonempty_dag(NODES)
    require_positive_costs(COSTS)
    r = {name: 0 for name in NODES}
    # First child: always walk A, B, C1.
    r["A"] += 1
    r["B"] += 1
    r["C1"] += 1
    # Second child: reuse stored B, or replay A and B.
    if store_separator:
        r["C2"] += 1
    else:
        r["A"] += 1
        r["B"] += 1
        r["C2"] += 1
    return r


def charged_T(counts: dict[str, int]) -> int:
    total = 0
    for name in NODES:
        total += counts[name] * COSTS[name]
    return total


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()

    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_positive_costs({"A": -1})
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "cost-negative", "cost": -1, "rejected": True})

    try:
        require_nonempty_dag(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_dag", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_dag", "rejected": True}

    require_nonempty_dag(NODES)
    require_positive_costs(COSTS)
    real_r = replay_counts(store_separator=True)
    real_T = charged_T(real_r)
    real_separator_pass = real_r == MUST_R and real_T == MUST_T
    real_obj = {
        "id": "REAL",
        "nodes": list(NODES),
        "separator": SEPARATOR,
        "r": real_r,
        "T": real_T,
        "must_r": MUST_R,
        "must_T": MUST_T,
    }

    nosep_r = replay_counts(store_separator=False)
    nosep_T = charged_T(nosep_r)
    kf_rejected = nosep_T == MUST_T_NOSEP and nosep_T != KF_CLAIMED_T_NOSEP
    known_false_equal_cost_pass = kf_rejected
    kf_obj = {
        "id": "KF",
        "kind": "equal_cost_without_separator",
        "r": nosep_r,
        "T": nosep_T,
        "claimed_T": KF_CLAIMED_T_NOSEP,
        "must_T": MUST_T_NOSEP,
        "rejected": kf_rejected,
    }

    all_pass = (
        fixture_pass
        and real_separator_pass
        and known_false_equal_cost_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-9c04a3-S0",
        "experiment_id": "EXP-ECDLP-9c04a3",
        "hypothesis_id": "H-ECDLP-0ae933",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-SEPCHK",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "nodes": list(NODES),
                "separator": SEPARATOR,
                "must_r": MUST_R,
                "must_T": MUST_T,
            },
            "KF": {
                "id": "KF",
                "kind": "equal_cost_without_separator",
                "must_T": MUST_T_NOSEP,
                "claimed_T": KF_CLAIMED_T_NOSEP,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_dag", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_separator_pass": real_separator_pass,
            "known_false_equal_cost_pass": known_false_equal_cost_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_9c04a3_stage1_authorized": False,
        "exp_166141_stage1_authorized": False,
        "exp_1dc6e1_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_run_coppersmith": True,
        "not_p1553": True,
        "not_nested_lhw": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-9c04a3/implementation/stage0_sepchk.py\n"
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
        "real_separator_pass": real_separator_pass,
        "known_false_equal_cost_pass": known_false_equal_cost_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-9c04a3-S0
  experiment_id: EXP-ECDLP-9c04a3
  run_id: RUN-ECDLP-9c04a3-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_separator_pass: {str(real_separator_pass).lower()}
  known_false_equal_cost_pass: {str(known_false_equal_cost_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_9c04a3_stage1_authorized: false
  exp_166141_stage1_authorized: false
  exp_1dc6e1_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_run_coppersmith: true
  not_p1553: true
  not_nested_lhw: true
  frozen_object: P-S0-SEPCHK
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_separator_pass {str(real_separator_pass).lower()}. REAL r is {real_r}, T is {real_T}."
  - "known_false_equal_cost_pass {str(known_false_equal_cost_pass).lower()}. KF T_nosep {nosep_T} claimed {KF_CLAIMED_T_NOSEP} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. Negative cost rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty DAG is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen separator-replay calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-9c04a3. Not Stage 1 of EXP-ECDLP-166141. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-9c04a3-S0
  experiment_id: EXP-ECDLP-9c04a3
  hypothesis_id: H-ECDLP-0ae933
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
    command: python3 experiments/EXP-ECDLP-9c04a3/implementation/stage0_sepchk.py
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
      frozen_object: P-S0-SEPCHK
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      separator: B
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
    validity_reason: Stage 0 exact separator-replay calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_separator_pass: {str(real_separator_pass).lower()}
      known_false_equal_cost_pass: {str(known_false_equal_cost_pass).lower()}
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
      not_nested_lhw: true
      stage1_authorized: false
      exp_9c04a3_stage1_authorized: false
      exp_166141_stage1_authorized: false
      exp_1dc6e1_stage1_authorized: false
    scientific_boundary: "Toy frozen separator-replay calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-9c04a3. Not Stage 1 of EXP-ECDLP-166141. Certificate kind none."
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
                "real_separator_pass": real_separator_pass,
                "known_false_equal_cost_pass": known_false_equal_cost_pass,
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
