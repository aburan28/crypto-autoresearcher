#!/usr/bin/env python3
"""P1040 public disambiguator scout for P1038 true vs P1039 false witnesses."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout as p1033


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1040_p231_public_disambiguator_scout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1040_p231_public_disambiguator_scout_probe.json"
DEFAULT_P1038 = STATE_DIR / "low_term_total2_p1038_p231_guarded_structural_family_supply_search_probe.json"
DEFAULT_P1039 = STATE_DIR / "low_term_total2_p1039_p231_strict_leaf8_route_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1040_p231_public_disambiguator_scout.v1"
ORDER = p1033.ORDER
PRIMARY_POOL = "p1029_leaf8_scout"
STRICT_TERMS = (8, 8, 11, 11)
STRICT_TAIL = (9, 12)

RuleFn = Callable[[dict[str, Any]], bool]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_json(value: Any, default: Any) -> Any:
    if isinstance(value, (list, dict)):
        return value
    if not isinstance(value, str):
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def parse_public(public: str) -> tuple[int, ...]:
    parsed = parse_json(public, [])
    if not isinstance(parsed, list):
        return ()
    return tuple(int_value(item) for item in parsed)


def phase_from_label(label: str) -> str:
    if label.endswith("_forward_raw") or label.endswith("_forward_compressed"):
        return "forward"
    if label.endswith("_scout_raw") or label.endswith("_scout_compressed"):
        return "scout"
    return "unknown"


def view_from_label(label: str) -> str:
    if label.endswith("_compressed"):
        return "compressed"
    if label.endswith("_raw"):
        return "raw"
    return "unknown"


def mod_delta_min(left: int, right: int) -> int:
    delta = (left - right) % ORDER
    return min(delta, (-delta) % ORDER)


def signed_coeff(value: int) -> int:
    value %= ORDER
    return value - ORDER if value > ORDER // 2 else value


def sorted_pair(left: dict[str, Any], right: dict[str, Any]) -> tuple[tuple[int, int], tuple[int, int]]:
    pair = sorted(
        [
            (int_value(left.get("q_coeff")) % ORDER, int_value(left.get("rhs")) % ORDER),
            (int_value(right.get("q_coeff")) % ORDER, int_value(right.get("rhs")) % ORDER),
        ]
    )
    return tuple(pair)  # type: ignore[return-value]


def tail_coeffs(form: dict[str, Any]) -> tuple[int, ...]:
    exact = parse_json(form.get("exact_tail_expression_key"), {})
    if isinstance(exact, dict):
        coeffs = exact.get("tail_coeffs") or []
        return tuple(int_value(item) % ORDER for item in coeffs)
    return ()


def prediction_event(
    artifact: str,
    pool: str,
    label: str,
    model: str,
    object_key: Any,
    group: dict[str, Any],
    prediction: dict[str, Any],
) -> dict[str, Any]:
    left = dict(prediction.get("left") or {})
    right = dict(prediction.get("right") or {})
    pair = sorted_pair(left, right)
    public = str(left.get("public_fingerprint") or group.get("public_fingerprint") or "")
    public_coords = parse_public(public)
    terms = tuple(int_value(item) for item in left.get("terms") or group.get("family", {}).get("terms") or [])
    tail = tuple(int_value(item) for item in left.get("tail_support") or group.get("family", {}).get("tail_support") or [])
    salts = sorted(
        {
            int_value(item)
            for form in (left, right)
            for item in (form.get("salt_tuple") or [])
            if isinstance(item, int) or str(item).isdigit()
        }
    )
    row_keys = sorted(
        {
            str(item)
            for form in (left, right)
            for item in (form.get("row_keys") or [])
            if str(item)
        }
    )
    q_values = [int_value(left.get("q_coeff")) % ORDER, int_value(right.get("q_coeff")) % ORDER]
    rhs_values = [int_value(left.get("rhs")) % ORDER, int_value(right.get("rhs")) % ORDER]
    coeffs = tail_coeffs(left) or tail_coeffs(right)
    return {
        "artifact": artifact,
        "is_primary": pool == PRIMARY_POOL,
        "label": label,
        "model": model,
        "object_key": object_key,
        "phase": phase_from_label(label),
        "pool": pool,
        "predicted_target": int_value(prediction.get("predicted_target")) % ORDER,
        "public": public,
        "public_coords": public_coords,
        "q_pair": tuple(item[0] for item in pair),
        "rhs_pair": tuple(item[1] for item in pair),
        "q_delta_min": mod_delta_min(q_values[0], q_values[1]),
        "rhs_delta_min": mod_delta_min(rhs_values[0], rhs_values[1]),
        "row_keys": tuple(row_keys),
        "row_key_count": len(row_keys),
        "same_row_key": len(row_keys) == 1,
        "salt_gap": (max(salts) - min(salts)) if len(salts) >= 2 else 0,
        "salt_pair": tuple(salts),
        "same_salt": len(salts) == 1,
        "source_secrets": tuple(int_value(item) % ORDER for item in prediction.get("source_secrets") or []),
        "tail": tail,
        "tail_coeff_signs": tuple(0 if signed_coeff(item) == 0 else (1 if signed_coeff(item) > 0 else -1) for item in coeffs),
        "tail_coeff_signed": tuple(signed_coeff(item) for item in coeffs),
        "terms": terms,
        "toy_secret_verified": bool(prediction.get("toy_secret_verified")),
        "view": view_from_label(label),
        "window": str(left.get("window") or group.get("window") or ""),
    }


def event_key(event: dict[str, Any]) -> tuple[Any, ...]:
    return (
        event["artifact"],
        event["pool"],
        event["phase"],
        event["window"],
        event["public"],
        event["terms"],
        event["tail"],
        event["q_pair"],
        event["rhs_pair"],
        event["predicted_target"],
    )


def family_key(event: dict[str, Any]) -> tuple[Any, ...]:
    return (
        event["artifact"],
        event["pool"],
        event["phase"],
        event["window"],
        event["public"],
        event["terms"],
        event["tail"],
    )


def load_events(path: Path, artifact: str) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    events = []
    for pool_result in payload.get("pool_results") or []:
        pool = str(pool_result.get("name") or "")
        for evaluation in pool_result.get("evaluations") or []:
            label = str(evaluation.get("label") or "")
            for object_result in evaluation.get("object_results") or []:
                model = str(object_result.get("model") or "")
                for group in object_result.get("groups") or []:
                    object_key = group.get("object_key")
                    for prediction in group.get("predictions") or []:
                        event = prediction_event(artifact, pool, label, model, object_key, group, prediction)
                        if event["terms"] == STRICT_TERMS and event["tail"] == STRICT_TAIL:
                            events.append(event)
    return events


def make_witnesses(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    raw_exact_count: dict[tuple[Any, ...], int] = defaultdict(int)
    raw_family_count: dict[tuple[Any, ...], int] = defaultdict(int)
    for event in events:
        by_key[event_key(event)].append(event)
        if event["view"] == "raw":
            raw_exact_count[event_key(event)] += 1
            raw_family_count[family_key(event)] += 1

    witnesses = []
    for key, group in sorted(by_key.items()):
        compressed_events = [event for event in group if event["view"] == "compressed"]
        if not compressed_events:
            continue
        rep = compressed_events[0]
        models = sorted({event["model"] for event in compressed_events})
        public_coords = rep["public_coords"]
        residues = {
            f"{axis}_mod_{modulus}": (public_coords[index] % modulus if len(public_coords) > index else None)
            for index, axis in enumerate(("x", "y"))
            for modulus in (2, 3, 5, 7, 11)
        }
        true_count = sum(1 for event in compressed_events if event["toy_secret_verified"])
        false_count = sum(1 for event in compressed_events if not event["toy_secret_verified"])
        witness = {
            "artifact": rep["artifact"],
            "compressed_event_count": len(compressed_events),
            "false_count": false_count,
            "is_primary": rep["is_primary"],
            "model_count": len(models),
            "models": models,
            "phase": rep["phase"],
            "pool": rep["pool"],
            "predicted_target": rep["predicted_target"],
            "public": rep["public"],
            "public_coords": list(public_coords),
            "q_delta_min": rep["q_delta_min"],
            "q_pair": list(rep["q_pair"]),
            "raw_exact_prediction_count": raw_exact_count[key],
            "raw_public_family_prediction_count": raw_family_count[family_key(rep)],
            "rhs_delta_min": rep["rhs_delta_min"],
            "rhs_pair": list(rep["rhs_pair"]),
            "row_key_count": rep["row_key_count"],
            "row_keys": list(rep["row_keys"]),
            "same_row_key": rep["same_row_key"],
            "same_salt": rep["same_salt"],
            "salt_gap": rep["salt_gap"],
            "salt_pair": list(rep["salt_pair"]),
            "source_secrets": list(rep["source_secrets"]),
            "tail": list(rep["tail"]),
            "tail_coeff_signed": list(rep["tail_coeff_signed"]),
            "tail_coeff_signs": list(rep["tail_coeff_signs"]),
            "terms": list(rep["terms"]),
            "true_count": true_count,
            "verified_label": "true" if true_count and not false_count else "false" if false_count and not true_count else "mixed",
            "window": rep["window"],
            **residues,
        }
        witnesses.append(witness)
    return witnesses


def witness_class(witness: dict[str, Any]) -> str:
    if witness["phase"] == "scout" and witness["is_primary"] and witness["verified_label"] == "true":
        return "primary_scout_true"
    if witness["phase"] == "forward" and witness["is_primary"] and witness["verified_label"] == "true":
        return "primary_forward_true"
    if witness["phase"] == "forward" and witness["is_primary"] and witness["verified_label"] == "false":
        return "primary_forward_false"
    if witness["phase"] == "forward" and not witness["is_primary"] and witness["verified_label"] == "false":
        return "diagnostic_forward_false"
    if witness["verified_label"] == "true":
        return "other_true"
    if witness["verified_label"] == "false":
        return "other_false"
    return "mixed"


def base_rules(witnesses: list[dict[str, Any]]) -> list[tuple[str, str, RuleFn]]:
    rules: list[tuple[str, str, RuleFn]] = [
        ("same_salt", "Both forms come from the same public salt.", lambda w: bool(w["same_salt"])),
        ("not_same_salt", "The pair uses distinct public salts.", lambda w: not bool(w["same_salt"])),
        ("salt_gap_ge_4", "Distinct salt gap is at least 4.", lambda w: int_value(w["salt_gap"]) >= 4),
        ("salt_gap_ge_8", "Distinct salt gap is at least 8.", lambda w: int_value(w["salt_gap"]) >= 8),
        ("salt_gap_ge_9", "Distinct salt gap is at least 9.", lambda w: int_value(w["salt_gap"]) >= 9),
        ("salt_gap_ne_3", "Salt gap is not 3.", lambda w: int_value(w["salt_gap"]) != 3),
        (
            "same_salt_or_gap_ge_8",
            "Same salt, or distinct salt gap at least 8.",
            lambda w: bool(w["same_salt"]) or int_value(w["salt_gap"]) >= 8,
        ),
        (
            "same_salt_or_gap_ge_9",
            "Same salt, or distinct salt gap at least 9.",
            lambda w: bool(w["same_salt"]) or int_value(w["salt_gap"]) >= 9,
        ),
        (
            "raw_exact_prediction_support",
            "Compressed witness has exact raw-prediction support.",
            lambda w: int_value(w["raw_exact_prediction_count"]) > 0,
        ),
        (
            "raw_public_family_prediction_support",
            "Compressed witness has raw prediction support in the same public/window/family.",
            lambda w: int_value(w["raw_public_family_prediction_count"]) > 0,
        ),
        ("rhs_delta_le_3000", "Minimal RHS delta is at most 3000.", lambda w: int_value(w["rhs_delta_min"]) <= 3000),
        ("rhs_delta_ge_5000", "Minimal RHS delta is at least 5000.", lambda w: int_value(w["rhs_delta_min"]) >= 5000),
        (
            "rhs_delta_outside_middle_3001_4999",
            "Minimal RHS delta is outside the middle band 3001..4999.",
            lambda w: int_value(w["rhs_delta_min"]) <= 3000 or int_value(w["rhs_delta_min"]) >= 5000,
        ),
        ("q_delta_ge_3000", "Minimal q delta is at least 3000.", lambda w: int_value(w["q_delta_min"]) >= 3000),
    ]

    for feature in ("salt_gap", "q_delta_min", "rhs_delta_min"):
        values = sorted({int_value(witness.get(feature)) for witness in witnesses})
        for value in values:
            rules.append((f"{feature}_le_{value}", f"{feature} <= {value}.", lambda w, f=feature, v=value: int_value(w.get(f)) <= v))
            rules.append((f"{feature}_ge_{value}", f"{feature} >= {value}.", lambda w, f=feature, v=value: int_value(w.get(f)) >= v))

    primary_true = [witness for witness in witnesses if witness_class(witness) == "primary_forward_true"]
    for feature in ("salt_gap", "q_delta_min", "rhs_delta_min"):
        true_values = sorted({int_value(witness.get(feature)) for witness in primary_true})
        if true_values:
            rules.append(
                (
                    f"{feature}_in_primary_true_values",
                    f"{feature} is one of the post-hoc primary true values {true_values}.",
                    lambda w, f=feature, vals=set(true_values): int_value(w.get(f)) in vals,
                )
            )

    for modulus in (2, 3, 5, 7, 11):
        for axis in ("x", "y"):
            feature = f"{axis}_mod_{modulus}"
            true_values = sorted({witness.get(feature) for witness in primary_true if witness.get(feature) is not None})
            if true_values:
                rules.append(
                    (
                        f"{feature}_in_primary_true_values",
                        f"public {feature} is one of the post-hoc primary true residues {true_values}.",
                        lambda w, f=feature, vals=set(true_values): w.get(f) in vals,
                    )
                )
    return rules


def score_rule(name: str, description: str, fn: RuleFn, witnesses: list[dict[str, Any]]) -> dict[str, Any]:
    classes = defaultdict(list)
    for witness in witnesses:
        classes[witness_class(witness)].append(witness)
    selected_by_class = {}
    for class_name, items in classes.items():
        selected_by_class[class_name] = [witness["id"] for witness in items if fn(witness)]
    primary_true_total = len(classes.get("primary_forward_true", []))
    primary_false_total = len(classes.get("primary_forward_false", []))
    diagnostic_false_total = len(classes.get("diagnostic_forward_false", []))
    primary_true_selected = len(selected_by_class.get("primary_forward_true", []))
    primary_false_selected = len(selected_by_class.get("primary_forward_false", []))
    diagnostic_false_selected = len(selected_by_class.get("diagnostic_forward_false", []))
    return {
        "description": description,
        "diagnostic_false_selected": diagnostic_false_selected,
        "diagnostic_false_total": diagnostic_false_total,
        "name": name,
        "primary_contrast_success": bool(
            primary_true_total > 0
            and primary_false_total > 0
            and primary_true_selected == primary_true_total
            and primary_false_selected == 0
        ),
        "primary_false_selected": primary_false_selected,
        "primary_false_total": primary_false_total,
        "primary_true_selected": primary_true_selected,
        "primary_true_total": primary_true_total,
        "scout_true_selected": len(selected_by_class.get("primary_scout_true", [])),
        "scout_true_total": len(classes.get("primary_scout_true", [])),
        "selected_by_class": selected_by_class,
        "strict_diagnostic_success": bool(
            primary_true_total > 0
            and primary_false_total > 0
            and primary_true_selected == primary_true_total
            and primary_false_selected == 0
            and diagnostic_false_selected == 0
        ),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    paths = {"p1038": Path(args.p1038), "p1039": Path(args.p1039)}
    events = []
    for artifact, path in paths.items():
        events.extend(load_events(path, artifact))
    witnesses = make_witnesses(events)
    for index, witness in enumerate(witnesses):
        witness["class"] = witness_class(witness)
        witness["id"] = f"W{index:04d}:{witness['artifact']}:{witness['pool']}:{witness['phase']}:{witness['window']}:{witness['public']}:{witness['predicted_target']}"

    rules = [score_rule(name, description, fn, witnesses) for name, description, fn in base_rules(witnesses)]
    rules.sort(
        key=lambda item: (
            not item["strict_diagnostic_success"],
            not item["primary_contrast_success"],
            item["diagnostic_false_selected"],
            -item["scout_true_selected"],
            item["name"],
        )
    )
    primary_contrast = [rule for rule in rules if rule["primary_contrast_success"]]
    strict_diagnostic = [rule for rule in rules if rule["strict_diagnostic_success"]]
    if strict_diagnostic:
        claim = "P1040_PUBLIC_DISAMBIGUATOR_CANDIDATE_WITH_DIAGNOSTIC_REJECTION"
        taxonomy = "OBSERVATION"
    elif primary_contrast:
        claim = "P1040_PRIMARY_PUBLIC_DISAMBIGUATOR_CANDIDATE_DIAGNOSTIC_OPEN"
        taxonomy = "OBSERVATION"
    else:
        claim = "NEGATIVE_RESULT_P1040_NO_PUBLIC_DISAMBIGUATOR_IN_CATALOG"
        taxonomy = "NEGATIVE RESULT"

    class_counts: dict[str, int] = defaultdict(int)
    for witness in witnesses:
        class_counts[witness["class"]] += 1

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p1038": str(paths["p1038"]),
            "p1039": str(paths["p1039"]),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1038_sha256": p1005.sha256_file(paths["p1038"]),
            "p1039_sha256": p1005.sha256_file(paths["p1039"]),
            "script_sha256": p1005.sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "class_counts": dict(sorted(class_counts.items())),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "POST-HOC: P1040 searches discriminators after observing P1038/P1039 labels.",
            "PUBLIC-FEATURES: rule predicates use public/local metadata only; labels are used only for scoring.",
            "NO NOVELTY CLAIM: any selected rule must be frozen and validated on a fresh holdout.",
            "INDEX-CALCULUS PRECURSOR: this is scalar-stability filtering, not linear algebra or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "primary_pool": PRIMARY_POOL,
            "strict_tail": list(STRICT_TAIL),
            "strict_terms": list(STRICT_TERMS),
            "target": args.targets,
        },
        "rules": rules[:64],
        "schema": SCHEMA,
        "summary": {
            "candidate_rule_count": len(rules),
            "claim_status": claim,
            "primary_contrast_rule_count": len(primary_contrast),
            "strict_diagnostic_rule_count": len(strict_diagnostic),
            "top_rules": rules[:12],
            "witness_class_counts": dict(sorted(class_counts.items())),
        },
        "timestamp": now_iso(),
        "witnesses": witnesses,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1038", default=str(DEFAULT_P1038), help="P1038 JSON artifact")
    parser.add_argument("--p1039", default=str(DEFAULT_P1039), help="P1039 JSON artifact")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Target label used for metadata")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    top = payload["summary"]["top_rules"][0] if payload["summary"]["top_rules"] else {}
    print(
        "claim={claim} witnesses={witnesses} primary_contrast_rules={primary} strict_diagnostic_rules={strict} top_rule={top} diag_false_selected={diag} out={out}".format(
            claim=payload["claim_status"],
            witnesses=len(payload["witnesses"]),
            primary=payload["summary"]["primary_contrast_rule_count"],
            strict=payload["summary"]["strict_diagnostic_rule_count"],
            top=top.get("name", "none"),
            diag=top.get("diagnostic_false_selected", "NA"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
