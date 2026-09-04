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
7. Implementations and evidence at any scale are admissible. Records and
   conclusions must state the tested parameters, the actual scope of the
   observation, and any transfer or extrapolation assumptions explicitly;
   scale is a disclosed property of the evidence, not an automatic
   prohibition or validator ceiling.
8. Unexpected observations must be recorded, not silently discarded.
9. Agents must not fabricate commands, outputs, timings, statistics, citations, or successful runs.
   **Every citation carries its provenance** — `recalled | retrieved | kb | internal`
   (`templates/research-records.md`, "Citation provenance"). A `recalled` reference
   comes from the model's own knowledge and no agent in this program has opened it:
   it is a pointer telling a reviewer where to look, never support. It may not back a
   coordinator decision, discharge a heuristic's `supporting_results`, or support
   `novelty_status: known` or `adaptation`, until an agent that actually read the
   source says so in a new record. Naming the nearest work you can recall, hedged and
   marked, is wanted — an unmarked recollection presented as a checked source is the
   violation.
10. Every conclusion must cite the experiment IDs and artifacts that support it.
11. An agent may request a stronger policy but may not silently alter its own model or reasoning level.
12. Any claim proposed as a breakthrough, closure result, or contradiction of established evidence must receive independent `review-breakthrough` review at `max` effort. That review may not be degraded or run on a backend that cannot reach it.
13. A persistent research goal may be marked `completed` only on the concurring judgement of **three independently-resolved models**. See "Goal closure quorum".
14. Every record identifier carries a **random 6-hex suffix**, minted via `python3 tools/allocate_id.py --next <type> --area|--date <x>` and confirmed with `--check` before use — e.g. `DEC-20260802-0edaee`. The legacy `\d{3}` form remains valid forever (those records are immutable) but **no new record may use it**. Never allocate by grepping for `max+1`: that asks committed state for a maximum, every concurrent worktree gets the same answer, and they mint the same identifier for different records — discovered only at merge time when both are already immutable. A random token scans no state and so cannot converge. `--sequential` is legacy-only and must never mint a record that will be merged. Identifiers no longer sort into creation order; use `added`/`recorded_at` or git history for chronology.
15. **An identifier remap is a last resort, not a repair.** Renaming a record that a *completed* archive names in its binding fields (`artifact_paths`, `write_scope`, `archive.path_sha256`, `archive.record_ids`, or the bound commit message) breaks that archive permanently — the commit is immutable, so its declared set and the live tree can never be reconciled. Before any remap, check whether the identifier appears in a completed archive's binding fields; if it does, supersede the record instead of renaming it.
16. **Amazon Bedrock is prohibited as a cost guardrail.** No runtime, agent,
    workflow, fallback, or model probe may select a provider, backend, endpoint,
    or model identifier containing `bedrock` (case-insensitive). Refuse before
    making a network request. API-backed `openai` and `local` runtimes are
    allowed, as are authenticated direct Codex and Claude Code sessions whose
    resolved provider is not Bedrock. Lack of any allowed API or direct runtime
    is a terminal infrastructure stop, never permission to use Bedrock.
    Historical receipts that record prior Bedrock use remain immutable and
    must not be rewritten.

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

## Goal closure quorum — SUSPENDED

> **Status: suspended.** The three-model requirement below is **not currently
> enforced**. A `GOAL-*` record may move to `status: completed` on a committed
> Coordinator decision showing a declared completion criterion was met, with no
> `completion_quorum` block required. The rule, its enforcement code, and its
> tests are retained in full and are restored by setting
> `GOAL_CLOSURE_QUORUM_REQUIRED = True` in `tools/validate_ledger.py`.
>
> **Why.** The rule presumes several backends binding to genuinely different
> models. In the harness as deployed there is one usable backend, so three
> attestations necessarily resolve to one model — which the rule itself defines
> as *not* a quorum. It therefore made `completed` unreachable for every goal
> regardless of research merit, and goals that met their criteria sat `paused`,
> which understates them. Suspending it trades a safeguard for reachability;
> that trade is deliberate and reversible, not a judgement that the safeguard
> was wrong.
>
> **What did not change.** Everything in "What the suspension does not relax"
> below still binds. In particular: never record an attestation you did not
> obtain, and never present a closure as more corroborated than it is. Closing a
> goal is still the strongest claim the program makes; it now rests on the
> Coordinator decision and its cited evidence alone, so that decision carries
> the full weight.
>
> **Restore when** more than one backend resolves — check with
> `python3 -m orchestration.adapter doctor --probe`.

