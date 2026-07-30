#!/usr/bin/env python3
"""P848 multi-root companion audit for the P847 transfer-324 obstruction.

P847 narrowed the direct-constructor bridge failure to one transfer-324 packet:
``22050.cf1@11731:uniform:256:salt168``.  This audit tests whether the packet
can be completed by public source-case companion leaves without reusing the
known P843 false-positive companion factor leaf.
"""

from __future__ import annotations

import argparse
import json
from argparse import Namespace
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_trim_probe as leaf_trim_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_transfer_probe as transfer_probe
import relation_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P846 = STATE_DIR / "low_term_total2_p846_public_factor_direct_replay_readiness_audit_probe.json"
DEFAULT_P847 = STATE_DIR / "low_term_total2_p847_public_factor_direct_constructor_bridge_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p848_public_factor_multiroot_companion_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p848_public_factor_multiroot_companion_audit.md"
SCHEMA = "ecdlp.low_term_total2_p848_public_factor_multiroot_companion_audit.v1"


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
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def scanner_args(params: dict[str, Any]) -> Namespace:
    return Namespace(
        factor_base_size=int_value(params.get("factor_base_size"), 16),
        max_relations=96,
        min_distinct_indices=4,
        min_unsigned_distinct_indices=2,
        product_factor=4096,
        require_unit_coefficients=True,
        row_count=128,
        row_factor=512,
        row_pool=int_value(params.get("row_pool"), 512),
        scout_limit=int_value(params.get("scout_limit"), 192),
        scout_mode=params.get("scout_mode") or "s3_coeff_spread",
        scout_order=params.get("scout_order") or "eval_cover_hits_high",
        seed=params.get("seed") or "ecdlp-frontier-signed-dual-sieve-v1",
        selected_limit=int_value(params.get("selected_limit"), 64),
    )


