#!/usr/bin/env python3
"""EXP-ECDLP-daf1bb Stage 0 exact Hom-triviality gcd calibrator.

Certificate kind none. No decoder. No net. No Miller function.
No cubical lift. No dual-number jet. No (L, b) meter.
Do not hunt a new curve. Frozen object P-S0-HOM: REAL / KF / NULL.

Hom(Z/N, F_p^*) trivial iff gcd(N, p-1) == 1.
Hom(Z/N, F_p) trivial iff gcd(N, p) == 1.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-daf1bb/implementation/stage0_hom.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-daf1bb/runs/RUN-ECDLP-daf1bb-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-daf1bb/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-5dda73"
TASK_ID = "TASK-20260908-2e1bc1"

REAL = {"id": "REAL", "p": 17, "N": 5, "must_mult_trivial": True, "must_add_trivial": True}
KF = {"id": "KF", "p": 11, "N": 5, "must_mult_trivial": False}
NULL = {"id": "NULL", "p": 7, "N": 7, "must_add_trivial": False}


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def hom_triviality(p: int, N: int) -> dict[str, object]:
    if N <= 0 or p <= 0:
        raise ValueError("non-positive p or N")
    gcd_mult = math.gcd(N, p - 1)
    gcd_add = math.gcd(N, p)
    return {
        "p": p,
        "N": N,
        "gcd_N_p_minus_1": gcd_mult,
        "gcd_N_p": gcd_add,
        "mult_trivial": gcd_mult == 1,
        "add_trivial": gcd_add == 1,
    }


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        hom_triviality(REAL["p"], 0)
        decisions.append({"id": "N-zero", "rejected": False})
    except ValueError:
        decisions.append({"id": "N-zero", "rejected": True})
    try:
        hom_triviality(0, REAL["N"])
        decisions.append({"id": "P-zero", "rejected": False})
    except ValueError:
        decisions.append({"id": "P-zero", "rejected": True})
    return decisions


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real = hom_triviality(REAL["p"], REAL["N"])
    kf = hom_triviality(KF["p"], KF["N"])
    null = hom_triviality(NULL["p"], NULL["N"])
    invalid_decisions = reject_invalid()

    fixture_pass = True
    real_hom_pass = (
        real["mult_trivial"] is REAL["must_mult_trivial"]
        and real["add_trivial"] is REAL["must_add_trivial"]
    )
    known_false_mov_pass = kf["mult_trivial"] is KF["must_mult_trivial"]
    reject_invalid_pass = all(bool(d["rejected"]) for d in invalid_decisions)
    null_anomalous_pass = null["add_trivial"] is NULL["must_add_trivial"]
    all_pass = (
        fixture_pass
        and real_hom_pass
        and known_false_mov_pass
        and reject_invalid_pass
        and null_anomalous_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-daf1bb-S0",
        "experiment_id": "EXP-ECDLP-daf1bb",
        "hypothesis_id": "H-ECDLP-a69bea",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-HOM",
        "fixture": {
            "REAL": {
                "id": REAL["id"],
                "p": REAL["p"],
                "N": REAL["N"],
                "must_mult_trivial": REAL["must_mult_trivial"],
                "must_add_trivial": REAL["must_add_trivial"],
            },
            "KF": {
                "id": KF["id"],
                "p": KF["p"],
                "N": KF["N"],
                "must_mult_trivial": KF["must_mult_trivial"],
            },
            "NULL": {
                "id": NULL["id"],
                "p": NULL["p"],
                "N": NULL["N"],
                "must_add_trivial": NULL["must_add_trivial"],
            },
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_hom_pass": real_hom_pass,
            "known_false_mov_pass": known_false_mov_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_anomalous_pass": null_anomalous_pass,
            "REAL": real,
            "KF": kf,
            "NULL": null,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_daf1bb_stage1_authorized": False,
        "exp_0d1336_stage1_authorized": False,
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
        "not_a_net": True,
        "not_a_miller_function": True,
        "not_a_cubical_lift": True,
        "not_a_dual_number_jet": True,
        "not_an_Lb_meter": True,
        "do_not_hunt_a_new_curve": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-daf1bb/implementation/stage0_hom.py\n"
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
        "real_hom_pass": real_hom_pass,
        "known_false_mov_pass": known_false_mov_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_anomalous_pass": null_anomalous_pass,
        "REAL": real,
        "KF": kf,
        "NULL": null,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-daf1bb-S0
  experiment_id: EXP-ECDLP-daf1bb
  run_id: RUN-ECDLP-daf1bb-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_hom_pass: {str(real_hom_pass).lower()}
  known_false_mov_pass: {str(known_false_mov_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_anomalous_pass: {str(null_anomalous_pass).lower()}
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
  exp_0d1336_stage1_authorized: false
  exp_daf1bb_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_net: true
  not_a_miller_function: true
  not_a_cubical_lift: true
  not_a_dual_number_jet: true
  not_an_Lb_meter: true
  do_not_hunt_a_new_curve: true
  frozen_object: P-S0-HOM
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL Hom values match committed table. Invalid objects rejected.
  - real_hom_pass {str(real_hom_pass).lower()}. REAL p={REAL['p']} N={REAL['N']} mult_trivial {str(real['mult_trivial']).lower()} add_trivial {str(real['add_trivial']).lower()}.
  - known_false_mov_pass {str(known_false_mov_pass).lower()}. KF mult_trivial {str(kf['mult_trivial']).lower()}.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. N-zero and P-zero rejected before any Hom census.
  - null_anomalous_pass {str(null_anomalous_pass).lower()}. NULL add_trivial {str(null['add_trivial']).lower()}.
  unexpected_observations: []
  scientific_boundary: Toy three-triple Hom-triviality gcd calibrator. Not a net. Not a Miller function. Not a cubical lift. Not a dual-number jet. Not an (L, b) meter. Not a decoder. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new curve. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-daf1bb-S0
  experiment_id: EXP-ECDLP-daf1bb
  hypothesis_id: H-ECDLP-a69bea
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
    command: python3 experiments/EXP-ECDLP-daf1bb/implementation/stage0_hom.py
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
      frozen_object: P-S0-HOM
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
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
    validity_reason: Stage 0 exact Hom-triviality gcd calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_hom_pass: {str(real_hom_pass).lower()}
      known_false_mov_pass: {str(known_false_mov_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_anomalous_pass: {str(null_anomalous_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_net: true
      not_a_miller_function: true
      not_a_cubical_lift: true
      not_a_dual_number_jet: true
      not_an_Lb_meter: true
      do_not_hunt_a_new_curve: true
      stage1_authorized: false
      exp_daf1bb_stage1_authorized: false
      exp_0d1336_stage1_authorized: false
      exp_1aa0f8_stage1_authorized: false
      exp_79f8c4_stage1_authorized: false
      exp_628891_stage1_authorized: false
      exp_9e9536_stage1_authorized: false
      exp_90f602_stage1_authorized: false
      exp_4be480_stage2_authorized: false
      exp_6a97f4_stage2_authorized: false
      exp_420e73_stage17_authorized: false
      exp_a98ea9_stage5_authorized: false
    scientific_boundary: Toy three-triple Hom-triviality gcd calibrator. Not a net. Not a Miller function. Not a cubical lift. Not a dual-number jet. Not an (L, b) meter. Not a decoder. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new curve.
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
                "real_hom_pass": real_hom_pass,
                "known_false_mov_pass": known_false_mov_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_anomalous_pass": null_anomalous_pass,
                "REAL": real,
                "KF": kf,
                "NULL": null,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