Closing out a goal is the strongest claim the program makes: it asserts that a
declared completion criterion was actually met. One model's judgement is not
enough for that, and neither is one model consulted three times.

**The suspended rule.** A `GOAL-*` record may move to `status: completed` only
when its `completion_quorum.attestations` list carries at least **three**
verdicts that are all `CONCUR` and whose `resolved_model_id` values are
**pairwise distinct**.

- Distinctness is on the **resolved** model, never the requested policy alias.
  Three aliases that all fall back to one backend produce correlated judgements;
  counting them three times is not independent agreement, and the validator
  rejects it. This is the failure mode the rule exists to prevent.
- If three distinct models cannot be resolved, the goal does not close. Record
  the narrowest supported result and leave the goal **`active`** with a recorded
  impediment and a concrete next action — an unattested closure is worse than an
  open goal, and a fabricated attestation is worse than both. (Before
  2026-09-04 this said "leave it `paused`"; pausing is no longer permitted —
  see "Goals are never paused" below.)

### What the suspension does not relax

These bind now, exactly as before:

- Attestations remain fully supported and are still worth recording. When you
  do record one it is a claim that a review happened, so it must be true:
  **never record an attestation you did not obtain.**
- Every attestation sets `independent_session: true`, names the role, records
  `requested_policy` and `resolved_model_id`, and cites the exact record IDs it
  reviewed. The validator still checks all of this whenever a
  `completion_quorum` block is present.
- A single `DISSENT` blocks closure. It is not outvoted; it stands until a new
  Coordinator decision supersedes it on the merits. This is ordinary
  self-consistency rather than part of the quorum: having obtained a dissent,
  closing anyway is incoherent at any quorum size.
- Attestations may be gathered before the transition, but
  `quorum_satisfied: true` on a goal that is not `completed` is an error: only a
  Coordinator ledger archive performs the transition.
- `closed_at_budget` and `cancelled` assert no success. Retiring a goal that
  *did* meet a criterion under one of those statuses, to understate it, is still
  a contract violation — the suspension removes the reason anyone would.
- A `completed` goal still requires a committed Coordinator decision showing the
  criterion was met. Reachable is not automatic.

Enforced by `check_goals` in `tools/validate_ledger.py`; failure modes pinned in
`tools/test_goal_closure_quorum.py`, whose tests exercise **both** the enforcing
and suspended modes so the rule can be switched back on intact. The rule is
prospective — goals closed before it existed are listed in
`PRE_QUORUM_GOAL_IDS` and that set must not grow.

## Goals are never paused

**A `GOAL-*` record may not take `status: paused` or `status: blocked`.** Both
were removed from the permitted set on user instruction (2026-09-04) and
`tools/validate_ledger.py` refuses them by name, with the remedy in the error
text. `blocked` is refused alongside `paused` on purpose: it is the same idling
under another name, and leaving it available would have made the rule cosmetic.

A campaign that meets an impediment **stays `active`** and records the
impediment, so the harness keeps returning to it rather than parking it. Record
it under an `impediments` list on the goal head, each entry naming:

```yaml
impediments:
  - id: IMP-1
    raised: '2026-09-04'
    condition: which declared pause_conditions item or blocker fired
    what_is_blocked: the exact task, claim, or batch — never "the goal"
    clears_when: a concrete, checkable condition
    recheck: what to run to test it (a command, a doctor probe, a queue render)
    asserts_nothing_about: the science
```

The `pause_conditions` field stays required and keeps its name — its entries are
still the declared list of things that can impede a campaign. What changed is
only their **effect**: triggering one records an impediment; it never changes
the goal's status.

### What this does not relax

"Never pause" is a scheduling rule. It is not permission to close, to promote,
or to lower a bar, and the three guarantees pausing used to carry all survive it:

