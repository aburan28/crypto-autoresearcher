#!/usr/bin/env python3
"""P905 public regime-switch scheduler over P903/P904 evaluated cases."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p905_regime_switch_scheduler.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p905_regime_switch_scheduler_probe.json"
P903_SOURCE = STATE_DIR / "low_term_total2_p903_relaxed_family_grid_validation_probe.json"
P904_SOURCE = STATE_DIR / "low_term_total2_p904_leaf90_top7_forward_freeze_probe.json"
SCHEMA = "ecdlp.low_term_total2_p905_regime_switch_scheduler.v1"
TARGET = "22050.cf1@11731"
RHO_ESTIMATE = 137
STRICT_TARGET_OPS = 136
MARGIN_TARGET_OPS = 135
SPLITS = ("train", "validation", "forward")


CLAUSES = [
    {
        "leaf_signatures": ["8/8"],
        "name": "c8_gap8_top7_lowleaf_hybrid_opsge0p70",
        "salt_gap_min": 8,
        "selector_groups": ["low_leaf", "hybrid"],
        "source_ops_min": 0.70,
        "top_ks": [7],
    },
    {
        "leaf_signatures": ["90/90"],
        "name": "c90_top7_lowterm_opsge0p70",
        "salt_gap_min": 0,
        "selector_groups": ["low_term"],
        "source_ops_min": 0.70,
        "top_ks": [7],
    },
    {
        "leaf_signatures": ["19/19"],
        "name": "c19_top4_lowleaf_hybrid_opsge0p70",
        "salt_gap_min": 0,
        "selector_groups": ["low_leaf", "hybrid"],
        "source_ops_min": 0.70,
        "top_ks": [4],
    },
]

SCHEDULERS = [
    {
        "clause_names": [
            "c8_gap8_top7_lowleaf_hybrid_opsge0p70",
            "c90_top7_lowterm_opsge0p70",
            "c19_top4_lowleaf_hybrid_opsge0p70",
        ],
        "name": "p905_c8gap8_then_c90_then_c19",
    },
    {
        "clause_names": ["c90_top7_lowterm_opsge0p70"],
        "name": "control_c90_only",
    },
    {
        "clause_names": ["c19_top4_lowleaf_hybrid_opsge0p70"],
        "name": "control_c19_only",
    },
    {
        "clause_names": ["c8_gap8_top7_lowleaf_hybrid_opsge0p70"],
        "name": "control_c8gap8_only",
    },
    {
        "clause_names": [
            "c90_top7_lowterm_opsge0p70",
            "c8_gap8_top7_lowleaf_hybrid_opsge0p70",
            "c19_top4_lowleaf_hybrid_opsge0p70",
        ],
        "name": "redteam_c90_then_c8gap8_then_c19",
    },
    {
        "clause_names": [
            "c19_top4_lowleaf_hybrid_opsge0p70",
            "c90_top7_lowterm_opsge0p70",
            "c8_gap8_top7_lowleaf_hybrid_opsge0p70",
        ],
        "name": "redteam_c19_then_c90_then_c8gap8",
    },
]


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
        return int(default)


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def load_rows() -> list[dict[str, Any]]:
    p903 = load_json(P903_SOURCE)
    p904 = load_json(P904_SOURCE)
    rows: list[dict[str, Any]] = []
    for source_name, payload in (("p903", p903), ("p904", p904)):
        for row in payload.get("evaluated_cases") or []:
            case = row.get("case") or {}
            split = str(case.get("split"))
            if split not in SPLITS:
                continue
            row = dict(row)
            case = dict(case)
            case["artifact_source"] = source_name
            row["case"] = case
            rows.append(row)
    return rows


def matches_clause(row: dict[str, Any], clause: dict[str, Any]) -> bool:
    case = row.get("case") or {}
    if str(case.get("target")) != TARGET:
        return False
    if case.get("leaf_signature") not in set(clause.get("leaf_signatures") or []):
        return False
    if int_value(case.get("top_k")) not in {int_value(v) for v in clause.get("top_ks") or []}:
        return False
    if case.get("selector_group") not in set(clause.get("selector_groups") or []):
        return False
    if float_value(case.get("ops_over_rho")) < float_value(clause.get("source_ops_min")):
        return False
    if int_value(case.get("salt_gap"), -1) < int_value(clause.get("salt_gap_min")):
        return False
    return True


def is_good(row: dict[str, Any]) -> bool:
    return bool(row.get("strict_below_rho") and row.get("public_key_verified"))


def row_set_key(row: dict[str, Any]) -> tuple[Any, ...]:
    case = row.get("case") or {}
    return (
        str(case.get("split")),
        int_value(case.get("transfer_index")),
        tuple(
            (
                str(row_leaf.get("row_key")),
                tuple(int_value(leaf) for leaf in row_leaf.get("leaf_indices") or []),
            )
            for row_leaf in case.get("row_leaf_keys") or []
        ),
    )


def row_order_key(row: dict[str, Any]) -> tuple[Any, ...]:
    case = row.get("case") or {}
    return (
        int_value(case.get("split_stream_ordinal")),
        str(case.get("selector")),
        int_value(case.get("global_stream_ordinal")),
    )


def compact_row(row: dict[str, Any] | None, total_cost: int | None = None, clause_name: str | None = None) -> dict[str, Any] | None:
    if row is None:
        return None
    case = row.get("case") or {}
    return {
        "clause": clause_name,
        "concrete_union_dedup_ops": row.get("concrete_union_dedup_ops"),
        "concrete_union_dedup_ops_over_rho": row.get("concrete_union_dedup_ops_over_rho"),
        "generator_case_cost_ops": row.get("generator_case_cost_ops"),
        "leaf_signature": case.get("leaf_signature"),
        "ops_over_rho": case.get("ops_over_rho"),
        "public_key_verified": row.get("public_key_verified"),
        "rank": case.get("rank"),
        "relation_count": case.get("relation_count"),
        "rho_estimate": row.get("rho_estimate"),
        "row_leaf_keys": case.get("row_leaf_keys"),
        "row_salts": case.get("row_salts"),
        "salt_gap": case.get("salt_gap"),
        "selector": case.get("selector"),
        "selector_group": case.get("selector_group"),
        "split": case.get("split"),
        "split_stream_ordinal": case.get("split_stream_ordinal"),
        "strict_below_rho": row.get("strict_below_rho"),
        "strict_below_rho_margin_ops": row.get("strict_below_rho_margin_ops"),
        "top_k": case.get("top_k"),
        "total_cost_ops": total_cost,
        "total_cost_over_rho": ratio(total_cost, RHO_ESTIMATE) if total_cost is not None else None,
        "transfer_index": case.get("transfer_index"),
    }


def clause_by_name() -> dict[str, dict[str, Any]]:
    return {str(clause["name"]): clause for clause in CLAUSES}


def evaluate_scheduler_split(rows: list[dict[str, Any]], scheduler: dict[str, Any], split: str) -> dict[str, Any]:
    clauses = clause_by_name()
    split_rows = [row for row in rows if (row.get("case") or {}).get("split") == split]
    generation_cost = 0
    remat_cost = 0
    false_before_good = 0
    first_selected: dict[str, Any] | None = None
    first_selected_clause: str | None = None
    first_good: dict[str, Any] | None = None
    first_good_clause: str | None = None
    first_good_total: int | None = None
    selected_counts: dict[str, int] = {}
    evaluated_counts: dict[str, int] = {}
    strict_counts: dict[str, int] = {}
    good_counts: dict[str, int] = {}
    duplicate_seen: set[tuple[str, int, str]] = set()
    for clause_name in scheduler.get("clause_names") or []:
        clause = clauses[str(clause_name)]
        selected = sorted([row for row in split_rows if matches_clause(row, clause)], key=row_order_key)
        selected_counts[str(clause_name)] = len(selected)
        strict_counts[str(clause_name)] = len([row for row in selected if row.get("strict_below_rho")])
        good_counts[str(clause_name)] = len([row for row in selected if is_good(row)])
        for row in selected:
            case = row.get("case") or {}
            # A row can match multiple clauses; charge it once in this direct enumeration.
            key = (str(case.get("split")), int_value(case.get("split_stream_ordinal")), str(case.get("selector")))
            if key in duplicate_seen:
                continue
            duplicate_seen.add(key)
            evaluated_counts[str(clause_name)] = evaluated_counts.get(str(clause_name), 0) + 1
            generation_cost += 1
            remat_cost += max(1, int_value(row.get("generator_case_cost_ops"), 1))
            total = generation_cost + remat_cost
            if first_selected is None:
                first_selected = row
                first_selected_clause = str(clause_name)
            if is_good(row):
                first_good = row
                first_good_clause = str(clause_name)
                first_good_total = total
                break
            false_before_good += 1
        if first_good is not None:
            break
    total_cost = generation_cost + remat_cost
    return {
        "evaluated_counts_by_clause": evaluated_counts,
        "false_before_first_good": false_before_good,
        "first_good_stop": compact_row(first_good, first_good_total, first_good_clause),
        "first_selected": compact_row(first_selected, None, first_selected_clause),
        "generation_cost_ops": generation_cost,
        "good_counts_by_clause": good_counts,
        "margin_pass": bool(first_good and first_good_total is not None and first_good_total <= MARGIN_TARGET_OPS),
        "rematerialization_cost_ops": remat_cost,
        "selected_counts_by_clause": selected_counts,
        "split": split,
        "strict_boundary_pass": bool(first_good and first_good_total is not None and first_good_total <= STRICT_TARGET_OPS),
        "strict_counts_by_clause": strict_counts,
        "total_cost_ops": total_cost,
        "total_cost_over_rho": ratio(total_cost, RHO_ESTIMATE),
    }


def evaluate_scheduler(rows: list[dict[str, Any]], scheduler: dict[str, Any]) -> dict[str, Any]:
    by_split = {split: evaluate_scheduler_split(rows, scheduler, split) for split in SPLITS}
    good_stops = [item.get("first_good_stop") for item in by_split.values() if item.get("first_good_stop")]
    distinct_good = {
        row_set_key({"case": stop, "strict_below_rho": True, "public_key_verified": True})
        for stop in good_stops
    }
    return {
        "all_splits_have_good_stop": all(bool(item.get("first_good_stop")) for item in by_split.values()),
        "all_splits_margin_pass": all(bool(item.get("margin_pass")) for item in by_split.values()),
        "by_split": by_split,
        "clause_names": scheduler.get("clause_names") or [],
        "distinct_first_good_stop_count": len(distinct_good),
        "name": scheduler.get("name"),
    }


def determine_claim(evaluated: list[dict[str, Any]]) -> str:
    primary = next(item for item in evaluated if item.get("name") == "p905_c8gap8_then_c90_then_c19")
    if primary.get("all_splits_margin_pass"):
        return "P905_REGIME_SWITCH_SYNTHESIS_PASS_NEEDS_FRESH_HOLDOUT"
    if primary.get("all_splits_have_good_stop"):
        return "P905_REGIME_SWITCH_SYNTHESIS_SIGNAL_COST_NEGATIVE"
    if any(item.get("all_splits_margin_pass") for item in evaluated):
        return "P905_ALT_REGIME_SWITCH_SYNTHESIS_PASS_NEEDS_FRESH_HOLDOUT"
    return "NEGATIVE_RESULT_P905_REGIME_SWITCH_MISSES_SPLIT"


def split_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for split in SPLITS:
        split_rows = [row for row in rows if (row.get("case") or {}).get("split") == split]
        out[split] = {
            "case_count": len(split_rows),
            "public_key_verified_count": len([row for row in split_rows if row.get("public_key_verified")]),
            "strict_count": len([row for row in split_rows if row.get("strict_below_rho")]),
            "verified_strict_count": len([row for row in split_rows if is_good(row)]),
        }
    return out


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows = load_rows()
    evaluated = [evaluate_scheduler(rows, scheduler) for scheduler in SCHEDULERS]
    primary = next(item for item in evaluated if item.get("name") == "p905_c8gap8_then_c90_then_c19")
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p903_source": str(P903_SOURCE),
            "p904_source": str(P904_SOURCE),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(evaluated),
        "clauses": CLAUSES,
        "created_at": now_iso(),
        "evaluated_schedulers": evaluated,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SYNTHESIS-NOT-FRESH: P905 uses P903/P904 outcomes to form the scheduler.",
            "PUBLIC-FEATURE-ONLY: clauses use source metadata, not verifier labels or derived secrets.",
            "DIRECT-GENERATOR ASSUMPTION: direct-family accounting assumes direct enumeration.",
            "RANK/DESCENT BOUNDARY: relation certificates, factor rank, and individual-log descent remain open.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p905_regime_switch_scheduler",
        "parameters": {
            "margin_target_ops": MARGIN_TARGET_OPS,
            "rho_estimate": RHO_ESTIMATE,
            "splits": list(SPLITS),
            "strict_target_ops": STRICT_TARGET_OPS,
            "target": TARGET,
        },
        "rank_descent_obligations": {
            "can_promote_to_descent": False,
            "factor_relation_rank_computed": False,
            "individual_log_descent_integrated": False,
            "obligation": (
                "Freeze the P905 scheduler before the next source window, then export relation "
                "certificates, compute target-eliminated factor rank, and test individual-log descent."
            ),
            "relation_equations_exported": False,
            "target_eliminated_rank_integrated": False,
        },
        "schema": SCHEMA,
        "summary": {
            "primary_scheduler": primary,
            "scheduler_count": len(evaluated),
            "split_summary": split_summary(rows),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "parameters": payload["parameters"],
                "summary": {
                    "primary_scheduler": payload["summary"]["primary_scheduler"],
                    "split_summary": payload["summary"]["split_summary"],
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
