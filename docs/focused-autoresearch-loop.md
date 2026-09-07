# Focused Autoresearch Loop

This layer turns the evidence contract into a small decision loop. It is
inspired by alphaXiv's July 2026 reproduction-campaign demonstration: stay on a
few critical experiments, show the dependency tree and every run status,
estimate the expensive stage before execution, and report results claim by
claim. The post is workflow input, not cryptanalytic evidence.

Source: <https://x.com/askalphaxiv/status/2076737985559822734>

## Operating rules

1. Keep at most three critical experiments active; the default is two.
2. Rank candidates by decision impact, falsifiability, mechanism novelty,
   reproduction readiness, and cost efficiency.
3. Every candidate must say what changes after a positive result and after a
   negative result. A test that cannot change a decision is deferred.
4. Resolve routine ambiguities with a deterministic, target-independent rule
   and record the question, resolution, basis, and confidence. Ask for input
   only when no auditable resolution exists.
5. A positive result cannot spawn an expansion until an independent verifier
   has passed. Negative and anomalous receipts remain immutable.
6. Completing one critical experiment triggers reranking before another is
   admitted. Parallel capacity is not a reason to fill the queue.
7. A campaign-level success phrase is decomposed into separately testable
   claims. `reproduced`, `partially_reproduced`, `not_reproduced`,
   `not_attempted`, `open`, and `invalidated` are distinct verdicts.
8. Every reproduced claim cites completed runs and immutable artifacts. Failed,
   cancelled, invalid, running, and planned runs remain in the run table but
   cannot satisfy a claim.
9. Every active or queued experiment records machine memory headroom, optional
   time/CPU/run estimates, dominant cost, complexity hypothesis, sharding plan, and stop
   rule before execution.
10. Scope deviations are attached to the claim they limit. A wording or scope
    correction appends a correction record containing both values and never
    overwrites the prior statement.
11. Correction chains are materialized in order before dependency checks,
    scoring, and selection. Each `prior_value` must match the effective value
    produced by all earlier corrections; stale paths or stale values invalidate
    the queue instead of silently selecting superseded work.

For legacy queues that already folded a correction into the base record, the base
field may equal the chain's final corrected value. The selector still verifies every
internal prior-to-corrected edge and rejects intermediate or unrelated base values.

## Queue v3 attention and cost model

Queue v3 keeps a required attention contract and optional stage estimates on
active or queued candidates:

- `attention_contract` names the decisive evidence, the inconclusive decision,
  the target-independent ambiguity rule, work that is explicitly peripheral,
  and the exact event that triggers reranking;
- `resource_estimate.stages` separates preparation, execution or theorem work,
  evaluation, and receipt packaging when a stage breakdown is useful. Time and
  CPU estimates are advisory and need not match a campaign total. Declared stage
  memory must fit machine headroom; a supplied breakdown names its dominant stage.

This distinction matters because a cheap construction can hide an expensive
evaluation or provenance pass. The selector reports the stage table before any
approved execution and rejects unreconciled estimates.

## Queue v2 evidence model

The v2 queue adds four campaign-level records around the existing focused
candidate list:

- `claims`: a claim-by-claim reproduction matrix with scope, expected and
  observed results, verdict, evidence runs, artifacts, deviations, and blockers;
- `runs`: a dependency-aware table containing planned, running, completed,
  failed, cancelled, and invalid attempts;
- `resource_estimate`: a required preflight on each active or queued candidate;
- `corrections`: an append-only record of prior value, corrected value, reason,
  timestamp, and supporting artifacts.

Candidate dependencies and run dependencies must both be acyclic. Expansion
from a positive parent still requires independent verification. A
`reproduced` claim has the stronger requirement that every cited run is
completed and the claim itself is independently verified.

Expansion edges retain the parent's disposition in the generated graph.
`verified_positive_expansion` is reserved for a verified positive parent;
inconclusive, negative, and untested scope successors are labeled separately.

The selector accepts v1 and v2 queues for replay, but new live queues use
`crypto.autoresearch.focus_queue.v3` and emit
`crypto.autoresearch.focus_plan.v3`.

## Executable queue

`tools/autoresearch_focus.py` validates a JSON queue and emits a hash-bound
focus plan:

```sh
python3 tools/autoresearch_focus.py focus/focus_queue_20260717.json \
  --output focus/current_plan.json \
  --report focus/current_plan.md
python3 -m unittest tools/test_autoresearch_focus.py
```

The queue rejects more than three active experiments, unresolved ambiguity,
unknown or cyclic dependencies, malformed scores, missing attention contracts,
invalid machine limits, claim evidence from noncompleted runs, and
expansion from an unverified positive parent. Completed receipts, the attention
contracts, claim matrix, run graph, estimates, and corrections are copied into
the hash-bound plan.

## Research boundary

The selector optimizes attention, not truth. Its score cannot excuse missing
full-path cost accounting or convert a valid relation into a better-than-rho
algorithm. A small-instance result must state its parameters and transfer
assumptions. A local mathematical identity, a global compiler, relation
collection, blind descent, and an end-to-end rho/Shoup claim belong in separate
claim rows. Existing experiment contracts, controls, immutable artifacts, and
independent verification remain authoritative.

Direction quality is assessed against `docs/target-result-profile.md`, the
canonical profile of a target-class result (exemplar:
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`). The profile defines
exponent-first ambition, formally stated and justified heuristics,
single-responsibility proof decomposition, scale-aware heuristic validation,
and concrete-cost honesty, and provides the checklist used when
ranking candidates by mechanism novelty and decision impact (rule 2) and when
deciding what a positive result may spawn (rule 5). Queue scores rank
attention only; profile conformance is a separate judgment recorded by the
Coordinator, not by the selector.
