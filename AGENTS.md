# Crypto Autoresearcher Agent Contract

This repository defines a multi-agent operating system for reproducible ECDLP experimentation.

## Roles

- **Coordinator** owns priorities, task decomposition, state transitions, and synthesis.
- **Idea Generator** proposes falsifiable mechanisms and experiments.
- **Executor** implements and runs approved experiments, preserving all artifacts.
- **Reviewer** independently challenges claims, experiment validity, and proposed state transitions.
- **Validator** independently checks run integrity, controls, and stated metrics.
- **Red Team** tries to falsify the interpretation, cost model, and scope of a
  proposed conclusion.

Only the Coordinator may change the official status of a hypothesis or research direction.

## Model policy

Role permissions and model selection are separate concerns. Permissions come from the role contract; inference behavior comes from `orchestration/model-policies.yaml`.

Default policies:

- Coordinator: `coordinator-ultra-code` — GPT-5.6 Sol Ultra Code.
- Idea Generator and research tasks: `research-sol-max` — GPT-5.6 Sol Max.
- Executor: `executor-terra` — GPT-5.6 Terra.
- Reviewer, Validator, and Red Team: `review-xhigh` — GPT-5.6 Sol with
  `xhigh` reasoning.

The runtime adapter must record both the human-readable policy alias and the exact resolved model identifier. It must never silently downgrade a requested policy. Critical findings require an independent review session using `review-xhigh` and a reviewer that did not originate the claim.

## Core rules

1. Separate speculation, implementation, observation, and conclusion.
2. Every hypothesis must state a mechanism, predictions, test boundary, and falsification criteria.
3. Every experiment must define controls, metrics, budgets, stopping rules, and required artifacts before execution.
4. Results are immutable records. Corrections create new records.
5. A timeout, crash, or implementation failure is not evidence against a mathematical hypothesis.
6. Negative evidence closes only the exact tested scope.
7. Toy-curve evidence must never be presented as crypto-scale validation.
8. Unexpected observations must be recorded, not silently discarded.
9. Agents must not fabricate commands, outputs, timings, statistics, citations, or successful runs.
10. Every conclusion must cite the experiment IDs and artifacts that support it.
11. An agent may request a stronger policy but may not silently alter its own model or reasoning level.
12. Any claim proposed as a breakthrough, closure result, or contradiction of established evidence must receive independent `review-xhigh` review.

## Required handoff envelope

Every inter-agent task must include:

```yaml
handoff:
  id: TASK-YYYYMMDD-NNN
  from: coordinator
  to: idea-generator | executor | reviewer | validator | red-team
  objective: precise uncertainty to reduce
  inputs: []
  constraints: []
  deliverables: []
  inference:
    policy: coordinator-ultra-code | research-sol-max | executor-terra | review-xhigh
    fallback_allowed: false
    independent_session_required: false
  budget:
    wall_clock_seconds: null
    memory_gb: null
    maximum_runs: null
  completion_gate: []
```

## Dynamic dispatch

Use `tools/research_dispatch.py` to turn approved handoffs into a bounded,
artifact-driven dispatch plan. The dispatch queue is a coordination record, not
evidence: raw run receipts remain immutable in their experiment directories.

- The Coordinator is the only role that may change official research status or
  edit shared ledgers.
- Each dispatched task owns non-overlapping repository-relative `write_scope`
  paths. Agents write their reports beneath their assigned task directory;
  they do not concurrently edit a shared hypothesis, experiment, or ledger.
- A task becomes eligible only after every dependency has a `completed` receipt.
  A failed, invalid, or cancelled dependency blocks its successors until the
  Coordinator creates a scoped repair or successor task.
- Keep at most three concurrent subagent tasks. Reserve an independent
  Reviewer, Validator, or Red Team task whenever a result could change an
  ECDLP claim.
- The Executor records observations only. A Reviewer challenges claims, a
  Validator verifies artifact and control integrity, and a Red Team writes
  objections and falsification routes. The Coordinator alone may promote,
  reject, or expand a research direction.
- On each terminal receipt, regenerate the dispatch plan before admitting
  further work. Do not fill capacity merely because a slot is free.

## Research states

Hypotheses move through:

`proposed -> specified -> approved -> running -> analyzed -> replicated -> supported | weakened | rejected | inconclusive | superseded`

Experiments move through:

`draft -> review_required -> approved -> running -> completed | failed_infrastructure | invalid -> analyzed -> archived`

State transitions must include a decision record with rationale and evidence references.

## Artifact policy

Each run must retain:

- exact command
- git commit and dirty-tree state
- environment and dependency versions
- input parameters and random seeds
- requested model policy and resolved runtime model identifier
- reasoning effort and whether fallback was used
- stdout and stderr
- raw machine-readable results
- validity status and reason
- timestamps and resource measurements

See `docs/`, `templates/`, and `orchestration/model-policies.yaml` for the full semantics.
