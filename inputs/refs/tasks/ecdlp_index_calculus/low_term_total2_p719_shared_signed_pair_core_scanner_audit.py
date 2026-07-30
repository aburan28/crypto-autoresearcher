#!/usr/bin/env python3
"""P719 replay audit for shared signed-pair cores in P716 two-by-two rel2 attempts."""

from __future__ import annotations

import argparse
import copy
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_guarded_shared_preassociation_timing_probe as shared_timing
import low_term_total2_p716_rel2_source_generation_enrichment as p716
import low_term_total2_p718_cross_window_row_key_reuse_audit as p718
import low_term_total2_p709_source_replay_no_archive_oracle as p709


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_P716 = STATE_DIR / "low_term_total2_p716_rel2_source_generation_enrichment_probe.json"
DEFAULT_P718 = STATE_DIR / "low_term_total2_p718_cross_window_row_key_reuse_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p719_shared_signed_pair_core_scanner_audit_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p716.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p716.float_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def compact_event_form(event: dict[str, Any]) -> dict[str, Any]:
    coeffs, rhs, terms = event["form"]
    return {
        "coeffs": [int_value(coeff) for coeff in coeffs],
        "rhs": int_value(rhs),
        "terms": [int_value(term) for term in terms],
    }


def normalized_event_forms(scan: dict[str, Any]) -> list[dict[str, Any]]:
    forms = [compact_event_form(event) for event in scan.get("_events") or scan.get("relation_events") or []]
    return sorted(forms, key=lambda item: (item["coeffs"], item["rhs"], item["terms"]))


def context_with_shared_scouts(context: dict[str, Any], shared_scouts: list[dict[str, Any]]) -> dict[str, Any]:
    built = dict(context["built"])
    built["scouts"] = shared_scouts
    return {**context, "built": built}


def scan_with_cover(
    verifier: Any,
    context: dict[str, Any],
    cover: dict[str, Any],
    max_relations: int,
) -> dict[str, Any]:
    scan = shared_timing.scan_from_cover(verifier, context, cover, max_relations)
    if "relation_events" not in scan and "_events" in scan:
        scan = {**scan, "relation_events": scan.get("_events") or []}
    return scan


def direct_cover(context: dict[str, Any]) -> dict[str, Any]:
    built = context["built"]
    return shared_timing.selected_leaf_association(
        built["scouts"],
        context["components"],
        int_value(built.get("p")),
        context["selected_leaf_indices"],
    )


def shared_cover(context: dict[str, Any], shared_scouts: list[dict[str, Any]]) -> dict[str, Any]:
    built = context["built"]
    return shared_timing.selected_leaf_association(
        shared_scouts,
        context["components"],
        int_value(built.get("p")),
        context["selected_leaf_indices"],
    )


def cost_parts(profile: dict[str, Any]) -> dict[str, int]:
    parts = profile.get("cost_parts") or {}
    return {key: int_value(parts.get(key)) for key in p718.COMPONENT_KEYS}


def reconstructed_ops(profile: dict[str, Any]) -> int:
    parts = profile.get("cost_parts") or {}
    scan = profile.get("scan") or {}
    return int_value(
        parts.get("reconstructed_preassociation_filter_ops"),
        int_value(scan.get("preassociation_filter_ops")),
    )


def compact_context_record(record: dict[str, Any]) -> dict[str, Any]:
    profile = record.get("profile") or {}
    return {
        "challenge_seed": profile.get("challenge_seed"),
        "context_index": int_value(record.get("context_index")),
        "cost_parts": profile.get("cost_parts") or {},
        "core_fingerprint": record.get("core_fingerprint"),
        "row_key": profile.get("row_key"),
        "row_pool_fingerprint": profile.get("row_pool_fingerprint"),
        "selected_leaf_indices": profile.get("selected_leaf_indices") or [],
        "selected_leaf_signature_keys": profile.get("selected_leaf_signature_keys") or [],
    }


