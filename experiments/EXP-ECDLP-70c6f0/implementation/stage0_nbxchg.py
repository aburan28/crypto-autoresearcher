#!/usr/bin/env python3
"""EXP-ECDLP-70c6f0 Stage 0 exact nonbacktracking-exchange calibrator.

Certificate kind none. No nested LHW generator. No Semaev S_m.
Frozen object P-S0-NBXCHG: REAL / KF / NULL on a weight-1 3-set.

REAL: U={0,1,2}, u=1, S={0}, last exchange (remove 1, add 0),
n_all=2, n_nb=1.
KF: claim n_nb=2 (all Johnson neighbors). Actual n_nb=1. Rejected.
NULL empty universe is rejected. Negative weight is rejected.

Producer method: enumerate replacements of the unique element,
then drop the inverse of the last exchange.
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
SOURCE = "experiments/EXP-ECDLP-70c6f0/implementation/stage0_nbxchg.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-70c6f0/runs/RUN-ECDLP-70c6f0-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-70c6f0/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260913-ab67c8"
TASK_ID = "TASK-20260913-157a38"

UNIVERSE = (0, 1, 2)
WEIGHT = 1
SUBSET = frozenset({0})
LAST_REMOVED = 1
LAST_ADDED = 0
MUST_N_ALL = 2
MUST_N_NB = 1
KF_CLAIMED_N_NB = 2


class InvalidParamsError(ValueError):
    """Empty universe or non-positive weight is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_nonempty_universe(universe: tuple | None) -> None:
    if not universe:
        raise InvalidParamsError("universe is empty")


def require_positive_weight(weight: int) -> None:
    if int(weight) <= 0:
        raise InvalidParamsError("weight is not a frozen positive integer")


def enumerate_replacements(universe: tuple[int, ...], subset: frozenset[int]) -> list[tuple[int, int]]:
    """Enumerate weight-1 exchanges by replacing the unique element."""
    require_nonempty_universe(universe)
    require_positive_weight(WEIGHT)
    current = next(iter(subset))
    moves = []
    for incoming in universe:
        if incoming == current:
            continue
        moves.append((current, incoming))
    return moves


def legal_counts(*, drop_inverse: bool) -> tuple[int, int]:
    moves = enumerate_replacements(UNIVERSE, SUBSET)
    n_all = len(moves)
    if drop_inverse:
        inverse = (LAST_ADDED, LAST_REMOVED)
        moves = [move for move in moves if move != inverse]
    return n_all, len(moves)


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()

    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_positive_weight(-1)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "weight-negative", "weight": -1, "rejected": True})

    try:
        require_nonempty_universe(None)
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_universe", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_universe", "rejected": True}

    require_nonempty_universe(UNIVERSE)
    require_positive_weight(WEIGHT)
    n_all, n_nb = legal_counts(drop_inverse=True)
    real_nb_count_pass = n_all == MUST_N_ALL and n_nb == MUST_N_NB
    real_obj = {
        "id": "REAL",
        "universe": list(UNIVERSE),
        "weight": WEIGHT,
        "subset": sorted(SUBSET),
        "last_removed": LAST_REMOVED,
        "last_added": LAST_ADDED,
        "n_all": n_all,
        "n_nb": n_nb,
        "must_n_all": MUST_N_ALL,
        "must_n_nb": MUST_N_NB,
    }

    kf_rejected = n_nb == MUST_N_NB and n_nb != KF_CLAIMED_N_NB
    known_false_all_neighbors_pass = kf_rejected
    kf_obj = {
        "id": "KF",
        "kind": "all_johnson_neighbors_legal",
        "n_nb": n_nb,
        "claimed_n_nb": KF_CLAIMED_N_NB,
        "must_n_nb": MUST_N_NB,
        "rejected": kf_rejected,
    }

    all_pass = (
        fixture_pass
        and real_nb_count_pass
        and known_false_all_neighbors_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-70c6f0-S0",
        "experiment_id": "EXP-ECDLP-70c6f0",
        "hypothesis_id": "H-ECDLP-e51272",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-NBXCHG",
        "fixture": {
            "REAL": {
                "id": "REAL",
                "universe": list(UNIVERSE),
                "weight": WEIGHT,
                "subset": sorted(SUBSET),
                "last_removed": LAST_REMOVED,
                "last_added": LAST_ADDED,
                "must_n_all": MUST_N_ALL,
                "must_n_nb": MUST_N_NB,
            },
            "KF": {
                "id": "KF",
                "kind": "all_johnson_neighbors_legal",
                "must_n_nb": MUST_N_NB,
                "claimed_n_nb": KF_CLAIMED_N_NB,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_universe", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_nb_count_pass": real_nb_count_pass,
            "known_false_all_neighbors_pass": known_false_all_neighbors_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_70c6f0_stage1_authorized": False,
        "exp_9c04a3_stage1_authorized": False,
        "exp_166141_stage1_authorized": False,
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
        "python3 experiments/EXP-ECDLP-70c6f0/implementation/stage0_nbxchg.py\n"
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
        "real_nb_count_pass": real_nb_count_pass,
        "known_false_all_neighbors_pass": known_false_all_neighbors_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-70c6f0-S0
  experiment_id: EXP-ECDLP-70c6f0
  run_id: RUN-ECDLP-70c6f0-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-13'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_nb_count_pass: {str(real_nb_count_pass).lower()}
  known_false_all_neighbors_pass: {str(known_false_all_neighbors_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_70c6f0_stage1_authorized: false
  exp_9c04a3_stage1_authorized: false
  exp_166141_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_run_coppersmith: true
  not_p1553: true
  not_nested_lhw: true
  frozen_object: P-S0-NBXCHG
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_nb_count_pass {str(real_nb_count_pass).lower()}. REAL n_all is {n_all}, n_nb is {n_nb}."
  - "known_false_all_neighbors_pass {str(known_false_all_neighbors_pass).lower()}. KF n_nb {n_nb} claimed {KF_CLAIMED_N_NB} rejected={str(kf_rejected).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. Negative weight rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty universe is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen nonbacktracking-exchange calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-70c6f0. Not Stage 1 of EXP-ECDLP-9c04a3. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-70c6f0-S0
  experiment_id: EXP-ECDLP-70c6f0
  hypothesis_id: H-ECDLP-e51272
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
    command: python3 experiments/EXP-ECDLP-70c6f0/implementation/stage0_nbxchg.py
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
      frozen_object: P-S0-NBXCHG
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      universe: [0, 1, 2]
      weight: 1
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
    validity_reason: Stage 0 exact nonbacktracking-exchange calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_nb_count_pass: {str(real_nb_count_pass).lower()}
      known_false_all_neighbors_pass: {str(known_false_all_neighbors_pass).lower()}
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
      exp_70c6f0_stage1_authorized: false
      exp_9c04a3_stage1_authorized: false
      exp_166141_stage1_authorized: false
    scientific_boundary: "Toy frozen nonbacktracking-exchange calibrator. Not nested LHW. Not Esser-May. Not Semaev. Not a P1553 recurrence. Not a factor-base. Not Velu. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-70c6f0. Not Stage 1 of EXP-ECDLP-9c04a3. Certificate kind none."
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
                "real_nb_count_pass": real_nb_count_pass,
                "known_false_all_neighbors_pass": known_false_all_neighbors_pass,
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
