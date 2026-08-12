#!/usr/bin/env python3
"""P830 public compression audit for P829 shared-pilot-only rows."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P829_SCRIPT = TASK_DIR / "low_term_total2_p829_shared_pilot_row_source_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p830_shared_pilot_compression_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p830_shared_pilot_compression_audit.md"
SCHEMA = "ecdlp.low_term_total2_p830_shared_pilot_compression_audit.v1"

FROZEN_PUBLIC_POLICY_NAME = "shared_core_score_hash_membership_rows_equal_remaining_p16"


def load_p829() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p829_for_p830", P829_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P829 helpers from {P829_SCRIPT}")
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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def csv_ints(raw: str) -> list[int]:
    return [int(part.strip()) for part in str(raw).split(",") if part.strip()]


def seed_int(seed_label: str | None) -> int:
    match = re.search(r"(\d+)$", str(seed_label or ""))
    return int(match.group(1)) if match else -1


def first_support(records: list[dict[str, Any]]) -> tuple[int, int]:
    supports = [tuple(int(value) for value in record.get("support") or ()) for record in records]
    supports = [support for support in supports if len(support) == 2]
    if not supports:
        return (0, 0)
    return tuple(sorted(supports)[0])


def row_tags(row: dict[str, Any]) -> set[str]:
    seed = int(row["seed_int"])
    left = int(row["support_left"])
    right = int(row["support_right"])
    support_sum = left + right
    support_span = abs(right - left)
    tags = set()
    for modulus in (2, 4, 8, 16, 32):
        tags.add(f"seed_mod{modulus}={seed % modulus}")
    tags.add(f"seed_band8={seed // 16}")
    for modulus in (2, 4, 8, 16):
        tags.add(f"support_sum_mod{modulus}={support_sum % modulus}")
    for modulus in (2, 4, 8):
        tags.add(f"support_left_mod{modulus}={left % modulus}")
        tags.add(f"support_right_mod{modulus}={right % modulus}")
        tags.add(f"support_span_mod{modulus}={support_span % modulus}")
    tags.add(f"support_parity={left % 2},{right % 2}")
    tags.add(f"support_span_bucket8={support_span // 8}")
    tags.add(f"support_span_bucket16={support_span // 16}")
    tags.add(f"support_low_bucket16={min(left, right) // 16}")
    tags.add(f"support_high_bucket16={max(left, right) // 16}")
    return tags


def find_p826_fixed_cost(p826_probe: Path, field_weight: int) -> dict[str, Any]:
    payload = load_json(p826_probe)
    for item in payload["summary"]["policy_results"]:
        if item.get("policy", {}).get("name") == FROZEN_PUBLIC_POLICY_NAME:
            aggregate = item["aggregate"]
            fixed = (
                int(aggregate["target_once_train_calibration_online_group_additions"])
                + int(aggregate["target_once_setup_group_additions"])
                + int(field_weight) * int(aggregate["target_once_train_calibration_field_ops"])
            )
            return {
                "fixed_cost": int(fixed),
                "p826_cost_over_rho": aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"],
                "p826_recovered_rho_baseline": int(aggregate["recovered_rho_baseline"]),
                "p826_recovered_row_count": int(aggregate["recovered_row_count"]),
                "p826_total_cost": int(aggregate["post_hit_scan_once_train_total_unit_cost"]),
            }
    raise ValueError(f"missing {FROZEN_PUBLIC_POLICY_NAME} in {p826_probe}")


def build_rows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    p829 = load_p829()
    p826 = p829.load_p826()
    p825 = p826.load_p825()
    p823 = p825.load_p823()
    env = p823.build_environment(args)
    env["p823"] = p823
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
        raise RuntimeError("P830 could not reproduce P826 final budgets")

    out_rows = []
    for record, profile, final_budget in zip(records, profiles, final_budgets):
        selected_policy = str(profile["policy_name"])
        pilot_prepared = record["prepared_by_policy_budget"][(env["p823"].FULL_POOL_POLICY, int(p826.FROZEN_PILOT_BUDGET))]
        final_prepared = record["prepared_by_policy_budget"][(selected_policy, int(final_budget))]
        namespace = (
            f"{record['namespace']}:p{p826.FROZEN_PREFIX_SEED_COUNT}:p830:{p826.FROZEN_SLATE}:"
            f"{p826.FROZEN_SELECTOR}:{p826.FROZEN_ALLOCATOR}:{selected_policy}:"
            f"pilot{p826.FROZEN_PILOT_BUDGET}:b{final_budget}"
        )
        context, source_meta = p829.merge_with_sources(
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
        row_keys = set(context["prepared"]["rows_meta"])
        details = p829.detailed_score_rows(
            env["p793"],
            context["prepared"],
            env["trained_by_group"][context["group_key"]],
            row_keys,
            int(context["order"]),
        )
        records_by_row = p825.rows_by_key({"prepared": context["prepared"]})
        for row_key, meta in context["prepared"]["rows_meta"].items():
            row_records = records_by_row.get(row_key, [])
            support_left, support_right = first_support(row_records)
            seed = seed_int(meta.get("seed_label"))
            detail = details.get(row_key) or {}
            recovered = bool(detail.get("matched_forms"))
            row = {
                "base_namespace": context["base_namespace"],
                "category": source_meta["row_source_categories"].get(row_key, "unknown"),
                "context_id": context["context_id"],
                "generic_rho_steps": int(meta.get("generic_rho_steps") or 0),
                "group_key": context["group_key"],
                "online_group_additions": int(meta.get("online_group_additions") or 0),
                "recovered": recovered,
                "recovered_rho_baseline": int(meta.get("generic_rho_steps") or 0) if recovered else 0,
                "row_key": row_key,
                "scored_form_count": int(detail.get("scored_form_count") or 0),
                "seed_int": seed,
                "seed_label": meta.get("seed_label"),
                "support_left": int(support_left),
                "support_right": int(support_right),
                "target": context["target"],
            }
            row["tags"] = sorted(row_tags(row))
            out_rows.append(row)
    meta = {
        "final_budgets": [int(value) for value in final_budgets],
        "selected_policy": sorted({str(profile["policy_name"]) for profile in profiles}),
        "test_namespaces": sorted({row["base_namespace"] for row in out_rows}),
    }
    return out_rows, meta


def row_totals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    recovered = [row for row in rows if row["recovered"]]
    return {
        "online_group_additions": sum(int(row["online_group_additions"]) for row in rows),
        "recovered_rho_baseline": sum(int(row["recovered_rho_baseline"]) for row in rows),
        "recovered_row_count": len(recovered),
        "rho_baseline": sum(int(row["generic_rho_steps"]) for row in rows),
        "row_count": len(rows),
        "scored_form_count": sum(int(row["scored_form_count"]) for row in rows),
    }


def totals_by_category(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {category: row_totals([row for row in rows if row["category"] == category]) for category in sorted({row["category"] for row in rows})}
    out["all"] = row_totals(rows)
    for item in out.values():
        item["recovered_row_rate_over_rows"] = ratio(item["recovered_row_count"], item["row_count"])
        item["recovered_rho_rate_over_rho"] = ratio(item["recovered_rho_baseline"], item["rho_baseline"])
    return out


def tag_stats(rows: list[dict[str, Any]], min_rows: int) -> list[dict[str, Any]]:
    by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for tag in row["tags"]:
            by_tag[tag].append(row)
    stats = []
    for tag, tagged_rows in by_tag.items():
        if len(tagged_rows) < int(min_rows):
            continue
        totals = row_totals(tagged_rows)
        stats.append(
            {
                "recovered_row_rate": ratio(totals["recovered_row_count"], totals["row_count"]),
                "tag": tag,
                **totals,
            }
        )
    stats.sort(
        key=lambda item: (
            int(item["recovered_row_count"]),
            float(item["recovered_row_rate"] or 0.0),
            int(item["recovered_rho_baseline"]),
            -int(item["online_group_additions"]),
            item["tag"],
        ),
        reverse=True,
    )
    return stats


def selected_by_tags(rows: list[dict[str, Any]], tags: set[str]) -> list[dict[str, Any]]:
    return [row for row in rows if set(row["tags"]) & tags]


def charged_model(
    selected_pilot_rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    fixed_cost: int,
    field_weight: int,
) -> dict[str, Any]:
    rows = list(base_rows) + list(selected_pilot_rows)
    totals = row_totals(rows)
    scoring_cost = int(field_weight) * int(totals["scored_form_count"]) * 4
    total_cost = int(fixed_cost) + int(totals["online_group_additions"]) + scoring_cost
    return {
        **totals,
        "fixed_cost": int(fixed_cost),
        "post_hit_total_cost": int(total_cost),
        "post_hit_total_cost_over_recovered_rho": ratio(total_cost, totals["recovered_rho_baseline"]),
        "scoring_field_weighted_cost": int(scoring_cost),
    }


def evaluate_cross_validated(rows: list[dict[str, Any]], fixed_cost: int, field_weight: int, top_ks: list[int], min_rows: int) -> list[dict[str, Any]]:
    namespaces = sorted({row["base_namespace"] for row in rows})
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    selected_by_k: dict[int, dict[str, dict[str, Any]]] = {int(k): {} for k in top_ks}
    diagnostics: dict[int, list[dict[str, Any]]] = {int(k): [] for k in top_ks}
    for namespace in namespaces:
        train = [row for row in pilot_rows if row["base_namespace"] != namespace]
        test = [row for row in pilot_rows if row["base_namespace"] == namespace]
        ranked = tag_stats(train, min_rows)
        for k in top_ks:
            chosen = {item["tag"] for item in ranked[: int(k)]}
            selected = selected_by_tags(test, chosen)
            for row in selected:
                selected_by_k[int(k)][row["row_key"] + "@" + row["context_id"]] = row
            diagnostics[int(k)].append(
                {
                    "heldout_namespace": namespace,
                    "selected_row_count": len(selected),
                    "selected_tags": sorted(chosen),
                    "test_pilot_rows": len(test),
                    "test_recovered_rows": sum(1 for row in test if row["recovered"]),
                    "test_selected_recovered_rows": sum(1 for row in selected if row["recovered"]),
                }
            )
    results = []
    for k in top_ks:
        selected = list(selected_by_k[int(k)].values())
        pilot_totals = row_totals(selected)
        charged = charged_model(selected, base_rows, fixed_cost, field_weight)
        results.append(
            {
                "charge_model": charged,
                "diagnostics": diagnostics[int(k)],
                "pilot_only_compression": ratio(pilot_totals["online_group_additions"], row_totals(pilot_rows)["online_group_additions"]),
                "pilot_only_recovered_preservation": ratio(pilot_totals["recovered_row_count"], row_totals(pilot_rows)["recovered_row_count"]),
                "policy": {
                    "kind": "loo_public_literal_union",
                    "top_k": int(k),
                },
                "selected_pilot_only": pilot_totals,
            }
        )
    results.sort(
        key=lambda item: (
            item["charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
            item["policy"]["top_k"],
        )
    )
    return results


def evaluate_oracle_upper(rows: list[dict[str, Any]], fixed_cost: int, field_weight: int, top_ks: list[int], min_rows: int) -> list[dict[str, Any]]:
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    ranked = tag_stats(pilot_rows, min_rows)
    results = []
    for k in top_ks:
        chosen = {item["tag"] for item in ranked[: int(k)]}
        selected = selected_by_tags(pilot_rows, chosen)
        pilot_totals = row_totals(selected)
        results.append(
            {
                "charge_model": charged_model(selected, base_rows, fixed_cost, field_weight),
                "pilot_only_compression": ratio(pilot_totals["online_group_additions"], row_totals(pilot_rows)["online_group_additions"]),
                "pilot_only_recovered_preservation": ratio(pilot_totals["recovered_row_count"], row_totals(pilot_rows)["recovered_row_count"]),
                "policy": {
                    "kind": "oracle_same_population_literal_union",
                    "selected_tags": sorted(chosen),
                    "top_k": int(k),
                },
                "selected_pilot_only": pilot_totals,
            }
        )
    results.sort(
        key=lambda item: (
            item["charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9,
            -item["selected_pilot_only"]["recovered_row_count"],
            item["policy"]["top_k"],
        )
    )
    return results


def determine_claim(full_model: dict[str, Any], best_public: dict[str, Any] | None, best_oracle: dict[str, Any] | None) -> str:
    full_ratio = full_model["post_hit_total_cost_over_recovered_rho"] or 10**9
    public_ratio = 10**9 if best_public is None else best_public["charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9
    oracle_ratio = 10**9 if best_oracle is None else best_oracle["charge_model"]["post_hit_total_cost_over_recovered_rho"] or 10**9
    if public_ratio < 1.0:
        return "P830_PUBLIC_SHARED_PILOT_COMPRESSION_BELOW_RHO"
    if public_ratio < full_ratio:
        return "P830_PUBLIC_SHARED_PILOT_COMPRESSION_IMPROVES_P826"
    if oracle_ratio < full_ratio:
        return "P830_ORACLE_COMPRESSION_CEILING_ONLY"
    return "NEGATIVE_RESULT_P830_PUBLIC_COMPRESSION_DOES_NOT_IMPROVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows, build_meta = build_rows(args)
    fixed = find_p826_fixed_cost(args.p826_probe, int(args.field_weight))
    top_ks = csv_ints(args.top_ks)
    category_totals = totals_by_category(rows)
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    full_model = charged_model(pilot_rows, base_rows, fixed["fixed_cost"], int(args.field_weight))
    public_results = evaluate_cross_validated(rows, fixed["fixed_cost"], int(args.field_weight), top_ks, int(args.min_literal_rows))
    oracle_results = evaluate_oracle_upper(rows, fixed["fixed_cost"], int(args.field_weight), top_ks, int(args.min_literal_rows))
    best_public = public_results[0] if public_results else None
    best_oracle = oracle_results[0] if oracle_results else None
    claim_status = determine_claim(full_model, best_public, best_oracle)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "p829_script": str(P829_SCRIPT),
            "script": str(Path(__file__)),
        },
        "build_meta": build_meta,
        "claim_status": claim_status,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC LITERALS: cross-validated policies use seed/support literal predicates only; no expected secret, recovered label, or line value is used at test time.",
            "MODEL-BOUND: charged cost is reconstructed from P826 fixed cost plus row-level online additions and scoring-field accounting.",
            "ORACLE CEILING: same-population literal ranking is reported separately and cannot be promoted as public validation.",
            "NO DEPLOYED-CURVE CLAIM: this is not a faster-than-rho ECDLP algorithm.",
        ],
        "method": "p830_shared_pilot_compression_audit",
        "parameters": {
            "fixed_cost": fixed,
            "min_literal_rows": int(args.min_literal_rows),
            "top_ks": top_ks,
        },
        "row_population": {
            "category_totals": category_totals,
            "full_p826_reconstructed_charge_model": full_model,
        },
        "schema": SCHEMA,
        "shared_pilot_compression": {
            "best_oracle_ceiling": best_oracle,
            "best_public_loo": best_public,
            "oracle_ceiling_results": oracle_results,
            "public_loo_results": public_results,
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compression = payload["shared_pilot_compression"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "shared_pilot_compression": {
            "best_oracle_ceiling": compression["best_oracle_ceiling"],
            "best_public_loo": compression["best_public_loo"],
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
    parser.add_argument("--top-ks", default="1,2,4,8,16")
    parser.add_argument("--min-literal-rows", type=int, default=16)
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
                "best_oracle_ceiling": summary["shared_pilot_compression"]["best_oracle_ceiling"],
                "best_public_loo": summary["shared_pilot_compression"]["best_public_loo"],
                "claim_status": summary["claim_status"],
                "full_p826_reconstructed_charge_model": summary["row_population"]["full_p826_reconstructed_charge_model"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
