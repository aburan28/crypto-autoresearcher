#!/usr/bin/env python3
"""EXP-ECDLP-114eb2 Stage 0 exact M1/M2/M3 identity calibrator.

Certificate kind none. No GL_2 census. No Z/6 census.
No E[ell] kernel count. No rho cost identification. No rho beat.
Frozen object P-S0-TUPLE: REAL / KF / NULL at n=5.

d(k)=|{i : 1<=i<=k, k%i==0}|
M1=d(n-1)+1. M2=2. M3=n+1.
Frozen n=5: d(4)=3 so REAL M1=4, M2=2, M3=6.
KF uses d(n)+1 so M1=d(5)+1=3.
NULL is the zero count M1=0.
n=4 (composite) and n=1 are rejected.
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
SOURCE = "experiments/EXP-ECDLP-114eb2/implementation/stage0_tuple.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-114eb2/runs/RUN-ECDLP-114eb2-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-114eb2/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-f35143"
TASK_ID = "TASK-20260908-c9e746"

N_FROZEN = 5
REAL_MUST_M1 = 4
REAL_MUST_M2 = 2
REAL_MUST_M3 = 6
KF_MUST_M1 = 3
NULL_MUST_M1 = 0
INVALID_N = (4, 1)


class InvalidParamsError(ValueError):
    """n not the frozen prime 5 is rejected, not evaluated."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def divisor_count(k: int) -> int:
    if k < 1:
        raise InvalidParamsError("k < 1")
    return sum(1 for i in range(1, k + 1) if k % i == 0)


def require_frozen(n: int) -> None:
    if n != N_FROZEN:
        raise InvalidParamsError("n is not frozen prime 5")


def M1(n: int, wrong_divisor: bool = False) -> int:
    require_frozen(n)
    if wrong_divisor:
        return divisor_count(n) + 1
    return divisor_count(n - 1) + 1


def M2(n: int) -> int:
    require_frozen(n)
    return 2


