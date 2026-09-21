#!/usr/bin/env python3
"""Exhaustive toy audit of special-j rational odd-isogeny closure.

This is a structural certificate, not an ECDLP solver.  It enumerates every
F_p-rational cyclic kernel of the declared odd prime degrees for the frozen
special-j twists, constructs the quotient with the repository's independent
Velu implementation, and records split/ramified/repeated-Frobenius strata.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import platform
import sys
import time
from pathlib import Path

import sympy

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from harness.isogeny_class import (  # noqa: E402
    curve_order,
    j_invariant,
    twists_of_j,
    velu_image,
    velu_odd,
)
from harness.toycurve import EllipticCurve  # noqa: E402

RUN_ID = "RUN-ECDLP-3c1bc0-001"
EXP_ID = "EXP-ECDLP-3c1bc0"
PRIMES = [101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191]
DEGREES = [3, 5, 7, 11, 13]
FAMILIES = {
    "j0": {"j": 0, "D": -3, "rational_modulus": 3},
    "j1728": {"j": 1728, "D": -4, "rational_modulus": 4},
}


def canonical_kernel(E: EllipticCurve, P: tuple[int, int], ell: int) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(E.mul(i, P) for i in range(1, ell)))


def enumerate_kernels(E: EllipticCurve, ell: int) -> list[tuple[tuple[tuple[int, int], ...], tuple[int, int]]]:
    """Enumerate each rational order-ell subgroup exactly once."""
    seen: dict[tuple[tuple[int, int], ...], tuple[int, int]] = {}
    for x in range(E.p):
        P = E.lift_x(x)
        if P is None or E.mul(ell, P) is not None:
            continue
        key = canonical_kernel(E, P, ell)
        seen.setdefault(key, P)
    return [(key, seen[key]) for key in sorted(seen)]


def legendre_symbol(value: int, ell: int) -> int:
    if value % ell == 0:
        return 0
    return 1 if pow(value % ell, (ell - 1) // 2, ell) == 1 else -1


def automorphism_order(p: int, j: int) -> int:
    if j % p == 0 and p % 3 == 1:
        return 6
    if j % p == 1728 % p and p % 4 == 1:
        return 4
    return 2


def sample_map_checks(E: EllipticCurve, target: EllipticCurve, kernel_pts: list[tuple[int, int]]) -> dict:
    samples: list[tuple[int, int]] = []
    for x in range(E.p):
        P = E.lift_x(x)
        if P is None or P in kernel_pts or E.negate(P) in kernel_pts:
            continue
        samples.append(P)
        if len(samples) == 8:
            break
    image_checks = []
    hom_checks = []
    for P in samples:
        image = velu_image(E, kernel_pts, P)
        image_checks.append(image is not None and target.is_on_curve(image))
    for P, Q in zip(samples[:4], samples[4:8]):
        lhs = velu_image(E, kernel_pts, E.add(P, Q))
        iP = velu_image(E, kernel_pts, P)
        iQ = velu_image(E, kernel_pts, Q)
        rhs = target.add(iP, iQ) if iP is not None and iQ is not None else None
        hom_checks.append(lhs == rhs)
    return {
        "sample_count": len(samples),
        "image_on_target_rate": sum(image_checks) / len(image_checks) if image_checks else 1.0,
        "homomorphism_check_rate": sum(hom_checks) / len(hom_checks) if hom_checks else 1.0,
        "all_images_on_target": all(image_checks),
        "all_homomorphism_checks": all(hom_checks),
    }


def audit_cell(family: str, p: int, a: int, b: int, ell: int, kernel: tuple[tuple[int, int], ...], generator: tuple[int, int]) -> dict:
    cfg = FAMILIES[family]
    E = EllipticCurve(p, a, b)
    source_order = curve_order(p, a, b)
    trace = p + 1 - source_order
    target_a, target_b, _ = velu_odd(E, generator, ell)
    target = EllipticCurve(p, target_a, target_b)
    target_order = curve_order(p, target_a, target_b)
    source_j = j_invariant(p, a, b)
    target_j = j_invariant(p, target_a, target_b)
    cm_D = int(cfg["D"])
    split = 0 if ell == abs(cm_D) else legendre_symbol(cm_D, ell)
    frobenius_discriminant = (trace * trace - 4 * p) % ell
    rational_cm = p % int(cfg["rational_modulus"]) == 1
    ramified = ell == abs(cm_D)
    repeated_frobenius = frobenius_discriminant == 0
    nonexceptional_rational = rational_cm and not ramified and not repeated_frobenius
    expected_preserve = nonexceptional_rational
    # velu_odd/velu_image use one representative from each +/- kernel pair;
    # `kernel` above deliberately retains the full subgroup for completeness.
    kernel_representatives = [E.mul(i, generator) for i in range(1, (ell + 1) // 2)]
    map_checks = sample_map_checks(E, target, kernel_representatives)
    valid = (
        E.mul(ell, generator) is None
        and len(kernel) == ell - 1
        and target_order == source_order
        and map_checks["all_images_on_target"]
        and map_checks["all_homomorphism_checks"]
    )
    same_special_j = target_j % p == source_j % p
    return {
        "family": family,
        "p": p,
        "source_a": a,
        "source_b": b,
        "source_j": source_j,
        "target_a": target_a,
        "target_b": target_b,
        "target_j": target_j,
        "source_order": source_order,
        "target_order": target_order,
        "trace": trace,
        "ell": ell,
        "kernel_generator": list(generator),
        "kernel_point_count": len(kernel),
        "cm_discriminant": cm_D,
        "cm_split_symbol": split,
        "rational_cm_available": rational_cm,
        "ramified_cm_degree": ramified,
        "frobenius_discriminant_mod_ell": frobenius_discriminant,
        "repeated_frobenius": repeated_frobenius,
        "nonexceptional_rational": nonexceptional_rational,
        "expected_special_j_preserved": expected_preserve,
        "same_special_j": same_special_j,
        "source_automorphism_order": automorphism_order(p, source_j),
        "target_automorphism_order": automorphism_order(p, target_j),
        "automorphism_order_match": automorphism_order(p, source_j) == automorphism_order(p, target_j),
        "map_checks": map_checks,
        "validity": valid,
    }


def main() -> int:
    started = time.time()
    results = []
    for family, cfg in FAMILIES.items():
        for p in PRIMES:
            for a, b in twists_of_j(p, int(cfg["j"])):
                E = EllipticCurve(p, a, b)
                for ell in DEGREES:
                    if ell == p or curve_order(p, a, b) % ell:
                        continue
                    for kernel, generator in enumerate_kernels(E, ell):
                        results.append(audit_cell(family, p, a, b, ell, kernel, generator))
    valid = [r for r in results if r["validity"]]
    eligible = [r for r in valid if r["nonexceptional_rational"]]
    invalid = [r for r in results if not r["validity"]]
    raw = {
        "run_id": RUN_ID,
        "experiment_id": EXP_ID,
        "specification_sha256": hashlib.sha256((REPO / "experiments" / EXP_ID / "specification.yaml").read_bytes()).hexdigest(),
        "prime_list": PRIMES,
        "degrees": DEGREES,
        "result_count": len(results),
        "valid_count": len(valid),
        "invalid_count": len(invalid),
        "results": results,
        "summary": {
            "valid_map_certificate_rate": len(valid) / len(results) if results else 1.0,
            "split_nonexceptional_cell_count": len(eligible),
            "split_nonexceptional_special_j_preservation_rate": (
                sum(r["same_special_j"] for r in eligible) / len(eligible) if eligible else 1.0
            ),
            "split_nonexceptional_target_automorphism_match_rate": (
                sum(r["automorphism_order_match"] for r in eligible) / len(eligible) if eligible else 1.0
            ),
            "nonexceptional_inert_cell_count": sum(
                r["cm_split_symbol"] == -1 for r in eligible
            ),
            "exceptional_cell_count": sum(
                r["rational_cm_available"] and not r["nonexceptional_rational"] for r in valid
            ),
            "nonrational_control_cell_count": sum(
                not r["rational_cm_available"] for r in valid
            ),
            "all_valid_cells_passed": bool(valid) and not invalid,
            "success_criterion_met": bool(valid) and not invalid and all(
                r["same_special_j"] and r["automorphism_order_match"] for r in eligible
            ),
            "falsification_criterion_met": any(
                r["nonexceptional_rational"] and r["validity"]
                and (not r["same_special_j"] or not r["automorphism_order_match"])
                for r in results
            ),
        },
        "wall_clock_seconds": round(time.time() - started, 6),
    }
    output = Path(os.environ.get("ECDLP_CLOSURE_OUT", "raw-result.json"))
    output.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    print(json.dumps(raw["summary"], sort_keys=True))
    return 0 if raw["summary"]["success_criterion_met"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
