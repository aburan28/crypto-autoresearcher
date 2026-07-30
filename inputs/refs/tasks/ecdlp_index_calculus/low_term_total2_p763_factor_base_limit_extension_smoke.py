#!/usr/bin/env python3
"""P763 smoke test for real factor-base limit propagation above 48."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P762_SCRIPT = TASK_DIR / "low_term_total2_p762_factor_base_capacity_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P762_SUMMARY = STATE_DIR / "low_term_total2_p762_factor_base_capacity_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p763_factor_base_limit_extension_smoke.md"
SCHEMA = "ecdlp.low_term_total2_p763_factor_base_limit_extension_smoke.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def case_exports_wide(item: dict[str, Any]) -> bool:
    actual = item.get("actual_factor_base_size") or {}
    return bool(
        int(actual.get("max") or 0) > 48
        and int(item.get("max_exported_factor_count") or 0) > 48
    )


def case_has_tail_support(item: dict[str, Any]) -> bool:
    return int(item.get("max_active_columns_ge_48") or 0) > 0


def case_rank_expands(item: dict[str, Any]) -> bool:
    return int(item.get("max_sparse_rank") or 0) > 48


def classify_case(item: dict[str, Any]) -> str:
    if case_exports_wide(item) and case_has_tail_support(item) and case_rank_expands(item):
        return "rank_expansion_signal"
    if case_exports_wide(item) and case_has_tail_support(item):
        return "wide_support_signal"
    if case_exports_wide(item):
        return "wide_export_no_tail_support"
    return "capacity_bound_at_48"


def class_counts(case_summaries: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in case_summaries:
        key = str(item["p763_class"])
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def determine_claim(case_summaries: list[dict[str, Any]]) -> str:
    total = len(case_summaries)
    wide_support = sum(1 for item in case_summaries if item["p763_class"] in {"wide_support_signal", "rank_expansion_signal"})
    rank_expansion = sum(1 for item in case_summaries if item["p763_class"] == "rank_expansion_signal")
    if total and rank_expansion == total:
        return "P763_FACTOR_BASE_LIMIT_ALL_RANK_EXPANSION_SIGNAL"
    if total and wide_support == total:
        return "P763_FACTOR_BASE_LIMIT_ALL_WIDE_SUPPORT_SIGNAL"
    if rank_expansion:
        return "P763_FACTOR_BASE_LIMIT_RANK_EXPANSION_SIGNAL"
    if wide_support >= 4:
        return "P763_FACTOR_BASE_LIMIT_WIDE_SUPPORT_SIGNAL"
    if wide_support:
        return "P763_FACTOR_BASE_LIMIT_PARTIAL_WIDE_SUPPORT_SIGNAL"
    return "NEGATIVE_RESULT_P763_FACTOR_BASE_LIMIT_EXTENSION_SMOKE"


def p762_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") or {}
    return {
        "capacity_bound_wide_case_count": summary.get("capacity_bound_wide_case_count"),
        "claim_status": payload.get("claim_status"),
        "max_exported_factor_count": summary.get("max_exported_factor_count"),
        "max_sparse_rank": summary.get("max_sparse_rank"),
        "rank_expansion_case_count": summary.get("rank_expansion_case_count"),
        "wide_case_count": summary.get("wide_case_count"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p762 = load_module("ecdlp_p762_factor_base_capacity_audit", P762_SCRIPT)
    p762_args = argparse.Namespace(
        cases=args.cases,
        max_relations=args.max_relations,
        max_subsets=args.max_subsets,
        p761_summary=args.p762_summary,
        pool_count=args.pool_count,
        public_substitution_ops_per_selected=args.public_substitution_ops_per_selected,
        row_policy=args.row_policy,
        seed_count=args.seed_count,
        selected_counts=args.selected_counts,
        sparse_policies=args.sparse_policies,
        walk_mode=args.walk_mode,
        width=args.width,
    )
    p762_payload = p762.analyze(p762_args)
    case_summaries = p762_payload["summary"]["case_summaries"]
    for item in case_summaries:
        item["p763_class"] = classify_case(item)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p762_summary": str(args.p762_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries),
        "code_changes_under_test": [
            "relation_probe.make_challenge accepts factor_base_limit and passes verifier.build_factor_base(..., limit=factor_base_limit).",
            "P746/P747/P748 counted scan paths pass requested factor_base_size to relation_probe.make_challenge.",
            "environment/main.py challenge helpers accept a default-preserving optional factor_base_limit.",
        ],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CAPACITY-SMOKE: this tests exported width and active support, not a full below-rho index-calculus algorithm.",
            "PUBLIC-DIAGNOSTIC: no expected secrets are used in width, support, or rank measurements.",
            "RANK-EXPANSION-SEPARATED: wide exported support is weaker than rank above 48.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p763_factor_base_limit_extension_smoke",
        "p762_control": p762_control(args.p762_summary),
        "parameters": {
            "cases": p762.parse_cases(args.cases),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pool_count": args.pool_count,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "seed_count": args.seed_count,
            "selected_counts": p762.csv_ints(args.selected_counts),
            "sparse_policies": p762.csv_strings(args.sparse_policies),
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": {
            "case_count": len(case_summaries),
            "case_summaries": case_summaries,
            "class_counts": class_counts(case_summaries),
            "max_active_columns_ge_48": max((int(item["max_active_columns_ge_48"]) for item in case_summaries), default=0),
            "max_exported_factor_count": max((int(item["max_exported_factor_count"]) for item in case_summaries), default=0),
            "max_sparse_rank": max((int(item["max_sparse_rank"]) for item in case_summaries), default=0),
            "rank_expansion_case_count": sum(1 for item in case_summaries if case_rank_expands(item)),
            "wide_export_case_count": sum(1 for item in case_summaries if case_exports_wide(item)),
            "wide_support_case_count": sum(1 for item in case_summaries if case_exports_wide(item) and case_has_tail_support(item)),
        },
    }


def slim_case(p762: Any, item: dict[str, Any]) -> dict[str, Any]:
    base = p762.slim_case(item)
    base["p763_class"] = item["p763_class"]
    return base


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p762 = load_module("ecdlp_p762_factor_base_capacity_audit_for_summary", P762_SCRIPT)
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "code_changes_under_test": payload["code_changes_under_test"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p762_control": payload["p762_control"],
        "parameters": payload["parameters"],
        "summary": {
            "case_count": payload["summary"]["case_count"],
            "case_summaries": [slim_case(p762, item) for item in payload["summary"]["case_summaries"]],
            "class_counts": payload["summary"]["class_counts"],
            "max_active_columns_ge_48": payload["summary"]["max_active_columns_ge_48"],
            "max_exported_factor_count": payload["summary"]["max_exported_factor_count"],
            "max_sparse_rank": payload["summary"]["max_sparse_rank"],
            "rank_expansion_case_count": payload["summary"]["rank_expansion_case_count"],
            "wide_export_case_count": payload["summary"]["wide_export_case_count"],
            "wide_support_case_count": payload["summary"]["wide_support_case_count"],
        },
    }


def default_cases() -> str:
    targets = [
        ("67.a1@9803", 66, "67"),
        ("21175.bc1@8089", 58, "21175"),
        ("23232.cr1@9643", 64, "23232b"),
    ]
    entries = []
    for requested in (64, 80):
        for target, budget, tag in targets:
            entries.append(
                f"fb{requested}_{tag}|{target}|{budget}|{requested}|ecdlp-p763-fb{requested}-{tag}-v1|fb{requested}"
            )
    return ",".join(entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=default_cases())
    parser.add_argument("--p762-summary", type=Path, default=DEFAULT_P762_SUMMARY)
    parser.add_argument("--seed-count", type=int, default=96)
    parser.add_argument("--selected-counts", default="32,64")
    parser.add_argument("--pool-count", type=int, default=96)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,pivot_high")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
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
                "claim_status": summary["claim_status"],
                "class_counts": summary["summary"]["class_counts"],
                "max_active_columns_ge_48": summary["summary"]["max_active_columns_ge_48"],
                "max_exported_factor_count": summary["summary"]["max_exported_factor_count"],
                "max_sparse_rank": summary["summary"]["max_sparse_rank"],
                "rank_expansion_case_count": summary["summary"]["rank_expansion_case_count"],
                "wide_export_case_count": summary["summary"]["wide_export_case_count"],
                "wide_support_case_count": summary["summary"]["wide_support_case_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
