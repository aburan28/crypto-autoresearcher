#!/usr/bin/env python3
"""P985 public false-positive discriminator for cumulative high-gap rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p869_p231_public_motif_predictor as p869
import low_term_total2_p870_p231_public_rule_materialization as p870
import low_term_total2_p872_p231_two_stage_materialization as p872
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p985_p231_cumulative_false_positive_discriminator.md"
DEFAULT_P984 = STATE_DIR / "low_term_total2_p984_p231_cumulative_high_gap_forward_probe.json"
DEFAULT_WINDOWS = (
    "11624_11631",
    "11632_11639",
    "11640_11647",
    "11648_11655",
    "11656_11663",
    "11664_11671",
    "11672_11679",
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p985_p231_cumulative_false_positive_discriminator_probe.json"
SCHEMA = "ecdlp.low_term_total2_p985_p231_cumulative_false_positive_discriminator.v1"
BROAD_LABEL = "union_public_key_verified AND union_rank >= 3 AND direct_ops_over_rho < 1"
HIGH_GAP_RULE = "top_k == 4 AND salt_gap >= 6"


@dataclass(frozen=True)
class PublicGuard:
    feature: str
    modulus: int
    allowed: tuple[Any, ...]

    @property
    def name(self) -> str:
        values = ",".join(str(value) for value in self.allowed)
        return f"{self.feature}_mod{self.modulus}_in_{values}"

    @property
    def rule(self) -> str:
        values = ", ".join(str(value) for value in self.allowed)
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


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
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


def high_gap_rule(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) == 4 and int_value(features.get("salt_gap"), -1) >= 6


def row_salts(case: dict[str, Any]) -> list[int]:
    salts = []
    for row_leaf in case.get("row_leaf_keys") or []:
        row_key = str(row_leaf.get("row_key"))
        if "salt" in row_key:
            salts.append(int_value(row_key.rsplit("salt", 1)[-1]))
    return sorted(salts)


def public_feature_value(case: dict[str, Any], feature: str, modulus: int) -> Any:
    public = case.get("public_features") or {}
    salts = row_salts(case)
    transfer = int_value(public.get("transfer_index"), int_value(case.get("transfer_index")))
    salt_gap = int_value(public.get("salt_gap"), -1)
    if feature == "min_salt":
        return min(salts) % modulus if salts else None
    if feature == "max_salt":
        return max(salts) % modulus if salts else None
    if feature == "salt_sum":
        return sum(salts) % modulus if salts else None
    if feature == "salt_pair":
        return tuple(salt % modulus for salt in salts)
    if feature == "transfer":
        return transfer % modulus
    if feature == "transfer_minus_min_salt":
        return (transfer - min(salts)) % modulus if salts else None
    if feature == "transfer_minus_max_salt":
        return (transfer - max(salts)) % modulus if salts else None
    if feature == "salt_gap":
        return salt_gap % modulus if salt_gap >= 0 else None
    return None


def guard_passes(case: dict[str, Any], guard: PublicGuard) -> bool:
    return public_feature_value(case, guard.feature, guard.modulus) in set(guard.allowed)


def is_direct_below_rho(case: dict[str, Any]) -> bool:
    return float_value(case.get("direct_ops_over_rho"), 10**9) < 1.0


def is_p867(case: dict[str, Any]) -> bool:
    return bool(case.get("p867_motif_verified_below_rho"))


def is_union(case: dict[str, Any]) -> bool:
    return bool(case.get("union_public_key_verified"))


def is_broad(case: dict[str, Any]) -> bool:
    return is_union(case) and int_value(case.get("union_rank")) >= 3 and is_direct_below_rho(case)


def is_rank4_broad(case: dict[str, Any]) -> bool:
    return is_broad(case) and int_value(case.get("union_rank")) >= 4


def relation_group_key(case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        case.get("target"),
        int_value(case.get("transfer_index")),
        case.get("union_derived_secret"),
        json.dumps(case.get("row_leaf_keys") or [], sort_keys=True),
    )


def row_leaf_set_key(case: dict[str, Any]) -> str:
    rows = []
    for row_leaf in case.get("row_leaf_keys") or []:
        rows.append(
            {
                "leaf_indices": [int_value(value) for value in row_leaf.get("leaf_indices") or []],
                "row_key": row_leaf.get("row_key"),
            }
        )
    return json.dumps(rows, sort_keys=True, separators=(",", ":"))


def matrix_form_proxy_key(case: dict[str, Any]) -> tuple[Any, ...]:
    public = case.get("public_features") or {}
    return (
        case.get("target"),
        case.get("leaf_selector"),
        tuple(public.get("leaf_gap_tuple") or []),
        row_leaf_set_key(case),
        int_value(case.get("union_rank")),
        int_value(case.get("union_relation_count")),
        int_value(case.get("relation_form_count")),
    )


def compact_case(case: dict[str, Any], guard: PublicGuard | None = None) -> dict[str, Any]:
    public = case.get("public_features") or {}
    payload = {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "is_broad_union_rank_ge3": is_broad(case),
        "is_p867": is_p867(case),
        "is_rank4_broad": is_rank4_broad(case),
        "leaf_selector": case.get("leaf_selector"),
        "matrix_form_proxy": list(matrix_form_proxy_key(case)),
        "relation_form_count": case.get("relation_form_count"),
        "row_salts": row_salts(case),
        "salt_gap": public.get("salt_gap"),
        "top_k": public.get("top_k"),
        "transfer_index": public.get("transfer_index") or case.get("transfer_index"),
        "union_public_key_verified": is_union(case),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
        "window": public.get("window") or case.get("window"),
    }
    if guard is not None:
        payload["guard_feature_value"] = public_feature_value(case, guard.feature, guard.modulus)
        payload["guard_passes"] = guard_passes(case, guard)
    return payload


def summarize_selected(name: str, selected_cases: list[dict[str, Any]]) -> dict[str, Any]:
    direct_sum = sum(float_value(case.get("direct_ops_over_rho")) for case in selected_cases)
    broad = [case for case in selected_cases if is_broad(case)]
    rank4 = [case for case in broad if int_value(case.get("union_rank")) >= 4]
    p867 = [case for case in selected_cases if is_p867(case)]
    union_verified = [case for case in selected_cases if is_union(case)]
    broad_relation_groups = {relation_group_key(case) for case in broad}
    return {
        "broad_direct_relation_amortized_ops_over_rho": ratio(direct_sum, len(broad_relation_groups)),
        "broad_matrix_form_proxy_count": len({matrix_form_proxy_key(case) for case in broad}),
        "broad_non_p867_count": sum(1 for case in broad if not is_p867(case)),
        "broad_precision": ratio(len(broad), len(selected_cases)),
        "broad_relation_group_count": len(broad_relation_groups),
        "broad_union_rank_ge3_count": len(broad),
        "direct_sum_ops_over_rho": round8(direct_sum),
        "leaf_selector_histogram": dict(sorted(Counter(str(case.get("leaf_selector")) for case in selected_cases).items())),
        "matrix_form_proxy_count": len({matrix_form_proxy_key(case) for case in selected_cases}),
        "max_direct_ops_over_rho": round8(
            max([float_value(case.get("direct_ops_over_rho")) for case in selected_cases], default=0.0)
        ),
        "min_direct_ops_over_rho": round8(
            min([float_value(case.get("direct_ops_over_rho")) for case in selected_cases], default=0.0)
        ),
        "name": name,
        "p867_positive_count": len(p867),
        "p867_precision": ratio(len(p867), len(selected_cases)),
        "p867_relation_group_count": len({relation_group_key(case) for case in p867}),
        "rank4_broad_count": len(rank4),
        "rank4_relation_group_count": len({relation_group_key(case) for case in rank4}),
        "rank_histogram": dict(sorted(Counter(str(case.get("union_rank")) for case in selected_cases).items())),
        "relation_form_count_sum": sum(int_value(case.get("relation_form_count")) for case in selected_cases),
        "relation_group_count": len({relation_group_key(case) for case in selected_cases}),
        "sample_broad_cases": [compact_case(case) for case in broad[:12]],
        "sample_selected_cases": [compact_case(case) for case in selected_cases[:12]],
        "salt_gap_histogram": dict(
            sorted(Counter(str((case.get("public_features") or {}).get("salt_gap")) for case in selected_cases).items())
        ),
        "selected_all_direct_below_rho": bool(
            selected_cases and all(is_direct_below_rho(case) for case in selected_cases)
        ),
        "selected_count": len(selected_cases),
        "union_precision": ratio(len(union_verified), len(selected_cases)),
        "union_relation_group_count": len({relation_group_key(case) for case in union_verified}),
        "union_verified_count": len(union_verified),
    }


def calibration_rows(p984: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for section in ("prior_cases", "fresh_cases"):
        for case in p984.get(section) or []:
            if isinstance(case, dict):
                rows.append(dict(case))
    return rows


def candidate_guards(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positives = [row for row in rows if is_broad(row)]
    negatives = [row for row in rows if not is_broad(row)]
    features = [
        "max_salt",
        "min_salt",
        "salt_sum",
        "salt_pair",
        "transfer",
        "transfer_minus_min_salt",
        "transfer_minus_max_salt",
        "salt_gap",
    ]
    candidates = []
    for modulus in range(2, 17):
        for feature_index, feature in enumerate(features):
            allowed = tuple(sorted({public_feature_value(row, feature, modulus) for row in positives}, key=str))
            if None in allowed:
                continue
            guard = PublicGuard(feature=feature, modulus=modulus, allowed=allowed)
            positive_preserved = sum(1 for row in positives if guard_passes(row, guard))
            negative_rejected = sum(1 for row in negatives if not guard_passes(row, guard))
            clean = positive_preserved == len(positives) and negative_rejected == len(negatives)
            candidates.append(
                {
                    "allowed_count": len(allowed),
                    "clean": clean,
                    "feature": feature,
                    "feature_priority": feature_index,
                    "guard": guard,
                    "modulus": modulus,
                    "name": guard.name,
                    "negative_rejected": negative_rejected,
                    "negative_total": len(negatives),
                    "positive_preserved": positive_preserved,
                    "positive_total": len(positives),
                    "rule": guard.rule,
                }
            )
    return candidates


def choose_guard(rows: list[dict[str, Any]]) -> tuple[PublicGuard | None, list[dict[str, Any]]]:
    candidates = candidate_guards(rows)
    clean = [candidate for candidate in candidates if candidate["clean"]]
    clean.sort(key=lambda row: (row["allowed_count"], row["modulus"], row["feature_priority"], row["name"]))
    if not clean:
        return None, candidates
    return clean[0]["guard"], candidates


def source_controls(p984: dict[str, Any]) -> dict[str, Any]:
    summary = p984.get("summary") or {}
    return {
        "p984_claim_expected": p984.get("claim_status") == "NEGATIVE_RESULT_P984_CUMULATIVE_HIGH_GAP_NOT_BELOW_RHO",
        "p984_control_pass": bool(summary.get("control_pass")),
        "p984_cumulative_selected_five": int_value(summary.get("cumulative_selected_count")) == 5,
        "p984_cumulative_broad_groups_four": int_value(summary.get("cumulative_broad_relation_group_count")) == 4,
        "p984_cumulative_broad_amortized_expected": summary.get("cumulative_broad_direct_relation_amortized_ops_over_rho")
        == 1.01094891,
    }


def analyze_validation(args: argparse.Namespace, guard: PublicGuard | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    windows = list(args.windows)
    source_paths = {window: p868.source_path(window) for window in windows}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    source_case_count_by_window: Counter[str] = Counter()
    first_stage_count_by_window: Counter[str] = Counter()
    second_stage_count_by_window: Counter[str] = Counter()
    high_gap_count_by_window: Counter[str] = Counter()
    guarded_count_by_window: Counter[str] = Counter()
    high_gap_selected: list[dict[str, Any]] = []
    guarded_selected: list[dict[str, Any]] = []

    for window in windows:
        source = p868.load_json(source_paths[window])
        params = repair_probe.source_parameters(source)
        probe_args = repair_probe.probe_args_from_source(source)
        cache_key = p868.json_key(
            {
                "bank_source": params.get("bank_source"),
                "config_source": params.get("config_source"),
                "direct_source": params.get("direct_source"),
                "radius": params.get("radius"),
                "transfer_source": params.get("transfer_source"),
            }
        )
        if cache_key not in build_cache:
            build_cache[cache_key] = (*repair_probe.build_specs(params), probe_args)
        verifier, records, config_source, specs_by_target, probe_args = build_cache[cache_key]

        for case in p868.iter_source_cases(source, window, targets):
            source_case_count_by_window[window] += 1
            context = hit_stream_probe.scan_case_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                case,
                probe_args,
                context_cache,
            )
            public_features = p869.public_features(case, context)
            if not p870.frozen_rule(public_features):
                continue
            first_stage_count_by_window[window] += 1
            if not p872.second_stage_rule(public_features):
                continue
            second_stage_count_by_window[window] += 1
            if not high_gap_rule(public_features):
                continue
            high_gap_count_by_window[window] += 1
            labeled = p868.analyze_case(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                context_cache,
                case,
            )
            row = p872.compact_selected_case(labeled, public_features)
            high_gap_selected.append(row)
            if guard is not None and guard_passes(row, guard):
                guarded_count_by_window[window] += 1
                guarded_selected.append(row)

    counts = {
        "first_stage_selected_case_count": sum(first_stage_count_by_window.values()),
        "first_stage_selected_count_by_window": dict(first_stage_count_by_window),
        "guarded_selected_case_count": sum(guarded_count_by_window.values()),
        "guarded_selected_count_by_window": dict(guarded_count_by_window),
        "high_gap_selected_case_count": sum(high_gap_count_by_window.values()),
        "high_gap_selected_count_by_window": dict(high_gap_count_by_window),
        "second_stage_selected_case_count": sum(second_stage_count_by_window.values()),
        "second_stage_selected_count_by_window": dict(second_stage_count_by_window),
        "source_case_count": sum(source_case_count_by_window.values()),
        "source_count_by_window": dict(source_case_count_by_window),
        "source_windows": {window: str(path) for window, path in source_paths.items()},
    }
    return high_gap_selected, guarded_selected, counts


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p984_path = Path(args.p984)
    p984 = load_json(p984_path)
    controls = source_controls(p984)
    calibration = calibration_rows(p984)
    guard, candidates = choose_guard(calibration)
    positives = [row for row in calibration if is_broad(row)]
    negatives = [row for row in calibration if not is_broad(row)]
    calibration_positive_preserved = sum(1 for row in positives if guard is not None and guard_passes(row, guard))
    calibration_negative_rejected = sum(1 for row in negatives if guard is None or not guard_passes(row, guard))
    calibration_pass = bool(
        guard is not None
        and calibration_positive_preserved == len(positives)
        and calibration_negative_rejected == len(negatives)
    )
    high_gap_rows, guarded_rows, validation_counts = analyze_validation(args, guard)
    high_gap_summary = summarize_selected("validation_high_gap", high_gap_rows)
    guarded_summary = summarize_selected("validation_guarded", guarded_rows)
    missed_broad_rows = [row for row in high_gap_rows if is_broad(row) and (guard is None or not guard_passes(row, guard))]
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in guarded_rows)
    validation_high_gap_reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in high_gap_rows)
    control_pass = all(controls.values())
    success = bool(
        control_pass
        and calibration_pass
        and reconstruction_error_count == 0
        and guarded_summary["selected_count"] > 0
        and guarded_summary["broad_relation_group_count"] > 0
        and (guarded_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) < 1.0
        and not missed_broad_rows
    )
    if not control_pass:
        claim = "NEGATIVE_RESULT_P985_CONTROL_FAILURE"
    elif not calibration_pass:
        claim = "NEGATIVE_RESULT_P985_NO_CLEAN_CALIBRATION_DISCRIMINATOR"
    elif guarded_summary["selected_count"] == 0:
        claim = "NEGATIVE_RESULT_P985_DISCRIMINATOR_SELECTS_NO_VALIDATION_ROWS"
    elif missed_broad_rows:
        claim = "NEGATIVE_RESULT_P985_DISCRIMINATOR_MISSES_VALIDATION_BROAD_ROWS"
    elif (guarded_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) >= 1.0:
        claim = "NEGATIVE_RESULT_P985_DISCRIMINATOR_NOT_BELOW_RHO_ON_VALIDATION"
    elif success:
        claim = "P985_PUBLIC_DISCRIMINATOR_VALIDATES_BELOW_RHO_ON_LATER_WINDOWS"
    else:
        claim = "NEGATIVE_RESULT_P985_DISCRIMINATOR_DIVERSITY_OR_RECONSTRUCTION_FAILURE"

    top_candidates = [
        {key: value for key, value in candidate.items() if key != "guard"}
        for candidate in sorted(candidates, key=lambda row: (not row["clean"], row["allowed_count"], row["modulus"], row["feature_priority"], row["name"]))[:24]
    ]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p984_source": str(p984_path),
            "script": str(Path(__file__)),
            "source_windows": validation_counts["source_windows"],
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p984_source_sha256": sha256_file(p984_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "broad_label": BROAD_LABEL,
        "calibration": {
            "calibration_rows": [compact_case(row, guard) for row in calibration],
            "candidate_count": len(candidates),
            "clean_candidate_count": sum(1 for candidate in candidates if candidate["clean"]),
            "negative_count": len(negatives),
            "negative_rejected": calibration_negative_rejected,
            "positive_count": len(positives),
            "positive_preserved": calibration_positive_preserved,
            "promoted_guard": None if guard is None else {"name": guard.name, "rule": guard.rule},
            "top_candidates": top_candidates,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P985_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CALIBRATION-CHOSEN: the guard is selected from P984 cumulative rows before validation.",
            "PUBLIC-FEATURE-GUARD: selection uses public source-salt, transfer, and selector features.",
            "FALSE-POSITIVES-CHARGED: guarded amortization charges every guarded selected row.",
            "NO-END-TO-END-BREAK: this is not a complete faster-than-rho ECDLP algorithm or target descent.",
        ],
        "method": "p985_p231_cumulative_false_positive_discriminator",
        "parameters": {
            "base_high_gap_rule": HIGH_GAP_RULE,
            "broad_label": BROAD_LABEL,
            "first_stage_rule": p872.FIRST_STAGE_RULE,
            "promoted_guard": None if guard is None else {"name": guard.name, "rule": guard.rule},
            "second_stage_rule": p872.SECOND_STAGE_RULE,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "windows": list(args.windows),
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summaries": [high_gap_summary, guarded_summary],
        "summary": {
            "calibration_pass": calibration_pass,
            "control_pass": control_pass,
            "discriminator_validation_success": success,
            "missed_broad_count": len(missed_broad_rows),
            "reconstruction_error_count": reconstruction_error_count,
            "validation_high_gap_reconstruction_error_count": validation_high_gap_reconstruction_error_count,
            **{f"validation_{key}": value for key, value in validation_counts.items() if key != "source_windows"},
            **{f"high_gap_{key}": value for key, value in high_gap_summary.items()},
            **{f"guarded_{key}": value for key, value in guarded_summary.items()},
        },
        "validation_high_gap_cases": high_gap_rows,
        "validation_high_gap_cases_compact": [compact_case(row, guard) for row in high_gap_rows],
        "validation_guarded_cases": guarded_rows,
        "validation_guarded_cases_compact": [compact_case(row, guard) for row in guarded_rows],
        "missed_broad_cases_compact": [compact_case(row, guard) for row in missed_broad_rows],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P985 contract path")
    parser.add_argument("--p984", default=str(DEFAULT_P984), help="P984 calibration JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target ids")
    parser.add_argument("--windows", nargs="+", default=list(DEFAULT_WINDOWS), help="Validation windows")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    guard = payload["parameters"]["promoted_guard"]
    print(
        "claim={claim} guard={guard} high_gap={high_gap} guarded={guarded} "
        "guarded_broad_groups={broad_groups} guarded_broad_amortized={broad_amortized} "
        "missed_broad={missed} out={out}".format(
            claim=payload["claim_status"],
            guard=None if guard is None else guard["name"],
            high_gap=summary["validation_high_gap_selected_case_count"],
            guarded=summary["validation_guarded_selected_case_count"],
            broad_groups=summary["guarded_broad_relation_group_count"],
            broad_amortized=summary["guarded_broad_direct_relation_amortized_ops_over_rho"],
            missed=summary["missed_broad_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
