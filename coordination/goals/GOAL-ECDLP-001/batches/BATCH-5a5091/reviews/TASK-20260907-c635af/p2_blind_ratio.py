#!/usr/bin/env python3
"""Blind re-derivation of the Stage 2 P2 aligned ratio.

Reads only RUN-ECDLP-5cad48-S2G raw-result S2-P523 M=5 P2 fields.
Does not read stage0.py, stage1.py, stage2.py, stage2_exact.py,
stage0_cs_audit.py, stage1_cs_audit.py, stage2_cs_audit.py,
S2CS raw-result, or execution-report-s2cs.yaml.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

S2 = Path("experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2G/raw-result.json")


def main() -> int:
    raw = json.loads(S2.read_text())
    p2 = None
    for cell in raw["cells"]:
        if cell["id"] != "S2-P523":
            continue
        for ms in cell["Ms"]:
            if int(ms["M"]) != 5:
                continue
            p2 = ms["arms"]["P2"]
    if p2 is None:
        raise SystemExit("refuse: S2-P523 M=5 P2 not found")
    g = float(p2["G_exact"])
    m_delta = float(p2["M_delta_exact"])
    w = float(p2["W_exact"])
    min_q = float(p2["min_q"])
    cs = float(p2["cs_bound_exact"])
    aligned = g / m_delta
    cs_re = 1.0 + math.sqrt(w / min_q)
    out = {
        "cell": "S2-P523",
        "M": 5,
        "arm": "P2",
        "G_exact": g,
        "M_delta_exact": m_delta,
        "W_exact": w,
        "min_q": min_q,
        "cs_bound_recorded": cs,
        "cs_bound_recomputed": cs_re,
        "aligned_ratio": aligned,
        "aligned_holds": aligned <= cs,
        "raw_G_versus_cs_bound": g <= cs,
        "raw_G_versus_cs_bound_is_units_mismatch": True,
    }
    dest = Path(
        "coordination/goals/GOAL-ECDLP-001/batches/BATCH-5a5091/reviews/"
        "TASK-20260907-c635af/blind_raw.json"
    )
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
