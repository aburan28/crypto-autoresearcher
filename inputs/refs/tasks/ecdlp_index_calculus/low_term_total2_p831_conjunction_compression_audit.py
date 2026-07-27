#!/usr/bin/env python3
"""P831 public conjunction compression audit for P829 pilot-only rows."""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P830_SCRIPT = TASK_DIR / "low_term_total2_p830_shared_pilot_compression_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p831_conjunction_compression_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p831_conjunction_compression_audit.md"
SCHEMA = "ecdlp.low_term_total2_p831_conjunction_compression_audit.v1"


def load_p830() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p830_for_p831", P830_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P830 helpers from {P830_SCRIPT}")
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


def row_uid(row: dict[str, Any]) -> str:
    return f"{row['context_id']}::{row['row_key']}"


def conjunction_name(pair: tuple[str, str]) -> str:
    return f"{pair[0]} && {pair[1]}"


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


def conjunction_stats(rows: list[dict[str, Any]], min_rows: int) -> list[dict[str, Any]]:
    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for pair in itertools.combinations(sorted(set(row["tags"])), 2):
            by_pair[pair].append(row)
    stats = []
    for pair, selected in by_pair.items():
        if len(selected) < int(min_rows):
            continue
        totals = row_totals(selected)
        if int(totals["recovered_row_count"]) <= 0:
            continue
        stats.append(
            {
                "conjunction": list(pair),
                "name": conjunction_name(pair),
                "recovered_rho_per_online": ratio(totals["recovered_rho_baseline"], totals["online_group_additions"]),
                "recovered_row_rate": ratio(totals["recovered_row_count"], totals["row_count"]),
                **totals,
            }
        )
    stats.sort(
        key=lambda item: (
            float(item["recovered_rho_per_online"] or 0.0),
            float(item["recovered_row_rate"] or 0.0),
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
    selected = {}
    for pair in pairs:
        for row in rows_matching_conjunction(rows, pair):
            selected[row_uid(row)] = row
    return list(selected.values())


def greedy_conjunctions(rows: list[dict[str, Any]], max_k: int, min_rows: int) -> list[dict[str, Any]]:
    candidates = conjunction_stats(rows, int(min_rows))
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
            if len(add_uids) < int(min_rows):
                continue
            added_rows = [by_uid[uid] for uid in add_uids]
            added_totals = row_totals(added_rows)
            if int(added_totals["recovered_row_count"]) <= 0:
                continue
            score = (
                float(ratio(added_totals["recovered_rho_baseline"], added_totals["online_group_additions"]) or 0.0),
                float(ratio(added_totals["recovered_row_count"], added_totals["row_count"]) or 0.0),
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
                        "recovered_rho_per_online": ratio(
                            added_totals["recovered_rho_baseline"],
                            added_totals["online_group_additions"],
                        ),
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
                "selected_increment": best["selected_increment"],
            }
        )
    return chosen


def evaluate_cross_validated(
    p830: Any,
    rows: list[dict[str, Any]],
    fixed_cost: int,
    field_weight: int,
    top_ks: list[int],
    min_rows: int,
) -> list[dict[str, Any]]:
    namespaces = sorted({row["base_namespace"] for row in rows})
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    max_k = max(top_ks)
    selected_by_k: dict[int, dict[str, dict[str, Any]]] = {int(k): {} for k in top_ks}
    diagnostics: dict[int, list[dict[str, Any]]] = {int(k): [] for k in top_ks}
    for namespace in namespaces:
        train = [row for row in pilot_rows if row["base_namespace"] != namespace]
        test = [row for row in pilot_rows if row["base_namespace"] == namespace]
        ranked = greedy_conjunctions(train, max_k, min_rows)
        for k in top_ks:
            chosen = [tuple(item["conjunction"]) for item in ranked[: int(k)]]
            selected = select_by_conjunctions(test, chosen)
            for row in selected:
                selected_by_k[int(k)][row_uid(row)] = row
            diagnostics[int(k)].append(
                {
                    "heldout_namespace": namespace,
                    "selected_conjunctions": [conjunction_name(pair) for pair in chosen],
                    "selected_row_count": len(selected),
                    "test_pilot_rows": len(test),
                    "test_recovered_rows": sum(1 for row in test if row["recovered"]),
                    "test_selected_recovered_rows": sum(1 for row in selected if row["recovered"]),
                }
            )
    pilot_totals_full = p830.row_totals(pilot_rows)
    results = []
    for k in top_ks:
        selected = list(selected_by_k[int(k)].values())
        selected_totals = p830.row_totals(selected)
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
                    "kind": "loo_public_two_literal_conjunction_union",
                    "top_k": int(k),
                },
                "selected_pilot_only": selected_totals,
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


