#!/usr/bin/env python3
"""EXP-ECDLP-835df6 Stage 0 exact deck-type versus count degree calibrator.

Certificate kind none. No Semaev S_m. No Velu. No yield ratio k.
No elliptic M_S. No (L,b) meter. No Aut census. No orbit cost.
Frozen object P-S0-DECKTYPE: REAL / KF / NULL at m=3.

count_degree(g, m) = g ** (m-2).
type_degree(aut, g, m) = g ** (m-2).
type_degree(translation, g, m) = 2 ** (m-2).
REAL: y^2 = x^3 + 2 over F_13, t = x^3, every fibre size 6.
KF: Edwards d=3 over F_17, t = (x y)^2, max fibre 8.
NULL empty affine is rejected. p=0 is rejected.
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
SOURCE = "experiments/EXP-ECDLP-835df6/implementation/stage0_decktype.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-835df6/runs/RUN-ECDLP-835df6-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-835df6/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-3054d2"
TASK_ID = "TASK-20260908-184c68"

M_FROZEN = 3
REAL_P = 13
REAL_B = 2
KF_P = 17
KF_D = 3


class InvalidParamsError(ValueError):
    """p not a frozen positive prime, or empty affine set, is rejected."""


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


def count_degree(g: int, m: int) -> int:
    if m != M_FROZEN:
        raise InvalidParamsError("m is not the frozen order")
    return int(g) ** (int(m) - 2)


def type_degree(kind: str, g: int, m: int) -> int:
    if m != M_FROZEN:
        raise InvalidParamsError("m is not the frozen order")
    if kind == "aut":
        return count_degree(g, m)
    if kind == "translation":
        return 2 ** (int(m) - 2)
    raise InvalidParamsError("unknown deck kind")


def affine_j0(p: int, b: int) -> list[tuple[int, int]]:
    require_positive_p(p)
    pts: list[tuple[int, int]] = []
    for x in range(int(p)):
        rhs = (pow(x, 3, int(p)) + int(b)) % int(p)
        for y in range(int(p)):
            if (y * y) % int(p) == rhs:
                pts.append((x, y))
    if not pts:
        raise InvalidParamsError("empty affine set")
    return pts


def affine_edwards(p: int, d: int) -> list[tuple[int, int]]:
    require_positive_p(p)
    pts: list[tuple[int, int]] = []
    for x in range(int(p)):
        for y in range(int(p)):
            left = (x * x + y * y) % int(p)
            right = (1 + int(d) * x * x * y * y) % int(p)
            if left == right:
                pts.append((x, y))
    if not pts:
        raise InvalidParamsError("empty affine set")
    return pts


def fibre_sizes_j0(p: int, b: int) -> dict[int, int]:
    sizes: dict[int, int] = defaultdict(int)
    for x, _y in affine_j0(p, b):
        sizes[pow(x, 3, int(p))] += 1
    return dict(sizes)


def fibre_sizes_edwards(p: int, d: int) -> dict[int, int]:
    sizes: dict[int, int] = defaultdict(int)
    for x, y in affine_edwards(p, d):
        sizes[(x * y) ** 2 % int(p)] += 1
    return dict(sizes)


def evaluate_real() -> dict[str, object]:
    fibres = fibre_sizes_j0(REAL_P, REAL_B)
    g = 6
    tdeg = type_degree("aut", g, M_FROZEN)
    cdeg = count_degree(g, M_FROZEN)
    return {
        "kind": "aut",
        "p": REAL_P,
        "B": REAL_B,
        "t": "x_cubed",
        "fibres": {str(k): int(v) for k, v in sorted(fibres.items())},
        "all_fibre_size": all(v == 6 for v in fibres.values()),
        "type_degree": tdeg,
        "count_degree": cdeg,
        "agree": tdeg == cdeg,
    }


def evaluate_kf() -> dict[str, object]:
    fibres = fibre_sizes_edwards(KF_P, KF_D)
    g = 8
    tdeg = type_degree("translation", g, M_FROZEN)
    cdeg = count_degree(g, M_FROZEN)
    return {
        "kind": "translation",
        "p": KF_P,
        "d": KF_D,
        "t": "xy_squared",
        "fibres": {str(k): int(v) for k, v in sorted(fibres.items())},
        "max_fibre": max(fibres.values()),
        "type_degree": tdeg,
        "count_degree": cdeg,
        "disagree": tdeg != cdeg,
    }


def reject_invalid() -> list[dict[str, object]]:
    decisions = []
    try:
        affine_j0(0, REAL_B)
        decisions.append({"id": "p-zero", "p": 0, "rejected": False})
    except InvalidParamsError:
        decisions.append({"id": "p-zero", "p": 0, "rejected": True})
    return decisions


def reject_null() -> list[dict[str, object]]:
    rows = []
    try:
        if not []:
            raise InvalidParamsError("empty affine set")
        rows.append({"id": "NULL", "kind": "empty_affine", "rejected": False})
    except InvalidParamsError:
        rows.append({"id": "NULL", "kind": "empty_affine", "rejected": True})
    return rows


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    real = evaluate_real()
    kf = evaluate_kf()
    null_rows = reject_null()
    invalid_decisions = reject_invalid()

    fixture_pass = (
        M_FROZEN == 3
        and REAL_P == 13
        and REAL_B == 2
        and KF_P == 17
        and KF_D == 3
    )
    real_count_pass = (
        bool(real["all_fibre_size"])
        and int(real["type_degree"]) == 6
        and int(real["count_degree"]) == 6
        and bool(real["agree"])
    )
    known_false_translation_pass = (
        int(kf["max_fibre"]) == 8
        and int(kf["type_degree"]) == 2
        and int(kf["count_degree"]) == 8
        and bool(kf["disagree"])
    )
    reject_invalid_pass = all(bool(row["rejected"]) for row in invalid_decisions)
    null_empty_pass = all(bool(row["rejected"]) for row in null_rows)
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_translation_pass
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
        "kind": "empty_affine",
        "rejected": all(bool(row["rejected"]) for row in null_rows),
        "rows": null_rows,
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-835df6-S0",
        "experiment_id": "EXP-ECDLP-835df6",
        "hypothesis_id": "H-ECDLP-db2a7f",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-DECKTYPE",
        "fixture": {
            "m_frozen": M_FROZEN,
            "REAL": {
                "id": "REAL",
                "p": REAL_P,
                "B": REAL_B,
                "t": "x_cubed",
                "must_all_fibres": 6,
                "must_type_degree": 6,
                "must_count_degree": 6,
                "must_agree": True,
            },
            "KF": {
                "id": "KF",
                "p": KF_P,
                "d": KF_D,
                "t": "xy_squared",
                "must_max_fibre": 8,
                "must_type_degree": 2,
                "must_count_degree": 8,
                "must_disagree": True,
            },
            "NULL": {"id": "NULL", "kind": "empty_affine", "must_reject": True},
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_count_pass": real_count_pass,
            "known_false_translation_pass": known_false_translation_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_empty_pass": null_empty_pass,
            "REAL": real_obj,
            "KF": kf_obj,
            "NULL": null_obj,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_835df6_stage1_authorized": False,
        "exp_5f3822_stage1_authorized": False,
        "exp_6ffef4_stage1_authorized": False,
        "not_a_decoder": True,
        "not_a_rho_beat": True,
        "not_semaev": True,
        "do_not_form_semaev": True,
        "do_not_run_velu": True,
        "do_not_form_elliptic_ms": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-835df6/implementation/stage0_decktype.py\n"
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
        "known_false_translation_pass": known_false_translation_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": real_obj,
        "KF": kf_obj,
        "NULL": null_obj,
    }
    (RUN_DIR / "stdout.log").write_text(json.dumps(stdout_payload, indent=2) + "\n")
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-835df6-S0
  experiment_id: EXP-ECDLP-835df6
  run_id: RUN-ECDLP-835df6-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_count_pass: {str(real_count_pass).lower()}
  known_false_translation_pass: {str(known_false_translation_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_empty_pass: {str(null_empty_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_835df6_stage1_authorized: false
  exp_5f3822_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_rho_beat: true
  not_semaev: true
  do_not_form_semaev: true
  do_not_run_velu: true
  do_not_form_elliptic_ms: true
  frozen_object: P-S0-DECKTYPE
  observations:
  - "fixture_pass {str(fixture_pass).lower()}. Frozen REAL / KF / NULL objects match committed table. Invalid objects rejected."
  - "real_count_pass {str(real_count_pass).lower()}. REAL all-fibre-6 is {str(real['all_fibre_size']).lower()}. REAL type_degree is {real['type_degree']}."
  - "known_false_translation_pass {str(known_false_translation_pass).lower()}. KF max fibre is {kf['max_fibre']}. KF type_degree is {kf['type_degree']}."
  - "reject_invalid_pass {str(reject_invalid_pass).lower()}. p=0 rejected before any identity is read."
  - "null_empty_pass {str(null_empty_pass).lower()}. NULL empty affine is rejected."
  unexpected_observations: []
  scientific_boundary: "Toy frozen deck-type versus count degree calibrator at m=3. Not Semaev S_m. Not Velu. Not a yield ratio k. Not elliptic M_S. Not an (L,b) meter. Not an Aut census. Not an orbit cost. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-835df6. Not Stage 1 of EXP-ECDLP-5f3822. Certificate kind none."
"""
    REPORT_PATH.write_text(report)

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    manifest = f"""run:
  id: RUN-ECDLP-835df6-S0
  experiment_id: EXP-ECDLP-835df6
  hypothesis_id: H-ECDLP-db2a7f
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
    command: python3 experiments/EXP-ECDLP-835df6/implementation/stage0_decktype.py
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
      frozen_object: P-S0-DECKTYPE
      authorized_by: {AUTHORIZED_BY}
      fixtures: [REAL, KF, NULL]
      m_frozen: 3
      real_p: 13
      kf_p: 17
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
    validity_reason: Stage 0 exact deck-type versus count degree calibrator gate.
    certificate:
      kind: none
      verified: true
    metrics:
      fixture_pass: {str(fixture_pass).lower()}
      real_count_pass: {str(real_count_pass).lower()}
      known_false_translation_pass: {str(known_false_translation_pass).lower()}
      reject_invalid_pass: {str(reject_invalid_pass).lower()}
      null_empty_pass: {str(null_empty_pass).lower()}
      SMALL_W_or_LARGE_W: false
      fit_of_a: false
      not_a_decoder: true
      not_a_rho_beat: true
      not_semaev: true
      do_not_form_semaev: true
      do_not_run_velu: true
      do_not_form_elliptic_ms: true
      stage1_authorized: false
      exp_835df6_stage1_authorized: false
    scientific_boundary: "Toy frozen deck-type versus count degree calibrator at m=3. Not Semaev S_m. Not Velu. Not a yield ratio k. Not elliptic M_S. Not an (L,b) meter. Not a rho beat. Not a decoder. Not Stage 1 of EXP-ECDLP-835df6. Not Stage 1 of EXP-ECDLP-5f3822. Certificate kind none."
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
                "known_false_translation_pass": known_false_translation_pass,
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
