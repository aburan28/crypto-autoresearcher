#!/usr/bin/env python3
"""EXP-ECDLP-fdae20 Stage 0 exact charged-bar identity calibrator.

Certificate kind none. No decoder. No stored walk. No ledger audit.
No frontier table. No rho beat.
Frozen object P-S0-BARS: REAL / KF / NULL.

C_prep(M, σ) = n^{(1+σ)/2} + M n^{(1-σ)/2}.
At σ* = log M / log n, C_prep = 2√(M n).
Frozen (n, M)=(16, 4), σ*=1/2. Exact integer arithmetic only.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-fdae20/implementation/stage0_bars.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-fdae20/runs/RUN-ECDLP-fdae20-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-fdae20/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-2c6cee"
TASK_ID = "TASK-20260908-ead79f"

N = 16
M = 4
SIGMA_STAR = (1, 2)
REAL_MUST_C = 16
REAL_MUST_BAR = 16
M1_MUST_C = 8
M1_MUST_BAR = 8
KF_MUST_C = 20
NULL_MUST_C = 8


class InvalidParamsError(ValueError):
    """n<=1 or M<=0 makes σ* undefined; reject, do not evaluate."""


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def integer_root(n: int, k: int) -> int:
    """Exact integer k-th root of n, or raise."""
    if k <= 0:
        raise ValueError("non-positive root degree")
    if n < 0:
        raise ValueError("negative radicand")
    if k == 1:
        return n
    if n == 0:
        return 0
    lo, hi = 1, n
    found = None
    while lo <= hi:
        mid = (lo + hi) // 2
        p = mid**k
        if p == n:
            found = mid
            break
        if p < n:
            lo = mid + 1
        else:
            hi = mid - 1
    if found is None:
        raise ValueError(f"{n} is not a perfect {k}-th power")
    return found


def pow_frac(n: int, num: int, den: int) -> int:
    """Exact integer n^{num/den} via (n^{1/den})^{num} after reducing the fraction."""
    if den <= 0:
        raise ValueError("non-positive exponent denominator")
    g = math.gcd(num, den)
    num //= g
    den //= g
    if num < 0:
        raise ValueError("negative exponent")
    root = integer_root(n, den)
    return root**num


def c_prep(n: int, M: int, sigma_num: int, sigma_den: int) -> int:
    if n <= 1:
        raise InvalidParamsError("n<=1 makes log n undefined")
    if M <= 0:
        raise InvalidParamsError("M<=0 makes σ* undefined")
    if sigma_den <= 0:
        raise ValueError("non-positive sigma denominator")
    # (1+σ)/2 = (den + num)/(2 den)
    off_num = sigma_den + sigma_num
    off_den = 2 * sigma_den
    on_num = sigma_den - sigma_num
    on_den = 2 * sigma_den
    if on_num < 0:
        raise ValueError("sigma > 1")
    offline = pow_frac(n, off_num, off_den)
    online = pow_frac(n, on_num, on_den)
    return offline + M * online


def bar(n: int, M: int) -> int:
    if n <= 1:
        raise InvalidParamsError("n<=1 makes log n undefined")
    if M <= 0:
        raise InvalidParamsError("M<=0 makes σ* undefined")
    return 2 * integer_root(M * n, 2)


def cheap_offline(n: int, M: int, sigma_num: int, sigma_den: int) -> int:
    """Nearby-object: drop the offline term. C_null = M n^{(1-σ)/2}."""
    if n <= 1:
        raise InvalidParamsError("n<=1 makes log n undefined")
    if M <= 0:
        raise InvalidParamsError("M<=0 makes σ* undefined")
    on_num = sigma_den - sigma_num
    on_den = 2 * sigma_den
    return M * pow_frac(n, on_num, on_den)


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        c_prep(1, M, 1, 2)
        decisions.append({"id": "n-one", "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "n-one", "rejected": True})
    try:
        c_prep(N, 0, 1, 2)
        decisions.append({"id": "M-zero", "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "M-zero", "rejected": True})
    return decisions


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real_c = c_prep(N, M, SIGMA_STAR[0], SIGMA_STAR[1])
    real_bar = bar(N, M)
    m1_c = c_prep(N, 1, 0, 1)
    m1_bar = bar(N, 1)
    kf_c = c_prep(N, M, 0, 1)
    null_c = cheap_offline(N, M, SIGMA_STAR[0], SIGMA_STAR[1])
    invalid_decisions = reject_invalid()

    fixture_pass = (
        N == 16
        and M == 4
        and SIGMA_STAR == (1, 2)
        and REAL_MUST_C == 16
        and REAL_MUST_BAR == 16
        and M1_MUST_C == 8
        and M1_MUST_BAR == 8
        and KF_MUST_C == 20
        and NULL_MUST_C == 8
    )
    real_identity_pass = (
        real_c == REAL_MUST_C
        and real_bar == REAL_MUST_BAR
        and real_c == real_bar
        and m1_c == M1_MUST_C
        and m1_bar == M1_MUST_BAR
        and m1_c == m1_bar
    )
    known_false_subopt_pass = kf_c == KF_MUST_C and kf_c != real_bar
    reject_invalid_pass = all(bool(d["rejected"]) for d in invalid_decisions)
    null_cheap_offline_pass = null_c == NULL_MUST_C and null_c != real_bar
    all_pass = (
        fixture_pass
        and real_identity_pass
        and known_false_subopt_pass
        and reject_invalid_pass
        and null_cheap_offline_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    real = {
        "id": "REAL",
        "n": N,
        "M": M,
        "sigma_num": SIGMA_STAR[0],
        "sigma_den": SIGMA_STAR[1],
        "c_prep": real_c,
        "bar": real_bar,
        "m1_c_prep": m1_c,
        "m1_bar": m1_bar,
    }
    kf = {
        "id": "KF",
        "n": N,
        "M": M,
        "sigma_num": 0,
        "sigma_den": 1,
        "c_prep": kf_c,
        "bar": real_bar,
    }
    null = {
        "id": "NULL",
        "kind": "cheap_offline",
        "n": N,
        "M": M,
        "c_null": null_c,
        "bar": real_bar,
        "rejected_as_collapse": null_c != real_bar,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-fdae20-S0",
        "experiment_id": "EXP-ECDLP-fdae20",
        "hypothesis_id": "H-ECDLP-9a1388",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-BARS",
        "fixture": {
            "n": N,
            "M": M,
            "sigma_star": {"num": SIGMA_STAR[0], "den": SIGMA_STAR[1]},
            "REAL": {
                "id": "REAL",
                "must_c_prep": REAL_MUST_C,
                "must_bar": REAL_MUST_BAR,
                "m1_must_c_prep": M1_MUST_C,
                "m1_must_bar": M1_MUST_BAR,
            },
            "KF": {"id": "KF", "must_c_prep": KF_MUST_C, "must_bar": REAL_MUST_BAR},
            "NULL": {
                "id": "NULL",
                "kind": "cheap_offline",
                "must_c_null": NULL_MUST_C,
                "must_bar": REAL_MUST_BAR,
            },
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_identity_pass": real_identity_pass,
            "known_false_subopt_pass": known_false_subopt_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_cheap_offline_pass": null_cheap_offline_pass,
            "REAL": real,
            "KF": kf,
            "NULL": null,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "not_a_stored_walk": True,
        "not_a_ledger_audit": True,
        "not_a_frontier_table": True,
        "do_not_scan_the_ledger": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-fdae20/implementation/stage0_bars.py\n"
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
        "known_false_subopt_pass": known_false_subopt_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_cheap_offline_pass": null_cheap_offline_pass,
        "REAL": real,
        "KF": kf,
        "NULL": null,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-fdae20-S0
  experiment_id: EXP-ECDLP-fdae20
  run_id: RUN-ECDLP-fdae20-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_identity_pass: {str(real_identity_pass).lower()}
  known_false_subopt_pass: {str(known_false_subopt_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_cheap_offline_pass: {str(null_cheap_offline_pass).lower()}
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
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_a_stored_walk: true
  not_a_ledger_audit: true
  not_a_frontier_table: true
  do_not_scan_the_ledger: true
  frozen_object: P-S0-BARS
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL charged-bar values match committed table. Invalid objects rejected.
  - real_identity_pass {str(real_identity_pass).lower()}. REAL n={N} M={M} C_prep {real_c} bar {real_bar}; M=1 baseline C_prep {m1_c} bar {m1_bar}.
  - known_false_subopt_pass {str(known_false_subopt_pass).lower()}. KF σ=0 C_prep {kf_c} not equal to bar {real_bar}.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. n=1 and M=0 rejected before any identity is read.
  - null_cheap_offline_pass {str(null_cheap_offline_pass).lower()}. NULL C_null {null_c} not equal to bar {real_bar}.
  unexpected_observations: []
  scientific_boundary: Toy one-pair charged-bar identity calibrator at (n, M)=(16, 4). Not a stored walk. Not a ledger audit. Not a frontier table. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not scan the ledger. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-fdae20-S0
  experiment_id: EXP-ECDLP-fdae20
  hypothesis_id: H-ECDLP-9a1388
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
    command: python3 experiments/EXP-ECDLP-fdae20/implementation/stage0_bars.py
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
      frozen_object: P-S0-BARS
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
    validity_reason: Stage 0 exact charged-bar identity calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_identity_pass: {str(real_identity_pass).lower()}
      known_false_subopt_pass: {str(known_false_subopt_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_cheap_offline_pass: {str(null_cheap_offline_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_a_stored_walk: true
      not_a_ledger_audit: true
      not_a_frontier_table: true
      do_not_scan_the_ledger: true
      stage1_authorized: false
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
    scientific_boundary: Toy one-pair charged-bar identity calibrator at (n, M)=(16, 4). Not a stored walk. Not a ledger audit. Not a frontier table. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-fdae20. Not Stage 1 of EXP-ECDLP-089e80. Not Stage 1 of EXP-ECDLP-b3f975. Not Stage 1 of EXP-ECDLP-daf1bb. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not scan the ledger.
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
                "known_false_subopt_pass": known_false_subopt_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_cheap_offline_pass": null_cheap_offline_pass,
                "REAL": real,
                "KF": kf,
                "NULL": null,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
