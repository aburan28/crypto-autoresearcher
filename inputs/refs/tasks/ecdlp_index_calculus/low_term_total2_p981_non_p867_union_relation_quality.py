#!/usr/bin/env python3
"""P981 audit of non-P867 union-verified relation quality."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p981_non_p867_union_relation_quality.md"
DEFAULT_P872 = STATE_DIR / "low_term_total2_p872_p231_two_stage_materialization_probe.json"
DEFAULT_P979 = STATE_DIR / "low_term_total2_p979_p231_frozen_public_gate_validation_probe.json"
DEFAULT_P980 = STATE_DIR / "low_term_total2_p980_p231_high_gap_frozen_refinement_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p981_non_p867_union_relation_quality_probe.json"
SCHEMA = "ecdlp.low_term_total2_p981_non_p867_union_relation_quality.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


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


def relation_group_key(case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        case.get("target"),
        int_value(case.get("transfer_index")),
        case.get("union_derived_secret"),
        json.dumps(case.get("row_leaf_keys") or [], sort_keys=True),
    )


def is_direct_below_rho(case: dict[str, Any]) -> bool:
    return float_value(case.get("direct_ops_over_rho"), 10**9) < 1.0


def is_p867(case: dict[str, Any]) -> bool:
    return bool(case.get("p867_motif_verified_below_rho"))


def is_union(case: dict[str, Any]) -> bool:
    return bool(case.get("union_public_key_verified"))


def is_broad(case: dict[str, Any]) -> bool:
    return is_union(case) and int_value(case.get("union_rank")) >= 3 and is_direct_below_rho(case)


def is_rank4(case: dict[str, Any]) -> bool:
    return is_union(case) and int_value(case.get("union_rank")) >= 4 and is_direct_below_rho(case)


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    public = case.get("public_features") or {}
    return {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "is_broad_union_rank_ge3": is_broad(case),
        "is_p867": is_p867(case),
        "is_rank4_union": is_rank4(case),
        "salt_gap": public.get("salt_gap"),
        "top_k": public.get("top_k"),
        "transfer_index": public.get("transfer_index") or case.get("transfer_index"),
        "union_public_key_verified": is_union(case),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
        "window": public.get("window") or case.get("window"),
    }


def summarize_cases(name: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(float_value(case.get("direct_ops_over_rho")) for case in cases)
    p867 = [case for case in cases if is_p867(case)]
    union = [case for case in cases if is_union(case)]
    broad = [case for case in cases if is_broad(case)]
    rank4 = [case for case in cases if is_rank4(case)]
    non_p867_broad = [case for case in broad if not is_p867(case)]
    p867_groups = {relation_group_key(case) for case in p867}
    broad_groups = {relation_group_key(case) for case in broad}
    rank4_groups = {relation_group_key(case) for case in rank4}
    non_p867_broad_groups = {relation_group_key(case) for case in non_p867_broad}
    rank_hist = Counter(str(case.get("union_rank")) for case in cases)
    broad_rank_hist = Counter(str(case.get("union_rank")) for case in broad)
    return {
        "broad_direct_relation_amortized_ops_over_rho": ratio(total, len(broad_groups)),
        "broad_false_positive_under_p867_count": len(non_p867_broad),
        "broad_false_positive_under_p867_relation_group_count": len(non_p867_broad_groups),
        "broad_precision": ratio(len(broad), len(cases)),
        "broad_rank_histogram": dict(sorted(broad_rank_hist.items())),
        "broad_relation_group_count": len(broad_groups),
        "broad_union_rank_ge3_count": len(broad),
        "direct_sum_ops_over_rho": round8(total),
        "name": name,
        "p867_direct_relation_amortized_ops_over_rho": ratio(total, len(p867_groups)),
        "p867_positive_count": len(p867),
        "p867_precision": ratio(len(p867), len(cases)),
        "p867_relation_group_count": len(p867_groups),
        "rank4_direct_relation_amortized_ops_over_rho": ratio(total, len(rank4_groups)),
        "rank4_relation_group_count": len(rank4_groups),
        "rank4_union_count": len(rank4),
        "rank_histogram": dict(sorted(rank_hist.items())),
        "sample_broad_non_p867_cases": [compact_case(case) for case in non_p867_broad[:8]],
        "selected_all_direct_below_rho": bool(cases and all(is_direct_below_rho(case) for case in cases)),
        "selected_count": len(cases),
        "union_direct_relation_amortized_ops_over_rho": ratio(total, len({relation_group_key(case) for case in union})),
        "union_precision": ratio(len(union), len(cases)),
        "union_relation_group_count": len({relation_group_key(case) for case in union}),
        "union_verified_count": len(union),
    }


def selected_cases(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [case for case in payload.get("selected_cases") or [] if isinstance(case, dict)]


def p980_controls(p980: dict[str, Any]) -> dict[str, Any]:
    summary = p980.get("summary") or {}
    return {
        "p980_claim_is_expected": p980.get("claim_status") == "NEGATIVE_RESULT_P980_HIGH_GAP_MISSES_STILL_LATER_P867_SIGNAL",
        "p980_direct_sum_expected": summary.get("direct_sum_ops_over_rho") == 1.58394161,
        "p980_p867_zero": int_value(summary.get("p867_positive_count")) == 0,
        "p980_rank3_one": int_value((summary.get("rank_histogram") or {}).get("3")) == 1,
        "p980_rank4_one": int_value((summary.get("rank_histogram") or {}).get("4")) == 1,
        "p980_selected_two": int_value(summary.get("selected_count")) == 2,
        "p980_union_two": int_value(summary.get("union_verified_count")) == 2,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p872_path = Path(args.p872)
    p979_path = Path(args.p979)
    p980_path = Path(args.p980)
    p872 = load_json(p872_path)
    p979 = load_json(p979_path)
    p980 = load_json(p980_path)
    p872_summary = summarize_cases("p872_selected_all", selected_cases(p872))
    p979_summary = summarize_cases("p979_exact_gate_selected", selected_cases(p979))
    p980_summary = summarize_cases("p980_high_gap_selected", selected_cases(p980))
    controls = p980_controls(p980)
    success = bool(
        all(controls.values())
        and p980_summary["p867_positive_count"] == 0
        and p980_summary["broad_relation_group_count"] == 2
        and p980_summary["broad_false_positive_under_p867_count"] == 2
        and (p980_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) < 1.0
        and p980_summary["rank4_union_count"] >= 1
    )
    if not all(controls.values()):
        claim = "NEGATIVE_RESULT_P981_CONTROL_FAILURE"
    elif success:
        claim = "P981_NON_P867_UNION_RANK_SIGNAL_IDENTIFIED_IN_P980"
    else:
        claim = "NEGATIVE_RESULT_P981_NO_NON_P867_UNION_RANK_SIGNAL"
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p872_source": str(p872_path),
            "p979_source": str(p979_path),
            "p980_source": str(p980_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p872_source_sha256": sha256_file(p872_path),
            "p979_source_sha256": sha256_file(p979_path),
            "p980_source_sha256": sha256_file(p980_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P981_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "LABEL-AUDIT: P981 changes the useful label for analysis; it does not retroactively make P980 a P867 success.",
            "COMPONENT-SIGNAL: union/rank source rows are relation-source evidence, not sparse linear algebra or target descent.",
            "NO-END-TO-END-BREAK: this is not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p981_non_p867_union_relation_quality",
        "schema": SCHEMA,
        "source_controls": controls,
        "summaries": [p872_summary, p979_summary, p980_summary],
        "summary": {
            "control_pass": all(controls.values()),
            "p872_broad_count": p872_summary["broad_union_rank_ge3_count"],
            "p872_broad_non_p867_count": p872_summary["broad_false_positive_under_p867_count"],
            "p979_broad_count": p979_summary["broad_union_rank_ge3_count"],
            "p979_broad_non_p867_count": p979_summary["broad_false_positive_under_p867_count"],
            "p980_broad_direct_relation_amortized_ops_over_rho": p980_summary[
                "broad_direct_relation_amortized_ops_over_rho"
            ],
            "p980_broad_non_p867_count": p980_summary["broad_false_positive_under_p867_count"],
            "p980_broad_relation_group_count": p980_summary["broad_relation_group_count"],
            "p980_p867_positive_count": p980_summary["p867_positive_count"],
            "p980_rank4_union_count": p980_summary["rank4_union_count"],
            "p980_selected_count": p980_summary["selected_count"],
            "p980_union_verified_count": p980_summary["union_verified_count"],
            "success": success,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P981 contract path")
    parser.add_argument("--p872", default=str(DEFAULT_P872), help="P872 selected-corpus JSON")
    parser.add_argument("--p979", default=str(DEFAULT_P979), help="P979 frozen validation JSON")
    parser.add_argument("--p980", default=str(DEFAULT_P980), help="P980 high-gap validation JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} p980_selected={selected} p980_p867={p867} "
        "p980_broad={broad} p980_broad_amortized={amortized} "
        "p980_rank4={rank4} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["p980_selected_count"],
            p867=summary["p980_p867_positive_count"],
            broad=summary["p980_broad_relation_group_count"],
            amortized=summary["p980_broad_direct_relation_amortized_ops_over_rho"],
            rank4=summary["p980_rank4_union_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
