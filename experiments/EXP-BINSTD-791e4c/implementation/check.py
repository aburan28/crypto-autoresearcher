#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-791e4c run artifacts.

Recomputes twin r_Tr / N_nl on a probe row without importing run.py stage
orchestration. Validates raw-result / manifest agreement and forbids prior
catalog seeds (dbca92/871156/6fd454/8196d7).
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

EXPERIMENT_ID = "EXP-BINSTD-791e4c"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
    "O-NULL-FAILS-ANTI-BAND",
    "O-NULL-ALSO-IN-ANTI-BAND",
    "O-STAGE2-SKIPPED",
}
MODULI = {
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
}
CURVE_B = {19: 1, 23: 1}
XR = {19: 0x2B41, 23: 0x55}
SPEARMAN_BAND = -0.70
FORBIDDEN_SEEDS = (202610038196, 202610038782, 202610039715, 202610034821)
EXPECTED_SEED = 202610033364
FLOOR_RTR = 4
FLOOR_NNL = 4
FLOOR_UNIQUE_PAIRS = 4
STAGE1_KEYS = ("n19_l3", "n19_l4", "n23_l3", "n23_l4")


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
            if pre.get("catalog_seed") in FORBIDDEN_SEEDS:
                errs.append("forbidden prior catalog seed reused")
            if pre.get("catalog_seed") != EXPECTED_SEED:
                errs.append("catalog_seed drifted from frozen contract")
            gates = pre.get("admission_gates") or {}
            if (
                gates.get("distinct_rTr_min") != FLOOR_RTR
                or gates.get("distinct_Nnl_min") != FLOOR_NNL
                or gates.get("unique_pairs_min") != FLOOR_UNIQUE_PAIRS
            ):
                errs.append("admission gates drifted")
            if not pre.get("stage2_authorized"):
                errs.append("Stage-2 must be authorized on this card")
        if (root / "stage0" / "v-catalog.json").is_file():
            cat = json.loads((root / "stage0" / "v-catalog.json").read_text())
            for key, n, ell in (
                ("n19_l3", 19, 3),
                ("n19_l4", 19, 4),
                ("n23_l3", 23, 3),
                ("n23_l4", 23, 4),
            ):
                cell = (cat.get("cells") or {}).get(key) or {}
                if cell.get("catalog_size", 0) < 24:
                    errs.append(f"{key} catalog_size < 24")
            cell = cat["cells"]["n19_l3"]
            basis = cell["catalog"][0]["basis"]
            F = Field(19, MODULI[19])
            ra, rb, na, nb, ok = encode_trace_nnl(F, CURVE_B[19], basis, XR[19])[:5]
            if not ok:
                errs.append("independent twin disagree on stage0 probe")
            probe_r = cell.get("probe_rTr") or {}
            probe_n = cell.get("probe_Nnl") or {}
            if probe_r.get("a") != ra or probe_r.get("b") != rb:
                errs.append("stage0 probe_rTr mismatch vs independent recompute")
            if probe_n.get("a") != na or probe_n.get("b") != nb:
                errs.append("stage0 probe_Nnl mismatch vs independent recompute")
            if "n17_l3" in (cat.get("cells") or {}) or "n17_l4" in (cat.get("cells") or {}):
                errs.append("n=17 cells must not be frozen as Stage-1 on this successor")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        panels_path = root / "stage1" / "panels.json"
        if panels_path.is_file():
            panels = json.loads(panels_path.read_text(encoding="utf-8"))
            for key in STAGE1_KEYS:
                if key not in panels:
                    errs.append(f"missing panel {key}")
            summary = raw.get("panels_summary") or {}
            for key, panel in panels.items():
                s = summary.get(key) or {}
                if s and s.get("distinct_rTr") != panel.get("distinct_rTr"):
                    errs.append(f"{key} distinct_rTr summary mismatch")
                if s and s.get("unique_pairs") != panel.get("unique_pairs"):
                    errs.append(f"{key} unique_pairs summary mismatch")
        results = root / "RESULTS.md"
        if results.is_file():
            text = results.read_text(encoding="utf-8")
            if outcome and outcome not in text:
                errs.append("RESULTS.md missing outcome label")
            if "dbca92" not in text.lower() and "Not a re-run" not in text:
                errs.append("RESULTS.md missing not-a-rerun disclosure")
    elif stage == 2:
        if outcome == "O-IMPEDIMENT":
            pass
        elif outcome == "O-STAGE2-SKIPPED":
            if not (root / "stage1" / "control-table.json").is_file():
                errs.append("missing stage1/control-table.json for skipped Stage-2")
        else:
            null_path = root / "stage2" / "null-results.json"
            if not null_path.is_file():
                errs.append("missing stage2/null-results.json")
            else:
                doc = json.loads(null_path.read_text(encoding="utf-8"))
                if doc.get("null_outcome") != outcome:
                    errs.append("null-results outcome mismatch vs raw-result")
                cells = doc.get("cells") or {}
                for key in STAGE1_KEYS:
                    if key not in cells:
                        errs.append(f"missing Stage-2 cell {key}")
            results = root / "RESULTS.md"
            if results.is_file() and outcome not in results.read_text(encoding="utf-8"):
                errs.append("RESULTS.md missing Stage-2 outcome label")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
