#!/usr/bin/env python3
"""Enumerable m=3 multiset-sum image on Z/rZ labels for the n=19 toy cell.

This realizes the proposal's enumerable sumset control without Magma/Sage:
basis indices map through a frozen seeded PRF into the prime-subgroup
labels of order r=130873 (Koblitz n=19 sibling). No discrete logarithm is
solved.
"""
from __future__ import annotations

import hashlib
import itertools
import random
from typing import Iterable

from union_math import (
    BATCHES_L4,
    BATCHES_L32,
    L4,
    L32,
    M,
    R,
    complementary_half_fold_size,
    rho_iteration_estimate,
    union_prob,
)


def _label(seed: int, parts: Iterable[int]) -> int:
    h = hashlib.sha256()
    h.update(seed.to_bytes(8, "little", signed=False))
    for p in parts:
        h.update(int(p).to_bytes(4, "little", signed=False))
    return int.from_bytes(h.digest()[:8], "little") % R


def enumerate_image(B: int, seed: int, m: int = M) -> tuple[set[int], int]:
    """Enumerate all nondecreasing m-tuples from range(B); map to Z/rZ."""
    image: set[int] = set()
    additions = 0
    for combo in itertools.combinations_with_replacement(range(B), m):
        # charge one "addition-equivalent" per multiset evaluated
        additions += 1
        image.add(_label(seed, combo))
        if additions > 10_000_000:
            raise RuntimeError("image enumeration exceeded 1e7 budget")
    return image, additions


def sample_union_frequency(
    image: set[int],
    L: int,
    batches: int,
    rng: random.Random,
    r: int = R,
) -> dict:
    hits = 0
    empty = 0
    hit_sets: list[frozenset[int]] = []
    for _ in range(batches):
        targets = [rng.randrange(r) for _ in range(L)]
        hit_idx = {i for i, t in enumerate(targets) if t in image}
        if hit_idx:
            hits += 1
            hit_sets.append(frozenset(hit_idx))
        else:
            empty += 1
    # lossy witness: two batches with same hit-count cardinality but different sets
    lossy = False
    by_count: dict[int, list[frozenset[int]]] = {}
    for s in hit_sets:
        by_count.setdefault(len(s), []).append(s)
    for sets in by_count.values():
        if len({frozenset(x) for x in sets}) >= 2:
            lossy = True
            break
    freq = hits / batches if batches else 0.0
    return {
        "batches": batches,
        "L": L,
        "hits": hits,
        "empty": empty,
        "union_frequency": freq,
        "lossy_witness_pair_found": lossy,
    }


def charge_coverage_additions(
    image: set[int],
    B: int,
    L: int,
    rng: random.Random,
    r: int = R,
) -> dict:
    """Charge T_test until each of L chosen targets has been hit (coverage).

    Headline uses complementary half-fold size per membership decision.
    Stops when all L are hit or after a hard cap of ceil(20*L/p_hat) trials.
    """
    t_test = complementary_half_fold_size(B)
    targets = [rng.randrange(r) for _ in range(L)]
    remaining = set(range(L))
    trials = 0
    p_hat = max(len(image) / r, 1e-300)
    cap = max(int(20 * L / p_hat) + 10, 1000)
    while remaining and trials < cap:
        # one membership probe against a fresh random point; if it equals a
        # remaining target and lies in the image, that target is covered.
        # For chosen-target coverage we instead test each remaining target
        # once per sweep, charging T_test per test.
        for i in list(remaining):
            trials += 1
            # membership decision on chosen target i
            in_image = targets[i] in image
            if in_image:
                remaining.discard(i)
            if trials >= cap:
                break
    charged = trials * t_test
    rho = rho_iteration_estimate(L=L)
    return {
        "L": L,
        "targets": targets,
        "trials": trials,
        "T_test_charged": t_test,
        "charged_additions": charged,
        "rho_iteration_estimate": rho,
        "charged_ratio": charged / rho if rho else float("inf"),
        "uncharged_ratio": trials / rho if rho else float("inf"),
        "coverage_complete": not remaining,
        "remaining": sorted(remaining),
        "cap": cap,
    }


def run_cell(cell_id: str, B: int, seed: int) -> dict:
    rng = random.Random(seed ^ (B * 1_000_003) ^ (hash(cell_id) & 0xFFFFFFFF))
    image, enum_adds = enumerate_image(B, seed=seed)
    p_hat = len(image) / R
    u4 = sample_union_frequency(image, L4, BATCHES_L4, rng)
    u32 = sample_union_frequency(image, L32, BATCHES_L32, rng)
    cov = charge_coverage_additions(image, B, L4, rng)
    pred4 = union_prob(p_hat, L4)
    pred32 = union_prob(p_hat, L32)
    lin_err = (L4 * p_hat) - pred4
    return {
        "cell_id": cell_id,
        "B": B,
        "image_size": len(image),
        "p_hat": p_hat,
        "enumeration_additions": enum_adds,
        "full_image": len(image) == R,
        "union_L4": u4,
        "union_L32": u32,
        "prediction_L4": pred4,
        "prediction_L32": pred32,
        "union_abs_deviation_L4": abs(u4["union_frequency"] - pred4),
        "union_abs_deviation_L32": abs(u32["union_frequency"] - pred32),
        "linearization_error": lin_err,
        "coverage": cov,
        "relation_rank_if_full_image": 0 if len(image) == R else None,
    }
