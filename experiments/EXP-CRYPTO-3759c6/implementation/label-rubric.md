# Label rubric — EXP-CRYPTO-3759c6 (frozen)

Preparation artifact for TASK-20260907-da9b67. This is the frozen relevance
rubric future independent labeling sessions must apply verbatim. **No actual
label is assigned by this document or by this preparation task.** All
assessor/adjudicator identities in `admission-template.json` remain
`"unverified"` until genuinely independent sessions record their own
attestations.

## Scope of a labeling decision

Each unique `(proposal_id, document_id)` pair — whether a direct
known-reference candidate (`ledger/proposals/IDEA-*.yaml` `source_refs`) or a
sampled null slot — receives exactly one of three labels: `relevant`,
`not_relevant`, `unresolved` (spec.labels.passes).

## What the assessor sees (masking, spec.labels.information_need / candidate_record)

**Information-need packet** (from the proposal):
- The proposal's question/claim/mechanism text and its named local technical
  need.
- Excluded: `source_refs`, any recorded query/search terms, novelty
  verdicts, later experiment outcomes, and any retrieval result.

**Candidate-record packet** (from the effective corpus record):
- The effective KN-LIT record's full technical text needed for a relevance
  judgment, under a stable opaque document label (not the real path/ID),
  plus excerpt locators.
- Masked: the pair's selection origin (i.e., whether it came from a
  known-reference candidate or a null draw), any query tokens supplied
  outside that record, scores, ranks, and baseline/arm assignment.

An assessor who can infer selection origin, query terms, scores, or arm
assignment from the packet has received a broken packet; halt and repair the
label-packet construction rather than proceed.

## Two independent passes (spec.labels.passes)

Two independent assessors, working from separately delivered packets with no
communication about a specific pair, each assign one label to every unique
candidate pair and every unique sampled null proposal/document pair.
Duplicate sampled slots reuse that pair's label while retaining sampling
multiplicity in `null-slots.jsonl` (a pair drawn twice is labeled once, but
both slot rows are kept).

## Rubric

### `relevant`
An explicit shared technical problem or mechanism between the proposal's
named need and the candidate record, **or** the candidate record is a
material named baseline/obstruction for that proposal's need — in either
case supported by a local excerpt and its locator. A shared incidental word
or a bare bibliography-style mention is **not** sufficient by itself
(spec.labels.rubric_relevant).

### `not_relevant`
The candidate record does not share an explicit technical problem/mechanism
with the proposal's need and is not a named baseline/obstruction for it, on
the content actually present in the record.

### `unresolved`
Insufficient corpus content, an ambiguous technical relation, or a missing
information need. Missing full-paper access is **not** equated with
`not_relevant`; local-record relevance is never equated with an external
paper's truth or a claim that the full source was read
(spec.labels.rubric_unresolved). Off-topic text may still contain matching
words — a word match alone is never grounds for `relevant`.

## Disagreement and third adjudication (spec.labels.disagreement)

- Matching `relevant`/`not_relevant` labels from the two passes are final.
- Any disagreement between the two passes, or either pass returning
  `unresolved`, routes to a **third, independent adjudicator** who is:
  - blind to the recorded query/search terms and to any retrieval result,
  - blind to the identities of the first two assessors,
  - given the same masked information-need and candidate-record packets.
- The adjudicator records an excerpt-supported decision. Both original
  labels and the adjudicator's rationale are preserved (never overwritten).
- Persisting uncertainty after adjudication remains `unresolved` — it is not
  forced to a binary outcome.

## Exclusion and denominators (spec.labels.exclusion)

Only labels finalized as `relevant` (post first-two-pass agreement or
adjudication) enter the positive denominator used for
`known_reference_micro_hit_rate_*` and the matched sparse-vs-Boolean delta.
`not_relevant` and `unresolved` candidates are separately counted and
retained in `labels-adjudicated.jsonl` — never deleted or silently dropped.
Random null draws are **never** removed because their label turned out
`relevant` or `unresolved`; they remain in the random-entry baseline with
their label recorded (spec.nulls.semantic_labels).

## Freeze and access-attestation (spec.labels.freeze)

Before any label is joined to a returned retrieval set:
1. Commit/hash the label packets as delivered to each assessor
   (`label-packets.jsonl`).
2. Commit/hash first-pass, second-pass, and adjudicated labels separately
   (`labels-pass1.jsonl`, `labels-pass2.jsonl`, `labels-adjudicated.jsonl`).
3. Record a read-access attestation for every assessor and the adjudicator
   in `label-access.json`, using the template below.
4. No relabeling is permitted because an arm later "missed" a target the
   label predicted, or for any other results-driven reason.

### Access-attestation template (per assessor/adjudicator)

```yaml
access_attestation:
  role: first_pass_assessor | second_pass_assessor | third_adjudicator
  session_identity: null            # unverified until a genuinely independent session records it
  independent_of_producer_session: null
  independent_of_other_assessors: null
  packet_hash_received: null        # sha256 of the exact packet this role was given
  blind_to_queries_and_results: null
  blind_to_other_assessor_identities: null   # third_adjudicator only
  attested_at_utc: null
  attestation_statement: null        # verbatim first-person statement, not paraphrased by the producer
```

No field above is populated by this preparation task; every value is `null`
pending a genuinely independent labeling session (spec.execution_gate,
DEC-20260907-b8bd3e.approval_scope.independent_review).

## Agreement reporting (spec.labels.agreement_reporting)

The future admission pass must report, without uncalibrated inter-rater
claims:
- exact two-pass agreement counts and a full cross-tabulation
  (relevant/not_relevant/unresolved × relevant/not_relevant/unresolved),
- disagreement and unresolved rates stratified by proposal and by the
  metadata strata defined in `spec.corpus_views.metadata`
  (title-only/abstract-only/both/neither).

## Study-level adequacy threshold (spec.query_extraction denominator_policy, spec.execution_gate)

At least 50 adjudicated `relevant` unique direct-reference candidate pairs
are required for study-level sample adequacy; report the distinct proposal
count separately. This threshold applies to the full study, never to the
narrower common exact/uncontaminated/BM25-representable matched-delta subset,
which reports its own N/P and is `NA` if empty. Reaching 50 pairs is not a
stopping signal for candidate collection — every candidate remains inventoried
regardless of when the threshold is crossed (spec.candidates.exhaustive_rule).
