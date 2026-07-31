#!/usr/bin/env python3
"""Plan source-generation lanes from quotient residual hits.

The priority-conditioned selector can surface rows whose target columns appear
only after quotient reduction, not in the raw exported forms.  This planner
turns those residual hits into concrete residual-promotion lanes, while keeping
collapsed exported-priority rows as negative controls.
"""

from __future__ import annotations

import argparse
import json
import shlex
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_ASSEMBLY = (
    STATE_DIR
    / "low_term_total2_residual_assembly_balance_scout_priority_conditioned_10464_10535_col6_col15_probe.json"
)
DEFAULT_CHARGED = (
    STATE_DIR
    / "low_term_total2_charged_residual_class_scout_priority_conditioned_10464_10535_col6_col15_probe.json"
)
DEFAULT_PAIR = (
    STATE_DIR
    / "low_term_total2_priority_export_pair_option_scout_priority_conditioned_10464_10535_col6_col15_probe.json"
)
DEFAULT_SELECTOR = (
    STATE_DIR
    / "low_term_total2_priority_conditioned_case_selector_10464_10535_col6_col15_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_residual_promotion_plan_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def order_reports(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reports = payload.get("order_reports")
    return reports if isinstance(reports, dict) else {}


def row_key_salts(row_keys: list[Any]) -> list[int]:
    salts = []
    for row_key in row_keys:
        text = str(row_key)
        if "salt" not in text:
            continue
        try:
            salts.append(int(text.rsplit("salt", 1)[1]))
        except ValueError:
            continue
    return salts


def compact_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": candidate.get("artifact"),
        "artifact_offset": int_value(candidate.get("artifact_offset")),
        "clause": candidate.get("clause"),
        "direct_ops_over_rho": candidate.get("direct_ops_over_rho"),
        "forms_count": int_value(candidate.get("forms_count")),
        "rank": int_value(candidate.get("rank")),
        "selector": candidate.get("selector"),
        "target": candidate.get("target"),
        "top_k": int_value(candidate.get("top_k")),
        "transfer_index": int_value(candidate.get("transfer_index")),
        "window": candidate.get("window"),
    }


