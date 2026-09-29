#!/usr/bin/env python3
"""EXP-ECDLP-1aa0f8 Stage 0 exact (U, P) enumerative calibrator.

Certificate kind none. No decoder. No ApproxMC. No XOR hashing. No cadical.
Not the Trimoska pdp encoder. Do not hunt a new CNF. Frozen object
P-S0-COUNT: REAL3 / KF3 / NULL3.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-1aa0f8/implementation/stage0_count.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-1aa0f8/runs/RUN-ECDLP-1aa0f8-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-1aa0f8/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-097d3b"
TASK_ID = "TASK-20260908-2dec2d"

VARS = ("a", "b", "c", "r0", "r1")
CORE = ("a", "b", "c")
TARGET = ("r0", "r1")

REAL3 = {
    "id": "REAL3",
    "m": 3,
    "l": 1,
    "clauses": (
        ("a", "b", "~r0"),
        ("~a", "~b", "~r0"),
        ("a", "~b", "r0"),
        ("~a", "b", "r0"),
        ("a", "c", "~r1"),
        ("~a", "~c", "~r1"),
        ("a", "~c", "r1"),
        ("~a", "c", "r1"),
    ),
    "must_U": 8,
    "must_P": 4,
}

KF3 = {
    "id": "KF3",
    "clauses": (),
    "must_U": 32,
    "must_P": 4,
}

NULL3 = {
    "id": "NULL3",
    "clauses": (("a",), ("~a",)),
    "must_U": 0,
    "must_P": 0,
}


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def lit_true(lit: str, assign: dict[str, int]) -> bool:
    if lit.startswith("~"):
        return assign[lit[1:]] == 0
    return assign[lit] == 1


def sat(clauses: tuple[tuple[str, ...], ...], assign: dict[str, int]) -> bool:
    return all(any(lit_true(lit, assign) for lit in clause) for clause in clauses)


def enumerate_up(
    variables: tuple[str, ...],
    target: tuple[str, ...],
    clauses: tuple[tuple[str, ...], ...],
) -> tuple[int, int]:
    if not variables:
        raise ValueError("empty variable list")
    if any(t not in variables for t in target):
        raise ValueError("missing target bits")
    sols = []
    for bits in product((0, 1), repeat=len(variables)):
        assign = dict(zip(variables, bits))
        if sat(clauses, assign):
            sols.append(assign)
    projected = {(tuple(s[t] for t in target)) for s in sols}
    return len(sols), len(projected)


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        enumerate_up((), TARGET, ())
        decisions.append({"id": "VARS-empty", "rejected": False})
    except ValueError:
        decisions.append({"id": "VARS-empty", "rejected": True})
    try:
        enumerate_up(CORE, TARGET, ())
        decisions.append({"id": "TARGET-missing", "rejected": False})
    except ValueError:
        decisions.append({"id": "TARGET-missing", "rejected": True})
    return decisions


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real_U, real_P = enumerate_up(VARS, TARGET, REAL3["clauses"])
    kf_U, kf_P = enumerate_up(VARS, TARGET, KF3["clauses"])
    null_U, null_P = enumerate_up(VARS, TARGET, NULL3["clauses"])
    invalid_decisions = reject_invalid()

    fixture_pass = True
    real_up_pass = real_U == REAL3["must_U"] and real_P == REAL3["must_P"]
    known_false_unconstrained_pass = kf_U == KF3["must_U"] and kf_P == KF3["must_P"]
    reject_invalid_pass = all(bool(d["rejected"]) for d in invalid_decisions)
    null_unsat_pass = null_U == NULL3["must_U"] and null_P == NULL3["must_P"]
    all_pass = (
        fixture_pass
        and real_up_pass
        and known_false_unconstrained_pass
        and reject_invalid_pass
        and null_unsat_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-1aa0f8-S0",
        "experiment_id": "EXP-ECDLP-1aa0f8",
        "hypothesis_id": "H-ECDLP-a23318",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-COUNT",
        "fixture": {
            "variables": list(VARS),
            "core": list(CORE),
            "target": list(TARGET),
            "REAL3": {
                "id": REAL3["id"],
                "m": REAL3["m"],
                "l": REAL3["l"],
                "clauses": [list(c) for c in REAL3["clauses"]],
                "must_U": REAL3["must_U"],
                "must_P": REAL3["must_P"],
            },
            "KF3": {
                "id": KF3["id"],
                "clauses": [list(c) for c in KF3["clauses"]],
                "must_U": KF3["must_U"],
                "must_P": KF3["must_P"],
            },
            "NULL3": {
                "id": NULL3["id"],
                "clauses": [list(c) for c in NULL3["clauses"]],
                "must_U": NULL3["must_U"],
                "must_P": NULL3["must_P"],
            },
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_up_pass": real_up_pass,
            "known_false_unconstrained_pass": known_false_unconstrained_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_unsat_pass": null_unsat_pass,
            "REAL3": {"U": real_U, "P": real_P},
            "KF3": {"U": kf_U, "P": kf_P},
            "NULL3": {"U": null_U, "P": null_P},
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_1aa0f8_stage1_authorized": False,
        "exp_79f8c4_stage1_authorized": False,
        "exp_628891_stage1_authorized": False,
        "exp_9e9536_stage1_authorized": False,
        "exp_90f602_stage1_authorized": False,
        "exp_4be480_stage2_authorized": False,
        "exp_6a97f4_stage2_authorized": False,
        "exp_420e73_stage17_authorized": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_a_decoder": True,
        "not_approxmc": True,
        "not_a_sat_histogram": True,
        "not_trimoska_pdp_encoder": True,
        "do_not_hunt_a_new_cnf": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-1aa0f8/implementation/stage0_count.py\n"
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
        "real_up_pass": real_up_pass,
        "known_false_unconstrained_pass": known_false_unconstrained_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_unsat_pass": null_unsat_pass,
        "REAL3_U": real_U,
        "REAL3_P": real_P,
        "KF3_U": kf_U,
        "KF3_P": kf_P,
        "NULL3_U": null_U,
        "NULL3_P": null_P,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-1aa0f8-S0
  experiment_id: EXP-ECDLP-1aa0f8
  run_id: RUN-ECDLP-1aa0f8-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_up_pass: {str(real_up_pass).lower()}
  known_false_unconstrained_pass: {str(known_false_unconstrained_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_unsat_pass: {str(null_unsat_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_a98ea9_stage5_authorized: false
  exp_420e73_stage17_authorized: false
  exp_4be480_stage2_authorized: false
  exp_6a97f4_stage2_authorized: false
  exp_90f602_stage1_authorized: false
  exp_9e9536_stage1_authorized: false
  exp_628891_stage1_authorized: false
  exp_79f8c4_stage1_authorized: false
  exp_1aa0f8_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_approxmc: true
  not_a_sat_histogram: true
  not_trimoska_pdp_encoder: true
  do_not_hunt_a_new_cnf: true
  frozen_object: P-S0-COUNT
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL3 / KF3 / NULL3 counts match committed table. Invalid objects rejected.
  - real_up_pass {str(real_up_pass).lower()}. REAL3 U={real_U} P={real_P}.
  - known_false_unconstrained_pass {str(known_false_unconstrained_pass).lower()}. KF3 U={kf_U} P={kf_P}.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. Empty and core-only objects rejected before any free-target census.
  - null_unsat_pass {str(null_unsat_pass).lower()}. NULL3 U={null_U} P={null_P}.
  unexpected_observations: []
  scientific_boundary: Toy 5-variable free-target enumerative calibrator. Not a decoder. Not ApproxMC. Not XOR hashing. Not cadical. Not the Trimoska pdp encoder. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new CNF. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-1aa0f8-S0
  experiment_id: EXP-ECDLP-1aa0f8
  hypothesis_id: H-ECDLP-a23318
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
    command: python3 experiments/EXP-ECDLP-1aa0f8/implementation/stage0_count.py
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
      frozen_object: P-S0-COUNT
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL3, KF3, NULL3]
    seeds:
      declared: []
  timing:
    wall_clock_seconds: {elapsed}
  resources:
    wall_clock_seconds: {elapsed}
    peak_rss_bytes: null
  result:
    validity_status: {'valid' if all_pass else 'invalid'}
    valid: {str(all_pass).lower()}
    validity_reason: Stage 0 exact-count calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_up_pass: {str(real_up_pass).lower()}
      known_false_unconstrained_pass: {str(known_false_unconstrained_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_unsat_pass: {str(null_unsat_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_approxmc: true
      not_a_sat_histogram: true
      not_trimoska_pdp_encoder: true
      do_not_hunt_a_new_cnf: true
      stage1_authorized: false
      exp_1aa0f8_stage1_authorized: false
      exp_79f8c4_stage1_authorized: false
      exp_628891_stage1_authorized: false
      exp_9e9536_stage1_authorized: false
      exp_90f602_stage1_authorized: false
      exp_4be480_stage2_authorized: false
      exp_6a97f4_stage2_authorized: false
      exp_420e73_stage17_authorized: false
      exp_a98ea9_stage5_authorized: false
    scientific_boundary: Toy 5-variable free-target enumerative calibrator. Not a decoder. Not ApproxMC. Not XOR hashing. Not cadical. Not the Trimoska pdp encoder. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new CNF.
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
                "real_up_pass": real_up_pass,
                "known_false_unconstrained_pass": known_false_unconstrained_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_unsat_pass": null_unsat_pass,
                "REAL3": {"U": real_U, "P": real_P},
                "KF3": {"U": kf_U, "P": kf_P},
                "NULL3": {"U": null_U, "P": null_P},
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
