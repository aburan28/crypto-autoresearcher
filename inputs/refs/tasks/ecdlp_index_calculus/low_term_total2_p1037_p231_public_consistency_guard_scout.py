#!/usr/bin/env python3
"""P1037 public consistency guards for P1036 q-diverse adjacent families."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout as p1033
import low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion as p1035
import low_term_total2_p1036_p231_adjacent_family_supply_scout as p1036


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1037_p231_public_consistency_guard_scout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1037_p231_public_consistency_guard_scout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1037_p231_public_consistency_guard_scout.v1"
ORDER = p1033.ORDER
SIGNAL_WINDOW = p1036.SIGNAL_WINDOW
CONTROL_LABEL = "p1029_leaf8_scout_scout_compressed"
PRIMARY_LABEL = "all_target_rows_later_compressed"

GuardFn = Callable[[dict[str, Any]], bool]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def mod_abs_delta(left: int, right: int) -> int:
    delta = (left - right) % ORDER
    return min(delta, (-delta) % ORDER)


def later_windows() -> list[str]:
    return [window for window in p1025.FRESH_WINDOWS if window > SIGNAL_WINDOW]


def salt_values(form: dict[str, Any]) -> tuple[int, ...]:
    values = []
    for value in p1033.salt_tuple(form):
        if isinstance(value, int):
            values.append(value)
    return tuple(values)


def row_key_values(form: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(value) for value in p1033.row_keys(form))


def min_cross_gap(left: tuple[int, ...], right: tuple[int, ...]) -> int | None:
    if not left or not right:
        return None
    return min(abs(a - b) for a in left for b in right)


def family_features(form: dict[str, Any]) -> dict[str, Any]:
    terms = p1036.terms_tuple(form)
    tail = p1036.tail_support_tuple(form)
    term_gap = terms[2] - terms[0] if len(terms) >= 3 else None
    tail_width = tail[-1] - tail[0] if len(tail) == 2 else None
    tail_offsets = tuple(value - terms[0] for value in tail) if terms and len(tail) == 2 else ()
    return {
        "exact_tail_expression_key": str(form.get("exact_tail_expression_key") or ""),
        "motif_key": str(form.get("motif_key") or ""),
        "tail_offsets": list(tail_offsets),
        "tail_support": list(tail),
        "tail_width": tail_width,
        "term_gap": term_gap,
        "terms": list(terms),
    }


def build_events(
    forms: list[dict[str, Any]],
    factors: int,
    windows: list[str],
    label: str,
    pool_name: str,
    compressed: bool,
) -> list[dict[str, Any]]:
    events = []
    for spec in p1036.object_specs():
        groups: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
        for index, form in enumerate(forms):
            if p1036.form_window(form) not in windows or not p1036.is_repeated_two_tail(form):
                continue
            key = (p1036.public_key(form), p1036.form_window(form), json_key(spec["key_fn"](form)))
            groups[key].append((index, form))
        for (public, window, object_key), group in sorted(groups.items()):
            q_values = sorted({p1036.q_coeff(form) for _index, form in group})
            if len(group) < 2 or len(q_values) < 2:
                continue
            row_key_set = sorted({key for _index, form in group for key in row_key_values(form)})
            salt_set = sorted({salt for _index, form in group for salt in salt_values(form)})
            representative = group[0][1]
            family = family_features(representative)
            for left_offset, (left_index, left) in enumerate(group):
                for right_index, right in group[left_offset + 1 :]:
                    predicted = p1033.derive_target_from_pair(left, right, factors)
                    if predicted is None:
                        continue
                    left_salts = salt_values(left)
                    right_salts = salt_values(right)
                    left_rows = row_key_values(left)
                    right_rows = row_key_values(right)
                    source_secrets = sorted(
                        {
                            int_value(value) % ORDER
                            for value in [left.get("source_secret"), right.get("source_secret")]
                            if value is not None
                        }
                    )
                    verified = bool(source_secrets and all(predicted == secret for secret in source_secrets))
                    left_q = p1036.q_coeff(left)
                    right_q = p1036.q_coeff(right)
                    left_rhs = int_value(left.get("rhs")) % ORDER
                    right_rhs = int_value(right.get("rhs")) % ORDER
                    salt_gap = min_cross_gap(left_salts, right_salts)
                    event = {
                        "compressed": compressed,
                        "evaluation_label": label,
                        "family": family,
                        "group_form_count": len(group),
                        "group_q_count": len(q_values),
                        "group_row_key_count": len(row_key_set),
                        "group_salt_count": len(salt_set),
                        "left_index": left_index,
                        "left_q": left_q,
                        "left_rhs": left_rhs,
                        "left_row_keys": list(left_rows),
                        "left_salts": list(left_salts),
                        "model": spec["name"],
                        "object_key": object_key,
                        "pair_distinct_row_key": set(left_rows).isdisjoint(set(right_rows)),
                        "pair_distinct_salt": set(left_salts).isdisjoint(set(right_salts)),
                        "pair_same_row_key": bool(set(left_rows) & set(right_rows)),
                        "pair_same_salt": bool(set(left_salts) & set(right_salts)),
                        "pool": pool_name,
                        "predicted_target": predicted,
                        "public_fingerprint": public,
                        "q_delta_abs": mod_abs_delta(left_q, right_q),
                        "rhs_delta_abs": mod_abs_delta(left_rhs, right_rhs),
                        "right_index": right_index,
                        "right_q": right_q,
                        "right_rhs": right_rhs,
                        "right_row_keys": list(right_rows),
                        "right_salts": list(right_salts),
                        "row_key_set": row_key_set,
                        "salt_gap": salt_gap,
                        "salt_set": salt_set,
                        "source_secrets": source_secrets,
                        "toy_secret_verified": verified,
                        "window": window,
                    }
                    events.append(event)
    return events


def selected_rows_for_eval(
    pool: dict[str, Any],
    scout_by_window: dict[str, list[dict[str, Any]]],
    later_by_window: dict[str, list[dict[str, Any]]],
    region: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    predicate = pool["predicate"]
    if region == "scout":
        windows = [SIGNAL_WINDOW]
        rows = p1035.selected_rows_for_pool(scout_by_window, windows, predicate, "fresh_validation")
    else:
        windows = later_windows()
        rows = p1035.selected_rows_for_pool(later_by_window, windows, predicate, "fresh_validation")
    return rows, windows


def collect_events(
    scout_by_window: dict[str, list[dict[str, Any]]],
    later_by_window: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_events = []
    eval_meta = []
    for pool in p1035.pool_specs():
        for region in ("scout", "later"):
            rows, windows = selected_rows_for_eval(pool, scout_by_window, later_by_window, region)
            for compressed in (False, True):
                suffix = "compressed" if compressed else "raw"
                label = f"{pool['name']}_{region}_{suffix}"
                forms, meta = p1036.reconstruct_pool(rows, compressed)
                factors = int_value(meta.get("factor_count"))
                events = build_events(forms, factors, windows, label, pool["name"], compressed)
                all_events.extend(events)
                eval_meta.append(
                    {
                        "event_count": len(events),
                        "label": label,
                        "meta": meta,
                        "row_count": len(rows),
                        "windows": windows,
                    }
                )
    return all_events, eval_meta


def guard_catalog() -> list[dict[str, Any]]:
    guards: list[tuple[str, str, GuardFn]] = [
        ("all_predictions", "No guard; baseline.", lambda e: True),
        ("model_exact_tail", "Exact-tail object only.", lambda e: e["model"] == "exact_tail"),
        ("model_motif", "Motif object only.", lambda e: e["model"] == "motif"),
        ("model_exact_or_motif", "Exact-tail or motif object only.", lambda e: e["model"] in {"exact_tail", "motif"}),
        ("pair_distinct_salt", "Pair salts are disjoint.", lambda e: bool(e["pair_distinct_salt"])),
        ("pair_distinct_row_key", "Pair row keys are disjoint.", lambda e: bool(e["pair_distinct_row_key"])),
        ("salt_gap_ge_2", "Minimum pair salt gap at least 2.", lambda e: (e["salt_gap"] is not None and e["salt_gap"] >= 2)),
        ("salt_gap_ge_3", "Minimum pair salt gap at least 3.", lambda e: (e["salt_gap"] is not None and e["salt_gap"] >= 3)),
        ("salt_gap_ge_5", "Minimum pair salt gap at least 5.", lambda e: (e["salt_gap"] is not None and e["salt_gap"] >= 5)),
        ("group_forms_ge_3", "Object group has at least 3 forms.", lambda e: e["group_form_count"] >= 3),
        ("group_forms_ge_4", "Object group has at least 4 forms.", lambda e: e["group_form_count"] >= 4),
        ("group_q_count_ge_3", "Object group has at least 3 q values.", lambda e: e["group_q_count"] >= 3),
        ("group_q_count_ge_4", "Object group has at least 4 q values.", lambda e: e["group_q_count"] >= 4),
        ("group_salt_count_ge_2", "Object group has at least 2 salts.", lambda e: e["group_salt_count"] >= 2),
        ("group_salt_count_ge_3", "Object group has at least 3 salts.", lambda e: e["group_salt_count"] >= 3),
        ("term_gap_ge_2", "Repeated-term gap at least 2.", lambda e: int_value(e["family"].get("term_gap"), -999) >= 2),
        ("term_gap_ge_3", "Repeated-term gap at least 3.", lambda e: int_value(e["family"].get("term_gap"), -999) >= 3),
        ("tail_width_ge_2", "Tail support width at least 2.", lambda e: int_value(e["family"].get("tail_width"), -999) >= 2),
        ("tail_width_ge_3", "Tail support width at least 3.", lambda e: int_value(e["family"].get("tail_width"), -999) >= 3),
        ("q_delta_abs_ge_500", "Pair q delta at least 500 in modular absolute value.", lambda e: e["q_delta_abs"] >= 500),
        ("q_delta_abs_ge_1000", "Pair q delta at least 1000 in modular absolute value.", lambda e: e["q_delta_abs"] >= 1000),
        ("rhs_delta_abs_ge_500", "Pair rhs delta at least 500 in modular absolute value.", lambda e: e["rhs_delta_abs"] >= 500),
        ("rhs_delta_abs_ge_1000", "Pair rhs delta at least 1000 in modular absolute value.", lambda e: e["rhs_delta_abs"] >= 1000),
    ]
    combo_specs: list[tuple[str, str, list[str]]] = [
        ("distinct_salt_and_term_gap_ge_2", "Disjoint pair salts and term gap at least 2.", ["pair_distinct_salt", "term_gap_ge_2"]),
        ("distinct_salt_and_term_gap_ge_3", "Disjoint pair salts and term gap at least 3.", ["pair_distinct_salt", "term_gap_ge_3"]),
        ("salt_gap_ge_3_and_term_gap_ge_3", "Salt gap at least 3 and term gap at least 3.", ["salt_gap_ge_3", "term_gap_ge_3"]),
        ("group_forms_ge_3_and_term_gap_ge_2", "At least 3 forms and term gap at least 2.", ["group_forms_ge_3", "term_gap_ge_2"]),
        ("group_forms_ge_4_and_term_gap_ge_3", "At least 4 forms and term gap at least 3.", ["group_forms_ge_4", "term_gap_ge_3"]),
        ("group_q_ge_3_and_tail_width_ge_2", "At least 3 q values and tail width at least 2.", ["group_q_count_ge_3", "tail_width_ge_2"]),
        ("group_q_ge_4_and_tail_width_ge_3", "At least 4 q values and tail width at least 3.", ["group_q_count_ge_4", "tail_width_ge_3"]),
        ("exact_or_motif_salt_gap_ge_3", "Exact-tail/motif and salt gap at least 3.", ["model_exact_or_motif", "salt_gap_ge_3"]),
        ("exact_or_motif_group_forms_ge_4", "Exact-tail/motif and at least 4 group forms.", ["model_exact_or_motif", "group_forms_ge_4"]),
        ("term_gap_ge_3_q_delta_ge_500", "Term gap at least 3 and q delta at least 500.", ["term_gap_ge_3", "q_delta_abs_ge_500"]),
    ]
    guard_map = {name: fn for name, _description, fn in guards}
    for name, description, parts in combo_specs:
        guards.append((name, description, lambda e, parts=tuple(parts): all(guard_map[part](e) for part in parts)))
    return [{"description": description, "fn": fn, "name": name} for name, description, fn in guards]


def score_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    samples = []
    for event in events[:12]:
        samples.append(
            {
                "evaluation_label": event["evaluation_label"],
                "family": event["family"],
                "model": event["model"],
                "predicted_target": event["predicted_target"],
                "public_fingerprint": event["public_fingerprint"],
                "q_delta_abs": event["q_delta_abs"],
                "right_q": event["right_q"],
                "left_q": event["left_q"],
                "salt_gap": event["salt_gap"],
                "source_secrets": event["source_secrets"],
                "toy_secret_verified": event["toy_secret_verified"],
                "window": event["window"],
            }
        )
    return {
        "false_count": sum(1 for event in events if not event["toy_secret_verified"]),
        "prediction_count": len(events),
        "sample_predictions": samples,
        "true_count": sum(1 for event in events if event["toy_secret_verified"]),
    }


def evaluate_guards(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels = sorted({event["evaluation_label"] for event in events})
    out = []
    for guard in guard_catalog():
        by_label = {}
        selected_all = []
        for label in labels:
            selected = [event for event in events if event["evaluation_label"] == label and guard["fn"](event)]
            by_label[label] = score_events(selected)
            selected_all.extend(selected)
        control = by_label.get(CONTROL_LABEL, score_events([]))
        primary = by_label.get(PRIMARY_LABEL, score_events([]))
        raw_later_false = sum(
            summary["false_count"]
            for label, summary in by_label.items()
            if "_later_raw" in label
        )
        out.append(
            {
                "all_selected": score_events(selected_all),
                "control_preserved": control["true_count"] > 0 and control["false_count"] == 0,
                "description": guard["description"],
                "guard": guard["name"],
                "primary_false_witness_rejected": primary["false_count"] == 0,
                "primary_later_compressed": primary,
                "raw_later_false_count": raw_later_false,
                "scout_control": control,
                "selected_by_label": by_label,
            }
        )
    return out


def determine_claim(guard_results: list[dict[str, Any]]) -> str:
    primary_signals = [
        result
        for result in guard_results
        if result["control_preserved"]
        and result["primary_later_compressed"]["prediction_count"] > 0
        and result["primary_later_compressed"]["false_count"] == 0
    ]
    if primary_signals:
        return "P1037_PUBLIC_GUARD_LATER_COMPRESSED_SIGNAL"
    false_rejectors = [
        result
        for result in guard_results
        if result["control_preserved"] and result["primary_false_witness_rejected"]
    ]
    if false_rejectors:
        return "P1037_PUBLIC_GUARD_REJECTS_COMPRESSED_FALSE_WITNESS_NO_LATER_SIGNAL"
    if any(result["control_preserved"] for result in guard_results):
        return "NEGATIVE_RESULT_P1037_CONTROL_GUARDS_KEEP_FALSE_WITNESS"
    return "NEGATIVE_RESULT_P1037_NO_GUARD_PRESERVES_CONTROL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    scout_by_window, scout_exists = p1035.load_rows([SIGNAL_WINDOW], args.targets, args.min_source_rank)
    later_by_window, later_exists = p1035.load_rows(later_windows(), args.targets, args.min_source_rank)
    events, eval_meta = collect_events(scout_by_window, later_by_window)
    guard_results = evaluate_guards(events)
    claim = determine_claim(guard_results)
    all_windows = [SIGNAL_WINDOW, *later_windows()]
    source_hashes = {
        window: p1005.sha256_file(p1007.expanded_source_path(window))
        for window in all_windows
        if p1007.expanded_source_path(window).exists()
    }
    false_rejectors = [
        result
        for result in guard_results
        if result["control_preserved"] and result["primary_false_witness_rejected"]
    ]
    primary_signals = [
        result
        for result in false_rejectors
        if result["primary_later_compressed"]["prediction_count"] > 0
    ]
    ranked_false_rejectors = sorted(
        false_rejectors,
        key=lambda result: (
            -int_value(result["scout_control"]["true_count"]),
            int_value(result["raw_later_false_count"]),
            result["guard"],
        ),
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1036_dependency_sha256": p1005.sha256_file(Path(p1036.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1037_") else "NEGATIVE RESULT",
        "event_count": len(events),
        "evaluation_meta": eval_meta,
        "guard_results": guard_results,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FINITE-CATALOG: P1037 tests a finite public guard list, not every possible consistency law.",
            "COMPRESSED-PRIMARY: row-signature-compressed later context is primary; raw-form results are duplicate-sensitive diagnostics.",
            "INDEX-CALCULUS PRECURSOR: this is relation-generation guardability, not sparse linear algebra or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "control_label": CONTROL_LABEL,
            "guard_count": len(guard_catalog()),
            "later_windows": later_windows(),
            "min_source_rank": args.min_source_rank,
            "primary_label": PRIMARY_LABEL,
            "signal_window": SIGNAL_WINDOW,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {
            "later_exists": later_exists,
            "scout_exists": scout_exists,
        },
        "summary": {
            "claim_status": claim,
            "control_preserving_guard_count": sum(1 for result in guard_results if result["control_preserved"]),
            "false_witness_rejecting_guard_count": len(false_rejectors),
            "primary_signal_guard_count": len(primary_signals),
            "top_false_witness_rejecting_guards": [
                {
                    "guard": result["guard"],
                    "primary_prediction_count": result["primary_later_compressed"]["prediction_count"],
                    "primary_false_count": result["primary_later_compressed"]["false_count"],
                    "raw_later_false_count": result["raw_later_false_count"],
                    "scout_true_count": result["scout_control"]["true_count"],
                }
                for result in ranked_false_rejectors[:12]
            ],
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    bits = [
        "{guard}:control_true={control_true} primary_pred={primary_pred} primary_false={primary_false} raw_false={raw_false}".format(
            guard=item["guard"],
            control_true=item["scout_true_count"],
            primary_pred=item["primary_prediction_count"],
            primary_false=item["primary_false_count"],
            raw_false=item["raw_later_false_count"],
        )
        for item in payload["summary"]["top_false_witness_rejecting_guards"][:6]
    ]
    print(
        "claim={claim} guards={guards} rejectors={rejectors} signals={signals} out={out} {bits}".format(
            claim=payload["claim_status"],
            guards=payload["summary"]["control_preserving_guard_count"],
            rejectors=payload["summary"]["false_witness_rejecting_guard_count"],
            signals=payload["summary"]["primary_signal_guard_count"],
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
