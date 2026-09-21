#!/usr/bin/env python3
"""P991 public-feature predictor audit for the P990 deriving basis family."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p985_p231_cumulative_false_positive_discriminator as p985


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p991_p231_public_basis_predictor_audit.md"
DEFAULT_P988 = STATE_DIR / "low_term_total2_p988_p231_forward_high_gap_density_audit_probe.json"
DEFAULT_P990 = STATE_DIR / "low_term_total2_p990_p231_term_basis_normalization_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p991_p231_public_basis_predictor_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p991_p231_public_basis_predictor_audit.v1"
TARGET_TERM_BASIS = "[3,3,5,5]"


@dataclass(frozen=True)
class PredicateSpec:
    name: str
    feature: str
    modulus: int | None
    allowed: tuple[Any, ...]
    priority: int

    @property
    def rule(self) -> str:
        values = ", ".join(str(value) for value in self.allowed)
        if self.modulus is None:
            return f"{self.feature} in {{{values}}}"
        return f"{self.feature} mod {self.modulus} in {{{values}}}"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def round8(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 8)


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round8(float(numerator) / float(denominator))


def row_salts(row: dict[str, Any]) -> list[int]:
    salts = row.get("row_salts")
    if salts:
        return sorted(int_value(value) for value in salts)
    return p985.row_salts(row)


def leaf_gap_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    public = row.get("public_features") or {}
    if public.get("leaf_gap_tuple") is not None:
        return tuple(int_value(value) for value in public.get("leaf_gap_tuple") or [])
    proxy = row.get("matrix_form_proxy") or []
    if len(proxy) > 2 and isinstance(proxy[2], list):
        return tuple(int_value(value) for value in proxy[2])
    return ()


def feature_value(row: dict[str, Any], feature: str, modulus: int | None) -> Any:
    salts = row_salts(row)
    transfer = int_value(row.get("transfer_index"))
    salt_gap = int_value(row.get("salt_gap"), -1)
    if feature == "salt_gap":
        value: Any = salt_gap
    elif feature == "top_k":
        value = int_value(row.get("top_k"))
    elif feature == "leaf_gap_tuple":
        value = leaf_gap_tuple(row)
    elif feature == "min_salt":
        value = min(salts) if salts else None
    elif feature == "max_salt":
        value = max(salts) if salts else None
    elif feature == "salt_sum":
        value = sum(salts) if salts else None
    elif feature == "salt_pair":
        value = tuple(salts)
    elif feature == "transfer":
        value = transfer
    elif feature == "transfer_minus_min_salt":
        value = transfer - min(salts) if salts else None
    elif feature == "transfer_minus_max_salt":
        value = transfer - max(salts) if salts else None
    elif feature == "transfer_plus_salt_sum":
        value = transfer + sum(salts) if salts else None
    else:
        value = None
    if value is None or modulus is None:
        return value
    if isinstance(value, tuple):
        return tuple(int_value(item) % modulus for item in value)
    return int_value(value) % modulus


def predicate_passes(row: dict[str, Any], predicate: PredicateSpec) -> bool:
    return feature_value(row, predicate.feature, predicate.modulus) in set(predicate.allowed)


def rule_passes(row: dict[str, Any], predicates: tuple[PredicateSpec, ...]) -> bool:
    return all(predicate_passes(row, predicate) for predicate in predicates)


def source_controls(p990: dict[str, Any]) -> dict[str, Any]:
    summary = p990.get("summary") or {}
    deriving = [
        row for row in ((p990.get("diagnostics") or {}).get("best_groups") or [])
        if row.get("group_type") == "exact_term_basis" and row.get("group_key") == TARGET_TERM_BASIS
    ]
    deriving_cases = set(deriving[0].get("case_ids") or []) if deriving else set()
    return {
        "p990_claim_expected": p990.get("claim_status") == "P990_TERM_BASIS_GROUP_DERIVES_SECRET",
        "p990_control_pass": bool(summary.get("control_pass")),
        "p990_deriver_count_two": int_value(summary.get("secret_deriving_below_rho_group_count")) == 2,
        "p990_target_basis_present": bool(deriving),
        "p990_target_basis_derives": bool(deriving and deriving[0].get("mixed_wide_relations_derive_secret")),
        "p990_target_basis_cases_expected": deriving_cases
        == {
            "11600_11607:11603:22050.cf1@11731:mode_low_term_span_total10:4",
            "11792_11799:11792:22050.cf1@11731:mode_low_term_span_total10:4",
        },
    }


def target_case_ids(p990: dict[str, Any]) -> set[str]:
    for row in (p990.get("diagnostics") or {}).get("best_groups") or []:
        if row.get("group_type") == "exact_term_basis" and row.get("group_key") == TARGET_TERM_BASIS:
            return set(str(case_id) for case_id in row.get("case_ids") or [])
    return set()


def calibration_rows(p988: dict[str, Any], positives: set[str]) -> list[dict[str, Any]]:
    rows = []
    for row in p988.get("combined_cases_compact") or []:
        if not isinstance(row, dict):
            continue
        copied = dict(row)
        copied["target_basis_positive"] = str(copied.get("case_id")) in positives
        rows.append(copied)
    return rows


def feature_specs(rows: list[dict[str, Any]], positives: list[dict[str, Any]]) -> list[PredicateSpec]:
    families: list[tuple[str, int | None, int]] = [
        ("salt_gap", None, 0),
        ("transfer", 7, 1),
        ("transfer", 8, 2),
        ("transfer", 9, 3),
        ("transfer", 11, 4),
        ("transfer", 13, 5),
        ("transfer", 16, 6),
        ("transfer_minus_min_salt", 7, 7),
        ("transfer_minus_max_salt", 7, 8),
        ("transfer_plus_salt_sum", 7, 9),
        ("min_salt", 8, 10),
        ("max_salt", 8, 11),
        ("salt_sum", 8, 12),
        ("salt_pair", 8, 13),
        ("leaf_gap_tuple", None, 14),
        ("top_k", None, 15),
        ("min_salt", None, 20),
        ("max_salt", None, 21),
        ("salt_pair", None, 22),
    ]
    specs = []
    for feature, modulus, priority in families:
        allowed = tuple(sorted({feature_value(row, feature, modulus) for row in positives}, key=str))
        if None in allowed or not allowed:
            continue
        name = f"{feature}" if modulus is None else f"{feature}_mod{modulus}"
        specs.append(PredicateSpec(name=name, feature=feature, modulus=modulus, allowed=allowed, priority=priority))
    return specs


def summarize_rule(name: str, predicates: tuple[PredicateSpec, ...], rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if rule_passes(row, predicates)]
    positives = [row for row in rows if row.get("target_basis_positive")]
    selected_positive = [row for row in selected if row.get("target_basis_positive")]
    selected_negative = [row for row in selected if not row.get("target_basis_positive")]
    direct_sum = sum(float(row.get("direct_ops_over_rho") or 0.0) for row in selected)
    return {
        "direct_sum_ops_over_rho": round8(direct_sum),
        "false_positive_count": len(selected_negative),
        "name": name,
        "positive_preserved_count": len(selected_positive),
        "positive_total": len(positives),
        "precision": ratio(len(selected_positive), len(selected)),
        "predicates": [{"name": predicate.name, "rule": predicate.rule} for predicate in predicates],
        "recall": ratio(len(selected_positive), len(positives)),
        "selected_amortized_ops_over_rho": ratio(direct_sum, len(selected)),
        "selected_case_ids": [row.get("case_id") for row in selected],
        "selected_count": len(selected),
    }


def candidate_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positives = [row for row in rows if row.get("target_basis_positive")]
    specs = feature_specs(rows, positives)
    rules: list[tuple[PredicateSpec, ...]] = [(spec,) for spec in specs]
    rules.extend(tuple(pair) for pair in itertools.combinations(specs, 2))
    summaries = []
    seen = set()
    for predicates in rules:
        key = tuple(predicate.name for predicate in predicates)
        if key in seen:
            continue
        seen.add(key)
        name = " AND ".join(predicate.name for predicate in predicates)
        summaries.append(summarize_rule(name, predicates, rows))
    summaries.sort(
        key=lambda row: (
            row["false_positive_count"],
            -row["positive_preserved_count"],
            len(row["predicates"]),
            sum(next(spec.priority for spec in specs if spec.name == predicate["name"]) for predicate in row["predicates"]),
            row["name"],
        )
    )
    return summaries


def loo_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in rows if row.get("target_basis_positive")]
    folds = []
    for heldout in positives:
        train = []
        for row in rows:
            copied = dict(row)
            if row.get("case_id") == heldout.get("case_id"):
                copied["target_basis_positive"] = False
            train.append(copied)
        candidates = candidate_rules(train)
        clean = [
            candidate for candidate in candidates
            if candidate["false_positive_count"] == 0 and candidate["positive_preserved_count"] == len(positives) - 1
        ]
        chosen = clean[0] if clean else (candidates[0] if candidates else None)
        predicates = tuple(
            parse_predicate_from_summary(predicate, train)
            for predicate in (chosen or {}).get("predicates") or []
        )
        passes = bool(chosen and rule_passes(heldout, predicates))
        folds.append(
            {
                "chosen_rule": chosen,
                "heldout_case_id": heldout.get("case_id"),
                "heldout_passes": passes,
            }
        )
    return {
        "fold_count": len(folds),
        "folds": folds,
        "passed": bool(folds and all(fold["heldout_passes"] for fold in folds)),
    }


def parse_predicate_from_summary(predicate_summary: dict[str, Any], rows: list[dict[str, Any]]) -> PredicateSpec:
    name = str(predicate_summary.get("name"))
    positives = [row for row in rows if row.get("target_basis_positive")]
    for spec in feature_specs(rows, positives):
        if spec.name == name:
            return spec
    raise ValueError(f"predicate not found: {name}")


def available_later_windows(start_transfer: int, stop_transfer: int, max_windows: int) -> tuple[list[str], list[str]]:
    available: list[str] = []
    missing: list[str] = []
    current = start_transfer
    for _ in range(max_windows):
        if current > stop_transfer:
            break
        window = f"{current}_{current + 7}"
        if p868.source_path(window).exists():
            available.append(window)
        else:
            missing.append(window)
        current += 8
    return available, missing


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p988_path = Path(args.p988)
    p990_path = Path(args.p990)
    p988 = load_json(p988_path)
    p990 = load_json(p990_path)
    controls = source_controls(p990)
    control_pass = all(controls.values())
    positives = target_case_ids(p990)
    rows = calibration_rows(p988, positives)
    candidates = candidate_rules(rows)
    clean = [
        candidate for candidate in candidates
        if candidate["false_positive_count"] == 0 and candidate["positive_preserved_count"] == len(positives)
    ]
    chosen = clean[0] if clean else (candidates[0] if candidates else None)
    loo = loo_report(rows)
    available, missing = available_later_windows(args.forward_start, args.forward_stop, args.forward_max_windows)
    success = bool(control_pass and chosen and chosen["false_positive_count"] == 0 and loo["passed"] and available)
    if not control_pass:
        claim = "NEGATIVE_RESULT_P991_CONTROL_FAILURE"
    elif not chosen:
        claim = "NEGATIVE_RESULT_P991_NO_PUBLIC_PREDICTOR_CANDIDATES"
    elif chosen["false_positive_count"] != 0:
        claim = "NEGATIVE_RESULT_P991_NO_CLEAN_PUBLIC_PREDICTOR"
    elif not loo["passed"]:
        claim = "NEGATIVE_RESULT_P991_PUBLIC_PREDICTOR_LOO_FAILS"
    elif not available:
        claim = "NEGATIVE_RESULT_P991_PUBLIC_PREDICTOR_CLEAN_BUT_NO_FORWARD_WINDOWS"
    elif success:
        claim = "P991_PUBLIC_BASIS_PREDICTOR_READY_FOR_FORWARD_VALIDATION"
    else:
        claim = "NEGATIVE_RESULT_P991_INVARIANT_FAILURE"
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p988_source": str(p988_path),
            "p990_source": str(p990_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p988_source_sha256": sha256_file(p988_path),
            "p990_source_sha256": sha256_file(p990_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P991_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-PREDICTOR: predicate body uses only pre-reconstruction row salts, transfer residues, salt gap, top_k, and leaf-gap tuple.",
            "CALIBRATION-ONLY: no later p231 source windows are currently available for forward validation.",
            "POST-RECONSTRUCTION-LABEL: positives come from P990 exact-basis reconstruction.",
            "NO-END-TO-END-BREAK: this does not establish sparse linear algebra or target descent.",
        ],
        "method": "p991_p231_public_basis_predictor_audit",
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "calibration_clean_candidate_count": len(clean),
            "calibration_row_count": len(rows),
            "chosen_false_positive_count": None if chosen is None else chosen["false_positive_count"],
            "chosen_positive_preserved_count": None if chosen is None else chosen["positive_preserved_count"],
            "chosen_selected_count": None if chosen is None else chosen["selected_count"],
            "control_pass": control_pass,
            "forward_available_window_count": len(available),
            "forward_missing_window_count": len(missing),
            "loo_passed": loo["passed"],
            "positive_case_count": len(positives),
            "public_predictor_success": success,
            "target_term_basis": TARGET_TERM_BASIS,
        },
        "calibration_rows": [
            {
                "case_id": row.get("case_id"),
                "direct_ops_over_rho": row.get("direct_ops_over_rho"),
                "leaf_gap_tuple": list(leaf_gap_tuple(row)),
                "row_salts": row_salts(row),
                "salt_gap": row.get("salt_gap"),
                "target_basis_positive": row.get("target_basis_positive"),
                "top_k": row.get("top_k"),
                "transfer_index": row.get("transfer_index"),
            }
            for row in rows
        ],
        "chosen_predictor": chosen,
        "top_candidates": candidates[:24],
        "leave_one_positive_out": loo,
        "forward_windows": {
            "available": available,
            "missing": missing,
            "start_transfer": args.forward_start,
            "stop_transfer": args.forward_stop,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P991 contract path")
    parser.add_argument("--p988", default=str(DEFAULT_P988), help="P988 forward density JSON")
    parser.add_argument("--p990", default=str(DEFAULT_P990), help="P990 term-basis JSON")
    parser.add_argument("--forward-start", type=int, default=11904, help="First later source window start")
    parser.add_argument("--forward-stop", type=int, default=12048, help="Last later source window start")
    parser.add_argument("--forward-max-windows", type=int, default=24, help="Maximum later windows to inspect")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    chosen = payload.get("chosen_predictor") or {}
    print(
        "claim={claim} positives={positives} chosen={chosen} selected={selected} "
        "false_pos={false_pos} loo={loo} forward_windows={forward} out={out}".format(
            claim=payload["claim_status"],
            positives=summary["positive_case_count"],
            chosen=chosen.get("name"),
            selected=summary["chosen_selected_count"],
            false_pos=summary["chosen_false_positive_count"],
            loo=summary["loo_passed"],
            forward=summary["forward_available_window_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
