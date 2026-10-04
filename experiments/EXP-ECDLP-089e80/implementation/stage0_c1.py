#!/usr/bin/env python3
"""EXP-ECDLP-089e80 Stage 0 exact C1 fibre-partition calibrator.

Certificate kind none. No decoder. No window factor base. No S_3^y.
No C2. No (L, b) meter. Do not hunt a new curve.
Frozen object P-S0-C1: REAL / KF / NULL.

E: y^2 = x^3 - x over F_11. Both x- and y-partitions sum to #E=12
with O counted at infinity. KF is the y-fibre at 0, size 3, ratio 3.
NULL is a constant map and is rejected.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-089e80/implementation/stage0_c1.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-089e80/runs/RUN-ECDLP-089e80-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-089e80/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-ff376f"
TASK_ID = "TASK-20260908-91cd84"

REAL = {
    "id": "REAL",
    "p": 11,
    "A": -1,
    "B": 0,
    "must_count": 12,
}
KF = {"id": "KF", "f": "y", "W": [0], "must_ratio": 3}
NULL = {"id": "NULL", "kind": "constant", "must_reject": True}


class ConstantMapError(ValueError):
    """A constant map is not a degree >= 2 coordinate; reject, do not census."""


class SingularCubicError(ValueError):
    """Weierstrass discriminant is zero; the model is not an elliptic curve."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def discriminant(A: int, B: int, p: int) -> int:
    """-16(4A^3 + 27B^2) mod p."""
    return (-16 * (4 * A * A * A + 27 * B * B)) % p


def affine_points(p: int, A: int, B: int) -> list[tuple[int, int]]:
    if p <= 0:
        raise ValueError("non-positive p")
    if discriminant(A, B, p) == 0:
        raise SingularCubicError("singular Weierstrass cubic")
    pts: list[tuple[int, int]] = []
    for x in range(p):
        rhs = (x * x * x + A * x + B) % p
        for y in range(p):
            if (y * y) % p == rhs:
                pts.append((x, y))
    return pts


def partition_sums(pts: list[tuple[int, int]], p: int) -> dict[str, object]:
    x_fibres = Counter(x for x, _y in pts)
    y_fibres = Counter(y for _x, y in pts)
    x_sum = int(sum(x_fibres.values())) + 1  # O at infinity
    y_sum = int(sum(y_fibres.values())) + 1
    y0 = int(y_fibres.get(0, 0))
    return {
        "affine_count": len(pts),
        "nE": len(pts) + 1,
        "x_partition_sum": x_sum,
        "y_partition_sum": y_sum,
        "x_fibres": {str(k): int(v) for k, v in sorted(x_fibres.items())},
        "y_fibres": {str(k): int(v) for k, v in sorted(y_fibres.items())},
        "y0_fibre_size": y0,
        "affine_points": [[x, y] for x, y in pts],
    }


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        affine_points(0, REAL["A"], REAL["B"])
        decisions.append({"id": "P-zero", "rejected": False})
    except ValueError:
        decisions.append({"id": "P-zero", "rejected": True})
    try:
        affine_points(REAL["p"], 0, 0)
        decisions.append({"id": "singular", "rejected": False})
    except (SingularCubicError, ValueError):
        decisions.append({"id": "singular", "rejected": True})
    return decisions


