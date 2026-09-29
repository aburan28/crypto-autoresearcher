"""Fixture panel definitions, generation, and input gating for EXP-AUXIN-684adf.

Frozen source: specification.yaml sections `arithmetic_definitions`,
`input_supply`, `positive_panels`, `inconsistency_panels`,
`wrong_target_panels`, `malformed_fixtures`, `zero_boundary`, and
`ordering_and_counts`. Every literal panel, family, mutation, and count
below is transcribed from that frozen text; nothing here expands or
narrows the declared scope.

Truth-separation discipline (binding, do not relax):

  * Fixture truth (`k`, `x`) is produced and held by the *generator*
    functions in this module. It is deliberately kept on a separate return
    channel from the "production input" (the ordered `(a, m)` congruences
    and `n`) that would be handed to `crt.fold_congruences`. Nothing in
    this module passes `k`/`x` into a call that also reaches crt.py's
    combiner; the combiner never receives them via this module.
  * The only consumers of `k`/`x` permitted by the specification are:
    (1) this generator itself, (2) the malformed/boundary input gate
    (which needs to know the target mode, not the combiner logic), and
    (3) the independent verification / toy-original-target-equality
    service in reference.py. crt.py never sees them.
  * No code below executes at import time. Panel/case tables here are
    plain data literals (tuples/dicts of small integers), not computed
    arithmetic; the functions that perform primality checks, primitive
    element search, or fixture-truth construction are defined but not
    invoked by importing this module.
  * Zero scientific execution occurs by writing this file: no fixture is
    evaluated, no primitive element is actually searched for, and no CRT
    cell is folded as part of producing this implementation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# arithmetic_definitions.primes
# ---------------------------------------------------------------------------

PRIMES: Tuple[Dict[str, object], ...] = (
    {
        "r": 101,
        "n": 100,
        "factorization": ((2, 2), (5, 2)),  # 2^2 * 5^2 = 100
    },
    {
        "r": 241,
        "n": 240,
        "factorization": ((2, 4), (3, 1), (5, 1)),  # 2^4 * 3 * 5 = 240
    },
)


def is_prime_trial_division(r: int) -> bool:
    """Deterministic trial division through isqrt(r).

    Per `arithmetic_definitions.primality`. Not called at import time.
    """
    if r < 2:
        return False
    if r in (2, 3):
        return True
    if r % 2 == 0:
        return False
    limit = math.isqrt(r)
    d = 3
    while d <= limit:
        if r % d == 0:
            return False
        d += 2
    return True


def verify_factorization(n: int, factorization: Sequence[Tuple[int, int]]) -> bool:
    """Verify every declared prime factor is prime and the powered product
    equals n exactly (per `arithmetic_definitions.primality`)."""
    product = 1
    for prime, exponent in factorization:
        if not is_prime_trial_division(prime):
            return False
        product *= prime ** exponent
    return product == n


def find_primitive_element(r: int, n: int, distinct_prime_factors: Sequence[int]) -> int:
    """Select the least integer zeta in [2, r-1] such that pow(zeta, n/q, r)
    != 1 for every distinct prime q dividing n, and pow(zeta, n, r) == 1.

    Per `arithmetic_definitions.primitive_element`. Not called at import
    time; this rule *defines* the fixture, it is not itself an asserted
    numerical result until actually invoked under a later authorized run.
    """
    for zeta in range(2, r):
        if pow(zeta, n, r) != 1:
            continue
        if all(pow(zeta, n // q, r) != 1 for q in distinct_prime_factors):
            return zeta
    raise ValueError(f"no primitive element found for r={r}, n={n}")


def distinct_primes(factorization: Sequence[Tuple[int, int]]) -> List[int]:
    return [p for p, _ in factorization]


# ---------------------------------------------------------------------------
# arithmetic_definitions.nonzero_positions / residue / divisors
# ---------------------------------------------------------------------------


def fixture_truth(zeta: int, r: int, k: int) -> int:
    """x = pow(zeta, k, r). Fixture truth; kept on the truth channel only."""
    return pow(zeta, k, r)


def fixture_residue(k: int, m: int) -> int:
    """a = k mod m for correct fixtures; canonical 0 <= a < m, a = 0 for m=1.

    Per `arithmetic_definitions.residue`.
    """
    if m == 1:
        return 0
    return k % m


def wrong_target_residue(k: int, m: int) -> int:
    """Wrong-target transformation: replace every residue by (k+1) mod m,
    while the fixture's original truth x = pow(zeta, k, r) is preserved
    unchanged. Per `wrong_target_panels.transformation`.
    """
    if m == 1:
        return 0
    return (k + 1) % m


# ---------------------------------------------------------------------------
# Token binding (input_supply)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TokenRecord:
    """One labeled supplied-token placeholder per constraint.

    Per `input_supply.token_binding`: labeled with the underlying fixture
    and original token index, exponent d, and source_kind =
    "synthetic_placeholder". No placeholder is an actual group point; no
    certificate here asserts a Cheon first stage was executed.
    """

    fixture_id: str
    original_token_index: int
    m: int
    d: int  # d = n // m
    source_kind: str = "synthetic_placeholder"


def make_token_record(fixture_id: str, original_token_index: int, n: int, m: int) -> TokenRecord:
    if n % m != 0:
        raise ValueError(f"m={m} does not divide n={n}")
    return TokenRecord(fixture_id=fixture_id, original_token_index=original_token_index, m=m, d=n // m)


def token_multiplicity_report(tokens: Sequence[TokenRecord]) -> Dict[str, object]:
    """Report token-reference count, distinct required exponent (d) count,
    and multiplicity per d, without silently treating duplicate acquisition
    as extra independent information (per `input_supply.token_binding`)."""
    d_values = [t.d for t in tokens]
    distinct_d = sorted(set(d_values))
    multiplicity = {d: d_values.count(d) for d in distinct_d}
    return {
        "token_reference_count": len(tokens),
        "distinct_d_count": len(distinct_d),
        "distinct_d_values": distinct_d,
        "multiplicity_by_d": multiplicity,
    }


# ---------------------------------------------------------------------------
# positive_panels (literal, transcribed verbatim from the specification)
# ---------------------------------------------------------------------------

POSITIVE_PANELS: Tuple[Dict[str, object], ...] = (
    {"id": "P00", "class": "empty_baseline", "m": (), "expected_M": 1},
    {"id": "P01", "class": "one", "m": (10,), "expected_M": 10},
    {"id": "P02", "class": "repeated", "m": (10, 10, 10), "expected_M": 10},
    {"id": "P03", "class": "nested", "m": (5, 10, 20), "expected_M": 20},
    {"id": "P04", "class": "noncoprime", "m": (4, 10), "expected_M": 20},
    {"id": "P05", "class": "coprime_partial", "m": (4, 5), "expected_M": 20},
    {"id": "P06", "class": "equal_lcm_single", "m": (20,), "expected_M": 20},
    {"id": "P07", "class": "equal_lcm_redundant", "m": (4, 5, 20, 20), "expected_M": 20},
    {
        "id": "P08",
        "class": "full_single",
        "m_by_r": {101: (100,), 241: (240,)},
        "expected_M": "n",
    },
    {
        "id": "P09",
        "class": "full_coprime",
        "m_by_r": {101: (4, 25), 241: (16, 3, 5)},
        "expected_M": "n",
    },
    {"id": "P10", "class": "modulus_one", "m": (1,), "expected_M": 1},
    {"id": "P11", "class": "modulus_one_augmented", "m": (1, 4, 10), "expected_M": 20},
)

# Panels whose supplied m_i are not all pairwise coprime relative to their
# lcm -- i.e. where the deliberately-faulty product rule M_bad=product(m_i)
# is expected to disagree with the true M=lcm(m_i). Per
# `controls.deliberately_faulty_product_rule`: "P02/P03/P04/P07/P11 must
# expose its error ... the other seven panels do not."
PRODUCT_RULE_MUTANT_EXPECTED_PANELS: Tuple[str, ...] = ("P02", "P03", "P04", "P07", "P11")

# ---------------------------------------------------------------------------
# inconsistency_panels
# ---------------------------------------------------------------------------

INCONSISTENCY_PANELS: Tuple[Dict[str, object], ...] = (
    {"id": "I01", "m": (10, 10), "residue_rules": ("k mod 10", "(k+1) mod 10")},
    {"id": "I02", "m": (4, 10), "residue_rules": ("k mod 4", "(k+1) mod 10")},
    {"id": "I03", "m": (5, 20), "residue_rules": ("k mod 5", "(k+1) mod 20")},
    {"id": "I04", "m": (20, 20), "residue_rules": ("k mod 20", "(k+1) mod 20")},
)


def inconsistency_residues(k: int, panel: Dict[str, object]) -> List[int]:
    """Evaluate an inconsistency panel's literal residue_rules against a
    given k. Rule strings are the two forms used throughout the
    specification: "k mod m" or "(k+1) mod m"."""
    out = []
    for m, rule in zip(panel["m"], panel["residue_rules"]):
        if rule.startswith("(k+1)"):
            out.append(wrong_target_residue(k, m))
        else:
            out.append(fixture_residue(k, m))
    return out


# ---------------------------------------------------------------------------
# wrong_target_panels
# ---------------------------------------------------------------------------

WRONG_TARGET_SOURCE_POSITIVE_IDS: Tuple[str, ...] = (
    "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P11",
)


def wrong_target_from_positive(panel: Dict[str, object], r: int) -> Dict[str, object]:
    """Derive a wrong_target panel definition from a positive panel by
    replacing every residue rule with (k+1) mod m, per
    `wrong_target_panels.transformation`. Original fixture truth x is
    unchanged; only the supplied residues are altered. Not executed here.
    """
    if panel["id"] not in WRONG_TARGET_SOURCE_POSITIVE_IDS:
        raise ValueError(f"panel {panel['id']} is not a declared wrong_target source")
    m_list = panel["m"] if "m" in panel else panel["m_by_r"][r]
    return {
        "id": f"WT-{panel['id']}",
        "source_positive_id": panel["id"],
        "m": tuple(m_list),
        "residue_rule": "(k+1) mod m",
        "expected_match_count": 0,
    }


# ---------------------------------------------------------------------------
# malformed_fixtures
# ---------------------------------------------------------------------------

MALFORMED_BASE_RULE = (
    "For each r use k=1 and positive P04, forward order, otherwise correct "
    "fields; apply one mutation only."
)

MALFORMED_CASES: Tuple[Dict[str, str], ...] = (
    {"id": "V01", "mutation": "replace r by r-1", "expected": "INPUT_UNSUPPORTED_R"},
    {"id": "V02", "mutation": "replace zeta by 1", "expected": "INPUT_NOT_PRIMITIVE"},
    {"id": "V03", "mutation": "remove factor 5 from n factorization", "expected": "INPUT_BAD_FACTORIZATION"},
    {"id": "V04", "mutation": "set first d to 0", "expected": "INPUT_BAD_D"},
    {"id": "V05", "mutation": "set first d to n+1", "expected": "INPUT_BAD_D"},
    {"id": "V06", "mutation": "set first m to 0", "expected": "INPUT_BAD_M"},
    {"id": "V07", "mutation": "set first m to 5 but retain first d=n/4", "expected": "INPUT_M_D_MISMATCH"},
    {"id": "V08", "mutation": "set first residue to -1", "expected": "INPUT_BAD_RESIDUE"},
    {"id": "V09", "mutation": "set first residue to first m", "expected": "INPUT_BAD_RESIDUE"},
    {"id": "V10", "mutation": "remove first supplied-token placeholder", "expected": "INPUT_MISSING_SUPPLY"},
    {"id": "V11", "mutation": "change first token exponent label to d+1 only", "expected": "INPUT_SUPPLY_BINDING_MISMATCH"},
    {"id": "V12", "mutation": "set x=0 with mode=nonzero", "expected": "INPUT_ZERO_NONZERO_MODE"},
)

# gate_order: the exact sequence of checks; expected error is the first
# failing check. Malformed cases never enter production CRT (crt.py).
GATE_ORDER: Tuple[str, ...] = (
    "supported_r_and_primality",
    "complete_factorization",
    "primitive_element",
    "nonzero_mode_boundary",
    "d_range_and_divisibility",
    "m_range_and_divisibility",
    "m_times_d_equals_n",
    "canonical_residue",
    "supply_presence",
    "supply_label_binding",
)

# Maps each gate stage to the malformed case(s) it is responsible for
# rejecting, so README.md and the future driver can cite exact provenance.
GATE_STAGE_TO_CASE: Dict[str, Tuple[str, ...]] = {
    "supported_r_and_primality": ("V01",),
    "complete_factorization": ("V03",),
    "primitive_element": ("V02",),
    "nonzero_mode_boundary": ("V12",),
    "d_range_and_divisibility": ("V04", "V05"),
    "m_range_and_divisibility": ("V06",),
    "m_times_d_equals_n": ("V07",),
    "canonical_residue": ("V08", "V09"),
    "supply_presence": ("V10",),
    "supply_label_binding": ("V11",),
}


@dataclass(frozen=True)
class GateOutcome:
    passed: bool
    failing_stage: Optional[str]
    error_code: Optional[str]


def run_input_gate(record: Dict[str, object]) -> GateOutcome:
    """Placeholder for the ordered validation gate described by GATE_ORDER.

    This function documents (and will, in a later authorized run,
    implement) the exact check sequence; it deliberately raises
    NotImplementedError here rather than silently approving or rejecting
    input, since actually gating and classifying a concrete malformed
    record is fixture *evaluation* -- explicitly out of scope for this
    zero-run implementation task. The concrete per-mutation checks are
    documented in GATE_STAGE_TO_CASE and README.md instead.
    """
    raise NotImplementedError(
        "run_input_gate is a documented future entry point; evaluating a "
        "concrete record is scientific execution and is not authorized by "
        "this implementation-only handoff (maximum_runs=0)."
    )


# ---------------------------------------------------------------------------
# zero_boundary
# ---------------------------------------------------------------------------

ZERO_BOUNDARY_CASES_PER_PRIME = 1
ZERO_BOUNDARY_DESCRIPTION = (
    "mode=zero, x=0, no constraints; original-target identity sentinel. "
    "Returns scalar 0 through the separate identity branch; no logarithm, "
    "CRT, first stage, or residual search is invoked."
)


# ---------------------------------------------------------------------------
# ordering_and_counts
# ---------------------------------------------------------------------------

PRIME_ORDER: Tuple[int, ...] = (101, 241)
FAMILY_ORDER: Tuple[str, ...] = ("malformed", "zero", "inconsistent", "wrong_target", "positive")

ORDER_VARIANTS: Tuple[Dict[str, str], ...] = (
    {"id": "forward", "transform": "Original record order."},
    {"id": "reverse", "transform": "Reverse the complete constraint records."},
    {"id": "rotate_left_one", "transform": "Move the first record to the end; empty stays empty."},
)


def apply_order_variant(records: Sequence[object], variant_id: str) -> List[object]:
    """Apply one of the three declared deterministic order variants to an
    ordered list of constraint records. These are invariance checks, not
    independent replications (per `duplicate_order_policy`)."""
    records = list(records)
    if variant_id == "forward":
        return records
    if variant_id == "reverse":
        return list(reversed(records))
    if variant_id == "rotate_left_one":
        if not records:
            return records
        return records[1:] + records[:1]
    raise ValueError(f"unknown order variant: {variant_id}")


TRAVERSAL_ORDER = "family_order, then prime_order, then panel_id, then ascending k, then listed order_variant"

# Exact declared counts, transcribed verbatim from
# `ordering_and_counts.formulas` and `ordering_and_counts.cases_by_prime`.
# These are frozen predictions to check completeness against, not
# computed/measured values.
CASE_COUNT_FORMULAS: Dict[str, str] = {
    "positive": "(100+240)*12*3 = 12240",
    "inconsistent": "(100+240)*4*3 = 4080",
    "wrong_target": "(100+240)*10*3 = 10200",
    "malformed": "2*12 = 24",
    "zero": "2*1 = 2",
    "total": "12240+4080+10200+24+2 = 26546",
}

CASE_COUNTS: Dict[str, int] = {
    "positive": 12240,
    "inconsistent": 4080,
    "wrong_target": 10200,
    "malformed": 24,
    "zero": 2,
    "total": 26546,
}

CASES_BY_PRIME: Dict[int, int] = {101: 7813, 241: 18733}
SCALAR_CONSTRAINT_CASES = 26520
REFERENCE_EXPONENT_VISITS = 5272800
PREDICTED_CANDIDATE_EQUALITY_EVALUATIONS: Dict[str, int] = {
    "positive": 509040,
    "wrong_target": 103440,
    "inconsistent": 0,
    "total": 612480,
}

# Per `controls.deliberately_faulty_product_rule`: exact expected count of
# cells where the faulty product-of-moduli mutant must expose its error.
PRODUCT_RULE_MUTANT_EXPECTED_TOTAL = 5100  # (100+240)*5*3


def declared_case_count_check() -> bool:
    """Sanity-check that the declared literal panel/family cardinalities in
    this module are consistent with the frozen CASE_COUNTS totals, using
    only counting arithmetic over the literal tables above (no fixture
    evaluation, no CRT, no primitive-element search). Not called at import
    time; intended as a pre-flight documentation check for the future
    driver, not a scientific measurement.
    """
    positive_panel_count = len(POSITIVE_PANELS)
    inconsistent_panel_count = len(INCONSISTENCY_PANELS)
    wrong_target_panel_count = len(WRONG_TARGET_SOURCE_POSITIVE_IDS)
    malformed_case_count = len(MALFORMED_CASES)

    n_sum = sum(p["n"] for p in PRIMES)  # 100 + 240 = 340
    order_variant_count = len(ORDER_VARIANTS)

    expected_positive = n_sum * positive_panel_count * order_variant_count
    expected_inconsistent = n_sum * inconsistent_panel_count * order_variant_count
    expected_wrong_target = n_sum * wrong_target_panel_count * order_variant_count
    expected_malformed = len(PRIMES) * malformed_case_count
    expected_zero = len(PRIMES) * ZERO_BOUNDARY_CASES_PER_PRIME

    computed_total = (
        expected_positive + expected_inconsistent + expected_wrong_target + expected_malformed + expected_zero
    )

    return (
        expected_positive == CASE_COUNTS["positive"]
        and expected_inconsistent == CASE_COUNTS["inconsistent"]
        and expected_wrong_target == CASE_COUNTS["wrong_target"]
        and expected_malformed == CASE_COUNTS["malformed"]
        and expected_zero == CASE_COUNTS["zero"]
        and computed_total == CASE_COUNTS["total"]
    )
