#!/usr/bin/env python3
"""
TASK-20260814-1ce70d (Validator) -- probe1: independently confirm the
SEED_ROOT=715923 seed formula, without importing stage0_v2_feasibility.py
(fresh, independent re-derivation, not a re-use of the producer's own code).

Checks:
  - The bisection instance (d=256, beta=40) reproduces seed_used=1398073216,
    matching TASK-20260814-ffd791's own reported seed at this cell and
    stage0_v2_feasibility.py's own bisection_results.json / run_manifest.yaml.
  - All 6 main-grid cells' seeds match run_manifest.yaml's own
    main_grid_seeds_used table, for the 5 cells where a seed_used value was
    recorded; for the 6th cell (d=256, beta=70), whose worker died before
    writing seed_used, this probe independently derives what the seed MUST
    have been from the same deterministic formula (FPLLL.set_random_seed is
    called before any lattice construction), which run_manifest.yaml itself
    could not recover.
"""
import json
import numpy as np

SEED_ROOT = 715923
STAGE_INDEX = 0

MAIN_CELLS = [(256, 40), (256, 55), (256, 70), (512, 40), (512, 55), (512, 70)]

REPORTED_MAIN_GRID_SEEDS = {
    (256, 40): 1398073216,
    (256, 55): 1615872610,
    (256, 70): None,  # not recoverable per run_manifest.yaml, disclosed reason
    (512, 40): 2074339090,
    (512, 55): 452658293,
    (512, 70): 915347894,
}

REPORTED_BISECTION_SEED = 1398073216
REPORTED_BISECTION_D_BETA = (256, 40)
REPORTED_TASK_20260814_FFD791_SEED_AT_D256_B40 = 1398073216


def seed_for(d, beta, arm_index=0, draw_index=0):
    return int(
        np.random.default_rng(
            [SEED_ROOT, STAGE_INDEX, d, beta, arm_index, draw_index]
        ).integers(0, 2**31 - 1)
    )


def main():
    results = {"seed_root": SEED_ROOT, "formula": "default_rng([SEED_ROOT, stage_index, d, beta, arm_index, draw_index])"}

    bisect_seed = seed_for(*REPORTED_BISECTION_D_BETA)
    results["bisection_check"] = {
        "d_beta": REPORTED_BISECTION_D_BETA,
        "independently_computed_seed": bisect_seed,
        "matches_stage0_v2_bisection_results_json": bisect_seed == REPORTED_BISECTION_SEED,
        "matches_task_20260814_ffd791_precedent_seed": bisect_seed == REPORTED_TASK_20260814_FFD791_SEED_AT_D256_B40,
    }

    main_grid_check = []
    for d, beta in MAIN_CELLS:
        computed = seed_for(d, beta)
        reported = REPORTED_MAIN_GRID_SEEDS[(d, beta)]
        entry = {
            "d": d, "beta": beta,
            "independently_computed_seed": computed,
            "reported_seed_in_run_manifest": reported,
        }
        if reported is None:
            entry["note"] = (
                "run_manifest.yaml records seed_used: null for this cell "
                "(worker SIGTERM-killed at the 7200s cap before it reached "
                "json.dump). This probe independently derives what the seed "
                "MUST have been from the same deterministic formula "
                "(FPLLL.set_random_seed(seed) is called before any lattice "
                "construction in worker_main_cell), corroborating -- not "
                "contradicting -- the producer's own disclosed gap."
            )
            entry["matches"] = "N/A (reported value not recorded)"
        else:
            entry["matches"] = computed == reported
        main_grid_check.append(entry)

    results["main_grid_seed_check"] = main_grid_check
    results["all_recorded_seeds_match"] = all(
        e["matches"] is True for e in main_grid_check if e["matches"] != "N/A (reported value not recorded)"
    )

    print(json.dumps(results, indent=2))
    with open("probe1_seed_formula_check_output.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
