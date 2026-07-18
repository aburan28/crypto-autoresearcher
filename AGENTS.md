# Crypto Autoresearcher Agent Contract

This repository defines a multi-agent operating system for reproducible ECDLP experimentation.

## Roles

- **Coordinator** owns priorities, task decomposition, state transitions, and synthesis.
- **Idea Generator** proposes falsifiable mechanisms and experiments.
- **Executor** implements and runs approved experiments, preserving all artifacts.
- **Reviewer** independently challenges claims, experiment validity, and proposed state transitions.

Only the Coordinator may change the official status of a hypothesis or research direction.

## Model policy

Role permissions and model selection are separate concerns. Permissions come from the role contract; inference behavior comes from `orchestration/model-policies.yaml`.

Default policies:

- Coordinator: `coordinator-ultra-code` — GPT-5.6 Sol Ultra Code.
- Idea Generator and research tasks: `research-sol-max` — GPT-5.6 Sol Max.
- Executor: `executor-code` — GPT-5.6 Sol Code.
- Reviewer and red team: `review-xhigh` — GPT-5.6 Sol with `xhigh` reasoning.

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
  to: idea-generator | executor | reviewer
  objective: precise uncertainty to reduce
  inputs: []
  constraints: []
  deliverables: []
  inference:
    policy: coordinator-ultra-code | research-sol-max | executor-code | review-xhigh
    fallback_allowed: false
    independent_session_required: false
  budget:
    wall_clock_seconds: null
    memory_gb: null
    maximum_runs: null
  completion_gate: []
```

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
