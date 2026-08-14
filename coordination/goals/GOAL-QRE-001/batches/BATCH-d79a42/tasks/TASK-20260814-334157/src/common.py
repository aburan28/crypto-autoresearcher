"""Shared helpers for TASK-20260814-334157.

Everything numerical here (prime ladders, exact rational interpolation, the
deterministic curve point) is IMPORTED from BATCH-973b49's run_counts.py rather
than re-implemented, so the instrument is the inherited one.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_B1 = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))),
    "BATCH-973b49", "tasks", "TASK-20260813-c99166", "src")
for _p in (_HERE, _B1):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from run_counts import (is_prime, primes_of_bitlength, any_point,      # noqa: E402,F401
                        interp_exact, poly_eval, fmt_poly, coeff_list)

TASK = "TASK-20260814-334157"
GOAL = "GOAL-QRE-001"
BATCH = "BATCH-d79a42"
LANE = "A"
SEED = 20260814
T_PER_TOFFOLI = 7

# PREREGISTRATION.md section 3.1
INV_LADDER = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20]
INV_HOLDOUT = [22, 24, 28, 32]
EC_LADDER = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
EC_HOLDOUT = [15, 16, 20, 24, 32]
CLOSED_FORM_ONLY_N = 256

PROHIBITION = (
    "This artifact states only what these circuits cost, and what a classical "
    "simulation of them returned, under the frozen convention of "
    "PREREGISTRATION.md. It contains no date, timeline, arrival probability, "
    "forecast, migration guidance or policy statement.")

BLIND_STATEMENT = (
    "Produced under an explicit instruction to work BLIND to specific "
    "published reversible modular inverters, by design and by declaration. "
    "Prior art on reversible modular inversion is filed in this program's own "
    "knowledge corpus (the batch queue's filed_sources_inventory names "
    "KN-LIT-771 and KN-LIT-1882) and was deliberately not read while deriving "
    "or counting the construction reported here. This is an independence "
    "condition for GOAL-QRE-001 completion criterion 2, not a claim that no "
    "prior art exists; see CORR-20260813-1a06db.")

CONVENTION_REF = (
    "PREREGISTRATION.md of TASK-20260814-e95462 (frozen at repository commit "
    "b3f6daddb0eb2c6e00a2acc470ddce386670ef0c, committed by "
    "TASK-20260814-19d2b9 at e2ea19643e45e0453df9d58b244e8d16b5d42ee3 before "
    "this task ran), which inherits BATCH-973b49's convention unchanged.")


def prime_pair(n):
    """Two primes of bitlength n with the lowest and the highest Hamming
    weight of p-2 among the 40 largest such primes; deterministic. This is
    PREREGISTRATION clause 3.2's adversarial pair, chosen so that any residual
    dependence of the count on the structure of p is exposed rather than
    averaged away."""
    ps = primes_of_bitlength(n, 40)
    ps.sort(key=lambda q: (bin(q - 2).count("1"), -q))
    lo, hi = ps[0], ps[-1]
    return [(lo, "low_weight"), (hi, "high_weight")] if lo != hi else \
           [(lo, "low_weight")]


def bw(p):
    e = p - 2
    return e.bit_length(), bin(e).count("1")


def fermat_pointadd_closed_form(n, p):
    """EV-QRE-45dfe1's frozen baseline closed form, transcribed from
    BATCH-973b49's counts.json field
    circuit_b_ec_point_addition.toffoli_closed_form_in_n_b_w:
        (8(b+w-2)+5)(20n^2+10n-8) + 50(n+1) + 2n.
    It is re-checked against a live enumeration of the inherited builder at
    every width in baseline_comparison.json, so it is used here as a
    convenience, never as an unchecked citation."""
    b, w = bw(p)
    return (8 * (b + w - 2) + 5) * (20 * n * n + 10 * n - 8) + 50 * (n + 1) + 2 * n
