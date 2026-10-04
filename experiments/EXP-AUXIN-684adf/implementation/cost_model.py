"""Integer cost proxy and comparator-frontier bookkeeping for EXP-AUXIN-684adf.

Frozen source: specification.yaml `cost_and_frontier` section (exact_proxy,
symbolic_total, memory, data, comparison_rule, comparator_rows) and
`input_supply.acquisition_cost_policy`.

Discipline (binding, do not relax):

  * `isqrtceil` and everything built on it use only Python's exact-integer
    `math.isqrt`; no floating point appears anywhere in this module. This
    matches the specification's "These are integer model units, not
    operation counts."
  * Every modeled/symbolic quantity is kept in a field distinct from any
    future measured quantity, and every acquisition/group-operation number
    that is not executed here is represented as `None` with an explicit
    `not_executed` reason -- never as a fabricated numeric estimate
    presented as measured.
  * No code below executes at import time. No cost is computed by writing
    this file; these are function/data definitions only, meant to be
    invoked by the later authorized driver run.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence


def isqrtceil(z: int) -> int:
    """Exact integer ceiling-square-root proxy.

    Per `cost_and_frontier.exact_proxy`:
        isqrtceil(z) = isqrt(z) if isqrt(z)^2 = z else isqrt(z) + 1
    """
    if z < 0:
        raise ValueError("isqrtceil requires a non-negative integer")
    r = math.isqrt(z)
    return r if r * r == z else r + 1


@dataclass(frozen=True)
class ResidualProxy:
    """W (total) and S (max single-stage) integer cost-proxy values for one
    cell, per `cost_and_frontier.exact_proxy`.

    For a nonempty list of moduli m_i with residual length L = n / M:
        W = sum(isqrtceil(m_i)) + isqrtceil(L)
        S = max({isqrtceil(m_i)} union {isqrtceil(L)})
    For an empty list (P00, the no-auxiliary baseline):
        W = isqrtceil(n), S = isqrtceil(n)
    """

    m_values: Sequence[int]
    L: int
    W: int
    S: int


def residual_proxy(m_values: Sequence[int], n: int, L: int) -> ResidualProxy:
    """Compute the exact integer W/S cost proxy for a cell.

    `m_values` must be the *actual* supplied list (including repeats;
    duplicates are never silently deduplicated, per
    "Report actual lists, multiplicities and L; do not silently deduplicate
    stage costs."). `L` is the residual length n/M for this cell (or n
    itself, conventionally, when the list is empty and no M has been
    established).
    """
    if not m_values:
        proxy = isqrtceil(n)
        return ResidualProxy(m_values=tuple(m_values), L=n, W=proxy, S=proxy)

    per_stage = [isqrtceil(m) for m in m_values]
    l_term = isqrtceil(L)
    W = sum(per_stage) + l_term
    S = max(per_stage + [l_term])
    return ResidualProxy(m_values=tuple(m_values), L=L, W=W, S=S)


@dataclass(frozen=True)
class SymbolicCostTerms:
    """Named symbolic terms of the total cost expression, per
    `cost_and_frontier.symbolic_total`. This structure carries labels for
    the terms of:

        C_factor(n) + C_divisorcert + C_setup + C_supply
          + sum_i C_first(m_i) + C_CRT + C_residual(L) + C_verify + C_data_IO

    with the source-motivated table model C_first(m) = O(sqrt(m) * log r)
    and residual O(sqrt(L) * log r), constants unspecified. No numeric
    value is assigned to the O(...) terms here -- they are documented
    symbolically, not evaluated, since the constants are explicitly
    unspecified in the frozen protocol.
    """

    term_names: Sequence[str] = (
        "C_factor(n)",
        "C_divisorcert",
        "C_setup",
        "C_supply",
        "sum_i C_first(m_i)",
        "C_CRT",
        "C_residual(L)",
        "C_verify",
        "C_data_IO",
    )
    first_stage_model: str = "O(sqrt(m) * log r), constant unspecified"
    residual_model: str = "O(sqrt(L) * log r), constant unspecified"
    note: str = (
        "A complete-recovery cost additionally accounts for inverse success "
        "probability and all attempts. That probability and real "
        "acquisition cost are unknown here; no numeric total is claimed."
    )


SYMBOLIC_COST_TERMS = SymbolicCostTerms()


@dataclass(frozen=True)
class AcquisitionAccounting:
    """Explicit not-executed accounting for actual group-token acquisition,
    per `input_supply.acquisition_cost_policy` and
    `cost_and_frontier.data`/`memory`.

    Every field that cannot be measured in this arithmetic-only calibration
    is `None` with `reason="not_executed"` -- never a fabricated estimate.
    """

    actual_acquisition_time_seconds: Optional[float] = None
    actual_acquisition_memory_bytes: Optional[int] = None
    actual_acquisition_data_bytes: Optional[int] = None
    actual_group_operations: Optional[int] = None
    reason: str = "not_executed"

    token_reference_count: Optional[int] = None
    distinct_d_requirement_count: Optional[int] = None
    sparse_token_count: Optional[int] = None
    dense_supply_q: Optional[int] = None  # q = max(d_i), comparator only


def comparator_dense_q(d_values: Sequence[int]) -> Optional[int]:
    """Dense-supply comparator q = max(d_i) nontrivial power positions, per
    `cost_and_frontier.data`. Returns None for an empty supply list (no
    comparator applicable); this is a comparator quantity only, never a
    conversion to acquisition seconds or an implied zero acquisition cost.
    """
    if not d_values:
        return None
    return max(d_values)


# ---------------------------------------------------------------------------
# comparator_rows (F0-F8), transcribed verbatim from
# `cost_and_frontier.comparator_rows`
# ---------------------------------------------------------------------------

COMPARATOR_ROWS: Dict[str, Dict[str, str]] = {
    "F0": {
        "name": "No-auxiliary original-input baseline",
        "assessment": (
            "P00 arithmetic enumeration; generic table and rho-type "
            "time/memory tradeoffs are contextual, not reproduced group "
            "baselines."
        ),
    },
    "F1": {
        "name": "Every single supplied divisor available in the current panel",
        "assessment": (
            "Enumerate every distinct listed m; report ceil-sqrt(m)+"
            "ceil-sqrt(n/m), memory proxy, source requirements, and "
            "minimum proxy with ties retained."
        ),
    },
    "F2": {
        "name": "Every arithmetic single-divisor possibility for n",
        "assessment": (
            "Enumerate every divisor m of the certified n; report the same "
            "proxy; unsupplied powers remain unavailable rather than free "
            "baseline inputs."
        ),
    },
    "F3": {
        "name": "Published multiple-power CRT table mechanism",
        "assessment": (
            "P09 full coprime coverage and every supplied partial panel; "
            "known precedent, source-motivated model only."
        ),
    },
    "F4": {
        "name": "Redundant and equal-LCM inputs",
        "assessment": (
            "P01/P02 and P03/P04/P05/P06/P07/P11; same residual count does "
            "not imply same acquisition, stage cost or memory."
        ),
    },
    "F5": {
        "name": "Table versus low-memory auxiliary-input variants",
        "assessment": (
            "Unresolved; parent-transmitted DEC-20260802-204 notes existing "
            "variants but current primary frontier and implementation are "
            "not reproduced."
        ),
    },
    "F6": {
        "name": "Sparse versus dense power acquisition",
        "assessment": (
            "Explicit symbolic acquisition/data rows only; no legal "
            "protocol supply or measured acquisition is established."
        ),
    },
    "F7": {
        "name": "IDEA-20260905-830138 typed supplied-token certificate",
        "assessment": (
            "Input grammar/provenance comparator, not an implemented "
            "solver; numerical algorithm comparison is not applicable."
        ),
    },
    "F8": {
        "name": "Complete published ECC frontier",
        "assessment": (
            "Unknown; no complete all-row frontier was retrieved. No "
            "global Pareto or novelty conclusion is permitted."
        ),
    },
}

DOMINATED_BY = "n/a (no result claimed)"
SOTA_DELTA = "no attack; conceptual/measurement contribution only; established improvement 0"


def divisors_of(n: int) -> List[int]:
    """All positive divisors of n, ascending. Used by comparator row F2's
    'every arithmetic single-divisor possibility for n'. Not called at
    import time."""
    divs = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
        i += 1
    return sorted(divs)


def single_divisor_proxy(n: int, m: int) -> int:
    """ceil-sqrt(m) + ceil-sqrt(n/m) single-divisor comparator proxy used by
    F1/F2. Requires m to divide n."""
    if n % m != 0:
        raise ValueError(f"m={m} does not divide n={n}")
    return isqrtceil(m) + isqrtceil(n // m)


def modeled_benefit_label(panel_W: int, baseline_W: int) -> str:
    """Descriptive label only: 'lower' | 'equal' | 'higher'. Per
    `decision_outcomes.modeled_benefit`: "This descriptive label cannot
    determine the scientific success outcome."""
    if panel_W < baseline_W:
        return "lower"
    if panel_W > baseline_W:
        return "higher"
    return "equal"


@dataclass(frozen=True)
class OperationCounters:
    """Explicit counters for arithmetic calls actually performed by the
    calibration (per `metrics.secondary`): gcd, inverse, residue-test,
    modular-power, and candidate-equality call counts, with integer operand
    bit lengths. All fields default to 0/empty; a future authorized run
    increments them, this module only defines the structure."""

    gcd_calls: int = 0
    inverse_calls: int = 0
    residue_test_calls: int = 0
    modular_power_calls: int = 0
    candidate_equality_calls: int = 0
    operand_bit_lengths: List[int] = field(default_factory=list)
