"""
Independent second count predictor for EXP-CRYPTO-9225d2.

Authored from experiments/EXP-CRYPTO-9225d2/specification.yaml ALONE. No other
file in this repository was read while writing this module. See
independence-report-v2.yaml for the required attestation.

specification.arithmetic.checker.count_predictor: "Independently implement
the declared branch/formula cost recurrence from public inputs; do not
consume measured counters or producer operation traces until the predictor
report is frozen." Accordingly every function below is a pure formula over
caller-supplied *structural* parameters (bit counts, branch labels, a curve's
`a` coefficient, m/d/N model parameters) — never a real scalar, curve point,
or measured counter. No function in this file is ever called anywhere in this
module; see independence-report-v2.yaml's no_scientific_run_attestation.

This module intentionally recomputes the cost recurrence from the spec text
independently of any producer implementation; the values below are read
directly off specification.arithmetic (rescale_finite, common_z_formula,
doubling.specializations, normalization, planted.exact_count_identity),
specification.goe_ruler.formula, and specification.model_256.
"""

from __future__ import annotations

import decimal
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, List, Literal, Optional


# ---------------------------------------------------------------------------
# Operation-count algebra: M (multiplications), S (squarings), I (inversions).
# specification.arithmetic.field_api: M, S, I are each separately counted
# field API operations; "no operand-is-one optimization removes a declared
# M/S call."
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OpCount:
    M: int = 0
    S: int = 0
    I: int = 0

    def __add__(self, other: "OpCount") -> "OpCount":
        return OpCount(self.M + other.M, self.S + other.S, self.I + other.I)

    def scaled(self, n: int) -> "OpCount":
        return OpCount(self.M * n, self.S * n, self.I * n)


# specification.addition.rescale_finite: "Compute z1sq=S(Z1),z2sq=S(Z2),
# z1cube=M(z1sq,Z1),z2cube=M(z2sq,Z2),U1=M(X1,z2sq),V1=M(Y1,z2cube),
# U2=M(X2,z1sq),V2=M(Y2,z1cube),Z=M(Z1,Z2). These seven M and two S are
# charged even for a coordinate equal to one."
RESCALE_FINITE = OpCount(M=7, S=2)

# specification.addition.common_z_formula: "Generic common-Z work is five M
# and two S; generic full ADD is twelve M and four S before output
# normalization."
COMMON_Z_GENERIC = OpCount(M=5, S=2)
ADD_GENERIC_FULL = OpCount(M=12, S=4)
assert ADD_GENERIC_FULL == RESCALE_FINITE + COMMON_Z_GENERIC, (
    "rescale_finite (7M+2S) + common_z_formula generic (5M+2S) must equal "
    "the spec's stated generic full ADD (12M+4S)"
)

# specification.doubling.specializations: "For secp256k1 a=0 omit only ZZ^2,
# retaining ZZ for Z3, giving one M and seven S. For the reduced rho curves
# a=1 compute Z4=S(ZZ),W=3*XX+Z4, giving one M and eight S."
DOUBLE_A0 = OpCount(M=1, S=7)
DOUBLE_A1 = OpCount(M=1, S=8)

# Branch/copy-only paths: no field calls charged.
# specification.addition.identity: "count the branch and copies but no field
# calls." specification.doubling.exceptional: "O returns O; finite Y=0
# returns O before polynomial calls. Count branch/copy work." The
# exceptional_after_rescaling "return O" branch still charges the rescale
# cost (see EXCEPTIONAL_RETURN_O below), it is only the DOUBLING/ADD-identity
# branches themselves that are field-call-free.
BRANCH_ONLY = OpCount()

# specification.addition.exceptional_after_rescaling: "If U1=U2 and V1=-V2,
# return O, retaining the rescale cost." I.e. RESCALE_FINITE with no
# common-Z work.
EXCEPTIONAL_RETURN_O = RESCALE_FINITE

# specification.normalization: "For finite output compute zi=I(Z),z2=S(zi),
# z3=M(z2,zi),x=M(X,z2),y=M(Y,z3), including Z=1. Charge three M, one S, one
# I; O has no inversion."
NORMALIZE = OpCount(M=3, S=1, I=1)
NORMALIZE_IDENTITY = OpCount()  # "O has no inversion."


def double_cost(a: int, exceptional: bool) -> OpCount:
    """Cost of one DOUBLE(R) call.

    `exceptional` covers both specification.doubling.exceptional branches:
    R=O, or R finite with Y=0. Both return O with branch/copy work only.
    """
    if exceptional:
        return BRANCH_ONLY
    if a == 0:
        return DOUBLE_A0
    if a == 1:
        return DOUBLE_A1
    raise ValueError(
        f"doubling.specializations only defines a in {{0, 1}} per the "
        f"specification; a={a} has no declared formula cost here"
    )


AddBranch = Literal["identity", "generic", "exceptional_double", "exceptional_return_O"]


