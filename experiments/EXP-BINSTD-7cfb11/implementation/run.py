#!/usr/bin/env python3
"""EXP-BINSTD-7cfb11 Stages 0-1 launcher: GF(2) sparse fill-in vs surplus.

Stage 0: freeze V-cardinality / surplus / β / seeds / sparse-LA pin; dual probe.
Stage 1: n=17 relation-like + ER-null fill-in at s∈{1.0,1.25,1.5,2.0}; dual meters.

Pure Python. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from matrices import cell_seed, erdos_renyi, nrows_for_surplus, relation_like  # noqa: E402
from route_bits import gauss_jordan_fill_in as fill_bits  # noqa: E402
from route_sets import gauss_jordan_fill_in as fill_sets  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-7cfb11"
HYPOTHESIS_ID = "H-BINSTD-480fb5"
APPROVED_BY = "DEC-20261003-40fe41"
EXP_ROOT = Path(__file__).resolve().parents[1]

# Frozen pins (also written to stage0/preregistered-predictions.json).
FB_SIZE = {17: 24, 23: 32, 31: 40}
ROW_WEIGHT = 4
SURPLUS = [1.0, 1.25, 1.5, 2.0]
BETA = 16.0
RELATION_SEED = 2026100301
ER_SEED = 2026100302
PROBE_SEED = 2026100303
MIN_SURPLUS_COMPLETED = 3
AUTHORIZED_STAGE1_N = (17,)
KIND_REL = 0
KIND_ER = 1

OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def write_yaml_manifest(path: Path, obj: dict) -> None:
    lines = ["---"]
    for key, value in obj.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif value is None:
            rendered = "null"
        elif isinstance(value, (int, float)):
            rendered = str(value)
        else:
            rendered = json.dumps(value)
        lines.append(f"{key}: {rendered}")
    write_text(path, "\n".join(lines) + "\n")


def dual_measure(sets_rows: list[set[int]], bits_rows: list[int], ncols: int) -> dict:
    a = fill_sets(sets_rows, ncols)
    b = fill_bits(bits_rows, ncols)
    agree = (
        a["nnz_initial"] == b["nnz_initial"]
        and a["nnz_after"] == b["nnz_after"]
        and a["rank"] == b["rank"]
        and a["fill_in_ratio"] == b["fill_in_ratio"]
    )
    return {"sets": a, "bits": b, "agree": agree, "fill_in_ratio": a["fill_in_ratio"] if agree else None}


def measure_cell(n: int, surplus: float, surplus_index: int, kind: str) -> dict:
    ncols = FB_SIZE[n]
    nrows = nrows_for_surplus(ncols, surplus)
    p = ROW_WEIGHT / ncols
    if kind == "relation":
        seed = cell_seed(RELATION_SEED, n, surplus_index, KIND_REL)
        sets_rows, bits_rows = relation_like(nrows, ncols, ROW_WEIGHT, seed)
    elif kind == "er_null":
        seed = cell_seed(ER_SEED, n, surplus_index, KIND_ER)
        sets_rows, bits_rows = erdos_renyi(nrows, ncols, p, seed)
    else:
        raise ValueError(kind)
    dual = dual_measure(sets_rows, bits_rows, ncols)
    f = dual["fill_in_ratio"]
    band_hold = None if f is None else (f <= BETA)
    return {
        "n": n,
        "fb_size": ncols,
        "surplus": surplus,
        "nrows": nrows,
        "row_weight": ROW_WEIGHT,
        "kind": kind,
        "seed": seed,
        "dual": dual,
        "fill_in_ratio": f,
        "beta": BETA,
        "band_hold": band_hold,
        "amazon_bedrock": "NOT_USED",
    }


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    pin = {
        "sparse_la_pin": (
            "GF(2) Gauss-Jordan: left-to-right first unused pivot row; "
            "XOR-clear that column from every other row; F = nnz_after / nnz_initial."
        ),
        "fb_size": FB_SIZE,
        "row_weight": ROW_WEIGHT,
        "surplus": SURPLUS,
        "beta": BETA,
        "relation_seed": RELATION_SEED,
        "er_seed": ER_SEED,
        "probe_seed": PROBE_SEED,
        "min_surplus_completed": MIN_SURPLUS_COMPLETED,
        "authorized_stage1_n": list(AUTHORIZED_STAGE1_N),
        "route_a": "implementation/route_sets.py",
        "route_b": "implementation/route_bits.py",
        "no_magma_sage_auxin": True,
        "amazon_bedrock": "NOT_USED",
    }
    pred = {
        "heuristic_id": "HEUR-BINSTD-7def74-H1",
        "quantity": "fill_in_ratio_F",
        "formula": "F := nnz_after_elim / nnz_initial <= beta",
        "beta": BETA,
        "source": "IDEA-20261002-7def74 / H-BINSTD-480fb5; frozen before Stage 1",
        "surplus": SURPLUS,
        "fb_size": FB_SIZE,
        "row_weight": ROW_WEIGHT,
        "min_surplus_completed": MIN_SURPLUS_COMPLETED,
        "prediction_note": (
            "Band is pre-registered from the idea's sparse-elim transfer hypothesis "
            "at toys, not from any run of this EXP."
        ),
        "amazon_bedrock": "NOT_USED",
    }
    # Probe: 8x8 identity (F=1) plus a 6x8 weight-3 relation-like fixture.
    ident_sets = [{i} for i in range(8)]
    ident_bits = [1 << i for i in range(8)]
    ident = dual_measure(ident_sets, ident_bits, 8)
    fixture_sets, fixture_bits = relation_like(6, 8, 3, PROBE_SEED)
    fixture = dual_measure(fixture_sets, fixture_bits, 8)
    twin_ok = bool(ident["agree"] and fixture["agree"] and ident["fill_in_ratio"] == 1.0)
    probe = {
        "identity_8x8": ident,
        "relation_like_6x8_w3": fixture,
        "twin_ok": twin_ok,
        "identity_F_is_1": ident["fill_in_ratio"] == 1.0,
    }
    write_json(EXP_ROOT / "stage0" / "la-pin.json", pin)
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    write_json(EXP_ROOT / "stage0" / "probe.json", probe)
    outcome = "O-STAGE0-OK" if twin_ok else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": outcome,
        "twin_ok": twin_ok,
        "probe": probe,
        "pins": pin,
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "amazon_bedrock": "NOT_USED",
        "elapsed_s": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "id": "RUN-BINSTD-d1729a",
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "status": "completed" if twin_ok else "invalid",
            "outcome": outcome,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not pred_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze",
            "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "id": "RUN-BINSTD-b8be43",
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "status": "failed_infrastructure",
                "outcome": "O-IMPEDIMENT",
                "amazon_bedrock": "NOT_USED",
            },
        )
        write_text(EXP_ROOT / "RESULTS.md", "# EXP-BINSTD-7cfb11 RESULTS\n\nO-IMPEDIMENT: missing Stage-0 freeze.\n")
        return raw
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    if pred.get("beta") != BETA:
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-ARTIFACT",
            "reason": "beta edited after freeze",
            "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "id": "RUN-BINSTD-b8be43",
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "status": "invalid",
                "outcome": "O-ARTIFACT",
                "amazon_bedrock": "NOT_USED",
            },
        )
        write_text(EXP_ROOT / "RESULTS.md", "# EXP-BINSTD-7cfb11 RESULTS\n\nO-ARTIFACT: beta edited after freeze.\n")
        return raw

    panels: dict[str, Any] = {}
    control_rows = []
    artifact = False
    surplus_completed = 0
    any_break = False
    n = 17
    for idx, s in enumerate(SURPLUS):
        rel = measure_cell(n, s, idx, "relation")
        er = measure_cell(n, s, idx, "er_null")
        key = f"n{n}_s{s}"
        if not rel["dual"]["agree"] or not er["dual"]["agree"]:
            artifact = True
        if rel["fill_in_ratio"] is not None and rel["dual"]["agree"]:
            surplus_completed += 1
            if rel["band_hold"] is False:
                any_break = True
        panels[key] = {"relation": rel, "er_null": er}
        control_rows.append(
            {
                "n": n,
                "surplus": s,
                "F_relation": rel["fill_in_ratio"],
                "F_er_null": er["fill_in_ratio"],
                "agree_relation": rel["dual"]["agree"],
                "agree_er": er["dual"]["agree"],
                "band_hold_relation": rel["band_hold"],
            }
        )

    if artifact:
        outcome = "O-ARTIFACT"
        meaning = "Dual-route nnz/rank/F disagreement on a Stage-1 cell."
    elif surplus_completed < MIN_SURPLUS_COMPLETED:
        outcome = "O-INCONCLUSIVE"
        meaning = f"Only {surplus_completed} of 4 surplus levels completed."
    elif any_break:
        outcome = "O-FAIL-BAND"
        meaning = "F > beta at a completed n=17 surplus (LA-fill-in-superlinear-in-surplus at this scale)."
    else:
        outcome = "O-SUPPORT"
        meaning = "F <= beta at every completed n=17 surplus with dual agreement (>=3 levels)."

    write_json(EXP_ROOT / "stage1" / "panels.json", panels)
    write_json(
        EXP_ROOT / "stage1" / "control-table.json",
        {"rows": control_rows, "beta": BETA, "n": 17, "amazon_bedrock": "NOT_USED"},
    )
    results = "\n".join(
        [
            "# EXP-BINSTD-7cfb11 RESULTS",
            "",
            f"outcome: {outcome}",
            f"meaning: {meaning}",
            f"surplus_completed: {surplus_completed}",
            f"beta: {BETA}",
            "scope: toy n=17 GF(2) sparse matrices with frozen |FB|=24, w=4; not an ECDLP solve; no n>=131.",
            "amazon_bedrock: NOT_USED",
            "",
        ]
    )
    write_text(EXP_ROOT / "RESULTS.md", results)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "meaning": meaning,
        "surplus_completed": surplus_completed,
        "any_band_break": any_break,
        "beta": BETA,
        "n": 17,
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "amazon_bedrock": "NOT_USED",
        "elapsed_s": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "id": "RUN-BINSTD-b8be43",
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "completed",
            "outcome": outcome,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True, choices=[0, 1])
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        raw = stage0(run_dir)
    else:
        raw = stage1(run_dir)
    print(json.dumps({"outcome": raw.get("outcome"), "stage": raw.get("stage")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — surface as O-IMPEDIMENT, never silent
        print(f"IMPEDIMENT: {exc}", file=sys.stderr)
        raise
