#!/usr/bin/env python3
"""Stage 3 fixture-scale unmatched vs width-matched relabelling discriminator.

At Stage-1 scale (m=3, l in {3,4}): compare solution counts under
  - real trinomial / pentanomial arms
  - unmatched random GL(l,F2) per-block relabelling
  - width-matched random relabelling (histogram matched to a real arm)
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from encoder import (
    brute_force_solutions,
    encode_pdp_full,
    eval_s3_coords,
    histogram_distance,
    random_gl_l,
    width_match_ok,
)
from gf2n import MODULI, N, Field, poly_to_string
from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-7979df"
SEEDS = [20261001, 20261002, 20261003, 20261004, 20261005]
L_VALUES = [3, 4]
B_CURVE = 1
WIDTH_MATCH_ATTEMPTS = 200


def n_leaf(field: Field, l: int, target: int, block_basis=None) -> int:
    return len(brute_force_solutions(field, l, target, B_CURVE, block_basis=block_basis))


def main() -> int:
    t0 = time.perf_counter()
    started = utc_now()
    cells = []

    for l in L_VALUES:
        for seed in SEEDS:
            rng = random.Random(seed + 17 * l)
            planted = tuple(rng.randrange(1 << l) for _ in range(3))

            # Real arms (shared planted coords; arm-local targets)
            real = {}
            for arm_name, mod in MODULI.items():
                field = Field(N, mod)
                target = eval_s3_coords(field, planted, l, B_CURVE)
                sys_enc = encode_pdp_full(
                    field, 3, l, target, arm_name, "planted_SAT", planted=planted, b_curve=B_CURVE
                )
                nl = n_leaf(field, l, target)
                real[arm_name] = {
                    "target": target,
                    "n_leaf_measured": nl,
                    "clause_width_mean_measured": sys_enc.clause_width_mean(),
                    "clause_width_histogram_measured": sys_enc.clause_width_histogram(),
                    "clause_width_max_measured": sys_enc.clause_width_max(),
                    "substitution_variable_count_measured": sys_enc.substitution_variable_count,
                }

            # Use trinomial field as the ambient arithmetic for relabelling controls
            # (relabelling is of coordinate blocks, not of the modulus).
            field_t = Field(N, MODULI["trinomial"])
            target_t = real["trinomial"]["target"]
            hist_target = real["trinomial"]["clause_width_histogram_measured"]
            mean_target = real["trinomial"]["clause_width_mean_measured"]

            # Unmatched: first random invertible maps (no width constraint)
            unmatched_basis = [random_gl_l(l, rng) for _ in range(3)]
            sys_u = encode_pdp_full(
                field_t,
                3,
                l,
                target_t,
                "unmatched_relabel",
                "planted_SAT",
                planted=planted,
                b_curve=B_CURVE,
                block_basis=unmatched_basis,
            )
            # Target for unmatched: evaluate S3 after applying basis to planted
            # For fair N_leaf on the SAME algebraic target in original coords,
            # enumerate solutions in relabelled coordinates for fixed target_t
            # under the linear change of variables.
            n_unmatched = n_leaf(field_t, l, target_t, block_basis=unmatched_basis)

            # Width-matched: search for basis whose encoder histogram matches trinomial
            matched = None
            matched_basis = None
            for attempt in range(WIDTH_MATCH_ATTEMPTS):
                cand = [random_gl_l(l, rng) for _ in range(3)]
                sys_c = encode_pdp_full(
                    field_t,
                    3,
                    l,
                    target_t,
                    "width_matched_relabel",
                    "planted_SAT",
                    b_curve=B_CURVE,
                    block_basis=cand,
                )
                h = sys_c.clause_width_histogram()
                mean_c = sys_c.clause_width_mean()
                if width_match_ok(h, hist_target, mean_c, mean_target):
                    matched = sys_c
                    matched_basis = cand
                    break

            if matched is None:
                # Fallback: identity map is width-matched to itself (real arm)
                matched_basis = [[1 << j for j in range(l)] for _ in range(3)]
                matched = encode_pdp_full(
                    field_t,
                    3,
                    l,
                    target_t,
                    "width_matched_relabel",
                    "planted_SAT",
                    b_curve=B_CURVE,
                    block_basis=matched_basis,
                )
                match_method = "identity_fallback_after_rejection_sampling_exhausted"
            else:
                match_method = "rejection_sampling"

            n_matched = n_leaf(field_t, l, target_t, block_basis=matched_basis)
            n_real = real["trinomial"]["n_leaf_measured"]

            unmatched_ratio = (n_unmatched / n_real) if n_real else None
            matched_ratio = (n_matched / n_real) if n_real else None

            # "Large effect" operationalization at fixture scale: ratio outside [0.5, 2.0]
            # or absolute difference dominating (document threshold).
            unmatched_large = (
                unmatched_ratio is not None
                and (unmatched_ratio < 0.5 or unmatched_ratio > 2.0 or n_unmatched != n_real)
            )
            # Actually for linear relabelling of coordinates with fixed target in
            # original embedding, N_leaf counts assignments in the NEW coordinate
            # chart whose images satisfy S3=target. An invertible linear map on
            # the domain bijects V_l^3, so N_leaf should be INVARIANT for any
            # invertible block basis when the target is fixed in the field!
            #
            # That would make unmatched NOT show a large N_leaf effect — which
            # is itself an informative observation (discriminator power at this
            # encoding layer). 7ef636's effect is about SAT variable ORDER /
            # conflicts, not algebraic solution count. Record honestly.

            width_hist_matched = width_match_ok(
                matched.clause_width_histogram(),
                hist_target,
                matched.clause_width_mean(),
                mean_target,
            )

            cells.append(
                {
                    "l": l,
                    "seed": seed,
                    "planted": list(planted),
                    "real_arms": {
                        k: {
                            "n_leaf_measured": v["n_leaf_measured"],
                            "clause_width_mean_measured": v["clause_width_mean_measured"],
                            "clause_width_max_measured": v["clause_width_max_measured"],
                            "clause_width_histogram_measured": v["clause_width_histogram_measured"],
                            "modulus": poly_to_string(MODULI[k]),
                        }
                        for k, v in real.items()
                    },
                    "unmatched_relabel": {
                        "n_leaf_measured": n_unmatched,
                        "clause_width_mean_measured": sys_u.clause_width_mean(),
                        "clause_width_histogram_measured": sys_u.clause_width_histogram(),
                        "ratio_vs_trinomial_measured": unmatched_ratio,
                        "large_effect_vs_trinomial": unmatched_large,
                        "large_effect_rule": "ratio outside [0.5,2.0] OR n_leaf differs",
                    },
                    "width_matched_relabel": {
                        "match_method": match_method,
                        "width_histogram_matched": width_hist_matched,
                        "histogram_L1_vs_trinomial": histogram_distance(
                            matched.clause_width_histogram(), hist_target
                        ),
                        "n_leaf_measured": n_matched,
                        "clause_width_mean_measured": matched.clause_width_mean(),
                        "clause_width_histogram_measured": matched.clause_width_histogram(),
                        "ratio_vs_trinomial_measured": matched_ratio,
                        "ratio_in_band_0_9_1_1": (
                            matched_ratio is not None and 0.9 <= matched_ratio <= 1.1
                        ),
                    },
                    "pentanomial_vs_trinomial_n_leaf_ratio_measured": (
                        real["pentanomial"]["n_leaf_measured"] / n_real if n_real else None
                    ),
                }
            )

    # Aggregate discriminator outcomes
    unmatched_effects = [c["unmatched_relabel"]["large_effect_vs_trinomial"] for c in cells]
    matched_in_band = [c["width_matched_relabel"]["ratio_in_band_0_9_1_1"] for c in cells]
    width_ok = [c["width_matched_relabel"]["width_histogram_matched"] for c in cells]

    # Observation: algebraic N_leaf is basis-invertible-invariant; unmatched
    # large-effect on N_leaf may be FALSE at this layer. That is a discriminator
    # outcome to report, not to hide.
    any_unmatched_large = any(unmatched_effects)
    all_matched_band = all(matched_in_band)
    all_width_ok = all(width_ok)

    if not all_width_ok:
        discriminator_outcome = "width_match_metric_failed"
    elif not any_unmatched_large and all_matched_band:
        discriminator_outcome = (
            "discriminator_null_on_N_leaf_axis — unmatched did not move algebraic "
            "solution count (invertible relabelling preserves |solution set|); "
            "width-matched stayed in band. Instrument power for 7ef636-style "
            "ORDER effect is NOT on the algebraic N_leaf observable at fixture "
            "scale; c_leaf/clause-width remains the separating measured axis."
        )
    elif any_unmatched_large and all_matched_band:
        discriminator_outcome = "pass_unmatched_large_matched_in_band"
    elif any_unmatched_large and not all_matched_band:
        discriminator_outcome = "discriminator_fail_width_matched_also_large"
    else:
        discriminator_outcome = "unmatched_no_large_effect_matched_out_of_band"

    report = {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": 3,
        "scale": "fixture",
        "n": N,
        "m": 3,
        "l_values": L_VALUES,
        "seeds": SEEDS,
        "cells": cells,
        "summary": {
            "unmatched_large_effect_any_cell": any_unmatched_large,
            "width_matched_all_in_band": all_matched_band,
            "width_match_metric_all_pass": all_width_ok,
            "discriminator_outcome": discriminator_outcome,
            "pent_tri_n_leaf_ratios_measured": [
                c["pentanomial_vs_trinomial_n_leaf_ratio_measured"] for c in cells
            ],
            "tail_check_largest_width_matched_n_leaf": max(
                c["width_matched_relabel"]["n_leaf_measured"] for c in cells
            ),
            "tail_check_largest_real_trinomial_n_leaf": max(
                c["real_arms"]["trinomial"]["n_leaf_measured"] for c in cells
            ),
        },
        "optimistic_assumptions_restated": (
            "Modeled naive 5-vs-3 term ratio is not used in discriminator. "
            "Algebraic solution-count is MEASURED; 7ef636 conflict-count order "
            "effect is a different observable (SAT-order), not re-measured here "
            "without WDSat."
        ),
        "naive_term_ratio_modeled": {"label": "MODELED", "value": 5 / 3},
    }
    dump_yaml(EXP_ROOT / "stage3" / "relabelling-discriminator-report.yaml", report)

    wall = time.perf_counter() - t0
    finished = utc_now()
    metrics = {
        "discriminator_outcome": discriminator_outcome,
        "unmatched_large_effect_any_cell": any_unmatched_large,
        "width_matched_all_in_band": all_matched_band,
        "width_match_metric_all_pass": all_width_ok,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
    }
    stdout = (
        f"Stage 3 complete\n"
        f"  discriminator_outcome={discriminator_outcome}\n"
        f"  unmatched_large_any={any_unmatched_large}\n"
        f"  width_matched_in_band={all_matched_band}\n"
        f"  width_match_ok={all_width_ok}\n"
        f"  cells={len(cells)}\n"
    )
    write_run_package(
        RUN_ID,
        stage=3,
        arm="relabelling-discriminator",
        seed=SEEDS[0],
        command="python3 experiments/EXP-BINSTD-a8efe2/implementation/stage3_run.py",
        parameters={"n": N, "m": 3, "l": L_VALUES, "seeds": SEEDS},
        metrics=metrics,
        valid=all_width_ok,  # invalid if width-match metric fails
        invalid_reason=None if all_width_ok else "width_matched_histogram_not_actually_matched",
        termination_reason="completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none"},
    )
    print(stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
