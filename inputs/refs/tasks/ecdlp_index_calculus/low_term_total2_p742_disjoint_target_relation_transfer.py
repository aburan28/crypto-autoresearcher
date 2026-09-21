#!/usr/bin/env python3
"""P742 disjoint-target relation translation and factor-bank transfer audit.

P741 found a non-22050 order-11779 target, ``67.a1@11789``. This audit uses
existing top-trial relation rows for that target as warm-start candidate
relations, translates them into P738/P740-style modular forms, verifies those
forms against the current verifier factor base, and then applies the old P740
order-11779 factor bank without using any candidate certificate as training.
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import low_term_total2_p740_disjoint_source_bank_transfer as p740
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


TASK_DIR = Path(__file__).resolve().parent
ENV_MAIN = TASK_DIR / "environment" / "main.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TARGET = "67.a1@11789"
DEFAULT_TRAINING_BANK = (
    STATE_DIR
    / "low_term_total2_target_eliminated_factor_relation_bank_dual_order_fullrank_11779_9887_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p742_disjoint_target_relation_transfer_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p742_disjoint_target_relation_transfer.md"
SCHEMA = "ecdlp.low_term_total2_p742_disjoint_target_relation_transfer.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_verifier_module() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_verifier_main", ENV_MAIN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import verifier helpers from {ENV_MAIN}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "median": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "median": median(values),
        "min": min(values),
    }


def parse_target(raw: str) -> tuple[str, int]:
    label, sep, prime = raw.partition("@")
    if not sep or not label:
        raise argparse.ArgumentTypeError(f"target must be label@prime: {raw!r}")
    return label, int(prime)


def target_key(label: str, p: int) -> str:
    return f"{label}@{int(p)}"


def load_target(verifier: Any, target: str) -> tuple[dict[str, Any], dict[str, Any]]:
    label, p = parse_target(target)
    by_label = {record["label"]: record for record in verifier.load_records()}
    record = by_label.get(label)
    if record is None:
        raise ValueError(f"unknown verifier label {label!r}")
    inv = verifier.reduction_invariants(record, p)
    return record, inv


def build_challenge(verifier: Any, record: dict[str, Any], inv: dict[str, Any], secret: int | None = None) -> dict[str, Any]:
    order = int_value(inv.get("base_order"))
    p = int_value(inv.get("p"))
    secret_value = 1 if secret is None else int(secret) % order
    public = verifier.mul_point(secret_value, inv["base"], record["ainvs"], p)
    factor_seed = f"{inv['label']}:{p}:{order}"
    factor_base = verifier.build_factor_base(record["ainvs"], p, order, seed=factor_seed)
    return {
        "label": inv["label"],
        "isogeny_class": inv.get("isogeny_class"),
        "p": p,
        "ainvs": record["ainvs"],
        "group_order": int_value(inv.get("order")),
        "base": verifier.point_to_json(inv["base"]),
        "base_order": order,
        "public": verifier.point_to_json(public),
        "factor_base": [verifier.point_to_json(point) for point in factor_base],
        "generic_rho_steps": math.ceil(math.sqrt(math.pi * order / 2.0)),
        "factor_base_seed": factor_seed,
    }


def load_jsonl_relations(path: Path) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            relations.append({"_line_number": line_number, "_parse_error": f"JSONDecodeError: {exc}"})
            continue
        if isinstance(row, dict):
            row["_line_number"] = line_number
            relations.append(row)
    return relations


def compact_form(coeffs: tuple[int, ...], rhs: int, terms: list[int]) -> dict[str, Any]:
    return {
        "coeffs": [int(value) for value in coeffs],
        "rhs": int(rhs),
        "terms": [int(term) for term in terms],
    }


def unique_forms(forms: list[tuple[tuple[int, ...], int, list[int], dict[str, Any]]]) -> list[tuple[tuple[int, ...], int, list[int], dict[str, Any]]]:
    seen: set[tuple[tuple[int, ...], int]] = set()
    out: list[tuple[tuple[int, ...], int, list[int], dict[str, Any]]] = []
    for coeffs, rhs, terms, relation in forms:
        key = (tuple(int(value) for value in coeffs), int(rhs))
        if key in seen:
            continue
        seen.add(key)
        out.append((coeffs, rhs, terms, relation))
    return out


def relation_support_stats(forms: list[dict[str, Any]], order: int) -> dict[str, Any]:
    support_sizes = []
    q_coeffs = set()
    touched = set()
    for form in forms:
        coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
        if coeffs:
            q_coeffs.add(coeffs[0])
        support = [index for index, coeff in enumerate(coeffs[1:]) if coeff % order]
        touched.update(support)
        support_sizes.append(len(support))
    return {
        "distinct_factor_columns": len(touched),
        "distinct_q_coefficients": len(q_coeffs),
        "factor_columns": sorted(touched),
        "support_size_stats": stat(support_sizes),
    }


def certificate_from_relation_file(
    verifier: Any,
    record: dict[str, Any],
    inv: dict[str, Any],
    relation_path: Path,
    target: str,
) -> dict[str, Any]:
    order = int_value(inv.get("base_order"))
    p = int_value(inv.get("p"))
    base = inv["base"]
    ainvs = record["ainvs"]
    syntax_challenge = build_challenge(verifier, record, inv)
    raw_relations = load_jsonl_relations(relation_path)
    parse_error_count = sum(1 for row in raw_relations if row.get("_parse_error"))

    syntax_forms: list[tuple[tuple[int, ...], int, list[int], dict[str, Any]]] = []
    syntax_error_count = 0
    for relation in raw_relations:
        if relation.get("_parse_error"):
            continue
        terms = verifier.relation_terms(relation, syntax_challenge, ainvs, p)
        if terms is None:
            syntax_error_count += 1
            continue
        coeffs, rhs = verifier.relation_linear_form(relation, terms, syntax_challenge, order)
        syntax_forms.append((tuple(coeffs), int(rhs), list(terms), relation))

    syntax_forms = unique_forms(syntax_forms)
    syntax_form_rows = [(coeffs, rhs, terms) for coeffs, rhs, terms, _relation in syntax_forms]
    inferred_secret, syntax_proves_secret, syntax_rank = verifier.derive_secret_from_relations(syntax_form_rows, order)
    verified_forms: list[tuple[tuple[int, ...], int, list[int], dict[str, Any]]] = []
    verify_error_count = 0
    public_key = None
    if inferred_secret is not None:
        verify_challenge = build_challenge(verifier, record, inv, int(inferred_secret))
        public_key = verifier.point_from_json(verify_challenge["public"])
        for coeffs, rhs, terms, relation in syntax_forms:
            if verifier.verify_relation(relation, verify_challenge, ainvs, p, base, public_key):
                verified_forms.append((coeffs, rhs, terms, relation))
            else:
                verify_error_count += 1

    verified_form_rows = [(coeffs, rhs, terms) for coeffs, rhs, terms, _relation in verified_forms]
    verified_secret, verified_proves_secret, verified_rank = verifier.derive_secret_from_relations(verified_form_rows, order)
    forms = [compact_form(coeffs, rhs, terms) for coeffs, rhs, terms, _relation in verified_forms]
    rowspace_ok = bool(
        verified_proves_secret
        and verified_secret is not None
        and inferred_secret is not None
        and int(verified_secret) % order == int(inferred_secret) % order
    )
    public_key_verified = rowspace_ok and len(forms) >= 2
    status = (
        "P742_DISJOINT_TARGET_RELATION_CERTIFICATE_PASS"
        if public_key_verified
        else "P742_DISJOINT_TARGET_RELATION_CERTIFICATE_NEEDS_REVIEW"
    )
    cost = load_json(relation_path.parent / "cost.json")
    return {
        "certificate_status": status,
        "clause": "p742_top_trial_mixed_wide_relation_rows",
        "derived_secret": int(verified_secret) if verified_secret is not None else None,
        "expected_secret": int(verified_secret) if public_key_verified and verified_secret is not None else None,
        "forms": forms,
        "forms_count": len(forms),
        "order": order,
        "product_factor": None,
        "public_key_verified": public_key_verified,
        "rank": int(verified_rank),
        "raw_relation_count": len(raw_relations),
        "rowspace_derives_expected_secret": rowspace_ok,
        "scan_row_count": len(forms),
        "selected": {
            "clause": "p742_top_trial_mixed_wide_relation_rows",
            "direct_ops": int_value(cost.get("group_ops"), len(raw_relations)),
            "direct_ops_over_rho": ratio(int_value(cost.get("group_ops"), len(raw_relations)), syntax_challenge["generic_rho_steps"]),
            "rho": syntax_challenge["generic_rho_steps"],
            "row_keys": [f"{target}:top_trial:{relation_path.parent.parent.parent.parent.name}"],
            "secret": int(verified_secret) if public_key_verified and verified_secret is not None else None,
            "selector": "top_trial_relations_jsonl",
            "shared_ops": None,
            "shared_ops_over_rho": None,
            "source_policy": "warm_start_top_trial_relation_rows",
            "target": target,
            "top_k": 0,
            "transfer_index": 0,
            "window": None,
        },
        "source": str(relation_path),
        "source_case_selector": {
            "selector": "top_trial_relations_jsonl",
            "target": target,
            "top_k": 0,
            "transfer_index": 0,
        },
        "support_summary": relation_support_stats(forms, order),
        "timing": None,
        "translation_diagnostics": {
            "factor_base_seed": syntax_challenge["factor_base_seed"],
            "factor_base_size": len(syntax_challenge["factor_base"]),
            "inferred_secret": int(inferred_secret) if inferred_secret is not None else None,
            "parse_error_count": parse_error_count,
            "syntax_error_count": syntax_error_count,
            "syntax_form_count": len(syntax_forms),
            "syntax_proves_secret": bool(syntax_proves_secret),
            "syntax_rank": int(syntax_rank),
            "verified_form_count": len(forms),
            "verified_proves_secret": bool(verified_proves_secret),
            "verified_rank": int(verified_rank),
            "verify_error_count": verify_error_count,
        },
        "window": relation_path.parent.parent.parent.parent.name,
    }


def relation_sources(args: argparse.Namespace, target: str) -> list[Path]:
    if args.relation_source:
        return sorted({Path(item) for item in args.relation_source})
    label, p = parse_target(target)
    target_dir = f"{label}_{p}"
    pattern = str(args.state_dir / "top_trials" / "*" / "artifacts" / "research" / target_dir / "relations.jsonl")
    return [Path(item) for item in sorted(glob.glob(pattern))]


def annotate_certificates(certs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated = []
    for index, cert in enumerate(certs):
        item = dict(cert)
        item["_artifact"] = str(cert.get("source") or "p742_in_memory_relation_certificate")
        item["_artifact_offset"] = index
        item["_global_index"] = index
        annotated.append(item)
    return annotated


def target_counts(certs: list[dict[str, Any]], order: int) -> dict[str, int]:
    counts = Counter(
        p740.selected_target(cert)
        for cert in certs
        if int_value(cert.get("order")) == order
    )
    return dict(sorted(counts.items()))


def determine_claim(
    cert_summary: dict[str, Any],
    transfer_audit: dict[str, Any],
    target_inventory: dict[str, Any],
) -> str:
    if int_value(transfer_audit.get("false_recoverable_form_count")):
        return "P742_DISJOINT_TARGET_FALSE_RECOVERY_NEEDS_REVIEW"
    if not int_value(cert_summary.get("verifier_valid_certificate_count")):
        return "NEGATIVE_RESULT_P742_NO_VERIFIER_VALID_DISJOINT_TARGET_CERTIFICATE"
    if int_value(transfer_audit.get("verified_recoverable_form_count")) and int_value(
        target_inventory.get("disjoint_order11779_candidate_target_count")
    ):
        return "P742_DISJOINT_TARGET_FACTOR_BANK_TRANSFER_SIGNAL"
    return "NEGATIVE_RESULT_P742_DISJOINT_TARGET_FACTOR_BANK_TRANSFER_NO_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    target = str(args.target)
    verifier = load_verifier_module()
    record, inv = load_target(verifier, target)
    order = int_value(inv.get("base_order"))
    paths = relation_sources(args, target)
    if not paths:
        raise ValueError(f"no relation sources found for {target}")

    certificates = [
        certificate_from_relation_file(verifier, record, inv, path, target)
        for path in paths
    ]
    candidate_certs = annotate_certificates(certificates)
    verifier_valid = [
        cert
        for cert in candidate_certs
        if cert.get("certificate_status") == "P742_DISJOINT_TARGET_RELATION_CERTIFICATE_PASS"
    ]
    training_paths = p740.training_paths_from_bank(Path(args.training_bank))
    training_certs = factor_bank.load_certificates(training_paths)
    transfer_audit = p740.audit_candidates(training_certs, verifier_valid, order)
    overlap = p740.source_window_overlap_report(training_certs, verifier_valid, order)
    training_targets = target_counts(training_certs, order)
    candidate_targets = target_counts(verifier_valid, order)
    disjoint_candidate_targets = sorted(set(candidate_targets) - set(training_targets))
    target_inventory = {
        "candidate_targets": candidate_targets,
        "disjoint_order11779_candidate_target_count": len(disjoint_candidate_targets),
        "disjoint_order11779_candidate_targets": disjoint_candidate_targets,
        "training_targets": training_targets,
    }
    cert_summary = {
        "candidate_certificate_count": len(candidate_certs),
        "candidate_relation_source_count": len(paths),
        "candidate_targets": sorted({str((cert.get("selected") or {}).get("target")) for cert in candidate_certs}),
        "distinct_expected_secrets": sorted(
            {
                int_value(cert.get("expected_secret"))
                for cert in verifier_valid
                if cert.get("expected_secret") is not None
            }
        ),
        "raw_relation_count": sum(int_value(cert.get("raw_relation_count")) for cert in candidate_certs),
        "translation_error_count": sum(
            int_value((cert.get("translation_diagnostics") or {}).get("parse_error_count"))
            + int_value((cert.get("translation_diagnostics") or {}).get("syntax_error_count"))
            + int_value((cert.get("translation_diagnostics") or {}).get("verify_error_count"))
            for cert in candidate_certs
        ),
        "verifier_valid_certificate_count": len(verifier_valid),
        "verifier_valid_form_count": sum(int_value(cert.get("forms_count")) for cert in verifier_valid),
    }
    payload = {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p741_inventory": str(args.state_dir / "low_term_total2_p741_order11779_disjoint_target_inventory.json"),
            "relation_sources": [str(path) for path in paths],
            "training_bank": str(args.training_bank),
            "training_certificate_paths": [str(path) for path in training_paths],
        },
        "candidate_certificate_summary": cert_summary,
        "candidate_certificates": certificates,
        "claim_status": "",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "WARM-START SOURCE: candidate relation rows come from existing top-trial artifacts, not fresh prospective harvesting.",
            "MODEL-BOUND: factor columns are the verifier's order-specific factor-base column namespace.",
            "DISJOINT TARGET: candidate certificates target 67.a1@11789 while the P740 training bank targets 22050.cf1@11731.",
            "NO FULL SPEEDUP CLAIM: relation generation, sparse linear algebra, and prospective target descent remain open.",
        ],
        "method": "p742_disjoint_target_relation_translation_and_p740_factor_bank_transfer",
        "order": order,
        "parameters": {
            "pollard_rho_baseline_steps": math.ceil(math.sqrt(math.pi * order / 2.0)),
            "target": target,
            "target_factor_base_size": int_value((certificates[0].get("translation_diagnostics") or {}).get("factor_base_size")),
            "training_bank_claim_status": load_json(Path(args.training_bank)).get("claim_status"),
        },
        "schema": SCHEMA,
        "source_window_overlap": overlap,
        "target_inventory": target_inventory,
        "target_metadata": {
            "base": verifier.point_to_json(inv["base"]),
            "base_order": order,
            "flags": inv.get("flags") or [],
            "group_order": int_value(inv.get("order")),
            "label": inv.get("label"),
            "p": int_value(inv.get("p")),
            "twist_order": int_value(inv.get("twist_order")),
        },
        "transfer_audit": transfer_audit,
    }
    payload["claim_status"] = determine_claim(cert_summary, transfer_audit, target_inventory)
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    transfer = payload["transfer_audit"]
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "candidate_certificate_summary": payload["candidate_certificate_summary"],
        "honesty_boundary": payload["honesty_boundary"],
        "order": payload["order"],
        "parameters": payload["parameters"],
        "source_window_overlap": payload["source_window_overlap"],
        "target_inventory": payload["target_inventory"],
        "target_metadata": payload["target_metadata"],
        "transfer_summary": {
            key: value
            for key, value in transfer.items()
            if key not in {"candidate_reports", "derived_factor_columns"}
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--training-bank", type=Path, default=DEFAULT_TRAINING_BANK)
    parser.add_argument("--relation-source", action="append", default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.state_dir = args.state_dir.expanduser().resolve()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "candidate_certificate_summary": summary["candidate_certificate_summary"],
                "claim_status": summary["claim_status"],
                "target_inventory": summary["target_inventory"],
                "transfer_summary": summary["transfer_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
