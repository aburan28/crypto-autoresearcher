#!/usr/bin/env python3
"""P724 target-67 row-materialization generator for the first hard hole."""

from __future__ import annotations

import argparse
import importlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p723_target_directed_source_alignment_audit as p723
import relation_probe


stress_probe = importlib.import_module(
    "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_"
    "static_bank_shared_challenge_salt_neighborhood_low_monic_c_stress_probe"
)
compress_probe = stress_probe.compress_probe
leaf_trim_probe = stress_probe.leaf_trim_probe
loto_selector_probe = stress_probe.loto_selector_probe
salt_neighborhood_probe = stress_probe.salt_neighborhood_probe

STATE_DIR = Path("ecdlp_index_calculus_state")
TARGET = "67.a1@9803"
NEGATIVE_TARGET = "22050.cf1@11731"
DEFAULT_SOURCE_OUT = (
    STATE_DIR
    / "frontier_public_leaf_policy_p724_target67_materialized_fixed_row_20488_20495_col15_selector_expanded_probe.json"
)
DEFAULT_AUDIT_OUT = STATE_DIR / "low_term_total2_p724_target67_row_materialization_generator_probe.json"
DEFAULT_ROW_SELECTORS = ",".join(
    [
        "target_cap2_ow0_hw3_lw0_sw0_cw0_aw1",
        "target_cap3_ow0_hw1_lw0_sw0_cw0_aw0",
        "target_cap3_ow3_hw3_lw0_sw0_cw0_aw1",
        "target_cap1_ow1_hw3_lw0_sw0_cw0_aw0",
    ]
)
DEFAULT_LEAF_SELECTORS = ",".join(
    [
        "mode_low_term_support_total1",
        "mode_low_term_support_total2",
        "mode_low_term_support_total3",
        "mode_low_term_support_total5",
        "mode_cost_low_term_support_total2",
        "mode_cost_low_term_support_total3",
        "mode_low_leaf_index_total2",
        "mode_cost_low_leaf_index_total2",
        "mode_hybrid_support_monic_b_total2",
        "mode_cost_hybrid_support_monic_b_total2",
        "mode_double_pair_first_total2",
        "mode_low_term_span_total2",
        "mode_low_term_span_total3",
        "mode_low_term_span_total5",
        "mode_low_monic_b_total2",
        "mode_low_monic_c_total2",
        "mode_low_double_pair_count_total2",
    ]
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return p723.p716.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p723.p716.float_value(value, default)


def parse_indices(raw: str) -> list[int]:
    values: list[int] = []
    for item in str(raw).split(","):
        item = item.strip()
        if not item:
            continue
        if ".." in item:
            lo_raw, hi_raw = item.split("..", 1)
            lo = int(lo_raw)
            hi = int(hi_raw)
            step = 1 if hi >= lo else -1
            values.extend(range(lo, hi + step, step))
        else:
            values.append(int(item))
    return sorted(set(values))


def split_csv(raw: str) -> list[str]:
    return [item.strip() for item in str(raw).split(",") if item.strip()]


def row_key_target(row: dict[str, Any]) -> str:
    return p723.target_prefix(compress_probe.row_key(row))


def raw_row_summary(cases: list[dict[str, Any]], target: str, negative_target: str) -> dict[str, Any]:
    rows = [row for case in cases for row in case.get("_rows") or [] if not row.get("error")]
    target_rows = [row for row in rows if row_key_target(row) == target]
    negative_rows = [row for row in rows if row_key_target(row) == negative_target]
    by_transfer = Counter(int_value(case.get("transfer_index")) for case in cases)
    return {
        "case_count": len(cases),
        "case_target_counts": dict(Counter(str(case.get("target")) for case in cases).most_common()),
        "case_transfer_counts": {str(key): by_transfer[key] for key in sorted(by_transfer)},
        "generic_rho_steps_max": max((int_value(case.get("generic_rho_steps")) for case in cases), default=0),
        "negative_target_raw_row_count": len(negative_rows),
        "raw_row_count": len(rows),
        "source_verified_case_count": sum(1 for case in cases if case.get("source_verified")),
        "target_key_exact_raw_row_count": len(target_rows),
        "target_key_exact_row_examples": [
            {
                "row_key": compress_probe.row_key(row),
                "row_ops": compress_probe.row_ops(row),
                "transfer_index": case.get("transfer_index"),
                "top_k": case.get("top_k"),
            }
            for case in cases
            for row in case.get("_rows") or []
            if not row.get("error") and row_key_target(row) == target
        ][:8],
    }


def leaf_target_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(row.get("target")) for row in rows)