def selected_case_lookup(selector_payload: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    out: dict[tuple[int, int], dict[str, Any]] = {}
    for case in selector_payload.get("selected_cases") or []:
        if not isinstance(case, dict):
            continue
        out[(int_value(case.get("transfer_index")), int_value(case.get("top_k")))] = case
    return out


def source_case_rows(source_path: Path) -> list[dict[str, Any]]:
    if not source_path.exists():
        return []
    payload = load_json(source_path)
    rows = []
    for policy_name, result in (payload.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        for offset, row in enumerate(result.get("stress_leaf_results") or []):
            if not isinstance(row, dict):
                continue
            rows.append({**row, "_policy": policy_name, "_policy_offset": offset})
    return rows


def row_key_list(value: Any) -> list[str]:
    return [str(item) for item in list_value(value)]


def direct_export_command(source_path: Path, cases_arg: str, output_path: str) -> str:
    parts = [
        "python3",
        "tasks/ecdlp_index_calculus/low_term_total2_direct_source_relation_equation_certificate.py",
        "--source",
        str(source_path),
        "--cases",
        cases_arg,
        "--out",
        output_path,
    ]
    return " ".join(shlex.quote(part) for part in parts)


def source_context(case: dict[str, Any]) -> dict[str, Any]:
    source_path = Path(str(case.get("source_artifact") or ""))
    rows = source_case_rows(source_path)
    transfer = int_value(case.get("transfer_index"))
    target = str(case.get("target") or "")
    required_row_keys = row_key_list(case.get("row_keys"))
    row_salts = Counter()
    same_transfer = []
    variant_cases = []
    for row in rows:
        if str(row.get("target")) != target:
            continue
        if int_value(row.get("transfer_index")) == transfer:
            row_keys = row_key_list(row.get("row_keys"))
            same_transfer.append(
                {
                    "leaf_selector": row.get("selector"),
                    "ops_over_rho": row.get("ops_over_rho"),
                    "policy": row.get("_policy"),
                    "policy_offset": int_value(row.get("_policy_offset")),
                    "public_key_verified": row.get("public_key_verified"),
                    "rank": int_value(row.get("rank")),
                    "row_keys": row_keys,
                    "source_verified": row.get("source_verified"),
                    "top_k": int_value(row.get("top_k")),
                }
            )
            row_salts.update(row_key_salts(row_keys))
            if (
                row_keys == required_row_keys
                and row.get("public_key_verified") is True
                and int_value(row.get("rank")) > 0
            ):
                variant_cases.append(
                    {
                        "case_arg": "|".join(
                            [
                                target,
                                str(transfer),
                                str(row.get("selector")),
                                str(int_value(row.get("top_k"))),
                            ]
                        ),
                        "leaf_selector": row.get("selector"),
                        "ops_over_rho": row.get("ops_over_rho"),
                        "rank": int_value(row.get("rank")),
                        "top_k": int_value(row.get("top_k")),
                    }
                )
    direct_variant_output = (
        str(STATE_DIR / f"low_term_total2_residual_promotion_{transfer}_selector_variant_direct_probe.json")
        if variant_cases
        else None
    )
    direct_variant_cases_arg = ";".join(
        row["case_arg"] for row in sorted(variant_cases, key=lambda item: str(item["case_arg"]))
    )
    return {
        "direct_variant_export_command": (
            direct_export_command(source_path, direct_variant_cases_arg, direct_variant_output)
            if direct_variant_output
            else None
        ),
        "direct_variant_output": direct_variant_output,
        "direct_variant_verified_case_count": len(variant_cases),
        "direct_variant_verified_cases": variant_cases,
        "observed_same_transfer_case_count": len(same_transfer),
        "observed_same_transfer_cases": same_transfer[:16],
        "observed_same_transfer_salts": sorted(row_salts),
        "source_artifact": str(source_path),
        "source_artifact_exists": source_path.exists(),
    }


def generator_command(
    lane: dict[str, Any],
    seed: str,
    output_path: str,
    leaf_selectors: str,
    top_k_grid: str,
) -> str:
    transfer = str(lane["transfer_index"])
    parts = [
        "python3",
        "tasks/ecdlp_index_calculus/"
        "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_monic_c_stress_probe.py",
        "--stress-transfer-indices",
        transfer,
        "--top-k-grid",
        top_k_grid,
        "--row-policies",
        "",
        "--fixed-row-selectors",
        "target_cap2_ow0_hw3_lw0_sw0_cw0_aw1",
        "--leaf-selectors",
        leaf_selectors,
        "--seed",
        seed,
        "--out",
        output_path,
    ]
    return " ".join(shlex.quote(part) for part in parts)


def target_residual_samples(assembly_report: dict[str, Any]) -> list[dict[str, Any]]:
    samples = []
    for sample in (assembly_report.get("samples_by_status") or {}).get("TARGET_RESIDUAL_HIT") or []:
        if isinstance(sample, dict):
            samples.append(sample)
    return samples


def collapsed_samples(assembly_report: dict[str, Any]) -> list[dict[str, Any]]:
    samples = []
    for sample in (assembly_report.get("samples_by_status") or {}).get("TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE") or []:
        if isinstance(sample, dict):
            samples.append(sample)
    return samples


def charged_group_key(group: dict[str, Any]) -> tuple[int, int]:
    samples = group.get("candidate_samples") or []
    if not samples:
        return 0, 0
    first = samples[0]
    return int_value(first.get("transfer_index")), int_value(first.get("top_k"))


def matching_charged_group(groups: list[dict[str, Any]], transfer: int, top_k: int) -> dict[str, Any] | None:
    for group in groups:
        if charged_group_key(group) == (transfer, top_k):
            return group
    return None


def residual_lane(
    order: str,
    sample: dict[str, Any],
    charged_groups: list[dict[str, Any]],
    selected_cases: dict[tuple[int, int], dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    candidate = compact_candidate(sample.get("candidate") or {})
    transfer = int_value(candidate.get("transfer_index"))
    top_k = int_value(candidate.get("top_k"))
    selected = selected_cases.get((transfer, top_k), {})
    charged = matching_charged_group(charged_groups, transfer, top_k) or {}
    seed_base = f"ecdlp-residual-promotion-{transfer}-top{top_k}"
    generator_outputs = [
        str(STATE_DIR / f"frontier_public_leaf_policy_p231_residual_promotion_{transfer}_seed{index}_probe.json")
        for index in range(args.seed_count)
    ]
    commands = [
        generator_command(
            {"transfer_index": transfer},
            f"{seed_base}-v{index}",
            generator_outputs[index],
            args.leaf_selectors,
            args.top_k_grid,
        )
        for index in range(args.seed_count)
    ]
    return {
        "action": "GENERATE_RESIDUAL_CLASS_SIBLINGS",
        "candidate": candidate,
        "charged_group": {
            "candidate_count": int_value(charged.get("candidate_count")),
            "free_column_support": charged.get("free_column_support") or [],
            "normalized_residual": charged.get("normalized_residual") or sample.get("normalized_residual"),
            "residual_support": charged.get("residual_support") or sample.get("residual_support") or [],
            "target_column_hits": charged.get("target_column_hits") or sample.get("residual_target_hits") or [],
        },
        "generator_commands": commands,
        "generator_outputs": generator_outputs,
        "order": order,
        "q_ratio_right_over_left": sample.get("q_ratio_right_over_left"),
        "raw_assembled_factor_support": sample.get("raw_assembled_factor_support") or [],
        "residual_support": sample.get("residual_support") or [],
        "residual_target_hits": sample.get("residual_target_hits") or [],
        "row_keys": selected.get("row_keys") or [],
        "row_salts": row_key_salts(selected.get("row_keys") or []),
        "source_context": source_context(selected) if selected else {},
        "success_gate": (
            "fresh sibling certificates produce an independent nonzero residual "
            "touching columns 6 or 15 after base-rowspace reduction"
        ),
        "transfer_index": transfer,
    }


def collapse_control_lane(order: str, sample: dict[str, Any]) -> dict[str, Any]:
    candidate = compact_candidate(sample.get("candidate") or {})
    return {
        "action": "NEGATIVE_CONTROL_GENERATE_MORE_Q_PARTNERS",
        "candidate": candidate,
        "order": order,
        "q_ratio_right_over_left": sample.get("q_ratio_right_over_left"),
        "raw_assembled_factor_support": sample.get("raw_assembled_factor_support") or [],
        "residual_support": sample.get("residual_support") or [],
        "residual_target_hits": sample.get("residual_target_hits") or [],
        "success_gate": "control only promotes if rowspace collapse no longer holds",
        "target_column_details": sample.get("target_column_details") or {},
        "transfer_index": int_value(candidate.get("transfer_index")),
    }


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    assembly = load_json(Path(args.assembly_artifact))
    charged = load_json(Path(args.charged_artifact))
    pair = load_json(Path(args.pair_artifact))
    selector = load_json(Path(args.selector_artifact))
    selected_cases = selected_case_lookup(selector)
    reports = {}
    residual_count = 0
    control_count = 0
    for order in sorted(set(order_reports(assembly)) | set(order_reports(charged))):
        assembly_report = order_reports(assembly).get(order, {})
        charged_report = order_reports(charged).get(order, {})
        charged_groups = [
            group
            for group in charged_report.get("residual_groups") or []
            if isinstance(group, dict) and group.get("target_column_hits")
        ]
        residual_lanes = [
            residual_lane(order, sample, charged_groups, selected_cases, args)
            for sample in target_residual_samples(assembly_report)
        ]
        control_lanes = [
            collapse_control_lane(order, sample)
            for sample in collapsed_samples(assembly_report)
        ]
        residual_count += len(residual_lanes)
        control_count += len(control_lanes)
        reports[order] = {
            "collapse_control_lane_count": len(control_lanes),
            "collapse_control_lanes": control_lanes,
            "pair_option_work_order": (order_reports(pair).get(order, {}) or {}).get("work_order") or {},
            "residual_lane_count": len(residual_lanes),
            "residual_lanes": residual_lanes,
            "target_columns": assembly_report.get("target_columns") or charged_report.get("target_columns") or [],
            "top_action": (
                "GENERATE_RESIDUAL_CLASS_SIBLINGS"
                if residual_lanes
                else "KEEP_Q_PAIR_COLLAPSE_CONTROLS"
                if control_lanes
                else "NO_RESIDUAL_PROMOTION_LANES"
            ),
        }
    claim_status = (
        "RESIDUAL_PROMOTION_PLAN_READY"
        if residual_count
        else "NEGATIVE_RESULT_NO_TARGET_RESIDUAL_PROMOTION_LANES"
    )
    return {
        "artifacts": {
            "assembly_artifact": args.assembly_artifact,
            "charged_artifact": args.charged_artifact,
            "pair_artifact": args.pair_artifact,
            "selector_artifact": args.selector_artifact,
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: residuals are in the current order-specific low-term factor-column namespace.",
            "HEURISTIC: generator commands are source-family steering hints, not target descent.",
            "OPEN: promotion requires independent residual classes and a completed target descent.",
            "This is not a deployed-curve or faster-than-Pollard-rho ECDLP claim.",
        ],
        "order_reports": reports,
        "schema": "ecdlp.low_term_total2_residual_promotion_plan.v1",
        "summary": {
            "collapse_control_lane_count": control_count,
            "order_count": len(reports),
            "residual_lane_count": residual_count,
            "seed_count_per_residual_lane": args.seed_count,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assembly-artifact", default=str(DEFAULT_ASSEMBLY))
    parser.add_argument("--charged-artifact", default=str(DEFAULT_CHARGED))
    parser.add_argument("--pair-artifact", default=str(DEFAULT_PAIR))
    parser.add_argument("--selector-artifact", default=str(DEFAULT_SELECTOR))
    parser.add_argument("--leaf-selectors", default="mode_low_term_support_total3,mode_low_term_support_total5,mode_low_term_support_total7,mode_low_term_support_total10,mode_low_term_support_total12")
    parser.add_argument("--top-k-grid", default="4,7,12,16,24,32")
    parser.add_argument("--seed-count", type=int, default=3)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_plan(args)
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
