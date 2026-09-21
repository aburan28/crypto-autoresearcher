"""Performance optimization layer over instrument.eval_series_mod.

NOT a change to the frozen digit machinery's mathematics: instrument.py's
eval_series_mod(series, t0, N, p) re-reduces every one of the formal group's
~81 Fraction coefficients mod N (via reduce_fraction_mod, one modular
inverse each) on EVERY call. That per-coefficient reduction does not depend
on t0 or on m -- only on (series, N, p), which are fixed for the whole
Stage 2 ladder of one instance. This experiment's ladder makes O(10^4-10^5)
calls per instance (vs. a26bde's 68), so re-reducing the same coefficients
every call is the dominant cost and is pure waste.

reduce_series_once() precomputes the reduced-coefficient list with the
UNMODIFIED, frozen instrument.reduce_fraction_mod (imported read-only via
frozen_ref, never copied-and-edited); fast_eval_reduced() then repeats
exactly instrument.eval_series_mod's own Horner loop on that precomputed
list, arithmetic-for-arithmetic identical, just skipping the redundant
re-reduction. self_check_equivalence() proves the two give bit-identical
results before this module is trusted for any instance, and is invoked at
driver startup (see instance_runner.py), not merely asserted here.
"""
from __future__ import annotations

import random

from frozen_ref import reduce_fraction_mod, eval_series_mod


def reduce_series_once(series, N: int, p: int) -> list[int]:
    return [reduce_fraction_mod(c, N, p) for c in series]


def fast_eval_reduced(reduced_series: list[int], t0: int, N: int) -> int:
    """Byte-for-byte the same Horner recurrence as instrument.eval_series_mod,
    operating on an already-reduced coefficient list instead of re-reducing
    Fractions on every call."""
    result = 0
    for cm in reversed(reduced_series):
        result = (result * t0 + cm) % N
    return result


def self_check_equivalence(series, N: int, p: int, n_samples: int = 25,
                            seed: int = 20260911) -> None:
    """Raise AssertionError if fast_eval_reduced ever disagrees with the
    frozen eval_series_mod on random t0 samples mod N, for this (series, N,
    p), INCLUDING at smaller derived moduli N2 = N // p**v (the case that
    actually arises inside digit_of_section_minus_torsion when
    normalize_proj strips a redundant common p-power factor). Cheap
    (n_samples * few calls of the slow path) relative to a whole ladder."""
    reduced = reduce_series_once(series, N, p)
    rng = random.Random(seed)
    for _ in range(n_samples):
        t0 = rng.randrange(N)
        slow = eval_series_mod(series, t0, N, p)
        fast = fast_eval_reduced(reduced, t0, N)
        if slow != fast:
            raise AssertionError(
                f"fastseries self-check FAILED: eval_series_mod({t0=}) = "
                f"{slow} but fast_eval_reduced = {fast} (N={N}, p={p}); "
                "the cached-series optimization is not equivalent to the "
                "frozen digit machinery -- refusing to use it.")
    # Also check at a smaller derived modulus N2 | N (a lower p-power),
    # the case fast_eval_reduced is actually used at inside the main ladder.
    for v in (1, 2, 3):
        N2 = N // (p ** v)
        if N2 <= 1:
            continue
        t0 = rng.randrange(N2)
        slow2 = eval_series_mod(series, t0, N2, p)
        fast2 = fast_eval_reduced(reduced, t0, N2)
        if slow2 != fast2:
            raise AssertionError(
                f"fastseries self-check FAILED at derived modulus N2=N/p^{v}: "
                f"eval_series_mod({t0=}, N2) = {slow2} but "
                f"fast_eval_reduced(reduced-at-N, {t0=}, N2) = {fast2} "
                f"(N={N}, p={p}); refusing to use the cached-series path.")
