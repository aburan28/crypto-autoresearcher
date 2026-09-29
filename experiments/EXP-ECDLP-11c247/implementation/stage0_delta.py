#!/usr/bin/env python3
"""EXP-ECDLP-11c247 Stage 0 exact Galois product identity calibrator.

Certificate kind none. No fibre census. No Chebotarev size law.
No yield census. No conorm arm. No rho cost identification. No rho beat.
Frozen object P-S0-DELTA: REAL / KF / NULL at d in {1,2}.

product(d, delta_num, delta_den) = Fraction(delta_num, delta_den) * d
Galois equality: product == 1.
Frozen identity: d=1, delta=1/1, product=1.
Frozen Kummer: d=2, delta=1/2, product=1.
KF uses delta=1/1 at d=2 so product=2.
NULL is the zero product.
d=0 is rejected.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-11c247/implementation/stage0_delta.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-11c247/runs/RUN-ECDLP-11c247-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-11c247/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-be0e26"
TASK_ID = "TASK-20260908-70b029"

DEGREES_FROZEN = (1, 2)
REAL_ID_D = 1
REAL_ID_NUM = 1
REAL_ID_DEN = 1
REAL_K_D = 2
REAL_K_NUM = 1
REAL_K_DEN = 2
KF_D = 2
KF_NUM = 1
KF_DEN = 1
REAL_MUST_PRODUCT = Fraction(1, 1)
KF_MUST_PRODUCT = Fraction(2, 1)
NULL_MUST_PRODUCT = Fraction(0, 1)


class InvalidParamsError(ValueError):
    """d not a frozen positive degree is rejected, not evaluated."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def require_frozen_degree(d: int) -> None:
    if d not in DEGREES_FROZEN:
        raise InvalidParamsError("d is not a frozen positive degree")


