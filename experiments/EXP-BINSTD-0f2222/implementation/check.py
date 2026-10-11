#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-0f2222.

Recomputes schoolbook P+Q==R on a hit example without importing run.py
stage orchestration. Validates freeze-list integer-n rows and band polarity.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from curve import Curve  # noqa: E402
from gf2 import Field, MODULI  # noqa: E402
from mitt import RELERR_BAND, models, relerr  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-0f2222"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}


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
    if claims.get("break") or claims.get("exponent_move"):
        errs.append("forbidden break/exponent claim present")
    outcome = raw.get("outcome")
    if outcome not in OUTCOMES:
        errs.append(f"unknown outcome {outcome!r}")
    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]

    if stage == 0:
        pre_p = root / "stage0" / "preregistered-predictions.json"
        note_p = root / "stage0" / "methodological-note.json"
        for pth in (pre_p, note_p):
            if not pth.is_file():
                errs.append(f"missing freeze file {pth}")
        if pre_p.is_file():
            pre = json.loads(pre_p.read_text(encoding="utf-8"))
            if pre.get("relerr_band") != RELERR_BAND:
                errs.append("relerr band drifted")
            cells = pre.get("cells")
            if not isinstance(cells, list) or not cells:
                errs.append("freeze cells must be a nonempty list")
            else:
                for i, cell in enumerate(cells):
                    if not isinstance(cell.get("n"), int):
                        errs.append(f"cells[{i}].n must be integer, not object-key")
                    if "N" not in cell or "e_m2_target" not in cell:
                        errs.append(f"cells[{i}] missing N or e_m2_target")
        if note_p.is_file():
            note = json.loads(note_p.read_text(encoding="utf-8"))
            if note.get("order_table") != note.get("order_school"):
                errs.append("independent: dual #E counts disagree in freeze")
            if note.get("empty_pool_hits") != 0:
                errs.append("empty-pool null must be zero hits at freeze")
            F = Field(17, MODULI[17])
            c = Curve(F, 0, 1)
            recomputed = c.count_by_trace()
            if recomputed != note.get("order_school"):
                errs.append("independent schoolbook #E mismatch vs freeze")
    elif stage == 1:
        for rel in (
            "stage1/bakeoff-table.json",
            "stage1/control-table.json",
            "RESULTS.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        table_p = root / "stage1" / "bakeoff-table.json"
        if table_p.is_file():
            table = json.loads(table_p.read_text(encoding="utf-8"))
            cells = table.get("cells") or []
            if not isinstance(cells, list):
                errs.append("bakeoff cells must be a list")
            F = Field(17, MODULI[17])
            c = Curve(F, 0, 1)
            if cells:
                r0 = cells[0]
                if not isinstance(r0.get("n"), int):
                    errs.append("bakeoff cell n must be integer")
                examples = r0.get("hit_examples") or []
                if examples:
                    ex = examples[0]
                    P = tuple(ex["P"])
                    Q = tuple(ex["Q"])
                    R = tuple(ex["R"])
                    S = c.add(P, Q)
                    if S is None or S[0] != R[0] or S[1] != R[1]:
                        errs.append("independent schoolbook P+Q != R on hit example")
                m = models(int(r0["N"]), int(table["group_order"]))
                if abs(m["p_m2"] - r0["p_m2"]) > 1e-12:
                    errs.append("independent M2 formula mismatch")
                expected_band = relerr(r0["p_hat"], m["p_m2"]) <= RELERR_BAND
                if r0.get("in_band_M2") != expected_band:
                    errs.append("in_band_M2 polarity mismatch vs independent relerr")
            holds = table.get("holds") or {}
            winners = [k for k, v in holds.items() if v >= 3]
            if table.get("outcome") == "O-SUPPORT" and len(winners) != 1:
                errs.append("O-SUPPORT requires exactly one model holding ≥3 cells")
            if table.get("outcome") == "O-FAIL-BAND" and winners:
                errs.append("O-FAIL-BAND but a model holds ≥3 cells")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
