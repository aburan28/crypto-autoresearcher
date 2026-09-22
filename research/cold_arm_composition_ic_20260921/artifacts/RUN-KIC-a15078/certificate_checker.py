#!/usr/bin/env python3
"""Independent target-certificate checker for RUN-KIC-56c897."""

from __future__ import annotations

import hashlib
import json
from typing import Any


class CertificateError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition: raise CertificateError(message)


def records(data: bytes) -> list[dict[str, Any]]:
    result = []
    for number, line in enumerate(data.decode().splitlines(), 1):
        if not line.strip(): continue
        value = json.loads(line); require(isinstance(value, dict), f"line {number} not object"); result.append(value)
    return result


def recompute(rows: list[list[int]], rhs: list[int], weights: list[int], *, modulus: int, expected_k: int, returned_d: int) -> dict[str, Any]:
    require(len(rows) == len(rhs) == len(weights), "certificate vector length mismatch")
    require(all(len(row) == expected_k + 1 for row in rows), "certificate row width mismatch")
    combined = [0] * (expected_k + 1); w_rhs = 0
    for weight, row, value in zip(weights, rows, rhs):
        for column, coefficient in enumerate(row): combined[column] = (combined[column] + weight * coefficient) % modulus
        w_rhs = (w_rhs + weight * value) % modulus
    w_a, w_b = combined[:expected_k], combined[expected_k]
    return {"wA": w_a, "wb": w_b, "wa": w_rhs,
            "valid": all(value == 0 for value in w_a) and w_b == 1 and w_rhs == returned_d}


def check(data: bytes, *, expected_scalar: int, modulus: int, expected_k: int) -> dict[str, Any]:
    parsed = records(data)
    relations = sorted([row for row in parsed if row.get("kind") == "relation_rank_receipt"], key=lambda row: row["accepted_relation"])
    summaries = [row for row in parsed if row.get("kind") == "relation_rank_summary"]
    require(len(summaries) == 1, "expected one summary")
    summary = summaries[0]
    require(summary.get("status") == "TARGET_IDENTIFIED", "status is not TARGET_IDENTIFIED")
    require(summary.get("factor_base_log_solution") is None, "factor logs were claimed")
    require(summary.get("linear_solution_verified") is False, "full linear solution was claimed")
    require(summary.get("target_certificate_verified") is True, "target certificate flag absent")
    require(summary.get("final_target_group_verified") is True, "final group verification absent")
    require(summary.get("recovered_fixture_scalar") == expected_scalar, "returned scalar mismatch")
    require(summary.get("target_pivot_at_relation") == len(relations), "target pivot is not terminal prefix row")
    require(summary.get("certificate_prefix_rows") == len(relations), "certificate prefix count mismatch")
    require(summary.get("admitted_relations") == len(relations), "admitted relation count mismatch")
    require(summary.get("rank_A_b") == summary.get("terminal_rank"), "rank_A_b naming mismatch")
    require(summary.get("rank_A_b_a") == summary.get("rank_A_b"), "augmented rank indicates inconsistency")
    require(summary.get("target_inconsistency_at_relation") is None, "inconsistency recorded")
    weights = summary.get("certificate_weights")
    require(isinstance(weights, list) and len(weights) == len(relations), "certificate weight count mismatch")
    coefficient_rows, rhs_values = [], []
    for weight, relation in zip(weights, relations):
        row = relation.get("sparse_row")
        require(isinstance(row, list) and len(row) == expected_k + 1, "relation row width mismatch")
        require(relation.get("verified_group_identity") is True, "relation group identity failed")
        coefficient_rows.append([int(value) for value in row]); rhs_values.append(int(relation["coefficient_a"]))
    independent = recompute(coefficient_rows, rhs_values, [int(value) for value in weights], modulus=modulus, expected_k=expected_k, returned_d=expected_scalar)
    w_a, w_b, w_rhs = independent["wA"], independent["wb"], independent["wa"]
    require(summary.get("matrix_columns") == expected_k + 1, "target variable is not the final matrix column")
    require(independent["valid"], "independent certificate equations failed")
    require(summary.get("certificate_wA") == w_a, "reported wA differs")
    require(summary.get("certificate_wb") == w_b, "reported wb differs")
    require(summary.get("certificate_wa") == w_rhs, "reported wa differs")
    material = {"weights": weights, "wA": w_a, "wb": w_b, "wa": w_rhs,
                "rank_A": summary.get("rank_A"), "rank_A_b": summary.get("rank_A_b"),
                "rank_A_b_a": summary.get("rank_A_b_a")}
    return {"valid": True, "relations": len(relations), "returned_d": w_rhs,
            "rank_A": summary.get("rank_A"), "rank_A_b": summary.get("rank_A_b"),
            "rank_A_b_a": summary.get("rank_A_b_a"), "nonzero_weights": sum(int(w) != 0 for w in weights),
            "independent_sha256": hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}


def self_test() -> None:
    for modulus in (17, 21044858204113):
        rows=[[1,1,0,1],[1,1,0,2]]; rhs=[12%modulus,19%modulus]; weights=[modulus-1,1]
        require(recompute(rows,rhs,weights,modulus=modulus,expected_k=3,returned_d=7)["valid"],"valid certificate rejected")
        mutated=list(weights);mutated[0]=(mutated[0]+1)%modulus
        require(not recompute(rows,rhs,mutated,modulus=modulus,expected_k=3,returned_d=7)["valid"],"mutated weights accepted")
        doubled=[(2*value)%modulus for value in weights]
        bad_wb=recompute(rows,rhs,doubled,modulus=modulus,expected_k=3,returned_d=7)
        require(bad_wb["wb"]==2 and not bad_wb["valid"],"wrong wb normalization accepted")
        require(not recompute(rows,rhs,weights,modulus=modulus,expected_k=3,returned_d=8)["valid"],"d+1 accepted")
    print(json.dumps({"self_test":"PASS","tests":8},sort_keys=True))

if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("--self-test",action="store_true");args=parser.parse_args()
    if args.self_test:self_test()
    else:raise SystemExit("library module")
