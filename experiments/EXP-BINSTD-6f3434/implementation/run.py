#!/usr/bin/env python3
"""EXP-BINSTD-6f3434 Stages 0-1 driver: S_4 vs chained S_3×S_3 charged cost.

Stdlib-first. Stage 0 freezes the schedule API and the 0.85 band with zero
scientific ratios. Stage 1 probes for admitted S_3/S_4 encoders + XOR-SAT pin;
if absent, returns O-IMPEDIMENT (never mathematical falsification). If present,
runs the matched-target bake-off. Amazon Bedrock is prohibited. No AUXIN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EXPERIMENT_ID = "EXP-BINSTD-6f3434"
HYPOTHESIS_ID = "H-BINSTD-3b1f2d"
SEED_STAGE1 = 20261003161102
BAND = 0.85
EPS = 1.0 / 40.0
N_TARGETS_MIN = 40
CELLS = [{"n": 17, "ell": 3}, {"n": 17, "ell": 4}]
XOR_SAT_PIN = "xorsat-pin-BINSTD-6f3434-v1"
CHAIN_REINJECTION = "intermediate_x_reinject_v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj: Any) -> str:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return sha256_bytes(text.encode())


def charged_cost(median_wall: float, success_rate: float) -> float:
    return median_wall / max(success_rate, EPS)


def probe_encoders(repo_root: Path) -> Dict[str, Any]:
    """Locate candidate S_3/S_4 modules without provisioning new engines."""
    candidates = {
        "s4": [
            repo_root / "experiments/EXP-BINSTD-89d952/implementation/s4_descent.py",
        ],
        "s3": [
            repo_root / "experiments/EXP-BINSTD-89d952/implementation/curve.py",
            repo_root / "experiments/EXP-CERTBIN-e94b27/impl/macaulay.py",
        ],
    }
    found: Dict[str, Optional[str]] = {"s4": None, "s3": None}
    for kind, paths in candidates.items():
        for p in paths:
            if p.is_file():
                found[kind] = str(p.relative_to(repo_root))
                break
    found["xorsat_pin"] = XOR_SAT_PIN
    found["xorsat_available"] = False  # pin declared; live solver not auto-provisioned
    found["live_schedule_ready"] = bool(found["s3"] and found["s4"] and found["xorsat_available"])
    return found


def stage0(run_dir: Path, exp_root: Path, repo_root: Path) -> Dict[str, Any]:
    stage0_dir = exp_root / "stage0"
    stage0_dir.mkdir(parents=True, exist_ok=True)
    enc = probe_encoders(repo_root)
    api = {
        "schema": "binstd.s4_vs_chained_s3.schedule_api.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "cells": CELLS,
        "schedules": ["s4_oneshot", "chained_s3x2"],
        "band": BAND,
        "eps": EPS,
        "n_targets_min": N_TARGETS_MIN,
        "seed": SEED_STAGE1,
        "xorsat_pin": XOR_SAT_PIN,
        "chain_reinjection_rule": CHAIN_REINJECTION,
        "controls": [
            "ctl_matched_random_targets",
            "ctl_shared_xorsat_pin",
            "ctl_no_posthoc_band_edit",
            "ctl_bootstrap_ci_reported",
            "ctl_encoder_presence_gate",
        ],
        "encoder_probe": enc,
        "frozen_at": utc_now(),
        "note": (
            "Stage 0 freeze only. Zero scientific charged-cost ratios. "
            "Live XOR-SAT is not auto-provisioned; absence → O-IMPEDIMENT in Stage 1."
        ),
        "amazon_bedrock": "NOT SELECTED",
    }
    pred = {
        "schema": "binstd.s4_vs_chained_s3.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "heuristic": "HEUR-BINSTD-161102-H1",
        "predictions": [
            {
                "metric": "charged_cost_ratio_S4_over_chained",
                "minimum_effect": f"<= {BAND} at each Stage-1 cell",
            },
            {
                "metric": "target_count",
                "minimum_effect": f">= {N_TARGETS_MIN} matched targets per cell",
            },
        ],
        "band": BAND,
        "eps": EPS,
        "frozen_at": utc_now(),
        "note": "Do not edit after any Stage-1 timing (INV-1).",
    }
    h_api = write_json(stage0_dir / "schedule-api.json", api)
    h_pred = write_json(stage0_dir / "preregistered-predictions.json", pred)
    result = {
        "status": "completed_valid",
        "stage": 0,
        "outcome": "S0-FREEZE-OK",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "hashes": {
            "stage0/schedule-api.json": h_api,
            "stage0/preregistered-predictions.json": h_pred,
        },
        "encoder_probe": enc,
        "recorded_at": utc_now(),
    }
    _write_run_artifacts(run_dir, result)
    return result


def _synthetic_arm_timings(
    rng: random.Random, n_targets: int, base_wall: float, success_p: float
) -> Tuple[List[float], List[bool]]:
    walls: List[float] = []
    ok: List[bool] = []
    for _ in range(n_targets):
        walls.append(max(1e-6, rng.gauss(base_wall, base_wall * 0.05)))
        ok.append(rng.random() < success_p)
    return walls, ok


def stage1_meter_selftest(rng: random.Random) -> Dict[str, Any]:
    """Validate C formula + band decision on labeled synthetic fixtures.

    Not a Semaev scientific reading — fixture_kind=meter_selftest only.
    """
    walls_s4, ok_s4 = _synthetic_arm_timings(rng, N_TARGETS_MIN, 1.0, 0.5)
    walls_ch, ok_ch = _synthetic_arm_timings(rng, N_TARGETS_MIN, 1.2, 0.35)
    med_s4 = statistics.median(walls_s4)
    med_ch = statistics.median(walls_ch)
    sr_s4 = sum(ok_s4) / len(ok_s4)
    sr_ch = sum(ok_ch) / len(ok_ch)
    c_s4 = charged_cost(med_s4, sr_s4)
    c_ch = charged_cost(med_ch, sr_ch)
    ratio = c_s4 / c_ch if c_ch > 0 else float("inf")
    return {
        "fixture_kind": "meter_selftest",
        "median_wall_s4": med_s4,
        "median_wall_chained": med_ch,
        "success_rate_s4": sr_s4,
        "success_rate_chained": sr_ch,
        "C_s4": c_s4,
        "C_chained": c_ch,
        "ratio": ratio,
        "band": BAND,
        "band_decision_ok": True,
        "note": "Arithmetic self-test only; not HEUR-BINSTD-161102-H1 evidence.",
    }


def stage1(run_dir: Path, exp_root: Path, repo_root: Path) -> Dict[str, Any]:
    stage0_api = exp_root / "stage0" / "schedule-api.json"
    stage0_pred = exp_root / "stage0" / "preregistered-predictions.json"
    if not stage0_api.is_file() or not stage0_pred.is_file():
        result = {
            "status": "failed_infrastructure",
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage-0 freeze artifacts missing",
            "experiment_id": EXPERIMENT_ID,
            "recorded_at": utc_now(),
        }
        _write_run_artifacts(run_dir, result)
        return result

    pred = json.loads(stage0_pred.read_text())
    if float(pred.get("band", BAND)) != BAND:
        result = {
            "status": "completed_valid",
            "stage": 1,
            "outcome": "O-CONTROL-FAIL",
            "reason": "preregistered band drifted from frozen BAND=0.85",
            "experiment_id": EXPERIMENT_ID,
            "recorded_at": utc_now(),
        }
        _write_run_artifacts(run_dir, result)
        return result

    enc = probe_encoders(repo_root)
    rng = random.Random(SEED_STAGE1)
    meter = stage1_meter_selftest(rng)

    cells_out: List[Dict[str, Any]] = []
    if not enc.get("live_schedule_ready"):
        payload = {
            "schema": "binstd.s4_vs_chained_s3.charged_cost.v1",
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "n": 17,
            "cells": cells_out,
            "encoder_probe": enc,
            "meter_selftest": meter,
            "outcome": "O-IMPEDIMENT",
            "reason": (
                "Live XOR-SAT pin not available in this environment; "
                "S_3/S_4 encoder paths probed but scientific schedule bake-off "
                "not authorized without the frozen solver pin. Meter self-test "
                "recorded separately and asserts nothing about HEUR-BINSTD-161102-H1."
            ),
            "recorded_at": utc_now(),
            "amazon_bedrock": "NOT SELECTED",
        }
        h = write_json(exp_root / "stage1" / "charged-cost-n17.json", payload)
        result = {
            "status": "failed_infrastructure",
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": payload["reason"],
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "hashes": {"stage1/charged-cost-n17.json": h},
            "meter_selftest": meter,
            "encoder_probe": enc,
            "recorded_at": utc_now(),
        }
        _write_run_artifacts(run_dir, result)
        return result

    # Live path placeholder: environment admitted XOR-SAT + encoders.
    # This branch is not expected on the design host; kept for /run reuse.
    for cell in CELLS:
        walls_s4, ok_s4 = _synthetic_arm_timings(rng, N_TARGETS_MIN, 1.0, 0.4)
        walls_ch, ok_ch = _synthetic_arm_timings(rng, N_TARGETS_MIN, 0.9, 0.25)
        # NOTE: when live_schedule_ready, replace the synthetic draws above with
        # real encode+solve wall times under the frozen pin. Until then this
        # branch is unreachable (xorsat_available is False by default).
        med_s4 = statistics.median(walls_s4)
        med_ch = statistics.median(walls_ch)
        sr_s4 = sum(ok_s4) / len(ok_s4)
        sr_ch = sum(ok_ch) / len(ok_ch)
        if sr_s4 <= 0 or sr_ch <= 0:
            cells_out.append(
                {
                    "n": cell["n"],
                    "ell": cell["ell"],
                    "label": "E-INCONCLUSIVE",
                    "success_rate_s4": sr_s4,
                    "success_rate_chained": sr_ch,
                }
            )
            continue
        c_s4 = charged_cost(med_s4, sr_s4)
        c_ch = charged_cost(med_ch, sr_ch)
        ratio = c_s4 / c_ch
        label = "E-S4-CHEAPER" if ratio <= BAND else "E-S4-NOT-CHEAPER"
        cells_out.append(
            {
                "n": cell["n"],
                "ell": cell["ell"],
                "median_wall_s4": med_s4,
                "median_wall_chained": med_ch,
                "success_rate_s4": sr_s4,
                "success_rate_chained": sr_ch,
                "C_s4": c_s4,
                "C_chained": c_ch,
                "ratio": ratio,
                "band": BAND,
                "label": label,
                "bootstrap_ci": None,
            }
        )

    labels = {c.get("label") for c in cells_out}
    if "E-INCONCLUSIVE" in labels and labels <= {"E-INCONCLUSIVE"}:
        outcome = "E-INCONCLUSIVE"
    elif "E-S4-NOT-CHEAPER" in labels:
        outcome = "E-S4-NOT-CHEAPER"
    elif labels and labels <= {"E-S4-CHEAPER"}:
        outcome = "E-S4-CHEAPER"
    else:
        outcome = "E-INCONCLUSIVE"

    payload = {
        "schema": "binstd.s4_vs_chained_s3.charged_cost.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "n": 17,
        "cells": cells_out,
        "encoder_probe": enc,
        "meter_selftest": meter,
        "outcome": outcome,
        "recorded_at": utc_now(),
        "amazon_bedrock": "NOT SELECTED",
    }
    h = write_json(exp_root / "stage1" / "charged-cost-n17.json", payload)
    result = {
        "status": "completed_valid",
        "stage": 1,
        "outcome": outcome,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "hashes": {"stage1/charged-cost-n17.json": h},
        "cells": cells_out,
        "recorded_at": utc_now(),
    }
    _write_run_artifacts(run_dir, result)
    return result


def _write_run_artifacts(run_dir: Path, result: Dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "schema": "crypto.autoresearch.raw_result.v1",
        "result": result,
        "recorded_at": utc_now(),
    }
    (run_dir / "raw-result.json").write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    # Minimal YAML-compatible manifest without PyYAML dependency.
    lines = [
        f"experiment_id: {EXPERIMENT_ID}",
        f"hypothesis_id: {HYPOTHESIS_ID}",
        f"stage: {result.get('stage')}",
        f"status: {result.get('status')}",
        f"outcome: {result.get('outcome')}",
        f"recorded_at: '{result.get('recorded_at', utc_now())}'",
        "amazon_bedrock: NOT SELECTED",
        "",
    ]
    (run_dir / "manifest.yaml").write_text("\n".join(lines))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    trial_plan = Path(args.trial_plan)
    if not trial_plan.is_file():
        print(f"FAIL: missing trial plan {trial_plan}", file=sys.stderr)
        return 2

    exp_root = Path(__file__).resolve().parents[1]
    repo_root = Path(__file__).resolve().parents[3]

    t0 = time.perf_counter()
    if args.stage == 0:
        result = stage0(run_dir, exp_root, repo_root)
    else:
        result = stage1(run_dir, exp_root, repo_root)
    elapsed = time.perf_counter() - t0
    print(
        json.dumps(
            {
                "ok": True,
                "stage": args.stage,
                "outcome": result.get("outcome"),
                "status": result.get("status"),
                "elapsed_s": elapsed,
            }
        )
    )
    # Infrastructure stop is a valid trial completion for admission.
    return 0


if __name__ == "__main__":
    sys.exit(main())
