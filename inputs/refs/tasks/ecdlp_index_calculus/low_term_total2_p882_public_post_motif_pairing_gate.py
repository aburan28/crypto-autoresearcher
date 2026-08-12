#!/usr/bin/env python3
"""P882 public post-motif row-quality/pairing gate.

P881 showed a below-rho single-row closure but an above-rho all-recovered
same-context motif bundle.  This probe freezes a simple public gate from
P880/P881 evidence, applies it to later windows, and then audits verifier rank
and closure after selection.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_p842_public_slice_motif_compression_audit as p842
import low_term_total2_p880_public_slice_motif_fresh_source_validation as p880
import low_term_total2_p881_public_slice_motif_rank_descent_audit as p881


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p882_public_post_motif_pairing_gate.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p882_public_post_motif_pairing_gate_probe.json"
DEFAULT_P842_SOURCE = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_P880_SOURCE = STATE_DIR / "low_term_total2_p880_public_slice_motif_fresh_source_validation_probe.json"
DEFAULT_P881_SOURCE = STATE_DIR / "low_term_total2_p881_public_slice_motif_rank_descent_audit_probe.json"
DEFAULT_VALIDATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_392_407_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_408_423_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_424_439_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_440_455_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_456_471_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p882_public_post_motif_pairing_gate.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def row_salt(row_key: str) -> int | None:
    match = re.search(r":salt(\d+)$", str(row_key))
    return int(match.group(1)) if match else None


def first_slice(row: dict[str, Any]) -> dict[str, Any]:
    selection = row.get("selection") or {}
    slices = selection.get("chosen_slices") or row.get("chosen_slices") or []
    return slices[0] if slices else {}


def row_features(row: dict[str, Any]) -> dict[str, Any]:
    selection = row.get("selection") or {}
    chosen = first_slice(row)
    salt = row_salt(str(row.get("row_key") or ""))
    transfer = int_value(row.get("transfer_index"))
    leaf_indices = [int_value(leaf) for leaf in row.get("leaf_indices") or []]
    if not leaf_indices and chosen.get("min_leaf_index") is not None:
        leaf_indices = [int_value(chosen.get("min_leaf_index"))]
    fixed_value = chosen.get("fixed_value")
    monomials = chosen.get("selected_factor_monomials")
    motif_ops = row.get("motif_ops_over_rho", selection.get("public_slice_motif_ops_over_rho"))
    return {
        "axis": chosen.get("axis"),
        "factor_zero_leaf_count": int_value(chosen.get("factor_zero_leaf_count")),
        "fixed_value": int_value(fixed_value) if fixed_value is not None else None,
        "leaf_indices": sorted(set(leaf_indices)),
        "max_leaf_index": max(leaf_indices) if leaf_indices else None,
        "min_leaf_index": min(leaf_indices) if leaf_indices else None,
        "motif_ops_over_rho": float(motif_ops) if motif_ops is not None else None,
        "relevant_leaf_count": int_value(chosen.get("relevant_leaf_count")),
        "row_key": row.get("row_key"),
        "row_salt": salt,
        "selected_factor_monomials": int_value(monomials) if monomials is not None else None,
        "target": row.get("target"),
        "transfer_index": transfer,
    }


def p880_training_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for result in payload.get("source_results") or []:
        for row in result.get("rows") or []:
            selection = row.get("selection") or {}
            if (
                selection.get("preserves_selected_root_pairs")
                and selection.get("public_slice_motif_beats_rho")
                and int_value(selection.get("chosen_count")) > 0
                and int_value(selection.get("selected_root_pair_count")) > 0
            ):
                rows.append(
                    {
                        **row,
                        "leaf_indices": [
                            int_value(item.get("min_leaf_index"))
                            for item in selection.get("chosen_slices") or []
                            if item.get("min_leaf_index") is not None
                        ],
                        "motif_ops_over_rho": selection.get("public_slice_motif_ops_over_rho"),
                        "training_label": "p880_recovered_support",
                    }
                )
    return rows


def p881_training_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for result in payload.get("source_results") or []:
        for row in result.get("recovered_rows") or []:
            rows.append({**row, "training_label": "p881_rank_descent"})
    return rows


def predicate_match(features: dict[str, Any], predicate: dict[str, Any]) -> bool:
    kind = predicate["kind"]
    value = predicate.get("value")
    if kind == "target_eq":
        return features.get("target") == value
    if kind == "fixed_value_eq":
        return features.get("fixed_value") == int_value(value)
    if kind == "leaf_contains":
        return int_value(value) in set(features.get("leaf_indices") or [])
    if kind == "monomials_lte":
        return features.get("selected_factor_monomials") is not None and int_value(features["selected_factor_monomials"]) <= int_value(value)
    if kind == "monomials_eq":
        return features.get("selected_factor_monomials") == int_value(value)
    if kind == "axis_eq":
        return features.get("axis") == value
    if kind == "transfer_mod_eq":
        modulus = int_value(predicate.get("modulus"))
        return modulus > 0 and int_value(features.get("transfer_index")) % modulus == int_value(value)
    if kind == "salt_mod_eq":
        modulus = int_value(predicate.get("modulus"))
        salt = features.get("row_salt")
        return salt is not None and modulus > 0 and int_value(salt) % modulus == int_value(value)
    if kind == "motif_ops_lte":
        return features.get("motif_ops_over_rho") is not None and float(features["motif_ops_over_rho"]) <= float(value)
    raise ValueError(f"unknown predicate kind {kind!r}")


def gate_match(row: dict[str, Any], gate: dict[str, Any]) -> bool:
    features = row_features(row)
    return all(predicate_match(features, predicate) for predicate in gate.get("predicates") or [])


def gate_name(predicates: list[dict[str, Any]]) -> str:
    if not predicates:
        return "all_recovered"
    parts = []
    for pred in predicates:
        if pred["kind"] in {"transfer_mod_eq", "salt_mod_eq"}:
            parts.append(f"{pred['kind']}:{pred.get('modulus')}={pred.get('value')}")
        else:
            parts.append(f"{pred['kind']}={pred.get('value')}")
    return "|".join(parts)


def dedupe_gates(gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for gate in gates:
        key = json.dumps(gate.get("predicates") or [], sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        out.append(gate)
    return out


def candidate_gates(training_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = [{"name": "all_recovered", "predicates": []}]
    feature_rows = [row_features(row) for row in training_rows]
    targets = sorted({row.get("target") for row in feature_rows if row.get("target")})
    fixed_values = sorted({row.get("fixed_value") for row in feature_rows if row.get("fixed_value") is not None})
    leaves = sorted({leaf for row in feature_rows for leaf in row.get("leaf_indices") or []})
    thresholds = sorted({value for row in feature_rows for value in [row.get("selected_factor_monomials")] if value is not None})
    thresholds.extend([24, 28, 30, 32, 34, 36, 40, 42])
    thresholds = sorted(set(int_value(value) for value in thresholds))

    def add(predicates: list[dict[str, Any]]) -> None:
        gates.append({"name": gate_name(predicates), "predicates": predicates})

    for target in targets:
        add([{"kind": "target_eq", "value": target}])
    for fixed in fixed_values:
        add([{"kind": "fixed_value_eq", "value": fixed}])
    for leaf in leaves:
        add([{"kind": "leaf_contains", "value": leaf}])
    for target in targets:
        for fixed in fixed_values:
            add([{"kind": "target_eq", "value": target}, {"kind": "fixed_value_eq", "value": fixed}])
        for leaf in leaves:
            add([{"kind": "target_eq", "value": target}, {"kind": "leaf_contains", "value": leaf}])
    for target in targets:
        for fixed in fixed_values:
            for leaf in leaves:
                base = [
                    {"kind": "target_eq", "value": target},
                    {"kind": "fixed_value_eq", "value": fixed},
                    {"kind": "leaf_contains", "value": leaf},
                ]
                add(base)
                for threshold in thresholds:
                    add([*base, {"kind": "monomials_lte", "value": threshold}])
                for modulus in (4, 8, 16):
                    for row in feature_rows:
                        if row.get("target") == target and row.get("fixed_value") == fixed and leaf in (row.get("leaf_indices") or []):
                            add([*base, {"kind": "transfer_mod_eq", "modulus": modulus, "value": int_value(row.get("transfer_index")) % modulus}])
                            salt = row.get("row_salt")
                            if salt is not None:
                                add([*base, {"kind": "salt_mod_eq", "modulus": modulus, "value": int_value(salt) % modulus}])
    for threshold in thresholds:
        add([{"kind": "monomials_lte", "value": threshold}])
    return dedupe_gates(gates)


def label_stats(rows: list[dict[str, Any]], p880_rows: list[dict[str, Any]], gate: dict[str, Any]) -> dict[str, Any]:
    selected = [row for row in rows if gate_match(row, gate)]
    p880_selected = [row for row in p880_rows if gate_match(row, gate)]
    closure = [
        row
        for row in selected
        if row.get("row_public_key_verified")
        and row.get("motif_ops_over_rho") is not None
        and float(row["motif_ops_over_rho"]) < 1.0
    ]
    rank_positive = [row for row in selected if int_value(row.get("rank")) > 0 or int_value(row.get("relation_count")) > 0]
    return {
        "closure_positive_count": len(closure),
        "closure_precision": ratio(len(closure), len(selected)),
        "false_positive_count": len(selected) - len(closure),
        "p880_support_count": len(p880_selected),
        "rank_positive_count": len(rank_positive),
        "rank_positive_precision": ratio(len(rank_positive), len(selected)),
        "selected_count": len(selected),
    }


def choose_gate(training_rows: list[dict[str, Any]], p880_rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = []
    for gate in candidate_gates(training_rows + p880_rows):
        stats = label_stats(training_rows, p880_rows, gate)
        gate = {**gate, "training_stats": stats}
        scored.append(gate)
    scored.sort(
        key=lambda gate: (
            int_value(gate["training_stats"]["closure_positive_count"]) > 0,
            int_value(gate["training_stats"]["p880_support_count"]) > 0,
            float(gate["training_stats"]["closure_precision"] or 0.0),
            -int_value(gate["training_stats"]["false_positive_count"]),
            float(gate["training_stats"]["rank_positive_precision"] or 0.0),
            int_value(gate["training_stats"]["p880_support_count"]),
            -int_value(gate["training_stats"]["selected_count"]),
            -len(gate.get("predicates") or []),
            gate["name"],
        ),
        reverse=True,
    )
    selected = scored[0]
    return {
        **selected,
        "candidate_count": len(scored),
        "top_candidates": [
            {
                "name": gate["name"],
                "predicates": gate.get("predicates") or [],
                "training_stats": gate["training_stats"],
            }
            for gate in scored[:12]
        ],
    }


def filter_source_results(source_results: list[dict[str, Any]], gate: dict[str, Any]) -> list[dict[str, Any]]:
    filtered = []
    for result in source_results:
        clean = dict(result)
        clean["recovered_rows"] = [row for row in result.get("recovered_rows") or [] if gate_match(row, gate)]
        filtered.append(clean)
    return filtered


def summarize_gate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    motif_ratios = [float(row["motif_ops_over_rho"]) for row in rows if row.get("motif_ops_over_rho") is not None]
    direct_ratios = [float(row["direct_ops_over_rho"]) for row in rows if row.get("direct_ops_over_rho") is not None]
    return {
        "direct_ops_over_rho_max": round(max(direct_ratios), 8) if direct_ratios else None,
        "direct_ops_over_rho_mean": round(mean(direct_ratios), 8) if direct_ratios else None,
        "direct_ops_over_rho_min": round(min(direct_ratios), 8) if direct_ratios else None,
        "motif_ops_over_rho_max": round(max(motif_ratios), 8) if motif_ratios else None,
        "motif_ops_over_rho_mean": round(mean(motif_ratios), 8) if motif_ratios else None,
        "motif_ops_over_rho_min": round(min(motif_ratios), 8) if motif_ratios else None,
        "rank_positive_count": len([row for row in rows if int_value(row.get("rank")) > 0 or int_value(row.get("relation_count")) > 0]),
        "row_count": len(rows),
        "row_public_key_verified_count": len([row for row in rows if row.get("row_public_key_verified")]),
    }


def determine_claim(gated_summary: dict[str, Any], baseline_summary: dict[str, Any]) -> str:
    if int_value(gated_summary.get("recovered_row_count")) == 0:
        if int_value(baseline_summary.get("recovered_row_count")) > 0:
            return "NEGATIVE_RESULT_P882_PUBLIC_GATE_SELECTS_NO_VALIDATION_ROWS"
        return "NEGATIVE_RESULT_P882_NO_VALIDATION_MOTIF_RECOVERED_ROWS"
    if int_value(gated_summary.get("motif_below_rho_verified_context_count")) > 0:
        return "P882_PUBLIC_GATE_CLOSES_VALIDATION_CONTEXT_BELOW_RHO"
    if int_value(gated_summary.get("row_motif_below_rho_public_key_verified_count")) > 0:
        return "P882_PUBLIC_GATE_CLOSES_VALIDATION_ROW_BELOW_RHO"
    if int_value(gated_summary.get("target_context_verified_count")) > 0:
        return "P882_PUBLIC_GATE_CLOSES_VALIDATION_CONTEXT_ABOVE_MOTIF_COST"
    if int_value(gated_summary.get("matrix_rank_sum")) > 0:
        return "P882_PUBLIC_GATE_SELECTS_VALIDATION_RANK_WITHOUT_CLOSURE"
    return "NEGATIVE_RESULT_P882_PUBLIC_GATE_NO_VALIDATION_RANK"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p842_payload = load_json(args.p842_source)
    p880_payload = load_json(args.p880_source)
    p881_payload = load_json(args.p881_source)
    p880_rows = p880_training_rows(p880_payload)
    p881_rows = p881_training_rows(p881_payload)
    selected_gate = choose_gate(p881_rows, p880_rows)

    motif_set = p880.normalize_motif_set(p842_payload["selected_policy"]["motif_set"])
    ps = p842.load_module("ecdlp_public_slice_for_p882", p842.PUBLIC_SLICE_SCRIPT)
    sources = args.signature_source or DEFAULT_VALIDATION_SOURCES
    sources = [Path(path) for path in sources[: int(args.max_sources)]]
    validation_results = [
        p881.evaluate_source(
            ps,
            source,
            motif_set,
            int(args.max_cases_per_source),
            int(args.max_factor_degree),
        )
        for source in sources
    ]
    baseline_contexts = p881.aggregate_contexts(ps, validation_results)
    baseline_summary = p881.aggregate_metrics(validation_results, baseline_contexts)
    gated_results = filter_source_results(validation_results, selected_gate)
    gated_contexts = p881.aggregate_contexts(ps, gated_results)
    gated_summary = p881.aggregate_metrics(gated_results, gated_contexts)
    gated_rows = [
        row
        for result in gated_results
        if not result.get("error")
        for row in result.get("recovered_rows") or []
        if not row.get("context_missing")
    ]
    claim_status = determine_claim(gated_summary, baseline_summary)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p842_source": str(args.p842_source),
            "p880_source": str(args.p880_source),
            "p881_source": str(args.p881_source),
            "script": str(Path(__file__)),
        },
        "baseline_all_recovered": {
            "context_groups": baseline_contexts,
            "summary": baseline_summary,
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "gated": {
            "context_groups": gated_contexts,
            "row_summary": summarize_gate_rows(gated_rows),
            "source_results": p881.strip_internal_source_results(gated_results),
            "summary": gated_summary,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "MOTIF-FROZEN: the slice motif is copied from P842/P880.",
            "GATE-FROZEN: P882 chooses the public gate from P880/P881 before validation rows are scored.",
            "PUBLIC-FEATURE BOUNDARY: gate predicates use only public row/motif fields.",
            "POST-SELECTION VERIFIER AUDIT: verifier rank/closure is measured after selection.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p882_public_post_motif_pairing_gate",
        "parameters": {
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "validation_source_count": len(sources),
        },
        "red_team_handoff": {
            "assumptions": [
                "P881 closure labels are sufficient to choose a first public post-motif row-quality gate.",
                "P880 recovered rows can be used only as unlabeled support, not as validation closure evidence.",
                "Validation labels after transfer 392 are used only after the gate is frozen.",
            ],
            "failure_modes": [
                "The selected gate may overfit the single P881 verified row.",
                "A gate can preserve rank-positive rows without enough independent forms for target closure.",
                "Transfer or salt phase predicates may be schedule artifacts rather than algebraic structure.",
            ],
            "next_concrete_action": (
                "If P882 is positive, replicate the frozen gate on windows after 472; "
                "if negative, broaden training to rank-positive labels and test a two-stage rank-before-closure selector."
            ),
        },
        "schema": SCHEMA,
        "selected_gate": selected_gate,
        "training": {
            "p880_recovered_support_count": len(p880_rows),
            "p881_closure_positive_count": len(
                [
                    row
                    for row in p881_rows
                    if row.get("row_public_key_verified")
                    and row.get("motif_ops_over_rho") is not None
                    and float(row["motif_ops_over_rho"]) < 1.0
                ]
            ),
            "p881_rank_positive_count": len([row for row in p881_rows if int_value(row.get("rank")) > 0 or int_value(row.get("relation_count")) > 0]),
            "p881_training_row_count": len(p881_rows),
        },
        "validation_sources": [str(source) for source in sources],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p842-source", type=Path, default=DEFAULT_P842_SOURCE)
    parser.add_argument("--p880-source", type=Path, default=DEFAULT_P880_SOURCE)
    parser.add_argument("--p881-source", type=Path, default=DEFAULT_P881_SOURCE)
    parser.add_argument("--signature-source", type=Path, action="append")
    parser.add_argument("--max-sources", type=int, default=len(DEFAULT_VALIDATION_SOURCES))
    parser.add_argument("--max-cases-per-source", type=int, default=24)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "baseline_summary": payload["baseline_all_recovered"]["summary"],
                "claim_status": payload["claim_status"],
                "gated_summary": payload["gated"]["summary"],
                "parameters": payload["parameters"],
                "selected_gate": {
                    "name": payload["selected_gate"]["name"],
                    "predicates": payload["selected_gate"]["predicates"],
                    "training_stats": payload["selected_gate"]["training_stats"],
                },
                "training": payload["training"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
