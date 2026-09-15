#!/usr/bin/env python3
"""Summarise the relabelling (proves-too-much object 2) control for V2."""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

ART = Path(__file__).resolve().parent.parent / "artifacts"

runs = json.loads((ART / "ptm2_wdsat_runs.json").read_text())
extra = json.loads((ART / "ptm2_null_and_identity.json").read_text())
by = {r["tag"]: r for r in runs + extra}

orig = by["ptm2_baseline_original_n15l5-11-U"]
ident = by["ptm2_identity_rewrite_n15l5-11-U"]
null = by["ptm2_null_original_n15l5-11-U"]
perms = [by[f"ptm2_perm_seed{s}"] for s in range(1661196, 1661206)]
nperms = [by[f"ptm2_nullperm_seed{s}"] for s in (1661196, 1661197, 1661198)]

pc = [p["conflicts"] for p in perms]
nc = [p["conflicts"] for p in nperms]
O, N = orig["conflicts"], null["conflicts"]

geo = lambda xs: round(st.geometric_mean(xs), 1)

out = {
    "instance": "n15l5-11-U (Xn15l5-11-U.anf, shipped S_4 point-decomposition instance)",
    "engine": "wdsat default (no flags), build v2_987b7f5ef9, MAX_ID 502, byte-identical to producer build wdsat_987b7f5ef9",
    "all_statuses_UNSAT": all(r.get("status") == "UNSAT" for r in [orig, ident, null] + perms + nperms),
    "structured_shipped_order_conflicts": O,
    "identity_rewrite_conflicts": ident["conflicts"],
    "identity_file_byte_identical_to_source": True,
    "matched_null_object_conflicts_my_measurement": N,
    "matched_null_object_conflicts_recorded_in_RUN-ICPERF-305ca3": 7697173,
    "permuted_structured": {
        "n_seeds": len(pc), "seeds": list(range(1661196, 1661206)),
        "conflicts": pc,
        "min": min(pc), "median": st.median(pc), "max": max(pc),
        "geometric_mean": geo(pc),
        "spread_max_over_min": round(max(pc) / min(pc), 1),
        "ratio_to_shipped_order": {"min": round(min(pc) / O, 2),
                                   "median": round(st.median(pc) / O, 1),
                                   "max": round(max(pc) / O, 1),
                                   "geometric_mean": round(geo(pc) / O, 1)},
        "ratio_to_null": {"min": round(min(pc) / N, 3),
                          "median": round(st.median(pc) / N, 3),
                          "max": round(max(pc) / N, 2),
                          "geometric_mean": round(geo(pc) / N, 3)},
        "n_seeds_at_or_above_3e5": sum(1 for c in pc if c >= 3e5),
        "n_seeds_above_10x_shipped": sum(1 for c in pc if c > 10 * O),
        "walls_s": [p["wall_s"] for p in perms],
        "loadavg1_at_start": [p["loadavg1_at_start"] for p in perms],
    },
    "permuted_null": {
        "n_seeds": len(nc), "seeds": [1661196, 1661197, 1661198],
        "conflicts": nc, "min": min(nc), "median": st.median(nc), "max": max(nc),
        "spread_max_over_min": round(max(nc) / min(nc), 2),
        "ratio_to_unpermuted_null": [round(c / N, 3) for c in nc],
    },
    "order_sensitivity": {
        "structured_spread_over_orders": round(max(pc) / min(pc), 1),
        "null_spread_over_orders": round(max(nc + [N]) / min(nc + [N]), 2),
        "shipped_order_advantage_over_null": round(N / O, 1),
        "median_random_order_advantage_over_null": round(N / st.median(pc), 2),
    },
}
print(json.dumps(out, indent=1))
(ART / "ptm2_analysis.json").write_text(json.dumps(out, indent=1))
