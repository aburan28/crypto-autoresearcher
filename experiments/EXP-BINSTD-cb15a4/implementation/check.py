#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-cb15a4 run artifacts.

Recomputes twin N_var on a probe row and validates band arithmetic without
importing run.py stage orchestration. Validates raw-result / manifest.
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

EXPERIMENT_ID = "EXP-BINSTD-cb15a4"
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
            if pre.get("alpha") != 1.0 or pre.get("M0_bytes") != 16 * 1024 * 1024:
                errs.append("preregistered (alpha,M0) drifted from frozen contract")
            # Independent RSS probe availability
            try:
                _ = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
            except Exception as exc:  # noqa: BLE001
                errs.append(f"RSS probe unavailable: {exc}")
        if (root / "stage0" / "v-catalog.json").is_file():
            cat = json.loads((root / "stage0" / "v-catalog.json").read_text())
            cell = cat["cells"]["n17_l3"]
            basis = cell["catalog"][0]["basis"]
            F = Field(17, MODULI[17])
            na, nb, dok = encode_n_var(F, CURVE_B[17], basis, XR[17])[:3]
            if not dok:
                errs.append("independent twin N_var disagree on Stage-0 probe")
            if na != cell["probe_N_var"]["a"] or nb != cell["probe_N_var"]["b"]:
                errs.append("Stage-0 probe N_var mismatch vs independent recompute")

    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        if (root / "RESULTS.md").is_file():
            text = (root / "RESULTS.md").read_text(encoding="utf-8")
            named = [o for o in OUTCOMES if o in text and o != "O-STAGE0-OK"]
            # Exactly one scientific O-* (excluding O-STAGE0-OK) should appear as Outcome
            if f"**{outcome}**" not in text and f"Outcome: **{outcome}**" not in text:
                if f"Outcome: **{outcome}**" not in text.replace(" ", ""):
                    if outcome not in text:
                        errs.append("RESULTS.md does not name the raw-result outcome")
        if (root / "stage1" / "panels.json").is_file() and (
            root / "stage0" / "preregistered-predictions.json"
        ).is_file():
            pre = json.loads((root / "stage0" / "preregistered-predictions.json").read_text())
            panels = json.loads((root / "stage1" / "panels.json").read_text())["panels"]
            m0 = pre["M0_bytes"]
            alpha = pre["alpha"]
            for p in panels:
                expected = int(m0 * (2.0 ** (alpha * p["ell"])))
                if p.get("band_bytes") != expected:
                    errs.append(f"band_bytes mismatch for ell={p['ell']}")
                if p.get("peak_rss_bytes") is not None:
                    holds = p["peak_rss_bytes"] <= expected
                    if p.get("band_holds") != holds:
                        errs.append("band_holds inconsistent with peak vs band")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
