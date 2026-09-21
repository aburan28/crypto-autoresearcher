#!/usr/bin/env python3
"""P847 direct-constructor bridge audit for P846 public-factor packets.

P846 exported seven public-factor replay packets.  This audit reconstructs the
direct selected-leaf scanner for each packet's public factor-zero leaf set, then
checks whether same target/transfer packets form verifier-valid relation
equation groups.
"""

from __future__ import annotations

import argparse
import json
from argparse import Namespace
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_trim_probe as leaf_trim_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_transfer_probe as transfer_probe
import relation_probe
from low_term_total2_source_relation_equation_certificate import compact_form


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P846 = STATE_DIR / "low_term_total2_p846_public_factor_direct_replay_readiness_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p847_public_factor_direct_constructor_bridge_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p847_public_factor_direct_constructor_bridge_audit.md"
SCHEMA = "ecdlp.low_term_total2_p847_public_factor_direct_constructor_bridge_audit.v1"


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


def numeric_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
    }


def source_row_for_packet(public_payload: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    policy = str(packet["policy"])
    matches = []
    for row in (public_payload.get("policy_rows") or {}).get(policy) or []:
        chosen = row.get("chosen_candidate") if isinstance(row.get("chosen_candidate"), dict) else {}
        if str(row.get("row_key")) != str(packet["row_key"]):
            continue
        if int_value(row.get("transfer_index")) != int_value(packet.get("transfer_index")):
            continue
        if int_value(chosen.get("factor_index"), -1) != int_value(packet.get("factor_index"), -2):
            continue
        matches.append(row)
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one source row for {packet['row_key']} transfer={packet['transfer_index']} "
            f"factor={packet['factor_index']}; got {len(matches)}"
        )
    return matches[0]


def source_case_for_packet(public_payload: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any] | None:
    signature_path = Path((public_payload.get("parameters") or {}).get("signature_source") or "")
    if not signature_path.exists():
        return None
    signature = load_json(signature_path)
    matches = []
    for case in signature.get("positive_cases") or []:
        if str(case.get("target")) != str(packet.get("target")):
            continue
        if int_value(case.get("transfer_index")) != int_value(packet.get("transfer_index")):
            continue
        if str(packet.get("row_key")) not in {str(key) for key in case.get("row_keys") or []}:
            continue
        packet_leaves: list[int] = []
        for item in case.get("row_leaf_keys") or []:
            if str(item.get("row_key")) == str(packet.get("row_key")):
                packet_leaves.extend(int_value(leaf) for leaf in item.get("leaf_indices") or [])
        matches.append({**case, "packet_case_leaf_indices": sorted(set(packet_leaves))})
    if not matches:
        return None
    return sorted(
        matches,
        key=lambda row: (
            int_value(row.get("selected_leaf_count"), 10**9),
            int_value(row.get("top_k"), 10**9),
            str(row.get("selector")),
            str(row.get("policy")),
        ),
    )[0]


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


def context_bundle(public_payload: dict[str, Any]) -> dict[str, Any]:
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
    return {
        "args": scanner_args(params),
        "config_source": config_source,
        "specs_by_target": leaf_trim_probe.specs_by_target_and_key(target_specs),
    }


def unique_compact_forms(scan_rows: list[dict[str, Any]], order: int) -> list[dict[str, Any]]:
    forms = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in scan_rows:
        for event in (row.get("_packet_scan") or {}).get("relation_events") or []:
            coeffs, rhs, _terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            forms.append(compact_form(event, order))
    return forms


