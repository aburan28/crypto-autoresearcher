#!/usr/bin/env python3
"""Scan row-pair neighborhoods for order-9887 priority support.

This is a post-scout aggregation tool.  It consumes priority-column form scout
artifacts, keeps exact two-row target/order cases, and asks whether any anchor
or nearby salt pair touches requested priority columns.  It does not build new
relations, derive target secrets, or promote a speedup claim.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_rowpair_neighborhood_support_scanner_probe.json"
SALT_RE = re.compile(r"salt(\d+)")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def parse_paths(raw: str) -> list[Path]:
    paths: list[Path] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        matches = sorted(Path(path) for path in glob.glob(item))
        paths.extend(matches or [Path(item)])
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def parse_ints(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def parse_anchor_pairs(raw: str) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        values = parse_ints(chunk)
        if len(values) != 2:
            raise ValueError(f"anchor pair must have two salts: {chunk!r}")
        pairs.append(tuple(sorted(values)))
    return pairs


def salts_from_row_keys(row_keys: list[Any]) -> tuple[int, ...]:
    salts: list[int] = []
    for row_key in row_keys:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return tuple(sorted(salts))


def row_pair_key(row_keys: list[Any]) -> str:
    return " + ".join(sorted(str(item) for item in row_keys))


def pair_distance(pair: tuple[int, int], anchor: tuple[int, int]) -> dict[str, Any]:
    return {
        "anchor": list(anchor),
        "linf": max(abs(pair[0] - anchor[0]), abs(pair[1] - anchor[1])),
        "l1": abs(pair[0] - anchor[0]) + abs(pair[1] - anchor[1]),
    }


def closest_anchor(pair: tuple[int, int], anchors: list[tuple[int, int]]) -> dict[str, Any] | None:
    if not anchors:
        return None
    distances = [pair_distance(pair, anchor) for anchor in anchors]
    distances.sort(key=lambda item: (int_value(item["linf"]), int_value(item["l1"]), item["anchor"]))
    return distances[0]


def source_label(path: Path) -> str:
    name = path.name
    if "targetcap3_variant" in name:
        return "p548_targetcap3"
    if "p547_default" in name:
        return "p547_default_allgated"
    if "remaining_cols" in name:
        return "p547_default_verified_remaining_cols"
    return path.stem


def bool_verified(case: dict[str, Any]) -> bool:
    return bool(case.get("verified") is True or case.get("public_key_verified_replay") is True)


def support_columns(case: dict[str, Any]) -> list[int]:
    support = {
        int_value(item)
        for item in list_value(case.get("term_support")) + list_value(case.get("coeff_support"))
    }
    return sorted(support)


def compact_case(
    artifact: Path,
    case: dict[str, Any],
    priority_columns: set[int],
    anchors: list[tuple[int, int]],
    radius: int,
) -> dict[str, Any] | None:
    row_keys = list_value(case.get("row_keys"))
    salts = salts_from_row_keys(row_keys)
    if len(row_keys) != 2 or len(salts) != 2:
        return None
    pair = (salts[0], salts[1])
    anchor = closest_anchor(pair, anchors)
    if anchor is None:
        return None
    exact_anchor = tuple(anchor["anchor"]) == pair
    in_neighborhood = exact_anchor or int_value(anchor["linf"]) <= radius
    if not in_neighborhood:
        return None
    support = support_columns(case)
    priority_hits = sorted(set(support) & priority_columns)
    verified = bool_verified(case)
    source_cost = float_value(case.get("source_charged_unit_ops_over_rho"))
    direct_cost = float_value(case.get("direct_ops_over_rho"))
    return {
        "artifact": str(artifact),
        "direct_ops_over_rho": direct_cost,
        "exact_anchor": exact_anchor,
        "nearest_anchor": anchor,
        "order": int_value(case.get("order")),
        "priority_hit_count": int_value(case.get("priority_hit_count")),
        "priority_support_hits": priority_hits,
        "row_keys": [str(item) for item in row_keys],
        "row_pair_key": row_pair_key(row_keys),
        "salt_pair": list(pair),
        "selector": case.get("selector"),
        "source_charged_unit_ops_over_rho": source_cost,
        "source_label": source_label(artifact),
        "support": support,
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
        "verified": verified,
    }


def load_cases(
    paths: list[Path],
    target: str,
    order: int,
    priority_columns: set[int],
    anchors: list[tuple[int, int]],
    radius: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    cases: list[dict[str, Any]] = []
    missing: list[str] = []
    seen: set[tuple[Any, ...]] = set()
    for path in paths:
        if not path.exists():
            missing.append(str(path))
            continue
        payload = load_json(path)
        for raw in list_value(payload.get("case_reports")):
            if not isinstance(raw, dict):
                continue
            if str(raw.get("target")) != target:
                continue
            if int_value(raw.get("order")) != order:
                continue
            item = compact_case(path, raw, priority_columns, anchors, radius)
            if item is None:
                continue
            key = (
                item["source_label"],
                item["target"],
                item["order"],
                item["transfer_index"],
                item["selector"],
                item["top_k"],
                tuple(item["row_keys"]),
                tuple(item["support"]),
            )
            if key in seen:
                continue
            seen.add(key)
            cases.append(item)
    return cases, missing


def support_key(case: dict[str, Any]) -> str:
    return ",".join(str(item) for item in case.get("support") or [])


def case_sort_key(case: dict[str, Any]) -> tuple[Any, ...]:
    priority_hits = case.get("priority_support_hits") or []
    source_cost = case.get("source_charged_unit_ops_over_rho")
    direct_cost = case.get("direct_ops_over_rho")
    nearest = case.get("nearest_anchor") or {}
    return (
        not bool(priority_hits),
        not bool(case.get("verified")),
        not bool(case.get("exact_anchor")),
        int_value(nearest.get("linf"), 999),
        -len(priority_hits),
        float(source_cost if source_cost is not None else 10**9),
        float(direct_cost if direct_cost is not None else 10**9),
        int_value(case.get("transfer_index")),
        str(case.get("selector")),
    )


def summarize(cases: list[dict[str, Any]], priority_columns: set[int]) -> dict[str, Any]:
    priority_cases = [case for case in cases if case.get("priority_support_hits")]
    verified_priority = [case for case in priority_cases if case.get("verified")]
    exact_cases = [case for case in cases if case.get("exact_anchor")]
    verified_cases = [case for case in cases if case.get("verified")]
    source_counts = Counter(str(case.get("source_label")) for case in cases)
    anchor_counts = Counter(",".join(map(str, (case.get("nearest_anchor") or {}).get("anchor") or [])) for case in cases)
    support_counts = Counter(support_key(case) for case in cases)
    return {
        "anchor_counts": dict(sorted(anchor_counts.items())),
        "case_count": len(cases),
        "exact_anchor_case_count": len(exact_cases),
        "priority_columns": sorted(priority_columns),
        "priority_support_case_count": len(priority_cases),
        "source_counts": dict(sorted(source_counts.items())),
        "support_counts": dict(sorted(support_counts.items())),
        "verified_case_count": len(verified_cases),
        "verified_priority_support_case_count": len(verified_priority),
    }


def claim_status(summary: dict[str, Any]) -> str:
    if int_value(summary.get("verified_priority_support_case_count")):
        return "VERIFIED_ROWPAIR_NEIGHBOR_PRIORITY_SUPPORT_FOUND"
    if int_value(summary.get("priority_support_case_count")):
        return "ALLGATED_ROWPAIR_NEIGHBOR_PRIORITY_SUPPORT_TRACE_FOUND"
    return "NO_ROWPAIR_NEIGHBOR_PRIORITY_SUPPORT_FOUND"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scout-artifacts", required=True)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--order", type=int, default=9887)
    parser.add_argument("--priority-columns", default="6,12,13")
    parser.add_argument("--anchor-pairs", default="203,204;207,208;206,209")
    parser.add_argument("--neighbor-radius", type=int, default=3)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--top-limit", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = parse_paths(args.scout_artifacts)
    priority_columns = set(parse_ints(args.priority_columns))
    anchors = parse_anchor_pairs(args.anchor_pairs)
    cases, missing = load_cases(
        paths,
        str(args.target),
        int(args.order),
        priority_columns,
        anchors,
        int(args.neighbor_radius),
    )
    cases.sort(key=case_sort_key)
    priority_cases = [case for case in cases if case.get("priority_support_hits")]
    verified_priority_cases = [case for case in priority_cases if case.get("verified")]
    near_misses = [case for case in cases if not case.get("priority_support_hits")]
    summary = summarize(cases, priority_columns)
    payload = {
        "artifacts": {
            "missing_scout_artifacts": missing,
            "scout_artifacts": [str(path) for path in paths],
        },
        "claim_status": claim_status(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: aggregates existing priority-scout JSON case reports.",
            "HEURISTIC: row-pair neighborhood ranking is a source-generation guide.",
            "NO SPEEDUP CLAIM: relation export, substitution, sparse-LA, fresh-target transfer, and rho accounting remain separate gates.",
        ],
        "parameters": {
            "anchor_pairs": [list(pair) for pair in anchors],
            "neighbor_radius": int(args.neighbor_radius),
            "order": int(args.order),
            "priority_columns": sorted(priority_columns),
            "target": str(args.target),
        },
        "priority_support_cases": priority_cases[: args.top_limit],
        "schema": "ecdlp.low_term_total2_order9887_rowpair_neighborhood_support_scanner.v1",
        "summary": summary,
        "top_near_misses": near_misses[: args.top_limit],
        "top_verified_priority_support_cases": verified_priority_cases[: args.top_limit],
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
