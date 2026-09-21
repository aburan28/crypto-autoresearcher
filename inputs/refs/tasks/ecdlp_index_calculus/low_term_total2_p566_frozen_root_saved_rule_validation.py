#!/usr/bin/env python3
"""Validate the frozen P565 high-hit/root-saved public rule on a gate artifact."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p566_order9887_leaf16_frozen_root_saved_20605_20616_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p566_frozen_root_saved_rule_validation_20605_20616_probe.json"


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


def p565_rule(case: dict[str, Any]) -> bool:
    metrics = case.get("gate_metrics") if isinstance(case.get("gate_metrics"), dict) else {}
    return (
        int_value(metrics.get("direct_selected_hit_root_ops")) >= 4
        and int_value(metrics.get("shared_signature_root_saved_ops")) >= 1
        and int_value(metrics.get("duplicate_selected_leaf_check_saved_ops")) >= 1
    )


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    metrics = case.get("gate_metrics") if isinstance(case.get("gate_metrics"), dict) else {}
    return {
        "case_entry": (
            f"{case.get('target')}|{int_value(case.get('transfer_index'))}|"
            f"{case.get('selector')}|{int_value(case.get('top_k'))}"
        ),
        "direct_below_rho": bool(case.get("direct_below_rho")),
        "direct_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
        "direct_union_public_key_verified": bool(case.get("direct_union_public_key_verified")),
        "duplicate_saved": int_value(metrics.get("duplicate_selected_leaf_check_saved_ops")),
        "hit_root_ops": int_value(metrics.get("direct_selected_hit_root_ops")),
        "rank": int_value(case.get("direct_union_rank")),
        "relation_count": int_value(case.get("direct_union_relation_count")),
        "row_keys": case.get("row_keys") or [],
        "selector": case.get("selector"),
        "shared_root_saved": int_value(metrics.get("shared_signature_root_saved_ops")),
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
    }


def summarize(cases: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    selected_verified = [case for case in selected if case.get("direct_union_public_key_verified")]
    selected_below_verified = [
        case
        for case in selected
        if case.get("direct_union_public_key_verified") and case.get("direct_below_rho")
    ]
    transfer_counts = Counter(str(case.get("transfer_index")) for case in selected)
    selector_counts = Counter(str(case.get("selector")).split("__", 1)[0] for case in selected)
    return {
        "case_count": len(cases),
        "claim_status": (
            "FROZEN_PUBLIC_ROOT_SAVED_RULE_VALIDATION_POSITIVE"
            if selected_below_verified
            else "NEGATIVE_RESULT_FROZEN_PUBLIC_ROOT_SAVED_RULE_NO_BELOW_RHO_VERIFIED"
        ),
        "direct_below_rho_verified_precision": ratio(len(selected_below_verified), len(selected)),
        "direct_verified_precision": ratio(len(selected_verified), len(selected)),
        "selected_count": len(selected),
        "selected_direct_below_rho_verified_count": len(selected_below_verified),
        "selected_direct_verified_count": len(selected_verified),
        "selector_counts": dict(sorted(selector_counts.items())),
        "transfer_counts": dict(sorted(transfer_counts.items(), key=lambda item: int(item[0]))),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gate = load_json(args.gate)
    cases = [case for case in gate.get("cases") or [] if isinstance(case, dict)]
    selected = [case for case in cases if p565_rule(case)]
    selected_below = [
        case
        for case in selected
        if case.get("direct_union_public_key_verified") and case.get("direct_below_rho")
    ]
    payload = {
        "artifacts": {"gate": str(args.gate)},
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 held-out validation block only.",
            "FROZEN RULE: selection uses the P565 public metric rule exactly.",
            "NO SUPPORT LABEL IN SELECTION: relation support and verifier outcome are used only for evaluation/export.",
            "NO SPEEDUP CLAIM: this validates a selector bucket, not a full index-calculus algorithm.",
        ],
        "method": "p566_frozen_root_saved_rule_validation",
        "rule": {
            "name": "root_saved_high_hit_candidate_7_13",
            "predicate": "direct_selected_hit_root_ops >= 4 and shared_signature_root_saved_ops >= 1 and duplicate_selected_leaf_check_saved_ops >= 1",
        },
        "schema": "ecdlp.low_term_total2_p566_frozen_root_saved_rule_validation.v1",
        "selected_below_rho_verified_case_entries": [compact_case(case)["case_entry"] for case in selected_below],
        "selected_cases": [compact_case(case) for case in selected[:200]],
        "summary": summarize(cases, selected),
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
