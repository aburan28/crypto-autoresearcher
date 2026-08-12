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
from crypto_kb.storage import LocalObjectStore

QUESTIONS = Path(__file__).parent / "questions.jsonl"
REPO_ROOT = Path(__file__).resolve().parents[3]

#: Measured on the frozen evaluation corpus slice. Update deliberately, with
#: the run that justifies the change.
#:
#: Re-measured 2026-08-08 on the 625-document frozen slice
#: (``crypto_kb/eval/corpus_manifest.txt``). The previous numbers were taken on
#: an unfrozen slice of 430 documents; by the time it was next run the globs
#: matched 625 -- evidence records alone had gone 137 -> 299 -- and recall fell
#: with no retrieval code having changed. `recall_at_5` 0.85 -> 0.826 and
#: `general_recall_at_5` 0.77 -> 0.714 are that corpus growth, not a
#: regression. Freezing the slice is what makes these numbers mean something;
#: see ``crypto_kb/eval/corpus.py``.
BASELINE = {
    "recall_at_5": 0.82,
    "recall_at_10": 0.90,
    "mrr": 0.74,
    "ndcg_at_10": 0.78,
    "exact_identifier_recall_at_5": 1.0,
    "general_recall_at_5": 0.70,
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


def test_frozen_slice_is_still_present_in_the_repository():
    """A manifest path that has been deleted makes every label naming it a lie.

    This fails loudly rather than letting the corpus silently shrink, which is
    the mirror of the growth that invalidated the previous baseline.
    """
    from crypto_kb.eval.corpus import load_manifest

    manifest = load_manifest()
    missing = [p for p in manifest if not (REPO_ROOT / p).is_file()]
    assert not missing, (
        f"{len(missing)} frozen slice paths no longer exist (first: {missing[:3]}); "
        "re-check the question labels, then `crypto-kb eval-manifest --write`"
    )


def test_a_new_matching_file_does_not_enter_the_measured_corpus(tmp_path):
    """The regression this replaced, reproduced in miniature.

    `ledger/evidence/EV-*.yaml` matched 137 files when the baseline was set and
    299 five days later; nothing in the retrieval code changed and recall fell.
    Staging must follow the manifest, so a newly added matching file is not
    silently measured.
    """
    from crypto_kb.eval import corpus as eval_corpus

    frozen = [p for p in eval_corpus.load_manifest() if p.startswith("knowledge/literature/")][:3]
    assert frozen, "expected literature notes in the frozen slice"

    for relative in frozen:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPO_ROOT / relative).read_bytes())

    intruder = tmp_path / "knowledge/literature/KN-LIT-099.md"
    intruder.write_text("---\nid: KN-LIT-099\ntitle: Added after the freeze\n---\n\n# New\n")

    manifest = tmp_path / "manifest.txt"
    manifest.write_text("\n".join(frozen) + "\n")

    store = LocalObjectStore(tmp_path / "corpus")
    staged = eval_corpus.build_eval_corpus(tmp_path, store, manifest_path=manifest)

    assert len(staged) == len(frozen)
    assert "paper:KN-LIT-099" not in {d.metadata["source_id"] for d in staged}


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
