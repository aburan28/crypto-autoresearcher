#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-7cfb11 run artifacts.

Recomputes dual GF(2) fill-in on the Stage-0 identity probe and on Stage-1
n=17 surplus 1.0 relation-like cell. Routes must not disagree.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from matrices import cell_seed, relation_like  # noqa: E402
from route_bits import gauss_jordan_fill_in as fill_bits  # noqa: E402
from route_sets import gauss_jordan_fill_in as fill_sets  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-7cfb11"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
BETA = 16.0
FB17 = 24
WEIGHT = 4
RELATION_SEED = 2026100301
KIND_REL = 0


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
    if claims.get("n_ge_131"):
        errs.append("forbidden n>=131 claim present")
    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/la-pin.json",
            "stage0/probe.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        ident_sets = [{i} for i in range(8)]
        ident_bits = [1 << i for i in range(8)]
        a = fill_sets(ident_sets, 8)
        b = fill_bits(ident_bits, 8)
        if a["fill_in_ratio"] != 1.0 or b["fill_in_ratio"] != 1.0:
            errs.append("identity fill-in is not 1")
        if a != {**a, **{k: b[k] for k in ("nnz_initial", "nnz_after", "rank", "fill_in_ratio")}} and (
            a["nnz_initial"] != b["nnz_initial"]
            or a["nnz_after"] != b["nnz_after"]
            or a["rank"] != b["rank"]
        ):
            errs.append("stage0 identity dual mismatch")
        if a["nnz_initial"] != b["nnz_initial"] or a["nnz_after"] != b["nnz_after"] or a["rank"] != b["rank"]:
            errs.append("stage0 identity dual mismatch")
        pred = root / "stage0" / "preregistered-predictions.json"
        if pred.is_file():
            p = json.loads(pred.read_text(encoding="utf-8"))
            if p.get("beta") != BETA:
                errs.append(f"frozen beta {p.get('beta')!r} != {BETA}")
        if raw.get("outcome") not in ("O-STAGE0-OK", "O-ARTIFACT"):
            errs.append(f"bad stage0 outcome {raw.get('outcome')!r}")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        ncols = FB17
        nrows = 24  # surplus 1.0
        seed = cell_seed(RELATION_SEED, 17, 0, KIND_REL)
        sets_rows, bits_rows = relation_like(nrows, ncols, WEIGHT, seed)
        a = fill_sets(sets_rows, ncols)
        b = fill_bits(bits_rows, ncols)
        if a["nnz_initial"] != b["nnz_initial"] or a["nnz_after"] != b["nnz_after"] or a["rank"] != b["rank"]:
            errs.append("stage1 surplus-1.0 dual mismatch on recompute")
        panels_path = root / "stage1" / "panels.json"
        if panels_path.is_file():
            panels = json.loads(panels_path.read_text(encoding="utf-8"))
            cell = (panels.get("n17_s1.0") or {}).get("relation") or {}
            reported = cell.get("fill_in_ratio")
            if reported is not None and reported != a["fill_in_ratio"]:
                errs.append("stage1 reported F disagrees with independent recompute")
            if outcome in ("O-SUPPORT", "O-FAIL-BAND"):
                pred = json.loads((root / "stage0" / "preregistered-predictions.json").read_text())
                if pred.get("beta") != BETA:
                    errs.append("band outcome against a mutated beta")
        results = (root / "RESULTS.md").read_text(encoding="utf-8") if (root / "RESULTS.md").is_file() else ""
        if outcome and outcome not in results:
            errs.append("RESULTS.md does not name the raw outcome")
    else:
        errs.append(f"unknown stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
