#!/usr/bin/env python3
"""Compare positive order-9887 trigger families against the P555 off-family repeat.

P555 showed that pinning recurrent row pairs was not enough: the verifier-positive
rows repeated support [1,9,11] instead of moving to desired families.  This
diagnostic joins existing priority-scout rows back to their public source rows
and shared-product gate metrics, then extracts public feature deltas that can be
used by the next source generator.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_POSITIVE_SCOUTS = ",".join(
    str(path)
    for path in (
        STATE_DIR / "low_term_total2_priority_column_form_scout_20224_20231_remaining_cols_11779_7_9887_6_7_verified_probe.json",
        STATE_DIR / "low_term_total2_priority_column_form_scout_20320_20327_remaining_cols_11779_7_9887_6_7_verified_probe.json",
        STATE_DIR / "low_term_total2_priority_column_form_scout_20336_20343_remaining_cols_11779_7_9887_6_7_verified_probe.json",
        STATE_DIR / "low_term_total2_priority_column_form_scout_20504_20511_remaining_cols_11779_7_9887_6_7_verified_probe.json",
        STATE_DIR / "low_term_total2_priority_column_form_scout_20512_20519_remaining_cols_11779_7_9887_6_7_verified_probe.json",
        STATE_DIR / "low_term_total2_priority_column_form_scout_20536_20543_remaining_cols_11779_7_9887_6_7_verified_probe.json",
    )
)
DEFAULT_OFF_SCOUTS = str(
    STATE_DIR
    / "low_term_total2_priority_column_form_scout_p555_order9887_pinned_family_20544_20554_density_gate_9887_1_6_12_13_probe.json"
)
DEFAULT_P555_SOURCE = STATE_DIR / "low_term_total2_order9887_p555_pinned_family_source_20544_20554_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_p556_column_conditioned_leaf_signature_delta_20224_20554_probe.json"
POSITIVE_FAMILIES = {
    (1, 6, 12),
    (1, 6, 13),
    (1, 7, 12),
    (1, 6, 7, 13),
}
OFF_FAMILY = (1, 9, 11)
TARGET = "67.a1@9803"
ORDER = 9887


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_paths(raw: str) -> list[Path]:
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def support_tuple(report: dict[str, Any]) -> tuple[int, ...]:
    values = report.get("term_support") or report.get("coeff_support") or []
    return tuple(int_value(value) for value in values)


def support_key(values: tuple[int, ...]) -> str:
    return ",".join(str(value) for value in values)


def row_pair_key(row_keys: list[str]) -> str:
    return " + ".join(sorted(str(item) for item in row_keys))


def salt_of(row_key: str) -> str:
    match = re.search(r"salt(\d+)", row_key)
    return f"salt{match.group(1)}" if match else row_key


def case_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("target"),
        int_value(row.get("transfer_index")),
        row.get("selector"),
        int_value(row.get("top_k")),
        tuple(sorted(str(item) for item in row.get("row_keys") or [])),
    )


def load_source_rows(source: Path) -> dict[tuple[Any, ...], dict[str, Any]]:
    payload = load_json(source)
    rows: dict[tuple[Any, ...], dict[str, Any]] = {}
    for policy in (payload.get("policies") or {}).values():
        for row in policy.get("stress_leaf_results") or []:
            if isinstance(row, dict):
                rows[case_key(row)] = row
    return rows


def load_product_cases(product_artifact: Path) -> dict[tuple[Any, ...], dict[str, Any]]:
    payload = load_json(product_artifact)
    rows: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in payload.get("cases") or []:
        if isinstance(row, dict):
            rows[case_key(row)] = row
    return rows


def leaf_signature(source_row: dict[str, Any]) -> tuple[int, ...]:
    indices: list[int] = []
    for entry in source_row.get("row_leaf_keys") or []:
        indices.extend(int_value(value) for value in entry.get("leaf_indices") or [])
    return tuple(sorted(indices))


def row_leaf_signature(source_row: dict[str, Any]) -> tuple[str, ...]:
    tokens: list[str] = []
    for entry in source_row.get("row_leaf_keys") or []:
        salt = salt_of(str(entry.get("row_key")))
        indices = ",".join(str(int_value(value)) for value in entry.get("leaf_indices") or [])
        tokens.append(f"{salt}:{indices}")
    return tuple(sorted(tokens))


def same_leaf_index(signature: tuple[int, ...]) -> bool:
    return bool(signature) and len(set(signature)) == 1


def classify(report: dict[str, Any], fallback: str) -> str:
    support = support_tuple(report)
    if support in POSITIVE_FAMILIES:
        return "positive_family"
    if support == OFF_FAMILY:
        return "off_family"
    return fallback


def compact_case(
    report: dict[str, Any],
    scout_path: Path,
    class_hint: str,
    source_row: dict[str, Any] | None,
    product_case: dict[str, Any] | None,
) -> dict[str, Any]:
    row_keys = [str(item) for item in report.get("row_keys") or []]
    support = support_tuple(report)
    source_row = source_row or {}
    product_case = product_case or {}
    gate_metrics = product_case.get("gate_metrics") if isinstance(product_case.get("gate_metrics"), dict) else {}
    signature = leaf_signature(source_row)
    return {
        "case_class": classify(report, class_hint),
        "direct_ops_over_rho": report.get("direct_ops_over_rho"),
        "duplicate_signature_density": gate_metrics.get("duplicate_signature_density"),
        "gate_selected": bool(report.get("public_product_gate_selected")),
        "leaf_signature": list(signature),
        "leaf_signature_key": ",".join(str(value) for value in signature),
        "matched_product_case": bool(product_case),
        "matched_source_row": bool(source_row),
        "order": int_value(report.get("order")),
        "priority_coeff_hits": report.get("priority_coeff_hits") or [],
        "priority_term_hits": report.get("priority_term_hits") or [],
        "public_key_verified": bool(report.get("public_key_verified_replay") or report.get("verified")),
        "rank": int_value(report.get("rank_replay")),
        "row_keys": row_keys,
        "row_leaf_signature": list(row_leaf_signature(source_row)),
        "row_pair_key": row_pair_key(row_keys),
        "row_salts": [salt_of(key) for key in sorted(row_keys)],
        "same_leaf_index": same_leaf_index(signature),
        "scan_row_count": int_value(report.get("scan_row_count")),
        "scout": str(scout_path),
        "selected_leaf_count": int_value(source_row.get("selected_leaf_count")),
        "selected_row_count": int_value(source_row.get("selected_row_count")),
        "selector": report.get("selector"),
        "shared_ops_over_rho": report.get("shared_ops_over_rho"),
        "source": report.get("source"),
        "source_below_rho": bool(source_row.get("below_rho")),
        "source_ops_over_rho": source_row.get("ops_over_rho"),
        "source_public_key_verified": bool(source_row.get("public_key_verified")),
        "source_verified": bool(source_row.get("source_verified")),
        "support": list(support),
        "support_key": support_key(support),
        "target": report.get("target"),
        "top_k": int_value(report.get("top_k")),
        "transfer_index": int_value(report.get("transfer_index")),
        "unique_selected_leaf_signature_count": int_value(gate_metrics.get("unique_selected_leaf_signature_count")),
        "verified": bool(report.get("verified")),
    }


def collect_cases(scout_paths: list[Path], class_hint: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cases: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    source_cache: dict[Path, dict[tuple[Any, ...], dict[str, Any]]] = {}
    product_cache: dict[Path, dict[tuple[Any, ...], dict[str, Any]]] = {}
    for scout_path in scout_paths:
        scout = load_json(scout_path)
        for report in scout.get("case_reports") or []:
            if report.get("target") != TARGET or int_value(report.get("order")) != ORDER:
                continue
            if not (report.get("public_key_verified_replay") or report.get("verified")):
                continue
            source_path = Path(str(report.get("source")))
            product_path = Path(str(report.get("artifact")))
            if source_path not in source_cache:
                source_cache[source_path] = load_source_rows(source_path)
            if product_path not in product_cache:
                product_cache[product_path] = load_product_cases(product_path)
            key = case_key(report)
            source_row = source_cache[source_path].get(key)
            product_case = product_cache[product_path].get(key)
            if source_row is None:
                errors.append({"error": "missing_source_row", "key": repr(key), "scout": str(scout_path), "source": str(source_path)})
            if product_case is None:
                errors.append({"error": "missing_product_case", "key": repr(key), "artifact": str(product_path), "scout": str(scout_path)})
            cases.append(compact_case(report, scout_path, class_hint, source_row, product_case))
    return cases, errors


def counter_dict(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in counter.most_common()}


def summarize(cases: list[dict[str, Any]]) -> dict[str, Any]:
    by_class = Counter(case["case_class"] for case in cases)
    by_support = Counter(case["support_key"] for case in cases)
    by_leaf = Counter((case["case_class"], case["leaf_signature_key"]) for case in cases)
    by_pair = Counter((case["case_class"], case["row_pair_key"]) for case in cases)
    return {
        "case_count": len(cases),
        "class_counts": counter_dict(by_class),
        "matched_product_case_count": sum(1 for case in cases if case["matched_product_case"]),
        "matched_source_row_count": sum(1 for case in cases if case["matched_source_row"]),
        "same_leaf_index_count": sum(1 for case in cases if case["same_leaf_index"]),
        "support_counts": counter_dict(by_support),
        "top_leaf_signatures_by_class": counter_dict(by_leaf),
        "top_row_pairs_by_class": counter_dict(by_pair),
    }


def class_feature_counters(cases: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for case in cases:
        cls = str(case["case_class"])
        tokens = [
            f"leaf={case['leaf_signature_key']}",
            f"selector={case['selector']}",
            f"top_k={case['top_k']}",
            f"pair={case['row_pair_key']}",
            f"same_leaf={case['same_leaf_index']}",
            f"selector_leaf={case['selector']}|{case['leaf_signature_key']}",
            f"topk_leaf={case['top_k']}|{case['leaf_signature_key']}",
        ]
        for token in tokens:
            counters[cls][token] += 1
    return counters


def feature_deltas(cases: list[dict[str, Any]]) -> dict[str, Any]:
    counters = class_feature_counters(cases)
    positive = counters.get("positive_family", Counter())
    off = counters.get("off_family", Counter())
    return {
        "positive_minus_off": counter_dict(positive - off),
        "off_minus_positive": counter_dict(off - positive),
        "positive_features": counter_dict(positive),
        "off_features": counter_dict(off),
    }


def matched_row_pair_deltas(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for case in cases:
        by_pair[str(case["row_pair_key"])][str(case["case_class"])].append(case)
    deltas: list[dict[str, Any]] = []
    for pair, classes in sorted(by_pair.items()):
        positives = classes.get("positive_family", [])
        off = classes.get("off_family", [])
        if not positives or not off:
            continue
        deltas.append(
            {
                "row_pair_key": pair,
                "positive_leaf_signatures": sorted({case["leaf_signature_key"] for case in positives}),
                "positive_supports": sorted({case["support_key"] for case in positives}),
                "positive_top_ks": sorted({case["top_k"] for case in positives}),
                "positive_transfers": sorted({case["transfer_index"] for case in positives}),
                "off_leaf_signatures": sorted({case["leaf_signature_key"] for case in off}),
                "off_supports": sorted({case["support_key"] for case in off}),
                "off_top_ks": sorted({case["top_k"] for case in off}),
                "off_transfers": sorted({case["transfer_index"] for case in off}),
            }
        )
    return deltas


def load_p555_lanes(path: Path) -> list[dict[str, Any]]:
    source = load_json(path)
    lanes: list[dict[str, Any]] = []
    for policy in (source.get("policies") or {}).values():
        lane = policy.get("lane")
        if isinstance(lane, dict):
            lanes.append(lane)
    return lanes


def recommendations(cases: list[dict[str, Any]], p555_source: Path) -> list[dict[str, Any]]:
    positives = [case for case in cases if case["case_class"] == "positive_family"]
    off_cases = [case for case in cases if case["case_class"] == "off_family"]
    positives_by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    positives_by_support: dict[str, list[dict[str, Any]]] = defaultdict(list)
    off_by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in positives:
        positives_by_pair[str(case["row_pair_key"])].append(case)
        positives_by_support[str(case["support_key"])].append(case)
    for case in off_cases:
        off_by_pair[str(case["row_pair_key"])].append(case)

    out: list[dict[str, Any]] = []
    for lane in load_p555_lanes(p555_source):
        desired = ",".join(str(value) for value in lane.get("desired_family") or [])
        spec = lane.get("source_policy_mutation") if isinstance(lane.get("source_policy_mutation"), dict) else {}
        pair = row_pair_key([str(item) for item in spec.get("pin_row_keys") or []])
        same_pair_positives = positives_by_pair.get(pair, [])
        template_positives = same_pair_positives or positives_by_support.get(desired, [])
        if not template_positives:
            continue
        force_leafs = sorted({case["leaf_signature_key"] for case in template_positives if case["leaf_signature_key"]})
        avoid_leafs = sorted({case["leaf_signature_key"] for case in off_by_pair.get(pair, []) if case["leaf_signature_key"]})
        out.append(
            {
                "lane_id": lane.get("lane_id"),
                "desired_family": lane.get("desired_family"),
                "pin_row_keys": spec.get("pin_row_keys") or [],
                "recommendation": "force_public_leaf_signature_before_support_replay",
                "evidence_scope": "same_row_pair" if same_pair_positives else "same_desired_family_other_pair",
                "force_leaf_signatures": force_leafs,
                "force_top_ks": sorted({case["top_k"] for case in template_positives}),
                "force_selectors": sorted({case["selector"] for case in template_positives}),
                "avoid_leaf_signatures_seen_in_p555": avoid_leafs,
                "positive_supports": sorted({case["support_key"] for case in template_positives}),
                "positive_transfers": sorted({case["transfer_index"] for case in template_positives}),
                "off_family_transfers": sorted({case["transfer_index"] for case in off_by_pair.get(pair, [])}),
            }
        )
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive-scouts", default=DEFAULT_POSITIVE_SCOUTS)
    parser.add_argument("--off-family-scouts", default=DEFAULT_OFF_SCOUTS)
    parser.add_argument("--p555-source", type=Path, default=DEFAULT_P555_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    positive_cases, positive_errors = collect_cases(parse_paths(args.positive_scouts), "positive_candidate")
    off_cases, off_errors = collect_cases(parse_paths(args.off_family_scouts), "off_candidate")
    cases = positive_cases + off_cases
    recs = recommendations(cases, args.p555_source)
    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: this is a toy-prime artifact audit for 67.a1@9803/order 9887.",
            "MODEL-BOUND: source signatures are taken from the current low-term total-2 shared-product harness.",
            "HEURISTIC: leaf-signature deltas are source-generation hypotheses, not proofs of relation probability.",
            "NO SPEEDUP CLAIM: this diagnostic does not perform new direct export, factor substitution, sparse linear algebra, target descent, or full rho accounting.",
        ],
        "method": "order9887_column_conditioned_leaf_signature_delta",
        "parameters": {
            "off_family": list(OFF_FAMILY),
            "off_family_scouts": [str(path) for path in parse_paths(args.off_family_scouts)],
            "out": str(args.out),
            "p555_source": str(args.p555_source),
            "positive_families": [list(item) for item in sorted(POSITIVE_FAMILIES)],
            "positive_scouts": [str(path) for path in parse_paths(args.positive_scouts)],
            "target": TARGET,
            "order": ORDER,
        },
        "schema": "ecdlp.low_term_total2_order9887_column_conditioned_leaf_signature_delta.v1",
        "summary": {
            **summarize(cases),
            "error_count": len(positive_errors) + len(off_errors),
            "matched_row_pair_delta_count": len(matched_row_pair_deltas(cases)),
            "recommendation_count": len(recs),
        },
        "feature_deltas": feature_deltas(cases),
        "matched_row_pair_deltas": matched_row_pair_deltas(cases),
        "recommendations": recs,
        "cases": cases,
        "errors": (positive_errors + off_errors)[:80],
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
