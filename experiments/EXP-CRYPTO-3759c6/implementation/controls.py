"""Fixed mechanical control panel and six obligation oracles (spec.controls).

EXP-CRYPTO-3759c6 preparation artifact for TASK-20260907-da9b67. Defines the
27-document synthetic panel (6 named fixtures + 21-document tie fixture) and
the six named mechanical obligations as *source definitions and checkable
oracle predicates*. This is a separate synthetic minicorpus, never inserted
into the production corpus/index, and never substituted for the full study
(spec.controls.scope). No fixture is materialized to disk or evaluated by
this preparation task: the constants below are the frozen fixture texts, and
the ``check_*`` functions are pure predicates over an already-computed result
dict that the future admission/run pass will produce by actually invoking
queries.py/evaluate.py against these fixtures.
"""

from __future__ import annotations

import dataclasses
from typing import Optional

# ---------------------------------------------------------------------------
# Fixed 6-document mechanical panel (spec.controls.fixtures)
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class ControlDocument:
    doc_id: str
    title: str
    abstract: str


CONTROL_FIXTURES: tuple[ControlDocument, ...] = (
    ControlDocument("c00", "alpha", "beta"),
    ControlDocument("c01", "ALPHA", "gamma"),
    ControlDocument("c02", "alphabet", "beta"),
    ControlDocument("c03", "delta", "epsilon"),
    # c04: byte-identical searchable text to c03, distinct ID (spec.controls.fixtures)
    ControlDocument("c04", "delta", "epsilon"),
    ControlDocument("c05", "", ""),
)

# ---------------------------------------------------------------------------
# 21-document identical-token tie fixture (spec.controls.tie_fixture)
# ---------------------------------------------------------------------------

TIE_FIXTURE: tuple[ControlDocument, ...] = tuple(
    ControlDocument(f"t{i:02d}", "tieprobe", "") for i in range(21)
)

CONTROL_DOCUMENT_COUNT = 27  # spec.controls.control_documents
OBLIGATIONS_COUNT = 6        # spec.controls.obligations_count

assert len(CONTROL_FIXTURES) == 6, "c00..c05 must be exactly six fixtures"
assert len(TIE_FIXTURE) == 21, "t00..t20 must be exactly twenty-one tie-fixture documents"
assert len(CONTROL_FIXTURES) + len(TIE_FIXTURE) == CONTROL_DOCUMENT_COUNT


def searchable_text(doc: ControlDocument) -> str:
    """title\\nabstract per spec.corpus_views.title_abstract concatenation rule."""
    return f"{doc.title}\n{doc.abstract}"


# ---------------------------------------------------------------------------
# Obligation result shape
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class ObligationResult:
    obligation_id: str
    passed: bool
    expected: object
    observed: object
    detail: Optional[str] = None


# ---------------------------------------------------------------------------
# Six named mechanical obligations (spec.controls.obligations)
# ---------------------------------------------------------------------------
#
# Each check_* function is a pure oracle: given a returned-set (or score) dict
# already produced by an actual queries.py/evaluate.py invocation against
# CONTROL_FIXTURES / TIE_FIXTURE, it asserts the expected mechanical outcome.
# None of these functions is invoked with real returned sets by this
# preparation task; no fixture is evaluated here.

def check_fixed_string_case_sensitivity(returned_alpha_cs: frozenset[str], returned_alpha_ci: frozenset[str], returned_alpha_word: frozenset[str]) -> ObligationResult:
    """Fixed-string case-sensitive 'alpha' matches c00,c02; case-insensitive
    also c01; word-boundary 'alpha' excludes alphabet (c02)."""
    expected_cs = frozenset({"c00", "c02"})
    expected_ci = frozenset({"c00", "c01", "c02"})
    expected_word = expected_ci - frozenset({"c02"})
    passed = (
        returned_alpha_cs == expected_cs
        and returned_alpha_ci == expected_ci
        and returned_alpha_word == expected_word
    )
    return ObligationResult(
        "fixed_string_case_sensitivity",
        passed,
        {"cs": expected_cs, "ci": expected_ci, "word": expected_word},
        {"cs": returned_alpha_cs, "ci": returned_alpha_ci, "word": returned_alpha_word},
    )


def check_boolean_and_or(returned_and_alpha_beta: frozenset[str], returned_or_alpha_epsilon: frozenset[str]) -> ObligationResult:
    """AND(alpha,beta) case-sensitive fixed matches c00,c02; OR(alpha,epsilon)
    matches c00,c02,c03,c04. A single word does not discharge AND."""
    expected_and = frozenset({"c00", "c02"})
    expected_or = frozenset({"c00", "c02", "c03", "c04"})
    passed = returned_and_alpha_beta == expected_and and returned_or_alpha_epsilon == expected_or
    return ObligationResult(
        "boolean_and_or",
        passed,
        {"and": expected_and, "or": expected_or},
        {"and": returned_and_alpha_beta, "or": returned_or_alpha_epsilon},
    )


