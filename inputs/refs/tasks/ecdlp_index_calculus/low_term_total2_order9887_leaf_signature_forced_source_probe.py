#!/usr/bin/env python3
"""Emit a source artifact that forces P556 public selected-leaf signatures.

This probe does not assert that the forced rows verify.  It only creates a
source artifact compatible with the existing shared-product gate and priority
scout so those tools can recompute direct/shared verification from the forced
row_leaf_keys.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_DELTA = STATE_DIR / "low_term_total2_order9887_p556_column_conditioned_leaf_signature_delta_20224_20554_probe.json"
DEFAULT_P555_SOURCE = STATE_DIR / "low_term_total2_order9887_p555_pinned_family_source_20544_20554_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_p557_leaf_signature_forced_source_20544_20554_probe.json"


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


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def leaf_signature_values(raw: str) -> list[int]:
    return [int(part) for part in str(raw).split(",") if part.strip()]


def desired_family_key(values: list[Any]) -> str:
    return ",".join(str(int_value(value)) for value in values)


def load_lanes(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lanes: dict[str, dict[str, Any]] = {}
    for policy in (source.get("policies") or {}).values():
        lane = policy.get("lane")
        if isinstance(lane, dict) and lane.get("lane_id"):
            lanes[str(lane["lane_id"])] = lane
    return lanes


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_lane: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_signature = Counter()
    by_top_k = Counter()
    for row in rows:
        by_lane[str(row.get("lane_id"))].append(row)
        by_signature[str(row.get("forced_leaf_signature_key"))] += 1
        by_top_k[int_value(row.get("top_k"))] += 1
    return {
        "case_count": len(rows),
        "forced_leaf_signature_counts": {key: int(value) for key, value in sorted(by_signature.items())},
        "lane_counts": {key: len(value) for key, value in sorted(by_lane.items())},
        "top_k_counts": {str(key): int(value) for key, value in sorted(by_top_k.items())},
    }


def make_row(
    lane: dict[str, Any],
    recommendation: dict[str, Any],
    selector: str,
    top_k: int,
    signature_key: str,
) -> dict[str, Any]:
    base_case = dict_value(lane.get("base_case"))
    row_keys = [str(item) for item in list_value(recommendation.get("pin_row_keys"))]
    signature = leaf_signature_values(signature_key)
    if len(signature) == 1 and len(row_keys) > 1:
        signature = signature * len(row_keys)
    if len(signature) != len(row_keys):
        raise ValueError(
            f"signature {signature_key!r} does not match row key count {len(row_keys)} "
            f"for lane {lane.get('lane_id')}"
        )
    row_leaf_keys = [
        {"leaf_indices": [int(index)], "row_key": row_key}
        for row_key, index in zip(sorted(row_keys), signature)
    ]
    desired = list_value(recommendation.get("desired_family"))
    transfer_index = int_value(base_case.get("transfer_index"))
    target = str(base_case.get("target"))
    return {
        "below_rho": False,
        "desired_family": desired,
        "desired_family_key": desired_family_key(desired),
        "errors": [],
        "force_evidence_scope": recommendation.get("evidence_scope"),
        "forced_leaf_signature": signature,
        "forced_leaf_signature_key": signature_key,
        "lane_id": lane.get("lane_id"),
        "ops_over_rho": None,
        "positive_supports": recommendation.get("positive_supports") or [],
        "positive_transfers": recommendation.get("positive_transfers") or [],
        "public_key_verified": False,
        "rank": 0,
        "relation_count": 0,
        "row_keys": row_keys,
        "row_leaf_keys": row_leaf_keys,
        "row_selector": f"{lane.get('lane_id')}_leaf_signature_forced",
        "row_selector_public_key_verified": None,
        "selected_leaf_count": len(signature),
        "selected_row_count": len(row_keys),
        "selector": selector,
        "source_verified": True,
        "target": target,
        "top_k": int(top_k),
        "transfer_index": transfer_index,
    }


def build_policies(delta: dict[str, Any], p555_source: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    lanes = load_lanes(p555_source)
    policies: dict[str, dict[str, Any]] = {}
    all_rows: list[dict[str, Any]] = []
    for recommendation in list_value(delta.get("recommendations")):
        lane_id = str(recommendation.get("lane_id"))
        lane = lanes.get(lane_id)
        if lane is None:
            continue
        rows: list[dict[str, Any]] = []
        for signature_key in list_value(recommendation.get("force_leaf_signatures")):
            for selector in list_value(recommendation.get("force_selectors")):
                for top_k in list_value(recommendation.get("force_top_ks")):
                    rows.append(make_row(lane, recommendation, str(selector), int_value(top_k), str(signature_key)))
        policy_name = f"{lane_id}_leaf_signature_forced"
        policies[policy_name] = {
            "delta_recommendation": recommendation,
            "lane": lane,
            "row_selector": {
                "selector": policy_name,
                "spec": {
                    "avoid_leaf_signatures_seen_in_p555": recommendation.get("avoid_leaf_signatures_seen_in_p555") or [],
                    "desired_family": recommendation.get("desired_family") or [],
                    "force_leaf_signatures": recommendation.get("force_leaf_signatures") or [],
                    "force_top_ks": recommendation.get("force_top_ks") or [],
                    "pin_row_keys": recommendation.get("pin_row_keys") or [],
                },
            },
            "stress_leaf_results": rows,
            "stress_leaf_summary": summarize_rows(rows),
        }
        all_rows.extend(rows)
    return policies, all_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delta", type=Path, default=DEFAULT_DELTA)
    parser.add_argument("--p555-source", type=Path, default=DEFAULT_P555_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    delta = load_json(args.delta)
    p555_source = load_json(args.p555_source)
    policies, rows = build_policies(delta, p555_source)
    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: source rows target 67.a1@9803/order 9887 only.",
            "MODEL-BOUND: forced rows use the current low-term total-2 selected-leaf replay harness.",
            "HEURISTIC: forcing public leaf indices is a source-generation hypothesis, not a relation certificate.",
            "NO SPEEDUP CLAIM: downstream gate/scout/export/substitution/sparse-LA/target-descent/rho accounting remain required.",
        ],
        "method": "order9887_leaf_signature_forced_source_generation",
        "parameters": {
            **dict_value(p555_source.get("parameters")),
            "delta": str(args.delta),
            "out": str(args.out),
            "p555_source": str(args.p555_source),
        },
        "policies": policies,
        "schema": "ecdlp.low_term_total2_order9887_leaf_signature_forced_source_probe.v1",
        "summary": {
            **summarize_rows(rows),
            "lane_count": len(policies),
            "recommendation_count": len(list_value(delta.get("recommendations"))),
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
