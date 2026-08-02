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
13. A persistent research goal may be marked `completed` only on the concurring judgement of **three independently-resolved models**. See "Goal closure quorum".

## Research-direction integrity and auditability

Research agents must pursue promising paths in good faith. An agent must not
deliberately abandon, suppress, mischaracterize, or steer work away from a
plausible high-value lead in order to derail the research program. This does
not require indiscriminate pursuit: a proposed deprioritization or closure
must name the evidence, budget, test boundary, remaining uncertainty, and a
concrete successor or revisit condition.

The harness monitors this requirement through durable, reviewable decision
records: the candidate or path considered, cited evidence, stated rationale,
ranking or Pareto comparison, action taken, and responsible model/session
provenance. Coordinators and independent reviewers may compare those records
against the ledger, dispatch plan, and later results, and must record a
supported concern about unjustified steering as an auditable finding. Do not
claim to store, infer, or expose private chain-of-thought; only explicit
decision summaries and ordinary research artifacts are retained and reviewed.

## Goal closure quorum

Closing out a goal is the strongest claim the program makes: it asserts that a
declared completion criterion was actually met. One model's judgement is not
enough for that, and neither is one model consulted three times.

A `GOAL-*` record may move to `status: completed` only when its
`completion_quorum.attestations` list carries at least **three** verdicts that
are all `CONCUR` and whose `resolved_model_id` values are **pairwise distinct**.

- Distinctness is on the **resolved** model, never the requested policy alias.
  Three aliases that all fall back to one backend produce correlated judgements;
  counting them three times is not independent agreement, and the validator
  rejects it. This is the failure mode the rule exists to prevent.
- Every attestation sets `independent_session: true`, names the role, records
  `requested_policy` and `resolved_model_id`, and cites the exact record IDs it
  reviewed.
- A single `DISSENT` blocks closure. It is not outvoted; it stands until a new
  Coordinator decision supersedes it on the merits.
- Attestations may be gathered before the transition, but
  `quorum_satisfied: true` on a goal that is not `completed` is an error: only a
  Coordinator ledger archive performs the transition.
- `paused`, `blocked`, and `closed_at_budget` assert no success and need no
  quorum. Retiring a goal that *did* meet a criterion under one of those
  statuses, to avoid the quorum, is a contract violation.

Enforced by `check_goals` in `tools/validate_ledger.py`; failure modes pinned in
`tools/test_goal_closure_quorum.py`. The rule is prospective — goals closed
before it existed are listed in `PRE_QUORUM_GOAL_IDS` and that set must not
grow.

If three distinct models cannot be resolved, the goal does not close. Record the
narrowest supported result and leave it `paused` with a concrete next action —
an unattested closure is worse than an open goal, and a fabricated attestation
is worse than both.

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

## Inventor protocol

The target profile above governs *what kind of result is worth having*.
`docs/inventor-protocol.md` (adopted 2026-07-28; technique abstract:
`knowledge/techniques/KN-TECH-056.md`) governs *how the search is run and how
it is allowed to end*. It binds the Idea Generator, Validator, and Red Team,
and adds nothing that relaxes the core rules. Four obligations:

- **Premature closure is a failure mode symmetric with overclaiming.** No role
  may decline to generate on the grounds that a target is exhaustively
  studied. "This space is mined" is a hypothesis about the search.
- **Closure standard.** A negative result claiming a lane is dead needs a
  named obstruction, an argument, and forward guidance naming what remains
  open. A count of screened-and-rejected mechanisms is a fatigue report and
  its honest status is `unverified`. This applies to the program's own
  standing saturation conclusions.
- **Controls before belief.** Any reported signal is an artifact until the
  identical measurement has been run against a null object of the same shape.
  A quantity that fails to decay when the parameter meant to destroy it
  increases is the canonical artifact tell. This extends rule 3 from
  infrastructure failures to statistical ones.
- **Pareto honesty in every deliverable.** Ideation and closure sessions carry
  `dominated_by` (settable to `null` only after checking every row of the
  frontier across time, memory, and data/queries) and a quantitative
  `sota_delta`. An unchecked `null` is a fabrication under rule 5.

Section 8 of the protocol (adopted 2026-08-01; technique abstract:
`knowledge/techniques/KN-TECH-080.md`) adds the **proof-architecture
portfolio** and extends the binding to the **Coordinator**, which is where the
protocol first gains a gate that can refuse work:

- A proof-oriented proposal — a theorem, asymptotic bound, certificate family,
  reduction, or closure argument — carries a `proof_search_map`
  (`templates/research-records.md`) before it is dispatched, and the
  Coordinator does not approve implementation or expensive experiments
  without one.
- The map's four audits (exact baseline reproduction, observation-collision
  search, quantifier-order statement, method ceiling with a nearby-object
  control) are deliberately cheap and run before compute. An audit that does
  not apply records why; it is not silently omitted.
- This is a falsification aid, not a new claim tier. A failed audit is
  frequently the useful result, and passing every audit still asserts nothing
  beyond what rules 4 and 6 already allow.

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

A branch is kept current with its base by **merging** the base into it.
Rebasing a branch that carries pushed run records is forbidden: it rewrites the
commits those records were archived in, and a run receipt whose commit no
longer exists is not reproducible. `tools/sync_open_branches.py` performs this
merge periodically for open pull requests and validates the merged tree before
pushing it. It never resolves a conflict: when a sync conflicts inside a ledger
record, run artifact, or knowledge entry, the resolution is a new superseding
record under a new id — the same rule as any other correction — and never an
edit that picks one side.

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
