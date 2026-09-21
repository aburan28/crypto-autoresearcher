#!/usr/bin/env python3
"""Scout public factor columns that should be targeted next.

The rank-gap diagnostic reports quotient residual classes, but a collector
needs a more actionable view: which public factor columns are still free after
the current greedy rank-gain candidates, whether those columns appear in forms,
and whether existing certificates create target-eliminated factor rows that
touch them.  This script keeps the same order-specific factor namespace as the
target-eliminated bank and turns the live scorer artifact into a work order for
the next selector/factor-base branch.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_factor_rank_gap_diagnostic as gap
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SCORER = STATE_DIR / "low_term_total2_factor_rank_candidate_scorer_target67_multibranch_live_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_factor_column_target_scout_target67_multibranch_live_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def paths_from_scorer(path: Path) -> tuple[list[Path], list[Path]]:
    payload = load_json(path)
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    return (
        [Path(item) for item in artifacts.get("base_certificates") or []],
        [Path(item) for item in artifacts.get("candidate_certificates") or []],
    )


def selected_key(info: dict[str, Any]) -> tuple[str, int]:
    return str(info.get("artifact")), int_value(info.get("artifact_offset"))


def candidate_key(cert: dict[str, Any]) -> tuple[str, int]:
    return str(cert.get("_artifact")), int_value(cert.get("_artifact_offset"))


def greedy_candidate_keys(scorer_payload: dict[str, Any]) -> set[tuple[str, int]]:
    keys: set[tuple[str, int]] = set()
    for item in scorer_payload.get("greedy_selected") or []:
        candidate = item.get("candidate") if isinstance(item.get("candidate"), dict) else {}
        keys.add(selected_key(candidate))
    return keys


def cert_family(cert: dict[str, Any]) -> str:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    selector = selected.get("selector") or "unknown_selector"
    top_k = selected.get("top_k") if selected.get("top_k") is not None else "unknown_topk"
    clause = cert.get("clause") or selected.get("clause") or "none"
    target = selected.get("target") or "unknown_target"
    return f"{target}|{selector}|top{top_k}|{clause}"


def selected_sample(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    rho = int_value(selected.get("rho"))
    shared_ops = selected.get("shared_ops")
    ops_over_rho = None
    if shared_ops is not None and rho:
        ops_over_rho = round(float(int_value(shared_ops) + 1) / float(rho), 8)
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "clause": cert.get("clause") or selected.get("clause"),
        "family": cert_family(cert),
        "generated_plus_shared_ops_over_rho": ops_over_rho,
        "selector": selected.get("selector"),
        "target": selected.get("target"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
        "window": cert.get("window"),
    }


def add_sample(bucket: dict[str, Any], cert: dict[str, Any], limit: int = 8) -> None:
    samples = bucket.setdefault("samples", [])
    if len(samples) < limit:
        samples.append(selected_sample(cert))


def column_form_profile(
    certificates: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> dict[int, dict[str, Any]]:
    profile: dict[int, dict[str, Any]] = {
        column: {
            "certificate_count": 0,
            "coefficient_support_count": 0,
            "families": Counter(),
            "form_count": 0,
            "term_occurrence_count": 0,
            "term_support_count": 0,
        }
        for column in range(factor_count)
    }
    certs_seen: dict[int, set[int]] = defaultdict(set)
    for cert_index, cert in enumerate(certificates):
        if int_value(cert.get("order")) != order:
            continue
        family = cert_family(cert)
        for form in [item for item in (cert.get("forms") or []) if isinstance(item, dict)]:
            coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
            factor_coeffs = gap.pad(coeffs[1:], factor_count)
            coeff_support = {idx for idx, value in enumerate(factor_coeffs) if value % order}
            term_values = [
                int_value(value)
                for value in (form.get("terms") or [])
                if 0 <= int_value(value) < factor_count
            ]
            term_counts = Counter(term_values)
            for column in coeff_support | set(term_counts):
                bucket = profile[column]
                bucket["families"][family] += 1
                bucket["form_count"] += 1
                if column in coeff_support:
                    bucket["coefficient_support_count"] += 1
                if column in term_counts:
                    bucket["term_support_count"] += 1
                    bucket["term_occurrence_count"] += term_counts[column]
                certs_seen[column].add(cert_index)
                add_sample(bucket, cert)
    for column, seen in certs_seen.items():
        profile[column]["certificate_count"] = len(seen)
    for bucket in profile.values():
        families = bucket["families"]
        bucket["families"] = dict(sorted(families.items(), key=lambda item: (-item[1], item[0]))[:10])
    return profile


def relation_support_counts(
    certificates: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> Counter[int]:
    counts: Counter[int] = Counter()
    for row in gap.unique_relation_rows(certificates, order, factor_count):
        for column in row.get("factor_support") or []:
            counts[int_value(column)] += 1
    return counts


def residual_groups_after_basis(
    order: int,
    basis_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
    factor_count: int,
) -> list[dict[str, Any]]:
    basis_rows = gap.unique_relation_rows(basis_certificates, order, factor_count)
    basis, pivots = gap.rref_rows([row["coeffs"] for row in basis_rows], order)
    free_columns = [idx for idx in range(factor_count) if idx not in set(pivots)]
    groups: dict[tuple[int, ...], dict[str, Any]] = {}
    for cert in candidate_certificates:
        if int_value(cert.get("order")) != order:
            continue
        signatures = set()
        for row in gap.relation_rows(cert, factor_count):
            residual = gap.reduce_row(row["coeffs"], basis, pivots, order)
            normalized = gap.normalize_vector(residual, order)
            if normalized is not None:
                signatures.add(normalized)
        for signature in signatures:
            group = groups.setdefault(
                signature,
                {
                    "candidate_count": 0,
                    "candidate_samples": [],
                    "free_column_support": [idx for idx in free_columns if signature[idx] % order],
                    "residual_support": [idx for idx, value in enumerate(signature) if value % order],
                },
            )
            group["candidate_count"] += 1
            if len(group["candidate_samples"]) < 8:
                group["candidate_samples"].append(selected_sample(cert))
    result = [{"normalized_residual": list(signature), **group} for signature, group in groups.items()]
    result.sort(
        key=lambda item: (
            -int_value(item.get("candidate_count")),
            item.get("free_column_support") or [],
            item.get("residual_support") or [],
        )
    )
    return result


def column_status(
    column: int,
    base_relation_count: int,
    post_relation_count: int,
    candidate_form_count: int,
    remaining_residual_support_count: int,
) -> str:
    if post_relation_count == 0 and candidate_form_count == 0:
        return "UNSEEN_IN_ROWS_AND_LIVE_FORMS"
    if post_relation_count == 0:
        return "SEEN_IN_FORMS_NOT_FACTOR_ROWS"
    if remaining_residual_support_count == 0:
        return "NO_REMAINING_RESIDUAL_SUPPORT"
    if base_relation_count == 0:
        return "NEWLY_TOUCHED_BUT_STILL_FREE"
    return "FREE_WITH_REMAINING_RESIDUAL_SUPPORT"


def analyze_order(
    order: int,
    base_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
    greedy_certificates: list[dict[str, Any]],
) -> dict[str, Any]:
    all_certs = base_certificates + candidate_certificates
    factor_count = gap.factor_count_for_order(all_certs, order)
    post_certificates = base_certificates + greedy_certificates
    remaining_candidates = [
        cert for cert in candidate_certificates if candidate_key(cert) not in {candidate_key(item) for item in greedy_certificates}
    ]

    base_rows = gap.unique_relation_rows(base_certificates, order, factor_count)
    post_rows = gap.unique_relation_rows(post_certificates, order, factor_count)
    base_basis, base_pivots = gap.rref_rows([row["coeffs"] for row in base_rows], order)
    post_basis, post_pivots = gap.rref_rows([row["coeffs"] for row in post_rows], order)
    post_free_columns = [idx for idx in range(factor_count) if idx not in set(post_pivots)]

    base_relation_counts = relation_support_counts(base_certificates, order, factor_count)
    post_relation_counts = relation_support_counts(post_certificates, order, factor_count)
    base_form_profile = column_form_profile(base_certificates, order, factor_count)
    candidate_form_profile = column_form_profile(candidate_certificates, order, factor_count)
    greedy_form_profile = column_form_profile(greedy_certificates, order, factor_count)
    remaining_groups = residual_groups_after_basis(order, post_certificates, remaining_candidates, factor_count)
    remaining_residual_counts: Counter[int] = Counter()
    for group in remaining_groups:
        for column in group.get("free_column_support") or []:
            remaining_residual_counts[int_value(column)] += int_value(group.get("candidate_count"))

    column_reports = []
    for column in range(factor_count):
        base_forms = base_form_profile[column]
        candidate_forms = candidate_form_profile[column]
        greedy_forms = greedy_form_profile[column]
        report = {
            "base_form_certificate_count": int_value(base_forms.get("certificate_count")),
            "base_relation_support_count": base_relation_counts[column],
            "candidate_form_certificate_count": int_value(candidate_forms.get("certificate_count")),
            "candidate_form_families": candidate_forms.get("families") or {},
            "column": column,
            "greedy_form_certificate_count": int_value(greedy_forms.get("certificate_count")),
            "is_post_greedy_free": column in post_free_columns,
            "post_greedy_relation_support_count": post_relation_counts[column],
            "remaining_residual_support_count": remaining_residual_counts[column],
            "status": column_status(
                column,
                base_relation_counts[column],
                post_relation_counts[column],
                int_value(candidate_forms.get("certificate_count")),
                remaining_residual_counts[column],
            ),
        }
        if report["is_post_greedy_free"]:
            column_reports.append(report)
    column_reports.sort(
        key=lambda item: (
            item["status"] != "UNSEEN_IN_ROWS_AND_LIVE_FORMS",
            item["status"] != "SEEN_IN_FORMS_NOT_FACTOR_ROWS",
            item["remaining_residual_support_count"],
            item["post_greedy_relation_support_count"],
            item["candidate_form_certificate_count"],
            item["column"],
        )
    )

    candidate_order_count = sum(1 for cert in candidate_certificates if int_value(cert.get("order")) == order)
    greedy_order_count = sum(1 for cert in greedy_certificates if int_value(cert.get("order")) == order)
    return {
        "base_rank": len(base_pivots),
        "base_free_columns": [idx for idx in range(factor_count) if idx not in set(base_pivots)],
        "candidate_certificate_count": candidate_order_count,
        "factor_variable_count": factor_count,
        "greedy_certificate_count": greedy_order_count,
        "post_greedy_deficiency": max(0, factor_count - len(post_pivots)),
        "post_greedy_free_columns": post_free_columns,
        "post_greedy_pivot_columns": post_pivots,
        "post_greedy_rank": len(post_pivots),
        "remaining_residual_group_count": len(remaining_groups),
        "remaining_residual_groups": remaining_groups[:12],
        "target_column_reports": column_reports,
        "work_order": work_order_for_order(order, candidate_order_count, column_reports),
    }


def work_order_for_order(order: int, candidate_count: int, column_reports: list[dict[str, Any]]) -> dict[str, Any]:
    free_columns = [int_value(item.get("column")) for item in column_reports]
    unseen = [
        int_value(item.get("column"))
        for item in column_reports
        if item.get("status") == "UNSEEN_IN_ROWS_AND_LIVE_FORMS"
    ]
    seen_not_rows = [
        int_value(item.get("column"))
        for item in column_reports
        if item.get("status") == "SEEN_IN_FORMS_NOT_FACTOR_ROWS"
    ]
    no_remaining = [
        int_value(item.get("column"))
        for item in column_reports
        if item.get("status") == "NO_REMAINING_RESIDUAL_SUPPORT"
    ]
    if candidate_count == 0:
        action = "GENERATE_ORDER_SPECIFIC_CANDIDATES"
        rationale = "no live candidate certificates exist for this order"
        priority = free_columns
    elif unseen or seen_not_rows:
        action = "TARGET_UNSEEN_OR_FORM_ONLY_COLUMNS"
        rationale = "some post-greedy free columns are absent from factor rows or only visible before elimination"
        priority = unseen + seen_not_rows
    elif no_remaining:
        action = "CREATE_NEW_RESIDUAL_CLASSES"
        rationale = "current remaining candidates do not touch these post-greedy free directions"
        priority = no_remaining
    else:
        action = "EXPLOIT_REMAINING_RESIDUAL_GROUPS"
        rationale = "remaining candidates already touch at least one free direction"
        priority = free_columns
    return {
        "action": action,
        "priority_columns": priority,
        "rationale": rationale,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorer-artifact", default=str(DEFAULT_SCORER))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scorer_path = Path(args.scorer_artifact)
    scorer_payload = load_json(scorer_path)
    base_paths, candidate_paths = paths_from_scorer(scorer_path)
    if not base_paths:
        raise ValueError("no base certificates in scorer artifact")
    base_certificates = factor_bank.load_certificates(base_paths)
    candidate_certificates = factor_bank.load_certificates(candidate_paths)
    greedy_keys = greedy_candidate_keys(scorer_payload)
    greedy_certificates = [cert for cert in candidate_certificates if candidate_key(cert) in greedy_keys]
    orders = sorted(
        {
            int_value(cert.get("order"))
            for cert in base_certificates + candidate_certificates
            if int_value(cert.get("order"))
        }
    )
    order_reports = {
        str(order): analyze_order(order, base_certificates, candidate_certificates, greedy_certificates)
        for order in orders
    }
    post_greedy_deficiency_total = sum(
        int_value(report.get("post_greedy_deficiency")) for report in order_reports.values()
    )
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
            "scorer_artifact": str(scorer_path),
        },
        "claim_status": (
            "POST_GREEDY_FACTOR_RANK_TARGETS_IDENTIFIED"
            if post_greedy_deficiency_total
            else "NO_POST_GREEDY_FACTOR_RANK_GAP"
        ),
        "created_at": now_iso(),
        "greedy_selected_count": len(greedy_certificates),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: columns are the verifier's current order-specific factor namespace.",
            "HEURISTIC: column targets are collector-design guidance, not a complete target descent or deployed-curve speedup claim.",
        ],
        "order_reports": order_reports,
        "schema": "ecdlp.low_term_total2_factor_column_target_scout.v1",
        "summary": {
            "candidate_certificate_count": len(candidate_certificates),
            "greedy_selected_count": len(greedy_certificates),
            "order_count": len(order_reports),
            "post_greedy_deficiency_total": post_greedy_deficiency_total,
            "post_greedy_rank_total": sum(int_value(report.get("post_greedy_rank")) for report in order_reports.values()),
            "work_orders": {
                order: report.get("work_order") for order, report in order_reports.items()
            },
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
