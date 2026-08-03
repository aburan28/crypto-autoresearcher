"""Retrieval evaluation harness.

Measures the retrieval layer against a curated question set, per category and
overall, and compares hybrid against dense-only and sparse-only baselines. The
point of the baselines is falsifiability: hybrid retrieval costs a second
index and a fusion step, and the claim that it is worth that has to be
checkable rather than assumed.

Two honest limits are stated in the output rather than papered over:

* **Unsupported-answer rate is not measured here.** It is a property of an
  answer, and this harness never generates one. What is measured is the
  retrieval-side precondition -- whether the passages needed to support an
  answer were returned at all.
* **A recall figure is only as good as its labels.** ``required_sources`` is
  hand-labelled, so a question whose true answer is in an unlabelled document
  scores as a miss. The number is a floor, not an estimate.
"""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from crypto_kb.models import ClaimStatus, SearchFilters, SearchResponse, SourceType
from crypto_kb.text import count_tokens

#: Plan Phase 12 gates. Kept as data so a failing gate is a reported number
#: rather than an argument.
GATES: dict[str, tuple[str, float]] = {
    "exact_identifier_recall_at_5": (">=", 0.95),
    "general_recall_at_5": (">=", 0.80),
    "filter_correctness": (">=", 1.0),
    "source_attribution": (">=", 0.95),
    "duplicate_rate": ("<=", 0.15),
    "median_context_tokens": ("<=", 5000),
}

#: Categories treated as exact-identifier lookups for gate purposes.
EXACT_CATEGORIES = frozenset({"exact-lookup", "mathematical-notation"})


@dataclass
class EvalQuestion:
    id: str
    query: str
    category: str = "general"
    required_sources: list[str] = field(default_factory=list)
    allowed_sources: list[str] = field(default_factory=list)
    forbidden_sources: list[str] = field(default_factory=list)
    required_metadata: dict[str, Any] = field(default_factory=dict)
    filters: dict[str, Any] = field(default_factory=dict)
    top_k: int = 8
    #: True when the corpus genuinely cannot answer it. Retrieval should return
    #: nothing relevant, and an agent should say so rather than improvise.
    expect_no_answer: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EvalQuestion":
        known = {f for f in cls.__dataclass_fields__}
        unknown = set(raw) - known
        if unknown:
            raise ValueError(f"question {raw.get('id')}: unknown fields {sorted(unknown)}")
        return cls(**raw)

    def search_filters(self) -> SearchFilters | None:
        if not self.filters:
            return None
        data = dict(self.filters)
        if "source_type" in data:
            data["source_type"] = [SourceType(v) for v in _listed(data["source_type"])]
        if "claim_status" in data:
            data["claim_status"] = [ClaimStatus(v) for v in _listed(data["claim_status"])]
        for key in ("field_type", "primitive", "topics", "curves", "source_id", "experiment_id"):
            if key in data:
                data[key] = _listed(data[key])
        return SearchFilters(**data)


@dataclass
class QuestionOutcome:
    question: EvalQuestion
    response: SearchResponse
    hit_ranks: list[int]
    recall_at_5: float
    recall_at_10: float
    reciprocal_rank: float
    ndcg_at_10: float
    filter_ok: bool
    forbidden_returned: list[str]
    attribution_ok: bool
    duplicate_rate: float
    context_tokens: int
    distinct_sources: int

    @property
    def top_score(self) -> float:
        return self.response.results[0].score if self.response.results else 0.0

    @property
    def passed(self) -> bool:
        if self.question.expect_no_answer:
            # A hybrid search always returns its nearest passages, and that is
            # not a defect: the corpus having nothing relevant is a judgement
            # about the *passages*, which only the reader can make. What is
            # checkable here is that nothing explicitly wrong was surfaced --
            # so these questions gate on forbidden sources, and their top
            # scores are reported to calibrate how weak "no answer" looks.
            return not self.forbidden_returned
        if self.forbidden_returned or not self.filter_ok:
            return False
        if not self.question.required_sources:
            # A filter-only question asserts nothing about *which* documents
            # come back, only that every one of them satisfies the constraint.
            return bool(self.response.results)
        return self.recall_at_5 >= 1.0