1. **An impediment is never evidence.** An infrastructure failure, an
   unresolvable backend, or an exhausted budget remains categorically not
   negative mathematical evidence (rule 3) and never a research conclusion.
   Recording it on an active goal does not make it a finding.
2. **An unservable review tier is still not downgradable.** If
   `review-breakthrough` (`degradable: false`) cannot be served, the goal stays
   active and the **claim stays un-promoted**. Substituting `validator` for
   `validator-breakthrough` to get a claim moving is the exact silent downgrade
   the policy layer forbids, and it is no more permitted now than before.
   What is blocked is the claim, not the campaign.
3. **An exhausted budget is still a hard stop on spending.** It does not become
   licence to keep going. The next batch requires a committed Coordinator
   budget decision with a recorded rationale. Never quietly raise a budget to
   keep a campaign turning.

Terminal retirement remains available and unchanged: `completed` on a met
criterion, `closed_at_budget` when the budget ran out without one, `cancelled`
when the campaign is abandoned. Each is a deliberate Coordinator act with a
committed decision — never the automatic response to an impediment.

**The standing temptation this creates.** A goal that can never be parked is a
goal that always looks runnable, and the honest failure mode of this rule is
make-work: dispatching an unranked task against an impeded campaign to keep the
loop turning. That is still forbidden. Never dispatch a task you cannot rank
ahead of doing nothing; an active goal whose every route is impeded is reported
as impeded, with its `recheck`, and the harness moves to the next goal.

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
- **Obstructions are measured, and are re-read as resources.** The named
  obstruction is recorded as the `obstruction` block of
  `templates/research-records.md`: a quantity, its measured value with units
  and error bars, the runs it is read from, and the scope it is claimed over.
  Prose alone does not satisfy the closure standard — an obstruction no later
  reader can compare or re-scope is a verdict, not a datum. Every such block
  carries a `resource_check`: the same indefiniteness, degree growth, or
  density defect that kills one approach is the hypothesis of another, and the
  check asks which theory reads this measurement as an asset. `examined: true`
  with `reading` recording that none was found is a complete answer; an
  unexamined obstruction is incomplete work. `tools/obstruction_registry.py`
  derives the standing set and re-poses the question at every rerank, so an
  obstruction measured under one goal stays visible to the others.
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
  review_plan: null               # required when this handoff opens a
                                  # claim-changing review round
