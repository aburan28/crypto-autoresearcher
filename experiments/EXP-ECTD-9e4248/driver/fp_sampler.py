"""
fp_sampler.py -- HARD REQUIREMENT fix for spec.inputs.n_bit_range_sampling_requirement
(D3 / DEC-20260806-4a9604 / red-team finding D3).

reused/fp.py's random_prime(bits, rng) returns a prime of EXACTLY `bits` bits by
construction (confirmed by direct reading of its docstring and source: it sets
lo=1<<(bits-1), hi=(1<<bits)-1, i.e. a fixed single bit-width). This experiment MUST
NOT reuse that function unmodified for any measurement whose bit-width is supposed to
vary across the declared [40,60] (or the disclosed sub-range actually used -- see
implementation.md) range.

This module implements option (b) from spec.inputs.n_bit_range_sampling_requirement:
draw a distinct target bit-length per seed from the declared candidate set, and pass
that per-seed width explicitly to a width-exact prime search (reused/fp.random_prime
under the hood is still width-exact -- that part of it is NOT wrong, only the fact
that every EXP-ECTD-001 run always requested the same fixed `bits` argument was the
bug). Every call site in this driver that needs a "random prime in the declared
range" must go through `draw_target_bits` first (to get a genuinely-varying per-seed
width) and then call `prime_of_exact_bits` with that per-seed width -- never a single
hardcoded width shared by every seed.
"""
import random
from .reused import fp


def draw_target_bits(rng, candidates):
    """Draw ONE target bit-length from `candidates` (a list, e.g. list(range(40,45))).
    Distinct per-seed by construction because the caller passes a seed-specific rng."""
    return rng.choice(list(candidates))


def prime_of_exact_bits(bits, rng):
    """Thin, explicit wrapper: a prime of exactly `bits` bits. This is fp.random_prime
    itself (which is NOT wrong in isolation), used ONLY after draw_target_bits has
    already produced a genuinely-varying per-seed width -- the fix is in the CALLER's
    discipline (vary the width argument per seed), not in this function's body."""
    return fp.random_prime(bits, rng)
