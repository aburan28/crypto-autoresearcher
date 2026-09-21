"""Random-quartic S_4 null control.

Draws 2,000 uniformly random monic squarefree quartics per prime per run,
using the exact SHA256-based seed rule of
`seeds_and_reproducibility.random_quartic_control_seed_rule`, and classifies
each via arm_b's OWN distinct-degree code path (polymod.py), not a
special-cased routine.
"""
from __future__ import annotations

import hashlib

import polymod as pm

DOMAIN = "EXP-MONO-4c7479/v1"


def _draw_coeff(domain: str, p: int, j: int, i: int, counter_start: int = 0):
    """Draw one coefficient b_i for draw index j at prime p, per the
    contract's exact seed rule, with rejection sampling against modulo
    bias. Returns (value, final_counter, num_rejections)."""
    threshold = (2 ** 256 // p) * p
    counter = counter_start
    rejections = 0
    while True:
        msg = f"{domain}|quartic-coeff|{p}|{j}|{i}|{counter}".encode("ascii")
        digest = hashlib.sha256(msg).digest()
        val = int.from_bytes(digest, "big")
        if val < threshold:
            return val % p, counter, rejections
        counter += 1
        rejections += 1


def draw_quartic(domain: str, p: int, j: int):
    """Draw one candidate monic quartic Y^4+b3 Y^3+b2 Y^2+b1 Y+b0 for draw
    index j. Coefficient index i ranges 0..3 (b0..b3); each coefficient's
    own rejection-sampling counter starts fresh at 0 per the seed rule
    (counter increments only within that coefficient's own draw)."""
    coeffs = {}
    total_rejections = 0
    for i in range(4):
        val, _, rej = _draw_coeff(domain, p, j, i)
        coeffs[i] = val
        total_rejections += rej
    b0, b1, b2, b3 = coeffs[0], coeffs[1], coeffs[2], coeffs[3]
    poly = [b0 % p, b1 % p, b2 % p, b3 % p, 1]
    return poly, total_rejections


def run(p: int, domain_suffix: str, n_draws: int = 2000):
    """Run the control for one prime. `domain_suffix` distinguishes the two
    replication runs' domain strings (e.g. 'run-20260830')."""
    domain = DOMAIN + "/" + domain_suffix
    histogram = {}
    raw_log = []
    j = 0
    accepted = 0
    total_discards = 0
    while accepted < n_draws:
        poly, rejections_this_draw = draw_quartic(domain, p, j)
        squarefree = pm.is_squarefree(poly, p)
        entry = {
            "draw_index": j,
            "coeffs_b0_b1_b2_b3": poly[:4],
            "modbias_rejections": rejections_this_draw,
            "squarefree": squarefree,
        }
        if not squarefree:
            entry["discarded"] = True
            raw_log.append(entry)
            total_discards += 1
            j += 1
            continue
        factors = pm.distinct_degree_factorization_shape(poly, p)
        label = pm.shape_to_partition_label(factors)
        entry["discarded"] = False
        entry["label"] = label
        raw_log.append(entry)
        histogram[label] = histogram.get(label, 0) + 1
        accepted += 1
        j += 1
    return {
        "prime": p,
        "domain": domain,
        "n_accepted": accepted,
        "n_squarefree_discards": total_discards,
        "histogram": histogram,
        "raw_log": raw_log,
    }
