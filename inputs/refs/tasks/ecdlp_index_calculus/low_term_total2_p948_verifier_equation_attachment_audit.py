#!/usr/bin/env python3
"""P948 verifier-equation attachment audit for P947 selected rows."""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tasks.ecdlp_index_calculus.low_term_total2_p942_hash_context_discriminator import (
    P939_SOURCE,
    int_value,
    load_json,
    load_rows,
    now_iso,
    window_start,
    write_json,
)
from tasks.ecdlp_index_calculus.low_term_total2_p947_chronology_rank_descent_audit import (
    modular_rank,
    select_rows,
    sorted_windows,
)


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p948_verifier_equation_attachment_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p948_verifier_equation_attachment_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p948_verifier_equation_attachment_audit.v1"

CANDIDATE_ARTIFACTS = [
    STATE_DIR / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_materialization_probe.json",
    STATE_DIR / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_probe.json",
    STATE_DIR / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe.json",
    STATE_DIR / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_minimize_probe.json",
    STATE_DIR / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_compress_probe.json",
]


def selected_p947_rows() -> list[dict[str, Any]]:
    rows_by_window, _artifact_summary = load_rows(P939_SOURCE)
    windows = sorted_windows(rows_by_window)
    selected: list[dict[str, Any]] = []
    for index, window in enumerate(windows):
        train_rows = [row for train_window in windows[:index] for row in rows_by_window[train_window]]
        selected.extend(select_rows("p945_guarded_same_hash_transfer_mod2_even_holdout", train_rows, rows_by_window[window]))
    return sorted(selected, key=lambda row: (window_start(str(row.get("window"))), int_value(row.get("transfer_index")), str(row.get("row_key"))))


def parse_challenge_seed(surface_id: Any) -> str | None:
    text = str(surface_id or "")
    parts = text.split("|")
    if len(parts) >= 3:
        return parts[2]
    return None


def compact_selected(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "b_coeff": row.get("b_coeff"),
        "c_coeff": row.get("c_coeff"),
        "constant": row.get("constant"),
        "hash": row.get("hash"),
        "p947_challenge_seed": parse_challenge_seed(row.get("surface_id")),
        "row_key": row.get("row_key"),
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "target_prime": row.get("target_prime"),
        "transfer_index": row.get("transfer_index"),
        "window": row.get("window"),
    }


def update_context(context: dict[str, Any], obj: dict[str, Any]) -> dict[str, Any]:
    out = dict(context)
    for key in [
        "base_order",
        "challenge_key",
        "challenge_mode",
        "challenge_seed",
        "public_key_verified",
        "target",
        "transfer_index",
    ]:
        if key in obj and obj.get(key) is not None:
            out[key] = obj.get(key)
    return out


def form_payload(obj: dict[str, Any]) -> dict[str, Any] | None:
    form = obj.get("form")
    if isinstance(form, dict) and isinstance(form.get("coeffs"), list) and form.get("rhs") is not None:
        return {
            "coeffs": [int_value(value) for value in form.get("coeffs")],
            "rhs": int_value(form.get("rhs")),
            "terms": form.get("terms") or [],
        }
    return None


def has_reconstructible_payload(obj: dict[str, Any]) -> bool:
    if form_payload(obj) is not None:
        return True
    if isinstance(obj.get("relations"), list) and obj.get("base_order") is not None:
        return True
    if isinstance(obj.get("event_summaries"), list) and obj.get("base_order") is not None:
        return True
    return False


