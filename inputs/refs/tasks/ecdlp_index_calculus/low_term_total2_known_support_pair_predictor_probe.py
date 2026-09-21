#!/usr/bin/env python3
"""Probe public predictors for known-factor support pairs.

The support10 scheduled collector failed in the important way: public selected
leaf support was small, but the later direct relation forms often landed on
factor columns outside the known-factor subspace, or landed inside it without
recovering the toy target.  This probe separates those two events.

Labels:
  * structural known-support form: a direct relation form has nonzero target
    coefficient and nonempty factor support fully inside known factor columns.
  * matching recovery: a provided holdout-descent report derives the expected
    toy secret from a known-support form.

Predicates use only scout/selection metadata available before direct
verification.  Direct public-key verification is reported as context, never as
a predictor.
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


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
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


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    value = cert.get("selected")
    return value if isinstance(value, dict) else {}


def direct_cost(cert: dict[str, Any]) -> float | None:
    return float_value(selected(cert).get("direct_ops_over_rho"))


def salt_numbers(row_keys: list[Any]) -> list[int]:
    salts: list[int] = []
    for row_key in row_keys:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return salts


def event_key(item: dict[str, Any]) -> tuple[str, int, str, int]:
    return (
        str(item.get("target")),
        int_value(item.get("transfer_index")),
        str(item.get("selector")),
        int_value(item.get("top_k")),
    )


def event_row_key(item: dict[str, Any]) -> tuple[str, int, str, int, tuple[str, ...]]:
    return (*event_key(item), tuple(str(row) for row in item.get("row_keys") or []))


def cert_lookup_keys(artifact: Any, offset: Any) -> list[tuple[str, int]]:
    artifact_text = str(artifact)
    offset_int = int_value(offset)
    return [
        (artifact_text, offset_int),
        (Path(artifact_text).name, offset_int),
    ]


def cert_keys_from_cert(cert: dict[str, Any]) -> list[tuple[str, int]]:
    return cert_lookup_keys(cert.get("_artifact"), cert.get("_artifact_offset"))


def cert_keys_from_recovery(item: dict[str, Any]) -> list[tuple[str, int]]:
    return cert_lookup_keys(item.get("artifact"), item.get("artifact_offset"))


def coeff_support(form: dict[str, Any], order: int) -> dict[str, Any]:
    coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
    if not coeffs:
        return {
            "support": [],
            "target_coefficient": 0,
            "terms": form.get("terms") or [],
        }
    return {
        "support": [idx for idx, coeff in enumerate(coeffs[1:]) if coeff % order],
        "target_coefficient": coeffs[0] % order,
        "terms": form.get("terms") or [],
    }


def load_certificates(paths: list[Path], cohort: str) -> list[dict[str, Any]]:
    certs: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for offset, cert in enumerate(payload.get("certificates") or []):
            if not isinstance(cert, dict):
                continue
            item = dict(cert)
            item["_artifact"] = str(path)
            item["_artifact_basename"] = path.name
            item["_artifact_offset"] = offset
            item["_cohort"] = cohort
            certs.append(item)
    return certs


def load_scout_reports(
    paths: list[Path],
) -> tuple[
    dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]],
    dict[tuple[str, int, str, int], list[dict[str, Any]]],
]:
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


def load_descent_reports(paths: list[Path]) -> tuple[set[int], dict[tuple[str, int], dict[str, Any]]]:
    known_columns: set[int] = set()
    labels: dict[tuple[str, int], dict[str, Any]] = {}
    for path in paths:
        payload = load_json(path)
        for columns in (payload.get("known_factor_columns") or {}).values():
            known_columns.update(int_value(column) for column in columns)
        for item in payload.get("recoveries") or []:
            if not isinstance(item, dict):
                continue
            form_recoveries = [
                form
                for form in item.get("form_recoveries") or []
                if isinstance(form, dict)
            ]
            record = {
                "descent_artifact": str(path),
                "descent_has_recoverable_form": any(form.get("recoverable") for form in form_recoveries),
                "descent_matching_supports": [
                    sorted(int_value(idx) for idx in form.get("support") or [])
                    for form in form_recoveries
                    if form.get("matches_expected_secret")
                ],
                "descent_recoverable_supports": [
                    sorted(int_value(idx) for idx in form.get("support") or [])
                    for form in form_recoveries
                    if form.get("recoverable")
                ],
                "has_descent_label": True,
                "is_matching_recovery": any(form.get("matches_expected_secret") for form in form_recoveries),
            }
            for key in cert_keys_from_recovery(item):
                labels[key] = record
    return known_columns, labels


def match_scout(
    cert: dict[str, Any],
    scout_by_row_key: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]],
    scout_by_event_key: dict[tuple[str, int, str, int], list[dict[str, Any]]],
) -> dict[str, Any]:
    sel = selected(cert)
    scout = scout_by_row_key.get(event_row_key(sel))
    if scout is not None:
        return scout
    matches = scout_by_event_key.get(event_key(sel), [])
    return matches[0] if len(matches) == 1 else {}


def annotate_items(
    certs: list[dict[str, Any]],
    scout_paths: list[Path],
    known_columns: set[int],
    descent_labels: dict[tuple[str, int], dict[str, Any]],
) -> list[dict[str, Any]]:
    scout_by_row_key, scout_by_event_key = load_scout_reports(scout_paths)
    items: list[dict[str, Any]] = []
    for cert in certs:
        sel = selected(cert)
        scout = match_scout(cert, scout_by_row_key, scout_by_event_key)
        order = int_value(cert.get("order"))
        form_records = []
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            info = coeff_support(form, order)
            support = [int_value(idx) for idx in info["support"]]
            target_coeff = int_value(info["target_coefficient"])
            form_records.append(
                {
                    "form_index": form_index,
                    "is_known_support_candidate": bool(
                        target_coeff and support and set(support).issubset(known_columns)
                    ),
                    "is_unknown_support_candidate": bool(support and not set(support).issubset(known_columns)),
                    "support": support,
                    "target_coefficient": target_coeff,
                    "terms": info.get("terms") or [],
                }
            )
        known_supports = sorted(
            {
                tuple(record["support"])
                for record in form_records
                if record["is_known_support_candidate"]
            }
        )
        unknown_supports = sorted(
            {
                tuple(record["support"])
                for record in form_records
                if record["is_unknown_support_candidate"]
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
        label: dict[str, Any] = {"has_descent_label": False, "is_matching_recovery": False}
        for key in cert_keys_from_cert(cert):
            if key in descent_labels:
                label = descent_labels[key]
                break
        row_keys = sel.get("row_keys") or []
        salts = salt_numbers(row_keys)
        item = {
            "artifact": cert.get("_artifact"),
            "artifact_basename": cert.get("_artifact_basename"),
            "artifact_offset": int_value(cert.get("_artifact_offset")),
            "certificate_status": cert.get("certificate_status"),
            "cohort": cert.get("_cohort"),
            "direct_cost_over_rho": direct_cost(cert),
            "direct_public_key_verified": cert.get("public_key_verified"),
            "form_count": len(form_records),
            "form_records": form_records,
            "has_descent_label": bool(label.get("has_descent_label")),
            "has_known_support_form": bool(known_supports),
            "has_unknown_support_form": bool(unknown_supports),
            "is_matching_recovery": bool(label.get("is_matching_recovery")),
            "known_form_support_pairs": [list(support) for support in known_supports if len(support) == 2],
            "known_form_supports": [list(support) for support in known_supports],
            "order": order,
            "row_keys": row_keys,
            "row_key_salts": salts,
            "salt_abs_gap": abs(salts[1] - salts[0]) if len(salts) >= 2 else None,
            "salt_first_lt_second": salts[0] < salts[1] if len(salts) >= 2 else None,
            "salt_max": max(salts) if salts else None,
            "salt_min": min(salts) if salts else None,
            "salt_signed_gap": salts[1] - salts[0] if len(salts) >= 2 else None,
            "salt_sum": sum(salts) if salts else None,
            "scout_artifact": scout.get("_scout_artifact"),
            "scout_direct_public_key_verified": scout.get("direct_public_key_verified"),
            "scout_public_product_gate_selected": scout.get("public_product_gate_selected"),
            "selected_support": selected_support,
            "selector": sel.get("selector"),
            "target": sel.get("target"),
            "top_k": int_value(sel.get("top_k")),
            "transfer_index": int_value(sel.get("transfer_index")),
            "unknown_form_support_pairs": [list(support) for support in unknown_supports if len(support) == 2],
            "unknown_form_supports": [list(support) for support in unknown_supports],
            "window": cert.get("window"),
        }
        item.update(
            {
                "descent_artifact": label.get("descent_artifact"),
                "descent_has_recoverable_form": bool(label.get("descent_has_recoverable_form")),
                "descent_matching_supports": label.get("descent_matching_supports") or [],
                "descent_recoverable_supports": label.get("descent_recoverable_supports") or [],
            }
        )
        items.append(item)
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


def evaluate(items: list[dict[str, Any]], predicate: Predicate, label_key: str) -> dict[str, Any]:
    selected_items = [item for item in items if predicate(item)]
    selected_positive = [item for item in selected_items if item.get(label_key)]
    all_positive = [item for item in items if item.get(label_key)]
    selected_matching = [item for item in selected_items if item.get("is_matching_recovery")]
    all_matching = [item for item in items if item.get("is_matching_recovery")]
    costs = [item["direct_cost_over_rho"] for item in selected_items if item.get("direct_cost_over_rho") is not None]
    cost_sum = sum(costs)
    cost_per_positive = cost_sum / len(selected_positive) if selected_positive else None
    cost_per_matching = cost_sum / len(selected_matching) if selected_matching else None
    return {
        "cost_over_rho": stat(costs),
        "cost_per_matching_recovery_over_rho": (
            round(cost_per_matching, 8) if cost_per_matching is not None else None
        ),
        "cost_per_positive_over_rho": (
            round(cost_per_positive, 8) if cost_per_positive is not None else None
        ),
        "direct_verified_selected_count": sum(1 for item in selected_items if item.get("direct_public_key_verified")),
        "has_descent_label_count": sum(1 for item in selected_items if item.get("has_descent_label")),
        "matching_recovery_count": len(selected_matching),
        "precision": round(len(selected_positive) / len(selected_items), 8) if selected_items else None,
        "positive_count": len(selected_positive),
        "recall": round(len(selected_positive) / len(all_positive), 8) if all_positive else None,
        "selected_certificate_count": len(selected_items),
        "total_certificate_count": len(items),
        "total_matching_recovery_count": len(all_matching),
        "total_positive_count": len(all_positive),
    }


def transfer_evaluate(items: list[dict[str, Any]], predicate: Predicate, label_key: str) -> dict[str, Any]:
    by_transfer: dict[tuple[str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_transfer[
            (
                str(item.get("target")),
                int_value(item.get("transfer_index")),
                str(item.get("cohort")),
            )
        ].append(item)
    costs: list[float] = []
    selected_transfers = 0
    positive_transfers = 0
    matching_transfers = 0
    total_positive_transfers = 0
    total_matching_transfers = 0
    for group in by_transfer.values():
        if any(item.get(label_key) for item in group):
            total_positive_transfers += 1
        if any(item.get("is_matching_recovery") for item in group):
            total_matching_transfers += 1
        chosen = [item for item in group if predicate(item)]
        if not chosen:
            continue
        selected_transfers += 1
        group_costs = [item["direct_cost_over_rho"] for item in chosen if item.get("direct_cost_over_rho") is not None]
        if group_costs:
            costs.append(min(group_costs))
        if any(item.get(label_key) for item in chosen):
            positive_transfers += 1
        if any(item.get("is_matching_recovery") for item in chosen):
            matching_transfers += 1
    cost_sum = sum(costs)
    cost_per_positive = cost_sum / positive_transfers if positive_transfers else None
    cost_per_matching = cost_sum / matching_transfers if matching_transfers else None
    return {
        "cost_over_rho_min_per_selected_transfer": stat(costs),
        "cost_per_matching_transfer_over_rho": (
            round(cost_per_matching, 8) if cost_per_matching is not None else None
        ),
        "cost_per_positive_transfer_over_rho": (
            round(cost_per_positive, 8) if cost_per_positive is not None else None
        ),
        "matching_transfer_count": matching_transfers,
        "positive_transfer_count": positive_transfers,
        "recall": round(positive_transfers / total_positive_transfers, 8) if total_positive_transfers else None,
        "selected_transfer_count": selected_transfers,
        "total_matching_transfer_count": total_matching_transfers,
        "total_positive_transfer_count": total_positive_transfers,
        "total_transfer_count": len(by_transfer),
    }


def support_set(item: dict[str, Any]) -> set[int]:
    return {int_value(value) for value in item.get("selected_support") or []}


def has_salt_pair(item: dict[str, Any]) -> bool:
    return item.get("salt_abs_gap") is not None


def salt_int(item: dict[str, Any], key: str) -> int | None:
    value = item.get(key)
    return value if isinstance(value, int) else None


def add_combined_public_predicates(
    predicates: dict[str, Predicate],
    label: str,
    predicate: Predicate,
) -> None:
    predicates[label] = predicate
    predicates[f"selector_lowterm5_topk_7_or_12_and_{label}"] = (
        lambda item, inner=predicate: str(item.get("selector")) == "mode_low_term_support_total5"
        and int_value(item.get("top_k")) in {7, 12}
        and inner(item)
    )
    for limit in range(6, 17):
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


def build_predicates(calibration_items: list[dict[str, Any]], known_columns: set[int]) -> dict[str, Predicate]:
    predicates: dict[str, Predicate] = {
        "all": lambda _item: True,
        "selector_lowterm_support_total5": lambda item: str(item.get("selector")) == "mode_low_term_support_total5",
        "topk_7_or_12": lambda item: int_value(item.get("top_k")) in {7, 12},
        "selector_lowterm5_topk_7_or_12": lambda item: str(item.get("selector")) == "mode_low_term_support_total5"
        and int_value(item.get("top_k")) in {7, 12},
    }
    top_ks = sorted({int_value(item.get("top_k")) for item in calibration_items})
    for top_k in top_ks:
        predicates[f"topk_{top_k}"] = lambda item, wanted=top_k: int_value(item.get("top_k")) == wanted
        predicates[f"selector_lowterm5_topk_{top_k}"] = (
            lambda item, wanted=top_k: str(item.get("selector")) == "mode_low_term_support_total5"
            and int_value(item.get("top_k")) == wanted
        )
    for limit in range(6, 17):
        predicates[f"selected_support_size_le_{limit}"] = (
            lambda item, threshold=limit: len(support_set(item)) <= threshold
        )
        predicates[f"selector_lowterm5_topk_7_or_12_support_size_le_{limit}"] = (
            lambda item, threshold=limit: str(item.get("selector")) == "mode_low_term_support_total5"
            and int_value(item.get("top_k")) in {7, 12}
            and len(support_set(item)) <= threshold
        )
    for column in sorted(known_columns):
        add_combined_public_predicates(
            predicates,
            f"selected_support_contains_col_{column}",
            lambda item, wanted=column: wanted in support_set(item),
        )
    for count in range(0, len(known_columns) + 1):
        predicates[f"known_overlap_ge_{count}"] = (
            lambda item, threshold=count: len(support_set(item) & known_columns) >= threshold
        )
    for limit in range(0, 10):
        predicates[f"selected_unknown_count_le_{limit}"] = (
            lambda item, threshold=limit: len(support_set(item) - known_columns) <= threshold
        )
        predicates[f"selector_lowterm5_topk_7_or_12_selected_unknown_count_le_{limit}"] = (
            lambda item, threshold=limit: str(item.get("selector")) == "mode_low_term_support_total5"
            and int_value(item.get("top_k")) in {7, 12}
            and len(support_set(item) - known_columns) <= threshold
        )
    positive_pairs = sorted(
        {
            tuple(pair)
            for item in calibration_items
            if item.get("has_known_support_form")
            for pair in item.get("known_form_support_pairs") or []
            if len(pair) == 2
        }
    )
    for pair in positive_pairs:
        label = "selected_support_contains_pair_" + "_".join(str(value) for value in pair)
        add_combined_public_predicates(
            predicates,
            label,
            lambda item, wanted=pair: all(value in support_set(item) for value in wanted),
        )
    positive_signatures = sorted(
        {
            tuple(item.get("selected_support") or [])
            for item in calibration_items
            if item.get("has_known_support_form") and item.get("selected_support")
        }
    )
    for index, signature in enumerate(positive_signatures[:64]):
        predicates[f"selected_support_signature_calpos_{index}"] = (
            lambda item, wanted=signature: tuple(item.get("selected_support") or []) == wanted
        )
    add_combined_public_predicates(predicates, "salt_pair_present", has_salt_pair)
    for parity in range(2):
        add_combined_public_predicates(
            predicates,
            f"salt_gap_parity_{parity}",
            lambda item, wanted=parity: has_salt_pair(item)
            and (int_value(item.get("salt_abs_gap")) % 2) == wanted,
        )
        add_combined_public_predicates(
            predicates,
            f"salt_sum_parity_{parity}",
            lambda item, wanted=parity: salt_int(item, "salt_sum") is not None
            and (int_value(item.get("salt_sum")) % 2) == wanted,
        )
    for modulus in (3, 4, 5, 8):
        for residue in range(modulus):
            add_combined_public_predicates(
                predicates,
                f"salt_gap_mod_{modulus}_eq_{residue}",
                lambda item, mod=modulus, wanted=residue: has_salt_pair(item)
                and (int_value(item.get("salt_abs_gap")) % mod) == wanted,
            )
            add_combined_public_predicates(
                predicates,
                f"salt_sum_mod_{modulus}_eq_{residue}",
                lambda item, mod=modulus, wanted=residue: salt_int(item, "salt_sum") is not None
                and (int_value(item.get("salt_sum")) % mod) == wanted,
            )
    for threshold in range(0, 24):
        add_combined_public_predicates(
            predicates,
            f"salt_abs_gap_le_{threshold}",
            lambda item, limit=threshold: has_salt_pair(item) and int_value(item.get("salt_abs_gap")) <= limit,
        )
        add_combined_public_predicates(
            predicates,
            f"salt_abs_gap_ge_{threshold}",
            lambda item, limit=threshold: has_salt_pair(item) and int_value(item.get("salt_abs_gap")) >= limit,
        )
    for threshold in range(150, 186):
        add_combined_public_predicates(
            predicates,
            f"salt_min_le_{threshold}",
            lambda item, limit=threshold: salt_int(item, "salt_min") is not None
            and int_value(item.get("salt_min")) <= limit,
        )
        add_combined_public_predicates(
            predicates,
            f"salt_max_ge_{threshold}",
            lambda item, limit=threshold: salt_int(item, "salt_max") is not None
            and int_value(item.get("salt_max")) >= limit,
        )
    add_combined_public_predicates(
        predicates,
        "salt_first_lt_second",
        lambda item: item.get("salt_first_lt_second") is True,
    )
    add_combined_public_predicates(
        predicates,
        "salt_first_gt_second",
        lambda item: item.get("salt_first_lt_second") is False,
    )
    return predicates


def rank_key(metrics: dict[str, Any]) -> tuple[float, float, int]:
    cost = metrics.get("cost_per_positive_over_rho")
    precision = metrics.get("precision")
    selected_count = int_value(metrics.get("selected_certificate_count"))
    return (
        float(cost) if isinstance(cost, (int, float)) else 1e9,
        -(float(precision) if isinstance(precision, (int, float)) else -1.0),
        selected_count,
    )


def sample_items(items: list[dict[str, Any]], predicate: Predicate, limit: int = 12) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in sorted(
        (candidate for candidate in items if predicate(candidate)),
        key=lambda candidate: (
            str(candidate.get("cohort")),
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
                "cohort": item.get("cohort"),
                "direct_cost_over_rho": item.get("direct_cost_over_rho"),
                "direct_public_key_verified": item.get("direct_public_key_verified"),
                "has_known_support_form": item.get("has_known_support_form"),
                "is_matching_recovery": item.get("is_matching_recovery"),
                "known_form_supports": item.get("known_form_supports"),
                "row_key_salts": item.get("row_key_salts"),
                "salt_abs_gap": item.get("salt_abs_gap"),
                "salt_sum": item.get("salt_sum"),
                "selected_support": item.get("selected_support"),
                "top_k": item.get("top_k"),
                "transfer_index": item.get("transfer_index"),
                "unknown_form_supports": item.get("unknown_form_supports"),
            }
        )
    return rows


def split_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "certificate_count": len(items),
        "direct_verified_count": sum(1 for item in items if item.get("direct_public_key_verified")),
        "known_support_form_count": sum(1 for item in items if item.get("has_known_support_form")),
        "matching_recovery_count": sum(1 for item in items if item.get("is_matching_recovery")),
        "with_descent_label_count": sum(1 for item in items if item.get("has_descent_label")),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retrospective-certificates", required=True)
    parser.add_argument("--retrospective-scouts", required=True)
    parser.add_argument("--scheduled-certificates")
    parser.add_argument("--scheduled-scouts")
    parser.add_argument("--descent-reports", required=True)
    parser.add_argument("--calibration-max-transfer", type=int, default=2527)
    parser.add_argument("--future-tail-min-transfer", type=int, default=2591)
    parser.add_argument("--label-key", default="has_known_support_form")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def metrics_bundle(items: list[dict[str, Any]], predicate: Predicate, label_key: str) -> dict[str, Any]:
    return {
        **evaluate(items, predicate, label_key),
        "transfer_metrics": transfer_evaluate(items, predicate, label_key),
    }


def main() -> None:
    args = parse_args()
    retrospective_cert_paths = parse_paths(args.retrospective_certificates)
    retrospective_scout_paths = parse_paths(args.retrospective_scouts)
    scheduled_cert_paths = parse_paths(args.scheduled_certificates)
    scheduled_scout_paths = parse_paths(args.scheduled_scouts)
    descent_paths = parse_paths(args.descent_reports)
    known_columns, descent_labels = load_descent_reports(descent_paths)
    retro_certs = load_certificates(retrospective_cert_paths, "retrospective")
    scheduled_certs = load_certificates(scheduled_cert_paths, "scheduled_actual")
    retro_items = annotate_items(retro_certs, retrospective_scout_paths, known_columns, descent_labels)
    scheduled_items = annotate_items(scheduled_certs, scheduled_scout_paths, known_columns, descent_labels)
    all_items = retro_items + scheduled_items

    calibration_items = [
        item
        for item in retro_items
        if int_value(item.get("transfer_index")) <= args.calibration_max_transfer
    ]
    retrospective_validation_items = [
        item
        for item in retro_items
        if int_value(item.get("transfer_index")) > args.calibration_max_transfer
    ]
    old_validation_items = [
        item
        for item in retro_items
        if args.calibration_max_transfer < int_value(item.get("transfer_index")) <= args.future_tail_min_transfer
    ]
    future_tail_items = [
        item
        for item in retro_items
        if int_value(item.get("transfer_index")) > args.future_tail_min_transfer
    ]
    predicates = build_predicates(calibration_items, known_columns)
    label_key = str(args.label_key)

    calibration_results = {
        name: evaluate(calibration_items, predicate, label_key)
        for name, predicate in sorted(predicates.items())
    }
    retrospective_validation_results = {
        name: metrics_bundle(retrospective_validation_items, predicate, label_key)
        for name, predicate in sorted(predicates.items())
    }
    scheduled_results = {
        name: metrics_bundle(scheduled_items, predicate, label_key)
        for name, predicate in sorted(predicates.items())
    }
    calibration_viable = [
        (name, metrics)
        for name, metrics in calibration_results.items()
        if int_value(metrics.get("positive_count")) > 0
    ]
    selected_name = min(calibration_viable, key=lambda pair: rank_key(pair[1]))[0] if calibration_viable else "all"
    frozen_names = [
        "selected_support_size_le_10",
        "selector_lowterm5_topk_7_or_12_support_size_le_10",
        selected_name,
    ]
    for name in (
        "selected_support_contains_pair_8_11",
        "selected_support_contains_pair_9_11",
        "selected_support_contains_pair_10_13",
        "selected_support_contains_pair_10_14",
        "selected_support_contains_pair_11_13",
    ):
        if name in predicates:
            frozen_names.append(name)
    frozen_names = list(dict.fromkeys(frozen_names))
    frozen_predicate_checks = {
        name: {
            "calibration": evaluate(calibration_items, predicates[name], label_key),
            "future_tail": metrics_bundle(future_tail_items, predicates[name], label_key),
            "old_validation": metrics_bundle(old_validation_items, predicates[name], label_key),
            "retrospective_validation": retrospective_validation_results[name],
            "scheduled_actual": scheduled_results[name],
        }
        for name in frozen_names
        if name in predicates
    }
    selected_scheduled = scheduled_results[selected_name]
    scheduled_baseline = scheduled_results["all"]
    if int_value(selected_scheduled.get("matching_recovery_count")) > 0:
        claim_status = "KNOWN_SUPPORT_PAIR_PREDICTOR_SCHEDULED_MATCHING_RECOVERY_FOUND"
    elif int_value(selected_scheduled.get("positive_count")) > 0:
        claim_status = "KNOWN_SUPPORT_PAIR_PREDICTOR_STRUCTURAL_SCHEDULED_SIGNAL_NEEDS_TARGET_COMPATIBILITY"
    elif int_value(scheduled_baseline.get("positive_count")) > 0:
        claim_status = "KNOWN_SUPPORT_PAIR_PREDICTOR_MISSES_SCHEDULED_STRUCTURAL_FORMS"
    else:
        claim_status = "SCHEDULED_SOURCE_NO_KNOWN_SUPPORT_STRUCTURAL_SIGNAL"

    payload = {
        "artifacts": {
            "descent_reports": [str(path) for path in descent_paths],
            "retrospective_certificates": [str(path) for path in retrospective_cert_paths],
            "retrospective_scouts": [str(path) for path in retrospective_scout_paths],
            "scheduled_certificates": [str(path) for path in scheduled_cert_paths],
            "scheduled_scouts": [str(path) for path in scheduled_scout_paths],
        },
        "calibration_max_transfer": args.calibration_max_transfer,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "future_tail_min_transfer": args.future_tail_min_transfer,
        "honesty_boundary": {
            "assumptions": [
                "Known factor columns are inherited from provided descent reports.",
                "Public predicates are selected from calibration transfers only.",
                "Scheduled support10 windows are evaluated as out-of-distribution actual-source validation.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HEURISTIC-COST",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "direct relation verification available before source selection",
                "deployment-relevant key recovery",
            ],
            "scope": "Public-feature predictor for whether relation-form factor support lands inside already-known factor columns.",
        },
        "known_factor_columns": sorted(known_columns),
        "label_key": label_key,
        "predicate_results": {
            "calibration": calibration_results,
            "retrospective_validation": retrospective_validation_results,
            "scheduled_actual": scheduled_results,
        },
        "frozen_predicate_checks": frozen_predicate_checks,
        "schema": "ecdlp.low_term_total2_known_support_pair_predictor_probe.v1",
        "selected_by_calibration": {
            "calibration": calibration_results[selected_name],
            "name": selected_name,
            "retrospective_validation": retrospective_validation_results[selected_name],
            "scheduled_actual": selected_scheduled,
            "scheduled_selected_samples": sample_items(scheduled_items, predicates[selected_name]),
            "validation_selected_samples": sample_items(retrospective_validation_items, predicates[selected_name]),
        },
        "split_summary": {
            "all": split_summary(all_items),
            "calibration": split_summary(calibration_items),
            "future_tail": split_summary(future_tail_items),
            "old_validation": split_summary(old_validation_items),
            "retrospective": split_summary(retro_items),
            "retrospective_validation": split_summary(retrospective_validation_items),
            "scheduled_actual": split_summary(scheduled_items),
        },
        "top_retrospective_validation_predicates": [
            {"name": name, **metrics}
            for name, metrics in sorted(
                retrospective_validation_results.items(),
                key=lambda pair: rank_key(pair[1]),
            )[:12]
        ],
        "top_scheduled_actual_predicates": [
            {"name": name, **metrics}
            for name, metrics in sorted(
                scheduled_results.items(),
                key=lambda pair: rank_key(pair[1]),
            )[:12]
        ],
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["split_summary"], indent=2, sort_keys=True))
    print(json.dumps(payload["selected_by_calibration"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
