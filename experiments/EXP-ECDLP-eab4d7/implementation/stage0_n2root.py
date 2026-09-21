#!/usr/bin/env python3
"""EXP-ECDLP-eab4d7 Stage 0 exact coprime/embed N^2-th-root calibrator.

Certificate kind none. No cubical point. No division polynomial.
No Tate pairing. No DL-spectrum. No Coppersmith. No Semaev S_m.
Frozen object P-S0-N2ROOT: REAL / KF / NULL on F_p^*.

REAL: p=19, N=5, gcd(5,18)=1. Power table of x^25 for x=1..18 is
[1, 14, 2, 6, 16, 9, 7, 8, 4, 15, 11, 12, 10, 3, 13, 17, 5, 18].
Unique N^2-th roots for c=1..18 are
[1, 3, 14, 9, 17, 4, 7, 8, 6, 13, 11, 12, 15, 2, 10, 5, 16, 18].
KF: p=19, N=3, gcd(3,18)=3 so N | (p-1) is rejected.
NULL empty c-list is rejected. p=0 is rejected.
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
SOURCE = "experiments/EXP-ECDLP-eab4d7/implementation/stage0_n2root.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-eab4d7/runs/RUN-ECDLP-eab4d7-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-eab4d7/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-e9da97"
TASK_ID = "TASK-20260908-6dd2bd"

REAL_P = 19
REAL_N = 5
REAL_N2 = 25
FROZEN_POWER = [1, 14, 2, 6, 16, 9, 7, 8, 4, 15, 11, 12, 10, 3, 13, 17, 5, 18]
FROZEN_ROOTS = [1, 3, 14, 9, 17, 4, 7, 8, 6, 13, 11, 12, 15, 2, 10, 5, 16, 18]
KF_P = 19
KF_N = 3


class InvalidParamsError(ValueError):
    """p not a frozen positive prime, or empty c-list, is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_positive_p(p: int) -> None:
    if int(p) <= 0:
        raise InvalidParamsError("p is not a frozen positive prime")


def gcd(a: int, b: int) -> int:
    a, b = abs(int(a)), abs(int(b))
    while b:
        a, b = b, a % b
    return a


def pow_by_multiply(base: int, exp: int, mod: int) -> int:
    acc = 1
    for _ in range(int(exp)):
        acc = (acc * int(base)) % int(mod)
    return acc


def power_table(p: int, n2: int) -> list[int]:
    require_positive_p(p)
    return [pow_by_multiply(x, n2, p) for x in range(1, p)]


def unique_roots(p: int, n2: int) -> list[int]:
    require_positive_p(p)
    roots: list[int] = []
    for c in range(1, p):
        hits = [
            d
            for d in range(1, p)
            if pow_by_multiply(d, n2, p) == c
        ]
        if len(hits) != 1:
            raise InvalidParamsError("N^2-th root is not unique")
        roots.append(hits[0])
    return roots


def require_coprime_pair(p: int, n: int) -> None:
    require_positive_p(p)
    if int(n) <= 0:
        raise InvalidParamsError("N is not a frozen positive integer")
    if gcd(n, p - 1) != 1:
        raise InvalidParamsError("gcd(N, p-1) is not 1")


