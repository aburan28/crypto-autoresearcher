#!/usr/bin/env python3
"""P1029 scout for neighboring total-2 motifs after the leaf-19 quotient negative."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1026_p231_affine_rhs_obstruction_audit as p1026
import low_term_total2_p1028_p231_relation_class_split_audit as p1028


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1029_p231_motif_neighbor_scout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1029_p231_motif_neighbor_scout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1029_p231_motif_neighbor_scout.v1"
ORDER = p1026.ORDER
LEAF19_KEY = "[19]"
SCOUT_SELECTOR = "mode_cost_hybrid_support_monic_b_total2"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def round8(value: float | None) -> float | None:
    return p1023.round8(value)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def source_rank(row: dict[str, Any]) -> int:
    return int_value(source_case(row).get("source_rank"))


def source_ops_over_rho(row: dict[str, Any]) -> float:
    try:
        return float(source_case(row).get("source_ops_over_rho") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def salt_gap(row: dict[str, Any]) -> int:
    return int_value(features(row).get("salt_gap"))


def top_k(row: dict[str, Any]) -> int:
    return int_value(features(row).get("top_k"))


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    values = features(row).get("unique_leaf_indices") or []
    return tuple(int_value(value) for value in values)


def leaf_key(row: dict[str, Any]) -> str:
    return json_key(list(leaf_tuple(row)))


def split_for_window(window: str) -> str:
    if window in p1022.POSITIVE_CALIBRATION_WINDOWS or window in p1022.VALIDATION_WINDOWS:
        return "training_seed"
    if window in p1022.NEGATIVE_CALIBRATION_WINDOWS:
        return "negative_control"
    if window in p1025.FRESH_WINDOWS:
        return "fresh_validation"
    return "unknown"


def split_set(form: dict[str, Any]) -> set[str]:
    return p1025.split_set(form)


def scout_predicate(row: dict[str, Any]) -> bool:
    return bool(
        features(row).get("leaf_selector") == SCOUT_SELECTOR
        and salt_gap(row) >= 3
        and source_ops_over_rho(row) >= 0.7
        and source_rank(row) >= 2
    )


def annotate_row(row: dict[str, Any], window: str, split: str) -> dict[str, Any]:
    out = dict(row)
    out["_p1023_window"] = window
    out["_p1023_split"] = split
    out["_p1029_leaf_key"] = leaf_key(row)
    return out


def row_signature(row: dict[str, Any]) -> str:
    return json_key(p1005.p996.row_key_signature(row))


def dedupe_by_row_signature(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row_signature(row)
        current = best.get(key)
        if current is None or top_k(row) < top_k(current):
            best[key] = row
    return [best[key] for key in sorted(best)]


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": row.get("case_id"),
        "label_positive": bool(row.get("label_positive")),
        "leaf_key": row.get("_p1029_leaf_key") or leaf_key(row),
        "row_key_signature": p1005.p996.row_key_signature(row),
        "salt_gap": salt_gap(row),
        "selected_ops_over_rho": round8(source_ops_over_rho(row)),
        "source_rank": source_rank(row),
        "split": row.get("_p1023_split"),
        "top_k": top_k(row),
        "window": row.get("_p1023_window") or row.get("window"),
    }


def selection_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positives = sum(1 for row in rows if bool(row.get("label_positive")))
    false = len(rows) - positives
    by_split = Counter(str(row.get("_p1023_split")) for row in rows)
    by_topk = Counter(str(top_k(row)) for row in rows)
    by_window = Counter(str(row.get("_p1023_window") or row.get("window")) for row in rows)
    fresh = [row for row in rows if row.get("_p1023_split") == "fresh_validation"]
    negative = [row for row in rows if row.get("_p1023_split") == "negative_control"]
    return {
        "false_count": false,
        "fresh_false_count": sum(1 for row in fresh if not bool(row.get("label_positive"))),
        "fresh_positive_count": sum(1 for row in fresh if bool(row.get("label_positive"))),
        "fresh_selected_count": len(fresh),
        "negative_control_selected_count": len(negative),
        "positive_count": positives,
        "precision": round8(positives / len(rows)) if rows else None,
        "selected_count": len(rows),
        "selected_ops_over_rho": round8(sum(source_ops_over_rho(row) for row in rows)),
        "split_counts": dict(sorted(by_split.items())),
        "top_k_counts": dict(sorted(by_topk.items(), key=lambda item: int_value(item[0]))),
        "unique_case_count": len({str(row.get("case_id")) for row in rows}),
        "unique_row_signature_count": len({row_signature(row) for row in rows}),
        "window_counts": dict(sorted(by_window.items())),
    }


def quotient_summary(forms: list[dict[str, Any]], order: int) -> dict[str, Any]:
    forms_by_public: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        forms_by_public[str(form.get("public_fingerprint"))].append(form)
    relations: list[dict[str, Any]] = []
    factor_count = 0
    public_summaries = []
    for public, group in sorted(forms_by_public.items()):
        group_relations, group_factor_count = p1026.target_relations_for_group(public, group, order)
        factor_count = max(factor_count, group_factor_count)
        nontrivial = [
            relation
            for relation in group_relations
            if relation.get("relation_status") == "TARGET_ELIMINATED_FACTOR_RELATION"
        ]
        relations.extend(nontrivial)
        public_summaries.append(
            {
                "form_count": len(group),
                "nontrivial_relation_count": len(nontrivial),
                "public_fingerprint": public,
                "unique_form_count": len(p1023.unique_forms(group)),
            }
        )
    matrix = p1028.matrix_summary(relations, factor_count) if factor_count else p1028.matrix_summary([], 0)
    return {
        "factor_count": factor_count,
        "matrix": matrix,
        "public_summaries": public_summaries,
        "relation_count": len(relations),
    }


def reconstruct_summary(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
    if not rows:
        return {
            "form_orders": [],
            "label": label,
            "quotient": quotient_summary([], 0),
            "raw_rank": p1023.rank_summary([], 0),
            "reconstructed_case_count": 0,
            "reconstruction_error_count": 0,
        }
    reconstructed, forms = p1025.reconstruct_partition(rows)
    form_orders = sorted({int_value(form.get("order")) for form in forms if int_value(form.get("order"))})
    order = form_orders[0] if form_orders == [ORDER] else 0
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed)
    return {
        "form_orders": form_orders,
        "label": label,
        "quotient": quotient_summary(forms, order) if order else quotient_summary([], 0),
        "raw_rank": p1023.rank_summary(forms, order) if order else p1023.rank_summary(forms, 0),
        "reconstructed_case_count": len(reconstructed),
        "reconstruction_error_count": reconstruction_error_count,
    }


def motif_summary(leaf: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    compressed = dedupe_by_row_signature(rows)
    raw_reconstruction = reconstruct_summary(rows, "case_level")
    compressed_reconstruction = reconstruct_summary(compressed, "row_signature_compressed")
    return {
        "leaf_key": leaf,
        "case_level_reconstruction": raw_reconstruction,
        "compressed_rows": [compact_row(row) for row in compressed[:16]],
        "row_signature_compressed_reconstruction": compressed_reconstruction,
        "sample_rows": [compact_row(row) for row in rows[:24]],
        "selection": selection_summary(rows),
    }


def reference_rows(
    windows: list[str],
    by_window: dict[str, list[dict[str, Any]]],
    split: str,
) -> list[dict[str, Any]]:
    return p1025.selected_rows_for_many(windows, by_window, split)


def determine_claim(reference: dict[str, Any], motifs: list[dict[str, Any]]) -> str:
    reference_selection = reference["selection"]
    if reference_selection["negative_control_selected_count"] or reference_selection["false_count"]:
        return "NEGATIVE_RESULT_P1029_REFERENCE_CONTROL_FAILED"
    neighbors = [motif for motif in motifs if motif["leaf_key"] != LEAF19_KEY]
    if not neighbors:
        return "NEGATIVE_RESULT_P1029_NO_NON19_NEIGHBOR_MOTIFS"
    clean_neighbors = [
        motif
        for motif in neighbors
        if not motif["selection"]["fresh_false_count"]
        and not motif["selection"]["negative_control_selected_count"]
        and motif["selection"]["fresh_positive_count"]
    ]
    consistent_neighbors = []
    for motif in clean_neighbors:
        raw = motif["row_signature_compressed_reconstruction"]["raw_rank"]
        quotient = motif["row_signature_compressed_reconstruction"]["quotient"]["matrix"]
        if raw.get("consistent_augmented_system") and int_value(raw.get("coefficient_rank")) > 0:
            consistent_neighbors.append(motif)
        elif quotient.get("matrix_consistent") and int_value(quotient.get("coefficient_rank")) > 0:
            consistent_neighbors.append(motif)
    if consistent_neighbors:
        return "P1029_CLEAN_NEIGHBOR_MOTIF_RELATION_SIGNAL"
    if clean_neighbors:
        return "P1029_CLEAN_NEIGHBOR_MOTIF_SCALAR_ONLY"
    if any(motif["selection"]["fresh_positive_count"] for motif in neighbors):
        return "P1029_NEIGHBOR_MOTIF_SCALAR_SIGNAL_NOISY_NOT_PROMOTABLE"
    return "NEGATIVE_RESULT_P1029_NEIGHBOR_MOTIFS_NO_FRESH_POSITIVES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    training_windows = [*p1022.POSITIVE_CALIBRATION_WINDOWS, *p1022.VALIDATION_WINDOWS]
    all_windows = [*training_windows, *p1022.NEGATIVE_CALIBRATION_WINDOWS, *p1025.FRESH_WINDOWS]
    by_window, exists = p1010.build_window_rows(all_windows, args.targets, args.min_source_rank)
    scout_by_leaf: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for window in all_windows:
        split = split_for_window(window)
        for row in by_window.get(window) or []:
            if scout_predicate(row):
                scout_by_leaf[leaf_key(row)].append(annotate_row(row, window, split))
    ref_rows = [
        *reference_rows(training_windows, by_window, "training_seed"),
        *reference_rows(p1022.NEGATIVE_CALIBRATION_WINDOWS, by_window, "negative_control"),
        *reference_rows(p1025.FRESH_WINDOWS, by_window, "fresh_validation"),
    ]
    reference = motif_summary(LEAF19_KEY, ref_rows)
    motifs = [motif_summary(leaf, rows) for leaf, rows in sorted(scout_by_leaf.items())]
    motifs.sort(
        key=lambda motif: (
            0 if motif["leaf_key"] == LEAF19_KEY else 1,
            -int_value(motif["selection"].get("fresh_positive_count")),
            int_value(motif["selection"].get("fresh_false_count")),
            motif["leaf_key"],
        )
    )
    claim = determine_claim(reference, motifs)
    source_hashes = {
        window: p1005.sha256_file(p1007.expanded_source_path(window))
        for window in all_windows
        if p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1028_dependency_sha256": p1005.sha256_file(Path(p1028.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "NEGATIVE RESULT" if claim.startswith("NEGATIVE_RESULT") else "OBSERVATION",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "SCOUT BOUNDARY: top-k and exact anchor row-key are relaxed for neighboring motifs, so this is not a promoted scheduler.",
            "INDEX-CALCULUS PRECURSOR: relation consistency is not sparse linear algebra closure or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target baseline; below-rho scalar rows are not deployment evidence.",
        ],
        "parameters": {
            "fresh_windows": p1025.FRESH_WINDOWS,
            "min_source_rank": args.min_source_rank,
            "negative_calibration_windows": p1022.NEGATIVE_CALIBRATION_WINDOWS,
            "reference_rule": p1022.PRIMARY_RULE_NAME,
            "scout_selector": SCOUT_SELECTOR,
            "scout_selector_constraints": {
                "exact_anchor_row_key": "relaxed",
                "salt_gap_min": 3,
                "source_ops_over_rho_min": 0.7,
                "source_rank_min": 2,
                "top_k": "relaxed",
            },
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "training_windows": training_windows,
        },
        "schema": SCHEMA,
        "source": {
            "exists": exists,
        },
        "summary": {
            "claim_status": claim,
            "motif_count": len(motifs),
            "neighbor_count": sum(1 for motif in motifs if motif["leaf_key"] != LEAF19_KEY),
            "reference_fresh_false_count": reference["selection"]["fresh_false_count"],
            "reference_fresh_positive_count": reference["selection"]["fresh_positive_count"],
            "reference_negative_control_selected_count": reference["selection"]["negative_control_selected_count"],
            "reference_selected_count": reference["selection"]["selected_count"],
        },
        "reference_leaf19": reference,
        "motifs": motifs,
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    neighbor_lines = []
    for motif in payload["motifs"]:
        if motif["leaf_key"] == LEAF19_KEY:
            continue
        selection = motif["selection"]
        neighbor_lines.append(
            "{leaf}:selected={selected} fresh_pos={fresh_pos} fresh_false={fresh_false}".format(
                leaf=motif["leaf_key"],
                selected=selection["selected_count"],
                fresh_pos=selection["fresh_positive_count"],
                fresh_false=selection["fresh_false_count"],
            )
        )
    print(
        "claim={claim} motifs={motifs} neighbors={neighbors} ref_selected={ref_selected} "
        "ref_fresh_pos={ref_fresh_pos} out={out} {neighbor_lines}".format(
            claim=payload["claim_status"],
            motifs=summary["motif_count"],
            neighbors=summary["neighbor_count"],
            ref_selected=summary["reference_selected_count"],
            ref_fresh_pos=summary["reference_fresh_positive_count"],
            out=args.out,
            neighbor_lines="; ".join(neighbor_lines),
        )
    )


if __name__ == "__main__":
    main()
