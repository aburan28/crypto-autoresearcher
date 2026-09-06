"""
Deterministic seeded curve sampling rule, per specification.yaml
inputs.curve_sampling_rule.

For a given bit size k: p = smallest prime >= 2^k (sympy.nextprime, exact).
Draw (a, b) uniformly from a seeded PRNG derived from the run's master seed;
reject singular curves, j-invariant 0 or 1728 (extra automorphisms), and any
curve whose exact group order N is not prime or equals p (anomalous curves
are drawn separately, only for the planted-path control -- see planted.py).
Continue until the requested count of unplanted curves is accepted. Every
rejection is recorded with its reason so the acceptance predicate is fully
auditable, not just its outcome.
"""
from __future__ import annotations
import random
from sympy import nextprime, isprime
from .curve_order import compute_group_order, verify_group_order
from .predicates import classify
from .ecc import seeded_rng


def j_invariant(a: int, b: int, p: int):
    denom = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if denom == 0:
        return None  # singular
    num = (1728 * 4 * pow(a, 3, p)) % p
    return (num * pow(denom, -1, p)) % p


def field_prime_for_bits(bit_size: int) -> int:
    return int(nextprime(1 << bit_size))


def sample_unplanted_curves(bit_size: int, master_seed: int, count: int, k_max: int, max_attempts: int = 200000):
    """Returns (p, accepted_list, rejection_tally, attempts_used) where each
    accepted entry is a dict with a, b, N, classify(...) and the rng draw
    index it was found at (for reproducibility)."""
    p = field_prime_for_bits(bit_size)
    rng = seeded_rng(master_seed, bit_size, "unplanted")
    order_rng = seeded_rng(master_seed, bit_size, "order-witness")

    accepted = []
    tally = {"singular": 0, "j_extremal": 0, "order_not_prime": 0, "order_equals_p": 0, "accepted": 0}
    attempts = 0
    while len(accepted) < count and attempts < max_attempts:
        attempts += 1
        a = rng.randrange(0, p)
        b = rng.randrange(0, p)
        j = j_invariant(a, b, p)
        if j is None:
            tally["singular"] += 1
            continue
        if j == 0 or j == 1728 % p:
            tally["j_extremal"] += 1
            continue
        N, ctr, npts = compute_group_order(a, b, p, order_rng)
        if not isprime(N):
            tally["order_not_prime"] += 1
            continue
        if N == p:
            tally["order_equals_p"] += 1
            continue
        assert verify_group_order(N, a, b, p, order_rng, trials=2)
        cls = classify(N, p, k_max)
        accepted.append({
            "a": a, "b": b, "p": p, "N": N, "j_invariant": j,
            "attempt_index": attempts, "classification": cls,
            "field_mults_for_order": ctr.field_mults,
        })
        tally["accepted"] += 1
    return p, accepted, tally, attempts