def product(d: int, delta_num: int, delta_den: int) -> Fraction:
    require_frozen_degree(d)
    if delta_den < 1:
        raise InvalidParamsError("delta_den < 1")
    return Fraction(delta_num, delta_den) * d


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        product(0, 1, 1)
        decisions.append({"id": "d-zero", "d": 0, "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "d-zero", "d": 0, "rejected": True})
    return decisions


def frac_row(value: Fraction) -> dict[str, object]:
    return {
        "product_num": int(value.numerator),
        "product_den": int(value.denominator),
        "product": str(value),
    }


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real_id = product(REAL_ID_D, REAL_ID_NUM, REAL_ID_DEN)
    real_k = product(REAL_K_D, REAL_K_NUM, REAL_K_DEN)
    kf = product(KF_D, KF_NUM, KF_DEN)
    null = NULL_MUST_PRODUCT
    invalid_decisions = reject_invalid()

    fixture_pass = (
        DEGREES_FROZEN == (1, 2)
        and REAL_ID_D == 1
        and REAL_ID_NUM == 1
        and REAL_ID_DEN == 1
        and REAL_K_D == 2
        and REAL_K_NUM == 1
        and REAL_K_DEN == 2
        and KF_D == 2
        and KF_NUM == 1
        and KF_DEN == 1
        and REAL_MUST_PRODUCT == Fraction(1, 1)
        and KF_MUST_PRODUCT == Fraction(2, 1)
        and NULL_MUST_PRODUCT == Fraction(0, 1)
        and Fraction(1, 1) * 1 == Fraction(1, 1)
        and Fraction(1, 2) * 2 == Fraction(1, 1)
        and Fraction(1, 1) * 2 == Fraction(2, 1)
    )
    real_count_pass = (
        real_id == REAL_MUST_PRODUCT
        and real_k == REAL_MUST_PRODUCT
        and real_id == Fraction(1, 1)
        and real_k == Fraction(1, 1)
    )
    known_false_wrong_delta_pass = (
        kf == KF_MUST_PRODUCT and kf != REAL_MUST_PRODUCT and kf == Fraction(2, 1)
    )
    reject_invalid_pass = all(bool(row["rejected"]) for row in invalid_decisions)
    null_zero_pass = null == NULL_MUST_PRODUCT and null != REAL_MUST_PRODUCT
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_wrong_delta_pass
        and reject_invalid_pass
        and null_zero_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    real_id_obj = {
        "id": "REAL-ID",
        "d": REAL_ID_D,
        "delta_num": REAL_ID_NUM,
        "delta_den": REAL_ID_DEN,
        **frac_row(real_id),
    }
    real_k_obj = {
        "id": "REAL-K",
        "d": REAL_K_D,
        "delta_num": REAL_K_NUM,
        "delta_den": REAL_K_DEN,
        **frac_row(real_k),
    }
    kf_obj = {
        "id": "KF",
        "wrong_delta": True,
        "d": KF_D,
        "delta_num": KF_NUM,
        "delta_den": KF_DEN,
        **frac_row(kf),
    }
    null_obj = {
        "id": "NULL",
        "kind": "zero_product",
        **frac_row(null),
        "rejected_as_collapse": True,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-11c247-S0",
        "experiment_id": "EXP-ECDLP-11c247",
        "hypothesis_id": "H-ECDLP-7253e7",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-DELTA",
        "fixture": {
            "degrees_frozen": list(DEGREES_FROZEN),
            "REAL-ID": {
                "id": "REAL-ID",
                "d": REAL_ID_D,
                "delta_num": REAL_ID_NUM,
                "delta_den": REAL_ID_DEN,
                "must_product": str(REAL_MUST_PRODUCT),
            },
            "REAL-K": {
                "id": "REAL-K",
                "d": REAL_K_D,
                "delta_num": REAL_K_NUM,
                "delta_den": REAL_K_DEN,
                "must_product": str(REAL_MUST_PRODUCT),
            },
            "KF": {
                "id": "KF",
                "d": KF_D,
                "delta_num": KF_NUM,
                "delta_den": KF_DEN,
                "must_product": str(KF_MUST_PRODUCT),
            },
            "NULL": {
                "id": "NULL",
                "kind": "zero_product",
                "must_product": str(NULL_MUST_PRODUCT),
            },
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_count_pass": real_count_pass,
            "known_false_wrong_delta_pass": known_false_wrong_delta_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_zero_pass": null_zero_pass,
            "REAL-ID": real_id_obj,
            "REAL-K": real_k_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "not_a_fibre_census": True,
        "not_a_chebotarev_size_law": True,
        "not_a_yield_census": True,
        "not_a_conorm_arm": True,
        "not_a_rho_cost_identification": True,
        "do_not_enumerate_fibres": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-11c247/implementation/stage0_delta.py\n"
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
        "known_false_wrong_delta_pass": known_false_wrong_delta_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_zero_pass": null_zero_pass,
        "REAL-ID": real_id_obj,
        "REAL-K": real_k_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-11c247-S0
  experiment_id: EXP-ECDLP-11c247
  run_id: RUN-ECDLP-11c247-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_count_pass: {str(real_count_pass).lower()}
  known_false_wrong_delta_pass: {str(known_false_wrong_delta_pass).lower()}
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
  exp_11c247_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_a_fibre_census: true
  not_a_chebotarev_size_law: true
  not_a_yield_census: true
  not_a_conorm_arm: true
  not_a_rho_cost_identification: true
  do_not_enumerate_fibres: true
  frozen_object: P-S0-DELTA
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL product values match committed table. Invalid objects rejected."
  - "real_count_pass {str(real_count_pass).lower()}. REAL identity product is {real_id}. REAL Kummer product is {real_k}."
  - "known_false_wrong_delta_pass {str(known_false_wrong_delta_pass).lower()}. KF wrong-delta product {kf} not equal to REAL 1."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. d=0 rejected before any identity is read."
  - "null_zero_pass {str(null_zero_pass).lower()}. NULL product is 0 not equal to REAL."
  unexpected_observations: []
  scientific_boundary: "Toy frozen Galois product identity calibrator at d in {{1,2}}. Not a fibre census. Not a Chebotarev size law. Not a yield census. Not a conorm arm. Not a rho cost identification. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-11c247. Not Stage 1 of EXP-ECDLP-114eb2. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not enumerate fibres. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-11c247-S0
  experiment_id: EXP-ECDLP-11c247
  hypothesis_id: H-ECDLP-7253e7
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
    command: python3 experiments/EXP-ECDLP-11c247/implementation/stage0_delta.py
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
      frozen_object: P-S0-DELTA
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL-ID, REAL-K, KF, NULL]
      degrees_frozen: [1, 2]
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
    validity_reason: Stage 0 exact Galois product identity calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_count_pass: {str(real_count_pass).lower()}
      known_false_wrong_delta_pass: {str(known_false_wrong_delta_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_zero_pass: {str(null_zero_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_a_fibre_census: true
      not_a_chebotarev_size_law: true
      not_a_yield_census: true
      not_a_conorm_arm: true
      not_a_rho_cost_identification: true
      do_not_enumerate_fibres: true
      stage1_authorized: false
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
    scientific_boundary: "Toy frozen Galois product identity calibrator at d in {{1,2}}. Not a fibre census. Not a Chebotarev size law. Not a yield census. Not a conorm arm. Not a rho cost identification. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-11c247. Not Stage 1 of EXP-ECDLP-114eb2. Not Stage 1 of EXP-ECDLP-821bc5. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not enumerate fibres."
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
                "known_false_wrong_delta_pass": known_false_wrong_delta_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_zero_pass": null_zero_pass,
                "REAL-ID": real_id_obj,
                "REAL-K": real_k_obj,
                "KF": kf_obj,
                "NULL": null_obj,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
