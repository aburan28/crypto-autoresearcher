#!/usr/bin/env python3
"""
Builds the machine-readable per-run summary of Q1/Q2/Q3 (+ secondary
metrics) from a run's raw-result.json, reported as measurements with bands
-- no interpretation, no verdict. Writes summary.json alongside
raw-result.json in the same run directory.
"""
import json
import statistics
import sys


def summarize(raw):
    members = [r for r in raw["member_records"] if r["role"] == "class_member"]
    base = [r for r in raw["member_records"] if r["role"] == "base_curve"]
    nulls = raw["null_records"]

    good_members = [r for r in members if r.get("contributes_cost_datum")]
    generic_members = [r for r in good_members if not r.get("special_j")]
    special_j_members = [r for r in good_members if r.get("special_j")]

    def band(values):
        if not values:
            return None
        d = {"n": len(values), "min": min(values), "max": max(values), "mean": statistics.mean(values)}
        if len(values) >= 2:
            d["stdev"] = statistics.stdev(values)
        return d

    q1_all = [r["group_ops"] for r in generic_members]
    q2_all = [r["q2_field_muls_per_group_op"] for r in generic_members if r.get("q2_field_muls_per_group_op") is not None]
    q3_all = [r["charged_end_to_end_cost_field_muls"] for r in generic_members if r.get("charged_end_to_end_cost_field_muls") is not None]

    base_seed_solved = [r for r in base if r.get("contributes_cost_datum")]
    base_q1 = [r["group_ops"] for r in base_seed_solved]

    summary = {
        "experiment_id": "EXP-ISOU-2ac81f",
        "bit_length": raw["bit_length"],
        "instance_label": raw["instance_label"],
        "terminal_status": raw["terminal_status"],
        "terminal_status_reasons": raw["terminal_status_reasons"],
        "completeness": {
            "class_number_h": raw["class_number_h"],
            "walk_vertex_count": raw["walk_vertex_count"],
            "complete": raw["completeness_ok"],
        },
        "null_object_separation": raw["null_object_separation"],
        "seed_dispersion_band_base_curve": raw["seed_dispersion_band"],
        "bsgs_cross_check": raw["bsgs_cross_check"],
        "special_j_members_excluded_from_generic_band": len(special_j_members),
        "counts": {
            "class_members_total": len(members),
            "class_members_solved": sum(1 for r in members if r["status"] == "solved"),
            "class_members_censored": sum(1 for r in members if r["status"] == "censored"),
            "class_members_certificate_failed": sum(
                1 for r in members if r["status"] == "solved" and not r.get("contributes_cost_datum")
            ),
            "null_objects_total": len(nulls),
            "null_objects_solved": sum(1 for r in nulls if r["status"] == "solved"),
        },
        "Q1_group_operations_to_solve": {
            "definition": "count of EC group operations (adds+doublings), common (affine) coordinate system",
            "base_curve_band": band(base_q1),
            "generic_class_members_band": band(q1_all),
            "special_j_members_band": band([r["group_ops"] for r in special_j_members]),
            "null_objects_band": band([r["group_ops"] for r in nulls if r.get("contributes_cost_datum")]),
        },
        "Q2_field_muls_per_group_op": {
            "definition": "instrumented (mul+sqr, 1:1 weighted) field cost per group op, member's own cheapest reachable model",
            "base_curve_value": raw.get("base_curve_q2_field_muls_per_group_op"),
            "generic_class_members_band": band(q2_all),
            "best_to_worst_ratio": (max(q2_all) / min(q2_all)) if q2_all and min(q2_all) > 0 else None,
            "a_minus_3_reachable_count": sum(1 for r in generic_members if r.get("a_minus_3_model_reachable")),
            "a_minus_3_not_reachable_count": sum(1 for r in generic_members if not r.get("a_minus_3_model_reachable")),
        },
        "Q3_charged_end_to_end_cost_field_muls": {
            "definition": "walk cost (measured, field muls) + solve cost (group_ops * Q2 per-op), vs base curve solve-only cost",
            "base_curve_solve_only_cost": raw.get("base_curve_charged_cost_field_muls"),
            "generic_class_members_band": band(q3_all),
            "members_cheaper_than_base_count": sum(
                1 for c in q3_all if raw.get("base_curve_charged_cost_field_muls") is not None and c < raw["base_curve_charged_cost_field_muls"]
            ),
            "members_compared": len(q3_all),
        },
        "secondary_metrics": {
            "montgomery_or_edwards_reachable_count": sum(
                1 for r in generic_members if r.get("montgomery_or_edwards_model_reachable")
            ),
            "special_j_member_ids": [r["vertex_id"] for r in special_j_members],
        },
        "tail_checks": {
            "cheapest_group_op_member_within_seed_band": None,
            "cheapest_per_op_member_has_a_minus3": None,
            "largest_walk_cost_vs_smallest_solve_saving": None,
        },
    }

    # tail check 1: cheapest group-op member vs base seed band
    if q1_all and raw["seed_dispersion_band"]:
        cheapest = min(q1_all)
        sb = raw["seed_dispersion_band"]
        lo, hi = sb["mean"] - 3 * sb["stdev"], sb["mean"] + 3 * sb["stdev"]
        summary["tail_checks"]["cheapest_group_op_member_within_seed_band"] = {
            "cheapest_value": cheapest, "band_lo": lo, "band_hi": hi,
            "within_band": lo <= cheapest <= hi,
        }
    # tail check 2: cheapest per-op member's a=-3 reachability
    if q2_all:
        cheapest_idx = q2_all.index(min(q2_all))
        cheapest_member = [r for r in generic_members if r.get("q2_field_muls_per_group_op") is not None][cheapest_idx]
        summary["tail_checks"]["cheapest_per_op_member_has_a_minus3"] = cheapest_member.get("a_minus_3_model_reachable")
    # tail check 3: largest walk cost vs smallest solve saving
    walk_costs = [r["walk_cost_field_muls_measured"] for r in generic_members if r.get("walk_cost_field_muls_measured") is not None]
    if walk_costs and q3_all and raw.get("base_curve_charged_cost_field_muls") is not None:
        largest_walk = max(walk_costs)
        base_cost = raw["base_curve_charged_cost_field_muls"]
        smallest_member_solve_only = None
        solve_only_costs = [
            r["group_ops"] * r["q2_field_muls_per_group_op"]
            for r in generic_members
            if r.get("q2_field_muls_per_group_op") is not None
        ]
        if solve_only_costs:
            smallest_member_solve_only = min(solve_only_costs)
            saving = base_cost - smallest_member_solve_only
            summary["tail_checks"]["largest_walk_cost_vs_smallest_solve_saving"] = {
                "largest_walk_cost_field_muls": largest_walk,
                "smallest_solve_only_saving_field_muls": saving,
                "walk_dominates": largest_walk > saving if saving is not None else None,
            }
    return summary


if __name__ == "__main__":
    run_dir = sys.argv[1]
    with open(f"{run_dir}/raw-result.json") as f:
        raw = json.load(f)
    summary = summarize(raw)
    with open(f"{run_dir}/summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(json.dumps(summary, indent=2, default=str))
