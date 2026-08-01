#!/usr/bin/env python3
"""P890 companion-row motif-cost compression audit for P889 contexts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p890_companion_row_motif_cost_compression.md"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_p889_train_only_public_source_family_scorer_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p890_companion_row_motif_cost_compression_probe.json"
SCHEMA = "ecdlp.low_term_total2_p890_companion_row_motif_cost_compression.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def context_key(group: dict[str, Any]) -> tuple[Any, ...]:
    return (
        group.get("target"),
        group.get("challenge_seed"),
        tuple(group.get("row_keys") or []),
    )


def row_context_key(row: dict[str, Any]) -> tuple[Any, ...] | None:
    key = row.get("context_key")
    if key:
        # P881 compact_context_key stores target/challenge separately in groups,
        # while recovered rows retain the raw tuple. Use the challenge seed slot.
        return tuple(key)
    return None


def row_component(row: dict[str, Any]) -> dict[str, Any]:
    selection = row.get("selection") or {}
    chosen_slices = selection.get("chosen_slices") or []
    first_slice = chosen_slices[0] if chosen_slices else {}
    factor_work = int_value(selection.get("factor_work"))
    relevant_leaf_evals = int_value(selection.get("relevant_leaf_evals"))
    quadratic_root_work = int_value(selection.get("quadratic_root_work"))
    recovered_root_count = int_value(selection.get("recovered_root_count"))
    variable_ops = factor_work + relevant_leaf_evals + quadratic_root_work + recovered_root_count
    motif_ops = int_value(row.get("motif_ops") or selection.get("public_slice_motif_ops"))
    fixed_overhead = motif_ops - variable_ops
    leaf_key = (
        first_slice.get("axis"),
        int_value(first_slice.get("fixed_value")),
        int_value(first_slice.get("min_leaf_index")),
    )
    leaf_variable_ops = relevant_leaf_evals + quadratic_root_work + recovered_root_count
    return {
        "factor_work": factor_work,
        "fixed_overhead": fixed_overhead,
        "leaf_key": list(leaf_key),
        "leaf_variable_ops": leaf_variable_ops,
        "motif_ops": motif_ops,
        "quadratic_root_work": quadratic_root_work,
        "recovered_root_count": recovered_root_count,
        "relevant_leaf_evals": relevant_leaf_evals,
        "row_key": row.get("row_key"),
        "row_public_key_verified": bool(row.get("row_public_key_verified")),
        "transfer_index": row.get("transfer_index"),
        "variable_ops": variable_ops,
    }


def rows_for_group(policy_report: dict[str, Any], group: dict[str, Any]) -> list[dict[str, Any]]:
    wanted = set(group.get("row_keys") or [])
    rows = []
    for source_result in policy_report.get("source_results") or []:
        for row in source_result.get("recovered_rows") or []:
            if row.get("context_missing"):
                continue
            if row.get("row_key") in wanted and row.get("target") == group.get("target"):
                rows.append(row)
    rows.sort(key=lambda item: (int_value(item.get("transfer_index")), str(item.get("row_key"))))
    return rows


def compressed_context(policy_name: str, group: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    components = [row_component(row) for row in rows]
    rho_estimate = None
    if group.get("motif_ops_over_rho"):
        rho_estimate = int(round(float(group["motif_ops"]) / float(group["motif_ops_over_rho"])))
    elif group.get("direct_ops_over_rho"):
        rho_estimate = int(round(float(group["direct_ops"]) / float(group["direct_ops_over_rho"])))

    fixed_overheads = [int_value(component.get("fixed_overhead")) for component in components]
    variable_sum = sum(int_value(component.get("variable_ops")) for component in components)
    factor_work_sum = sum(int_value(component.get("factor_work")) for component in components)
    leaf_groups: dict[tuple[Any, ...], list[int]] = defaultdict(list)
    for component in components:
        leaf_groups[tuple(component["leaf_key"])].append(int_value(component.get("leaf_variable_ops")))
    shared_leaf_variable_sum = sum(max(values) for values in leaf_groups.values())

    baseline_ops = int_value(group.get("motif_ops"))
    shared_fixed_ops = (max(fixed_overheads) if fixed_overheads else 0) + variable_sum
    shared_fixed_leaf_ops = (max(fixed_overheads) if fixed_overheads else 0) + factor_work_sum + shared_leaf_variable_sum
    optimistic_fixed_leaf_ops = (min(fixed_overheads) if fixed_overheads else 0) + factor_work_sum + shared_leaf_variable_sum
    strict_below_target = (rho_estimate - 1) if rho_estimate else None
    return {
        "baseline_motif_ops": baseline_ops,
        "baseline_motif_ops_over_rho": ratio(baseline_ops, rho_estimate),
        "components": components,
        "context": {
            "challenge_seed": group.get("challenge_seed"),
            "direct_ops": group.get("direct_ops"),
            "direct_ops_over_rho": group.get("direct_ops_over_rho"),
            "matrix_rank": group.get("matrix_rank"),
            "motif_ops": group.get("motif_ops"),
            "motif_ops_over_rho": group.get("motif_ops_over_rho"),
            "row_keys": group.get("row_keys"),
            "target": group.get("target"),
            "union": group.get("union"),
        },
        "fixed_overhead_values": fixed_overheads,
        "leaf_groups": {str(key): values for key, values in sorted(leaf_groups.items())},
        "optimistic_fixed_leaf_ops": optimistic_fixed_leaf_ops,
        "optimistic_fixed_leaf_ops_over_rho": ratio(optimistic_fixed_leaf_ops, rho_estimate),
        "policy_name": policy_name,
        "required_savings_for_strict_below_rho": (baseline_ops - strict_below_target) if strict_below_target is not None else None,
        "rho_estimate": rho_estimate,
        "shared_fixed_and_leaf_ops": shared_fixed_leaf_ops,
        "shared_fixed_and_leaf_ops_over_rho": ratio(shared_fixed_leaf_ops, rho_estimate),
        "shared_fixed_ops": shared_fixed_ops,
        "shared_fixed_ops_over_rho": ratio(shared_fixed_ops, rho_estimate),
        "strict_below_rho_target_ops": strict_below_target,
    }


def determine_claim(contexts: list[dict[str, Any]]) -> str:
    if any(
        item.get("rho_estimate") is not None and int_value(item.get("shared_fixed_and_leaf_ops")) < int_value(item.get("rho_estimate"))
        for item in contexts
    ):
        return "P890_COMPANION_SHARED_WORK_BEATS_RHO_CONSERVATIVE"
    if any(
        item.get("rho_estimate") is not None
        and int_value(item.get("optimistic_fixed_leaf_ops")) <= int_value(item.get("rho_estimate"))
        for item in contexts
    ):
        return "P890_COMPANION_SHARED_WORK_REACHES_RHO_OPTIMISTIC_ONLY"
    return "NEGATIVE_RESULT_P890_COMPANION_SHARED_WORK_STILL_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source = load_json(args.source)
    compressed = []
    for policy_name, policy_report in (source.get("validation") or {}).get("policy_reports", {}).items():
        for group in policy_report.get("context_groups") or []:
            if not group.get("target_context_public_key_verified"):
                continue
            rows = rows_for_group(policy_report, group)
            if len(rows) < 2:
                continue
            compressed.append(compressed_context(policy_name, group, rows))
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p889_source": str(args.source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(compressed),
        "compressed_contexts": compressed,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "COST-MODEL ONLY: no new verifier primitive is implemented.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p890_companion_row_motif_cost_compression",
        "parameters": {
            "context_count": len(compressed),
        },
        "red_team_handoff": {
            "assumptions": [
                "Rows with the same fixed value and selected leaf can share leaf/root setup work.",
                "Inferred fixed overhead can be charged once across companion rows in a future implementation.",
                "The optimistic min-overhead model is a boundary check, not a valid win claim.",
            ],
            "failure_modes": [
                "The inferred fixed overhead may contain row-specific work that cannot be shared.",
                "The leaf/root sharing model may double count savings if factor work dominates.",
                "A cost-model near miss needs implementation before it can become evidence of a real speedup.",
            ],
            "next_concrete_action": (
                "If conservative sharing misses narrowly, implement a concrete union-level evaluator for the transfer-712 companion rows and measure actual reusable work."
            ),
        },
        "schema": SCHEMA,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "compressed_contexts": payload["compressed_contexts"],
                "parameters": payload["parameters"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
