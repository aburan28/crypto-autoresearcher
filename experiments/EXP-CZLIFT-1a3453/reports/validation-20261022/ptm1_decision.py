#!/usr/bin/env python3
"""PTM-1 through the frozen decision rule (TASK-20261022-8ebef8).

Substitutes the planted sequence f(k) = floor(p k / n) mod p for one higher
digit on every recorded curve, builds its shuffled control with the
producer's own per-curve permutation (rng protocol reproduced by
j2_replay.protocol_point and the eps draws), scores both with the producer's
instrument run.spectrum, and evaluates the specification's falsification
criterion under the two available readings of "its shuffled control has
none": per curve-row (raw rows) and per digit aggregated over curves
(manifest by_digit.shuffled_above, the only per-digit record).
Usage: python3 -B ptm1_decision.py OUT.json RUN_DIR RUN_DIR
"""
from __future__ import annotations

import importlib.util
import json
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
import j2_replay  # noqa: E402


def producer_perm(c, seed):
    p, A, N, n = c["p"], c["A"], c["N"], c["n"]
    rng = random.Random(seed * 104_729 + p * 17 + (A % p))
    j2_replay.protocol_point(A % p, c["B"] % p, p, n, N // n, rng)
    for _ in range(1, n):
        rng.randrange(p)
    return np.array(rng.sample(range(n), n))


def main():
    out_path, *runs = sys.argv[1:]
    out = {}
    for run_dir in runs:
        raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
        seed = raw["metrics"]["seed"]
        rows = []
        for c in raw["raw"]["curves"]:
            p, n = c["p"], c["n"]
            k = np.arange(n, dtype=np.int64)
            f = (p * k // n) % p
            f[0] = 0
            perm = producer_perm(c, seed)
            r_max, r_ab, T = producer.spectrum(f, p, n)
            s_max, s_ab, _ = producer.spectrum(f[perm], p, n)
            rows.append({"label": c["label"], "arm": c["arm"], "p": p, "n": n, "T": T,
                         "planted_above": r_ab, "planted_max": r_max,
                         "shuffled_above": s_ab, "shuffled_max": s_max})
        agg_above = sum(r["planted_above"] for r in rows)
        agg_shuf = sum(r["shuffled_above"] for r in rows)
        out[os.path.basename(run_dir.rstrip("/"))] = {
            "seed": seed,
            "curves_planted_spike": sum(r["planted_above"] > 0 for r in rows),
            "curves_shuffled_spike": sum(r["shuffled_above"] > 0 for r in rows),
            "curves_planted_spike_and_shuffled_clean": sum(r["planted_above"] > 0 and r["shuffled_above"] == 0 for r in rows),
            "by_digit_above": agg_above, "by_digit_shuffled_above": agg_shuf,
            "falsifies_per_row_reading": any(r["planted_above"] > 0 and r["shuffled_above"] == 0 for r in rows),
            "falsifies_per_digit_aggregate_reading": agg_above > 0 and agg_shuf == 0,
            "success_criterion_would_hold": agg_above == 0 and agg_shuf == 0,
            "shuffled_spike_curves": [(r["label"], r["p"], r["n"], round(r["shuffled_max"] - r["T"], 2))
                                      for r in rows if r["shuffled_above"] > 0],
            "rows": rows}
    json.dump(out, open(out_path, "w"), indent=1)
    for run, v in out.items():
        print(run, {k: v[k] for k in v if k != "rows"})


if __name__ == "__main__":
    main()
