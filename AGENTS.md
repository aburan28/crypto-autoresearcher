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

Role permissions and model selection are separate concerns, and neither names a
vendor. Permissions come from the role contract; inference requirements come
from `orchestration/model-policies.yaml`; the concrete model that serves a
policy comes from `orchestration/model-bindings.yaml`, resolved by
`orchestration/adapter/`. Full semantics: `docs/inference-backends.md`.

Default policies (capability contracts, not products):

- Coordinator: `coordinator-orchestration-code`.
- Idea Generator and research tasks: `research-deep`.
- Executor: `executor-implementation`.
- Reviewer, Validator, and Red Team: `review-adversarial`, which requires
  `xhigh` reasoning and an independent session.
- Claimed breakthroughs, closure results, and contradictions between validated
  evidence records: `review-breakthrough` at `max`. This is the only policy
  that may never be degraded — no amendment or permission runs it on a backend
  that cannot reach `max`. Ordinary reviews stay on `review-adversarial`;
  paying the top tier for every validator pass would price review out of the
  loop, which is how claims end up unreviewed.

Policy ids are permanent. The pre-2.0 ids (`coordinator-ultra-code`,
`coordinator-sol-max`, `research-sol-max`, `executor-terra`, `review-xhigh`)
are carried forever as aliases so already-committed handoffs keep resolving;
write new handoffs with the canonical ids.

The adapter records the requested policy and the exact resolved model
identifier, and never silently downgrades a requested policy. A substitution
requires `fallback_allowed` in the handoff and is recorded as `fallback_used`
with its reason; accepting a model that misses a stated requirement
additionally requires `degraded_allowed` and a Coordinator-approved
`inference_amendment`, and every gap is recorded in `degraded_requirements`. A
model identifier is unverified configuration until
`python3 -m orchestration.adapter doctor --probe` confirms the backend serves
it; `model_verified` carries that status into every manifest. Critical findings
require an independent `review-adversarial` session and a reviewer that did not
originate the claim.

Runtimes are interchangeable too. Claude Code, an OpenAI-protocol agent CLI,
and this repository's own `api_direct` runtime (`orchestration/agent/`) are
three runtimes over the same role contracts; `orchestration/roles.yaml` holds
each role's authority and tool surface in runtime-neutral terms, and
`tools/check_runtime_bindings.py` fails the build when a runtime's agent
definition drifts from it.

Under `api_direct` the ownership rules below are enforced rather than
requested: a write outside the task's declared `write_scope` is refused and the
refusal is recorded, existing artifacts cannot be overwritten, only allow-listed
commands and read-only git subcommands run, an exhausted step or wall-clock
budget is reported as such and never as a result, and a role whose capabilities
that runtime cannot provide is refused outright rather than run with a reduced
tool surface.

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
12. Any claim proposed as a breakthrough, closure result, or contradiction of established evidence must receive independent `review-breakthrough` review at `max` effort. That review may not be degraded or run on a backend that cannot reach it.

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
  artifact_paths: []
  archived_by: TASK-YYYYMMDD-NNN
  inference:
    policy: coordinator-orchestration-code | coordinator-orchestration |
            research-deep | executor-implementation | executor-mechanical |
            review-adversarial | review-breakthrough
    reasoning_effort: null          # per-task calibration; null = policy default
    fallback_allowed: false
    degraded_allowed: false
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

## Durable research commits

Research is not durable merely because it appears in a working tree, task
handoff, or agent response. The Coordinator must use the dispatcher's
Coordinator-only archival tasks to create and verify commits at two points:

1. A **snapshot commit** follows a producer and commits its exact theory,
   implementation, run, or task-report artifacts before an independent agent
   reviews them.
2. A **ledger commit** follows the required reviews and commits the exact
   evidence, decision, hypothesis-status, and synthesis records before an
   official research-state transition.

Workers do not commit into a shared worktree. Commit tasks run alone, stage
only their declared repository-relative paths, and record a post-commit
receipt. The dispatcher verifies that receipt against Git: the commit must be
reachable from `HEAD`, have the expected parent, change exactly the declared
artifacts, preserve their recorded hashes, and name the task and record IDs.

Every theory, run receipt, validation report, red-team report, persistent-goal
checkpoint, ledger record, and knowledge item must be assigned to exactly one
archival task. A missing, dirty, malformed, or scope-expanding commit blocks
downstream review or promotion; it is an evidence-integrity failure, not a
mathematical result.

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
- requested model policy, backend, and resolved runtime model identifier
- model provenance and whether that identifier has been probe-verified
- reasoning effort, whether fallback was used, and any degraded requirements
- stdout and stderr
- raw machine-readable results
- validity status and reason
- timestamps and resource measurements

See `docs/`, `templates/`, and `docs/inference-backends.md` for the full semantics.
