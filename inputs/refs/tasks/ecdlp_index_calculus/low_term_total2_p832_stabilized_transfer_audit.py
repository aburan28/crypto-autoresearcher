#!/usr/bin/env python3
"""P832 stabilized public transfer audit for P829 pilot-only rows."""

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
P831_SCRIPT = TASK_DIR / "low_term_total2_p831_conjunction_compression_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p832_stabilized_transfer_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p832_stabilized_transfer_audit.md"
SCHEMA = "ecdlp.low_term_total2_p832_stabilized_transfer_audit.v1"


def load_p831() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p831_for_p832", P831_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P831 helpers from {P831_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def density(totals: dict[str, Any]) -> float:
    online = int(totals.get("online_group_additions") or 0)
    if online <= 0:
        return 0.0
    return float(totals.get("recovered_rho_baseline") or 0) / float(online)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def csv_ints(raw: str) -> list[int]:
    return [int(part.strip()) for part in str(raw).split(",") if part.strip()]


def row_uid(row: dict[str, Any]) -> str:
    return f"{row['context_id']}::{row['row_key']}"


def conjunction_name(pair: tuple[str, str]) -> str:
    return f"{pair[0]} && {pair[1]}"


def support_span_bucket(row: dict[str, Any]) -> int:
    return abs(int(row["support_right"]) - int(row["support_left"])) // 16


def candidate_support_bucket(pair: tuple[str, str], rows: list[dict[str, Any]]) -> int:
    for tag in pair:
        if tag.startswith("support_span_bucket16="):
            return int(tag.split("=", 1)[1])
    buckets = Counter(support_span_bucket(row) for row in rows)
    if not buckets:
        return -1
    return buckets.most_common(1)[0][0]


def support_bucket_priors(
    row_totals_fn: Any,
    train_rows: list[dict[str, Any]],
) -> dict[int, float]:
    by_bucket: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in train_rows:
        by_bucket[support_span_bucket(row)].append(row)
    priors = {bucket: density(row_totals_fn(rows)) for bucket, rows in by_bucket.items()}
    priors[-1] = density(row_totals_fn(train_rows))
    return priors


def smoothed_density(
    totals: dict[str, Any],
    prior_density: float,
    prior_online: int,
) -> float:
    online = int(totals["online_group_additions"])
    recovered_rho = int(totals["recovered_rho_baseline"])
    return (float(recovered_rho) + float(prior_density) * int(prior_online)) / float(online + int(prior_online))


def harmonic(values: list[float]) -> float:
    positives = [value for value in values if value > 0.0]
    if len(positives) != len(values) or not positives:
        return 0.0
    return float(len(positives)) / sum(1.0 / value for value in positives)


def stable_conjunction_stats(
    row_totals_fn: Any,
    rows: list[dict[str, Any]],
    min_rows_per_namespace: int,
    min_total_rows: int,
    prior_online: int,
    require_recovered_each_namespace: bool,
) -> list[dict[str, Any]]:
    namespaces = sorted({row["base_namespace"] for row in rows})
    if len(namespaces) < 2:
        return []
    by_pair_ns: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        tags = sorted(set(row["tags"]))
        for pair in itertools.combinations(tags, 2):
            by_pair_ns[pair][row["base_namespace"]].append(row)

    priors = support_bucket_priors(row_totals_fn, rows)
    stats = []
    for pair, by_ns in by_pair_ns.items():
        if any(len(by_ns.get(namespace, [])) < int(min_rows_per_namespace) for namespace in namespaces):
            continue
        selected = [row for namespace in namespaces for row in by_ns[namespace]]
        if len(selected) < int(min_total_rows):
            continue
        totals = row_totals_fn(selected)
        if int(totals["recovered_row_count"]) <= 0:
            continue
        bucket = candidate_support_bucket(pair, selected)
        prior = priors.get(bucket, priors[-1])
        per_namespace = []
        smoothed_scores = []
        for namespace in namespaces:
            ns_totals = row_totals_fn(by_ns[namespace])
            if require_recovered_each_namespace and int(ns_totals["recovered_row_count"]) <= 0:
                per_namespace = []
                break
            ns_smoothed = smoothed_density(ns_totals, prior, int(prior_online))
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
                "conjunction": list(pair),
                "name": conjunction_name(pair),
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
            item["name"],
        ),
        reverse=True,
    )
    return stats


def rows_matching_conjunction(rows: list[dict[str, Any]], pair: tuple[str, str]) -> list[dict[str, Any]]:
    left, right = pair
    return [row for row in rows if left in set(row["tags"]) and right in set(row["tags"])]


