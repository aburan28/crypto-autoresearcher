#!/usr/bin/env python3
"""Independent checker: recomputes envelope and covered dual meters from integer n."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))
from covered import covered_size_dual, grow_lists
from envelope import class_counts, envelope_amqm_bound, pair_count

EXPERIMENT_ID = "EXP-GRUMPY-cd7b82"
OUTCOMES_S0 = {"O-STAGE0-OK"}
OUTCOMES_S1 = {"O-SUPPORT-M12", "O-FAIL-M1", "O-FAIL-M2", "O-ARTIFACT", "O-IMPEDIMENT"}


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
        if raw.get("outcome") not in OUTCOMES_S0:
            errs.append(f"bad stage0 outcome {raw.get('outcome')!r}")
        freeze = root / "stage0" / "floor-table.json"
        pred = root / "stage0" / "preregistered-predictions.json"
        if not freeze.is_file():
            errs.append("missing stage0/floor-table.json")
        else:
            doc = json.loads(freeze.read_text(encoding="utf-8"))
            rows = doc.get("rows") or []
            if not isinstance(rows, list) or not rows:
                errs.append("floor-table rows must be a nonempty list")
            else:
                probe = rows[0]
                if not isinstance(probe.get("n"), int):
                    errs.append("floor-table n must be integer field (not a dict key)")
                n = int(probe["n"])
                k = int(probe["k"])
                n_free = int(probe["n_free"])
                ell = int(probe["l"])
                bound = envelope_amqm_bound(n, k, n_free)
                if bound != int(probe["envelope_bound"]):
                    errs.append("stage0 envelope recompute mismatch")
        if not pred.is_file():
            errs.append("missing stage0/preregistered-predictions.json")
    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES_S1:
            errs.append(f"bad outcome {outcome!r}")
        rows_path = root / "stage1" / "decomposition-rows.json"
        if outcome != "O-IMPEDIMENT":
            if not rows_path.is_file():
                errs.append("missing stage1/decomposition-rows.json")
            else:
                doc = json.loads(rows_path.read_text(encoding="utf-8"))
                rows = doc.get("rows") or []
                if not isinstance(rows, list):
                    errs.append("decomposition rows must be a list")
                elif rows:
                    r0 = rows[0]
                    if not isinstance(r0.get("n"), int):
                        errs.append("decomposition n must be integer field")
                    n = int(r0["n"])
                    ell = int(r0["l"])
                    k = int(r0["k"])
                    n_free = 2 if k == 2 else 3
                    rates = (1, 1) if k == 2 else (1, 1, 1)
                    betas = (0, 1) if k == 2 else (0, 1, 2)
                    m = max(1, int(round(ell**0.5)))
                    steps = (1, m) if k == 2 else (1, m, m + 1)
                    counts = class_counts(n, rates, n_free)
                    p_n = pair_count(counts)
                    lists = grow_lists(n, rates, n_free, ell, steps)
                    c_a, c_b, ok = covered_size_dual(lists, ell, betas)
                    if not ok:
                        errs.append("check.py dual covered disagree")
                    if p_n != int(r0["P_n"]):
                        errs.append("P_n recompute mismatch")
                    if c_a != int(r0["C_n"]):
                        errs.append("C_n recompute mismatch")
            if not (root / "RESULTS.md").is_file():
                errs.append("missing RESULTS.md")
    else:
        errs.append(f"unknown stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
