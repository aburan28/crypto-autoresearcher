#!/usr/bin/env python3
"""P876 target-local non-P867 motif clustering and held-out selector validation."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p869_p231_public_motif_predictor as p869
import low_term_total2_p872_p231_two_stage_materialization as p872
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p876_p231_target67_non_p867_motif_selector.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p876_p231_target67_non_p867_motif_selector_probe.json"
DEFAULT_TARGET = "67.a1@9803"
DEFAULT_TRAIN_WINDOWS = (
    "11288_11295",
    "11296_11303",
    "11304_11311",
    "11312_11319",
    "11320_11327",
    "11328_11335",
    "11336_11343",
)
DEFAULT_HELDOUT_WINDOWS = (
    "11344_11351",
    "11352_11359",
    "11360_11367",
    "11368_11375",
    "11376_11383",
    "11384_11391",
    "11392_11399",
)
SCHEMA = "ecdlp.low_term_total2_p876_p231_target67_non_p867_motif_selector.v1"


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def topk_gate(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) <= 12


def list_value(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def tuple_value(value: Any) -> tuple[Any, ...]:
    return tuple(list_value(value))


def compact_feature_row(features: dict[str, Any]) -> dict[str, Any]:
    return {
        "all_has_double_pair": features.get("all_has_double_pair"),
        "case_id": features.get("case_id"),
        "count_double_pair": features.get("count_double_pair"),
        "count_shape_2p2": features.get("count_shape_2p2"),
        "leaf_gap_tuple": list(tuple_value(features.get("leaf_gap_tuple"))),
        "leaf_selector": features.get("leaf_selector"),
        "leaf_selector_family": features.get("leaf_selector_family"),
        "missing_selected_feature_count": features.get("missing_selected_feature_count"),
        "salt_gap": features.get("salt_gap"),
        "selected_feature_count": features.get("selected_feature_count"),
        "selected_leaf_occurrence_count": features.get("selected_leaf_occurrence_count"),
        "top_k": features.get("top_k"),
        "transfer_index": features.get("transfer_index"),
        "unique_leaf_count": features.get("unique_leaf_count"),
        "unique_leaf_indices": list(tuple_value(features.get("unique_leaf_indices"))),
        "window": features.get("window"),
    }


def compact_case(row: dict[str, Any], features: dict[str, Any], candidates: list[str] | None = None) -> dict[str, Any]:
    compact = p868.compact_case(row)
    compact["public_features"] = compact_feature_row(features)
    compact["direct_ops"] = row.get("direct_ops")
    compact["generic_rho_steps"] = row.get("generic_rho_steps")
    compact["p867_motif_verified_below_rho"] = bool(row.get("p867_motif_verified_below_rho"))
    compact["reconstructed_error_count"] = int_value(row.get("reconstructed_error_count"))
    compact["matched_candidate_rules"] = candidates or []
    compact["matched_non_p867_same_tail_derivations"] = [
        {
            "exact_tail_expression_key": item.get("exact_tail_expression_key"),
            "motif": item.get("motif"),
            "row_keys": item.get("row_keys"),
        }
        for item in matched_non_p867_derivations(row)
    ][:8]
    return compact


def source_paths(windows: list[str]) -> dict[str, Path]:
    return {window: p868.source_path(window) for window in windows}


def feature_for_case(case: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    features = p869.public_features(case, context)
    selected_feature_count = len(p869.selected_public_features(case, context))
    features["selected_feature_count"] = selected_feature_count
    features["missing_selected_feature_count"] = max(
        0,
        int_value(features.get("selected_leaf_occurrence_count")) - selected_feature_count,
    )
    return features


@dataclass(frozen=True)
class CandidateRule:
    name: str
    kind: str
    values: tuple[Any, ...]

    def matches(self, features: dict[str, Any]) -> bool:
        family = str(features.get("leaf_selector_family"))
        selector = str(features.get("leaf_selector"))
        top_k = int_value(features.get("top_k"))
        occurrence = int_value(features.get("selected_leaf_occurrence_count"))
        unique = int_value(features.get("unique_leaf_count"))
        gap = tuple_value(features.get("leaf_gap_tuple"))
        if self.kind == "selector_topk_gap":
            return (selector, top_k, gap) == self.values
        if self.kind == "family_topk_gap":
            return (family, top_k, gap) == self.values
        if self.kind == "family_topk_occurrence":
            return (family, top_k, occurrence) == self.values
        if self.kind == "family_occurrence_gap":
            return (family, occurrence, gap) == self.values
        if self.kind == "family_unique_gap":
            return (family, unique, gap) == self.values
        if self.kind == "selector_topk":
            return (selector, top_k) == self.values
        if self.kind == "family_topk":
            return (family, top_k) == self.values
        return False

    def to_json(self) -> dict[str, Any]:
        return {"kind": self.kind, "name": self.name, "values": list(self.values)}


def candidate_rules_from_positive(features: dict[str, Any]) -> list[CandidateRule]:
    family = str(features.get("leaf_selector_family"))
    selector = str(features.get("leaf_selector"))
    top_k = int_value(features.get("top_k"))
    occurrence = int_value(features.get("selected_leaf_occurrence_count"))
    unique = int_value(features.get("unique_leaf_count"))
    gap = tuple_value(features.get("leaf_gap_tuple"))
    specs = [
        ("selector_topk_gap", (selector, top_k, gap)),
        ("family_topk_gap", (family, top_k, gap)),
        ("family_topk_occurrence", (family, top_k, occurrence)),
        ("family_occurrence_gap", (family, occurrence, gap)),
        ("family_unique_gap", (family, unique, gap)),
        ("selector_topk", (selector, top_k)),
        ("family_topk", (family, top_k)),
    ]
    rules = []
    for kind, values in specs:
        value_text = ",".join(p868.json_key(value) if isinstance(value, tuple) else str(value) for value in values)
        rules.append(CandidateRule(name=f"{kind}:{value_text}", kind=kind, values=values))
    return rules


def unique_rules(rules: list[CandidateRule]) -> list[CandidateRule]:
    seen = set()
    result = []
    for rule in rules:
        key = (rule.kind, p868.json_key(rule.values))
        if key in seen:
            continue
        seen.add(key)
        result.append(rule)
    return result


def matched_non_p867_derivations(case: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in case.get("same_tail_derivations") or []
        if item.get("matches_expected_secret") and not item.get("is_p867_motif")
    ]


def is_non_p867_below_rho(case: dict[str, Any]) -> bool:
    ratio = case.get("direct_ops_over_rho")
    return bool(
        case.get("union_public_key_verified")
        and ratio is not None
        and float(ratio) < 1.0
        and int_value(case.get("p867_motif_matched_derivation_count")) == 0
    )


def build_rows(
    windows: list[str],
    target: str,
    select_public: Callable[[dict[str, Any]], bool],
    reconstruct: bool,
    selected_rule_names: Callable[[dict[str, Any]], list[str]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, str]]:
    paths = source_paths(windows)
    source_counts: Counter[str] = Counter()
    rows: list[dict[str, Any]] = []
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    for window in windows:
        source = p868.load_json(paths[window])
        params = repair_probe.source_parameters(source)
        probe_args = repair_probe.probe_args_from_source(source)
        cache_key = p868.json_key(
            {
                "bank_source": params.get("bank_source"),
                "config_source": params.get("config_source"),
                "direct_source": params.get("direct_source"),
                "radius": params.get("radius"),
                "transfer_source": params.get("transfer_source"),
            }
        )
        if cache_key not in build_cache:
            build_cache[cache_key] = (*repair_probe.build_specs(params), probe_args)
        verifier, records, config_source, specs_by_target, probe_args = build_cache[cache_key]

        for case in p868.iter_source_cases(source, window, {target}):
            source_counts[window] += 1
            context = hit_stream_probe.scan_case_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                case,
                probe_args,
                context_cache,
            )
            features = feature_for_case(case, context)
            if not select_public(features):
                continue
            labeled = (
                p868.analyze_case(
                    verifier,
                    records,
                    config_source,
                    specs_by_target,
                    probe_args,
                    context_cache,
                    case,
                )
                if reconstruct
                else None
            )
            rows.append(
                {
                    "case": labeled,
                    "features": features,
                    "matched_rule_names": selected_rule_names(features) if selected_rule_names else [],
                    "source_case": case,
                    "window": window,
                }
            )
    return rows, dict(source_counts), {window: str(path) for window, path in paths.items()}


def evaluate_rules(rules: list[CandidateRule], train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positives = [row for row in train_rows if row["case"] and is_non_p867_below_rho(row["case"])]
    results = []
    for rule in rules:
        selected = [row for row in train_rows if rule.matches(row["features"])]
        true_pos = [row for row in selected if row["case"] and is_non_p867_below_rho(row["case"])]
        results.append(
            {
                **rule.to_json(),
                "train_false_positive_count": len(selected) - len(true_pos),
                "train_precision": safe_ratio(len(true_pos), len(selected)),
                "train_recall": safe_ratio(len(true_pos), len(positives)),
                "train_selected_count": len(selected),
                "train_true_positive_count": len(true_pos),
            }
        )
    return sorted(
        results,
        key=lambda row: (
            -(row.get("train_precision") or 0.0),
            -int_value(row.get("train_true_positive_count")),
            int_value(row.get("train_selected_count")),
            str(row.get("name")),
        ),
    )


def rule_from_json(row: dict[str, Any]) -> CandidateRule:
    values = []
    for value in row.get("values") or []:
        if isinstance(value, list):
            values.append(tuple(value))
        else:
            values.append(value)
    return CandidateRule(name=str(row.get("name")), kind=str(row.get("kind")), values=tuple(values))


def promote_rules(rule_metrics: list[dict[str, Any]]) -> list[CandidateRule]:
    promoted = [
        row
        for row in rule_metrics
        if int_value(row.get("train_true_positive_count")) > 0
        and (row.get("train_precision") or 0.0) >= 0.25
        and int_value(row.get("train_selected_count")) <= 24
    ]
    if not promoted:
        promoted = [row for row in rule_metrics if int_value(row.get("train_true_positive_count")) > 0][:12]
    return [rule_from_json(row) for row in promoted[:16]]


def motif_clusters(rows: list[dict[str, Any]]) -> dict[str, Any]:
    motif_counter: Counter[str] = Counter()
    exact_counter: Counter[str] = Counter()
    examples: dict[str, dict[str, Any]] = {}
    for row in rows:
        case = row["case"]
        if not case:
            continue
        for derivation in matched_non_p867_derivations(case):
            motif_key = p868.json_key(derivation.get("motif"))
            exact_key = str(derivation.get("exact_tail_expression_key"))
            motif_counter[motif_key] += 1
            exact_counter[exact_key] += 1
            examples.setdefault(
                exact_key,
                {
                    "case_id": case.get("case_id"),
                    "direct_ops_over_rho": case.get("direct_ops_over_rho"),
                    "exact_tail_expression_key": exact_key,
                    "motif": derivation.get("motif"),
                    "public_features": compact_feature_row(row["features"]),
                    "row_keys": derivation.get("row_keys"),
                    "transfer_index": case.get("transfer_index"),
                    "window": case.get("window"),
                },
            )
    return {
        "exact_cluster_count": len(exact_counter),
        "exact_clusters": [
            {"count": count, "example": examples.get(key), "exact_tail_expression_key": key}
            for key, count in exact_counter.most_common()
        ],
        "motif_cluster_count": len(motif_counter),
        "motif_clusters": [
            {"count": count, "motif": json.loads(key)}
            for key, count in motif_counter.most_common()
        ],
    }


def summarize_labeled(rows: list[dict[str, Any]], source_counts: dict[str, int]) -> dict[str, Any]:
    cases = [row["case"] for row in rows if row.get("case")]
    union_verified = [case for case in cases if case.get("union_public_key_verified")]
    below = [
        case
        for case in union_verified
        if case.get("direct_ops_over_rho") is not None and float(case["direct_ops_over_rho"]) < 1.0
    ]
    non_p867 = [case for case in below if int_value(case.get("p867_motif_matched_derivation_count")) == 0]
    p867 = [case for case in below if int_value(case.get("p867_motif_matched_derivation_count")) > 0]
    return {
        "below_rho_union_case_count": len(below),
        "p867_below_rho_case_count": len(p867),
        "public_selected_case_count": len(rows),
        "reconstructed_case_count": len(cases),
        "reconstruction_error_count": sum(int_value(case.get("reconstructed_error_count")) for case in cases),
        "selected_count_by_window": dict(Counter(str(row.get("window")) for row in rows)),
        "selected_fraction": safe_ratio(len(rows), sum(source_counts.values())),
        "source_case_count": sum(source_counts.values()),
        "source_count_by_window": source_counts,
        "target_local_non_p867_below_rho_case_count": len(non_p867),
        "union_public_key_verified_case_count": len(union_verified),
    }


def recurrence_count(heldout_rows: list[dict[str, Any]], train_exact_keys: set[str]) -> int:
    count = 0
    for row in heldout_rows:
        case = row.get("case")
        if not case or not is_non_p867_below_rho(case):
            continue
        if any(str(item.get("exact_tail_expression_key")) in train_exact_keys for item in matched_non_p867_derivations(case)):
            count += 1
    return count


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("heldout_below_rho_union_case_count")) > 0 and int_value(
        summary.get("heldout_train_exact_recurrence_case_count")
    ) > 0:
        return "P876_TARGET67_PUBLIC_SIGNATURE_SELECTS_HELDOUT_RECURRENT_NON_P867_BELOW_RHO"
    if int_value(summary.get("heldout_below_rho_union_case_count")) > 0:
        return "P876_TARGET67_PUBLIC_SIGNATURE_SELECTS_HELDOUT_NON_P867_BELOW_RHO"
    if int_value(summary.get("heldout_public_selected_case_count")) > 0:
        return "NEGATIVE_RESULT_P876_PUBLIC_SIGNATURES_SELECT_HELDOUT_WITHOUT_BELOW_RHO"
    return "NEGATIVE_RESULT_P876_PUBLIC_SIGNATURES_SELECT_ZERO_HELDOUT_CASES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    target = args.target
    train_windows = list(args.train_windows)
    heldout_windows = list(args.heldout_windows)

    train_rows, train_source_counts, train_sources = build_rows(
        train_windows,
        target,
        topk_gate,
        reconstruct=True,
    )
    train_positive_rows = [row for row in train_rows if row["case"] and is_non_p867_below_rho(row["case"])]
    train_clusters = motif_clusters(train_positive_rows)
    candidate_rules = unique_rules(
        [rule for row in train_positive_rows for rule in candidate_rules_from_positive(row["features"])]
    )
    rule_metrics = evaluate_rules(candidate_rules, train_rows)
    promoted_rules = promote_rules(rule_metrics)

    def heldout_names(features: dict[str, Any]) -> list[str]:
        return [rule.name for rule in promoted_rules if rule.matches(features)]

    heldout_rows, heldout_source_counts, heldout_sources = build_rows(
        heldout_windows,
        target,
        lambda features: bool(heldout_names(features)),
        reconstruct=True,
        selected_rule_names=heldout_names,
    )
    train_exact_keys = {
        str(cluster.get("exact_tail_expression_key"))
        for cluster in train_clusters.get("exact_clusters") or []
    }
    heldout_summary = summarize_labeled(heldout_rows, heldout_source_counts)
    train_summary = summarize_labeled(train_rows, train_source_counts)
    heldout_recurrence = recurrence_count(heldout_rows, train_exact_keys)

    summary = {
        "claim_status": None,
        "heldout_below_rho_union_case_count": heldout_summary["below_rho_union_case_count"],
        "heldout_public_selected_case_count": heldout_summary["public_selected_case_count"],
        "heldout_reconstructed_case_count": heldout_summary["reconstructed_case_count"],
        "heldout_reconstruction_error_count": heldout_summary["reconstruction_error_count"],
        "heldout_source_case_count": heldout_summary["source_case_count"],
        "heldout_target_local_non_p867_below_rho_case_count": heldout_summary[
            "target_local_non_p867_below_rho_case_count"
        ],
        "heldout_train_exact_recurrence_case_count": heldout_recurrence,
        "promoted_candidate_count": len(promoted_rules),
        "target": target,
        "train_below_rho_union_case_count": train_summary["below_rho_union_case_count"],
        "train_exact_cluster_count": train_clusters["exact_cluster_count"],
        "train_motif_cluster_count": train_clusters["motif_cluster_count"],
        "train_public_selected_case_count": train_summary["public_selected_case_count"],
        "train_reconstructed_case_count": train_summary["reconstructed_case_count"],
        "train_source_case_count": train_summary["source_case_count"],
        "train_target_local_non_p867_below_rho_case_count": train_summary[
            "target_local_non_p867_below_rho_case_count"
        ],
    }
    claim = determine_claim(summary)
    summary["claim_status"] = claim

    heldout_cases_sorted = sorted(
        heldout_rows,
        key=lambda row: (
            not bool(row["case"] and is_non_p867_below_rho(row["case"])),
            float((row["case"] or {}).get("direct_ops_over_rho") or 10**18),
            str(row["features"].get("case_id")),
        ),
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "heldout_source_windows": heldout_sources,
            "train_source_windows": train_sources,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P876_") else "NEGATIVE RESULT",
        "created_at": p872.now_iso(),
        "heldout_selected_cases": [
            compact_case(row["case"], row["features"], row["matched_rule_names"])
            for row in heldout_cases_sorted
            if row.get("case")
        ],
        "heldout_summary": heldout_summary,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "TARGET-LOCAL BOUNDARY: P876 trains and validates only on 67.a1@9803 inside p231 fixed-row artifacts.",
            "SELECTOR BOUNDARY: held-out selection uses public features only.",
            "MOTIF BOUNDARY: same-tail motifs are diagnostic until they support a reusable target-descent mechanism.",
            "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p876_p231_target67_non_p867_motif_selector",
        "parameters": {
            "base_gate": "top_k <= 12",
            "heldout_windows": heldout_windows,
            "target": target,
            "train_windows": train_windows,
        },
        "promoted_candidate_rules": [rule.to_json() for rule in promoted_rules],
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "Training labels are limited to P875 train windows.",
                "Held-out rules are fixed before held-out relation reconstruction.",
                "Only selected held-out cases are reconstructed, so recall over unselected cases remains unknown.",
            ],
            "claim_or_task": "Cluster P875 non-P867 motifs and validate target-local public signatures on held-out 67.a1@9803 windows.",
            "evidence_so_far": [
                f"Train non-P867 below-rho cases: {summary['train_target_local_non_p867_below_rho_case_count']}.",
                f"Promoted public rules: {summary['promoted_candidate_count']}.",
                f"Held-out below-rho cases: {summary['heldout_below_rho_union_case_count']}.",
            ],
            "failure_modes": [
                "Candidate rules may overfit the seven P875 positives.",
                "Held-out positives may use different exact same-tail motifs.",
                "Same-p231-family results may not transfer to larger prime-field targets.",
            ],
            "next_concrete_action": (
                "If held-out positive, build P877 to isolate the best public selector and run a second disjoint held-out window; otherwise widen motif-public-feature candidates."
            ),
            "status": "OBSERVATION" if claim.startswith("P876_") else "NEGATIVE RESULT",
        },
        "rule_metrics": rule_metrics,
        "schema": SCHEMA,
        "summary": summary,
        "train_motif_clusters": train_clusters,
        "train_summary": train_summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--heldout-windows", nargs="+", default=list(DEFAULT_HELDOUT_WINDOWS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--train-windows", nargs="+", default=list(DEFAULT_TRAIN_WINDOWS))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    p872.write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