def evaluate_oracle_upper(
    p830: Any,
    rows: list[dict[str, Any]],
    fixed_cost: int,
    field_weight: int,
    top_ks: list[int],
    min_rows: int,
) -> list[dict[str, Any]]:
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    max_k = max(top_ks)
    ranked = greedy_conjunctions(pilot_rows, max_k, min_rows)
    pilot_totals_full = p830.row_totals(pilot_rows)
    results = []
    for k in top_ks:
        chosen = [tuple(item["conjunction"]) for item in ranked[: int(k)]]
        selected = select_by_conjunctions(pilot_rows, chosen)
        selected_totals = p830.row_totals(selected)
        results.append(
            {
                "charge_model": p830.charged_model(selected, base_rows, fixed_cost, field_weight),
                "pilot_only_compression": ratio(
                    selected_totals["online_group_additions"],
                    pilot_totals_full["online_group_additions"],
                ),
                "pilot_only_recovered_preservation": ratio(
                    selected_totals["recovered_row_count"],
                    pilot_totals_full["recovered_row_count"],
                ),
                "policy": {
                    "kind": "oracle_same_population_two_literal_conjunction_union",
                    "selected_conjunctions": [conjunction_name(pair) for pair in chosen],
                    "top_k": int(k),
                },
                "selected_pilot_only": selected_totals,
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
        return "P831_PUBLIC_CONJUNCTION_COMPRESSION_BELOW_RHO"
    if public_ratio < full_ratio:
        return "P831_PUBLIC_CONJUNCTION_COMPRESSION_IMPROVES_P826"
    if oracle_ratio < full_ratio:
        return "P831_ORACLE_CONJUNCTION_CEILING_ONLY"
    return "NEGATIVE_RESULT_P831_CONJUNCTION_COMPRESSION_DOES_NOT_IMPROVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p830 = load_p830()
    rows, build_meta = p830.build_rows(args)
    fixed = p830.find_p826_fixed_cost(args.p826_probe, int(args.field_weight))
    top_ks = csv_ints(args.top_ks)
    category_totals = p830.totals_by_category(rows)
    pilot_rows = [row for row in rows if row["category"] == "pilot_only"]
    base_rows = [row for row in rows if row["category"] != "pilot_only"]
    full_model = p830.charged_model(pilot_rows, base_rows, fixed["fixed_cost"], int(args.field_weight))
    public_results = evaluate_cross_validated(
        p830,
        rows,
        fixed["fixed_cost"],
        int(args.field_weight),
        top_ks,
        int(args.min_conjunction_rows),
    )
    oracle_results = evaluate_oracle_upper(
        p830,
        rows,
        fixed["fixed_cost"],
        int(args.field_weight),
        top_ks,
        int(args.min_conjunction_rows),
    )
    best_public = public_results[0] if public_results else None
    best_oracle = oracle_results[0] if oracle_results else None
    claim_status = determine_claim(full_model, best_public, best_oracle)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "p830_script": str(P830_SCRIPT),
            "script": str(Path(__file__)),
        },
        "build_meta": build_meta,
        "claim_status": claim_status,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC CONJUNCTIONS: leave-one-namespace policies use only public seed/support tags at test time.",
            "MODEL-BOUND: charged cost is reconstructed from P826 fixed cost plus row-level online additions and scoring-field accounting.",
            "ORACLE CEILING: same-population conjunction ranking is reported separately and cannot be promoted as public validation.",
            "NO DEPLOYED-CURVE CLAIM: this is not a faster-than-rho ECDLP algorithm.",
        ],
        "method": "p831_conjunction_compression_audit",
        "parameters": {
            "fixed_cost": fixed,
            "min_conjunction_rows": int(args.min_conjunction_rows),
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
    parser.add_argument("--top-ks", default="1,2,4,8,16,32")
    parser.add_argument("--min-conjunction-rows", type=int, default=8)
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