def collect_records_from_artifact(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    records: list[dict[str, Any]] = []

    def walk(obj: Any, context: dict[str, Any], trace: str) -> None:
        if isinstance(obj, dict):
            local_context = update_context(context, obj)
            row_key = obj.get("row_key")
            surface_id = obj.get("surface_id")
            if row_key or surface_id:
                form = form_payload(obj)
                record = {
                    "artifact": str(path),
                    "artifact_name": path.name,
                    "base_order": local_context.get("base_order"),
                    "challenge_key": local_context.get("challenge_key"),
                    "challenge_mode": local_context.get("challenge_mode"),
                    "challenge_seed": local_context.get("challenge_seed"),
                    "form": form,
                    "has_explicit_form": form is not None,
                    "has_reconstructible_payload": has_reconstructible_payload(obj),
                    "materialized_relation_count": obj.get("materialized_relation_count"),
                    "path": trace,
                    "public_key_verified": local_context.get("public_key_verified"),
                    "rank": obj.get("rank") if obj.get("rank") is not None else obj.get("materialized_rank"),
                    "relation_count": obj.get("relation_count") if obj.get("relation_count") is not None else obj.get("materialized_relation_count"),
                    "row_key": row_key,
                    "selected_leaf_indices": obj.get("selected_leaf_indices"),
                    "surface_id": surface_id,
                    "target": obj.get("target") if obj.get("target") is not None else local_context.get("target"),
                    "transfer_index": obj.get("transfer_index") if obj.get("transfer_index") is not None else local_context.get("transfer_index"),
                }
                records.append(record)
            for key, value in obj.items():
                walk(value, local_context, f"{trace}.{key}" if trace else str(key))
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, context, f"{trace}[{index}]")

    walk(payload, {}, "")
    return records


