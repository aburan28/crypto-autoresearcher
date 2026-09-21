#!/usr/bin/env python3
"""Blind re-derivation of the Stage 0 P2 aligned ratio.

Reads only RUN-ECDLP-5cad48-S0 raw-result P2 fields.
Does not read stage0.py, stage0_cs_audit.py, S0CS raw-result,
or execution-report-s0cs.yaml.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

S0 = Path("experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S0/raw-result.json")


def main() -> int:
    raw = json.loads(S0.read_text())
    p2 = raw["arms"]["P2"]
    g = float(p2["G"])
    m_delta = float(p2["M_delta"])
    w = float(p2["W"])
    min_q = float(p2["min_q"])
    cs = float(p2["cs_bound"])
    aligned = g / m_delta
    cs_re = 1.0 + math.sqrt(w / min_q)
    out = {
        "arm": "P2",
        "G": g,
        "M_delta": m_delta,
        "W": w,
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
        "TASK-20260907-e85ce5/blind_raw.json"
    )
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
