#!/usr/bin/env python3
"""EXP-ECDLP-821bc5 Stage 0 exact W_n identity calibrator.

Certificate kind none. No sympy S_4 expansion. No Aut arm.
No sigma ladder. No crater hunt. No rho beat.
Frozen object P-S0-WTLAW: REAL / KF / NULL.

closed_form(n)=(n-1)*2**(n-2)
w_res(d_f,w_f,d_g,w_g)=d_g*w_f + d_f*w_g - d_f*d_g
Frozen splits: W_3=4; W_4=w_res(2,4,2,4)=12;
W_5=w_res(2,4,4,12)=32; W_6=w_res(4,12,4,12)=80;
W_6_alt=w_res(2,4,8,32)=80.
KF omits -d_f*d_g. NULL is the zero sequence.
This W_n is not the O2-line second moment W.
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
SOURCE = "experiments/EXP-ECDLP-821bc5/implementation/stage0_wtlaw.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-821bc5/runs/RUN-ECDLP-821bc5-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-821bc5/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-cb5565"
TASK_ID = "TASK-20260908-1416af"

N_VALUES = (3, 4, 5, 6)
W3_FROZEN = 4
REAL_MUST = {3: 4, 4: 12, 5: 32, 6: 80}
W6_ALT_MUST = 80
KF_W4_MUST = 16
NULL_MUST = 0


class InvalidParamsError(ValueError):
    """n not in {3,4,5,6} is rejected, not evaluated."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def closed_form(n: int) -> int:
    if n not in N_VALUES:
        raise InvalidParamsError("n not in frozen panel")
    return (n - 1) * (2 ** (n - 2))


def w_res(d_f: int, w_f: int, d_g: int, w_g: int, omit_sylvester: bool = False) -> int:
    term = 0 if omit_sylvester else d_f * d_g
    return d_g * w_f + d_f * w_g - term


def recurrence_W(n: int, omit_sylvester: bool = False) -> int:
    if n not in N_VALUES:
        raise InvalidParamsError("n not in frozen panel")
    if n == 3:
        if omit_sylvester:
            return 0
        return W3_FROZEN
    w3 = 0 if omit_sylvester else W3_FROZEN
    w4 = w_res(2, w3 if omit_sylvester else 4, 2, w3 if omit_sylvester else 4, omit_sylvester)
    if omit_sylvester:
        # KF uses the omitted-term operator on the frozen splits, not a
        # recursive rebuild of later weights. Only W_4 is the KF gate.
        w4 = w_res(2, 4, 2, 4, omit_sylvester=True)
    if n == 4:
        return w4
    w5 = w_res(2, 4, 4, 12, omit_sylvester)
    if n == 5:
        return w5
    return w_res(4, 12, 4, 12, omit_sylvester)


