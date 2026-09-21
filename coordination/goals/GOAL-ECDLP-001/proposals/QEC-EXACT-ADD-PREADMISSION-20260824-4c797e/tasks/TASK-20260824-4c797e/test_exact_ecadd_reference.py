#!/usr/bin/env python3
"""Single deterministic control suite pre-registered for TASK-20260824-4c797e."""
from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

from exact_ecadd_reference import (
    OMEGA,
    Scratch,
    TINY_CURVE,
    TINY_TABLE,
    candidate_translate,
    complete_add,
    selected_addend,
    subgroup,
    total_idiv,
    total_imul,
)

TEST_PLAN = {
    "protocol_version": 2,
    "amendment": "CORR-20260824-91d34a",
    "seeds": [],
    "tiny_curve": {"p": 13, "b": 7, "subgroup_order": 7, "generator": [7, 5]},
    "addresses": [0, 1],
    "magnitudes": [1, 3],
    "signs": [0, 1],
    "enables": [0, 1],
    "controls": [
        "total interfaces compose in both orders for every F_p pair",
        "disabled candidate is identity for every F_p pair/address/sign",
        "enabled candidate matches an independent complete group law for every subgroup accumulator/address/sign",
        "all scratch, flags, qROM targets and effective-enable state clean",
        "each address/sign/enable cleaned basis map is a permutation",
        "all four exceptional classes are exercised",
        "omit-totalization control fails at X-a=0",
        "premature-cleanup control disagrees on an exceptional input",
    ],
}


def main() -> dict:
    started = time.time()
    curve = TINY_CURVE
    points = subgroup(curve)
    assert len(set(points)) == curve.order
    assert all(curve.on_curve(p) for p in points)
    assert all(p is None or p != OMEGA for p in points)

    counts = {
        "total_interface_pairs": 0,
        "disabled_field_pairs": 0,
        "enabled_subgroup_cases": 0,
        "basis_permutation_blocks": 0,
        "cleanup_checks": 0,
        "exception_branch_hits": {k: 0 for k in ("fO", "fA", "fNA", "fN2A")},
    }

    for x in range(curve.p):
        for y in range(curve.p):
            s = Scratch()
            x1, y1 = total_idiv(x, y, curve.p, s)
            x2, y2 = total_imul(x1, y1, curve.p, s)
            assert (x2, y2) == (x, y) and s.clean()
            s = Scratch()
            x1, y1 = total_imul(x, y, curve.p, s)
            x2, y2 = total_idiv(x1, y1, curve.p, s)
            assert (x2, y2) == (x, y) and s.clean()
            counts["total_interface_pairs"] += 1
            for address in TEST_PLAN["addresses"]:
                for sign in TEST_PLAN["signs"]:
                    got = candidate_translate(curve, TINY_TABLE, (x, y), address, sign, 0)
                    assert got.output == (x, y)
                    assert got.scratch_clean
                    counts["disabled_field_pairs"] += 1
                    counts["cleanup_checks"] += 1

    encoded_points = tuple(curve.encode(p) for p in points)
    for address in TEST_PLAN["addresses"]:
        for sign in TEST_PLAN["signs"]:
            addend = selected_addend(curve, TINY_TABLE, address, sign)
            for enable in TEST_PLAN["enables"]:
                outputs = []
                for point, word in zip(points, encoded_points):
                    got = candidate_translate(curve, TINY_TABLE, word, address, sign, enable)
                    expected = point if not enable else complete_add(curve, point, addend)
                    assert got.output == curve.encode(expected)
                    assert got.scratch_clean
                    outputs.append(got.output)
                    counts["cleanup_checks"] += 1
                    if enable:
                        counts["enabled_subgroup_cases"] += 1
                        if got.exceptional_branch:
                            counts["exception_branch_hits"][got.exceptional_branch] += 1
                assert len(set(outputs)) == curve.order
                counts["basis_permutation_blocks"] += 1

    assert all(v > 0 for v in counts["exception_branch_hits"].values())

    negative = {}
    try:
        candidate_translate(curve, TINY_TABLE, TINY_TABLE[0], 0, 0, 0, omit_totalization=True)
        negative["omit_totalization"] = {"detected": False, "reason": "partial division unexpectedly accepted X-a=0"}
    except ZeroDivisionError as exc:
        negative["omit_totalization"] = {"detected": True, "reason": str(exc)}
    bad = candidate_translate(curve, TINY_TABLE, OMEGA, 0, 0, 1, premature_flag_cleanup=True)
    expected = curve.encode(TINY_TABLE[0])
    negative["premature_flag_cleanup"] = {
        "detected": bad.output != expected or not bad.scratch_clean,
        "observed_output": list(bad.output),
        "expected_output": list(expected),
        "scratch_clean": bad.scratch_clean,
    }
    assert all(v["detected"] for v in negative.values())

    elapsed = time.time() - started
    return {
        "schema": "crypto.autoresearch.control_results.v1",
        "task_id": "TASK-20260824-4c797e",
        "status": "completed_valid",
        "test_plan": TEST_PLAN,
        "counts": counts,
        "negative_controls": negative,
        "coherent_address_check": {
            "method": "full_cleaned_basis_permutation",
            "blocks": counts["basis_permutation_blocks"],
            "all_blocks_bijective": True,
            "all_ancillas_clean": True,
            "linear_extension": "Each cleaned address/sign/enable block is the required permutation; controlled direct sum therefore agrees on every superposition by linearity.",
        },
        "elapsed_seconds": elapsed,
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "unexpected_observations": [],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    args = parser.parse_args()
    result = main()
    Path(args.json).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))

