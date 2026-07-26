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

## Target result profile

The canonical exemplar of the output this system exists to produce is
Wesolowski's *supersingular isogeny problem in time and memory p^{1/3+o(1)}*
(full text: `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`; analysis:
`docs/target-result-profile.md`, checklist C1–C18; technique abstract:
`knowledge/techniques/KN-TECH-055.md`). All roles bias toward that pattern:

- **Exponent-first ambition**: prefer mechanisms that move the asymptotic
  exponent of a central hard problem over logarithmic-cofactor polishing.
- **Explicit conditional rigor**: results may be conditional, but every
  heuristic is numbered, formally stated, given a random-model justification
  (rigorous bound + classical distribution theorem), and paired with a
  falsification condition and a validation plan. A heuristic-conditional claim
  is never presented as unconditional.
- **Proof architecture**: results decompose into single-responsibility lemmas
  (size bounds, runtime, correctness, success probability) with explicit
  per-attempt-cost × inverse-success-probability bookkeeping.
- **Structural ingredients**: hunt for external theorems, bounds, and
  correspondences that convert a bottleneck step into a tractable one
  (meet-in-the-middle splits, re-randomization with mixing-time justification,
  reduction-network cascades into corollaries).
- **Validation at scale**: every heuristic gets a pre-registered experimental
  validation — distribution-level comparison against the theoretical
  prediction, using correspondence tricks to reach cryptographically relevant
  parameters where direct computation is infeasible.
- **Cost and scope honesty**: every asymptotic claim carries memory beside
  time, disclosure of what hides in o(1)/polylog cofactors, a concrete-cost
  table at standardized parameter sets with optimistic assumptions flagged,
  time–memory tradeoffs, and an explicit affected-vs-safe scope statement.

Before any asymptotic-complexity claim transitions toward `supported`, the
Coordinator verifies the promotion gates in `agents/coordinator.md`: archived
proof decomposition, validated heuristics, concrete-cost table, and
independent `review-xhigh` plus red-team pass. This profile biases direction
and never lowers the evidence rules above.

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
- requested model policy and resolved runtime model identifier
- reasoning effort and whether fallback was used
- stdout and stderr
- raw machine-readable results
- validity status and reason
- timestamps and resource measurements

See `docs/`, `templates/`, and `orchestration/model-policies.yaml` for the full semantics.
