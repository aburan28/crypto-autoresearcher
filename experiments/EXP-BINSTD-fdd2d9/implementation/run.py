#!/usr/bin/env python3
"""EXP-BINSTD-fdd2d9 Stages 0-1: catalog-count integer check.

Two independent arithmetic routes (difference, product). No encoding.
Approved by DEC-20261003-2e4a60; execution unlock DEC-20261003-6c2db4.
No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from route_difference import compute as compute_difference  # noqa: E402
from route_product import compute as compute_product  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-fdd2d9"
HYPOTHESIS_ID = "H-BINSTD-f9fa00"
APPROVED_BY = "DEC-20261003-2e4a60"
UNLOCK_DEC = "DEC-20261003-6c2db4"
TASK_ID = "TASK-20261003-c9329a"
EXP_ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "n_sum": 59,
    "n_product": 7429,
    "gap_product": 8,
    "span": 6,
    "ell_lo": 3,
    "ell_hi": 4,
    "ell_product": 12,
    "cells": 6,
    "catalog": 12,
    "slots": 72,
    "hour_cap": 6,
    "slot_quot": 6,
    "bound_hundredths": 70,
    "half_hundredths": 50,
    "hundredths_excess": 20,
    "distinct_floor": 3,
    "catalog_quot": 4,
    "excess_product": 80,
    "cross_two_thirds": 1,
    "cross_three_fifths": 5,
}

AGREE_KEYS = (
    "n_sum",
    "gap_product",
    "span",
    "ell_product",
    "slots",
    "slot_quot",
    "hundredths_excess",
    "catalog_quot",
    "excess_product",
    "cross_two_thirds",
    "cross_three_fifths",
)


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


def write_certificate(run_dir: Path, stage: int, outcome: str, extras: dict) -> None:
    lines = [
        "kind: integer_catalog_check",
        "claim_tier: observational",
        f"experiment_id: {EXPERIMENT_ID}",
        f"hypothesis_id: {HYPOTHESIS_ID}",
        f"stage: {stage}",
        f"outcome: {outcome}",
        "discrete_log: false",
        "decomposition: false",
        "key_recovery: false",
        "encoding_run: false",
        "amazon_bedrock: NOT_USED",
    ]
    for k, v in extras.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            lines.append(f'{k}: "{v}"')
    write_text(run_dir / "certificate.yaml", "\n".join(lines) + "\n")


def _imports_of(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def routes_independent() -> tuple[bool, dict]:
    diff_path = _IMPL / "route_difference.py"
    prod_path = _IMPL / "route_product.py"
    d_imp = _imports_of(diff_path)
    p_imp = _imports_of(prod_path)
    ok = "route_product" not in d_imp and "route_difference" not in p_imp
    return ok, {
        "difference_imports": sorted(d_imp),
        "product_imports": sorted(p_imp),
        "independent": ok,
    }


def matches_expected(row: dict, keys: tuple[str, ...]) -> bool:
    return all(row.get(k) == EXPECTED[k] for k in keys)


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    independent, import_audit = routes_independent()
    diff = compute_difference()
    encoding = bool(diff.get("encoding_run"))
    catalog_ok = diff.get("ell_product") == 12 and diff.get("catalog") != 9
    excess_ok = diff.get("hundredths_excess") == 20
    slots_ok = diff.get("slots") == 72
    freeze = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "unlock_decision": UNLOCK_DEC,
        "task_id": TASK_ID,
        "expected": EXPECTED,
        "prediction": (
            "Three times 4 is 12. Seventy exceeds 50 by 20. "
            "The product of 20 and 4 is 80. Six times 12 is 72."
        ),
        "routes": ["difference", "product"],
        "encoding_run": False,
        "amazon_bedrock": "NOT SELECTED",
        "import_audit": import_audit,
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", freeze)
    write_json(
        EXP_ROOT / "stage0" / "v-catalog.json",
        {
            "route": "difference",
            "values": diff,
            "independent": independent,
            "catalog_ok": catalog_ok,
            "excess_ok": excess_ok,
            "slots_ok": slots_ok,
        },
    )

    if encoding or not independent:
        outcome = "O-ARTIFACT"
    elif not catalog_ok or diff.get("ell_product") != 12:
        outcome = "O-ARTIFACT"
    elif not excess_ok:
        outcome = "O-FAIL"
    elif not slots_ok or not matches_expected(
        diff,
        (
            "n_sum",
            "gap_product",
            "span",
            "ell_product",
            "slots",
            "slot_quot",
            "catalog_quot",
            "excess_product",
            "cross_two_thirds",
            "cross_three_fifths",
        ),
    ):
        outcome = "O-FAIL"
    else:
        outcome = "O-STAGE0-OK"

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "unlock_decision": UNLOCK_DEC,
        "stage": 0,
        "status": "ok" if outcome == "O-STAGE0-OK" else "stop",
        "outcome": outcome,
        "route": "difference",
        "values": diff,
        "independent": independent,
        "implementations_agree": None,
        "encoding_run": encoding,
        "wall_clock_seconds": time.time() - t0,
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "outcome": outcome,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    write_certificate(
        run_dir,
        0,
        outcome,
        {
            "hundredths_excess": diff.get("hundredths_excess"),
            "ell_product": diff.get("ell_product"),
        },
    )
    return raw


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    cat_path = EXP_ROOT / "stage0" / "v-catalog.json"
    pre_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not cat_path.is_file() or not pre_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "stage": 1,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage-0 freeze missing",
            "claims": {"break": False, "exponent_move": False},
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment"},
        )
        write_certificate(run_dir, 1, "O-IMPEDIMENT", {"reason": "Stage-0 freeze missing"})
        return raw

    independent, import_audit = routes_independent()
    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    diff = cat["values"]
    prod = compute_product()
    encoding = bool(prod.get("encoding_run") or diff.get("encoding_run"))
    agree = all(diff.get(k) == prod.get(k) for k in AGREE_KEYS)
    catalog_ok = prod.get("ell_product") == 12 and prod.get("catalog") != 9
    excess_ok = prod.get("hundredths_excess") == 20
    product_ok = prod.get("excess_product") == 80
    n_product_ok = prod.get("n_product") == 7429
    slots_ok = prod.get("slots") == 72

    if encoding or not independent:
        outcome = "O-ARTIFACT"
    elif not catalog_ok:
        outcome = "O-ARTIFACT"
    elif agree and not excess_ok:
        outcome = "O-FAIL"
    elif not agree:
        outcome = "O-ARTIFACT"
    elif catalog_ok and excess_ok and product_ok and n_product_ok and slots_ok:
        outcome = "O-SUPPORT"
    else:
        outcome = "O-FAIL"

    control = {
        "independent": independent,
        "import_audit": import_audit,
        "implementations_agree": agree,
        "agree_keys": list(AGREE_KEYS),
        "difference": {k: diff.get(k) for k in AGREE_KEYS},
        "product": {k: prod.get(k) for k in (*AGREE_KEYS, "n_product")},
        "expected": EXPECTED,
        "encoding_run": encoding,
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)
    write_json(
        EXP_ROOT / "stage1" / "panels.json",
        {"difference": diff, "product": prod, "outcome": outcome},
    )

    lines = [
        f"# RESULTS — {EXPERIMENT_ID} Stages 0-1",
        "",
        f"- Hypothesis: {HYPOTHESIS_ID}",
        f"- Approved by: {APPROVED_BY}",
        f"- Unlock: {UNLOCK_DEC} / {TASK_ID}",
        f"- Outcome: **{outcome}**",
        f"- implementations_agree: {agree}",
        f"- routes independent: {independent}",
        f"- encoding_run: {encoding}",
        "",
        "## Integer checks",
        "",
        f"- 3×4 catalog/ell_product: difference={diff.get('ell_product')} "
        f"product={prod.get('ell_product')} expected=12",
        f"- 70−50 hundredths_excess: difference={diff.get('hundredths_excess')} "
        f"product={prod.get('hundredths_excess')} expected=20",
        f"- 20×4 excess_product: difference={diff.get('excess_product')} "
        f"product={prod.get('excess_product')} expected=80",
        f"- 6×12 slots: difference={diff.get('slots')} product={prod.get('slots')} expected=72",
        f"- n_product: product-route={prod.get('n_product')} expected=7429",
        "",
        "## Claims",
        "",
        "- break: false",
        "- exponent_move: false",
        "- encoding: not run",
        "- n>=131 transfer: not claimed",
        "",
        "Amazon Bedrock: NOT_USED",
        "",
    ]
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(lines))

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "unlock_decision": UNLOCK_DEC,
        "stage": 1,
        "status": "ok",
        "outcome": outcome,
        "route": "product",
        "values": prod,
        "independent": independent,
        "implementations_agree": agree,
        "encoding_run": encoding,
        "hundredths_excess": prod.get("hundredths_excess"),
        "excess_product": prod.get("excess_product"),
        "ell_product": prod.get("ell_product"),
        "n_product": prod.get("n_product"),
        "slots": prod.get("slots"),
        "wall_clock_seconds": time.time() - t0,
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": outcome,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    write_certificate(
        run_dir,
        1,
        outcome,
        {
            "hundredths_excess": prod.get("hundredths_excess"),
            "excess_product": prod.get("excess_product"),
            "implementations_agree": agree,
        },
    )
    return raw


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, choices=[0, 1])
    p.add_argument("--trial-plan", type=str, default="")
    p.add_argument("--run-dir", type=str, default="")
    args = p.parse_args(argv)
    if not args.run_dir:
        print("--run-dir required", file=sys.stderr)
        return 2
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        stage0(run_dir)
    elif args.stage == 1:
        stage1(run_dir)
    else:
        print("stage required", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
