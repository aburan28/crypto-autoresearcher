#!/usr/bin/env python3
"""Filter candidate certificates by target-eliminated form-support families.

Recent anti-cancellation probes can repair rank while repeatedly exporting
families that fail stricter factor-substitution holdout.  This helper keeps the
raw replay artifact intact and writes a derived candidate-certificate artifact
whose forms satisfy an explicit family gate.  The gate can either name support
families directly or require all support columns to live in a derivable
factor-column set learned from holdout audits.

The gate is only a scheduler/triage mechanism.  Passing it is not target
descent and is not a faster-than-rho claim; the filtered candidates must still
pass rank, repair-bank, family-holdout, cost, sparse-LA, and transfer gates.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def family_key(family: tuple[int, ...]) -> str:
    return ",".join(str(item) for item in family)


def parse_families(raw: str | None) -> set[tuple[int, ...]]:
    families: set[tuple[int, ...]] = set()
    if not raw:
        return families
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        family = tuple(int(part.strip()) for part in chunk.split(",") if part.strip())
        if family:
            families.add(family)
    return families


def parse_int_set(raw: str | None) -> set[int]:
    values: set[int] = set()
    if not raw:
        return values
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if chunk:
            values.add(int(chunk))
    return values


def form_family(cert: dict[str, Any], form: dict[str, Any]) -> tuple[int, ...]:
    order = max(1, int_value(cert.get("order")))
    coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
    return tuple(index for index, value in enumerate(coeffs[1:]) if value % order)


def compact_selected(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected")
    if not isinstance(selected, dict):
        return {}
    keep = (
        "direct_ops_over_rho",
        "row_keys",
        "selected_leaf_indices_by_row",
        "selector",
        "target",
        "top_k",
        "transfer_index",
    )
    return {key: selected.get(key) for key in keep}


def annotate_form_gate(
    cert: dict[str, Any],
    avoid: set[tuple[int, ...]],
    require: set[tuple[int, ...]],
    avoid_columns: set[int],
    require_columns: set[int],
    max_avoid_column_count: int | None,
) -> tuple[list[dict[str, Any]], Counter[str], Counter[str]]:
    kept_forms: list[dict[str, Any]] = []
    all_counts: Counter[str] = Counter()
    kept_counts: Counter[str] = Counter()
    for form_index, form in enumerate(cert.get("forms") or []):
        if not isinstance(form, dict):
            continue
        family = form_family(cert, form)
        key = family_key(family)
        if key:
            all_counts[key] += 1
        allowed = bool(family)
        if require:
            allowed = allowed and family in require
        if avoid:
            allowed = allowed and family not in avoid
        if require_columns:
            allowed = allowed and all(column in require_columns for column in family)
        if avoid_columns:
            avoid_column_count = len(set(family) & avoid_columns)
            if max_avoid_column_count is None:
                allowed = allowed and avoid_column_count == 0
            else:
                allowed = allowed and avoid_column_count <= max_avoid_column_count
        if allowed:
            copied = dict(form)
            copied["_family"] = list(family)
            copied["_family_key"] = key
            copied["_source_form_index"] = form_index
            kept_forms.append(copied)
            kept_counts[key] += 1
    return kept_forms, all_counts, kept_counts


def gate_certificate(
    cert: dict[str, Any],
    cert_index: int,
    avoid: set[tuple[int, ...]],
    require: set[tuple[int, ...]],
    avoid_columns: set[int],
    require_columns: set[int],
    max_avoid_column_count: int | None,
    preserve_certificate_forms: bool,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    kept_forms, all_counts, kept_counts = annotate_form_gate(
        cert,
        avoid,
        require,
        avoid_columns,
        require_columns,
        max_avoid_column_count,
    )
    report = {
        "all_family_counts": dict(sorted(all_counts.items())),
        "direct_ops_over_rho": cert.get("direct_ops_over_rho"),
        "forms_count": len(cert.get("forms") or []),
        "kept_family_counts": dict(sorted(kept_counts.items())),
        "kept_form_count": len(kept_forms),
        "output_form_count": len(cert.get("forms") or []) if kept_forms and preserve_certificate_forms else len(kept_forms),
        "preserve_certificate_forms": preserve_certificate_forms,
        "rank": cert.get("rank"),
        "selected": compact_selected(cert),
        "source_certificate_index": cert_index,
        "status": "PASS" if kept_forms else "FILTERED_NO_ADMISSIBLE_FORMS",
    }
    if not kept_forms:
        return None, report
    filtered = dict(cert)
    if preserve_certificate_forms:
        kept_indexes = {
            int_value(form.get("_source_form_index"))
            for form in kept_forms
        }
        output_forms = []
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            family = form_family(cert, form)
            copied = dict(form)
            copied["_family"] = list(family)
            copied["_family_gate_passed"] = form_index in kept_indexes
            copied["_family_key"] = family_key(family)
            copied["_source_form_index"] = form_index
            output_forms.append(copied)
        filtered["forms"] = output_forms
        filtered["forms_count"] = len(output_forms)
    else:
        filtered["forms"] = kept_forms
        filtered["forms_count"] = len(kept_forms)
    filtered["_source_artifact_offset"] = cert.get("_artifact_offset", cert_index)
    filtered["_family_gate"] = {
        "all_family_counts": dict(sorted(all_counts.items())),
        "avoid_families": [list(family) for family in sorted(avoid)],
        "avoid_family_columns": sorted(avoid_columns),
        "kept_family_counts": dict(sorted(kept_counts.items())),
        "max_avoid_family_column_count": max_avoid_column_count,
        "preserve_certificate_forms": preserve_certificate_forms,
        "require_families": [list(family) for family in sorted(require)],
        "require_family_columns": sorted(require_columns),
    }
    return filtered, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-artifact", required=True, type=Path)
    parser.add_argument(
        "--avoid-families",
        default="",
        help="Semicolon-separated support families to drop, e.g. '3,5;5,6;0,6'.",
    )
    parser.add_argument(
        "--require-families",
        default="",
        help="Semicolon-separated support families to keep exclusively. Empty means any non-avoided family.",
    )
    parser.add_argument(
        "--avoid-family-columns",
        default="",
        help="Comma- or semicolon-separated factor columns to reject in any support family.",
    )
    parser.add_argument(
        "--require-family-columns",
        default="",
        help="Comma- or semicolon-separated factor columns; every kept support column must be in this set.",
    )
    parser.add_argument(
        "--max-avoid-family-column-count",
        type=int,
        default=None,
        help="Allow kept families to touch at most this many avoid-family-columns.",
    )
    parser.add_argument(
        "--preserve-certificate-forms-if-any-pass",
        action="store_true",
        help=(
            "Keep every form in a certificate if at least one form passes the family "
            "gate. This preserves target-elimination form pairs for downstream rank "
            "audits while still reporting which forms passed the gate."
        ),
    )
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = load_json(args.candidate_artifact)
    avoid = parse_families(args.avoid_families)
    require = parse_families(args.require_families)
    avoid_columns = parse_int_set(args.avoid_family_columns)
    require_columns = parse_int_set(args.require_family_columns)
    max_avoid_column_count = args.max_avoid_family_column_count
    certificates = [
        cert for cert in source.get("certificates") or []
        if isinstance(cert, dict)
    ]
    kept: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    all_family_counts: Counter[str] = Counter()
    kept_family_counts: Counter[str] = Counter()
    for cert_index, cert in enumerate(certificates):
        filtered, report = gate_certificate(
            cert,
            cert_index,
            avoid,
            require,
            avoid_columns,
            require_columns,
            max_avoid_column_count,
            bool(args.preserve_certificate_forms_if_any_pass),
        )
        reports.append(report)
        all_family_counts.update(report.get("all_family_counts") or {})
        kept_family_counts.update(report.get("kept_family_counts") or {})
        if filtered is not None:
            filtered["_artifact_offset"] = len(kept)
            kept.append(filtered)
    payload = {
        "artifacts": {
            "candidate_artifact": str(args.candidate_artifact),
        },
        "certificates": kept,
        "claim_status": (
            "FAMILY_GATED_CANDIDATES_FOUND"
            if kept
            else "NEGATIVE_RESULT_NO_FAMILY_GATED_CANDIDATES_FOUND"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: this is a post-export family gate, not target descent.",
            "HEURISTIC: family and column gating is based on prior toy holdout failures and derivable-column audits.",
            "NO SPEEDUP CLAIM: filtered candidates still require rank, repair-bank, family-holdout, source-cost, sparse-LA, and transfer gates.",
        ],
        "parameters": {
            "avoid_family_columns": sorted(avoid_columns),
            "avoid_families": [list(family) for family in sorted(avoid)],
            "max_avoid_family_column_count": max_avoid_column_count,
            "require_family_columns": sorted(require_columns),
            "require_families": [list(family) for family in sorted(require)],
        },
        "reports": reports,
        "schema": "ecdlp.low_term_total2_candidate_family_gate.v1",
        "summary": {
            "all_family_counts": dict(sorted(all_family_counts.items())),
            "candidate_certificate_count": len(certificates),
            "filtered_certificate_count": len(certificates) - len(kept),
            "kept_certificate_count": len(kept),
            "kept_family_counts": dict(sorted(kept_family_counts.items())),
            "kept_form_count": sum(len(cert.get("forms") or []) for cert in kept),
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
