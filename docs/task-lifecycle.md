# Research Task Lifecycle

## 1. Intake

The Coordinator records a research question with scope, motivation, constraints, and the decision it is intended to inform.

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

## 10. Synthesis

Synthesis statements must reference hypothesis, experiment, run, evidence, and decision IDs. They must explicitly distinguish toy-scale, medium-scale, and cryptographic-scale evidence.

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
