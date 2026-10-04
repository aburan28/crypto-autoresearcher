#!/usr/bin/env python3
"""Independent checker for EXP-LHW-b49bc6 run artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

import freeze as F
from route_a import comb_a, next_prime_a
from route_b import comb_b, next_prime_b
from walks import millirho, weight_class

EXPERIMENT_ID = "EXP-LHW-b49bc6"
OUTCOMES = {
    "O-SUPPORT", "O-E1", "O-E2", "O-FAIL-BAND", "O-INCONCLUSIVE",
    "O-ARTIFACT", "O-IMPEDIMENT", "O-STAGE0-OK",
}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path, man_path = run_dir / "raw-result.json", run_dir / "manifest.yaml"
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
    if claims.get("break") or claims.get("exponent_move"):
        errs.append("forbidden break/exponent claim present")
    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    if stage == 0:
        for rel in ("stage0/preregistered-predictions.json", "stage0/frontier-table.json"):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        for m, w in F.CELLS:
            if comb_a(m, w) != comb_b(m, w) or comb_a(m, w) != F.BINOM[(m, w)]:
                errs.append(f"binom mismatch {(m, w)}")
            if next_prime_a(1 << (m + 2)) != F.L_PRIME[m]:
                errs.append(f"l_prime mismatch m={m}")
            if next_prime_b(1 << (m + 2)) != F.L_PRIME[m]:
                errs.append(f"l_prime B mismatch m={m}")
        pre = root / "stage0" / "preregistered-predictions.json"
        if pre.is_file():
            pred = json.loads(pre.read_text(encoding="utf-8"))
            if pred.get("e1_max_millirho") != F.E1_MAX_MILLIRHO:
                errs.append("E1 millirho freeze edited")
            if pred.get("e2_min_millirho") != F.E2_MIN_MILLIRHO:
                errs.append("E2 millirho freeze edited")
            if pred.get("t_grid") != list(F.T_GRID):
                errs.append("T_GRID freeze edited")
        if millirho(10, 20) != 2000:
            errs.append("millirho identity 20/10 failed")
        if len(weight_class(20, 2)) != 190:
            errs.append("W(20,2) cardinality")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        pre = root / "stage0" / "preregistered-predictions.json"
        if not pre.is_file():
            errs.append("Stage 1 without Stage-0 freeze")
        if outcome in ("O-E1", "O-E2") and (root / "stage1" / "control-table.json").is_file():
            ctl = json.loads((root / "stage1" / "control-table.json").read_text())
            for key, cell in (ctl.get("cells") or {}).items():
                if cell.get("wap_control_pass") is False:
                    errs.append(f"{key}: E1/E2 without W_ap control")
    else:
        errs.append(f"bad stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
