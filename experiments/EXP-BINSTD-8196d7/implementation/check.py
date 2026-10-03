#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-8196d7 run artifacts.

Recomputes twin r_Tr / N_nl on a probe row without importing run.py stage
orchestration. Validates raw-result / manifest agreement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import encode_trace_nnl  # noqa: E402
from gf2n import Field  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-8196d7"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55}
SPEARMAN_BAND = -0.70


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

    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    outcome = raw.get("outcome")
    if outcome not in OUTCOMES:
        errs.append(f"unknown outcome {outcome!r}")

    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/v-catalog.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        if (root / "stage0" / "preregistered-predictions.json").is_file():
            pre = json.loads((root / "stage0" / "preregistered-predictions.json").read_text())
            if pre.get("spearman_band") != SPEARMAN_BAND:
                errs.append("preregistered Spearman band drifted from frozen contract")
        if (root / "stage0" / "v-catalog.json").is_file():
            cat = json.loads((root / "stage0" / "v-catalog.json").read_text())
            cell = cat["cells"]["n17_l3"]
            basis = cell["catalog"][0]["basis"]
            F = Field(17, MODULI[17])
            ra, rb, na, nb, ok = encode_trace_nnl(F, CURVE_B[17], basis, XR[17])[:5]
            if not ok:
                errs.append("independent twin disagree on stage0 probe")
            probe_r = cell.get("probe_rTr") or {}
            probe_n = cell.get("probe_Nnl") or {}
            if probe_r.get("a") != ra or probe_r.get("b") != rb:
                errs.append("stage0 probe_rTr mismatch vs independent recompute")
            if probe_n.get("a") != na or probe_n.get("b") != nb:
                errs.append("stage0 probe_Nnl mismatch vs independent recompute")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        panels_path = root / "stage1" / "panels.json"
        if panels_path.is_file():
            panels = json.loads(panels_path.read_text())
            panel = panels.get("n17_l3") or {}
            rows = panel.get("rows") or []
            if rows:
                r0 = rows[0]
                F = Field(17, MODULI[17])
                ra, rb, na, nb, ok = encode_trace_nnl(
                    F, CURVE_B[17], r0["basis"], XR[17]
                )[:5]
                if not ok:
                    errs.append("stage1 row0 twin disagree")
                if r0.get("r_Tr") != ra or r0.get("N_nl") != na:
                    errs.append("stage1 row0 values mismatch independent twin")
            # Band polarity check: in_band iff rho <= -0.70 when finite
            rho = panel.get("spearman_rho")
            if rho is not None and rho == rho:
                expected = rho <= SPEARMAN_BAND
                if panel.get("in_band") != expected:
                    errs.append("in_band inconsistent with Spearman <= -0.70 band")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
