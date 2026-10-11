#!/usr/bin/env python3
"""Stage 1 structural fixture + certificate equality for EXP-BINSTD-a8efe2.

m=3, l in {3,4}, arms trinomial / pentanomial; optional normal-basis arm.
Brute-force verifies encoder ↔ algebraic oracle certificate equality per arm
and compares core-variable counts / block partitions / solution-count ratios.
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from encoder import (
    brute_force_solutions,
    encode_pdp_full,
    encoder_solutions,
    eval_s3_coords,
)
from gf2n import MODULI, N, Field, is_irreducible, poly_to_string
from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-ffab44"
SEEDS = [20261001, 20261002, 20261003, 20261004, 20261005]
B_CURVE = 1


def try_normal_basis(n: int = N) -> dict:
    """Attempt a normal-basis construction; skip with reason if not cheaply constructible.

    A normal element β satisfies that {β, β^2, ..., β^{2^{n-1}}} is an F_2-basis.
    We search in the trinomial model; if found, report as third arm metadata only
    (structure-constant multiplication not folded into penta/tri ratio).
    """
    field = Field(n, MODULI["trinomial"])
    for cand in range(1, min(field.q, 512)):
        basis = []
        x = cand
        ok = True
        seen = []
        for _ in range(n):
            seen.append(x)
            x = field.sqr(x)
        # Check linear independence of seen as bit-vectors
        mat = seen[:]
        rank = 0
        used = [False] * n
        for row in range(n):
            piv = None
            for j in range(n):
                if not used[j] and ((mat[j] >> row) & 1):
                    piv = j
                    break
            if piv is None:
                ok = False
                break
            used[piv] = True
            rank += 1
            for j in range(n):
                if j != piv and ((mat[j] >> row) & 1):
                    mat[j] ^= mat[piv]
        if ok and rank == n:
            return {
                "constructible": True,
                "normal_element": cand,
                "normal_element_hex": hex(cand),
                "model_modulus": poly_to_string(MODULI["trinomial"]),
                "interpretation": (
                    "THIRD arm only; structure-constant multiplication. "
                    "Not folded into pentanomial/trinomial ratio."
                ),
                "encoded_in_stage1": False,
                "reason_not_encoded": (
                    "Protocol: report as separately interpreted third arm. "
                    "Full structure-constant CNF-XOR encoder deferred; "
                    "constructibility recorded. Not an invalidation."
                ),
            }
    return {
        "constructible": False,
        "skipped_with_reason": "no normal element found in search bound <512",
        "encoded_in_stage1": False,
    }


def run_cell(l: int, seed: int) -> dict:
    rng = random.Random(seed)
    arms = {}
    for arm_name, mod in MODULI.items():
        field = Field(N, mod)
        # Planted SAT
        planted = tuple(rng.randrange(1 << l) for _ in range(3))
        target_sat = eval_s3_coords(field, planted, l, B_CURVE)
        # UNSAT attempt: random target; may accidentally be SAT — label by intent
        target_unsat = rng.randrange(1 << N)
        while target_unsat == target_sat:
            target_unsat = rng.randrange(1 << N)

        sys_sat = encode_pdp_full(
            field, 3, l, target_sat, arm_name, "planted_SAT", planted=planted, b_curve=B_CURVE
        )
        alg_sat = brute_force_solutions(field, l, target_sat, B_CURVE)
        enc_sat = encoder_solutions(sys_sat)
        cert_eq_sat = sorted(alg_sat) == sorted(enc_sat)
        planted_in = planted in alg_sat

        sys_u = encode_pdp_full(
            field, 3, l, target_unsat, arm_name, "UNSAT", planted=None, b_curve=B_CURVE
        )
        alg_u = brute_force_solutions(field, l, target_unsat, B_CURVE)
        enc_u = encoder_solutions(sys_u)
        cert_eq_u = sorted(alg_u) == sorted(enc_u)

        arms[arm_name] = {
            "modulus": poly_to_string(mod),
            "core_variable_count": sys_sat.core_variable_count,
            "block_partition": sys_sat.block_partition,
            "planted_SAT": {
                "planted": list(planted),
                "target": target_sat,
                "n_solutions_algebraic": len(alg_sat),
                "n_solutions_encoder": len(enc_sat),
                "certificate_set_equality_encoder_oracle": cert_eq_sat,
                "planted_in_solution_set": planted_in,
                "clause_width_mean_measured": sys_sat.clause_width_mean(),
                "clause_width_max_measured": sys_sat.clause_width_max(),
                "substitution_variable_count_measured": sys_sat.substitution_variable_count,
                "clause_width_histogram_measured": sys_sat.clause_width_histogram(),
            },
            "UNSAT_intent": {
                "target": target_unsat,
                "actually_unsat": len(alg_u) == 0,
                "n_solutions_algebraic": len(alg_u),
                "n_solutions_encoder": len(enc_u),
                "certificate_set_equality_encoder_oracle": cert_eq_u,
                "clause_width_mean_measured": sys_u.clause_width_mean(),
                "substitution_variable_count_measured": sys_u.substitution_variable_count,
            },
        }

    tri = arms["trinomial"]
    pent = arms["pentanomial"]
    core_match = tri["core_variable_count"] == pent["core_variable_count"]
    block_match = tri["block_partition"] == pent["block_partition"]
    n_tri = tri["planted_SAT"]["n_solutions_algebraic"]
    n_pent = pent["planted_SAT"]["n_solutions_algebraic"]
    ratio = (n_pent / n_tri) if n_tri else None
    cert_all = (
        tri["planted_SAT"]["certificate_set_equality_encoder_oracle"]
        and pent["planted_SAT"]["certificate_set_equality_encoder_oracle"]
        and tri["UNSAT_intent"]["certificate_set_equality_encoder_oracle"]
        and pent["UNSAT_intent"]["certificate_set_equality_encoder_oracle"]
    )
    # Cross-arm: equisatisfiability of planted (both SAT) and solution-count ratio
    # Full tuple-set identity across different moduli is NOT expected without
    # phi-transport (owned by f37254, excluded). Measured separately.
    cross_tuple_equal = (
        sorted(tuple(tri["planted_SAT"]["planted"]))  # noqa — placeholder compare counts only
        and False
    )
    # Explicit: compare whether the planted bitstrings (same seed stream order)
    # — they differ per-arm because rng advances per arm. Re-run with shared plant:
    return {
        "l": l,
        "seed": seed,
        "arms": arms,
        "structural_fixture": {
            "core_variable_count_identical": core_match,
            "block_partition_identical": block_match,
            "core_variable_count": tri["core_variable_count"],
            "block_partition": tri["block_partition"],
        },
        "certificate_set_equality": cert_all,
        "leaf_or_solution_count_ratio_measured": ratio,
        "leaf_or_solution_count_ratio_in_band": (
            ratio is not None and 0.95 <= ratio <= 1.05
        ),
        "cross_arm_tuple_set_equality": {
            "measured": False,
            "note": (
                "Exact cross-arm solution-tuple multiset identity requires "
                "field-isomorphism transport (IDEA-20260922-f37254), which this "
                "packet must NOT implement (HOLD-I non-duplication). "
                "certificate_set_equality here = encoder↔oracle per arm "
                "(brute-force verified)."
            ),
        },
        "clause_width_ratio_measured": (
            pent["planted_SAT"]["clause_width_mean_measured"]
            / tri["planted_SAT"]["clause_width_mean_measured"]
            if tri["planted_SAT"]["clause_width_mean_measured"]
            else None
        ),
        "naive_term_ratio_modeled": {"label": "MODELED", "value": 5 / 3},
    }


def run_cell_shared_plant(l: int, seed: int) -> dict:
    """Same planted coordinates under both moduli (independent arithmetic per arm)."""
    rng = random.Random(seed)
    planted = tuple(rng.randrange(1 << l) for _ in range(3))
    arms = {}
    for arm_name, mod in MODULI.items():
        field = Field(N, mod)
        target_sat = eval_s3_coords(field, planted, l, B_CURVE)
        target_unsat = rng.randrange(1 << N)
        # keep unsat draw independent but deterministic per arm via local rng copy advancement

        sys_sat = encode_pdp_full(
            field, 3, l, target_sat, arm_name, "planted_SAT", planted=planted, b_curve=B_CURVE
        )
        alg_sat = brute_force_solutions(field, l, target_sat, B_CURVE)
        enc_sat = encoder_solutions(sys_sat)

        sys_u = encode_pdp_full(
            field, 3, l, target_unsat, arm_name, "UNSAT", b_curve=B_CURVE
        )
        alg_u = brute_force_solutions(field, l, target_unsat, B_CURVE)
        enc_u = encoder_solutions(sys_u)

        arms[arm_name] = {
            "modulus": poly_to_string(mod),
            "core_variable_count": sys_sat.core_variable_count,
            "block_partition": sys_sat.block_partition,
            "planted_SAT": {
                "planted": list(planted),
                "target": target_sat,
                "solutions_algebraic": [list(s) for s in sorted(alg_sat)],
                "n_solutions_algebraic": len(alg_sat),
                "n_solutions_encoder": len(enc_sat),
                "certificate_set_equality_encoder_oracle": sorted(alg_sat) == sorted(enc_sat),
                "planted_in_solution_set": planted in alg_sat,
                "clause_width_mean_measured": sys_sat.clause_width_mean(),
                "clause_width_max_measured": sys_sat.clause_width_max(),
                "substitution_variable_count_measured": sys_sat.substitution_variable_count,
                "clause_width_histogram_measured": sys_sat.clause_width_histogram(),
            },
            "UNSAT_intent": {
                "target": target_unsat,
                "actually_unsat": len(alg_u) == 0,
                "n_solutions_algebraic": len(alg_u),
                "n_solutions_encoder": len(enc_u),
                "certificate_set_equality_encoder_oracle": sorted(alg_u) == sorted(enc_u),
                "clause_width_mean_measured": sys_u.clause_width_mean(),
                "substitution_variable_count_measured": sys_u.substitution_variable_count,
            },
        }

    tri, pent = arms["trinomial"], arms["pentanomial"]
    n_tri = tri["planted_SAT"]["n_solutions_algebraic"]
    n_pent = pent["planted_SAT"]["n_solutions_algebraic"]
    ratio = (n_pent / n_tri) if n_tri else None
    cert_all = all(
        arms[a][k]["certificate_set_equality_encoder_oracle"]
        for a in arms
        for k in ("planted_SAT", "UNSAT_intent")
    )
    return {
        "l": l,
        "seed": seed,
        "shared_planted_coords": list(planted),
        "arms": arms,
        "structural_fixture": {
            "core_variable_count_identical": tri["core_variable_count"] == pent["core_variable_count"],
            "block_partition_identical": tri["block_partition"] == pent["block_partition"],
            "core_variable_count": tri["core_variable_count"],
            "block_partition": tri["block_partition"],
        },
        "certificate_set_equality": cert_all,
        "leaf_or_solution_count_ratio_measured": ratio,
        "leaf_or_solution_count_ratio_in_band": ratio is not None and 0.95 <= ratio <= 1.05,
        "cross_arm_note": (
            "Shared planted coordinates; targets differ per modulus arithmetic. "
            "N_leaf ratio compares solution counts. Tuple-set identity across "
            "moduli requires phi-transport (excluded)."
        ),
        "clause_width_ratio_measured": (
            pent["planted_SAT"]["clause_width_mean_measured"]
            / tri["planted_SAT"]["clause_width_mean_measured"]
            if tri["planted_SAT"]["clause_width_mean_measured"]
            else None
        ),
        "substitution_variable_count_ratio_measured": (
            pent["planted_SAT"]["substitution_variable_count_measured"]
            / tri["planted_SAT"]["substitution_variable_count_measured"]
            if tri["planted_SAT"]["substitution_variable_count_measured"]
            else None
        ),
        "naive_term_ratio_modeled": {"label": "MODELED", "value": 5 / 3},
    }


def main() -> int:
    # Predictions must already exist
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.yaml"
    if not pred_path.exists():
        raise SystemExit("REFUSE: Stage 0 predictions missing; cannot start Stage 1")

    t0 = time.perf_counter()
    started = utc_now()
    cells = []
    for l in (3, 4):
        for seed in SEEDS:
            cells.append(run_cell_shared_plant(l, seed))

    # Aggregate structural + certificate
    structural_ok = all(
        c["structural_fixture"]["core_variable_count_identical"]
        and c["structural_fixture"]["block_partition_identical"]
        for c in cells
    )
    cert_ok = all(c["certificate_set_equality"] for c in cells)
    ratios = [c["leaf_or_solution_count_ratio_measured"] for c in cells if c["leaf_or_solution_count_ratio_measured"] is not None]
    cw_ratios = [c["clause_width_ratio_measured"] for c in cells if c["clause_width_ratio_measured"] is not None]

    normal = try_normal_basis()

    fixture_report = {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": 1,
        "n": N,
        "m": 3,
        "l_values": [3, 4],
        "seeds": SEEDS,
        "structural_fixture_pass": structural_ok,
        "predictions_ref": "experiments/EXP-BINSTD-a8efe2/stage0/preregistered-predictions.yaml",
        "cells": cells,
        "normal_basis_third_arm": normal,
        "summary": {
            "core_variable_counts": {
                "l3": 9,
                "l4": 12,
            },
            "all_cells_core_match": structural_ok,
            "mean_solution_count_ratio_measured": sum(ratios) / len(ratios) if ratios else None,
            "solution_count_ratio_spread_measured": {
                "min": min(ratios) if ratios else None,
                "max": max(ratios) if ratios else None,
            },
            "mean_clause_width_ratio_measured": sum(cw_ratios) / len(cw_ratios) if cw_ratios else None,
            "naive_term_ratio_modeled": {"label": "MODELED", "value": 5 / 3},
        },
        "halt_stage2a_on_fixture_fail": not structural_ok or not cert_ok,
    }

    cert_report = {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": 1,
        "certificate_set_equality": cert_ok,
        "definition": (
            "Per-arm encoder solution multiset equals algebraic-oracle multiset "
            "under that arm's modulus (brute-force over 2^{ml} assignments). "
            "Cross-arm geometric tuple identity is out of scope without "
            "f37254 phi-transport (excluded)."
        ),
        "cells": [
            {
                "l": c["l"],
                "seed": c["seed"],
                "certificate_set_equality": c["certificate_set_equality"],
                "trinomial_planted_n": c["arms"]["trinomial"]["planted_SAT"]["n_solutions_algebraic"],
                "pentanomial_planted_n": c["arms"]["pentanomial"]["planted_SAT"]["n_solutions_algebraic"],
                "leaf_or_solution_count_ratio_measured": c["leaf_or_solution_count_ratio_measured"],
            }
            for c in cells
        ],
        "all_cells_pass": cert_ok,
    }

    # Strip bulky solution lists from fixture yaml for readability — keep counts
    cells_light = []
    for c in cells:
        cl = {
            "l": c["l"],
            "seed": c["seed"],
            "shared_planted_coords": c["shared_planted_coords"],
            "structural_fixture": c["structural_fixture"],
            "certificate_set_equality": c["certificate_set_equality"],
            "leaf_or_solution_count_ratio_measured": c["leaf_or_solution_count_ratio_measured"],
            "leaf_or_solution_count_ratio_in_band": c["leaf_or_solution_count_ratio_in_band"],
            "clause_width_ratio_measured": c["clause_width_ratio_measured"],
            "substitution_variable_count_ratio_measured": c["substitution_variable_count_ratio_measured"],
            "naive_term_ratio_modeled": c["naive_term_ratio_modeled"],
            "arms": {},
        }
        for aname, a in c["arms"].items():
            ps = dict(a["planted_SAT"])
            ps.pop("solutions_algebraic", None)
            cl["arms"][aname] = {
                "modulus": a["modulus"],
                "core_variable_count": a["core_variable_count"],
                "block_partition": a["block_partition"],
                "planted_SAT": ps,
                "UNSAT_intent": a["UNSAT_intent"],
            }
        cells_light.append(cl)
    fixture_report["cells"] = cells_light

    dump_yaml(EXP_ROOT / "stage1" / "structural-fixture-report.yaml", fixture_report)
    dump_yaml(EXP_ROOT / "stage1" / "certificate-equality.yaml", cert_report)

    wall = time.perf_counter() - t0
    finished = utc_now()
    valid = structural_ok and cert_ok
    metrics = {
        "structural_fixture_pass": structural_ok,
        "certificate_set_equality": cert_ok,
        "mean_solution_count_ratio_measured": fixture_report["summary"]["mean_solution_count_ratio_measured"],
        "mean_clause_width_ratio_measured": fixture_report["summary"]["mean_clause_width_ratio_measured"],
        "normal_basis_constructible": normal.get("constructible"),
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
    }
    stdout = (
        f"Stage 1 complete\n"
        f"  structural_fixture_pass={structural_ok}\n"
        f"  certificate_set_equality={cert_ok}\n"
        f"  mean N_leaf ratio measured={metrics['mean_solution_count_ratio_measured']}\n"
        f"  mean clause_width_ratio measured={metrics['mean_clause_width_ratio_measured']}\n"
        f"  normal_basis={normal.get('constructible')}\n"
        f"  cells={len(cells)}\n"
    )
    write_run_package(
        RUN_ID,
        stage=1,
        arm="structural-fixture",
        seed=SEEDS[0],
        command="python3 experiments/EXP-BINSTD-a8efe2/implementation/stage1_run.py",
        parameters={"n": N, "m": 3, "l": [3, 4], "seeds": SEEDS},
        metrics=metrics,
        valid=valid,
        invalid_reason=None if valid else "structural_or_certificate_failure",
        termination_reason="completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none"},
    )
    print(stdout)
    if fixture_report["halt_stage2a_on_fixture_fail"]:
        print("HALT: Stage 2a blocked by fixture/certificate failure")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
