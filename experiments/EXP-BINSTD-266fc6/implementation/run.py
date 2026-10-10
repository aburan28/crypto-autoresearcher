#!/usr/bin/env python3
"""EXP-BINSTD-266fc6 Stages 0-1 driver: Part-2 CERT independence under planted faults.

Stdlib-only. Uses stubbed synthetic relation fixtures so Stages 0-1 admit and
run without Magma/Sage/curve libs. Live Part-2 relations may replace stubs
under a later amendment; this driver never claims O-SUPPORT or break.
Amazon Bedrock is prohibited. No AUXIN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

AXES = ("label", "quot", "bind")
CERT_NAMES = {
    "label": "CERT-LABEL",
    "quot": "CERT-QUOT",
    "bind": "CERT-BIND",
}
N_RELATIONS_STAGE1 = 50
SEED_STAGE1 = 2026100326715
EXPERIMENT_ID = "EXP-BINSTD-266fc6"
HYPOTHESIS_ID = "H-BINSTD-953387"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_relation(rng: random.Random, n: int, idx: int) -> Dict[str, Any]:
    """Synthetic triple-sealed relation fixture (stub, not a live Part-2 emit)."""
    payload = {
        "n": n,
        "idx": idx,
        "label_ok": True,
        "quot_ok": True,
        "bind_ok": True,
        "label_token": f"L-{n}-{idx}-{rng.getrandbits(32):08x}",
        "quot_token": f"Q-{n}-{idx}-{rng.getrandbits(32):08x}",
        "bind_token": f"B-{n}-{idx}-{rng.getrandbits(32):08x}",
        "fixture_kind": "stub_synthetic",
        "padding": "",
    }
    payload["bind_hash"] = sha256_bytes(
        f"{payload['label_token']}|{payload['quot_token']}|{payload['bind_token']}".encode()
    )
    return payload


def verify_certs(rel: Dict[str, Any]) -> Dict[str, bool]:
    """Predicate checks for the three certificate axes on a (possibly planted) relation."""
    bind_ok = (
        rel.get("bind_ok", False)
        and rel.get("bind_hash")
        == sha256_bytes(
            f"{rel['label_token']}|{rel['quot_token']}|{rel['bind_token']}".encode()
        )
    )
    return {
        "label": bool(rel.get("label_ok", False)),
        "quot": bool(rel.get("quot_ok", False)),
        "bind": bool(bind_ok),
    }


def plant_fault(rel: Dict[str, Any], axis: str) -> Dict[str, Any]:
    """Plant a single-axis defect without token side-effects on other axes.

    Stub predicates are independent flags (+ bind_hash for CERT-BIND). Token
    strings are left intact on label/quot plants so BIND's hash seal is not
    accidentally coupled; bind plants corrupt bind_hash only. Live Part-2
    may exhibit real coupling — that is an E-COUPLED reading under amendment.
    """
    out = dict(rel)
    if axis == "label":
        out["label_ok"] = False
    elif axis == "quot":
        out["quot_ok"] = False
    elif axis == "bind":
        out["bind_hash"] = "0" * 64
    elif axis == "triple":
        out["label_ok"] = False
        out["quot_ok"] = False
        out["bind_hash"] = "0" * 64
    elif axis == "null_off_cert":
        out["padding"] = "x" + out.get("padding", "")
    else:
        raise ValueError(f"unknown plant axis: {axis}")
    out["planted_axis"] = axis
    return out


def rates(accepts: List[bool]) -> float:
    if not accepts:
        return float("nan")
    return sum(1 for a in accepts if a) / len(accepts)


def stage0(run_dir: Path, exp_root: Path) -> Dict[str, Any]:
    stage0_dir = exp_root / "stage0"
    stage0_dir.mkdir(parents=True, exist_ok=True)
    api = {
        "schema": "binstd.part2.planted_fault_api.v1",
        "experiment_id": EXPERIMENT_ID,
        "axes": list(AXES),
        "certificates": [CERT_NAMES[a] for a in AXES],
        "controls": [
            "ctl_no_fault_all_green",
            "ctl_triple_fault_all_red",
            "ctl_single_axis_plant_label",
            "ctl_single_axis_plant_quot",
            "ctl_single_axis_plant_bind",
            "null_object_random_bit_flip_off_certificate_bytes",
        ],
        "fixture_kind": "stub_synthetic",
        "n_stage1": 17,
        "n_relations_min": N_RELATIONS_STAGE1,
        "thresholds": {
            "on_axis_reject_rate_min": 0.99,
            "off_axis_accept_rate_min": 0.99,
            "no_fault_red_rate_max": 0.01,
            "cross_talk_max": 0.05,
        },
        "frozen_at": utc_now(),
        "note": (
            "Stage 0 freeze only. Zero scientific certificate rates. "
            "Stub fixtures admit Stages 0-1 without curve libs."
        ),
    }
    pred = {
        "schema": "binstd.part2.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "heuristic": "HEUR-BINSTD-2b71e5-H1",
        "predictions": [
            {
                "metric": "on_axis_reject_rate",
                "minimum_effect": ">=0.99 per planted axis",
            },
            {
                "metric": "off_axis_accept_rate",
                "minimum_effect": ">=0.99 for each non-planted certificate",
            },
        ],
        "frozen_before_stage1": True,
        "frozen_at": utc_now(),
    }
    api_path = stage0_dir / "planted-fault-api.json"
    pred_path = stage0_dir / "preregistered-predictions.json"
    api_path.write_text(json.dumps(api, indent=2, sort_keys=True) + "\n")
    pred_path.write_text(json.dumps(pred, indent=2, sort_keys=True) + "\n")
    return {
        "stage": 0,
        "status": "completed_valid",
        "outcome": "S0-FREEZE-OK",
        "api_sha256": sha256_bytes(api_path.read_bytes()),
        "predictions_sha256": sha256_bytes(pred_path.read_bytes()),
        "scientific_rates": None,
        "asserts_nothing_about": [
            "O-SUPPORT",
            "break",
            "exponent",
            "n>=131 transfer",
            "Part-2 live relation ranks",
        ],
    }


def stage1(run_dir: Path, exp_root: Path) -> Dict[str, Any]:
    api_path = exp_root / "stage0" / "planted-fault-api.json"
    pred_path = exp_root / "stage0" / "preregistered-predictions.json"
    if not api_path.is_file() or not pred_path.is_file():
        return {
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage 0 freeze artifacts missing; not negative evidence",
        }
    rng = random.Random(SEED_STAGE1)
    n = 17
    relations = [make_relation(rng, n, i) for i in range(N_RELATIONS_STAGE1)]

    no_fault = [verify_certs(r) for r in relations]
    no_fault_red = {a: rates([not v[a] for v in no_fault]) for a in AXES}
    triple = [verify_certs(plant_fault(r, "triple")) for r in relations]
    triple_green = {a: rates([v[a] for v in triple]) for a in AXES}
    null_flip = [verify_certs(plant_fault(r, "null_off_cert")) for r in relations]
    null_red = {a: rates([not v[a] for v in null_flip]) for a in AXES}

    matrix: Dict[str, Dict[str, Any]] = {}
    for plant in AXES:
        planted = [plant_fault(r, plant) for r in relations]
        verified = [verify_certs(p) for p in planted]
        row = {}
        for cert in AXES:
            accept = rates([v[cert] for v in verified])
            row[cert] = {"accept_rate": accept, "reject_rate": 1.0 - accept}
        matrix[plant] = row

    on_axis_ok = all(matrix[a][a]["reject_rate"] >= 0.99 for a in AXES)
    off_axis_ok = all(
        matrix[plant][cert]["accept_rate"] >= 0.99
        for plant in AXES
        for cert in AXES
        if plant != cert
    )
    control_ok = (
        all(no_fault_red[a] <= 0.01 for a in AXES)
        and all(triple_green[a] <= 0.01 for a in AXES)
        and all(null_red[a] <= 0.01 for a in AXES)
    )

    if not control_ok:
        outcome, status, reading = "O-CONTROL-FAIL", "completed_valid", "controls_failed"
    elif on_axis_ok and off_axis_ok:
        outcome, status, reading = "E-INDEPENDENT", "completed_valid", "single_axis_plants_separate"
    else:
        outcome, status, reading = "E-COUPLED", "completed_valid", "cross_talk_or_on_axis_miss_named"

    stage1_dir = exp_root / "stage1"
    stage1_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = stage1_dir / "matrix-n17.json"
    payload = {
        "n": n,
        "n_relations": N_RELATIONS_STAGE1,
        "seed": SEED_STAGE1,
        "fixture_kind": "stub_synthetic",
        "matrix": matrix,
        "controls": {
            "no_fault_red_rate": no_fault_red,
            "triple_fault_green_rate": triple_green,
            "null_off_cert_red_rate": null_red,
        },
        "outcome": outcome,
        "reading": reading,
        "on_axis_ok": on_axis_ok,
        "off_axis_ok": off_axis_ok,
        "control_ok": control_ok,
    }
    matrix_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return {
        "stage": 1,
        "status": status,
        "outcome": outcome,
        "reading": reading,
        "n": n,
        "n_relations": N_RELATIONS_STAGE1,
        "matrix_sha256": sha256_bytes(matrix_path.read_bytes()),
        "on_axis_ok": on_axis_ok,
        "off_axis_ok": off_axis_ok,
        "control_ok": control_ok,
        "asserts_nothing_about": ["O-SUPPORT", "break", "exponent", "n>=131 transfer"],
    }


def write_artifacts(run_dir: Path, result: Dict[str, Any], stage: int) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "stage": stage,
        "recorded_at": utc_now(),
        "amazon_bedrock": "NOT SELECTED",
        "result": result,
    }
    (run_dir / "raw-result.json").write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    # Minimal YAML without PyYAML dependency in the driver.
    lines = [
        f"run_id: {run_dir.name}",
        f"experiment_id: {EXPERIMENT_ID}",
        f"hypothesis_id: {HYPOTHESIS_ID}",
        f"stage: {stage}",
        f"status: {result.get('status')}",
        f"outcome: {result.get('outcome')}",
        f"recorded_at: {utc_now()}",
        "certificate:",
        "  kind: none",
        "  note: Instrument / observational; no DLP solve certificate.",
        "amazon_bedrock: NOT SELECTED",
        "",
    ]
    (run_dir / "manifest.yaml").write_text("\n".join(lines))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    exp_root = Path(__file__).resolve().parents[1]
    result = stage0(run_dir, exp_root) if args.stage == 0 else stage1(run_dir, exp_root)
    write_artifacts(run_dir, result, args.stage)
    print(json.dumps({"ok": True, "stage": args.stage, "outcome": result.get("outcome")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
