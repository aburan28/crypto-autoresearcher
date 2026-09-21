#!/usr/bin/env python3
"""P828 prefix-span generator and amortization audit for P826/P827."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P827_SCRIPT = TASK_DIR / "low_term_total2_p827_cost_descent_sensitivity_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P826_PROBE = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p828_span_top_generator_amortization_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p828_span_top_generator_amortization_audit.md"
SCHEMA = "ecdlp.low_term_total2_p828_span_top_generator_amortization_audit.v1"

FROZEN_PUBLIC_POLICY_NAME = "shared_core_score_hash_membership_rows_equal_remaining_p16"
DIRECT_SPAN_POLICY_NAME = "equal_prefix_span_top"
DEFAULT_RELATION_SPEEDUPS = (1, 2, 4, 8, 16, 32, 64)
DEFAULT_AMORTIZATION_FACTORS = (1, 2, 4, 8, 16, 32, 64)


def load_p827() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p827_for_p828", P827_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P827 helpers from {P827_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def csv_ints(raw: str) -> list[int]:
    return [int(part.strip()) for part in str(raw).split(",") if part.strip()]


def retotal_breakdown(
    base: dict[str, Any],
    *,
    relation_online_generation: int,
    label: str,
    model_boundary: str,
) -> dict[str, Any]:
    components = dict(base["components"])
    components["relation_online_generation"] = int(relation_online_generation)
    fixed = float(base["target_once_fixed_cost"])
    scoring = float(components["scoring_field_weighted"])
    relation_variable = float(relation_online_generation) + scoring
    total = fixed + relation_variable
    rho = int(base["recovered_rho_baseline"])
    return {
        "component_share_of_total": {key: ratio(value, total) for key, value in components.items()},
        "components": components,
        "current_cost_over_rho": ratio(total, rho),
        "field_weight_inferred": base["field_weight_inferred"],
        "label": label,
        "model_boundary": model_boundary,
        "post_hit_total_cost": round(total, 8),
        "recovered_rho_baseline": rho,
        "relation_variable_cost": round(relation_variable, 8),
        "target_once_fixed_cost": round(fixed, 8),
    }


def context_amplification(item: dict[str, Any]) -> dict[str, Any]:
    contexts = []
    recovered_total = 0
    covered_total = 0
    for context in item.get("context_results") or []:
        recovered = int(context.get("recovered_row_count") or 0)
        covered = int(context.get("covered_target_count") or 0)
        recovered_total += recovered
        covered_total += covered
        contexts.append(
            {
                "context_id": context.get("context_id"),
                "covered_target_count": covered,
                "coverage_per_recovered_row": ratio(covered, recovered),
                "recovered_row_count": recovered,
                "target": context.get("target"),
            }
        )
    return {
        "aggregate_coverage_per_recovered_row": ratio(covered_total, recovered_total),
        "boundary": (
            "This measures only currently scored row/coverage multiplicity. It is not a target-descent algorithm "
            "and does not count new individual-log descent relations."
        ),
        "context_results": contexts,
        "covered_target_count": covered_total,
        "recovered_row_count": recovered_total,
    }


def first_crossing(thresholds: dict[str, Any]) -> dict[str, Any] | None:
    return thresholds.get("best_grid_crossing_without_target_descent")


def determine_claim(
    direct_span: dict[str, Any],
    frozen: dict[str, Any],
    no_rescan: dict[str, Any],
    no_rescan_thresholds: dict[str, Any],
) -> str:
    direct_ratio = direct_span["current_cost_over_rho"] or 10**9
    frozen_ratio = frozen["current_cost_over_rho"] or 10**9
    no_rescan_ratio = no_rescan["current_cost_over_rho"] or 10**9
    if direct_ratio < 1.0:
        return "P828_DIRECT_SPAN_TOP_GENERATOR_BELOW_RHO"
    if direct_ratio < frozen_ratio:
        return "P828_DIRECT_SPAN_TOP_GENERATOR_IMPROVES_P826"
    if no_rescan_ratio < frozen_ratio and first_crossing(no_rescan_thresholds) is not None:
        return "P828_NO_RESCAN_NARROWS_COST_FRONTIER_BUT_DIRECT_SPAN_GENERATOR_FAILS"
    return "NEGATIVE_RESULT_P828_SPAN_TOP_GENERATOR_DOES_NOT_MOVE_FRONTIER"


def compact_scenario(breakdown: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    return {
        "breakdown": {
            "current_cost_over_rho": breakdown["current_cost_over_rho"],
            "post_hit_total_cost": breakdown["post_hit_total_cost"],
            "recovered_rho_baseline": breakdown["recovered_rho_baseline"],
            "relation_variable_cost": breakdown["relation_variable_cost"],
            "target_once_fixed_cost": breakdown["target_once_fixed_cost"],
        },
        "first_no_descent_crossing": first_crossing(thresholds),
        "speedup_required_by_amortization": thresholds["speedup_required_by_amortization"],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p827 = load_p827()
    p826 = load_json(args.p826_probe)
    frozen_item = p827.find_policy(p826, FROZEN_PUBLIC_POLICY_NAME)
    direct_span_item = p827.find_policy(p826, DIRECT_SPAN_POLICY_NAME)
    full_pool_item = p827.find_policy(p826, "equal_full_pool")
    if frozen_item is None:
        raise ValueError(f"missing frozen public policy {FROZEN_PUBLIC_POLICY_NAME}")
    if direct_span_item is None:
        raise ValueError(f"missing direct span policy {DIRECT_SPAN_POLICY_NAME}")

    relation_speedups = csv_ints(args.relation_speedups)
    amortization_factors = csv_ints(args.amortization_factors)

    frozen_breakdown = p827.component_breakdown(frozen_item)
    direct_span_breakdown = p827.component_breakdown(direct_span_item)
    source_split = p827.source_split(frozen_item)
    continuation_online = int(source_split["continuation_online_group_additions_sum"])
    no_rescan_breakdown = retotal_breakdown(
        frozen_breakdown,
        relation_online_generation=continuation_online,
        label="p826_same_recovery_charge_only_selected_span_continuation_online",
        model_boundary=(
            "MODEL-BOUND: preserves P826 pilot-plus-span recovered rows but removes the pilot/merge residual online "
            "cost. This is a break-even proxy for a future constructive generator, not a measured generator."
        ),
    )

    frozen_thresholds = p827.threshold_audit(frozen_breakdown, relation_speedups, amortization_factors)
    direct_span_thresholds = p827.threshold_audit(direct_span_breakdown, relation_speedups, amortization_factors)
    no_rescan_thresholds = p827.threshold_audit(no_rescan_breakdown, relation_speedups, amortization_factors)
    claim_status = determine_claim(
        direct_span_breakdown,
        frozen_breakdown,
        no_rescan_breakdown,
        no_rescan_thresholds,
    )

    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p826_probe": str(args.p826_probe),
            "p827_helper": str(P827_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generator_audit": {
            "direct_span_top_measured": {
                "amplification_probe": context_amplification(direct_span_item),
                "breakdown": direct_span_breakdown,
                "policy": p827.compact_policy(direct_span_item),
                "thresholds": direct_span_thresholds,
            },
            "frozen_p826_current": {
                "amplification_probe": context_amplification(frozen_item),
                "breakdown": frozen_breakdown,
                "policy": p827.compact_policy(frozen_item),
                "thresholds": frozen_thresholds,
            },
            "p826_no_pilot_rescan_counterfactual": {
                "breakdown": no_rescan_breakdown,
                "source_split": source_split,
                "thresholds": no_rescan_thresholds,
            },
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MEASURED DIRECT GENERATOR: equal_prefix_span_top is a direct span-top support-family scan from P826 policy results.",
            "MODEL-BOUND NO-RESCAN: the no-pilot-rescan scenario preserves P826 recovery while subtracting pilot/merge residual online cost; it is not a measured generator.",
            "TARGET-DESCENT NOT SOLVED: the amplification probe measures row/coverage multiplicity only.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p828_span_top_generator_amortization_audit",
        "parameters": {
            "amortization_factors": amortization_factors,
            "direct_span_policy_name": DIRECT_SPAN_POLICY_NAME,
            "frozen_public_policy_name": FROZEN_PUBLIC_POLICY_NAME,
            "relation_speedups": relation_speedups,
        },
        "policy_comparison": {
            "direct_span_top_measured": p827.compact_policy(direct_span_item),
            "frozen_p826_current": p827.compact_policy(frozen_item),
            "full_pool": p827.compact_policy(full_pool_item),
        },
        "schema": SCHEMA,
        "summary": {
            "direct_span_vs_p826_recovered_row_delta": int(direct_span_item["aggregate"]["recovered_row_count"])
            - int(frozen_item["aggregate"]["recovered_row_count"]),
            "direct_span_vs_p826_rho_ratio_delta": ratio(
                direct_span_breakdown["current_cost_over_rho"] - frozen_breakdown["current_cost_over_rho"],
                1,
            ),
            "p826_no_rescan_cost_over_rho": no_rescan_breakdown["current_cost_over_rho"],
            "p826_no_rescan_first_crossing": first_crossing(no_rescan_thresholds),
        },
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    audit = payload["generator_audit"]
    return {
        **payload,
        "generator_audit": {
            "direct_span_top_measured": compact_scenario(
                audit["direct_span_top_measured"]["breakdown"],
                audit["direct_span_top_measured"]["thresholds"],
            ),
            "frozen_p826_current": compact_scenario(
                audit["frozen_p826_current"]["breakdown"],
                audit["frozen_p826_current"]["thresholds"],
            ),
            "p826_no_pilot_rescan_counterfactual": compact_scenario(
                audit["p826_no_pilot_rescan_counterfactual"]["breakdown"],
                audit["p826_no_pilot_rescan_counterfactual"]["thresholds"],
            ),
        },
        "schema": f"{SCHEMA}.summary",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p826-probe", type=Path, default=DEFAULT_P826_PROBE)
    parser.add_argument("--relation-speedups", default=",".join(str(value) for value in DEFAULT_RELATION_SPEEDUPS))
    parser.add_argument("--amortization-factors", default=",".join(str(value) for value in DEFAULT_AMORTIZATION_FACTORS))
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
                "claim_status": payload["claim_status"],
                "direct_span_top_measured": summary["generator_audit"]["direct_span_top_measured"],
                "frozen_p826_current": summary["generator_audit"]["frozen_p826_current"],
                "p826_no_pilot_rescan_counterfactual": summary["generator_audit"]["p826_no_pilot_rescan_counterfactual"],
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
