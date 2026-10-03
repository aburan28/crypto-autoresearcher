#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-88a926.

Recomputes schoolbook P+Q==R on a hit example without importing run.py
stage orchestration. Validates freeze-list integer-n rows, density match,
and pairwise yield-band polarity.
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
from mitt import (  # noqa: E402
    DENSITY_MATCH_MAX,
    YIELD_BAND,
    binomial_hw_density,
    density_rel_err,
    in_yield_band,
    models,
    ratio,
    relerr,
)

EXPERIMENT_ID = "EXP-BINSTD-88a926"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}


def _hit_ok(curve: Curve, examples) -> str | None:
    if not examples:
        return None
    ex = examples[0]
    P = tuple(ex["P"])
    Q = tuple(ex["Q"])
    R = tuple(ex["R"])
    S = curve.add(P, Q)
    if S is None or S[0] != R[0] or S[1] != R[1]:
        return "independent schoolbook P+Q != R on hit example"
    return None


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
            if pre.get("yield_ratio_band") != YIELD_BAND:
                errs.append("yield band drifted")
            cells = pre.get("cells")
            if not isinstance(cells, list) or not cells:
                errs.append("freeze cells must be a nonempty list")
            else:
                for i, cell in enumerate(cells):
                    if not isinstance(cell.get("n"), int):
                        errs.append(f"cells[{i}].n must be integer, not object-key")
                    dens_nb = binomial_hw_density(int(cell["n"]), int(cell["c_nb"]))
                    dens_pb = binomial_hw_density(int(cell["n"]), int(cell["c_pb"]))
                    if abs(dens_nb - float(cell["density_nb"])) > 1e-12:
                        errs.append(f"cells[{i}] density_nb mismatch")
                    if abs(dens_pb - float(cell["density_pb"])) > 1e-12:
                        errs.append(f"cells[{i}] density_pb mismatch")
                    if density_rel_err(dens_nb, dens_pb) > DENSITY_MATCH_MAX:
                        errs.append(f"cells[{i}] density match >10%")
                    if cell.get("walk"):
                        errs.append("walk must be false")
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
            "stage1/three-arm-yield.json",
            "stage1/control-table.json",
            "RESULTS.md",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        table_p = root / "stage1" / "three-arm-yield.json"
        if table_p.is_file():
            table = json.loads(table_p.read_text(encoding="utf-8"))
            cells = table.get("cells") or []
            if not isinstance(cells, list):
                errs.append("three-arm cells must be a list")
            F = Field(17, MODULI[17])
            c = Curve(F, 0, 1)
            if cells:
                r0 = cells[0]
                if not isinstance(r0.get("n"), int):
                    errs.append("three-arm cell n must be integer")
                for key in ("hit_examples_nb", "hit_examples_pb", "hit_examples_uni"):
                    msg = _hit_ok(c, r0.get(key) or [])
                    if msg:
                        errs.append(f"{key}: {msg}")
                m = models(int(r0["N"]), int(table["group_order"]))
                if abs(m["p_m2"] - r0["p_m2"]) > 1e-12:
                    errs.append("independent M2 formula mismatch")
                r_nb_pb = ratio(r0["nb_p_hat"], r0["pb_p_hat"])
                if abs(r_nb_pb - r0["ratio_nb_over_pb"]) > 1e-12:
                    errs.append("ratio_nb_over_pb mismatch")
                if r0.get("in_band_nb_pb") != in_yield_band(r_nb_pb):
                    errs.append("in_band_nb_pb polarity mismatch")
                if abs(relerr(r0["uni_p_hat"], m["p_m1"]) - r0["uniform_relerr_M1"]) > 1e-12:
                    errs.append("uniform_relerr_M1 mismatch")
                if r0.get("walk"):
                    errs.append("walk must be false")
            if table.get("outcome") != raw.get("outcome"):
                errs.append("table outcome vs raw-result mismatch")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
