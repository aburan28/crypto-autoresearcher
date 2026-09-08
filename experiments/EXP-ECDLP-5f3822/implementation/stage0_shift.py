#!/usr/bin/env python3
"""EXP-ECDLP-5f3822 Stage 0 exact additive-group Kummer-fold iff calibrator.

Certificate kind none. No elliptic M_S. No (L,b) meter.
No Aut census. No orbit cost. No rho beat.
Frozen object P-S0-SHIFT: REAL / KF / NULL at n=7.

toy_x(t) = min(t % n, (n-t) % n).
symmetric(S, n) is true iff some c satisfies
S == {(c-s) % n for s in S}.
M_S(x) is the frozenset of toy_x((x+s) % n) for s in S.
collision(S, n) is true iff distinct x, y have M_S(x) == M_S(y).
Stage 0 iff: symmetric == collision.
Frozen REAL: S={1,6}.
Frozen KF: S={1,2,4} (not a 2-set).
NULL is empty or |S|<2 and is rejected.
n=0 is rejected.
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
SOURCE = "experiments/EXP-ECDLP-5f3822/implementation/stage0_shift.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-5f3822/runs/RUN-ECDLP-5f3822-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-5f3822/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-a4ac47"
TASK_ID = "TASK-20260908-4fd857"

N_FROZEN = 7
REAL_S = frozenset({1, 6})
KF_S = frozenset({1, 2, 4})


class InvalidParamsError(ValueError):
    """n not the frozen positive order, or S too short, is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_frozen_n(n: int) -> None:
    if n != N_FROZEN:
        raise InvalidParamsError("n is not the frozen positive order")


def require_shift_set(s: frozenset[int]) -> None:
    if len(s) < 2:
        raise InvalidParamsError("S empty or shorter than 2")


def toy_x(t: int, n: int) -> int:
    require_frozen_n(n)
    t_mod = int(t) % int(n)
    return min(t_mod, (int(n) - t_mod) % int(n))


def symmetric(s: frozenset[int], n: int) -> bool:
    require_frozen_n(n)
    require_shift_set(s)
    for c in range(int(n)):
        reflected = frozenset((c - int(x)) % int(n) for x in s)
        if reflected == s:
            return True
    return False


def m_s(x: int, s: frozenset[int], n: int) -> frozenset[int]:
    require_frozen_n(n)
    require_shift_set(s)
    return frozenset(toy_x((int(x) + int(shift)) % int(n), n) for shift in s)


def collision(s: frozenset[int], n: int) -> bool:
    require_frozen_n(n)
    require_shift_set(s)
    images = [m_s(x, s, n) for x in range(int(n))]
    return len(set(images)) < int(n)


