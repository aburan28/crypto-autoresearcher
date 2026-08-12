#!/usr/bin/env python3
"""P1079 residual row pivot for remaining columns after the P1073 packet."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_factor_rank_gap_diagnostic as gap
import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1063_p231_free_column_source_construction as p1063
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069
import low_term_total2_p1071_p231_remaining_column_source_expansion as p1071
import low_term_total2_p1078_p231_remaining_column_source_family_pivot as p1078
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1079_p231_remaining_column_residual_row_pivot.md"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_P1069 = STATE_DIR / "low_term_total2_p1069_p231_forward_transfer_descent_accounting_probe.json"
DEFAULT_P1073 = STATE_DIR / "low_term_total2_p1073_p231_topk7_order_compression_probe.json"
DEFAULT_P1074 = STATE_DIR / "low_term_total2_p1074_p231_disjoint_source_packet_validation_probe.json"
DEFAULT_P1078 = STATE_DIR / "low_term_total2_p1078_p231_remaining_column_source_family_pivot_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1079_p231_remaining_column_residual_row_pivot_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1079_p231_remaining_column_residual_row_pivot.v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_columns(text: str) -> list[int]:
    return [int(item) for item in text.split(",") if item.strip()]


def direct_charge(cert: dict[str, Any]) -> float:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    value = p1055.float_value(selected.get("direct_ops_over_rho"))
    return value if value is not None else float("inf")


def cert_key(cert: dict[str, Any]) -> tuple[str, int]:
    return (str(cert.get("_artifact")), p1055.int_value(cert.get("_artifact_offset"), -1))


def pad(values: list[int], length: int) -> list[int]:
    return values + [0] * max(0, length - len(values))


def selected_summary(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    row_keys = [str(item) for item in selected.get("row_keys") or []]
    salts = p1055.extract_salts(row_keys)
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": p1055.int_value(cert.get("_artifact_offset"), -1),
        "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
        "forms_count": cert.get("forms_count"),
        "public_key_verified": cert.get("public_key_verified"),
        "rank": cert.get("rank"),
        "row_keys": row_keys,
        "salt_max": max(salts) if salts else None,
        "salt_min": min(salts) if salts else None,
        "salt_sum": sum(salts) if salts else None,
        "selected_term_support": cert.get("selected_term_support") or [],
        "selector": selected.get("selector"),
        "target": selected.get("target"),
        "top_k": selected.get("top_k"),
        "transfer_index": selected.get("transfer_index"),
        "window": cert.get("window"),
    }


def relation_rows_for_cert(cert: dict[str, Any], order: int, factor_count: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for relation in factor_bank.target_eliminated_rows(cert):
        if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
            continue
        coeffs = pad([p1055.int_value(value) % order for value in relation.get("canonical_coeffs") or []], factor_count)
        rhs = p1055.int_value(relation.get("canonical_rhs")) % order
        key = (tuple(coeffs), rhs)
        if key in seen:
            continue
        seen.add(key)
        support = [idx for idx, coeff in enumerate(coeffs) if coeff % order]
        rows.append(
            {
                "cert_key": cert_key(cert),
                "coeffs": coeffs,
                "factor_support": support,
                "parent": selected_summary(cert),
                "pair": relation.get("pair") or [],
                "rhs": rhs,
            }
        )
    return rows


def unique_rows(rows: list[dict[str, Any]], order: int, factor_count: int) -> list[dict[str, Any]]:
    rows_by_key: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    for row in rows:
        coeffs = tuple(pad([p1055.int_value(value) % order for value in row.get("coeffs") or []], factor_count))
        rhs = p1055.int_value(row.get("rhs")) % order
        if not any(coeffs):
            continue
        rows_by_key.setdefault((coeffs, rhs), {**row, "coeffs": list(coeffs), "rhs": rhs})
    return list(rows_by_key.values())


def rank_from_rows(
    base_certs: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    order: int,
    factor_count_hint: int,
    column: int,
) -> dict[str, Any]:
    source_unique = unique_rows(source_rows, order, factor_count_hint)
    factor_count = max(
        factor_count_hint,
        gap.factor_count_for_order(base_certs, order),
        max([len(row.get("coeffs") or []) for row in source_unique] or [0]),
    )
    base_rows = gap.unique_relation_rows(base_certs, order, factor_count)
    source_unique = unique_rows(source_rows, order, factor_count)
    base_basis, base_pivots = gap.rref_rows([row["coeffs"] for row in base_rows], order)
    plus_basis, plus_pivots = gap.rref_rows([row["coeffs"] for row in base_rows + source_unique], order)
    source_support = Counter()
    for row in source_unique:
        for item in row.get("factor_support") or []:
            source_support[p1055.int_value(item)] += 1
    return {
        "base_plus_source_free_columns": [idx for idx in range(factor_count) if idx not in set(plus_pivots)],
        "base_plus_source_rank": len(plus_pivots),
        "base_rank": len(base_pivots),
        "column_free_after_source": column not in set(plus_pivots),
        "factor_variable_count": factor_count,
        "source_rank_gain_over_base": len(plus_pivots) - len(base_pivots),
        "source_rows_touching_column": source_support[column],
        "source_support_columns": sorted(source_support),
        "source_unique_row_count": len(source_unique),
    }


def result_from_rows(
    base_certs: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    charge: float,
    args: argparse.Namespace,
    factor_count_hint: int,
) -> dict[str, Any]:
    rank = rank_from_rows(base_certs, source_rows, args.order, factor_count_hint, args.column)
    gain = rank["source_rank_gain_over_base"]
    return {
        **rank,
        "charge_per_rank_gain": round(charge / gain, 8) if gain else None,
        "direct_certificate_artifact_count": None,
        "selected_case_count": None,
        "selected_window_count": None,
        "strict_source_charge_over_rho": round(charge, 8),
        "usable_source_certificate_count": None,
    }


def cert_matches_ref(cert: dict[str, Any], ref: dict[str, Any], source: str) -> bool:
    if not p1071.cert_matches_ref(cert, ref, source):
        return False
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    cert_keys = sorted(str(item) for item in selected.get("row_keys") or [])
    ref_keys = sorted(str(item) for item in ref.get("row_keys") or [])
    return cert_keys == ref_keys


def load_direct_certs_for_window(
    row: dict[str, Any],
    cache: dict[Path, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    _, candidate_paths = p1055.scorer_paths(row["scorer_artifact"])
    paths = p1055.direct_source_paths(candidate_paths, row["window_start"], row["window_end"])
    return p1055.load_certs_cached(paths, cache)


def load_base_certs_for_windows(
    windows: set[str],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    certs_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    for window in sorted(windows, key=lambda key: factor_rows[key]["window_start"]):
        row = factor_rows[window]
        base_paths, _ = p1055.scorer_paths(row["scorer_artifact"])
        for cert in p1055.load_certs_cached(base_paths, cache):
            certs_by_key[p1055.cert_key(cert)] = cert
    return list(certs_by_key.values())


def exact_certs_for_refs(
    refs: list[dict[str, Any]],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    certs: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for ref in refs:
        row = factor_rows.get(ref["window"])
        if row is None:
            raise ValueError(f"missing factor row for baseline ref window {ref['window']}")
        matches = [cert for cert in load_direct_certs_for_window(row, cache) if cert_matches_ref(cert, ref, args.source)]
        if not matches:
            raise ValueError(f"no exact direct certificate for baseline ref {ref['case_id']}")
        if len(matches) > 1:
            raise ValueError(f"ambiguous exact direct certificate for baseline ref {ref['case_id']}: {len(matches)}")
        key = cert_key(matches[0])
        if key not in seen:
            seen.add(key)
            certs.append(matches[0])
    return certs


def collect_candidate_certs(context: dict[str, Any], args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[Path]]:
    promotion_window_end = context["promotion_window_end"]
    certs_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    direct_paths: list[Path] = []
    for _, row in sorted(context["factor_rows"].items(), key=lambda item: item[1]["window_start"]):
        if row["window_start"] <= promotion_window_end:
            continue
        _, candidate_paths = p1055.scorer_paths(row["scorer_artifact"])
        paths = p1055.direct_source_paths(candidate_paths, row["window_start"], row["window_end"])
        direct_paths.extend(paths)
        for cert in p1055.load_certs_cached(paths, context["cache"]):
            selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
            clause = str(cert.get("clause") or selected.get("clause") or "")
            if str(selected.get("target")) != args.target or clause != args.source:
                continue
            certs_by_key[cert_key(cert)] = cert
    return list(certs_by_key.values()), sorted(set(direct_paths))


def row_summary(row: dict[str, Any]) -> dict[str, Any]:
    parent = row.get("parent") or {}
    return {
        "artifact": parent.get("artifact"),
        "artifact_offset": parent.get("artifact_offset"),
        "direct_ops_over_rho": parent.get("direct_ops_over_rho"),
        "factor_support": row.get("factor_support") or [],
        "pair": row.get("pair") or [],
        "row_keys": parent.get("row_keys") or [],
        "selector": parent.get("selector"),
        "top_k": parent.get("top_k"),
        "transfer_index": parent.get("transfer_index"),
        "window": parent.get("window"),
    }


def classify_stats(stats: dict[str, Any], remaining_columns: set[int]) -> list[str]:
    removed = set(stats.get("removed_free_columns") or [])
    charge = p1055.float_value(stats.get("marginal_charge_over_rho")) or float("inf")
    if removed & remaining_columns:
        return ["remaining_column_hit_below_rho" if charge < 1.0 else "remaining_column_hit_above_rho"]
    if stats.get("marginal_rank_gain", 0) > 0:
        return ["rank_gain_no_remaining_column"]
    return []


def item_sort_key(item: dict[str, Any], remaining_columns: set[int]) -> tuple[Any, ...]:
    stats = item["stats"]
    removed = set(stats.get("removed_free_columns") or [])
    charge = p1055.float_value(stats.get("marginal_charge_over_rho")) or float("inf")
    return (
        not bool(removed & remaining_columns),
        charge,
        -p1055.int_value(stats.get("marginal_rank_gain")),
        item.get("support_class") or "",
        item.get("id") or "",
    )


def scan_rows(
    candidate_rows: list[dict[str, Any]],
    strict_base_certs: list[dict[str, Any]],
    strict_rows: list[dict[str, Any]],
    strict_charge: float,
    strict_result: dict[str, Any],
    context: dict[str, Any],
    args: argparse.Namespace,
    remaining_columns: set[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    progress: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    strict_windows = {ref["window"] for ref in context["strict_refs"]}
    factor_count_hint = max(
        [p1055.int_value(context["factor_rows"][window].get("factor_variable_count")) for window in strict_windows] or [0]
    )
    for row in candidate_rows:
        parent = row.get("parent") or {}
        parent_window = str(parent.get("window") or "")
        windows = set(strict_windows)
        if parent_window and parent_window in context["factor_rows"]:
            windows.add(parent_window)
        base_certs = load_base_certs_for_windows(windows, context["factor_rows"], context["cache"])
        local_factor_hint = max(
            factor_count_hint,
            max([p1055.int_value(context["factor_rows"][window].get("factor_variable_count")) for window in windows] or [0]),
        )
        charge = strict_charge + (p1055.float_value(parent.get("direct_ops_over_rho")) or 0.0)
        result = result_from_rows(base_certs, strict_rows + [row], charge, args, local_factor_hint)
        stats = p1063.marginal_stats(strict_result, result, sorted(remaining_columns | {14, 15}))
        classes = classify_stats(stats, remaining_columns)
        if not classes:
            continue
        support = set(row.get("factor_support") or [])
        support_class = "touches_67"
        if len(support & remaining_columns) == 1:
            support_class = "exactly_one_67"
        if 15 not in support and support & remaining_columns:
            support_class += "_no15"
        item = {
            "classes": classes,
            "id": f"{parent.get('artifact')}:{parent.get('artifact_offset')}:{row.get('pair')}",
            "row": row_summary(row),
            "stats": stats,
            "support_class": support_class,
        }
        progress.append(item)
        if "remaining_column_hit_below_rho" in classes or "remaining_column_hit_above_rho" in classes:
            remaining.append(item)
    progress.sort(key=lambda item: item_sort_key(item, remaining_columns))
    remaining.sort(key=lambda item: item_sort_key(item, remaining_columns))
    return progress, remaining


def scan_parent_certs(
    candidate_certs: list[dict[str, Any]],
    baseline_cert_keys: set[tuple[str, int]],
    strict_base_certs: list[dict[str, Any]],
    strict_rows: list[dict[str, Any]],
    strict_charge: float,
    strict_result: dict[str, Any],
    context: dict[str, Any],
    args: argparse.Namespace,
    remaining_columns: set[int],
    factor_count: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    progress: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    strict_windows = {ref["window"] for ref in context["strict_refs"]}
    for cert in candidate_certs:
        if cert_key(cert) in baseline_cert_keys:
            continue
        rows = relation_rows_for_cert(cert, args.order, factor_count)
        if not rows:
            continue
        parent = selected_summary(cert)
        parent_window = str(parent.get("window") or "")
        windows = set(strict_windows)
        if parent_window and parent_window in context["factor_rows"]:
            windows.add(parent_window)
        base_certs = load_base_certs_for_windows(windows, context["factor_rows"], context["cache"])
        factor_hint = max([p1055.int_value(context["factor_rows"][window].get("factor_variable_count")) for window in windows] or [factor_count])
        charge = strict_charge + direct_charge(cert)
        result = result_from_rows(base_certs, strict_rows + rows, charge, args, factor_hint)
        stats = p1063.marginal_stats(strict_result, result, sorted(remaining_columns | {14, 15}))
        classes = classify_stats(stats, remaining_columns)
        if not classes:
            continue
        support = sorted({idx for row in rows for idx in row.get("factor_support") or []})
        item = {
            "cert": {**parent, "relation_row_count": len(rows), "relation_support_columns": support},
            "classes": classes,
            "id": f"{cert.get('_artifact')}:{cert.get('_artifact_offset')}",
            "stats": stats,
        }
        progress.append(item)
        if "remaining_column_hit_below_rho" in classes or "remaining_column_hit_above_rho" in classes:
            remaining.append(item)
    progress.sort(key=lambda item: item_sort_key(item, remaining_columns))
    remaining.sort(key=lambda item: item_sort_key(item, remaining_columns))
    return progress, remaining


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=DEFAULT_P1067)
    parser.add_argument("--p1069", type=Path, default=DEFAULT_P1069)
    parser.add_argument("--p1073", type=Path, default=DEFAULT_P1073)
    parser.add_argument("--p1074", type=Path, default=DEFAULT_P1074)
    parser.add_argument("--p1078", type=Path, default=DEFAULT_P1078)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--remaining-columns", default="6,7")
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument("--promoted-selector", default="mode_low_term_support_total5")
    parser.add_argument("--promoted-top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    args = parser.parse_args()

    remaining_columns = set(parse_columns(args.remaining_columns))
    context = p1078.build_context(args)
    p1078_payload = load_json(args.p1078) if args.p1078.exists() else {}

    baseline_certs = exact_certs_for_refs(context["strict_refs"], context["factor_rows"], context["cache"], args)
    baseline_cert_keys = {cert_key(cert) for cert in baseline_certs}
    candidate_certs, direct_paths = collect_candidate_certs(context, args)
    factor_count = max(
        max([p1055.int_value(row.get("factor_variable_count")) for row in context["factor_rows"].values()] or [0]),
        gap.factor_count_for_order(baseline_certs + candidate_certs, args.order),
    )

    strict_rows = []
    for cert in baseline_certs:
        strict_rows.extend(relation_rows_for_cert(cert, args.order, factor_count))
    strict_windows = {ref["window"] for ref in context["strict_refs"]}
    strict_base_certs = load_base_certs_for_windows(strict_windows, context["factor_rows"], context["cache"])
    strict_charge = sum(p1055.float_value(ref.get("direct_ops_over_rho")) or 0.0 for ref in context["strict_refs"])
    strict_result = result_from_rows(strict_base_certs, strict_rows, strict_charge, args, factor_count)

    all_candidate_rows = []
    support_candidate_rows = []
    row_support_counts = Counter()
    for cert in candidate_certs:
        if cert_key(cert) in baseline_cert_keys:
            continue
        rows = relation_rows_for_cert(cert, args.order, factor_count)
        for row in rows:
            support = set(row.get("factor_support") or [])
            if support & remaining_columns:
                row_support_counts["touches_remaining"] += 1
                support_candidate_rows.append(row)
            if len(support & remaining_columns) == 1:
                row_support_counts["touches_exactly_one_remaining"] += 1
            if support & remaining_columns and 15 not in support:
                row_support_counts["touches_remaining_no15"] += 1
            all_candidate_rows.append(row)
    support_candidate_rows.sort(
        key=lambda row: (
            p1055.float_value((row.get("parent") or {}).get("direct_ops_over_rho")) or float("inf"),
            (row.get("parent") or {}).get("transfer_index") or -1,
            row.get("pair") or [],
        )
    )

    row_progress, row_remaining = scan_rows(
        all_candidate_rows,
        strict_base_certs,
        strict_rows,
        strict_charge,
        strict_result,
        context,
        args,
        remaining_columns,
    )
    cert_progress, cert_remaining = scan_parent_certs(
        candidate_certs,
        baseline_cert_keys,
        strict_base_certs,
        strict_rows,
        strict_charge,
        strict_result,
        context,
        args,
        remaining_columns,
        factor_count,
    )

    row_success = any("remaining_column_hit_below_rho" in item["classes"] for item in row_remaining)
    cert_success = any("remaining_column_hit_below_rho" in item["classes"] for item in cert_remaining)
    any_remaining = bool(row_remaining or cert_remaining)
    if row_success or cert_success:
        claim_status = "POSITIVE_SIGNAL_P1079_RESIDUAL_ROW_MOVES_67_BELOW_RHO"
    elif any_remaining:
        claim_status = "OBSERVATION_P1079_RESIDUAL_ROW_67_DIRECTION_ABOVE_RHO"
    elif row_support_counts["touches_remaining"]:
        claim_status = "NEGATIVE_RESULT_P1079_RESIDUAL_67_SUPPORT_DEPENDENT_AFTER_1415_PACKET"
    else:
        claim_status = "NEGATIVE_RESULT_P1079_NO_RESIDUAL_67_SUPPORT_AFTER_1415_PACKET"

    p1078_strict_packet = ((p1078_payload.get("controls") or {}).get("strict_p1073_packet") or {})
    baseline_alignment = {
        "p1078_strict_free_columns": p1078_strict_packet.get("base_plus_source_free_columns"),
        "p1078_strict_rank_gain": p1078_strict_packet.get("source_rank_gain_over_base"),
        "p1079_strict_free_columns": strict_result.get("base_plus_source_free_columns"),
        "p1079_strict_rank_gain": strict_result.get("source_rank_gain_over_base"),
        "same_free_columns": p1078_strict_packet.get("base_plus_source_free_columns")
        == strict_result.get("base_plus_source_free_columns"),
    }

    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "direct_certificate_artifact_count": len(direct_paths),
            "direct_certificate_artifact_digest": p1069.digest_paths(direct_paths),
            "p1059": p1069.sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1067": p1069.sha256_file(args.p1067) if args.p1067.exists() else None,
            "p1069": p1069.sha256_file(args.p1069) if args.p1069.exists() else None,
            "p1073": p1069.sha256_file(args.p1073) if args.p1073.exists() else None,
            "p1074": p1069.sha256_file(args.p1074) if args.p1074.exists() else None,
            "p1078": p1069.sha256_file(args.p1078) if args.p1078.exists() else None,
            "script": p1069.sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1078": str(args.p1078),
            "script": str(Path(__file__)),
        },
        "baseline_alignment": baseline_alignment,
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "TARGET-ELIMINATED-ROW-PIVOT",
            "SINGLE-TARGET",
            "POLLARD-RHO-BOUNDARY",
            "DIRECT-OPS-CAVEAT",
        ],
        "controls": {
            "p1078_replay_controls": ((p1078_payload.get("controls") or {}).get("replay_controls")),
            "strict_result_exact_row_model": strict_result,
        },
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "pre_materialized_certificate_pool": True,
            "row_level_split_public_routing_untested": True,
        },
        "parameters": {
            "candidate_universe": "post-promotion exact direct-source certificates and their target-eliminated relation rows",
            "factor_count": factor_count,
            "order": args.order,
            "remaining_columns": sorted(remaining_columns),
            "strict_ref_case_ids": [ref["case_id"] for ref in context["strict_refs"]],
            "target": args.target,
        },
        "record_counts": {
            "baseline_certificate_count": len(baseline_certs),
            "candidate_certificate_count": len(candidate_certs) - len(baseline_cert_keys & {cert_key(cert) for cert in candidate_certs}),
            "candidate_relation_row_count": len(all_candidate_rows),
            "cert_progress_count": len(cert_progress),
            "cert_remaining_count": len(cert_remaining),
            "direct_certificate_artifact_count": len(direct_paths),
            "row_progress_count": len(row_progress),
            "row_remaining_count": len(row_remaining),
            **dict(row_support_counts),
        },
        "schema": SCHEMA,
        "strict_success": bool(row_success or cert_success),
        "summary": {
            "baseline_alignment_same_free_columns": baseline_alignment["same_free_columns"],
            "best_cert_remaining": cert_remaining[0] if cert_remaining else None,
            "best_row_remaining": row_remaining[0] if row_remaining else None,
            "candidate_certificate_count": len(candidate_certs) - len(baseline_cert_keys & {cert_key(cert) for cert in candidate_certs}),
            "candidate_relation_row_count": len(all_candidate_rows),
            "claim_status": claim_status,
            "row_remaining_count": len(row_remaining),
            "row_support_counts": dict(row_support_counts),
            "support_candidate_rows": [row_summary(row) for row in support_candidate_rows[:12]],
            "strict_free_columns": strict_result.get("base_plus_source_free_columns"),
            "strict_success": bool(row_success or cert_success),
        },
        "timestamp_utc": p1071.now_iso(),
        "top_cert_progress": cert_progress[:12],
        "top_cert_remaining": cert_remaining[:12],
        "top_row_progress": row_progress[:20],
        "top_row_remaining": row_remaining[:20],
    }
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={success} candidate_certs={certs} rows={rows} "
        "row_remaining={row_remaining} cert_remaining={cert_remaining} out={out}".format(
            claim=claim_status,
            success=bool(row_success or cert_success),
            certs=payload["record_counts"]["candidate_certificate_count"],
            rows=len(all_candidate_rows),
            row_remaining=len(row_remaining),
            cert_remaining=len(cert_remaining),
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