def add_cost(branch: AddBranch, a: int = 0, double_exceptional: bool = False) -> OpCount:
    """Cost of one ADD(P, Q) call, selected by which specification.addition
    branch it takes.

    branch:
      "identity"             -- one operand is O; addition.identity.
      "generic"               -- neither operand O, distinct-x case;
                                  rescale_finite + common_z_formula generic.
      "exceptional_double"    -- same-x, same-y after rescaling: DOUBLE the
                                  first point, "retaining the rescale cost."
      "exceptional_return_O"  -- same-x, opposite-y after rescaling: return
                                  O, "retaining the rescale cost."
    """
    if branch == "identity":
        return BRANCH_ONLY
    if branch == "generic":
        return ADD_GENERIC_FULL
    if branch == "exceptional_return_O":
        return EXCEPTIONAL_RETURN_O
    if branch == "exceptional_double":
        return RESCALE_FINITE + double_cost(a, double_exceptional)
    raise ValueError(f"unrecognised ADD branch: {branch!r}")


@dataclass(frozen=True)
class ScalarBitStep:
    """One bit of specification.arithmetic.scalar_algorithm's loop:
    "for every bit set R=DOUBLE(R), then if bit=1 set R=ADD(R,(Gx,Gy,1))."

    This dataclass carries no real scalar/curve data; it is the caller's
    declaration of which branch each DOUBLE/ADD call would take, to be
    supplied later from an actual traced run -- never fabricated or
    evaluated here.
    """

    double_exceptional: bool
    bit_is_one: bool
    add_branch: Optional[AddBranch] = None
    add_double_exceptional: bool = False


def scalar_multiply_reference_cost(steps: Iterable[ScalarBitStep], a: int = 0,
                                    final_result_is_identity: bool = False) -> OpCount:
    """Sum the reference (unplanted) M/S/I cost of one full scalar multiply.

    specification.arithmetic.scalar_algorithm: "Start R=O; for every bit set
    R=DOUBLE(R), then if bit=1 set R=ADD(R,(Gx,Gy,1)). Normalize the final R
    once." The normalize() charge is therefore added EXACTLY ONCE, after the
    bit loop, regardless of how many bits/branches were processed -- see
    independence-report-v2.yaml's normalize_composition_reasoning for the
    exact textual derivation.
    """
    total = OpCount()
    for step in steps:
        total = total + double_cost(a, step.double_exceptional)
        if step.bit_is_one:
            if step.add_branch is None:
                raise ValueError("bit_is_one=True steps must declare add_branch")
            total = total + add_cost(step.add_branch, a=a,
                                      double_exceptional=step.add_double_exceptional)
    total = total + (NORMALIZE_IDENTITY if final_result_is_identity else NORMALIZE)
    return total


def apply_planted(reference: OpCount) -> OpCount:
    """specification.arithmetic.planted.exact_count_identity:
    "M_planted=2*M_reference, S_planted=S_reference, I_planted=I_reference
    for the same input and branch trace."

    Because `reference` (built by scalar_multiply_reference_cost) already
    includes the single normalize() charge's 3 M's as top-level M(a,b) calls,
    doubling M here doubles those 3 normalize-M's along with every other M in
    the trace -- i.e. under the planted routine, 3 of the doubled M's belong
    to the once-per-cell normalize() call, exactly as required. No separate
    "normalize twice" step is introduced; normalize() is still charged
    exactly once per scalar-multiply cell, its M count is simply part of what
    planted's top-level M(a,b) duplication doubles.
    """
    return OpCount(M=2 * reference.M, S=reference.S, I=reference.I)


def planted_expected_factor(reference: OpCount) -> Fraction:
    """specification.arithmetic.planted.expected_factor:
    (2*M_reference+S_reference+100*I_reference)/(M_reference+S_reference+100*I_reference)
    """
    m, s, i = reference.M, reference.S, reference.I
    denom = m + s + 100 * i
    if denom == 0:
        raise ValueError("reference op count has zero weighted total; factor undefined")
    return Fraction(2 * m + s + 100 * i, denom)


# ---------------------------------------------------------------------------
# specification.goe_ruler.formula: raw_GOE=(M+S+100*I)/16, "exact
# representation: Integer numerator and denominator 16; compare counts and
# ratios as exact rationals before rendering decimals."
# ---------------------------------------------------------------------------


def raw_GOE(op: OpCount) -> Fraction:
    return Fraction(op.M + op.S + 100 * op.I, 16)


# ---------------------------------------------------------------------------
# specification.model_256: the affine-normalized rho-step cost recurrence,
# structurally distinct from the Jacobian scalar-multiply recurrence above.
#
# "Use the exact affine-normalized rho step, not scalar-multiplication GOE.
# Generic addition is 15M+5S+I and a=0 doubling is 4M+8S+I. Under equal
# branch probabilities the generic mean is (34M+18S+3I)/3, hence 22/3 GOE per
# transition."
# ---------------------------------------------------------------------------

RHO_STEP_ADD_GENERIC = OpCount(M=15, S=5, I=1)
RHO_STEP_DOUBLE_A0 = OpCount(M=4, S=8, I=1)