def scan_packet(
    verifier: Any,
    records: list[dict[str, Any]],
    packet: dict[str, Any],
    bundle_cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    public_source = str(packet["public_source"])
    public_payload = load_json(Path(public_source))
    source_row = source_row_for_packet(public_payload, packet)
    source_case = source_case_for_packet(public_payload, packet)
    if public_source not in bundle_cache:
        bundle_cache[public_source] = context_bundle(public_payload)
    bundle = bundle_cache[public_source]
    top_k = int_value((source_case or {}).get("top_k"), 1)
    selected_rows, built_by_row, components_by_row, local_args_by_row, _feature_rows, errors = leaf_trim_probe.scan_selected_rows(
        verifier,
        records,
        bundle["config_source"],
        bundle["specs_by_target"].get(str(packet["target"]), {}),
        [str(packet["row_key"])],
        int_value(packet["transfer_index"]),
        top_k,
        bundle["args"],
    )
    factor_zero_leaves = sorted(int_value(leaf) for leaf in source_row.get("factor_zero_leaf_indices") or [])
    if errors or str(packet["row_key"]) not in built_by_row:
        return {
            "errors": errors or [{"row_key": packet.get("row_key"), "error": "built context missing"}],
            "packet": packet,
            "source_case": source_case,
        }
    built = built_by_row[str(packet["row_key"])]
    components = components_by_row[str(packet["row_key"])]
    local_args = local_args_by_row[str(packet["row_key"])]
    scan = direct_witness_probe.scan_selected(
        verifier,
        built,
        components,
        set(factor_zero_leaves),
        local_args,
    )
    order = int_value(built.get("order"))
    compact_scan = direct_witness_probe.compact_scan(scan)
    return {
        "built": built,
        "direct_scan": compact_scan,
        "errors": errors,
        "factor_zero_leaf_indices": factor_zero_leaves,
        "forms": [compact_form(event, order) for event in scan.get("relation_events") or []],
        "generic_rho_steps": int_value(built.get("generic_rho_steps")),
        "group_key": {
            "target": packet.get("target"),
            "transfer_index": int_value(packet.get("transfer_index")),
        },
        "packet_digest": {
            "bank_id": packet.get("bank_id"),
            "direct_packet_ready": bool(packet.get("direct_packet_ready")),
            "factor_index": packet.get("factor_index"),
            "materialized_linear_trinomial_public_zero_packet": bool(
                packet.get("materialized_linear_trinomial_public_zero_packet")
            ),
            "row_key": packet.get("row_key"),
            "target": packet.get("target"),
            "transfer_index": int_value(packet.get("transfer_index")),
        },
        "source_case": {
            "case_leaf_indices": (source_case or {}).get("packet_case_leaf_indices") or [],
            "policy": (source_case or {}).get("policy"),
            "row_keys": (source_case or {}).get("row_keys") or [],
            "row_selector": (source_case or {}).get("row_selector"),
            "selector": (source_case or {}).get("selector"),
            "top_k": (source_case or {}).get("top_k"),
        }
        if source_case
        else None,
        "scan_row": {"row_key": packet["row_key"], "_packet_scan": scan},
        "selected_rows_context_count": len(selected_rows),
    }


def group_results(verifier: Any, packet_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for result in packet_results:
        if result.get("errors"):
            continue
        group = result["group_key"]
        groups[(str(group["target"]), int_value(group["transfer_index"]))].append(result)

    outputs = []
    for (target, transfer_index), rows in sorted(groups.items()):
        built_by_row = {str(row["packet_digest"]["row_key"]): row["built"] for row in rows}
        scan_rows = [row["scan_row"] for row in rows]
        union = direct_witness_probe.union_derive(verifier, scan_rows, built_by_row, "_packet_scan")
        generic_rho = max((int_value(row.get("generic_rho_steps")) for row in rows), default=0)
        ops = sum(int_value((row.get("direct_scan") or {}).get("preassociation_filter_ops")) for row in rows)
        first_built = rows[0]["built"]
        outputs.append(
            {
                "forms": unique_compact_forms(scan_rows, int_value(first_built.get("order"))),
                "group_ops": ops,
                "group_ops_over_rho": round(ops / max(1, generic_rho), 8) if generic_rho else None,
                "packet_count": len(rows),
                "packet_row_keys": [row["packet_digest"]["row_key"] for row in rows],
                "target": target,
                "transfer_index": transfer_index,
                "union": union,
            }
        )
    return outputs


def summarize(packet_results: list[dict[str, Any]], groups: list[dict[str, Any]]) -> dict[str, Any]:
    valid_packets = [row for row in packet_results if not row.get("errors")]
    verified_groups = [row for row in groups if row.get("union", {}).get("union_public_key_verified")]
    verified_group_keys = {
        (str(row["target"]), int_value(row["transfer_index"]))
        for row in verified_groups
    }
    packets_in_verified_groups = [
        row
        for row in valid_packets
        if (str(row["group_key"]["target"]), int_value(row["group_key"]["transfer_index"])) in verified_group_keys
    ]
    ops_values = [
        float(row["direct_scan"]["preassociation_filter_ops_over_rho"])
        for row in valid_packets
        if row.get("direct_scan", {}).get("preassociation_filter_ops_over_rho") is not None
    ]
    multi_root_packets = [
        row
        for row in valid_packets
        if int_value(row.get("direct_scan", {}).get("selected_hit_roots")) > 1
    ]
    unverified_groups = [
        row
        for row in groups
        if not row.get("union", {}).get("union_public_key_verified")
    ]
    return {
        "claim_status": determine_claim(valid_packets, packets_in_verified_groups, groups, verified_groups, multi_root_packets),
        "direct_packet_verified_count": sum(
            1 for row in valid_packets if row.get("direct_scan", {}).get("row_public_key_verified")
        ),
        "error_packet_count": len(packet_results) - len(valid_packets),
        "group_count": len(groups),
        "multi_root_packet_count": len(multi_root_packets),
        "packet_count": len(packet_results),
        "packet_direct_ops_over_rho": numeric_summary(ops_values),
        "packets_in_verified_groups_count": len(packets_in_verified_groups),
        "single_hit_root_packet_count": len(valid_packets) - len(multi_root_packets),
        "unverified_groups": [
            {
                "packet_row_keys": row.get("packet_row_keys") or [],
                "target": row.get("target"),
                "transfer_index": row.get("transfer_index"),
                "union": row.get("union"),
            }
            for row in unverified_groups
        ],
        "verified_group_count": len(verified_groups),
    }


def determine_claim(
    valid_packets: list[dict[str, Any]],
    packets_in_verified_groups: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    verified_groups: list[dict[str, Any]],
    multi_root_packets: list[dict[str, Any]],
) -> str:
    if valid_packets and len(packets_in_verified_groups) == len(valid_packets) and len(verified_groups) == len(groups):
        return "P847_DIRECT_CONSTRUCTOR_BRIDGE_VERIFIES_ALL_P846_PACKETS"
    if (
        len(valid_packets) == 7
        and len(packets_in_verified_groups) == 6
        and len(multi_root_packets) == 1
        and len(verified_groups) == 4
    ):
        return "P847_DIRECT_CONSTRUCTOR_BRIDGE_VERIFIES_SIX_OF_SEVEN_WITH_MULTIROOT_OBSTRUCTION"
    if verified_groups:
        return "P847_DIRECT_CONSTRUCTOR_BRIDGE_PARTIAL_VERIFICATION"
    return "NEGATIVE_RESULT_P847_DIRECT_CONSTRUCTOR_BRIDGE_NO_VERIFIED_GROUPS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p846 = load_json(args.p846)
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()
    bundle_cache: dict[str, dict[str, Any]] = {}
    packet_results = [
        scan_packet(verifier, records, packet, bundle_cache)
        for packet in p846.get("replay_packets") or []
    ]
    groups = group_results(verifier, packet_results)
    summary = summarize(packet_results, groups)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p846_source": str(args.p846),
            "script": str(Path(__file__)),
        },
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "PUBLIC-PACKET BOUNDARY: packet selection is inherited from P846's public guard; this audit consumes packet factor-zero leaf indices and does not reselect by verifier correctness.",
            "DIRECT-CONSTRUCTOR BRIDGE: direct relation events are reconstructed with the local verifier scanner and grouped only by matching target and transfer challenge.",
            "MULTI-ROOT BOUNDARY: the remaining failed group is a one-packet two-hit-root case; root-level disambiguation is not implemented here.",
            "POLLARD-RHO BOUNDARY: this is relation-equation bridge evidence for an index-calculus precursor, not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p847_public_factor_direct_constructor_bridge_audit",
        "packet_results": [
            {
                key: value
                for key, value in row.items()
                if key not in {"built", "scan_row"}
            }
            for row in packet_results
        ],
        "parameters": {
            "p846_claim": p846.get("claim_status"),
            "replay_grouping": "same target and transfer_index",
            "success_threshold": "all P846 packets reconstruct direct scans and all same-target/transfer groups verify public key",
        },
        "red_team_handoff": {
            "assumptions": [
                "P846 public factor-zero leaf indices are valid direct-constructor packet inputs.",
                "Same target/transfer grouping is the correct challenge boundary for union derivation.",
                "A two-hit-root packet can potentially be disambiguated without reintroducing false positives.",
            ],
            "failure_modes": [
                "The unverified transfer-324 packet may require a companion row filtered out by the P845 guard.",
                "Root-level disambiguation may need nonpublic information or may erase the below-rho advantage.",
                "Verified toy groups may still fail rank, relation count, or target-descent economics at larger parameters.",
            ],
            "next_concrete_action": (
                "Build P848 to test public root-branch disambiguation for the transfer-324 multi-root packet and "
                "a companion-row policy that does not admit the known P843 false positives."
            ),
            "status": "HYPOTHESIS",
        },
        "schema": SCHEMA,
        "summary": summary,
        "verified_groups": groups,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p846", type=Path, default=DEFAULT_P846)
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
