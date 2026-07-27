#!/usr/bin/env python3
"""P862 replay P861 p231 rejected rows through the relation lane."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848
import low_term_total2_p850_split_lane_fresh_disjoint_validation as p850
import low_term_total2_p851_relation_matrix_rank_growth_audit as p851
import low_term_total2_p856_variable_anchor_pair_elimination_audit as p856
import low_term_total2_p858_candidate_leaf_upstream_pair_selector_audit as p858
import low_term_total2_p859_public_leaf_bundle_rescue_audit as p859


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p862_p231_rejected_relation_lane_replay.md"
DEFAULT_P861 = STATE_DIR / "low_term_total2_p861_p231_refresh_materialization_replay_probe.json"
DEFAULT_QROOT = STATE_DIR / "low_term_total2_ffe_public_factor_quadratic_root_p231_frozen_prefix_1160_1167_probe.json"
DEFAULT_P845 = STATE_DIR / "low_term_total2_p845_public_factor_surface_slack_guard_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p862_p231_rejected_relation_lane_replay_probe.json"
SCHEMA = "ecdlp.low_term_total2_p862_p231_rejected_relation_lane_replay.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p850.int_value(value, default)


def below_rho(value: Any) -> bool:
    return value is not None and float(value) < 1.0


def guard_threshold(p845_payload: dict[str, Any]) -> int:
    return int_value(p845_payload["selected_guard"]["guard"]["threshold"])


def p861_rejected_keys(p861_payload: dict[str, Any]) -> set[tuple[str, int, str]]:
    keys = set()
    for row in (p861_payload.get("guard_audit") or {}).get("audited_rows") or []:
        if not row.get("p845_rejected"):
            continue
        keys.add((str(row.get("target")), int_value(row.get("transfer_index")), str(row.get("row_key"))))
    return keys


def select_qroot_rows(
    qroot_payload: dict[str, Any],
    p861_payload: dict[str, Any],
    threshold: int,
) -> tuple[str, list[dict[str, Any]]]:
    policy = str((p861_payload.get("guard_audit") or {}).get("best_policy") or "")
    if not policy:
        policy = str((qroot_payload.get("summary") or {}).get("best_policy") or "")
    keys = p861_rejected_keys(p861_payload)
    sage_cache: dict[str, dict[str, Any]] = {}
    rows = []
    for row in (qroot_payload.get("policy_rows") or {}).get(policy) or []:
        key = (str(row.get("target")), int_value(row.get("transfer_index")), str(row.get("row_key")))
        if key not in keys:
            continue
        features = p850.candidate_surface_features(qroot_payload, row, sage_cache)
        if int_value(features.get("surface_ffe_ops")) <= threshold:
            continue
        rows.append({**row, "_candidate_surface_features": features})
    return policy, rows


def verified_direct_variant(row: dict[str, Any]) -> dict[str, Any] | None:
    return (row.get("variant_summary") or {}).get("best_verified_with_candidate_leaf")


def direct_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if not row.get("error")]
    verified = [row for row in valid if verified_direct_variant(row)]
    below = [
        row
        for row in verified
        if below_rho((verified_direct_variant(row) or {}).get("ops_over_rho"))
    ]
    ops = [
        float((verified_direct_variant(row) or {}).get("ops_over_rho"))
        for row in verified
        if (verified_direct_variant(row) or {}).get("ops_over_rho") is not None
    ]
    return {
        "below_rho_direct_verified_count": len(below),
        "direct_replay_error_count": len(rows) - len(valid),
        "direct_replay_row_count": len(rows),
        "direct_verified_count": len(verified),
        "max_direct_ops_over_rho": max(ops) if ops else None,
        "mean_direct_ops_over_rho": round(sum(ops) / len(ops), 8) if ops else None,
        "min_direct_ops_over_rho": min(ops) if ops else None,
        "standalone_direct_count": sum(
            1
            for row in verified
            if row.get("relation_discriminator_class") == "standalone_direct_relation_verified"
        ),
        "companion_direct_count": sum(
            1
            for row in verified
            if row.get("relation_discriminator_class") == "companion_group_relation_verified"
        ),
        "same_row_expanded_direct_count": sum(
            1
            for row in verified
            if row.get("relation_discriminator_class") == "same_row_expanded_relation_verified"
        ),
    }


def compact_direct_row(row: dict[str, Any]) -> dict[str, Any]:
    best = verified_direct_variant(row)
    return {
        "candidate_factor_leaf_indices": row.get("candidate_factor_leaf_indices") or [],
        "error": row.get("error"),
        "p845_surface_ffe_ops": (row.get("candidate_features") or {}).get("surface_ffe_ops"),
        "qroot_ops_over_rho": (row.get("candidate_features") or {}).get("public_factor_quadratic_root_ops_over_rho"),
        "relation_discriminator_class": row.get("relation_discriminator_class"),
        "row_key": row.get("row_key"),
        "source_case": row.get("source_case"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "verified_direct_variant": best,
    }


def build_source_case(row: dict[str, Any]) -> dict[str, Any]:
    source_case = dict(row.get("source_case") or {})
    source_case["target"] = row.get("target")
    source_case["transfer_index"] = row.get("transfer_index")
    return source_case


def collect_bundle_policy_rows(
    verifier: Any,
    records: list[dict[str, Any]],
    public_path: Path,
    public_payload: dict[str, Any],
    direct_rows: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    rows_by_policy: dict[str, list[dict[str, Any]]] = {policy: [] for policy in p859.POLICIES}
    errors: list[dict[str, Any]] = []
    context_cache: dict[
        tuple[Any, ...],
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]],
    ] = {}
    scan_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    built_cache: dict[tuple[Any, ...], dict[str, Any]] = {}

    for index, row in enumerate(direct_rows):
        if row.get("error"):
            errors.append(
                {
                    "index": index,
                    "row_key": row.get("row_key"),
                    "error": f"direct row error: {row.get('error')}",
                }
            )
            continue
        source_case = build_source_case(row)
        ckey = p851.context_key(str(public_path), source_case)
        if ckey not in context_cache:
            context_cache[ckey] = p848.build_context(verifier, records, public_payload, source_case)
        built_by_row, components_by_row, local_args_by_row = context_cache[ckey]
        selected_row_key = str(row.get("row_key"))
        if selected_row_key not in built_by_row:
            errors.append({"index": index, "row_key": selected_row_key, "error": "row key missing from built context"})
            continue
        built = built_by_row[selected_row_key]
        group = p856.group_tuple(row.get("target"), row.get("transfer_index"), built.get("challenge_seed"))

        for policy in p859.POLICIES:
            bundle = p859.bundle_for_policy(row, policy)
            scans = []
            for bundle_row_key, leaves in sorted(bundle.items()):
                if bundle_row_key not in built_by_row:
                    errors.append(
                        {
                            "index": index,
                            "policy": policy,
                            "row_key": selected_row_key,
                            "bundle_row_key": bundle_row_key,
                            "error": "bundle row key missing from built context",
                        }
                    )
                    continue
                selected = sorted({int_value(leaf) for leaf in leaves})
                if not selected:
                    continue
                skey = p851.scan_key(str(public_path), source_case, bundle_row_key, selected)
                if skey not in scan_cache:
                    scan_cache[skey] = p848.direct_witness_probe.scan_selected(
                        verifier,
                        built_by_row[bundle_row_key],
                        components_by_row[bundle_row_key],
                        set(selected),
                        local_args_by_row[bundle_row_key],
                    )
                    built_cache[skey] = built_by_row[bundle_row_key]
                scan = scan_cache[skey]
                scan_row = {
                    "forms": [
                        p858.event_form_record(
                            event,
                            {
                                "scan_key": skey,
                                "scan_ops": int_value(scan.get("preassociation_filter_ops")),
                                "scan_rho": int_value(built_cache[skey].get("generic_rho_steps")),
                                "selected_row_key": bundle_row_key,
                            },
                            public_order,
                        )
                        for public_order, event in enumerate(scan.get("relation_events") or [])
                    ],
                    "leaf_count": len(selected),
                    "scan_key": skey,
                    "scan_ops": int_value(scan.get("preassociation_filter_ops")),
                    "scan_rho": int_value(built_cache[skey].get("generic_rho_steps")),
                    "selected_row_key": bundle_row_key,
                }
                scans.append(scan_row)
            if scans:
                selection = p859.select_pair_from_bundle(verifier, built, scans)
            else:
                selection = {
                    "bundle_full_ops": 0,
                    "bundle_scan_count": 0,
                    "candidate": None,
                    "cumulative_ops": 0,
                    "cumulative_ops_over_rho": None,
                    "delta_anchor": None,
                    "delta_rhs": None,
                    "gcd_delta_anchor_order": None,
                    "invertible": False,
                    "policy_key": None,
                    "processed_scan_count": 0,
                    "selected": False,
                    "selected_ops": None,
                    "selected_ops_over_rho": None,
                    "selected_scan_count": 0,
                    "tail_equal": False,
                    "verified": False,
                }
            rows_by_policy[policy].append(
                {
                    **selection,
                    "bank_id": row.get("bank_id"),
                    "bundle_leaf_count": sum(len(leaves) for leaves in bundle.values()),
                    "candidate_features": row.get("candidate_features") or {},
                    "group_id": p856.group_id(group),
                    "hidden_false_factor": bool((row.get("hidden_factor_labels") or {}).get("chosen_false_positive_source")),
                    "p845_surface_ffe_ops": (row.get("candidate_features") or {}).get("surface_ffe_ops"),
                    "policy": policy,
                    "qroot_ops_over_rho": (row.get("candidate_features") or {}).get("public_factor_quadratic_root_ops_over_rho"),
                    "relation_discriminator_class": row.get("relation_discriminator_class"),
                    "row_index": index,
                    "row_key": selected_row_key,
                    "target": str(row.get("target")),
                    "transfer_index": int_value(row.get("transfer_index")),
                }
            )
    return rows_by_policy, errors


def summarize_bundle_policy(group_rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in group_rows if row.get("selected")]
    verified = [row for row in selected if row.get("verified")]
    selected_below = [row for row in verified if below_rho(row.get("selected_ops_over_rho"))]
    streaming_below = [row for row in verified if below_rho(row.get("streaming_ops_over_rho"))]
    conservative_below = [row for row in verified if below_rho(row.get("conservative_cumulative_ops_over_rho"))]
    false_selected = [row for row in selected if not row.get("tail_equal") or not row.get("verified")]
    selected_ops = [float(row["selected_ops_over_rho"]) for row in selected_below if row.get("selected_ops_over_rho") is not None]
    streaming_ops = [float(row["streaming_ops_over_rho"]) for row in streaming_below if row.get("streaming_ops_over_rho") is not None]
    conservative_ops = [
        float(row["conservative_cumulative_ops_over_rho"])
        for row in conservative_below
        if row.get("conservative_cumulative_ops_over_rho") is not None
    ]
    return {
        "false_selected_group_count": len(false_selected),
        "group_count": len(group_rows),
        "groups_with_selected_pair": len(selected),
        "groups_with_verified_pair": len(verified),
        "groups_with_verified_pair_selected_cost_below_rho": len(selected_below),
        "groups_with_streaming_below_rho_verified_pair": len(streaming_below),
        "groups_with_conservative_below_rho_verified_pair": len(conservative_below),
        "max_conservative_ops_over_rho": max(conservative_ops) if conservative_ops else None,
        "max_selected_ops_over_rho": max(selected_ops) if selected_ops else None,
        "max_streaming_ops_over_rho": max(streaming_ops) if streaming_ops else None,
        "mean_conservative_ops_over_rho": round(sum(conservative_ops) / len(conservative_ops), 8) if conservative_ops else None,
        "mean_selected_ops_over_rho": round(sum(selected_ops) / len(selected_ops), 8) if selected_ops else None,
        "mean_streaming_ops_over_rho": round(sum(streaming_ops) / len(streaming_ops), 8) if streaming_ops else None,
        "min_conservative_ops_over_rho": min(conservative_ops) if conservative_ops else None,
        "min_selected_ops_over_rho": min(selected_ops) if selected_ops else None,
        "min_streaming_ops_over_rho": min(streaming_ops) if streaming_ops else None,
    }


def summarize_bundles(rows_by_policy: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]], dict[str, Any]]:
    group_rows_by_policy = {policy: p859.group_policy_rows(rows) for policy, rows in rows_by_policy.items()}
    policy_summaries = {
        policy: summarize_bundle_policy(group_rows)
        for policy, group_rows in group_rows_by_policy.items()
    }
    best_policy, best_summary = max(
        policy_summaries.items(),
        key=lambda item: (
            item[1]["groups_with_verified_pair_selected_cost_below_rho"],
            item[1]["groups_with_streaming_below_rho_verified_pair"],
            item[1]["groups_with_conservative_below_rho_verified_pair"],
            -item[1]["false_selected_group_count"],
        ),
    )
    return group_rows_by_policy, policy_summaries, {"best_policy": best_policy, "best_policy_summary": best_summary}


def determine_claim(direct: dict[str, Any], bundle: dict[str, Any], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P862_RECONSTRUCTION_ERRORS"
    direct_below = int_value(direct.get("below_rho_direct_verified_count")) > 0
    bundle_selected = int_value((bundle.get("best_policy_summary") or {}).get("groups_with_verified_pair_selected_cost_below_rho")) > 0
    bundle_streaming = int_value((bundle.get("best_policy_summary") or {}).get("groups_with_streaming_below_rho_verified_pair")) > 0
    bundle_conservative = int_value((bundle.get("best_policy_summary") or {}).get("groups_with_conservative_below_rho_verified_pair")) > 0
    if direct_below and bundle_conservative:
        return "P862_P231_REJECTED_ROWS_VERIFY_AND_BUNDLE_PAIR_BELOW_RHO"
    if bundle_conservative:
        return "P862_P231_REJECTED_BUNDLE_PAIR_BELOW_RHO"
    if direct_below and bundle_streaming:
        return "P862_P231_REJECTED_ROWS_VERIFY_AND_STREAMING_BUNDLE_PAIR_BELOW_RHO"
    if direct_below and bundle_selected:
        return "P862_P231_REJECTED_ROWS_VERIFY_AND_SELECTED_BUNDLE_PAIR_BELOW_RHO"
    if direct_below:
        return "P862_P231_REJECTED_ROWS_VERIFY_AS_DIRECT_RELATIONS"
    if bundle_selected:
        return "P862_P231_REJECTED_BUNDLE_SELECTED_PAIR_ONLY"
    return "NEGATIVE_RESULT_P862_P231_REJECTED_RELATION_REPLAY_NOT_FOUND"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p861_payload = load_json(args.p861)
    qroot_payload = load_json(args.qroot)
    p845_payload = load_json(args.p845)
    threshold = guard_threshold(p845_payload)
    selected_policy, qroot_rows = select_qroot_rows(qroot_payload, p861_payload, threshold)
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    signature_cache: dict[str, dict[str, Any]] = {}
    context_cache: dict[
        tuple[Any, ...],
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]],
    ] = {}
    direct_rows = [
        p850.analyze_rejected_row(
            verifier,
            records,
            args.qroot,
            qroot_payload,
            row,
            row["_candidate_surface_features"],
            signature_cache,
            context_cache,
            args.max_variants,
        )
        for row in qroot_rows
    ]
    rows_by_policy, bundle_errors = collect_bundle_policy_rows(
        verifier,
        records,
        args.qroot,
        qroot_payload,
        direct_rows,
    )
    group_rows_by_policy, policy_summaries, bundle_summary = summarize_bundles(rows_by_policy)
    direct = direct_summary(direct_rows)
    all_errors = [
        {"source": "direct", **row}
        for row in direct_rows
        if row.get("error")
    ] + [{"source": "bundle", **row} for row in bundle_errors]
    claim = determine_claim(direct, bundle_summary, all_errors)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p845_source": str(args.p845),
            "p861_source": str(args.p861),
            "qroot_source": str(args.qroot),
            "script": str(Path(__file__)),
        },
        "bundle_group_rows": group_rows_by_policy,
        "bundle_policy_summaries": policy_summaries,
        "bundle_summary": bundle_summary,
        "claim_status": claim,
        "created_at": now_iso(),
        "direct_replay_rows": [compact_direct_row(row) for row in direct_rows],
        "direct_summary": direct,
        "errors": all_errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "P861-BOUND: candidates are the two P861 P845-rejected p231 qroot rows.",
            "P845 BOUNDARY: rejected rows remain rejected as standalone preserving factor packets.",
            "PUBLIC-BUNDLE BOUNDARY: bundle policies use source-case leaf maps before relation-event extraction.",
            "HIDDEN-LABEL BOUNDARY: qroot false-positive labels are reported only after public P845 rejection.",
            "POLLARD-RHO BOUNDARY: this is relation-lane evidence for an index-calculus path, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p862_p231_rejected_relation_lane_replay",
        "parameters": {
            "bundle_policies": list(p859.POLICIES),
            "event_policy_after_scan": p859.EVENT_POLICY,
            "max_variants": args.max_variants,
            "p845_surface_threshold": threshold,
            "qroot_policy": selected_policy,
            "qroot_rejected_row_count": len(qroot_rows),
        },
        "qroot_rejected_rows": [
            {
                "candidate_factor_leaf_indices": row.get("factor_zero_leaf_indices") or [],
                "chosen_candidate": row.get("chosen_candidate"),
                "ops_over_rho": row.get("public_factor_quadratic_root_ops_over_rho"),
                "row_key": row.get("row_key"),
                "surface_ffe_ops": row["_candidate_surface_features"].get("surface_ffe_ops"),
                "target": row.get("target"),
                "transfer_index": row.get("transfer_index"),
            }
            for row in qroot_rows
        ],
        "red_team_handoff": {
            "assumptions": [
                "The p231 source-case leaf map is public material in the same sense as P850/P859 source-case maps.",
                "P845 rejected false-factor rows may be relation-useful even when not preserving standalone qroot selected roots.",
                "The same-support/terms event selector remains the public variable-anchor pairing rule for this replay.",
            ],
            "evidence_so_far": [
                f"Direct below-rho verified rows: {direct.get('below_rho_direct_verified_count')}/{direct.get('direct_replay_row_count')}.",
                f"Best bundle policy: {bundle_summary.get('best_policy')}.",
                f"Best bundle selected-cost below-rho groups: {(bundle_summary.get('best_policy_summary') or {}).get('groups_with_verified_pair_selected_cost_below_rho')}.",
            ],
            "failure_modes": [
                "The p231 family may not replicate beyond transfer 1167.",
                "The rejected rows may share a source-case pattern that is too narrow for a general source generator.",
                "The relation lane still needs larger-window sparse matrix/rank accounting and target-descent validation.",
            ],
            "next_concrete_action": (
                "Build P863 as a p231 forward-window replication: generate or summarize the next p231 frozen-prefix window, run qroot rejection, and replay P862 with the same public bundle policies."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P862_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": {
            "best_bundle_policy": bundle_summary.get("best_policy"),
            "best_bundle_selected_below_rho_group_count": (bundle_summary.get("best_policy_summary") or {}).get(
                "groups_with_verified_pair_selected_cost_below_rho"
            ),
            "best_bundle_streaming_below_rho_group_count": (bundle_summary.get("best_policy_summary") or {}).get(
                "groups_with_streaming_below_rho_verified_pair"
            ),
            "best_bundle_conservative_below_rho_group_count": (bundle_summary.get("best_policy_summary") or {}).get(
                "groups_with_conservative_below_rho_verified_pair"
            ),
            "claim_status": claim,
            "direct_below_rho_verified_count": direct.get("below_rho_direct_verified_count"),
            "direct_verified_count": direct.get("direct_verified_count"),
            "error_count": len(all_errors),
            "qroot_rejected_row_count": len(qroot_rows),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p861", type=Path, default=DEFAULT_P861)
    parser.add_argument("--qroot", type=Path, default=DEFAULT_QROOT)
    parser.add_argument("--p845", type=Path, default=DEFAULT_P845)
    parser.add_argument("--max-variants", type=int, default=2048)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
