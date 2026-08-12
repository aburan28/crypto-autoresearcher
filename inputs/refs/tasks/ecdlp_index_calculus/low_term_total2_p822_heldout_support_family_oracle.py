#!/usr/bin/env python3
"""P822 held-out support-family oracle audit for ECDLP continuation gates."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P819_SCRIPT = TASK_DIR / "low_term_total2_p819_support_family_oracle_bound.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p822_heldout_support_family_oracle_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p822_heldout_support_family_oracle.md"
SCHEMA = "ecdlp.low_term_total2_p822_heldout_support_family_oracle.v1"


def load_p819() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p819_for_p822", P819_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P819 helpers from {P819_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def p822_claim(p819_claim: str) -> str:
    if p819_claim == "P819_SUPPORT_FAMILY_ORACLE_GATE_BELOW_RHO":
        return "P822_HELDOUT_SUPPORT_FAMILY_ORACLE_BELOW_RHO"
    if p819_claim == "P819_SUPPORT_FAMILY_ORACLE_IMPROVES_EQUAL_BUDGET_FULL_POOL":
        return "P822_HELDOUT_SUPPORT_FAMILY_ORACLE_IMPROVES_EQUAL_BUDGET_FULL_POOL"
    return "NEGATIVE_RESULT_P822_HELDOUT_SUPPORT_FAMILY_ORACLE_FAILS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p819 = load_p819()
    payload = p819.analyze(args)
    payload["artifacts"] = {
        **payload["artifacts"],
        "contract": str(DEFAULT_CONTRACT),
        "p819_script": str(P819_SCRIPT),
        "script": str(Path(__file__)),
    }
    payload["claim_status"] = p822_claim(str(payload["claim_status"]))
    payload["honesty_boundary"] = [
        "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
        "HELD-OUT CONSTRUCTORS: oracle choices are evaluated on fresh constructor namespaces used by P821.",
        "ORACLE BOUND: per-context support family and budget are chosen with recovered-label knowledge and are not a public algorithm.",
        "BUDGET-PRESERVING: each oracle policy preserves the same total continuation trial budget as the matching equal-budget control.",
        "SCAN-CHARGED: reported costs include prefix and continuation online scan cost plus target-once calibration and all-pair prefix setup.",
        "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
    ]
    payload["method"] = "p822_heldout_support_family_oracle"
    payload["schema"] = SCHEMA
    payload["summary"]["heldout_constructor_namespaces"] = payload["summary"]["constructor_namespaces"]
    payload["summary"]["oracle_source"] = "P819 support-family oracle machinery on P821 held-out constructors"
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p819 = load_p819()
    p815 = p819.load_p818().load_module("ecdlp_p815_summary_for_p822", p819.load_p818().P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_summary_for_p822", p815.P812_SCRIPT)
    summary = payload["summary"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **summary,
            "policy_results": [p815.compact_policy_result(p812, item) for item in summary["policy_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument(
        "--constructor-namespaces",
        default="posthit-p821-heldout-v29,posthit-p821-heldout-v30,posthit-p821-heldout-v31",
    )
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--prefix-seed-counts", default="8,16,32")
    parser.add_argument("--prefix-trial-budget", type=int, default=256)
    parser.add_argument("--average-continuation-budgets", default="16,32,64")
    parser.add_argument("--oracle-modes", default="core,score,seen,hash,public_supports,all_supports")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--top-span-bins", type=int, default=2)
    parser.add_argument("--top-endpoint-bins", type=int, default=4)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p819 = load_p819()
    p818 = p819.load_p818()
    payload = analyze(args)
    p818.write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    p818.write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        p819.json.dumps(
            {
                "best_equal_adaptive_gate": summary["summary"]["best_equal_adaptive_gate"],
                "best_hash_control": summary["summary"]["best_hash_control"],
                "best_oracle_gate": summary["summary"]["best_oracle_gate"],
                "claim_status": summary["claim_status"],
                "full_pool": summary["summary"]["full_pool"],
                "heldout_constructor_namespaces": summary["summary"]["heldout_constructor_namespaces"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
