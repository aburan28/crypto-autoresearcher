#!/usr/bin/env python3
"""Blind re-derivation of two archived S2BD M_delta-swap flags.

Reads only RUN-ECDLP-5cad48-S2BD raw-result.json fields G_exact,
M_delta_exact, and cs_bound_recorded for S2-P8219 M=9, S2-P8219 M=20,
and S2-P32779 M=13.
Must not import or read the S2MX producer or its run artifacts.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
S2BD = REPO / "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2BD/raw-result.json"
WANTED = {("S2-P8219", 9), ("S2-P8219", 20), ("S2-P32779", 13)}
FORBIDDEN = [
    REPO / "experiments/EXP-ECDLP-5cad48/implementation/stage2_m_delta_swap.py",
    REPO / "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2MX/raw-result.json",
    REPO / "experiments/EXP-ECDLP-5cad48/execution-report-s2mx.yaml",
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
    same = found[("S2-P8219", 20)]
    nxt = found[("S2-P32779", 13)]
    if miss["M_delta_exact"] == 0.0 or same["M_delta_exact"] == 0.0 or nxt["M_delta_exact"] == 0.0:
        raise SystemExit("refuse: M_delta_exact is zero")

    def flags(hold: dict) -> dict:
        miss_if_md = bool((miss["G_exact"] / hold["M_delta_exact"]) <= miss["cs_bound_recorded"])
        this_if_miss = bool((hold["G_exact"] / miss["M_delta_exact"]) <= hold["cs_bound_recorded"])
        return {
            "cell": hold["cell"],
            "M": hold["M"],
            "arm": hold["arm"],
            "role": hold["role"],
            "G_exact": hold["G_exact"],
            "M_delta_exact": hold["M_delta_exact"],
            "cs_bound_recorded": hold["cs_bound_recorded"],
            "miss_would_hold_if_this_M_delta": miss_if_md,
            "this_would_hold_if_miss_M_delta": this_if_miss,
        }

    payload = {
        "n_blind_holds": 2,
        "miss": {
            "cell": miss["cell"],
            "M": miss["M"],
            "arm": miss["arm"],
            "role": miss["role"],
            "G_exact": miss["G_exact"],
            "M_delta_exact": miss["M_delta_exact"],
            "cs_bound_recorded": miss["cs_bound_recorded"],
        },
        "next_tightest": flags(nxt),
        "same_cell_M20": flags(same),
    }
    dest = Path(__file__).with_name("blind_raw.json")
    dest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
