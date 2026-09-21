#!/usr/bin/env python3
"""P1063 non-salt free-column source-construction audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1056_p231_public_source_cost_reducer as p1056
import low_term_total2_p1059_p231_rowkey_prefix_shared_source as p1059


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1063_p231_free_column_source_construction.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1062 = STATE_DIR / "low_term_total2_p1062_p231_multi_family_rank_diversity_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1063_p231_free_column_source_construction_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1063_p231_free_column_source_construction.v1"

CaseSelector = Callable[[dict[str, Any]], list[dict[str, Any]]]
RuleFn = Callable[[dict[str, Any]], bool]
DISALLOWED_RULE_TOKENS = ("salt_", "unique_salts")


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


def selected_rowkey_from_p1059(path: Path) -> tuple[str, ...]:
    payload = load_json(path)
    rowkey = ((payload.get("parameters") or {}).get("selected_rowkey")) or (
        (payload.get("summary") or {}).get("selected_rowkey")
    )
    if not rowkey:
        raise ValueError(f"P1059 artifact has no selected rowkey: {path}")
    return tuple(sorted(str(item) for item in rowkey))


def load_p1054_records(args: argparse.Namespace) -> tuple[list[dict[str, Any]], str, list[Path]]:
    p1054_payload = p1055.load_json(args.p1054)
    p1054_expression = (
        ((p1054_payload.get("selected_rule") or {}).get("expression"))
        or ((p1054_payload.get("summary") or {}).get("selected_rule_expression"))
    )
    if not p1054_expression:
        raise ValueError("P1054 artifact has no selected rule expression")
    p1054_rule = p1055.compile_rule(str(p1054_expression))
    factor_paths = sorted(args.state_dir.glob(args.factor_glob))
    selected_paths = sorted(args.state_dir.glob(args.selected_glob))
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
    source_windows = p1055.load_source_case_windows(
        selected_paths,
        args.target,
        args.selector,
        args.top_k,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    records = [
        row
        for row in p1055.join_windows(factor_windows, source_windows, args.column)
        if p1054_rule(row)
    ]
    return records, str(p1054_expression), factor_paths + selected_paths


def rule_allowed(rule: dict[str, Any]) -> bool:
    expression = str(rule.get("expression") or "")
    return not any(token in expression for token in DISALLOWED_RULE_TOKENS)


def non_salt_rule_catalog(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [rule for rule in p1056.rule_catalog(rows) if rule_allowed(rule)]


def case_key(case: dict[str, Any]) -> tuple[tuple[str, ...], int]:
    return p1059.normalized_rowkeys(case), p1059.transfer_index(case)


def union_selectors(selectors: list[CaseSelector]) -> CaseSelector:
    def select(row: dict[str, Any]) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        seen: set[tuple[tuple[str, ...], int]] = set()
        for selector in selectors:
            for case in selector(row):
                key = case_key(case)
                if key in seen:
                    continue
                seen.add(key)
                selected.append(case)
        return selected

    return select


def all_cases_when(rule: RuleFn) -> CaseSelector:
    def select(row: dict[str, Any]) -> list[dict[str, Any]]:
        return list(row.get("source_cases") or []) if rule(row) else []

    return select


def exact_anchor_forward(exact_selector: CaseSelector, anchor_window: str) -> CaseSelector:
    def select(row: dict[str, Any]) -> list[dict[str, Any]]:
        return exact_selector(row) if row.get("window") == anchor_window else []

    return select


def compact_result(result: dict[str, Any], max_windows: int = 24, max_cases: int = 16) -> dict[str, Any]:
    compact = dict(result)
    windows = compact.get("selected_windows") or []
    cases = compact.get("selected_case_details") or []
    compact["selected_windows"] = windows[:max_windows]
    compact["selected_windows_truncated"] = len(windows) > max_windows
    compact["selected_case_details"] = cases[:max_cases]
    compact["selected_case_details_truncated"] = len(cases) > max_cases
    return compact


def prepare_bundles(
    rows: list[dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> dict[int, dict[str, Any]]:
    bundles: dict[int, dict[str, Any]] = {}
    for row in rows:
        base_paths, source_certs, direct_paths = p1056.selected_certificates_for_row(
            row,
            cache,
            args.target,
            args.selector,
            args.top_k,
            args.source,
        )
        source_by_transfer: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for cert in source_certs:
            selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
            source_by_transfer[p1055.int_value(selected.get("transfer_index"), -1)].append(cert)
        bundles[id(row)] = {
            "base_certs": p1055.load_certs_cached(sorted(base_paths), cache),
            "direct_path_count": len(direct_paths),
            "source_by_transfer": dict(source_by_transfer),
        }
    return bundles


def evaluate_fast(
    rows: list[dict[str, Any]],
    selector: CaseSelector,
    bundles: dict[int, dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    base_certificates: dict[tuple[str, int], dict[str, Any]] = {}
    source_certificates: dict[tuple[str, int], dict[str, Any]] = {}
    selected_rows: list[dict[str, Any]] = []
    selected_case_details: list[dict[str, Any]] = []
    charge = 0.0
    direct_path_count = 0
    factor_hint = 0
    for row in rows:
        selected_cases = selector(row)
        if not selected_cases:
            continue
        selected_rows.append(row)
        factor_hint = max(factor_hint, p1055.int_value(row.get("factor_variable_count")))
        bundle = bundles[id(row)]
        direct_path_count += bundle["direct_path_count"]
        for cert in bundle["base_certs"]:
            base_certificates[p1055.cert_key(cert)] = cert
        transfers = {p1059.transfer_index(case) for case in selected_cases}
        for transfer in transfers:
            for cert in bundle["source_by_transfer"].get(transfer, []):
                source_certificates[p1055.cert_key(cert)] = cert
        for case in selected_cases:
            direct_charge = p1059.direct_charge(case)
            charge += direct_charge
            selected_case_details.append(
                {
                    "direct_ops_over_rho": round(direct_charge, 8),
                    "direct_public_key_verified": bool(case.get("direct_public_key_verified")),
                    "priority_hits": case.get("priority_hits") or [],
                    "row_keys": list(p1059.normalized_rowkeys(case)),
                    "selected_term_support": case.get("selected_term_support") or [],
                    "transfer_index": p1059.transfer_index(case),
                    "window": row["window"],
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
        "selected_window_count": len(selected_rows),
        "selected_windows": [row["window"] for row in selected_rows],
        "source_rank_gain_over_base": gain,
        "source_rows_touching_column": rank["source_rows_touching_column"],
        "source_support_columns": rank["source_support_columns"],
        "source_unique_row_count": rank["source_unique_row_count"],
        "strict_source_charge_over_rho": round(charge, 8),
        "usable_source_certificate_count": len(source_certificates),
    }


def marginal_stats(current: dict[str, Any], union: dict[str, Any], priority_columns: list[int]) -> dict[str, Any]:
    current_charge = p1055.float_value(current.get("strict_source_charge_over_rho")) or 0.0
    union_charge = p1055.float_value(union.get("strict_source_charge_over_rho")) or 0.0
    current_rank = p1055.int_value(current.get("source_rank_gain_over_base"))
    union_rank = p1055.int_value(union.get("source_rank_gain_over_base"))
    current_free = {p1055.int_value(item) for item in current.get("base_plus_source_free_columns") or []}
    union_free = {p1055.int_value(item) for item in union.get("base_plus_source_free_columns") or []}
    removed = sorted(current_free - union_free)
    charge_delta = round(union_charge - current_charge, 8)
    rank_delta = union_rank - current_rank
    return {
        "charge_per_marginal_rank_gain": round(charge_delta / rank_delta, 8) if rank_delta > 0 else None,
        "marginal_charge_over_rho": charge_delta,
        "marginal_rank_gain": rank_delta,
        "priority_columns_freed": [col for col in priority_columns if col in removed],
        "removed_free_columns": removed,
        "union_free_columns": sorted(union_free),
        "union_rank_gain": union_rank,
        "union_strict_source_charge_over_rho": round(union_charge, 8),
    }


def rule_meta(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "complexity": rule["complexity"],
        "expression": rule["expression"],
        "kind": rule.get("kind"),
    }


def sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    stats = item["stats"]
    cpg = stats["charge_per_marginal_rank_gain"]
    return (
        -stats["marginal_rank_gain"],
        -len(stats["removed_free_columns"]),
        cpg if cpg is not None else float("inf"),
        stats["marginal_charge_over_rho"],
        item["rule"]["complexity"],
        item["rule"]["expression"],
    )


def scan_rules(
    rows: list[dict[str, Any]],
    base_selector: CaseSelector,
    base_result: dict[str, Any],
    rules: list[dict[str, Any]],
    bundles: dict[int, dict[str, Any]],
    args: argparse.Namespace,
    priority_columns: list[int],
    max_report: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    positives: list[dict[str, Any]] = []
    for rule in rules:
        selector = union_selectors([base_selector, all_cases_when(rule["fn"])])
        union = evaluate_fast(rows, selector, bundles, args)
        stats = marginal_stats(base_result, union, priority_columns)
        if stats["marginal_rank_gain"] <= 0:
            continue
        positives.append({"rule": rule, "stats": stats, "union": union})
    positives.sort(key=sort_key)
    public = [
        {
            "rule": rule_meta(item["rule"]),
            "stats": item["stats"],
            "union": compact_result(item["union"], max_windows=10, max_cases=8),
        }
        for item in positives[:max_report]
    ]
    return positives, public


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1062", type=Path, default=DEFAULT_P1062)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
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
    parser.add_argument("--max-forward-oracle-report", type=int, default=20)
    parser.add_argument("--max-public-report", type=int, default=20)
    args = parser.parse_args()

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    selected_rowkey = selected_rowkey_from_p1059(args.p1059)
    records, p1054_expression, input_paths = load_p1054_records(args)
    rows_by_split = {
        split: [row for row in records if row["split"] == split]
        for split in ("calibration", "p1052_gap", "forward_validation")
    }
    anchor_rows = [row for row in rows_by_split["forward_validation"] if row["window"] == args.anchor_window]
    cache: dict[Path, list[dict[str, Any]]] = {}
    bundles = prepare_bundles(rows_by_split["calibration"] + rows_by_split["forward_validation"], cache, args)

    exact_selector = p1059.rowkey_first_selector(selected_rowkey)
    anchor_forward_selector = exact_anchor_forward(exact_selector, args.anchor_window)
    train_base = evaluate_fast(rows_by_split["calibration"], exact_selector, bundles, args)
    forward_anchor = evaluate_fast(anchor_rows, exact_selector, bundles, args)
    forward_full = evaluate_fast(rows_by_split["forward_validation"], p1059.all_cases_selector, bundles, args)
    full_forward_stats = marginal_stats(forward_anchor, forward_full, priority_columns)

    train_rules = non_salt_rule_catalog(rows_by_split["calibration"])
    train_positive, train_positive_public = scan_rules(
        rows_by_split["calibration"],
        exact_selector,
        train_base,
        train_rules,
        bundles,
        args,
        priority_columns,
        args.max_public_report,
    )
    selected_rule = train_positive[0]["rule"] if train_positive else None
    public_forward = (
        evaluate_fast(
            rows_by_split["forward_validation"],
            union_selectors([anchor_forward_selector, all_cases_when(selected_rule["fn"])]),
            bundles,
            args,
        )
        if selected_rule
        else forward_anchor
    )
    public_forward_stats = marginal_stats(forward_anchor, public_forward, priority_columns)

    forward_rules = non_salt_rule_catalog(rows_by_split["forward_validation"])
    oracle_positive, oracle_public = scan_rules(
        rows_by_split["forward_validation"],
        anchor_forward_selector,
        forward_anchor,
        forward_rules,
        bundles,
        args,
        priority_columns,
        args.max_forward_oracle_report,
    )
    oracle_best = oracle_positive[0] if oracle_positive else None

    strict_success = (
        selected_rule is not None
        and public_forward_stats["marginal_rank_gain"] > 0
        and public_forward_stats["marginal_charge_over_rho"] < 1.0
    )
    cost_reduced_public = (
        selected_rule is not None
        and public_forward_stats["marginal_rank_gain"] > 0
        and public_forward_stats["marginal_charge_over_rho"] < full_forward_stats["marginal_charge_over_rho"]
    )
    oracle_signal = (
        oracle_best is not None
        and oracle_best["stats"]["marginal_rank_gain"] > 0
        and oracle_best["stats"]["marginal_charge_over_rho"] < full_forward_stats["marginal_charge_over_rho"]
    )
    if strict_success:
        claim_status = "POSITIVE_SIGNAL_P1063_PUBLIC_FREE_COLUMN_BELOW_RHO"
    elif cost_reduced_public:
        claim_status = "POSITIVE_SIGNAL_P1063_PUBLIC_FREE_COLUMN_COST_REDUCED_NOT_RHO"
    elif oracle_signal:
        claim_status = "POSITIVE_SIGNAL_P1063_FORWARD_SOURCE_FEATURE_ORACLE_ONLY"
    elif full_forward_stats["marginal_rank_gain"] > 0:
        claim_status = "NEGATIVE_RESULT_P1063_EXTRA_RANK_DIFFUSE_IN_P1054_BROAD_BRANCH"
    else:
        claim_status = "NEGATIVE_RESULT_P1063_NO_EXTRA_RANK_IN_P1054_BRANCH"

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in input_paths if path.exists()]),
            "input_artifact_digest": digest_paths(input_paths),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "p1059": sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1062": sha256_file(args.p1062) if args.p1062.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1059": str(args.p1059),
            "p1062": str(args.p1062),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NO-SALT-REPLAY",
            "PUBLIC-SOURCE-CONSTRUCTION-FEATURES",
            "FREE-COLUMN-PRESSURE",
            "INDEX-CALCULUS-PRECURSOR",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "forward_anchor": compact_result(forward_anchor),
            "forward_full_p1054": compact_result(forward_full),
            "forward_full_p1054_stats": full_forward_stats,
            "forward_oracle_candidates": oracle_public,
            "public_forward": compact_result(public_forward),
            "public_forward_stats": public_forward_stats,
            "train_base": compact_result(train_base),
            "train_positive_candidates": train_positive_public,
        },
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "forward_oracle_is_not_public_selector": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "rank_direction_without_target_descent_is_incomplete": True,
            "salt_and_rowkey_thresholds_excluded_from_p1063_catalog": True,
        },
        "parameters": {
            "anchor_window": args.anchor_window,
            "column": args.column,
            "excluded_rule_tokens": list(DISALLOWED_RULE_TOKENS),
            "order": args.order,
            "p1054_rule": p1054_expression,
            "priority_columns": priority_columns,
            "selected_public_expression": selected_rule["expression"] if selected_rule else None,
            "selected_rowkey_control": list(selected_rowkey),
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "top_k": args.top_k,
        },
        "record_counts": {
            "calibration_windows": len(rows_by_split["calibration"]),
            "forward_anchor_windows": len(anchor_rows),
            "forward_oracle_positive_count": len(oracle_positive),
            "forward_rule_count": len(forward_rules),
            "forward_windows": len(rows_by_split["forward_validation"]),
            "p1052_gap_windows": len(rows_by_split["p1052_gap"]),
            "train_positive_count": len(train_positive),
            "train_rule_count": len(train_rules),
        },
        "schema": SCHEMA,
        "summary": {
            "anchor_exact_charge": forward_anchor["strict_source_charge_over_rho"],
            "anchor_exact_free_columns": forward_anchor["base_plus_source_free_columns"],
            "anchor_exact_rank_gain": forward_anchor["source_rank_gain_over_base"],
            "claim_status": claim_status,
            "full_p1054_forward_extra_gain": full_forward_stats["marginal_rank_gain"],
            "full_p1054_forward_marginal_charge": full_forward_stats["marginal_charge_over_rho"],
            "full_p1054_forward_removed_free_columns": full_forward_stats["removed_free_columns"],
            "oracle_best_expression": oracle_best["rule"]["expression"] if oracle_best else None,
            "oracle_best_stats": oracle_best["stats"] if oracle_best else None,
            "public_forward_extra_gain": public_forward_stats["marginal_rank_gain"],
            "public_forward_marginal_charge": public_forward_stats["marginal_charge_over_rho"],
            "public_forward_removed_free_columns": public_forward_stats["removed_free_columns"],
            "selected_public_expression": selected_rule["expression"] if selected_rule else None,
            "strict_success": strict_success,
            "weak_positive": strict_success or cost_reduced_public or oracle_signal,
        },
        "timestamp_utc": now_iso(),
    }
    payload["strict_success"] = bool(strict_success)
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={success} selected={selected} public_extra={public_extra} "
        "full_extra={full_extra} full_charge={full_charge} oracle={oracle} out={out}".format(
            claim=claim_status,
            success=payload["strict_success"],
            selected=payload["summary"]["selected_public_expression"],
            public_extra=payload["summary"]["public_forward_extra_gain"],
            full_extra=payload["summary"]["full_p1054_forward_extra_gain"],
            full_charge=payload["summary"]["full_p1054_forward_marginal_charge"],
            oracle=payload["summary"]["oracle_best_expression"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
