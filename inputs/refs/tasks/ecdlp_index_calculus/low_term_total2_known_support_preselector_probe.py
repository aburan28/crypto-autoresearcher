#!/usr/bin/env python3
"""Probe public preselectors for known-factor one-relation descent.

The known-factor holdout descent probe showed that some fresh direct-source
relation forms recover a toy target using only factor columns already derived
from the training bank.  This script asks the next operational question:
can public, pre-relation selected-leaf features predict those useful forms
well enough to reduce the search-cost proxy?

This is a retrospective toy diagnostic.  It uses a calibration split to choose
public predicates and reports the later holdout slice separately.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable


Predicate = Callable[[dict[str, Any]], bool]
SALT_RE = re.compile(r"salt(\d+)")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_paths(raw: str) -> list[Path]:
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def salt_numbers(row_keys: list[Any]) -> list[int]:
    salts: list[int] = []
    for row_key in row_keys:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return salts


def cert_key_from_cert(cert: dict[str, Any]) -> tuple[str, int]:
    return (str(cert.get("_artifact")), int_value(cert.get("_artifact_offset")))


def cert_key_from_recovery(item: dict[str, Any]) -> tuple[str, int]:
    return (str(item.get("artifact")), int_value(item.get("artifact_offset")))


def event_key(item: dict[str, Any]) -> tuple[str, int, str, int]:
    return (
        str(item.get("target")),
        int_value(item.get("transfer_index")),
        str(item.get("selector")),
        int_value(item.get("top_k")),
    )


def event_row_key(item: dict[str, Any]) -> tuple[str, int, str, int, tuple[str, ...]]:
    return (*event_key(item), tuple(str(row) for row in item.get("row_keys") or []))


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    value = cert.get("selected")
    return value if isinstance(value, dict) else {}


def direct_cost(cert: dict[str, Any]) -> float | None:
    return float_value(selected(cert).get("direct_ops_over_rho"))


def form_support(form: dict[str, Any], order: int) -> list[int]:
    coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
    return [idx for idx, coeff in enumerate(coeffs[1:]) if coeff % order]


def load_certificates(paths: list[Path]) -> list[dict[str, Any]]:
    certs: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for offset, cert in enumerate(payload.get("certificates") or []):
            if not isinstance(cert, dict):
                continue
            item = dict(cert)
            item["_artifact"] = str(path)
            item["_artifact_offset"] = offset
            certs.append(item)
    return certs


def load_scout_reports(paths: list[Path]) -> tuple[dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]], dict[tuple[str, int, str, int], list[dict[str, Any]]]]:
    by_row_key: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    by_event_key: dict[tuple[str, int, str, int], list[dict[str, Any]]] = defaultdict(list)
    for path in paths:
        payload = load_json(path)
        for report in payload.get("case_reports") or []:
            if not isinstance(report, dict):
                continue
            item = dict(report)
            item["_scout_artifact"] = str(path)
            by_row_key[event_row_key(item)] = item
            by_event_key[event_key(item)].append(item)
    return by_row_key, by_event_key


def annotate_items(
    certs: list[dict[str, Any]],
    descent: dict[str, Any],
    scout_paths: list[Path],
) -> list[dict[str, Any]]:
    scout_by_row_key, scout_by_event_key = load_scout_reports(scout_paths)
    recoveries = [
        item
        for item in descent.get("recoveries") or []
        if any(form.get("matches_expected_secret") for form in item.get("form_recoveries") or [])
    ]
    recovery_by_key = {cert_key_from_recovery(item): item for item in recoveries}
    items: list[dict[str, Any]] = []
    for cert in certs:
        sel = selected(cert)
        key = cert_key_from_cert(cert)
        scout = scout_by_row_key.get(event_row_key(sel))
        if scout is None:
            matches = scout_by_event_key.get(event_key(sel), [])
            scout = matches[0] if len(matches) == 1 else {}
        order = int_value(cert.get("order"))
        support_from_forms = sorted(
            {
                idx
                for form in cert.get("forms") or []
                if isinstance(form, dict)
                for idx in form_support(form, order)
            }
        )
        selected_support = sorted(
            {
                int_value(value)
                for value in (
                    scout.get("selected_term_support")
                    or cert.get("selected_term_support")
                    or []
                )
            }
        )
        recovery = recovery_by_key.get(key)
        matching_supports = []
        if recovery is not None:
            for form in recovery.get("form_recoveries") or []:
                if form.get("matches_expected_secret"):
                    matching_supports.append(sorted(int_value(idx) for idx in form.get("support") or []))
        row_keys = sel.get("row_keys") or []
        salts = salt_numbers(row_keys)
        salt_abs_gap = abs(salts[1] - salts[0]) if len(salts) >= 2 else None
        salt_signed_gap = salts[1] - salts[0] if len(salts) >= 2 else None
        items.append(
            {
                "artifact": cert.get("_artifact"),
                "artifact_offset": int_value(cert.get("_artifact_offset")),
                "cert_key": key,
                "direct_cost_over_rho": direct_cost(cert),
                "form_support_union": support_from_forms,
                "is_matching_recovery": recovery is not None,
                "matching_supports": matching_supports,
                "order": order,
                "row_keys": row_keys,
                "row_key_salts": salts,
                "salt_abs_gap": salt_abs_gap,
                "salt_first_lt_second": salts[0] < salts[1] if len(salts) >= 2 else None,
                "salt_max": max(salts) if salts else None,
                "salt_min": min(salts) if salts else None,
                "salt_signed_gap": salt_signed_gap,
                "salt_sum": sum(salts) if salts else None,
                "scout_artifact": scout.get("_scout_artifact"),
                "selected_support": selected_support,
                "selector": sel.get("selector"),
                "target": sel.get("target"),
                "top_k": int_value(sel.get("top_k")),
                "transfer_index": int_value(sel.get("transfer_index")),
            }
        )
    return items


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0.0}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
        "sum": round(sum(values), 8),
    }


def evaluate(items: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    selected_items = [item for item in items if predicate(item)]
    selected_matching = [item for item in selected_items if item["is_matching_recovery"]]
    all_matching = [item for item in items if item["is_matching_recovery"]]
    costs = [item["direct_cost_over_rho"] for item in selected_items if item.get("direct_cost_over_rho") is not None]
    cost_sum = sum(costs)
    cost_per_recovery = cost_sum / len(selected_matching) if selected_matching else None
    return {
        "cost_over_rho": stat(costs),
        "cost_per_matching_recovery_over_rho": (
            round(cost_per_recovery, 8) if cost_per_recovery is not None else None
        ),
        "matching_recovery_count": len(selected_matching),
        "precision": round(len(selected_matching) / len(selected_items), 8) if selected_items else None,
        "recall": round(len(selected_matching) / len(all_matching), 8) if all_matching else None,
        "selected_certificate_count": len(selected_items),
        "total_certificate_count": len(items),
        "total_matching_recovery_count": len(all_matching),
    }


def sample_items(items: list[dict[str, Any]], predicate: Predicate, limit: int = 12) -> list[dict[str, Any]]:
    rows = []
    for item in sorted(
        (candidate for candidate in items if predicate(candidate)),
        key=lambda candidate: (
            int_value(candidate.get("transfer_index")),
            int_value(candidate.get("top_k")),
            str(candidate.get("artifact")),
            int_value(candidate.get("artifact_offset")),
        ),
    )[:limit]:
        rows.append(
            {
                "artifact": item.get("artifact"),
                "artifact_offset": item.get("artifact_offset"),
                "direct_cost_over_rho": item.get("direct_cost_over_rho"),
                "is_matching_recovery": item.get("is_matching_recovery"),
                "matching_supports": item.get("matching_supports"),
                "row_key_salts": item.get("row_key_salts"),
                "row_keys": item.get("row_keys"),
                "salt_abs_gap": item.get("salt_abs_gap"),
                "salt_first_lt_second": item.get("salt_first_lt_second"),
                "salt_sum": item.get("salt_sum"),
                "selected_support": item.get("selected_support"),
                "top_k": item.get("top_k"),
                "transfer_index": item.get("transfer_index"),
            }
        )
    return rows


def transfer_evaluate(items: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    by_transfer: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_transfer[(str(item.get("target")), int_value(item.get("transfer_index")))].append(item)
    costs: list[float] = []
    selected_transfers = 0
    matching_transfers = 0
    total_matching_transfers = 0
    for group in by_transfer.values():
        if any(item["is_matching_recovery"] for item in group):
            total_matching_transfers += 1
        chosen = [item for item in group if predicate(item)]
        if not chosen:
            continue
        selected_transfers += 1
        group_costs = [item["direct_cost_over_rho"] for item in chosen if item.get("direct_cost_over_rho") is not None]
        if group_costs:
            costs.append(min(group_costs))
        if any(item["is_matching_recovery"] for item in chosen):
            matching_transfers += 1
    cost_sum = sum(costs)
    cost_per_matching = cost_sum / matching_transfers if matching_transfers else None
    return {
        "cost_over_rho_min_per_selected_transfer": stat(costs),
        "cost_per_matching_transfer_over_rho": (
            round(cost_per_matching, 8) if cost_per_matching is not None else None
        ),
        "matching_transfer_count": matching_transfers,
        "recall": round(matching_transfers / total_matching_transfers, 8) if total_matching_transfers else None,
        "selected_transfer_count": selected_transfers,
        "total_matching_transfer_count": total_matching_transfers,
        "total_transfer_count": len(by_transfer),
    }


def support_set(item: dict[str, Any]) -> set[int]:
    return {int_value(value) for value in item.get("selected_support") or []}


def has_salt_pair(item: dict[str, Any]) -> bool:
    return item.get("salt_abs_gap") is not None


def salt_int(item: dict[str, Any], key: str) -> int | None:
    value = item.get(key)
    return value if isinstance(value, int) else None


def build_predicates(calibration_items: list[dict[str, Any]], known_columns: set[int]) -> dict[str, Predicate]:
    recovery_pairs = sorted(
        {
            tuple(support)
            for item in calibration_items
            if item["is_matching_recovery"]
            for support in item.get("matching_supports") or []
            if len(support) == 2
        }
    )
    predicates: dict[str, Predicate] = {
        "all": lambda _item: True,
        "selector_lowterm_support_total5": lambda item: str(item.get("selector")) == "mode_low_term_support_total5",
        "topk_7_or_12": lambda item: int_value(item.get("top_k")) in {7, 12},
        "selector_lowterm5_topk_7_or_12": lambda item: str(item.get("selector")) == "mode_low_term_support_total5"
        and int_value(item.get("top_k")) in {7, 12},
        "selected_support_contains_11": lambda item: 11 in support_set(item),
    }

    def add_combined_public_predicates(label: str, predicate: Predicate) -> None:
        predicates[label] = predicate
        predicates[f"selector_lowterm5_topk_7_or_12_and_{label}"] = (
            lambda item, inner=predicate: str(item.get("selector")) == "mode_low_term_support_total5"
            and int_value(item.get("top_k")) in {7, 12}
            and inner(item)
        )
        for limit in range(6, 15):
            predicates[f"selected_support_size_le_{limit}_and_{label}"] = (
                lambda item, inner=predicate, threshold=limit: len(support_set(item)) <= threshold
                and inner(item)
            )
            predicates[f"selector_lowterm5_topk_7_or_12_support_size_le_{limit}_and_{label}"] = (
                lambda item, inner=predicate, threshold=limit: str(item.get("selector")) == "mode_low_term_support_total5"
                and int_value(item.get("top_k")) in {7, 12}
                and len(support_set(item)) <= threshold
                and inner(item)
            )

    add_combined_public_predicates("salt_pair_present", has_salt_pair)
    for parity in range(2):
        add_combined_public_predicates(
            f"salt_gap_parity_{parity}",
            lambda item, wanted=parity: has_salt_pair(item)
            and (int_value(item.get("salt_abs_gap")) % 2) == wanted,
        )
        add_combined_public_predicates(
            f"salt_sum_parity_{parity}",
            lambda item, wanted=parity: salt_int(item, "salt_sum") is not None
            and (int_value(item.get("salt_sum")) % 2) == wanted,
        )
    for modulus in (3, 4, 5, 8):
        for residue in range(modulus):
            add_combined_public_predicates(
                f"salt_gap_mod_{modulus}_eq_{residue}",
                lambda item, mod=modulus, wanted=residue: has_salt_pair(item)
                and (int_value(item.get("salt_abs_gap")) % mod) == wanted,
            )
            add_combined_public_predicates(
                f"salt_sum_mod_{modulus}_eq_{residue}",
                lambda item, mod=modulus, wanted=residue: salt_int(item, "salt_sum") is not None
                and (int_value(item.get("salt_sum")) % mod) == wanted,
            )
    for threshold in range(0, 17):
        add_combined_public_predicates(
            f"salt_abs_gap_le_{threshold}",
            lambda item, limit=threshold: has_salt_pair(item) and int_value(item.get("salt_abs_gap")) <= limit,
        )
        add_combined_public_predicates(
            f"salt_abs_gap_ge_{threshold}",
            lambda item, limit=threshold: has_salt_pair(item) and int_value(item.get("salt_abs_gap")) >= limit,
        )
    for threshold in range(160, 181):
        add_combined_public_predicates(
            f"salt_min_le_{threshold}",
            lambda item, limit=threshold: salt_int(item, "salt_min") is not None
            and int_value(item.get("salt_min")) <= limit,
        )
        add_combined_public_predicates(
            f"salt_max_ge_{threshold}",
            lambda item, limit=threshold: salt_int(item, "salt_max") is not None
            and int_value(item.get("salt_max")) >= limit,
        )
    add_combined_public_predicates(
        "salt_first_lt_second",
        lambda item: item.get("salt_first_lt_second") is True,
    )
    add_combined_public_predicates(
        "salt_first_gt_second",
        lambda item: item.get("salt_first_lt_second") is False,
    )
    for pair in recovery_pairs:
        label = "selected_support_contains_pair_" + "_".join(str(value) for value in pair)

        def predicate(item: dict[str, Any], wanted: tuple[int, ...] = pair) -> bool:
            support = support_set(item)
            return all(value in support for value in wanted)

        predicates[label] = predicate
        predicates["selector_lowterm5_topk_7_or_12_and_" + label] = (
            lambda item, wanted=pair: str(item.get("selector")) == "mode_low_term_support_total5"
            and int_value(item.get("top_k")) in {7, 12}
            and all(value in support_set(item) for value in wanted)
        )
    for count in range(2, max(known_columns) + 1 if known_columns else 3):
        predicates[f"known_overlap_ge_{count}"] = (
            lambda item, threshold=count: len(support_set(item) & known_columns) >= threshold
        )
    for limit in range(2, 9):
        predicates[f"unknown_support_count_le_{limit}"] = (
            lambda item, threshold=limit: len(support_set(item) - known_columns) <= threshold
        )
        predicates[f"selector_lowterm5_topk_7_or_12_unknown_support_count_le_{limit}"] = (
            lambda item, threshold=limit: str(item.get("selector")) == "mode_low_term_support_total5"
            and int_value(item.get("top_k")) in {7, 12}
            and len(support_set(item) - known_columns) <= threshold
        )
    for limit in range(6, 15):
        predicates[f"selected_support_size_le_{limit}"] = (
            lambda item, threshold=limit: len(support_set(item)) <= threshold
        )
        predicates[f"selector_lowterm5_topk_7_or_12_support_size_le_{limit}"] = (
            lambda item, threshold=limit: str(item.get("selector")) == "mode_low_term_support_total5"
            and int_value(item.get("top_k")) in {7, 12}
            and len(support_set(item)) <= threshold
        )
    return predicates


def rank_key(metrics: dict[str, Any]) -> tuple[float, float, int]:
    cost = metrics.get("cost_per_matching_recovery_over_rho")
    precision = metrics.get("precision")
    selected_count = int_value(metrics.get("selected_certificate_count"))
    return (
        float(cost) if isinstance(cost, (int, float)) else 1e9,
        -(float(precision) if isinstance(precision, (int, float)) else -1.0),
        selected_count,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--holdout-descent", required=True)
    parser.add_argument("--holdout-certificates", required=True)
    parser.add_argument("--scouts", required=True)
    parser.add_argument("--calibration-max-transfer", type=int, default=2527)
    parser.add_argument("--future-tail-min-transfer", type=int)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    descent_path = Path(args.holdout_descent)
    descent = load_json(descent_path)
    cert_paths = parse_paths(args.holdout_certificates)
    scout_paths = parse_paths(args.scouts)
    certs = load_certificates(cert_paths)
    items = annotate_items(certs, descent, scout_paths)

    known_columns = {
        int_value(column)
        for columns in (descent.get("known_factor_columns") or {}).values()
        for column in columns
    }
    calibration_items = [item for item in items if int_value(item.get("transfer_index")) <= args.calibration_max_transfer]
    validation_items = [item for item in items if int_value(item.get("transfer_index")) > args.calibration_max_transfer]
    predicates = build_predicates(calibration_items, known_columns)

    full_results: dict[str, Any] = {}
    calibration_results: dict[str, Any] = {}
    validation_results: dict[str, Any] = {}
    for name, predicate in sorted(predicates.items()):
        full_results[name] = {
            **evaluate(items, predicate),
            "transfer_metrics": transfer_evaluate(items, predicate),
        }
        calibration_results[name] = evaluate(calibration_items, predicate)
        validation_results[name] = {
            **evaluate(validation_items, predicate),
            "transfer_metrics": transfer_evaluate(validation_items, predicate),
        }

    calibration_viable = [
        (name, metrics)
        for name, metrics in calibration_results.items()
        if int_value(metrics.get("matching_recovery_count")) > 0
    ]
    selected_name = min(calibration_viable, key=lambda pair: rank_key(pair[1]))[0] if calibration_viable else "all"
    selected_validation = validation_results[selected_name]
    baseline_validation = validation_results["all"]
    frozen_predicate_checks: dict[str, Any] = {}
    frozen_names = ["selected_support_size_le_10"]
    if selected_name not in frozen_names:
        frozen_names.append(selected_name)
    if args.future_tail_min_transfer is not None:
        future_tail_items = [
            item
            for item in items
            if int_value(item.get("transfer_index")) > args.future_tail_min_transfer
        ]
        old_validation_items = [
            item
            for item in items
            if args.calibration_max_transfer < int_value(item.get("transfer_index")) <= args.future_tail_min_transfer
        ]
        for name in frozen_names:
            predicate = predicates.get(name)
            if predicate is None:
                continue
            frozen_predicate_checks[name] = {
                "expanded_validation": {
                    **evaluate(validation_items, predicate),
                    "transfer_metrics": transfer_evaluate(validation_items, predicate),
                },
                "future_tail": {
                    **evaluate(future_tail_items, predicate),
                    "min_transfer_exclusive": args.future_tail_min_transfer,
                    "transfer_metrics": transfer_evaluate(future_tail_items, predicate),
                },
                "old_validation": {
                    **evaluate(old_validation_items, predicate),
                    "max_transfer_inclusive": args.future_tail_min_transfer,
                    "min_transfer_exclusive": args.calibration_max_transfer,
                    "transfer_metrics": transfer_evaluate(old_validation_items, predicate),
                },
            }
    selected_cost = selected_validation.get("cost_per_matching_recovery_over_rho")
    baseline_cost = baseline_validation.get("cost_per_matching_recovery_over_rho")
    if isinstance(selected_cost, (int, float)) and selected_cost < 1.0:
        claim_status = "KNOWN_SUPPORT_PRESELECTOR_VALIDATES_BELOW_RHO_SIGNAL"
    elif (
        isinstance(selected_cost, (int, float))
        and isinstance(baseline_cost, (int, float))
        and selected_cost < baseline_cost
    ):
        claim_status = "KNOWN_SUPPORT_PRESELECTOR_REDUCES_COST_NEEDS_MORE_GAIN"
    else:
        claim_status = "KNOWN_SUPPORT_PRESELECTOR_NO_VALIDATED_COST_GAIN"

    payload = {
        "artifacts": {
            "holdout_certificates": [str(path) for path in cert_paths],
            "holdout_descent": str(descent_path),
            "scouts": [str(path) for path in scout_paths],
        },
        "calibration_max_transfer": args.calibration_max_transfer,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": {
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HEURISTIC-COST",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "source-charged shared-product collector",
                "deployment-relevant break",
            ],
            "scope": "Retrospective public-feature preselector over direct-source toy certificates; validation split is later transfers only.",
        },
        "known_factor_columns": sorted(known_columns),
        "predicate_results": {
            "calibration": calibration_results,
            "full": full_results,
            "validation": validation_results,
        },
        "frozen_predicate_checks": frozen_predicate_checks,
        "schema": "ecdlp.low_term_total2_known_support_preselector_probe.v1",
        "selected_by_calibration": {
            "baseline_validation": baseline_validation,
            "name": selected_name,
            "validation_selected_samples": sample_items(validation_items, predicates[selected_name]),
            "validation": selected_validation,
        },
        "top_validation_predicates": [
            {"name": name, **metrics}
            for name, metrics in sorted(
                validation_results.items(),
                key=lambda pair: rank_key(pair[1]),
            )[:12]
        ],
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["selected_by_calibration"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
