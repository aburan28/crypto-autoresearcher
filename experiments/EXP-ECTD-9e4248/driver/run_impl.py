"""
run_impl.py -- RUN-ECTD-9e4248-impl entry point: smoke test on ONE vertical edge
plus its matched horizontal comparison pair, exercising the full new instrumentation
(conductor/end-ring computation, vertical Velu-isogeny construction,
CTRL-END-RING-CERTIFICATE) before the full screen is attempted.

Run: python3 -m driver.run_impl   (from experiments/EXP-ECTD-9e4248/)
"""
import json
import os
import sys
import time

from . import run_common, orchestrate

RUN_ID = "RUN-ECTD-9e4248-impl"
EXPERIMENT_ID = "EXP-ECTD-9e4248"
BUDGET = run_common.Budget(wall_clock_seconds_per_run=10800, total_cpu_hours=60,
                            maximum_memory_gb=16, maximum_runs=2)

FB_SIZE = 8
GB_BUDGET = {"max_pairs": 20000, "max_degree": 60, "wall_seconds": 60.0}
MACAULAY_CAP = 6
BIT_CANDIDATES = list(range(40, 45))
MASTER_SEEDS = [301]


def main():
    run_dir = os.path.join(os.path.dirname(__file__), "..", "runs", RUN_ID)
    run_dir = os.path.abspath(run_dir)
    os.makedirs(run_dir, exist_ok=True)

    started_at = time.time()
    result = orchestrate.run_pipeline(
        master_seeds=MASTER_SEEDS, n_needed=1, budget=BUDGET, rng_seed=301001,
        fb_size=FB_SIZE, gb_budget=GB_BUDGET, macaulay_cap=MACAULAY_CAP,
        bit_candidates=BIT_CANDIDATES, coordinate_null_subsample=1,
        per_pair_attempts=5000, max_extra_seeds=4,
    )
    finished_at = time.time()

    n_completed = len(result["completed_edges"])
    achieved_bits = [e["achieved_bits"] for e in result["completed_edges"]]
    status = "completed_valid" if n_completed >= 1 else "invalid_measurement"
    invalid_reason = None if n_completed >= 1 else "smoke edge failed to construct within attempt budget"

    raw = {
        "run_id": RUN_ID,
        "experiment_id": EXPERIMENT_ID,
        "purpose": "smoke test: implement conductor/volcano computation, vertical Velu "
                   "isogeny construction, and CTRL-END-RING-CERTIFICATE on ONE vertical "
                   "edge plus its horizontal comparison pair",
        "n_completed_edges": n_completed,
        "master_seeds": MASTER_SEEDS,
        "achieved_bit_length_distribution": achieved_bits,
        "target_bit_candidates_declared": BIT_CANDIDATES,
        "n_bit_range_sampling_requirement_note": (
            "per-seed target bit length drawn from a genuinely-varying candidate set "
            "(not a single fixed width -- fixes D3); this run used the SAME "
            "sub-range as EXP-ECTD-001's own disclosed scoping decision (40-44 bits, "
            "not the full declared [40,60]) for BSGS/rho tractability -- see "
            "implementation.md"),
        "attempts_log": result["attempts_log"],
        "end_ring_fail_count": result["end_ring_fail_count"],
        "coordinate_null_receipts": result["coordinate_null_receipts"],
        "glv_instrument": result["glv_instrument"],
        "permutation_results": result["permutation_results"],
        "ctrl_no_class_invariant_endpoint": result["ctrl_no_class_invariant_endpoint"],
        "decision_result": result["decision_result"],
        "decision_branch": result["decision_result"]["decision_branch"],
        "decision_branch_note": (
            "n_completed_edges=1 < min_vertical_edges=8 by DESIGN for this smoke run "
            "(this run intentionally covers 1 edge, mirroring RUN-ECTD-001-impl's own "
            "documented scope) -- resource_incomplete here reflects the SMOKE RUN'S "
            "designed scope, not an execution failure; see edge-level detail below for "
            "whether the new instrumentation itself worked"),
        "edges_elapsed_s": result["edges_elapsed_s"],
        "wall_seconds_total": finished_at - started_at,
        "certificate": {"kind": "none",
                        "note": "pure measurement + construction run; the matched "
                                "rho/bsgs baseline WITHIN each edge does emit its own "
                                "discrete_log certificates, independently verified -- "
                                "see completed_edges[*].rho_bsgs"},
    }

    # per-edge detail (includes rho_bsgs certificates)
    raw["completed_edges_detail"] = result["completed_edges"]

    run_common.write_json(os.path.join(run_dir, "raw-result.json"), raw)

    manifest = run_common.build_run_manifest(
        run_id=RUN_ID, experiment_id=EXPERIMENT_ID,
        command="python3 -m driver.run_impl",
        started_at=started_at, finished_at=finished_at,
        seeds={"master_seeds": MASTER_SEEDS, "rng_seed": 301001},
        parameters={"fb_size": FB_SIZE, "gb_budget": GB_BUDGET, "macaulay_cap": MACAULAY_CAP,
                    "bit_candidates": BIT_CANDIDATES, "n_needed": 1},
        result_dict={"decision_branch": result["decision_result"]["decision_branch"],
                     "n_completed_classes": n_completed,
                     "wall_seconds_total": finished_at - started_at,
                     "certificate": {"kind": "none"}},
        artifacts_list=["raw-result.json", "manifest.yaml", "environment.json",
                        "stdout.log", "stderr.log", "command.txt"],
        status=status, invalid_reason=invalid_reason,
    )
    run_common.write_yaml(os.path.join(run_dir, "manifest.yaml"), manifest)
    run_common.write_json(os.path.join(run_dir, "environment.json"), run_common.environment_snapshot())
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write("python3 -m driver.run_impl\n")

    print(json.dumps({"status": status, "decision_branch": result["decision_result"]["decision_branch"],
                       "n_completed_edges": n_completed, "wall_seconds": finished_at - started_at}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
