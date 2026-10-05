#!/usr/bin/env python3
"""EXP-BINSTD-ffc4f4 Stages 0-1 launcher (frozen contract v1).

Successor of EXP-BINSTD-6c199f after EV-BINSTD-78ca0d / DEC-20261003-9575fd
(weaken). Independent replication of cell (17,3) under a disjoint catalog
seed and GP-seed roster. Stage-2 (n∈{19,23} GP/random + random-vs-random
null, ε=0.15) is specified in the contract and implemented here, but is
NOT admitted on trial-plan-v1.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n≥131
transfer. Do not re-run EXP-BINSTD-6c199f.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import encode_n_var  # noqa: E402
from gf2n import Field  # noqa: E402
from product_space import (  # noqa: E402
    dim_vv_agree,
    geometric_basis,
    random_basis,
)

EXPERIMENT_ID = "EXP-BINSTD-ffc4f4"
HYPOTHESIS_ID = "H-BINSTD-39a59f"
APPROVED_BY = "DEC-20261003-d4ae67"
PARENT_EXPERIMENT_ID = "EXP-BINSTD-6c199f"
PARENT_CATALOG_SEED = 2026100327
PARENT_GP_SEEDS = [3, 5, 7, 9, 11, 13, 17, 19, 21, 25, 27, 33]
EXP_ROOT = Path(__file__).resolve().parents[1]

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}

DELTA = 0.10
EPSILON = 0.15
CATALOG_SEED = 2026100331
MATCH_ATTEMPTS_PER_GP = 64
MIN_MATCHED_PAIRS = 8
GP_SEEDS = [35, 37, 39, 41, 43, 45, 49, 51, 53, 57, 59, 65]
AUTHORIZED_STAGE1_CELLS = [(17, 3)]
STAGE2_CELLS = [(19, 3), (23, 3)]
STAGE0_CATALOG_CELLS = [(17, 3), (17, 4), (19, 3), (23, 3)]
NULL_PAIR_COUNT = 12


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
    lines = []
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            s = str(v).replace("\n", " ")
            lines.append(f'{k}: "{s}"')
    write_text(path, "\n".join(lines) + "\n")


def _rng(seed: int):
    import numpy as np

    return np.random.default_rng(seed)


def _assert_disjoint_catalog() -> None:
    if CATALOG_SEED == PARENT_CATALOG_SEED:
        raise RuntimeError("catalog_seed collides with parent EXP-BINSTD-6c199f")
    if set(GP_SEEDS) & set(PARENT_GP_SEEDS):
        raise RuntimeError("GP seed roster collides with parent EXP-BINSTD-6c199f")


def measure_v(F, n: int, basis: list[int]) -> dict:
    da, db, dok = dim_vv_agree(basis, F)
    na, nb, nok, det = encode_n_var(F, CURVE_B[n], basis, XR[n])
    return {
        "basis": list(basis),
        "dimVV_a": da,
        "dimVV_b": db,
        "dimVV": da,
        "Nvar_a": na,
        "Nvar_b": nb,
        "N_var": na,
        "twin_ok": bool(dok and nok),
        "encode_details": {
            "lin_rank_a": det.get("lin_rank_a"),
            "lin_rank_b": det.get("lin_rank_b"),
            "nv0": det.get("nv0"),
        },
    }


def _median(values: list[float]) -> float:
    xs = sorted(values)
    if not xs:
        return float("nan")
    mid = len(xs) // 2
    if len(xs) % 2:
        return xs[mid]
    return 0.5 * (xs[mid - 1] + xs[mid])


def stage0(run_dir: Path) -> dict:
    _assert_disjoint_catalog()
    t0 = time.time()
    twin_ok = True
    cells: dict[str, Any] = {}
    for n, ell in STAGE0_CATALOG_CELLS:
        key = f"n{n}_l{ell}"
        F = Field(n, MODULI[n])
        gp_catalog = []
        for g in GP_SEEDS:
            basis = geometric_basis(ell, F, seed_elem=g)
            if len(basis) != ell:
                twin_ok = False
            m = measure_v(F, n, basis)
            if not m["twin_ok"]:
                twin_ok = False
            gp_catalog.append({"kind": f"geo_g{g}", "g": g, **m})
        probe_basis = geometric_basis(ell, F, seed_elem=GP_SEEDS[0])
        probe = measure_v(F, n, probe_basis)
        if not probe["twin_ok"]:
            twin_ok = False
        rng = _rng(CATALOG_SEED + 17 * n + ell)
        dim_gp0 = int(gp_catalog[0]["dimVV"])
        hit = 0
        for _ in range(64):
            rb = random_basis(ell, n, rng)
            m = measure_v(F, n, rb)
            if m["twin_ok"] and abs(int(m["dimVV"]) - dim_gp0) <= 1 and int(m["N_var"]) > 0:
                hit += 1
        cells[key] = {
            "n": n,
            "ell": ell,
            "gp_catalog": gp_catalog,
            "probe": {
                "basis": probe["basis"],
                "dimVV": {"a": probe["dimVV_a"], "b": probe["dimVV_b"]},
                "N_var": {"a": probe["Nvar_a"], "b": probe["Nvar_b"]},
                "twin_ok": probe["twin_ok"],
            },
            "match_feasibility_hits_per_64": hit,
            "authorized_stage1": (n, ell) in AUTHORIZED_STAGE1_CELLS,
            "specified_stage2": (n, ell) in STAGE2_CELLS,
            "stage1_admission_note": (
                None
                if (n, ell) in AUTHORIZED_STAGE1_CELLS
                else (
                    "Specified for Stage 2 (not admitted on trial-plan-v1)."
                    if (n, ell) in STAGE2_CELLS
                    else (
                        "Deferred: unstructured random dimVV support does not overlap "
                        "GP dimVV within ±1 at this (n,ell) on the frozen pin."
                        if hit == 0
                        else "Deferred off Stage-1 replication card."
                    )
                )
            ),
        }

    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "predecessor_experiment_id": PARENT_EXPERIMENT_ID,
        "predecessor_evidence_id": "EV-BINSTD-78ca0d",
        "predecessor_decision_id": "DEC-20261003-9575fd",
        "parent_catalog_seed_forbidden": PARENT_CATALOG_SEED,
        "delta": DELTA,
        "epsilon_null": EPSILON,
        "band_upper": 1.0 - DELTA,
        "min_matched_pairs": MIN_MATCHED_PAIRS,
        "match_rule": "|dimVV_GP - dimVV_rand| <= 1",
        "catalog_seed": CATALOG_SEED,
        "gp_seeds": GP_SEEDS,
        "parent_gp_seeds_forbidden": PARENT_GP_SEEDS,
        "match_attempts_per_gp": MATCH_ATTEMPTS_PER_GP,
        "authorized_stage1_cells": [
            {"n": n, "ell": ell} for n, ell in AUTHORIZED_STAGE1_CELLS
        ],
        "specified_stage2_cells": [
            {"n": n, "ell": ell} for n, ell in STAGE2_CELLS
        ],
        "encoder_pin": {
            "descend": "encode_s3.descend_s3",
            "n_var_twins": [
                "encode_s3._rank_and_pivot_vars_a",
                "encode_s3._rank_and_pivot_vars_b",
            ],
            "dim_vv_twins": [
                "product_space.dim_vv_path_a",
                "product_space.dim_vv_path_b",
            ],
        },
        "moduli": {str(k): hex(v) for k, v in MODULI.items()},
        "curve_B": CURVE_B,
        "xR": {str(k): hex(v) for k, v in XR.items()},
        "prediction": (
            f"FORALL Stage-1 cells {(17, 3)}: across >= {MIN_MATCHED_PAIRS} "
            f"GP/random pairs with |Δ dim(V·V)| <= 1, median "
            f"N_var(GP)/N_var(rand) <= {1.0 - DELTA} (= 1−δ with δ={DELTA}), "
            "OR label GP-not-cheaper-at-matched-product-dim / O-FAIL-BAND. "
            "Independent of EXP-BINSTD-6c199f catalog_seed 2026100327."
        ),
        "stage2_note": (
            "n∈{19,23} GP/random δ-band + random-vs-random null with ε="
            f"{EPSILON} is SPECIFIED in this contract and implemented under "
            "--stage 2, but NOT AUTHORIZED on trial-plan-v1 (Stages 0-1 only)."
        ),
        "amazon_bedrock": "NOT_USED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", prereg)
    write_json(
        EXP_ROOT / "stage0" / "v-catalog.json",
        {
            "cells": cells,
            "twin_ok": twin_ok,
            "catalog_seed": CATALOG_SEED,
            "parent_catalog_seed_forbidden": PARENT_CATALOG_SEED,
        },
    )
    status = "completed" if twin_ok else "artifact"
    outcome = "O-STAGE0-OK" if twin_ok else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": status,
        "outcome_hint": outcome,
        "twin_ok": twin_ok,
        "catalog_seed": CATALOG_SEED,
        "parent_catalog_seed_forbidden": PARENT_CATALOG_SEED,
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "freeze": {
            "preregistered_predictions": "stage0/preregistered-predictions.json",
            "v_catalog": "stage0/v-catalog.json",
        },
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "status": status,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def build_matched_pairs(n: int, ell: int, gp_catalog: list[dict], rng_salt: int) -> dict:
    F = Field(n, MODULI[n])
    rng = _rng(CATALOG_SEED + rng_salt + 1000 * n + ell)
    pairs = []
    twin_fail = False
    for gp in gp_catalog:
        if not gp.get("twin_ok", False):
            twin_fail = True
        dim_gp = int(gp["dimVV"])
        nvar_gp = int(gp["N_var"])
        matched = None
        for attempt in range(MATCH_ATTEMPTS_PER_GP):
            basis = random_basis(ell, n, rng)
            m = measure_v(F, n, basis)
            if not m["twin_ok"]:
                twin_fail = True
                continue
            if abs(int(m["dimVV"]) - dim_gp) <= 1 and int(m["N_var"]) > 0:
                ratio = float(nvar_gp) / float(m["N_var"]) if m["N_var"] else float("inf")
                matched = {
                    "gp_kind": gp["kind"],
                    "gp_g": gp.get("g"),
                    "gp_basis": gp["basis"],
                    "gp_dimVV": dim_gp,
                    "gp_N_var": nvar_gp,
                    "rand_basis": m["basis"],
                    "rand_dimVV": m["dimVV"],
                    "rand_N_var": m["N_var"],
                    "dimVV_delta": abs(int(m["dimVV"]) - dim_gp),
                    "ratio_GP_over_rand": ratio,
                    "twin_ok": True,
                    "match_attempt": attempt,
                }
                break
        if matched is not None:
            pairs.append(matched)
    ratios = [p["ratio_GP_over_rand"] for p in pairs if math.isfinite(p["ratio_GP_over_rand"])]
    median = _median(ratios)
    band_upper = 1.0 - DELTA
    enough = len(pairs) >= MIN_MATCHED_PAIRS
    in_band = enough and math.isfinite(median) and median <= band_upper
    return {
        "n": n,
        "ell": ell,
        "matched_pair_count": len(pairs),
        "min_matched_pairs": MIN_MATCHED_PAIRS,
        "pairs": pairs,
        "median_ratio_GP_over_rand": median,
        "band_upper": band_upper,
        "delta": DELTA,
        "in_band": in_band,
        "enough_pairs": enough,
        "twin_fail": twin_fail,
    }


def build_random_vs_random(n: int, ell: int) -> dict:
    F = Field(n, MODULI[n])
    rng = _rng(CATALOG_SEED + 9000 * n + ell)
    pairs = []
    twin_fail = False
    for i in range(NULL_PAIR_COUNT):
        a = measure_v(F, n, random_basis(ell, n, rng))
        b = measure_v(F, n, random_basis(ell, n, rng))
        if not a["twin_ok"] or not b["twin_ok"]:
            twin_fail = True
            continue
        if int(a["N_var"]) <= 0 or int(b["N_var"]) <= 0:
            continue
        ratio = float(a["N_var"]) / float(b["N_var"])
        pairs.append(
            {
                "i": i,
                "a_basis": a["basis"],
                "b_basis": b["basis"],
                "a_N_var": a["N_var"],
                "b_N_var": b["N_var"],
                "a_dimVV": a["dimVV"],
                "b_dimVV": b["dimVV"],
                "ratio": ratio,
                "abs_ratio_minus_1": abs(ratio - 1.0),
                "twin_ok": True,
            }
        )
    absdevs = [p["abs_ratio_minus_1"] for p in pairs]
    median_abs = _median(absdevs)
    enough = len(pairs) >= MIN_MATCHED_PAIRS
    in_band = enough and math.isfinite(median_abs) and median_abs <= EPSILON
    return {
        "n": n,
        "ell": ell,
        "pair_count": len(pairs),
        "min_pairs": MIN_MATCHED_PAIRS,
        "pairs": pairs,
        "median_abs_ratio_minus_1": median_abs,
        "epsilon": EPSILON,
        "in_band": in_band,
        "enough_pairs": enough,
        "twin_fail": twin_fail,
        "match_note": "random-vs-random matched on dim(V)=ell only (IDEA null)",
    }


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    cat_path = EXP_ROOT / "stage0" / "v-catalog.json"
    pre_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not cat_path.is_file() or not pre_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze files",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment"},
        )
        return raw

    catalog_doc = json.loads(cat_path.read_text(encoding="utf-8"))
    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    if float(pre.get("delta", -1)) != DELTA:
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "invalid",
            "outcome": "O-ARTIFACT",
            "reason": "delta drift vs frozen Stage-0 constant",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "invalid"},
        )
        return raw
    if int(pre.get("catalog_seed", -1)) != CATALOG_SEED or int(pre.get("catalog_seed", -1)) == PARENT_CATALOG_SEED:
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "invalid",
            "outcome": "O-ARTIFACT",
            "reason": "catalog_seed is parent seed or drifted",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "invalid"},
        )
        return raw

    panels: dict[str, Any] = {}
    any_twin_fail = False
    any_inconclusive = False
    all_in_band = True
    any_fail_band = False
    for n, ell in AUTHORIZED_STAGE1_CELLS:
        key = f"n{n}_l{ell}"
        cell = catalog_doc["cells"][key]
        panel = build_matched_pairs(n, ell, cell["gp_catalog"], rng_salt=0)
        panels[key] = panel
        if panel["twin_fail"]:
            any_twin_fail = True
        if not panel["enough_pairs"]:
            any_inconclusive = True
        if panel["enough_pairs"] and not panel["in_band"]:
            any_fail_band = True
            all_in_band = False
        elif panel["enough_pairs"] and panel["in_band"]:
            pass
        else:
            all_in_band = False

    if any_twin_fail:
        outcome = "O-ARTIFACT"
        status = "artifact"
    elif any_inconclusive:
        outcome = "O-INCONCLUSIVE"
        status = "completed"
    elif any_fail_band or not all_in_band:
        outcome = "O-FAIL-BAND"
        status = "completed"
    else:
        outcome = "O-SUPPORT"
        status = "completed"

    control = {
        "delta": DELTA,
        "epsilon_null_specified_not_run_on_v1": EPSILON,
        "min_matched_pairs": MIN_MATCHED_PAIRS,
        "match_rule": "|dimVV_GP - dimVV_rand| <= 1",
        "catalog_seed": CATALOG_SEED,
        "parent_catalog_seed_forbidden": PARENT_CATALOG_SEED,
        "cells": {
            k: {
                "matched_pair_count": v["matched_pair_count"],
                "median_ratio_GP_over_rand": v["median_ratio_GP_over_rand"],
                "in_band": v["in_band"],
                "enough_pairs": v["enough_pairs"],
                "twin_fail": v["twin_fail"],
            }
            for k, v in panels.items()
        },
        "outcome": outcome,
        "replication_of": "EXP-BINSTD-6c199f cell (17,3) under disjoint catalog",
        "cites": ["EV-BINSTD-78ca0d", "DEC-20261003-9575fd"],
    }
    write_json(EXP_ROOT / "stage1" / "panels.json", panels)
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    lines = [
        f"# RESULTS — {EXPERIMENT_ID}",
        "",
        f"- Hypothesis: {HYPOTHESIS_ID}",
        f"- Approved by: {APPROVED_BY}",
        f"- Predecessor: {PARENT_EXPERIMENT_ID} / EV-BINSTD-78ca0d / DEC-20261003-9575fd",
        f"- Outcome: **{outcome}**",
        f"- δ (frozen): {DELTA} → band upper = {1.0 - DELTA}",
        f"- catalog_seed: {CATALOG_SEED} (parent {PARENT_CATALOG_SEED} forbidden)",
        f"- Stage-2 n∈{{19,23}} + random-vs-random ε={EPSILON} specified, NOT RUN on trial-plan-v1",
        "",
        "## Panels (Stage-1 replication cell)",
        "",
    ]
    for k, v in panels.items():
        lines.append(
            f"- `{k}`: matched={v['matched_pair_count']}, "
            f"median_ratio={v['median_ratio_GP_over_rand']}, "
            f"in_band={v['in_band']}, twin_fail={v['twin_fail']}"
        )
    lines.extend(
        [
            "",
            "## Claims",
            "",
            "- break: false",
            "- exponent_move: false",
            "- n>=131 transfer: false",
            "- amazon_bedrock: NOT_USED",
            "- not a re-run of EXP-BINSTD-6c199f",
            "",
        ]
    )
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(lines))

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": status,
        "outcome": outcome,
        "panels": {k: {
            "matched_pair_count": v["matched_pair_count"],
            "median_ratio_GP_over_rand": v["median_ratio_GP_over_rand"],
            "in_band": v["in_band"],
            "enough_pairs": v["enough_pairs"],
        } for k, v in panels.items()},
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": status,
            "outcome": outcome,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def stage2(run_dir: Path) -> dict:
    """Specified Stage-2; not admitted by trial-plan-v1."""
    t0 = time.time()
    cat_path = EXP_ROOT / "stage0" / "v-catalog.json"
    if not cat_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 2,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze files",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 2, "status": "impediment"},
        )
        return raw
    catalog_doc = json.loads(cat_path.read_text(encoding="utf-8"))
    gp_panels: dict[str, Any] = {}
    null_panels: dict[str, Any] = {}
    any_twin_fail = False
    for n, ell in STAGE2_CELLS:
        key = f"n{n}_l{ell}"
        cell = catalog_doc["cells"][key]
        gp_panels[key] = build_matched_pairs(n, ell, cell["gp_catalog"], rng_salt=2000)
        null_panels[key] = build_random_vs_random(n, ell)
        if gp_panels[key]["twin_fail"] or null_panels[key]["twin_fail"]:
            any_twin_fail = True
    write_json(EXP_ROOT / "stage2" / "gp-panels.json", gp_panels)
    write_json(EXP_ROOT / "stage2" / "null-panels.json", null_panels)
    if any_twin_fail:
        outcome = "O-ARTIFACT"
        status = "artifact"
    else:
        outcome = "O-STAGE2-COMPLETE"
        status = "completed"
    write_text(
        EXP_ROOT / "RESULTS-stage2.md",
        "\n".join(
            [
                f"# RESULTS Stage-2 — {EXPERIMENT_ID}",
                "",
                f"- Outcome: **{outcome}**",
                f"- ε (frozen): {EPSILON}",
                "- Not admitted on trial-plan-v1.",
                "- amazon_bedrock: NOT_USED",
                "",
            ]
        ),
    )
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "stage": 2,
        "status": status,
        "outcome": outcome,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 2,
            "status": status,
            "outcome": outcome,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1, 2])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    _ = args.trial_plan
    if args.stage == 0:
        stage0(run_dir)
    elif args.stage == 1:
        stage1(run_dir)
    else:
        stage2(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
