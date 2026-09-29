#!/usr/bin/env python3
"""Blind re-derivation of two archived S2BD counterfactual aligned ratios.

Reads only RUN-ECDLP-5cad48-S2BD raw-result.json fields G_exact and
M_delta_exact for S2-P8219 M=9 and S2-P32779 M=13.
Must not import or read the S2TP producer or its run artifacts.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
S2BD = REPO / "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2BD/raw-result.json"
WANTED = {("S2-P8219", 9), ("S2-P32779", 13)}
FORBIDDEN = [
    REPO / "experiments/EXP-ECDLP-5cad48/implementation/stage2_tight_pair.py",
    REPO / "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2TP/raw-result.json",
    REPO / "experiments/EXP-ECDLP-5cad48/execution-report-s2tp.yaml",
]


def main() -> int:
    for path in FORBIDDEN:
        if path.exists():
            # Existence is allowed; opening is not. Do not read these paths.
            pass
    raw = json.loads(S2BD.read_text())
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S2BD":
        raise SystemExit("refuse: unexpected S2BD run_id")
    found = {}
    for cell in raw.get("cells") or []:
        key = (cell.get("cell"), int(cell.get("M")))
        if key not in WANTED:
            continue
        found[key] = {
            "cell": cell["cell"],
            "M": int(cell["M"]),
            "arm": cell.get("arm", "floor(Mx/p)"),
            "role": cell.get("role"),
            "G_exact": float(cell["G_exact"]),
            "M_delta_exact": float(cell["M_delta_exact"]),
            "cs_bound_recorded": float(cell["cs_bound_recorded"]),
        }
    if set(found) != WANTED:
        raise SystemExit(f"refuse: expected {WANTED}, got {set(found)}")
    miss = found[("S2-P8219", 9)]
    nxt = found[("S2-P32779", 13)]
    if miss["M_delta_exact"] == 0.0 or nxt["M_delta_exact"] == 0.0:
        raise SystemExit("refuse: M_delta_exact is zero")
    cf_next_g = nxt["G_exact"] / miss["M_delta_exact"]
    cf_next_md = miss["G_exact"] / nxt["M_delta_exact"]
    payload = {
        "n_pair_cells": 2,
        "cells": [miss, nxt],
        "counterfactual_aligned_miss_with_next_G": cf_next_g,
        "counterfactual_aligned_miss_with_next_M_delta": cf_next_md,
        "miss_would_hold_if_next_G": bool(cf_next_g <= miss["cs_bound_recorded"]),
        "miss_would_hold_if_next_M_delta": bool(cf_next_md <= miss["cs_bound_recorded"]),
    }
    dest = Path(__file__).with_name("blind_raw.json")
    dest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