@dataclass
class EvalReport:
    mode: str
    outcomes: list[QuestionOutcome]

    # -- aggregate metrics -------------------------------------------------

    def metric(self, name: str) -> float:
        return self.metrics()[name]

    def metrics(self) -> dict[str, float]:
        answerable = [o for o in self.outcomes if not o.question.expect_no_answer]
        exact = [o for o in answerable if o.question.category in EXACT_CATEGORIES]
        general = [o for o in answerable if o.question.category not in EXACT_CATEGORIES]
        constrained = [o for o in self.outcomes if o.question.filters or o.question.forbidden_sources]

        return {
            "questions": float(len(self.outcomes)),
            "recall_at_5": _mean([o.recall_at_5 for o in answerable]),
            "recall_at_10": _mean([o.recall_at_10 for o in answerable]),
            "mrr": _mean([o.reciprocal_rank for o in answerable]),
            "ndcg_at_10": _mean([o.ndcg_at_10 for o in answerable]),
            "exact_identifier_recall_at_5": _mean([o.recall_at_5 for o in exact]),
            "general_recall_at_5": _mean([o.recall_at_5 for o in general]),
            "filter_correctness": _mean([1.0 if o.filter_ok and not o.forbidden_returned else 0.0 for o in constrained]),
            "source_attribution": _mean([1.0 if o.attribution_ok else 0.0 for o in self.outcomes]),
            "duplicate_rate": _mean([o.duplicate_rate for o in self.outcomes]),
            "source_diversity": _mean([float(o.distinct_sources) for o in self.outcomes]),
            "median_context_tokens": float(
                statistics.median([o.context_tokens for o in self.outcomes]) if self.outcomes else 0
            ),
            # Mean top score on questions the corpus cannot answer. Compare it
            # against the answerable mean: if they overlap, score is not a
            # usable signal for "the corpus knows this", which is exactly why
            # the tool documentation tells agents not to read it as one.
            "unanswerable_top_score": _mean(
                [o.top_score for o in self.outcomes if o.question.expect_no_answer]
            ),
            "answerable_top_score": _mean(
                [o.top_score for o in self.outcomes if not o.question.expect_no_answer]
            ),
            "pass_rate": _mean([1.0 if o.passed else 0.0 for o in self.outcomes]),
        }

    def by_category(self) -> dict[str, dict[str, float]]:
        grouped: dict[str, list[QuestionOutcome]] = {}
        for outcome in self.outcomes:
            grouped.setdefault(outcome.question.category, []).append(outcome)
        return {
            category: {
                "questions": float(len(items)),
                "recall_at_5": _mean([o.recall_at_5 for o in items if not o.question.expect_no_answer]),
                "mrr": _mean([o.reciprocal_rank for o in items if not o.question.expect_no_answer]),
                "pass_rate": _mean([1.0 if o.passed else 0.0 for o in items]),
            }
            for category, items in sorted(grouped.items())
        }

    @property
    def failed_gates(self) -> dict[str, tuple[float, str, float]]:
        failures: dict[str, tuple[float, str, float]] = {}
        metrics = self.metrics()
        for name, (comparison, threshold) in GATES.items():
            value = metrics.get(name)
            if value is None or math.isnan(value):
                continue
            if comparison == ">=" and value < threshold:
                failures[name] = (value, comparison, threshold)
            elif comparison == "<=" and value > threshold:
                failures[name] = (value, comparison, threshold)
        return failures

    def failures(self) -> list[QuestionOutcome]:
        return [o for o in self.outcomes if not o.passed]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "metrics": self.metrics(),
            "by_category": self.by_category(),
            "failed_gates": {
                name: {"value": value, "comparison": comparison, "threshold": threshold}
                for name, (value, comparison, threshold) in self.failed_gates.items()
            },
            "failures": [
                {
                    "id": o.question.id,
                    "query": o.question.query,
                    "category": o.question.category,
                    "required_sources": o.question.required_sources,
                    "returned_sources": [r.source_id for r in o.response.results],
                    "forbidden_returned": o.forbidden_returned,
                    "filter_ok": o.filter_ok,
                }
                for o in self.failures()
            ],
        }


# --------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------


def load_questions(path: str | Path) -> list[EvalQuestion]:
    questions: list[EvalQuestion] = []
    seen: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            question = EvalQuestion.from_dict(raw)
            if question.id in seen:
                raise ValueError(f"{path}:{line_number}: duplicate question id {question.id}")
            seen.add(question.id)
            questions.append(question)
    return questions


def evaluate(retriever, questions: Iterable[EvalQuestion], mode: str = "hybrid") -> EvalReport:
    outcomes = [_run_one(retriever, question, mode) for question in questions]
    return EvalReport(mode=mode, outcomes=outcomes)


def evaluate_modes(
    retriever, questions: list[EvalQuestion], modes: list[str]
) -> dict[str, EvalReport]:
    return {mode: evaluate(retriever, questions, mode) for mode in modes}


def _run_one(retriever, question: EvalQuestion, mode: str) -> QuestionOutcome:
    response = retriever.search(
        query=question.query,
        top_k=question.top_k,
        filters=question.search_filters(),
        client="eval",
        mode=mode,
    )
    returned = [result.source_id for result in response.results]

    ranks: list[int] = []
    for required in question.required_sources:
        rank = next((i + 1 for i, source in enumerate(returned) if source == required), None)
        if rank is not None:
            ranks.append(rank)

    required_count = len(question.required_sources)
    recall_5 = (
        len([r for r in ranks if r <= 5]) / required_count if required_count else float("nan")
    )
    recall_10 = (
        len([r for r in ranks if r <= 10]) / required_count if required_count else float("nan")
    )
    reciprocal = 1.0 / min(ranks) if ranks else (0.0 if required_count else float("nan"))

    forbidden = [s for s in returned if s in set(question.forbidden_sources)]
    filter_ok = _filters_respected(question, response)
    attribution_ok = all(
        result.source_id and result.source_uri and result.content_hash
        for result in response.results
    )
    unique_hashes = {result.content_hash or result.chunk_id for result in response.results}
    duplicate_rate = (
        1.0 - len(unique_hashes) / len(response.results) if response.results else 0.0
    )
    context_tokens = sum(count_tokens(result.text) for result in response.results)

    return QuestionOutcome(
        question=question,
        response=response,
        hit_ranks=sorted(ranks),
        recall_at_5=recall_5,
        recall_at_10=recall_10,
        reciprocal_rank=reciprocal,
        ndcg_at_10=_ndcg(ranks, required_count),
        filter_ok=filter_ok,
        forbidden_returned=forbidden,
        attribution_ok=attribution_ok,
        duplicate_rate=duplicate_rate,
        context_tokens=context_tokens,
        distinct_sources=len(set(returned)),
    )


