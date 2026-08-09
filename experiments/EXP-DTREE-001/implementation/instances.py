"""RUN-DTREE-001: freeze main instances, targets, standard/medium factor
bases, and the exact-enumeration slope grid.

Seed-to-size mapping. The specification states seeds {1,2,3} map "one-to-one"
to sizes {16,20,24} without pinning the exact pairing. This module adopts the
only natural reading -- ascending seed to ascending bit size (seed1<->16,
seed2<->20, seed3<->24) -- and records that choice explicitly here and in the
frozen artifact so it is auditable, per AGENTS.md rule 8 (nothing about the
mapping is silently assumed).
"""
from __future__ import annotations

import math
from math import comb

from harness.toycurve import generate_instance
from harness.semaev import build_factor_base

MAIN_SPECS = [(16, 1), (20, 2), (24, 3)]   # (field_bits, seed)
TINY_SPECS = [(8, 1), (10, 1), (12, 1)]    # (field_bits, seed) -- all seed 1 per spec
MEDIUM_MULTIPLIERS = [2, 4, 8, 16]
N_TARGETS = 50
GRID_MIN_BPRIME = 8
GRID_MIN_C = 50
GRID_MAX_LAMBDA = 0.7
GRID_MIN_CELLS_REQUIRED = 6


def seed_int(seed: int, tag: str) -> int:
    from harness.toycurve import _seed_int
    return _seed_int(seed, tag)


def freeze_main_instance(bits: int, seed: int) -> dict:
    inst = generate_instance(seed=seed, field_bits=bits)
    E = inst.curve()
    N = inst.n
    B = math.ceil(math.sqrt(N))
    standard_fb = build_factor_base(inst, B)  # seed defaults to inst.seed
    medium_fbs = {}
    for mult in MEDIUM_MULTIPLIERS:
        size = mult * B
        medium_fbs[mult] = {"size": size, "factor_base": build_factor_base(inst, size)}

    targets = []
    seen_points = set()
    for i in range(N_TARGETS):
        a = seed_int(seed, f"target_a_{i}") % N
        b = seed_int(seed, f"target_b_{i}") % N
        R = E.add(E.mul(a, inst.P), E.mul(b, inst.Q))
        seen_points.add(R)
        targets.append({"index": i, "a": a, "b": b, "R": list(R) if R is not None else None})

    return {
        "field_bits": bits, "seed": seed,
        "p": inst.p, "a": inst.a, "b": inst.b,
        "P": list(inst.P), "Q": list(inst.Q), "n": N, "k": inst.k,
        "standard_B": B,
        "standard_factor_base": standard_fb,
        "medium_bases": medium_fbs,
        "targets": targets,
        "distinct_target_points": len(seen_points),
        "requested_target_count": N_TARGETS,
        "group_order_n": N,
    }


def lambda_table(N: int, b_min: int = GRID_MIN_BPRIME, b_max: int | None = None) -> list[dict]:
    """Exact C(B',3) and lambda=C(B',3)/N for a sweep of candidate B' values.

    b_max defaults to a value comfortably past where lambda exceeds the 0.7
    ceiling for any N tested here (so the table visibly demonstrates the
    monotone trend, not just the boundary), while staying cheap: since
    C(B',3) is strictly increasing in B', once C(B',3) > 5*N further B'
    values cannot possibly qualify and are omitted from the table.
    """
    rows = []
    bp = b_min
    while True:
        c = comb(bp, 3)
        lam = c / N if N > 0 else float("inf")
        qualifies = (bp >= GRID_MIN_BPRIME) and (c >= GRID_MIN_C) and (lam <= GRID_MAX_LAMBDA)
        rows.append({"b_prime": bp, "c_b_prime_3": c, "lambda": lam, "qualifies": qualifies})
        if b_max is not None:
            if bp >= b_max:
                break
        elif c > 5 * N and bp > b_min + 4:
            break
        bp += 1
        if bp > 4096:  # hard safety stop, never reached for these tiny N
            break
    return rows


def freeze_tiny_instance(bits: int, seed: int) -> dict:
    inst = generate_instance(seed=seed, field_bits=bits)
    N = inst.n
    table = lambda_table(N)
    qualifying = [row["b_prime"] for row in table if row["qualifies"]]
    return {
        "field_bits": bits, "seed": seed,
        "p": inst.p, "a": inst.a, "b": inst.b,
        "P": list(inst.P), "Q": list(inst.Q), "n": N, "k": inst.k,
        "lambda_table": table,
        "qualifying_b_prime": qualifying,
    }


def build_frozen_instances() -> dict:
    mains = {bits: freeze_main_instance(bits, seed) for bits, seed in MAIN_SPECS}
    tinies = {bits: freeze_tiny_instance(bits, seed) for bits, seed in TINY_SPECS}

    total_qualifying_cells = sum(len(t["qualifying_b_prime"]) for t in tinies.values())
    design_infeasible = total_qualifying_cells < GRID_MIN_CELLS_REQUIRED

    return {
        "seed_to_size_mapping": {str(bits): seed for bits, seed in MAIN_SPECS},
        "main_instances": mains,
        "tiny_instances": tinies,
        "slope_grid": {
            "rule": {"b_prime_min": GRID_MIN_BPRIME, "c_min": GRID_MIN_C,
                     "lambda_max": GRID_MAX_LAMBDA,
                     "min_cells_required_across_all_tiny_curves": GRID_MIN_CELLS_REQUIRED},
            "per_curve_qualifying_b_prime": {
                bits: tinies[bits]["qualifying_b_prime"] for bits, _ in TINY_SPECS
            },
            "total_qualifying_cells": total_qualifying_cells,
            "design_infeasible": design_infeasible,
        },
    }


def _int_keys(d: dict) -> dict:
    return {int(k): v for k, v in d.items()}


def load_frozen(raw_json_path: str) -> dict:
    """Reload the frozen-instances structure written by RUN-DTREE-001's
    raw.json, restoring the int-keyed dicts JSON round-tripping turns into
    string keys (main_instances/tiny_instances by field_bits, medium_bases
    by multiplier, per_curve_qualifying_b_prime by field_bits)."""
    import json
    with open(raw_json_path) as f:
        doc = json.load(f)
    frozen = doc["raw"]
    frozen["main_instances"] = _int_keys(frozen["main_instances"])
    for rec in frozen["main_instances"].values():
        rec["medium_bases"] = _int_keys(rec["medium_bases"])
    frozen["tiny_instances"] = _int_keys(frozen["tiny_instances"])
    frozen["slope_grid"]["per_curve_qualifying_b_prime"] = _int_keys(
        frozen["slope_grid"]["per_curve_qualifying_b_prime"])
    return frozen
