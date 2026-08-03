"""The evaluation harness, and the measured baseline it currently reports.

The thresholds asserted here are *measured*, not aspirational -- they sit just
below the numbers the current configuration produces, so this test fails when
retrieval regresses rather than when it fails to reach a target. The plan's
gates live in ``harness.GATES`` and are checked separately by
``crypto-kb evaluate``; one of them is not met today, and the README says so.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from crypto_kb.eval.harness import GATES, evaluate, evaluate_modes, format_report, load_questions

QUESTIONS = Path(__file__).parent / "questions.jsonl"

#: Measured on the evaluation corpus slice. Update deliberately, with the run
#: that justifies the change.
BASELINE = {
    "recall_at_5": 0.85,
    "recall_at_10": 0.90,
    "mrr": 0.74,
    "ndcg_at_10": 0.78,
    "exact_identifier_recall_at_5": 1.0,
    "general_recall_at_5": 0.77,
    "filter_correctness": 1.0,
    "source_attribution": 1.0,
}


@pytest.fixture(scope="module")
def questions():
    return load_questions(QUESTIONS)


@pytest.fixture(scope="module")
def report(eval_environment, questions):
    return evaluate(eval_environment["retriever"], questions, mode="hybrid")


def test_question_set_covers_every_category(questions):
    categories = {q.category for q in questions}
    expected = {
        "exact-lookup",
        "semantic-paraphrase",
        "mathematical-notation",
        "metadata-constrained",
        "negative-result",
        "contradictory-evidence",
        "paper-vs-experiment",
        "superseded",
        "source-attribution",
        "unanswerable",
    }
    assert expected <= categories, f"missing categories: {sorted(expected - categories)}"


def test_question_set_is_large_enough(questions):
    assert len(questions) >= 30, "the plan calls for 30+ questions before tuning retrieval"


def test_labelled_sources_exist_in_the_corpus(eval_environment, questions):
    """A label naming a document that was never indexed measures nothing."""
    retriever = eval_environment["retriever"]
    missing = []
    for question in questions:
        for source_id in question.required_sources:
            if retriever.get_source(source_id) is None:
                missing.append((question.id, source_id))
    assert not missing, f"labels reference unindexed sources: {missing}"


@pytest.mark.parametrize("metric,threshold", sorted(BASELINE.items()))
def test_measured_baseline_holds(report, metric, threshold):
    value = report.metrics()[metric]
    assert value >= threshold, (
        f"{metric} regressed to {value:.3f} (baseline {threshold}); "
        "if this is an intended trade-off, update BASELINE with the run that justifies it"
    )


def test_filters_never_leak_excluded_content(report):
    for outcome in report.outcomes:
        assert outcome.filter_ok, f"{outcome.question.id} returned results violating its filters"
        assert not outcome.forbidden_returned, (
            f"{outcome.question.id} returned forbidden sources {outcome.forbidden_returned}"
        )


def test_retrieved_context_stays_bounded(report):
    assert report.metrics()["median_context_tokens"] <= GATES["median_context_tokens"][1]


def test_duplicate_rate_is_within_the_gate(report):
    assert report.metrics()["duplicate_rate"] <= GATES["duplicate_rate"][1]


def test_hybrid_beats_single_mode_baselines_on_ranking(eval_environment, questions):
    """The claim that hybrid earns its second index, stated so it can fail."""
    reports = evaluate_modes(eval_environment["retriever"], questions, ["hybrid", "dense", "sparse"])
    hybrid = reports["hybrid"].metrics()
    dense = reports["dense"].metrics()
    sparse = reports["sparse"].metrics()

    assert hybrid["recall_at_5"] >= dense["recall_at_5"]
    assert hybrid["ndcg_at_10"] >= dense["ndcg_at_10"]
    # Sparse is the stronger single mode on this corpus -- it is full of exact
    # identifiers. Hybrid has to be at least its equal on ranking quality to
    # be worth running.
    assert hybrid["ndcg_at_10"] >= sparse["ndcg_at_10"] - 0.02
    assert hybrid["mrr"] >= sparse["mrr"] - 0.02


def test_report_renders(eval_environment, questions):
    reports = evaluate_modes(eval_environment["retriever"], questions, ["hybrid"])
    text = format_report(reports)
    assert "retrieval evaluation" in text
    assert "gates (hybrid)" in text
    assert "unsupported-answer rate is not measured" in text


def test_gate_failures_are_reported_not_hidden(report):
    """A gate that is not met must show up in `failed_gates`."""
    metrics = report.metrics()
    for name, (comparison, threshold) in GATES.items():
        value = metrics[name]
        met = value >= threshold if comparison == ">=" else value <= threshold
        assert met == (name not in report.failed_gates), f"{name} reporting is inconsistent"
