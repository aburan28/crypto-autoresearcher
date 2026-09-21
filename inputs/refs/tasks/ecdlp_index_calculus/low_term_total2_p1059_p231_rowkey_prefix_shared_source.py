#!/usr/bin/env python3
"""P1059 case-level row-key prefix audit for the P1057/P1058 anchor."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1056_p231_public_source_cost_reducer as p1056
import low_term_total2_p1057_p231_single_anchor_direction_subgate as p1057
import low_term_total2_p1058_p231_disjoint_replication_batching as p1058


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1059_p231_rowkey_prefix_shared_source.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1056 = STATE_DIR / "low_term_total2_p1056_p231_public_source_cost_reducer_probe.json"
DEFAULT_P1057 = STATE_DIR / "low_term_total2_p1057_p231_single_anchor_direction_subgate_probe.json"
DEFAULT_P1058 = STATE_DIR / "low_term_total2_p1058_p231_disjoint_replication_batching_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1059_p231_rowkey_prefix_shared_source.v1"


CaseSelector = Callable[[dict[str, Any]], list[dict[str, Any]]]


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


def parse_window(value: str) -> tuple[int, int]:
    start, end = value.split("_", 1)
    return int(start), int(end)


def normalized_rowkeys(case: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(str(item) for item in (case.get("row_keys") or [])))


def transfer_index(case: dict[str, Any]) -> int:
    return p1055.int_value(case.get("transfer_index"), -1)


def direct_charge(case: dict[str, Any]) -> float:
    return p1055.float_value(case.get("direct_ops_over_rho")) or 0.0


def first_by_transfer(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not cases:
        return []
    return [min(cases, key=transfer_index)]


def last_by_transfer(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not cases:
        return []
    return [max(cases, key=transfer_index)]


def rowkey_first_selector(rowkey: tuple[str, ...]) -> CaseSelector:
    def select(row: dict[str, Any]) -> list[dict[str, Any]]:
        matches = [case for case in row.get("source_cases") or [] if normalized_rowkeys(case) == rowkey]
        return first_by_transfer(matches)

    return select


def rowkey_all_selector(rowkey: tuple[str, ...]) -> CaseSelector:
    def select(row: dict[str, Any]) -> list[dict[str, Any]]:
        return [case for case in row.get("source_cases") or [] if normalized_rowkeys(case) == rowkey]

    return select


def all_cases_selector(row: dict[str, Any]) -> list[dict[str, Any]]:
    return list(row.get("source_cases") or [])


def first_transfer_selector(row: dict[str, Any]) -> list[dict[str, Any]]:
    return first_by_transfer(list(row.get("source_cases") or []))


def last_transfer_selector(row: dict[str, Any]) -> list[dict[str, Any]]:
    return last_by_transfer(list(row.get("source_cases") or []))


def verified_only_selector(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [case for case in row.get("source_cases") or [] if bool(case.get("direct_public_key_verified"))]


def transfer_set(cases: list[dict[str, Any]]) -> set[int]:
    return {transfer_index(case) for case in cases if transfer_index(case) >= 0}


def compact_result(result: dict[str, Any], max_windows: int = 20, max_cases: int = 16) -> dict[str, Any]:
    compact = dict(result)
    windows = compact.get("selected_windows") or []
    cases = compact.get("selected_case_details") or []
    compact["selected_windows"] = windows[:max_windows]
    compact["selected_windows_truncated"] = len(windows) > max_windows
    compact["selected_case_details"] = cases[:max_cases]
    compact["selected_case_details_truncated"] = len(cases) > max_cases
    return compact


def evaluate_case_policy(
    rows: list[dict[str, Any]],
    selector: CaseSelector,
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    base_paths: set[Path] = set()
    direct_paths: set[Path] = set()
    source_certificates: dict[tuple[str, int], dict[str, Any]] = {}
    selected_rows: list[dict[str, Any]] = []
    selected_case_details: list[dict[str, Any]] = []
    charge = 0.0

    for row in rows:
        selected_cases = selector(row)
        if not selected_cases:
            continue
        selected_rows.append(row)
        transfers = transfer_set(selected_cases)
        base, source_certs, direct = p1056.selected_certificates_for_row(
            row,
            cache,
            args.target,
            args.selector,
            args.top_k,
            args.source,
        )
        base_paths.update(base)
        direct_paths.update(direct)
        for case in selected_cases:
            charge += direct_charge(case)
            selected_case_details.append(
                {
                    "direct_ops_over_rho": round(direct_charge(case), 8),
                    "direct_public_key_verified": bool(case.get("direct_public_key_verified")),
                    "priority_hits": case.get("priority_hits") or [],
                    "row_keys": list(normalized_rowkeys(case)),
                    "transfer_index": transfer_index(case),
                    "window": row["window"],
                }
            )
        for cert in source_certs:
            selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
            if p1055.int_value(selected.get("transfer_index"), -1) in transfers:
                source_certificates[p1055.cert_key(cert)] = cert

    base_certs = p1055.load_certs_cached(sorted(base_paths), cache)
    factor_hint = max([p1055.int_value(row.get("factor_variable_count")) for row in selected_rows] or [0])
    rank = p1055.rank_audit(
        base_certs,
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
        "direct_certificate_artifact_count": len(direct_paths),
        "factor_variable_count": rank["factor_variable_count"],
        "selected_case_count": len(selected_case_details),
        "selected_case_details": selected_case_details,
        "selected_window_count": len(selected_rows),
        "selected_windows": [row["window"] for row in selected_rows],
        "source_rank_gain_over_base": gain,
        "source_rows_touching_column": rank["source_rows_touching_column"],
        "source_unique_row_count": rank["source_unique_row_count"],
        "strict_source_charge_over_rho": round(charge, 8),
        "usable_source_certificate_count": len(source_certificates),
    }


def choose_rowkey_policy(
    train_rows: list[dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> tuple[tuple[str, ...] | None, list[dict[str, Any]]]:
    rowkeys = sorted(
        {
            normalized_rowkeys(case)
            for row in train_rows
            for case in row.get("source_cases") or []
            if normalized_rowkeys(case)
        }
    )
    candidates = []
    for rowkey in rowkeys:
        result = evaluate_case_policy(train_rows, rowkey_first_selector(rowkey), cache, args)
        if result["source_rank_gain_over_base"] < args.min_train_rank_gain:
            continue
        if result["strict_source_charge_over_rho"] >= args.max_train_charge_over_rho:
            continue
        candidates.append({"rowkey": rowkey, "train": result})
    candidates.sort(
        key=lambda item: (
            item["train"]["charge_per_rank_gain"] or float("inf"),
            item["train"]["strict_source_charge_over_rho"],
            list(item["rowkey"]),
        )
    )
    public = [
        {
            "rowkey": list(item["rowkey"]),
            "train": compact_result(item["train"], max_windows=8, max_cases=8),
        }
        for item in candidates[:20]
    ]
    return (candidates[0]["rowkey"] if candidates else None), public


def load_rows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], str, str, str, list[Path]]:
    records, p1054_expression, p1056_expression, p1057_expression, input_paths = p1058.load_records_and_rules(args)
    return records, p1054_expression, p1056_expression, p1057_expression, input_paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--p1056", type=Path, default=DEFAULT_P1056)
    parser.add_argument("--p1057", type=Path, default=DEFAULT_P1057)
    parser.add_argument("--p1058", type=Path, default=DEFAULT_P1058)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
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
    parser.add_argument("--min-train-rank-gain", type=int, default=2)
    parser.add_argument("--min-forward-rank-gain", type=int, default=2)
    parser.add_argument("--max-train-charge-over-rho", type=float, default=1.0)
    parser.add_argument("--max-forward-charge-over-rho", type=float, default=1.0)
    args = parser.parse_args()

    records, p1054_expression, p1056_expression, p1057_expression, input_paths = load_rows(args)
    direction_rule = p1055.compile_rule(p1057_expression)
    rows_by_split = {
        split: [row for row in records if row["split"] == split]
        for split in ("calibration", "p1052_gap", "forward_validation")
    }
    frozen_rows_by_split = {
        split: [row for row in rows if direction_rule(row)]
        for split, rows in rows_by_split.items()
    }
    anchor_start, anchor_end = parse_window(args.anchor_window)
    anchor_rows = [
        row
        for row in frozen_rows_by_split["forward_validation"]
        if row["window_start"] == anchor_start and row["window_end"] == anchor_end
    ]
    before_anchor_rows = [
        row for row in frozen_rows_by_split["forward_validation"] if row["window_end"] < anchor_start
    ]
    after_anchor_rows = [
        row for row in frozen_rows_by_split["forward_validation"] if row["window_start"] > anchor_end
    ]

    cache: dict[Path, list[dict[str, Any]]] = {}
    selected_rowkey, rowkey_candidates = choose_rowkey_policy(
        frozen_rows_by_split["calibration"],
        cache,
        args,
    )

    controls = {
        "all_cases": all_cases_selector,
        "first_transfer": first_transfer_selector,
        "last_transfer": last_transfer_selector,
        "verified_only_post_verifier_diagnostic": verified_only_selector,
    }
    if selected_rowkey is not None:
        controls["calibrated_rowkey_first"] = rowkey_first_selector(selected_rowkey)
        controls["calibrated_rowkey_all"] = rowkey_all_selector(selected_rowkey)

    splits = {
        "calibration": frozen_rows_by_split["calibration"],
        "p1052_gap": frozen_rows_by_split["p1052_gap"],
        "forward_all": frozen_rows_by_split["forward_validation"],
        "forward_anchor": anchor_rows,
        "forward_before_anchor": before_anchor_rows,
        "forward_after_anchor": after_anchor_rows,
    }
    results = {
        name: {
            split: compact_result(evaluate_case_policy(rows, selector, cache, args))
            for split, rows in splits.items()
        }
        for name, selector in controls.items()
    }

    rowkey_forward = (results.get("calibrated_rowkey_first") or {}).get("forward_anchor") or {}
    rowkey_train = (results.get("calibrated_rowkey_first") or {}).get("calibration") or {}
    if selected_rowkey is None:
        claim_status = "NEGATIVE_RESULT_P1059_NO_CALIBRATION_ROWKEY_PREFIX"
    elif (
        rowkey_train.get("source_rank_gain_over_base", 0) >= args.min_train_rank_gain
        and rowkey_forward.get("source_rank_gain_over_base", 0) >= args.min_forward_rank_gain
        and (rowkey_forward.get("strict_source_charge_over_rho") or float("inf"))
        < args.max_forward_charge_over_rho
    ):
        claim_status = "POSITIVE_SIGNAL_P1059_ROWKEY_PREFIX_TOTAL_BELOW_RHO_LOW_SUPPORT"
    else:
        claim_status = "NEGATIVE_RESULT_P1059_ROWKEY_PREFIX_FAILS_FORWARD"

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in input_paths if path.exists()]),
            "input_artifact_digest": digest_paths(input_paths),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "p1056": sha256_file(args.p1056) if args.p1056.exists() else None,
            "p1057": sha256_file(args.p1057) if args.p1057.exists() else None,
            "p1058": sha256_file(args.p1058) if args.p1058.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1056": str(args.p1056),
            "p1057": str(args.p1057),
            "p1058": str(args.p1058),
            "script": str(Path(__file__)),
        },
        "calibration_rowkey_candidates": rowkey_candidates,
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "FROZEN-WINDOW-RULE",
            "CALIBRATION-SELECTED",
            "LOW-SUPPORT",
            "PUBLIC-ROWKEY-PREFIX",
            "TARGET-ELIMINATED-FACTOR-RANK",
            "INDEX-CALCULUS-PRECURSOR",
            "NOT-SPARSE-LA-CLOSURE",
            "NOT-TARGET-DESCENT",
            "POLLARD-RHO-BOUNDARY",
        ],
        "controls": results,
        "honesty_boundary": {
            "case_prefix_selected_from_calibration_only": True,
            "cryptographic_scale_unproved": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "rank_measured_from_target_eliminated_certificate_rows": True,
            "verified_only_control_is_post_verifier_diagnostic": True,
        },
        "parameters": {
            "anchor_window": args.anchor_window,
            "column": args.column,
            "order": args.order,
            "p1054_rule": p1054_expression,
            "p1056_rule": p1056_expression,
            "p1057_rule": p1057_expression,
            "selected_rowkey": list(selected_rowkey) if selected_rowkey is not None else None,
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "top_k": args.top_k,
        },
        "record_counts": {
            "frozen_calibration_windows": len(frozen_rows_by_split["calibration"]),
            "frozen_forward_after_anchor_windows": len(after_anchor_rows),
            "frozen_forward_all_windows": len(frozen_rows_by_split["forward_validation"]),
            "frozen_forward_anchor_windows": len(anchor_rows),
            "frozen_forward_before_anchor_windows": len(before_anchor_rows),
            "frozen_p1052_gap_windows": len(frozen_rows_by_split["p1052_gap"]),
            "p1056_calibration_windows": len(rows_by_split["calibration"]),
            "p1056_forward_windows": len(rows_by_split["forward_validation"]),
            "p1056_gap_windows": len(rows_by_split["p1052_gap"]),
        },
        "schema": SCHEMA,
        "summary": {
            "anchor_rowkey_prefix_charge": rowkey_forward.get("strict_source_charge_over_rho"),
            "anchor_rowkey_prefix_charge_per_rank_gain": rowkey_forward.get("charge_per_rank_gain"),
            "anchor_rowkey_prefix_rank_gain": rowkey_forward.get("source_rank_gain_over_base"),
            "anchor_whole_window_charge": results["all_cases"]["forward_anchor"][
                "strict_source_charge_over_rho"
            ],
            "anchor_whole_window_rank_gain": results["all_cases"]["forward_anchor"][
                "source_rank_gain_over_base"
            ],
            "claim_status": claim_status,
            "rowkey_prefix_forward_below_rho": (
                (rowkey_forward.get("strict_source_charge_over_rho") or float("inf"))
                < args.max_forward_charge_over_rho
            ),
            "selected_rowkey": list(selected_rowkey) if selected_rowkey is not None else None,
            "train_rowkey_prefix_charge": rowkey_train.get("strict_source_charge_over_rho"),
            "train_rowkey_prefix_rank_gain": rowkey_train.get("source_rank_gain_over_base"),
        },
        "timestamp_utc": now_iso(),
    }
    payload["strict_success"] = claim_status.startswith("POSITIVE_SIGNAL")
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={success} rowkey={rowkey} "
        "anchor_charge={charge} anchor_gain={gain} whole_charge={whole} out={out}".format(
            claim=claim_status,
            success=payload["strict_success"],
            rowkey=payload["summary"]["selected_rowkey"],
            charge=payload["summary"]["anchor_rowkey_prefix_charge"],
            gain=payload["summary"]["anchor_rowkey_prefix_rank_gain"],
            whole=payload["summary"]["anchor_whole_window_charge"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