def reconstruct_attempts(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    build_args = argparse.Namespace(
        max_transfer=args.max_transfer,
        min_transfer=args.min_transfer,
        p709=args.p709,
        source_pattern=args.source_pattern,
        target=args.target,
        thresholds="0.544,0.568,0.616,1.0",
    )
    reports, metadata = p716.build_window_reports(build_args)
    policy = p716.SourcePolicy("two_by_two_any_cost_le_1p0", "two_by_two_any", 1.0)
    attempts: list[dict[str, Any]] = []
    for report in reports:
        accepted = [row for row in report["candidates"] if p716.policy_accepts(policy, row)]
        accepted.sort(key=p716.row_sort_key)
        if not accepted:
            continue
        candidate = accepted[0]
        source = metadata["source_cache"][str(candidate["source"])]
        verifier, contexts, product_factor, max_relations = p709.direct_source.timing_probe.selected_contexts_from_source_case(
            source,
            candidate["source_case"],
        )
        direct_rows, direct_ops, rho, row_profiles = p709.direct_source.timing_probe.direct_witness_rows(
            verifier,
            contexts,
        )
        built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
        direct_union = p709.direct_source.direct_witness_probe.union_derive(
            verifier,
            direct_rows,
            built_by_row,
            "_scan",
        )
        context_records = []
        for index, (context, profile) in enumerate(zip(contexts, row_profiles)):
            context_records.append(
                {
                    "context": context,
                    "context_index": index,
                    "core_fingerprint": p718.signed_pair_core_fingerprint(context["built"]),
                    "profile": profile,
                }
            )
        attempts.append(
            {
                "attempt_index": len(attempts),
                "candidate": candidate,
                "contexts": context_records,
                "direct_ops": direct_ops,
                "direct_ops_over_rho": ratio(direct_ops, rho),
                "direct_union": direct_union,
                "max_relations": max_relations,
                "product_factor": product_factor,
                "rho": rho,
                "source": str(candidate["source"]),
                "window_end": report["window_end"],
                "window_start": report["window_start"],
            }
        )
    return attempts, {
        "candidate_window_count": sum(1 for report in reports if report["candidates"]),
        "source_window_count": len(reports),
    }


def attempt_shared_scan(attempt: dict[str, Any]) -> dict[str, Any]:
    verifier = None
    contexts = [record["context"] for record in attempt["contexts"]]
    if contexts:
        # selected_contexts_from_source_case has already built a verifier-compatible context;
        # the scanner only needs the verifier object for relation derivation.
        source = p718.load_json(Path(attempt["source"]))
        verifier, _contexts, _product_factor, _max_relations = p709.direct_source.timing_probe.selected_contexts_from_source_case(
            source,
            attempt["candidate"]["source_case"],
        )
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in attempt["contexts"]:
        groups[str(record["core_fingerprint"])].append(record)
    direct_scan_rows = []
    shared_scan_rows = []
    group_reports = []
    cover_mismatch_count = 0
    event_mismatch_count = 0
    for core_key, members in sorted(groups.items(), key=lambda item: item[0]):
        shared_scouts = members[0]["context"]["built"]["scouts"]
        core_signed_pair_ops = min(
            int_value((record["profile"].get("cost_parts") or {}).get("selected_signed_pair_ops"))
            for record in members
        )
        residual_ops = 0
        member_reports = []
        for record in members:
            context = record["context"]
            profile = record["profile"]
            direct = direct_cover(context)
            shared = shared_cover(context, shared_scouts)
            direct_normalized = shared_timing.normalized_cover(direct)
            shared_normalized = shared_timing.normalized_cover(shared)
            direct_scan = scan_with_cover(verifier, context, direct, int_value(attempt.get("max_relations")))
            shared_context = context_with_shared_scouts(context, shared_scouts)
            shared_scan = scan_with_cover(verifier, shared_context, shared, int_value(attempt.get("max_relations")))
            direct_events = normalized_event_forms(direct_scan)
            shared_events = normalized_event_forms(shared_scan)
            cover_match = direct_normalized == shared_normalized
            event_match = direct_events == shared_events
            if not cover_match:
                cover_mismatch_count += 1
            if not event_match:
                event_mismatch_count += 1
            direct_scan_rows.append({"row_key": context["row_key"], "_scan": direct_scan})
            shared_scan_rows.append({"row_key": context["row_key"], "_scan": shared_scan})
            parts = cost_parts(profile)
            residual_ops += reconstructed_ops(profile) - int_value(parts.get("selected_signed_pair_ops"))
            member_reports.append(
                {
                    **compact_context_record(record),
                    "cover_match": cover_match,
                    "direct_event_count": len(direct_events),
                    "event_match": event_match,
                    "shared_event_count": len(shared_events),
                }
            )
        group_reports.append(
            {
                "core_fingerprint": core_key,
                "core_signed_pair_ops_charged_once": core_signed_pair_ops,
                "member_count": len(members),
                "members": member_reports,
                "residual_ops": residual_ops,
                "shared_core_ops": core_signed_pair_ops + residual_ops,
            }
        )
    built_by_row = {str(record["context"]["row_key"]): record["context"]["built"] for record in attempt["contexts"]}
    direct_union = p709.direct_source.direct_witness_probe.union_derive(
        verifier,
        direct_scan_rows,
        built_by_row,
        "_scan",
    )
    shared_union = p709.direct_source.direct_witness_probe.union_derive(
        verifier,
        shared_scan_rows,
        built_by_row,
        "_scan",
    )
    union_match = {
        "derived_secret": direct_union.get("union_derived_secret") == shared_union.get("union_derived_secret"),
        "public_key_verified": bool(direct_union.get("union_public_key_verified"))
        == bool(shared_union.get("union_public_key_verified")),
        "rank": int_value(direct_union.get("union_rank")) == int_value(shared_union.get("union_rank")),
        "relation_count": int_value(direct_union.get("union_relation_count"))
        == int_value(shared_union.get("union_relation_count")),
    }
    independent_ops = sum(reconstructed_ops(record["profile"]) for record in attempt["contexts"])
    shared_ops = sum(int_value(group.get("shared_core_ops")) for group in group_reports)
    return {
        "attempt_index": attempt["attempt_index"],
        "cover_mismatch_count": cover_mismatch_count,
        "direct_hit": bool(direct_union.get("union_public_key_verified")),
        "direct_ops": independent_ops,
        "direct_union": direct_union,
        "event_mismatch_count": event_mismatch_count,
        "group_count": len(group_reports),
        "groups": group_reports,
        "hit_match": union_match["public_key_verified"],
        "rank": int_value(direct_union.get("union_rank")),
        "rho": int_value(attempt.get("rho")),
        "shared_hit": bool(shared_union.get("union_public_key_verified")),
        "shared_ops": shared_ops,
        "shared_union": shared_union,
        "source": attempt.get("source"),
        "union_match": union_match,
        "union_matches_all_fields": all(union_match.values()),
        "window_start": attempt.get("window_start"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    p718_payload = load_json(Path(args.p718))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    attempts, meta = reconstruct_attempts(args)
    attempt_reports = [attempt_shared_scan(attempt) for attempt in attempts]
    rhos = sorted({int_value(report.get("rho")) for report in attempt_reports if int_value(report.get("rho"))})
    rho = rhos[0] if len(rhos) == 1 else max(rhos, default=0)
    direct_hit_count = sum(1 for report in attempt_reports if report.get("direct_hit"))
    shared_hit_count = sum(1 for report in attempt_reports if report.get("shared_hit"))
    fallback_over_rho = float_value(meta["source_window_count"] - shared_hit_count)
    direct_ops = sum(int_value(report.get("direct_ops")) for report in attempt_reports)
    shared_ops = sum(int_value(report.get("shared_ops")) for report in attempt_reports)
    direct_source_over_rho = ratio(direct_ops, rho)
    shared_source_over_rho = ratio(shared_ops, rho)
    shared_plus_fallback = round(float_value(shared_source_over_rho) + fallback_over_rho, 8)
    shared_new_bank_total = round(shared_plus_fallback + factor_charge, 8)
    all_covers_match = all(int_value(report.get("cover_mismatch_count")) == 0 for report in attempt_reports)
    all_events_match = all(int_value(report.get("event_mismatch_count")) == 0 for report in attempt_reports)
    all_unions_match = all(report.get("union_matches_all_fields") for report in attempt_reports)
    below_rho_marginal = bool(shared_plus_fallback < meta["source_window_count"])
    below_rho_new_bank = bool(shared_new_bank_total < meta["source_window_count"])
    if all_covers_match and all_events_match and all_unions_match and below_rho_marginal:
        claim_status = "P719_REPLAY_BACKED_SHARED_SIGNED_PAIR_CORE_BELOW_RHO_ON_P716_SURFACE"
    elif all_covers_match and all_events_match and all_unions_match:
        claim_status = "P719_SHARED_SIGNED_PAIR_CORE_REPLAY_MATCHES_BUT_COST_ABOVE_RHO"
    else:
        claim_status = "NEGATIVE_RESULT_P719_SHARED_SIGNED_PAIR_CORE_REPLAY_MISMATCH"
    summary = {
        "all_covers_match": all_covers_match,
        "all_events_match": all_events_match,
        "all_unions_match": all_unions_match,
        "attempt_count": len(attempt_reports),
        "direct_hit_count": direct_hit_count,
        "direct_source_charge_ops": direct_ops,
        "direct_source_charge_over_rho": direct_source_over_rho,
        "direct_source_plus_fallback_over_rho": round(float_value(direct_source_over_rho) + float_value(meta["source_window_count"] - direct_hit_count), 8),
        "factor_bank_charge_over_rho": factor_charge,
        "fallback_charge_over_rho": fallback_over_rho,
        "p718_claim_status": p718_payload.get("claim_status"),
        "p718_signed_core_source_plus_fallback_over_rho": next(
            (
                model.get("source_plus_fallback_over_rho")
                for model in p718_payload.get("reuse_models") or []
                if model.get("model") == "exact_signed_pair_core_reuse"
            ),
            None,
        ),
        "rho": rho,
        "rho_baseline_over_rho": meta["source_window_count"],
        "shared_below_rho_marginal": below_rho_marginal,
        "shared_below_rho_new_bank": below_rho_new_bank,
        "shared_hit_count": shared_hit_count,
        "shared_new_bank_total_over_rho": shared_new_bank_total,
        "shared_source_charge_ops": shared_ops,
        "shared_source_charge_over_rho": shared_source_over_rho,
        "shared_source_plus_fallback_over_rho": shared_plus_fallback,
        "signed_pair_core_group_count": sum(int_value(report.get("group_count")) for report in attempt_reports),
        "source_window_count": meta["source_window_count"],
        "total_cover_mismatch_count": sum(int_value(report.get("cover_mismatch_count")) for report in attempt_reports),
        "total_event_mismatch_count": sum(int_value(report.get("event_mismatch_count")) for report in attempt_reports),
        "union_mismatch_count": sum(1 for report in attempt_reports if not report.get("union_matches_all_fields")),
        "unique_rhos": rhos,
    }
    return {
        "artifacts": {
            "p709": str(Path(args.p709)),
            "p716": str(Path(args.p716)),
            "p718": str(Path(args.p718)),
        },
        "attempt_reports": attempt_reports,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source-generator stress rows outside the P709 source map, not live fresh harvesting.",
            "The shared scanner reuses an exact scout/signed-pair list inside each two-row attempt and checks covers, event forms, and union derivation against direct replay.",
            "The rho comparison is an operation ledger, not wall-clock calibration.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "method": "p719_shared_signed_pair_core_scanner_audit",
        "parameters": {
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "policy": "two_by_two_any_cost_le_1p0:budget1",
            "source_pattern": args.source_pattern,
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p719_shared_signed_pair_core_scanner_audit.v1",
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p716", default=str(DEFAULT_P716))
    parser.add_argument("--p718", default=str(DEFAULT_P718))
    parser.add_argument("--source-pattern", default=p716.p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