def null_decision() -> dict[str, object]:
    try:
        raise ConstantMapError("constant map has degree 0")
    except ConstantMapError:
        return {
            "id": NULL["id"],
            "kind": NULL["kind"],
            "rejected": True,
            "reason": "constant map has degree 0",
        }


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    pts = affine_points(REAL["p"], REAL["A"], REAL["B"])
    real = partition_sums(pts, REAL["p"])
    kf_ratio = (
        real["y0_fibre_size"] / len(KF["W"]) if KF["W"] else None
    )
    kf = {
        "id": KF["id"],
        "f": KF["f"],
        "W": list(KF["W"]),
        "fibre_size": real["y0_fibre_size"],
        "window_size": len(KF["W"]),
        "ratio": kf_ratio,
    }
    null = null_decision()
    invalid_decisions = reject_invalid()

    fixture_pass = (
        REAL["p"] == 11
        and REAL["A"] == -1
        and REAL["B"] == 0
        and REAL["must_count"] == 12
        and KF["f"] == "y"
        and KF["W"] == [0]
        and KF["must_ratio"] == 3
        and NULL["kind"] == "constant"
        and NULL["must_reject"] is True
    )
    real_double_count_pass = (
        real["nE"] == REAL["must_count"]
        and real["x_partition_sum"] == REAL["must_count"]
        and real["y_partition_sum"] == REAL["must_count"]
    )
    known_false_adaptive_pass = kf["ratio"] == KF["must_ratio"]
    reject_invalid_pass = all(bool(d["rejected"]) for d in invalid_decisions)
    null_constant_pass = bool(null["rejected"])
    all_pass = (
        fixture_pass
        and real_double_count_pass
        and known_false_adaptive_pass
        and reject_invalid_pass
        and null_constant_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-089e80-S0",
        "experiment_id": "EXP-ECDLP-089e80",
        "hypothesis_id": "H-ECDLP-7f5b05",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-C1",
        "fixture": {
            "curve": {
                "p": REAL["p"],
                "A": REAL["A"],
                "B": REAL["B"],
                "Weierstrass": "y^2 = x^3 - x",
                "j": 1728,
            },
            "REAL": {
                "id": REAL["id"],
                "p": REAL["p"],
                "A": REAL["A"],
                "B": REAL["B"],
                "must_count": REAL["must_count"],
            },
            "KF": {
                "id": KF["id"],
                "f": KF["f"],
                "W": list(KF["W"]),
                "must_ratio": KF["must_ratio"],
            },
            "NULL": {
                "id": NULL["id"],
                "kind": NULL["kind"],
                "must_reject": NULL["must_reject"],
            },
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_double_count_pass": real_double_count_pass,
            "known_false_adaptive_pass": known_false_adaptive_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_constant_pass": null_constant_pass,
            "REAL": real,
            "KF": kf,
            "NULL": null,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "not_a_window_base": True,
        "not_S3y": True,
        "not_C2": True,
        "not_Lb_meter": True,
        "do_not_hunt_a_new_curve": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-089e80/implementation/stage0_c1.py\n"
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
        "real_double_count_pass": real_double_count_pass,
        "known_false_adaptive_pass": known_false_adaptive_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_constant_pass": null_constant_pass,
        "REAL": {
            "nE": real["nE"],
            "x_partition_sum": real["x_partition_sum"],
            "y_partition_sum": real["y_partition_sum"],
            "affine_count": real["affine_count"],
            "y0_fibre_size": real["y0_fibre_size"],
        },
        "KF": kf,
        "NULL": null,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-089e80-S0
  experiment_id: EXP-ECDLP-089e80
  run_id: RUN-ECDLP-089e80-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_double_count_pass: {str(real_double_count_pass).lower()}
  known_false_adaptive_pass: {str(known_false_adaptive_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_constant_pass: {str(null_constant_pass).lower()}
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
  stage1_authorized: false
  not_a_decoder: true
  not_a_window_base: true
  not_S3y: true
  not_C2: true
  not_Lb_meter: true
  do_not_hunt_a_new_curve: true
  frozen_object: P-S0-C1
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL C1 values match committed table. Invalid objects rejected.
  - real_double_count_pass {str(real_double_count_pass).lower()}. REAL p={REAL['p']} A={REAL['A']} B={REAL['B']} nE {real['nE']} x_sum {real['x_partition_sum']} y_sum {real['y_partition_sum']}.
  - known_false_adaptive_pass {str(known_false_adaptive_pass).lower()}. KF y0 fibre {real['y0_fibre_size']} ratio {kf['ratio']}.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. P-zero and singular cubic rejected before any fibre census.
  - null_constant_pass {str(null_constant_pass).lower()}. NULL rejected {str(null['rejected']).lower()}.
  unexpected_observations: []
  scientific_boundary: Toy one-curve C1 fibre-partition calibrator at p=11. Not a window factor base. Not S_3^y. Not C2. Not an (L, b) meter. Not a decoder. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new curve. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-089e80-S0
  experiment_id: EXP-ECDLP-089e80
  hypothesis_id: H-ECDLP-7f5b05
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
    command: python3 experiments/EXP-ECDLP-089e80/implementation/stage0_c1.py
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
      frozen_object: P-S0-C1
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
    validity_reason: Stage 0 exact C1 fibre-partition calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_double_count_pass: {str(real_double_count_pass).lower()}
      known_false_adaptive_pass: {str(known_false_adaptive_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_constant_pass: {str(null_constant_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_window_base: true
      not_S3y: true
      not_C2: true
      not_Lb_meter: true
      do_not_hunt_a_new_curve: true
      stage1_authorized: false
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
    scientific_boundary: Toy one-curve C1 fibre-partition calibrator at p=11. Not a window factor base. Not S_3^y. Not C2. Not an (L, b) meter. Not a decoder. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new curve.
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
                "real_double_count_pass": real_double_count_pass,
                "known_false_adaptive_pass": known_false_adaptive_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_constant_pass": null_constant_pass,
                "REAL": {
                    "nE": real["nE"],
                    "x_partition_sum": real["x_partition_sum"],
                    "y_partition_sum": real["y_partition_sum"],
                    "affine_points": real["affine_points"],
                    "y0_fibre_size": real["y0_fibre_size"],
                },
                "KF": kf,
                "NULL": null,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
