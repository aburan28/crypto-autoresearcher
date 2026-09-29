"""Offline sparse adapter, deterministic samplers, and exact summary statistics.

EXP-CRYPTO-3759c6 preparation artifact for TASK-20260907-da9b67. Implements
the frozen-interface producer side of spec.sparse_model, spec.nulls,
spec.bootstrap, spec.metrics, and spec.pipeline stage ordering. No index is
written, no scoring is run, and no sample is drawn by this preparation task:
every function that would touch real corpus/query/label data is a frozen
interface raising NotImplementedError, or a pure deterministic function that
this task does not call against real inputs.

This module mirrors — for the frozen 4.1 offline evaluation only — the BM25
implementation pinned in the source packet at commit
5401431c1576bf0e75fac70df1cc54f409ed7c85
(kb/src/crypto_kb/embeddings/sparse.py, kb/src/crypto_kb/text.py), reproduced
here in memory so the study never calls save/stage/ingest/reindex, Qdrant, or
network. It is a *reimplementation from static inspection*, not an import of
the kb package: any drift between this file and the pinned source is an
admission defect to be caught by hash binding in implementation-manifest.yaml
and by the future independent_checker.py review, not silently reconciled.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import re
from enum import Enum
from fractions import Fraction
from typing import Iterable, Optional

# ---------------------------------------------------------------------------
# Sparse model constants (spec.sparse_model) — pinned, not tunable
# ---------------------------------------------------------------------------

K1 = 1.2
B = 0.75
IDENTIFIER_PARTS_WEIGHT = 0.3
_INDEX_MASK = 0xFFFFFFFF

# Tokenizer reproduced from kb/src/crypto_kb/text.py at SOURCE_COMMIT (see
# module docstring). Any future divergence between this pattern set and the
# pinned source is an admission defect, not a silent fix.
_IDENTIFIER = re.compile(
    r"""
      [A-Za-z]+_\{[^}\s]+\}
    | [A-Za-z]+\^\{[^}\s]+\}
    | [A-Za-z]+_[A-Za-z0-9]+
    | [A-Za-z]{2,}\([A-Za-z0-9^,\s]+\)
    | [A-Za-z0-9]+(?:-[A-Za-z0-9]+)+
    | \d{4}/\d{3,5}
    | \d+(?:\.\d+)+
    """,
    re.VERBOSE,
)
_WORD = re.compile(r"[A-Za-z]+|\d+")
_STOPWORDS = frozenset(
    """
    a an and are as at be by for from has have in into is it its of on or that the
    to was were will with this these those we our they their there than then such
    can could may might not but if when which while also been being do does did
    """.split()
)


def search_terms(text: str) -> list[str]:
    """Identifiers whole plus decomposed words, stopwords dropped (pinned tokenizer)."""
    terms: list[str] = []
    spans: list[tuple[int, int]] = []
    for match in _IDENTIFIER.finditer(text):
        token = match.group(0).lower()
        if len(token) > 1:
            terms.append(token)
            spans.append(match.span())
        terms.extend(w.lower() for w in _WORD.findall(match.group(0)))
    covered: set[int] = set()
    for start, end in spans:
        covered.update(range(start, end))
    for match in _WORD.finditer(text):
        if match.start() in covered:
            continue
        word = match.group(0).lower()
        if word in _STOPWORDS:
            continue
        terms.append(word)
    return [t for t in terms if t]


def weighted_terms(text: str, part_weight: float = IDENTIFIER_PARTS_WEIGHT) -> dict[str, float]:
    """Whole identifiers and words at weight 1, identifier parts at part_weight."""
    weights: dict[str, float] = {}
    spans: list[tuple[int, int]] = []
    for match in _IDENTIFIER.finditer(text):
        token = match.group(0).lower()
        if len(token) > 1:
            weights[token] = weights.get(token, 0.0) + 1.0
            spans.append(match.span())
        for word in _WORD.findall(match.group(0)):
            key = word.lower()
            weights[key] = weights.get(key, 0.0) + part_weight
    covered: set[int] = set()
    for start, end in spans:
        covered.update(range(start, end))
    for match in _WORD.finditer(text):
        if match.start() in covered:
            continue
        word = match.group(0).lower()
        if word in _STOPWORDS:
            continue
        weights[word] = weights.get(word, 0.0) + 1.0
    return weights


def term_index(term: str) -> int:
    """Pinned blake2b four-byte index (spec.sparse_model.numeric_and_hash)."""
    digest = hashlib.blake2b(term.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big") & _INDEX_MASK


@dataclasses.dataclass(frozen=True)
class SourceStatistics:
    """Source-level document frequency table (spec.sparse_model.statistics).

    D equals the full admitted literature document count; length is per
    title/abstract document; average is max(total_length/D, 1). Path filters
    restrict return eligibility, not these global statistics. Constructed
    from a real admitted corpus by the future admission pass; not
    instantiated by this preparation task.
    """

    doc_count: int
    total_length: int
    document_frequency: dict[str, int]

    @property
    def average_length(self) -> float:
        if self.doc_count == 0:
            return 1.0
        return max(self.total_length / self.doc_count, 1.0)

    def idf(self, term: str) -> float:
        df = self.document_frequency.get(term, 0)
        value = math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))
        return max(value, 0.01)


@dataclasses.dataclass(frozen=True)
class SparseVector:
    indices: tuple[int, ...]
    values: tuple[float, ...]


def embed_document(text: str, stats: SourceStatistics) -> SparseVector:
    """document_weight = tf*2.2/(tf+1.2*(0.25+0.75*sum(weighted_terms)/average_length))
    (spec.sparse_model.document_weight, k1=1.2, b=0.75). Six-decimal rounding
    on individual vector components (spec.sparse_model.numeric_and_hash).
    """
    weights = weighted_terms(text)
    if not weights:
        return SparseVector(indices=(), values=())
    length = sum(weights.values())
    avgdl = stats.average_length
    norm = K1 * (1.0 - B + B * length / avgdl)
    seen: dict[int, float] = {}
    for term, tf in weights.items():
        weight = tf * (K1 + 1.0) / (tf + norm)
        index = term_index(term)
        seen[index] = seen.get(index, 0.0) + weight
    indices = tuple(seen.keys())
    values = tuple(round(v, 6) for v in seen.values())
    return SparseVector(indices=indices, values=values)


def embed_query(text: str, stats: SourceStatistics) -> SparseVector:
    """query_weight = idf*(1+log(w) if w>1 else w) (spec.sparse_model.query_weight)."""
    seen: dict[int, float] = {}
    for term, weight in weighted_terms(text).items():
        scaled = 1.0 + math.log(weight) if weight > 1.0 else weight
        index = term_index(term)
        seen[index] = seen.get(index, 0.0) + stats.idf(term) * scaled
    indices = tuple(seen.keys())
    values = tuple(round(v, 6) for v in seen.values())
    return SparseVector(indices=indices, values=values)


def sparse_dot(a: SparseVector, b: SparseVector) -> float:
    """Pinned sparse dot product over shared indices (spec.sparse_model.numeric_and_hash)."""
    b_map = dict(zip(b.indices, b.values))
    total = 0.0
    for idx, val in zip(a.indices, a.values):
        if idx in b_map:
            total += val * b_map[idx]
    return total


def positive_score_top_k(
    scores: dict[str, float],
    k: int,
    lexical_order: Iterable[str],
) -> list[str]:
    """First k strictly positive sparse-score documents in descending score
    order, ties by lexical canonical path order (spec.arms.title_abstract_sparse20,
    spec.sparse_model.zero_scores). Zero/negative scores never fill K; a truly
    empty positive set is the empty return, distinctly reported. This is a
    pure ranking function over already-computed scores; it is not invoked by
    this preparation task against real corpus scores.
    """
    lexical_index = {doc_id: i for i, doc_id in enumerate(lexical_order)}
    positive = [(doc_id, score) for doc_id, score in scores.items() if score > 0]
    positive.sort(key=lambda pair: (-pair[1], lexical_index.get(pair[0], len(lexical_index))))
    return [doc_id for doc_id, _ in positive[:k]]


# ---------------------------------------------------------------------------
# Deterministic null sampler (spec.nulls.sampling)
# ---------------------------------------------------------------------------

def _u32_be(value: int) -> bytes:
    return value.to_bytes(4, "big", signed=False)


def _u64_be(value: int) -> bytes:
    return value.to_bytes(8, "big", signed=False)


def _length_prefixed_utf8(s: str) -> bytes:
    encoded = s.encode("utf-8")
    return _u32_be(len(encoded)) + encoded


NULL_DOMAIN = "RECALL3759/null"
BOOTSTRAP_DOMAIN = "RECALL3759/bootstrap"


def null_sample_index(proposal_id: str, seed: int, slot_j: int, doc_count: int) -> tuple[int, int]:
    """Rejection-sampled uniform index in [0, doc_count) for one null slot.

    SHA256 over: length-prefixed domain "RECALL3759/null", length-prefixed
    proposal_id, u64 seed, u32 slot_j, u64 rejection counter c (spec.nulls.sampling,
    spec.nulls.byte_encoding). Returns (index, rejection_count). D=0 must never
    reach this function (checked by the caller per spec.nulls.byte_encoding);
    this pure function is not invoked against real proposal IDs by this
    preparation task.
    """
    if doc_count <= 0:
        raise ValueError("doc_count must be positive; D=0 prevents sampling (spec.nulls.byte_encoding)")
    threshold = (2**256 // doc_count) * doc_count
    counter = 0
    while True:
        payload = (
            _length_prefixed_utf8(NULL_DOMAIN)
            + _length_prefixed_utf8(proposal_id)
            + _u64_be(seed)
            + _u32_be(slot_j)
            + _u64_be(counter)
        )
        digest = hashlib.sha256(payload).digest()
        h = int.from_bytes(digest, "big")
        if h < threshold:
            return h % doc_count, counter
        counter += 1


def bootstrap_resample_index(resample_index: int, draw_index: int, proposal_count: int, seed: int = 20260904) -> tuple[int, int]:
    """Rejection-sampled uniform proposal index in [0, proposal_count) for one
    bootstrap draw. SHA256 over: length-prefixed domain "RECALL3759/bootstrap",
    u64 seed, u32 resample_index, u32 draw_index, u64 rejection counter — no
    proposal-ID field (spec.bootstrap.sampler). Not invoked against a real
    proposal population by this preparation task.
    """
    if proposal_count <= 0:
        raise ValueError("proposal_count must be positive (fewer than two clusters is NA per spec.bootstrap.interpretation)")
    threshold = (2**256 // proposal_count) * proposal_count
    counter = 0
    while True:
        payload = (
            _length_prefixed_utf8(BOOTSTRAP_DOMAIN)
            + _u64_be(seed)
            + _u32_be(resample_index)
            + _u32_be(draw_index)
            + _u64_be(counter)
        )
        digest = hashlib.sha256(payload).digest()
        h = int.from_bytes(digest, "big")
        if h < threshold:
            return h % proposal_count, counter
        counter += 1


# ---------------------------------------------------------------------------
# Exact fraction statistics (spec.metrics, spec.nulls.margin, spec.bootstrap)
# ---------------------------------------------------------------------------

class ClusterSensitivityLabel(str, Enum):
    UNDEFINED = "undefined"                     # P < 2
    LIMITED_CLUSTER_SENSITIVITY = "limited_cluster_sensitivity"  # 2 <= P < 10
    STANDARD = "standard"                        # P >= 10


def micro_hit_rate(hits: int, denominator: int) -> Optional[Fraction]:
    """Exact micro rate as a Fraction; NA (None) if the denominator is empty
    (spec.metrics.denominator_policy: empty strata are NA, not zero)."""
    if denominator == 0:
        return None
    return Fraction(hits, denominator)


def signed_paired_delta(sparse_hits: int, boolean_hits: int, denominator: int) -> Optional[Fraction]:
    """sparse20 minus boolean20 on the identical common pair set; NA if the
    common set is empty (spec.metrics.paired_comparison, denominator_policy)."""
    if denominator == 0:
        return None
    return Fraction(sparse_hits - boolean_hits, denominator)


def null_margin_satisfied(observed_rate: Fraction, null_rate: Fraction) -> tuple[bool, bool]:
    """R>=3*q AND R-q>=0.20, exact rational comparisons (spec.nulls.margin).
    Returns (factor_three_ok, absolute_margin_ok); both must hold for the
    declared descriptive margin.
    """
    factor_three_ok = observed_rate >= 3 * null_rate
    absolute_margin_ok = (observed_rate - null_rate) >= Fraction(20, 100)
    return factor_three_ok, absolute_margin_ok


def cluster_sensitivity_label(proposal_count: int) -> ClusterSensitivityLabel:
    if proposal_count < 2:
        return ClusterSensitivityLabel.UNDEFINED
    if proposal_count < 10:
        return ClusterSensitivityLabel.LIMITED_CLUSTER_SENSITIVITY
    return ClusterSensitivityLabel.STANDARD


def nearest_rank_percentiles(sorted_values: list[Fraction]) -> tuple[Fraction, Fraction]:
    """One-based order statistics 50 and 1950 of 2000 sorted nondecreasing
    values (spec.bootstrap.percentile_rule). No interpolation. Caller is
    responsible for supplying exactly 2000 sorted values from a real
    bootstrap run; this preparation task performs no resampling.
    """
    if len(sorted_values) != 2000:
        raise ValueError("expected exactly 2000 shared cluster resample slots (spec.bootstrap.resamples)")
    return sorted_values[49], sorted_values[1949]  # 1-based 50th, 1950th -> 0-based 49, 1949


# ---------------------------------------------------------------------------
# Pipeline stage ordering (spec.pipeline.invocation)
# ---------------------------------------------------------------------------

class Stage(str, Enum):
    CONTROLS = "controls"
    NULL_MEMBERSHIP = "null_membership"
    POSITIVE_RESULTS = "positive_results"


STAGE_ORDER: tuple[Stage, ...] = (Stage.CONTROLS, Stage.NULL_MEMBERSHIP, Stage.POSITIVE_RESULTS)


class StageOrderViolation(Exception):
    pass


@dataclasses.dataclass
class StageGate:
    """Enforces spec.pipeline.invocation ordering within one seed invocation:
    run all six mechanical obligations first and write their report; then
    construct label-blind returned sets and write/hash the null
    membership/semantic-stratum report before joining positive reference
    labels; then write positive arm metrics, paired deltas, failed terms and
    ranks. A failed control invalidates the evaluator and blocks all later
    stages for that invocation (spec.controls.report_order).

    This gate object can be exercised by unit-level self-tests of its
    ordering logic without touching real corpus/label/query data (source-only
    static inspection is permitted); it is not driven against real invocation
    data by this preparation task.
    """

    completed: list[Stage] = dataclasses.field(default_factory=list)
    controls_passed: Optional[bool] = None

    def advance(self, stage: Stage) -> None:
        expected_index = len(self.completed)
        if expected_index >= len(STAGE_ORDER) or stage != STAGE_ORDER[expected_index]:
            raise StageOrderViolation(
                f"expected stage {STAGE_ORDER[expected_index] if expected_index < len(STAGE_ORDER) else 'none (all complete)'}, got {stage}"
            )
        if stage != Stage.CONTROLS and self.controls_passed is not True:
            raise StageOrderViolation("controls must pass before null/positive stages")
        self.completed.append(stage)

    def record_controls_result(self, passed: bool) -> None:
        self.controls_passed = passed


# ---------------------------------------------------------------------------
# Failure capture / checkpoint interfaces (spec.runtime.failure_capture, .resume)
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class LaunchRecord:
    """Written before setup, in an exclusive attempt directory
    (spec.runtime.failure_capture). Fields only; not constructed by this task."""

    attempt_id: str
    seed: int
    commit: str
    started_at_utc: str
    pid: int


@dataclasses.dataclass(frozen=True)
class ReceiptRecord:
    """Written on catchable exit only (spec.runtime.failure_capture). A
    missing receipt after SIGKILL remains an incomplete attempt, never a
    negative_observation. Fields only; not constructed by this task."""

    attempt_id: str
    exit_status: str
    stages_completed: tuple[Stage, ...]
    wall_seconds: float


@dataclasses.dataclass(frozen=True)
class CheckpointRecord:
    """Persist hashes, completed inventory/control/null/treatment stage
    boundaries and counters (spec.runtime.resume). Resume uses the same
    frozen seed and query order in a new exclusive attempt; no favorable
    restart, seed replacement, or index write. Fields only; not constructed
    by this task."""

    stage_boundaries: dict[str, int]
    content_hashes: dict[str, str]
    remaining_work: str


def exclusive_attempt_directory_name(seed: int, attempt_ordinal: int) -> str:
    """Deterministic naming for an exclusive attempt directory; does not
    create or reserve any directory. Real attempt-directory creation and
    exclusivity locking is future admission/runner work, not this
    preparation task."""
    return f"seed-{seed}-attempt-{attempt_ordinal:03d}"
