# Crypto Autoresearcher Agent Contract

This repository defines a multi-agent operating system for reproducible ECDLP experimentation.

## Roles

- **Coordinator** owns priorities, task decomposition, state transitions, and synthesis.
- **Idea Generator** proposes falsifiable mechanisms and experiments.
- **Executor** implements and runs approved experiments, preserving all artifacts.

Only the Coordinator may change the official status of a hypothesis or research direction.

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

## Required handoff envelope

Every inter-agent task must include:

```yaml
handoff:
  id: TASK-YYYYMMDD-NNN
  from: coordinator
  to: idea-generator | executor
  objective: precise uncertainty to reduce
  inputs: []
  constraints: []
  deliverables: []
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
- stdout and stderr
- raw machine-readable results
- validity status and reason
- timestamps and resource measurements

See `docs/` and `templates/` for the full semantics.