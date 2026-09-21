#!/usr/bin/env python3
"""Emit P560 second-stage extra-leaf pressure rows around the P559 07_06 channel."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P555_SOURCE = STATE_DIR / "low_term_total2_order9887_p555_pinned_family_source_20544_20554_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_p560_anchor0706_extra_leaf_pressure_source_20544_probe.json"
DEFAULT_SELECTORS = "mode_cost_low_term_support_total2,mode_double_pair_first_total2,mode_low_term_support_total2"
DEFAULT_TOP_KS = "4,7,12,16"
DEFAULT_EXTRA_LEAF_INDICES = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"
DEFAULT_CROSS_EXTRA_INDICES = "3,9,12,13"


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


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in str(raw).split(",") if item.strip()]


def parse_int_csv(raw: str) -> list[int]:
    return [int(item) for item in parse_csv(raw)]


def unique_sorted(values: list[int]) -> list[int]:
    return sorted({int(value) for value in values})


def desired_family_key(values: list[Any]) -> str:
    return ",".join(str(int_value(value)) for value in values)


def load_lane(source: dict[str, Any], lane_id: str) -> dict[str, Any]:
    for policy in (source.get("policies") or {}).values():
        lane = policy.get("lane") if isinstance(policy, dict) else None
        if isinstance(lane, dict) and str(lane.get("lane_id")) == lane_id:
            return lane
    raise ValueError(f"lane_id {lane_id!r} not found")


def mutation_key(kind: str, left: list[int], right: list[int]) -> str:
    left_key = "-".join(f"{value:02d}" for value in left)
    right_key = "-".join(f"{value:02d}" for value in right)
    return f"{kind}_L{left_key}_R{right_key}"


def forced_selector(base_selector: str, key: str) -> str:
    return f"{base_selector}__p560_{key}"


def build_mutations(
    anchor_left: int,
    anchor_right: int,
    extra_indices: list[int],
    cross_extra_indices: list[int],
) -> list[dict[str, Any]]:
    mutations: list[dict[str, Any]] = []

    def add(kind: str, left_values: list[int], right_values: list[int]) -> None:
        left = unique_sorted(left_values)
        right = unique_sorted(right_values)
        mutations.append(
            {
                "kind": kind,
                "left_leaf_indices": left,
                "mutation_key": mutation_key(kind, left, right),
                "right_leaf_indices": right,
            }
        )

    add("anchor_control", [anchor_left], [anchor_right])
    for extra in extra_indices:
        if extra != anchor_left:
            add("left_extra", [anchor_left, extra], [anchor_right])
        if extra != anchor_right:
            add("right_extra", [anchor_left], [anchor_right, extra])
        add("shared_extra", [anchor_left, extra], [anchor_right, extra])
    for left_extra in cross_extra_indices:
        for right_extra in cross_extra_indices:
            add("cross_extra", [anchor_left, left_extra], [anchor_right, right_extra])

    seen: set[tuple[str, tuple[int, ...], tuple[int, ...]]] = set()
    out: list[dict[str, Any]] = []
    for mutation in mutations:
        key = (
            str(mutation["kind"]),
            tuple(int(value) for value in mutation["left_leaf_indices"]),
            tuple(int(value) for value in mutation["right_leaf_indices"]),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(mutation)
    out.sort(key=lambda item: (str(item["kind"]), str(item["mutation_key"])))
    return out


def make_row(
    lane: dict[str, Any],
    base_selector: str,
    top_k: int,
    mutation: dict[str, Any],
) -> dict[str, Any]:
    base_case = dict_value(lane.get("base_case"))
    spec = dict_value(lane.get("source_policy_mutation"))
    row_keys = sorted(str(item) for item in list_value(spec.get("pin_row_keys")))
    if len(row_keys) != 2:
        raise ValueError(f"expected two pinned row keys for {lane.get('lane_id')}")
    desired = list_value(lane.get("desired_family"))
    left_indices = [int_value(value) for value in list_value(mutation.get("left_leaf_indices"))]
    right_indices = [int_value(value) for value in list_value(mutation.get("right_leaf_indices"))]
    row_leaf_keys = [
        {"leaf_indices": left_indices, "row_key": row_keys[0]},
        {"leaf_indices": right_indices, "row_key": row_keys[1]},
    ]
    selected_leaf_count = len(set(left_indices)) + len(set(right_indices))
    selector = forced_selector(base_selector, str(mutation["mutation_key"]))
    return {
        "base_selector": base_selector,
        "below_rho": False,
        "desired_family": desired,
        "desired_family_key": desired_family_key(desired),
        "errors": [],
        "left_leaf_indices": left_indices,
        "lane_id": lane.get("lane_id"),
        "mutation_kind": mutation.get("kind"),
        "mutation_key": mutation.get("mutation_key"),
        "ops_over_rho": None,
        "public_key_verified": False,
        "rank": 0,
        "relation_count": 0,
        "right_leaf_indices": right_indices,
        "row_keys": row_keys,
        "row_leaf_keys": row_leaf_keys,
        "row_selector": f"{lane.get('lane_id')}_p560_anchor0706_extra_leaf_pressure",
        "row_selector_public_key_verified": None,
        "selected_leaf_count": selected_leaf_count,
        "selected_row_count": 2,
        "selector": selector,
        "source_verified": True,
        "target": base_case.get("target"),
        "top_k": int(top_k),
        "transfer_index": int_value(base_case.get("transfer_index")),
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_kind = Counter(str(row.get("mutation_kind")) for row in rows)
    by_selected_leaf_count = Counter(str(row.get("selected_leaf_count")) for row in rows)
    by_selector = Counter(str(row.get("base_selector")) for row in rows)
    by_top_k = Counter(str(row.get("top_k")) for row in rows)
    mutation_keys = {str(row.get("mutation_key")) for row in rows}
    return {
        "base_selector_counts": dict(sorted(by_selector.items())),
        "case_count": len(rows),
        "mutation_count": len(mutation_keys),
        "mutation_kind_counts": dict(sorted(by_kind.items())),
        "selected_leaf_count_counts": dict(sorted(by_selected_leaf_count.items())),
        "top_k_counts": dict(sorted(by_top_k.items(), key=lambda item: int(item[0]))),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p555-source", type=Path, default=DEFAULT_P555_SOURCE)
    parser.add_argument("--lane-id", default="P554-L001")
    parser.add_argument("--anchor-left", type=int, default=7)
    parser.add_argument("--anchor-right", type=int, default=6)
    parser.add_argument("--extra-leaf-indices", default=DEFAULT_EXTRA_LEAF_INDICES)
    parser.add_argument("--cross-extra-indices", default=DEFAULT_CROSS_EXTRA_INDICES)
    parser.add_argument("--selectors", default=DEFAULT_SELECTORS)
    parser.add_argument("--top-ks", default=DEFAULT_TOP_KS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p555_source = load_json(args.p555_source)
    lane = load_lane(p555_source, args.lane_id)
    selectors = parse_csv(args.selectors)
    top_ks = parse_int_csv(args.top_ks)
    extra_indices = parse_int_csv(args.extra_leaf_indices)
    cross_extra_indices = parse_int_csv(args.cross_extra_indices)
    mutations = build_mutations(args.anchor_left, args.anchor_right, extra_indices, cross_extra_indices)
    rows = [
        make_row(lane, selector, top_k, mutation)
        for mutation in mutations
        for selector in selectors
        for top_k in top_ks
    ]
    policy_name = f"{lane.get('lane_id')}_p560_anchor0706_extra_leaf_pressure"
    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: source rows target 67.a1@9803/order 9887 only.",
            "MODEL-BOUND: second-stage rows are replayed through the current low-term total-2 harness.",
            "HEURISTIC: extra-leaf pressure is a source-policy diagnostic, not a complete target descent.",
            "NO SPEEDUP CLAIM: export, substitution, sparse-LA, target descent, and full rho accounting remain required.",
        ],
        "method": "order9887_p560_anchor0706_extra_leaf_pressure_source",
        "parameters": {
            **dict_value(p555_source.get("parameters")),
            "anchor_left": int(args.anchor_left),
            "anchor_right": int(args.anchor_right),
            "cross_extra_indices": cross_extra_indices,
            "extra_leaf_indices": extra_indices,
            "lane_id": args.lane_id,
            "out": str(args.out),
            "p555_source": str(args.p555_source),
            "selectors": selectors,
            "top_ks": top_ks,
        },
        "policies": {
            policy_name: {
                "lane": lane,
                "row_selector": {
                    "selector": policy_name,
                    "spec": {
                        "anchor_leaf_pair": [int(args.anchor_left), int(args.anchor_right)],
                        "cross_extra_indices": cross_extra_indices,
                        "desired_family": lane.get("desired_family"),
                        "extra_leaf_indices": extra_indices,
                        "pin_row_keys": dict_value(lane.get("source_policy_mutation")).get("pin_row_keys"),
                        "selectors": selectors,
                        "top_ks": top_ks,
                    },
                },
                "stress_leaf_results": rows,
                "stress_leaf_summary": summarize_rows(rows),
            }
        },
        "schema": "ecdlp.low_term_total2_order9887_p560_anchor0706_extra_leaf_pressure_source_probe.v1",
        "summary": {
            **summarize_rows(rows),
            "anchor_leaf_pair": [int(args.anchor_left), int(args.anchor_right)],
            "cross_extra_index_count": len(cross_extra_indices),
            "extra_leaf_index_count": len(extra_indices),
            "lane_count": 1,
            "selector_count": len(selectors),
            "top_k_count": len(top_ks),
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