def check_empty_and_nonexistent_queries(returned_omega: frozenset[str], returned_empty_structured: frozenset[str], returned_empty_sparse_positive: frozenset[str]) -> ObligationResult:
    """A nonexistent fixed token 'omega' and a truly empty structured query
    return no documents; all-empty/no-overlap sparse inputs return no
    positive-score documents."""
    passed = (
        returned_omega == frozenset()
        and returned_empty_structured == frozenset()
        and returned_empty_sparse_positive == frozenset()
    )
    return ObligationResult(
        "empty_and_nonexistent_queries",
        passed,
        {"omega": frozenset(), "empty_structured": frozenset(), "empty_sparse": frozenset()},
        {"omega": returned_omega, "empty_structured": returned_empty_structured, "empty_sparse": returned_empty_sparse_positive},
    )


def check_sparse_tie_on_identical_documents(scores: dict[str, float], ordered_ids: tuple[str, ...]) -> ObligationResult:
    """The sparse query 'delta' gives positive equal scores to the identical
    c03/c04 texts, with c03 ranked before c04 by stable lexical tie order.
    Asserted mechanically from equal vectors and positive overlap, never a
    guessed semantic rank."""
    c03_score = scores.get("c03")
    c04_score = scores.get("c04")
    equal_positive = c03_score is not None and c04_score is not None and c03_score == c04_score and c03_score > 0
    order_ok = ordered_ids.index("c03") < ordered_ids.index("c04") if "c03" in ordered_ids and "c04" in ordered_ids else False
    passed = equal_positive and order_ok
    return ObligationResult(
        "sparse_tie_on_identical_documents",
        passed,
        {"equal_positive": True, "c03_before_c04": True},
        {"c03_score": c03_score, "c04_score": c04_score, "order_ok": order_ok},
    )


def check_leakage_flag_triggers(flag_triggered_on_target_metadata_query: bool, rejected_target_metadata_query: bool) -> ObligationResult:
    """A synthetic explicit target ID/DOI/title query triggers the leakage
    flag before scoring; a query assembled from target metadata is rejected."""
    passed = flag_triggered_on_target_metadata_query and rejected_target_metadata_query
    return ObligationResult(
        "leakage_flag_triggers",
        passed,
        {"flag_triggered": True, "rejected": True},
        {"flag_triggered": flag_triggered_on_target_metadata_query, "rejected": rejected_target_metadata_query},
    )


def check_view_routing_and_tie_fixture(full_body_routed_correctly: bool, title_abstract_routed_correctly: bool, path_exclusion_ok: bool, tie_fixture_first20_ids: tuple[str, ...]) -> ObligationResult:
    """Full-body and title/abstract routing, path exclusion and stable K
    cutoff are checked against an independently constructed finite-set
    oracle; the 21-document identical-token tie fixture returns the first 20
    lexical IDs (t00..t19)."""
    expected_first20 = tuple(f"t{i:02d}" for i in range(20))
    tie_ok = tie_fixture_first20_ids == expected_first20
    passed = full_body_routed_correctly and title_abstract_routed_correctly and path_exclusion_ok and tie_ok
    return ObligationResult(
        "view_routing_and_tie_fixture",
        passed,
        {"tie_fixture_first20": expected_first20},
        {"tie_fixture_first20": tie_fixture_first20_ids, "full_body_ok": full_body_routed_correctly, "title_abstract_ok": title_abstract_routed_correctly, "path_exclusion_ok": path_exclusion_ok},
    )


ALL_OBLIGATION_IDS: tuple[str, ...] = (
    "fixed_string_case_sensitivity",
    "boolean_and_or",
    "empty_and_nonexistent_queries",
    "sparse_tie_on_identical_documents",
    "leakage_flag_triggers",
    "view_routing_and_tie_fixture",
)
assert len(ALL_OBLIGATION_IDS) == OBLIGATIONS_COUNT


def all_obligations_passed(results: list[ObligationResult]) -> bool:
    """Failure of any one control invalidates the evaluator and blocks
    null/treatment interpretation for that invocation (spec.controls.report_order).
    Pure aggregator; not invoked against real obligation results by this task."""
    seen = {r.obligation_id for r in results}
    if seen != set(ALL_OBLIGATION_IDS):
        missing = set(ALL_OBLIGATION_IDS) - seen
        raise ValueError(f"incomplete control report; missing obligations: {sorted(missing)}")
    return all(r.passed for r in results)