def _filters_respected(question: EvalQuestion, response: SearchResponse) -> bool:
    """Every returned result must satisfy the filters and required metadata.

    Checked against the returned payloads rather than trusting the query
    builder: a filter that silently fails to apply is the failure mode this
    metric exists to catch, and it cannot be caught by inspecting the filter.
    """
    expectations: dict[str, Any] = {**question.filters, **question.required_metadata}
    expectations.pop("superseded", None)
    for result in response.results:
        for field_name, expected in expectations.items():
            actual = getattr(result, field_name, None)
            if actual is None:
                return False
            expected_values = {
                v.value if hasattr(v, "value") else str(v) for v in _listed(expected)
            }
            actual_values = (
                {str(v) for v in actual} if isinstance(actual, list) else {str(actual)}
            )
            if not (expected_values & actual_values):
                return False
    return True


def _ndcg(ranks: list[int], required_count: int, k: int = 10) -> float:
    if not required_count:
        return float("nan")
    gain = sum(1.0 / math.log2(rank + 1) for rank in ranks if rank <= k)
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(required_count, k)))
    return gain / ideal if ideal else 0.0


def _mean(values: list[float]) -> float:
    usable = [v for v in values if not math.isnan(v)]
    if not usable:
        return float("nan")
    return sum(usable) / len(usable)


def _listed(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return [value]


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def format_report(reports: dict[str, EvalReport]) -> str:
    lines: list[str] = []
    modes = list(reports)
    metric_names = [
        "questions",
        "recall_at_5",
        "recall_at_10",
        "mrr",
        "ndcg_at_10",
        "exact_identifier_recall_at_5",
        "general_recall_at_5",
        "filter_correctness",
        "source_attribution",
        "duplicate_rate",
        "source_diversity",
        "median_context_tokens",
        "answerable_top_score",
        "unanswerable_top_score",
        "pass_rate",
    ]

    width = max(len(name) for name in metric_names) + 2
    lines.append("retrieval evaluation")
    lines.append("")
    lines.append("metric".ljust(width) + "".join(mode.rjust(12) for mode in modes))
    lines.append("-" * (width + 12 * len(modes)))
    tables = {mode: report.metrics() for mode, report in reports.items()}
    for name in metric_names:
        row = name.ljust(width)
        for mode in modes:
            row += _fmt(tables[mode].get(name, float("nan"))).rjust(12)
        lines.append(row)

    primary = reports.get("hybrid") or reports[modes[0]]
    lines.append("")
    lines.append(f"gates ({primary.mode})")
    for name, (comparison, threshold) in GATES.items():
        value = primary.metrics().get(name, float("nan"))
        verdict = "FAIL" if name in primary.failed_gates else ("n/a" if math.isnan(value) else "pass")
        lines.append(f"  {name:<34} {_fmt(value):>10}  {comparison} {threshold:<8} {verdict}")

    lines.append("")
    lines.append(f"by category ({primary.mode})")
    for category, values in primary.by_category().items():
        lines.append(
            f"  {category:<24} n={int(values['questions']):<3} "
            f"recall@5={_fmt(values['recall_at_5'])}  pass={_fmt(values['pass_rate'])}"
        )

    failures = primary.failures()
    if failures:
        lines.append("")
        lines.append(f"failing questions ({len(failures)})")
        for outcome in failures:
            returned = ", ".join(dict.fromkeys(r.source_id for r in outcome.response.results)) or "(nothing)"
            if outcome.question.expect_no_answer:
                wanted = "(corpus cannot answer; checked for forbidden sources only)"
            elif outcome.question.required_sources:
                wanted = ", ".join(outcome.question.required_sources)
            else:
                wanted = f"(any result satisfying {outcome.question.filters})"
            lines.append(f"  {outcome.question.id} [{outcome.question.category}] {outcome.question.query}")
            lines.append(f"    wanted:   {wanted}")
            lines.append(f"    returned: {returned}")

    lines.append("")
    lines.append(
        "note: unsupported-answer rate is not measured -- this harness retrieves, it does not "
        "answer. Recall is a floor: it counts only hand-labelled sources."
    )
    return "\n".join(lines)


def _fmt(value: float) -> str:
    if isinstance(value, float) and math.isnan(value):
        return "n/a"
    if float(value).is_integer() and abs(value) >= 10:
        return str(int(value))
    return f"{value:.3f}"
