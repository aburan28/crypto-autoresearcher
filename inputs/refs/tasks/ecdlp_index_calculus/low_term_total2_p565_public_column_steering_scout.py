#!/usr/bin/env python3
"""Scout public features that separate P563/P564 leaf-16 support families.

The script is deliberately offline: it consumes existing replay artifacts, keeps
support labels separate from public gate/source features, and reports only
bounded steering hypotheses for the next held-out experiment.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P563_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p563_order9887_public_leaf16_repair_selector_20597_density_gate_probe.json"
)
DEFAULT_P563_PRIORITY = (
    STATE_DIR
    / "low_term_total2_priority_column_form_scout_p563_order9887_public_leaf16_repair_selector_20597_9887_1_6_12_13_probe.json"
)
DEFAULT_P564_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p564_order9887_leaf16_heldout_20592_20604_density_gate_probe.json"
)
DEFAULT_P564_CERTS = (
    STATE_DIR
    / "low_term_total2_direct_relation_equation_certificate_67_order9887_p564_leaf16_heldout_20592_20604_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p565_public_column_steering_scout_probe.json"


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


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


def case_key(target: str, transfer_index: int, selector: str, top_k: int) -> str:
    return f"{target}|{int(transfer_index)}|{selector}|{int(top_k)}"


def support_key(values: list[int]) -> str:
    return ",".join(str(value) for value in sorted({int_value(value) for value in values}))


def form_support(form: dict[str, Any], order: int) -> list[int]:
    coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
    return [idx for idx, value in enumerate(coeffs[1:]) if value % order]


def p563_support_labels(priority: dict[str, Any]) -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    for report in priority.get("case_reports") or []:
        if not isinstance(report, dict):
            continue
        target = str(report.get("target"))
        transfer = int_value(report.get("transfer_index"))
        selector = str(report.get("selector"))
        top_k = int_value(report.get("top_k"))
        support = [int_value(value) for value in report.get("coeff_support") or []]
        labels[case_key(target, transfer, selector, top_k)] = {
            "label_source": "p563_priority_replay",
            "order": int_value(report.get("order"), 9887),
            "rank": int_value(report.get("rank_replay")),
            "support": support,
            "support_key": support_key(support),
            "verified_label": bool(report.get("public_key_verified_replay")),
        }
    return labels


def cert_support_labels(certs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    for cert in certs.get("certificates") or []:
        if not isinstance(cert, dict):
            continue
        selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
        target = str(selected.get("target"))
        transfer = int_value(selected.get("transfer_index"))
        selector = str(selected.get("selector"))
        top_k = int_value(selected.get("top_k"))
        order = int_value(cert.get("order"), 9887)
        supports = []
        for form in cert.get("forms") or []:
            if isinstance(form, dict):
                supports.extend(form_support(form, order))
        support = sorted(set(supports))
        labels[case_key(target, transfer, selector, top_k)] = {
            "label_source": "direct_certificate",
            "order": order,
            "rank": int_value(cert.get("rank")),
            "support": support,
            "support_key": support_key(support),
            "verified_label": bool(cert.get("public_key_verified")),
        }
    return labels


def parse_salt(row_key: str) -> int | None:
    match = re.search(r"salt(\d+)", row_key)
    return int(match.group(1)) if match else None


def parse_right_anchor(selector: str) -> int | None:
    match = re.search(r"_ra(\d+)_", selector)
    return int(match.group(1)) if match else None


def base_selector(selector: str) -> str:
    return selector.split("__", 1)[0]


def row_features(case: dict[str, Any], source_name: str, labels: dict[str, dict[str, Any]]) -> dict[str, Any]:
    target = str(case.get("target"))
    transfer = int_value(case.get("transfer_index"))
    selector = str(case.get("selector"))
    top_k = int_value(case.get("top_k"))
    key = case_key(target, transfer, selector, top_k)
    row_keys = [str(row_key) for row_key in case.get("row_keys") or []]
    salts = [salt for salt in (parse_salt(row_key) for row_key in row_keys) if salt is not None]
    metrics = case.get("gate_metrics") if isinstance(case.get("gate_metrics"), dict) else {}
    label = labels.get(key, {})
    support = [int_value(value) for value in label.get("support") or []]
    out = {
        "base_selector": base_selector(selector),
        "direct_below_rho": bool(case.get("direct_below_rho")),
        "direct_below_rho_verified": bool(
            case.get("direct_below_rho") and case.get("direct_union_public_key_verified")
        ),
        "direct_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
        "direct_verified": bool(case.get("direct_union_public_key_verified")),
        "duplicate_saved": int_value(metrics.get("duplicate_selected_leaf_check_saved_ops")),
        "duplicate_signature_density": float_value(metrics.get("duplicate_signature_density")),
        "hit_root_ops": int_value(metrics.get("direct_selected_hit_root_ops")),
        "labeled_support": bool(label),
        "label_source": label.get("label_source"),
        "right_anchor": parse_right_anchor(selector),
        "row_pair": "+".join(f"salt{salt}" for salt in salts),
        "salt_delta": (max(salts) - min(salts)) if len(salts) == 2 else None,
        "salt_left": salts[0] if len(salts) >= 1 else None,
        "salt_right": salts[1] if len(salts) >= 2 else None,
        "selector": selector,
        "shared_root_saved": int_value(metrics.get("shared_signature_root_saved_ops")),
        "source_name": source_name,
        "support": support,
        "support_has_6_13": 6 in support and 13 in support,
        "support_has_7_13": 7 in support and 13 in support,
        "support_key": label.get("support_key"),
        "target": target,
        "top_k": top_k,
        "transfer_index": transfer,
        "unique_signature_fraction": float_value(metrics.get("unique_signature_fraction")),
        "unique_signature_count": int_value(metrics.get("unique_selected_leaf_signature_count")),
    }
    out["public_metric_bucket"] = (
        f"hit={out['hit_root_ops']};saved={out['shared_root_saved']};"
        f"dup={out['duplicate_saved']};anchor={out['right_anchor']}"
    )
    return out


def load_dataset(p563_gate: dict[str, Any], p564_gate: dict[str, Any], labels: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for source_name, gate in [("p563_calibration", p563_gate), ("p564_heldout", p564_gate)]:
        for case in gate.get("cases") or []:
            if isinstance(case, dict):
                rows.append(row_features(case, source_name, labels))
    return rows


RulePredicate = Callable[[dict[str, Any]], bool]


def rule_specs() -> list[tuple[str, str, RulePredicate]]:
    return [
        (
            "root_saved_high_hit_candidate_7_13",
            "hit_root_ops >= 4 and shared_root_saved >= 1 and duplicate_saved >= 1",
            lambda row: row["hit_root_ops"] >= 4
            and row["shared_root_saved"] >= 1
            and row["duplicate_saved"] >= 1,
        ),
        (
            "low_hit_no_root_saved_candidate_6_13_labeled",
            "hit_root_ops == 2 and shared_root_saved == 0",
            lambda row: row["hit_root_ops"] == 2 and row["shared_root_saved"] == 0,
        ),
        (
            "above_rho_anchor13_control_shape",
            "right_anchor == 13 and hit_root_ops >= 3 and shared_root_saved == 0",
            lambda row: row["right_anchor"] == 13
            and row["hit_root_ops"] >= 3
            and row["shared_root_saved"] == 0,
        ),
        (
            "duplicate_leaf_anchor9_shape",
            "right_anchor == 9 and duplicate_saved >= 1",
            lambda row: row["right_anchor"] == 9 and row["duplicate_saved"] >= 1,
        ),
        (
            "any_public_hit_root",
            "hit_root_ops >= 1",
            lambda row: row["hit_root_ops"] >= 1,
        ),
    ]


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "direct_below_rho_verified": row["direct_below_rho_verified"],
        "direct_ops_over_rho": row["direct_ops_over_rho"],
        "direct_verified": row["direct_verified"],
        "hit_root_ops": row["hit_root_ops"],
        "right_anchor": row["right_anchor"],
        "row_pair": row["row_pair"],
        "selector": row["selector"],
        "shared_root_saved": row["shared_root_saved"],
        "source_name": row["source_name"],
        "support_key": row["support_key"],
        "transfer_index": row["transfer_index"],
    }


def summarize_selection(selected: list[dict[str, Any]], all_rows: list[dict[str, Any]]) -> dict[str, Any]:
    labeled = [row for row in selected if row["labeled_support"]]
    support_counts = Counter(str(row["support_key"]) for row in labeled)
    source_counts = Counter(str(row["source_name"]) for row in selected)
    selected_count = len(selected)
    direct_verified = sum(1 for row in selected if row["direct_verified"])
    below_verified = sum(1 for row in selected if row["direct_below_rho_verified"])
    support_6_13 = sum(1 for row in labeled if row["support_has_6_13"])
    support_7_13 = sum(1 for row in labeled if row["support_has_7_13"])
    return {
        "selected_count": selected_count,
        "selected_fraction": ratio(selected_count, len(all_rows)),
        "source_counts": dict(sorted(source_counts.items())),
        "direct_verified_count": direct_verified,
        "direct_below_rho_verified_count": below_verified,
        "direct_verified_precision": ratio(direct_verified, selected_count),
        "direct_below_rho_verified_precision": ratio(below_verified, selected_count),
        "labeled_support_count": len(labeled),
        "support_6_13_count": support_6_13,
        "support_7_13_count": support_7_13,
        "support_6_13_labeled_precision": ratio(support_6_13, len(labeled)),
        "support_7_13_labeled_precision": ratio(support_7_13, len(labeled)),
        "support_counts": dict(sorted(support_counts.items())),
        "examples": [compact_row(row) for row in selected[:8]],
    }


def evaluate_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reports = []
    for name, description, predicate in rule_specs():
        selected = [row for row in rows if predicate(row)]
        reports.append({"rule": name, "description": description, **summarize_selection(selected, rows)})
    reports.sort(
        key=lambda report: (
            -int_value(report.get("direct_below_rho_verified_count")),
            -float_value(report.get("direct_below_rho_verified_precision")),
            -int_value(report.get("support_6_13_count")) - int_value(report.get("support_7_13_count")),
            str(report.get("rule")),
        )
    )
    return reports


def bucket_reports(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row["public_metric_bucket"])].append(row)
    reports = []
    for bucket, selected in buckets.items():
        reports.append({"bucket": bucket, **summarize_selection(selected, rows)})
    reports.sort(
        key=lambda report: (
            -int_value(report.get("direct_below_rho_verified_count")),
            -int_value(report.get("labeled_support_count")),
            str(report.get("bucket")),
        )
    )
    return reports


def dataset_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labeled = [row for row in rows if row["labeled_support"]]
    source_counts = Counter(str(row["source_name"]) for row in rows)
    support_counts = Counter(str(row["support_key"]) for row in labeled)
    return {
        "case_count": len(rows),
        "direct_verified_count": sum(1 for row in rows if row["direct_verified"]),
        "direct_below_rho_verified_count": sum(1 for row in rows if row["direct_below_rho_verified"]),
        "labeled_support_count": len(labeled),
        "source_counts": dict(sorted(source_counts.items())),
        "support_counts": dict(sorted(support_counts.items())),
        "support_6_13_count": sum(1 for row in labeled if row["support_has_6_13"]),
        "support_7_13_count": sum(1 for row in labeled if row["support_has_7_13"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p563-gate", type=Path, default=DEFAULT_P563_GATE)
    parser.add_argument("--p563-priority", type=Path, default=DEFAULT_P563_PRIORITY)
    parser.add_argument("--p564-gate", type=Path, default=DEFAULT_P564_GATE)
    parser.add_argument("--p564-certificates", type=Path, default=DEFAULT_P564_CERTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p563_gate = load_json(args.p563_gate)
    p563_priority = load_json(args.p563_priority)
    p564_gate = load_json(args.p564_gate)
    p564_certs = load_json(args.p564_certificates)
    labels = {}
    labels.update(p563_support_labels(p563_priority))
    labels.update(cert_support_labels(p564_certs))
    rows = load_dataset(p563_gate, p564_gate, labels)
    rules = evaluate_rules(rows)
    buckets = bucket_reports(rows)
    output = {
        "artifacts": {
            "p563_gate": str(args.p563_gate),
            "p563_priority": str(args.p563_priority),
            "p564_certificates": str(args.p564_certificates),
            "p564_gate": str(args.p564_gate),
        },
        "created_at": now_iso(),
        "dataset_summary": dataset_summary(rows),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local harness only.",
            "POST-HOC SCOUT: rules are derived after seeing P563/P564 outcomes and must be frozen before validation.",
            "PUBLIC-FEATURE BOUNDARY: candidate rules use source metadata and public gate metrics only; support labels are used only for scoring.",
            "NO SPEEDUP CLAIM: this is a column-steering diagnostic, not an end-to-end index-calculus algorithm.",
        ],
        "method": "p565_public_column_steering_scout",
        "metric_bucket_reports": buckets[:40],
        "rule_reports": rules,
        "schema": "ecdlp.low_term_total2_p565_public_column_steering_scout.v1",
        "summary": {
            "best_7_13_rule": next(
                (report for report in rules if report["rule"] == "root_saved_high_hit_candidate_7_13"),
                None,
            ),
            "claim_status": (
                "PUBLIC_COLUMN_STEERING_CANDIDATE_FOUND"
                if any(
                    report["rule"] == "root_saved_high_hit_candidate_7_13"
                    and int_value(report.get("direct_below_rho_verified_count")) > 0
                    and int_value(report.get("support_7_13_count")) > 0
                    for report in rules
                )
                else "NO_PUBLIC_COLUMN_STEERING_CANDIDATE_FOUND"
            ),
            "dataset": dataset_summary(rows),
            "interpretation": (
                "The high-hit/root-saved bucket isolates the held-out [1,7,13] "
                "positive cases in the current artifacts.  The [1,6,13] family "
                "is still only cleanly separated within labeled P563 rows; a "
                "fresh validation must freeze the rule before replay."
            ),
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
