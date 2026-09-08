#!/usr/bin/env python3
"""Stage 0: curve generation with certificates (all rungs) + forced-value
table, written and SHA256-hashed BEFORE any curve arm is enumerated
(ordering_control). Writes RUN-RELN-f202be-stage0."""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import curve_gen
import zn_integer_arms as zn
import runutil as ru
import spectral_crosscheck as sc

RUNS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runs"))
RUN_ID = "RUN-RELN-f202be-stage0"
RUN_DIR = os.path.join(RUNS_DIR, RUN_ID)

RUNGS = [14, 16, 18, 20]


def main():
    t_start = time.time()
    os.makedirs(RUN_DIR, exist_ok=True)
    stdout_lines = []

    def log(msg):
        print(msg)
        stdout_lines.append(msg)

    log(f"stage0 start {ru.now_iso()}")

    # Spectral module self-test (independent brute-force check), recorded
    # before any curve is used.
    selftest = sc.selftest()
    ru.write_json(os.path.join(RUN_DIR, "spectral_selftest.json"), selftest)
    log(f"spectral selftest: {selftest}")
    if not selftest["pass"]:
        log("FATAL: spectral selftest failed, aborting stage0")
        with open(os.path.join(RUN_DIR, "stdout.log"), "w") as f:
            f.write("\n".join(stdout_lines))
        sys.exit(1)

    curves_by_rung = {}
    forced_table_rows = []

    for k in RUNGS:
        log(f"generating curves for rung {k}")
        res = curve_gen.generate_curves_for_rung(k, min_curves=3, max_seeds=400)
        curves_by_rung[k] = res
        log(f"  rung {k}: accepted={len(res['accepted'])} rejected={len(res['rejected'])} "
            f"seeds_scanned={res['seeds_scanned']} sufficient={res['sufficient']}")
        if not res["sufficient"]:
            log(f"  STOP RULE: rung {k} has fewer than 3 accepted curves within 400 seeds; "
                f"rung reported not_run.")
            continue
        for c in res["accepted"]:
            row = zn.forced_value_table_for_curve(c["N"])
            row["rung"] = k
            row["seed"] = c["seed"]
            row["p"] = c["p"]
            forced_table_rows.append(row)
            log(f"    curve seed={c['seed']} p={c['p']} N={c['N']} B1_even={row['B1_even']} "
                f"B2={row['B2']} mu={row['mu']:.4f}")

    curves_json = {
        k: {
            "accepted": res["accepted"],
            "rejected": res["rejected"],
            "seeds_scanned": res["seeds_scanned"],
            "sufficient": res["sufficient"],
        }
        for k, res in curves_by_rung.items()
    }
    ru.write_json(os.path.join(RUN_DIR, "curves.json"), curves_json)

    forced_table = {"rows": forced_table_rows}
    ru.write_json(os.path.join(RUN_DIR, "forced-value-table.json"), forced_table)
    forced_table_hash = ru.sha256_json(forced_table)
    log(f"forced-value-table.json written and hashed: sha256={forced_table_hash}")

    manifest = {
        "run": {
            "id": RUN_ID,
            "experiment_id": "EXP-RELN-f202be",
            "stage": "stage0_derivations_and_forced_value_table",
            "status": "completed_valid",
            "code": {
                "commit": ru.git_commit(),
                "dirty": ru.git_dirty(),
                "command": "python3 source/run_stage0.py",
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "reasoning_effort": None,
                "fallback_used": False,
                "fallback_reason": None,
                "independent_session": False,
            },
            "environment": ru.environment_info(),
            "forced_value_table_sha256": forced_table_hash,
            "ordering_control": "forced-value-table.json written and hashed before any curve-arm "
                                 "enumeration in stage2; timestamps in this manifest and stage2 "
                                 "manifests are directly comparable.",
            "timing": {"started_at_epoch": t_start, "finished_at_epoch": time.time(),
                       "wall_seconds": time.time() - t_start},
            "rungs_sufficient": {str(k): curves_by_rung[k]["sufficient"] for k in RUNGS},
        }
    }
    ru.write_json(os.path.join(RUN_DIR, "manifest.json"), manifest)
    with open(os.path.join(RUN_DIR, "command.txt"), "w") as f:
        f.write("python3 source/run_stage0.py\n")
    with open(os.path.join(RUN_DIR, "environment.json"), "w") as f:
        json.dump(ru.environment_info(), f, indent=2)
    with open(os.path.join(RUN_DIR, "stdout.log"), "w") as f:
        f.write("\n".join(stdout_lines))
    with open(os.path.join(RUN_DIR, "stderr.log"), "w") as f:
        f.write("")

    log(f"stage0 done, wall={time.time()-t_start:.2f}s")


if __name__ == "__main__":
    main()
