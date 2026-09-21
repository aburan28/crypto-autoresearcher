#!/usr/bin/env python3
"""P855 anchor-coefficient feature-bucket audit.

P854 ruled out cheap support/term/RHS/transfer-only anchor predictors.  This
audit attaches richer public context to each anchor sample from the P850/P851
line and tests leave-one-challenge-group-out feature buckets.

The audit measures exact anchor prediction only.  Hidden false-positive labels
are retained only as outcome strata and are not used in predictor keys.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p848_public_factor_multiroot_companion_audit as p848
import low_term_total2_p851_relation_matrix_rank_growth_audit as p851


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P850 = STATE_DIR / "low_term_total2_p850_split_lane_fresh_disjoint_validation_probe.json"
DEFAULT_P851 = STATE_DIR / "low_term_total2_p851_relation_matrix_rank_growth_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p855_anchor_feature_bucket_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p855_anchor_feature_bucket_audit.md"
SCHEMA = "ecdlp.low_term_total2_p855_anchor_feature_bucket_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p851.int_value(value, default)


def group_tuple(target: Any, transfer_index: Any, challenge_seed: Any) -> tuple[str, int, str]:
    return str(target), int_value(transfer_index), str(challenge_seed)


def group_id(group: tuple[str, int, str]) -> str:
    return f"{group[0]}|transfer={group[1]}|{group[2]}"


def majority(values: list[Any]) -> Any:
    counts = Counter(values)
    if not counts:
        return None
    return sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))[0][0]


def safe_ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 8)


def bucket(value: Any, boundaries: tuple[int, ...]) -> str:
    if value is None:
        return "none"
    value = int_value(value)
    for boundary in boundaries:
        if value <= boundary:
            return str(boundary)
    return f"gt{boundaries[-1]}"


def salt_from_row_key(row_key: str) -> int | None:
    match = re.search(r":salt([0-9]+)$", str(row_key))
    if not match:
        return None
    return int(match.group(1))


def variant(row: dict[str, Any]) -> dict[str, Any] | None:
    return (row.get("variant_summary") or {}).get("best_verified_with_candidate_leaf")


def row_lookup(public_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for rows in (public_payload.get("policy_rows") or {}).values():
        for row in rows or []:
            if isinstance(row, dict) and row.get("row_key") and row.get("row_key") not in out:
                out[str(row["row_key"])] = row
    return out


def simple_row_features(row: dict[str, Any] | None) -> dict[str, Any]:
    if not row:
        return {}
    chosen = row.get("chosen_candidate") if isinstance(row.get("chosen_candidate"), dict) else {}
    return {
        "factor_index": chosen.get("factor_index"),
        "factor_monomials": chosen.get("factor_monomials"),
        "factor_total_degree": chosen.get("factor_total_degree"),
        "factor_zero_leaf_count": row.get("factor_zero_leaf_count"),
        "public_factor_ops_bucket": bucket(row.get("public_factor_quadratic_root_ops"), (64, 96, 128, 160, 224)),
        "public_ops_over_rho_bucket": bucket_float(row.get("public_factor_quadratic_root_ops_over_rho")),
        "quadratic_preserves_selected_root_pairs": bool(row.get("quadratic_preserves_selected_root_pairs")),
        "row_salt": salt_from_row_key(str(row.get("row_key") or "")),
        "selected_leaf_count": row.get("selected_leaf_count"),
    }


def bucket_float(value: Any) -> str:
    if value is None:
        return "none"
    try:
        scaled = int(round(float(value) * 1000))
    except (TypeError, ValueError):
        return "none"
    return bucket(scaled, (500, 750, 1000, 1250, 1500, 2000))


def trigger_features(row: dict[str, Any]) -> dict[str, Any]:
    features = row.get("candidate_features") or {}
    source_case = row.get("source_case") or {}
    chosen = row.get("chosen_candidate") if isinstance(row.get("chosen_candidate"), dict) else {}
    return {
        "bank_id": row.get("bank_id"),
        "factor_index": features.get("factor_index"),
        "factor_monomials": features.get("factor_monomials"),
        "factor_root_scan_ops_bucket": bucket(features.get("factor_root_scan_ops"), (64, 80, 96, 112, 128)),
        "factor_total_degree": features.get("factor_total_degree"),
        "full_remainder_ops_bucket": bucket_float(features.get("full_remainder_ffe_ops_over_rho")),
        "relation_class": row.get("relation_discriminator_class"),
        "remainder_monomials_bucket": bucket(features.get("remainder_monomials"), (128, 192, 256, 320, 448)),
        "row_salt": salt_from_row_key(str(row.get("row_key") or "")),
        "source_case_policy": source_case.get("policy"),
        "source_case_selector": source_case.get("selector"),
        "source_case_top_k": source_case.get("top_k"),
        "surface_ffe_ops_bucket": bucket(features.get("surface_ffe_ops"), (64, 72, 80, 88, 96, 112)),
        "variant_name": (variant(row) or {}).get("name"),
        "chosen_factor_root_scan_bucket": bucket(chosen.get("factor_root_scan_ops"), (64, 80, 96, 112, 128)),
    }


def predictor_key(name: str, sample: dict[str, Any]) -> tuple[Any, ...]:
    support = tuple(sample["support"])
    event = sample.get("event_row_features") or {}
    trig = sample.get("trigger_features") or {}
    base = (sample["target"], support)
    if name == "support":
        return base
    if name == "support_terms":
        return base + (tuple(sample["terms"]),)
    if name == "event_salt":
        return base + ("event_salt", event.get("row_salt"))
    if name == "trigger_salt":
        return base + ("trigger_salt", trig.get("row_salt"))
    if name == "relation_class":
        return base + ("class", trig.get("relation_class"))
    if name == "variant_name":
        return base + ("variant", trig.get("variant_name"))
    if name == "source_policy_topk":
        return base + ("policy", trig.get("source_case_policy"), trig.get("source_case_top_k"))
    if name == "trigger_factor_index":
        return base + ("trigger_factor", trig.get("factor_index"))
    if name == "event_factor_index":
        return base + ("event_factor", event.get("factor_index"))
    if name == "trigger_surface_bucket":
        return base + ("trigger_surface", trig.get("surface_ffe_ops_bucket"))
    if name == "event_public_ops_bucket":
        return base + ("event_public_ops", event.get("public_ops_over_rho_bucket"))
    if name == "trigger_factor_surface_policy":
        return base + (
            "combo",
            trig.get("factor_index"),
            trig.get("surface_ffe_ops_bucket"),
            trig.get("source_case_policy"),
        )
    raise KeyError(name)


PREDICTORS = [
    "support",
    "support_terms",
    "event_salt",
    "trigger_salt",
    "relation_class",
    "variant_name",
    "source_policy_topk",
    "trigger_factor_index",
    "event_factor_index",
    "trigger_surface_bucket",
    "event_public_ops_bucket",
    "trigger_factor_surface_policy",
]


def collect_samples(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    p850 = load_json(args.p850)
    p851_payload = load_json(args.p851)
    p851_groups = {
        group_tuple(group.get("target"), group.get("transfer_index"), group.get("challenge_seed")): {
            "below_rho": group.get("deduped_ops_over_rho") is not None
            and float(group["deduped_ops_over_rho"]) < 1.0,
            "deduped_ops_over_rho": group.get("deduped_ops_over_rho"),
            "hidden_false_candidate_count": group.get("hidden_false_candidate_count"),
        }
        for group in p851_payload.get("challenge_groups") or []
    }
    verifier = p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    public_cache: dict[str, dict[str, Any]] = {}
    row_cache: dict[str, dict[str, dict[str, Any]]] = {}
    context_cache: dict[
        tuple[Any, ...],
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]],
    ] = {}
    scan_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    built_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    group_seen_forms: dict[tuple[str, int, str], set[tuple[tuple[int, ...], int]]] = defaultdict(set)
    samples = []
    errors = []
    for index, row in enumerate(p850.get("relation_lane_rows") or []):
        best = variant(row)
        if not best or not best.get("verified"):
            errors.append({"index": index, "row_key": row.get("row_key"), "error": "missing verified P850 variant"})
            continue
        public_source = str(row["public_source"])
        if public_source not in public_cache:
            public_cache[public_source] = load_json(Path(public_source))
            row_cache[public_source] = row_lookup(public_cache[public_source])
        public_payload = public_cache[public_source]
        source_case = p851.compact_source_case(row)
        ckey = p851.context_key(public_source, source_case)
        if ckey not in context_cache:
            context_cache[ckey] = p848.build_context(verifier, records, public_payload, source_case)
        built_by_row, components_by_row, local_args_by_row = context_cache[ckey]
        challenge_seeds = set()
        scan_rows = []
        for selected_row_key, leaves in sorted((best.get("leaves_by_row") or {}).items()):
            selected = sorted({int_value(leaf) for leaf in leaves})
            if not selected:
                continue
            skey = p851.scan_key(public_source, source_case, selected_row_key, selected)
            if skey not in scan_cache:
                scan_cache[skey] = p848.direct_witness_probe.scan_selected(
                    verifier,
                    built_by_row[selected_row_key],
                    components_by_row[selected_row_key],
                    set(selected),
                    local_args_by_row[selected_row_key],
                )
                built_cache[skey] = built_by_row[selected_row_key]
            challenge_seeds.add(str(built_cache[skey].get("challenge_seed")))
            scan_rows.append((selected_row_key, skey, selected, scan_cache[skey]))
        if len(challenge_seeds) != 1:
            errors.append(
                {
                    "index": index,
                    "row_key": row.get("row_key"),
                    "error": "variant spans multiple challenge seeds",
                    "challenge_seeds": sorted(challenge_seeds),
                }
            )
            continue
        group = group_tuple(row.get("target"), row.get("transfer_index"), next(iter(challenge_seeds)))
        group_meta = p851_groups.get(group, {})
        trigger = trigger_features(row)
        trigger_hidden_false = bool((row.get("hidden_factor_labels") or {}).get("chosen_false_positive_source"))
        for selected_row_key, _skey, selected, scan in scan_rows:
            event_row = row_cache[public_source].get(str(selected_row_key))
            event_features = simple_row_features(event_row)
            for event in scan.get("relation_events") or []:
                form_key = p851.form_key(event)
                if form_key in group_seen_forms[group]:
                    continue
                group_seen_forms[group].add(form_key)
                coeffs, rhs, terms = event["form"]
                coeffs_tuple = tuple(int(coeff) for coeff in coeffs)
                support = tuple(index for index, coeff in enumerate(coeffs_tuple) if coeff != 0)
                if 0 not in support:
                    continue
                samples.append(
                    {
                        "anchor": coeffs_tuple[0],
                        "below_rho": bool(group_meta.get("below_rho")),
                        "coeff_values": tuple(coeffs_tuple[index] for index in support),
                        "event_row_features": event_features,
                        "event_row_key": selected_row_key,
                        "event_selected_leaf_count": len(selected),
                        "group": group,
                        "group_id": group_id(group),
                        "hidden_false_group": bool(group_meta.get("hidden_false_candidate_count")),
                        "rhs": int(rhs),
                        "support": support,
                        "target": str(row.get("target")),
                        "terms": tuple(int(term) for term in terms),
                        "transfer_index": int_value(row.get("transfer_index")),
                        "trigger_features": trigger,
                        "trigger_hidden_false": trigger_hidden_false,
                        "trigger_row_key": row.get("row_key"),
                    }
                )
    return samples, errors


def repeated_support_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups_by_support: dict[tuple[str, tuple[int, ...]], set[str]] = defaultdict(set)
    for sample in samples:
        groups_by_support[(sample["target"], tuple(sample["support"]))].add(sample["group_id"])
    return [
        sample
        for sample in samples
        if len(groups_by_support[(sample["target"], tuple(sample["support"]))]) >= 2
    ]


def evaluate_predictors(samples: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    repeated = repeated_support_samples(samples)
    results: dict[str, Counter[str]] = defaultdict(Counter)
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sample in repeated:
        same_support_train = [
            other
            for other in repeated
            if other["target"] == sample["target"]
            and tuple(other["support"]) == tuple(sample["support"])
            and other["group_id"] != sample["group_id"]
        ]
        for name in PREDICTORS:
            key = predictor_key(name, sample)
            train = [other for other in same_support_train if predictor_key(name, other) == key]
            results[name]["total"] += 1
            if not train:
                results[name]["uncovered"] += 1
                continue
            predicted = majority([other["anchor"] for other in train])
            results[name]["covered"] += 1
            if predicted == sample["anchor"]:
                results[name]["correct"] += 1
                if len(examples[name]) < 5:
                    examples[name].append(
                        {
                            "anchor": sample["anchor"],
                            "group_id": sample["group_id"],
                            "key": list(key),
                            "row": sample["trigger_row_key"],
                            "support": list(sample["support"]),
                            "target": sample["target"],
                        }
                    )
    return {
        name: {
            "accuracy": safe_ratio(counts["correct"], counts["total"]),
            "correct": counts["correct"],
            "coverage": safe_ratio(counts["covered"], counts["total"]),
            "covered_accuracy": safe_ratio(counts["correct"], counts["covered"]),
            "covered": counts["covered"],
            "examples": examples.get(name, []),
            "total": counts["total"],
            "uncovered": counts["uncovered"],
        }
        for name, counts in sorted(results.items())
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    samples, errors = collect_samples(args)
    repeated = repeated_support_samples(samples)
    predictor_results = evaluate_predictors(samples)
    claim = determine_claim(predictor_results, errors)
    return {
        "anchor_samples": compact_sample_summary(repeated),
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p850_source": str(args.p850),
            "p851_source": str(args.p851),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "FEATURE-BUCKET BOUNDARY: predictors use exact feature-bucket matches and are scored leave-one-challenge-group-out.",
            "COVERAGE BOUNDARY: high uncovered rates mean a feature bucket is too specific for current data.",
            "HIDDEN-LABEL BOUNDARY: hidden false-positive labels are retained only for stratification, not predictor keys.",
            "NO-CROSS-TRANSFER-RANK-MIXING: anchor guesses are not aggregated as a linear system.",
            "POLLARD-RHO BOUNDARY: this is an anchor-feature diagnostic, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p855_anchor_feature_bucket_audit",
        "parameters": {
            "prediction_protocol": "leave-one-challenge-group-out exact feature-bucket majority inside repeated support signatures",
            "predictors": PREDICTORS,
        },
        "predictor_results": predictor_results,
        "red_team_handoff": {
            "assumptions": [
                "Richer P850 row/candidate public features are the right next source for anchor prediction.",
                "Exact feature-bucket matching is a fair first test before using learned models.",
            ],
            "failure_modes": [
                "Feature buckets may be too sparse to cover held-out groups.",
                "Anchor values may remain high-entropy even after public feature conditioning.",
                "A learned model could overfit toy parameters without improving target descent.",
            ],
            "next_concrete_action": (
                "Build P856 to test whether variable-anchor skeletons can be consumed directly by target descent or "
                "whether a regularized model over row/candidate features predicts anchor buckets with held-out coverage."
            ),
            "status": "HYPOTHESIS" if claim.startswith("P855_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summarize(samples, repeated, predictor_results, errors),
    }


def compact_sample_summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    by_target = defaultdict(int)
    hidden = 0
    below = 0
    for sample in samples:
        by_target[sample["target"]] += 1
        hidden += int(bool(sample.get("hidden_false_group")))
        below += int(bool(sample.get("below_rho")))
    return {
        "below_rho_sample_count": below,
        "hidden_false_sample_count": hidden,
        "sample_count": len(samples),
        "samples_by_target": dict(sorted(by_target.items())),
    }


def determine_claim(results: dict[str, dict[str, Any]], errors: list[dict[str, Any]]) -> str:
    if errors:
        return "NEGATIVE_RESULT_P855_RECONSTRUCTION_ERRORS"
    covered = [row for row in results.values() if int_value(row.get("covered"))]
    best_accuracy = max((float(row.get("accuracy") or 0.0) for row in results.values()), default=0.0)
    best_covered = max((float(row.get("covered_accuracy") or 0.0) for row in covered), default=0.0)
    if best_accuracy > 0:
        return "P855_FEATURE_BUCKETS_HAVE_ANCHOR_EXACT_MATCH_SIGNAL"
    if best_covered > 0:
        return "P855_FEATURE_BUCKETS_HAVE_COVERED_ANCHOR_SIGNAL_BUT_ZERO_TOTAL_ACCURACY"
    if any(float(row.get("coverage") or 0.0) > 0 for row in results.values()):
        return "NEGATIVE_RESULT_P855_FEATURE_BUCKETS_COVER_BUT_FAIL_ANCHOR"
    return "NEGATIVE_RESULT_P855_FEATURE_BUCKETS_TOO_SPARSE_OR_FAIL"


def summarize(
    samples: list[dict[str, Any]],
    repeated: list[dict[str, Any]],
    results: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    best_total = None
    best_total_accuracy = -1.0
    best_covered = None
    best_covered_accuracy = -1.0
    for name, row in results.items():
        accuracy = float(row.get("accuracy") or 0.0)
        covered_accuracy = float(row.get("covered_accuracy") or 0.0)
        if accuracy > best_total_accuracy:
            best_total = name
            best_total_accuracy = accuracy
        if covered_accuracy > best_covered_accuracy:
            best_covered = name
            best_covered_accuracy = covered_accuracy
    return {
        "best_covered_accuracy": best_covered_accuracy if best_covered is not None else None,
        "best_covered_predictor": best_covered,
        "best_total_accuracy": best_total_accuracy if best_total is not None else None,
        "best_total_predictor": best_total,
        "claim_status": determine_claim(results, errors),
        "error_count": len(errors),
        "predictor_count": len(results),
        "repeated_support_sample_count": len(repeated),
        "sample_count": len(samples),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p850", type=Path, default=DEFAULT_P850)
    parser.add_argument("--p851", type=Path, default=DEFAULT_P851)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