def source_leaf_summary(rows: list[dict[str, Any]], target: str, negative_target: str) -> dict[str, Any]:
    rel2 = [row for row in rows if int_value(row.get("relation_count")) == 2]
    target_rows = [row for row in rows if str(row.get("target")) == target]
    target_rel2 = [row for row in target_rows if int_value(row.get("relation_count")) == 2]
    negative_rows = [row for row in rows if str(row.get("target")) == negative_target]
    return {
        "below_rho_count": sum(1 for row in rows if row.get("below_rho")),
        "negative_target_count": len(negative_rows),
        "public_key_verified_count": sum(1 for row in rows if row.get("public_key_verified")),
        "rel2_count": len(rel2),
        "rel2_verified_count": sum(1 for row in rel2 if row.get("public_key_verified")),
        "target_counts": dict(leaf_target_counts(rows).most_common()),
        "target_count": len(target_rows),
        "target_rel2_count": len(target_rel2),
        "target_rel2_verified_count": sum(1 for row in target_rel2 if row.get("public_key_verified")),
        "target_rel2_examples": [
            {
                "ops_over_rho": row.get("ops_over_rho"),
                "relation_count": row.get("relation_count"),
                "row_keys": row.get("row_keys") or [],
                "selector": row.get("selector"),
                "top_k": row.get("top_k"),
                "transfer_index": row.get("transfer_index"),
            }
            for row in target_rel2[:8]
        ],
        "total_count": len(rows),
    }


def determine_claim(raw_summary: dict[str, Any], leaf_summary: dict[str, Any]) -> str:
    if int_value(raw_summary.get("negative_target_raw_row_count")):
        return "NEGATIVE_RESULT_P724_TARGET_FILTER_LEAKED_NEGATIVE_TARGET_ROWS"
    if int_value(leaf_summary.get("negative_target_count")):
        return "NEGATIVE_RESULT_P724_SOURCE_ARTIFACT_LEAKED_NEGATIVE_TARGET_ROWS"
    if int_value(raw_summary.get("target_key_exact_raw_row_count")) == 0:
        return "NEGATIVE_RESULT_P724_NO_TARGET67_RAW_MATERIALIZATION"
    if int_value(leaf_summary.get("target_rel2_count")) == 0:
        return "P724_TARGET67_MATERIALIZED_REL2_CONVERSION_OPEN"
    return "P724_TARGET67_REL2_MATERIALIZED_SHARED_CORE_SCORING_REQUIRED"


