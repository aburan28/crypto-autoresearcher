"""Independent full-domain reference / verification service for EXP-AUXIN-684adf.

Frozen source: specification.yaml, `arithmetic_definitions.independent_reference`
and `arithmetic_definitions.toy_original_verification`, plus the
`independent_enumeration`, `matched_null`, `inconsistent_known_false`,
`consistent_wrong_target`, `order_invariance`, and
`deliberately_faulty_product_rule` controls.

Independence discipline (binding, do not relax):

  * This module MUST NOT import crt.py, any of its helper functions
    (`fold_congruences`, `canonical_residue`, `modular_inverse`,
    `enumerate_candidates`), or any value crt.py predicted (a candidate set,
    a modulus M, a k0). Every routine below is written from the frozen
    specification text directly, using its own brute-force scan over the
    full residue domain e = 0, ..., n-1. This is a deliberate logic fork,
    not a call-through, so that a bug shared between "production" and
    "reference" cannot hide inside both silently agreeing.
  * The fixture generator's ground truth `x` (and the exponent `k` used to
    construct it) is intentionally allowed to reach this module -- the
    specification explicitly designates the independent verifier (and the
    toy original-target equality service) as one of the only two places
    truth may flow. It must never flow back into crt.py.
  * No group operation, elliptic-curve point, or actual Cheon first-stage
    logic is implemented here. `verify_original_target` computes ordinary
    modular exponentiation scalar equality (`pow(zeta, e, r) == x`), which
    the specification explicitly labels a disclosed scalar-equality
    surrogate, not a measured group operation.
  * No code below executes at import time; only functions/data are defined.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple


def _independent_canonical_residue(a: int, m: int) -> int:
    """Own copy of canonical-residue reduction (not shared with crt.py).

    Deliberately re-derived from the same specification sentence rather than
    imported, so the reference path does not depend on crt.py's
    implementation of the same rule.
    """
    if m <= 0:
        raise ValueError("modulus m must be a positive integer")
    if m == 1:
        return 0
    return a % m


def full_domain_matches(n: int, congruences: Sequence[Tuple[int, int]]) -> List[int]:
    """Brute-force scan e = 0, ..., n-1 and retain exactly those satisfying
    every supplied congruence.

    This is the independent reference set: it does not compute a modulus or
    a folded residue at all, it simply tests every candidate exponent in the
    full domain against every congruence directly. With no congruences
    supplied (the empty system), every e in [0, n) is retained, matching the
    specification's `empty_system` definition (M=1, k0=0, all n exponents).
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    canonical = [(_independent_canonical_residue(a, m), m) for (a, m) in congruences]

    matches: List[int] = []
    for e in range(n):
        ok = True
        for (a, m) in canonical:
            if e % m != a:
                ok = False
                break
        if ok:
            matches.append(e)
    return matches


def is_consistent(n: int, congruences: Sequence[Tuple[int, int]]) -> bool:
    """A system is consistent (by the independent reference) iff its
    full-domain match set is nonempty."""
    return len(full_domain_matches(n, congruences)) > 0


class SetComparison(NamedTuple):
    """Result of comparing a production candidate set against the
    independent reference set."""

    equal: bool
    reference_set: List[int]
    production_set: List[int]
    first_counterexample: Optional[int]
    reference_only: List[int]
    production_only: List[int]


def compare_candidate_sets(
    reference_candidates: Sequence[int], production_candidates: Sequence[int]
) -> SetComparison:
    """Compare two candidate-exponent sets by exact set equality (sorted).

    Per `metrics.primary`: "Exact candidate-set disagreement count and first
    counterexample artifact." This function reports the sorted sets, an
    equality flag, and, when unequal, the first counterexample by ascending
    value plus the full symmetric-difference breakdown so nothing is
    discarded.
    """
    ref_sorted = sorted(reference_candidates)
    prod_sorted = sorted(production_candidates)
    ref_set = set(ref_sorted)
    prod_set = set(prod_sorted)

    reference_only = sorted(ref_set - prod_set)
    production_only = sorted(prod_set - ref_set)
    equal = ref_sorted == prod_sorted

    first_counterexample = None
    if not equal:
        symmetric = sorted(reference_only + production_only)
        first_counterexample = symmetric[0] if symmetric else None

    return SetComparison(
        equal=equal,
        reference_set=ref_sorted,
        production_set=prod_sorted,
        first_counterexample=first_counterexample,
        reference_only=reference_only,
        production_only=production_only,
    )


class OriginalTargetVerification(NamedTuple):
    """Result of the independent toy original-target equality check."""

    match_count: int
    first_match_index: Optional[int]
    scalars: List[int]