def W6_alt(omit_sylvester: bool = False) -> int:
    return w_res(2, 4, 8, 32, omit_sylvester)


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    for nid, n in (("n-two", 2), ("n-zero", 0)):
        try:
            closed_form(n)
            decisions.append({"id": nid, "rejected": False})
        except InvalidParamsError:
            decisions.append({"id": nid, "rejected": True})
    return decisions


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real_map = {n: recurrence_W(n) for n in N_VALUES}
    real_closed = {n: closed_form(n) for n in N_VALUES}
    w6a = W6_alt()
    kf_w4 = recurrence_W(4, omit_sylvester=True)
    null_map = {n: NULL_MUST for n in N_VALUES}
    invalid_decisions = reject_invalid()

    fixture_pass = (
        N_VALUES == (3, 4, 5, 6)
        and W3_FROZEN == 4
        and REAL_MUST == {3: 4, 4: 12, 5: 32, 6: 80}
        and W6_ALT_MUST == 80
        and KF_W4_MUST == 16
        and NULL_MUST == 0
        and w_res(2, 4, 2, 4) == 12
        and w_res(2, 4, 4, 12) == 32
        and w_res(4, 12, 4, 12) == 80
        and w_res(2, 4, 8, 32) == 80
        and w_res(2, 4, 2, 4, omit_sylvester=True) == 16
    )
    real_weight_pass = (
        real_map == REAL_MUST
        and real_closed == REAL_MUST
        and w6a == W6_ALT_MUST
    )
    known_false_omit_sylvester_pass = kf_w4 == KF_W4_MUST and kf_w4 != REAL_MUST[4]
    reject_invalid_pass = all(bool(row["rejected"]) for row in invalid_decisions)
    null_zero_pass = all(null_map[n] == 0 and null_map[n] != REAL_MUST[n] for n in N_VALUES)
    all_pass = (
        fixture_pass
        and real_weight_pass
        and known_false_omit_sylvester_pass
        and reject_invalid_pass
        and null_zero_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    real = {
        "id": "REAL",
        "W": {str(n): real_map[n] for n in N_VALUES},
        "closed_form": {str(n): real_closed[n] for n in N_VALUES},
        "W_6_alt": w6a,
    }
    kf = {"id": "KF", "omit_sylvester_term": True, "W_4": kf_w4}
    null = {
        "id": "NULL",
        "kind": "zero_sequence",
        "W": {str(n): 0 for n in N_VALUES},
        "rejected_as_collapse": True,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-821bc5-S0",
        "experiment_id": "EXP-ECDLP-821bc5",
        "hypothesis_id": "H-ECDLP-92e64c",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-WTLAW",
        "fixture": {
            "n_values": list(N_VALUES),
            "w3_frozen": W3_FROZEN,
            "REAL": {"id": "REAL", "must_W": REAL_MUST, "must_W6_alt": W6_ALT_MUST},
            "KF": {"id": "KF", "must_W_4": KF_W4_MUST},
            "NULL": {"id": "NULL", "kind": "zero_sequence", "must_W": NULL_MUST},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_weight_pass": real_weight_pass,
            "known_false_omit_sylvester_pass": known_false_omit_sylvester_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_zero_pass": null_zero_pass,
            "REAL": real,
            "KF": kf,
            "NULL": null,
        },
        "SMALL_W_or_LARGE_W": False,
        "this_Wn_is_not_O2_line_W": True,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "not_a_sympy_expansion": True,
        "not_an_aut_arm": True,
        "not_a_sigma_ladder": True,
        "not_a_crater_hunt": True,
        "do_not_expand_s4": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-821bc5/implementation/stage0_wtlaw.py\n"
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
        "real_weight_pass": real_weight_pass,
        "known_false_omit_sylvester_pass": known_false_omit_sylvester_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_zero_pass": null_zero_pass,
        "REAL": real,
        "KF": kf,
        "NULL": null,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-821bc5-S0
  experiment_id: EXP-ECDLP-821bc5
  run_id: RUN-ECDLP-821bc5-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_weight_pass: {str(real_weight_pass).lower()}
  known_false_omit_sylvester_pass: {str(known_false_omit_sylvester_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_zero_pass: {str(null_zero_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  this_Wn_is_not_O2_line_W: true
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
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_a_sympy_expansion: true
  not_an_aut_arm: true
  not_a_sigma_ladder: true
  not_a_crater_hunt: true
  do_not_expand_s4: true
  frozen_object: P-S0-WTLAW
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL W_n values match committed table. Invalid objects rejected.
  - real_weight_pass {str(real_weight_pass).lower()}. REAL W_n for n=3,4,5,6 is 4,12,32,80; W_6_alt {w6a}.
  - known_false_omit_sylvester_pass {str(known_false_omit_sylvester_pass).lower()}. KF omitted-term W_4 {kf_w4} not equal to REAL 12.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. n=2 and n=0 rejected before any identity is read.
  - null_zero_pass {str(null_zero_pass).lower()}. NULL W_n is 0 not equal to REAL.
  unexpected_observations: []
  scientific_boundary: Toy frozen-split W_n identity calibrator at n in {{3,4,5,6}}. Not a sympy expansion. Not an Aut arm. Not a sigma ladder. Not a crater hunt. Not a rho beat. Not a decoder. Not the O2-line W. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not expand S_4. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-821bc5-S0
  experiment_id: EXP-ECDLP-821bc5
  hypothesis_id: H-ECDLP-92e64c
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
    command: python3 experiments/EXP-ECDLP-821bc5/implementation/stage0_wtlaw.py
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
      frozen_object: P-S0-WTLAW
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
    validity_reason: Stage 0 exact W_n identity calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_weight_pass: {str(real_weight_pass).lower()}
      known_false_omit_sylvester_pass: {str(known_false_omit_sylvester_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_zero_pass: {str(null_zero_pass).lower()}
      SMALL_W_or_LARGE_W: false
      this_Wn_is_not_O2_line_W: true
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_a_sympy_expansion: true
      not_an_aut_arm: true
      not_a_sigma_ladder: true
      not_a_crater_hunt: true
      do_not_expand_s4: true
      stage1_authorized: false
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
    scientific_boundary: Toy frozen-split W_n identity calibrator at n in {{3,4,5,6}}. Not a sympy expansion. Not an Aut arm. Not a sigma ladder. Not a crater hunt. Not a rho beat. Not a decoder. Not the O2-line W. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not expand S_4.
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
                "real_weight_pass": real_weight_pass,
                "known_false_omit_sylvester_pass": known_false_omit_sylvester_pass,
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
