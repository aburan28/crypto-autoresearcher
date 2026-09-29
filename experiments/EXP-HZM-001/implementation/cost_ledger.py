"""Frozen charged-cost ledger for the defect-scaled hyperplane-signature
route, per specification.yaml inputs.frozen_cost_ledger.charged_stages and
the immutable snapshot's charged_cost_model block.

Charges every named stage (sampled_point_generation,
evaluation_matrix_construction, left_kernel_and_reductions, defect_loop,
signature_construction, duplicate_storage_or_streaming,
failed_outer_restrictions, zero_minor_reconstruction,
final_group_equality_verification) as an explicit operation count, and
compares the resulting charged expected per-target work against the frozen
Pollard-rho bound ceil(N**0.5).

STATUS UNDER EXP-HZM-001: written and unit-smoke-tested in isolation (see
SELFTEST.md), but NOT invoked as part of a formal protocol run. Because
CTRL-HZM-MANUSCRIPT-ALIGNMENT failed in RUN-HZM-001-a (the pinned H formula
does not match the manuscript's own displayed H equation -- see
manuscript_alignment.md), computing a charged cost against a formula the
manuscript itself does not actually assert this way would misrepresent an
unverified quantity as a measured/charged cost. This module is provided as
a reusable, honestly-labeled reference implementation for a future protocol
amendment; it makes NO cost claim under EXP-HZM-001's current run set.

Every number this module returns is labeled `modeled` (derived from the
spec's own pinned formulas), never `measured`, per docs/evidence-and-
reproducibility.md's heuristic-validation and cost-model reporting rules.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import sympy


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return int(sympy.binomial(n, k))


@dataclass(frozen=True)
class ChargedCostModel:
    """All fields are MODELED quantities derived from the specification's
    pinned formulas, not measured counts from an executed enumeration run.
    """
    N: int
    L: int
    d: int
    M_candidate_completions: int
    H_signature_mass_as_pinned: int   # spec's H = binom(L+d, d-1)
    q_success_probability: float
    charged_expected_signatures: float  # H / q (spec's own lower-bound quantity)
    rho_bound: int
    survives_rho_gate: bool
    optimistic_assumptions: list


def model_charged_cost(N: int, L: int, d: int) -> ChargedCostModel:
    """Reproduces specification.yaml's own pinned algebra exactly
    (M=binom(L+d,d), H=binom(L+d,d-1)=M*d/(L+1), q=1-(1-1/N)^M), for
    reference/reuse only. This is the SPEC's pinned formula, not an
    independently re-verified manuscript equation -- RUN-HZM-001-a found
    the manuscript's own displayed H formula uses a different base symbol
    (l=2*l') than the spec assumed (l'=L for both M and H).
    """
    M = binom(L + d, d)
    H = binom(L + d, d - 1)
    q = 1.0 - (1.0 - 1.0 / N) ** M
    charged_expected_signatures = H / q if q > 0 else float("inf")
    rho_bound = math.isqrt(N - 1) + 1  # ceil(sqrt(N)) for integer N
    survives = charged_expected_signatures < rho_bound
    return ChargedCostModel(
        N=N, L=L, d=d,
        M_candidate_completions=M,
        H_signature_mass_as_pinned=H,
        q_success_probability=q,
        charged_expected_signatures=charged_expected_signatures,
        rho_bound=rho_bound,
        survives_rho_gate=survives,
        optimistic_assumptions=[
            "Charges only H/q signature constructions; ignores matrix "
            "construction, failed-outer-restriction retries beyond the "
            "q-implied retry count, duplicate storage/streaming overhead, "
            "reconstruction, and final verification stages -- all of which "
            "the frozen cost ledger's other named stages require charging "
            "in a full run (this reference function models only the "
            "signature-count bottleneck term, per the snapshot's own "
            "cheapest_decisive_gate framing).",
            "Assumes poly(log N) bit cost per field/group operation, so "
            "N-exponent comparisons are unaffected by bit-cost conversion "
            "(specification.yaml inputs.frozen_cost_ledger.conversion_rule).",
            "Uses the SPEC's pinned H=binom(L+d,d-1), which RUN-HZM-001-a "
            "found does NOT match the manuscript's own displayed H formula "
            "(binom(l+d,d-1) with l=2*L in the manuscript's notation). This "
            "function is therefore a reproduction of the SPEC's algebra, "
            "not an independently verified manuscript quantity.",
        ],
    )
