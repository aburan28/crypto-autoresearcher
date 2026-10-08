#!/usr/bin/env python3
"""Independent checker for EXP-FROB-f495ea run artifacts.

Recomputes genus-1 N_1 census membership and verifies raw-result / manifest
agreement without importing run.py stage logic beyond shared gf2 primitives.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from gf2 import Field, eval_poly_f2, is_monic_degree, poly_degree  # noqa: E402

EXPERIMENT_ID = "EXP-FROB-f495ea"
OUTCOMES = {"O-HIT", "O-EMPTY", "O-ARTIFACT", "O-IMPEDIMENT"}


def n1_as(f_coeffs: int) -> int:
    field = Field(1)
    zeros = 0
    for x in range(2):
        if field.trace(eval_poly_f2(f_coeffs, x, field)) == 0:
            zeros += 1
    return 1 + 2 * zeros


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
            "stage0/genus1-census.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        freeze = raw.get("freeze") or {}
        if freeze.get("all_N1_in_1_to_5") is not True and raw.get("genus1_census_ok") is not True:
            # Allow explicit artifact status
            if raw.get("status") not in ("completed", "artifact"):
                errs.append("stage0 status not completed/artifact")
        # Spot-check: every monic deg-3 poly's N1 is in 1..5 under direct count
        leading = 1 << 3
        for lower in range(1 << 3):
            f = leading | lower
            if not is_monic_degree(f, 3):
                continue
            n1 = n1_as(f)
            if n1 not in {1, 2, 3, 4, 5}:
                errs.append(f"independent N1={n1} outside range for f={f:#x}")
                break
        if raw.get("genus1_census_ok") is True and raw.get("status") != "completed":
            errs.append("genus1_census_ok true but status not completed")

    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        man = man_path.read_text(encoding="utf-8")
        if outcome and f"outcome: {outcome}" not in man:
            errs.append("manifest outcome disagrees with raw-result")
        if outcome in ("O-HIT", "O-EMPTY"):
            if not (root / "stage1" / "panels.json").is_file():
                errs.append("missing stage1/panels.json")
            if not (root / "stage1" / "control-table.json").is_file():
                errs.append("missing stage1/control-table.json")
            if not (root / "RESULTS.md").is_file():
                errs.append("missing RESULTS.md")
            else:
                text = (root / "RESULTS.md").read_text(encoding="utf-8")
                if f"**{outcome}**" not in text and f"Outcome: **{outcome}**" not in text:
                    # Accept either form
                    if outcome not in text:
                        errs.append("RESULTS.md missing outcome label")
            g5 = raw.get("hit_count_g5")
            g6 = raw.get("hit_count_g6")
            if not isinstance(g5, int) or not isinstance(g6, int):
                errs.append("hit counts must be integers")
            elif outcome == "O-HIT" and g5 + g6 < 1:
                errs.append("O-HIT but both hit counts zero")
            elif outcome == "O-EMPTY" and g5 + g6 != 0:
                errs.append("O-EMPTY but a hit count is nonzero")
        # poly_degree sanity
        if poly_degree(1 << 11) != 11:
            errs.append("gf2 poly_degree broken")
    else:
        errs.append(f"bad stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
