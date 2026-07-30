#!/usr/bin/env python3
"""Summarize independent target-column residual classes.

Residual scouts can emit many candidate rows and repeated motifs.  This tool
deduplicates normalized quotient residuals, separates repeats of a known class
from independent classes, and emits the next promotion frontier.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_KNOWN_RESIDUAL = "0,0,0,0,1,0,11778,0,0,0,0,0,0,0,0,0"
DEFAULT_OUT = STATE_DIR / "low_term_total2_independent_residual_frontier_probe.json"


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


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def parse_known_residuals(raw: str | None) -> set[tuple[int, ...]]:
    if not raw:
        return set()
    out = set()
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        out.add(tuple(int_value(part) for part in chunk.split(",") if part.strip()))
    return out


def order_reports(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reports = payload.get("order_reports")
    return reports if isinstance(reports, dict) else {}


def vector_key(values: list[Any]) -> tuple[int, ...]:
    return tuple(int_value(item) for item in values)


def compact_candidate(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": sample.get("artifact"),
        "artifact_offset": int_value(sample.get("artifact_offset")),
        "charged_ops_over_rho": sample.get("charged_ops_over_rho"),
        "direct_ops_over_rho": sample.get("direct_ops_over_rho"),
        "forms_count": int_value(sample.get("forms_count")),
        "rank": int_value(sample.get("rank")),
        "selector": sample.get("selector"),
        "target": sample.get("target"),
        "top_k": int_value(sample.get("top_k")),
        "transfer_index": int_value(sample.get("transfer_index")),
        "window": sample.get("window"),
    }


def artifact_window(path: str | None) -> str | None:
    if not path:
        return None
    name = Path(path).name
    parts = name.rsplit("_", 3)
    if len(parts) >= 3:
        return "_".join(parts[-3:-1])
    return None


def residual_priority(row: dict[str, Any]) -> tuple[Any, ...]:
    hits = set(row.get("target_column_hits") or [])
    both = {6, 15} <= hits
    has15 = 15 in hits
    independent = not row.get("matches_known_residual")
    min_ops = row.get("charged_ops_over_rho_min")
    return (
        not both,
        not has15,
        not independent,
        float(min_ops if min_ops is not None else 10**18),
        -int_value(row.get("candidate_count")),
    )


def compact_group(group: dict[str, Any], known_residuals: set[tuple[int, ...]]) -> dict[str, Any]:
    normalized = [int_value(item) for item in group.get("normalized_residual") or []]
    key = tuple(normalized)
    samples = [compact_candidate(sample) for sample in list_value(group.get("candidate_samples"))]
    first = samples[0] if samples else {}
    hits = [int_value(item) for item in list_value(group.get("target_column_hits"))]
    return {
        "candidate_count": int_value(group.get("candidate_count")),
        "candidate_samples": samples[:8],
        "charged_ops_over_rho_min": group.get("charged_ops_over_rho_min"),
        "first_artifact_window": artifact_window(first.get("artifact")),
        "first_transfer_index": first.get("transfer_index"),
        "first_top_k": first.get("top_k"),
        "first_selector": first.get("selector"),
        "free_column_support": list_value(group.get("free_column_support")),
        "matches_known_residual": key in known_residuals,
        "normalized_residual": normalized,
        "residual_support": list_value(group.get("residual_support")),
        "target_column_hits": hits,
    }


def collect_charged(paths: list[Path], known_residuals: set[tuple[int, ...]]) -> tuple[dict[str, dict[tuple[int, ...], dict[str, Any]]], Counter[str]]:
    by_order: dict[str, dict[tuple[int, ...], dict[str, Any]]] = defaultdict(dict)
    action_counts: Counter[str] = Counter()
    for path in paths:
        payload = load_json(path)
        for order, report in order_reports(payload).items():
            work_order = report.get("work_order") if isinstance(report.get("work_order"), dict) else {}
            if work_order.get("action"):
                action_counts[str(work_order.get("action"))] += 1
            for group in report.get("residual_groups") or []:
                if not isinstance(group, dict) or not group.get("target_column_hits"):
                    continue
                compact = compact_group(group, known_residuals)
                key = tuple(compact["normalized_residual"])
                prior = by_order[str(order)].get(key)
                if prior is None:
                    by_order[str(order)][key] = compact
                    continue
                prior["candidate_count"] += compact["candidate_count"]
                prior["candidate_samples"].extend(compact["candidate_samples"])
                prior["candidate_samples"] = prior["candidate_samples"][:8]
                prior_min = prior.get("charged_ops_over_rho_min")
                new_min = compact.get("charged_ops_over_rho_min")
                if new_min is not None and (prior_min is None or float(new_min) < float(prior_min)):
                    prior["charged_ops_over_rho_min"] = new_min
                    prior["first_artifact_window"] = compact.get("first_artifact_window")
                    prior["first_transfer_index"] = compact.get("first_transfer_index")
                    prior["first_top_k"] = compact.get("first_top_k")
                    prior["first_selector"] = compact.get("first_selector")
    return by_order, action_counts


def collect_bank_summaries(paths: list[Path]) -> list[dict[str, Any]]:
    out = []
    for path in paths:
        payload = load_json(path)
        summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
        order_audits = payload.get("order_audits") if isinstance(payload.get("order_audits"), dict) else {}
        out.append(
            {
                "artifact": str(path),
                "summary": summary,
                "order_audits": {
                    order: {
                        "deficiency": audit.get("deficiency"),
                        "factor_variables_derivable_count": audit.get("factor_variables_derivable_count"),
                        "rank": audit.get("rank"),
                        "unique_factor_relation_count": audit.get("unique_factor_relation_count"),
                    }
                    for order, audit in order_audits.items()
                    if isinstance(audit, dict)
                },
            }
        )
    return out


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    known_residuals = parse_known_residuals(args.known_residuals)
    charged_paths = parse_paths(args.charged_artifacts)
    bank_paths = parse_paths(args.bank_artifacts)
    by_order, action_counts = collect_charged(charged_paths, known_residuals)
    reports = {}
    total_classes = 0
    independent_classes = 0
    col15_classes = 0
    both_classes = 0
    for order, groups in sorted(by_order.items(), key=lambda item: int_value(item[0], 10**9)):
        rows = sorted(groups.values(), key=residual_priority)
        status_counts = Counter()
        for row in rows:
            total_classes += 1
            hits = set(row.get("target_column_hits") or [])
            if not row.get("matches_known_residual"):
                independent_classes += 1
                status_counts["INDEPENDENT_TARGET_RESIDUAL_CLASS"] += 1
            else:
                status_counts["KNOWN_TARGET_RESIDUAL_CLASS_REPEAT"] += 1
            if 15 in hits:
                col15_classes += 1
                status_counts["COLUMN_15_RESIDUAL_CLASS"] += 1
            if {6, 15} <= hits:
                both_classes += 1
                status_counts["COLUMN_6_AND_15_RESIDUAL_CLASS"] += 1
        reports[order] = {
            "frontier_classes": rows,
            "frontier_class_count": len(rows),
            "status_counts": dict(sorted(status_counts.items())),
            "top_action": (
                "PROMOTE_COLUMN_15_AND_MIXED_TARGET_RESIDUALS"
                if any(15 in set(row.get("target_column_hits") or []) for row in rows)
                else "PROMOTE_INDEPENDENT_TARGET_RESIDUALS"
                if any(not row.get("matches_known_residual") for row in rows)
                else "GENERATE_MORE_INDEPENDENT_RESIDUALS"
            ),
        }
    claim_status = (
        "COLUMN_15_TARGET_RESIDUAL_FRONTIER_READY"
        if col15_classes
        else "INDEPENDENT_TARGET_RESIDUAL_FRONTIER_READY"
        if independent_classes
        else "KNOWN_TARGET_RESIDUAL_REPEATS_ONLY"
        if total_classes
        else "NEGATIVE_RESULT_NO_TARGET_RESIDUAL_CLASSES"
    )
    return {
        "artifacts": {
            "bank_artifacts": [str(path) for path in bank_paths],
            "charged_artifacts": [str(path) for path in charged_paths],
        },
        "bank_summaries": collect_bank_summaries(bank_paths),
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: residual classes live in the current order-specific low-term factor-column namespace.",
            "OPEN: residual promotion is not a target descent or a deployed-curve attack.",
            "Pollard rho remains the baseline; this artifact only prioritizes relation classes.",
        ],
        "known_residuals": [list(row) for row in sorted(known_residuals)],
        "order_reports": reports,
        "schema": "ecdlp.low_term_total2_independent_residual_frontier.v1",
        "summary": {
            "charged_action_counts": dict(sorted(action_counts.items())),
            "column_15_class_count": col15_classes,
            "column_6_and_15_class_count": both_classes,
            "independent_class_count": independent_classes,
            "order_count": len(reports),
            "target_residual_class_count": total_classes,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--charged-artifacts", required=True)
    parser.add_argument("--bank-artifacts", default="")
    parser.add_argument("--known-residuals", default=DEFAULT_KNOWN_RESIDUAL)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
