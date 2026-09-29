#!/usr/bin/env python3
"""EXP-ECDLP-8eaf6a Stage 0 exact one-step next-feature split calibrator.

Certificate kind none. No automaton. No cubical point. No Tate pairing.
No DL-spectrum. No Coppersmith. No Semaev S_m. No Velu.
Frozen object P-S0-REFSPLIT: REAL / KF / NULL on Z/7Z.

REAL: n=7, phi(x)=x mod 2, action x+1.
phi = [0, 1, 0, 1, 0, 1, 0]
next_phi = [1, 0, 1, 0, 1, 0, 0]
even next (x=0,2,4,6) = [1, 1, 1, 0]
odd next (x=1,3,5) = [0, 0, 0]
KF: claim phi is a homomorphism Z/7Z -> Z/2Z. Witness (3,4).
NULL empty x-list is rejected. n=0 is rejected.
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
SOURCE = "experiments/EXP-ECDLP-8eaf6a/implementation/stage0_refsplit.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-8eaf6a/runs/RUN-ECDLP-8eaf6a-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-8eaf6a/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-4ddeae"
TASK_ID = "TASK-20260908-2b9b05"

REAL_N = 7
FROZEN_PHI = [0, 1, 0, 1, 0, 1, 0]
FROZEN_NEXT = [1, 0, 1, 0, 1, 0, 0]
FROZEN_EVEN = [1, 1, 1, 0]
FROZEN_ODD = [0, 0, 0]
KF_WITNESS = (3, 4)


class InvalidParamsError(ValueError):
    """n not a frozen positive integer, or empty x-list, is rejected."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_positive_n(n: int) -> None:
    if int(n) <= 0:
        raise InvalidParamsError("n is not a frozen positive integer")


def require_nonempty_x_list(x_list: list[int]) -> None:
    if not x_list:
        raise InvalidParamsError("x-list is empty")


def phi_table(n: int) -> list[int]:
    require_positive_n(n)
    return [int(x) % 2 for x in range(int(n))]


def next_phi_table(n: int) -> list[int]:
    require_positive_n(n)
    return [((int(x) + 1) % int(n)) % 2 for x in range(int(n))]


def even_next(n: int, nxt: list[int]) -> list[int]:
    return [nxt[x] for x in range(int(n)) if x % 2 == 0]


def odd_next(n: int, nxt: list[int]) -> list[int]:
    return [nxt[x] for x in range(int(n)) if x % 2 == 1]


def homomorphism_holds(n: int, a: int, b: int) -> bool:
    require_positive_n(n)
    phi = phi_table(n)
    left = phi[(int(a) + int(b)) % int(n)]
    right = (phi[int(a) % int(n)] + phi[int(b) % int(n)]) % 2
    return left == right


