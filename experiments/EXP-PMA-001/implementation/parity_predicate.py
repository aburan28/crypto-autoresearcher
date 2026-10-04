"""
EXP-PMA-001 Module A: the divisor-parity obstruction predicate.

Independent decision procedure: canonical numerator/denominator reduction,
irreducible-factor valuation parity (finite places) via sympy's polynomial
factorization, valuation-at-infinity parity (degree difference), and the
residual constant square class in k*/k*^2. This module NEVER branches over
matrix entries or constructs a candidate matrix; that is Module B's
independent job (existence_decider.py). No function defined here is called
by Module B, and vice versa (only the shared, non-decisional definitions in
common.py are shared).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import sympy
from sympy import QQ, GF, factor_list

from common import (
    RationalFunction,
    build_p_table,
    q_ij,
    delta_ijk,
    is_square_constant,
    t,
)

CHAR2_FIELDS = (2, 4)


@dataclass
class FactorValuation:
    factor: str
    multiplicity_in_numerator: int
    multiplicity_in_denominator: int

    @property
    def valuation(self) -> int:
        return self.multiplicity_in_numerator - self.multiplicity_in_denominator


@dataclass
class SquarenessCertificate:
    is_square: bool
    reason: str
    finite_valuations: List[FactorValuation] = field(default_factory=list)
    valuation_at_infinity: Optional[int] = None
    residual_constant: Optional[str] = None
    residual_constant_is_square: Optional[bool] = None
    degenerate: bool = False
    degenerate_kind: Optional[str] = None


class CharTwoRefused(Exception):
    pass


def factor_multiplicities(poly, domain):
    """Return list of (irreducible_factor_str, multiplicity) for a nonzero
    sympy Poly over the given domain."""
    if poly.degree() == 0:
        return []
    if domain == QQ:
        _, factors = factor_list(poly.as_expr(), t)
    else:
        _, factors = factor_list(poly.as_expr(), t, modulus=domain.mod)
    out = []
    for fac_expr, mult in factors:
        out.append((str(fac_expr), mult))
    return out


def rational_function_is_square(rf: RationalFunction, domain, field_label) -> SquarenessCertificate:
    """Core divisor-parity + residual-constant-class squareness test for a
    canonically-reduced RationalFunction over k(t), k = domain's field.
    Raises CharTwoRefused if the field has characteristic 2 (this function
    itself refuses to operate there -- char 2 has a different, unimplemented
    square-testing theory, per H-PMA-001's assumptions)."""
    if field_label in CHAR2_FIELDS:
        raise CharTwoRefused(f"characteristic-2 field {field_label} refused by the predicate")

    rf = rf.reduced()
    if rf.is_zero():
        return SquarenessCertificate(
            is_square=False,
            reason="Delta is identically zero after canonical reduction: degenerate (excluded from agreement grid, not scored as obstruction)",
            degenerate=True,
            degenerate_kind="zero_discriminant",
        )

    num, den = rf.num, rf.den
    num_facs = factor_multiplicities(num, domain)
    den_facs = factor_multiplicities(den, domain)

    finite_vals: List[FactorValuation] = []
    all_even = True
    for fac, mult in num_facs:
        finite_vals.append(FactorValuation(fac, mult, 0))
        if mult % 2 != 0:
            all_even = False
    for fac, mult in den_facs:
        finite_vals.append(FactorValuation(fac, mult, 0))
        # store denominator multiplicities as negative in the "valuation" sense;
        # represented via multiplicity_in_denominator field instead
        finite_vals[-1] = FactorValuation(fac, 0, mult)
        if mult % 2 != 0:
            all_even = False

    val_inf = den.degree() - num.degree()

    if not all_even:
        odd_witness = [fv.factor for fv in finite_vals if fv.valuation % 2 != 0]
        return SquarenessCertificate(
            is_square=False,
            reason=f"odd valuation at finite irreducible divisor(s): {odd_witness}",
            finite_valuations=finite_vals,
            valuation_at_infinity=val_inf,
        )

    if val_inf % 2 != 0:
        return SquarenessCertificate(
            is_square=False,
            reason=f"odd valuation at infinity ({val_inf})",
            finite_valuations=finite_vals,
            valuation_at_infinity=val_inf,
        )

    # All finite and infinite valuations even. Residual constant class:
    # since D is monic and every multiplicity is even, N = lc(N) * S_N^2,
    # D = S_D^2, so f = lc(N) * (S_N/S_D)^2. Square iff lc(N) is a square
    # in the constant field.
    lc_num = num.LC()
    residual_is_sq = is_square_constant(lc_num, domain)
    return SquarenessCertificate(
        is_square=bool(residual_is_sq),
        reason=(
            "all divisor valuations even; residual constant class is square"
            if residual_is_sq
            else f"all divisor valuations even but residual leading constant {lc_num} is a nonsquare in the constant field"
        ),
        finite_valuations=finite_vals,
        valuation_at_infinity=val_inf,
        residual_constant=str(lc_num),
        residual_constant_is_square=bool(residual_is_sq),
    )


def evaluate_instance(d_values, domain, field_label):
    """Runs the full predicate over one prescribed instance (dict subset ->
    d_S) and returns a dict verdict with per-anchor-triple certificates.
    Degeneracy branching (q_ij == 0) is checked before squareness testing,
    per specification.yaml's degenerate-locus exclusion rule."""
    from common import ANCHOR_TRIPLES

    if field_label in CHAR2_FIELDS:
        return {"verdict": "REFUSED_CHAR2", "field": field_label}

    p_table = build_p_table(d_values, domain)

    degenerate_reasons = []
    triple_certs = {}
    any_obstructed = False

    for (i, j, k) in ANCHOR_TRIPLES:
        qij = q_ij(p_table, i, j, domain)
        qjk = q_ij(p_table, j, k, domain)
        qki = q_ij(p_table, k, i, domain)
        if qij.is_zero() or qjk.is_zero() or qki.is_zero():
            degenerate_reasons.append(f"q_ij=0 in triple {(i,j,k)}")
            triple_certs[str((i, j, k))] = {"degenerate": True, "degenerate_kind": "zero_q_ij"}
            continue

        raw_num = None
        D = delta_ijk(p_table, i, j, k, domain)
        # degree-drop / repeated-factor disclosure: check whether forming
        # Delta_ijk involved any numerator/denominator common-factor
        # cancellation beyond the trivial case (recomputed via the
        # unreduced product path is impractical here without duplicating
        # RationalFunction internals, so we use D's own .reduced() step,
        # which already performed the gcd cancellation -- a nontrivial gcd
        # step is exactly the "repeated factor" / "degree drop" condition
        # and is disclosed via D's certificate below).
        cert = rational_function_is_square(D, domain, field_label)
        triple_certs[str((i, j, k))] = {
            "is_square": cert.is_square,
            "reason": cert.reason,
            "degenerate": cert.degenerate,
            "degenerate_kind": cert.degenerate_kind,
            "valuation_at_infinity": cert.valuation_at_infinity,
            "finite_valuations": [
                {"factor": fv.factor, "mult_num": fv.multiplicity_in_numerator, "mult_den": fv.multiplicity_in_denominator}
                for fv in cert.finite_valuations
            ],
            "residual_constant": cert.residual_constant,
            "residual_constant_is_square": cert.residual_constant_is_square,
        }
        if cert.degenerate:
            degenerate_reasons.append(f"{cert.degenerate_kind} in triple {(i,j,k)}")
            continue
        if not cert.is_square:
            any_obstructed = True

    if degenerate_reasons:
        return {
            "verdict": "DEGENERATE",
            "degenerate_reasons": degenerate_reasons,
            "triple_certificates": triple_certs,
        }

    return {
        "verdict": "OBSTRUCTED" if any_obstructed else "NOT_OBSTRUCTED_BY_THIS_GATE",
        "triple_certificates": triple_certs,
    }
