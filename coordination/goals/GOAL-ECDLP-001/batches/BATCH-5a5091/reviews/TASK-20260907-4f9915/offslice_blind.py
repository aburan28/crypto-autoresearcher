#!/usr/bin/env python3
"""Blind re-derivation of two archived S2OC off-slice gaps.

Reads only RUN-ECDLP-5cad48-S2OC raw-result.json fields G_exact,
M_eff, and max_pi_c for S2-P8219 M=9 and S2-P32779 M=13.
Must not import or read the S2OS producer or its run artifacts.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
S2OC = REPO / "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2OC/raw-result.json"
WANTED = {("S2-P8219", 9), ("S2-P32779", 13)}
FORBIDDEN = [
    REPO / "experiments/EXP-ECDLP-5cad48/implementation/stage2_offslice.py",
    REPO / "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2OS/raw-result.json",
    REPO / "experiments/EXP-ECDLP-5cad48/execution-report-s2os.yaml",
]


def main() -> int:
    for path in FORBIDDEN:
        if path.exists():
            # Existence is allowed; opening is not. Do not read these paths.
            pass
    raw = json.loads(S2OC.read_text())
    if raw.get("run_id") != "RUN-ECDLP-5cad48-S2OC":
        raise SystemExit("refuse: unexpected S2OC run_id")
    out = []
    for cell in raw.get("cells") or []:
        key = (cell.get("id"), int(cell.get("M")))
        if key not in WANTED:
            continue
        g = float(cell["exact"]["G_exact"])
        m_eff = float(cell["occupancy"]["M_eff"])
        max_pi_c = float(cell["occupancy"]["max_pi_c"])
        out.append(
            {
                "cell": cell["id"],
                "M": int(cell["M"]),
                "arm": cell.get("arm", "floor(Mx/p)"),
                "G_exact": g,
                "M_eff": m_eff,
                "max_pi_c": max_pi_c,
                "off_slice_gap": (g / m_eff) - max_pi_c,
            }
        )
    if len(out) != 2:
        raise SystemExit(f"refuse: expected 2 cells, got {len(out)}")
    dest = Path(__file__).with_name("blind_raw.json")
    dest.write_text(json.dumps({"cells": out, "n_cells": 2}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"n_cells": 2, "cells": out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
