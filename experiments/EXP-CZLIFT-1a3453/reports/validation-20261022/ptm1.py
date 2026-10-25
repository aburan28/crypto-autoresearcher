#!/usr/bin/env python3
"""PTM-1 proves-too-much control for EXP-CZLIFT-1a3453 (TASK-20261022-8ebef8).

Planted digit sequence f(k) = floor(p k / n) mod p (a deterministic function of
the discrete log k; f(0) = 0 placeholder as in the instrument's arrays) is fed
to the PRODUCER'S instrument, run.spectrum (imported read-only; run with
python3 -B so no bytecode is written into producer directories), and to the
validator's own spectrum (j2_replay.spectrum), for every curve (p, n)
recorded in both runs.  Also fed: the planted sequence re-indexed by a seeded
full-range permutation (the instrument's shuffled-control construction), which
must come back clean.  The sealed blind grid (blind/blind_output.json) is
compared cell by cell.
Usage: python3 -B ptm1.py OUT.json RUN_DIR RUN_DIR
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, REPO)
spec = importlib.util.spec_from_file_location(
    "producer_run", os.path.join(REPO, "experiments/EXP-CZLIFT-1a3453/implementation/run.py"))
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)
sys.path.insert(0, HERE)
import j2_replay  # noqa: E402  (validator's own spectrum)


def main():
    out_path, *runs = sys.argv[1:]
    blind = json.load(open(os.path.join(HERE, "blind", "blind_output.json")))["C_planted_PTM1"]["grid"]
    rows = []
    for run_dir in runs:
        raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
        seed = raw["metrics"]["seed"]
        for c in raw["raw"]["curves"]:
            p, n = c["p"], c["n"]
            m = (n - 1) // 2
            k = np.arange(n, dtype=np.int64)
            f = (p * k // n) % p
            f[0] = 0
            inst_max, inst_above, inst_T = producer.spectrum(f, p, n)
            my_max, my_above, my_T, my_a, my_t = j2_replay.spectrum(f, p, n)
            perm = np.array(random.Random(seed * 7 + p).sample(range(n), n))
            sh_max, sh_above, _ = producer.spectrum(f[perm], p, n)
            b = blind.get(f"{p},{n}")
            rows.append({"run": os.path.basename(run_dir.rstrip("/")), "arm": c["arm"], "label": c["label"],
                         "p": p, "n": n, "m": m, "T": inst_T,
                         "instrument_max": inst_max, "instrument_above": inst_above,
                         "validator_max": my_max, "validator_above": my_above,
                         "argmax_a": my_a, "argmax_t": my_t,
                         "instrument_excess": inst_max - inst_T,
                         "shuffled_planted_max": sh_max, "shuffled_planted_above": sh_above,
                         "blind_zone_m_le_T": m <= inst_T,
                         "blind_grid_planted_max": None if b is None else b["planted_max"],
                         "blind_grid_T": None if b is None else b["T"],
                         "blind_grid_spikes": None if b is None else b["planted_spikes"]})
    summ = {
        "curves": len(rows),
        "instrument_vs_validator_max_abs_diff": max(abs(r["instrument_max"] - r["validator_max"]) for r in rows),
        "instrument_vs_validator_above_equal": all(r["instrument_above"] == r["validator_above"] for r in rows),
        "blind_grid_found": sum(r["blind_grid_planted_max"] is not None for r in rows),
        "blind_grid_vs_instrument_max_abs_diff": max(abs(r["blind_grid_planted_max"] - r["instrument_max"])
                                                     for r in rows if r["blind_grid_planted_max"] is not None),
        "blind_grid_vs_instrument_T_abs_diff": max(abs(r["blind_grid_T"] - r["T"])
                                                   for r in rows if r["blind_grid_T"] is not None),
        "blind_grid_vs_instrument_spikes_equal": all(r["blind_grid_spikes"] == r["instrument_above"]
                                                     for r in rows if r["blind_grid_spikes"] is not None),
        "spiking_curves": sum(r["instrument_above"] > 0 for r in rows),
        "non_spiking_curves": [(r["run"], r["label"], r["p"], r["n"], r["m"], round(r["T"], 3),
                                round(r["instrument_max"], 3)) for r in rows if r["instrument_above"] == 0],
        "non_spiking_all_in_blind_zone": all(r["blind_zone_m_le_T"] for r in rows if r["instrument_above"] == 0),
        "spiking_all_outside_blind_zone": all(not r["blind_zone_m_le_T"] for r in rows if r["instrument_above"] > 0),
        "min_excess_spiking": min(r["instrument_excess"] for r in rows if r["instrument_above"] > 0),
        "max_excess": max(r["instrument_excess"] for r in rows),
        "median_excess_spiking": float(np.median([r["instrument_excess"] for r in rows if r["instrument_above"] > 0])),
        "max_over_m_range": [min(r["instrument_max"] / r["m"] for r in rows), max(r["instrument_max"] / r["m"] for r in rows)],
        "shuffled_planted_spikes_total": sum(r["shuffled_planted_above"] for r in rows),
        "shuffled_planted_max_excess": max(r["shuffled_planted_max"] - r["T"] for r in rows),
        "per_run_blind_zone_curves": {},
    }
    for run in sorted({r["run"] for r in rows}):
        rr = [r for r in rows if r["run"] == run]
        summ["per_run_blind_zone_curves"][run] = {
            "total": len(rr), "blind": sum(r["blind_zone_m_le_T"] for r in rr),
            "cm_blind": sum(r["blind_zone_m_le_T"] for r in rr if r["arm"] == "cm_canonical"),
            "random_blind": sum(r["blind_zone_m_le_T"] for r in rr if r["arm"] == "random_naive")}
    json.dump({"summary": summ, "rows": rows}, open(out_path, "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