def build_attachments(artifacts: list[Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    artifact_summaries: dict[str, Any] = {}
    for path in artifacts:
        if not path.exists():
            artifact_summaries[str(path)] = {"exists": False, "record_count": 0}
            continue
        artifact_records = collect_records_from_artifact(path)
        records.extend(artifact_records)
        artifact_summaries[str(path)] = {
            "exists": True,
            "explicit_form_record_count": sum(1 for record in artifact_records if record.get("has_explicit_form")),
            "record_count": len(artifact_records),
            "reconstructible_payload_count": sum(1 for record in artifact_records if record.get("has_reconstructible_payload")),
            "row_key_count": len({record.get("row_key") for record in artifact_records if record.get("row_key")}),
            "transfer_index_count": len({record.get("transfer_index") for record in artifact_records if record.get("transfer_index") is not None}),
        }
    return records, artifact_summaries


def record_ref(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_name": record.get("artifact_name"),
        "base_order": record.get("base_order"),
        "challenge_seed": record.get("challenge_seed"),
        "has_explicit_form": bool(record.get("has_explicit_form")),
        "has_reconstructible_payload": bool(record.get("has_reconstructible_payload")),
        "path": record.get("path"),
        "public_key_verified": record.get("public_key_verified"),
        "rank": record.get("rank"),
        "relation_count": record.get("relation_count"),
        "row_key": record.get("row_key"),
        "target": record.get("target"),
        "transfer_index": record.get("transfer_index"),
    }


def summarize_matches(selected_rows: list[dict[str, Any]], records: list[dict[str, Any]]) -> dict[str, Any]:
    by_row_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_surface_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_row_transfer: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record.get("row_key"):
            by_row_key[str(record["row_key"])].append(record)
        if record.get("surface_id"):
            by_surface_id[str(record["surface_id"])].append(record)
        if record.get("row_key") and record.get("transfer_index") is not None:
            by_row_transfer[(str(record["row_key"]), int(record["transfer_index"]))].append(record)

    selected_details: list[dict[str, Any]] = []
    exact_transfer_form_records: list[dict[str, Any]] = []
    exact_transfer_payload_records: list[dict[str, Any]] = []
    row_key_only_payload_records: list[dict[str, Any]] = []
    for row in selected_rows:
        row_key = str(row.get("row_key"))
        transfer = int_value(row.get("transfer_index"))
        exact_surface = by_surface_id.get(str(row.get("surface_id")), [])
        exact_transfer = by_row_transfer.get((row_key, transfer), [])
        row_key_matches = by_row_key.get(row_key, [])
        row_key_only = [
            record
            for record in row_key_matches
            if record.get("transfer_index") is None or int_value(record.get("transfer_index")) != transfer
        ]
        exact_transfer_form_records.extend([record for record in exact_transfer if record.get("has_explicit_form")])
        exact_transfer_payload_records.extend([record for record in exact_transfer if record.get("has_reconstructible_payload")])
        row_key_only_payload_records.extend([record for record in row_key_only if record.get("has_explicit_form") or record.get("has_reconstructible_payload")])
        selected_details.append(
            {
                "exact_surface_match_count": len(exact_surface),
                "exact_transfer_explicit_form_count": sum(1 for record in exact_transfer if record.get("has_explicit_form")),
                "exact_transfer_match_count": len(exact_transfer),
                "exact_transfer_payload_count": sum(1 for record in exact_transfer if record.get("has_reconstructible_payload")),
                "p947_row": compact_selected(row),
                "row_key_match_count": len(row_key_matches),
                "row_key_only_payload_count": sum(
                    1 for record in row_key_only if record.get("has_explicit_form") or record.get("has_reconstructible_payload")
                ),
                "row_key_only_sample": [record_ref(record) for record in row_key_only[:5]],
                "surface_match_sample": [record_ref(record) for record in exact_surface[:5]],
                "transfer_match_sample": [record_ref(record) for record in exact_transfer[:5]],
            }
        )

    return {
        "exact_surface_matched_rows": sum(1 for item in selected_details if item["exact_surface_match_count"] > 0),
        "exact_transfer_explicit_form_records": len(exact_transfer_form_records),
        "exact_transfer_matched_rows": sum(1 for item in selected_details if item["exact_transfer_match_count"] > 0),
        "exact_transfer_payload_records": len(exact_transfer_payload_records),
        "row_key_matched_rows": sum(1 for item in selected_details if item["row_key_match_count"] > 0),
        "row_key_only_payload_records": len(row_key_only_payload_records),
        "row_key_payload_rows": sum(1 for item in selected_details if item["row_key_only_payload_count"] > 0),
        "selected_details": selected_details,
    }


def rank_exact_transfer_forms(match_summary: dict[str, Any], records: list[dict[str, Any]], selected_rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected_pairs = {(str(row.get("row_key")), int_value(row.get("transfer_index"))) for row in selected_rows}
    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if not record.get("has_explicit_form"):
            continue
        pair = (str(record.get("row_key")), int_value(record.get("transfer_index")))
        if pair not in selected_pairs:
            continue
        base_order = record.get("base_order")
        challenge_seed = record.get("challenge_seed")
        if base_order is None or challenge_seed is None:
            continue
        groups[(str(challenge_seed), int(base_order))].append(record)
    reports = []
    for (challenge_seed, base_order), items in groups.items():
        rows = [item["form"]["coeffs"] + [item["form"]["rhs"]] for item in items if item.get("form")]
        coeff_rows = [row[:-1] for row in rows]
        reports.append(
            {
                "base_order": base_order,
                "challenge_seed": challenge_seed,
                "form_count": len(rows),
                "rank": modular_rank(coeff_rows, int(base_order)) if coeff_rows else {"rank": 0},
                "row_keys": sorted({str(item.get("row_key")) for item in items}),
                "transfer_indices": sorted({int_value(item.get("transfer_index")) for item in items}),
            }
        )
    return {
        "group_count": len(reports),
        "groups": sorted(reports, key=lambda item: (item["challenge_seed"], item["base_order"])),
        "rank_boundary": "Only exact row_key+transfer_index explicit forms are ranked. Row-key-only forms are intentionally excluded.",
    }


def determine_claim(match_summary: dict[str, Any], rank_report: dict[str, Any]) -> str:
    if int_value(match_summary.get("exact_transfer_explicit_form_records")) > 0 and int_value(rank_report.get("group_count")) > 0:
        return "P948_EXACT_TRANSFER_VERIFIER_FORMS_AVAILABLE"
    if int_value(match_summary.get("exact_transfer_matched_rows")) > 0:
        return "NEGATIVE_RESULT_P948_EXACT_TRANSFER_MATCHES_LACK_FORMS"
    if int_value(match_summary.get("row_key_payload_rows")) > 0:
        return "NEGATIVE_RESULT_P948_ROW_KEY_PAYLOADS_EXIST_BUT_TRANSFER_EXACT_JOIN_MISSING"
    return "NEGATIVE_RESULT_P948_NO_VERIFIER_ATTACHMENT_FOR_P947_ROWS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    selected_rows = selected_p947_rows()
    artifacts = args.artifact or CANDIDATE_ARTIFACTS
    records, artifact_summaries = build_attachments([Path(path) for path in artifacts])
    match_summary = summarize_matches(selected_rows, records)
    rank_report = rank_exact_transfer_forms(match_summary, records, selected_rows)
    selected_row_keys = sorted({str(row.get("row_key")) for row in selected_rows})
    selected_transfers = sorted({int_value(row.get("transfer_index")) for row in selected_rows})
    matched_row_keys = sorted(
        {
            str(item["p947_row"]["row_key"])
            for item in match_summary["selected_details"]
            if item["row_key_match_count"] > 0
        }
    )
    return {
        "artifacts": {
            "candidate_artifacts": [str(path) for path in artifacts],
            "contract": str(args.contract),
            "p939_source": str(P939_SOURCE),
            "script": str(Path(__file__)),
        },
        "artifact_summaries": artifact_summaries,
        "claim_status": determine_claim(match_summary, rank_report),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this joins existing archive artifacts; no fresh relation-harvester replay is claimed.",
            "FAIL-CLOSED-TRANSFER-JOIN: row-key-only equation payloads are not accepted as transfer-specific P947 verifier forms.",
            "RANK-PROXY-BOUNDARY: P947 factor coefficient rank is separate from verifier relation rank.",
            "POLLARD-RHO BOUNDARY: attachment evidence is not a complete faster-than-rho ECDLP algorithm.",
        ],
        "match_summary": {
            key: value for key, value in match_summary.items() if key != "selected_details"
        },
        "method": "p948_verifier_equation_attachment_audit",
        "parameters": {
            "candidate_artifact_count": len(artifacts),
            "selected_row_count": len(selected_rows),
            "selected_row_key_count": len(selected_row_keys),
            "selected_row_keys": selected_row_keys,
            "selected_transfer_indices": selected_transfers,
            "selected_transfer_count": len(selected_transfers),
        },
        "rank_report": rank_report,
        "regeneration_spec": {
            "missing_join_fields": [
                "surface_id",
                "transfer_index",
                "p947_challenge_seed",
                "verifier_challenge_seed",
                "base_order",
                "linear_form_coeffs",
                "linear_form_rhs",
                "target_scalar_column",
            ],
            "missing_p947_row_keys": sorted(set(selected_row_keys) - set(matched_row_keys)),
            "required_next_artifact": (
                "Regenerate a compact relation-harvester/static-bank pass for the exact P947 selected surface ids, "
                "including row_key, transfer_index, challenge_seed, base_order, coeffs, rhs, and verifier result."
            ),
        },
        "schema": SCHEMA,
        "selected_details": match_summary["selected_details"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--artifact", action="append", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    match = payload["match_summary"]
    print(
        f"claim={payload['claim_status']} "
        f"selected={payload['parameters']['selected_row_count']} "
        f"rowkey_rows={match['row_key_matched_rows']} "
        f"rowkey_payload_rows={match['row_key_payload_rows']} "
        f"exact_transfer_rows={match['exact_transfer_matched_rows']} "
        f"exact_forms={match['exact_transfer_explicit_form_records']} "
        f"rank_groups={payload['rank_report']['group_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
