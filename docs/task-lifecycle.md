# Research Task Lifecycle

## 0. Persistent goal binding

For a sustained campaign, the Coordinator creates or resumes a
`ledger/goals/GOAL-<AREA>-<tok>.yaml` record before intake, where `<tok>` is
the random six-hex value emitted by
`python3 tools/allocate_id.py --next goal --area AREA` and confirmed with
`--check`. Existing three-digit goal IDs remain valid legacy records and are
resumed under their exact immutable IDs; they are never renamed for style. The
record binds the objective to its research questions, completion criteria,
pause conditions, budget, batch queue, latest verified commit, and exactly one
next action. The initial goal checkpoint is committed before work begins.

## 1. Intake

The Coordinator records a research question with scope, motivation, constraints, and the decision it is intended to inform.

The question enters the executable focus queue before experiment design. The
queue admits at most three active critical experiments and requires explicit
positive, negative, and inconclusive decision branches plus recorded ambiguity
resolutions and excluded peripheral work.

## 2. Ideation

The Idea Generator returns one or more structured proposals. Each proposal must contain a mechanism, predictions, minimal test, falsification criteria, confounders, and interpretation limits.

## 3. Hypothesis specification

The Coordinator converts a selected proposal into a hypothesis. A hypothesis is ready only when its tested scope is explicit and its possible outcomes are distinguishable.

## 4. Experiment design

The Coordinator creates an experiment contract containing:

- input instances;
- controls and baselines;
- independent variables;
- primary and secondary metrics;
- seed and replication strategy;
- resource budget;
- stage-by-stage wall-clock, CPU, memory, and sharding estimates;
- stopping and invalidation rules;
- success and falsification criteria;
- required artifacts.

The experiment enters `review_required` until these fields are complete.

## 5. Approval and handoff

The Coordinator approves the frozen protocol and sends it to the Executor. Protocol changes after approval require a versioned amendment. Exploratory changes must be labeled exploratory and cannot be evaluated against the original confirmatory criterion.

The Coordinator also records a bounded task card in the dispatch queue with an
exclusive write scope, resource budget, completion gate, and dependencies. Use
`tools/research_dispatch.py` to select the ready cards. If a producer result
could change a research claim, mark the task `review_required: true` and create
a dependent Reviewer, Validator, or Red Team task before dispatching it.

The Coordinator commits the frozen hypothesis, specification, and handoff by
their exact paths before starting work. A task card must name every artifact it
will produce and the Coordinator-only archive task that will commit it.

## 6. Execution

The Executor creates immutable run records. Each planned run reaches one terminal status:

- `completed_valid`;
- `completed_invalid`;
- `failed_infrastructure`;
- `failed_implementation`;
- `resource_exhaustion`;
- `cancelled_by_budget`.

## 7. Validation

Before analysis, the Executor checks:

- expected run count;
- schema validity;
- duplicated or missing seeds;
- agreement between raw and summarized data;
- control comparability;
- unexpected protocol deviations.

## 7a. Snapshot commit

After a producer reaches a terminal outcome, the Coordinator runs its isolated
snapshot archive task before any dependent review. The task stages only the
declared producer artifacts, creates a commit naming the task and record IDs,
and records the commit, parent, paths, and file hashes. The dispatcher verifies
that receipt against Git. A failed snapshot gate stops the review chain; it is
an evidence-integrity failure, not a negative result.

## 8. Analysis

Analysis must separate:

1. **Observation** — what was measured.
2. **Comparison** — how it differs from the predefined control.
3. **Inference** — what explanations are compatible with the result.
4. **Limitation** — what the experiment cannot establish.

## 9. Coordinator review

The Coordinator assigns an evidence strength and chooses one transition:

- `replicate` — promising or surprising result needs independent confirmation;
- `expand` — test broader instances or parameter ranges;
- `refine` — improve the mechanism or experiment;
- `support` — evidence supports the scoped prediction;
- `weaken` — evidence lowers confidence but is not decisive;
- `reject_scoped` — valid evidence contradicts the exact tested prediction;
- `inconclusive` — data do not discriminate explanations;
- `pause` — low expected information gain relative to cost.

Before a `weaken` or `reject_scoped` transition, the Coordinator seeks the
strongest checkable refutation artifact the result admits — counterexample
certificate, then derivation note, then declared `empirical_only` — and
records it in the evidence record's `proof_status`/`proof_refs`
(`docs/claims-and-verification.md`, "Refutation artifacts"). The artifact is
archived before the decision that relies on it.

The decision record's `knowledge_promotion` field is filled at this step: a
`support` or `reject_scoped` decision backed by `replicated`/`strong`
evidence promotes a `KN-FIND` entry into `knowledge/findings/` (per
`/curate-knowledge`); any other outcome records a concrete `not_warranted`
reason. Proven scoped negatives are promoted like positives — they are the
boundaries future ideation checks against.

## 9a. Ledger commit and official transition

After every required Validator, Reviewer, and Red Team task completes, the
Coordinator runs an isolated ledger archive task. It commits the exact review
reports, analysis, evidence record, decision record, and any hypothesis-status
or knowledge update. The task must pass the post-commit diff-and-hash check
before the Coordinator records an official transition. Workers never race to
commit inside a shared worktree.

## 10. Synthesis

Synthesis statements must reference hypothesis, experiment, run, evidence, and
decision IDs. They must state the tested parameters and distinguish direct
observations from transfer or extrapolation arguments.

## 10a. Goal checkpoint, rerank, and continuation

For an active `GOAL-*`, the Coordinator updates the goal record in the ledger
archive commit with the completed batch, verified commit, decision, and next
action. Only then rerank and schedule the next bounded batch. A scoped negative
result, invalid run, or empty batch ends the affected task but leaves the goal
active unless a declared completion or pause condition is committed.

## Protocol amendments

```yaml
protocol_amendment:
  experiment_id: EXP-...
  version_from: 1
  version_to: 2
  reason: why the original protocol cannot proceed unchanged
  changes: []
  affected_runs: []
  confirmatory_status: preserved | reset | exploratory_only
  approved_by: coordinator
```

An amendment must never retroactively alter raw run records.
