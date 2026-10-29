#!/usr/bin/env python3
"""Blind re-derivation of the EXP-ICPERF-e467a5 primary metrics.

Written by the audit reader (validator, claude-opus-5-5) from
experiments/EXP-ICPERF-e467a5/specification.yaml alone. It does not import,
read or reuse implementation/run.py, implementation/check.py, RESULTS.md or
any report. It reads only the frozen specification, the unit's raw output
(raw-result.json) and the session journal's session_finished summary.

Usage: python3 -I blind_rederive.py <repo_root>
Prints one JSON object. Writes nothing.
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

import yaml

root = Path(sys.argv[1])
exp = root / "experiments/EXP-ICPERF-e467a5"
spec = yaml.safe_load((exp / "specification.yaml").read_text())["experiment"]
inp = spec["inputs"]
cp, cs, cst = inp["c_probe_ns"], inp["c_state_ns"], inp["c_step_ns"]
bn, bd, T = inp["bl_num"], inp["bl_den"], inp["states"]

# Spec formula, literally: price = (370 * 2100 * 10) / (21 * 40 * 40).
# The "10" is either `states` or `bl_den`; both are 10 in the frozen inputs,
# so the two readings coincide here. Both are computed and reported.
price_states = Fraction(cp * cs * T, bn * cst * cst)
price_blden = Fraction(cp * cs * bd, bn * cst * cst)

# Spec literals for the online times (preregistered_prediction.formula).
spec_online = {
    (1000, 2): (18500, 80),
    (4000, 2): (74000, 320),
    (1000, 4): (9250, 40),
}
spec_probes = {(1000, 2): 50, (4000, 2): 200, (1000, 4): 25}

derived_cells = []
for cell in inp["cells"]:
    r, A = cell["r"], cell["A"]
    # control 3: probe count is (r/A)/states; require exact division
    # (invalidation rule: an inexact division invalidates the run).
    exact = (r % A == 0) and ((r // A) % T == 0)
    bsgs = Fraction(r, A) / T
    ic_ns, bl_ns = spec_online[(r, A)]
    ratio = Fraction(ic_ns, bl_ns)
    derived_cells.append({
        "name": cell["name"], "r": r, "A": A,
        "bsgs_probes": str(bsgs), "exact_division": exact,
        "spec_probe_literal": spec_probes[(r, A)],
        "probe_time_check": bsgs * cp == ic_ns,  # probes * c_probe == spec IC online time
        "spec_online_ns": [ic_ns, bl_ns],
        "ratio": f"{ratio.numerator}/{ratio.denominator}",
        "ratio_equals_price": ratio == price_states,
    })

derived = {
    "price_ratio_num": price_states.numerator,
    "price_ratio_den": price_states.denominator,
    "price_reading_bl_den_same": price_states == price_blden,
    "ratios_agree": all(c["ratio_equals_price"] for c in derived_cells),
    "all_match_bsgs": all(Fraction(c["bsgs_probes"]) == c["spec_probe_literal"]
                          and c["exact_division"] for c in derived_cells),
    "cells": derived_cells,
}

# Recompute the same quantities from the unit's raw output fields (not from
# its reported booleans), then compare with its reported fields.
raw = json.loads((exp / "runs/RUN-ICPERF-943efa/raw-result.json").read_text())
raw_cells = []
for c in raw["cells"]:
    rr = Fraction(c["ic_online_ns"], c["bl_online_ns"])
    raw_cells.append({
        "name": c["name"],
        "ratio_from_raw_times": f"{rr.numerator}/{rr.denominator}",
        "reported_ratio": f"{c['ratio_num']}/{c['ratio_den']}",
        "probes_equal_bsgs_formula": Fraction(c["r"], c["A"]) / T == c["probes"],
        "times_equal_spec_literals": (c["ic_online_ns"], c["bl_online_ns"]) == spec_online[(c["r"], c["A"])],
        "ic_time_equals_probes_x_cprobe": c["probes"] * cp == c["ic_online_ns"],
    })
from_raw = {
    "price_ratio_num": raw["price_ratio_num"],
    "price_ratio_den": raw["price_ratio_den"],
    "price_reduced": Fraction(raw["price_ratio_num"], raw["price_ratio_den"]).denominator == raw["price_ratio_den"],
    "ratios_agree_recomputed": all(Fraction(c["ic_online_ns"], c["bl_online_ns"]) == price_states for c in raw["cells"]),
    "all_match_bsgs_recomputed": all(Fraction(c["r"], c["A"]) / T == c["probes"] for c in raw["cells"]),
    "reported_ratios_agree": raw["ratios_agree"],
    "reported_all_match_bsgs": raw["all_match_bsgs"],
    "inputs_equal_spec": [raw[k] for k in ("c_probe_ns", "c_state_ns", "c_step_ns", "bl_num", "bl_den", "states")] == [cp, cs, cst, bn, bd, T],
    "cells_equal_spec": sorted((c["name"], c["r"], c["A"]) for c in raw["cells"]) == sorted((c["name"], c["r"], c["A"]) for c in inp["cells"]),
    "cells": raw_cells,
}

# Session summary (session_finished) metrics.
summary = None
for line in (exp / "runbook-sessions/RBS-ICPERF-b7e41c/journal.jsonl").read_text().splitlines():
    e = json.loads(line)
    if e["type"] == "session_finished":
        summary = {"metrics": e["summary"]["metrics"], "units": e["summary"]["units"]}

print(json.dumps({"derived_from_spec": derived, "recomputed_from_raw": from_raw,
                  "session_summary": summary}, indent=1, sort_keys=True))
