#!/usr/bin/env python3
"""P1065 early-stop compression for the P1064 relaxed high-mean band."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1059_p231_rowkey_prefix_shared_source as p1059
import low_term_total2_p1063_p231_free_column_source_construction as p1063
import low_term_total2_p1064_p231_chronology_safe_high_mean_ops as p1064


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1065_p231_relaxed_high_mean_early_stop.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1063 = STATE_DIR / "low_term_total2_p1063_p231_free_column_source_construction_probe.json"
DEFAULT_P1064 = STATE_DIR / "low_term_total2_p1064_p231_chronology_safe_high_mean_ops_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1065_p231_relaxed_high_mean_early_stop_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1065_p231_relaxed_high_mean_early_stop.v1"

CaseSelector = Callable[[dict[str, Any]], list[dict[str, Any]]]
CaseKey = tuple[str, int, tuple[str, ...]]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted({path for path in paths if path.exists()}):
        digest.update(str(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def condition_expression(feature: str, op: str, threshold: float) -> str:
    value = f"{threshold:.8f}".rstrip("0").rstrip(".")
    return f"{feature} {op} {value}"


def case_key(row: dict[str, Any], case: dict[str, Any]) -> CaseKey:
    return row["window"], p1059.transfer_index(case), p1059.normalized_rowkeys(case)


def salts_from_rowkeys(rowkeys: tuple[str, ...]) -> list[int]:
    return p1055.extract_salts(list(rowkeys))


def case_ref(row: dict[str, Any], case: dict[str, Any], index: int) -> dict[str, Any]:
    rowkeys = p1059.normalized_rowkeys(case)
    salts = salts_from_rowkeys(rowkeys)
    direct_charge = p1059.direct_charge(case)
    return {
        "case_id": f"{row['window']}:{p1059.transfer_index(case)}:{'|'.join(rowkeys)}",
        "direct_ops_over_rho": round(direct_charge, 8),
        "direct_public_key_verified": bool(case.get("direct_public_key_verified")),
        "index": index,
        "priority_hits": case.get("priority_hits") or [],
        "row_keys": list(rowkeys),
        "salt_max": max(salts) if salts else None,
        "salt_min": min(salts) if salts else None,
        "salt_sum": sum(salts) if salts else None,
        "selected_term_support": case.get("selected_term_support") or [],
        "transfer_index": p1059.transfer_index(case),
        "window": row["window"],
        "window_mean_ops": round(p1055.float_value(row.get("mean_ops")) or 0.0, 8),
        "window_start": row["window_start"],
    }


def key_from_ref(ref: dict[str, Any]) -> CaseKey:
    return ref["window"], int(ref["transfer_index"]), tuple(ref["row_keys"])


def exact_cases_selector(keys: set[CaseKey]) -> CaseSelector:
    def select(row: dict[str, Any]) -> list[dict[str, Any]]:
        selected = []
        for case in row.get("source_cases") or []:
            if case_key(row, case) in keys:
                selected.append(case)
        return selected

    return select


def evaluate_with_cases(
    rows: list[dict[str, Any]],
    anchor_selector: CaseSelector,
    refs: list[dict[str, Any]],
    bundles: dict[int, dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    keys = {key_from_ref(ref) for ref in refs}
    selector = p1063.union_selectors([anchor_selector, exact_cases_selector(keys)])
    return p1063.evaluate_fast(rows, selector, bundles, args)


def single_case_audits(
    validation_rows: list[dict[str, Any]],
    anchor: dict[str, Any],
    anchor_selector: CaseSelector,
    refs: list[dict[str, Any]],
    bundles: dict[int, dict[str, Any]],
    args: argparse.Namespace,
    priority_columns: list[int],
) -> list[dict[str, Any]]:
    audits = []
    for ref in refs:
        result = evaluate_with_cases(validation_rows, anchor_selector, [ref], bundles, args)
        stats = p1063.marginal_stats(anchor, result, priority_columns)
        audits.append(
            {
                **ref,
                "adds_usable_source_certificate": (
                    p1055.int_value(result.get("usable_source_certificate_count"))
                    > p1055.int_value(anchor.get("usable_source_certificate_count"))
                ),
                "single_base_plus_source_free_columns": result["base_plus_source_free_columns"],
                "single_marginal_charge_over_rho": stats["marginal_charge_over_rho"],
                "single_marginal_rank_gain": stats["marginal_rank_gain"],
                "single_removed_free_columns": stats["removed_free_columns"],
                "single_source_support_columns": result["source_support_columns"],
                "single_usable_source_certificate_count": result["usable_source_certificate_count"],
            }
        )
    return audits


def compact_result(result: dict[str, Any], max_windows: int = 24, max_cases: int = 16) -> dict[str, Any]:
    compact = dict(result)
    windows = compact.get("selected_windows") or []
    cases = compact.get("selected_case_details") or []
    compact["selected_windows"] = windows[:max_windows]
    compact["selected_windows_truncated"] = len(windows) > max_windows
    compact["selected_case_details"] = cases[:max_cases]
    compact["selected_case_details_truncated"] = len(cases) > max_cases
    return compact


def prefix_summary(
    name: str,
    refs: list[dict[str, Any]],
    public_policy: bool,
    caveat: str,
    validation_rows: list[dict[str, Any]],
    anchor: dict[str, Any],
    anchor_selector: CaseSelector,
    bundles: dict[int, dict[str, Any]],
    args: argparse.Namespace,
    priority_columns: list[int],
    target_column: int,
) -> dict[str, Any]:
    first_rank = None
    first_column = None
    checkpoints: list[dict[str, Any]] = []
    for length in range(1, len(refs) + 1):
        prefix = refs[:length]
        result = evaluate_with_cases(validation_rows, anchor_selector, prefix, bundles, args)
        stats = p1063.marginal_stats(anchor, result, priority_columns)
        checkpoint = {
            "last_case_id": prefix[-1]["case_id"],
            "length": length,
            "marginal_charge_over_rho": stats["marginal_charge_over_rho"],
            "marginal_rank_gain": stats["marginal_rank_gain"],
            "removed_free_columns": stats["removed_free_columns"],
            "union_free_columns": stats["union_free_columns"],
        }
        if stats["marginal_rank_gain"] > 0 and first_rank is None:
            first_rank = checkpoint
        if target_column in stats["removed_free_columns"] and first_column is None:
            first_column = checkpoint
        if stats["marginal_rank_gain"] > 0 or target_column in stats["removed_free_columns"] or length in (1, len(refs)):
            checkpoints.append(checkpoint)
    final = evaluate_with_cases(validation_rows, anchor_selector, refs, bundles, args)
    final_stats = p1063.marginal_stats(anchor, final, priority_columns)
    return {
        "caveat": caveat,
        "checkpoints": checkpoints,
        "final": compact_result(final),
        "final_stats": final_stats,
        "first_column_removal_prefix": first_column,
        "first_rank_gain_prefix": first_rank,
        "ordered_case_ids": [ref["case_id"] for ref in refs],
        "policy": name,
        "public_policy": public_policy,
    }


def sorted_refs(refs: list[dict[str, Any]], policy: str) -> list[dict[str, Any]]:
    if policy == "chronological":
        return sorted(refs, key=lambda ref: (ref["window_start"], ref["transfer_index"], ref["case_id"]))
    if policy == "high_mean_then_transfer":
        return sorted(refs, key=lambda ref: (-ref["window_mean_ops"], ref["transfer_index"], ref["case_id"]))
    if policy == "latest_window_then_transfer":
        return sorted(refs, key=lambda ref: (-ref["window_start"], ref["transfer_index"], ref["case_id"]))
    if policy == "low_min_salt_then_transfer":
        return sorted(refs, key=lambda ref: (ref["salt_min"] if ref["salt_min"] is not None else 10**9, ref["transfer_index"], ref["case_id"]))
    if policy == "low_salt_sum_then_transfer":
        return sorted(refs, key=lambda ref: (ref["salt_sum"] if ref["salt_sum"] is not None else 10**9, ref["transfer_index"], ref["case_id"]))
    if policy == "diagnostic_verified_first":
        return sorted(refs, key=lambda ref: (not ref["direct_public_key_verified"], ref["transfer_index"], ref["case_id"]))
    if policy == "diagnostic_certificate_oracle":
        return sorted(
            refs,
            key=lambda ref: (
                -p1055.int_value(ref.get("single_marginal_rank_gain")),
                10 not in (ref.get("single_removed_free_columns") or []),
                ref["single_marginal_charge_over_rho"],
                ref["case_id"],
            ),
        )
    raise ValueError(f"unknown policy: {policy}")


def policy_specs(refs_with_single: list[dict[str, Any]]) -> list[dict[str, Any]]:
    specs = [
        {
            "caveat": "uses only window order and transfer index; no verifier labels",
            "name": "chronological",
            "public_policy": True,
        },
        {
            "caveat": "uses P1064's public mean-ops feature as a priority score; exploratory and requires fresh holdout",
            "name": "high_mean_then_transfer",
            "public_policy": True,
        },
        {
            "caveat": "uses public window chronology in reverse; exploratory and requires fresh holdout",
            "name": "latest_window_then_transfer",
            "public_policy": True,
        },
        {
            "caveat": "uses public row-key salt minimum; exploratory and requires fresh holdout",
            "name": "low_min_salt_then_transfer",
            "public_policy": True,
        },
        {
            "caveat": "uses public row-key salt sum; exploratory and requires fresh holdout",
            "name": "low_salt_sum_then_transfer",
            "public_policy": True,
        },
        {
            "caveat": "uses direct verifier label and is diagnostic only",
            "name": "diagnostic_verified_first",
            "public_policy": False,
        },
        {
            "caveat": "uses rank/certificate outcome and is diagnostic only",
            "name": "diagnostic_certificate_oracle",
            "public_policy": False,
        },
    ]
    for spec in specs:
        spec["refs"] = sorted_refs(refs_with_single, spec["name"])
    return specs


def best_public_prefix(policy_results: list[dict[str, Any]], target_column: int) -> dict[str, Any] | None:
    candidates = []
    for result in policy_results:
        first = result.get("first_column_removal_prefix")
        if not result.get("public_policy") or not first:
            continue
        if target_column not in (first.get("removed_free_columns") or []):
            continue
        candidates.append(result)
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            item["first_column_removal_prefix"]["marginal_charge_over_rho"],
            item["first_column_removal_prefix"]["length"],
            item["policy"],
        )
    )
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1063", type=Path, default=DEFAULT_P1063)
    parser.add_argument("--p1064", type=Path, default=DEFAULT_P1064)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--target-column", type=int, default=10)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    parser.add_argument("--anchor-window", default="18464_18471")
    args = parser.parse_args()

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    selected_rowkey = p1063.selected_rowkey_from_p1059(args.p1059)
    records, p1054_expression, input_paths = p1063.load_p1054_records(args)
    forward_rows = [row for row in records if row["split"] == "forward_validation"]
    discovery_end = p1064.discovery_end_from_p1063(args.p1063, args.anchor_window)
    validation_rows = [row for row in forward_rows if row["window_start"] > discovery_end]
    anchor_rows = [row for row in validation_rows if row["window"] == args.anchor_window]
    if not anchor_rows:
        raise ValueError(f"anchor window {args.anchor_window} is not in the validation split")

    cache: dict[Path, list[dict[str, Any]]] = {}
    bundles = p1063.prepare_bundles(forward_rows, cache, args)
    exact_selector = p1059.rowkey_first_selector(selected_rowkey)
    anchor_selector = p1063.exact_anchor_forward(exact_selector, args.anchor_window)
    anchor_cases = exact_selector(anchor_rows[0])
    if not anchor_cases:
        raise ValueError(f"exact P1059 anchor case missing in {args.anchor_window}")
    anchor_case_key = case_key(anchor_rows[0], anchor_cases[0])
    anchor = p1063.evaluate_fast(anchor_rows, exact_selector, bundles, args)

    p1064_payload = load_json(args.p1064)
    relaxed_expression = ((p1064_payload.get("summary") or {}).get("relaxed_expression"))
    if not relaxed_expression:
        anchor_mean = p1055.float_value(anchor_rows[0].get("mean_ops")) or 0.0
        relaxed_expression = condition_expression("mean_ops", ">=", anchor_mean)
    relaxed_rule = p1055.compile_rule(str(relaxed_expression))
    relaxed_selector = p1063.union_selectors([anchor_selector, p1063.all_cases_when(relaxed_rule)])
    full_relaxed = p1063.evaluate_fast(validation_rows, relaxed_selector, bundles, args)
    full_relaxed_stats = p1063.marginal_stats(anchor, full_relaxed, priority_columns)

    exact_expression = p1064.expression_from_p1063(args.p1063)
    exact_rule = p1055.compile_rule(exact_expression)
    exact_transfer = p1063.evaluate_fast(
        validation_rows,
        p1063.union_selectors([anchor_selector, p1063.all_cases_when(exact_rule)]),
        bundles,
        args,
    )
    exact_transfer_stats = p1063.marginal_stats(anchor, exact_transfer, priority_columns)

    candidate_refs: list[dict[str, Any]] = []
    seen: set[CaseKey] = set()
    index = 0
    for row in validation_rows:
        for case in relaxed_selector(row):
            key = case_key(row, case)
            if key == anchor_case_key or key in seen:
                continue
            seen.add(key)
            candidate_refs.append(case_ref(row, case, index))
            index += 1

    single_audits = single_case_audits(
        validation_rows,
        anchor,
        anchor_selector,
        candidate_refs,
        bundles,
        args,
        priority_columns,
    )
    refs_by_id = {ref["case_id"]: ref for ref in single_audits}
    refs_with_single = [refs_by_id[ref["case_id"]] for ref in candidate_refs]

    policy_results = [
        prefix_summary(
            spec["name"],
            spec["refs"],
            bool(spec["public_policy"]),
            str(spec["caveat"]),
            validation_rows,
            anchor,
            anchor_selector,
            bundles,
            args,
            priority_columns,
            args.target_column,
        )
        for spec in policy_specs(refs_with_single)
    ]

    best_single_rank_cases = [
        ref
        for ref in sorted(
            refs_with_single,
            key=lambda item: (
                -p1055.int_value(item.get("single_marginal_rank_gain")),
                args.target_column not in (item.get("single_removed_free_columns") or []),
                item["single_marginal_charge_over_rho"],
                item["case_id"],
            ),
        )
        if p1055.int_value(ref.get("single_marginal_rank_gain")) > 0
    ]
    best_public = best_public_prefix(policy_results, args.target_column)
    public_below_rho = bool(
        best_public
        and best_public["first_column_removal_prefix"]
        and best_public["first_column_removal_prefix"]["marginal_charge_over_rho"] < 1.0
    )
    diagnostic_below_rho = any(
        result.get("first_column_removal_prefix")
        and result["first_column_removal_prefix"]["marginal_charge_over_rho"] < 1.0
        for result in policy_results
        if not result.get("public_policy")
    )

    if public_below_rho:
        claim_status = "POSITIVE_SIGNAL_P1065_EXPLORATORY_PUBLIC_EARLY_STOP_BELOW_RHO_REQUIRES_HOLDOUT"
    elif diagnostic_below_rho:
        claim_status = "DIAGNOSTIC_P1065_CERTIFICATE_ORACLE_BELOW_RHO_ONLY"
    elif best_single_rank_cases:
        claim_status = "OBSERVATION_P1065_SINGLE_CASE_RANK_CARRIER_ABOVE_RHO"
    else:
        claim_status = "NEGATIVE_RESULT_P1065_NO_SINGLE_OR_PREFIX_COLUMN10_CARRIER"

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in input_paths if path.exists()]),
            "input_artifact_digest": digest_paths(input_paths),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "p1059": sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1063": sha256_file(args.p1063) if args.p1063.exists() else None,
            "p1064": sha256_file(args.p1064) if args.p1064.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1059": str(args.p1059),
            "p1063": str(args.p1063),
            "p1064": str(args.p1064),
            "script": str(Path(__file__)),
        },
        "candidate_cases": refs_with_single,
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "EXPLORATORY-POLICY-FAMILY",
            "NO-VERIFIER-LABEL-PROMOTION",
            "FREE-COLUMN-PRESSURE",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "anchor": compact_result(anchor),
            "exact_transfer": compact_result(exact_transfer),
            "exact_transfer_stats": exact_transfer_stats,
            "full_relaxed": compact_result(full_relaxed),
            "full_relaxed_stats": full_relaxed_stats,
            "policy_results": policy_results,
        },
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "fresh_holdout_required_before_public_algorithm_claim": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "policy_family_chosen_after_p1064_band": True,
            "target_descent_not_implemented": True,
            "verifier_or_certificate_oracles_not_promoted": True,
        },
        "parameters": {
            "anchor_case_key": [anchor_case_key[0], anchor_case_key[1], list(anchor_case_key[2])],
            "anchor_window": args.anchor_window,
            "column": args.column,
            "discovery_end": discovery_end,
            "exact_expression": exact_expression,
            "order": args.order,
            "p1054_rule": p1054_expression,
            "priority_columns": priority_columns,
            "relaxed_expression": relaxed_expression,
            "selected_rowkey_control": list(selected_rowkey),
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "target_column": args.target_column,
            "top_k": args.top_k,
        },
        "record_counts": {
            "candidate_case_count": len(refs_with_single),
            "forward_windows": len(forward_rows),
            "rank_bearing_single_case_count": len(best_single_rank_cases),
            "validation_windows": len(validation_rows),
        },
        "schema": SCHEMA,
        "strict_success": False,
        "summary": {
            "best_public_first_charge": (
                best_public["first_column_removal_prefix"]["marginal_charge_over_rho"] if best_public else None
            ),
            "best_public_first_length": (
                best_public["first_column_removal_prefix"]["length"] if best_public else None
            ),
            "best_public_policy": best_public["policy"] if best_public else None,
            "best_single_rank_case": best_single_rank_cases[0] if best_single_rank_cases else None,
            "claim_status": claim_status,
            "exact_transfer_marginal_rank_gain": exact_transfer_stats["marginal_rank_gain"],
            "exploratory_public_below_rho": public_below_rho,
            "full_relaxed_marginal_charge": full_relaxed_stats["marginal_charge_over_rho"],
            "full_relaxed_marginal_rank_gain": full_relaxed_stats["marginal_rank_gain"],
            "full_relaxed_removed_free_columns": full_relaxed_stats["removed_free_columns"],
            "rank_bearing_single_case_count": len(best_single_rank_cases),
            "strict_success": False,
            "target_column": args.target_column,
            "weak_positive": public_below_rho or diagnostic_below_rho or bool(best_single_rank_cases),
        },
        "timestamp_utc": now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} public_below_rho={public} best_public_policy={policy} "
        "best_public_charge={charge} single_rank_cases={single} full_relaxed_charge={full} out={out}".format(
            claim=claim_status,
            public=public_below_rho,
            policy=payload["summary"]["best_public_policy"],
            charge=payload["summary"]["best_public_first_charge"],
            single=len(best_single_rank_cases),
            full=payload["summary"]["full_relaxed_marginal_charge"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
