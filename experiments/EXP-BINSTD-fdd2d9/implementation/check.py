#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-fdd2d9 run artifacts.

Recomputes 3×4=12, 70−50=20, 20×4=80, 6×12=72 without importing either
arithmetic route module. Verifies route independence via AST. No encoding.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-BINSTD-fdd2d9"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
_IMPL = Path(__file__).resolve().parent
_ROOT = Path(__file__).resolve().parents[1]


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


def independent_integers() -> dict:
    return {
        "ell_product": 3 * 4,
        "hundredths_excess": 70 - 50,
        "catalog_quot": 12 // 3,
        "excess_product": 20 * 4,
        "slots": 6 * 12,
        "n_sum": 17 + 19 + 23,
        "n_product": 17 * 19 * 23,
        "gap_product": 2 * 4,
        "span": 23 - 17,
        "cross_two_thirds": 7 * 3 - 10 * 2,
        "cross_three_fifths": 7 * 5 - 10 * 3,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    cert_path = run_dir / "certificate.yaml"
    errs: list[str] = []
    for p, label in (
        (raw_path, "raw-result.json"),
        (man_path, "manifest.yaml"),
        (cert_path, "certificate.yaml"),
    ):
        if not p.is_file() or p.stat().st_size == 0:
            errs.append(f"missing/empty {label}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
        errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move"):
        errs.append("forbidden break/exponent claim present")
    if raw.get("encoding_run"):
        errs.append("encoding_run must be false")
    outcome = raw.get("outcome")
    if outcome not in OUTCOMES:
        errs.append(f"unknown outcome {outcome!r}")

    d_imp = _imports_of(_IMPL / "route_difference.py")
    p_imp = _imports_of(_IMPL / "route_product.py")
    if "route_product" in d_imp or "route_difference" in p_imp:
        errs.append("routes import each other")

    indep = independent_integers()
    if indep["ell_product"] != 12 or indep["hundredths_excess"] != 20:
        errs.append("independent recompute of 12/20 failed")
    if indep["excess_product"] != 80 or indep["slots"] != 72:
        errs.append("independent recompute of 80/72 failed")
    if indep["n_product"] != 7429:
        errs.append("independent recompute of n_product failed")

    stage = raw.get("stage")
    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/v-catalog.json",
        ):
            if not (_ROOT / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        cat_path = _ROOT / "stage0" / "v-catalog.json"
        if cat_path.is_file():
            cat = json.loads(cat_path.read_text(encoding="utf-8"))
            vals = cat.get("values") or {}
            if vals.get("ell_product") != indep["ell_product"]:
                errs.append("Stage-0 ell_product mismatch vs independent recompute")
            if vals.get("hundredths_excess") != indep["hundredths_excess"]:
                errs.append("Stage-0 hundredths_excess mismatch vs independent recompute")
            if vals.get("excess_product") != indep["excess_product"]:
                errs.append("Stage-0 excess_product mismatch vs independent recompute")
            if vals.get("catalog") == 9:
                errs.append("catalog reported as 9")
        if outcome == "O-STAGE0-OK":
            if raw.get("route") != "difference":
                errs.append("Stage 0 must be the difference route")
    elif stage == 1:
        for rel in (
            "stage1/panels.json",
            "stage1/control-table.json",
            "RESULTS.md",
        ):
            if not (_ROOT / rel).is_file():
                errs.append(f"missing {rel}")
        ctrl_path = _ROOT / "stage1" / "control-table.json"
        if ctrl_path.is_file():
            ctrl = json.loads(ctrl_path.read_text(encoding="utf-8"))
            if not ctrl.get("independent"):
                errs.append("Stage-1 control missing route independence")
            prod = ctrl.get("product") or {}
            if prod.get("n_product") != indep["n_product"]:
                errs.append("Stage-1 n_product mismatch vs independent recompute")
            if prod.get("excess_product") != indep["excess_product"]:
                errs.append("Stage-1 excess_product mismatch vs independent recompute")
            if outcome == "O-SUPPORT":
                if not ctrl.get("implementations_agree"):
                    errs.append("O-SUPPORT requires implementations_agree")
                if raw.get("hundredths_excess") != 20 or raw.get("excess_product") != 80:
                    errs.append("O-SUPPORT requires excess 20 and product 80")
        results = _ROOT / "RESULTS.md"
        if results.is_file():
            text = results.read_text(encoding="utf-8")
            labels = [o for o in OUTCOMES if f"**{o}**" in text]
            if len(labels) != 1:
                errs.append("RESULTS.md must name exactly one O-* label")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
