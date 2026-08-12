#!/usr/bin/env python3
"""P881 rank/descent audit for the frozen public slice motif.

P880 showed that the P842 exact-factor motif replicates on fresh windows.  This
audit moves one layer deeper: after public motif selection, reconstruct verifier
relation events for only the motif-recovered leaves, then aggregate rank and
target closure inside compatible challenge contexts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_p842_public_slice_motif_compression_audit as p842
import low_term_total2_p880_public_slice_motif_fresh_source_validation as p880


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p881_public_slice_motif_rank_descent_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p881_public_slice_motif_rank_descent_audit_probe.json"
DEFAULT_P842_SOURCE = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_P880_SOURCE = STATE_DIR / "low_term_total2_p880_public_slice_motif_fresh_source_validation_probe.json"
DEFAULT_LATER_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_312_327_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_328_343_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_344_359_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_360_375_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_376_391_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p881_public_slice_motif_rank_descent_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def short_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def modular_rank(matrix: list[list[int]], modulus: int) -> dict[str, Any]:
    if not matrix:
        return {"rank": 0, "nonunit_pivot_obstruction_count": 0}
    rows = [[int(cell) % modulus for cell in row] for row in matrix]
    row_count = len(rows)
    col_count = max((len(row) for row in rows), default=0)
    for row in rows:
        row.extend([0] * (col_count - len(row)))
    rank = 0
    nonunit_obstructions = 0
    for col in range(col_count):
        pivot = None
        nonunit_seen = False
        for pos in range(rank, row_count):
            value = rows[pos][col] % modulus
            if value == 0:
                continue
            if math.gcd(value, modulus) == 1:
                pivot = pos
                break
            nonunit_seen = True
        if pivot is None:
            if nonunit_seen:
                nonunit_obstructions += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, modulus)
        rows[rank] = [(value * inv) % modulus for value in rows[rank]]
        for pos in range(row_count):
            if pos == rank:
                continue
            factor = rows[pos][col] % modulus
            if factor:
                rows[pos] = [
                    (rows[pos][idx] - factor * rows[rank][idx]) % modulus
                    for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return {"rank": rank, "nonunit_pivot_obstruction_count": nonunit_obstructions}


def selected_pairs(chosen: list[dict[str, Any]]) -> list[tuple[int, int]]:
    pairs = []
    for candidate in chosen:
        for leaf, root in candidate.get("selected_pairs") or []:
            pairs.append((int(leaf), int(root)))
    return sorted(set(pairs))


def recovered_selection(selection: dict[str, Any]) -> bool:
    return (
        bool(selection.get("preserves_selected_root_pairs"))
        and bool(selection.get("public_slice_motif_beats_rho"))
        and int_value(selection.get("chosen_count")) > 0
        and int_value(selection.get("original_selected_root_pair_count")) > 0
        and int_value(selection.get("selected_root_pair_count")) > 0
    )


def source_positive_cases(path: Path, max_cases: int) -> list[dict[str, Any]]:
    payload = load_json(path)
    cases = [case for case in payload.get("positive_cases") or [] if isinstance(case, dict)]
    if max_cases > 0:
        return cases[:max_cases]
    return cases


def materialization_inputs(ps: Any, ps_args: argparse.Namespace) -> dict[str, Any]:
    bank = ps.load_json(ps_args.bank_source)
    config_source = ps.load_json(ps_args.config_source)
    direct_source = ps.load_json(ps_args.direct_source)
    transfer_source = ps.load_json(ps_args.transfer_source)
    params = transfer_source.get("parameters") if isinstance(transfer_source, dict) else {}
    radius = int(ps_args.radius if ps_args.radius is not None else (params or {}).get("radius") or 4)
    bank_rows = {
        ps.cross_surface_probe.compress_probe.row_key(row): row
        for row in bank.get("bank_rows") or []
        if isinstance(row, dict) and ps.cross_surface_probe.compress_probe.row_key(row)
    }
    specs_by_target = ps.cross_surface_probe.leaf_trim_probe.specs_by_target_and_key(
        ps.cross_surface_probe.salt_neighborhood_probe.witness_specs(direct_source, bank_rows, radius)
    )
    verifier = ps.cross_surface_probe.relation_probe.load_verifier_module()
    records = verifier.load_records()
    return {
        "config_source": config_source,
        "records": records,
        "specs_by_target": specs_by_target,
        "verifier": verifier,
    }


def surface_contexts_for_source(
    ps: Any,
    ps_args: argparse.Namespace,
    positive_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    inputs = materialization_inputs(ps, ps_args)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    contexts: dict[str, dict[str, Any]] = {}
    hit_stream = ps.cross_surface_probe.hit_stream_probe
    for case in positive_cases:
        context = hit_stream.scan_case_context(
            inputs["verifier"],
            inputs["records"],
            inputs["config_source"],
            inputs["specs_by_target"],
            case,
            ps_args,
            context_cache,
        )
        for item in hit_stream.unique_row_leaf_keys(case):
            row_key = str(item.get("row_key") or "")
            if row_key not in context["built_by_row"]:
                continue
            built = context["built_by_row"][row_key]
            surface_id = f"{built['target']}|{row_key}|{built.get('challenge_seed')}"
            contexts[surface_id] = {
                "built": built,
                "case": {
                    "target": case.get("target"),
                    "transfer_index": int_value(case.get("transfer_index")),
                    "top_k": int_value(case.get("top_k")),
                    "selector": case.get("selector"),
                    "row_selector": case.get("row_selector"),
                    "policy": case.get("policy"),
                },
                "components": context["components_by_row"][row_key],
                "local_args": context["local_args_by_row"][row_key],
                "row_key": row_key,
                "verifier": inputs["verifier"],
            }
    return contexts


def form_key(event: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    coeffs, rhs, _terms = event["form"]
    return tuple(int(coeff) for coeff in coeffs), int(rhs)


def compact_form(event: dict[str, Any], row_key: str) -> dict[str, Any]:
    coeffs, rhs, terms = event["form"]
    support = [index for index, coeff in enumerate(coeffs) if int(coeff) != 0]
    return {
        "coeffs": [int(coeff) for coeff in coeffs],
        "rhs": int(rhs),
        "row_key": row_key,
        "support": support,
        "terms": [int(term) for term in terms],
    }


def context_key(surface_context: dict[str, Any]) -> tuple[Any, ...]:
    built = surface_context["built"]
    return (
        str(built.get("target")),
        str(built.get("challenge_seed")),
        int_value(built.get("p")),
        int_value(built.get("order")),
        short_hash(built.get("base")),
        short_hash(built.get("public")),
    )


def compact_context_key(key: tuple[Any, ...]) -> dict[str, Any]:
    return {
        "target": key[0],
        "challenge_seed": key[1],
        "p": key[2],
        "order": key[3],
        "base_hash": key[4],
        "public_hash": key[5],
    }


def evaluate_source(
    ps: Any,
    source_path: Path,
    motif_set: dict[str, Any],
    max_cases_per_source: int,
    max_factor_degree: int,
) -> dict[str, Any]:
    ps_args = p842.public_slice_args(ps)
    ps_args.signature_source = source_path
    ps_args.max_cases = int(max_cases_per_source)
    ps_args.max_factor_degree = int(max_factor_degree)
    print(f"p881 materializing {source_path} max_cases={ps_args.max_cases}", flush=True)
    positive_cases = source_positive_cases(source_path, int(max_cases_per_source))
    try:
        surface_records, case_results = p842.materialize_surface_records(ps, ps_args)
        surface_contexts = surface_contexts_for_source(ps, ps_args, positive_cases)
        records_by_id = {
            str(record["surface_id"]): record
            for record in surface_records
            if isinstance(record, dict) and record.get("surface_id")
        }
        surface_ids = sorted(
            records_by_id,
            key=lambda surface_id: (
                p842.transfer_index(records_by_id[surface_id]),
                str(records_by_id[surface_id].get("target")),
                surface_id,
            ),
        )
        rows = []
        direct_scan = ps.cross_surface_probe.direct_witness_probe
        for surface_id in surface_ids:
            record = records_by_id[surface_id]
            candidates = ps.build_public_candidates(record, int(max_factor_degree))
            chosen = [candidate for candidate in candidates if p842.candidate_matches(candidate, motif_set)]
            selection = p842.evaluate_chosen(ps, record, chosen, str(motif_set["name"]))
            if not recovered_selection(selection):
                continue
            pairs = selected_pairs(chosen)
            leaf_indices = sorted({leaf for leaf, _root in pairs})
            surface_context = surface_contexts.get(surface_id)
            if not surface_context:
                rows.append(
                    {
                        "context_missing": True,
                        "leaf_indices": leaf_indices,
                        "row_key": record.get("row_key"),
                        "selection": selection,
                        "surface_id": surface_id,
                        "target": record.get("target"),
                        "transfer_index": p842.transfer_index(record),
                    }
                )
                continue
            scan = direct_scan.scan_selected(
                surface_context["verifier"],
                surface_context["built"],
                surface_context["components"],
                set(leaf_indices),
                surface_context["local_args"],
            )
            built = surface_context["built"]
            rho = int_value(built.get("generic_rho_steps"))
            rows.append(
                {
                    "case": surface_context["case"],
                    "context_key": list(context_key(surface_context)),
                    "context_missing": False,
                    "direct_ops": int_value(scan.get("preassociation_filter_ops")),
                    "direct_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
                    "event_summaries": scan.get("event_summaries") or [],
                    "forms": [compact_form(event, str(record.get("row_key"))) for event in scan.get("relation_events") or []],
                    "generic_rho_steps": rho,
                    "leaf_indices": leaf_indices,
                    "motif_ops": int_value(selection.get("public_slice_motif_ops")),
                    "motif_ops_over_rho": selection.get("public_slice_motif_ops_over_rho"),
                    "rank": int_value(scan.get("rank")),
                    "relation_count": int_value(scan.get("relation_count")),
                    "row_key": record.get("row_key"),
                    "row_public_key_verified": bool(scan.get("row_public_key_verified")),
                    "selection": selection,
                    "surface_id": surface_id,
                    "target": record.get("target"),
                    "transfer_index": p842.transfer_index(record),
                    "_built": built,
                    "_scan": scan,
                    "_verifier": surface_context["verifier"],
                }
            )
        return {
            "case_result_count": len(case_results or []),
            "error": None,
            "positive_case_count": len(positive_cases),
            "recovered_rows": rows,
            "source": p880.source_summary(source_path),
            "surface_count": len(surface_ids),
        }
    except Exception as exc:  # noqa: BLE001 - experiment evidence.
        return {
            "case_result_count": 0,
            "error": f"{type(exc).__name__}: {exc}",
            "error_traceback": traceback.format_exc().splitlines(),
            "positive_case_count": len(positive_cases),
            "recovered_rows": [],
            "source": p880.source_summary(source_path),
            "surface_count": 0,
        }


def aggregate_contexts(ps: Any, source_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for result in source_results:
        for row in result.get("recovered_rows") or []:
            if row.get("context_missing"):
                continue
            grouped[tuple(row["context_key"])].append(row)

    direct_witness = ps.cross_surface_probe.direct_witness_probe
    out = []
    for key, rows in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1])):
        form_records: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
        for row in rows:
            for form in row.get("forms") or []:
                form_tuple = (
                    tuple(int(coeff) for coeff in form["coeffs"]),
                    int(form["rhs"]),
                    [int(term) for term in form.get("terms") or []],
                )
                dedupe_key = (form_tuple[0], form_tuple[1])
                form_records.setdefault(
                    dedupe_key,
                    {
                        **form,
                        "form": form_tuple,
                    },
                )
        forms = [record["form"] for record in form_records.values()]
        order = int_value(key[3])
        matrix_rank = modular_rank([list(record["form"][0]) for record in form_records.values()], order)
        verifier = rows[0]["_verifier"]
        synthetic_rows = []
        built_by_row: dict[str, dict[str, Any]] = {}
        for row in rows:
            synthetic_rows.append(
                {
                    "row_key": row["row_key"],
                    "_motif_scan": row["_scan"],
                }
            )
            built_by_row[str(row["row_key"])] = row["_built"]
        union = direct_witness.union_derive(verifier, synthetic_rows, built_by_row, "_motif_scan")
        motif_ops = sum(int_value(row.get("motif_ops")) for row in rows)
        direct_ops = sum(int_value(row.get("direct_ops")) for row in rows)
        rho = max((int_value(row.get("generic_rho_steps")) for row in rows), default=0)
        out.append(
            {
                **compact_context_key(key),
                "deduped_form_count": len(forms),
                "direct_ops": direct_ops,
                "direct_ops_over_rho": ratio(direct_ops, rho),
                "matrix_rank": matrix_rank,
                "motif_ops": motif_ops,
                "motif_ops_over_rho": ratio(motif_ops, rho),
                "recovered_row_count": len(rows),
                "relation_count_sum": sum(int_value(row.get("relation_count")) for row in rows),
                "row_keys": sorted({str(row.get("row_key")) for row in rows}),
                "row_public_key_verified_count": len([row for row in rows if row.get("row_public_key_verified")]),
                "rows": [
                    {
                        "direct_ops_over_rho": row.get("direct_ops_over_rho"),
                        "leaf_indices": row.get("leaf_indices"),
                        "motif_ops_over_rho": row.get("motif_ops_over_rho"),
                        "rank": row.get("rank"),
                        "relation_count": row.get("relation_count"),
                        "row_key": row.get("row_key"),
                        "row_public_key_verified": row.get("row_public_key_verified"),
                        "transfer_index": row.get("transfer_index"),
                    }
                    for row in rows
                ],
                "target_context_public_key_verified": bool(union["union_public_key_verified"]),
                "union": union,
            }
        )
    return out


def aggregate_metrics(source_results: list[dict[str, Any]], context_groups: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        row
        for result in source_results
        if not result.get("error")
        for row in result.get("recovered_rows") or []
        if not row.get("context_missing")
    ]
    motif_ratios = [float(row["motif_ops_over_rho"]) for row in rows if row.get("motif_ops_over_rho") is not None]
    direct_ratios = [float(row["direct_ops_over_rho"]) for row in rows if row.get("direct_ops_over_rho") is not None]
    row_verified = [row for row in rows if row.get("row_public_key_verified")]
    row_motif_below_verified = [
        row
        for row in row_verified
        if row.get("motif_ops_over_rho") is not None and float(row["motif_ops_over_rho"]) < 1.0
    ]
    row_direct_below_verified = [
        row
        for row in row_verified
        if row.get("direct_ops_over_rho") is not None and float(row["direct_ops_over_rho"]) < 1.0
    ]
    verified_groups = [group for group in context_groups if group.get("target_context_public_key_verified")]
    motif_below_verified_groups = [
        group
        for group in verified_groups
        if group.get("motif_ops_over_rho") is not None and float(group["motif_ops_over_rho"]) < 1.0
    ]
    direct_below_verified_groups = [
        group
        for group in verified_groups
        if group.get("direct_ops_over_rho") is not None and float(group["direct_ops_over_rho"]) < 1.0
    ]
    return {
        "compatible_source_count": len([result for result in source_results if not result.get("error") and result.get("surface_count")]),
        "context_group_count": len(context_groups),
        "deduped_form_count": sum(int_value(group.get("deduped_form_count")) for group in context_groups),
        "direct_below_rho_verified_context_count": len(direct_below_verified_groups),
        "direct_ops_over_rho_max": round(max(direct_ratios), 8) if direct_ratios else None,
        "direct_ops_over_rho_mean": round(mean(direct_ratios), 8) if direct_ratios else None,
        "direct_ops_over_rho_min": round(min(direct_ratios), 8) if direct_ratios else None,
        "error_source_count": len([result for result in source_results if result.get("error")]),
        "matrix_rank_sum": sum(int_value((group.get("matrix_rank") or {}).get("rank")) for group in context_groups),
        "motif_below_rho_verified_context_count": len(motif_below_verified_groups),
        "motif_ops_over_rho_max": round(max(motif_ratios), 8) if motif_ratios else None,
        "motif_ops_over_rho_mean": round(mean(motif_ratios), 8) if motif_ratios else None,
        "motif_ops_over_rho_min": round(min(motif_ratios), 8) if motif_ratios else None,
        "recovered_row_count": len(rows),
        "relation_count_sum": sum(int_value(row.get("relation_count")) for row in rows),
        "row_direct_below_rho_public_key_verified_count": len(row_direct_below_verified),
        "row_motif_below_rho_public_key_verified_count": len(row_motif_below_verified),
        "row_public_key_verified_count": len(row_verified),
        "source_count": len(source_results),
        "surface_count": sum(int_value(result.get("surface_count")) for result in source_results if not result.get("error")),
        "target_context_verified_count": len(verified_groups),
    }


def strip_internal_source_results(source_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stripped_results = []
    for result in source_results:
        clean = dict(result)
        clean_rows = []
        for row in result.get("recovered_rows") or []:
            clean_rows.append({key: value for key, value in row.items() if not key.startswith("_")})
        clean["recovered_rows"] = clean_rows
        stripped_results.append(clean)
    return stripped_results


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("compatible_source_count")) == 0:
        return "NEGATIVE_RESULT_P881_NO_COMPATIBLE_LATER_SOURCES"
    if int_value(summary.get("motif_below_rho_verified_context_count")) > 0:
        return "P881_FROZEN_MOTIF_CLOSES_LATER_TARGET_CONTEXT_BELOW_RHO"
    if int_value(summary.get("row_motif_below_rho_public_key_verified_count")) > 0:
        return "P881_FROZEN_MOTIF_CLOSES_LATER_SINGLE_ROW_BELOW_RHO_WITH_PAIRING_GAP"
    if int_value(summary.get("target_context_verified_count")) > 0:
        return "P881_FROZEN_MOTIF_CLOSES_LATER_TARGET_CONTEXT_ABOVE_MOTIF_GROUP_COST"
    if int_value(summary.get("recovered_row_count")) > 0 and int_value(summary.get("matrix_rank_sum")) > 0:
        return "P881_FROZEN_MOTIF_SUPPLIES_LATER_RANK_WITHOUT_TARGET_CLOSURE"
    if int_value(summary.get("recovered_row_count")) > 0:
        return "P881_FROZEN_MOTIF_SUPPLIES_LATER_ROWS_WITHOUT_RANK"
    return "NEGATIVE_RESULT_P881_FROZEN_MOTIF_NO_LATER_RECOVERED_ROWS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p842_payload = load_json(args.p842_source)
    motif_set = p880.normalize_motif_set(p842_payload["selected_policy"]["motif_set"])
    ps = p842.load_module("ecdlp_public_slice_for_p881", p842.PUBLIC_SLICE_SCRIPT)
    sources = args.signature_source or DEFAULT_LATER_SOURCES
    sources = [Path(path) for path in sources[: int(args.max_sources)]]
    source_results = [
        evaluate_source(
            ps,
            source,
            motif_set,
            int(args.max_cases_per_source),
            int(args.max_factor_degree),
        )
        for source in sources
    ]
    context_groups = aggregate_contexts(ps, source_results)
    summary = aggregate_metrics(source_results, context_groups)
    claim_status = determine_claim(summary)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p842_source": str(args.p842_source),
            "p880_source": str(args.p880_source),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "context_groups": context_groups,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "MOTIF-FROZEN: the motif set is copied from P842/P880 and not retrained on later labels.",
            "PUBLIC-SELECTION BOUNDARY: public factor signatures select rows before verifier relation reconstruction.",
            "RELATION-RECONSTRUCTION BOUNDARY: verifier events audit rank/closure after selection and are not selection inputs.",
            "COMPATIBILITY BOUNDARY: challenge contexts are kept separate.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p881_public_slice_motif_rank_descent_audit",
        "p880_positive_control": {
            "aggregate_metrics": (load_json(args.p880_source).get("aggregate_metrics") if args.p880_source.exists() else None),
            "claim_status": (load_json(args.p880_source).get("claim_status") if args.p880_source.exists() else None),
        },
        "parameters": {
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "source_count": len(sources),
        },
        "red_team_handoff": {
            "assumptions": [
                "A motif-recovered leaf that reconstructs verifier relation events is a valid relation-supply datum.",
                "Context-local rank and public-key closure are the correct next tests after P880's relation-supply result.",
                "Motif cost and direct verifier replay cost must remain separate metrics.",
            ],
            "failure_modes": [
                "Recovered rows may stay target-local and fail outside 22050.cf1@11731.",
                "Rows can have relation rank without enough independent forms for individual-log closure.",
                "Direct verifier replay can cost more than the public motif model and therefore cannot be used as a speedup claim.",
            ],
            "next_concrete_action": (
                "If P881 closes contexts, replicate with later sources and implement a true relation-matrix builder; "
                "if it only supplies rank, design a public row-pairing rule that selects compatible rows before verifier replay."
            ),
        },
        "schema": SCHEMA,
        "source_results": strip_internal_source_results(source_results),
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p842-source", type=Path, default=DEFAULT_P842_SOURCE)
    parser.add_argument("--p880-source", type=Path, default=DEFAULT_P880_SOURCE)
    parser.add_argument("--signature-source", type=Path, action="append")
    parser.add_argument("--max-sources", type=int, default=len(DEFAULT_LATER_SOURCES))
    parser.add_argument("--max-cases-per-source", type=int, default=24)
    parser.add_argument("--max-factor-degree", type=int, default=1)
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
                "parameters": payload["parameters"],
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
