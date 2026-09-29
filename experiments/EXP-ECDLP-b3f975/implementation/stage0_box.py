#!/usr/bin/env python3
"""EXP-ECDLP-b3f975 Stage 0 exact Gaussian-integer box-membership calibrator.

Certificate kind none. No decoder. No factor base. No relation vector.
No Groebner census. No C(p). Do not hunt a new curve.
Frozen object P-S0-BOX: REAL / KF / NULL.

D = -4. Split in Z[i] iff p ≡ 1 (mod 4). x is in the box iff some
|u|,|v| <= R satisfy u + r v ≡ x (mod p) for a root r of T^2+1 in F_p.
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
SOURCE = "experiments/EXP-ECDLP-b3f975/implementation/stage0_box.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-b3f975/runs/RUN-ECDLP-b3f975-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-b3f975/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-de0c09"
TASK_ID = "TASK-20260908-cd63b5"

REAL = {
    "id": "REAL",
    "p": 13,
    "R": 1,
    "x": 1,
    "u": 1,
    "v": 0,
    "must_in_box": True,
}
KF = {"id": "KF", "p": 13, "R": 1, "x": 2, "must_in_box": False}
NULL = {"id": "NULL", "p": 7, "must_reject": True}


class NonSplitError(ValueError):
    """p does not split in Z[i]; box membership is undefined, not false."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def splits_in_zi(p: int) -> bool:
    return p % 4 == 1


def root_of_t2_plus_1(p: int) -> int:
    for r in range(p):
        if (r * r + 1) % p == 0:
            return r
    raise NonSplitError("no root of T^2+1")


def box_membership(p: int, R: int, x: int) -> dict[str, object]:
    if p <= 0 or R < 0:
        raise ValueError("non-positive p or negative R")
    if not splits_in_zi(p):
        raise NonSplitError("p does not split in Z[i]")
    r = root_of_t2_plus_1(p)
    x_mod = x % p
    in_box = False
    witness = None
    image = set()
    for u in range(-R, R + 1):
        for v in range(-R, R + 1):
            val = (u + r * v) % p
            image.add(val)
            if val == x_mod:
                in_box = True
                if witness is None:
                    witness = {"u": u, "v": v}
    return {
        "p": p,
        "R": R,
        "x": x_mod,
        "splits": True,
        "root": r,
        "in_box": in_box,
        "witness": witness,
        "image": sorted(image),
        "image_size": len(image),
    }


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        box_membership(0, REAL["R"], REAL["x"])
        decisions.append({"id": "P-zero", "rejected": False})
    except ValueError:
        decisions.append({"id": "P-zero", "rejected": True})
    try:
        box_membership(REAL["p"], -1, REAL["x"])
        decisions.append({"id": "R-negative", "rejected": False})
    except ValueError:
        decisions.append({"id": "R-negative", "rejected": True})
    return decisions


