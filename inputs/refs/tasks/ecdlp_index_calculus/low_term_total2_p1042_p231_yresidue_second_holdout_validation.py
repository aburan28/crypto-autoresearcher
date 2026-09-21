#!/usr/bin/env python3
"""P1042 second holdout for the frozen P1041 y-residue strict route."""

from __future__ import annotations

import argparse
from pathlib import Path

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1038_p231_guarded_structural_family_supply_search as p1038
import low_term_total2_p1041_p231_yresidue_strict_route_validation as p1041


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1042_p231_yresidue_second_holdout_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1042_p231_yresidue_second_holdout_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1042_p231_yresidue_second_holdout_validation.v1"
DEFAULT_START = "12888_12895"
DEFAULT_MAX_WINDOWS = 16


CLAIM_MAP = {
    "NEGATIVE_RESULT_P1041_YRESIDUE_FALSE_PREDICTION": "NEGATIVE_RESULT_P1042_YRESIDUE_FALSE_PREDICTION",
    "P1041_YRESIDUE_STRICT_ROUTE_FORWARD_SUPPLY_SIGNAL": "P1042_YRESIDUE_STRICT_ROUTE_FORWARD_SUPPLY_SIGNAL",
    "NEGATIVE_RESULT_P1041_YRESIDUE_Q_DIVERSE_NO_FACTOR_MATCH": "NEGATIVE_RESULT_P1042_YRESIDUE_Q_DIVERSE_NO_FACTOR_MATCH",
    "NEGATIVE_RESULT_P1041_YRESIDUE_NO_Q_DIVERSE_GROUPS": "NEGATIVE_RESULT_P1042_YRESIDUE_NO_Q_DIVERSE_GROUPS",
    "NEGATIVE_RESULT_P1041_YRESIDUE_NO_FILTERED_SUPPLY": "NEGATIVE_RESULT_P1042_YRESIDUE_NO_FILTERED_SUPPLY",
}


def analyze(args: argparse.Namespace) -> dict:
    payload = p1041.analyze(args)
    claim = CLAIM_MAP.get(payload["claim_status"], payload["claim_status"].replace("P1041", "P1042"))
    payload["schema"] = SCHEMA
    payload["claim_status"] = claim
    payload["claim_taxonomy"] = "OBSERVATION" if claim.startswith("P1042_") else "NEGATIVE RESULT"
    payload["summary"]["claim_status"] = claim
    payload["artifacts"]["script"] = str(Path(__file__))
    payload["artifacts"]["p1041_source"] = str(
        Path("tasks/ecdlp_index_calculus/low_term_total2_p1041_p231_yresidue_strict_route_validation.py")
    )
    payload["artifact_hashes"]["script_sha256"] = p1005.sha256_file(Path(__file__))
    payload["artifact_hashes"]["p1041_source_sha256"] = p1005.sha256_file(
        Path("tasks/ecdlp_index_calculus/low_term_total2_p1041_p231_yresidue_strict_route_validation.py")
    )
    payload["honesty_boundary"] = [
        "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
        "FROZEN-FROM-P1040-P1041: y mod 11 in {2,7} is unchanged for this second holdout.",
        "STRICT-ROUTE: the primary claim only covers p1029_leaf8_scout.",
        "COMPRESSED-PRIMARY: row-signature-compressed primary forward forms drive the claim.",
        "DIAGNOSTIC-POOLS: widened pools are red-team diagnostics and do not promote the strict-route claim.",
        "INDEX-CALCULUS PRECURSOR: this is relation-generation filtering, not sparse linear algebra or target descent.",
        "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
    ]
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Maximum forward windows to scan")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to scan")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    p1038.write_json(Path(args.out), payload)
    bits = []
    for item in payload["summary"]["forward_by_pool"]:
        bits.append(
            "{name}:rows={rows} filt={filtered} c_qdiv={qdiv} c_pred={pred} c_false={false} raw_pred={raw_pred} raw_false={raw_false}".format(
                name=item["name"],
                rows=item["row_count"],
                filtered=item["compressed_filtered_form_count"],
                qdiv=item["compressed_q_diverse_group_count"],
                pred=item["compressed_prediction_count"],
                false=item["compressed_false_count"],
                raw_pred=item["raw_prediction_count"],
                raw_false=item["raw_false_count"],
            )
        )
    print(
        "claim={claim} windows={windows} out={out} {bits}".format(
            claim=payload["claim_status"],
            windows=",".join(payload["parameters"]["forward_windows"]),
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
