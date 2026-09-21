#!/usr/bin/env python3
"""EXP-ECDLP-a294b6 Stage 0 exact split/inert Gauss-norm calibrator.

Certificate kind none. No Coppersmith. No Semaev S_m. No Velu.
No yield ratio k. No elliptic M_S. No (L,b) meter. No Aut census.
No orbit cost. No 1D-versus-2D eps-hat comparison.
Frozen object P-S0-QRESIDUE: REAL / KF / NULL in Z[i].

REAL: p=13 splits (p ≡ 1 mod 4), π = 2+3i, lattice (2,3), (-3,2).
Shortest-lift norms of x=0..12 are the frozen 13-tuple
[0, 1, 4, 4, 2, 1, 2, 2, 1, 2, 4, 4, 1].
KF: inert p=7 (p ≡ 3 mod 4) is rejected.
NULL empty residue list is rejected. p=0 is rejected.
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
SOURCE = "experiments/EXP-ECDLP-a294b6/implementation/stage0_qresidue.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-a294b6/runs/RUN-ECDLP-a294b6-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-a294b6/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-39f596"
TASK_ID = "TASK-20260908-301223"

RING = "Z[i]"
REAL_P = 13
REAL_PI = (2, 3)
REAL_BASIS = ((2, 3), (-3, 2))
FROZEN_NORMS = [0, 1, 4, 4, 2, 1, 2, 2, 1, 2, 4, 4, 1]
KF_P = 7
SEARCH_BOUND = 12


class InvalidParamsError(ValueError):
    """p not a frozen positive split prime, or empty residue list, is rejected."""


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


def splits_in_zi(p: int) -> bool:
    require_positive_p(p)
    return int(p) % 4 == 1


def require_split_prime(p: int) -> None:
    if not splits_in_zi(p):
        raise InvalidParamsError("p does not split in Z[i]")


def shortest_lift(x: int, basis: tuple[tuple[int, int], tuple[int, int]]) -> tuple[int, int, int]:
    """Return (norm, u, v) for a shortest vector in (x,0) + Z*b0 + Z*b1."""
    b0, b1 = basis
    best_n = None
    best_u = 0
    best_v = 0
    for a in range(-SEARCH_BOUND, SEARCH_BOUND + 1):
        for b in range(-SEARCH_BOUND, SEARCH_BOUND + 1):
            u = int(x) + a * b0[0] + b * b1[0]
            v = a * b0[1] + b * b1[1]
            n = u * u + v * v
            if best_n is None or n < best_n or (n == best_n and (u, v) < (best_u, best_v)):
                best_n = n
                best_u = u
                best_v = v
    if best_n is None:
        raise InvalidParamsError("empty lattice search")
    return int(best_n), int(best_u), int(best_v)


def gauss_norm_table(p: int, residues: list[int], basis: tuple[tuple[int, int], tuple[int, int]]) -> list[int]:
    require_split_prime(p)
    if not residues:
        raise InvalidParamsError("empty residue list")
    return [shortest_lift(x, basis)[0] for x in residues]


def evaluate_real() -> dict[str, object]:
    residues = list(range(REAL_P))
    lifts = [shortest_lift(x, REAL_BASIS) for x in residues]
    norms = [row[0] for row in lifts]
    vecs = [[row[1], row[2]] for row in lifts]
    return {
        "kind": "split",
        "p": REAL_P,
        "p_mod_4": REAL_P % 4,
        "pi": [REAL_PI[0], REAL_PI[1]],
        "lattice_basis": [[REAL_BASIS[0][0], REAL_BASIS[0][1]], [REAL_BASIS[1][0], REAL_BASIS[1][1]]],
        "norms": norms,
        "vectors": vecs,
        "matches_frozen": norms == FROZEN_NORMS,
    }


def evaluate_kf() -> dict[str, object]:
    try:
        gauss_norm_table(KF_P, list(range(KF_P)), REAL_BASIS)
        return {
            "kind": "inert",
            "p": KF_P,
            "p_mod_4": KF_P % 4,
            "rejected": False,
        }
    except InvalidParamsError:
        return {
            "kind": "inert",
            "p": KF_P,
            "p_mod_4": KF_P % 4,
            "rejected": True,
        }


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        require_split_prime(0)
        decisions.append({"id": "p-zero", "p": 0, "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "p-zero", "p": 0, "rejected": True})
    return decisions


def reject_null() -> list[dict[str, object]]:
    rows = []
    try:
        gauss_norm_table(REAL_P, [], REAL_BASIS)
        rows.append({"id": "NULL", "kind": "empty_residues", "rejected": False})
    except InvalidParamsError:
        rows.append({"id": "NULL", "kind": "empty_residues", "rejected": True})
    return rows


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real = evaluate_real()
    kf = evaluate_kf()
    null_rows = reject_null()
    invalid_decisions = reject_invalid()

    fixture_pass = (
        RING == "Z[i]"
        and REAL_P == 13
        and REAL_PI == (2, 3)
        and REAL_BASIS == ((2, 3), (-3, 2))
        and KF_P == 7
        and FROZEN_NORMS == [0, 1, 4, 4, 2, 1, 2, 2, 1, 2, 4, 4, 1]
    )
    real_norm_pass = bool(real["matches_frozen"]) and list(real["norms"]) == FROZEN_NORMS
    known_false_inert_pass = bool(kf["rejected"]) and int(kf["p_mod_4"]) == 3
    reject_invalid_pass = all(bool(row["rejected"]) for row in invalid_decisions)
    null_empty_pass = all(bool(row["rejected"]) for row in null_rows)
    all_pass = (
        fixture_pass
        and real_norm_pass
        and known_false_inert_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    elapsed = time.perf_counter() - t0
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = git_head()

    real_obj = {"id": "REAL", **real}
    kf_obj = {"id": "KF", **kf}
    null_obj = {
        "id": "NULL",
        "kind": "empty_residues",
        "rejected": all(bool(row["rejected"]) for row in null_rows),
        "rows": null_rows,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-a294b6-S0",
        "experiment_id": "EXP-ECDLP-a294b6",
        "hypothesis_id": "H-ECDLP-cacf58",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-QRESIDUE",
        "fixture": {
            "ring": RING,
            "REAL": {
                "id": "REAL",
                "p": REAL_P,
                "p_mod_4": 1,
                "pi": [2, 3],
                "lattice_basis": [[2, 3], [-3, 2]],
                "must_norms": FROZEN_NORMS,
            },
            "KF": {
                "id": "KF",
                "p": KF_P,
                "p_mod_4": 3,
                "must_reject": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_residues", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_norm_pass": real_norm_pass,
            "known_false_inert_pass": known_false_inert_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_a294b6_stage1_authorized": False,
        "exp_835df6_stage1_authorized": False,
        "exp_5f3822_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "not_coppersmith": True,
        "not_semaev": True,
        "do_not_run_coppersmith": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_form_elliptic_ms": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-a294b6/implementation/stage0_qresidue.py\n"
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
        "real_norm_pass": real_norm_pass,
        "known_false_inert_pass": known_false_inert_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-a294b6-S0
  experiment_id: EXP-ECDLP-a294b6
  run_id: RUN-ECDLP-a294b6-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_norm_pass: {str(real_norm_pass).lower()}
  known_false_inert_pass: {str(known_false_inert_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_a294b6_stage1_authorized: false
  exp_835df6_stage1_authorized: false
  exp_5f3822_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_coppersmith: true
  not_semaev: true
  do_not_run_coppersmith: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_form_elliptic_ms: true
  frozen_object: P-S0-QRESIDUE
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_norm_pass {str(real_norm_pass).lower()}. REAL norms are {real['norms']}."
  - "known_false_inert_pass {str(known_false_inert_pass).lower()}. KF p={kf['p']} p_mod_4={kf['p_mod_4']} rejected={str(kf['rejected']).lower()}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. p=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty residue list is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen split/inert Gauss-norm calibrator in Z[i]. Not Coppersmith. Not Semaev S_m. Not Velu. Not a yield ratio k. Not elliptic M_S. Not an (L,b) meter. Not an Aut census. Not an orbit cost. Not a 1D-versus-2D eps-hat comparison. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-a294b6. Not Stage 1 of EXP-ECDLP-835df6. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-a294b6-S0
  experiment_id: EXP-ECDLP-a294b6
  hypothesis_id: H-ECDLP-cacf58
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
    command: python3 experiments/EXP-ECDLP-a294b6/implementation/stage0_qresidue.py
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
      frozen_object: P-S0-QRESIDUE
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      ring: Z[i]
      real_p: 13
      kf_p: 7
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
    validity_reason: Stage 0 exact split/inert Gauss-norm calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_norm_pass: {str(real_norm_pass).lower()}
      known_false_inert_pass: {str(known_false_inert_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_coppersmith: true
      not_semaev: true
      do_not_run_coppersmith: true
      do_not_form_semaev: true
      do_not_run_velu: true
      do_not_form_elliptic_ms: true
      stage1_authorized: false
      exp_a294b6_stage1_authorized: false
      exp_835df6_stage1_authorized: false
    scientific_boundary: "Toy frozen split/inert Gauss-norm calibrator in Z[i]. Not Coppersmith. Not Semaev S_m. Not Velu. Not a yield ratio k. Not elliptic M_S. Not an (L,b) meter. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-a294b6. Not Stage 1 of EXP-ECDLP-835df6. Certificate kind none."
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
                "real_norm_pass": real_norm_pass,
                "known_false_inert_pass": known_false_inert_pass,
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
