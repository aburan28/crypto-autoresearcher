"""RUN-DTREE-012: aggregation -- optimal B_med per size, C_2/C_1 with
bootstrap CIs, slope decision (reported, not concluded), fully charged
totals.

"Fully charged total" (secondary metric, spec: "preprocessing + medium-base
logs + K descents + verification"). K is not pinned by the frozen spec; this
module fixes K = standard_B (the number of relations a real linear-algebra
stage would need is the standard index-calculus convention: roughly one
relation per factor-base element) and states that choice here rather than
leaving it implicit. "Verification" cost (certificate re-checking) is not
separately instrumented -- it is reported as "not separately measured" rather
than folded silently into the total.
"""
from __future__ import annotations

import hashlib
import json
import os

import costs


def deterministic_seed(*parts) -> int:
    """A reproducible integer seed from arbitrary parts, in place of Python's
    built-in hash() -- which is DELIBERATELY randomized per-process for
    strings (PYTHONHASHSEED) unless fixed, and so is not reproducible across
    separate invocations of this same command. Every source of randomness in
    this experiment must be reconstructible from the recorded command and
    revision alone (AGENTS.md rule 4 / the completion gate); a per-process
    hash salt would silently break that for the bootstrap CI.
    """
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(digest[:8], 16)


def load_run_raw(run_dir: str) -> dict:
    with open(os.path.join(run_dir, "raw.json")) as f:
        return json.load(f)["raw"]


def aggregate(runs_dir: str, frozen: dict) -> dict:
    size_to_single = {16: "RUN-DTREE-003", 20: "RUN-DTREE-004", 24: "RUN-DTREE-005"}
    size_to_depth2 = {16: "RUN-DTREE-006", 20: "RUN-DTREE-007", 24: "RUN-DTREE-008"}

    single = {bits: load_run_raw(os.path.join(runs_dir, rid)) for bits, rid in size_to_single.items()}
    depth2 = {bits: load_run_raw(os.path.join(runs_dir, rid)) for bits, rid in size_to_depth2.items()}
    medbase = load_run_raw(os.path.join(runs_dir, "RUN-DTREE-009"))
    rho = load_run_raw(os.path.join(runs_dir, "RUN-DTREE-010"))
    probsamp = load_run_raw(os.path.join(runs_dir, "RUN-DTREE-011"))
    slope_result = load_run_raw(os.path.join(runs_dir, "RUN-DTREE-002"))

    per_size = {}
    for bits in (16, 20, 24):
        sl = single[bits]
        d2 = depth2[bits]
        c1 = sl["c1_single_level"]
        configs = d2["per_config_summary"]

        defined = {k: v for k, v in configs.items() if v["c2"] is not None}
        optimal_key = min(defined, key=lambda k: defined[k]["c2"]) if defined else None
        optimal = defined[optimal_key] if optimal_key else None

        vp = costs.validity_prefix_check(configs)

        bootstrap_by_config = {}
        winners = []
        for key, cfg_summary in configs.items():
            cfg_raw = d2["configs"].get(key)
            if cfg_raw is None:
                continue
            boot = costs.bootstrap_c2_over_c1(sl["per_target"], cfg_raw, n_boot=2000,
                                               seed=deterministic_seed("bootstrap", bits, key))
            bootstrap_by_config[key] = boot
            if (c1 is not None and cfg_summary["c2"] is not None
                    and cfg_summary["c2"] < 0.8 * c1
                    and boot.get("applicable") and boot.get("ci_entirely_below_1")):
                winners.append(key)

        b_med_at_optimum = optimal["b_med_size"] if optimal else None
        # RUN-DTREE-009's raw.json is {"by_size": {"<bits>": {..., "extrapolation_to_full_grid": {...}}}}
        # (see costs.run_medbase_logs / driver.cmd_medbase_logs) -- index into it per size, not at the top level.
        preproc = medbase["by_size"][str(bits)]["extrapolation_to_full_grid"]
        fully_charged = {}
        K = sl["standard_B"]
        for key, cfg_summary in configs.items():
            mult = cfg_summary["b_med_multiplier"]
            pre = preproc.get(mult) or preproc.get(str(mult))
            if cfg_summary["c2"] is None or pre is None:
                fully_charged[key] = {"total": None, "reason": "c2 or preprocessing undefined for this config"}
                continue
            fully_charged[key] = {
                "preprocessing_medbase_logtable_seconds": pre["extrapolated_total_seconds"],
                "k_descents": K,
                "k_times_c2_seconds": K * cfg_summary["c2"],
                "verification_cost": "not separately measured (certificate re-check cost negligible "
                                      "relative to Groebner solve cost and not separately instrumented)",
                "total_seconds": pre["extrapolated_total_seconds"] + K * cfg_summary["c2"],
            }

        per_size[bits] = {
            "c1_single_level": c1,
            "standard_B": sl["standard_B"],
            "optimal_config": optimal_key, "optimal_c2": optimal["c2"] if optimal else None,
            "optimal_b_med": b_med_at_optimum,
            "optimal_b_med_gt_standard_B": (b_med_at_optimum > sl["standard_B"]) if b_med_at_optimum else None,
            "validity_prefix": vp,
            "bootstrap_by_config": bootstrap_by_config,
            "winning_configs_c2_below_0_8_c1_and_ci_below_1": winners,
            "fully_charged_totals_by_config": fully_charged,
            "rho_baseline_group_operations": rho["by_size"][str(bits)]["group_operations_summary"],
        }

    largest_size = 24
    generic_heuristic_labels_by_size = {
        bits: {k: v["label"] for k, v in probsamp["by_size"][str(bits)]["generic_heuristic_control"].items()}
        for bits in (16, 20, 24)
    }

    return {
        "per_size": per_size,
        "largest_size_bits": largest_size,
        "c2_claim_decided_positive_at_largest_size": bool(per_size[largest_size]["winning_configs_c2_below_0_8_c1_and_ci_below_1"]),
        "c1_slope_fit": slope_result["confirmatory_slope_fit"],
        "c1_design_infeasible": slope_result["design_infeasible"],
        "generic_heuristic_labels_by_size": generic_heuristic_labels_by_size,
    }
