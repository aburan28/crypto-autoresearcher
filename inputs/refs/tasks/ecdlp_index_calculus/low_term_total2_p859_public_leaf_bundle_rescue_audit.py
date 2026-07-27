#!/usr/bin/env python3
"""P859 public leaf-bundle rescue audit.

P858 showed that the public candidate leaf alone covers only 62/88 compatible
challenge groups.  This audit tests public bundle expansions from the P850
source-case data and measures whether they recover the misses without hidden
labels or verifier-guided selection.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848
import low_term_total2_p851_relation_matrix_rank_growth_audit as p851
import low_term_total2_p856_variable_anchor_pair_elimination_audit as p856
import low_term_total2_p857_public_event_pair_selector_audit as p857
import low_term_total2_p858_candidate_leaf_upstream_pair_selector_audit as p858


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P851 = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p859_public_leaf_bundle_rescue_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p859_public_leaf_bundle_rescue_audit.md"
SCHEMA = "ecdlp.low_term_total2_p859_public_leaf_bundle_rescue_audit.v1"
EVENT_POLICY = "same_support_terms_event"
POLICIES = (
    "candidate_leaf_only",
    "same_row_source_case_leaves",
    "source_case_all",
    "source_case_without_candidate_leaf",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p856.int_value(value, default)


def below_rho(value: Any) -> bool:
    return value is not None and float(value) < 1.0


def bundle_for_policy(row: dict[str, Any], policy: str) -> dict[str, list[int]]:
    row_key = str(row.get("row_key"))
    candidate = sorted({int_value(leaf) for leaf in row.get("candidate_factor_leaf_indices") or []})
    case_leaf_map = {
        str(key): sorted({int_value(leaf) for leaf in leaves or []})
        for key, leaves in (row.get("case_leaf_map") or {}).items()
    }
    if policy == "candidate_leaf_only":
        return {row_key: candidate} if candidate else {}
    if policy == "same_row_source_case_leaves":
        leaves = case_leaf_map.get(row_key) or candidate
        return {row_key: leaves} if leaves else {}
    if policy == "source_case_all":
        return {key: leaves for key, leaves in sorted(case_leaf_map.items()) if leaves}
    if policy == "source_case_without_candidate_leaf":
        bundle = {}
        for key, leaves in sorted(case_leaf_map.items()):
            kept = list(leaves)
            if key == row_key and candidate:
                kept = [leaf for leaf in kept if leaf not in set(candidate)]
            if kept:
                bundle[key] = kept
        return bundle
    raise ValueError(f"unknown policy {policy}")


def select_pair_from_bundle(
    verifier: Any,
    built: dict[str, Any],
    scans: list[dict[str, Any]],
) -> dict[str, Any]:
    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    cumulative_ops = 0
    cumulative_rho = 0
    processed_scan_count = 0
    for scan in sorted(
        scans,
        key=lambda item: (
            int_value(item.get("scan_ops")),
            str(item.get("selected_row_key")),
            repr(item.get("scan_key")),
        ),
    ):
        processed_scan_count += 1
        cumulative_ops += int_value(scan.get("scan_ops"))
        cumulative_rho = max(cumulative_rho, int_value(scan.get("scan_rho")))
        for form in sorted(scan["forms"], key=p857.public_form_sort_key):
            key = p857.selector_key(form, EVENT_POLICY)
            if key is None:
                continue
            buckets[key].append(form)
        ready = [
            (key, sorted(bucket, key=p857.public_form_sort_key)[:2])
            for key, bucket in buckets.items()
            if len(bucket) >= 2
        ]
        if not ready:
            continue
        ready.sort(key=lambda item: (str(item[0]), p857.public_form_sort_key(item[1][0]), p857.public_form_sort_key(item[1][1])))
        key, pair = ready[0]
        left, right = pair
        derivation = p857.evaluate_selected_pair(verifier, built, left, right)
        selected_ops, selected_rho, selected_scan_count = p857.pair_scan_cost(left, right)
        return {
            **derivation,
            "bundle_full_ops": sum(int_value(item.get("scan_ops")) for item in scans),
            "bundle_scan_count": len(scans),
            "cumulative_ops": cumulative_ops,
            "cumulative_ops_over_rho": round(cumulative_ops / max(1, cumulative_rho), 8) if cumulative_rho else None,
            "policy_key": p857.public_key_for_json(key),
            "processed_scan_count": processed_scan_count,
            "selected": True,
            "selected_ops": selected_ops,
            "selected_ops_over_rho": round(selected_ops / max(1, selected_rho), 8) if selected_rho else None,
            "selected_scan_count": selected_scan_count,
        }
    rho = max((int_value(scan.get("scan_rho")) for scan in scans), default=0)
    full_ops = sum(int_value(scan.get("scan_ops")) for scan in scans)
    return {
        "bundle_full_ops": full_ops,
        "bundle_scan_count": len(scans),
        "candidate": None,
        "cumulative_ops": full_ops,
        "cumulative_ops_over_rho": round(full_ops / max(1, rho), 8) if rho else None,
        "delta_anchor": None,
        "delta_rhs": None,
        "gcd_delta_anchor_order": None,
        "invertible": False,
        "policy_key": None,
        "processed_scan_count": len(scans),
        "selected": False,
        "selected_ops": None,
        "selected_ops_over_rho": None,
        "selected_scan_count": 0,
        "tail_equal": False,
        "verified": False,
    }


def collect_policy_rows(args: argparse.Namespace) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    p850 = load_json(args.p850)
    meta_by_group = p858.p851_group_meta(args.p851)
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    public_cache: dict[str, dict[str, Any]] = {}
    context_cache: dict[
        tuple[Any, ...],
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]],
    ] = {}
    scan_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    built_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    rows_by_policy: dict[str, list[dict[str, Any]]] = {policy: [] for policy in POLICIES}
    errors = []

    for index, row in enumerate(p850.get("relation_lane_rows") or []):
        public_source = str(row["public_source"])
        if public_source not in public_cache:
            public_cache[public_source] = load_json(Path(public_source))
        source_case = p851.compact_source_case(row)
        ckey = p851.context_key(public_source, source_case)
        if ckey not in context_cache:
            context_cache[ckey] = p848.build_context(verifier, records, public_cache[public_source], source_case)
        built_by_row, components_by_row, local_args_by_row = context_cache[ckey]

        selected_row_key = str(row.get("row_key"))
        if selected_row_key not in built_by_row:
            errors.append({"index": index, "row_key": selected_row_key, "error": "row key missing from built context"})
            continue
        built = built_by_row[selected_row_key]
        group = p856.group_tuple(row.get("target"), row.get("transfer_index"), built.get("challenge_seed"))
        meta = meta_by_group.get(group, {})

        for policy in POLICIES:
            bundle = bundle_for_policy(row, policy)
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
                skey = p851.scan_key(public_source, source_case, bundle_row_key, selected)
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
                selection = select_pair_from_bundle(verifier, built, scans)
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
                    "hidden_false_candidate_count": int_value(meta.get("hidden_false_candidate_count")),
                    "hidden_false_factor": bool((row.get("hidden_factor_labels") or {}).get("chosen_false_positive_source")),
                    "p851_ops_over_rho": meta.get("deduped_ops_over_rho"),
                    "p851_rank": meta.get("p851_rank"),
                    "policy": policy,
                    "relation_discriminator_class": row.get("relation_discriminator_class"),
                    "row_index": index,
                    "row_key": selected_row_key,
                    "target": str(row.get("target")),
                    "transfer_index": int_value(row.get("transfer_index")),
                }
            )
    return rows_by_policy, errors


def group_policy_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["group_id"]].append(row)

    group_rows = []
    for gid, items in sorted(grouped.items()):
        cumulative_ops = 0
        processed = 0
        selected = None
        # Conservative: do not deduplicate scans shared across row bundles.
        for row in sorted(
            items,
            key=lambda item: (
                int_value(item.get("bundle_full_ops")),
                str(item.get("row_key")),
                int_value(item.get("row_index")),
            ),
        ):
            processed += 1
            cumulative_ops += int_value(row.get("cumulative_ops"))
            if row.get("selected"):
                selected = row
                break
        if selected is None:
            first = items[0]
            group_rows.append(
                {
                    "candidate_row_count": len(items),
                    "conservative_cumulative_ops": cumulative_ops,
                    "group_id": gid,
                    "processed_bundle_count": processed,
                    "selected": False,
                    "target": first.get("target"),
                    "transfer_index": first.get("transfer_index"),
                }
            )
            continue
        rho = 0
        if selected.get("cumulative_ops_over_rho") is not None and selected.get("cumulative_ops"):
            rho = round(int_value(selected.get("cumulative_ops")) / float(selected["cumulative_ops_over_rho"]))
        group_rows.append(
            {
                "bundle_scan_count": selected.get("bundle_scan_count"),
                "candidate_row_count": len(items),
                "conservative_cumulative_ops": cumulative_ops,
                "conservative_cumulative_ops_over_rho": round(cumulative_ops / max(1, rho), 8) if rho else None,
                "group_id": gid,
                "hidden_false_candidate_count": selected.get("hidden_false_candidate_count"),
                "p851_ops_over_rho": selected.get("p851_ops_over_rho"),
                "p851_rank": selected.get("p851_rank"),
                "policy": selected.get("policy"),
                "policy_key": selected.get("policy_key"),
                "processed_bundle_count": processed,
                "processed_scan_count": selected.get("processed_scan_count"),
                "row_key": selected.get("row_key"),
                "selected": True,
                "selected_ops_over_rho": selected.get("selected_ops_over_rho"),
                "streaming_ops_over_rho": selected.get("cumulative_ops_over_rho"),
                "tail_equal": selected.get("tail_equal"),
                "target": selected.get("target"),
                "transfer_index": selected.get("transfer_index"),
                "verified": selected.get("verified"),
            }
        )
    return group_rows


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows_by_policy, errors = collect_policy_rows(args)
    group_rows_by_policy = {policy: group_policy_rows(rows) for policy, rows in rows_by_policy.items()}
    candidate_groups = {
        row["group_id"]
        for row in group_rows_by_policy["candidate_leaf_only"]
        if row.get("verified") and below_rho(row.get("selected_ops_over_rho"))
    }
    policy_summaries = {
        policy: summarize_policy(group_rows, candidate_groups)
        for policy, group_rows in group_rows_by_policy.items()
    }
    claim = determine_claim(policy_summaries, errors)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p850_source": str(args.p850),
            "p851_source": str(args.p851),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "errors": errors,
        "group_miss_rows": {
            policy: sorted(
                [row for row in group_rows if not row.get("selected")],
                key=lambda row: (row.get("target"), int_value(row.get("transfer_index")), row.get("group_id")),
            )
            for policy, group_rows in group_rows_by_policy.items()
        },
        "group_outlier_rows": {
            policy: sorted(
                [
                    row
                    for row in group_rows
                    if row.get("selected")
                    and (
                        not row.get("verified")
                        or not below_rho(row.get("streaming_ops_over_rho"))
                        or (row.get("p851_ops_over_rho") is not None and float(row["p851_ops_over_rho"]) >= 1.0)
                    )
                ],
                key=lambda row: (
                    not row.get("verified"),
                    float(row.get("streaming_ops_over_rho") or 10**9),
                    row.get("target"),
                    int_value(row.get("transfer_index")),
                ),
            )
            for policy, group_rows in group_rows_by_policy.items()
        },
        "group_result_rows": group_rows_by_policy,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "P850-BOUND: row candidates and source-case leaf maps come from P850; this is not source discovery from scratch.",
            "PUBLIC-BUNDLE BOUNDARY: bundle policies use row/source-case leaf maps before relation-event extraction.",
            "FORBIDDEN PRE-SCAN INPUT BOUNDARY: policies do not use event forms, anchor coefficient, RHS, verifier outcome, derived scalar, or hidden labels.",
            "CONSERVATIVE GROUP COST: group streaming does not deduplicate scans shared across multiple row bundles.",
            "POLLARD-RHO BOUNDARY: this is a leaf-bundle rescue audit for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p859_public_leaf_bundle_rescue_audit",
        "parameters": {
            "event_policy_after_scan": EVENT_POLICY,
            "policies": list(POLICIES),
        },
        "policy_summaries": policy_summaries,
        "red_team_handoff": {
            "assumptions": [
                "P850 case_leaf_map is public source-case material and can be used before relation-event extraction.",
                "Conservative row-bundle streaming is acceptable for a first rescue audit.",
                "Recovering P858 misses is valuable only if added scan cost remains explicit.",
            ],
            "failure_modes": [
                "Bundle expansion may recover misses only by spending above rho.",
                "Source-case leaf maps may still depend on a non-promotable upstream P850 candidate process.",
                "A better implementation may need cross-row scan deduplication to avoid conservative overcharging.",
            ],
            "next_concrete_action": (
                "Build P860 to deduplicate shared scans across selected row bundles and replay the best P859 public bundle policy on a fresh disjoint bank."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P859_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summarize_all(policy_summaries, errors),
    }


def summarize_policy(group_rows: list[dict[str, Any]], candidate_groups: set[str]) -> dict[str, Any]:
    selected = [row for row in group_rows if row.get("selected")]
    verified = [row for row in selected if row.get("verified")]
    selected_below = [row for row in verified if below_rho(row.get("selected_ops_over_rho"))]
    streaming_below = [row for row in verified if below_rho(row.get("streaming_ops_over_rho"))]
    conservative_below = [row for row in verified if below_rho(row.get("conservative_cumulative_ops_over_rho"))]
    false_selected = [row for row in selected if not row.get("tail_equal") or not row.get("verified")]
    selected_groups = {row["group_id"] for row in selected_below}
    rescued = selected_groups - candidate_groups
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
        "groups_with_conservative_below_rho_verified_pair": len(conservative_below),
        "groups_with_streaming_below_rho_verified_pair": len(streaming_below),
        "groups_with_verified_pair": len(verified),
        "groups_with_verified_pair_selected_cost_below_rho": len(selected_below),
        "max_selected_ops_over_rho": max(selected_ops) if selected_ops else None,
        "max_conservative_ops_over_rho": max(conservative_ops) if conservative_ops else None,
        "max_streaming_ops_over_rho": max(streaming_ops) if streaming_ops else None,
        "mean_selected_ops_over_rho": round(sum(selected_ops) / len(selected_ops), 8) if selected_ops else None,
        "mean_conservative_ops_over_rho": round(sum(conservative_ops) / len(conservative_ops), 8) if conservative_ops else None,
        "mean_streaming_ops_over_rho": round(sum(streaming_ops) / len(streaming_ops), 8) if streaming_ops else None,
        "min_selected_ops_over_rho": min(selected_ops) if selected_ops else None,
        "min_conservative_ops_over_rho": min(conservative_ops) if conservative_ops else None,
        "min_streaming_ops_over_rho": min(streaming_ops) if streaming_ops else None,
        "p858_miss_rescued_selected_cost_below_rho_count": len(rescued),
        "rescued_group_ids_sample": sorted(rescued)[:12],
    }


def determine_claim(policy_summaries: dict[str, dict[str, Any]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P859_RECONSTRUCTION_ERRORS"
    best = max(
        policy_summaries.items(),
        key=lambda item: (
            item[1]["groups_with_verified_pair_selected_cost_below_rho"],
            item[1]["groups_with_streaming_below_rho_verified_pair"],
            -item[1]["false_selected_group_count"],
        ),
    )
    if best[1]["groups_with_verified_pair_selected_cost_below_rho"] == best[1]["group_count"]:
        if best[1]["groups_with_conservative_below_rho_verified_pair"] == best[1]["group_count"]:
            return f"P859_{best[0].upper()}_RECOVERS_ALL_GROUPS_BELOW_RHO"
        if best[1]["groups_with_streaming_below_rho_verified_pair"] == best[1]["group_count"]:
            return f"P859_{best[0].upper()}_RECOVERS_ALL_GROUPS_BELOW_RHO"
        return f"P859_{best[0].upper()}_RECOVERS_ALL_GROUPS_WITH_STREAMING_OUTLIERS"
    if best[1]["p858_miss_rescued_selected_cost_below_rho_count"] > 0:
        return f"P859_{best[0].upper()}_RESCUES_P858_MISSES_PARTIALLY"
    return "NEGATIVE_RESULT_P859_PUBLIC_LEAF_BUNDLES_DO_NOT_RESCUE_P858_MISSES"


def summarize_all(policy_summaries: dict[str, dict[str, Any]], errors: list[dict[str, Any]]) -> dict[str, Any]:
    best_policy, best_summary = max(
        policy_summaries.items(),
        key=lambda item: (
            item[1]["groups_with_verified_pair_selected_cost_below_rho"],
            item[1]["groups_with_streaming_below_rho_verified_pair"],
            -item[1]["false_selected_group_count"],
        ),
    )
    return {
        "best_policy": best_policy,
        "best_policy_summary": best_summary,
        "claim_status": determine_claim(policy_summaries, errors),
        "error_count": len(errors),
        "policy_count": len(policy_summaries),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p850", type=Path, default=DEFAULT_P850)
    parser.add_argument("--p851", type=Path, default=DEFAULT_P851)
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
