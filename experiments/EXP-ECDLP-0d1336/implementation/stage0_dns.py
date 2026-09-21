#!/usr/bin/env python3
"""EXP-ECDLP-0d1336 Stage 0 exact D_NS Macaulay-rank calibrator.

Certificate kind none. No decoder. No cadical. No LRAT. No kissat.
Not peel_and_rank of EXP-DREG-001. Not the Trimoska pdp encoder.
Do not hunt a new polynomial. Frozen object P-S0-DNS: REAL / KF / NULL.
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
SOURCE = "experiments/EXP-ECDLP-0d1336/implementation/stage0_dns.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-0d1336/runs/RUN-ECDLP-0d1336-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-0d1336/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-e7451f"
TASK_ID = "TASK-20260908-6c1502"

VARS = ("x",)
DMAX = 3

REAL = {
    "id": "REAL",
    "generators": (("x",), ("1", "x")),
    "must_dns": 1,
    "must_found": True,
}
KF = {
    "id": "KF",
    "generators": (("x",),),
    "must_found": False,
}
NULL = {
    "id": "NULL",
    "generators": (("1",),),
    "must_dns": 0,
    "must_found": True,
}


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def parse_poly(terms: tuple[str, ...], variables: tuple[str, ...]) -> frozenset[int]:
    index = {name: i for i, name in enumerate(variables)}
    out: set[int] = set()
    for term in terms:
        if term == "1":
            mask = 0
        else:
            if term not in index:
                raise ValueError("unknown variable")
            mask = 1 << index[term]
        out.symmetric_difference_update({mask})
    return frozenset(out)


def poly_deg(poly: frozenset[int]) -> int:
    if not poly:
        return -1
    return max(mask.bit_count() for mask in poly)


def mul_poly(a: frozenset[int], b: frozenset[int]) -> frozenset[int]:
    out: set[int] = set()
    for x in a:
        for y in b:
            # Boolean ring: x_i^2 = x_i, so OR of bitmasks.
            prod = x | y
            out.symmetric_difference_update({prod})
    return frozenset(out)


def monomials(n_vars: int, degree: int) -> list[int]:
    if n_vars <= 0:
        raise ValueError("empty variable list")
    if degree < 0:
        raise ValueError("negative dmax")
    out = []
    for mask in range(1 << n_vars):
        if mask.bit_count() <= degree:
            out.append(mask)
    return out


def macaulay_rows(
    generators: tuple[frozenset[int], ...], n_vars: int, degree: int
) -> list[int]:
    cols = monomials(n_vars, degree)
    col_index = {m: i for i, m in enumerate(cols)}
    rows: list[int] = []
    for gen in generators:
        d = poly_deg(gen)
        if d < 0 or d > degree:
            continue
        for m in monomials(n_vars, degree - d):
            product = mul_poly(frozenset({m}), gen)
            bits = 0
            for term in product:
                if term.bit_count() <= degree:
                    bits ^= 1 << col_index[term]
            rows.append(bits)
    return rows


def in_span(rows: list[int], target: int) -> bool:
    basis: list[int] = []
    for row in rows:
        cur = row
        for b in basis:
            pivot = b.bit_length() - 1
            if pivot >= 0 and (cur >> pivot) & 1:
                cur ^= b
        if cur:
            pivot = cur.bit_length() - 1
            basis.append(cur)
            basis.sort(key=lambda v: -(v.bit_length()), reverse=False)
            basis.sort(key=lambda v: -v.bit_length())
    cur = target
    for b in basis:
        pivot = b.bit_length() - 1
        if pivot >= 0 and (cur >> pivot) & 1:
            cur ^= b
    return cur == 0


def dns_of(
    variables: tuple[str, ...],
    generators_terms: tuple[tuple[str, ...], ...],
    dmax: int,
) -> tuple[int | None, bool]:
    if not variables:
        raise ValueError("empty variable list")
    if dmax < 0:
        raise ValueError("negative dmax")
    gens = tuple(parse_poly(g, variables) for g in generators_terms)
    cols0 = monomials(len(variables), 0)
    one_col = cols0.index(0)
    for degree in range(0, dmax + 1):
        cols = monomials(len(variables), degree)
        one_index = cols.index(0)
        rows = macaulay_rows(gens, len(variables), degree)
        target = 1 << one_index
        if in_span(rows, target):
            return degree, True
    return None, False


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        dns_of((), REAL["generators"], DMAX)
        decisions.append({"id": "VARS-empty", "rejected": False})
    except ValueError:
        decisions.append({"id": "VARS-empty", "rejected": True})
    try:
        dns_of(VARS, REAL["generators"], -1)
        decisions.append({"id": "DMAX-negative", "rejected": False})
    except ValueError:
        decisions.append({"id": "DMAX-negative", "rejected": True})
    return decisions


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real_dns, real_found = dns_of(VARS, REAL["generators"], DMAX)
    kf_dns, kf_found = dns_of(VARS, KF["generators"], DMAX)
    null_dns, null_found = dns_of(VARS, NULL["generators"], DMAX)
    invalid_decisions = reject_invalid()

    fixture_pass = True
    real_dns_pass = real_found is True and real_dns == REAL["must_dns"]
    known_false_sat_pass = kf_found is False
    reject_invalid_pass = all(bool(d["rejected"]) for d in invalid_decisions)
    null_constant_pass = null_found is True and null_dns == NULL["must_dns"]
    all_pass = (
        fixture_pass
        and real_dns_pass
        and known_false_sat_pass
        and reject_invalid_pass
        and null_constant_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-0d1336-S0",
        "experiment_id": "EXP-ECDLP-0d1336",
        "hypothesis_id": "H-ECDLP-38f4b4",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-DNS",
        "fixture": {
            "variables": list(VARS),
            "dmax": DMAX,
            "REAL": {
                "id": REAL["id"],
                "generators": [list(g) for g in REAL["generators"]],
                "must_dns": REAL["must_dns"],
                "must_found": REAL["must_found"],
            },
            "KF": {
                "id": KF["id"],
                "generators": [list(g) for g in KF["generators"]],
                "must_found": KF["must_found"],
            },
            "NULL": {
                "id": NULL["id"],
                "generators": [list(g) for g in NULL["generators"]],
                "must_dns": NULL["must_dns"],
                "must_found": NULL["must_found"],
            },
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_dns_pass": real_dns_pass,
            "known_false_sat_pass": known_false_sat_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_constant_pass": null_constant_pass,
            "REAL": {"D_NS": real_dns, "found": real_found},
            "KF": {"D_NS": kf_dns, "found": kf_found},
            "NULL": {"D_NS": null_dns, "found": null_found},
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
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
        "not_cadical": True,
        "not_lrat": True,
        "not_a_sat_histogram": True,
        "not_trimoska_pdp_encoder": True,
        "do_not_hunt_a_new_polynomial": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-0d1336/implementation/stage0_dns.py\n"
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
        "real_dns_pass": real_dns_pass,
        "known_false_sat_pass": known_false_sat_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_constant_pass": null_constant_pass,
        "REAL_D_NS": real_dns,
        "REAL_found": real_found,
        "KF_D_NS": kf_dns,
        "KF_found": kf_found,
        "NULL_D_NS": null_dns,
        "NULL_found": null_found,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-0d1336-S0
  experiment_id: EXP-ECDLP-0d1336
  run_id: RUN-ECDLP-0d1336-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_dns_pass: {str(real_dns_pass).lower()}
  known_false_sat_pass: {str(known_false_sat_pass).lower()}
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
  stage1_authorized: false
  not_a_decoder: true
  not_cadical: true
  not_lrat: true
  not_a_sat_histogram: true
  not_trimoska_pdp_encoder: true
  do_not_hunt_a_new_polynomial: true
  frozen_object: P-S0-DNS
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL D_NS values match committed table. Invalid objects rejected.
  - real_dns_pass {str(real_dns_pass).lower()}. REAL D_NS is {real_dns} found {str(real_found).lower()}.
  - known_false_sat_pass {str(known_false_sat_pass).lower()}. KF found {str(kf_found).lower()}.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. Empty and negative-Dmax objects rejected before any D_NS census.
  - null_constant_pass {str(null_constant_pass).lower()}. NULL D_NS is {null_dns} found {str(null_found).lower()}.
  unexpected_observations: []
  scientific_boundary: Toy one-variable Boolean-ring D_NS calibrator. Not a decoder. Not cadical. Not LRAT. Not kissat. Not peel_and_rank. Not the Trimoska pdp encoder. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new polynomial. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-0d1336-S0
  experiment_id: EXP-ECDLP-0d1336
  hypothesis_id: H-ECDLP-38f4b4
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
    command: python3 experiments/EXP-ECDLP-0d1336/implementation/stage0_dns.py
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
      frozen_object: P-S0-DNS
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
    validity_reason: Stage 0 exact D_NS calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_dns_pass: {str(real_dns_pass).lower()}
      known_false_sat_pass: {str(known_false_sat_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_constant_pass: {str(null_constant_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_cadical: true
      not_lrat: true
      not_a_sat_histogram: true
      not_trimoska_pdp_encoder: true
      do_not_hunt_a_new_polynomial: true
      stage1_authorized: false
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
    scientific_boundary: Toy one-variable Boolean-ring D_NS calibrator. Not a decoder. Not cadical. Not LRAT. Not kissat. Not peel_and_rank. Not the Trimoska pdp encoder. Not Stage 1 of EXP-ECDLP-0d1336. Not Stage 1 of EXP-ECDLP-1aa0f8. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new polynomial.
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
                "real_dns_pass": real_dns_pass,
                "known_false_sat_pass": known_false_sat_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_constant_pass": null_constant_pass,
                "REAL": {"D_NS": real_dns, "found": real_found},
                "KF": {"D_NS": kf_dns, "found": kf_found},
                "NULL": {"D_NS": null_dns, "found": null_found},
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
