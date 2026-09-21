#!/usr/bin/env python3
"""Validate frozen public phase-route predictors for order-9887 leaf-16 cases.

P565 found a post-hoc high-hit/root-saved bucket. P566 falsified that exact
bucket but exposed stronger raw direct leaf-16 families. This script freezes a
small public-feature rule family from P564/P566 and applies it to a disjoint
validation gate artifact. It uses verifier outcomes only for scoring.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P564_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p564_order9887_leaf16_heldout_20592_20604_density_gate_probe.json"
)
DEFAULT_P566_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p566_order9887_leaf16_frozen_root_saved_20605_20616_density_gate_probe.json"
)
DEFAULT_VALIDATION_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p567_order9887_phase_route_20617_20628_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p567_phase_route_predictor_validation_20617_20628_probe.json"


Feature = dict[str, Any]
Predicate = Callable[[Feature], bool]


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


def case_entry(case: Feature) -> str:
    return (
        f"{case.get('target')}|{int_value(case.get('transfer_index'))}|"
        f"{case.get('selector')}|{int_value(case.get('top_k'))}"
    )


def parse_right_anchor(selector: str) -> int | None:
    match = re.search(r"_ra(\d+)_", selector)
    return int(match.group(1)) if match else None


def parse_salt(row_key: str) -> int | None:
    match = re.search(r"salt(\d+)", row_key)
    return int(match.group(1)) if match else None


def base_selector(selector: str) -> str:
    return selector.split("__", 1)[0]


def feature_case(case: dict[str, Any], source_name: str) -> Feature:
    selector = str(case.get("selector"))
    transfer = int_value(case.get("transfer_index"))
    metrics = case.get("gate_metrics") if isinstance(case.get("gate_metrics"), dict) else {}
    row_keys = [str(row_key) for row_key in case.get("row_keys") or []]
    salts = [salt for salt in (parse_salt(row_key) for row_key in row_keys) if salt is not None]
    direct_verified = bool(case.get("direct_union_public_key_verified"))
    direct_below = bool(case.get("direct_below_rho"))
    return {
        "base_selector": base_selector(selector),
        "case_entry": case_entry(case),
        "direct_below_rho": direct_below,
        "direct_below_rho_verified": bool(direct_verified and direct_below),
        "direct_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
        "direct_verified": direct_verified,
        "duplicate_saved": int_value(metrics.get("duplicate_selected_leaf_check_saved_ops")),
        "hit_root_ops": int_value(metrics.get("direct_selected_hit_root_ops")),
        "phase_mod12": transfer % 12,
        "rank": int_value(case.get("direct_union_rank")),
        "relation_count": int_value(case.get("direct_union_relation_count")),
        "right_anchor": parse_right_anchor(selector),
        "row_keys": row_keys,
        "row_pair": "+".join(f"salt{salt}" for salt in salts),
        "salt_left": salts[0] if len(salts) >= 1 else None,
        "salt_right": salts[1] if len(salts) >= 2 else None,
        "selector": selector,
        "shared_root_saved": int_value(metrics.get("shared_signature_root_saved_ops")),
        "source_name": source_name,
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": transfer,
    }


def load_features(path: Path, source_name: str) -> list[Feature]:
    gate = load_json(path)
    return [
        feature_case(case, source_name)
        for case in gate.get("cases") or []
        if isinstance(case, dict)
    ]


def phase_anchor9_root_saved_hit2(row: Feature) -> bool:
    return (
        row["phase_mod12"] in {1, 6}
        and row["right_anchor"] == 9
        and row["hit_root_ops"] >= 2
        and row["shared_root_saved"] >= 1
        and row["duplicate_saved"] >= 1
    )


def phase6_right207_anyselector_hit1(row: Feature) -> bool:
    return row["phase_mod12"] == 6 and row["salt_right"] == 207 and row["hit_root_ops"] >= 1


def phase6_right207_cost_hybrid_hit1(row: Feature) -> bool:
    return (
        row["phase_mod12"] == 6
        and row["salt_right"] == 207
        and row["base_selector"] == "mode_cost_hybrid_support_monic_b_total2"
        and row["hit_root_ops"] >= 1
    )


def phase_route_union_v1(row: Feature) -> bool:
    return phase_anchor9_root_saved_hit2(row) or phase6_right207_anyselector_hit1(row)


def hit_positive_control(row: Feature) -> bool:
    return row["hit_root_ops"] >= 1


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "phase_route_union_v1",
            "phase anchor-9 root-saved route OR phase-6 right-salt-207 hit route",
            phase_route_union_v1,
        ),
        (
            "phase_anchor9_root_saved_hit2",
            "transfer mod 12 in {1,6}, right_anchor=9, hit>=2, shared_saved>=1, duplicate_saved>=1",
            phase_anchor9_root_saved_hit2,
        ),
        (
            "phase6_right207_anyselector_hit1",
            "transfer mod 12=6, right row salt=207, hit>=1",
            phase6_right207_anyselector_hit1,
        ),
        (
            "phase6_right207_cost_hybrid_hit1",
            "transfer mod 12=6, right row salt=207, cost_hybrid selector, hit>=1",
            phase6_right207_cost_hybrid_hit1,
        ),
        (
            "hit_positive_control",
            "hit>=1 public-metric load control",
            hit_positive_control,
        ),
    ]


def compact_case(row: Feature) -> dict[str, Any]:
    return {
        "base_selector": row["base_selector"],
        "case_entry": row["case_entry"],
        "direct_below_rho_verified": row["direct_below_rho_verified"],
        "direct_ops_over_rho": row["direct_ops_over_rho"],
        "direct_verified": row["direct_verified"],
        "duplicate_saved": row["duplicate_saved"],
        "hit_root_ops": row["hit_root_ops"],
        "phase_mod12": row["phase_mod12"],
        "rank": row["rank"],
        "relation_count": row["relation_count"],
        "right_anchor": row["right_anchor"],
        "row_pair": row["row_pair"],
        "selector": row["selector"],
        "shared_root_saved": row["shared_root_saved"],
        "source_name": row["source_name"],
        "target": row["target"],
        "top_k": row["top_k"],
        "transfer_index": row["transfer_index"],
    }


def summarize_rule(rows: list[Feature], name: str, description: str, predicate: Predicate) -> dict[str, Any]:
    selected = [row for row in rows if predicate(row)]
    verified = [row for row in selected if row["direct_verified"]]
    below_verified = [row for row in selected if row["direct_below_rho_verified"]]
    best_below = sorted(
        below_verified,
        key=lambda row: (
            float_value(row.get("direct_ops_over_rho"), 10**18),
            int_value(row.get("transfer_index")),
            str(row.get("selector")),
        ),
    )
    return {
        "description": description,
        "direct_below_rho_verified_count": len(below_verified),
        "direct_below_rho_verified_precision": ratio(len(below_verified), len(selected)),
        "direct_verified_count": len(verified),
        "direct_verified_precision": ratio(len(verified), len(selected)),
        "examples": [compact_case(row) for row in best_below[:12]],
        "phase_counts": dict(sorted(Counter(str(row["phase_mod12"]) for row in selected).items(), key=lambda item: int(item[0]))),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected).most_common(16)),
        "rule": name,
        "selected_case_entries": [row["case_entry"] for row in selected],
        "selected_count": len(selected),
        "selected_direct_below_rho_verified_case_entries": [row["case_entry"] for row in below_verified],
        "selected_fraction": ratio(len(selected), len(rows)),
        "source_counts": dict(sorted(Counter(str(row["source_name"]) for row in selected).items())),
        "transfer_counts": dict(sorted(Counter(str(row["transfer_index"]) for row in selected).items(), key=lambda item: int(item[0]))),
    }


def dataset_summary(rows: list[Feature]) -> dict[str, Any]:
    return {
        "case_count": len(rows),
        "direct_below_rho_verified_count": sum(1 for row in rows if row["direct_below_rho_verified"]),
        "direct_verified_count": sum(1 for row in rows if row["direct_verified"]),
        "phase_counts": dict(sorted(Counter(str(row["phase_mod12"]) for row in rows).items(), key=lambda item: int(item[0]))),
        "source_counts": dict(sorted(Counter(str(row["source_name"]) for row in rows).items())),
    }


def evaluate(rows: list[Feature]) -> list[dict[str, Any]]:
    reports = [summarize_rule(rows, name, description, predicate) for name, description, predicate in rule_specs()]
    reports.sort(key=lambda report: (0 if report["rule"] == "phase_route_union_v1" else 1, str(report["rule"])))
    return reports


def main_rule_report(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return next(report for report in reports if report["rule"] == "phase_route_union_v1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p564-gate", type=Path, default=DEFAULT_P564_GATE)
    parser.add_argument("--p566-gate", type=Path, default=DEFAULT_P566_GATE)
    parser.add_argument("--validation-gate", type=Path, default=DEFAULT_VALIDATION_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    training_rows = load_features(args.p564_gate, "p564_train") + load_features(args.p566_gate, "p566_train")
    validation_rows = load_features(args.validation_gate, "p567_validation")
    training_reports = evaluate(training_rows)
    validation_reports = evaluate(validation_rows)
    main_train = main_rule_report(training_reports)
    main_validation = main_rule_report(validation_reports)
    payload = {
        "artifacts": {
            "p564_gate": str(args.p564_gate),
            "p566_gate": str(args.p566_gate),
            "validation_gate": str(args.validation_gate),
        },
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "FROZEN RULE: rule definitions are in this script before validation scoring.",
            "PUBLIC-FEATURE BOUNDARY: selection uses transfer index, public row salts, anchor, selector name, and public gate metrics only.",
            "POST-GATE ROUTE: direct selected-leaf hit metrics are public but not yet a cheap source-generation oracle.",
            "NO SPEEDUP CLAIM: this validates route selection, not a complete index-calculus algorithm or deployed-curve break.",
        ],
        "method": "p567_phase_route_predictor_validation",
        "schema": "ecdlp.low_term_total2_p567_phase_route_predictor_validation.v1",
        "summary": {
            "claim_status": (
                "FROZEN_PHASE_ROUTE_VALIDATION_POSITIVE"
                if main_validation["direct_below_rho_verified_count"]
                else "NEGATIVE_RESULT_FROZEN_PHASE_ROUTE_NO_BELOW_RHO_VERIFIED"
            ),
            "main_rule": "phase_route_union_v1",
            "training": {
                "dataset": dataset_summary(training_rows),
                "main_rule": {
                    key: main_train[key]
                    for key in [
                        "selected_count",
                        "direct_verified_count",
                        "direct_below_rho_verified_count",
                        "direct_below_rho_verified_precision",
                        "selected_fraction",
                    ]
                },
            },
            "validation": {
                "dataset": dataset_summary(validation_rows),
                "main_rule": {
                    key: main_validation[key]
                    for key in [
                        "selected_count",
                        "direct_verified_count",
                        "direct_below_rho_verified_count",
                        "direct_below_rho_verified_precision",
                        "selected_fraction",
                    ]
                },
            },
        },
        "training_rule_reports": training_reports,
        "validation_rule_reports": validation_reports,
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