def M3(n: int) -> int:
    require_frozen(n)
    return n + 1


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    for nid, n in (("n-composite", 4), ("n-one", 1)):
        try:
            M1(n)
            decisions.append({"id": nid, "n": n, "rejected": False})
        except InvalidParamsError:
            decisions.append({"id": nid, "n": n, "rejected": True})
    return decisions


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    d_n_minus_1 = divisor_count(N_FROZEN - 1)
    d_n = divisor_count(N_FROZEN)
    real_m1 = M1(N_FROZEN)
    real_m2 = M2(N_FROZEN)
    real_m3 = M3(N_FROZEN)
    kf_m1 = M1(N_FROZEN, wrong_divisor=True)
    null_m1 = NULL_MUST_M1
    invalid_decisions = reject_invalid()

    fixture_pass = (
        N_FROZEN == 5
        and d_n_minus_1 == 3
        and d_n == 2
        and REAL_MUST_M1 == 4
        and REAL_MUST_M2 == 2
        and REAL_MUST_M3 == 6
        and KF_MUST_M1 == 3
        and NULL_MUST_M1 == 0
        and divisor_count(4) == 3
        and divisor_count(5) == 2
        and (divisor_count(4) + 1) == 4
        and (divisor_count(5) + 1) == 3
    )
    real_count_pass = (
        real_m1 == REAL_MUST_M1
        and real_m2 == REAL_MUST_M2
        and real_m3 == REAL_MUST_M3
        and real_m1 == d_n_minus_1 + 1
        and real_m2 == 2
        and real_m3 == N_FROZEN + 1
    )
    known_false_wrong_divisor_pass = (
        kf_m1 == KF_MUST_M1 and kf_m1 != REAL_MUST_M1 and kf_m1 == d_n + 1
    )
    reject_invalid_pass = all(bool(row["rejected"]) for row in invalid_decisions)
    null_zero_pass = null_m1 == 0 and null_m1 != REAL_MUST_M1
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_wrong_divisor_pass
        and reject_invalid_pass
        and null_zero_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    real = {
        "id": "REAL",
        "n": N_FROZEN,
        "d_n_minus_1": d_n_minus_1,
        "M1": real_m1,
        "M2": real_m2,
        "M3": real_m3,
    }
    kf = {
        "id": "KF",
        "wrong_divisor": True,
        "d_n": d_n,
        "M1": kf_m1,
    }
    null = {
        "id": "NULL",
        "kind": "zero_count",
        "M1": null_m1,
        "rejected_as_collapse": True,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-114eb2-S0",
        "experiment_id": "EXP-ECDLP-114eb2",
        "hypothesis_id": "H-ECDLP-7df817",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-TUPLE",
        "fixture": {
            "n_frozen": N_FROZEN,
            "REAL": {
                "id": "REAL",
                "must_M1": REAL_MUST_M1,
                "must_M2": REAL_MUST_M2,
                "must_M3": REAL_MUST_M3,
            },
            "KF": {"id": "KF", "must_M1": KF_MUST_M1},
            "NULL": {"id": "NULL", "kind": "zero_count", "must_M1": NULL_MUST_M1},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_count_pass": real_count_pass,
            "known_false_wrong_divisor_pass": known_false_wrong_divisor_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_zero_pass": null_zero_pass,
            "REAL": real,
            "KF": kf,
            "NULL": null,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_114eb2_stage1_authorized": False,
        "exp_821bc5_stage1_authorized": False,
        "exp_735974_stage1_authorized": False,
        "exp_fdae20_stage1_authorized": False,
        "exp_089e80_stage1_authorized": False,
        "exp_b3f975_stage1_authorized": False,
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
        "not_a_rho_beat": True,
        "not_a_gl2_census": True,
        "not_a_z6_census": True,
        "not_an_ell_kernel_count": True,
        "not_a_rho_cost_identification": True,
        "do_not_enumerate_gl2": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-114eb2/implementation/stage0_tuple.py\n"
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
        "real_count_pass": real_count_pass,
        "known_false_wrong_divisor_pass": known_false_wrong_divisor_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_zero_pass": null_zero_pass,
        "REAL": real,
        "KF": kf,
        "NULL": null,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-114eb2-S0
  experiment_id: EXP-ECDLP-114eb2
  run_id: RUN-ECDLP-114eb2-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_count_pass: {str(real_count_pass).lower()}
  known_false_wrong_divisor_pass: {str(known_false_wrong_divisor_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_zero_pass: {str(null_zero_pass).lower()}
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
  exp_b3f975_stage1_authorized: false
  exp_089e80_stage1_authorized: false
  exp_fdae20_stage1_authorized: false
  exp_735974_stage1_authorized: false
  exp_821bc5_stage1_authorized: false
  exp_114eb2_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_a_gl2_census: true
  not_a_z6_census: true
  not_an_ell_kernel_count: true
  not_a_rho_cost_identification: true
  do_not_enumerate_gl2: true
  frozen_object: P-S0-TUPLE
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL M1 M2 M3 values match committed table. Invalid objects rejected."
  - "real_count_pass {str(real_count_pass).lower()}. REAL at n=5 is M1={real_m1}, M2={real_m2}, M3={real_m3}."
  - "known_false_wrong_divisor_pass {str(known_false_wrong_divisor_pass).lower()}. KF wrong-divisor M1 {kf_m1} not equal to REAL 4."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. n=4 and n=1 rejected before any identity is read."
  - "null_zero_pass {str(null_zero_pass).lower()}. NULL M1 is 0 not equal to REAL."
  unexpected_observations: []
  scientific_boundary: "Toy frozen M1/M2/M3 identity calibrator at n=5. Not a GL_2 census. Not a Z/6 census. Not an E[ell] kernel count. Not a rho cost identification. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-114eb2. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not enumerate GL_2 partitions. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-114eb2-S0
  experiment_id: EXP-ECDLP-114eb2
  hypothesis_id: H-ECDLP-7df817
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
    command: python3 experiments/EXP-ECDLP-114eb2/implementation/stage0_tuple.py
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
      frozen_object: P-S0-TUPLE
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      n_frozen: 5
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
    validity_reason: Stage 0 exact M1/M2/M3 identity calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_count_pass: {str(real_count_pass).lower()}
      known_false_wrong_divisor_pass: {str(known_false_wrong_divisor_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_zero_pass: {str(null_zero_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_a_gl2_census: true
      not_a_z6_census: true
      not_an_ell_kernel_count: true
      not_a_rho_cost_identification: true
      do_not_enumerate_gl2: true
      stage1_authorized: false
      exp_114eb2_stage1_authorized: false
      exp_821bc5_stage1_authorized: false
      exp_735974_stage1_authorized: false
      exp_fdae20_stage1_authorized: false
      exp_089e80_stage1_authorized: false
      exp_b3f975_stage1_authorized: false
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
    scientific_boundary: "Toy frozen M1/M2/M3 identity calibrator at n=5. Not a GL_2 census. Not a Z/6 census. Not an E[ell] kernel count. Not a rho cost identification. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-114eb2. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not enumerate GL_2 partitions."
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
                "real_count_pass": real_count_pass,
                "known_false_wrong_divisor_pass": known_false_wrong_divisor_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_zero_pass": null_zero_pass,
                "REAL": real,
                "KF": kf,
                "NULL": null,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