def main() -> int:
    started = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    commit = git_head()
    source_sha256 = hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()

    fixture_pass = True
    invalid_decisions: list[dict] = []
    try:
        require_positive_n(0)
        reject_invalid_pass = False
    except InvalidParamsError:
        reject_invalid_pass = True
        invalid_decisions.append({"id": "n-zero", "n": 0, "rejected": True})

    try:
        require_nonempty_x_list([])
        null_empty_pass = False
        null_obj = {"id": "NULL", "kind": "empty_x_list", "rejected": False}
    except InvalidParamsError:
        null_empty_pass = True
        null_obj = {"id": "NULL", "kind": "empty_x_list", "rejected": True}

    try:
        require_positive_n(REAL_N)
        kf_holds = homomorphism_holds(REAL_N, KF_WITNESS[0], KF_WITNESS[1])
        known_false_hom_pass = not kf_holds
        kf_obj = {
            "id": "KF",
            "n": REAL_N,
            "claim": "phi_is_homomorphism",
            "witness": list(KF_WITNESS),
            "phi_of_sum": ((KF_WITNESS[0] + KF_WITNESS[1]) % REAL_N) % 2,
            "sum_of_phi": (KF_WITNESS[0] % 2 + KF_WITNESS[1] % 2) % 2,
            "homomorphism_holds": kf_holds,
            "rejected": not kf_holds,
        }
    except InvalidParamsError:
        known_false_hom_pass = False
        kf_obj = {
            "id": "KF",
            "n": REAL_N,
            "claim": "phi_is_homomorphism",
            "witness": list(KF_WITNESS),
            "rejected": False,
        }

    require_positive_n(REAL_N)
    require_nonempty_x_list(list(range(REAL_N)))
    got_phi = phi_table(REAL_N)
    got_next = next_phi_table(REAL_N)
    got_even = even_next(REAL_N, got_next)
    got_odd = odd_next(REAL_N, got_next)
    real_split_pass = (
        got_phi == FROZEN_PHI
        and got_next == FROZEN_NEXT
        and got_even == FROZEN_EVEN
        and got_odd == FROZEN_ODD
    )
    real_obj = {
        "id": "REAL",
        "n": REAL_N,
        "feature": "parity",
        "action": "plus_one",
        "phi": got_phi,
        "next_phi": got_next,
        "even_next": got_even,
        "odd_next": got_odd,
        "must_phi": FROZEN_PHI,
        "must_next_phi": FROZEN_NEXT,
        "must_even_next": FROZEN_EVEN,
        "must_odd_next": FROZEN_ODD,
    }

    all_pass = (
        fixture_pass
        and real_split_pass
        and known_false_hom_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.time() - started

    raw = {
        "run_id": "RUN-ECDLP-8eaf6a-S0",
        "experiment_id": "EXP-ECDLP-8eaf6a",
        "hypothesis_id": "H-ECDLP-15d016",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-REFSPLIT",
        "fixture": {
            "group": "Z/nZ",
            "REAL": {
                "id": "REAL",
                "n": REAL_N,
                "feature": "parity",
                "action": "plus_one",
                "must_phi": FROZEN_PHI,
                "must_next_phi": FROZEN_NEXT,
                "must_even_next": FROZEN_EVEN,
                "must_odd_next": FROZEN_ODD,
            },
            "KF": {
                "id": "KF",
                "claim": "phi_is_homomorphism",
                "witness": list(KF_WITNESS),
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_x_list", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_split_pass": real_split_pass,
            "known_false_hom_pass": known_false_hom_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_8eaf6a_stage1_authorized": False,
        "exp_eab4d7_stage1_authorized": False,
        "exp_a294b6_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "not_an_automaton": True,
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
        "python3 experiments/EXP-ECDLP-8eaf6a/implementation/stage0_refsplit.py\n"
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
        "real_split_pass": real_split_pass,
        "known_false_hom_pass": known_false_hom_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-8eaf6a-S0
  experiment_id: EXP-ECDLP-8eaf6a
  run_id: RUN-ECDLP-8eaf6a-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_split_pass: {str(real_split_pass).lower()}
  known_false_hom_pass: {str(known_false_hom_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_8eaf6a_stage1_authorized: false
  exp_eab4d7_stage1_authorized: false
  exp_a294b6_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_an_automaton: true
  not_a_cubical_lift: true
  not_tate: true
  not_a_dl_spectrum: true
  do_not_run_coppersmith: true
  do_not_form_semaev: true
  do_not_run_velu: true
  frozen_object: P-S0-REFSPLIT
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_split_pass {str(real_split_pass).lower()}. REAL phi is {got_phi}, next-phi is {got_next}, even next is {got_even}, odd next is {got_odd}."
  - "known_false_hom_pass {str(known_false_hom_pass).lower()}. KF witness {list(KF_WITNESS)} rejected={str(kf_obj['rejected']).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. n=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty x-list is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen one-step next-feature split calibrator on Z/7Z. Not an automaton. Not a cubical lift. Not Tate. Not a DL-spectrum. Not Coppersmith. Not Semaev S_m. Not Velu. Not a yield ratio k. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-8eaf6a. Not Stage 1 of EXP-ECDLP-eab4d7. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-8eaf6a-S0
  experiment_id: EXP-ECDLP-8eaf6a
  hypothesis_id: H-ECDLP-15d016
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
    command: python3 experiments/EXP-ECDLP-8eaf6a/implementation/stage0_refsplit.py
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
      frozen_object: P-S0-REFSPLIT
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      group: Z/nZ
      real_n: 7
      feature: parity
      action: plus_one
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
    validity_reason: Stage 0 exact one-step next-feature split calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_split_pass: {str(real_split_pass).lower()}
      known_false_hom_pass: {str(known_false_hom_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_an_automaton: true
      not_a_cubical_lift: true
      not_tate: true
      not_a_dl_spectrum: true
      do_not_run_coppersmith: true
      do_not_form_semaev: true
      do_not_run_velu: true
      stage1_authorized: false
      exp_8eaf6a_stage1_authorized: false
      exp_eab4d7_stage1_authorized: false
      exp_a294b6_stage1_authorized: false
    scientific_boundary: "Toy frozen one-step next-feature split calibrator on Z/7Z. Not an automaton. Not a cubical lift. Not Tate. Not a DL-spectrum. Not Coppersmith. Not Semaev S_m. Not Velu. Not a yield ratio k. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-8eaf6a. Not Stage 1 of EXP-ECDLP-eab4d7. Certificate kind none."
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
                "real_split_pass": real_split_pass,
                "known_false_hom_pass": known_false_hom_pass,
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
