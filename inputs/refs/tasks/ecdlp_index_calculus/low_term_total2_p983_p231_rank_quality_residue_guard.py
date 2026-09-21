#!/usr/bin/env python3
"""P983 public residue guard for high-gap p231 rank quality."""

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
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p983_p231_rank_quality_residue_guard.md"
DEFAULT_P980 = STATE_DIR / "low_term_total2_p980_p231_high_gap_frozen_refinement_probe.json"
DEFAULT_P982 = STATE_DIR / "low_term_total2_p982_p231_broad_label_frozen_validation_probe.json"
DEFAULT_WINDOWS = (
    "11512_11519",
    "11520_11527",
    "11528_11535",
    "11536_11543",
    "11544_11551",
    "11552_11559",
    "11560_11567",
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p983_p231_rank_quality_residue_guard_probe.json"
SCHEMA = "ecdlp.low_term_total2_p983_p231_rank_quality_residue_guard.v1"
BROAD_LABEL = "union_public_key_verified AND union_rank >= 3 AND direct_ops_over_rho < 1"
BASE_HIGH_GAP_RULE = "top_k == 4 AND salt_gap >= 6"


@dataclass(frozen=True)
class ResidueGuard:
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


def row_salts(case: dict[str, Any]) -> list[int]:
    salts = []
    for row_leaf in case.get("row_leaf_keys") or []:
        row_key = str(row_leaf.get("row_key"))
        if "salt" in row_key:
            salts.append(int_value(row_key.rsplit("salt", 1)[-1]))
    return sorted(salts)


def feature_value(case: dict[str, Any], feature: str, modulus: int) -> Any:
    public = case.get("public_features") or {}
    salts = row_salts(case)
    if feature == "min_salt":
        return min(salts) % modulus if salts else None
    if feature == "max_salt":
        return max(salts) % modulus if salts else None
    if feature == "salt_sum":
        return sum(salts) % modulus if salts else None
    if feature == "salt_pair":
        return tuple(salt % modulus for salt in salts)
    if feature == "transfer":
        return int_value(public.get("transfer_index"), int_value(case.get("transfer_index"))) % modulus
    if feature == "transfer_minus_min_salt":
        return (int_value(public.get("transfer_index"), int_value(case.get("transfer_index"))) - min(salts)) % modulus if salts else None
    if feature == "transfer_minus_max_salt":
        return (int_value(public.get("transfer_index"), int_value(case.get("transfer_index"))) - max(salts)) % modulus if salts else None
    return None


def guard_passes(case: dict[str, Any], guard: ResidueGuard) -> bool:
    return feature_value(case, guard.feature, guard.modulus) in set(guard.allowed)


def high_gap_rule(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) == 4 and int_value(features.get("salt_gap"), -1) >= 6


def is_direct_below_rho(case: dict[str, Any]) -> bool:
    return float_value(case.get("direct_ops_over_rho"), 10**9) < 1.0


def is_p867(case: dict[str, Any]) -> bool:
    return bool(case.get("p867_motif_verified_below_rho"))


def is_union(case: dict[str, Any]) -> bool:
    return bool(case.get("union_public_key_verified"))


def is_broad(case: dict[str, Any]) -> bool:
    return is_union(case) and int_value(case.get("union_rank")) >= 3 and is_direct_below_rho(case)


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


def compact_case(case: dict[str, Any], guard: ResidueGuard | None = None) -> dict[str, Any]:
    public = case.get("public_features") or {}
    payload = {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "is_broad_union_rank_ge3": is_broad(case),
        "is_p867": is_p867(case),
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
        payload["guard_feature_value"] = feature_value(case, guard.feature, guard.modulus)
        payload["guard_passes"] = guard_passes(case, guard)
    return payload


def summarize_selected(selected_cases: list[dict[str, Any]]) -> dict[str, Any]:
    direct_sum = sum(float_value(case.get("direct_ops_over_rho")) for case in selected_cases)
    p867 = [case for case in selected_cases if is_p867(case)]
    union_verified = [case for case in selected_cases if is_union(case)]
    broad = [case for case in selected_cases if is_broad(case)]
    non_p867_broad = [case for case in broad if not is_p867(case)]
    broad_relation_groups = {relation_group_key(case) for case in broad}
    return {
        "broad_direct_relation_amortized_ops_over_rho": ratio(direct_sum, len(broad_relation_groups)),
        "broad_matrix_form_proxy_count": len({matrix_form_proxy_key(case) for case in broad}),
        "broad_non_p867_count": len(non_p867_broad),
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
        "p867_positive_count": len(p867),
        "p867_precision": ratio(len(p867), len(selected_cases)),
        "p867_relation_group_count": len({relation_group_key(case) for case in p867}),
        "rank4_broad_count": sum(1 for case in broad if int_value(case.get("union_rank")) >= 4),
        "rank_histogram": dict(sorted(Counter(str(case.get("union_rank")) for case in selected_cases).items())),
        "relation_form_count_sum": sum(int_value(case.get("relation_form_count")) for case in selected_cases),
        "relation_group_count": len({relation_group_key(case) for case in selected_cases}),
        "sample_broad_cases": [compact_case(case) for case in broad[:8]],
        "sample_selected_cases": [compact_case(case) for case in selected_cases[:8]],
        "selected_all_direct_below_rho": bool(
            selected_cases and all(is_direct_below_rho(case) for case in selected_cases)
        ),
        "selected_count": len(selected_cases),
        "union_precision": ratio(len(union_verified), len(selected_cases)),
        "union_relation_group_count": len({relation_group_key(case) for case in union_verified}),
        "union_verified_count": len(union_verified),
    }


def calibration_rows(p980: dict[str, Any], p982: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for source_name, payload in (("p980", p980), ("p982", p982)):
        for case in payload.get("selected_cases") or []:
            if not isinstance(case, dict):
                continue
            item = dict(case)
            item["calibration_source"] = source_name
            rows.append(item)
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
    ]
    candidates = []
    for modulus in range(2, 17):
        for feature_index, feature in enumerate(features):
            allowed = tuple(sorted({feature_value(row, feature, modulus) for row in positives}, key=str))
            if None in allowed:
                continue
            guard = ResidueGuard(feature=feature, modulus=modulus, allowed=allowed)
            positive_preserved = sum(1 for row in positives if guard_passes(row, guard))
            negative_rejected = sum(1 for row in negatives if not guard_passes(row, guard))
            clean = positive_preserved == len(positives) and negative_rejected == len(negatives)
            candidates.append(
                {
                    "guard": guard,
                    "clean": clean,
                    "feature": feature,
                    "feature_priority": feature_index,
                    "modulus": modulus,
                    "allowed_count": len(allowed),
                    "positive_preserved": positive_preserved,
                    "positive_total": len(positives),
                    "negative_rejected": negative_rejected,
                    "negative_total": len(negatives),
                    "rule": guard.rule,
                    "name": guard.name,
                }
            )
    return candidates


def choose_guard(rows: list[dict[str, Any]]) -> tuple[ResidueGuard | None, list[dict[str, Any]]]:
    candidates = candidate_guards(rows)
    clean = [candidate for candidate in candidates if candidate["clean"]]
    clean.sort(key=lambda row: (row["allowed_count"], row["modulus"], row["feature_priority"], row["name"]))
    if not clean:
        return None, candidates
    return clean[0]["guard"], candidates


def source_controls(p982: dict[str, Any]) -> dict[str, Any]:
    summary = p982.get("summary") or {}
    return {
        "p982_claim_is_expected": p982.get("claim_status")
        == "NEGATIVE_RESULT_P982_BROAD_LABEL_SIGNAL_NOT_BELOW_RHO_ON_LATER_WINDOWS",
        "p982_control_pass": bool(summary.get("control_pass")),
        "p982_selected_two": int_value(summary.get("selected_count")) == 2,
        "p982_broad_one": int_value(summary.get("broad_relation_group_count")) == 1,
        "p982_broad_amortized_expected": summary.get("broad_direct_relation_amortized_ops_over_rho") == 1.50364964,
        "p982_rank2_one": int_value((summary.get("rank_histogram") or {}).get("2")) == 1,
        "p982_rank3_one": int_value((summary.get("rank_histogram") or {}).get("3")) == 1,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p980_path = Path(args.p980)
    p982_path = Path(args.p982)
    p980 = load_json(p980_path)
    p982 = load_json(p982_path)
    rows = calibration_rows(p980, p982)
    guard, candidates = choose_guard(rows)
    controls = source_controls(p982)
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
            selected = p872.compact_selected_case(labeled, public_features)
            high_gap_selected.append(selected)
            if guard is not None and guard_passes(selected, guard):
                guarded_count_by_window[window] += 1
                guarded_selected.append(selected)

    high_gap_summary = summarize_selected(high_gap_selected)
    guarded_summary = summarize_selected(guarded_selected)
    calibration_positive_count = sum(1 for row in rows if is_broad(row))
    calibration_negative_count = sum(1 for row in rows if not is_broad(row))
    calibration_positive_preserved = sum(1 for row in rows if is_broad(row) and guard is not None and guard_passes(row, guard))
    calibration_negative_rejected = sum(1 for row in rows if not is_broad(row) and (guard is None or not guard_passes(row, guard)))
    calibration_pass = bool(
        guard is not None
        and calibration_positive_preserved == calibration_positive_count
        and calibration_negative_rejected == calibration_negative_count
    )
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in guarded_selected)
    control_pass = all(controls.values())
    success = bool(
        control_pass
        and calibration_pass
        and reconstruction_error_count == 0
        and guarded_summary["selected_count"] > 0
        and guarded_summary["broad_relation_group_count"] > 0
        and (guarded_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) < 1.0
        and guarded_summary["broad_matrix_form_proxy_count"] >= 1
    )
    if not control_pass:
        claim = "NEGATIVE_RESULT_P983_CONTROL_FAILURE"
    elif not calibration_pass:
        claim = "NEGATIVE_RESULT_P983_NO_CLEAN_CALIBRATION_GUARD"
    elif guarded_summary["selected_count"] == 0:
        claim = "NEGATIVE_RESULT_P983_RESIDUE_GUARD_SELECTS_NO_LATER_ROWS"
    elif guarded_summary["broad_relation_group_count"] == 0:
        claim = "NEGATIVE_RESULT_P983_RESIDUE_GUARD_HAS_NO_BROAD_VALIDATION_ROWS"
    elif (guarded_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) >= 1.0:
        claim = "NEGATIVE_RESULT_P983_RESIDUE_GUARD_NOT_BELOW_RHO_ON_VALIDATION"
    elif success:
        claim = "P983_RESIDUE_GUARD_VALIDATES_BROAD_RANK_SIGNAL_BELOW_RHO"
    else:
        claim = "NEGATIVE_RESULT_P983_RESIDUE_GUARD_DIVERSITY_OR_RECONSTRUCTION_FAILURE"

    top_candidates = [
        {key: value for key, value in candidate.items() if key != "guard"}
        for candidate in sorted(candidates, key=lambda row: (not row["clean"], row["allowed_count"], row["modulus"], row["feature_priority"], row["name"]))[:20]
    ]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p980_source": str(p980_path),
            "p982_source": str(p982_path),
            "script": str(Path(__file__)),
            "source_windows": {window: str(path) for window, path in source_paths.items()},
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p980_source_sha256": sha256_file(p980_path),
            "p982_source_sha256": sha256_file(p982_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "broad_label": BROAD_LABEL,
        "calibration": {
            "candidate_count": len(candidates),
            "calibration_rows": [compact_case(row, guard) for row in rows],
            "clean_candidate_count": sum(1 for candidate in candidates if candidate["clean"]),
            "negative_count": calibration_negative_count,
            "negative_rejected": calibration_negative_rejected,
            "positive_count": calibration_positive_count,
            "positive_preserved": calibration_positive_preserved,
            "promoted_guard": None if guard is None else {"name": guard.name, "rule": guard.rule},
            "top_candidates": top_candidates,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P983_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CALIBRATION-CHOSEN: the promoted residue guard is selected from P980/P982 calibration rows before validation.",
            "PUBLIC-FEATURE-GUARD: only public source-salt and selector features are used for row selection.",
            "MATRIX-PROXY-ONLY: form diversity is compact proxy evidence, not a solved sparse linear algebra instance.",
            "NO-END-TO-END-BREAK: this is not a complete faster-than-rho ECDLP algorithm or target descent.",
        ],
        "method": "p983_p231_rank_quality_residue_guard",
        "parameters": {
            "base_high_gap_rule": BASE_HIGH_GAP_RULE,
            "broad_label": BROAD_LABEL,
            "first_stage_rule": p872.FIRST_STAGE_RULE,
            "promoted_guard": None if guard is None else {"name": guard.name, "rule": guard.rule},
            "second_stage_rule": p872.SECOND_STAGE_RULE,
            "targets": sorted(targets),
            "windows": windows,
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "broad_validation_success": success,
            "calibration_pass": calibration_pass,
            "control_pass": control_pass,
            "first_stage_selected_case_count": sum(first_stage_count_by_window.values()),
            "first_stage_selected_count_by_window": dict(first_stage_count_by_window),
            "guarded_selected_case_count": sum(guarded_count_by_window.values()),
            "guarded_selected_count_by_window": dict(guarded_count_by_window),
            "high_gap_selected_case_count": sum(high_gap_count_by_window.values()),
            "high_gap_selected_count_by_window": dict(high_gap_count_by_window),
            "reconstruction_error_count": reconstruction_error_count,
            "second_stage_selected_case_count": sum(second_stage_count_by_window.values()),
            "second_stage_selected_count_by_window": dict(second_stage_count_by_window),
            "source_case_count": sum(source_case_count_by_window.values()),
            "source_count_by_window": dict(source_case_count_by_window),
            **{f"base_{key}": value for key, value in high_gap_summary.items()},
            **{f"guarded_{key}": value for key, value in guarded_summary.items()},
        },
        "validation_high_gap_cases": high_gap_selected,
        "validation_guarded_cases": guarded_selected,
        "validation_high_gap_cases_compact": [compact_case(case, guard) for case in high_gap_selected],
        "validation_guarded_cases_compact": [compact_case(case, guard) for case in guarded_selected],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P983 contract path")
    parser.add_argument("--p980", default=str(DEFAULT_P980), help="P980 calibration JSON")
    parser.add_argument("--p982", default=str(DEFAULT_P982), help="P982 calibration/control JSON")
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
        "guarded_p867={p867} out={out}".format(
            claim=payload["claim_status"],
            guard=None if guard is None else guard["name"],
            high_gap=summary["high_gap_selected_case_count"],
            guarded=summary["guarded_selected_case_count"],
            broad_groups=summary["guarded_broad_relation_group_count"],
            broad_amortized=summary["guarded_broad_direct_relation_amortized_ops_over_rho"],
            p867=summary["guarded_p867_positive_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
