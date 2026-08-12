#!/usr/bin/env python3
"""P971 public single-row selector audit."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p971_public_single_row_selector_audit.md"
DEFAULT_P969 = STATE_DIR / "low_term_total2_p969_heldout_rank3_seed_budget_rescue_probe.json"
DEFAULT_P970 = STATE_DIR / "low_term_total2_p970_rank4_from_p969_seed_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p971_public_single_row_selector_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p971_public_single_row_selector_audit.v1"


RuleFn = Callable[[dict[str, Any]], bool]


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


def bool_value(value: Any) -> bool:
    return bool(value)


def one_leaf_signature(signature: str) -> tuple[str, int] | None:
    parts = [part.strip() for part in str(signature).split(",") if part.strip()]
    if len(parts) != 1 or ":" not in parts[0]:
        return None
    row_short, leaf_raw = parts[0].rsplit(":", 1)
    try:
        return row_short, int(leaf_raw)
    except ValueError:
        return None


def verified_rank(early: dict[str, Any], expected_secret: int, target_rank: int) -> bool:
    return (
        bool(early.get("public_key_verified"))
        and int_value(early.get("rank")) >= int(target_rank)
        and early.get("derived_secret") == expected_secret
    )


def first_public_event(row: dict[str, Any]) -> dict[str, Any]:
    events = row.get("candidate_event_signatures") or []
    if not events:
        return {}
    return (events[0] or {}).get("public_keys") or {}


def public_features(row: dict[str, Any], row_short: str, leaf: int) -> dict[str, Any]:
    first = first_public_event(row)
    event_count = int_value(row.get("candidate_event_count"))
    non_event = int_value(row.get("non_event_marginal_ops"))
    seed_ops = int_value(row.get("seed_ops"))
    return {
        "candidate_event_count": event_count,
        "candidate_event_count_eq_2": event_count == 2,
        "candidate_event_count_eq_4": event_count == 4,
        "candidate_event_count_ge_1": event_count >= 1,
        "candidate_event_count_ge_4": event_count >= 4,
        "first_row_x": first.get("row_x"),
        "first_scout_pos": first.get("scout_pos"),
        "first_scout_s3_root_product": first.get("scout_s3_root_product"),
        "first_scout_s3_root_sum": first.get("scout_s3_root_sum"),
        "first_scout_unsigned_indices": first.get("scout_unsigned_indices"),
        "first_term_shape": first.get("term_shape"),
        "first_term_support": first.get("term_support"),
        "has_candidate_events": event_count > 0,
        "leaf": int(leaf),
        "non_event_marginal_le_1": non_event <= 1,
        "non_event_marginal_le_2": non_event <= 2,
        "non_event_marginal_ops": non_event,
        "row_leaf": f"{row_short}:{leaf}",
        "row_short": row_short,
        "seed_ops": seed_ops,
        "seed_ops_le_118": seed_ops <= 118,
        "seed_ops_le_122": seed_ops <= 122,
    }


def compact_candidate(row: dict[str, Any]) -> dict[str, Any]:
    labels = row.get("labels") or {}
    return {
        "accepted_added_relation_count": labels.get("accepted_added_relation_count"),
        "added_signature": row.get("added_signature"),
        "budget_success": labels.get("budget_success"),
        "candidate_event_count": row["features"].get("candidate_event_count"),
        "context": row.get("context"),
        "early_ops": labels.get("early_ops"),
        "early_rank": labels.get("early_rank"),
        "non_event_marginal_ops": row["features"].get("non_event_marginal_ops"),
        "rank3_verified": labels.get("rank3_verified"),
        "rank4_verified": labels.get("rank4_verified"),
        "row_short": row["features"].get("row_short"),
        "seed_ops": row["features"].get("seed_ops"),
        "seed_selector": row.get("seed_selector"),
        "source_kinds": sorted(row.get("source_kinds") or []),
    }


def add_or_merge_candidate(
    out: dict[tuple[Any, ...], dict[str, Any]],
    key: tuple[Any, ...],
    candidate: dict[str, Any],
) -> None:
    if key not in out:
        out[key] = candidate
        return
    existing = out[key]
    existing.setdefault("source_kinds", set()).update(candidate.get("source_kinds") or set())
    existing.setdefault("source_records", []).extend(candidate.get("source_records") or [])
    existing_labels = existing.setdefault("labels", {})
    for label_key, value in (candidate.get("labels") or {}).items():
        if isinstance(value, bool):
            existing_labels[label_key] = bool(existing_labels.get(label_key)) or value
        elif existing_labels.get(label_key) in (None, 0):
            existing_labels[label_key] = value


def p969_candidates(p969: dict[str, Any], expected_secret: int) -> list[dict[str, Any]]:
    by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for audit in p969.get("seed_audits") or []:
        seed = audit.get("seed") or {}
        seed_selector = str(seed.get("selector"))
        for result in audit.get("completion_results") or []:
            if int_value(result.get("added_leaf_count")) != 1:
                continue
            parsed = one_leaf_signature(str(result.get("added_signature") or ""))
            if parsed is None:
                continue
            row_short, leaf = parsed
            early = result.get("early_stop") or {}
            labels = {
                "accepted_added_relation_count": int_value(result.get("accepted_added_relation_count")),
                "accepted_rank_raiser": int_value(result.get("accepted_added_relation_count")) > 0,
                "budget_success": bool(result.get("budget_success")),
                "early_ops": early.get("ops"),
                "early_rank": early.get("rank"),
                "early_verified": bool(early.get("public_key_verified")),
                "rank3_verified": verified_rank(early, expected_secret, 3),
                "rank4_verified": verified_rank(early, expected_secret, 4),
            }
            features = public_features(result, row_short, leaf)
            key = ("p969", seed_selector, features["row_leaf"], features["seed_ops"])
            add_or_merge_candidate(
                by_key,
                key,
                {
                    "added_signature": result.get("added_signature"),
                    "context": "p969_rank3_seed_budget_rescue",
                    "features": features,
                    "labels": labels,
                    "seed_selector": seed_selector,
                    "source_kinds": {str(result.get("selector_kind"))},
                    "source_records": [
                        {
                            "completion_mode": result.get("completion_mode"),
                            "completion_scheme": result.get("completion_scheme"),
                            "selector_kind": result.get("selector_kind"),
                        }
                    ],
                },
            )
    return list(by_key.values())


def p970_candidates(p970: dict[str, Any], expected_secret: int) -> list[dict[str, Any]]:
    by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    seed_selector = ((p970.get("frontier_seed") or {}).get("compressed_rank3_seed") or {}).get("selector")
    for result in p970.get("completion_results") or []:
        if int_value(result.get("added_leaf_count")) != 1:
            continue
        parsed = one_leaf_signature(str(result.get("added_signature") or ""))
        if parsed is None:
            continue
        row_short, leaf = parsed
        early = result.get("early_stop") or {}
        labels = {
            "accepted_added_relation_count": int_value(result.get("accepted_added_relation_count")),
            "accepted_rank_raiser": int_value(result.get("accepted_added_relation_count")) > 0,
            "below_rho_rank4": bool((early.get("success"))),
            "budget_success": False,
            "early_ops": early.get("ops"),
            "early_rank": early.get("rank"),
            "early_verified": bool(early.get("public_key_verified")),
            "rank3_verified": verified_rank(early, expected_secret, 3),
            "rank4_verified": verified_rank(early, expected_secret, 4),
        }
        features = public_features(result, row_short, leaf)
        key = ("p970", seed_selector, features["row_leaf"], features["seed_ops"])
        add_or_merge_candidate(
            by_key,
            key,
            {
                "added_signature": result.get("added_signature"),
                "context": "p970_rank4_from_p969_seed",
                "features": features,
                "labels": labels,
                "seed_selector": seed_selector,
                "source_kinds": {str(result.get("selector_kind"))},
                "source_records": [
                    {
                        "completion_mode": result.get("completion_mode"),
                        "completion_scheme": result.get("completion_scheme"),
                        "selector_kind": result.get("selector_kind"),
                    }
                ],
            },
        )
    return list(by_key.values())


def rules() -> list[dict[str, Any]]:
    return [
        {
            "description": "Public event count identifies four scheduled candidate events and the seed is at or below 118 ops.",
            "name": "seed_ops_le118_and_candidate_event_count_eq4",
            "predicate": lambda f: f["seed_ops_le_118"] and f["candidate_event_count_eq_4"],
        },
        {
            "description": "Public first-event term support matches the P969 useful event and seed ops are at or below 118.",
            "name": "seed_ops_le118_and_first_term_support_1_7_12",
            "predicate": lambda f: f["seed_ops_le_118"] and f["first_term_support"] == "1,7,12",
        },
        {
            "description": "Public first-event unsigned-index multiset matches the P969 useful event and seed ops are at or below 118.",
            "name": "seed_ops_le118_and_first_unsigned_1_7_7_12",
            "predicate": lambda f: f["seed_ops_le_118"] and f["first_scout_unsigned_indices"] == "1,7,7,12",
        },
        {
            "description": "Public event count identifies four scheduled candidate events.",
            "name": "candidate_event_count_eq4",
            "predicate": lambda f: f["candidate_event_count_eq_4"],
        },
        {
            "description": "Public event count identifies at least four scheduled candidate events.",
            "name": "candidate_event_count_ge4",
            "predicate": lambda f: f["candidate_event_count_ge_4"],
        },
        {
            "description": "Public first-event term support matches the P969 useful event.",
            "name": "first_term_support_1_7_12",
            "predicate": lambda f: f["first_term_support"] == "1,7,12",
        },
        {
            "description": "Public first-event unsigned-index multiset matches the P969 useful event.",
            "name": "first_unsigned_1_7_7_12",
            "predicate": lambda f: f["first_scout_unsigned_indices"] == "1,7,7,12",
        },
        {
            "description": "Public row/leaf identity selects the observed useful single row.",
            "name": "row_salt208_leaf3",
            "predicate": lambda f: f["row_short"] == "salt208" and f["leaf"] == 3,
        },
        {
            "description": "Public row/leaf identity selects the observed useful single row and seed ops are at or below 118.",
            "name": "seed_ops_le118_and_row_salt208_leaf3",
            "predicate": lambda f: f["seed_ops_le_118"] and f["row_short"] == "salt208" and f["leaf"] == 3,
        },
        {
            "description": "Public event count plus low marginal overhead.",
            "name": "candidate_event_count_ge1_and_non_event_le2",
            "predicate": lambda f: f["candidate_event_count_ge_1"] and f["non_event_marginal_le_2"],
        },
        {
            "description": "Public low overhead only.",
            "name": "non_event_marginal_le1",
            "predicate": lambda f: f["non_event_marginal_le_1"],
        },
    ]


def score_rule(rule: dict[str, Any], candidates: list[dict[str, Any]], context: str) -> dict[str, Any]:
    predicate: RuleFn = rule["predicate"]
    selected = [row for row in candidates if predicate(row["features"])]
    rank3 = [row for row in selected if bool((row.get("labels") or {}).get("rank3_verified"))]
    rank4 = [row for row in selected if bool((row.get("labels") or {}).get("rank4_verified"))]
    budget = [row for row in selected if bool((row.get("labels") or {}).get("budget_success"))]
    accepted = [row for row in selected if bool((row.get("labels") or {}).get("accepted_rank_raiser"))]
    below_rho_rank4 = [row for row in selected if bool((row.get("labels") or {}).get("below_rho_rank4"))]
    return {
        "accepted_rank_raiser_count": len(accepted),
        "below_rho_rank4_count": len(below_rho_rank4),
        "budget_success_count": len(budget),
        "context": context,
        "false_budget_count": len(selected) - len(budget),
        "false_rank3_count": len(selected) - len(rank3),
        "false_rank4_count": len(selected) - len(rank4),
        "rank3_verified_count": len(rank3),
        "rank4_verified_count": len(rank4),
        "rule_description": rule["description"],
        "rule_name": rule["name"],
        "selected": [compact_candidate(row) for row in selected],
        "selected_count": len(selected),
        "uses_accepted_labels": False,
    }


def evaluate_rules(p969_rows: list[dict[str, Any]], p970_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for rule in rules():
        out.append(
            {
                "p969": score_rule(rule, p969_rows, "p969_rank3_seed_budget_rescue"),
                "p970": score_rule(rule, p970_rows, "p970_rank4_from_p969_seed"),
                "rule_description": rule["description"],
                "rule_name": rule["name"],
                "uses_accepted_labels": False,
            }
        )
    return out


def best_budget_rule(rule_scores: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        row
        for row in rule_scores
        if row["p969"]["budget_success_count"] > 0 and row["p969"]["false_budget_count"] == 0
    ]
    if not candidates:
        return None
    order = {rule["name"]: index for index, rule in enumerate(rules())}
    candidates.sort(
        key=lambda row: (
            row["p969"]["selected_count"],
            -row["p969"]["budget_success_count"],
            order.get(row["rule_name"], 999),
        )
    )
    return candidates[0]


def best_rank3_rule(rule_scores: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        row
        for row in rule_scores
        if row["p969"]["selected_count"] > 0 and row["p969"]["false_rank3_count"] == 0
    ]
    if not candidates:
        return None
    order = {rule["name"]: index for index, rule in enumerate(rules())}
    candidates.sort(
        key=lambda row: (
            row["p969"]["selected_count"],
            -row["p969"]["rank3_verified_count"],
            order.get(row["rule_name"], 999),
        )
    )
    return candidates[0]


def summarize(rule_scores: list[dict[str, Any]], p969_rows: list[dict[str, Any]], p970_rows: list[dict[str, Any]]) -> dict[str, Any]:
    budget_rule = best_budget_rule(rule_scores)
    rank3_rule = best_rank3_rule(rule_scores)
    p970_rank4_hits = [
        row
        for score in rule_scores
        for row in score["p970"]["selected"]
        if row.get("rank4_verified")
    ]
    if budget_rule and budget_rule["p970"]["below_rho_rank4_count"] > 0:
        claim = "P971_PUBLIC_RULE_SELECTS_RANK4_BELOW_RHO"
    elif budget_rule:
        claim = "P971_PUBLIC_EVENT_SCHEDULE_RULE_ISOLATES_P969_BUDGET_RESCUE_NO_RANK4_FOLLOWUP"
    elif rank3_rule:
        claim = "P971_PUBLIC_EVENT_SCHEDULE_RULE_SELECTS_RANK3_RAISERS_BUDGET_OPEN"
    else:
        claim = "NEGATIVE_RESULT_P971_NO_PUBLIC_RULE_FOR_P969_BUDGET_RESCUE"
    return {
        "best_budget_rule": {
            "p969": budget_rule["p969"],
            "p970": budget_rule["p970"],
            "rule_description": budget_rule["rule_description"],
            "rule_name": budget_rule["rule_name"],
        }
        if budget_rule
        else None,
        "best_rank3_rule": {
            "p969": rank3_rule["p969"],
            "p970": rank3_rule["p970"],
            "rule_description": rank3_rule["rule_description"],
            "rule_name": rank3_rule["rule_name"],
        }
        if rank3_rule
        else None,
        "claim_status": claim,
        "p969_budget_positive_count": sum(1 for row in p969_rows if row["labels"].get("budget_success")),
        "p969_candidate_count": len(p969_rows),
        "p969_rank3_positive_count": sum(1 for row in p969_rows if row["labels"].get("rank3_verified")),
        "p970_candidate_count": len(p970_rows),
        "p970_rank4_positive_count": len(p970_rank4_hits),
        "rule_count": len(rule_scores),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p969 = load_json(Path(args.p969))
    p970 = load_json(Path(args.p970))
    p969_rows = p969_candidates(p969, int(args.expected_secret))
    p970_rows = p970_candidates(p970, int(args.expected_secret))
    rule_scores = evaluate_rules(p969_rows, p970_rows)
    summary = summarize(rule_scores, p969_rows, p970_rows)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p969_result": str(args.p969),
            "p970_result": str(args.p970),
            "script": str(Path(__file__)),
        },
        "candidate_tables": {
            "p969_single_leaf_candidates": [compact_candidate(row) for row in p969_rows],
            "p970_single_leaf_candidates": [compact_candidate(row) for row in p970_rows],
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "SAME-FRONTIER-SCREEN: rules are scored on the P969/P970 frontier, not a broad heldout population.",
            "NO-ACCEPTED-LABEL-SELECTION: rule predicates use only public event-schedule and cost fields; accepted-relation labels are scoring labels only.",
            "PUBLIC-SCREEN-NOT-END-TO-END: this audits source selection, not full relation collection, rank-4 completion, sparse linear algebra, or target descent.",
        ],
        "method": "p971_public_single_row_selector_audit",
        "parameters": {
            "expected_secret": int(args.expected_secret),
            "p969": str(args.p969),
            "p970": str(args.p970),
        },
        "rule_scores": rule_scores,
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p969", type=Path, default=DEFAULT_P969)
    parser.add_argument("--p970", type=Path, default=DEFAULT_P970)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--expected-secret", type=int, default=2351)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    best = summary.get("best_budget_rule") or {}
    print(
        f"claim={payload['claim_status']} "
        f"p969_candidates={summary['p969_candidate_count']} "
        f"p969_budget_positive={summary['p969_budget_positive_count']} "
        f"p970_candidates={summary['p970_candidate_count']} "
        f"p970_rank4_positive={summary['p970_rank4_positive_count']} "
        f"rules={summary['rule_count']} "
        f"best_budget_rule={best.get('rule_name')} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
