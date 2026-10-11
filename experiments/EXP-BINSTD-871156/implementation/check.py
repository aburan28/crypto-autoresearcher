#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-871156 run artifacts.

Recomputes twin r_Tr / N_nl on a probe row without importing run.py stage
orchestration. Validates raw-result / manifest agreement and forbids v1 seed.
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

EXPERIMENT_ID = "EXP-BINSTD-871156"
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
FORBIDDEN_V1_SEED = 202610038782
EXPECTED_SEED = 202610038196


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
            if pre.get("catalog_seed") == FORBIDDEN_V1_SEED:
                errs.append("forbidden v1 catalog seed reused")
            if pre.get("catalog_seed") != EXPECTED_SEED:
                errs.append("catalog_seed drifted from frozen contract")
            gates = pre.get("admission_gates") or {}
            if gates.get("distinct_rTr_min") != 3 or gates.get("distinct_Nnl_min") != 2:
                errs.append("admission gates drifted")
        if (root / "stage0" / "v-catalog.json").is_file():
            cat = json.loads((root / "stage0" / "v-catalog.json").read_text())
            cell = cat["cells"]["n17_l3"]
            if cell.get("catalog_size", 0) < 24:
                errs.append("n17_l3 catalog_size < 24")
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
            cell4 = cat["cells"].get("n17_l4") or {}
            if cell4.get("catalog_size", 0) < 24:
                errs.append("n17_l4 catalog_size < 24")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        panels_path = root / "stage1" / "panels.json"
        if panels_path.is_file():
            panels = json.loads(panels_path.read_text(encoding="utf-8"))
            for key in ("n17_l3", "n17_l4"):
                if key not in panels:
                    errs.append(f"missing panel {key}")
            summary = raw.get("panels_summary") or {}
            for key, panel in panels.items():
                s = summary.get(key) or {}
                if s and s.get("distinct_rTr") != panel.get("distinct_rTr"):
                    errs.append(f"{key} distinct_rTr summary mismatch")
        results = root / "RESULTS.md"
        if results.is_file():
            text = results.read_text(encoding="utf-8")
            if outcome and outcome not in text:
                errs.append("RESULTS.md missing outcome label")
            if "Not a re-run of EXP-BINSTD-8196d7" not in text and "not a re-run" not in text.lower():
                errs.append("RESULTS.md missing not-a-rerun disclosure")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