def rho_generic_mean_transition_cost() -> Fraction:
    """(34M+18S+3I)/3, derived from two ADD-type branches (transition
    branches 0 and 2, per specification.rho.transition.branches) and one
    DOUBLE-type branch (branch 1), each equally likely:
        2*(15M+5S+I) + 1*(4M+8S+I) = 34M+18S+3I, divided by 3 branches.
    Returned as a triple of exact Fraction components (M, S, I) per branch,
    not yet weighted into GOE units.
    """
    total = RHO_STEP_ADD_GENERIC.scaled(2) + RHO_STEP_DOUBLE_A0
    assert total == OpCount(M=34, S=18, I=3), (
        "generic rho transition mean numerator must equal the spec's stated "
        "34M+18S+3I"
    )
    return total


def rho_generic_mean_transition_GOE() -> Fraction:
    """22/3 GOE per transition, per specification.model_256.arithmetic."""
    total = rho_generic_mean_transition_cost()
    goe = Fraction(total.M + total.S + 100 * total.I, 3 * 16)
    assert goe == Fraction(22, 3)
    return goe


# ---------------------------------------------------------------------------
# specification.model_256.formulas / specification.rho.model:
#   C = sqrt(pi*N/2)
#   L = C + m*2^d               (total transitions)
#   R = C/m + 2^d                (parallel rounds)
#   E = theta*L, theta = 2^-d    (expected stored endpoints)
#   modeled slot count = least power of two >= max(1024, 2*ceil(E))
#   table_bytes = slots * 256
#   feasible iff table_bytes <= 8 GiB
#
# These are pure formulas over caller-supplied N, m, d; they are never
# evaluated against secp256k1's real order or any real rung's N within this
# implementation-review task.
# ---------------------------------------------------------------------------

# 100-digit pi constant used only to seed a Decimal sqrt computation; not
# executed/evaluated anywhere in this file.
_PI_100 = decimal.Decimal(
    "3.14159265358979323846264338327950288419716939937510582097494459230781"
    "640628620899862803482534211706798"
)


def C_sqrt_piN_over_2(N: int, precision: int = 50) -> decimal.Decimal:
    """C = sqrt(pi*N/2) at the requested decimal precision.

    N is expected to be a group order supplied by the caller (e.g. secp256k1's
    order, or a reduced rung's N); this function performs no lookup and
    fabricates no curve.
    """
    if N <= 0:
        raise ValueError("N must be a positive group order")
    with decimal.localcontext() as ctx:
        ctx.prec = precision + 10
        pi = +_PI_100  # round to context precision
        value = (pi * decimal.Decimal(N) / 2).sqrt()
        return +value  # round to requested-ish precision in caller context


def total_transitions_prediction(N: int, m: int, d: int, precision: int = 50) -> decimal.Decimal:
    """L = C + m*2^d, i.e. C + m/theta with theta=2^-d."""
    C = C_sqrt_piN_over_2(N, precision)
    return C + decimal.Decimal(m) * (decimal.Decimal(2) ** d)


def parallel_rounds_prediction(N: int, m: int, d: int, precision: int = 50) -> decimal.Decimal:
    """R = C/m + 2^d, i.e. C/m + 1/theta with theta=2^-d."""
    C = C_sqrt_piN_over_2(N, precision)
    return C / decimal.Decimal(m) + (decimal.Decimal(2) ** d)


def expected_stored_endpoints(N: int, m: int, d: int, precision: int = 50) -> decimal.Decimal:
    """E = theta*L."""
    theta = decimal.Decimal(2) ** (-d)
    L = total_transitions_prediction(N, m, d, precision)
    return theta * L


def modeled_slot_count(expected_endpoints: decimal.Decimal) -> int:
    """Least power of two >= max(1024, 2*ceil(E))."""
    target = max(1024, 2 * math.ceil(expected_endpoints))
    slots = 1
    while slots < target:
        slots *= 2
    return slots


def table_bytes(slots: int, slot_bytes: int = 256) -> int:
    """specification.rho.table.slot_bytes: 256."""
    return slots * slot_bytes


def is_feasible(table_bytes_value: int, memory_cap_bytes: int = 8 * (2 ** 30)) -> bool:
    """specification.model_256.feasibility: "Mark infeasible ... whenever
    even table bytes exceed it."
    """
    return table_bytes_value <= memory_cap_bytes


def transition_GOE_total(N: int, m: int, d: int, precision: int = 50) -> decimal.Decimal:
    """Modeled total transition GOE = L * 22/3, per specification.model_256.
    cost_rows: "Report transition GOE L*22/3 ..."

    Returned as Decimal (not Fraction) because L already depends on the
    irrational C=sqrt(pi*N/2); the 22/3 weighting itself remains an exact
    rational and is applied as such via Fraction->Decimal conversion at the
    configured precision.
    """
    L = total_transitions_prediction(N, m, d, precision)
    weight = decimal.Decimal(22) / decimal.Decimal(3)
    return L * weight


def endpoint_communication_bytes(expected_endpoints: decimal.Decimal) -> decimal.Decimal:
    """specification.model_256.cost_rows: "endpoint communication 256*E
    payload bytes plus an explicitly unknown transport overhead."
    """
    return decimal.Decimal(256) * expected_endpoints