def verify_original_target(zeta: int, r: int, candidates: Sequence[int], x: int) -> OriginalTargetVerification:
    """Independently evaluate pow(zeta, e, r) for every candidate exponent
    `e` and compare against fixture truth `x`.

    Per `arithmetic_definitions.toy_original_verification`: "Evaluate all
    candidates, including after a match, and record match count and
    first-match index." This is a disclosed scalar-equality surrogate for
    [candidate]P = Q, not a group-operation measurement, and it is computed
    here independently of any production-side scalar computation.
    """
    scalars = [pow(zeta, e, r) for e in candidates]
    match_indices = [i for i, s in enumerate(scalars) if s == x]
    return OriginalTargetVerification(
        match_count=len(match_indices),
        first_match_index=(match_indices[0] if match_indices else None),
        scalars=scalars,
    )


def faulty_product_modulus(m_values: Sequence[int]) -> int:
    """Deliberately-faulty "product rule" mutant: M_bad = product(m_i), with
    the empty product defined as 1.

    Per `controls.deliberately_faulty_product_rule`: this is intentionally
    wrong whenever the supplied m_i are not pairwise coprime (it overcounts
    the true combined modulus, which is lcm(m_i)), and is used as an
    analytical mutant check inside existing cells, not as an extra
    scientific run. It must never be used to determine actual coverage.
    """
    product = 1
    for m in m_values:
        product *= m
    return product


class ProductMutantCheck(NamedTuple):
    """Outcome of comparing M_bad against the independent reference
    cardinality and n-divisibility."""

    m_bad: int
    reference_cardinality: int
    n: int
    expected_cardinality_if_m_bad_correct: Optional[int]
    mutant_detected: bool
    detection_reason: str


def check_product_rule_mutant(n: int, m_values: Sequence[int], reference_candidates: Sequence[int]) -> ProductMutantCheck:
    """Detect whether the faulty product-of-moduli rule would have claimed a
    different (wrong) coverage than the independent reference cardinality
    actually observed.

    The mutant is "detected" (i.e. exposed as wrong) when M_bad does not
    divide n, or when n // M_bad (its claimed candidate count, when
    M_bad divides n) disagrees with the independent reference's actual
    candidate count. Per the specification this must happen in exactly
    (100+240)*5*3 = 5100 cells (panels P02, P03, P04, P07, P11 -- i.e. every
    panel whose supplied m_i are not all pairwise coprime with M == lcm) and
    must NOT happen in the other seven positive panels.
    """
    m_bad = faulty_product_modulus(m_values)
    ref_card = len(reference_candidates)

    if m_bad <= 0:
        return ProductMutantCheck(
            m_bad=m_bad,
            reference_cardinality=ref_card,
            n=n,
            expected_cardinality_if_m_bad_correct=None,
            mutant_detected=True,
            detection_reason="M_bad is non-positive; cannot represent a modulus",
        )

    if n % m_bad != 0:
        return ProductMutantCheck(
            m_bad=m_bad,
            reference_cardinality=ref_card,
            n=n,
            expected_cardinality_if_m_bad_correct=None,
            mutant_detected=True,
            detection_reason="M_bad does not divide n",
        )

    claimed_count = n // m_bad
    if claimed_count != ref_card:
        return ProductMutantCheck(
            m_bad=m_bad,
            reference_cardinality=ref_card,
            n=n,
            expected_cardinality_if_m_bad_correct=claimed_count,
            mutant_detected=True,
            detection_reason="M_bad-implied candidate count disagrees with independent reference cardinality",
        )

    return ProductMutantCheck(
        m_bad=m_bad,
        reference_cardinality=ref_card,
        n=n,
        expected_cardinality_if_m_bad_correct=claimed_count,
        mutant_detected=False,
        detection_reason="M_bad agrees with independent reference on this cell (expected for coprime-modulus panels)",
    )


def order_invariance_check(results: Sequence[SetComparison]) -> Dict[str, object]:
    """Compare the independent reference outcome across order variants of the
    same unpermuted cell.

    Per `controls.order_invariance`: "All three orders have identical
    canonical coset or rejection outcome for the same unpermuted cell."
    `results` is expected to be the SetComparison (or, for inconsistent
    cells, an equivalent reference-only outcome) for each order variant of
    one fixed cell, in variant order. This function only inspects the
    reference sets (never a production value) to state whether the
    reference agrees across variants; comparing production outputs across
    variants is a separate, later scientific step.
    """
    if not results:
        return {"invariant": True, "reference_sets": []}
    reference_sets = [tuple(r.reference_set) for r in results]
    invariant = all(s == reference_sets[0] for s in reference_sets)
    return {"invariant": invariant, "reference_sets": [list(s) for s in reference_sets]}
