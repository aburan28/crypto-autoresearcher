#!/usr/bin/env python3
"""P836 schedule-constrained public support rule-list audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P835_SCRIPT = TASK_DIR / "low_term_total2_p835_support_schedule_generator_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p836_schedule_constrained_rule_list_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p836_schedule_constrained_rule_list_audit.md"
SCHEMA = "ecdlp.low_term_total2_p836_schedule_constrained_rule_list_audit.v1"


def load_p835() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p835_for_p836", P835_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P835 helpers from {P835_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def csv_ints(raw: str) -> list[int]:
    return [int(part.strip()) for part in str(raw).split(",") if part.strip()]


def csv_floats(raw: str) -> list[float]:
    return [float(part.strip()) for part in str(raw).split(",") if part.strip()]


def csv_depths(raw: str) -> list[int]:
    return sorted({int(part.strip()) for part in str(raw).split(",") if part.strip()})


def depth_minima(raw: str, default: int) -> dict[int, int]:
    out: dict[int, int] = {}
    for part in str(raw).split(","):
        part = part.strip()
        if not part:
            continue
        depth, value = part.split(":", 1)
        out[int(depth)] = int(value)
    out[-1] = int(default)
    return out


def row_uid(row: dict[str, Any]) -> str:
    return f"{row['context_id']}::{row['row_key']}"


def schedule_key(namespace: str, stratify_by: str, slice_label: str, group_key: str) -> str:
    return f"{namespace}::{stratify_by}::{slice_label}::{group_key}"


def support_clause_only(p834: Any, clause: tuple[str, ...]) -> bool:
    return p834.clause_kind(clause) == "support_only"


class PairSetCache:
    def __init__(self, p835: Any) -> None:
        self.p835 = p835
        self._cache: dict[tuple[int, tuple[str, ...]], set[tuple[int, int]]] = {}
        self._tag_cache: dict[int, dict[str, set[tuple[int, int]]]] = {}

    def tag_index(self, factor_base_size: int) -> dict[str, set[tuple[int, int]]]:
        fb_size = int(factor_base_size)
        if fb_size not in self._tag_cache:
            by_tag: dict[str, set[tuple[int, int]]] = defaultdict(set)
            for left in range(fb_size):
                for right in range(left + 1, fb_size):
                    pair = (left, right)
                    for tag in self.p835.support_tags_for_pair(left, right):
                        by_tag[tag].add(pair)
            self._tag_cache[fb_size] = by_tag
        return self._tag_cache[fb_size]

    def pairs(self, factor_base_size: int, clause: tuple[str, ...]) -> set[tuple[int, int]]:
        key = (int(factor_base_size), tuple(clause))
        if key not in self._cache:
            index = self.tag_index(int(factor_base_size))
            tag_sets = [index.get(tag, set()) for tag in clause]
            if not tag_sets:
                pairs: set[tuple[int, int]] = set()
            elif any(not values for values in tag_sets):
                pairs = set()
            else:
                tag_sets.sort(key=len)
                pairs = set(tag_sets[0])
                for values in tag_sets[1:]:
                    pairs.intersection_update(values)
            self._cache[key] = pairs
        return self._cache[key]


def group_factor_base_sizes(p835: Any, rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        str(group_key): p835.factor_base_size_for_group(str(group_key), rows)
        for group_key in sorted({str(row["group_key"]) for row in rows})
    }


def total_pair_count(group_fbs: dict[str, int]) -> int:
    return sum(int(fb) * (int(fb) - 1) // 2 for fb in group_fbs.values())


def union_schedule_from_clauses(
    p835: Any,
    cache: PairSetCache,
    group_fbs: dict[str, int],
    clauses: list[tuple[str, ...]],
) -> dict[str, Any]:
    all_pair_count = total_pair_count(group_fbs)
    by_group = {}
    union_pair_count = 0
    for group_key, fb_size in group_fbs.items():
        group_pairs: set[tuple[int, int]] = set()
        for clause in clauses:
            group_pairs.update(cache.pairs(int(fb_size), clause))
        all_group_pairs = int(fb_size) * (int(fb_size) - 1) // 2
        by_group[group_key] = {
            "all_pair_count": all_group_pairs,
            "factor_base_size": int(fb_size),
            "union_pair_count": len(group_pairs),
            "union_schedule_fraction": ratio(len(group_pairs), all_group_pairs),
            "union_schedule_speedup": ratio(all_group_pairs, len(group_pairs)),
        }
        union_pair_count += len(group_pairs)
    return {
        "all_pair_count": all_pair_count,
        "group_schedules": by_group,
        "support_clause_count": len(clauses),
        "union_pair_count": union_pair_count,
        "union_schedule_fraction": ratio(union_pair_count, all_pair_count),
        "union_schedule_speedup": ratio(all_pair_count, union_pair_count),
    }


def greedy_schedule_rule_list(
    p833: Any,
    p834: Any,
    p835: Any,
    p830: Any,
    cache: PairSetCache,
    train_rows: list[dict[str, Any]],
    group_fbs: dict[str, int],
    max_k: int,
    depths: list[int],
    min_rows_per_namespace_by_depth: dict[int, int],
    min_total_rows_by_depth: dict[int, int],
    prior_online: int,
    require_recovered_each_namespace: bool,
    max_candidates: int,
    score_mode: str,
    max_schedule_fraction: float,
) -> tuple[list[dict[str, Any]], int]:
    candidates = p833.recurrent_clause_stats(
        p830.row_totals,
        train_rows,
        depths,
        min_rows_per_namespace_by_depth,
        min_total_rows_by_depth,
        prior_online,
        require_recovered_each_namespace,
        max_candidates,
    )
    support_candidates = [
        candidate
        for candidate in candidates
        if support_clause_only(p834, tuple(candidate["clause"]))
    ]
    uid_to_row = {row_uid(row): row for row in train_rows}
    selected_uids: set[str] = set()
    chosen = []
    union_by_group: dict[str, set[tuple[int, int]]] = {group_key: set() for group_key in group_fbs}
    all_pair_count = total_pair_count(group_fbs)
    for _index in range(int(max_k)):
        best = None
        best_add_uids: set[str] = set()
        best_new_union_by_group: dict[str, set[tuple[int, int]]] | None = None
        for candidate in support_candidates:
            clause = tuple(candidate["clause"])
            candidate_uids = set(candidate["_uids"])
            add_uids = candidate_uids - selected_uids
            if not add_uids:
                continue
            added_rows = [uid_to_row[uid] for uid in add_uids if uid in uid_to_row]
            added_totals = p830.row_totals(added_rows)
            if int(added_totals["recovered_row_count"]) <= 0:
                continue
            new_union_by_group = {group_key: set(values) for group_key, values in union_by_group.items()}
            marginal_pair_count = 0
            for group_key, fb_size in group_fbs.items():
                pairs = cache.pairs(int(fb_size), clause)
                before = len(new_union_by_group[group_key])
                new_union_by_group[group_key].update(pairs)
                marginal_pair_count += len(new_union_by_group[group_key]) - before
            if marginal_pair_count <= 0:
                continue
            new_union_count = sum(len(values) for values in new_union_by_group.values())
            schedule_fraction = float(new_union_count) / float(all_pair_count)
            if schedule_fraction > float(max_schedule_fraction):
                continue
            marginal_rho = int(added_totals["recovered_rho_baseline"])
            marginal_rows = int(added_totals["recovered_row_count"])
            pair_density = float(marginal_rho) / float(marginal_pair_count)
            online_density = float(ratio(marginal_rho, added_totals["online_group_additions"]) or 0.0)
            if score_mode == "support_pair_density":
                score = (
                    pair_density,
                    online_density,
                    marginal_rows,
                    marginal_rho,
                    -marginal_pair_count,
                    -int(candidate["depth"]),
                    candidate["name"],
                )
            elif score_mode == "rho_first":
                score = (
                    marginal_rho,
                    pair_density,
                    online_density,
                    marginal_rows,
                    -marginal_pair_count,
                    -int(candidate["depth"]),
                    candidate["name"],
                )
            else:
                score = (
                    marginal_rows,
                    marginal_rho,
                    pair_density,
                    online_density,
                    -marginal_pair_count,
                    -int(candidate["depth"]),
                    candidate["name"],
                )
            if best is None or score > best["score"]:
                best = {
                    "candidate": candidate,
                    "score": score,
                    "selected_increment": {
                        **added_totals,
                        "marginal_pair_count": int(marginal_pair_count),
                        "marginal_recovered_rho_per_pair": round(pair_density, 8),
                        "marginal_recovered_rho_per_online": ratio(
                            added_totals["recovered_rho_baseline"],
                            added_totals["online_group_additions"],
                        ),
                        "post_add_schedule_fraction": round(schedule_fraction, 8),
                        "post_add_schedule_speedup": ratio(all_pair_count, new_union_count),
                    },
                }
                best_add_uids = add_uids
                best_new_union_by_group = new_union_by_group
        if best is None:
            break
        selected_uids.update(best_add_uids)
        union_by_group = best_new_union_by_group or union_by_group
        candidate = best["candidate"]
        chosen.append(
            {
                "clause": candidate["clause"],
                "depth": candidate["depth"],
                "name": candidate["name"],
                "score_components": candidate["score_components"],
                "selected_increment": best["selected_increment"],
            }
        )
    return chosen, len(support_candidates)


def evaluate_schedule_constrained(
    p833: Any,
    p834: Any,
    p835: Any,
    p830: Any,
    rows: list[dict[str, Any]],
    fixed_cost: int,
    field_weight: int,
    top_ks: list[int],
    depths: list[int],
    min_rows_per_namespace_by_depth: dict[int, int],
    min_total_rows_by_depth: dict[int, int],
    prior_online: int,
    require_recovered_each_namespace: bool,
    max_candidates: int,
    score_mode: str,
    max_schedule_fraction: float,
    stratify_by: str | None,
) -> list[dict[str, Any]]:
    cache = PairSetCache(p835)
    namespaces = sorted({row["base_namespace"] for row in rows})
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    selected_by_k: dict[int, dict[str, dict[str, Any]]] = {int(k): {} for k in top_ks}
    attributions_by_k: dict[int, dict[str, dict[str, Any]]] = {int(k): {} for k in top_ks}
    schedules_by_k: dict[int, dict[str, dict[str, Any]]] = {int(k): {} for k in top_ks}
    diagnostics: dict[int, list[dict[str, Any]]] = {int(k): [] for k in top_ks}
    max_k = max(top_ks)
    for namespace in namespaces:
        for audit_slice in p833.make_slices(pilot_rows, namespace, stratify_by):
            if not audit_slice["test"]:
                continue
            group_fbs = group_factor_base_sizes(p835, audit_slice["test"])
            ranked, candidate_count = greedy_schedule_rule_list(
                p833,
                p834,
                p835,
                p830,
                cache,
                audit_slice["train"],
                group_fbs,
                max_k,
                depths,
                min_rows_per_namespace_by_depth,
                min_total_rows_by_depth,
                prior_online,
                require_recovered_each_namespace,
                max_candidates,
                score_mode,
                max_schedule_fraction,
            )
            for k in top_ks:
                clauses = [tuple(item["clause"]) for item in ranked[: int(k)]]
                selected = p833.select_by_clauses(audit_slice["test"], clauses)
                selected_schedule = union_schedule_from_clauses(p835, cache, group_fbs, clauses)
                for group_key, fb_size in group_fbs.items():
                    key = schedule_key(
                        str(namespace),
                        str(stratify_by or "none"),
                        str(audit_slice["label"]),
                        str(group_key),
                    )
                    schedules_by_k[int(k)][key] = {
                        **p835.support_schedule_stats(int(fb_size), clauses),
                        "heldout_namespace": str(namespace),
                        "slice_label": str(audit_slice["label"]),
                        "stratify_by": str(stratify_by or "none"),
                        "group_key": str(group_key),
                    }
                for row in selected:
                    uid = row_uid(row)
                    selected_by_k[int(k)][uid] = row
                    matching = [clause for clause in clauses if p833.row_matches_clause(row, clause)]
                    if uid not in attributions_by_k[int(k)]:
                        first = matching[0]
                        key = schedule_key(
                            str(namespace),
                            str(stratify_by or "none"),
                            str(audit_slice["label"]),
                            str(row["group_key"]),
                        )
                        attributions_by_k[int(k)][uid] = {
                            "clause": list(first),
                            "clause_kind": p834.clause_kind(first),
                            "heldout_namespace": str(namespace),
                            "matching_clause_count": len(matching),
                            "matching_clause_kinds": sorted({p834.clause_kind(clause) for clause in matching}),
                            "rule_name": p834.clause_name(first),
                            "slice_label": str(audit_slice["label"]),
                            "stratify_by": str(stratify_by or "none"),
                            "support_only_matching_clauses": [list(clause) for clause in matching],
                            "support_schedule_key": key,
                            "row": row,
                        }
                diagnostics[int(k)].append(
                    {
                        "candidate_count": int(candidate_count),
                        "chosen_rule_count": len(clauses),
                        "heldout_namespace": str(namespace),
                        "max_schedule_fraction": float(max_schedule_fraction),
                        "selected_rules": [p834.clause_name(clause) for clause in clauses],
                        "selected_row_count": len(selected),
                        "slice_label": str(audit_slice["label"]),
                        "stratify_by": str(stratify_by or "none"),
                        "support_schedule": selected_schedule,
                        "test_pilot_rows": len(audit_slice["test"]),
                        "test_recovered_rows": sum(1 for row in audit_slice["test"] if row["recovered"]),
                        "test_selected_recovered_rows": sum(1 for row in selected if row["recovered"]),
                        "train_namespaces": sorted({row["base_namespace"] for row in audit_slice["train"]}),
                        "train_pilot_rows": len(audit_slice["train"]),
                        "train_recovered_rows": sum(1 for row in audit_slice["train"] if row["recovered"]),
                    }
                )
    results = []
    for k in top_ks:
        selected = list(selected_by_k[int(k)].values())
        attributions = list(attributions_by_k[int(k)].values())
        schedules = schedules_by_k[int(k)]
        schedule_model = p835.exact_schedule_adjusted_model(
            p830,
            base_rows,
            selected,
            attributions,
            schedules,
            fixed_cost,
            field_weight,
        )
        selected_totals = p830.row_totals(selected)
        policy_kind = "loo_public_support_schedule_constrained_rule_list"
        if stratify_by:
            policy_kind = f"loo_public_{stratify_by}_stratified_support_schedule_constrained_rule_list"
        results.append(
            {
                "diagnostics": diagnostics[int(k)],
                "policy": {
                    "depths": depths,
                    "kind": policy_kind,
                    "max_candidates": int(max_candidates),
                    "max_schedule_fraction": float(max_schedule_fraction),
                    "min_rows_per_namespace_by_depth": {
                        str(key): value for key, value in min_rows_per_namespace_by_depth.items() if key != -1
                    },
                    "min_total_rows_by_depth": {
                        str(key): value for key, value in min_total_rows_by_depth.items() if key != -1
                    },
                    "prior_online": int(prior_online),
                    "require_recovered_each_namespace": bool(require_recovered_each_namespace),
                    "score_mode": score_mode,
                    "stratify_by": stratify_by or None,
                    "top_k_per_slice": int(k),
                },
                "schedule_adjusted_charge_model": schedule_model,
                "selected_pilot_only": {
                    **selected_totals,
                    "recovered_rho_per_online": ratio(
                        selected_totals["recovered_rho_baseline"],
                        selected_totals["online_group_additions"],
                    ),
                    "recovered_row_rate": ratio(
                        selected_totals["recovered_row_count"],
                        selected_totals["row_count"],
                    ),
                },
            }
        )
    results.sort(
        key=lambda item: (
            item["schedule_adjusted_charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
            item["policy"]["max_schedule_fraction"],
            item["policy"]["score_mode"],
            item["policy"]["top_k_per_slice"],
        )
    )
    return results


def best_ratio(item: dict[str, Any] | None, key: str = "post_hit_total_cost_over_recovered_rho") -> float:
    if item is None:
        return 10**9
    value = item.get(key)
    return float(value) if value is not None else 10**9


def determine_claim(
    full_model: dict[str, Any],
    p833_model: dict[str, Any],
    p835_model: dict[str, Any],
    best: dict[str, Any] | None,
) -> str:
    if best is None:
        return "NEGATIVE_RESULT_P836_NO_SCHEDULE_CONSTRAINED_RULES"
    best_model = best["schedule_adjusted_charge_model"]
    best_value = float(best_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    p826_value = float(full_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    p833_value = float(p833_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    p835_value = float(p835_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    if best_value < 1.0:
        return "P836_SCHEDULE_CONSTRAINED_RULE_LIST_BELOW_RHO_MODEL_SIGNAL"
    if best_value < p826_value:
        return "P836_SCHEDULE_CONSTRAINED_RULE_LIST_BEATS_P826_MODEL"
    if best_value < p835_value:
        return "P836_SCHEDULE_CONSTRAINED_RULE_LIST_IMPROVES_P835_BUT_NOT_P826"
    if best_value < p833_value:
        return "P836_SCHEDULE_CONSTRAINED_RULE_LIST_IMPROVES_P833_BUT_NOT_P835"
    return "NEGATIVE_RESULT_P836_SCHEDULE_CONSTRAINT_LOSES_TOO_MUCH_RECALL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p835 = load_p835()
    p834 = p835.load_p834()
    p833 = p834.load_p833()
    p832 = p833.load_p832()
    p831 = p832.load_p831()
    p830 = p831.load_p830()
    rows, build_meta = p830.build_rows(args)
    fixed = p830.find_p826_fixed_cost(args.p826_probe, int(args.field_weight))
    fixed_cost = int(fixed["fixed_cost"])
    field_weight = int(args.field_weight)
    p833_reconstructed = p834.reconstruct_p833_best(p833, p830, rows, fixed_cost, field_weight, args)
    p833_best = p833_reconstructed["best_public_rule_list"]
    if p833_best is None:
        raise RuntimeError("P836 could not reconstruct P833 best public rule-list result")

    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    p833_selected, p833_attributions, p833_schedules = p835.selected_rows_with_attribution(p834, p833_best, pilot_rows)
    full_model = p830.charged_model(pilot_rows, base_rows, fixed_cost, field_weight)
    p833_measured = p830.charged_model(p833_selected, base_rows, fixed_cost, field_weight)
    p835_schedule_model = p835.exact_schedule_adjusted_model(
        p830,
        base_rows,
        p833_selected,
        p833_attributions,
        p833_schedules,
        fixed_cost,
        field_weight,
    )

    top_ks = csv_ints(args.top_ks)
    max_schedule_fractions = csv_floats(args.max_schedule_fractions)
    score_modes = [mode.strip() for mode in str(args.schedule_score_modes).split(",") if mode.strip()]
    global_depths = csv_depths(args.rule_depths)
    group_depths = csv_depths(args.group_rule_depths)
    min_ns = depth_minima(args.min_rule_rows_per_namespace_by_depth, int(args.min_rule_rows_per_namespace))
    min_total = depth_minima(args.min_rule_total_rows_by_depth, int(args.min_rule_total_rows))
    group_min_ns = depth_minima(args.group_min_rule_rows_per_namespace_by_depth, int(args.group_min_rule_rows_per_namespace))
    group_min_total = depth_minima(args.group_min_rule_total_rows_by_depth, int(args.group_min_rule_total_rows))

    policy_results = []
    for score_mode in score_modes:
        for max_fraction in max_schedule_fractions:
            policy_results.extend(
                evaluate_schedule_constrained(
                    p833,
                    p834,
                    p835,
                    p830,
                    rows,
                    fixed_cost,
                    field_weight,
                    top_ks,
                    global_depths,
                    min_ns,
                    min_total,
                    int(args.support_prior_online),
                    bool(args.require_recovered_each_namespace),
                    int(args.max_rule_candidates),
                    score_mode,
                    float(max_fraction),
                    None,
                )
            )
            policy_results.extend(
                evaluate_schedule_constrained(
                    p833,
                    p834,
                    p835,
                    p830,
                    rows,
                    fixed_cost,
                    field_weight,
                    top_ks,
                    group_depths,
                    group_min_ns,
                    group_min_total,
                    int(args.support_prior_online),
                    bool(args.require_recovered_each_namespace),
                    int(args.max_group_rule_candidates),
                    score_mode,
                    float(max_fraction),
                    "group_key",
                )
            )
    policy_results.sort(
        key=lambda item: (
            item["schedule_adjusted_charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
            item["policy"]["kind"],
            item["policy"]["max_schedule_fraction"],
            item["policy"]["top_k_per_slice"],
        )
    )
    best = policy_results[0] if policy_results else None
    claim_status = determine_claim(full_model, p833_measured, p835_schedule_model, best)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "p830_script": str(p831.P830_SCRIPT),
            "p831_script": str(p832.P831_SCRIPT),
            "p832_script": str(p833.P832_SCRIPT),
            "p833_script": str(p834.P833_SCRIPT),
            "p834_script": str(p835.P834_SCRIPT),
            "p835_script": str(P835_SCRIPT),
            "script": str(Path(__file__)),
        },
        "build_meta": build_meta,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MODEL-BOUND: P836 selects public support-only leaves under exact support-pair schedule-width caps and scales eligible row online additions by schedule fraction.",
            "NOT A DIRECT CONSTRUCTOR: P836 does not yet alter P799/P800 row construction or prove generated_online_group_additions improve by the modeled amount.",
            "PUBLIC RULES: held-out rows are selected only by support tag predicates trained on other namespaces.",
            "POLLARD-RHO BOUNDARY: below-P826 or below-rho ratios are generator-model signals until direct construction, sparse linear algebra, and target descent are measured.",
            "NO DEPLOYED-CURVE CLAIM: this is not a faster-than-rho deployed ECDLP algorithm.",
        ],
        "method": "p836_schedule_constrained_rule_list_audit",
        "parameters": {
            "fixed_cost": fixed,
            "max_schedule_fractions": max_schedule_fractions,
            "schedule_score_modes": score_modes,
            "top_ks": top_ks,
        },
        "red_team_handoff": {
            "assumptions": [
                "Marginal support-pair mass is a useful proxy for the online cost of a future direct support-schedule generator.",
                "A rule selected under a schedule-width cap can be generated at online cost proportional to the selected support-pair fraction.",
                "Recovered-rho denominator and scoring-field work remain the same as the selected held-out rows.",
            ],
            "failure_modes": [
                "The schedule-width cap may discard too much recovered-rho mass to beat P835/P826.",
                "Training recovered-rho per pair may not transfer to held-out namespaces.",
                "Actual row construction may not speed up in proportion to support-pair enumeration width.",
            ],
            "next_concrete_action_if_promising": (
                "Wire the best P836 support schedule into P799/P800 and replace modeled online scaling with measured generated_online_group_additions."
            ),
        },
        "row_population": {
            "category_totals": p830.totals_by_category(rows),
            "full_p826_reconstructed_charge_model": full_model,
            "p833_measured_best": p833_measured,
            "p835_schedule_adjusted_model": p835_schedule_model,
        },
        "schedule_constrained_rule_list": {
            "best_schedule_constrained": best,
            "p833_public_rule_list_best": p833_best,
            "policy_results": policy_results,
        },
        "schema": SCHEMA,
    }


def compact_result(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    return {
        "diagnostics": item["diagnostics"],
        "policy": item["policy"],
        "schedule_adjusted_charge_model": item["schedule_adjusted_charge_model"],
        "selected_pilot_only": item["selected_pilot_only"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload["schedule_constrained_rule_list"]["policy_results"]
    compact_results = sorted(
        (compact_result(item) for item in results),
        key=lambda item: (
            item["schedule_adjusted_charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
            item["policy"]["kind"],
            item["policy"]["max_schedule_fraction"],
            item["policy"]["top_k_per_slice"],
        ),
    )[: int(payload["parameters"].get("summary_policy_limit", 24) or 24)]
    return {
        **payload,
        "schedule_constrained_rule_list": {
            "best_schedule_constrained": compact_result(
                payload["schedule_constrained_rule_list"]["best_schedule_constrained"]
            ),
            "p833_public_rule_list_best": payload["schedule_constrained_rule_list"]["p833_public_rule_list_best"],
            "top_policy_results": compact_results,
        },
        "schema": f"{SCHEMA}.summary",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p826-probe", type=Path, default=DEFAULT_P826_PROBE)
    parser.add_argument("--p777-summary", type=Path, default=STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json")
    parser.add_argument("--p786-summary", type=Path, default=STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json")
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--train-constructor-namespaces", default="")
    parser.add_argument("--test-constructor-namespaces", default="posthit-p826-fresh-v32,posthit-p826-fresh-v33,posthit-p826-fresh-v34")
    parser.add_argument("--loo-constructor-namespaces", default="")
    parser.add_argument("--skip-loo", action="store_true", default=True)
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--prefix-seed-counts", default="8")
    parser.add_argument("--prefix-trial-budget", type=int, default=256)
    parser.add_argument("--average-continuation-budgets", default="64")
    parser.add_argument("--pilot-budgets", default="16")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--top-span-bins", type=int, default=2)
    parser.add_argument("--top-endpoint-bins", type=int, default=4)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--top-ks", default="1,2,4,8,16,32")
    parser.add_argument("--min-conjunction-rows", type=int, default=8)
    parser.add_argument("--min-stable-rows-per-namespace", type=int, default=4)
    parser.add_argument("--min-stable-total-rows", type=int, default=8)
    parser.add_argument("--min-rule-rows-per-namespace", type=int, default=4)
    parser.add_argument("--min-rule-rows-per-namespace-by-depth", default="1:12,2:4,3:2")
    parser.add_argument("--min-rule-total-rows", type=int, default=8)
    parser.add_argument("--min-rule-total-rows-by-depth", default="1:24,2:8,3:4")
    parser.add_argument("--group-min-rule-rows-per-namespace", type=int, default=1)
    parser.add_argument("--group-min-rule-rows-per-namespace-by-depth", default="1:4,2:1,3:1")
    parser.add_argument("--group-min-rule-total-rows", type=int, default=2)
    parser.add_argument("--group-min-rule-total-rows-by-depth", default="1:8,2:2,3:2")
    parser.add_argument("--rule-depths", default="1,2,3")
    parser.add_argument("--group-rule-depths", default="1,2,3")
    parser.add_argument("--score-modes", default="density_first,recall_first")
    parser.add_argument("--schedule-score-modes", default="support_pair_density,rho_first,recall_first")
    parser.add_argument("--max-schedule-fractions", default="0.25,0.33,0.5,0.56,0.67")
    parser.add_argument("--support-prior-online", type=int, default=64)
    parser.add_argument("--require-recovered-each-namespace", action="store_true")
    parser.add_argument("--max-rule-candidates", type=int, default=4000)
    parser.add_argument("--max-group-rule-candidates", type=int, default=2500)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    best = summary["schedule_constrained_rule_list"]["best_schedule_constrained"]
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_schedule_constrained": best,
                "claim_status": summary["claim_status"],
                "full_p826_reconstructed_charge_model": summary["row_population"]["full_p826_reconstructed_charge_model"],
                "p833_measured_best": summary["row_population"]["p833_measured_best"],
                "p835_schedule_adjusted_model": summary["row_population"]["p835_schedule_adjusted_model"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
