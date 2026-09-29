"""Independent structural checker — deliberately separate from producer code.

EXP-CRYPTO-3759c6 preparation artifact for TASK-20260907-da9b67.

AUTHORSHIP AND INDEPENDENCE NOTICE (read before use):
    This file was authored in the SAME preparation task, by the SAME
    executor session, as corpus.py, queries.py, evaluate.py and controls.py.
    Placing a checker in its own module does NOT establish independent
    authorship, and running it does NOT constitute a successful independent
    review. Genuine independence requires a separately claimed, genuinely
    independent session per spec.execution_gate and
    DEC-20260907-b8bd3e.approval_scope.independent_review: independent label
    authors, an independent third adjudicator, and an independently authored
    evaluator checker with a preregistered claim-review plan, none of which
    this handoff opens. Until that independent session exists and is
    recorded, no invocation of this module may be cited as "independently
    verified" or "checked" evidence. This file records that limitation in
    every function contract below rather than implying otherwise.

Design constraint honored: this module imports NOTHING from corpus.py,
queries.py, evaluate.py, or controls.py. Every check below is reimplemented
from the frozen specification text alone, so it cannot silently inherit a
producer-side bug. It also performs no census, labeling, query execution, or
scoring; every function is a pure function over already-produced result
values from a future admitted run, and is not invoked by this preparation
task.
"""

from __future__ import annotations

import dataclasses
import hashlib
from fractions import Fraction
from typing import Optional

# ---------------------------------------------------------------------------
# Set-membership / count identities (independent reimplementation)
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class CheckResult:
    check_id: str
    passed: bool
    detail: str


def check_set_membership_consistency(
    returned_set: frozenset[str],
    admitted_universe: frozenset[str],
) -> CheckResult:
    """Independently verifies returned_set is a subset of the admitted
    document universe for that arm/view. This is a structural containment
    check, not a relevance judgment or a proof the retrieval logic itself is
    correct — it can only catch a returned set that reaches outside the
    admitted corpus. Not invoked against real returned sets by this task.
    """
    extraneous = returned_set - admitted_universe
    passed = len(extraneous) == 0
    return CheckResult(
        "set_membership_consistency",
        passed,
        f"extraneous={sorted(extraneous)}" if extraneous else "returned_set subset of admitted_universe",
    )


def check_count_identity(
    micro_hits: int,
    per_proposal_hit_counts: dict[str, int],
) -> CheckResult:
    """Independently re-derive the micro hit count as the sum of per-proposal
    hit counts, catching an aggregation bug distinct from the producer's own
    summation. Structural arithmetic re-derivation only; does not validate
    that any individual hit is a correct or true relevance judgment. Not
    invoked against real counts by this task.
    """
    recomputed = sum(per_proposal_hit_counts.values())
    passed = recomputed == micro_hits
    return CheckResult(
        "count_identity",
        passed,
        f"recomputed={recomputed} reported={micro_hits}",
    )


def check_exhaustive_pair_denominator(
    reported_denominator: int,
    exclusions: dict[str, int],
    total_candidates: int,
) -> CheckResult:
    """Independently re-derive a reported denominator as
    total_candidates - sum(exclusions.values()), to catch a silently dropped
    exclusion category (spec.corpus.denominators: reconcile totals by
    explicit row IDs). Not invoked against real candidate counts by this task.
    """
    recomputed = total_candidates - sum(exclusions.values())
    passed = recomputed == reported_denominator
    return CheckResult(
        "exhaustive_pair_denominator",
        passed,
        f"recomputed={recomputed} reported={reported_denominator} exclusions={exclusions}",
    )


# ---------------------------------------------------------------------------
# Null-expectation identity (independent reimplementation, no producer import)
# ---------------------------------------------------------------------------

def check_uniform_entry_expectation(
    returned_set_size: int,
    doc_count: int,
    reported_expectation: Fraction,
) -> CheckResult:
    """Finite-set uniform-entry identity Pr[X in S] = |S|/|D| for nonempty D
    (H-CRYPTO-1d65d5.formalization.smallest_obligation). Independently
    recomputed from the two integers alone, without importing evaluate.py's
    own exact_null_expectation implementation. Not invoked against real
    counts by this task.
    """
    if doc_count <= 0:
        return CheckResult("uniform_entry_expectation", False, "doc_count must be positive (D=0 case is undefined)")
    recomputed = Fraction(returned_set_size, doc_count)
    passed = recomputed == reported_expectation
    return CheckResult(
        "uniform_entry_expectation",
        passed,
        f"recomputed={recomputed} reported={reported_expectation}",
    )


def check_margin_inequalities(
    observed_rate: Fraction,
    null_rate: Fraction,
    reported_factor_three_ok: bool,
    reported_absolute_margin_ok: bool,
) -> CheckResult:
    """Independently recompute R>=3q and R-q>=0.20 using exact rational
    arithmetic, without importing evaluate.py's implementation
    (spec.nulls.margin). Not invoked against real rates by this task.
    """
    recomputed_factor = observed_rate >= 3 * null_rate
    recomputed_absolute = (observed_rate - null_rate) >= Fraction(20, 100)
    passed = recomputed_factor == reported_factor_three_ok and recomputed_absolute == reported_absolute_margin_ok
    return CheckResult(
        "margin_inequalities",
        passed,
        f"factor3 recomputed={recomputed_factor} reported={reported_factor_three_ok}; "
        f"absolute recomputed={recomputed_absolute} reported={reported_absolute_margin_ok}",
    )


