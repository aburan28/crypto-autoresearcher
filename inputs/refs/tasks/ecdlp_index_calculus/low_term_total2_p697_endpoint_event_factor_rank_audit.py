#!/usr/bin/env python3
"""P697 endpoint-event factor-rank audit.

P696 found endpoint-bearing relation events after single-leaf mutation scans.
This audit converts those public forms into aggregate candidate certificates and
scores their target-eliminated factor relations against the P691 order-9887
base bank.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_direct_source_relation_equation_certificate as direct_export
import low_term_total2_p690_false_rank_certificate_factor_audit as p690
import low_term_total2_p691_factor_bank_deficiency_target_audit as p691
import low_term_total2_p693_endpoint_column_source_support_scout as p693
import low_term_total2_p696_endpoint_leaf_mutation_scout as p696
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = p696.DEFAULT_SOURCE
DEFAULT_PRODUCT = p696.DEFAULT_PRODUCT
DEFAULT_OUT = STATE_DIR / "low_term_total2_p697_endpoint_event_factor_rank_audit_probe.json"
ORDER = p690.ORDER


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def relation_key(relation: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    return tuple(int_value(value) % ORDER for value in relation["canonical_coeffs"]), int_value(
        relation["canonical_rhs"]
    ) % ORDER


def form_key(form: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    return tuple(int_value(value) % ORDER for value in form.get("coeffs") or []), int_value(
        form.get("rhs")
    ) % ORDER


def form_tuple(form: dict[str, Any]) -> tuple[tuple[int, ...], int, list[int]]:
    return (
        tuple(int_value(value) % ORDER for value in form.get("coeffs") or []),
        int_value(form.get("rhs")) % ORDER,
        [int_value(term) for term in form.get("terms") or []],
    )


def support_from_coeffs(coeffs: list[int]) -> list[int]:
    return [index for index, value in enumerate(coeffs) if value % ORDER]


def relation_record(
    context: dict[str, Any],
    leaf_index: int,
    support: dict[str, Any],
    scan: dict[str, Any],
    event: dict[str, Any],
    priority_columns: set[int],
) -> dict[str, Any]:
    coeffs, rhs, terms = event["form"]
    coeff_values = [int_value(value) % ORDER for value in coeffs]
    factor_coeffs = coeff_values[1:]
    coeff_support = support_from_coeffs(factor_coeffs)
    term_support = sorted({int_value(term) for term in terms})
    return {
        "_built": context["built"],
        "coeff_priority_hits": sorted(set(coeff_support) & priority_columns),
        "coeff_support": coeff_support,
        "direct_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
        "form": {
            "coeffs": coeff_values,
            "rhs": int_value(rhs) % ORDER,
            "terms": term_support,
        },
        "form_index": int_value(event.get("form_index")),
        "leaf_index": leaf_index,
        "priority_leaf_hits": sorted(set(support["term_support"]) & priority_columns),
        "q_coeff": coeff_values[0] if coeff_values else 0,
        "relation_rank": int_value(scan.get("rank")),
        "row_key": str(context.get("row_key")),
        "row_public_key_verified": bool(scan.get("row_public_key_verified")),
        "scout_pos": int_value(event.get("scout_pos")),
        "selected_hit_roots": int_value(scan.get("selected_hit_roots")),
        "term_priority_hits": sorted(set(term_support) & priority_columns),
        "term_support": term_support,
    }


def unique_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[tuple[int, ...], int]] = set()
    out: list[dict[str, Any]] = []
    for record in records:
        key = form_key(record["form"])
        if key in seen:
            continue
        seen.add(key)
        out.append(record)
    return out


def build_row_contexts(args: argparse.Namespace) -> tuple[Any, dict[tuple[str, int, int, str], dict[str, Any]], int, int]:
    source = load_json(Path(args.source))
    product = load_json(Path(args.product))
    source_index = p693.build_source_index(source)
    params = repair_probe.source_parameters(source)
    probe_args = repair_probe.probe_args_from_source(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    row_contexts: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    missing_source_case_count = 0
    for product_case in p693.product_cases(product, args.target, int_value(args.max_cases)):
        source_case = source_index.get(p693.exact_case_key(product_case))
        if source_case is None:
            missing_source_case_count += 1
            continue
        context = hit_stream_probe.scan_case_context(
            verifier,
            records,
            config_source,
            specs_by_target,
            source_case,
            probe_args,
            context_cache,
        )
        for row_context in p696.p694.contexts_from_source_case(context, source_case):
            row_contexts.setdefault(p696.row_context_key(row_context), row_context)
    return verifier, row_contexts, len(context_cache), missing_source_case_count


def collect_mutation_records(
    verifier: Any,
    row_contexts: dict[tuple[str, int, int, str], dict[str, Any]],
    priority_columns: set[int],
    max_endpoint_leaves: int,
) -> dict[str, Any]:
    scanned_endpoint_leaf_count = 0
    endpoint_leaf_count = 0
    endpoint_leaf_hit_root_count = 0
    records: list[dict[str, Any]] = []
    priority_leaf_counts: Counter[int] = Counter()
    priority_coeff_counts: Counter[int] = Counter()
    priority_term_counts: Counter[int] = Counter()
    for _key, context in sorted(row_contexts.items()):
        leaves = context["components"].get("leaves") or []
        for leaf_index in range(len(leaves)):
            support = p696.leaf_support(context, leaf_index)
            priority_hits = sorted(set(support["term_support"]) & priority_columns)
            if not priority_hits:
                continue
            endpoint_leaf_count += 1
            priority_leaf_counts.update(priority_hits)
            if max_endpoint_leaves > 0 and scanned_endpoint_leaf_count >= max_endpoint_leaves:
                continue
            scanned_endpoint_leaf_count += 1
            scan = direct_export.direct_witness_probe.scan_selected(
                verifier,
                context["built"],
                context["components"],
                {leaf_index},
                context["local_args"],
            )
            if int_value(scan.get("selected_hit_roots")):
                endpoint_leaf_hit_root_count += 1
            for event in scan.get("relation_events") or []:
                record = relation_record(context, leaf_index, support, scan, event, priority_columns)
                records.append(record)
                priority_coeff_counts.update(record["coeff_priority_hits"])
                priority_term_counts.update(record["term_priority_hits"])
    endpoint_records = [
        record for record in records if record["coeff_priority_hits"] or record["term_priority_hits"]
    ]
    endpoint_coeff_records = [record for record in records if record["coeff_priority_hits"]]
    return {
        "all_records": records,
        "endpoint_coeff_records": endpoint_coeff_records,
        "endpoint_leaf_count": endpoint_leaf_count,
        "endpoint_leaf_hit_root_count": endpoint_leaf_hit_root_count,
        "endpoint_records": endpoint_records,
        "priority_coeff_counts": priority_coeff_counts,
        "priority_leaf_counts": priority_leaf_counts,
        "priority_term_counts": priority_term_counts,
        "scanned_endpoint_leaf_count": scanned_endpoint_leaf_count,
    }


def union_derive(verifier: Any, records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    built_by_row: dict[str, dict[str, Any]] = {}
    for record in records:
        row_key = str(record["row_key"])
        built_by_row[row_key] = record["_built"]
        rows.append(
            {
                "_scan": {"relation_events": [{"form": form_tuple(record["form"])}]},
                "row_key": row_key,
            }
        )
    if not rows:
        return {
            "union_derived_secret": None,
            "union_public_key_verified": False,
            "union_rank": 0,
            "union_relation_count": 0,
        }
    return direct_export.direct_witness_probe.union_derive(verifier, rows, built_by_row, "_scan")


def pseudo_certificate(
    name: str,
    records: list[dict[str, Any]],
    target: str,
    union: dict[str, Any],
) -> dict[str, Any]:
    return {
        "certificate_status": (
            "PUBLIC_DIRECT_RELATION_EQUATIONS_VERIFY_PUBLIC_KEY"
            if union.get("union_public_key_verified")
            else "PUBLIC_DIRECT_RELATION_EQUATIONS_NEED_REVIEW_AGGREGATE"
        ),
        "clause": name,
        "derived_secret": union.get("union_derived_secret"),
        "expected_secret": union.get("union_derived_secret") if union.get("union_public_key_verified") else None,
        "forms": [record["form"] for record in records],
        "forms_count": len(records),
        "order": ORDER,
        "public_key_verified": bool(union.get("union_public_key_verified")),
        "rank": int_value(union.get("union_rank")),
        "selected": {
            "clause": name,
            "direct_ops_over_rho": None,
            "rho": None,
            "row_keys": sorted({str(record["row_key"]) for record in records}),
            "selector": name,
            "target": target,
            "top_k": 0,
            "transfer_index": 0,
        },
    }


def base_bank(paths: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    certificates = factor_bank.load_certificates(paths)
    candidates, missing = p690.find_candidates(certificates)
    candidate_keys = {p690.selected_key(cert) for cert in candidates}
    base = [cert for cert in certificates if p690.selected_key(cert) not in candidate_keys]
    return base, candidates, {"missing_p690_candidates": missing, "paths": [str(path) for path in paths]}


def bank_state(certificates: list[dict[str, Any]]) -> dict[str, Any]:
    raw, unique, factor_count = p691.collect_relations(certificates)
    matrix = [relation["canonical_coeffs"] for relation in unique]
    rhs = [int_value(relation["canonical_rhs"]) % ORDER for relation in unique]
    rank = factor_bank.rank_mod(matrix, ORDER)
    augmented_rank = factor_bank.rank_mod([row + [rhs[index]] for index, row in enumerate(matrix)], ORDER)
    columns, missing_columns = p691.derive_columns(matrix, rhs, factor_count)
    return {
        "augmented_rank": augmented_rank,
        "columns": columns,
        "factor_count": factor_count,
        "matrix": matrix,
        "missing_columns": missing_columns,
        "rank": rank,
        "raw": raw,
        "rhs": rhs,
        "unique": unique,
    }


def compact_relation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_coeffs": row["canonical_coeffs"],
        "canonical_rhs": row["canonical_rhs"],
        "factor_support": row["factor_support"],
        "multiplicity": row.get("multiplicity"),
        "pair": row.get("pair"),
    }


def evaluate_candidate(
    name: str,
    base: list[dict[str, Any]],
    base_state: dict[str, Any],
    cert: dict[str, Any],
    priority_columns: set[int],
    sample_limit: int,
) -> dict[str, Any]:
    candidate_state = bank_state([cert])
    with_state = bank_state(base + [cert])
    base_keys = {relation_key(relation) for relation in base_state["unique"]}
    candidate_unique = candidate_state["unique"]
    new_unique = [row for row in candidate_unique if relation_key(row) not in base_keys]
    missing_set = set(priority_columns)
    candidate_missing_touch = [row for row in candidate_unique if set(row["factor_support"]) & missing_set]
    new_missing_touch = [row for row in new_unique if set(row["factor_support"]) & missing_set]
    base_derivable = sum(1 for column in base_state["columns"] if column["derivable"])
    with_derivable = sum(1 for column in with_state["columns"] if column["derivable"])
    newly_derivable_priority = sorted(
        column
        for column in priority_columns
        if column in base_state["missing_columns"] and column not in with_state["missing_columns"]
    )
    return {
        "candidate_augmented_rank": candidate_state["augmented_rank"],
        "candidate_factor_relation_count": len(candidate_state["raw"]),
        "candidate_rank": candidate_state["rank"],
        "candidate_unique_factor_relation_count": len(candidate_unique),
        "candidate_unique_missing_touch_count": len(candidate_missing_touch),
        "claim_status": (
            "MARGINAL_FACTOR_RANK_GAIN"
            if with_state["rank"] > base_state["rank"]
            else "NEW_MISSING_TOUCH_RELATIONS_DEPENDENT"
            if new_missing_touch
            else "NEW_FACTOR_RELATIONS_NO_MISSING_TOUCH"
            if new_unique
            else "NO_NEW_FACTOR_RELATIONS"
        ),
        "factor_variables_derivable_gain": with_derivable - base_derivable,
        "missing_columns_after": with_state["missing_columns"],
        "name": name,
        "new_missing_touch_relation_count": len(new_missing_touch),
        "new_missing_touch_relation_samples": [compact_relation(row) for row in new_missing_touch[:sample_limit]],
        "new_unique_factor_relation_count": len(new_unique),
        "new_unique_relation_samples": [compact_relation(row) for row in new_unique[:sample_limit]],
        "newly_derivable_priority_columns": newly_derivable_priority,
        "rank_after": with_state["rank"],
        "rank_before": base_state["rank"],
        "rank_gain": with_state["rank"] - base_state["rank"],
        "unique_factor_relation_count_after": len(with_state["unique"]),
        "unique_factor_relation_count_before": len(base_state["unique"]),
        "unique_factor_relation_gain": len(with_state["unique"]) - len(base_state["unique"]),
    }


def compact_event_sample(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "coeff_priority_hits": record["coeff_priority_hits"],
        "coeff_support": record["coeff_support"],
        "form_index": record["form_index"],
        "leaf_index": record["leaf_index"],
        "q_coeff": record["q_coeff"],
        "rhs": record["form"]["rhs"],
        "row_key": record["row_key"],
        "scout_pos": record["scout_pos"],
        "term_priority_hits": record["term_priority_hits"],
        "term_support": record["term_support"],
    }


def determine_claim(candidate_evaluations: list[dict[str, Any]]) -> str:
    if any(item["newly_derivable_priority_columns"] for item in candidate_evaluations):
        return "P697_ENDPOINT_EVENTS_DERIVE_PRIORITY_COLUMNS"
    if any(int_value(item["rank_gain"]) > 0 for item in candidate_evaluations):
        return "P697_ENDPOINT_EVENTS_ADD_FACTOR_RANK"
    if any(int_value(item["new_missing_touch_relation_count"]) > 0 for item in candidate_evaluations):
        return "P697_ENDPOINT_EVENTS_ADD_DEPENDENT_MISSING_TOUCH_RELATIONS"
    if any(int_value(item["new_unique_factor_relation_count"]) > 0 for item in candidate_evaluations):
        return "P697_ENDPOINT_EVENTS_ADD_UNIQUE_NONMISSING_RELATIONS"
    return "NEGATIVE_RESULT_P697_ENDPOINT_EVENTS_NO_FACTOR_BANK_PROGRESS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    priority_columns = p693.parse_columns(args.priority_columns)
    verifier, row_contexts, context_cache_entry_count, missing_source_case_count = build_row_contexts(args)
    mutation = collect_mutation_records(
        verifier,
        row_contexts,
        priority_columns,
        int_value(args.max_endpoint_leaves),
    )
    all_records = unique_records(mutation["all_records"])
    endpoint_records = unique_records(mutation["endpoint_records"])
    endpoint_coeff_records = unique_records(mutation["endpoint_coeff_records"])
    base, excluded_candidates, bank_meta = base_bank(
        [Path(path) for path in (args.certificate or [str(path) for path in p690.DEFAULT_CERTIFICATE_PATHS])]
    )
    base_state = bank_state(base)
    candidate_specs = [
        ("p697_endpoint_coeff_forms", endpoint_coeff_records),
        ("p697_endpoint_event_forms", endpoint_records),
        ("p697_endpoint_leaf_all_forms", all_records),
    ]
    candidate_certificates = []
    candidate_evaluations = []
    union_summaries = {}
    for name, records in candidate_specs:
        union = union_derive(verifier, records)
        union_summaries[name] = union
        cert = pseudo_certificate(name, records, args.target, union)
        candidate_certificates.append(cert)
        candidate_evaluations.append(
            evaluate_candidate(
                name,
                base,
                base_state,
                cert,
                priority_columns,
                int_value(args.sample_limit, 12),
            )
        )
    claim_status = determine_claim(candidate_evaluations)
    summary = {
        "all_unique_form_count": len(all_records),
        "base_augmented_rank": base_state["augmented_rank"],
        "base_certificate_count": len(base),
        "base_factor_variable_count": base_state["factor_count"],
        "base_missing_columns": base_state["missing_columns"],
        "base_rank": base_state["rank"],
        "base_unique_factor_relation_count": len(base_state["unique"]),
        "context_cache_entry_count": context_cache_entry_count,
        "endpoint_coeff_unique_form_count": len(endpoint_coeff_records),
        "endpoint_event_unique_form_count": len(endpoint_records),
        "endpoint_leaf_count": mutation["endpoint_leaf_count"],
        "endpoint_leaf_hit_root_count": mutation["endpoint_leaf_hit_root_count"],
        "excluded_p690_candidate_count": len(excluded_candidates),
        "max_rank_gain": max([int_value(item["rank_gain"]) for item in candidate_evaluations] or [0]),
        "max_unique_factor_relation_gain": max(
            [int_value(item["unique_factor_relation_gain"]) for item in candidate_evaluations] or [0]
        ),
        "missing_source_case_count": missing_source_case_count,
        "priority_columns": sorted(priority_columns),
        "scanned_endpoint_leaf_count": mutation["scanned_endpoint_leaf_count"],
    }
    summary.update(
        {
            "priority_coeff_event_counts": {
                str(column): mutation["priority_coeff_counts"][column] for column in sorted(priority_columns)
            },
            "priority_leaf_counts": {
                str(column): mutation["priority_leaf_counts"][column] for column in sorted(priority_columns)
            },
            "priority_term_event_counts": {
                str(column): mutation["priority_term_counts"][column] for column in sorted(priority_columns)
            },
        }
    )
    return {
        "artifacts": {
            "base_certificates": bank_meta["paths"],
            "product": str(Path(args.product)),
            "source": str(Path(args.source)),
        },
        "candidate_evaluations": candidate_evaluations,
        "case_examples": {
            "all_form_samples": [compact_event_sample(record) for record in all_records[: int_value(args.sample_limit, 12)]],
            "endpoint_coeff_form_samples": [
                compact_event_sample(record)
                for record in endpoint_coeff_records[: int_value(args.sample_limit, 12)]
            ],
        },
        "claim_status": claim_status,
        "created_at": p696.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: aggregate pseudo-certificates assume P696 public forms for the same target can be paired for target elimination.",
            "HEURISTIC: rank growth is an index-calculus precursor, not a complete relation collection or target descent.",
            "A rank gain here is not a faster-than-Pollard-rho algorithm; source-generation cost, sparse linear algebra, and individual-log descent remain open.",
        ],
        "method": "p697_endpoint_event_factor_rank_audit",
        "parameters": {
            "max_cases": int_value(args.max_cases),
            "max_endpoint_leaves": int_value(args.max_endpoint_leaves),
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p697_endpoint_event_factor_rank_audit.v1",
        "summary": summary,
        "union_summaries": union_summaries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--product", default=str(DEFAULT_PRODUCT))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--certificate", action="append", default=None, help="Base certificate artifact to include.")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--max-endpoint-leaves", type=int, default=0)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"candidate_evaluations": payload["candidate_evaluations"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
