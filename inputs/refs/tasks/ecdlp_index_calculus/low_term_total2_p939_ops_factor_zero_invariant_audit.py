#!/usr/bin/env python3
"""P939 representation-invariant audit for P938 ops windows."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p939_ops_factor_zero_invariant_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p939_ops_factor_zero_invariant_audit_probe.json"
P938_SOURCE = STATE_DIR / "low_term_total2_p938_ops_split_perturbation_redteam_probe.json"
SCHEMA = "ecdlp.low_term_total2_p939_ops_factor_zero_invariant_audit.v1"
P936_CONTROL = "p936_ops_high_singleton_window_count_gain_control"
P935_BASE = "p935_repeat2_switch_rank_min1_reproduced"


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
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def source_window(item: dict[str, Any]) -> str:
    return str(item.get("heldout_source_window"))


def window_start(window: str) -> int:
    try:
        return int(window.split("_", 1)[0])
    except (AttributeError, ValueError):
        return 10**12


def qr_artifact_for_window(state_dir: Path, window: str) -> Path | None:
    refreshed = state_dir / f"low_term_total2_ffe_public_factor_quadratic_root_fresh_{window}_expanded_p939_refresh_probe.json"
    if refreshed.exists():
        return refreshed
    regular = state_dir / f"low_term_total2_ffe_public_factor_quadratic_root_fresh_{window}_expanded_probe.json"
    if regular.exists():
        return regular
    return None


def selected_item_by_window(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {source_window(item): item for item in items}


def qr_best_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in ((payload.get("summary") or {}).get("best_policy_surfaces") or []) if isinstance(row, dict)]


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "hash": row.get("selected_factor_hash"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "row_key": row.get("row_key"),
        "ratio": row.get("public_factor_quadratic_root_ops_over_rho"),
        "preserve": bool(row.get("quadratic_preserves_selected_root_pairs")),
        "below_rho": bool(row.get("public_factor_quadratic_root_beats_rho")),
        "false_positive": bool(row.get("chosen_false_positive_source")),
        "coefficients": row.get("selected_factor_coefficients"),
        "factor_index": (row.get("chosen_candidate") or {}).get("factor_index"),
        "factor_total_degree": (row.get("chosen_candidate") or {}).get("factor_total_degree"),
        "factor_monomials": (row.get("chosen_candidate") or {}).get("factor_monomials"),
    }


def hash_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = row.get("selected_factor_hash")
        if key:
            out.setdefault(str(key), []).append(compact_row(row))
    return out


def item_support(item: dict[str, Any]) -> dict[str, Any]:
    support = item.get("heldout_support") or {}
    p903 = (item.get("p903_score") or {}).get("score") or {}
    metadata = item.get("selector_metadata") or {}
    selected_ops = metadata.get("selected_ops_candidate") or {}
    return {
        "selected_rule_names": item.get("rule_names") or [],
        "selected_rule_families": item.get("rule_families") or [],
        "base_rule_name": metadata.get("base_rule_name"),
        "ops_rule_name": selected_ops.get("rule_name"),
        "ops_selected_value": metadata.get("ops_selected_value"),
        "heldout_positive_indices": support.get("positive_indices") or [],
        "heldout_recovered_positive_indices": support.get("recovered_positive_indices") or [],
        "heldout_false_indices": support.get("false_selected_indices") or [],
        "p903_passes": bool((item.get("p903_score") or {}).get("passes")),
        "p903_cost_ops": p903.get("charged_candidate_cost_ops"),
        "p903_selected_c19_indices": p903.get("selected_c19_indices") or [],
    }


def window_record(
    state_dir: Path,
    window: str,
    ops_rule: str | None,
    p936_by: dict[str, dict[str, Any]],
    p935_by: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    path = qr_artifact_for_window(state_dir, window)
    qr_payload = load_json(path) if path else {}
    best_summary = (qr_payload.get("summary") or {}).get("best_policy_summary") or {}
    rows = qr_best_rows(qr_payload)
    hashes = hash_rows(rows)
    hash_counts = Counter({key: len(value) for key, value in hashes.items()})
    surface_count = int_value(best_summary.get("surface_count"))
    preserving = int_value(best_summary.get("quadratic_preserving_surface_count"))
    below = int_value(best_summary.get("charged_below_rho_count"))
    false_count = int_value(best_summary.get("quadratic_false_positive_surface_count"))
    return {
        "artifact": str(path) if path else None,
        "artifact_present": path is not None,
        "best_policy": (qr_payload.get("summary") or {}).get("best_policy"),
        "best_policy_summary": best_summary,
        "control_class": "ops_rule_window" if ops_rule else "non_ops_control",
        "factor_hash_counts": dict(sorted(hash_counts.items())),
        "heldout_window": window,
        "is_ops_rule_window": bool(ops_rule),
        "ops_rule_name": ops_rule,
        "p935_support": item_support(p935_by.get(window) or {}),
        "p936_support": item_support(p936_by.get(window) or {}),
        "quadratic_below_rho_rate": ratio(below, surface_count) if surface_count else None,
        "quadratic_false_positive_rate": ratio(false_count, surface_count) if surface_count else None,
        "quadratic_preserving_rate": ratio(preserving, surface_count) if surface_count else None,
        "repeated_factor_hash_count": sum(1 for count in hash_counts.values() if count >= 2),
        "repeated_factor_hash_surface_count": sum(count for count in hash_counts.values() if count >= 2),
        "surface_rows": [compact_row(row) for row in rows],
        "window_start": window_start(window),
    }


def pair_overlap(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_hashes = {str(row.get("hash")) for row in left.get("surface_rows") or [] if row.get("hash")}
    right_hashes = {str(row.get("hash")) for row in right.get("surface_rows") or [] if row.get("hash")}
    shared = sorted(left_hashes & right_hashes)
    shared_rows: dict[str, dict[str, Any]] = {}
    for key in shared:
        lrows = [row for row in left.get("surface_rows") or [] if row.get("hash") == key]
        rrows = [row for row in right.get("surface_rows") or [] if row.get("hash") == key]
        shared_rows[key] = {
            "left_rows": lrows,
            "right_rows": rrows,
            "all_rows_below_rho": all(bool(row.get("below_rho")) for row in lrows + rrows),
            "all_rows_preserve": all(bool(row.get("preserve")) for row in lrows + rrows),
            "any_false_positive": any(bool(row.get("false_positive")) for row in lrows + rrows),
            "left_count": len(lrows),
            "right_count": len(rrows),
        }
    return {
        "left_window": left.get("heldout_window"),
        "right_window": right.get("heldout_window"),
        "left_class": left.get("control_class"),
        "right_class": right.get("control_class"),
        "pair_class": "ops_ops"
        if left.get("is_ops_rule_window") and right.get("is_ops_rule_window")
        else ("ops_control" if left.get("is_ops_rule_window") or right.get("is_ops_rule_window") else "control_control"),
        "shared_factor_hash_count": len(shared),
        "shared_factor_hashes": shared,
        "shared_hash_rows": shared_rows,
    }


def aggregate(records: list[dict[str, Any]], class_name: str) -> dict[str, Any]:
    selected = [record for record in records if record.get("control_class") == class_name and record.get("artifact_present")]
    if not selected:
        return {"window_count": 0}
    return {
        "window_count": len(selected),
        "mean_below_rho_rate": round(
            sum(float(record.get("quadratic_below_rho_rate") or 0.0) for record in selected) / len(selected),
            8,
        ),
        "mean_false_positive_rate": round(
            sum(float(record.get("quadratic_false_positive_rate") or 0.0) for record in selected) / len(selected),
            8,
        ),
        "mean_preserving_rate": round(
            sum(float(record.get("quadratic_preserving_rate") or 0.0) for record in selected) / len(selected),
            8,
        ),
        "total_repeated_hash_surface_count": sum(
            int_value(record.get("repeated_factor_hash_surface_count")) for record in selected
        ),
        "windows": [record.get("heldout_window") for record in selected],
    }


def determine_claim(ops_pair: dict[str, Any] | None, pair_summary: dict[str, Any]) -> str:
    if not ops_pair:
        return "NEGATIVE_RESULT_P939_MISSING_OPS_FACTOR_ARTIFACT"
    if int_value(ops_pair.get("shared_factor_hash_count")) == 0:
        return "NEGATIVE_RESULT_P939_OPS_WINDOWS_DO_NOT_SHARE_FACTOR_ZERO_HASH"
    clean_shared = [
        row
        for row in (ops_pair.get("shared_hash_rows") or {}).values()
        if row.get("all_rows_below_rho") and row.get("all_rows_preserve") and not row.get("any_false_positive")
    ]
    if not clean_shared:
        return "NEGATIVE_RESULT_P939_SHARED_FACTOR_HASH_FAILS_CLEAN_GATE"
    if int_value(pair_summary.get("pairs_with_shared_hash_count")) > 1:
        return "P939_OPS_SHARE_CLEAN_FACTOR_ZERO_INVARIANT_BUT_NONUNIQUE"
    return "P939_OPS_SHARE_UNIQUE_CLEAN_FACTOR_ZERO_INVARIANT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p938 = load_json(args.p938_source)
    ops_rule_windows = {
        str(window): str(rule)
        for window, rule in ((p938.get("split_details") or {}).get("ops_rule_windows") or {}).items()
    }
    second = (p938.get("summary") or {}).get("second_holdout") or {}
    p936_by = selected_item_by_window(list(second.get(P936_CONTROL) or []))
    p935_by = selected_item_by_window(list(second.get(P935_BASE) or []))
    windows = sorted(set(p936_by) | set(p935_by), key=lambda item: (window_start(item), item))
    records = [
        window_record(args.state_dir, window, ops_rule_windows.get(window), p936_by, p935_by)
        for window in windows
    ]
    pairs = [pair_overlap(left, right) for left, right in combinations(records, 2)]
    pairs_with_shared = [pair for pair in pairs if int_value(pair.get("shared_factor_hash_count")) > 0]
    ops_pairs = [pair for pair in pairs if pair.get("pair_class") == "ops_ops"]
    ops_pair = ops_pairs[0] if ops_pairs else None
    max_shared = max((int_value(pair.get("shared_factor_hash_count")) for pair in pairs), default=0)
    pair_summary = {
        "max_shared_factor_hash_count": max_shared,
        "ops_pair_shared_factor_hash_count": int_value((ops_pair or {}).get("shared_factor_hash_count")),
        "ops_pair_shared_rank": 1
        + sum(
            1
            for pair in pairs
            if int_value(pair.get("shared_factor_hash_count"))
            > int_value((ops_pair or {}).get("shared_factor_hash_count"))
        )
        if ops_pair
        else None,
        "pairs_with_shared_hash_count": len(pairs_with_shared),
        "pairs_with_shared_hash_by_class": dict(sorted(Counter(pair.get("pair_class") for pair in pairs_with_shared).items())),
        "top_shared_pairs": sorted(
            pairs_with_shared,
            key=lambda pair: (
                -int_value(pair.get("shared_factor_hash_count")),
                str(pair.get("pair_class")),
                str(pair.get("left_window")),
                str(pair.get("right_window")),
            ),
        )[:16],
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p938_source": str(args.p938_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(ops_pair, pair_summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores frozen P936/P938 rows and frozen/generated FFE artifacts.",
            "REPRESENTATION-MECHANISM-AUDIT: this tests factor-zero/quadratic-root invariants, not full target descent.",
            "NON-UNIQUENESS-TESTED: shared hashes are compared against non-ops control-window pairs.",
            "P903-BLIND-FIT: inherits the P936/P938 selector lineage.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus component audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p939_ops_factor_zero_invariant_audit",
        "parameters": {
            "ops_rule_windows": ops_rule_windows,
            "p936_control": P936_CONTROL,
            "p935_base": P935_BASE,
        },
        "pair_overlaps": pair_summary,
        "schema": SCHEMA,
        "summary": {
            "ops_pair": ops_pair,
            "ops_windows": aggregate(records, "ops_rule_window"),
            "control_windows": aggregate(records, "non_ops_control"),
            "window_records": records,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p938-source", type=Path, default=P938_SOURCE)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    ops = (payload.get("summary") or {}).get("ops_windows") or {}
    controls = (payload.get("summary") or {}).get("control_windows") or {}
    pair = (payload.get("summary") or {}).get("ops_pair") or {}
    print(
        "claim={claim} ops_windows={ops_n} controls={ctrl_n} "
        "ops_shared_hashes={shared} shared_pairs={pairs} "
        "ops_below_mean={ops_below} control_below_mean={ctrl_below} out={out}".format(
            claim=payload.get("claim_status"),
            ops_n=ops.get("window_count"),
            ctrl_n=controls.get("window_count"),
            shared=pair.get("shared_factor_hash_count"),
            pairs=(payload.get("pair_overlaps") or {}).get("pairs_with_shared_hash_count"),
            ops_below=ops.get("mean_below_rho_rate"),
            ctrl_below=controls.get("mean_below_rho_rate"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
