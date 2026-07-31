#!/usr/bin/env python3
"""EXP-STR-005 / BATCH-015: RT35-CTRL-1 and RT35-CTRL-2 supply-and-structure probe.

Zero alpha / ladder / cost. Orbit closure DISABLED (include_phi_orbits=False).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from harness.endomorphism_la import (
    _build_phi_invariant_factor_base,
    _build_random_factor_base,
    _collect_relations,
    _find_zeta3,
    _generate_j0_instance,
)

CELLS = [
    {"name": "L12", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 12, "m": 2, "R_base": 5},
    {"name": "L13", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 13, "m": 2, "R_base": 6},
    {"name": "L24", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 24, "m": 2, "R_base": 9},
    {"name": "L25", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 25, "m": 2, "R_base": 10},
    {"name": "L48", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 48, "m": 2, "R_base": 17},
    {"name": "L49", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 49, "m": 2, "R_base": 18},
    {"name": "L96", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 96, "m": 2, "R_base": 33},
    {"name": "L97", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 97, "m": 2, "R_base": 34},
    {"name": "L192", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 192, "m": 2, "R_base": 65},
    {"name": "L193", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 193, "m": 2, "R_base": 66},
    {"name": "X96", "curve": "CURVE-J16S3", "seed": 3, "bits": 16, "B": 96, "m": 2, "R_base": 33},
    {"name": "X97", "curve": "CURVE-J16S3", "seed": 3, "bits": 16, "B": 97, "m": 2, "R_base": 34},
    {"name": "A12M3", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 12, "m": 3, "R_base": 5},
    {"name": "A13M3", "curve": "CURVE-J12S1", "seed": 1, "bits": 12, "B": 13, "m": 3, "R_base": 6},
]

OUT = Path("experiments/EXP-STR-005/results")


def ctrl4_check(F: list[int], B: int, zeta3: int, p: int) -> dict:
    len_ok = len(F) == B
    block_failures = []
    if len(F) >= 3:
        n_blocks = len(F) // 3
        for j in range(n_blocks):
            x0 = F[3 * j]
            for k in range(3):
                expected = (pow(zeta3, k, p) * x0) % p
                got = F[3 * j + k]
                if got != expected:
                    block_failures.append({"j": j, "k": k, "expected": expected, "got": got})
    return {
        "len_equals_B": len_ok,
        "len_F": len(F),
        "B": B,
        "orbit_block_ok": len(block_failures) == 0 and len(F) >= 3,
        "orbit_block_failures": block_failures[:5],
        "short_list": len(F) < B,
    }


def main() -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)

    # cache instances
    instances = {}
    for key, seed, bits in (("CURVE-J12S1", 1, 12), ("CURVE-J16S3", 3, 16)):
        inst = _generate_j0_instance(seed=seed, field_bits=bits)
        if inst is None:
            raise RuntimeError(f"failed to generate {key}")
        zeta3 = _find_zeta3(inst.p)
        if zeta3 is None:
            raise RuntimeError(f"no zeta3 for {key}")
        instances[key] = (inst, zeta3)

    # RT35-CTRL-1
    inst, zeta3 = instances["CURVE-J12S1"]
    ctrl1 = {"curve": "CURVE-J12S1", "p": inst.p, "n": inst.n, "seed": inst.seed, "zeta3": zeta3, "B_checks": {}}
    for B in (192, 193):
        F = _build_phi_invariant_factor_base(inst, B, zeta3)
        ctrl1["B_checks"][str(B)] = ctrl4_check(F, B, zeta3, inst.p)
    ctrl1_fail = any(v["short_list"] or not v["orbit_block_ok"] or not v["len_equals_B"] for v in ctrl1["B_checks"].values())
    ctrl1["disposition"] = "FAIL_SHORT_OR_STRUCTURE" if ctrl1_fail else "PASS_CTRL4"

    # RT35-CTRL-2
    supply_rows = []
    for cell in CELLS:
        inst, zeta3 = instances[cell["curve"]]
        B, m, R_base = cell["B"], cell["m"], cell["R_base"]
        for arm, builder in (
            ("A_prime_phi_invariant_fb", lambda: _build_phi_invariant_factor_base(inst, B, zeta3)),
            ("E_prime_random_fb", lambda: _build_random_factor_base(inst, B)),
        ):
            F = builder()
            # collect with closure disabled; ask for R_base relations
            relations, hits, attempts = _collect_relations(
                inst, F, m, num_targets=R_base, zeta3=0, include_phi_orbits=False
            )
            shortfall = max(0, R_base - len(relations))
            supply_rows.append(
                {
                    "cell": cell["name"],
                    "curve": cell["curve"],
                    "arm": arm,
                    "B": B,
                    "m": m,
                    "R_base": R_base,
                    "len_F": len(F),
                    "fb_short": len(F) < B,
                    "len_relations": len(relations),
                    "hits": hits,
                    "attempts": attempts,
                    "shortfall": shortfall,
                    "shortfall_ge_2": shortfall >= 2,
                }
            )

    ctrl2_fail = any(r["shortfall_ge_2"] or r["fb_short"] for r in supply_rows)
    ctrl2 = {
        "disposition": "FAIL_SUPPLY_OR_FB_SHORT" if ctrl2_fail else "PASS_SUPPLY",
        "rows": supply_rows,
        "n_rows": len(supply_rows),
        "n_shortfall_ge_2": sum(1 for r in supply_rows if r["shortfall_ge_2"]),
        "n_fb_short": sum(1 for r in supply_rows if r["fb_short"]),
    }

    # Pre-registered falsification of stand-down basis
    stand_down_basis_defective = ctrl1_fail or ctrl2_fail
    out = {
        "experiment_id": "EXP-STR-005",
        "task_id": "TASK-20260730-001",
        "goal_id": "GOAL-ECDLP-001",
        "batch_id": "BATCH-015",
        "claim_tier": "toy",
        "what_this_is_not": [
            "Not an H-STR-002 mechanism test",
            "Not an attack or attack improvement",
            "No alpha, ladder, driver, rank, or cost measured",
        ],
        "rt35_ctrl_1": ctrl1,
        "rt35_ctrl_2": ctrl2,
        "stand_down_basis_defective_on_committed_code": stand_down_basis_defective,
        "elapsed_seconds": round(time.time() - t0, 3),
    }
    path = OUT / "probe_results.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "ctrl1": ctrl1["disposition"],
        "ctrl2": ctrl2["disposition"],
        "stand_down_basis_defective": stand_down_basis_defective,
        "elapsed": out["elapsed_seconds"],
        "path": str(path),
    }, indent=2))


if __name__ == "__main__":
    main()
