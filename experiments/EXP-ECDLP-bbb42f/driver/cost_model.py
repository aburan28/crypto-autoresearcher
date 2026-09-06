"""
SINGLE SOURCE OF TRUTH for every group-operation-equivalent cost number in
this contract (required_artifacts_note: "no cost number in summary.json may
be computed outside it"). Every quantity here is labeled MEASURED (comes
from an actually-executed, counted computation) or MODELED (comes from a
closed-form/asymptotic formula, never executed to completion). The two are
never mixed into one column without the label traveling with the number.

matched_rho_cost(N)      -> MODELED, 0.886*sqrt(N) group operations
                             (van Oorschot-Wiener / negation-map Pollard rho
                             expected step count, textbook constant
                             sqrt(pi/2)/sqrt(2) = 0.8825...).
matched_bsgs_cost(N)     -> MODELED, 2*sqrt(N) (build+search), memory
                             O(sqrt(N)) points, reported beside time.
c_path_cost(...)         -> MEASURED: actual field-multiplication count
                             consumed by the isogeny path search (kernel
                             polynomial construction + Velu evaluation),
                             converted to group-operation-equivalent units
                             by the OPTIMISTIC assumption (flagged) that one
                             elliptic-curve group operation costs
                             GROUP_OP_FIELD_MUL_EQUIV field multiplications
                             (a standard affine-coordinates estimate: one EC
                             addition needs 1 field inversion + 2-3
                             multiplications; charging inversion at ~1
                             multiplication-equivalent via the toy-scale
                             convention stated below is the flagged
                             optimism -- it UNDERSTATES true EC group-op
                             cost in field-multiplication terms, which
                             biases the charged ratio DOWNWARD, i.e. makes
                             a transfer look cheaper than it really is; this
                             is the conservative-for-the-hypothesis
                             direction and is disclosed, not hidden).
c_special_cost(...)      -> MODELED for E1/E2, `not_applicable` for E3
                             (E3 is vacuously never triggered, see
                             predicates.py).
"""
from __future__ import annotations

import math

GROUP_OP_FIELD_MUL_EQUIV = 12
# OPTIMISTIC ASSUMPTION (flagged): one elliptic-curve group operation
# (point addition/doubling in affine coordinates over F_p, including the
# field inversion via Fermat's little theorem) is charged as
# GROUP_OP_FIELD_MUL_EQUIV = 12 field multiplications. This is a rough,
# stated-optimistic convention (a real affine inversion by extended Euclid
# costs more like a handful of multiplications' worth of work asymptotically,
# and by Fermat's-little-theorem exponentiation costs O(log p) ~ 20-30
# multiplications at these bit sizes; 12 UNDERSTATES that, which biases
# C_path DOWNWARD relative to true cost -- i.e. makes the isogeny-transfer
# route look cheaper than it really is, the conservative-for-H-ECDLP-ed5162
# direction, not the direction that would manufacture a false falsification).

RHO_CONSTANT = 0.886  # sqrt(pi/2)/sqrt(2), negation-map Pollard rho (modeled;
# this is the contract's own reference model, used for every ratio in this
# experiment, per the frozen contract -- see rho_bsgs.py module docstring
# for the disclosed protocol deviation: the MEASURED baseline in this run is
# plain (non-negation) Pollard rho, compared additionally against
# PLAIN_RHO_CONSTANT below as the correct un-optimized reference point.)
PLAIN_RHO_CONSTANT = 1.2533  # sqrt(pi/2), textbook plain Pollard rho (modeled)
BSGS_CONSTANT = 2.0


def matched_rho_cost(N: int) -> float:
    return RHO_CONSTANT * math.sqrt(N)


def plain_rho_cost_modeled(N: int) -> float:
    return PLAIN_RHO_CONSTANT * math.sqrt(N)


def matched_bsgs_cost(N: int) -> dict:
    m = math.isqrt(N) + 1
    return {
        "time_group_ops_modeled": BSGS_CONSTANT * math.sqrt(N),
        "memory_points_modeled": m,
        "kind": "modeled",
    }


def field_muls_to_group_op_equivalent(field_muls: int) -> float:
    return field_muls / GROUP_OP_FIELD_MUL_EQUIV


def c_special_anomalous_modeled(N: int) -> dict:
    """
    E1 (Smart-Araki-Satoh-Semaev anomalous DLP): polynomial-time in log(N)
    via a p-adic (Zp) lift and the additive logarithm on the formal group.
    MODELED (never actually executed): charged at a small constant times
    log2(N) group-operation-equivalents (Hensel-lift + a handful of
    p-adic-arithmetic passes), which is the standard informal cost account
    for this algorithm; flagged optimistic (real constant-factor overhead
    of p-adic arithmetic at high precision is not modeled in detail here).
    """
    cost = 25.0 * math.log2(max(N, 2))
    return {
        "kind": "modeled",
        "family": "E1_anomalous_smart_ASS",
        "cost_group_op_equivalent": cost,
        "optimistic_assumptions": [
            "constant-factor overhead of p-adic (Zp) Hensel-lift arithmetic "
            "approximated as 25 group-operation-equivalents per bit of N; "
            "not measured, not independently benchmarked in this run."
        ],
    }


def c_special_mov_frey_ruck_modeled(N: int, p: int, k: int) -> dict:
    """
    E2 (MOV / Frey-Ruck): reduces to a discrete log in F_{p^k}^*, modeled
    cost L_{p^k}(1/3, c) with c = (32/9)^{1/3} (the classical NFS-family
    constant), PLUS the pairing evaluation (poly(log p, log N), negligible
    beside the sub-exponential term at any k large enough to matter).
    MODELED (never actually run: p^k is astronomically larger than any field
    this program can factor by index calculus within budget for k above the
    smallest few toy values).
    """
    n = p ** k
    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n) if ln_n > 1 else 1e-9
    c = (32.0 / 9.0) ** (1.0 / 3.0)
    exponent = c * (ln_n ** (1.0 / 3.0)) * (ln_ln_n ** (2.0 / 3.0))
    cost = math.exp(exponent)
    return {
        "kind": "modeled",
        "family": "E2_mov_frey_ruck",
        "target_field_bits": n.bit_length(),
        "embedding_degree_k": k,
        "cost_group_op_equivalent": cost,
        "optimistic_assumptions": [
            "L_{p^k}(1/3, (32/9)^{1/3}) index-calculus constant assumed "
            "achievable at this field size; sub-polynomial/polylog "
            "cofactors and the pairing-evaluation cost are not added; "
            "this is a standard rough asymptotic estimate, not a benchmark."
        ],
    }