def check_signed_delta_identity(
    n01: int,
    n10: int,
    n_total: int,
    reported_delta: Fraction,
) -> CheckResult:
    """signed delta = (n01 - n10) / N under an explicitly declared four-way
    orientation (H-CRYPTO-1d65d5.formalization.smallest_obligation), where
    n01 = sparse-hit/boolean-miss pairs and n10 = sparse-miss/boolean-hit
    pairs. Independently recomputed; not invoked by this task.
    """
    if n_total == 0:
        return CheckResult("signed_delta_identity", reported_delta is None, "N=0 must report NA, not a numeric delta")
    recomputed = Fraction(n01 - n10, n_total)
    passed = recomputed == reported_delta
    return CheckResult(
        "signed_delta_identity",
        passed,
        f"recomputed={recomputed} reported={reported_delta} n01={n01} n10={n10} N={n_total}",
    )


# ---------------------------------------------------------------------------
# Rank / tie identities
# ---------------------------------------------------------------------------

def check_stable_lexical_tie_order(returned_order: tuple[str, ...], expected_lexical_order_subset: tuple[str, ...]) -> CheckResult:
    """Independently verify a returned tie-broken ranking follows the
    corpus-wide UTF-8 bytewise lexical path order for tied elements
    (spec.arms.title_abstract_boolean20, spec.arms.title_abstract_sparse20,
    spec.controls.tie_fixture). Not invoked against real rankings by this task.
    """
    filtered = tuple(doc_id for doc_id in expected_lexical_order_subset if doc_id in returned_order)
    passed = returned_order == filtered
    return CheckResult(
        "stable_lexical_tie_order",
        passed,
        f"returned={returned_order} expected_subset_order={filtered}",
    )


def check_top_k_size(returned_order: tuple[str, ...], k: int, positive_candidate_count: int) -> CheckResult:
    """Independently verify |returned| == min(k, positive_candidate_count),
    catching an off-by-one or zero-fill defect distinct from the producer's
    own truncation logic (spec.sparse_model.zero_scores). Not invoked here.
    """
    expected_len = min(k, positive_candidate_count)
    passed = len(returned_order) == expected_len
    return CheckResult(
        "top_k_size",
        passed,
        f"returned_len={len(returned_order)} expected_len={expected_len}",
    )


# ---------------------------------------------------------------------------
# Hash-binding checks (independent, no shared code path with the producer's
# own hashing utility beyond stdlib hashlib itself)
# ---------------------------------------------------------------------------

def independent_sha256(raw: bytes) -> str:
    """Hash bytes with the standard library directly, so a producer-side
    hashing helper bug cannot silently propagate into the checker's own
    digest. Not invoked against real artifact bytes by this task.
    """
    return hashlib.sha256(raw).hexdigest()


def check_manifest_hash_binding(
    file_bytes: bytes,
    declared_sha256: str,
) -> CheckResult:
    """Independently recompute a declared artifact's sha256 from its actual
    bytes. This validates the recorded hash against the bytes; it does NOT
    validate that the bytes themselves encode correct labels, queries, or
    corpus content. Not invoked against real artifact bytes by this task.
    """
    recomputed = independent_sha256(file_bytes)
    passed = recomputed == declared_sha256
    return CheckResult(
        "manifest_hash_binding",
        passed,
        f"recomputed={recomputed} declared={declared_sha256}",
    )


def check_acyclic_hash_dependencies(dependency_edges: dict[str, tuple[str, ...]]) -> CheckResult:
    """Independently verify a manifest's declared hash-dependency graph is
    acyclic and that no manifest references its own digest
    (spec.artifacts.exact_bytes: hash dependencies must be acyclic; a report
    identifies its manifest by path without its digest). Not invoked against
    a real dependency graph by this task.
    """
    visiting: set[str] = set()
    visited: set[str] = set()
    cycle_detail: Optional[str] = None

    def visit(node: str, stack: list[str]) -> bool:
        nonlocal cycle_detail
        if node in visiting:
            cycle_detail = " -> ".join(stack + [node])
            return False
        if node in visited:
            return True
        visiting.add(node)
        for dep in dependency_edges.get(node, ()):
            if not visit(dep, stack + [node]):
                return False
        visiting.discard(node)
        visited.add(node)
        return True

    ok = True
    for node in dependency_edges:
        if node not in visited:
            if not visit(node, []):
                ok = False
                break
    return CheckResult(
        "acyclic_hash_dependencies",
        ok,
        "acyclic" if ok else f"cycle detected: {cycle_detail}",
    )


# ---------------------------------------------------------------------------
# Explicit scope statement
# ---------------------------------------------------------------------------

STRUCTURAL_VALIDITY_IS_NOT_RELEVANCE_TRUTH = (
    "Every check in this module verifies internal structural/arithmetic "
    "consistency (set containment, count identities, exact-fraction "
    "recomputation, hash binding, acyclic dependency graphs). None of them "
    "establishes that a relevance label is correct, that a query replay is "
    "historically faithful, that the corpus census is complete, or that this "
    "module was authored or executed by a session independent of the "
    "producer. A passing result here is not a proof of evaluator "
    "correctness and is not, by itself, a successful independent review."
)