def select_by_conjunctions(rows: list[dict[str, Any]], pairs: list[tuple[str, str]]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for pair in pairs:
        for row in rows_matching_conjunction(rows, pair):
            selected[row_uid(row)] = row
    return list(selected.values())


def stable_greedy_conjunctions(
    row_totals_fn: Any,
    rows: list[dict[str, Any]],
    max_k: int,
    min_rows_per_namespace: int,
    min_total_rows: int,
    prior_online: int,
    require_recovered_each_namespace: bool,
) -> tuple[list[dict[str, Any]], int]:
    candidates = stable_conjunction_stats(
        row_totals_fn,
        rows,
        min_rows_per_namespace,
        min_total_rows,
        prior_online,
        require_recovered_each_namespace,
    )
    by_uid = {row_uid(row): row for row in rows}
    selected_uids: set[str] = set()
    chosen = []
    for _index in range(int(max_k)):
        best = None
        best_add_uids: set[str] = set()
        for candidate in candidates:
            pair = tuple(candidate["conjunction"])
            candidate_uids = {row_uid(row) for row in rows_matching_conjunction(rows, pair)}
            add_uids = candidate_uids - selected_uids
            if not add_uids:
                continue
            added_rows = [by_uid[uid] for uid in add_uids]
            added_totals = row_totals_fn(added_rows)
            if int(added_totals["recovered_row_count"]) <= 0:
                continue
            increment_density = ratio(
                added_totals["recovered_rho_baseline"],
                added_totals["online_group_additions"],
            )
            score = (
                float(candidate["score_components"]["min_smoothed_recovered_rho_per_online"]),
                float(candidate["score_components"]["harmonic_smoothed_recovered_rho_per_online"]),
                float(increment_density or 0.0),
                int(added_totals["recovered_row_count"]),
                int(added_totals["recovered_rho_baseline"]),
                -int(added_totals["online_group_additions"]),
                candidate["name"],
            )
            if best is None or score > best["score"]:
                best = {
                    "candidate": candidate,
                    "score": score,
                    "selected_increment": {
                        **added_totals,
                        "recovered_rho_per_online": increment_density,
                        "recovered_row_rate": ratio(added_totals["recovered_row_count"], added_totals["row_count"]),
                    },
                }
                best_add_uids = add_uids
        if best is None:
            break
        selected_uids.update(best_add_uids)
        chosen.append(
            {
                "conjunction": best["candidate"]["conjunction"],
                "name": best["candidate"]["name"],
                "score_components": best["candidate"]["score_components"],
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
    slices = []
    for label in labels:
        train = [row for row in train_pool if row[stratify_by] == label]
        test = [row for row in test_pool if row[stratify_by] == label]
        if test:
            slices.append({"label": str(label), "train": train, "test": test})
    return slices


def evaluate_stable_cross_validated(
    p830: Any,
    rows: list[dict[str, Any]],
    fixed_cost: int,
    field_weight: int,
    top_ks: list[int],
    min_rows_per_namespace: int,
    min_total_rows: int,
    prior_online: int,
    require_recovered_each_namespace: bool,
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
            chosen_ranked, candidate_count = stable_greedy_conjunctions(
                p830.row_totals,
                audit_slice["train"],
                max_k,
                min_rows_per_namespace,
                min_total_rows,
                prior_online,
                require_recovered_each_namespace,
            )
            for k in top_ks:
                chosen = [tuple(item["conjunction"]) for item in chosen_ranked[: int(k)]]
                selected = select_by_conjunctions(audit_slice["test"], chosen)
                for row in selected:
                    selected_by_k[int(k)][row_uid(row)] = row
                diagnostics[int(k)].append(
                    {
                        "candidate_count": int(candidate_count),
                        "heldout_namespace": namespace,
                        "selected_conjunctions": [conjunction_name(pair) for pair in chosen],
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
        policy_kind = "loo_public_stabilized_two_literal_conjunction_union"
        if stratify_by:
            policy_kind = f"loo_public_{stratify_by}_stratified_stabilized_two_literal_conjunction_union"
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
                    "kind": policy_kind,
                    "min_rows_per_namespace": int(min_rows_per_namespace),
                    "min_total_rows": int(min_total_rows),
                    "prior_online": int(prior_online),
                    "require_recovered_each_namespace": bool(require_recovered_each_namespace),
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
    p831_best_public: dict[str, Any] | None,
    p831_best_oracle: dict[str, Any] | None,
    best_stabilized_public: dict[str, Any] | None,
) -> str:
    full_ratio = float(full_model["post_hit_total_cost_over_recovered_rho"] or 10**9)
    stabilized_ratio = best_ratio(best_stabilized_public)
    p831_public_ratio = best_ratio(p831_best_public)
    oracle_ratio = best_ratio(p831_best_oracle)
    if stabilized_ratio < 1.0:
        return "P832_STABILIZED_PUBLIC_TRANSFER_BELOW_RHO"
    if stabilized_ratio < full_ratio:
        return "P832_STABILIZED_PUBLIC_TRANSFER_IMPROVES_P826"
    if stabilized_ratio < p831_public_ratio:
        return "P832_STABILIZATION_IMPROVES_PUBLIC_TRANSFER_BUT_NOT_P826"
    if oracle_ratio < full_ratio:
        return "NEGATIVE_RESULT_P832_STABILIZED_TRANSFER_DOES_NOT_CLOSE_ORACLE_GAP"
    return "NEGATIVE_RESULT_P832_STABILIZED_TRANSFER_DOES_NOT_IMPROVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p831 = load_p831()
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
    global_stable = evaluate_stable_cross_validated(
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
    group_stable = evaluate_stable_cross_validated(
        p830,
        rows,
        fixed["fixed_cost"],
        int(args.field_weight),
        top_ks,
        int(args.target_min_stable_rows_per_namespace),
        int(args.target_min_stable_total_rows),
        int(args.support_prior_online),
        bool(args.require_recovered_each_namespace),
        "group_key",
    )
    public_candidates = []
    if global_stable:
        public_candidates.append(global_stable[0])
    if group_stable:
        public_candidates.append(group_stable[0])
    public_candidates.sort(
        key=lambda item: (
            item["charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
        )
    )
    best_public = public_candidates[0] if public_candidates else None
    claim_status = determine_claim(full_model, p831_public[0] if p831_public else None, p831_oracle[0] if p831_oracle else None, best_public)

    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "p830_script": str(p831.P830_SCRIPT),
            "p831_script": str(P831_SCRIPT),
            "script": str(Path(__file__)),
        },
        "build_meta": build_meta,
        "claim_status": claim_status,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC TRANSFER: held-out rows are selected only by conjunctions trained on other namespaces.",
            "STABILIZATION: a selected conjunction must recur in both training namespaces for the audited slice.",
            "MODEL-BOUND: cost uses P826 fixed cost plus measured row online additions and scoring-field accounting.",
            "ORACLE CEILING: P831 same-population compression remains separated from public validation.",
            "NO DEPLOYED-CURVE CLAIM: this is an index-calculus precursor audit, not a faster-than-rho deployed ECDLP algorithm.",
        ],
        "method": "p832_stabilized_public_transfer_audit",
        "parameters": {
            "fixed_cost": fixed,
            "min_conjunction_rows_for_p831_baseline": int(args.min_conjunction_rows),
            "min_stable_rows_per_namespace": int(args.min_stable_rows_per_namespace),
            "min_stable_total_rows": int(args.min_stable_total_rows),
            "require_recovered_each_namespace": bool(args.require_recovered_each_namespace),
            "support_prior_online": int(args.support_prior_online),
            "target_min_stable_rows_per_namespace": int(args.target_min_stable_rows_per_namespace),
            "target_min_stable_total_rows": int(args.target_min_stable_total_rows),
            "top_ks": top_ks,
        },
        "red_team_handoff": {
            "assumptions": [
                "The support-bucket prior is public because it is fit only on training namespaces.",
                "Held-out namespace labels are not used for ranking, only for scoring after selection.",
                "Group-key stratification may improve recall by reducing transfer distance, but it increases policy count.",
            ],
            "failure_modes": [
                "The stable recurrence filter can discard rare real signal.",
                "The support-bucket prior may smooth away high-yield sparse conjunctions.",
                "Per-group top-k selection can overcharge policy search if promoted without a separate selection budget.",
                "Any result above rho is not an ECDLP break; it is only a relation-generation signal.",
            ],
            "next_concrete_action_if_negative": (
                "Test tree or DNF policies that preserve the P831 oracle rows while enforcing namespace recurrence "
                "at the leaf level."
            ),
        },
        "row_population": {
            "category_totals": category_totals,
            "full_p826_reconstructed_charge_model": full_model,
        },
        "schema": SCHEMA,
        "stabilized_transfer": {
            "best_public_stabilized": best_public,
            "best_public_stabilized_candidates": public_candidates,
            "global_stable_results": global_stable,
            "group_key_stratified_stable_results": group_stable,
            "p831_oracle_ceiling_best": p831_oracle[0] if p831_oracle else None,
            "p831_public_loo_best": p831_public[0] if p831_public else None,
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    transfer = payload["stabilized_transfer"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "stabilized_transfer": {
            "best_public_stabilized": transfer["best_public_stabilized"],
            "best_public_stabilized_candidates": transfer["best_public_stabilized_candidates"],
            "p831_oracle_ceiling_best": transfer["p831_oracle_ceiling_best"],
            "p831_public_loo_best": transfer["p831_public_loo_best"],
        },
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
    parser.add_argument("--target-min-stable-rows-per-namespace", type=int, default=1)
    parser.add_argument("--target-min-stable-total-rows", type=int, default=2)
    parser.add_argument("--support-prior-online", type=int, default=64)
    parser.add_argument("--require-recovered-each-namespace", action="store_true")
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
                "best_public_stabilized": summary["stabilized_transfer"]["best_public_stabilized"],
                "claim_status": summary["claim_status"],
                "full_p826_reconstructed_charge_model": summary["row_population"]["full_p826_reconstructed_charge_model"],
                "p831_oracle_ceiling_best": summary["stabilized_transfer"]["p831_oracle_ceiling_best"],
                "p831_public_loo_best": summary["stabilized_transfer"]["p831_public_loo_best"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