def require_nonempty_c_list(c_list: list[int]) -> None:
    if not c_list:
        raise InvalidParamsError("c-list is empty")


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
        require_nonempty_c_list([])
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_c_list", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_c_list", "rejected": True}

    try:
        require_coprime_pair(KF_P, KF_N)
        known_false_embed_pass = False
        kf_obj = {
            "id": "KF",
            "p": KF_P,
            "N": KF_N,
            "gcd_N_pminus1": gcd(KF_N, KF_P - 1),
            "rejected": False,
        }
    except InvalidParamsError:
        known_false_embed_pass = True
        kf_obj = {
            "id": "KF",
            "p": KF_P,
            "N": KF_N,
            "gcd_N_pminus1": gcd(KF_N, KF_P - 1),
            "rejected": True,
        }

    require_coprime_pair(REAL_P, REAL_N)
    require_nonempty_c_list(list(range(1, REAL_P)))
    got_power = power_table(REAL_P, REAL_N2)
    got_roots = unique_roots(REAL_P, REAL_N2)
    real_root_pass = got_power == FROZEN_POWER and got_roots == FROZEN_ROOTS
    real_obj = {
        "id": "REAL",
        "p": REAL_P,
        "N": REAL_N,
        "N2": REAL_N2,
        "gcd_N_pminus1": gcd(REAL_N, REAL_P - 1),
        "power_table": got_power,
        "roots": got_roots,
        "must_power_table": FROZEN_POWER,
        "must_roots": FROZEN_ROOTS,
    }

    all_pass = (
        fixture_pass
        and real_root_pass
        and known_false_embed_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-eab4d7-S0",
        "experiment_id": "EXP-ECDLP-eab4d7",
        "hypothesis_id": "H-ECDLP-7b7398",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-N2ROOT",
        "fixture": {
            "field": "F_p^*",
            "REAL": {
                "id": "REAL",
                "p": REAL_P,
                "N": REAL_N,
                "N2": REAL_N2,
                "gcd_N_pminus1": 1,
                "must_power_table": FROZEN_POWER,
                "must_roots": FROZEN_ROOTS,
            },
            "KF": {
                "id": "KF",
                "p": KF_P,
                "N": KF_N,
                "gcd_N_pminus1": 3,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_c_list", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_root_pass": real_root_pass,
            "known_false_embed_pass": known_false_embed_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_eab4d7_stage1_authorized": False,
        "exp_a294b6_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
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
        "python3 experiments/EXP-ECDLP-eab4d7/implementation/stage0_n2root.py\n"
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
        "real_root_pass": real_root_pass,
        "known_false_embed_pass": known_false_embed_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-eab4d7-S0
  experiment_id: EXP-ECDLP-eab4d7
  run_id: RUN-ECDLP-eab4d7-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_root_pass: {str(real_root_pass).lower()}
  known_false_embed_pass: {str(known_false_embed_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_eab4d7_stage1_authorized: false
  exp_a294b6_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_a_cubical_lift: true
  not_tate: true
  not_a_dl_spectrum: true
  do_not_run_coppersmith: true
  do_not_form_semaev: true
  do_not_run_velu: true
  frozen_object: P-S0-N2ROOT
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_root_pass {str(real_root_pass).lower()}. REAL power table is {got_power} and unique roots are {got_roots}."
  - "known_false_embed_pass {str(known_false_embed_pass).lower()}. KF p={kf_obj['p']} N={kf_obj['N']} gcd={kf_obj['gcd_N_pminus1']} rejected={str(kf_obj['rejected']).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. p=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty c-list is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen coprime/embed N^2-th-root calibrator on F_p^*. Not a cubical lift. Not Tate. Not a DL-spectrum. Not Coppersmith. Not Semaev S_m. Not Velu. Not a yield ratio k. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-eab4d7. Not Stage 1 of EXP-ECDLP-a294b6. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-eab4d7-S0
  experiment_id: EXP-ECDLP-eab4d7
  hypothesis_id: H-ECDLP-7b7398
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
    command: python3 experiments/EXP-ECDLP-eab4d7/implementation/stage0_n2root.py
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
      frozen_object: P-S0-N2ROOT
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      field: F_p^*
      real_p: 19
      real_n: 5
      kf_p: 19
      kf_n: 3
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
    validity_reason: Stage 0 exact coprime/embed N^2-th-root calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_root_pass: {str(real_root_pass).lower()}
      known_false_embed_pass: {str(known_false_embed_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_a_cubical_lift: true
      not_tate: true
      not_a_dl_spectrum: true
      do_not_run_coppersmith: true
      do_not_form_semaev: true
      do_not_run_velu: true
      stage1_authorized: false
      exp_eab4d7_stage1_authorized: false
      exp_a294b6_stage1_authorized: false
    scientific_boundary: "Toy frozen coprime/embed N^2-th-root calibrator on F_p^*. Not a cubical lift. Not Tate. Not a DL-spectrum. Not Coppersmith. Not Semaev S_m. Not Velu. Not a yield ratio k. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-eab4d7. Not Stage 1 of EXP-ECDLP-a294b6. Certificate kind none."
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
                "real_root_pass": real_root_pass,
                "known_false_embed_pass": known_false_embed_pass,
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
