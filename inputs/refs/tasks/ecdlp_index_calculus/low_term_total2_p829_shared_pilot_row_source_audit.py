#!/usr/bin/env python3
"""P829 shared-pilot row-source attribution audit for P826."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P826_SCRIPT = TASK_DIR / "low_term_total2_p826_frozen_shared_pilot_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p829_shared_pilot_row_source_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p829_shared_pilot_row_source_audit.md"
SCHEMA = "ecdlp.low_term_total2_p829_shared_pilot_row_source_audit.v1"


def load_p826() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p826_for_p829", P826_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P826 helpers from {P826_SCRIPT}")
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


def source_category(sources: set[str]) -> str:
    has_pilot = "shared_full_pool_pilot" in sources
    has_continuation = "selected_support_continuation" in sources
    if has_pilot and has_continuation:
        return "both_pilot_and_continuation_duplicate"
    if has_pilot:
        return "pilot_only"
    if has_continuation:
        return "continuation_only"
    return "unknown"


def merge_with_sources(
    p825: Any,
    env: dict[str, Any],
    record: dict[str, Any],
    pilot_prepared: dict[str, Any],
    final_prepared: dict[str, Any],
    namespace: str,
    selected_policy: str,
    pilot_budget: int,
    final_budget: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    context_id = env["p812"].context_id(namespace, record["group_key"])
    rows_meta: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    examples: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    row_sources: dict[str, set[str]] = {}
    source_old_keys: dict[str, list[dict[str, Any]]] = defaultdict(list)
    stats = Counter()

    for source_name, prepared in (
        ("shared_full_pool_pilot", pilot_prepared),
        ("selected_support_continuation", final_prepared),
    ):
        by_row = p825.rows_by_key(prepared)
        by_example = p825.examples_by_key(prepared)
        for old_key in sorted(prepared["prepared"]["rows_meta"]):
            fingerprint = p825.row_fingerprint(prepared, old_key, by_row)
            if fingerprint in seen:
                new_key = seen[fingerprint]
                row_sources.setdefault(new_key, set()).add(source_name)
                source_old_keys[new_key].append({"old_key": old_key, "source": source_name})
                stats[f"{source_name}_deduped_rows"] += 1
                continue
            row_index = len(rows_meta)
            new_key = f"{record['target']}:829:{row_index}"
            seen[fingerprint] = new_key
            row_sources[new_key] = {source_name}
            source_old_keys[new_key].append({"old_key": old_key, "source": source_name})
            meta = copy.deepcopy(prepared["prepared"]["rows_meta"][old_key])
            meta["replica"] = 0
            meta["row_index"] = row_index
            rows_meta[new_key] = meta
            stats[f"{source_name}_added_rows"] += 1
            for old_record in by_row.get(old_key, []):
                new_record = copy.deepcopy(old_record)
                new_record["replica"] = 0
                new_record["row_index"] = row_index
                new_record["row_key"] = new_key
                records.append(new_record)
            source_example = by_example.get(old_key)
            if source_example is None:
                source_example = {"features": {}, "label": False, "target": record["target"]}
            example = copy.deepcopy(source_example)
            example["context_id"] = context_id
            example["group_key"] = record["group_key"]
            example["namespace"] = namespace
            example["row_key"] = new_key
            example["target"] = record["target"]
            examples.append(example)

    records.sort(
        key=lambda item: (
            tuple(item.get("support") or ()),
            int(item.get("replica") or 0),
            int(item.get("row_index") or 0),
            int(item.get("form_index") or 0),
        )
    )
    row_keys = set(rows_meta)
    context = {
        "allocated_continuation_budget": int(final_budget),
        "base_namespace": record["namespace"],
        "context_id": context_id,
        "examples": examples,
        "factor_base_size": int(final_prepared.get("factor_base_size") or pilot_prepared.get("factor_base_size") or 0),
        "group_key": record["group_key"],
        "namespace": namespace,
        "order": int(final_prepared["order"]),
        "pilot_budget": int(pilot_budget),
        "pool_online_group_additions": int(env["p797"].row_online(rows_meta, row_keys)),
        "pool_recovered_label_count": sum(1 for example in examples if example.get("label")),
        "pool_rho_baseline": int(env["p797"].row_rho(rows_meta, row_keys)),
        "pool_row_count": len(row_keys),
        "prefix_row_count": int(final_prepared.get("prefix_row_count") or pilot_prepared.get("prefix_row_count") or 0),
        "prepared": {
            "dest_target": record["target"],
            "order": int(final_prepared["order"]),
            "records": records,
            "row_count": len(row_keys),
            "rows_meta": rows_meta,
        },
        "setup_stats": final_prepared["setup_stats"],
        "shared_pilot_policy_name": "continuation_all_pair",
        "support_policy_name": selected_policy,
        "target": record["target"],
    }
    row_source_categories = {row_key: source_category(sources) for row_key, sources in row_sources.items()}
    source_meta = {
        "merge_stats": {key: int(value) for key, value in stats.items()},
        "row_source_categories": row_source_categories,
        "row_sources": {key: sorted(values) for key, values in row_sources.items()},
        "source_old_keys": source_old_keys,
    }
    return context, source_meta


def detailed_score_rows(
    p793: Any,
    prepared: dict[str, Any],
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    row_keys: set[str],
    order: int,
) -> dict[str, dict[str, Any]]:
    rows_meta = prepared["rows_meta"]
    row_results: dict[str, dict[str, Any]] = {}
    for record in prepared["records"]:
        row_key = str(record["row_key"])
        if row_key not in row_keys:
            continue
        parts = p793.line_parts(record, int(order))
        if parts is None or parts["line_key"] not in trained:
            continue
        line_value = int(trained[parts["line_key"]]["line_value"])
        known_sum = (int(parts["scale"]) * line_value) % int(order)
        try:
            secret = ((int(record["rhs"]) - known_sum) * pow(int(record["q_coeff"]), -1, int(order))) % int(order)
        except ValueError:
            continue
        row = row_results.setdefault(
            row_key,
            {
                **rows_meta[row_key],
                "matched_forms": [],
                "scored_form_count": 0,
            },
        )
        row["scored_form_count"] += 1
        if secret == int(record["expected_secret"]):
            row["matched_forms"].append(
                {
                    "form_index": int(record["form_index"]),
                    "line_key": list(parts["line_key"]),
                    "support": [int(value) for value in record["support"]],
                }
            )
    return row_results


def summarize_sources(
    env: dict[str, Any],
    contexts: dict[str, dict[str, Any]],
    source_maps: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    totals: dict[str, Counter] = defaultdict(Counter)
    context_summaries = []
    recovered_samples = []
    for context_id, context in sorted(contexts.items()):
        rows_meta = context["prepared"]["rows_meta"]
        row_keys = set(rows_meta)
        details = detailed_score_rows(
            env["p793"],
            context["prepared"],
            env["trained_by_group"][context["group_key"]],
            row_keys,
            int(context["order"]),
        )
        source_meta = source_maps[context_id]
        context_totals: dict[str, Counter] = defaultdict(Counter)
        for row_key, meta in rows_meta.items():
            category = source_meta["row_source_categories"].get(row_key, "unknown")
            for bucket in (category, "all"):
                totals[bucket]["row_count"] += 1
                totals[bucket]["online_group_additions"] += int(meta.get("online_group_additions") or 0)
                totals[bucket]["rho_baseline"] += int(meta.get("generic_rho_steps") or 0)
                context_totals[bucket]["row_count"] += 1
                context_totals[bucket]["online_group_additions"] += int(meta.get("online_group_additions") or 0)
                context_totals[bucket]["rho_baseline"] += int(meta.get("generic_rho_steps") or 0)
        for row_key, row in details.items():
            category = source_meta["row_source_categories"].get(row_key, "unknown")
            scored = int(row.get("scored_form_count") or 0)
            recovered = bool(row.get("matched_forms"))
            for bucket in (category, "all"):
                totals[bucket]["scored_row_count"] += 1
                totals[bucket]["scored_form_count"] += scored
                context_totals[bucket]["scored_row_count"] += 1
                context_totals[bucket]["scored_form_count"] += scored
                if recovered:
                    totals[bucket]["recovered_row_count"] += 1
                    totals[bucket]["recovered_rho_baseline"] += int(row.get("generic_rho_steps") or 0)
                    context_totals[bucket]["recovered_row_count"] += 1
                    context_totals[bucket]["recovered_rho_baseline"] += int(row.get("generic_rho_steps") or 0)
        for row_key, row in sorted(details.items()):
            if row.get("matched_forms") and len(recovered_samples) < 24:
                recovered_samples.append(
                    {
                        "category": source_meta["row_source_categories"].get(row_key, "unknown"),
                        "context_id": context_id,
                        "row_key": row_key,
                        "seed_label": row.get("seed_label"),
                        "target": context["target"],
                    }
                )
        context_summaries.append(
            {
                "context_id": context_id,
                "group_key": context["group_key"],
                "merge_stats": source_meta["merge_stats"],
                "source_totals": compact_totals(context_totals),
                "target": context["target"],
            }
        )
    compacted = compact_totals(totals)
    for category, item in compacted.items():
        item["recovered_row_rate_over_rows"] = ratio(item["recovered_row_count"], item["row_count"])
        item["recovered_rho_rate_over_rho"] = ratio(item["recovered_rho_baseline"], item["rho_baseline"])
    return {
        "context_summaries": context_summaries,
        "recovered_samples": recovered_samples,
        "source_totals": compacted,
    }


def compact_totals(raw: dict[str, Counter]) -> dict[str, dict[str, int]]:
    keys = [
        "online_group_additions",
        "recovered_rho_baseline",
        "recovered_row_count",
        "rho_baseline",
        "row_count",
        "scored_form_count",
        "scored_row_count",
    ]
    return {
        category: {key: int(counter.get(key) or 0) for key in keys}
        for category, counter in sorted(raw.items())
    }


def build_p829(args: argparse.Namespace) -> dict[str, Any]:
    p826 = load_p826()
    p825 = p826.load_p825()
    p823 = p825.load_p823()
    env = p823.build_environment(args)
    env["p823"] = p823
    env["pilot_budgets"] = [p826.FROZEN_PILOT_BUDGET]
    records = [
        record
        for record in env["records_by_prefix"][int(p826.FROZEN_PREFIX_SEED_COUNT)]
        if record["namespace"] in set(env["test_namespaces"])
    ]
    profiles = [
        p825.choose_support(record, p825.SLATES[p826.FROZEN_SLATE], p826.FROZEN_PILOT_BUDGET, p826.FROZEN_SELECTOR)
        for record in records
    ]
    final_budgets = p825.allocate_budgets(
        profiles,
        env["candidate_budgets"],
        p826.FROZEN_AVERAGE_BUDGET * len(records) - p826.FROZEN_PILOT_BUDGET * len(records),
        p826.FROZEN_ALLOCATOR,
    )
    if final_budgets is None:
        raise RuntimeError("P829 could not reproduce P826 final budgets")
    contexts = {}
    source_maps = {}
    choices = []
    for record, profile, final_budget in zip(records, profiles, final_budgets):
        selected_policy = str(profile["policy_name"])
        pilot_prepared = record["prepared_by_policy_budget"][(env["p823"].FULL_POOL_POLICY, int(p826.FROZEN_PILOT_BUDGET))]
        final_prepared = record["prepared_by_policy_budget"][(selected_policy, int(final_budget))]
        namespace = (
            f"{record['namespace']}:p{p826.FROZEN_PREFIX_SEED_COUNT}:p829:{p826.FROZEN_SLATE}:"
            f"{p826.FROZEN_SELECTOR}:{p826.FROZEN_ALLOCATOR}:{selected_policy}:"
            f"pilot{p826.FROZEN_PILOT_BUDGET}:b{final_budget}"
        )
        context, source_meta = merge_with_sources(
            p825,
            env,
            record,
            pilot_prepared,
            final_prepared,
            namespace,
            selected_policy,
            p826.FROZEN_PILOT_BUDGET,
            int(final_budget),
        )
        contexts[context["context_id"]] = context
        source_maps[context["context_id"]] = source_meta
        choices.append(
            {
                "allocated_final_budget": int(final_budget),
                "base_context_id": record["context_id"],
                "group_key": record["group_key"],
                "selected_policy": selected_policy,
                "target": record["target"],
            }
        )
    source_summary = summarize_sources(env, contexts, source_maps)
    source_totals = source_summary["source_totals"]
    pilot_only = source_totals.get("pilot_only", {})
    continuation_only = source_totals.get("continuation_only", {})
    both = source_totals.get("both_pilot_and_continuation_duplicate", {})
    pilot_recovered = int(pilot_only.get("recovered_row_count") or 0) + int(both.get("recovered_row_count") or 0)
    continuation_recovered = int(continuation_only.get("recovered_row_count") or 0) + int(both.get("recovered_row_count") or 0)
    all_recovered = int(source_totals.get("all", {}).get("recovered_row_count") or 0)
    if pilot_recovered > continuation_recovered:
        claim_status = "P829_SHARED_PILOT_ROWS_DOMINATE_P826_RECOVERY"
    elif continuation_recovered > pilot_recovered:
        claim_status = "P829_SELECTED_CONTINUATION_ROWS_DOMINATE_P826_RECOVERY"
    elif all_recovered:
        claim_status = "P829_PILOT_AND_CONTINUATION_RECOVERY_BALANCED"
    else:
        claim_status = "NEGATIVE_RESULT_P829_NO_RECOVERED_ROWS_REPRODUCED"
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_script": str(P826_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "handoff": {
            "next_concrete_action": (
                "Build P830 to replace the high-yield pilot-only row source with a smaller public support schedule, "
                "using P829 pilot-only recovered row fingerprints as the target population."
            ),
            "status": "OBSERVATION",
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MODEL-BOUND: P829 rebuilds P826 contexts and attributes rows by deterministic row fingerprint during merge.",
            "NO BELOW-RHO CLAIM: this is row-source attribution, not a faster-than-rho ECDLP algorithm.",
            "TARGET-DESCENT NOT SOLVED: recovered rows are source-attributed but not converted into individual-log descent.",
        ],
        "method": "p829_shared_pilot_row_source_audit",
        "parameters": {
            "average_continuation_budget": p826.FROZEN_AVERAGE_BUDGET,
            "final_budgets": [int(value) for value in final_budgets],
            "pilot_budget": p826.FROZEN_PILOT_BUDGET,
            "prefix_seed_count": p826.FROZEN_PREFIX_SEED_COUNT,
            "selected_choices": choices,
            "selector": p826.FROZEN_SELECTOR,
            "slate": p826.FROZEN_SLATE,
        },
        "schema": SCHEMA,
        "source_attribution": {
            **source_summary,
            "derived_recovered_counts": {
                "all_recovered_rows": all_recovered,
                "continuation_inclusive_recovered_rows": continuation_recovered,
                "pilot_inclusive_recovered_rows": pilot_recovered,
            },
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload["source_attribution"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "source_attribution": {
            "derived_recovered_counts": source["derived_recovered_counts"],
            "source_totals": source["source_totals"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--train-constructor-namespaces", default="")
    parser.add_argument(
        "--test-constructor-namespaces",
        default="posthit-p826-fresh-v32,posthit-p826-fresh-v33,posthit-p826-fresh-v34",
    )
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
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_p829(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "derived_recovered_counts": summary["source_attribution"]["derived_recovered_counts"],
                "source_totals": summary["source_attribution"]["source_totals"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