```

## Review architecture

Independence is a property of how a review was *set up*, and it is spent the
moment the setup stops being declared. Every claim-changing review round — one
that can move a hypothesis status, close a lane, or support a headline claim —
runs under a `review_plan` written by the Coordinator **before any reviewer
runs** (`templates/research-records.md`). Five obligations:

- **The Coordinator records its prior first.** What it expects the review to
  find goes in the plan, before any report returns. "Three reviewers concurred"
  and "three reviewers concurred with what the Coordinator already believed"
  are different findings and only a pre-recorded prior separates them. A prior
  the review overturns is one of the most informative results the program can
  produce, and it is unrecoverable if written afterwards.
- **Joints are enumerated and owned.** The claim's load-bearing steps are named
  and each is assigned to exactly one reviewer, with a *worked* attack plan —
  what to build, compute, or vary, and where the Coordinator thinks it breaks.
  Reviewers told only to "review this" converge on whatever is most legible, so
  their agreement measures shared taste rather than coverage. One owner per
  joint buys coverage; an unowned joint is visible before the round instead of
  after the claim ships.
- **Blindness within a round is declared, and lifting it is deliberate.**
  Reviewers may not read each other's reports; each attests to what it read. A
  later hardening round may legitimately let a reviewer see earlier verdicts —
  that is `blindness.lifted_for` with a rationale, never drift.
- **Proves-too-much is a required control.** The argument is run against
  objects for which its conclusion is KNOWN FALSE. This is "controls before
  belief" applied to an argument rather than a measurement: a null object
  detects an artifactual signal, a known-false object detects an artifactual
  proof. An argument that still goes through where its conclusion is false is
  wrong somewhere nobody has read closely enough yet.
- **A load-bearing quantity gets a blind re-derivation.** An agent re-derives
  it from the statement of the quantity and the parameters alone, never reading
  the producer's implementation, notes, or report (`blind_rederivation.
  blind_from`). This is *not* replication: recomputing from the producer's own
  artifacts reproduces a wrong-but-self-consistent implementation faithfully,
  which is exactly the failure mode validation cannot see. Agreement is then
  evidence about the quantity; disagreement localises to one of two named
  implementations.

Reviewers report on their own joints, not on the whole claim: a blinded
reviewer cannot see the other joints by construction, so a whole-claim verdict
from one is an opinion formed from a fraction of the evidence. The Coordinator
composes them. `tools/check_review_independence.py` checks that the composition
rests on the independence it claims — every joint owned, every assigned
reviewer attested, no undeclared sibling reads, and no re-deriver whose
declared sources intersect its `blind_from`.

Departures from the plan go in `procedure_deviations` rather than being quietly
absorbed. Acting before a report returns, reassigning a joint mid-round, or
dropping a control may all be right in the moment; none of them is
self-documenting, and a review protocol that is silently deviated from is worth
less than one that was never declared, because it still reads as rigorous.

## Inter-agent messaging

Sessions run in separate chats, worktrees, containers, and runtimes, and cannot
see each other. `tools/agent_bus.py` carries messages between them as write-once
files under `coordination/bus/`, addressed by role. Full contract:
`docs/inter-agent-messaging.md`.

It is a FEED, not a notification, for the same reason the merge digest is:
sessions are ephemeral, so most sessions that need a message do not exist when
it is sent. Read `inbox --as <addr>` on wake and before reporting done; nothing
is delivered.

Binding limits, which exist so that adding a channel does not create a way
around the rules above:

- **A message never confers authority.** An Executor starts from a frozen
  approved contract at a declared path and refuses without one, whatever an
  inbox says. A status change is a committed ledger record; a message about one
  is a notification that it already happened, never the change itself.
- **A message is never evidence.** Evidence is a run record under
  `experiments/`. Cite IDs in `refs:` and let the reader read the record; a
  message describing a result is hearsay.
- **A message never carries a task.** Real work travels as a `TASK-*` handoff
  envelope through the dispatcher, with a write scope, budget, and completion
  gate. A request that skips those skips all three and is invisible to the
  dispatch plan.
- **Never record an agreement, attestation, or approval you did not obtain.**
  A message quoting an uncommitted decision is a fabrication under core rule 5,
  exactly as an invented run would be.

Bus records are coordination traffic: `validate_ledger.py` does not know about
them, and they are immutable like everything else — a correction supersedes by
reference and never overwrites.

### Two transports, one rule

Messaging exists at two layers, and **every limit above applies identically to
both**:

- **Across sessions** — `tools/agent_bus.py`, durable, any runtime.
- **Within one session** — `SendMessage`, live, between subagents of a single
  Claude Code session. Declared as the `send_messages` optional capability in
  `orchestration/roles.yaml` and held by all five roles on that runtime.

The in-process layer is the *more* dangerous of the two, not the less. A
Coordinator subagent and an Executor subagent in one session can now talk
directly, in real time, with nothing written down — which is precisely the
shape of an approval that never happened. So, restated because the live
transport makes it easy to forget:

- A Coordinator subagent saying "approved" **is not an approval**. Approval is
  a frozen contract at a declared path plus a committed decision record. An
  Executor that cannot find both refuses, no matter who said what in-session.
- A message is not a deliverable. Work product goes to the task directory
  under the assigned `write_scope`; a result that exists only in a peer's
  message never happened.
- Messages leave no auditable trace. Anything that must survive the session —
  a decision, a receipt, a handoff, an objection that bears on a claim — is
  written as a record, and put on the bus if a peer must be told.

Use the live layer for what it is good at: a mid-run blocker, a progress
signal, a clarifying question, steering a long-running peer. Use records for
everything that has consequences.

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
- Concurrent subagent tasks are bounded by the dispatch queue's own declared
  `max_concurrent`, not by a fixed ceiling in this document. The prior fixed
  ceiling of three was REMOVED on the user's EXPLICIT DIRECTION of 2026-08-05
  ("remove the concurrent limit from the code rules"); see
  `tools/research_dispatch.py`'s `MAX_CONCURRENT_CEILING` for the mechanism
  and its restore path. Sizing `max_concurrent` to what the execution
  environment can actually run without degrading is the dispatching
  Coordinator's responsibility, not a rule the tooling enforces for you: see
  GOAL-AES-003 BATCH-002 (`DEC-20260802-b226fb` budget_accounting) for the
  recorded cost of dispatching more producers than a machine had headroom
  for. Reserve an independent Reviewer, Validator, or Red Team task whenever
  a result could change an ECDLP claim.
- Several sessions may work one goal at once. Who holds a task and which
  batches are open are write-once side files, not fields of the shared queue
  or goal head: `tools/goal_lanes.py claim|release` per task and
  `open-lane|close-lane` per batch, read back by
  `tools/research_dispatch.py --claims refs`. Claim a Ready Task before
  launching its subagent and release it on return; another session's live
  claim is listed as `running` and is not yours to start. A second batch on
  the same goal is a second lane on its own branch, editing `goal.yaml` only
  additively inside its own ledger archive. A claim is a pointer, never a
  permission. See `docs/concurrent-goal-lanes.md`.
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
pushing it. Coordinators must routinely fetch and inspect `origin/main` for
new commits—at the start of an active session, before a snapshot or ledger
commit, and before requesting review or merge—and promptly merge those changes
into each open branch. Record the base commit checked and merge outcome in the
task receipt. It never resolves a conflict: when a sync conflicts inside a ledger
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

## Knowledge retrieval policy

`kb/` builds a derived retrieval index over the corpus and exposes it to
Claude Code, Codex, and OpenCode through one read-only MCP server. The index is
derived: object storage and this repository's records remain the source of
truth, and the index can be deleted and rebuilt from them without loss.

Use `search_knowledge` before:

- asserting that an ECDLP avenue has already been tested;
- claiming that an approach is known to fail;
- citing a paper or a prior internal experiment;
- proposing an experiment likely to duplicate earlier work;
- changing an authoritative research conclusion.

Search behavior:

1. Start with 4-6 results.
2. Use exact identifiers where known (`EXP-GGM-001`, `KN-LIT-024`, `P-256`,
   `Theorem 4.3`). An identifier in the query is resolved as an exact lookup and
   placed first.
3. Filter by `field_type` and `source_type`.
4. Call `get_context` only for results that affect the conclusion.
5. Distinguish published claims from internal hypotheses: read `claim_status`,
   `evidence_level`, and `authority`, which rank machine-checked proof >
   reproduced experiment > single-run experiment > peer-reviewed > preprint >
   internal analysis > agent hypothesis.
6. Include source IDs and experiment IDs in the output.
7. Report contradictory sources rather than picking one. Results are capped at
   two passages per source so disagreement stays visible.
8. Do not treat retrieval scores as evidence quality. The evaluation harness
   measures score distributions for answerable and unanswerable questions and
   they overlap; score ranks relevance, not truth.
9. Do not repeatedly retrieve the same query in one task.

Bounds and prohibitions:

- Retrieval never substitutes for the evidence rules in **Core rules**. A
  passage returned by `search_knowledge` is a pointer to a record, not a
  citation in itself; cite the experiment, run, and evidence IDs it carries.
- **A remembered paper is a pointer in exactly the same sense.** Retrieval is
  the instrument that converts one into a citation, and the conversion is
  recorded: an entry moves from `provenance: recalled` to `kb` (resolved
  through this index to a corpus record) or `retrieved` (an agent fetched and
  read the source) only in a new record naming the verifying agent in
  `verified_by`. This is rule 9's second half, and it is the one bound that
  applies to agents holding no retrieval tool at all: they may cite from
  memory, marked, and the burden passes to whoever reviews them.
- Superseded material is excluded by default and is never deleted. Ask for it
  explicitly (`include_superseded`) when auditing a retracted conclusion.
- Absence of a search result is not evidence that something was not tried.
  Recall is measured as a floor, not an estimate, and the index only covers
  what has been staged into the corpus.
- No agent may write to the index. The MCP server exposes no ingestion or
  deletion tool; the write path is the ingestion worker, driven by corpus
  events. Do not add one.
