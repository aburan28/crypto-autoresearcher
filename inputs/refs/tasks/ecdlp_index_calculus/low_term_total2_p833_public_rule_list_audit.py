#!/usr/bin/env python3
"""P833 public recurrent rule-list audit for P829 pilot-only rows."""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P832_SCRIPT = TASK_DIR / "low_term_total2_p832_stabilized_transfer_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p833_public_rule_list_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p833_public_rule_list_audit.md"
SCHEMA = "ecdlp.low_term_total2_p833_public_rule_list_audit.v1"


def load_p832() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p832_for_p833", P832_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P832 helpers from {P832_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def csv_ints(raw: str) -> list[int]:
    return [int(part.strip()) for part in str(raw).split(",") if part.strip()]


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


def min_for_depth(minima: dict[int, int], depth: int) -> int:
    return int(minima.get(int(depth), minima.get(-1, 1)))


def row_uid(row: dict[str, Any]) -> str:
    return f"{row['context_id']}::{row['row_key']}"


def clause_name(clause: tuple[str, ...]) -> str:
    return " && ".join(clause)


def support_span_bucket(row: dict[str, Any]) -> int:
    return abs(int(row["support_right"]) - int(row["support_left"])) // 16


def clause_support_bucket(clause: tuple[str, ...], rows: list[dict[str, Any]]) -> int:
    for tag in clause:
        if tag.startswith("support_span_bucket16="):
            return int(tag.split("=", 1)[1])
    buckets = Counter(support_span_bucket(row) for row in rows)
    if not buckets:
        return -1
    return buckets.most_common(1)[0][0]


def density(totals: dict[str, Any]) -> float:
    online = int(totals.get("online_group_additions") or 0)
    if online <= 0:
        return 0.0
    return float(totals.get("recovered_rho_baseline") or 0) / float(online)


def support_bucket_priors(row_totals_fn: Any, train_rows: list[dict[str, Any]]) -> dict[int, float]:
    by_bucket: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in train_rows:
        by_bucket[support_span_bucket(row)].append(row)
    priors = {bucket: density(row_totals_fn(rows)) for bucket, rows in by_bucket.items()}
    priors[-1] = density(row_totals_fn(train_rows))
    return priors


def smoothed_density(totals: dict[str, Any], prior_density: float, prior_online: int) -> float:
    online = int(totals["online_group_additions"])
    recovered_rho = int(totals["recovered_rho_baseline"])
    return (float(recovered_rho) + float(prior_density) * int(prior_online)) / float(online + int(prior_online))


def harmonic(values: list[float]) -> float:
    positives = [value for value in values if value > 0.0]
    if not positives or len(positives) != len(values):
        return 0.0
    return float(len(positives)) / sum(1.0 / value for value in positives)


def row_matches_clause(row: dict[str, Any], clause: tuple[str, ...]) -> bool:
    tags = set(row["tags"])
    return all(tag in tags for tag in clause)


