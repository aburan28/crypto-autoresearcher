#!/usr/bin/env python3
"""P839 replication audit for P838 support-forcing prefix signals."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P838_SCRIPT = TASK_DIR / "low_term_total2_p838_support_forcing_seed_material_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p839_support_forcing_replication_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p839_support_forcing_replication_audit.md"
SCHEMA = "ecdlp.low_term_total2_p839_support_forcing_replication_audit.v1"


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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def csv_strings(raw: str) -> list[str]:
    return [part.strip() for part in str(raw).split(",") if part.strip()]


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def p838_args(args: argparse.Namespace, generator_namespace: str) -> argparse.Namespace:
    return argparse.Namespace(
        budgets=args.budgets,
        control_count=args.control_count,
        encodings=args.encodings,
        field_weight=args.field_weight,
        generator_namespace=generator_namespace,
        max_items_per_target=args.max_items_per_target,
        max_relations=args.max_relations,
        max_schedules=args.max_schedules,
        max_subsets=args.max_subsets,
        min_line_rows=args.min_line_rows,
        out=None,
        p777_summary=args.p777_summary,
        p786_summary=args.p786_summary,
        p837_summary=args.p837_summary,
        row_policy=args.row_policy,
        seeds_per_prefix=args.seeds_per_prefix,
        sparse_policies=args.sparse_policies,
        summary_out=None,
        train_replicas=args.train_replicas,
        train_seed_namespace=args.train_seed_namespace,
        walk_mode=args.walk_mode,
        width=args.width,
    )


def policy_by_name(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["policy"]["name"]: item for item in result["policy_results"]}


def target_breakdown(policy: dict[str, Any], support_meta: list[dict[str, Any]]) -> list[dict[str, Any]]:
    breakdown = []
    for meta, target_result in zip(support_meta, policy.get("target_results") or []):
        aggregate = target_result["aggregate"]
        breakdown.append(
            {
                "generated_rows": int(aggregate["generated_row_count"]),
                "group_key": meta["group_key"],
                "intended_support_hits": int(aggregate["intended_support_hit_row_count"]),
                "recovered_rows": int(aggregate["recovered_row_count"]),
                "selected_support_hits": int(aggregate["selected_support_hit_row_count"]),
            }
        )
    return breakdown


def compact_policy(policy: dict[str, Any], support_meta: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = policy["aggregate"]
    keep = [
        "generated_once_train_total_unit_cost",
        "generated_once_train_total_unit_cost_over_recovered_rho",
        "generated_online_group_additions",
        "generated_row_count",
        "generated_row_rho_baseline",
        "intended_support_hit_rate",
        "intended_support_hit_row_count",
        "primary_minus_max_control_recovered_rows",
        "recovered_rho_baseline",
        "recovered_row_count",
        "selected_support_hit_rate",
        "selected_support_hit_row_count",
    ]
    return {
        "aggregate": {key: aggregate.get(key) for key in keep},
        "policy": policy["policy"],
        "policy_claim": policy.get("policy_claim"),
        "target_breakdown": target_breakdown(policy, support_meta),
    }


def case_summary(round_index: int, result: dict[str, Any]) -> dict[str, Any]:
    policies = policy_by_name(result)
    schedule = policies["schedule"]
    neutral = policies["neutral"]
    rotated = policies["rotated"]
    schedule_agg = schedule["aggregate"]
    neutral_agg = neutral["aggregate"]
    rotated_agg = rotated["aggregate"]
    max_control_intended = max(
        int(neutral_agg["intended_support_hit_row_count"]),
        int(rotated_agg["intended_support_hit_row_count"]),
    )
    max_control_recovered = max(
        int(neutral_agg["recovered_row_count"]),
        int(rotated_agg["recovered_row_count"]),
    )
    intended_lift = int(schedule_agg["intended_support_hit_row_count"]) - max_control_intended
    recovered_margin = int(schedule_agg["recovered_row_count"]) - max_control_recovered
    strict_pass = intended_lift > 0 and recovered_margin >= 0
    support_meta = result.get("support_meta") or []
    return {
        "budget": int(result["budget"]),
        "control_intended_hit_count": max_control_intended,
        "control_recovered_row_count": max_control_recovered,
        "encoding": result["encoding"],
        "intended_lift": intended_lift,
        "policies": {
            name: compact_policy(policy, support_meta)
            for name, policy in sorted(policies.items())
        },
        "recovered_margin": recovered_margin,
        "round_index": int(round_index),
        "schedule_intended_hit_count": int(schedule_agg["intended_support_hit_row_count"]),
        "schedule_name": result["schedule_name"],
        "schedule_recovered_row_count": int(schedule_agg["recovered_row_count"]),
        "source_name": result["source_name"],
        "strict_support_forcing_pass": strict_pass,
    }


def round_summary(round_index: int, generator_namespace: str, payload: dict[str, Any]) -> dict[str, Any]:
    cases = [
        case_summary(round_index, result)
        for result in payload["support_forcing"]["schedule_results"]
    ]
    return {
        "cases": cases,
        "claim_status": payload["claim_status"],
        "generator_namespace": generator_namespace,
        "round_index": int(round_index),
    }


def summarize_replication(
    round_summaries: list[dict[str, Any]],
    min_passes_per_case: int,
    min_stable_schedule_blocks: int,
) -> dict[str, Any]:
    by_case: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for round_item in round_summaries:
        for case in round_item["cases"]:
            by_case[(case["schedule_name"], case["encoding"])].append(case)

    case_summaries = []
    for (schedule_name, encoding), cases in sorted(by_case.items()):
        pass_count = sum(1 for case in cases if case["strict_support_forcing_pass"])
        total_schedule_hits = sum(int(case["schedule_intended_hit_count"]) for case in cases)
        total_control_hits = sum(int(case["control_intended_hit_count"]) for case in cases)
        total_generated_rows = sum(
            int(case["policies"]["schedule"]["aggregate"]["generated_row_count"])
            for case in cases
        )
        case_summaries.append(
            {
                "control_intended_hit_count": total_control_hits,
                "encoding": encoding,
                "pass_count": pass_count,
                "recovered_margin_min": min(int(case["recovered_margin"]) for case in cases),
                "round_count": len(cases),
                "schedule_intended_hit_count": total_schedule_hits,
                "schedule_intended_hit_rate": ratio(total_schedule_hits, total_generated_rows),
                "schedule_name": schedule_name,
                "stable_case": pass_count >= int(min_passes_per_case),
            }
        )

    encoding_summaries = []
    by_encoding: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in case_summaries:
        by_encoding[item["encoding"]].append(item)
    for encoding, items in sorted(by_encoding.items()):
        stable_blocks = sum(1 for item in items if item["stable_case"])
        pass_count = sum(int(item["pass_count"]) for item in items)
        encoding_summaries.append(
            {
                "encoding": encoding,
                "pass_count": pass_count,
                "stable_case_count": stable_blocks,
                "stable_encoding_family": stable_blocks >= int(min_stable_schedule_blocks),
                "total_case_count": len(items),
                "total_control_intended_hit_count": sum(int(item["control_intended_hit_count"]) for item in items),
                "total_schedule_intended_hit_count": sum(int(item["schedule_intended_hit_count"]) for item in items),
            }
        )

    stable_families = [item for item in encoding_summaries if item["stable_encoding_family"]]
    stable_cases = [item for item in case_summaries if item["stable_case"]]
    any_single_pass = any(int(item["pass_count"]) > 0 for item in case_summaries)
    any_recovery_margin = any(
        int(case["recovered_margin"]) > 0
        for round_item in round_summaries
        for case in round_item["cases"]
    )
    if stable_families:
        claim_status = "P839_REPLICATED_ENCODING_FAMILY_SUPPORT_SIGNAL"
    elif stable_cases:
        claim_status = "P839_SCHEDULE_LOCAL_REPLICATION_ONLY"
    elif any_single_pass:
        claim_status = "P839_UNSTABLE_SINGLE_ROUND_SUPPORT_SIGNAL"
    elif any_recovery_margin:
        claim_status = "P839_RECOVERY_ENRICHMENT_WITHOUT_REPLICATED_SUPPORT"
    else:
        claim_status = "NEGATIVE_RESULT_P839_NO_REPLICATED_SUPPORT_FORCING"

    return {
        "case_summaries": case_summaries,
        "claim_status": claim_status,
        "encoding_summaries": encoding_summaries,
        "min_passes_per_case": int(min_passes_per_case),
        "min_stable_schedule_blocks": int(min_stable_schedule_blocks),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p838 = load_module("ecdlp_p838_for_p839", P838_SCRIPT)
    round_payloads = []
    round_summaries = []
    for round_index in range(int(args.replications)):
        generator_namespace = f"{args.generator_namespace}-r{round_index:02d}"
        print(f"running replication {round_index + 1}/{args.replications} namespace={generator_namespace}", flush=True)
        round_payload = p838.analyze(p838_args(args, generator_namespace))
        round_payloads.append(round_payload)
        round_summaries.append(round_summary(round_index, generator_namespace, round_payload))

    replication = summarize_replication(
        round_summaries,
        int(args.min_passes_per_case),
        int(args.min_stable_schedule_blocks),
    )
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p838_script": str(P838_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": replication["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "REPLICATION AUDIT: P839 grades stability across generator namespaces and schedule blocks.",
            "ENCODING-FAMILY RULE: promotion requires the same encoding family to be stable on multiple schedule blocks.",
            "CONTROL-BOUND: each passing case must beat neutral and rotated controls on intended-support hits while preserving recovered-row count.",
            "POLLARD-RHO BOUNDARY: this tests a relation-generation subproblem and is not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p839_support_forcing_replication_audit",
        "parameters": {
            "budgets": args.budgets,
            "encodings": csv_strings(args.encodings),
            "generator_namespace": args.generator_namespace,
            "max_items_per_target": int(args.max_items_per_target),
            "max_schedules": int(args.max_schedules),
            "min_passes_per_case": int(args.min_passes_per_case),
            "min_stable_schedule_blocks": int(args.min_stable_schedule_blocks),
            "replications": int(args.replications),
            "seeds_per_prefix": int(args.seeds_per_prefix),
            "train_seed_namespace": args.train_seed_namespace,
        },
        "red_team_handoff": {
            "assumptions": [
                "Independent generator namespaces are a useful first proxy for seed-material stability.",
                "The same encoding family should replicate across schedule blocks before promotion.",
                "Neutral and rotated controls bound generic prefix correlation at this toy scale.",
            ],
            "failure_modes": [
                "A stable prefix encoding may still exploit generator quirks rather than algebraic support construction.",
                "A negative result at three namespaces may miss a rarer encoding family.",
                "Recovered-row enrichment can remain useful even when exact intended support does not replicate.",
            ],
            "next_concrete_action": (
                "If no encoding-family signal replicates, switch from prefix encoding to explicit public slice/pair predictors; "
                "if one does replicate, integrate its measured rate into the P836/P826 residual-gap model."
            ),
        },
        "replication": {
            **replication,
            "rounds": round_summaries,
        },
        "round_payloads": round_payloads,
        "schema": SCHEMA,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **{key: value for key, value in payload.items() if key != "round_payloads"},
        "schema": f"{SCHEMA}.summary",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json")
    parser.add_argument("--p786-summary", type=Path, default=STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json")
    parser.add_argument("--p837-summary", type=Path, default=STATE_DIR / "low_term_total2_p837_schedule_direct_constructor_audit_summary.json")
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--generator-namespace", default="p839-support-replication-v1")
    parser.add_argument("--replications", type=int, default=3)
    parser.add_argument("--min-passes-per-case", type=int, default=2)
    parser.add_argument("--min-stable-schedule-blocks", type=int, default=2)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--budgets", default="128")
    parser.add_argument("--encodings", default="repeat,mods")
    parser.add_argument("--max-items-per-target", type=int, default=12)
    parser.add_argument("--max-schedules", type=int, default=2)
    parser.add_argument("--seeds-per-prefix", type=int, default=3)
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
                "case_summaries": summary["replication"]["case_summaries"],
                "claim_status": summary["claim_status"],
                "encoding_summaries": summary["replication"]["encoding_summaries"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
