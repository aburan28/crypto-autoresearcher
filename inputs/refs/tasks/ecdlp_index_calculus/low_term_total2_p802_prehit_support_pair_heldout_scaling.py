#!/usr/bin/env python3
"""P802 held-out scaling validation for the P801 pre-hit support-pair constructor."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P801_SCRIPT = TASK_DIR / "low_term_total2_p801_pre_hit_support_pair_constructor.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p802_prehit_support_pair_heldout_scaling_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p802_prehit_support_pair_heldout_scaling.md"
SCHEMA = "ecdlp.low_term_total2_p802_prehit_support_pair_heldout_scaling.v1"
DEFAULT_SUPPORT_BUDGETS = "64,128,256,512"
DEFAULT_TRIAL_BUDGETS = "64,128,256,512"
DEFAULT_CONSTRUCTOR_NAMESPACES = "prehitpair-heldout-v2,prehitpair-heldout-v3,prehitpair-heldout-v4"
POLICY_NAMES = ("requested_support_prehit", "rotated_support_prehit", "all_pair_first_hit_control")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def seed_labels(count: int) -> list[str]:
    return [f"t{index:04d}" for index in range(int(count))]


def clone_row_for_trial(row: dict[str, Any], trial_budget: int) -> dict[str, Any]:
    copied = {**row}
    copied["configured_trials"] = int(trial_budget)
    return copied


def scan_seed_grid(
    p801: Any,
    p746: Any,
    p748: Any,
    verifier: Any,
    challenge: dict[str, Any],
    secret: int,
    base: Any,
    public: Any,
    ainvs: list[int],
    p: int,
    order: int,
    target: str,
    factor_base_size: int,
    seed_label: str,
    full_seed: str,
    support_budgets: list[int],
    trial_budgets: list[int],
    point_policy: dict[Any, dict[tuple[int, str], tuple[int, int]]],
    support_policy_stats: dict[tuple[int, str], dict[str, int]],
    args: argparse.Namespace,
) -> dict[tuple[int, int, str], dict[str, Any]]:
    max_trial = max(int(value) for value in trial_budgets)
    walk = p746.walk_schedule(verifier, str(args.walk_mode), base, public, ainvs, p)
    a, b = p746.deterministic_start(int(order), full_seed, str(args.walk_mode))
    lhs = verifier.add_points(verifier.mul_point(a, base, ainvs, p), verifier.mul_point(b, public, ainvs, p), ainvs, p)
    hits: dict[tuple[int, str], dict[str, Any]] = {}
    zero_b_hits = Counter()

    for trial in range(1, max_trial + 1):
        entries = point_policy.get(lhs) or {}
        if entries:
            for support_key, support in entries.items():
                if support_key in hits:
                    continue
                if b % int(order) == 0:
                    zero_b_hits[support_key] += 1
                    continue
                relation = {"a": int(a), "b": int(b), "indices": [int(support[0]), int(support[1])]}
                terms = verifier.relation_terms(relation, challenge, ainvs, p)
                if terms is None or not verifier.verify_relation(relation, challenge, ainvs, p, base, public):
                    continue
                setup = int(support_policy_stats[support_key]["targeted_setup_group_additions"])
                hits[support_key] = p801.hit_row(
                    p748,
                    verifier,
                    target,
                    seed_label,
                    full_seed,
                    challenge,
                    secret,
                    order,
                    factor_base_size,
                    walk,
                    max_trial,
                    trial,
                    setup,
                    relation,
                    terms,
                )
        if len(hits) == len(support_policy_stats) or trial == max_trial:
            break
        delta = p746.select_delta(walk, full_seed, trial, a, b)
        a = (a + int(delta["da"])) % int(order)
        b = (b + int(delta["db"])) % int(order)
        lhs = verifier.add_points(lhs, delta["delta"], ainvs, p)

    rows = {}
    for support_budget in support_budgets:
        for policy_name in POLICY_NAMES:
            support_key = (int(support_budget), policy_name)
            stats = support_policy_stats[support_key]
            hit = hits.get(support_key)
            for trial_budget in trial_budgets:
                if hit is not None and int(hit["scanned_trials"]) <= int(trial_budget):
                    row = clone_row_for_trial(hit, int(trial_budget))
                else:
                    row = p801.base_row(
                        p748,
                        target,
                        seed_label,
                        full_seed,
                        challenge,
                        secret,
                        order,
                        factor_base_size,
                        walk,
                        int(trial_budget),
                        int(trial_budget),
                        int(stats["targeted_setup_group_additions"]),
                    )
                row["_p802_policy"] = {
                    "policy": policy_name,
                    "support_budget": int(support_budget),
                    "targeted_support_count": int(stats["targeted_support_count"]),
                    "targeted_unique_point_count": int(stats["targeted_unique_point_count"]),
                    "trial_budget": int(trial_budget),
                }
                row["zero_b_hits"] = int(zero_b_hits.get(support_key) or 0)
                row["zero_b_skips"] = int(zero_b_hits.get(support_key) or 0)
                rows[(int(support_budget), int(trial_budget), policy_name)] = row
    return rows


def collect_namespace_rows(
    p801: Any,
    p746: Any,
    p748: Any,
    relprobe: Any,
    base_item: dict[str, Any],
    trained_by_support_budget: dict[int, dict[tuple[int, int, int, int], dict[str, Any]]],
    support_budgets: list[int],
    trial_budgets: list[int],
    case: dict[str, Any],
    namespace: str,
    args: argparse.Namespace,
) -> tuple[dict[tuple[int, int, str], list[dict[str, Any]]], dict[tuple[int, str], dict[str, int]], int]:
    verifier, record, inv = p746.load_target(relprobe, str(base_item["target"]))
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    factor_base_size = int(case["factor_base_size"])
    sample_seed = (
        f"ecdlp-p802-{namespace}-{slug(base_item['target'])}:sample:"
        f"fb{factor_base_size}:w2:{args.walk_mode}"
    )
    sample_challenge, _sample_secret = relprobe.make_challenge(verifier, inv, ainvs, sample_seed, factor_base_size)
    factor_base = [
        verifier.point_from_json(point)
        for point in sample_challenge["factor_base"][: max(1, min(factor_base_size, len(sample_challenge["factor_base"])))]
    ]
    supports_by_policy = p801.policy_support_sets(trained_by_support_budget, support_budgets, len(factor_base))
    point_policy, support_policy_stats = p801.build_point_policy_map(verifier, factor_base, ainvs, p, supports_by_policy)
    rows_by_grid = {
        (int(support_budget), int(trial_budget), policy_name): []
        for support_budget in support_budgets
        for trial_budget in trial_budgets
        for policy_name in POLICY_NAMES
    }
    for seed_label in seed_labels(int(args.scan_seed_count)):
        full_seed = (
            f"ecdlp-p802-{namespace}-{slug(base_item['target'])}:"
            f"{seed_label}:fb{factor_base_size}:w2:{args.walk_mode}"
        )
        challenge, secret = relprobe.make_challenge(verifier, inv, ainvs, full_seed, factor_base_size)
        base = verifier.point_from_json(challenge["base"])
        public = verifier.point_from_json(challenge["public"])
        rows = scan_seed_grid(
            p801,
            p746,
            p748,
            verifier,
            challenge,
            secret,
            base,
            public,
            ainvs,
            p,
            order,
            str(base_item["target"]),
            len(factor_base),
            seed_label,
            full_seed,
            support_budgets,
            trial_budgets,
            point_policy,
            support_policy_stats,
            args,
        )
        for grid_key, row in rows.items():
            rows_by_grid[grid_key].append(row)
    return rows_by_grid, support_policy_stats, order


def aggregate_grid_results(p801: Any, items: list[dict[str, Any]], policy_name: str) -> dict[str, Any]:
    result = p801.aggregate_policy_results(items, policy_name)
    return result


def determine_grid_claim(result: dict[str, Any], peers: dict[str, dict[str, Any]]) -> str:
    aggregate = result["aggregate"]
    name = result["policy"]["name"]
    if int(aggregate["hit_row_count"]) == 0:
        return "no_targeted_hits"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9
    rotated = int((peers.get("rotated_support_prehit") or {}).get("aggregate", {}).get("recovered_row_count") or 0)
    all_pair = int((peers.get("all_pair_first_hit_control") or {}).get("aggregate", {}).get("recovered_row_count") or 0)
    peer_max = max(rotated, all_pair)
    if name == "requested_support_prehit" and int(aggregate["recovered_row_count"]) > peer_max and ratio_value < 1.0:
        return "requested_support_heldout_below_rho"
    if name == "requested_support_prehit" and int(aggregate["recovered_row_count"]) > peer_max:
        return "requested_support_heldout_enrichment_cost_boundary"
    if name in {"rotated_support_prehit", "all_pair_first_hit_control"}:
        return "control_boundary"
    return "cost_boundary"


def best_result(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    viable = [
        item
        for item in items
        if item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if not viable:
        return None
    item = min(viable, key=lambda row: row["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"])
    aggregate = item["aggregate"]
    return {
        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate["generated_once_train_total_unit_cost_over_recovered_rho"],
        "generated_row_count": aggregate["generated_row_count"],
        "hit_row_count": aggregate["hit_row_count"],
        "hit_row_rate_over_generated": aggregate["hit_row_rate_over_generated"],
        "policy": item["policy"]["name"],
        "policy_claim": item["policy_claim"],
        "recovered_row_count": aggregate["recovered_row_count"],
        "support_budget": item["support_budget"],
        "targeted_support_count": aggregate["targeted_support_count"],
        "trial_budget": item["trial_budget"],
    }


def requested_monotonicity(grid_results: list[dict[str, Any]]) -> dict[str, Any]:
    requested = [item for item in grid_results if item["policy"]["name"] == "requested_support_prehit"]
    by_trial: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_support: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in requested:
        by_trial[int(item["trial_budget"])].append(item)
        by_support[int(item["support_budget"])].append(item)

    def nondecreasing(values: list[int]) -> bool:
        return all(values[index] <= values[index + 1] for index in range(len(values) - 1))

    support_checks = []
    for trial_budget, rows in sorted(by_trial.items()):
        ordered = sorted(rows, key=lambda item: int(item["support_budget"]))
        support_checks.append(
            {
                "axis": "support_budget",
                "fixed_trial_budget": trial_budget,
                "nondecreasing_recovered": nondecreasing([int(item["aggregate"]["recovered_row_count"]) for item in ordered]),
                "values": [
                    {
                        "recovered": int(item["aggregate"]["recovered_row_count"]),
                        "support_budget": int(item["support_budget"]),
                    }
                    for item in ordered
                ],
            }
        )
    trial_checks = []
    for support_budget, rows in sorted(by_support.items()):
        ordered = sorted(rows, key=lambda item: int(item["trial_budget"]))
        trial_checks.append(
            {
                "axis": "trial_budget",
                "fixed_support_budget": support_budget,
                "nondecreasing_recovered": nondecreasing([int(item["aggregate"]["recovered_row_count"]) for item in ordered]),
                "values": [
                    {
                        "recovered": int(item["aggregate"]["recovered_row_count"]),
                        "trial_budget": int(item["trial_budget"]),
                    }
                    for item in ordered
                ],
            }
        )
    return {
        "support_budget_checks": support_checks,
        "trial_budget_checks": trial_checks,
        "support_budget_nondecreasing_count": sum(1 for item in support_checks if item["nondecreasing_recovered"]),
        "trial_budget_nondecreasing_count": sum(1 for item in trial_checks if item["nondecreasing_recovered"]),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    claims = [item["policy_claim"] for item in summary["grid_results"]]
    if "requested_support_heldout_below_rho" in claims:
        return "P802_REQUESTED_SUPPORT_PREHIT_HELDOUT_BELOW_RHO_REPLICATES"
    if "requested_support_heldout_enrichment_cost_boundary" in claims:
        return "P802_REQUESTED_SUPPORT_PREHIT_HELDOUT_ENRICHMENT_BOUNDARY"
    return "NEGATIVE_RESULT_P802_PREHIT_SUPPORT_HELDOUT_NO_REPLICATION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.width) != 2:
        raise ValueError("P802 validates width-2 support pairs; use --width 2")
    p801 = load_module("ecdlp_p801_for_p802", P801_SCRIPT)
    p800 = p801.load_module("ecdlp_p800_for_p802", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p802", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p802", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p802", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p802", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p802", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p802", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p802", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p802", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p802", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p802", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p802", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p802", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p802", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p802", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p802", p782.P780_SCRIPT)
    stack = p780.load_stack()
    p746 = stack["p746"]
    p748 = stack["p748"]
    relprobe = stack["relprobe"]
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    support_budgets = csv_ints(args.support_budgets)
    trial_budgets = csv_ints(args.trial_budgets)
    namespaces = csv_strings(args.constructor_namespaces)

    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    print(f"preparing train namespace {args.train_seed_namespace}", flush=True)
    train_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], train_args)
        for key in required
    }
    trained_by_group_support = {
        group_key: {
            int(budget): p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
            for budget in support_budgets
        }
        for group_key in required
    }

    scan_bank = {}
    for namespace in namespaces:
        for group_key in required:
            case = p784.case_from_group(
                base_groups[group_key],
                p784.TRIM12_DELTA,
                namespace,
                "p802",
                p784.DEST_SEED_COUNT,
                p784.DEST_POOL_COUNT,
            )
            print(f"heldout scanning namespace={namespace} group={group_key} rows={args.scan_seed_count}", flush=True)
            rows_by_grid, support_policy_stats, order = collect_namespace_rows(
                p801,
                p746,
                p748,
                relprobe,
                base_groups[group_key],
                trained_by_group_support[group_key],
                support_budgets,
                trial_budgets,
                case,
                namespace,
                args,
            )
            scan_bank[(namespace, group_key)] = {
                "order": order,
                "rows_by_grid": rows_by_grid,
                "support_policy_stats": support_policy_stats,
            }

    grid_results = []
    for support_budget in support_budgets:
        for trial_budget in trial_budgets:
            print(f"scoring support_budget={support_budget} trial_budget={trial_budget}", flush=True)
            policy_items: dict[str, list[dict[str, Any]]] = {name: [] for name in POLICY_NAMES}
            for namespace in namespaces:
                for group_key in required:
                    bank = scan_bank[(namespace, group_key)]
                    for policy_name in POLICY_NAMES:
                        support_key = (int(support_budget), policy_name)
                        grid_key = (int(support_budget), int(trial_budget), policy_name)
                        item = p801.evaluate_policy(
                            p797,
                            p793,
                            p792,
                            p789,
                            train_prepared[group_key],
                            trained_by_group_support[group_key][int(support_budget)],
                            bank["rows_by_grid"][grid_key],
                            int(bank["order"]),
                            str(base_groups[group_key]["target"]),
                            policy_name,
                            bank["support_policy_stats"][support_key],
                            args,
                        )
                        item["namespace"] = namespace
                        item["group_key"] = group_key
                        policy_items[policy_name].append(item)
            policy_results = []
            for policy_name in POLICY_NAMES:
                policy_results.append(aggregate_grid_results(p801, policy_items[policy_name], policy_name))
            by_name = {item["policy"]["name"]: item for item in policy_results}
            for item in policy_results:
                item["support_budget"] = int(support_budget)
                item["trial_budget"] = int(trial_budget)
                item["policy_claim"] = determine_grid_claim(item, by_name)
                grid_results.append(item)

    summary = {
        "best_generated": best_result(grid_results),
        "constructor_namespaces": namespaces,
        "grid_results": grid_results,
        "monotonicity": requested_monotonicity(grid_results),
        "scan_seed_count": args.scan_seed_count,
        "support_budgets": support_budgets,
        "train_seed_namespace": args.train_seed_namespace,
        "trial_budgets": trial_budgets,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p801_script": str(P801_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "HELD-OUT NAMESPACE MODEL: constructor challenge seeds differ from P801 and are not used for training.",
            "CONSERVATIVE SETUP: support point-sum setup is charged per target/namespace aggregate item.",
            "CONTROL-BOUND: rotated support-pair tables and all-pair first-hit tables test whether requested supports add value beyond table size and generic two-factor hits.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p802_prehit_support_pair_heldout_scaling",
        "parameters": {
            "constructor_namespaces": namespaces,
            "control_count": args.control_count,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "row_policy": args.row_policy,
            "scan_seed_count": args.scan_seed_count,
            "sparse_policies": args.sparse_policies,
            "support_budgets": support_budgets,
            "train_replicas": args.train_replicas,
            "train_seed_namespace": args.train_seed_namespace,
            "trial_budgets": trial_budgets,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def compact_grid_result(item: dict[str, Any]) -> dict[str, Any]:
    aggregate = item["aggregate"]
    return {
        "aggregate": {
            "generated_once_train_total_unit_cost_over_recovered_rho": aggregate[
                "generated_once_train_total_unit_cost_over_recovered_rho"
            ],
            "generated_row_count": aggregate["generated_row_count"],
            "hit_row_count": aggregate["hit_row_count"],
            "hit_row_rate_over_generated": aggregate["hit_row_rate_over_generated"],
            "max_control_recovered_row_count": aggregate["max_control_recovered_row_count"],
            "primary_minus_max_control_recovered_rows": aggregate["primary_minus_max_control_recovered_rows"],
            "recovered_row_count": aggregate["recovered_row_count"],
            "recovered_row_rate_over_hit": aggregate["recovered_row_rate_over_hit"],
            "targeted_setup_group_additions": aggregate["targeted_setup_group_additions"],
            "targeted_support_count": aggregate["targeted_support_count"],
            "targeted_unique_point_count": aggregate["targeted_unique_point_count"],
        },
        "policy": item["policy"],
        "policy_claim": item["policy_claim"],
        "support_budget": item["support_budget"],
        "trial_budget": item["trial_budget"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact = {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "grid_results": [compact_grid_result(item) for item in payload["summary"]["grid_results"]],
        },
    }
    return compact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default=DEFAULT_CONSTRUCTOR_NAMESPACES)
    parser.add_argument("--support-budgets", default=DEFAULT_SUPPORT_BUDGETS)
    parser.add_argument("--trial-budgets", default=DEFAULT_TRIAL_BUDGETS)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--control-count", type=int, default=8)
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
                "best_generated": summary["summary"]["best_generated"],
                "claim_status": summary["claim_status"],
                "monotonicity": summary["summary"]["monotonicity"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
