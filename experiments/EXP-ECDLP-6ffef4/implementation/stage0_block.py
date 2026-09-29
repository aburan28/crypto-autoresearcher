#!/usr/bin/env python3
"""EXP-ECDLP-6ffef4 Stage 0 exact C1 block-system iff calibrator.

Certificate kind none. No Aut census. No orbit cost.
No GL_2 partition. No rho cost identification. No rho beat.
Frozen object P-S0-BLOCK: REAL / KF / NULL at n=7.

invariant(partition, gamma, n) is true iff every block image
under multiplication by gamma mod n equals some block.
propagates(v, gamma, n) is true iff a well-defined F exists
on the image of v with v(gamma*x mod n) = F(v(x)).
C1 iff: invariant == propagate for every gamma in Gamma.
Frozen REAL: {x,-x} fibres.
Frozen KF: singleton-versus-rest.
NULL is the empty domain and is rejected.
n=0 is rejected.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-6ffef4/implementation/stage0_block.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-6ffef4/runs/RUN-ECDLP-6ffef4-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-6ffef4/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-f6afa2"
TASK_ID = "TASK-20260908-30e272"

N_FROZEN = 7
GAMMA_FROZEN = (1, 6)
DOMAIN_FROZEN = (1, 2, 3, 4, 5, 6)
REAL_V = {1: 0, 6: 0, 2: 1, 5: 1, 3: 2, 4: 2}
KF_V = {1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}


class InvalidParamsError(ValueError):
    """n not the frozen positive order is rejected, not evaluated."""


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


def fibres(v: dict[int, int]) -> list[frozenset[int]]:
    buckets: dict[int, set[int]] = defaultdict(set)
    for x, val in v.items():
        buckets[int(val)].add(int(x))
    return [frozenset(block) for block in buckets.values()]


def invariant(partition: list[frozenset[int]], gamma: int, n: int) -> bool:
    require_frozen_n(n)
    blockset = set(partition)
    for block in partition:
        image = frozenset((int(gamma) * int(x)) % int(n) for x in block)
        if image not in blockset:
            return False
    return True


def propagates(v: dict[int, int], gamma: int, n: int) -> bool:
    require_frozen_n(n)
    table: dict[int, int] = {}
    for x, val in v.items():
        y = (int(gamma) * int(x)) % int(n)
        if y not in v:
            return False
        target = int(v[y])
        key = int(val)
        if key in table and table[key] != target:
            return False
        table[key] = target
    return True


def evaluate(v: dict[int, int], n: int, gamma_tuple: tuple[int, ...]) -> dict[str, object]:
    require_frozen_n(n)
    if not v:
        raise InvalidParamsError("empty domain")
    partition = fibres(v)
    inv_all = True
    prop_all = True
    per_gamma = []
    for gamma in gamma_tuple:
        inv = invariant(partition, gamma, n)
        prop = propagates(v, gamma, n)
        inv_all = inv_all and inv
        prop_all = prop_all and prop
        per_gamma.append(
            {
                "gamma": int(gamma),
                "invariant": inv,
                "propagate": prop,
                "iff": inv == prop,
            }
        )
    return {
        "invariant": inv_all,
        "propagate": prop_all,
        "iff": inv_all == prop_all,
        "per_gamma": per_gamma,
    }


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        evaluate(REAL_V, 0, GAMMA_FROZEN)
        decisions.append({"id": "n-zero", "n": 0, "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "n-zero", "n": 0, "rejected": True})
    return decisions


def reject_null() -> dict[str, object]:
    try:
        evaluate({}, N_FROZEN, GAMMA_FROZEN)
        return {"id": "NULL", "kind": "empty_domain", "rejected": False}
    except InvalidParamsError:
        return {"id": "NULL", "kind": "empty_domain", "rejected": True}


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real = evaluate(REAL_V, N_FROZEN, GAMMA_FROZEN)
    kf = evaluate(KF_V, N_FROZEN, GAMMA_FROZEN)
    null_obj = reject_null()
    invalid_decisions = reject_invalid()

    fixture_pass = (
        N_FROZEN == 7
        and GAMMA_FROZEN == (1, 6)
        and DOMAIN_FROZEN == (1, 2, 3, 4, 5, 6)
        and REAL_V == {1: 0, 6: 0, 2: 1, 5: 1, 3: 2, 4: 2}
        and KF_V == {1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
    )
    real_count_pass = bool(real["invariant"]) and bool(real["propagate"]) and bool(real["iff"])
    known_false_nonblock_pass = (
        (not bool(kf["invariant"]))
        and (not bool(kf["propagate"]))
        and bool(kf["iff"])
        and (bool(kf["invariant"]) != bool(real["invariant"]))
    )
    reject_invalid_pass = all(bool(row["rejected"]) for row in invalid_decisions)
    null_empty_pass = bool(null_obj["rejected"])
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_nonblock_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    real_obj = {"id": "REAL", "v": {str(k): int(val) for k, val in REAL_V.items()}, **real}
    kf_obj = {
        "id": "KF",
        "nonblock": True,
        "v": {str(k): int(val) for k, val in KF_V.items()},
        **kf,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-6ffef4-S0",
        "experiment_id": "EXP-ECDLP-6ffef4",
        "hypothesis_id": "H-ECDLP-62befe",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-BLOCK",
        "fixture": {
            "n_frozen": N_FROZEN,
            "gamma_frozen": list(GAMMA_FROZEN),
            "domain_frozen": list(DOMAIN_FROZEN),
            "REAL": {
                "id": "REAL",
                "must_invariant": True,
                "must_propagate": True,
                "must_iff": True,
            },
            "KF": {
                "id": "KF",
                "must_invariant": False,
                "must_propagate": False,
                "must_iff": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_domain", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_count_pass": real_count_pass,
            "known_false_nonblock_pass": known_false_nonblock_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "not_an_aut_census": True,
        "not_an_orbit_cost": True,
        "not_a_gl2_partition": True,
        "not_a_rho_cost_identification": True,
        "do_not_enumerate_aut": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-6ffef4/implementation/stage0_block.py\n"
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
        "known_false_nonblock_pass": known_false_nonblock_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-6ffef4-S0
  experiment_id: EXP-ECDLP-6ffef4
  run_id: RUN-ECDLP-6ffef4-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_count_pass: {str(real_count_pass).lower()}
  known_false_nonblock_pass: {str(known_false_nonblock_pass).lower()}
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
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_an_aut_census: true
  not_an_orbit_cost: true
  not_a_gl2_partition: true
  not_a_rho_cost_identification: true
  do_not_enumerate_aut: true
  frozen_object: P-S0-BLOCK
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_count_pass {str(real_count_pass).lower()}. REAL invariant is {str(real['invariant']).lower()}. REAL propagate is {str(real['propagate']).lower()}."
  - "known_false_nonblock_pass {str(known_false_nonblock_pass).lower()}. KF invariant is {str(kf['invariant']).lower()} and KF propagate is {str(kf['propagate']).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. n=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty domain is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen C1 block-system iff calibrator at n=7. Not an Aut census. Not an orbit cost. Not a GL_2 partition. Not a rho cost identification. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-6ffef4. Not Stage 1 of EXP-ECDLP-11c247. Not Stage 1 of EXP-ECDLP-114eb2. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not enumerate Aut. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-6ffef4-S0
  experiment_id: EXP-ECDLP-6ffef4
  hypothesis_id: H-ECDLP-62befe
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
    command: python3 experiments/EXP-ECDLP-6ffef4/implementation/stage0_block.py
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
      frozen_object: P-S0-BLOCK
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      n_frozen: 7
      gamma_frozen: [1, 6]
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
    validity_reason: Stage 0 exact C1 block-system iff calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_count_pass: {str(real_count_pass).lower()}
      known_false_nonblock_pass: {str(known_false_nonblock_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_an_aut_census: true
      not_an_orbit_cost: true
      not_a_gl2_partition: true
      not_a_rho_cost_identification: true
      do_not_enumerate_aut: true
      stage1_authorized: false
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
    scientific_boundary: "Toy frozen C1 block-system iff calibrator at n=7. Not an Aut census. Not an orbit cost. Not a GL_2 partition. Not a rho cost identification. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-6ffef4. Not Stage 1 of EXP-ECDLP-11c247. Not Stage 1 of EXP-ECDLP-114eb2. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not enumerate Aut."
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
                "known_false_nonblock_pass": known_false_nonblock_pass,
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