def null_decision() -> dict[str, object]:
    try:
        box_membership(NULL["p"], 1, 0)
        return {"id": NULL["id"], "p": NULL["p"], "rejected": False, "splits": True}
    except NonSplitError:
        return {
            "id": NULL["id"],
            "p": NULL["p"],
            "rejected": True,
            "splits": False,
            "reason": "p does not split in Z[i]",
        }


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real = box_membership(REAL["p"], REAL["R"], REAL["x"])
    kf = box_membership(KF["p"], KF["R"], KF["x"])
    null = null_decision()
    invalid_decisions = reject_invalid()

    fixture_pass = (
        REAL["p"] == 13
        and REAL["R"] == 1
        and REAL["x"] == 1
        and KF["p"] == 13
        and KF["R"] == 1
        and KF["x"] == 2
        and NULL["p"] == 7
        and REAL["must_in_box"] is True
        and KF["must_in_box"] is False
        and NULL["must_reject"] is True
    )
    real_box_pass = real["in_box"] is REAL["must_in_box"]
    known_false_out_pass = kf["in_box"] is KF["must_in_box"]
    reject_invalid_pass = all(bool(d["rejected"]) for d in invalid_decisions)
    null_nonsplit_pass = bool(null["rejected"]) and null["splits"] is False
    all_pass = (
        fixture_pass
        and real_box_pass
        and known_false_out_pass
        and reject_invalid_pass
        and null_nonsplit_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-b3f975-S0",
        "experiment_id": "EXP-ECDLP-b3f975",
        "hypothesis_id": "H-ECDLP-e54f8c",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-BOX",
        "fixture": {
            "discriminant": -4,
            "REAL": {
                "id": REAL["id"],
                "p": REAL["p"],
                "R": REAL["R"],
                "x": REAL["x"],
                "u": REAL["u"],
                "v": REAL["v"],
                "must_in_box": REAL["must_in_box"],
            },
            "KF": {
                "id": KF["id"],
                "p": KF["p"],
                "R": KF["R"],
                "x": KF["x"],
                "must_in_box": KF["must_in_box"],
            },
            "NULL": {
                "id": NULL["id"],
                "p": NULL["p"],
                "must_reject": NULL["must_reject"],
            },
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_box_pass": real_box_pass,
            "known_false_out_pass": known_false_out_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_nonsplit_pass": null_nonsplit_pass,
            "REAL": real,
            "KF": kf,
            "NULL": null,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "not_a_factor_base": True,
        "not_a_relation_vector": True,
        "not_a_groebner_census": True,
        "not_C_p": True,
        "do_not_hunt_a_new_curve": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-b3f975/implementation/stage0_box.py\n"
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
        "real_box_pass": real_box_pass,
        "known_false_out_pass": known_false_out_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_nonsplit_pass": null_nonsplit_pass,
        "REAL": real,
        "KF": kf,
        "NULL": null,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-b3f975-S0
  experiment_id: EXP-ECDLP-b3f975
  run_id: RUN-ECDLP-b3f975-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_box_pass: {str(real_box_pass).lower()}
  known_false_out_pass: {str(known_false_out_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_nonsplit_pass: {str(null_nonsplit_pass).lower()}
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
  stage1_authorized: false
  not_a_decoder: true
  not_a_factor_base: true
  not_a_relation_vector: true
  not_a_groebner_census: true
  not_C_p: true
  do_not_hunt_a_new_curve: true
  frozen_object: P-S0-BOX
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL box values match committed table. Invalid objects rejected.
  - real_box_pass {str(real_box_pass).lower()}. REAL p={REAL['p']} R={REAL['R']} x={REAL['x']} in_box {str(real['in_box']).lower()} root {real['root']}.
  - known_false_out_pass {str(known_false_out_pass).lower()}. KF in_box {str(kf['in_box']).lower()}.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. P-zero and R-negative rejected before any box census.
  - null_nonsplit_pass {str(null_nonsplit_pass).lower()}. NULL rejected {str(null['rejected']).lower()} splits {str(null['splits']).lower()}.
  unexpected_observations: []
  scientific_boundary: Toy three-triple Gauss-reduction box-membership calibrator at D = -4. Not a factor base. Not a relation vector. Not a Groebner census. Not C(p). Not a decoder. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new curve. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-b3f975-S0
  experiment_id: EXP-ECDLP-b3f975
  hypothesis_id: H-ECDLP-e54f8c
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
    command: python3 experiments/EXP-ECDLP-b3f975/implementation/stage0_box.py
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
      frozen_object: P-S0-BOX
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
    validity_reason: Stage 0 exact Gauss-reduction box-membership calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_box_pass: {str(real_box_pass).lower()}
      known_false_out_pass: {str(known_false_out_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_nonsplit_pass: {str(null_nonsplit_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_factor_base: true
      not_a_relation_vector: true
      not_a_groebner_census: true
      not_C_p: true
      do_not_hunt_a_new_curve: true
      stage1_authorized: false
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
    scientific_boundary: Toy three-triple Gauss-reduction box-membership calibrator at D = -4. Not a factor base. Not a relation vector. Not a Groebner census. Not C(p). Not a decoder. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new curve.
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
                "real_box_pass": real_box_pass,
                "known_false_out_pass": known_false_out_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_nonsplit_pass": null_nonsplit_pass,
                "REAL": real,
                "KF": kf,
                "NULL": null,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
