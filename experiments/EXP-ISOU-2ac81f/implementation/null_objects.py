"""
Different-ORDER null-object control: at least 8 random curves over a
DECLARED SMALLER prime p' with N' <= N/16 (contract's mandatory
null_object_different_order control). These are cost-RESOLUTION null
objects (they must clearly separate from the class members' costs on the
group-operation axis); same-p different-trace curves are a separate,
purely STRUCTURAL null object (they must never appear in the class walk --
enforced by the (j, trace) dedup key and the order-equality edge
certificate in class_walk.py, not tested again here).
"""
from __future__ import annotations

import random

from curve_utils import build_qr_table, point_count_with_qr
from base_curve_search import is_prime, next_prime


def generate_null_objects(N: int, p_bit_length: int, seed: int, count: int = 8):
    """
    Chooses a smaller prime p' with p' small enough that the Hasse-bounded
    max order (p'+1+2*sqrt(p')) is <= N/16, then finds `count` distinct
    curves over F_p' (varying b, a = -3 fixed for consistency with the
    base curve's model family) with valid (nonsingular) equations. Returns
    a list of dicts {p, a, b, N, t}.
    """
    target_max_order = N // 16
    # Choose p' MUCH smaller than the N/16 floor the contract requires (that
    # floor is a MINIMUM required gap, not a target): a null object barely
    # inside N/16 sits well within the base curve's wide seed-dispersion
    # band (Pollard rho step counts have high relative dispersion), so it
    # would fail to separate for a reason having nothing to do with the
    # class-member cost question. Using p' an order of magnitude smaller
    # still satisfies N' <= N/16 while giving genuine, resolvable
    # separation.
    p_prime_bits = max(4, p_bit_length - 10)
    rng = random.Random(seed)
    objects = []
    tries = 0
    while len(objects) < count and tries < 20000:
        tries += 1
        low = 1 << (p_prime_bits - 1)
        high = (1 << p_prime_bits) - 1
        cand = rng.randrange(low, high)
        p2 = next_prime(cand)
        if p2 > high:
            continue
        hasse_max = p2 + 1 + 2 * int(p2 ** 0.5 + 2)
        if hasse_max > target_max_order:
            continue
        qr = build_qr_table(p2)
        a2 = (-3) % p2
        found = False
        for b2 in range(1, 500):
            disc = (4 * pow(a2, 3, p2) + 27 * pow(b2, 2, p2)) % p2
            if disc == 0:
                continue
            N2 = point_count_with_qr(p2, a2, b2, qr)
            if N2 > target_max_order:
                continue
            t2 = p2 + 1 - N2
            if t2 == 0:
                continue
            if not is_prime(N2):
                # Prime order keeps every scalar-multiple ambiguity out of
                # this control (BSGS's cross-check specifically needs a
                # well-defined cyclic group of the point's actual order);
                # non-prime N' is simply rejected rather than handled with
                # extra order-of-point bookkeeping.
                continue
            objects.append({"p": p2, "a": a2, "b": b2, "N": N2, "t": t2})
            found = True
            break
        if not found:
            continue
    return objects
