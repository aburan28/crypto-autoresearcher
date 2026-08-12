#!/usr/bin/env python3
"""P1071 expanded source-family audit for remaining target-descent columns."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1059_p231_rowkey_prefix_shared_source as p1059
import low_term_total2_p1063_p231_free_column_source_construction as p1063
import low_term_total2_p1065_p231_relaxed_high_mean_early_stop as p1065
import low_term_total2_p1067_p231_post_carrier_source_refresh as p1067
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1071_p231_remaining_column_source_expansion.md"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_P1069 = STATE_DIR / "low_term_total2_p1069_p231_forward_transfer_descent_accounting_probe.json"
DEFAULT_P1070 = STATE_DIR / "low_term_total2_p1070_p231_second_direction_source_pool_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1071_p231_remaining_column_source_expansion_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1071_p231_remaining_column_source_expansion.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def cert_matches_ref(cert: dict[str, Any], ref: dict[str, Any], source: str) -> bool:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    clause = str(cert.get("clause") or selected.get("clause") or "")
    return (
        str(selected.get("target")) == ref["target"]
        and str(selected.get("selector")) == ref["selector"]
        and p1055.int_value(selected.get("top_k"), -1) == p1055.int_value(ref.get("top_k"), -2)
        and p1055.int_value(selected.get("transfer_index"), -1) == p1055.int_value(ref.get("transfer_index"), -2)
        and clause == source
    )


def salts_from_rowkeys(rowkeys: tuple[str, ...]) -> list[int]:
    return p1055.extract_salts(list(rowkeys))


def ref_from_case(row: dict[str, Any], case: dict[str, Any], index: int, source: str) -> dict[str, Any]:
    rowkeys = p1059.normalized_rowkeys(case)
    salts = salts_from_rowkeys(rowkeys)
    return {
        "case_id": (
            f"{row['window']}:{p1059.transfer_index(case)}:"
            f"{case.get('selector')}:{case.get('top_k')}:{'|'.join(rowkeys)}"
        ),
        "direct_ops_over_rho": round(p1059.direct_charge(case), 8),
        "direct_public_key_verified": bool(case.get("direct_public_key_verified")),
        "index": index,
        "priority_hits": case.get("priority_hits") or [],
        "row_keys": list(rowkeys),
        "salt_max": max(salts) if salts else None,
        "salt_min": min(salts) if salts else None,
        "salt_sum": sum(salts) if salts else None,
        "selected_term_support": case.get("selected_term_support") or [],
        "selector": str(case.get("selector")),
        "source": source,
        "target": str(case.get("target")),
        "top_k": p1055.int_value(case.get("top_k"), -1),
        "transfer_index": p1059.transfer_index(case),
        "window": row["window"],
        "window_end": row["window_end"],
        "window_mean_ops": round(p1055.float_value(row.get("mean_ops")) or 0.0, 8),
        "window_start": row["window_start"],
    }


def ref_from_existing(ref: dict[str, Any], args: argparse.Namespace, source: str) -> dict[str, Any]:
    rowkeys = tuple(str(item) for item in ref["row_keys"])
    return {
        **ref,
        "case_id": (
            f"{ref['window']}:{ref['transfer_index']}:{args.promoted_selector}:"
            f"{args.promoted_top_k}:{'|'.join(rowkeys)}"
        ),
        "selector": args.promoted_selector,
        "source": source,
        "target": args.target,
        "top_k": args.promoted_top_k,
        "window_end": p1069.window_end(ref),
    }


def load_factor_rows(args: argparse.Namespace) -> tuple[dict[str, dict[str, Any]], list[Path]]:
    factor_paths = sorted(args.state_dir.glob(args.factor_glob))
    factor_windows = p1055.load_factor_windows(
        factor_paths,
        str(args.order),
        args.column,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    return factor_windows, factor_paths


def load_expanded_refs(
    args: argparse.Namespace,
    factor_rows: dict[str, dict[str, Any]],
    promotion_window_end: int,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[Path]]:
    refs: list[dict[str, Any]] = []
    paths = sorted(args.state_dir.glob(args.selected_glob))
    targets: Counter[str] = Counter()
    combos: Counter[tuple[str, int]] = Counter()
    windows_by_combo: dict[tuple[str, int], set[str]] = defaultdict(set)
    index = 0
    for path in paths:
        window = p1055.window_from_name(path)
        if window is None:
            continue
        start, end = window
        key = p1055.window_key(start, end)
        row = factor_rows.get(key)
        if row is None or start <= promotion_window_end:
            continue
        payload = load_json(path)
        for case in payload.get("case_reports") or []:
            if not isinstance(case, dict) or str(case.get("target")) != args.target:
                continue
            combo = (str(case.get("selector")), p1055.int_value(case.get("top_k"), -1))
            ref = ref_from_case(row, case, index, args.source)
            refs.append(ref)
            targets[ref["target"]] += 1
            combos[combo] += 1
            windows_by_combo[combo].add(key)
            index += 1
    refs.sort(key=lambda ref: (ref["window_start"], ref["transfer_index"], ref["selector"], ref["top_k"], ref["case_id"]))
    inventory = {
        "case_count": len(refs),
        "combo_counts": [
            {"selector": selector, "top_k": top_k, "cases": count, "windows": len(windows_by_combo[(selector, top_k)])}
            for (selector, top_k), count in combos.most_common()
        ],
        "combo_count": len(combos),
        "fresh_target_available_in_selected_source_family": len(targets) > 1,
        "target_counts": dict(targets),
        "window_count": len({ref["window"] for ref in refs}),
    }
    return refs, inventory, paths


def compact_result(result: dict[str, Any], max_cases: int = 18) -> dict[str, Any]:
    compact = p1065.compact_result(result, max_cases=max_cases)
    compact["selected_case_details"] = [
        {
            key: case.get(key)
            for key in [
                "direct_ops_over_rho",
                "direct_public_key_verified",
                "priority_hits",
                "row_keys",
                "selector",
                "top_k",
                "transfer_index",
                "window",
            ]
            if key in case
        }
        for case in compact.get("selected_case_details") or []
    ]
    return compact


def evaluate_refs(
    refs: list[dict[str, Any]],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    base_certificates: dict[tuple[str, int], dict[str, Any]] = {}
    source_certificates: dict[tuple[str, int], dict[str, Any]] = {}
    refs_by_window: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ref in refs:
        refs_by_window[ref["window"]].append(ref)

    charge = 0.0
    direct_path_count = 0
    factor_hint = 0
    selected_case_details: list[dict[str, Any]] = []
    for window, window_refs in sorted(refs_by_window.items(), key=lambda item: factor_rows[item[0]]["window_start"]):
        row = factor_rows[window]
        scorer = row.get("scorer_artifact")
        if not isinstance(scorer, Path) or not scorer.exists():
            continue
        base_paths, candidate_paths = p1055.scorer_paths(scorer)
        direct_paths = p1055.direct_source_paths(candidate_paths, row["window_start"], row["window_end"])
        for cert in p1055.load_certs_cached(sorted(base_paths), cache):
            base_certificates[p1055.cert_key(cert)] = cert
        source_candidates = p1055.load_certs_cached(direct_paths, cache)
        direct_path_count += len(direct_paths)
        factor_hint = max(factor_hint, p1055.int_value(row.get("factor_variable_count")))
        for ref in window_refs:
            charge += p1055.float_value(ref.get("direct_ops_over_rho")) or 0.0
            for cert in source_candidates:
                if cert_matches_ref(cert, ref, ref.get("source") or args.source):
                    source_certificates[p1055.cert_key(cert)] = cert
            selected_case_details.append(
                {
                    "direct_ops_over_rho": ref.get("direct_ops_over_rho"),
                    "direct_public_key_verified": ref.get("direct_public_key_verified"),
                    "priority_hits": ref.get("priority_hits") or [],
                    "row_keys": ref.get("row_keys") or [],
                    "selected_term_support": ref.get("selected_term_support") or [],
                    "selector": ref.get("selector"),
                    "top_k": ref.get("top_k"),
                    "transfer_index": ref.get("transfer_index"),
                    "window": ref.get("window"),
                }
            )

    rank = p1055.rank_audit(
        list(base_certificates.values()),
        list(source_certificates.values()),
        args.order,
        factor_hint,
        args.column,
    )
    gain = rank["source_rank_gain_over_base"]
    return {
        "base_plus_source_free_columns": rank["base_plus_source_free_columns"],
        "base_plus_source_rank": rank["base_plus_source_rank"],
        "base_rank": rank["base_rank"],
        "charge_per_rank_gain": round(charge / gain, 8) if gain else None,
        "direct_certificate_artifact_count": direct_path_count,
        "factor_variable_count": rank["factor_variable_count"],
        "selected_case_count": len(selected_case_details),
        "selected_case_details": selected_case_details,
        "selected_window_count": len(refs_by_window),
        "selected_windows": sorted(refs_by_window, key=lambda item: factor_rows[item]["window_start"]),
        "source_rank_gain_over_base": gain,
        "source_rows_touching_column": rank["source_rows_touching_column"],
        "source_support_columns": rank["source_support_columns"],
        "source_unique_row_count": rank["source_unique_row_count"],
        "strict_source_charge_over_rho": round(charge, 8),
        "usable_source_certificate_count": len(source_certificates),
    }


def compact_hit(hit: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "case_id",
        "direct_ops_over_rho",
        "direct_public_key_verified",
        "marginal_charge_over_rho",
        "marginal_rank_gain",
        "removed_free_columns",
        "row_keys",
        "selector",
        "top_k",
        "transfer_index",
        "union_free_columns",
        "window",
        "window_start",
    ]
    return {key: hit.get(key) for key in keys if key in hit}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=DEFAULT_P1067)
    parser.add_argument("--p1069", type=Path, default=DEFAULT_P1069)
    parser.add_argument("--p1070", type=Path, default=DEFAULT_P1070)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--promoted-selector", default="mode_low_term_support_total5")
    parser.add_argument("--promoted-top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    args = parser.parse_args()

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    p1067_payload = load_json(args.p1067)
    p1069_payload = load_json(args.p1069)
    p1070_payload = load_json(args.p1070)
    train_ref = ref_from_existing((p1067_payload.get("summary") or {})["best_single_rank_case"], args, args.source)
    promotion_ref = ref_from_existing((p1069_payload.get("parameters") or {})["promotion_case"], args, args.source)
    promotion_window_end = p1069.window_end(promotion_ref)

    factor_rows, factor_paths = load_factor_rows(args)
    expanded_refs, inventory, selected_paths = load_expanded_refs(args, factor_rows, promotion_window_end)
    selected_rowkey = p1063.selected_rowkey_from_p1059(args.p1059)
    anchor_ref = {
        "case_id": f"{args.promoted_selector}:{args.promoted_top_k}:18464_18471:18465:{'|'.join(selected_rowkey)}",
        "direct_ops_over_rho": 0.83211679,
        "direct_public_key_verified": True,
        "priority_hits": [6, 15],
        "row_keys": list(selected_rowkey),
        "selected_term_support": [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "selector": args.promoted_selector,
        "source": args.source,
        "target": args.target,
        "top_k": args.promoted_top_k,
        "transfer_index": 18465,
        "window": "18464_18471",
        "window_end": 18471,
        "window_start": 18464,
    }
    promoted_refs = [anchor_ref, train_ref, promotion_ref]
    cache: dict[Path, list[dict[str, Any]]] = {}
    promoted_packet = evaluate_refs(promoted_refs, factor_rows, cache, args)
    promoted_free = promoted_packet.get("base_plus_source_free_columns") or []

    single_hits: list[dict[str, Any]] = []
    single_audit_count = 0
    for ref in expanded_refs:
        result = evaluate_refs(promoted_refs + [ref], factor_rows, cache, args)
        stats = p1063.marginal_stats(promoted_packet, result, priority_columns)
        single_audit_count += 1
        if stats["marginal_rank_gain"] > 0 or stats["removed_free_columns"]:
            single_hits.append(
                {
                    **ref,
                    "marginal_charge_over_rho": stats["marginal_charge_over_rho"],
                    "marginal_rank_gain": stats["marginal_rank_gain"],
                    "removed_free_columns": stats["removed_free_columns"],
                    "union_free_columns": stats["union_free_columns"],
                }
            )
    single_hits.sort(
        key=lambda item: (
            p1055.float_value(item.get("marginal_charge_over_rho")) or float("inf"),
            -p1055.int_value(item.get("marginal_rank_gain")),
            item["case_id"],
        )
    )

    refs_by_combo: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for ref in expanded_refs:
        refs_by_combo[(ref["selector"], p1055.int_value(ref.get("top_k"), -1))].append(ref)

    combo_results = []
    combo_hits = []
    for (selector, top_k), refs in sorted(refs_by_combo.items()):
        result = evaluate_refs(promoted_refs + refs, factor_rows, cache, args)
        stats = p1063.marginal_stats(promoted_packet, result, priority_columns)
        item = {
            "case_count": len(refs),
            "first_case_id": refs[0]["case_id"] if refs else None,
            "result": compact_result(result, max_cases=8),
            "selector": selector,
            "stats": stats,
            "top_k": top_k,
            "window_count": len({ref["window"] for ref in refs}),
        }
        combo_results.append(item)
        if stats["marginal_rank_gain"] > 0 or stats["removed_free_columns"]:
            combo_hits.append(item)
    combo_hits.sort(
        key=lambda item: (
            p1055.float_value(item["stats"].get("marginal_charge_over_rho")) or float("inf"),
            -p1055.int_value(item["stats"].get("marginal_rank_gain")),
            item["selector"],
            item["top_k"],
        )
    )

    full_result = evaluate_refs(promoted_refs + expanded_refs, factor_rows, cache, args)
    full_stats = p1063.marginal_stats(promoted_packet, full_result, priority_columns)
    original_family = [ref for ref in expanded_refs if ref["selector"] == args.promoted_selector and ref["top_k"] == args.promoted_top_k]
    original_result = evaluate_refs(promoted_refs + original_family, factor_rows, cache, args)
    original_stats = p1063.marginal_stats(promoted_packet, original_result, priority_columns)
    success = bool(single_hits or combo_hits or full_stats["marginal_rank_gain"] > 0 or full_stats["removed_free_columns"])
    if success:
        claim_status = "OBSERVATION_P1071_EXPANDED_SOURCE_FAMILY_HAS_SECOND_DIRECTION"
    else:
        claim_status = "NEGATIVE_RESULT_P1071_EXPANDED_SOURCE_ARTIFACTS_NO_SECOND_DIRECTION"

    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "factor_artifact_count": len(factor_paths),
            "factor_artifact_digest": p1069.digest_paths(factor_paths),
            "p1059": p1069.sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1067": p1069.sha256_file(args.p1067) if args.p1067.exists() else None,
            "p1069": p1069.sha256_file(args.p1069) if args.p1069.exists() else None,
            "p1070": p1069.sha256_file(args.p1070) if args.p1070.exists() else None,
            "script": p1069.sha256_file(Path(__file__)),
            "selected_artifact_count": len(selected_paths),
            "selected_artifact_digest": p1069.digest_paths(selected_paths),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1059": str(args.p1059),
            "p1067": str(args.p1067),
            "p1069": str(args.p1069),
            "p1070": str(args.p1070),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "SOURCE-FAMILY-EXPANSION",
            "SINGLE-TARGET",
            "ORACLE-POOL-AUDIT",
            "POLLARD-RHO-BOUNDARY",
        ],
        "controls": {
            "full_expanded_pool": {"result": compact_result(full_result), "stats": full_stats},
            "original_p1070_family": {"case_count": len(original_family), "result": compact_result(original_result), "stats": original_stats},
            "promoted_packet": compact_result(promoted_packet),
            "p1070_summary": p1070_payload.get("summary"),
        },
        "expanded_source_inventory": inventory,
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "fresh_target_artifacts_available": bool(inventory["fresh_target_available_in_selected_source_family"]),
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "public_selector_not_trained_if_oracle_hit": True,
            "single_target_artifact_family": True,
        },
        "parameters": {
            "candidate_surface": "all selected-source selector/top-k cases after promoted carrier",
            "column": args.column,
            "order": args.order,
            "priority_columns": priority_columns,
            "promoted_free_columns": promoted_free,
            "promoted_refs": promoted_refs,
            "promoted_selector": args.promoted_selector,
            "promoted_top_k": args.promoted_top_k,
            "promotion_window_end": promotion_window_end,
            "source": args.source,
            "target": args.target,
        },
        "record_counts": {
            "combo_count": len(refs_by_combo),
            "combo_hit_count": len(combo_hits),
            "expanded_case_count": len(expanded_refs),
            "expanded_window_count": len({ref["window"] for ref in expanded_refs}),
            "single_audit_count": single_audit_count,
            "single_hit_count": len(single_hits),
        },
        "schema": SCHEMA,
        "selector_topk_results": [
            {
                "case_count": item["case_count"],
                "selector": item["selector"],
                "stats": item["stats"],
                "top_k": item["top_k"],
                "window_count": item["window_count"],
            }
            for item in combo_results
        ],
        "strict_success": success,
        "summary": {
            "best_combo_hit": (
                {
                    "case_count": combo_hits[0]["case_count"],
                    "selector": combo_hits[0]["selector"],
                    "stats": combo_hits[0]["stats"],
                    "top_k": combo_hits[0]["top_k"],
                    "window_count": combo_hits[0]["window_count"],
                }
                if combo_hits
                else None
            ),
            "best_single_hit": compact_hit(single_hits[0]) if single_hits else None,
            "claim_status": claim_status,
            "combo_hit_count": len(combo_hits),
            "expanded_case_count": len(expanded_refs),
            "fresh_target_artifacts_available": inventory["fresh_target_available_in_selected_source_family"],
            "full_pool_marginal_charge_over_rho": full_stats["marginal_charge_over_rho"],
            "full_pool_marginal_rank_gain": full_stats["marginal_rank_gain"],
            "full_pool_removed_free_columns": full_stats["removed_free_columns"],
            "full_pool_union_free_columns": full_stats["union_free_columns"],
            "original_family_marginal_rank_gain": original_stats["marginal_rank_gain"],
            "original_family_removed_free_columns": original_stats["removed_free_columns"],
            "promoted_remaining_free_columns": promoted_free,
            "single_hit_count": len(single_hits),
            "strict_success": success,
        },
        "timestamp_utc": now_iso(),
        "top_combo_hits": [
            {
                "case_count": item["case_count"],
                "selector": item["selector"],
                "stats": item["stats"],
                "top_k": item["top_k"],
                "window_count": item["window_count"],
            }
            for item in combo_hits[:12]
        ],
        "top_single_hits": [compact_hit(hit) for hit in single_hits[:20]],
    }
    write_json(args.out, payload)
    print(
        "claim={claim} success={success} expanded_cases={cases} single_hits={single_hits} "
        "combo_hits={combo_hits} full_rank_gain={rank} full_removed={removed} out={out}".format(
            claim=claim_status,
            success=success,
            cases=len(expanded_refs),
            single_hits=len(single_hits),
            combo_hits=len(combo_hits),
            rank=full_stats["marginal_rank_gain"],
            removed=full_stats["removed_free_columns"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
