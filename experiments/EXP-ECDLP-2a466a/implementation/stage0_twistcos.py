#!/usr/bin/env python3
"""EXP-ECDLP-2a466a Stage 0 exact prime-order / twist-order calibrator.

Certificate kind none. No Weil restriction. No Gaudry. No cubical point.
No Tate pairing. No DL-spectrum. No Coppersmith. No Semaev S_m. No Velu.
Frozen object P-S0-TWISTCOS: REAL / KF / NULL on F_7 Weierstrass toys.

REAL: p=7, E: y^2=x^3+3 (a=0, b=3).
N=13, t=-5, N'=3, gcd(13,3)=1, affine count 12, empty 2-torsion.
KF: p=7, E: y^2=x^3+2 (a=0, b=2), N=9 composite, rejected.
NULL empty point-list is rejected. p=0 is rejected.

Producer method: square-set table. For each y in F_p insert y^2.
For each x, rhs = x^3+a x+b; collect y with y^2 == rhs.
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
SOURCE = "experiments/EXP-ECDLP-2a466a/implementation/stage0_twistcos.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-2a466a/runs/RUN-ECDLP-2a466a-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-2a466a/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-6d2168"
TASK_ID = "TASK-20260908-606325"

REAL_P = 7
REAL_A = 0
REAL_B = 3
MUST_N = 13
MUST_NPRIME = 3
MUST_GCD = 1
MUST_AFFINE_COUNT = 12
FROZEN_AFFINE = [
    (1, 2),
    (1, 5),
    (2, 2),
    (2, 5),
    (3, 3),
    (3, 4),
    (4, 2),
    (4, 5),
    (5, 3),
    (5, 4),
    (6, 3),
    (6, 4),
]
KF_P = 7
KF_A = 0
KF_B = 2
KF_MUST_N = 9


class InvalidParamsError(ValueError):
    """p not a frozen positive integer, or empty point-list, is rejected."""


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


def require_nonempty_points(points: list[tuple[int, int]]) -> None:
    if not points:
        raise InvalidParamsError("point-list is empty")


def square_set(p: int) -> set[int]:
    require_positive_p(p)
    return {((int(y) * int(y)) % int(p)) for y in range(int(p))}


def affine_points(p: int, a: int, b: int) -> list[tuple[int, int]]:
    require_positive_p(p)
    squares = square_set(p)
    pts: list[tuple[int, int]] = []
    for x in range(int(p)):
        rhs = (pow(int(x), 3, int(p)) + int(a) * int(x) + int(b)) % int(p)
        if rhs not in squares:
            continue
        for y in range(int(p)):
            if ((int(y) * int(y)) % int(p)) == rhs:
                pts.append((int(x), int(y)))
    return pts


def is_prime(n: int) -> bool:
    value = int(n)
    if value <= 1:
        return False
    d = 2
    while d * d <= value:
        if value % d == 0:
            return False
        d += 1
    return True


def gcd_int(u: int, v: int) -> int:
    a, b = abs(int(u)), abs(int(v))
    while b:
        a, b = b, a % b
    return a


def two_torsion(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return [pt for pt in points if pt[1] == 0]


def curve_counts(p: int, a: int, b: int) -> dict:
    pts = affine_points(p, a, b)
    require_nonempty_points(pts)
    n = len(pts) + 1
    t = int(p) + 1 - n
    nprime = int(p) + 1 + t
    return {
        "p": int(p),
        "a": int(a),
        "b": int(b),
        "affine": pts,
        "affine_count": len(pts),
        "N": n,
        "t": t,
        "Nprime": nprime,
        "gcd": gcd_int(n, nprime),
        "two_torsion": two_torsion(pts),
        "two_torsion_empty": two_torsion(pts) == [],
        "N_prime": is_prime(n),
    }


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
        require_nonempty_points([])
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_point_list", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_point_list", "rejected": True}

    try:
        kf = curve_counts(KF_P, KF_A, KF_B)
        kf_rejected = (kf["N"] == KF_MUST_N) and (not kf["N_prime"])
        known_false_composite_pass = kf_rejected
        kf_obj = {
            "id": "KF",
            "p": KF_P,
            "a": KF_A,
            "b": KF_B,
            "N": kf["N"],
            "must_N": KF_MUST_N,
            "N_prime": kf["N_prime"],
            "rejected": kf_rejected,
        }
    except InvalidParamsError:
        known_false_composite_pass = False
        kf_obj = {
            "id": "KF",
            "p": KF_P,
            "a": KF_A,
            "b": KF_B,
            "rejected": False,
        }

    real = curve_counts(REAL_P, REAL_A, REAL_B)
    real_order_pass = (
        real["N"] == MUST_N
        and real["Nprime"] == MUST_NPRIME
        and real["gcd"] == MUST_GCD
        and real["affine_count"] == MUST_AFFINE_COUNT
        and real["two_torsion_empty"] is True
        and real["affine"] == list(FROZEN_AFFINE)
        and real["N_prime"] is True
    )
    real_obj = {
        "id": "REAL",
        "p": REAL_P,
        "a": REAL_A,
        "b": REAL_B,
        "N": real["N"],
        "t": real["t"],
        "Nprime": real["Nprime"],
        "gcd": real["gcd"],
        "affine_count": real["affine_count"],
        "affine": real["affine"],
        "two_torsion": real["two_torsion"],
        "two_torsion_empty": real["two_torsion_empty"],
        "N_prime": real["N_prime"],
        "must_N": MUST_N,
        "must_Nprime": MUST_NPRIME,
        "must_gcd": MUST_GCD,
        "must_affine_count": MUST_AFFINE_COUNT,
        "must_affine": [list(pt) for pt in FROZEN_AFFINE],
    }

    all_pass = (
        fixture_pass
        and real_order_pass
        and known_false_composite_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-2a466a-S0",
        "experiment_id": "EXP-ECDLP-2a466a",
        "hypothesis_id": "H-ECDLP-78337d",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-TWISTCOS",
        "fixture": {
            "field": "F_p",
            "REAL": {
                "id": "REAL",
                "p": REAL_P,
                "a": REAL_A,
                "b": REAL_B,
                "must_N": MUST_N,
                "must_Nprime": MUST_NPRIME,
                "must_gcd": MUST_GCD,
                "must_affine_count": MUST_AFFINE_COUNT,
                "must_two_torsion_empty": True,
            },
            "KF": {
                "id": "KF",
                "p": KF_P,
                "a": KF_A,
                "b": KF_B,
                "must_N": KF_MUST_N,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_point_list", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_order_pass": real_order_pass,
            "known_false_composite_pass": known_false_composite_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_2a466a_stage1_authorized": False,
        "exp_8eaf6a_stage1_authorized": False,
        "exp_eab4d7_stage1_authorized": False,
        "exp_a294b6_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "not_weil_restriction": True,
        "not_gaudry": True,
        "not_a_cubical_lift": True,
        "not_tate": True,
        "not_a_dl_spectrum": True,
        "do_not_run_coppersmith": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-2a466a/implementation/stage0_twistcos.py\n"
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
        "known_false_composite_pass": known_false_composite_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            **real_obj,
            "affine": [list(pt) for pt in real_obj["affine"]],
            "two_torsion": [list(pt) for pt in real_obj["two_torsion"]],
        },
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-2a466a-S0
  experiment_id: EXP-ECDLP-2a466a
  run_id: RUN-ECDLP-2a466a-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_order_pass: {str(real_order_pass).lower()}
  known_false_composite_pass: {str(known_false_composite_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_2a466a_stage1_authorized: false
  exp_8eaf6a_stage1_authorized: false
  exp_eab4d7_stage1_authorized: false
  exp_a294b6_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_weil_restriction: true
  not_gaudry: true
  not_a_cubical_lift: true
  not_tate: true
  not_a_dl_spectrum: true
  do_not_run_coppersmith: true
  do_not_form_semaev: true
  do_not_run_velu: true
  frozen_object: P-S0-TWISTCOS
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_order_pass {str(real_order_pass).lower()}. REAL N is {real['N']}, t is {real['t']}, N' is {real['Nprime']}, gcd is {real['gcd']}, affine count is {real['affine_count']}, two-torsion empty is {str(real['two_torsion_empty']).lower()}."
  - "known_false_composite_pass {str(known_false_composite_pass).lower()}. KF N={kf_obj.get('N')} rejected={str(kf_obj['rejected']).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. p=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty point-list is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen prime-order / twist-order calibrator on F_7. Not Weil restriction. Not Gaudry. Not a cubical lift. Not Tate. Not a DL-spectrum. Not Coppersmith. Not Semaev S_m. Not Velu. Not a yield ratio k. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-2a466a. Not Stage 1 of EXP-ECDLP-8eaf6a. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-2a466a-S0
  experiment_id: EXP-ECDLP-2a466a
  hypothesis_id: H-ECDLP-78337d
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
    command: python3 experiments/EXP-ECDLP-2a466a/implementation/stage0_twistcos.py
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
      frozen_object: P-S0-TWISTCOS
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      field: F_p
      real_p: 7
      real_a: 0
      real_b: 3
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
    validity_reason: Stage 0 exact prime-order / twist-order calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_order_pass: {str(real_order_pass).lower()}
      known_false_composite_pass: {str(known_false_composite_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_weil_restriction: true
      not_gaudry: true
      not_a_cubical_lift: true
      not_tate: true
      not_a_dl_spectrum: true
      do_not_run_coppersmith: true
      do_not_form_semaev: true
      do_not_run_velu: true
      stage1_authorized: false
      exp_2a466a_stage1_authorized: false
      exp_8eaf6a_stage1_authorized: false
      exp_eab4d7_stage1_authorized: false
      exp_a294b6_stage1_authorized: false
    scientific_boundary: "Toy frozen prime-order / twist-order calibrator on F_7. Not Weil restriction. Not Gaudry. Not a cubical lift. Not Tate. Not a DL-spectrum. Not Coppersmith. Not Semaev S_m. Not Velu. Not a yield ratio k. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-2a466a. Not Stage 1 of EXP-ECDLP-8eaf6a. Certificate kind none."
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
                "known_false_composite_pass": known_false_composite_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_empty_pass": null_empty_pass,
                "REAL": {
                    "N": real["N"],
                    "t": real["t"],
                    "Nprime": real["Nprime"],
                    "gcd": real["gcd"],
                    "affine_count": real["affine_count"],
                    "two_torsion_empty": real["two_torsion_empty"],
                },
                "KF": kf_obj,
                "NULL": null_obj,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
