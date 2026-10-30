# Crypto Autoresearcher Agent Contract

## Literature first

Before any work, follow [the literature-first rule](docs/agent-contract-extended.md#literature-first). Its prior source review, linked task notes, assumption checks, and explicit evidence-gap requirements are binding for every task.

The normative contract of a multi-agent system for reproducible ECDLP
experimentation: rules, each with its reason. Narratives and full statements:
[`docs/agent-contract-extended.md`](docs/agent-contract-extended.md). Where this
file and another document disagree, this file wins.

Conventions shared with `aburan28/crypto`, `aburan28/cryptanalysis` and
`aburan28/crypto-lean` — object storage, the validation vocabulary, curve
identity, the skill surface and the shared-code parity list — are stated once in
[`docs/lab-contract.md`](docs/lab-contract.md). That file wins on a shared
convention; this file wins on anything specific to this repository, and either
wins over a skill, a runtime file or a generated block.

## Observe first; interpret later

Lead with scoped results and checks, recognize component progress, and pursue
the next technical step. Follow the
[observation and communication rule](docs/agent-contract-extended.md#observe-first-interpret-later)
for evidence, ownership, comparison scope, and the 2026-10-30 rule against
repeated overall-goal verdicts.

## Name the obstruction

When substantial research, cryptanalysis or audit work cannot meet a proof, implementation, experiment or validation requirement, create or update a linked problem record before repeating or handing off the blocked approach. The full [problem-record rule](docs/agent-contract-supplement.md#name-the-obstruction) is binding, including its evidence distinctions, exit criteria, next test and preservation of the original requirement. A problem record alone resolves nothing.

## Budgets: progress first

Research cost estimates are advisory, may be null, and never need repeated user
approval (user, 2026-09-06). Only a committed Coordinator stagnation review (≥
90 days without documented progress; evidence, scope, a next action, an
assessment from the last seven days) may cap spending. Memory/concurrency limits
and justified process watchdogs protect the machine; they are not budget. Fixed
sample counts, locked plans, write scopes, controls, immutable records,
independent review and the Bedrock ban still bind.
`docs/research-budget-policy.md`.

## Entry points

- **`run`** (`plugins/crypto-autoresearcher-harness/skills/run/SKILL.md`, same
  name on every host) is the only public execution skill: it runs existing
  experiment programs and reports outputs after the literature-first review
  required above, adding no other preflight, validation, audit, protocol
  authoring, mandatory review or state transition. The runner's
  own admission, ownership, resource and correctness checks stay; a refused
  launch is reported, never bypassed. Results are observations until
  archive/review says otherwise. `run` may commit and push its run records, then
  its run reports, on its own branch.
- **Runbooks** (`docs/runbook-execution.md`, owner 2026-10-16) let the
  mechanical tier execute: `tools/runbook.py` runs, records and reports, so the
  operator writes no number; `audit-runs` replays a sample it cannot predict.
- **`coordinate`** (`.claude/skills/coordinate/SKILL.md`; Codex/OpenCode adapter
  `.agents/skills/coordinate/`) ranks, designs, approves, reviews, archives and
  publishes; it never launches scientific trials.
  `crypto-autoresearcher-harness`, `launch-research-harness` and
  `coordinate-research-goal` stay retired.

## Skill routing

Use [the workflow map](docs/skill-routing.md) and [route](.claude/skills/route/SKILL.md)
when selecting a recurring analysis, implementation, review or maintenance workflow.
Canonical skills live under `.claude/skills/`; `.agents/skills/` exposes the same
names to Codex/OpenCode. Choose by action first, then load a relevant subject profile.
After the literature-first review above, explicit scientific execution goes
directly to `run`: catalog checks and subject assessment are not launch
prerequisites. This map adds no runtime role or authority.

## Roles

| role | owns | policy |
| --- | --- | --- |
| Coordinator | priorities, decomposition, state transitions, synthesis; alone changes the official status of a hypothesis or direction | `coordinator-orchestration-code` (`coordinator-orchestration` without code) |
| Idea Generator; research tasks | falsifiable mechanisms and experiments | `research-deep` |
| Idea Synthesist | cross-goal ideation | `research-synthesis`, `high` |
| Experiment Director | writes the mechanical tier's runbook and task card, assesses its runs | `director-runbook` |
| Executor | implements and runs approved experiments, keeps every artifact, records observations only | `executor-implementation`; `executor-mechanical` for judgment-free re-runs and approved runbooks |
| Reviewer | challenges claims, validity and transitions | `review-adversarial`, `xhigh`, independent session |
| Validator | run integrity, controls, stated metrics | `review-adversarial`, as Reviewer; `audit-sweep` screens runbook sessions, never a review gate |
| Red Team | tries to falsify interpretation, cost model and scope | `review-adversarial`, as Reviewer |
| Consolidator | carries pointers between lanes, weighing relevance, never correctness; adjudicates nothing | `consolidation-routing`, `high`, independent of the lanes it reads |


Contracts: `agents/*.md`; authority and tools: `orchestration/roles.yaml`;
`tools/check_runtime_bindings.py` fails the build when a runtime's agent
definition drifts from it.

## Visual research record

Every experiment run, evidence review and substantive search for new
isogenies, curves, scalar rules, endomorphisms or related ECDLP mechanisms
leaves a report, a graph or diagram, and a PDF, following the
`research-visuals` skill (`.claude/skills/research-visuals/SKILL.md`, also
`.agents/skills/`), negative, failed and inconclusive work included. A verified
finding or correction updates the affected canonical graph source and
rendering in the same change; if none changes, record what was checked and
why. Label conjectural edges and extrapolations; cite immutable evidence for
verified ones.

## Experiment protocol, export and review

Owner, 2026-10-22. Every experiment, benchmark, sweep or training run in this
repository and its siblings is designed from a frozen `experiment.protocol/v1`
record (`docs/experiment-protocol.md`; skill `experiment-protocol`), leaves
its data as one `experiment.export/v1` bundle beside the raw records, and may
be reviewed by any other runner through a write-once `experiment.review/v1`
record (skill `review-run`). `tools/experiment_protocol.py` checks all three.
A protocol names its controls (A/A, positive, negative) or excuses each, its
variable ledger, randomization and blinding, power, counted metrics with
their resolution, the isolation a clock needs, and the checkpoint policy
under which a restored row keeps its counts and loses its clock. A review is
an input to `review-evidence`, never the decision.

## Standing user authorization

"All is approved. Ideas/experiments should be always approved" (user,
2026-09-06). Never ask the user to select, confirm or reapprove ideas,
protocols or experiments: the Coordinator records approval under this
authorization once a protocol is complete **and approvable** ("Approval is
bounded by execution").
Completeness (controls, metrics, budgets, stopping rules, artifact paths,
dependencies, inference policy, committed handoffs) is the Coordinator's job;
an incomplete protocol is completed or records its impediment, never parked on
the user. Approval asserts nothing about the hypothesis. It covers the five CM
proposals prospectively; immutable artifacts stay as written.

## Model policy

Permissions: the role contract. Inference requirements:
`orchestration/model-policies.yaml`. Serving model:
`orchestration/model-bindings.yaml`, resolved by `orchestration/adapter/`.
None names a vendor (`docs/inference-backends.md`). Each role's policy is in
"Roles".

**Model tiers** (`docs/model-tiers.md`): each policy has a `model_tier`
floor (mechanical < director < core < frontier); the resolver refuses models
below it.

Policy ids are permanent; pre-2.0 aliases (`model-policies.yaml`) resolve
forever; new handoffs use canonical ids. The adapter records requested policy
and resolved model and never silently downgrades: substitution needs
`fallback_allowed` (recorded `fallback_used`); a model missing a stated
requirement also needs `degraded_allowed` and a Coordinator-approved
`inference_amendment`, every gap listed in `degraded_requirements`. A model id
is unverified until `python3 -m orchestration.adapter doctor --probe` confirms
it (`model_verified`). Delivery (`interactive` | `batch` | `auto` with
`deadline_seconds`) is recorded per manifest and changes nothing else; `auto`
never batches urgent work; expired or errored batch results are infrastructure
signal. Single-turn prompts batch through `python3 -m orchestration.adapter
batch …`, with write-once records under `coordination/inference-batches/`
(`docs/batch-inference.md`). Runtimes (Claude Code, OpenAI-protocol CLIs,
`api_direct`) are interchangeable over the same role contracts; `api_direct`
enforces write scope, no-overwrite, command allow-list and budget stops rather
than requesting them.

## Mandatory progress-fidelity gate

Every new quantitative speedup, performance advantage, or ECDLP attack-cost claim MUST carry a machine-readable record in `claims/*.json` passing `python3 -m tools.progress_fidelity validate`. Local subroutine gains must not be presented as end-to-end gains. Such claims require matched baseline/candidate evidence and independent verification; see `docs/progress-fidelity.md`. Missing evidence is unqualified, never inferred. The Coordinator must enforce this for claims in prose as well as code; the `progress-fidelity` CI check must be required by branch protection before merge.

This gate qualifies those claims; it does not require descriptive observations
to assert an advantage or invent a baseline comparison. Report the actual
controls and reference specified by the study, and defer broader interpretation.

## Intermediate-cost and asymmetric-access hypotheses

For assessments of hidden mathematical advantage, follow [the full rule](docs/agent-contract-extended.md#intermediate-cost-and-asymmetric-access-hypotheses). Its scope, cost, secrecy, portfolio, and uncertainty obligations are binding.

## Core rules

1. Separate speculation, implementation, observation and conclusion.
2. A hypothesis states mechanism, predictions, test boundary and falsification
   criteria.
3. An experiment defines controls, metrics, budgets, stopping rules and required
   artifacts before execution.
4. Results are immutable records; corrections are new records.
5. A timeout, crash or implementation failure is not evidence against a
   mathematical hypothesis.
6. Negative evidence closes only the exact tested scope.
7. Evidence at any scale is admissible; records state tested parameters, actual
   scope and every transfer or extrapolation assumption.
8. Unexpected observations are recorded, never silently discarded.
9. Never fabricate commands, outputs, timings, statistics, citations or runs.
   Every citation carries provenance `recalled | retrieved | kb | internal`
   (`templates/research-records.md`); a `recalled` reference is a pointer, never
   support, until an agent that read the source says so in a new record naming
   itself in `verified_by`.
10. Every conclusion cites its supporting experiment IDs and artifacts.
11. An agent may request a stronger policy; it never silently alters its own
    model or reasoning level.
12. A claimed breakthrough, closure result or contradiction of established
    evidence gets independent `review-breakthrough` review at `max`, never
    degraded.
13. Goal closure quorum: suspended (below).
14. New record ids carry a random 6-hex suffix: `python3 tools/allocate_id.py
    --next <type> --area|--date <x>`, then `--check`. Never allocate by grepping
    for `max+1`: concurrent worktrees mint the same id. Legacy `\d{3}` ids stay
    valid; ids do not sort by creation (read `added`/`recorded_at`).
15. Remap identifiers only as a last resort: a record named in a *completed*
    archive's binding fields (`artifact_paths`, `write_scope`,
    `archive.path_sha256`, `archive.record_ids`, bound commit message) is
    superseded, never renamed.
16. **Amazon Bedrock is prohibited**: no runtime, fallback or probe selects a
    provider, endpoint or model id containing `bedrock`; refuse before any
    request. No alternative means a terminal infrastructure stop, never
    permission. The adapter's offline guard enforces it; records carry no
    attestation field for it; historical receipts stay immutable.

## Research-direction integrity

Pursue promising paths in good faith; never abandon, suppress or steer away from
a plausible high-value lead to derail the program. A deprioritization or closure
names evidence, budget, test boundary, remaining uncertainty and a successor or
revisit condition. Decision records (candidate, evidence, rationale, ranking,
action, model/session provenance) are the audit trail; private chain-of-thought
is neither stored nor inferred.

Rank observational work by the question it can clarify, measurement quality,
reproducibility and unresolved uncertainty. Lack of an expected attack advantage
or immediate application is not grounds to dismiss a measurement or stop
presenting its data.

## Goal closure quorum (suspended)

Rule 13 (three `CONCUR` attestations from pairwise-distinct resolved models
before `status: completed`) is **suspended**
(`GOAL_CLOSURE_QUORUM_REQUIRED = False`, `tools/validate_ledger.py`): one
deployed backend makes three attestations one model, which the rule itself
calls no quorum; restore it when `doctor --probe` resolves more than one.
Still binding: `completed` needs a committed Coordinator decision showing a
declared criterion met; never record an attestation you did not obtain; a
recorded `DISSENT` blocks closure; `closed_at_budget` and `cancelled` assert
no success and never understate a met criterion; `PRE_QUORUM_GOAL_IDS` must
not grow. Full statement: `docs/agent-contract-extended.md`.

## Goals are never paused

`paused` and `blocked` are not `GOAL-*` statuses (user, 2026-09-04; refused by
`tools/validate_ledger.py`). An impeded campaign stays `active` and records
`impediments` (`id`, `raised`, `condition`, `what_is_blocked` (a task or
claim, never "the goal"), `clears_when`, `recheck`, `asserts_nothing_about`).
`pause_conditions` keep their name; triggering one records an impediment and
changes no status.

This is a scheduling rule and relaxes nothing: an impediment is never negative
mathematical evidence (rule 5); an unservable `review-breakthrough`
(`degradable: false`) leaves the claim un-promoted, never downgraded to
`validator`. Routine estimates do not stop research: only the exceptional
stagnation policy caps a budget, and a watchdog stop is not campaign
exhaustion. Terminal retirement (`completed`, `closed_at_budget`,
`cancelled`) is a deliberate Coordinator act with a committed decision. A goal
that can never be parked always looks runnable: never dispatch a task you
cannot rank ahead of doing nothing; report an impeded goal with its `recheck`
and move on.

## ECC comes first, and its budget is unlimited

User, 2026-09-04. The ECC area set is declared once in
`orchestration/research-priority.yaml` and read via `tools/ecc_priority.py`
(`--list-areas`, `--classify`, `--open-ideas`, `--budget-violations`); never
infer it from an id prefix.

1. **Unlimited budget.** Active and draft ECC goals have
   `campaign_budget.maximum_batches: null` and
   `total_wall_clock_seconds: null` (validated). `max_concurrent` stays
   bounded: machine headroom. Unlimited removes the batch ceiling, not the
   duty to rank: never dispatch a task you cannot rank ahead of doing nothing.
2. **ECC first, always.** Every selection point considers ECC goals first; a
   non-ECC goal is worked only when no ECC goal offers a ranked, justified
   task. Priority orders the queue, manufactures no work, and lowers no
   evidence bar: ECC results meet the same scope, certificate and claim-tier
   standards.
3. **Open ECC ideas are designed, not shelved.** An open idea is `proposed`
   with no hypothesis or experiment citing it; `/design-experiment` makes it a
   hypothesis and a frozen contract at `approved_by: null` until a committed
   Coordinator decision approves it under the standing authorization.

### Approval is bounded by execution

The approved-unrun capacity cap from 2026-10-07 is removed by user direction
(2026-10-11). `tools/portfolio_kpis.py` reports the backlog for prioritization;
neither its count nor `--capacity` blocks design or approval. An open ECC idea
is ranked and designed when its protocol can be completed. Approval requires:

- **Runnable.** Before approval, require `python3
  tools/experiment_preapproval.py --packet <PACKET.json>` to report
  `approvable: true` for the exact prospective frozen specification, trial
  plan, executor handoff and queue, including committed source/input hashes,
  complete supervisor and trial archive coverage, an execution route, and a
  lawful goal lane. The probe is read-only and grants no execution authority.
  Implementation is the design lane's; a contract that fails this check stays
  `review_required` with its exact blockers recorded. After the Coordinator's
  approval decision and archive are committed, `python3
  tools/newest_experiments.py --experiment <EXP-ID> --json` must report
  `execution_state: ready` before dispatch. A mismatch stops dispatch and
  requires an additive correction.

If a complete contract cannot yet be made runnable, keep it `review_required`
and record the missing launcher in the goal's `next_action`. An approved, unrun
contract is neither evidence nor a failure of its hypothesis. Rank runnable
work ahead of drafting more contracts when it offers a justified next run.

## Research direction

For algorithmic-complexity, inventor-protocol and scheme-construction work, follow the full binding [research-direction rule](docs/agent-contract-supplement.md#research-direction). It states the target profile, proof and cost obligations, controls against premature closure, and security-game requirements. Descriptive observations retain their actual scope and reference.

## Handoffs

Every inter-agent task is a `handoff` record (`templates/research-records.md`,
"Agent handoff"): `objective`, inputs, constraints, deliverables,
`artifact_paths`, `archived_by`, `inference` (policy, effort,
fallback/degraded flags, independence, delivery), `budget` (only limits
actually set), `completion_gate`, and a `review_plan` when it opens a
claim-changing review round. New handoffs carry no attestation fields and no
null-placeholder blocks.

**Dispatch preconditions bind the dispatcher** before launch, listed on the
card or not: `archived_by` bound to exactly one archival task; declared inputs
committed and pushed; a lane claimed (`tools/goal_lanes.py`) when the goal is
already being worked, within `max_concurrent`. Success waives no
precondition, and a card is never edited to make a past dispatch look
compliant: a correction record supplies what followed
(`CORR-20260915-6708e4`).

## Review architecture

A claim-changing review round runs under a `review_plan` the Coordinator writes
**before any reviewer runs**: its prior recorded first; each load-bearing joint
owned by exactly one reviewer with a worked attack plan; blindness within the
round declared and lifted only deliberately (`blindness.lifted_for`); a
proves-too-much control on objects whose conclusion is known false; a blind
re-derivation of each load-bearing quantity from statement and parameters alone
(`blind_rederivation.blind_from`; replicating from the producer's artifacts is
not one). Reviewers report on their joints and the Coordinator composes;
`tools/check_review_independence.py` checks the composition. Departures go in
`procedure_deviations`.

## Messaging and coordination

- `tools/agent_bus.py` carries write-once, role-addressed messages between
  sessions (`coordination/bus/`): a feed, read on wake and before reporting done
  (`inbox --as <addr>`). In-session `SendMessage` obeys the same rules and is
  the more dangerous.
- **A message never confers authority, is never evidence, never carries a task,
  and never records an agreement you did not obtain.** Work travels as a
  `TASK-*` handoff through `tools/research_dispatch.py`; a decision is a
  committed record; a result exists in its run directory or not at all. Messages
  past the bus shelf life are digest material, not pending work
  (`docs/inter-agent-messaging.md`).
- **Dynamic dispatch.** `tools/research_dispatch.py` turns approved handoffs
  into a bounded plan (`--ready-only`: the Ready Tasks). Tasks own
  non-overlapping `write_scope`s and write under their task directory; a task is
  eligible only when every dependency has a `completed` receipt; the queue's own
  `max_concurrent` bounds concurrency (user, 2026-08-05). Regenerate the plan on
  each terminal receipt; never fill a slot because it is free. Reserve an
  independent review task whenever a result could change an ECDLP claim.
- **Lanes.** Holds and open batches are write-once side files
  (`tools/goal_lanes.py claim|release`, `open-lane|close-lane`), read by
  `research_dispatch.py --claims refs`; another session's live claim is
  `running`, not yours (`docs/concurrent-goal-lanes.md`).
- The `crypto-autoresearcher-peer` MCP board (`docs/peer-coordination.md`) is
  optional advisory telemetry: never a run admission gate; its messages assign
  nothing.

## Concurrency: many agents, many worktrees

- **Generated artifacts**: `knowledge/INDEX.md`, `coordination/**/dispatch_plan.*`,
  and `ledger/.index/` are gitignored. `main-health.yml` archives its cache;
  checked-in `coordination/portfolio_health/latest.json` is historical pending review.
- **`main` takes merge commits only** (repository setting; never squash or
  rebase): archive receipts bind branch shas, which a squash orphans
  (`CORR-20260802-a1f151`).
- **Continue through the PR** (user, 2026-10-14; supersedes the 2026-10-09
  stop rule): open it ready for review, never as a draft unless the user asks
  (`docs/ci-tiers.md`). Work for an
  existing research lane goes to its `lane/<lane>` branch with
  `scripts/lane-push.sh <lane>`, not a new PR, and a PR's head stays within 30
  CI checks (`ci:over-budget` otherwise). The authoring session follows its PR through CI, review, conflict resolution,
  and merge or closure. Any model tier may
  fix its own PR's failures and merge it under the same gates. Subscribe to PR
  activity when supported; otherwise use spaced check-ins, not busy polling or
  a foreground wait on CI. Check in about 50 minutes after activity, then about
  four hours apart if nothing changes; stop after three unchanged check-ins,
  merge or closure, or an instruction to stop. New activity resets the count.
- **Auto-merge is on by default** (user, 2026-10-24): the moment a PR against
  `main` is open and ready for review, enable GitHub auto-merge
  (`gh pr merge <n> --auto --merge`), then keep the normal check-in flow; do
  not poll it to completion. Auto-merge exists only when the base is the
  repository's default branch: a PR based on a feature branch (stacked work)
  can never be auto-merged, so retarget it to `main` once its parent lands, or
  merge the stack bottom-up by hand. Enabling auto-merge waives no gate below:
  required checks, review and approvals still decide, and a failure is fixed,
  never merged. If the user asks to leave the PR open or wait for review,
  disable auto-merge (`gh pr merge <n> --disable-auto`) so it stays open.
- **Merge** the PR for the current user task when its final diff is complete,
  the current head has all required and applicable checks successful (or
  legitimately skipped), no check pending (except as below) or failed, no
  conflict, no open blocking thread, and Claude Approvals passing where it
  runs. Review failure
  logs and fix failures caused by the change; report unrelated failures with
  evidence on the PR. A new commit resets the current-head checks. Never skip,
  disable, or rerun a check merely to get green, and never bypass branch
  protection or required review. Use a merge commit and an expected-head guard
  where supported.
  Confirm the merged state and merge commit before reporting success. A merge
  is a git operation,
  not a research-state transition. If a concrete gate prevents merging, name
  it on the PR and continue the check-in flow; do not treat a ready PR as done.
- **Checks that never start do not block** (owner, 2026-10-23). A nonrequired
  check queued for at least 24 hours without a runner may be excluded only if
  every check that ran on the current head passed. Name it and its wait in the
  merge commit. Required checks always wait; report their absence on the PR.
  A started, running check remains pending.
- **Archive receipts bind to content first**: `path_sha256` verified, commit
  reachability advisory, a content mismatch fatal.
- **Goal checkpoints are one write-once file per batch**
  (`tools/shard_goal.py`), converted when a goal is next opened, never in bulk.
  Goal heads over 64 KiB and `next_action` over 1,000 characters are flagged: a
  next action points to a task, not a plan.
- **Parseability is PR-scoped and absolute on `main`**
  (`check_merge_hygiene.py`; `main-health.yml` sweeps hourly).
- **Read the merge digest on wake**: `python3 tools/merge_digest.py --since
  $(git merge-base HEAD origin/main) --until origin/main` (one
  `coordination/events/main/<sha>.yaml` per merge).
- **Merge `main` in to stay current**, never rebase pushed records;
  `.github/workflows/sync-branches.yml` runs `tools/sync_open_branches.py` every
  six hours and resolves no conflicts. A conflict inside a record becomes a
  superseding record under a new id.
- `tools/lab_sync.py` may carry `ledger/`, `coordination/`, `experiments/` and
  `knowledge/` as signed CRDT ops (`docs/cairn-lab.md`); it relaxes nothing
  above, and git stays what archives bind.

## Durable research commits

Research is durable only when committed. The Coordinator's archival tasks
(dispatcher, Coordinator-only) commit at two points: a **snapshot commit** of a
producer's exact artifacts before independent review, and a **ledger commit**
of evidence, decision, status and synthesis records before an official
transition. Commit tasks run alone, stage only declared paths, and record a
receipt the dispatcher verifies against git (reachable from `HEAD`, expected
parent, exactly the declared artifacts, recorded hashes, task and record ids
named). Every theory, run receipt, review report, checkpoint, ledger record
and knowledge item belongs to exactly one archival task; a missing or dirty
commit blocks promotion and is an integrity failure, not a result. Fetch and
inspect `origin/main` at session start, before each archival commit, and
before requesting review or merge; record the base commit and merge outcome in
the receipt.

## Research states

Hypotheses: `proposed -> specified -> approved -> running -> analyzed ->
replicated -> supported | weakened | rejected | inconclusive | superseded`.

Experiments: `draft -> review_required -> approved -> running -> completed |
failed_infrastructure | invalid -> analyzed -> archived`.

Every transition has a decision record with rationale and evidence
references. A specification states, before any run, what each outcome changes
(`decision_impact`) and carries no outcome field
(`check_outcome_not_prewritten`).

## Artifact policy

**Execution-proof integration is integral to the proof chain** (owner,
2026-10-16). Work implementing it follows
[docs/execution-proof-chain.md](docs/execution-proof-chain.md): bind the approved
protocol, executable, inputs, complete workload and raw output through metric
checks, evidence, independent review and Cairn settlement/audit. No covered
claim may be called execution verified merely because its receipt was hashed,
its witness checks, or its schema passes. This is a required integration and
release contract, not a claim that today's runners enforce it. Missing proof
support stays explicit; scientific authority and historical records retain
their existing rules.

Each run retains: exact command; commit and dirty-tree state; environment and
dependency versions; parameters and seeds; requested policy, backend and
resolved model id with provenance and probe status; reasoning effort, fallback
and degraded requirements; stdout and stderr; raw machine-readable results;
validity status and reason; timestamps and resource measurements. An artifact of
1 MiB or more is stored gzipped (`x.gz`), and one still 10 MiB or more is a
`x.gz.blob.json` pointer into S3; receipts bind content digests and readers go
through `tools/artifact_store.py` (`docs/artifact-storage.md`). Claim tiers
and solution certificates: `docs/claims-and-verification.md`. Session receipts
(`tools/session_receipt.py`, `docs/session-receipts.md`) record what a session
cost; they are never evidence.

Every benchmark, profiler session, and evaluation an agent runs also produces a
durable measurement report, including regressions, failed attempts, and censored
runs. The report states the question, exact workload and controls, revisions
(baseline and candidate where applicable), hardware and tool versions, commands, raw measurements,
correctness checks, costs, uncertainty and limits; it links to the underlying
artifacts. Any interpretation is labeled separately; a usefulness or attack
verdict is not a required report field. Retain native profiler captures (for
example Nsight Compute `.ncu-rep` files) and source or instruction-level exports when produced.
If capture fails, retain its logs and state which artifact is absent. Keep the
report and raw artifacts in a durable evidence path, or commit a manifest with
digests and stable artifact locations. Never replace a raw capture with a
summary, overwrite a prior attempt, or discard an unfavorable result; each
rerun gets a distinct record.

## Data files live in the artifact store

Owner, 2026-10-24: any non-code file over 1 MiB, and any data-suffixed file
(`.jsonl`, `.gz`, `.npy`, logs, archives) over 64 KiB, lives in
`s3://setec-astronomy-artifacts` with a `.artifacts.json` manifest in its
directory, moved with `tools/artifacts/artifacts.py push` (not `git add`) and
read after `pull`. The `artifacts` CI check fails a PR that adds one to Git.
Never delete remote objects. See [`docs/artifacts.md`](docs/artifacts.md).

## Papers

For manuscripts, follow [the paper contract](docs/agent-contract-extended.md#papers). Its layout, evidence, anonymity, submission, and build requirements are binding.

## Knowledge retrieval

Before claims about prior work or literature, follow [the retrieval policy](docs/agent-contract-extended.md#knowledge-retrieval). Its provenance, scope, and contradiction checks are binding.

## Curve identity and measured bounds

New curve comparisons and UI exports follow `docs/curve-identities.md` and
`tools/curve_identity.py`: reuse EC1 aliases and full curve UIDs across IC and
Pollard rho, keep factor-base/isogeny identities separate, keep historical
names, never infer identity from field degree alone.

A cost claim enters the ledger only as a **measured bound**: a sealed
`ECBND1h...` record from the measuring harness (aburan28/crypto
`docs/bounds/README.md`) in an evidence record's `measured_bound` block with
matching `claim_tier`, naming exactly one level (exponent, constant, primitive
weights, machine). A frontier moves only on a paired challenge verdict;
`inadmissible` is never negative evidence; the Coordinator's decision, not the
verdict, changes state. Wall time is never a bound.
`docs/bounds-and-frontiers.md`.

## Weak-curve and isogenous-representative audits

Before weak-curve, CM, endomorphism, or isogeny claims, read [`audit-curve`](.claude/skills/audit-curve/SKILL.md) and follow [the full audit rule](docs/agent-contract-extended.md#weak-curve-and-isogenous-representative-audits). Its scope, controls, transfer, cost, and inference requirements are binding. The [curve-audit topic index](docs/agent-contract-topic-rules.md#weak-curve-and-isogenous-representative-audits) specifies the applicable labels. A singular or invalid formula-compatible companion supports only an implementation-weak label.

## Cursor Cloud specific instructions

On Cursor Cloud, follow the binding [environment instructions](docs/agent-contract-supplement.md#cursor-cloud-specific-instructions) for Python, extras, dashboard and Lean setup.

## Progress metrics (daily lab report)

## Resume checkpoints in S3 before every run
A session can end at any moment (token or usage limits, a crash, a reclaimed
container), and a worktree that only it knew about is then lost. So **before
any experiment run starts, the leads, the spec and everything needed to
resume the effort are checked into S3**, and kept current while it runs.
- `scripts/checkpoint.sh init` writes `.resume/RESUME.md` (gitignored). Fill
  every section for a reader who has none of this conversation: goal, the
  lead or hypothesis and where it came from, the spec or protocol path with
  frozen inputs, the current state with measured numbers and where raw output
  lives, next steps with exact commands, every run in flight (command, host,
  instance id or pid, log and output paths, how to collect it), and the stop
  and success conditions. The gate rejects missing or empty sections and
  leftover `TODO(checkpoint)` markers.
- `scripts/checkpoint.sh push` uploads one checkpoint to
  `s3://setec-astronomy-artifacts/checkpoints/<repo>/<branch>/<stamp>/`:
  `RESUME.md`, the spec, leads, protocol and plan files the branch changed, a
  git bundle of unpushed commits, a patch of uncommitted changes, untracked
  files (large ones listed, not copied) and `meta.json`. Earlier checkpoints
  are never overwritten. Push again whenever a run starts or finishes,
  results arrive, or the plan changes.
- **Claude Code enforces this** (`.claude/hooks/checkpoint-hook.sh`): writing
  a spec, leads, protocol or plan file, or `RESUME.md`, pushes a checkpoint,
  and run launchers (`scripts/run_*`, sweeps, benchmarks, `nohup`, background
  commands, `cargo run --release`, `expspec run`, `sage-run`, cloud launches)
  are refused until `RESUME.md` is complete and the push succeeded. A command
  that is not an experiment run may opt out with `CHECKPOINT_SKIP=<reason>`.
  **Other runtimes (Codex)** run `scripts/checkpoint.sh gate` before
  launching and do not launch if it fails.
- Claude Code sessions have no AWS credentials, so the script works from a
  token (tried first; an AWS profile is only a fallback). The token is a
  presigned POST policy that can only write under `checkpoints/`, plus a
  presigned link to an index of recent checkpoints, so push, `list`, `share`
  and `restore` all work without credentials. A job on the owner's Mac
  re-mints it every 15 minutes (7-day lifetime) into
  `~/.config/checkpoint/upload-token`, where the script finds it; a session
  elsewhere is given it as `CHECKPOINT_UPLOAD_TOKEN`. The bucket host is in
  this repo's sandbox network allowlist (`.claude/settings.json`). It is a bearer credential: never
  commit it or put it in a PR, report or task card.
- To resume: `scripts/checkpoint.sh list` shows the latest checkpoint per
  branch (from the index, up to 15 minutes behind);
  `scripts/checkpoint.sh restore <repo>/<branch>[/<stamp>]` rebuilds the
  worktree next to this checkout and puts `RESUME.md` in it. `share` prints a
  presigned URL that `restore <url>` accepts anywhere.
A checkpoint is a safety net, not the record: the spec, protocol and results
still land in a PR under the rules above. Switching runtimes:
[docs/runtime-relay.md](docs/runtime-relay.md).
When changing tracked results, follow the binding [daily progress-metrics rule](docs/agent-contract-supplement.md#progress-metrics-daily-lab-report): extend the exporter in the same PR, retain stable metric ids and emit only measured, committed values.