def find_obstruction_packet(p846: dict[str, Any], p847: dict[str, Any]) -> dict[str, Any]:
    unverified = ((p847.get("summary") or {}).get("unverified_groups") or [])
    if not unverified:
        raise RuntimeError("P847 has no unverified group to audit")
    group = unverified[0]
    target = str(group["target"])
    transfer = int_value(group["transfer_index"])
    row_keys = {str(key) for key in group.get("packet_row_keys") or []}
    matches = [
        packet
        for packet in p846.get("replay_packets") or []
        if str(packet.get("target")) == target
        and int_value(packet.get("transfer_index")) == transfer
        and str(packet.get("row_key")) in row_keys
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one obstruction packet, got {len(matches)}")
    return matches[0]


def source_row_for_packet(public_payload: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    matches = []
    for row in (public_payload.get("policy_rows") or {}).get(str(packet["policy"])) or []:
        chosen = row.get("chosen_candidate") if isinstance(row.get("chosen_candidate"), dict) else {}
        if str(row.get("row_key")) != str(packet["row_key"]):
            continue
        if int_value(row.get("transfer_index")) != int_value(packet.get("transfer_index")):
            continue
        if int_value(chosen.get("factor_index"), -1) != int_value(packet.get("factor_index"), -2):
            continue
        matches.append(row)
    if len(matches) != 1:
        raise RuntimeError(f"expected one source row for obstruction packet, got {len(matches)}")
    return matches[0]


def transfer_source_rows(public_payload: dict[str, Any], packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for row in (public_payload.get("policy_rows") or {}).get(str(packet["policy"])) or []:
        if str(row.get("target")) != str(packet["target"]):
            continue
        if int_value(row.get("transfer_index")) != int_value(packet.get("transfer_index")):
            continue
        if row.get("chosen_candidate") is None:
            continue
        rows[str(row["row_key"])] = row
    return rows


def source_case_for_packet(public_payload: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    signature_path = Path((public_payload.get("parameters") or {}).get("signature_source") or "")
    signature = load_json(signature_path)
    matches = []
    for case in signature.get("positive_cases") or []:
        if str(case.get("target")) != str(packet.get("target")):
            continue
        if int_value(case.get("transfer_index")) != int_value(packet.get("transfer_index")):
            continue
        if str(packet.get("row_key")) not in {str(key) for key in case.get("row_keys") or []}:
            continue
        matches.append(case)
    if len(matches) != 1:
        raise RuntimeError(f"expected one source case for obstruction packet, got {len(matches)}")
    return matches[0]


def leaf_map_from_case(case: dict[str, Any]) -> dict[str, list[int]]:
    return {
        str(item["row_key"]): sorted({int_value(leaf) for leaf in item.get("leaf_indices") or []})
        for item in case.get("row_leaf_keys") or []
    }


def false_positive_leaves(rows: dict[str, dict[str, Any]]) -> dict[str, set[int]]:
    return {
        row_key: {int_value(leaf) for leaf in row.get("factor_zero_leaf_indices") or []}
        for row_key, row in rows.items()
        if bool(row.get("chosen_false_positive_source"))
    }


def build_context(
    verifier: Any,
    records: list[dict[str, Any]],
    public_payload: dict[str, Any],
    source_case: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Namespace]]:
    params = public_payload.get("parameters") or {}
    bank = load_json(Path(params["bank_source"]))
    config_source = load_json(Path(params["config_source"]))
    direct_source = load_json(Path(params["direct_source"]))
    bank_rows = {
        transfer_probe.row_key(row): row
        for row in bank.get("bank_rows") or []
        if isinstance(row, dict) and transfer_probe.row_key(row)
    }
    target_specs = transfer_probe.witness_specs(
        direct_source,
        bank_rows,
        int_value(params.get("radius"), 4),
    )
    specs_by_target = leaf_trim_probe.specs_by_target_and_key(target_specs)
    rows, built_by_row, components_by_row, local_args_by_row, _features, errors = leaf_trim_probe.scan_selected_rows(
        verifier,
        records,
        config_source,
        specs_by_target.get(str(source_case["target"]), {}),
        [str(key) for key in source_case.get("row_keys") or []],
        int_value(source_case["transfer_index"]),
        int_value(source_case["top_k"]),
        scanner_args(params),
    )
    if errors:
        raise RuntimeError(f"context reconstruction errors: {errors}")
    if len(rows) != len(source_case.get("row_keys") or []):
        raise RuntimeError("not all source-case rows reconstructed")
    return built_by_row, components_by_row, local_args_by_row


def compact_scan(scan: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_summaries": scan.get("event_summaries") or [],
        "preassociation_filter_ops": int_value(scan.get("preassociation_filter_ops")),
        "preassociation_filter_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
        "rank": int_value(scan.get("rank")),
        "relation_count": int_value(scan.get("relation_count")),
        "row_public_key_verified": bool(scan.get("row_public_key_verified")),
        "selected_hit_events": int_value(scan.get("selected_hit_events")),
        "selected_hit_roots": int_value(scan.get("selected_hit_roots")),
        "selected_leaf_count": int_value(scan.get("selected_leaf_count")),
        "selected_leaf_indices": scan.get("selected_leaf_indices") or [],
    }


def evaluate_variant(
    verifier: Any,
    name: str,
    leaves_by_row: dict[str, list[int]],
    built_by_row: dict[str, dict[str, Any]],
    components_by_row: dict[str, dict[str, Any]],
    local_args_by_row: dict[str, Namespace],
    known_false_positive_leaves: dict[str, set[int]],
) -> dict[str, Any]:
    scan_rows = []
    row_results = {}
    ops = 0
    rho = 0
    for row_key, leaves in sorted(leaves_by_row.items()):
        selected = sorted({int_value(leaf) for leaf in leaves})
        if not selected:
            continue
        scan = direct_witness_probe.scan_selected(
            verifier,
            built_by_row[row_key],
            components_by_row[row_key],
            set(selected),
            local_args_by_row[row_key],
        )
        scan_rows.append({"row_key": row_key, "_scan": scan})
        ops += int_value(scan.get("preassociation_filter_ops"))
        rho = max(rho, int_value(built_by_row[row_key].get("generic_rho_steps")))
        row_results[row_key] = compact_scan(scan)
    union = direct_witness_probe.union_derive(verifier, scan_rows, built_by_row, "_scan")
    used_false_leaf_by_row = {
        row_key: sorted(set(leaves) & known_false_positive_leaves.get(row_key, set()))
        for row_key, leaves in leaves_by_row.items()
        if set(leaves) & known_false_positive_leaves.get(row_key, set())
    }
    return {
        "leaves_by_row": {row_key: sorted(leaves) for row_key, leaves in sorted(leaves_by_row.items())},
        "name": name,
        "ops": ops,
        "ops_over_rho": round(ops / max(1, rho), 8) if rho else None,
        "row_results": row_results,
        "union": union,
        "uses_known_false_positive_leaf": bool(used_false_leaf_by_row),
        "used_false_positive_leaf_by_row": used_false_leaf_by_row,
        "verified": bool(union.get("union_public_key_verified")),
    }


def build_variants(
    packet: dict[str, Any],
    packet_source_row: dict[str, Any],
    case_leaf_map: dict[str, list[int]],
    known_false_positive_leaves: dict[str, set[int]],
) -> dict[str, dict[str, list[int]]]:
    packet_row = str(packet["row_key"])
    companion_rows = [row_key for row_key in case_leaf_map if row_key != packet_row]
    packet_leaves = sorted({int_value(leaf) for leaf in packet_source_row.get("factor_zero_leaf_indices") or []})
    variants: dict[str, dict[str, list[int]]] = {
        "packet_only": {packet_row: packet_leaves},
        "same_row_source_case_leaves": {packet_row: case_leaf_map.get(packet_row, [])},
        "source_case_all": case_leaf_map,
        "source_case_without_known_false_positive_leaf": {
            row_key: sorted(set(leaves) - known_false_positive_leaves.get(row_key, set()))
            for row_key, leaves in case_leaf_map.items()
        },
    }
    no_fp_companion: dict[str, list[int]] = {packet_row: packet_leaves}
    fp_only_companion: dict[str, list[int]] = {packet_row: packet_leaves}
    for row_key in companion_rows:
        leaves = set(case_leaf_map.get(row_key) or [])
        no_fp_companion[row_key] = sorted(leaves - known_false_positive_leaves.get(row_key, set()))
        fp_only_companion[row_key] = sorted(leaves & known_false_positive_leaves.get(row_key, set()))
        for leaf in sorted(leaves - known_false_positive_leaves.get(row_key, set())):
            variants[f"packet_plus_{row_key.rsplit(':', 1)[-1]}_leaf{leaf}"] = {
                packet_row: packet_leaves,
                row_key: [leaf],
            }
    variants["packet_plus_companion_without_false_positive_leaf"] = no_fp_companion
    variants["packet_plus_companion_false_positive_leaf_only"] = fp_only_companion
    return variants


def determine_claim(variants: list[dict[str, Any]]) -> str:
    verified = [variant for variant in variants if variant["verified"]]
    verified_without_false_leaf = [
        variant for variant in verified if not variant["uses_known_false_positive_leaf"]
    ]
    verified_with_false_leaf = [
        variant for variant in verified if variant["uses_known_false_positive_leaf"]
    ]
    if verified_without_false_leaf:
        return "P848_MULTIROOT_COMPLETION_WITHOUT_FALSE_POSITIVE_LEAF"
    if verified_with_false_leaf:
        return "P848_MULTIROOT_COMPLETION_REQUIRES_REJECTED_FALSE_POSITIVE_LEAF"
    return "NEGATIVE_RESULT_P848_MULTIROOT_COMPLETION_NOT_FOUND"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p846 = load_json(args.p846)
    p847 = load_json(args.p847)
    packet = find_obstruction_packet(p846, p847)
    public_payload = load_json(Path(packet["public_source"]))
    source_case = source_case_for_packet(public_payload, packet)
    packet_source_row = source_row_for_packet(public_payload, packet)
    same_transfer_rows = transfer_source_rows(public_payload, packet)
    known_false_positive_leaves = false_positive_leaves(same_transfer_rows)
    case_leaf_map = leaf_map_from_case(source_case)
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()
    built_by_row, components_by_row, local_args_by_row = build_context(
        verifier,
        records,
        public_payload,
        source_case,
    )
    variants = [
        evaluate_variant(
            verifier,
            name,
            leaves_by_row,
            built_by_row,
            components_by_row,
            local_args_by_row,
            known_false_positive_leaves,
        )
        for name, leaves_by_row in build_variants(
            packet,
            packet_source_row,
            case_leaf_map,
            known_false_positive_leaves,
        ).items()
    ]
    verified = [variant for variant in variants if variant["verified"]]
    verified_without_false_leaf = [
        variant for variant in verified if not variant["uses_known_false_positive_leaf"]
    ]
    verified_with_false_leaf = [
        variant for variant in verified if variant["uses_known_false_positive_leaf"]
    ]
    best_no_false = sorted(
        [variant for variant in variants if not variant["uses_known_false_positive_leaf"]],
        key=lambda item: (
            not item["verified"],
            -int_value(item["union"].get("union_rank")),
            float(item["ops_over_rho"] or 10**9),
            item["name"],
        ),
    )[0]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p846_source": str(args.p846),
            "p847_source": str(args.p847),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(variants),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "PUBLIC-SOURCE-CASE BOUNDARY: companion leaves come from the transfer-324 public source case; verifier outcomes are used only for audit scoring.",
            "FALSE-POSITIVE BOUNDARY: P843/P845 identified salt167 leaf 65 as the rejected false-positive factor packet; variants report whether they use that leaf.",
            "ROOT-DISAMBIGUATION BOUNDARY: this audit tests leaf/companion completion, not a new root-level kernel that selects one of the two roots inside leaf 65.",
            "POLLARD-RHO BOUNDARY: this is relation-equation bridge evidence for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p848_public_factor_multiroot_companion_audit",
        "obstruction": {
            "case_leaf_map": case_leaf_map,
            "known_false_positive_leaves": {
                row_key: sorted(leaves) for row_key, leaves in known_false_positive_leaves.items()
            },
            "packet_factor_zero_leaf_indices": packet_source_row.get("factor_zero_leaf_indices") or [],
            "packet_row_key": packet["row_key"],
            "target": packet["target"],
            "transfer_index": int_value(packet["transfer_index"]),
        },
        "parameters": {
            "p846_claim": p846.get("claim_status"),
            "p847_claim": (p847.get("summary") or {}).get("claim_status"),
            "success_threshold": "verified completion below rho without using a known false-positive companion leaf",
            "variant_count": len(variants),
        },
        "red_team_handoff": {
            "assumptions": [
                "The P843 false-positive leaf marker is the right guardrail for transfer-324 companion selection.",
                "The source-case leaf set is a legitimate public companion search space, but not a deployable selector by itself.",
                "A verified completion that uses salt167 leaf 65 would reopen the P843 false-positive channel unless a new public discriminator is found.",
            ],
            "failure_modes": [
                "A future discriminator may separate salt167 leaf 65 as relation-useful while still rejecting the factor false-positive interpretation.",
                "The non-false companion leaves reach rank 2 but may need one additional public row outside this source case.",
                "The toy-scale companion dependency may not replicate on fresh disjoint banks.",
            ],
            "next_concrete_action": (
                "Build P849 to search for a public discriminator that permits relation-useful companion leaf 65 only when "
                "it forms a verifying direct-equation group, while still rejecting the P843 false-positive factor packet; "
                "also test one-row-outside-source-case companions for transfer 324."
            ),
            "status": "NEGATIVE RESULT" if not verified_without_false_leaf else "HYPOTHESIS",
        },
        "summary": {
            "best_no_false_positive_leaf_variant": {
                "name": best_no_false["name"],
                "ops_over_rho": best_no_false["ops_over_rho"],
                "union": best_no_false["union"],
            },
            "claim_status": determine_claim(variants),
            "verified_variant_count": len(verified),
            "verified_with_known_false_positive_leaf_count": len(verified_with_false_leaf),
            "verified_without_known_false_positive_leaf_count": len(verified_without_false_leaf),
        },
        "schema": SCHEMA,
        "variants": variants,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p846", type=Path, default=DEFAULT_P846)
    parser.add_argument("--p847", type=Path, default=DEFAULT_P847)
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
