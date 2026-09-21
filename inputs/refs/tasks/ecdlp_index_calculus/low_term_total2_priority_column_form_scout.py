#!/usr/bin/env python3
"""Replay fresh shared-product rows and scout missing factor columns.

The factor-column target scout identifies order-specific columns that are still
absent from verified forms.  This script searches existing shared-product gate
artifacts for public rows whose replayed relation forms touch those priority
columns.  It is intentionally a bounded scout: it does not promote rows into
the rank bank by itself, but it tells the next collector which target/selector
families can expose the missing columns.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_dependency_circuit_probe as dependency_probe
import low_term_total2_fixed_leaf_shared_context_audit_probe as context_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
import low_term_total2_source_relation_equation_certificate as certificate_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_priority_column_form_scout_2280_2351_probe.json"
DEFAULT_SOURCE_TEMPLATE = (
    "ecdlp_index_calculus_state/"
    "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_{window}_probe.json"
)
DEFAULT_PRIORITY_COLUMNS = "9887=0,5,6,7,8;11779=7,10,15"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def window_label(path: Path) -> str:
    matches = re.findall(r"(?<!\d)(\d{4,})_(\d{4,})(?!\d)", path.name)
    if matches:
        start, end = matches[-1]
        return f"{start}_{end}"
    return path.stem


def parse_priority_columns(raw: str) -> dict[int, set[int]]:
    out: dict[int, set[int]] = {}
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError("priority entries must look like ORDER=COL,COL")
        order_raw, cols_raw = chunk.split("=", 1)
        out[int(order_raw.strip())] = {
            int(item.strip()) for item in cols_raw.split(",") if item.strip()
        }
    return out


def parse_targets(raw: str) -> set[str]:
    return {item.strip() for item in raw.split(",") if item.strip()}


def source_for_window(template: str, window: str) -> Path:
    return Path(template.format(window=window))


def case_key(case: dict[str, Any], window: str) -> tuple[Any, ...]:
    return (
        window,
        case.get("target"),
        int_value(case.get("transfer_index")),
        case.get("selector"),
        int_value(case.get("top_k")),
        tuple(sorted(str(item) for item in case.get("row_keys") or [])),
    )


def case_selected(case: dict[str, Any], gate_selected_only: bool) -> bool:
    return (not gate_selected_only) or bool(case.get("public_product_gate_selected"))


def case_verified(case: dict[str, Any], verified_only: bool) -> bool:
    return (not verified_only) or bool(case.get("shared_product_union_public_key_verified"))


def compact_case(case: dict[str, Any], artifact: Path, window: str) -> dict[str, Any]:
    metrics = case.get("gate_metrics") if isinstance(case.get("gate_metrics"), dict) else {}
    rho = int_value(case.get("rho"))
    shared_ops = int_value(case.get("shared_product_ledger_ops"))
    return {
        "artifact": str(artifact),
        "direct_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
        "hit_root_ops": int_value(metrics.get("direct_selected_hit_root_ops")),
        "public_product_gate_selected": bool(case.get("public_product_gate_selected")),
        "rho": rho,
        "root_saved_ops": int_value(metrics.get("shared_signature_root_saved_ops")),
        "row_keys": case.get("row_keys") or [],
        "selector": case.get("selector"),
        "shared_ops": shared_ops,
        "shared_ops_over_rho": case.get("shared_product_ledger_ops_over_rho"),
        "source_charged_unit_ops_over_rho": ratio(shared_ops + 1, rho),
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
        "verified": bool(case.get("shared_product_union_public_key_verified")),
        "window": window,
    }


def unique_relation_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return certificate_probe.unique_events(rows)


def form_supports(forms: list[dict[str, Any]], order: int) -> tuple[set[int], set[int]]:
    term_support: set[int] = set()
    coeff_support: set[int] = set()
    for form in forms:
        term_support.update(int_value(term) for term in form.get("terms") or [])
        for idx, coeff in enumerate((form.get("coeffs") or [])[1:]):
            if int_value(coeff) % order:
                coeff_support.add(idx)
    return term_support, coeff_support


def replay_case(
    case: dict[str, Any],
    artifact: Path,
    source_template: str,
) -> dict[str, Any]:
    window = window_label(artifact)
    source_path = source_for_window(source_template, window)
    source = load_json(source_path)
    source_case = context_probe.find_source_case(
        source,
        str(case.get("target")),
        int_value(case.get("transfer_index")),
        str(case.get("selector")),
        int_value(case.get("top_k")),
    )
    verifier, contexts, _product_factor, max_relations = timing_probe.selected_contexts_from_source_case(
        source,
        source_case,
    )
    shared_covers, product_profile = timing_probe.shared_product_pair_association(contexts)
    scan_rows = timing_probe.scan_from_covers(verifier, contexts, shared_covers, max_relations)
    events = unique_relation_events(scan_rows)
    if not contexts:
        raise ValueError(f"no contexts for {window} {case.get('target')}")
    built = contexts[0]["built"]
    order = int(built["order"])
    forms = [certificate_probe.compact_form(event, order) for event in events]
    derived = dependency_probe.public_derive_from_events(
        verifier,
        [{"form": event["form"]} for event in events],
        order,
        built["base"],
        built["public"],
        built["ainvs"],
        int(built["p"]),
    )
    source_row_keys = sorted(str(item) for item in source_case.get("row_keys") or [])
    case_row_keys = sorted(str(item) for item in case.get("row_keys") or [])
    term_support, coeff_support = form_supports(forms, order)
    return {
        "coeff_support": sorted(coeff_support),
        "derived_secret": derived.get("derived_secret"),
        "forms": forms,
        "forms_count": len(forms),
        "order": order,
        "product_profile": {
            key: value for key, value in product_profile.items() if key != "signature_groups"
        },
        "public_key_verified": bool(derived.get("public_key_verified")),
        "rank": int_value(derived.get("rank")),
        "row_keys_match_source": source_row_keys == case_row_keys,
        "scan_row_count": len(scan_rows),
        "source": str(source_path),
        "source_case_row_keys": source_row_keys,
        "term_support": sorted(term_support),
    }


def load_cases(
    product_artifacts: list[Path],
    targets: set[str],
    gate_selected_only: bool,
    verified_only: bool,
) -> list[tuple[Path, str, dict[str, Any]]]:
    rows: list[tuple[Path, str, dict[str, Any]]] = []
    seen: set[tuple[Any, ...]] = set()
    for artifact in product_artifacts:
        payload = load_json(artifact)
        window = window_label(artifact)
        for case in payload.get("cases") or []:
            if not isinstance(case, dict):
                continue
            if targets and str(case.get("target")) not in targets:
                continue
            if not case_selected(case, gate_selected_only):
                continue
            if not case_verified(case, verified_only):
                continue
            key = case_key(case, window)
            if key in seen:
                continue
            seen.add(key)
            rows.append((artifact, window, case))
    rows.sort(
        key=lambda item: (
            item[1],
            str(item[2].get("target")),
            int_value(item[2].get("transfer_index")),
            str(item[2].get("selector")),
            int_value(item[2].get("top_k")),
        )
    )
    return rows


def parse_paths(raw: str) -> list[Path]:
    return [Path(item) for item in raw.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product-artifacts", required=True)
    parser.add_argument("--source-template", default=DEFAULT_SOURCE_TEMPLATE)
    parser.add_argument("--priority-columns", default=DEFAULT_PRIORITY_COLUMNS)
    parser.add_argument("--targets", default="67.a1@9803,22050.cf1@11731")
    parser.add_argument("--max-replays", type=int, default=80)
    parser.add_argument("--gate-selected-only", action="store_true")
    parser.add_argument("--verified-only", action="store_true")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    product_artifacts = parse_paths(args.product_artifacts)
    priority_columns = parse_priority_columns(args.priority_columns)
    targets = parse_targets(args.targets)
    candidate_rows = load_cases(
        product_artifacts,
        targets,
        gate_selected_only=args.gate_selected_only,
        verified_only=args.verified_only,
    )
    reports: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for artifact, window, case in candidate_rows[: max(0, args.max_replays)]:
        compact = compact_case(case, artifact, window)
        try:
            replay = replay_case(case, artifact, args.source_template)
        except Exception as error:  # Preserve failure details for red-team use.
            errors.append({**compact, "error": str(error)})
            continue
        order = int_value(replay.get("order"))
        priority = priority_columns.get(order, set())
        term_hits = sorted(priority & set(replay.get("term_support") or []))
        coeff_hits = sorted(priority & set(replay.get("coeff_support") or []))
        reports.append(
            {
                **compact,
                "coeff_support": replay.get("coeff_support"),
                "forms_count": replay.get("forms_count"),
                "order": order,
                "priority_coeff_hits": coeff_hits,
                "priority_hit_count": len(set(term_hits) | set(coeff_hits)),
                "priority_term_hits": term_hits,
                "public_key_verified_replay": replay.get("public_key_verified"),
                "rank_replay": replay.get("rank"),
                "row_keys_match_source": replay.get("row_keys_match_source"),
                "scan_row_count": replay.get("scan_row_count"),
                "source": replay.get("source"),
                "term_support": replay.get("term_support"),
            }
        )
    reports.sort(
        key=lambda row: (
            -int_value(row.get("priority_hit_count")),
            not bool(row.get("public_key_verified_replay")),
            float(row.get("source_charged_unit_ops_over_rho") or 10**9),
            str(row.get("window")),
            int_value(row.get("transfer_index")),
        )
    )
    hit_reports = [row for row in reports if int_value(row.get("priority_hit_count")) > 0]
    order_hits = Counter(str(row.get("order")) for row in hit_reports)
    payload = {
        "artifacts": {
            "product_artifacts": [str(path) for path in product_artifacts],
            "source_template": args.source_template,
        },
        "case_reports": reports[:200],
        "claim_status": (
            "PRIORITY_COLUMN_FORM_HITS_FOUND"
            if hit_reports
            else "NO_PRIORITY_COLUMN_FORM_HITS_FOUND"
        ),
        "created_at": now_iso(),
        "errors": errors[:40],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: forms are replayed through the verifier's current shared-product relation model.",
            "HEURISTIC: priority-column hits are selector-design evidence, not a complete target descent or deployed-curve speedup claim.",
        ],
        "parameters": {
            "gate_selected_only": bool(args.gate_selected_only),
            "max_replays": args.max_replays,
            "priority_columns": {str(order): sorted(cols) for order, cols in priority_columns.items()},
            "targets": sorted(targets),
            "verified_only": bool(args.verified_only),
        },
        "schema": "ecdlp.low_term_total2_priority_column_form_scout.v1",
        "summary": {
            "candidate_case_count": len(candidate_rows),
            "error_count": len(errors),
            "order_hit_counts": dict(sorted(order_hits.items())),
            "priority_hit_count": len(hit_reports),
            "replayed_case_count": len(reports),
            "verified_priority_hit_count": sum(
                1 for row in hit_reports if row.get("public_key_verified_replay")
            ),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
