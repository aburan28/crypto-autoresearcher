#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-9001b3 run artifacts.

Validates shared-baseline package-median floor-clear: freeze cites
EV-BINSTD-602614 / EV-BINSTD-cd47a8; Stage-0 floor_clear_calibration_ok +
density_batch_size + shared_baseline; band arithmetic;
process_isolated_delta_shared_baseline rss_mode; no Bedrock/break.
"""
from __future__ import annotations

import json
import resource
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import encode_n_var  # noqa: E402
from gf2n import Field  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-9001b3"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
MODULI = {
    23: (1 << 23) | (1 << 5) | 1,
    29: (1 << 29) | (1 << 2) | 1,
    31: (1 << 31) | (1 << 3) | 1,
}
CURVE_B = {23: 1, 29: 1, 31: 1}
XR = {23: 0x55, 29: 0x71, 31: 0x13}
FORBIDDEN_SEEDS = {202610032056, 2026100375050, 2026100343342, 2026100377593}
RSS_MODE = "process_isolated_delta_shared_baseline"


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

    cited = raw.get("evidence_cited")
    if isinstance(cited, list):
        if "EV-BINSTD-602614" not in cited or "EV-BINSTD-cd47a8" not in cited:
            errs.append(
                "evidence_cited must include EV-BINSTD-602614 and EV-BINSTD-cd47a8"
            )

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
            pre = json.loads(
                (root / "stage0" / "preregistered-predictions.json").read_text()
            )
            if pre.get("alpha") != 1.0 or pre.get("M0_bytes") != 16 * 1024 * 1024:
                errs.append("preregistered (alpha,M0) drifted from frozen contract")
            if pre.get("catalog_seed") in FORBIDDEN_SEEDS:
                errs.append("successor catalog_seed must differ from parent seeds")
            ec = pre.get("evidence_cited") or []
            if "EV-BINSTD-602614" not in ec or "EV-BINSTD-cd47a8" not in ec:
                errs.append(
                    "Stage-0 freeze must cite EV-BINSTD-602614 and EV-BINSTD-cd47a8"
                )
            if "shared_baseline" not in str(pre.get("delta_formula", "")):
                errs.append("Stage-0 missing shared_baseline delta_rss formula")
            if "density_batch" not in str(pre.get("density_batch_formula", "")):
                errs.append("Stage-0 missing density_batch formula")
            if pre.get("rss_mode") != RSS_MODE:
                errs.append("Stage-0 rss_mode must be process_isolated_delta_shared_baseline")
            if outcome == "O-STAGE0-OK":
                if not pre.get("floor_clear_calibration_ok"):
                    errs.append("O-STAGE0-OK requires floor_clear_calibration_ok")
                if not pre.get("density_batch_size"):
                    errs.append("O-STAGE0-OK requires frozen density_batch_size")
                if int(pre.get("density_batch_size") or 0) < 32:
                    errs.append("frozen density_batch_size must be >= 32 (parent froze 8)")
                if not pre.get("shared_baseline_rss_bytes"):
                    errs.append("O-STAGE0-OK requires frozen shared_baseline_rss_bytes")
            try:
                _ = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
            except Exception as exc:  # noqa: BLE001
                errs.append(f"RSS probe unavailable: {exc}")
        if (root / "stage0" / "v-catalog.json").is_file():
            cat = json.loads((root / "stage0" / "v-catalog.json").read_text())
            if "allocator_ok" not in cat:
                errs.append("Stage-0 catalog missing allocator_ok")
            if "floor_clear_calibration_ok" not in cat:
                errs.append("Stage-0 catalog missing floor_clear_calibration_ok")
            if "shared_baseline_rss_bytes" not in cat:
                errs.append("Stage-0 catalog missing shared_baseline_rss_bytes")
            cell = cat["cells"]["n31_l12"]
            basis = cell["catalog"][0]["basis"]
            F = Field(31, MODULI[31])
            na, nb, dok = encode_n_var(F, CURVE_B[31], basis, XR[31])[:3]
            if not dok:
                errs.append("independent twin N_var disagree on Stage-0 probe")
            if na != cell["probe_N_var"]["a"] or nb != cell["probe_N_var"]["b"]:
                errs.append("Stage-0 probe N_var mismatch vs independent recompute")

    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        if (root / "stage1" / "panels.json").is_file() and (
            root / "stage0" / "preregistered-predictions.json"
        ).is_file():
            pre = json.loads(
                (root / "stage0" / "preregistered-predictions.json").read_text()
            )
            blob = json.loads((root / "stage1" / "panels.json").read_text())
            panels = blob["panels"]
            m0 = pre["M0_bytes"]
            alpha = pre["alpha"]
            shared = int(pre.get("shared_baseline_rss_bytes") or 0)
            if not pre.get("floor_clear_calibration_ok"):
                errs.append("Stage-1 requires Stage-0 floor_clear_calibration_ok")
            for p in panels:
                expected = int(m0 * (2.0 ** (alpha * p["ell"])))
                if p.get("band_bytes") != expected:
                    errs.append(f"band_bytes mismatch for ell={p['ell']}")
                if p.get("rss_mode") != RSS_MODE:
                    errs.append(
                        "Stage-1 panel missing process_isolated_delta_shared_baseline rss_mode"
                    )
                if "delta_rss_bytes" not in p:
                    errs.append("Stage-1 panel missing delta_rss_bytes")
                if "density_batch" not in p:
                    errs.append("Stage-1 panel missing density_batch")
                if p.get("baseline_source") != "stage0_shared_frozen":
                    errs.append("Stage-1 panel must use stage0_shared_frozen baseline")
                if p.get("shared_baseline_rss_bytes") != shared:
                    errs.append("Stage-1 panel baseline drifted from Stage-0 freeze")
                if p.get("peak_rss_bytes") is not None:
                    holds = p["peak_rss_bytes"] <= expected
                    if p.get("band_holds") != holds:
                        errs.append("band_holds inconsistent with peak vs band")
                    expected_delta = max(0, int(p["peak_rss_bytes"]) - shared)
                    if int(p["delta_rss_bytes"]) != expected_delta:
                        errs.append("delta_rss_bytes inconsistent with shared baseline")
            if "instrument_clears_floor" not in blob:
                errs.append("stage1/panels missing instrument_clears_floor")
            if blob.get("rss_mode") != RSS_MODE:
                errs.append("stage1/panels rss_mode mismatch")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
