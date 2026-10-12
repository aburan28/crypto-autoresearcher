#!/usr/bin/env python3
"""Independent checker for EXP-FROB-7d51ae run artifacts.

Recomputes Stage-0 Weil/jac gates on reported hits and verifies raw-result /
manifest agreement without importing run.py stage orchestration.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from hyperelliptic import jac_order_from_counts, point_count_curve, weils_ok  # noqa: E402

EXPERIMENT_ID = "EXP-FROB-7d51ae"
OUTCOMES = {"O-POSITIVE", "O-NEGATIVE", "O-NO-MODEL", "O-ARTIFACT", "O-IMPEDIMENT"}
GGMP_VS_DEGREE = 6


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    errs: list[str] = []
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
    if raw.get("claims", {}).get("break") or raw.get("claims", {}).get("exponent_move"):
        errs.append("forbidden break/exponent claim present")

    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]

    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/genus2-census.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        prereg = json.loads((root / "stage0" / "preregistered-predictions.json").read_text(encoding="utf-8"))
        if prereg.get("ggmp_vs_degree_m3") != GGMP_VS_DEGREE:
            errs.append("preregistered GGMP degree mismatch")
        census = json.loads((root / "stage0" / "genus2-census.json").read_text(encoding="utf-8"))
        for hit in census.get("hits", []):
            h, f = hit["h"], hit["f"]
            n1 = point_count_curve(h, f, 1)
            n2 = point_count_curve(h, f, 2)
            if n1 != hit.get("N1") or n2 != hit.get("N2"):
                errs.append(f"hit count mismatch for h={h} f={f}")
            if not weils_ok(n1, n2):
                errs.append(f"Weil gate fail for h={h} f={f}")
            jac = jac_order_from_counts(n1, n2)
            if jac != hit.get("jac_order"):
                errs.append(f"jac_order mismatch for h={h} f={f}")
            if jac % 19 != 0:
                errs.append(f"19 does not divide jac for h={h} f={f}")
        if raw.get("status") != "completed":
            errs.append("stage0 status not completed")

    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        man = man_path.read_text(encoding="utf-8")
        if outcome and (
            f"outcome: {outcome}" not in man and f'outcome: "{outcome}"' not in man
        ):
            errs.append("manifest outcome disagrees with raw-result")
        if outcome in OUTCOMES - {"O-IMPEDIMENT"}:
            if outcome != "O-IMPEDIMENT" and not (root / "stage0" / "genus2-census.json").is_file():
                errs.append("missing stage0 census for stage1")
        if outcome in {"O-POSITIVE", "O-NEGATIVE", "O-NO-MODEL", "O-ARTIFACT"}:
            if not (root / "stage1" / "panels.json").is_file():
                errs.append("missing stage1/panels.json")
            if not (root / "stage1" / "control-table.json").is_file():
                errs.append("missing stage1/control-table.json")
            if not (root / "RESULTS.md").is_file():
                errs.append("missing RESULTS.md")
            else:
                text = (root / "RESULTS.md").read_text(encoding="utf-8")
                if f"**{outcome}**" not in text:
                    errs.append("RESULTS.md missing bold outcome marker")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
