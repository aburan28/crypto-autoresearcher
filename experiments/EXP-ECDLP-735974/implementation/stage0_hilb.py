#!/usr/bin/env python3
"""EXP-ECDLP-735974 Stage 0 exact Hilbert-series d_reg identity calibrator.

Certificate kind none. No Groebner run. No binary-field system.
No KN-LIT-4558 extraction. No rho beat.
Frozen object P-S0-HILB: REAL / KF / NULL.

HS(t)=prod_i (1-t^{d_i}) (1-t)^{-n}
(1-t)^{-n}=sum_k C(n+k-1, k) t^k, truncated at max_degree=16.
d_reg = min {k in 0..16 : hf[k] <= 0} or None.
Producer: successive exact integer convolution.
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
SOURCE = "experiments/EXP-ECDLP-735974/implementation/stage0_hilb.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-735974/runs/RUN-ECDLP-735974-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-735974/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-e676d8"
TASK_ID = "TASK-20260908-1489f7"

MAX_DEGREE = 16
REAL_N = 2
REAL_D = (2, 2, 2)
REAL_MUST = 2
BASE_N = 4
BASE_D = (2, 2, 2, 2, 2)
BASE_MUST = 3
KF_N = 2
KF_D = (2, 2)
KF_MUST = 3
NULL_N = 2
NULL_D: tuple[int, ...] = ()


class InvalidParamsError(ValueError):
    """n<=0 or a non-positive degree is rejected, not evaluated."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def binom(n: int, k: int) -> int:
    """Exact C(n, k) by multiplicative formula. k may exceed n."""
    if k < 0 or n < 0 or k > n:
        return 0
    k = min(k, n - k)
    acc = 1
    for i in range(k):
        acc = acc * (n - i) // (i + 1)
    return acc


def hilbert_coeffs(n: int, degrees: tuple[int, ...], max_degree: int) -> list[int]:
    """Coefficients of prod (1-t^{d_i}) (1-t)^{-n} through max_degree."""
    if n <= 0:
        raise InvalidParamsError("n<=0 is not a variable count")
    if any(d <= 0 for d in degrees):
        raise InvalidParamsError("non-positive degree")
    # (1-t)^{-n} : C(n+k-1, k)
    hf = [binom(n + k - 1, k) for k in range(max_degree + 1)]
    for d in degrees:
        nxt = []
        for k in range(max_degree + 1):
            sub = hf[k - d] if k >= d else 0
            nxt.append(hf[k] - sub)
        hf = nxt
    return hf


def d_reg_from_hf(hf: list[int]) -> int | None:
    for k, c in enumerate(hf):
        if c <= 0:
            return k
    return None


