#!/usr/bin/env sage-python
"""Test the P1511 P1510-style product-circuit semijoin boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

from sage.all import GF, PolynomialRing


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
CRYPTO = Path("/Volumes/Volume/crypto-autoresearcher")
CONTRACT = STATE / "experiment_contract_p1511_sparse_batch_relation_incidence.md"
DERIVATION = CRYPTO / "ideas/artifacts/ECDLP-IDEA-117/p1511_factorized_semijoin_derivation.md"
OUT = STATE / "p1511_factorized_semijoin_gate.json"
NOTE = RESEARCH / "p1511_factorized_semijoin_gate.md"

EXPECTED = {
    CONTRACT: "e500bb779cf21b78cf43ef1af720510786cd476fce62eb2fc9b67b7b179bc863",
    DERIVATION: "7ed54eaddc1adfba97422a6bb41e8ee5b590ff29537d90ef163ac3a4b94c8b55",
    ROOT / "tasks/ecdlp_index_calculus/p1510_global_truncated_marked_resultant_compiler.py":
        "dc96f1a76c831d4dba4e80b7dbc1ae2672d5b7b84f6ec0bb40b7c94f8f0417ed",
    STATE / "p1510_global_truncated_marked_resultant_compiler.json":
        "55435eda07e37e1b30f882f20480c3bc612e83094640a0203ab5c6096cb0f589",
    STATE / "p1510_global_truncated_marked_resultant_compiler_audit.json":
        "25268ebd0c65ea83672088b93b4490fd47236876fd31037dbe76f753f1a455b6",
    STATE / "p1493_pair_support_resultant_reporter.json":
        "cdfe2470ec5a9f231688b1d61d4bba5fb11dcb587982f892b21eee36b0e5ecf7",
    STATE / "p1493_pair_support_resultant_reporter_audit.json":
        "ab75dff4153657b55a12fd371fe56e0b029f984319d1a185c5a118274a179e49",
    STATE / "p1511_fd_width_gate.json":
        "70be73f8c598eee05cac4e82aaab6b0a0b263e08a209e6f3199e157fe86e5684",
    STATE / "p1511_fd_width_gate_audit.json":
        "e5a71121acb0942a18f69133d8a58d6164ef5d08d24fe3d772250264606ffcfc",
    CRYPTO / "focus/archive/focus_queue_p1511_semijoin_active.json":
        "e554391a4122e77034c500891258300828d513051777e58772caadf1b0df3d8a",
    CRYPTO / "focus/archive/focus_plan_p1511_semijoin_active.json":
        "a4b56782b5acc600561bc26300b2de2ae7a93866f387ac7e9727e65bdfb56a13",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def parse_sizes(value: str) -> list[int]:
    sizes = [int(part) for part in value.split(",") if part.strip()]
    if not sizes or any(size < 2 for size in sizes):
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers >=2")
    return sizes


def poly_slots(polynomial: Any) -> int:
    return int(polynomial.degree()) + 1 if polynomial else 1


def balanced_product(factors: list[Any]) -> tuple[Any, dict[str, int]]:
    if not factors:
        raise ValueError("empty product tree")
    current = list(factors)
    multiplication_count = 0
    schoolbook_upper = 0
    coefficient_input_traffic = 0
    peak_live_slots = sum(poly_slots(value) for value in current)
    while len(current) > 1:
        next_level = []
        current_slots = sum(poly_slots(value) for value in current)
        next_slots = 0
        for index in range(0, len(current), 2):
            if index + 1 == len(current):
                product = current[index]
            else:
                left = current[index]
                right = current[index + 1]
                left_slots = poly_slots(left)
                right_slots = poly_slots(right)
                coefficient_input_traffic += left_slots + right_slots
                schoolbook_upper += left_slots * right_slots
                multiplication_count += 1
                product = left * right
            next_level.append(product)
            next_slots += poly_slots(product)
            peak_live_slots = max(peak_live_slots, current_slots + next_slots)
        current = next_level
    return current[0], {
        "multiplication_count": multiplication_count,
        "schoolbook_upper": schoolbook_upper,
        "coefficient_input_traffic": coefficient_input_traffic,
        "peak_live_coefficient_slots": peak_live_slots,
    }


def source_tuple(position: int, r: int, side: str) -> tuple[int, int, int]:
    surface, offset = divmod(position, r * r)
    first, second = divmod(offset, r)
    if side not in {"target", "a3"}:
        raise ValueError(side)
    return surface, first, second


def make_roots(r: int, modulus: int) -> tuple[list[int], list[int]]:
    total = r**3
    cursor = r + 1
    left = []
    for position in range(total):
        surface, first, second = source_tuple(position, r, "target")
        if first == 0 and second == 0:
            left.append(surface + 1)
        else:
            left.append(cursor)
            cursor += 1
    right = []
    for position in range(total):
        surface, first, second = source_tuple(position, r, "a3")
        if first == 0 and second == 0:
            right.append(surface + 1)
        else:
            right.append(cursor)
            cursor += 1
    if cursor > modulus:
        raise RuntimeError(f"r={r} needs {cursor - 1} distinct field labels in F_{modulus}")
    return left, right


def synthetic_cell(r: int) -> dict[str, Any]:
    modulus = 65537
    field = GF(modulus)
    ring = PolynomialRing(field, f"W1511_semijoin_{r}")
    W = ring.gen()
    left_roots, right_roots = make_roots(r, modulus)
    left_factors = [W - field(root) for root in left_roots]
    right_factors = [W - field(root) for root in right_roots]
    left_product, left_tree = balanced_product(left_factors)
    right_product, right_tree = balanced_product(right_factors)
    common = left_product.gcd(right_product).monic()
    expected = ring.one()
    for root in range(1, r + 1):
        expected *= W - field(root)
    expected = expected.monic()
    recovered_roots = sorted(int(root) for root in common.roots(multiplicities=False))

    left_backpointers: dict[int, list[tuple[int, int, int]]] = {}
    right_backpointers: dict[int, list[tuple[int, int, int]]] = {}
    for position, root in enumerate(left_roots):
        left_backpointers.setdefault(root, []).append(source_tuple(position, r, "target"))
    for position, root in enumerate(right_roots):
        right_backpointers.setdefault(root, []).append(source_tuple(position, r, "a3"))
    source_rows = []
    for root in recovered_roots:
        for target, first, second in left_backpointers[root]:
            for start, third, fourth in right_backpointers[root]:
                source_rows.append({
                    "root": root,
                    "target_index": target,
                    "factor_indices": [first, second, start, third, fourth],
                })
    expected_rows = [
        {
            "root": index + 1,
            "target_index": index,
            "factor_indices": [0, 0, index, 0, 0],
        }
        for index in range(r)
    ]

    left_nonzero = sum(coefficient != 0 for coefficient in left_product)
    right_nonzero = sum(coefficient != 0 for coefficient in right_product)
    leaf_count = r**3
    rho_proxy = r ** 2.5
    return {
        "r": r,
        "field_modulus": modulus,
        "target_surface_count": r,
        "leaves_per_surface": r * r,
        "left_leaf_count": leaf_count,
        "right_leaf_count": leaf_count,
        "total_leaf_count": 2 * leaf_count,
        "left_product_degree": int(left_product.degree()),
        "right_product_degree": int(right_product.degree()),
        "left_nonzero_coefficient_count": left_nonzero,
        "right_nonzero_coefficient_count": right_nonzero,
        "left_coefficient_density": left_nonzero / poly_slots(left_product),
        "right_coefficient_density": right_nonzero / poly_slots(right_product),
        "common_factor_degree": int(common.degree()),
        "common_factor_coefficients": [int(value) for value in common],
        "common_factor_sha256": hashlib.sha256(
            b"|".join(str(int(value)).encode("ascii") for value in common)
        ).hexdigest(),
        "expected_common_factor_matches": common == expected,
        "recovered_common_roots": recovered_roots,
        "source_rows": source_rows,
        "expected_source_rows_match": source_rows == expected_rows,
        "source_row_count": len(source_rows),
        "left_product_tree": left_tree,
        "right_product_tree": right_tree,
        "leaf_count_over_rho_r2p5": leaf_count / rho_proxy,
        "expected_leaf_count_over_rho_sqrt_r": math.sqrt(r),
        "thin_r2_control_over_rho": (r * r) / rho_proxy,
        "batch_marker_order_lower_bound": int(common.degree()),
    }


def render_note(payload: dict[str, Any]) -> str:
    lines = [
        "# P1511 Factorized Semijoin Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "The exact P1510 product grammar uses `r^2` bounded-degree pair-resultant",
        "leaves per target. A batch of `Theta(r)` targets and the partitioned A3",
        "side therefore each require `r^3` provenance-bearing leaves before gcd.",
        "",
        "| r | leaves/side | product degree | gcd degree | leaves/rho | thin/rho |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["synthetic_cells"]:
        lines.append(
            f"| {row['r']} | {row['left_leaf_count']} | {row['left_product_degree']} | "
            f"{row['common_factor_degree']} | {row['leaf_count_over_rho_r2p5']:.6f} | "
            f"{row['thin_r2_control_over_rho']:.6f} |"
        )
    lines += [
        "",
        "Every planted common factor and six-position provenance row is recovered",
        "exactly. The gcd output is only linear in r, but the favorable linear-leaf",
        "input circuit is already cubic. Its leaf-count/rho ratio is `sqrt(r)`,",
        "while the thin `r^2` control remains below rho.",
        "",
        "This closes P1510-per-target products, dense batch gcd, product/remainder",
        "trees, and the same leaves in a quotient module. It does not rule out a new",
        "target-uniform representation constructed before P1510 leaf emission.",
        "Relation collection, blind descent, and a generic rho/Shoup improvement",
        "remain unattempted.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=parse_sizes, default=parse_sizes("4,6,8,12,16,24,32"))
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--note", type=Path, default=NOTE)
    args = parser.parse_args()

    frozen_hashes = {str(path): sha256(path) for path in EXPECTED}
    if any(frozen_hashes[str(path)] != expected for path, expected in EXPECTED.items()):
        failures = [
            str(path) for path, expected in EXPECTED.items()
            if frozen_hashes[str(path)] != expected
        ]
        raise RuntimeError(f"P1511 frozen input hash mismatch: {failures}")

    p1510 = load(STATE / "p1510_global_truncated_marked_resultant_compiler.json")
    p1510_audit = load(STATE / "p1510_global_truncated_marked_resultant_compiler_audit.json")
    p1493 = load(STATE / "p1493_pair_support_resultant_reporter.json")
    p1493_audit = load(STATE / "p1493_pair_support_resultant_reporter_audit.json")
    synthetic_cells = [synthetic_cell(r) for r in args.sizes]

    p1510_cells = p1510["construction"]["synthetic_cells"]
    p1510_leaf_formula = all(
        int(row["arithmetic"]["quadratic_resultant_count"]) == int(row["r"]) ** 2
        for row in p1510_cells
    )
    checks = {
        "all_frozen_hashes_exact": True,
        "p1510_exactly_r2_pair_resultant_leaves_per_target": p1510_leaf_formula,
        "p1510_prior_audit_passes_12_of_12": (
            p1510_audit["status"] == "PASS_P1510_GLOBAL_TRUNCATED_MARKED_RESULTANT_COMPILER_AUDIT"
            and p1510_audit["check_pass_count"] == 12
        ),
        "p1493_exact_pair_support_and_batch_boundary_preserved": (
            p1493["status"].startswith("MIXED_RESULT_P1493")
            and p1493_audit["status"].startswith("PASS")
        ),
        "all_synthetic_products_have_r3_degree_and_leaves": all(
            row["left_leaf_count"] == row["r"] ** 3
            and row["right_leaf_count"] == row["r"] ** 3
            and row["left_product_degree"] == row["r"] ** 3
            and row["right_product_degree"] == row["r"] ** 3
            for row in synthetic_cells
        ),
        "all_linear_common_factor_outputs_exact": all(
            row["expected_common_factor_matches"]
            and row["common_factor_degree"] == row["r"]
            for row in synthetic_cells
        ),
        "all_source_backpointers_recover_exact_five_factor_rows": all(
            row["expected_source_rows_match"] and row["source_row_count"] == row["r"]
            for row in synthetic_cells
        ),
        "all_product_trees_charge_every_leaf": all(
            row["left_product_tree"]["multiplication_count"] == row["left_leaf_count"] - 1
            and row["right_product_tree"]["multiplication_count"] == row["right_leaf_count"] - 1
            for row in synthetic_cells
        ),
        "cubic_leaf_count_exceeds_rho_by_sqrt_r": all(
            abs(row["leaf_count_over_rho_r2p5"] - row["expected_leaf_count_over_rho_sqrt_r"])
            < 1e-12
            and row["leaf_count_over_rho_r2p5"] > 1.0
            for row in synthetic_cells
        ),
        "thin_r2_control_remains_below_rho": all(
            row["thin_r2_control_over_rho"] < 1.0 for row in synthetic_cells
        ),
    }
    if not all(checks.values()):
        failures = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"P1511 semijoin gate failures: {failures}")

    payload = {
        "schema": "autolab.ecdlp.p1511_factorized_semijoin_gate.v1",
        "status": "NEGATIVE_P1511_P1510_STYLE_PRODUCT_CIRCUIT_INPUT_CUBIC",
        "source": str(Path(__file__).resolve()),
        "source_sha256": sha256(Path(__file__).resolve()),
        "contract": str(CONTRACT),
        "contract_sha256": sha256(CONTRACT),
        "derivation": str(DERIVATION),
        "derivation_sha256": sha256(DERIVATION),
        "frozen_hashes": frozen_hashes,
        "synthetic_cells": synthetic_cells,
        "checks": checks,
        "check_count": len(checks),
        "check_pass_count": sum(checks.values()),
        "claim_status": {
            "p1510_single_target_global_compiler": "reproduced",
            "p1511_p1510_style_factorized_semijoin": "not_reproduced",
            "target_uniform_pre_leaf_representation": "open",
            "relation_collection": "not_attempted",
            "blind_descent": "not_attempted",
            "generic_shoup_breakthrough": "not_attempted",
        },
        "interpretation": (
            "The favorable planted control recovers a linear common-factor and source-row "
            "output exactly, but each side of the declared P1510 product-circuit semijoin "
            "already contains r^3 constant-size provenance leaves. Dense gcd, product/remainder "
            "trees, and quotient-module repackagings cannot lower an input-generation exponent "
            "that already exceeds rho. This is a scoped product-grammar negative, not a lower "
            "bound against a new target-uniform representation built before leaf emission."
        ),
        "next_action": (
            "Close P1511 and preregister a representation-changing source-biconditional "
            "linear-complex gate that is constructed before P1510 leaf emission."
        ),
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    write_atomic(args.out, encoded)
    write_atomic(args.note, render_note(payload).encode("utf-8"))
    print(
        f"status={payload['status']} checks={payload['check_pass_count']}/{payload['check_count']} "
        f"sizes={','.join(str(value) for value in args.sizes)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