def select_by_clauses(rows: list[dict[str, Any]], clauses: list[tuple[str, ...]]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for clause in clauses:
        for row in rows:
            if row_matches_clause(row, clause):
                selected[row_uid(row)] = row
    return list(selected.values())


def recurrent_clause_stats(
    row_totals_fn: Any,
    train_rows: list[dict[str, Any]],
    depths: list[int],
    min_rows_per_namespace_by_depth: dict[int, int],
    min_total_rows_by_depth: dict[int, int],
    prior_online: int,
    require_recovered_each_namespace: bool,
    max_candidates: int,
) -> list[dict[str, Any]]:
    namespaces = sorted({row["base_namespace"] for row in train_rows})
    if len(namespaces) < 2:
        return []
    uid_to_row = {row_uid(row): row for row in train_rows}
    by_clause_ns: dict[tuple[str, ...], dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in train_rows:
        tags = sorted(set(row["tags"]))
        namespace = row["base_namespace"]
        for depth in depths:
            if len(tags) < depth:
                continue
            for clause in itertools.combinations(tags, int(depth)):
                by_clause_ns[clause][namespace].add(row_uid(row))

    priors = support_bucket_priors(row_totals_fn, train_rows)
    stats = []
    for clause, by_ns in by_clause_ns.items():
        depth = len(clause)
        min_ns = min_for_depth(min_rows_per_namespace_by_depth, depth)
        min_total = min_for_depth(min_total_rows_by_depth, depth)
        if any(len(by_ns.get(namespace, set())) < min_ns for namespace in namespaces):
            continue
        selected_uids: set[str] = set()
        for namespace in namespaces:
            selected_uids.update(by_ns[namespace])
        if len(selected_uids) < min_total:
            continue
        selected = [uid_to_row[uid] for uid in selected_uids]
        totals = row_totals_fn(selected)
        if int(totals["recovered_row_count"]) <= 0:
            continue
        bucket = clause_support_bucket(clause, selected)
        prior = priors.get(bucket, priors[-1])
        per_namespace = []
        smoothed_scores = []
        for namespace in namespaces:
            ns_rows = [uid_to_row[uid] for uid in by_ns[namespace]]
            ns_totals = row_totals_fn(ns_rows)
            if require_recovered_each_namespace and int(ns_totals["recovered_row_count"]) <= 0:
                per_namespace = []
                break
            ns_smoothed = smoothed_density(ns_totals, prior, prior_online)
            smoothed_scores.append(ns_smoothed)
            per_namespace.append(
                {
                    "namespace": namespace,
                    "raw_recovered_rho_per_online": ratio(
                        ns_totals["recovered_rho_baseline"],
                        ns_totals["online_group_additions"],
                    ),
                    "smoothed_recovered_rho_per_online": round(ns_smoothed, 8),
                    **ns_totals,
                }
            )
        if not per_namespace:
            continue
        stats.append(
            {
                "_uids": selected_uids,
                "clause": list(clause),
                "depth": int(depth),
                "name": clause_name(clause),
                "per_namespace": per_namespace,
                "score_components": {
                    "harmonic_smoothed_recovered_rho_per_online": round(harmonic(smoothed_scores), 8),
                    "min_smoothed_recovered_rho_per_online": round(min(smoothed_scores), 8),
                    "raw_recovered_rho_per_online": ratio(
                        totals["recovered_rho_baseline"],
                        totals["online_group_additions"],
                    ),
                    "support_bucket_prior_density": round(prior, 8),
                    "support_span_bucket16": int(bucket),
                },
                **totals,
            }
        )
    stats.sort(
        key=lambda item: (
            float(item["score_components"]["min_smoothed_recovered_rho_per_online"]),
            float(item["score_components"]["harmonic_smoothed_recovered_rho_per_online"]),
            float(item["score_components"]["raw_recovered_rho_per_online"] or 0.0),
            int(item["recovered_row_count"]),
            int(item["recovered_rho_baseline"]),
            -int(item["online_group_additions"]),
            -int(item["depth"]),
            item["name"],
        ),
        reverse=True,
    )
    return stats[: int(max_candidates)]


def greedy_rule_list(
    row_totals_fn: Any,
    train_rows: list[dict[str, Any]],
    max_k: int,
    depths: list[int],
    min_rows_per_namespace_by_depth: dict[int, int],
    min_total_rows_by_depth: dict[int, int],
    prior_online: int,
    require_recovered_each_namespace: bool,
    max_candidates: int,
    score_mode: str,
) -> tuple[list[dict[str, Any]], int]:
    candidates = recurrent_clause_stats(
        row_totals_fn,
        train_rows,
        depths,
        min_rows_per_namespace_by_depth,
        min_total_rows_by_depth,
        prior_online,
        require_recovered_each_namespace,
        max_candidates,
    )
    uid_to_row = {row_uid(row): row for row in train_rows}
    selected_uids: set[str] = set()
    chosen = []
    for _index in range(int(max_k)):
        best = None
        best_add_uids: set[str] = set()
        for candidate in candidates:
            candidate_uids = set(candidate["_uids"])
            add_uids = candidate_uids - selected_uids
            if not add_uids:
                continue
            added_rows = [uid_to_row[uid] for uid in add_uids]
            added_totals = row_totals_fn(added_rows)
            if int(added_totals["recovered_row_count"]) <= 0:
                continue
            marginal_density = float(
                ratio(added_totals["recovered_rho_baseline"], added_totals["online_group_additions"]) or 0.0
            )
            if score_mode == "recall_first":
                score = (
                    int(added_totals["recovered_row_count"]),
                    int(added_totals["recovered_rho_baseline"]),
                    marginal_density,
                    float(candidate["score_components"]["min_smoothed_recovered_rho_per_online"]),
                    -int(added_totals["online_group_additions"]),
                    -int(candidate["depth"]),
                    candidate["name"],
                )
            else:
                score = (
                    marginal_density,
                    float(candidate["score_components"]["min_smoothed_recovered_rho_per_online"]),
                    float(candidate["score_components"]["harmonic_smoothed_recovered_rho_per_online"]),
                    int(added_totals["recovered_row_count"]),
                    int(added_totals["recovered_rho_baseline"]),
                    -int(added_totals["online_group_additions"]),
                    -int(candidate["depth"]),
                    candidate["name"],
                )
            if best is None or score > best["score"]:
                best = {
                    "candidate": candidate,
                    "score": score,
                    "selected_increment": {
                        **added_totals,
                        "recovered_rho_per_online": ratio(
                            added_totals["recovered_rho_baseline"],
                            added_totals["online_group_additions"],
                        ),
                        "recovered_row_rate": ratio(
                            added_totals["recovered_row_count"],
                            added_totals["row_count"],
                        ),
                    },
                }
                best_add_uids = add_uids
        if best is None:
            break
        selected_uids.update(best_add_uids)
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
    return chosen, len(candidates)


def make_slices(
    pilot_rows: list[dict[str, Any]],
    heldout_namespace: str,
    stratify_by: str | None,
) -> list[dict[str, Any]]:
    train_pool = [row for row in pilot_rows if row["base_namespace"] != heldout_namespace]
    test_pool = [row for row in pilot_rows if row["base_namespace"] == heldout_namespace]
    if stratify_by is None:
        return [{"label": "all", "train": train_pool, "test": test_pool}]
    labels = sorted({row[stratify_by] for row in test_pool})
    return [
        {
            "label": str(label),
            "train": [row for row in train_pool if row[stratify_by] == label],
            "test": [row for row in test_pool if row[stratify_by] == label],
        }
        for label in labels
    ]


def evaluate_rule_list_cross_validated(
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
    stratify_by: str | None,
) -> list[dict[str, Any]]:
    namespaces = sorted({row["base_namespace"] for row in rows})
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    selected_by_k: dict[int, dict[str, dict[str, Any]]] = {int(k): {} for k in top_ks}
    diagnostics: dict[int, list[dict[str, Any]]] = {int(k): [] for k in top_ks}
    max_k = max(top_ks)
    for namespace in namespaces:
        for audit_slice in make_slices(pilot_rows, namespace, stratify_by):
            ranked, candidate_count = greedy_rule_list(
                p830.row_totals,
                audit_slice["train"],
                max_k,
                depths,
                min_rows_per_namespace_by_depth,
                min_total_rows_by_depth,
                prior_online,
                require_recovered_each_namespace,
                max_candidates,
                score_mode,
            )
            for k in top_ks:
                clauses = [tuple(item["clause"]) for item in ranked[: int(k)]]
                selected = select_by_clauses(audit_slice["test"], clauses)
                for row in selected:
                    selected_by_k[int(k)][row_uid(row)] = row
                diagnostics[int(k)].append(
                    {
                        "candidate_count": int(candidate_count),
                        "heldout_namespace": namespace,
                        "selected_rules": [clause_name(clause) for clause in clauses],
                        "selected_row_count": len(selected),
                        "slice_label": audit_slice["label"],
                        "stratify_by": stratify_by or "none",
                        "test_pilot_rows": len(audit_slice["test"]),
                        "test_recovered_rows": sum(1 for row in audit_slice["test"] if row["recovered"]),
                        "test_selected_recovered_rows": sum(1 for row in selected if row["recovered"]),
                        "train_namespaces": sorted({row["base_namespace"] for row in audit_slice["train"]}),
                        "train_pilot_rows": len(audit_slice["train"]),
                        "train_recovered_rows": sum(1 for row in audit_slice["train"] if row["recovered"]),
                    }
                )
    pilot_totals_full = p830.row_totals(pilot_rows)
    results = []
    for k in top_ks:
        selected = list(selected_by_k[int(k)].values())
        selected_totals = p830.row_totals(selected)
        policy_kind = "loo_public_recurrent_rule_list"
        if stratify_by:
            policy_kind = f"loo_public_{stratify_by}_stratified_recurrent_rule_list"
        results.append(
            {
                "charge_model": p830.charged_model(selected, base_rows, fixed_cost, field_weight),
                "diagnostics": diagnostics[int(k)],
                "pilot_only_compression": ratio(
                    selected_totals["online_group_additions"],
                    pilot_totals_full["online_group_additions"],
                ),
                "pilot_only_recovered_preservation": ratio(
                    selected_totals["recovered_row_count"],
                    pilot_totals_full["recovered_row_count"],
                ),
                "policy": {
                    "depths": depths,
                    "kind": policy_kind,
                    "max_candidates": int(max_candidates),
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
                "selected_pilot_only": selected_totals,
            }
        )
    results.sort(
        key=lambda item: (
            item["charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
            item["policy"]["top_k_per_slice"],
        )
    )
    return results


def best_ratio(item: dict[str, Any] | None) -> float:
    if item is None:
        return 10**9
    value = item["charge_model"]["post_hit_total_cost_over_recovered_rho"]
    return float(value) if value is not None else 10**9


def determine_claim(
    full_model: dict[str, Any],
    p832_best_public: dict[str, Any] | None,
    p831_best_oracle: dict[str, Any] | None,
    best_rule_list: dict[str, Any] | None,
) -> str:
    full_ratio = float(full_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    p832_ratio = best_ratio(p832_best_public)
    rule_ratio = best_ratio(best_rule_list)
    oracle_ratio = best_ratio(p831_best_oracle)
    if rule_ratio < 1.0:
        return "P833_PUBLIC_RULE_LIST_BELOW_RHO"
    if rule_ratio < full_ratio:
        return "P833_PUBLIC_RULE_LIST_IMPROVES_P826"
    if rule_ratio < p832_ratio:
        return "P833_PUBLIC_RULE_LIST_IMPROVES_P832_BUT_NOT_P826"
    if oracle_ratio < full_ratio:
        return "NEGATIVE_RESULT_P833_RULE_LIST_DOES_NOT_CLOSE_ORACLE_GAP"
    return "NEGATIVE_RESULT_P833_RULE_LIST_DOES_NOT_IMPROVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p832 = load_p832()
    p831 = p832.load_p831()
    p830 = p831.load_p830()
    rows, build_meta = p830.build_rows(args)
    fixed = p830.find_p826_fixed_cost(args.p826_probe, int(args.field_weight))
    top_ks = csv_ints(args.top_ks)
    category_totals = p830.totals_by_category(rows)
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    full_model = p830.charged_model(pilot_rows, base_rows, fixed["fixed_cost"], int(args.field_weight))

    p831_public = p831.evaluate_cross_validated(
        p830,
        rows,
        fixed["fixed_cost"],
        int(args.field_weight),
        top_ks,
        int(args.min_conjunction_rows),
    )
    p831_oracle = p831.evaluate_oracle_upper(
        p830,
        rows,
        fixed["fixed_cost"],
        int(args.field_weight),
        top_ks,
        int(args.min_conjunction_rows),
    )
    p832_global = p832.evaluate_stable_cross_validated(
        p830,
        rows,
        fixed["fixed_cost"],
        int(args.field_weight),
        top_ks,
        int(args.min_stable_rows_per_namespace),
        int(args.min_stable_total_rows),
        int(args.support_prior_online),
        bool(args.require_recovered_each_namespace),
        None,
    )

    global_depths = csv_depths(args.rule_depths)
    group_depths = csv_depths(args.group_rule_depths)
    min_ns = depth_minima(args.min_rule_rows_per_namespace_by_depth, int(args.min_rule_rows_per_namespace))
    min_total = depth_minima(args.min_rule_total_rows_by_depth, int(args.min_rule_total_rows))
    group_min_ns = depth_minima(args.group_min_rule_rows_per_namespace_by_depth, int(args.group_min_rule_rows_per_namespace))
    group_min_total = depth_minima(args.group_min_rule_total_rows_by_depth, int(args.group_min_rule_total_rows))

    policy_results = []
    for score_mode in str(args.score_modes).split(","):
        score_mode = score_mode.strip()
        if not score_mode:
            continue
        policy_results.extend(
            evaluate_rule_list_cross_validated(
                p830,
                rows,
                fixed["fixed_cost"],
                int(args.field_weight),
                top_ks,
                global_depths,
                min_ns,
                min_total,
                int(args.support_prior_online),
                bool(args.require_recovered_each_namespace),
                int(args.max_rule_candidates),
                score_mode,
                None,
            )
        )
        policy_results.extend(
            evaluate_rule_list_cross_validated(
                p830,
                rows,
                fixed["fixed_cost"],
                int(args.field_weight),
                top_ks,
                group_depths,
                group_min_ns,
                group_min_total,
                int(args.support_prior_online),
                bool(args.require_recovered_each_namespace),
                int(args.max_group_rule_candidates),
                score_mode,
                "group_key",
            )
        )
    policy_results.sort(
        key=lambda item: (
            item["charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
            item["policy"]["kind"],
            item["policy"]["top_k_per_slice"],
        )
    )
    best_rule_list = policy_results[0] if policy_results else None
    p832_best = p832_global[0] if p832_global else None
    claim_status = determine_claim(full_model, p832_best, p831_oracle[0] if p831_oracle else None, best_rule_list)

    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "p830_script": str(p831.P830_SCRIPT),
            "p831_script": str(p832.P831_SCRIPT),
            "p832_script": str(P832_SCRIPT),
            "script": str(Path(__file__)),
        },
        "build_meta": build_meta,
        "claim_status": claim_status,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC RULE LIST: held-out rows are selected only by rules trained on other namespaces.",
            "RECURRENT LEAVES: every rule leaf must recur across both training namespaces for the audited slice.",
            "MODEL-BOUND: cost uses P826 fixed cost plus measured row online additions and scoring-field accounting.",
            "ORACLE CEILING: P831 same-population compression remains separated from public validation.",
            "NO DEPLOYED-CURVE CLAIM: this is an index-calculus precursor audit, not a faster-than-rho deployed ECDLP algorithm.",
        ],
        "method": "p833_public_recurrent_rule_list_audit",
        "parameters": {
            "fixed_cost": fixed,
            "group_rule_depths": group_depths,
            "max_group_rule_candidates": int(args.max_group_rule_candidates),
            "max_rule_candidates": int(args.max_rule_candidates),
            "min_conjunction_rows_for_p831_baseline": int(args.min_conjunction_rows),
            "rule_depths": global_depths,
            "score_modes": [mode.strip() for mode in str(args.score_modes).split(",") if mode.strip()],
            "support_prior_online": int(args.support_prior_online),
            "top_ks": top_ks,
        },
        "red_team_handoff": {
            "assumptions": [
                "Training recovered-row labels are allowed only for ranking rules inside non-held-out namespaces.",
                "Held-out namespace labels are used only for final evaluation.",
                "Depth-3 rules are public tag conjunctions, not private oracle row identifiers.",
            ],
            "failure_modes": [
                "Depth-3 rules may overfit recurring namespace artifacts.",
                "Recall-first scoring can select too much pilot mass and erase compression gains.",
                "Density-first scoring can miss rare recovered-rho mass.",
                "Any result above rho is not an ECDLP break; it is only a relation-generation signal.",
            ],
            "next_concrete_action_if_negative": (
                "Switch from row-tag rule learning to a structural pilot generator: derive the recurrent rules from "
                "support schedules or polynomial identities and charge generation directly."
            ),
        },
        "row_population": {
            "category_totals": category_totals,
            "full_p826_reconstructed_charge_model": full_model,
        },
        "rule_list_transfer": {
            "best_public_rule_list": best_rule_list,
            "p831_oracle_ceiling_best": p831_oracle[0] if p831_oracle else None,
            "p831_public_loo_best": p831_public[0] if p831_public else None,
            "p832_public_stabilized_best": p832_best,
            "public_rule_list_results": policy_results,
        },
        "schema": SCHEMA,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    transfer = payload["rule_list_transfer"]
    return {
        **payload,
        "rule_list_transfer": {
            "best_public_rule_list": transfer["best_public_rule_list"],
            "p831_oracle_ceiling_best": transfer["p831_oracle_ceiling_best"],
            "p831_public_loo_best": transfer["p831_public_loo_best"],
            "p832_public_stabilized_best": transfer["p832_public_stabilized_best"],
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
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_public_rule_list": summary["rule_list_transfer"]["best_public_rule_list"],
                "claim_status": summary["claim_status"],
                "full_p826_reconstructed_charge_model": summary["row_population"]["full_p826_reconstructed_charge_model"],
                "p831_oracle_ceiling_best": summary["rule_list_transfer"]["p831_oracle_ceiling_best"],
                "p832_public_stabilized_best": summary["rule_list_transfer"]["p832_public_stabilized_best"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
