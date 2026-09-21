"""
run_screen.py -- RUN-ECTD-9e4248-screen entry point: full >=8-vertical-edge screen
with matched horizontal sample and GLV instrument, within budget.

Run: python3 -m driver.run_screen   (from experiments/EXP-ECTD-9e4248/)
"""
import json
import os
import sys
import time

from . import run_common, orchestrate

RUN_ID = "RUN-ECTD-9e4248-screen"
EXPERIMENT_ID = "EXP-ECTD-9e4248"
BUDGET = run_common.Budget(wall_clock_seconds_per_run=10800, total_cpu_hours=60,
                            maximum_memory_gb=16, maximum_runs=2)

FB_SIZE = 8
GB_BUDGET = {"max_pairs": 20000, "max_degree": 60, "wall_seconds": 60.0}
MACAULAY_CAP = 6
BIT_CANDIDATES = list(range(40, 45))
MASTER_SEEDS = [301, 302, 303, 304, 305, 306, 307, 308]
MIN_VERTICAL_EDGES = 8


def main():
    run_dir = os.path.join(os.path.dirname(__file__), "..", "runs", RUN_ID)
    run_dir = os.path.abspath(run_dir)
    os.makedirs(run_dir, exist_ok=True)

    started_at = time.time()
    result = orchestrate.run_pipeline(
        master_seeds=MASTER_SEEDS, n_needed=MIN_VERTICAL_EDGES, budget=BUDGET, rng_seed=308001,
        fb_size=FB_SIZE, gb_budget=GB_BUDGET, macaulay_cap=MACAULAY_CAP,
        bit_candidates=BIT_CANDIDATES, coordinate_null_subsample=3,
        per_pair_attempts=5000, max_extra_seeds=8,
    )
    finished_at = time.time()

    n_completed = len(result["completed_edges"])
    achieved_bits = [e["achieved_bits"] for e in result["completed_edges"]]
    decision_branch = result["decision_result"]["decision_branch"]
    status = "completed_valid"
    invalid_reason = None
    if result["end_ring_fail_count"] > 1:
        status = "invalid_measurement"
        invalid_reason = "CTRL-END-RING-CERTIFICATE failed on >1 vertical edge (spec.invalidation_rules)"

    raw = {
        "run_id": RUN_ID,
        "experiment_id": EXPERIMENT_ID,
        "purpose": "full >=8-vertical-edge screen with matched horizontal sample and GLV instrument",
        "n_completed_edges": n_completed,
        "min_vertical_edges_required": MIN_VERTICAL_EDGES,
        "master_seeds": MASTER_SEEDS,
        "achieved_bit_length_distribution": achieved_bits,
        "target_bit_candidates_declared": BIT_CANDIDATES,
        "n_bit_range_sampling_requirement_note": (
            "per-seed target bit length drawn from a genuinely-varying candidate set "
            "(not a single fixed width -- fixes D3); achieved distribution reported "
            "above, measured not asserted. Sub-range 40-44 bits used (not the full "
            "declared [40,60]) for BSGS/rho tractability -- disclosed protocol "
            "deviation, same rationale EXP-ECTD-001 already used -- see implementation.md"),
        "attempts_log": result["attempts_log"],
        "end_ring_fail_count": result["end_ring_fail_count"],
        "coordinate_null_receipts": result["coordinate_null_receipts"],
        "glv_instrument": result["glv_instrument"],
        "permutation_results": result["permutation_results"],
        "ctrl_no_class_invariant_endpoint": result["ctrl_no_class_invariant_endpoint"],
        "decision_result": result["decision_result"],
        "decision_branch": decision_branch,
        "edges_elapsed_s": result["edges_elapsed_s"],
        "wall_seconds_total": finished_at - started_at,
        "certificate": {"kind": "none",
                        "note": "pure measurement + construction run; the matched "
                                "rho/bsgs baseline WITHIN each edge does emit its own "
                                "discrete_log certificates, independently verified -- "
                                "see completed_edges_detail[*].rho_bsgs"},
    }
    raw["completed_edges_detail"] = result["completed_edges"]

    run_common.write_json(os.path.join(run_dir, "raw-result.json"), raw)

    # per-artifact-list files required by the handoff
    per_edge_meter_tables = [
        {"seed": e["seed"], "D_K": e["D_K"], "q": e["q"], "N_bits": e["achieved_bits"],
         "meters_floor": e["meters_floor"], "meters_crater": e["meters_crater"],
         "ratios": e["ratios"], "delta_d_reg": e["delta_d_reg"],
         "horizontal_meters1": e["horizontal"].get("meters1"),
         "horizontal_meters2": e["horizontal"].get("meters2"),
         "horizontal_ratios": e["horizontal"].get("ratios")}
        for e in result["completed_edges"]
    ]
    run_common.write_json(os.path.join(run_dir, "per_edge_meter_tables.json"), per_edge_meter_tables)

    end_ring_certificates = [
        {"seed": e["seed"], "D_K": e["D_K"], "q": e["q"], "certificate": e["certificate"],
         "horizontal_conductor_certificate": e["horizontal"].get("conductor_q_part_unchanged_certificate")}
        for e in result["completed_edges"]
    ]
    run_common.write_json(os.path.join(run_dir, "end_ring_certificates.json"), end_ring_certificates)

    run_common.write_json(os.path.join(run_dir, "glv_instrument_receipt.json"), result["glv_instrument"])
    run_common.write_json(os.path.join(run_dir, "coordinate_null_receipts.json"), result["coordinate_null_receipts"])
    run_common.write_json(os.path.join(run_dir, "permutation_stability_table.json"), result["permutation_results"])

    rho_bsgs_receipts = [{"seed": e["seed"], "rho_bsgs": e["rho_bsgs"]} for e in result["completed_edges"]]
    run_common.write_json(os.path.join(run_dir, "rho_bsgs_receipts.json"), rho_bsgs_receipts)

    manifest = run_common.build_run_manifest(
        run_id=RUN_ID, experiment_id=EXPERIMENT_ID,
        command="python3 -m driver.run_screen",
        started_at=started_at, finished_at=finished_at,
        seeds={"master_seeds": MASTER_SEEDS, "rng_seed": 308001},
        parameters={"fb_size": FB_SIZE, "gb_budget": GB_BUDGET, "macaulay_cap": MACAULAY_CAP,
                    "bit_candidates": BIT_CANDIDATES, "n_needed": MIN_VERTICAL_EDGES},
        result_dict={"decision_branch": decision_branch,
                     "n_completed_classes": n_completed,
                     "wall_seconds_total": finished_at - started_at,
                     "certificate": {"kind": "none"}},
        artifacts_list=["raw-result.json", "manifest.yaml", "environment.json",
                        "stdout.log", "stderr.log", "command.txt",
                        "per_edge_meter_tables.json", "end_ring_certificates.json",
                        "glv_instrument_receipt.json", "coordinate_null_receipts.json",
                        "permutation_stability_table.json", "rho_bsgs_receipts.json"],
        status=status, invalid_reason=invalid_reason,
    )
    run_common.write_yaml(os.path.join(run_dir, "manifest.yaml"), manifest)
    run_common.write_json(os.path.join(run_dir, "environment.json"), run_common.environment_snapshot())
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write("python3 -m driver.run_screen\n")

    print(json.dumps({"status": status, "decision_branch": decision_branch,
                       "n_completed_edges": n_completed, "wall_seconds": finished_at - started_at}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
