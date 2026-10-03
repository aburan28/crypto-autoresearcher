#!/usr/bin/env python3
"""Independent checker for EXP-SEMBIN-d830d5 Stage 0-2 run artifacts.

Recomputes the EXP-SEMBIN-92724f D1 finite-k counting-cap identity without
importing run.py stage drivers. Verifies raw-result.json / manifest.yaml.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

EXPERIMENT_ID = "EXP-SEMBIN-d830d5"
STAGE0_OK = {"S0-FREEZE-OK"}
STAGE1_OK = {"SMOKE_PASS", "O-ARTIFACT", "O-IMPEDIMENT"}
STAGE2_OK = {
    "O-CONSERVED",
    "O-EXCHANGED",
    "O-NO-YIELD",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
}
CANDIDATE_CELLS = [(24, 6, 3), (30, 7, 3), (36, 8, 4)]
STAGE2_CELLS = [(30, 7, 3), (36, 8, 4)]


def exact_counting_identity(k: int, m: int) -> bool:
    size_v = 1 << k
    typed_domain = 1 << (m * k)
    untyped_domain = math.comb(size_v + m - 1, m)
    corr = Fraction(1)
    for j in range(m):
        corr *= Fraction(size_v + j, size_v)
    ratio = Fraction(typed_domain, untyped_domain)
    return ratio * corr == math.factorial(m)


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
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move") or claims.get("attack") or claims.get("fips"):
        errs.append("forbidden break/exponent/attack/fips claim present")

    result = raw.get("result") or {}
    status = result.get("status")
    if status not in ("completed_valid", "failed_infrastructure"):
        errs.append(f"unexpected status {status!r}")
    stage = result.get("stage", raw.get("stage"))
    outcome = result.get("outcome")
    root = Path(__file__).resolve().parents[1]

    # Independent D1 pin
    for n, k, m in CANDIDATE_CELLS:
        if not exact_counting_identity(k, m):
            errs.append(f"D1 identity failed for cell ({n},{k},{m})")
    # Pin known value: m=3,k=6 → m! = 6
    if math.factorial(3) != 6:
        errs.append("factorial pin failed")

    if stage == 0:
        if outcome not in STAGE0_OK:
            errs.append(f"stage0 outcome {outcome!r}")
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/backend-probe.json",
            "stage0/worksheet-note.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        if (root / "stage0/preregistered-predictions.json").is_file():
            pred = json.loads((root / "stage0/preregistered-predictions.json").read_text())
            cells = pred.get("candidate_cells") or []
            got = {(c["n"], c["k"], c["m"]) for c in cells}
            if got != set(CANDIDATE_CELLS):
                errs.append(f"stage0 candidate cells {sorted(got)} != {CANDIDATE_CELLS}")
    elif stage == 1:
        if outcome not in STAGE1_OK:
            errs.append(f"stage1 outcome {outcome!r}")
        for rel in (
            "stage1/finite-k-cap-identity.json",
            "stage1/planted-relation-smoke.json",
            "stage1/untyped-descend-smoke.json",
            "stage1/smoke-note.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing stage1 file {rel}")
        cap_path = root / "stage1/finite-k-cap-identity.json"
        if cap_path.is_file():
            cap = json.loads(cap_path.read_text())
            if cap.get("all_identities_hold") is not True:
                errs.append("stage1 cap file reports identities not holding")
    elif stage == 2:
        if outcome not in STAGE2_OK:
            errs.append(f"stage2 outcome {outcome!r}")
        for rel in (
            "stage2/c2-rescope.json",
            "stage2/ladder-rows.json",
            "stage2/arm-summaries.json",
            "stage2/ladder-note.md",
            "RESULTS.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing stage2 file {rel}")
        # Stage 0/1 must remain present (not rewritten away).
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/backend-probe.json",
            "stage1/finite-k-cap-identity.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing required prior artifact {rel}")
        rescope_path = root / "stage2/c2-rescope.json"
        if rescope_path.is_file():
            rs = json.loads(rescope_path.read_text())
            cells = {(c["n"], c["k"], c["m"]) for c in rs.get("rescoped_cells") or []}
            if cells != set(STAGE2_CELLS):
                errs.append(f"c2-rescope cells {sorted(cells)} != {STAGE2_CELLS}")
            if rs.get("rescoped_C2_sizes_required") != 2:
                errs.append("c2-rescope sizes_required != 2")
        results = (root / "RESULTS.md").read_text(encoding="utf-8")
        if f"**{outcome}**" not in results and outcome not in results:
            errs.append("RESULTS.md does not name the Stage-2 outcome")
        if "Bedrock" not in results and "BEDROCK" not in results:
            errs.append("RESULTS.md missing Bedrock marker")
    else:
        errs.append(f"unexpected stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print(json.dumps({"ok": True, "stage": stage, "outcome": outcome}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