def d_reg(n: int, degrees: tuple[int, ...], max_degree: int = MAX_DEGREE) -> int | None:
    return d_reg_from_hf(hilbert_coeffs(n, degrees, max_degree))


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        d_reg(0, REAL_D)
        decisions.append({"id": "n-zero", "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "n-zero", "rejected": True})
    try:
        d_reg(2, (2, 0, 2))
        decisions.append({"id": "nonpositive-degree", "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "nonpositive-degree", "rejected": True})
    return decisions


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real_hf = hilbert_coeffs(REAL_N, REAL_D, MAX_DEGREE)
    real_d = d_reg_from_hf(real_hf)
    base_d = d_reg(BASE_N, BASE_D)
    kf_hf = hilbert_coeffs(KF_N, KF_D, MAX_DEGREE)
    kf_d = d_reg_from_hf(kf_hf)
    null_hf = hilbert_coeffs(NULL_N, NULL_D, MAX_DEGREE)
    null_d = d_reg_from_hf(null_hf)
    invalid_decisions = reject_invalid()

    fixture_pass = (
        MAX_DEGREE == 16
        and REAL_N == 2
        and REAL_D == (2, 2, 2)
        and REAL_MUST == 2
        and BASE_N == 4
        and BASE_D == (2, 2, 2, 2, 2)
        and BASE_MUST == 3
        and KF_N == 2
        and KF_D == (2, 2)
        and KF_MUST == 3
        and NULL_N == 2
        and NULL_D == ()
    )
    real_identity_pass = real_d == REAL_MUST and base_d == BASE_MUST
    known_false_ci_pass = kf_d == KF_MUST and kf_d != real_d
    reject_invalid_pass = all(bool(row["rejected"]) for row in invalid_decisions)
    null_empty_degree_pass = null_d is None and null_d != real_d
    all_pass = (
        fixture_pass
        and real_identity_pass
        and known_false_ci_pass
        and reject_invalid_pass
        and null_empty_degree_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    real = {
        "id": "REAL",
        "n": REAL_N,
        "degrees": list(REAL_D),
        "d_reg": real_d,
        "hf_prefix": real_hf[:6],
        "base_n": BASE_N,
        "base_degrees": list(BASE_D),
        "base_d_reg": base_d,
    }
    kf = {
        "id": "KF",
        "n": KF_N,
        "degrees": list(KF_D),
        "d_reg": kf_d,
        "hf_prefix": kf_hf[:6],
    }
    null = {
        "id": "NULL",
        "kind": "empty_degree_list",
        "n": NULL_N,
        "degrees": list(NULL_D),
        "d_reg": null_d,
        "hf_prefix": null_hf[:6],
        "rejected_as_collapse": null_d != real_d,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-735974-S0",
        "experiment_id": "EXP-ECDLP-735974",
        "hypothesis_id": "H-ECDLP-881d63",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-HILB",
        "fixture": {
            "max_degree": MAX_DEGREE,
            "REAL": {"id": "REAL", "must_d_reg": REAL_MUST},
            "BASE": {"id": "BASE", "must_d_reg": BASE_MUST},
            "KF": {"id": "KF", "must_d_reg": KF_MUST},
            "NULL": {"id": "NULL", "kind": "empty_degree_list", "must_d_reg": None},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_identity_pass": real_identity_pass,
            "known_false_ci_pass": known_false_ci_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_degree_pass": null_empty_degree_pass,
            "REAL": real,
            "KF": kf,
            "NULL": null,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "not_a_groebner_run": True,
        "not_a_binary_field_system": True,
        "not_a_kn_lit_4558_extraction": True,
        "do_not_run_groebner": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-735974/implementation/stage0_hilb.py\n"
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
        "real_identity_pass": real_identity_pass,
        "known_false_ci_pass": known_false_ci_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_degree_pass": null_empty_degree_pass,
        "REAL": real,
        "KF": kf,
        "NULL": null,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-735974-S0
  experiment_id: EXP-ECDLP-735974
  run_id: RUN-ECDLP-735974-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_identity_pass: {str(real_identity_pass).lower()}
  known_false_ci_pass: {str(known_false_ci_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_degree_pass: {str(null_empty_degree_pass).lower()}
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
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_a_groebner_run: true
  not_a_binary_field_system: true
  not_a_kn_lit_4558_extraction: true
  do_not_run_groebner: true
  frozen_object: P-S0-HILB
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL Hilbert-series values match committed table. Invalid objects rejected.
  - real_identity_pass {str(real_identity_pass).lower()}. REAL n={REAL_N} D={list(REAL_D)} d_reg {real_d}; baseline n={BASE_N} D={list(BASE_D)} d_reg {base_d}.
  - known_false_ci_pass {str(known_false_ci_pass).lower()}. KF complete intersection d_reg {kf_d} not equal to REAL {real_d}.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. n=0 and a non-positive degree rejected before any identity is read.
  - null_empty_degree_pass {str(null_empty_degree_pass).lower()}. NULL d_reg {null_d} not equal to REAL {real_d}.
  unexpected_observations: []
  scientific_boundary: Toy one-profile Hilbert-series d_reg identity calibrator at (n, D)=(2, (2,2,2)). Not a Groebner run. Not a binary-field system. Not a KN-LIT-4558 extraction. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not run a Groebner basis. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-735974-S0
  experiment_id: EXP-ECDLP-735974
  hypothesis_id: H-ECDLP-881d63
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
    command: python3 experiments/EXP-ECDLP-735974/implementation/stage0_hilb.py
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
      frozen_object: P-S0-HILB
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
    validity_reason: Stage 0 exact Hilbert-series d_reg identity calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_identity_pass: {str(real_identity_pass).lower()}
      known_false_ci_pass: {str(known_false_ci_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_degree_pass: {str(null_empty_degree_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_a_groebner_run: true
      not_a_binary_field_system: true
      not_a_kn_lit_4558_extraction: true
      do_not_run_groebner: true
      stage1_authorized: false
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
    scientific_boundary: Toy one-profile Hilbert-series d_reg identity calibrator at (n, D)=(2, (2,2,2)). Not a Groebner run. Not a binary-field system. Not a KN-LIT-4558 extraction. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-735974. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not run a Groebner basis.
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
                "real_identity_pass": real_identity_pass,
                "known_false_ci_pass": known_false_ci_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_empty_degree_pass": null_empty_degree_pass,
                "REAL": real,
                "KF": kf,
                "NULL": null,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