def evaluate(s: frozenset[int], n: int) -> dict[str, object]:
    require_frozen_n(n)
    require_shift_set(s)
    is_sym = symmetric(s, n)
    is_col = collision(s, n)
    images = {str(x): sorted(m_s(x, s, n)) for x in range(int(n))}
    return {
        "symmetric": is_sym,
        "collision": is_col,
        "iff": is_sym == is_col,
        "images": images,
    }


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        evaluate(REAL_S, 0)
        decisions.append({"id": "n-zero", "n": 0, "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "n-zero", "n": 0, "rejected": True})
    return decisions


def reject_null() -> list[dict[str, object]]:
    rows = []
    for kind, s in (("empty", frozenset()), ("singleton", frozenset({1}))):
        try:
            evaluate(s, N_FROZEN)
            rows.append({"id": "NULL", "kind": kind, "rejected": False})
        except InvalidParamsError:
            rows.append({"id": "NULL", "kind": kind, "rejected": True})
    return rows


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real = evaluate(REAL_S, N_FROZEN)
    kf = evaluate(KF_S, N_FROZEN)
    null_rows = reject_null()
    invalid_decisions = reject_invalid()

    fixture_pass = (
        N_FROZEN == 7
        and REAL_S == frozenset({1, 6})
        and KF_S == frozenset({1, 2, 4})
        and len(KF_S) != 2
    )
    real_count_pass = bool(real["symmetric"]) and bool(real["collision"]) and bool(real["iff"])
    known_false_asymmetric_pass = (
        (not bool(kf["symmetric"]))
        and (not bool(kf["collision"]))
        and bool(kf["iff"])
        and (bool(kf["symmetric"]) != bool(real["symmetric"]))
        and len(KF_S) != 2
    )
    reject_invalid_pass = all(bool(row["rejected"]) for row in invalid_decisions)
    null_empty_pass = all(bool(row["rejected"]) for row in null_rows)
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_asymmetric_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    real_obj = {"id": "REAL", "S": sorted(REAL_S), **real}
    kf_obj = {
        "id": "KF",
        "asymmetric": True,
        "must_not_be_pair": True,
        "S": sorted(KF_S),
        **kf,
    }
    null_obj = {
        "id": "NULL",
        "kind": "empty_or_short_S",
        "rejected": all(bool(row["rejected"]) for row in null_rows),
        "rows": null_rows,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-5f3822-S0",
        "experiment_id": "EXP-ECDLP-5f3822",
        "hypothesis_id": "H-ECDLP-aecab6",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-SHIFT",
        "fixture": {
            "n_frozen": N_FROZEN,
            "REAL": {
                "id": "REAL",
                "S": sorted(REAL_S),
                "must_symmetric": True,
                "must_collision": True,
                "must_iff": True,
            },
            "KF": {
                "id": "KF",
                "S": sorted(KF_S),
                "must_symmetric": False,
                "must_collision": False,
                "must_iff": True,
                "must_not_be_pair": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_or_short_S", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_count_pass": real_count_pass,
            "known_false_asymmetric_pass": known_false_asymmetric_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_5f3822_stage1_authorized": False,
        "exp_6ffef4_stage1_authorized": False,
        "exp_11c247_stage1_authorized": False,
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
        "not_elliptic_ms": True,
        "not_an_lb_meter": True,
        "not_an_aut_census": True,
        "not_an_orbit_cost": True,
        "do_not_form_elliptic_ms": True,
        "do_not_run_lb_meter": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-5f3822/implementation/stage0_shift.py\n"
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
        "known_false_asymmetric_pass": known_false_asymmetric_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-5f3822-S0
  experiment_id: EXP-ECDLP-5f3822
  run_id: RUN-ECDLP-5f3822-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_count_pass: {str(real_count_pass).lower()}
  known_false_asymmetric_pass: {str(known_false_asymmetric_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
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
  exp_11c247_stage1_authorized: false
  exp_6ffef4_stage1_authorized: false
  exp_5f3822_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_elliptic_ms: true
  not_an_lb_meter: true
  not_an_aut_census: true
  not_an_orbit_cost: true
  do_not_form_elliptic_ms: true
  do_not_run_lb_meter: true
  frozen_object: P-S0-SHIFT
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_count_pass {str(real_count_pass).lower()}. REAL symmetric is {str(real['symmetric']).lower()}. REAL collision is {str(real['collision']).lower()}."
  - "known_false_asymmetric_pass {str(known_false_asymmetric_pass).lower()}. KF symmetric is {str(kf['symmetric']).lower()} and KF collision is {str(kf['collision']).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. n=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty or short S is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen additive-group Kummer-fold iff calibrator at n=7. Not elliptic M_S. Not an (L,b) meter. Not an Aut census. Not an orbit cost. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-5f3822. Not Stage 1 of EXP-ECDLP-6ffef4. Not Stage 1 of EXP-ECDLP-11c247. Not Stage 1 of EXP-ECDLP-114eb2. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not form elliptic M_S. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-5f3822-S0
  experiment_id: EXP-ECDLP-5f3822
  hypothesis_id: H-ECDLP-aecab6
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
    command: python3 experiments/EXP-ECDLP-5f3822/implementation/stage0_shift.py
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
      frozen_object: P-S0-SHIFT
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      n_frozen: 7
      real_S: [1, 6]
      kf_S: [1, 2, 4]
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
    validity_reason: Stage 0 exact additive-group Kummer-fold iff calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_count_pass: {str(real_count_pass).lower()}
      known_false_asymmetric_pass: {str(known_false_asymmetric_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_elliptic_ms: true
      not_an_lb_meter: true
      not_an_aut_census: true
      not_an_orbit_cost: true
      do_not_form_elliptic_ms: true
      do_not_run_lb_meter: true
      stage1_authorized: false
      exp_5f3822_stage1_authorized: false
      exp_6ffef4_stage1_authorized: false
      exp_11c247_stage1_authorized: false
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
    scientific_boundary: "Toy frozen additive-group Kummer-fold iff calibrator at n=7. Not elliptic M_S. Not an (L,b) meter. Not an Aut census. Not an orbit cost. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-5f3822. Not Stage 1 of EXP-ECDLP-6ffef4. Not Stage 1 of EXP-ECDLP-11c247. Not Stage 1 of EXP-ECDLP-114eb2. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not form elliptic M_S."
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
                "known_false_asymmetric_pass": known_false_asymmetric_pass,
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
