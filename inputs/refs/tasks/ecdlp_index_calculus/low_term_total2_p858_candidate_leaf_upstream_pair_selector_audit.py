#!/usr/bin/env python3
"""P858 candidate-leaf upstream pair-selector audit.

P857 selected same-support/term pairs after P850/P851 relation events were
available.  This audit moves one stage upstream: select only the P850 public
candidate row and candidate factor leaf, then test whether the resulting scan
emits a row-local support/term pair that can eliminate the variable anchor.

The row source is still P850's public split-lane candidate set.  This does not
claim independent source discovery or a complete ECDLP algorithm.
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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P851 = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p858_candidate_leaf_upstream_pair_selector_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p858_candidate_leaf_upstream_pair_selector_audit.md"
SCHEMA = "ecdlp.low_term_total2_p858_candidate_leaf_upstream_pair_selector_audit.v1"
POLICY = "same_support_terms_event"


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


def p851_group_meta(path: Path) -> dict[tuple[str, int, str], dict[str, Any]]:
    payload = load_json(path)
    return {
        p856.group_tuple(group.get("target"), group.get("transfer_index"), group.get("challenge_seed")): {
            "deduped_ops_over_rho": group.get("deduped_ops_over_rho"),
            "hidden_false_candidate_count": group.get("hidden_false_candidate_count"),
            "p851_rank": (group.get("union") or {}).get("union_rank"),
            "p851_relation_count": (group.get("union") or {}).get("union_relation_count"),
        }
        for group in payload.get("challenge_groups") or []
    }


def event_form_record(event: dict[str, Any], scan_row: dict[str, Any], public_order: int) -> dict[str, Any]:
    coeffs, rhs, terms = event["form"]
    coeffs_tuple = tuple(int(coeff) for coeff in coeffs)
    return {
        "_public_order": public_order,
        "coeffs": coeffs_tuple,
        "rhs": int(rhs),
        "scan_key": scan_row["scan_key"],
        "scan_ops": int_value(scan_row.get("scan_ops")),
        "scan_rho": int_value(scan_row.get("scan_rho")),
        "selected_row_key": scan_row["selected_row_key"],
        "support": tuple(index for index, coeff in enumerate(coeffs_tuple) if int(coeff) != 0),
        "tail_key": p856.non_anchor_tail_key(coeffs_tuple),
        "terms": tuple(int(term) for term in terms),
    }


def select_pair_from_scan(forms: list[dict[str, Any]]) -> tuple[list[Any], dict[str, Any], dict[str, Any]] | None:
    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for form in sorted(forms, key=p857.public_form_sort_key):
        key = p857.selector_key(form, POLICY)
        if key is None:
            continue
        buckets[key].append(form)
    ready = [
        (key, sorted(bucket, key=p857.public_form_sort_key)[:2])
        for key, bucket in buckets.items()
        if len(bucket) >= 2
    ]
    if not ready:
        return None
    ready.sort(key=lambda item: (str(item[0]), p857.public_form_sort_key(item[1][0]), p857.public_form_sort_key(item[1][1])))
    key, pair = ready[0]
    return p857.public_key_for_json(key), pair[0], pair[1]


def collect_candidate_scans(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    p850 = load_json(args.p850)
    meta_by_group = p851_group_meta(args.p851)
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    public_cache: dict[str, dict[str, Any]] = {}
    context_cache: dict[
        tuple[Any, ...],
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]],
    ] = {}
    scan_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    built_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    row_results = []
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
        selected = sorted({int_value(leaf) for leaf in row.get("candidate_factor_leaf_indices") or []})
        if selected_row_key not in built_by_row:
            errors.append({"index": index, "row_key": selected_row_key, "error": "row key missing from built context"})
            continue
        if not selected:
            errors.append({"index": index, "row_key": selected_row_key, "error": "missing candidate factor leaf indices"})
            continue
        skey = p851.scan_key(public_source, source_case, selected_row_key, selected)
        if skey not in scan_cache:
            scan_cache[skey] = p848.direct_witness_probe.scan_selected(
                verifier,
                built_by_row[selected_row_key],
                components_by_row[selected_row_key],
                set(selected),
                local_args_by_row[selected_row_key],
            )
            built_cache[skey] = built_by_row[selected_row_key]
        scan = scan_cache[skey]
        built = built_cache[skey]
        group = p856.group_tuple(row.get("target"), row.get("transfer_index"), built.get("challenge_seed"))
        scan_row = {
            "scan_key": skey,
            "scan_ops": int_value(scan.get("preassociation_filter_ops")),
            "scan_rho": int_value(built.get("generic_rho_steps")),
            "selected_row_key": selected_row_key,
        }
        forms = [
            event_form_record(event, scan_row, public_order)
            for public_order, event in enumerate(scan.get("relation_events") or [])
        ]
        pair = select_pair_from_scan(forms)
        derivation: dict[str, Any] = {
            "candidate": None,
            "delta_anchor": None,
            "delta_rhs": None,
            "gcd_delta_anchor_order": None,
            "invertible": False,
            "tail_equal": False,
            "verified": False,
        }
        policy_key = None
        selected_ops = None
        selected_ops_over_rho = None
        selected_scan_count = 0
        if pair is not None:
            policy_key, left, right = pair
            derivation = p857.evaluate_selected_pair(verifier, built, left, right)
            selected_ops, selected_rho, selected_scan_count = p857.pair_scan_cost(left, right)
            selected_ops_over_rho = round(selected_ops / max(1, selected_rho), 8) if selected_rho else None

        ops = int_value(scan.get("preassociation_filter_ops"))
        rho = int_value(built.get("generic_rho_steps"))
        meta = meta_by_group.get(group, {})
        row_results.append(
            {
                **derivation,
                "bank_id": row.get("bank_id"),
                "candidate_features": row.get("candidate_features") or {},
                "event_count": len(forms),
                "group_id": p856.group_id(group),
                "hidden_false_factor": bool((row.get("hidden_factor_labels") or {}).get("chosen_false_positive_source")),
                "hidden_false_candidate_count": int_value(meta.get("hidden_false_candidate_count")),
                "p851_ops_over_rho": meta.get("deduped_ops_over_rho"),
                "p851_rank": meta.get("p851_rank"),
                "policy": POLICY,
                "policy_key": policy_key,
                "relation_discriminator_class": row.get("relation_discriminator_class"),
                "row_index": index,
                "row_key": selected_row_key,
                "scan_ops": ops,
                "scan_ops_over_rho": round(ops / max(1, rho), 8) if rho else None,
                "scan_rho": rho,
                "selected": pair is not None,
                "selected_leaf_indices": selected,
                "selected_ops": selected_ops,
                "selected_ops_over_rho": selected_ops_over_rho,
                "selected_scan_count": selected_scan_count,
                "target": str(row.get("target")),
                "transfer_index": int_value(row.get("transfer_index")),
            }
        )
    return row_results, errors


def group_stream_rows(row_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in row_results:
        grouped[row["group_id"]].append(row)

    group_rows = []
    for gid, rows in sorted(grouped.items()):
        cumulative_ops = 0
        cumulative_rho = 0
        processed = 0
        selected_row = None
        for row in sorted(
            rows,
            key=lambda item: (
                int_value(item.get("scan_ops")),
                str(item.get("row_key")),
                int_value(item.get("row_index")),
            ),
        ):
            processed += 1
            cumulative_ops += int_value(row.get("scan_ops"))
            cumulative_rho = max(cumulative_rho, int_value(row.get("scan_rho")))
            if row.get("selected"):
                selected_row = row
                break
        if selected_row is None:
            first = rows[0]
            group_rows.append(
                {
                    "group_id": gid,
                    "processed_scan_count": processed,
                    "selected": False,
                    "target": first.get("target"),
                    "transfer_index": first.get("transfer_index"),
                }
            )
            continue
        stream_ratio = round(cumulative_ops / max(1, cumulative_rho), 8) if cumulative_rho else None
        group_rows.append(
            {
                "candidate_row_count": len(rows),
                "cumulative_ops": cumulative_ops,
                "cumulative_ops_over_rho": stream_ratio,
                "group_id": gid,
                "hidden_false_candidate_count": selected_row.get("hidden_false_candidate_count"),
                "p851_ops_over_rho": selected_row.get("p851_ops_over_rho"),
                "p851_rank": selected_row.get("p851_rank"),
                "policy_key": selected_row.get("policy_key"),
                "processed_scan_count": processed,
                "row_key": selected_row.get("row_key"),
                "scan_ops_over_rho": selected_row.get("scan_ops_over_rho"),
                "selected": True,
                "selected_ops_over_rho": selected_row.get("selected_ops_over_rho"),
                "tail_equal": selected_row.get("tail_equal"),
                "target": selected_row.get("target"),
                "transfer_index": selected_row.get("transfer_index"),
                "verified": selected_row.get("verified"),
            }
        )
    return group_rows


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    row_results, errors = collect_candidate_scans(args)
    group_rows = group_stream_rows(row_results)
    claim = determine_claim(row_results, group_rows, errors)
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
        "group_outlier_rows": sorted(
            [
                row
                for row in group_rows
                if row.get("selected")
                and (
                    not row.get("verified")
                    or not below_rho(row.get("cumulative_ops_over_rho"))
                    or (row.get("p851_ops_over_rho") is not None and float(row["p851_ops_over_rho"]) >= 1.0)
                )
            ],
            key=lambda row: (
                not row.get("verified"),
                float(row.get("cumulative_ops_over_rho") or 10**9),
                row.get("target"),
                int_value(row.get("transfer_index")),
            ),
        ),
        "group_miss_rows": sorted(
            [row for row in group_rows if not row.get("selected")],
            key=lambda row: (row.get("target"), int_value(row.get("transfer_index")), row.get("group_id")),
        ),
        "group_result_rows": group_rows,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "UPSTREAM-BUT-STILL-P850-BOUND: rows come from P850's public split-lane relation candidates; this does not discover source rows from scratch.",
            "PRE-SCAN SELECTOR BOUNDARY: candidate row and candidate leaf are selected before relation-event extraction.",
            "FORBIDDEN PRE-SCAN INPUT BOUNDARY: selection does not use event forms, anchor coefficient, RHS, verifier outcome, derived scalar, or hidden labels.",
            "NO-CROSS-TRANSFER-MIXING: pair derivation is evaluated only inside identical target/transfer/challenge-seed groups.",
            "POLLARD-RHO BOUNDARY: this is an upstream selector audit for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p858_candidate_leaf_upstream_pair_selector_audit",
        "parameters": {
            "event_policy_after_scan": POLICY,
            "leaf_selector": "candidate_factor_leaf_indices on row_key",
            "row_selector": "P850 relation_lane_rows public split-lane candidate set",
        },
        "red_team_handoff": {
            "assumptions": [
                "P850 relation-lane rows are a public candidate stream suitable for an upstream audit.",
                "Candidate factor leaves are selected without verifier outcomes.",
                "Row-local support/term pairability is the right next proxy for P857's event-level selector.",
            ],
            "failure_modes": [
                "The P850 relation-lane candidate set may still hide the true source-discovery cost.",
                "A row-local result may fail when generated prospectively on fresh banks.",
                "Streaming cost can remain above rho when a group needs more than one public row scan.",
            ],
            "next_concrete_action": (
                "Build P859 as a public leaf-bundle rescue audit for the 26 P858 misses: compare candidate-only, same-row source-case, and companion/source-case leaf bundles "
                "without hidden labels, then charge the added scans before any prospective fresh-bank replay."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P858_") else "NEGATIVE RESULT",
        },
        "row_result_sample": sorted(
            [row for row in row_results if row.get("selected")],
            key=lambda row: (
                not row.get("verified"),
                not below_rho(row.get("selected_ops_over_rho")),
                float(row.get("selected_ops_over_rho") or 10**9),
                row.get("target"),
                int_value(row.get("transfer_index")),
            ),
        )[:16],
        "schema": SCHEMA,
        "summary": summarize(row_results, group_rows, errors),
        "target_summary": summarize_targets(group_rows),
    }


def determine_claim(
    row_results: list[dict[str, Any]],
    group_rows: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> str:
    if errors:
        return "NEGATIVE_RESULT_P858_RECONSTRUCTION_ERRORS"
    if not row_results:
        return "NEGATIVE_RESULT_P858_NO_CANDIDATE_ROWS"
    group_count = len(group_rows)
    group_selected_below = [
        row for row in group_rows if row.get("verified") and below_rho(row.get("selected_ops_over_rho"))
    ]
    group_streaming_below = [
        row for row in group_rows if row.get("verified") and below_rho(row.get("cumulative_ops_over_rho"))
    ]
    false_selected = [
        row
        for row in group_rows
        if row.get("selected") and (not row.get("tail_equal") or not row.get("verified"))
    ]
    if len(group_selected_below) == group_count and not false_selected:
        if len(group_streaming_below) == group_count:
            return "P858_CANDIDATE_LEAF_SELECTOR_COVERS_ALL_GROUPS_BELOW_RHO"
        return "P858_CANDIDATE_LEAF_SELECTOR_COVERS_ALL_GROUPS_WITH_STREAMING_OUTLIER"
    if group_selected_below:
        return "P858_CANDIDATE_LEAF_SELECTOR_PARTIAL_BELOW_RHO"
    return "NEGATIVE_RESULT_P858_CANDIDATE_LEAF_SELECTOR_FAILS"


def summarize(
    row_results: list[dict[str, Any]],
    group_rows: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    selected_rows = [row for row in row_results if row.get("selected")]
    verified_rows = [row for row in selected_rows if row.get("verified")]
    below_rows = [row for row in verified_rows if below_rho(row.get("selected_ops_over_rho"))]
    selected_groups = [row for row in group_rows if row.get("selected")]
    verified_groups = [row for row in selected_groups if row.get("verified")]
    selected_below_groups = [row for row in verified_groups if below_rho(row.get("selected_ops_over_rho"))]
    streaming_below_groups = [row for row in verified_groups if below_rho(row.get("cumulative_ops_over_rho"))]
    p851_above_to_selected_below = [
        row
        for row in selected_below_groups
        if row.get("p851_ops_over_rho") is not None and float(row["p851_ops_over_rho"]) >= 1.0
    ]
    p851_above_to_streaming_below = [
        row
        for row in streaming_below_groups
        if row.get("p851_ops_over_rho") is not None and float(row["p851_ops_over_rho"]) >= 1.0
    ]
    row_ops = [float(row["selected_ops_over_rho"]) for row in below_rows if row.get("selected_ops_over_rho") is not None]
    group_stream_ops = [
        float(row["cumulative_ops_over_rho"])
        for row in streaming_below_groups
        if row.get("cumulative_ops_over_rho") is not None
    ]
    return {
        "candidate_row_count": len(row_results),
        "claim_status": determine_claim(row_results, group_rows, errors),
        "error_count": len(errors),
        "false_selected_group_count": sum(
            1 for row in selected_groups if not row.get("tail_equal") or not row.get("verified")
        ),
        "group_count": len(group_rows),
        "groups_with_selected_pair": len(selected_groups),
        "groups_with_streaming_below_rho_verified_pair": len(streaming_below_groups),
        "groups_with_verified_pair": len(verified_groups),
        "groups_with_verified_pair_selected_cost_below_rho": len(selected_below_groups),
        "max_row_selected_ops_over_rho": max(row_ops) if row_ops else None,
        "max_streaming_ops_over_rho": max(group_stream_ops) if group_stream_ops else None,
        "mean_row_selected_ops_over_rho": round(sum(row_ops) / len(row_ops), 8) if row_ops else None,
        "mean_streaming_ops_over_rho": round(sum(group_stream_ops) / len(group_stream_ops), 8) if group_stream_ops else None,
        "min_row_selected_ops_over_rho": min(row_ops) if row_ops else None,
        "min_streaming_ops_over_rho": min(group_stream_ops) if group_stream_ops else None,
        "p851_above_to_selected_below_rho_count": len(p851_above_to_selected_below),
        "p851_above_to_streaming_below_rho_count": len(p851_above_to_streaming_below),
        "row_local_below_rho_verified_pair_count": len(below_rows),
        "row_local_pairable_count": len(selected_rows),
        "row_local_verified_pair_count": len(verified_rows),
    }


def summarize_targets(group_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in group_rows:
        by_target[str(row.get("target"))].append(row)
    summary = {}
    for target, rows in sorted(by_target.items()):
        selected = [row for row in rows if row.get("selected")]
        verified = [row for row in selected if row.get("verified")]
        selected_below = [row for row in verified if below_rho(row.get("selected_ops_over_rho"))]
        streaming_below = [row for row in verified if below_rho(row.get("cumulative_ops_over_rho"))]
        summary[target] = {
            "group_count": len(rows),
            "groups_with_selected_pair": len(selected),
            "groups_with_verified_pair": len(verified),
            "groups_with_verified_pair_selected_cost_below_rho": len(selected_below),
            "groups_with_streaming_below_rho_verified_pair": len(streaming_below),
            "miss_count": len(rows) - len(selected),
        }
    return summary


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
