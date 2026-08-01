#!/usr/bin/env python3
"""Drift-aware source-only scheduler for leaf-16 order-9887 relation routing.

The scheduler trains only on source-row metadata joined with verifier labels for
scoring.  Validation selection uses source metadata alone; direct below-rho
labels are reported only after selection.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p570_pre_hit_source_feature_scout as p570


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCES = [
    STATE_DIR / "low_term_total2_order9887_p566_leaf16_frozen_root_saved_source_20605_20616_probe.json",
    STATE_DIR / "low_term_total2_order9887_p567_leaf16_phase_route_source_20617_20628_probe.json",
    STATE_DIR / "low_term_total2_order9887_p568_leaf16_right207_volume_source_20629_20640_probe.json",
    STATE_DIR / "low_term_total2_order9887_p570_leaf16_pre_hit_source_20641_20652_probe.json",
    STATE_DIR / "low_term_total2_order9887_p571_leaf16_pre_hit_source_20653_20664_probe.json",
]
DEFAULT_TRAIN_GATES = [
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p566_order9887_leaf16_frozen_root_saved_20605_20616_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p567_order9887_phase_route_20617_20628_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p568_order9887_right207_volume_20629_20640_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p570_order9887_pre_hit_source_20641_20652_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p571_order9887_pre_hit_source_20653_20664_density_gate_probe.json",
]
DEFAULT_VALIDATION_SOURCE = STATE_DIR / "low_term_total2_order9887_p572_leaf16_drift_scheduler_source_20665_20676_probe.json"
DEFAULT_VALIDATION_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p572_order9887_drift_scheduler_20665_20676_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p572_drift_aware_pre_hit_scheduler_20665_20676_probe.json"


Feature = dict[str, Any]


TOKEN_FIELDS = [
    "base_selector",
    "leaf_signature",
    "policy_role",
    "right_anchor",
    "row_pair",
    "salt_left",
    "salt_right",
    "selected_leaf_count",
    "top_k",
    "transfer_mod12",
    "transfer_mod7",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


def block_label(path: Path) -> str:
    name = path.name
    p_match = re.search(r"_(p\d+)_", name)
    range_match = re.search(r"_(\d{5})_(\d{5})_", name)
    if p_match and range_match:
        return f"{p_match.group(1)}_{range_match.group(1)}_{range_match.group(2)}"
    if p_match:
        return p_match.group(1)
    return path.stem


def block_start(row: Feature) -> int:
    return int(row.get("transfer_index") or 0)


def parse_paths(raw: str | None, defaults: list[Path]) -> list[Path]:
    return p570.parse_paths(raw, defaults)


def load_blocks(source_paths: list[Path], gate_paths: list[Path]) -> list[dict[str, Any]]:
    if len(source_paths) != len(gate_paths):
        raise ValueError("train source and gate counts must match")
    blocks = []
    for source_path, gate_path in zip(source_paths, gate_paths):
        rows = p570.source_rows([source_path], p570.gate_labels([gate_path]), block_label(source_path))
        for row in rows:
            row["block_label"] = block_label(source_path)
        blocks.append(
            {
                "gate": gate_path,
                "label": block_label(source_path),
                "rows": rows,
                "source": source_path,
            }
        )
    blocks.sort(key=lambda block: min((block_start(row) for row in block["rows"]), default=0))
    return blocks


def row_tokens(row: Feature) -> list[str]:
    tokens = [f"{field}={row.get(field)}" for field in TOKEN_FIELDS]
    phase = row.get("transfer_mod12")
    mod7 = row.get("transfer_mod7")
    salt_right = row.get("salt_right")
    pair = row.get("row_pair")
    anchor = row.get("right_anchor")
    base = row.get("base_selector")
    role = row.get("policy_role")
    leaf = row.get("leaf_signature")
    tokens.extend(
        [
            f"phase_salt={phase}:{salt_right}",
            f"phase_mod7={phase}:{mod7}",
            f"phase_row_pair={phase}:{pair}",
            f"phase_anchor={phase}:{anchor}",
            f"phase_pair_anchor={phase}:{pair}:{anchor}",
            f"phase_pair_anchor_base={phase}:{pair}:{anchor}:{base}",
            f"phase_pair_role={phase}:{pair}:{role}",
            f"salt_anchor={salt_right}:{anchor}",
            f"row_pair_anchor={pair}:{anchor}",
            f"row_pair_leaf={pair}:{leaf}",
            f"mod7_salt={mod7}:{salt_right}",
        ]
    )
    return tokens


def dataset_summary(rows: list[Feature]) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    return {
        "case_count": len(rows),
        "direct_below_rho_verified_count": len(positives),
        "direct_verified_count": sum(1 for row in rows if row["direct_verified"]),
        "positive_block_counts": dict(Counter(str(row.get("block_label")) for row in positives).most_common()),
        "positive_phase_salt_counts": dict(
            Counter(f"{row.get('transfer_mod12')}:{row.get('salt_right')}" for row in positives).most_common()
        ),
        "positive_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in positives).items(), key=lambda item: int(item[0]))
        ),
        "source_artifact_counts": dict(Counter(str(row["source_artifact"]) for row in rows).most_common()),
    }


def block_weights(rows: list[Feature], decay: float) -> dict[str, float]:
    labels = sorted({str(row.get("block_label")) for row in rows})
    label_to_last = {
        label: max(int(row.get("transfer_index") or 0) for row in rows if str(row.get("block_label")) == label)
        for label in labels
    }
    ordered = [label for label, _last in sorted(label_to_last.items(), key=lambda item: item[1])]
    max_index = len(ordered) - 1
    return {
        label: float(decay ** (max_index - index))
        for index, label in enumerate(ordered)
    }


def train_model(rows: list[Feature], decay: float, min_token_selected: int) -> dict[str, Any]:
    weights = block_weights(rows, decay)
    total_weight = 0.0
    positive_weight = 0.0
    token_stats: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {"positive_n": 0, "positive_w": 0.0, "selected_n": 0, "selected_w": 0.0}
    )
    for row in rows:
        weight = weights.get(str(row.get("block_label")), 1.0)
        total_weight += weight
        positive = bool(row["direct_below_rho_verified"])
        if positive:
            positive_weight += weight
        for token in row_tokens(row):
            stats = token_stats[token]
            stats["selected_n"] = int(stats["selected_n"]) + 1
            stats["selected_w"] = float(stats["selected_w"]) + weight
            if positive:
                stats["positive_n"] = int(stats["positive_n"]) + 1
                stats["positive_w"] = float(stats["positive_w"]) + weight
    base_rate = (positive_weight + 0.5) / (total_weight + 1.0) if total_weight else 0.0
    scored_tokens = {}
    for token, stats in token_stats.items():
        selected_n = int(stats["selected_n"])
        positive_n = int(stats["positive_n"])
        if selected_n < min_token_selected or not positive_n:
            continue
        selected_w = float(stats["selected_w"])
        positive_w = float(stats["positive_w"])
        precision = (positive_w + 0.25) / (selected_w + 0.5)
        lift = precision / max(base_rate, 1e-12)
        evidence = math.sqrt(max(positive_w, 0.0))
        scored_tokens[token] = {
            **stats,
            "contribution": round(math.log(max(lift, 1e-12)) * evidence, 8),
            "lift": round(lift, 8),
            "precision": round(precision, 8),
        }
    return {
        "base_rate": round(base_rate, 8),
        "block_weights": weights,
        "decay": decay,
        "min_token_selected": min_token_selected,
        "scored_tokens": scored_tokens,
        "top_tokens": top_tokens(scored_tokens, 30),
    }


def top_tokens(scored_tokens: dict[str, dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    rows = [
        {"token": token, **stats}
        for token, stats in scored_tokens.items()
        if float(stats.get("contribution") or 0.0) > 0.0
    ]
    rows.sort(
        key=lambda item: (
            -float(item.get("contribution") or 0.0),
            -float(item.get("precision") or 0.0),
            -int(item.get("positive_n") or 0),
            str(item.get("token")),
        )
    )
    return rows[:limit]


def score_row(row: Feature, model: dict[str, Any]) -> dict[str, Any]:
    scored_tokens = model["scored_tokens"]
    evidence = []
    score = 0.0
    for token in row_tokens(row):
        stats = scored_tokens.get(token)
        if not stats:
            continue
        contribution = float(stats.get("contribution") or 0.0)
        if contribution <= 0.0:
            continue
        score += contribution
        evidence.append(
            {
                "contribution": round(contribution, 8),
                "lift": stats.get("lift"),
                "positive_n": stats.get("positive_n"),
                "precision": stats.get("precision"),
                "selected_n": stats.get("selected_n"),
                "token": token,
            }
        )
    evidence.sort(key=lambda item: (-float(item["contribution"]), str(item["token"])))
    return {"evidence_tokens": evidence[:8], "source_score": round(score, 8)}


def compact_row(row: Feature, scored: dict[str, Any] | None = None) -> dict[str, Any]:
    out = p570.compact_row(row)
    if scored:
        out["evidence_tokens"] = scored.get("evidence_tokens")
        out["source_score"] = scored.get("source_score")
    return out


def schedule_rows(rows: list[Feature], model: dict[str, Any], budget: int) -> list[dict[str, Any]]:
    scored = []
    for row in rows:
        score = score_row(row, model)
        if float(score["source_score"]) <= 0.0:
            continue
        scored.append({"row": row, **score})
    scored.sort(
        key=lambda item: (
            -float(item["source_score"]),
            int(item["row"].get("transfer_index") or 0),
            str(item["row"].get("row_pair")),
            int(item["row"].get("right_anchor") or 0),
            str(item["row"].get("base_selector")),
        )
    )
    return scored[:budget]


def selection_report(rows: list[Feature], selected: list[dict[str, Any]], label: str) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    selected_rows = [item["row"] for item in selected]
    selected_positive = [item for item in selected if item["row"]["direct_below_rho_verified"]]
    selected_verified = [item for item in selected if item["row"]["direct_verified"]]
    return {
        "direct_below_rho_verified_count": len(selected_positive),
        "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
        "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
        "direct_verified_count": len(selected_verified),
        "examples": [compact_row(item["row"], item) for item in selected[:12]],
        "label": label,
        "positive_examples": [compact_row(item["row"], item) for item in selected_positive[:12]],
        "raw_positive_count": len(positives),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected_rows).most_common(16)),
        "selected_case_entries": [item["row"]["case_entry"] for item in selected],
        "selected_direct_below_rho_verified_case_entries": [item["row"]["case_entry"] for item in selected_positive],
        "selected_count": len(selected),
        "selected_fraction": ratio(len(selected), len(rows)),
        "transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in selected_rows).items(), key=lambda item: int(item[0]))
        ),
    }


def evaluate_model(rows: list[Feature], model: dict[str, Any], primary_budget: int, priority_budget: int) -> dict[str, Any]:
    priority = schedule_rows(rows, model, priority_budget)
    primary = schedule_rows(rows, model, primary_budget)
    return {
        "primary": selection_report(rows, primary, f"top_{primary_budget}_source_score"),
        "priority": selection_report(rows, priority, f"top_{priority_budget}_source_score"),
    }


def leave_one_block_out(blocks: list[dict[str, Any]], decay: float, min_token_selected: int, primary_budget: int, priority_budget: int) -> list[dict[str, Any]]:
    reports = []
    for heldout in blocks:
        train_rows = [row for block in blocks if block is not heldout for row in block["rows"]]
        model = train_model(train_rows, decay, min_token_selected)
        reports.append(
            {
                "heldout_block": heldout["label"],
                "heldout_source": str(heldout["source"]),
                "heldout_dataset": dataset_summary(heldout["rows"]),
                "score_reports": evaluate_model(heldout["rows"], model, primary_budget, priority_budget),
                "training_dataset": dataset_summary(train_rows),
            }
        )
    return reports


def rolling_validation(blocks: list[dict[str, Any]], decay: float, min_token_selected: int, primary_budget: int, priority_budget: int) -> list[dict[str, Any]]:
    reports = []
    for index, heldout in enumerate(blocks[1:], start=1):
        prior_blocks = blocks[:index]
        train_rows = [row for block in prior_blocks for row in block["rows"]]
        model = train_model(train_rows, decay, min_token_selected)
        reports.append(
            {
                "heldout_block": heldout["label"],
                "heldout_source": str(heldout["source"]),
                "heldout_dataset": dataset_summary(heldout["rows"]),
                "score_reports": evaluate_model(heldout["rows"], model, primary_budget, priority_budget),
                "training_blocks": [block["label"] for block in prior_blocks],
                "training_dataset": dataset_summary(train_rows),
            }
        )
    return reports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-sources", default=None)
    parser.add_argument("--train-gates", default=None)
    parser.add_argument("--validation-source", type=Path, default=DEFAULT_VALIDATION_SOURCE)
    parser.add_argument("--validation-gate", type=Path, default=DEFAULT_VALIDATION_GATE)
    parser.add_argument("--primary-budget", type=int, default=186)
    parser.add_argument("--priority-budget", type=int, default=24)
    parser.add_argument("--decay", type=float, default=0.55)
    parser.add_argument("--min-token-selected", type=int, default=4)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_sources = parse_paths(args.train_sources, DEFAULT_TRAIN_SOURCES)
    train_gates = parse_paths(args.train_gates, DEFAULT_TRAIN_GATES)
    blocks = load_blocks(train_sources, train_gates)
    train_rows = [row for block in blocks for row in block["rows"]]
    validation_rows = p570.source_rows(
        [args.validation_source],
        p570.gate_labels([args.validation_gate]),
        "validation",
    )
    for row in validation_rows:
        row["block_label"] = block_label(args.validation_source)
    model = train_model(train_rows, args.decay, args.min_token_selected)
    validation_reports = evaluate_model(validation_rows, model, args.primary_budget, args.priority_budget)
    primary = validation_reports["primary"]
    payload = {
        "artifacts": {
            "train_gates": [str(path) for path in train_gates],
            "train_sources": [str(path) for path in train_sources],
            "validation_gate": str(args.validation_gate),
            "validation_source": str(args.validation_source),
        },
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: source scores use transfer, row-pair, salt, anchor, leaf, selector, and policy metadata only.",
            "LABEL BOUNDARY: verifier outcomes and rho comparisons are used only for training/evaluation labels, not for validation-row selection.",
            "HEURISTIC: recency weighting responds to observed route drift and is not a theorem about future transfer phases.",
            "NO SPEEDUP CLAIM: this is a source scheduler before relation collection, sparse linear algebra, and arbitrary target descent are closed.",
        ],
        "leave_one_block_out": leave_one_block_out(
            blocks,
            args.decay,
            args.min_token_selected,
            args.primary_budget,
            args.priority_budget,
        ),
        "method": "p572_drift_aware_pre_hit_source_scheduler",
        "model": {
            "base_rate": model["base_rate"],
            "block_weights": model["block_weights"],
            "decay": model["decay"],
            "min_token_selected": model["min_token_selected"],
            "top_tokens": model["top_tokens"],
        },
        "rolling_validation": rolling_validation(
            blocks,
            args.decay,
            args.min_token_selected,
            args.primary_budget,
            args.priority_budget,
        ),
        "schema": "ecdlp.low_term_total2_p572_drift_aware_pre_hit_scheduler.v1",
        "summary": {
            "claim_status": (
                "DRIFT_AWARE_SOURCE_SCHEDULER_VALIDATION_POSITIVE"
                if primary["direct_below_rho_verified_count"]
                else "NEGATIVE_RESULT_DRIFT_AWARE_SOURCE_SCHEDULER_NO_VALIDATION_POSITIVE"
            ),
            "primary_budget": args.primary_budget,
            "priority_budget": args.priority_budget,
            "training": dataset_summary(train_rows),
            "validation": {
                "dataset": dataset_summary(validation_rows),
                "primary": primary,
                "priority": validation_reports["priority"],
            },
        },
        "validation_score_reports": validation_reports,
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