def analyze(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    transfer_source = load_json(Path(args.transfer_source))
    params = transfer_source.get("parameters") if isinstance(transfer_source, dict) else {}
    if not isinstance(params, dict):
        params = {}
    radius = int(args.radius if args.radius is not None else params.get("radius") or 4)
    top_k_grid = compress_probe.parse_ints(args.top_k_grid, [4, 7, 12, 16, 24])
    stress_indices = parse_indices(args.stress_transfer_indices)
    fixed_row_selectors = split_csv(args.fixed_row_selectors)
    leaf_specs = [stress_probe.parse_leaf_selector(item) for item in split_csv(args.leaf_selectors)]

    bank = load_json(Path(args.bank_source))
    config_source = load_json(Path(args.config_source))
    direct_source = load_json(Path(args.direct_source))
    compress_source = load_json(Path(args.compress_source))
    labels = loto_selector_probe.oracle_labels(compress_source)
    bank_rows = {
        compress_probe.row_key(row): row
        for row in bank.get("bank_rows") or []
        if isinstance(row, dict) and compress_probe.row_key(row)
    }
    target_specs = [
        spec
        for spec in salt_neighborhood_probe.witness_specs(direct_source, bank_rows, radius)
        if str(spec.get("target")) == args.target
    ]
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()
    cases = loto_selector_probe.scan_cases(
        verifier,
        records,
        config_source,
        target_specs,
        stress_indices,
        top_k_grid,
        labels,
        args,
    )
    chosen = stress_probe.train_row_specs(
        verifier,
        [],
        labels,
        [],
        fixed_row_selectors,
        int(args.leaf_residue_modulus),
    )
    target_specs_by_key = leaf_trim_probe.specs_by_target_and_key(
        salt_neighborhood_probe.witness_specs(direct_source, bank_rows, radius)
    )

    policy_results: dict[str, dict[str, Any]] = {}
    all_leaf_results: list[dict[str, Any]] = []
    for policy, chosen_policy in chosen.items():
        row_results = stress_probe.evaluate_row_selector(
            verifier,
            cases,
            [],
            chosen_policy,
            labels,
            int(args.leaf_residue_modulus),
        )
        leaf_results: list[dict[str, Any]] = []
        for case, row_result in zip(cases, row_results, strict=True):
            leaf_results.extend(
                stress_probe.scan_case_for_leaf_selectors(
                    verifier,
                    records,
                    config_source,
                    target_specs_by_key,
                    case,
                    row_result,
                    leaf_specs,
                    int(args.leaf_residue_modulus),
                    args,
                )
            )
        policy_results[policy] = {
            "row_selector": chosen_policy,
            "stress_leaf_results": leaf_results,
            "stress_leaf_summary": stress_probe.summarize_rows(leaf_results),
            "stress_row_results": row_results,
            "stress_row_summary": loto_selector_probe.metrics(
                row_results,
                sum(1 for case in cases if case.get("source_verified")),
            ),
        }
        all_leaf_results.extend(leaf_results)

    raw_summary = raw_row_summary(cases, args.target, args.negative_target)
    leaf_summary = source_leaf_summary(all_leaf_results, args.target, args.negative_target)
    claim_status = determine_claim(raw_summary, leaf_summary)
    stress_probe.compact_training_cases(cases)

    source_payload = {
        "created_at": now_iso(),
        "method": "p724_target67_row_materialization_generator",
        "parameters": {
            "bank_source": str(Path(args.bank_source)),
            "compress_source": str(Path(args.compress_source)),
            "config_source": str(Path(args.config_source)),
            "direct_source": str(Path(args.direct_source)),
            "factor_base_size": int(args.factor_base_size),
            "fixed_row_selectors": fixed_row_selectors,
            "leaf_selectors": split_csv(args.leaf_selectors),
            "negative_target": args.negative_target,
            "radius": radius,
            "row_count": int(args.row_count),
            "row_pool": int(args.row_pool),
            "scout_limit": int(args.scout_limit),
            "scout_mode": args.scout_mode,
            "scout_order": args.scout_order,
            "selected_limit": int(args.selected_limit),
            "stress_transfer_indices": stress_indices,
            "target": args.target,
            "top_k_grid": top_k_grid,
            "transfer_source": str(Path(args.transfer_source)),
        },
        "policies": policy_results,
        "schema": "ecdlp.frontier_public_leaf_policy_p724_target67_materialized.v1",
        "summary": {
            "claim_status": claim_status,
            "leaf_summary": leaf_summary,
            "raw_materialization_summary": raw_summary,
        },
    }
    audit_payload = {
        "claim_status": claim_status,
        "created_at": source_payload["created_at"],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: uses archived AutoLab salt-neighborhood materializer and verifier machinery.",
            "PUBLIC-DESCRIPTOR ONLY: target label, row keys, selectors, transfer index, top-k, and public row/leaf descriptors are used.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, large-prime scaling, and complete individual-log recovery remain open.",
        ],
        "interpretation": (
            "Target-67 row-key materialization succeeded but rel2 conversion remains open."
            if claim_status == "P724_TARGET67_MATERIALIZED_REL2_CONVERSION_OPEN"
            else "Inspect claim_status and summaries for the next branch."
        ),
        "method": "p724_target67_row_materialization_generator",
        "parameters": source_payload["parameters"],
        "schema": "ecdlp.low_term_total2_p724_target67_row_materialization_generator.v1",
        "source_artifact": str(Path(args.out)),
        "summary": source_payload["summary"],
    }
    return source_payload, audit_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-out", default=str(DEFAULT_AUDIT_OUT))
    parser.add_argument("--bank-source", default=str(stress_probe.DEFAULT_BANK_SOURCE))
    parser.add_argument("--compress-source", default=str(stress_probe.DEFAULT_COMPRESS_SOURCE))
    parser.add_argument("--config-source", default=str(stress_probe.DEFAULT_CONFIG_SOURCE))
    parser.add_argument("--direct-source", default=str(stress_probe.DEFAULT_DIRECT_SOURCE))
    parser.add_argument("--factor-base-size", type=int, default=16)
    parser.add_argument("--fixed-row-selectors", default=DEFAULT_ROW_SELECTORS)
    parser.add_argument("--leaf-residue-modulus", type=int, default=16)
    parser.add_argument("--leaf-selectors", default=DEFAULT_LEAF_SELECTORS)
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--min-distinct-indices", type=int, default=4)
    parser.add_argument("--min-unsigned-distinct-indices", type=int, default=2)
    parser.add_argument("--negative-target", default=NEGATIVE_TARGET)
    parser.add_argument("--out", default=str(DEFAULT_SOURCE_OUT))
    parser.add_argument("--product-factor", type=int, default=4096)
    parser.add_argument("--radius", type=int)
    parser.add_argument("--row-count", type=int, default=128)
    parser.add_argument("--row-factor", type=int, default=512)
    parser.add_argument("--row-pool", type=int, default=512)
    parser.add_argument("--scout-limit", type=int, default=192)
    parser.add_argument("--scout-mode", default="s3_coeff_spread")
    parser.add_argument("--scout-order", default="eval_cover_hits_high")
    parser.add_argument("--seed", default="ecdlp-frontier-signed-dual-sieve-v1")
    parser.add_argument("--selected-limit", type=int, default=64)
    parser.add_argument("--stress-transfer-indices", default="20488..20495")
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--top-k-grid", default="4,7,12,16,24")
    parser.add_argument("--transfer-source", default=str(stress_probe.DEFAULT_TRANSFER_SOURCE))
    parser.add_argument("--allow-combined-coefficients", dest="require_unit_coefficients", action="store_false")
    parser.set_defaults(require_unit_coefficients=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_payload, audit_payload = analyze(args)
    write_json(Path(args.out), source_payload)
    write_json(Path(args.audit_out), audit_payload)
    print(
        json.dumps(
            {
                "claim_status": audit_payload["claim_status"],
                "leaf_summary": audit_payload["summary"]["leaf_summary"],
                "raw_materialization_summary": audit_payload["summary"]["raw_materialization_summary"],
                "source_artifact": audit_payload["source_artifact"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
