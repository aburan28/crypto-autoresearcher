#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-6cca48 run artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from run import (  # noqa: E402
    CELLS,
    EXPERIMENT_ID,
    OUTCOMES,
    admissible,
    closed_form_source_hash,
    leaf_count,
)

EXP_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    errs: list[str] = []
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    if not raw_path.is_file() or raw_path.stat().st_size == 0:
        errs.append("missing/empty raw-result.json")
    if not man_path.is_file() or man_path.stat().st_size == 0:
        errs.append("missing/empty manifest.yaml")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
        errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move") or claims.get("rho_competitive"):
        errs.append("forbidden break/exponent/rho claim present")
    stage = raw.get("stage")
    if stage == 0:
        for rel in (
            "stage0/affordability-table.json",
            "stage0/preregistered-predictions.json",
            "stage0/forward-condition-disclaimer.json",
            "stage0/dependency-gate.json",
            "stage0/closed-form-pin.json",
        ):
            if not (EXP_ROOT / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        # Independent recomputation of every cell
        for cell in CELLS:
            try:
                got = leaf_count(cell["m"], cell["l"], cell["mu"])
            except Exception as exc:  # noqa: BLE001
                errs.append(f"leaf_count failed for {cell['id']}: {exc}")
                continue
            if got != cell["predicted_leaves"]:
                errs.append(
                    f"independent leaf_count mismatch {cell['id']}: {got} != {cell['predicted_leaves']}"
                )
            if not admissible(cell["m"], cell["l"], cell["n"]):
                errs.append(f"admissibility failed for {cell['id']}")
        pin = json.loads((EXP_ROOT / "stage0/closed-form-pin.json").read_text())
        if pin.get("closed_form_source_sha256") != closed_form_source_hash():
            errs.append("closed-form pin mismatch vs live source")
    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"outcome {outcome!r} not in {OUTCOMES}")
        results = EXP_ROOT / "RESULTS.md"
        if outcome in ("O-ARITH-OK", "O-ARITH-FAIL", "O-ARTIFACT"):
            if not results.is_file():
                errs.append("missing RESULTS.md")
            else:
                text = results.read_text(encoding="utf-8")
                hits = [lab for lab in OUTCOMES if f"**{lab}**" in text]
                if len(hits) != 1:
                    errs.append(f"RESULTS.md must name exactly one O-* label, found {hits}")
                elif hits[0] != outcome:
                    errs.append("RESULTS.md label disagrees with raw-result outcome")
        # Independent recomputation always
        for cell in CELLS:
            got = leaf_count(cell["m"], cell["l"], cell["mu"])
            if got != cell["predicted_leaves"] and outcome == "O-ARITH-OK":
                errs.append(f"O-ARITH-OK but independent mismatch on {cell['id']}")
        if outcome in ("O-ARITH-OK", "O-ARITH-FAIL"):
            for rel in ("stage1/recompute-table.json", "stage1/control-table.json"):
                if not (EXP_ROOT / rel).is_file():
                    errs.append(f"missing {rel}")
    else:
        errs.append(f"unknown stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
