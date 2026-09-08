#!/usr/bin/env python3
"""EXP-ECDLP-79f8c4 Stage 0 brute-force Aut instrument.

Certificate kind none. No decoder. No BreakID. No saucy. No cadical.
Not a torsion-invariant V. Not the Trimoska pdp encoder. Do not hunt a
new CNF. Frozen object P-S0-AUT: REAL3 / KF3 / NULL3.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-79f8c4/implementation/stage0_aut.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-79f8c4/runs/RUN-ECDLP-79f8c4-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-79f8c4/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-8da768"
TASK_ID = "TASK-20260908-734346"

VARS = ("a0", "a1", "b0", "b1", "c0", "c1")

REAL3 = {
    "id": "REAL3",
    "m": 3,
    "l": 2,
    "clauses": (
        ("a0", "b0", "c0"),
        ("a0", "a1"),
        ("b0", "b1"),
        ("c0", "c1"),
    ),
    "must_aut_order": 6,
    "must_aut_images": (
        ("a0", "a1", "b0", "b1", "c0", "c1"),
        ("a0", "a1", "c0", "c1", "b0", "b1"),
        ("b0", "b1", "a0", "a1", "c0", "c1"),
        ("b0", "b1", "c0", "c1", "a0", "a1"),
        ("c0", "c1", "a0", "a1", "b0", "b1"),
        ("c0", "c1", "b0", "b1", "a0", "a1"),
    ),
}

KF3 = {
    "id": "KF3",
    "extra_clauses": (("a1", "b1", "c1"),),
    "must_aut_order": 12,
    "must_aut_images": (
        ("a0", "a1", "b0", "b1", "c0", "c1"),
        ("a0", "a1", "c0", "c1", "b0", "b1"),
        ("a1", "a0", "b1", "b0", "c1", "c0"),
        ("a1", "a0", "c1", "c0", "b1", "b0"),
        ("b0", "b1", "a0", "a1", "c0", "c1"),
        ("b0", "b1", "c0", "c1", "a0", "a1"),
        ("b1", "b0", "a1", "a0", "c1", "c0"),
        ("b1", "b0", "c1", "c0", "a1", "a0"),
        ("c0", "c1", "a0", "a1", "b0", "b1"),
        ("c0", "c1", "b0", "b1", "a0", "a1"),
        ("c1", "c0", "a1", "a0", "b1", "b0"),
        ("c1", "c0", "b1", "b0", "a1", "a0"),
    ),
}

NULL3 = {
    "id": "NULL3",
    "clauses": (
        ("a0",),
        ("a1", "b0"),
        ("b1", "c0", "c1"),
        ("a1", "c0"),
        ("b1",),
    ),
    "must_aut_order": 1,
}

INVALID = {
    "CNF-empty": {"clauses": []},
    "BLOCKS-twoblock": {"blocks": {"A": 2, "B": 2}},
}

REQUIRED_BLOCKS = {"A": 2, "B": 2, "C": 2}


def as_clause_set(clauses) -> set[frozenset[str]]:
    return {frozenset(cl) for cl in clauses}


def aut_images(clauses, variables=VARS) -> list[tuple[str, ...]]:
    clause_set = as_clause_set(clauses)
    found: list[tuple[str, ...]] = []
    for perm in permutations(variables):
        mapping = dict(zip(variables, perm))
        mapped = {frozenset(mapping[v] for v in cl) for cl in clause_set}
        if mapped == clause_set:
            found.append(tuple(mapping[v] for v in variables))
    return found


def clauses_well_formed(clauses, *, require_nonempty: bool) -> bool:
    if not isinstance(clauses, (list, tuple)):
        return False
    if require_nonempty and len(clauses) == 0:
        return False
    for cl in clauses:
        if not cl:
            return False
        for lit in cl:
            if lit not in VARS:
                return False
    return True


def blocks_well_formed(blocks: dict, *, require_three: bool) -> bool:
    if not isinstance(blocks, dict) or not blocks:
        return False
    if require_three and set(blocks) != {"A", "B", "C"}:
        return False
    if len(blocks) < 3:
        return False
    for name, width in blocks.items():
        if name not in {"A", "B", "C"}:
            return False
        if width != REQUIRED_BLOCKS.get(name):
            return False
    return True


def reject_invalid() -> dict[str, bool]:
    decisions = {}
    empty = INVALID["CNF-empty"]["clauses"]
    decisions["CNF-empty"] = not clauses_well_formed(empty, require_nonempty=True)
    twoblock = INVALID["BLOCKS-twoblock"]["blocks"]
    decisions["BLOCKS-twoblock"] = not blocks_well_formed(twoblock, require_three=True)
    return decisions


def measure(clauses) -> dict:
    images = aut_images(clauses)
    return {
        "aut_order": len(images),
        "aut_images": [list(img) for img in images],
        "aut_images_tuples": images,
    }


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    invalid_decisions = reject_invalid()
    reject_invalid_pass = all(invalid_decisions.values())
    fixture_blocks_ok = blocks_well_formed(REQUIRED_BLOCKS, require_three=True)
    fixture_real_ok = clauses_well_formed(REAL3["clauses"], require_nonempty=True)
    fixture_kf_ok = clauses_well_formed(
        REAL3["clauses"] + KF3["extra_clauses"], require_nonempty=True
    )
    fixture_null_ok = clauses_well_formed(NULL3["clauses"], require_nonempty=True)

    real = measure(REAL3["clauses"])
    kf = measure(REAL3["clauses"] + KF3["extra_clauses"])
    null = measure(NULL3["clauses"])

    real_images = set(real["aut_images_tuples"])
    kf_images = set(kf["aut_images_tuples"])
    real_expected = set(REAL3["must_aut_images"])
    kf_expected = set(KF3["must_aut_images"])

    fixture_pass = (
        fixture_blocks_ok
        and fixture_real_ok
        and fixture_kf_ok
        and fixture_null_ok
        and real["aut_order"] == REAL3["must_aut_order"]
        and kf["aut_order"] == KF3["must_aut_order"]
        and null["aut_order"] == NULL3["must_aut_order"]
        and real_images == real_expected
        and kf_images == kf_expected
    )
    real_aut_mfact_pass = (
        real["aut_order"] == REAL3["must_aut_order"]
        and real_images == real_expected
    )
    known_false_extra_pass = (
        kf["aut_order"] == KF3["must_aut_order"]
        and kf_images == kf_expected
    )
    null_trivial_pass = null["aut_order"] == NULL3["must_aut_order"]

    all_pass = (
        fixture_pass
        and real_aut_mfact_pass
        and known_false_extra_pass
        and reject_invalid_pass
        and null_trivial_pass
    )
    elapsed = time.perf_counter() - t0
    source_bytes = Path(__file__).read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    commit = git_head()

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-79f8c4-S0",
        "experiment_id": "EXP-ECDLP-79f8c4",
        "hypothesis_id": "H-ECDLP-536b21",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-AUT",
        "fixture": {
            "variables": list(VARS),
            "REAL3": {
                "id": REAL3["id"],
                "m": REAL3["m"],
                "l": REAL3["l"],
                "clauses": [list(c) for c in REAL3["clauses"]],
                "must_aut_order": REAL3["must_aut_order"],
                "must_aut_images": [list(img) for img in REAL3["must_aut_images"]],
            },
            "KF3": {
                "id": KF3["id"],
                "extra_clauses": [list(c) for c in KF3["extra_clauses"]],
                "must_aut_order": KF3["must_aut_order"],
                "must_aut_images": [list(img) for img in KF3["must_aut_images"]],
            },
            "NULL3": {
                "id": NULL3["id"],
                "clauses": [list(c) for c in NULL3["clauses"]],
                "must_aut_order": NULL3["must_aut_order"],
            },
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_aut_mfact_pass": real_aut_mfact_pass,
            "known_false_extra_pass": known_false_extra_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_trivial_pass": null_trivial_pass,
            "REAL3": {
                "aut_order": real["aut_order"],
                "aut_images": real["aut_images"],
            },
            "KF3": {
                "aut_order": kf["aut_order"],
                "aut_images": kf["aut_images"],
            },
            "NULL3": {
                "aut_order": null["aut_order"],
                "aut_images": null["aut_images"],
            },
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_79f8c4_stage1_authorized": False,
        "exp_628891_stage1_authorized": False,
        "exp_9e9536_stage1_authorized": False,
        "exp_90f602_stage1_authorized": False,
        "exp_4be480_stage2_authorized": False,
        "exp_6a97f4_stage2_authorized": False,
        "exp_420e73_stage17_authorized": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_a_decoder": True,
        "not_breakid": True,
        "not_a_sat_histogram": True,
        "not_trimoska_pdp_encoder": True,
        "not_torsion_invariant_v": True,
        "do_not_hunt_a_new_cnf": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }

    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-79f8c4/implementation/stage0_aut.py\n"
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
        "real_aut_mfact_pass": real_aut_mfact_pass,
        "known_false_extra_pass": known_false_extra_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_trivial_pass": null_trivial_pass,
        "REAL3_aut_order": real["aut_order"],
        "KF3_aut_order": kf["aut_order"],
        "NULL3_aut_order": null["aut_order"],
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-79f8c4-S0
  experiment_id: EXP-ECDLP-79f8c4
  run_id: RUN-ECDLP-79f8c4-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_aut_mfact_pass: {str(real_aut_mfact_pass).lower()}
  known_false_extra_pass: {str(known_false_extra_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_trivial_pass: {str(null_trivial_pass).lower()}
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
  stage1_authorized: false
  not_a_decoder: true
  not_breakid: true
  not_a_sat_histogram: true
  not_trimoska_pdp_encoder: true
  not_torsion_invariant_v: true
  do_not_hunt_a_new_cnf: true
  frozen_object: P-S0-AUT
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL3 / KF3 / NULL3 Aut orders match committed images. Invalid objects rejected.
  - real_aut_mfact_pass {str(real_aut_mfact_pass).lower()}. REAL3 |Aut|={real['aut_order']} with committed S_3 images.
  - known_false_extra_pass {str(known_false_extra_pass).lower()}. KF3 |Aut|={kf['aut_order']} with committed planted bit-swap images.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. Empty CNF and two-block objects rejected before any m=3 census.
  - null_trivial_pass {str(null_trivial_pass).lower()}. NULL3 |Aut|={null['aut_order']}.
  unexpected_observations: []
  scientific_boundary: Toy 6-variable 3-block Aut instrument. Not a decoder. Not BreakID. Not saucy. Not cadical. Not a torsion-invariant V. Not the Trimoska pdp encoder. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new CNF. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    from datetime import datetime, timezone

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-79f8c4-S0
  experiment_id: EXP-ECDLP-79f8c4
  hypothesis_id: H-ECDLP-536b21
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
    command: python3 experiments/EXP-ECDLP-79f8c4/implementation/stage0_aut.py
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
      frozen_object: P-S0-AUT
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL3, KF3, NULL3]
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
    validity_reason: Stage 0 brute-force Aut instrument gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_aut_mfact_pass: {str(real_aut_mfact_pass).lower()}
      known_false_extra_pass: {str(known_false_extra_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_trivial_pass: {str(null_trivial_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_breakid: true
      not_a_sat_histogram: true
      not_trimoska_pdp_encoder: true
      not_torsion_invariant_v: true
      do_not_hunt_a_new_cnf: true
      stage1_authorized: false
      exp_79f8c4_stage1_authorized: false
      exp_628891_stage1_authorized: false
      exp_9e9536_stage1_authorized: false
      exp_90f602_stage1_authorized: false
      exp_4be480_stage2_authorized: false
      exp_6a97f4_stage2_authorized: false
      exp_420e73_stage17_authorized: false
      exp_a98ea9_stage5_authorized: false
    scientific_boundary: Toy 6-variable 3-block Aut instrument. Not a decoder. Not BreakID. Not saucy. Not cadical. Not a torsion-invariant V. Not the Trimoska pdp encoder. Not Stage 1 of EXP-ECDLP-79f8c4. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new CNF.
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
                "real_aut_mfact_pass": real_aut_mfact_pass,
                "known_false_extra_pass": known_false_extra_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_trivial_pass": null_trivial_pass,
                "REAL3_aut_order": real["aut_order"],
                "KF3_aut_order": kf["aut_order"],
                "NULL3_aut_order": null["aut_order"],
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
