#!/usr/bin/env python3
"""The matched null for EXP-SEMBIN-354a75: eq. (11)'s object, realized.

WHAT THE CONTROL IS FOR. eq. (11) is not a statement about elliptic curves. It
is a statement about a symmetric random mapping from V^t to F_q: Section 4.3
adopts that model, counts its classes as K, and reads off
P = 1 - (1 - 1/q)^K. So the model can be BUILT. Draw one uniform value in F_q
for each class, count how many classes land on each target, and push those
counts through the same ratio code the curve cells use. If the pipeline reports
a shortfall on an object that is literally the model, the shortfall is the
pipeline's and every curve-derived number is void.

WHICH CLASS COUNT IS REALIZED, AND WHY IT IS NOT A FREE CHOICE. The number of
classes of t-tuples from V under permutation is exactly C(|V|+t-1, t). Semaev
writes K ~ |V|^t/t!, which is the same quantity with the coincidences dropped,
and the two differ by

    C(|V|+t-1, t) / (|V|^t/t!) = prod_{i=1}^{t-1} (1 + i/|V|),

a factor that is 1.0002 at |V| = 4096, t = 2 and 14.8 at |V| = 4, t = 6. The
null is realized on the EXACT class count, because that is the number of
classes the curve enumeration also has; comparing it against eq. (11) under
the exact-multiset variant is therefore the honest test of the pipeline, and
comparing the same realization against Semaev's variant MEASURES the
approximation above rather than testing anything about the code. Both are
reported, and the closed form is checked against the realization so that a
reader can see the two agree.

The null is evaluated over ALL q targets, not over a sample: the object is
synthetic, so there is no reason to inherit the contract's 2000-draw sampling
error here. The 2000-draw version is reported beside it precisely so that the
sampling error the curve cells do carry can be seen on an object whose true
value is known.
"""
from __future__ import annotations

from math import comb, factorial, prod

import numpy as np

from yield_stats import Z95, eq11, poisson_fit, ratio_block, wilson


def class_count_inflation(v_size: int, t: int) -> float:
    """C(|V|+t-1, t) / (|V|^t / t!), in closed form."""
    return float(prod(1.0 + i / v_size for i in range(1, t)))


def realize_symmetric_map(n: int, t: int, k: int, seed: int,
                          mode: str = "exact_multiset") -> np.ndarray:
    """Per-target counts for one realization of the model's random mapping.

    Returns an array of length q: entry z is the number of classes whose value
    is z, which is exactly what the curve pipeline calls the per-R count.

    mode="exact_multiset" realizes one value per genuine permutation class,
    C(|V|+t-1, t) of them. mode="ordered" realizes one value per ORDERED tuple,
    |V|^t of them, which is the non-symmetric map and is the known-false
    realization: it inflates the expected count by t! against the symmetric
    one and is here to show the pipeline can see that.
    """
    q = 1 << n
    v_size = 1 << k
    if mode == "exact_multiset":
        K = comb(v_size + t - 1, t)
    elif mode == "ordered":
        K = v_size ** t
    else:
        raise ValueError(f"unknown null mode {mode}")
    rng = np.random.default_rng(seed)
    counts = np.zeros(q, dtype=np.int64)
    # Chunked so that a cell with 8.4 million classes never holds more than a
    # few million draws at once; bincount is accumulated rather than rebuilt.
    remaining, chunk = K, 1 << 22
    while remaining > 0:
        take = int(min(chunk, remaining))
        vals = rng.integers(0, q, size=take, dtype=np.int64)
        counts += np.bincount(vals, minlength=q)
        remaining -= take
    assert int(counts.sum()) == K, (int(counts.sum()), K)
    return counts


def null_block(n: int, m: int, t: int, k: int, seeds: list[int],
               draws: int = 2000, mode: str = "exact_multiset") -> dict:
    """The matched-null control for one cell, over every seed.

    Reports the ratio against BOTH class-count variants. The gate the contract
    reads -- "the realized-random-map matched null returns ratio 1 within its
    interval" -- is the one against the variant that matches what was
    realized; the other is the measured size of eq. (11)'s class-count
    approximation.
    """
    q = 1 << n
    v_size = 1 << k
    K = (comb(v_size + t - 1, t) if mode == "exact_multiset"
         else v_size ** t)
    per_seed = []
    for seed in seeds:
        counts = realize_symmetric_map(n, t, k, seed, mode=mode)
        hits_all = int(np.count_nonzero(counts))
        rng = np.random.default_rng(seed ^ 0x5EED)
        sample = counts[rng.integers(0, q, size=draws)]
        entry = {"seed": seed, "exact_hit_fraction_all_q_targets": hits_all / q,
                 "exact_mean_count": float(counts.mean()),
                 "sampled_draws": draws}
        for variant in ("semaev_v_to_the_t_over_t_factorial",
                        "exact_multiset_count_binom_V_plus_t_minus_1_choose_t",
                        "known_false_v_to_the_t_no_symmetry"):
            model = eq11(n, t, k, variant)
            lo, hi = wilson(hits_all, q)
            entry[variant] = {
                "modelled_P": model["P"],
                "modelled_lambda": model["lambda"],
                "exact_ratio_all_q_targets": (hits_all / q) / model["P"],
                "exact_ratio_ci95": [lo / model["P"], hi / model["P"]],
                "sampled": ratio_block(sample, n, t, k, variant),
            }
        entry["poisson_fit_of_realization"] = poisson_fit(sample)
        per_seed.append(entry)
    matched = ("exact_multiset_count_binom_V_plus_t_minus_1_choose_t"
               if mode == "exact_multiset"
               else "known_false_v_to_the_t_no_symmetry")
    ratios = [s[matched]["exact_ratio_all_q_targets"] for s in per_seed]
    return {
        "cell": {"n": n, "m": m, "t": t, "k": k},
        "realized_mode": mode,
        "realized_class_count": K,
        "matched_variant": matched,
        "class_count_inflation_closed_form": class_count_inflation(v_size, t),
        "class_count_inflation_realized": (
            K / (v_size ** t / factorial(t)) if mode == "exact_multiset"
            else float("nan")),
        "matched_ratio_per_seed": ratios,
        "matched_ratio_mean": float(np.mean(ratios)),
        "matched_ratio_min": float(np.min(ratios)),
        "matched_ratio_max": float(np.max(ratios)),
        "per_seed": per_seed,
    }
