#!/usr/bin/env python3
"""Export public relation-equation certificates from direct source rows.

The shared-product certificate exporter intentionally certifies only rows that
survive the amortized selected-product replay.  This companion exporter keeps a
narrower boundary: it replays the direct selected-leaf scanner for named public
source cases and exports the same compact public linear forms.  It is useful for
testing whether a candidate factor-column direction is visible before a
shared-product-compatible gate has been found.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import low_term_total2_fixed_leaf_shared_context_audit_probe as context_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_source_relation_equation_certificate import compact_form


DEFAULT_SOURCE = (
    "ecdlp_index_calculus_state/"
    "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_2400_2407_probe.json"
)


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


def parse_cases(raw: str) -> list[tuple[str, int, str, int]]:
    cases: list[tuple[str, int, str, int]] = []
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split("|")
        if len(parts) != 4:
            raise ValueError("cases must look like TARGET|TRANSFER|SELECTOR|TOP_K")
        target, transfer, selector, top_k = parts
        cases.append((target, int(transfer), selector, int(top_k)))
    return cases


def selected_term_support(contexts: list[dict[str, Any]]) -> list[int]:
    support: set[int] = set()
    for context in contexts:
        selected = {int_value(leaf) for leaf in context.get("selected_leaf_indices") or []}
        for scout in context["built"].get("scouts") or []:
            pos = scout.get("scout_pos")
            if pos in selected or (isinstance(pos, int) and pos - 1 in selected):
                support.update(int_value(index) for index, _sign in scout.get("signed_terms") or [])
    return sorted(support)


def direct_unique_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in rows:
        scan = row.get("_scan") if isinstance(row.get("_scan"), dict) else {}
        for event in scan.get("relation_events") or []:
            coeffs, rhs, _terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            events.append(event)
    return events


def certificate_for_case(
    source: dict[str, Any],
    source_path: Path,
    target: str,
    transfer_index: int,
    selector: str,
    top_k: int,
) -> dict[str, Any]:
    source_case = context_probe.find_source_case(source, target, transfer_index, selector, top_k)
    verifier, contexts, product_factor, max_relations = timing_probe.selected_contexts_from_source_case(
        source,
        source_case,
    )
    direct_rows, direct_ops, rho, row_profiles = timing_probe.direct_witness_rows(verifier, contexts)
    built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
    direct_union = direct_witness_probe.union_derive(verifier, direct_rows, built_by_row, "_scan")
    if not contexts:
        raise ValueError(f"no selected contexts for {target} {transfer_index} {selector} top{top_k}")
    order = int(contexts[0]["built"]["order"])
    events = direct_unique_events(direct_rows)
    public_key_verified = bool(direct_union.get("union_public_key_verified"))
    derived_secret = direct_union.get("union_derived_secret")
    return {
        "certificate_status": (
            "PUBLIC_DIRECT_RELATION_EQUATIONS_VERIFY_PUBLIC_KEY"
            if public_key_verified
            else "PUBLIC_DIRECT_RELATION_EQUATIONS_NEED_REVIEW"
        ),
        "clause": "direct_source",
        "derived_secret": derived_secret,
        "expected_secret": derived_secret if public_key_verified else None,
        "forms": [compact_form(event, order) for event in events],
        "forms_count": len(events),
        "order": order,
        "product_factor": product_factor,
        "public_key_verified": public_key_verified,
        "rank": int_value(direct_union.get("union_rank")),
        "scan_row_count": len(direct_rows),
        "selected": {
            "clause": "direct_source",
            "direct_ops": direct_ops,
            "direct_ops_over_rho": ratio(direct_ops, rho),
            "rho": rho,
            "row_keys": source_case.get("row_keys") or [],
            "secret": derived_secret if public_key_verified else None,
            "selector": selector,
            "shared_ops": None,
            "shared_ops_over_rho": None,
            "target": target,
            "top_k": top_k,
            "transfer_index": transfer_index,
        },
        "source": str(source_path),
        "source_case_selector": {
            "selector": source_case.get("selector"),
            "target": source_case.get("target"),
            "top_k": source_case.get("top_k"),
            "transfer_index": source_case.get("transfer_index"),
        },
        "selected_term_support": selected_term_support(contexts),
        "timing": None,
        "window": "_".join(str(part) for part in [transfer_index, transfer_index]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument(
        "--cases",
        required=True,
        help="Semicolon-separated TARGET|TRANSFER|SELECTOR|TOP_K entries.",
    )
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = Path(args.source)
    source = load_json(source_path)
    certificates = [
        certificate_for_case(source, source_path, target, transfer, selector, top_k)
        for target, transfer, selector, top_k in parse_cases(args.cases)
    ]
    passing = [
        cert
        for cert in certificates
        if cert.get("certificate_status") == "PUBLIC_DIRECT_RELATION_EQUATIONS_VERIFY_PUBLIC_KEY"
    ]
    payload = {
        "artifacts": {"source": str(source_path)},
        "certificates": certificates,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: equations are replayed from direct selected-leaf source rows in the local verifier relation model.",
            "These direct-source equations are not shared-product amortized certificates; they are a bridge for testing missing factor-column visibility.",
            "This is not a complete index-calculus target descent for deployed curves.",
        ],
        "schema": "ecdlp.low_term_total2_direct_source_relation_equation_certificate.v1",
        "summary": {
            "certificate_count": len(certificates),
            "claim_status": (
                "PUBLIC_DIRECT_RELATION_EQUATION_CERTIFICATES_ALL_PASS"
                if certificates and len(passing) == len(certificates)
                else "PUBLIC_DIRECT_RELATION_EQUATION_CERTIFICATES_INCOMPLETE"
            ),
            "passing_certificate_count": len(passing),
            "targets": sorted({str((cert.get("selected") or {}).get("target")) for cert in certificates}),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
