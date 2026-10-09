# Crypto Autoresearcher Agent Contract

A multi-agent operating system for reproducible ECDLP experimentation. This
file is the normative contract: rules, with one-line reasons. The
incident narratives and worked reasoning behind them are in
[`docs/agent-contract-extended.md`](docs/agent-contract-extended.md), and the
rules cite the document that holds their full statement. Where this file and
any other document disagree, this file wins.

## Budgets: progress first

Research cost estimates are advisory, may be null, and never need repeated
user approval (user instruction, 2026-09-06). Only a committed Coordinator
stagnation review — ≥ 90 days without documented progress, with evidence,
scope, a next action and an assessment from the last seven days — may cap
spending. Memory/concurrency limits and justified process watchdogs are
machine protection, not budget. Fixed sample counts, locked plans, write
scopes, controls, immutable records, independent review and the Bedrock
prohibition still bind. `docs/research-budget-policy.md`.

## Entry points

- **`run`** is the single public execution skill
  (`plugins/crypto-autoresearcher-harness/skills/run/SKILL.md`; adapters
  expose the same name on every host). It executes existing experiment
  programs and reports outputs: no prepended preflight, validation, audit or
  protocol authoring; no appended mandatory review or state transition. Keep
  the runner's own admission, ownership, resource and correctness checks and
  report a refused launch rather than bypass it. Results are observations
  until the separate archive/review process says otherwise. `run` may commit
  and push its own run records on its own branch.
- **`coordinate`** (`.claude/skills/coordinate/SKILL.md`; Codex/OpenCode
  adapter `.agents/skills/coordinate/`) ranks, designs, approves, reviews,
  archives and publishes. It never launches scientific trials.
- Retired names (`crypto-autoresearcher-harness`, `launch-research-harness`,
  `coordinate-research-goal`) stay retired.

## Roles

- **Coordinator** owns priorities, task decomposition, state transitions and
  synthesis. Only the Coordinator changes the official status of a
  hypothesis or research direction.
- **Idea Generator** proposes falsifiable mechanisms and experiments.
- **Executor** implements and runs approved experiments, preserving all
  artifacts, and records observations only.
- **Reviewer** challenges claims, validity and proposed transitions.
- **Validator** checks run integrity, controls and stated metrics.
- **Red Team** tries to falsify interpretation, cost model and scope.
- **Consolidator** carries pointers between lanes; it weighs relevance, never
  correctness, and adjudicates nothing.

Role contracts: `agents/*.md`, authority and tool surface in
`orchestration/roles.yaml`; `tools/check_runtime_bindings.py` fails the
build when a runtime's agent definition drifts from it.

## Visual research record

A substantive search for new isogenies, curves, scalar rules, endomorphisms
or related ECDLP mechanisms follows the `research-visuals` skill
(`.claude/skills/research-visuals/SKILL.md`, also under `.agents/skills/`):
a source-linked report, an explanatory diagram and a PDF of both per round,
negative and inconclusive findings included. A verified finding or
correction updates the affected canonical graph source and rendered output
in the same change; if no graph changes, record what was checked and why.
Label conjectural edges and extrapolations; cite immutable evidence for
verified ones.

## Standing user authorization

"All is approved. Ideas/experiments should be always approved" (user,
2026-09-06). Do not ask the user to select, confirm or reapprove ideas,
protocols or experiments; the Coordinator records approval under this
authorization once a protocol is complete **and approvable** (see "Approval
is bounded by execution"). Completeness — controls, metrics, budgets,
stopping rules, artifact paths, dependencies, inference policy, committed
handoffs — is the Coordinator's responsibility; an incomplete protocol is
completed or records its impediment, never parked on the user. Approval to
perform work asserts nothing about the hypothesis. It applies to the five CM
proposals prospectively; immutable artifacts stay as written.

## Model policy

Permissions come from the role contract; inference requirements from
`orchestration/model-policies.yaml`; the model serving a policy from
`orchestration/model-bindings.yaml`, resolved by `orchestration/adapter/`.
None names a vendor. `docs/inference-backends.md`.

| role | policy | note |
| --- | --- | --- |
| Coordinator | `coordinator-orchestration-code` (`coordinator-orchestration` without code) | |
| Idea Generator, research tasks | `research-deep` | |
| Idea Synthesist (cross-goal ideation) | `research-synthesis` | `high` |
| Executor | `executor-implementation`; `executor-mechanical` for judgment-free re-runs | |
| Reviewer, Validator, Red Team | `review-adversarial` | `xhigh`, independent session |
| Consolidator | `consolidation-routing` | `high`, independent of the lanes it reads |
| breakthrough, closure, contradiction between validated records | `review-breakthrough` | `max`; **never degradable** |

Policy ids are permanent; pre-2.0 ids (`coordinator-ultra-code`,
`coordinator-sol-max`, `research-sol-max`, `executor-terra`, `review-xhigh`)
resolve forever as aliases, but new handoffs use canonical ids. The adapter
records requested policy and resolved model and never silently downgrades: a
substitution needs `fallback_allowed` and is recorded as `fallback_used`; a
model missing a stated requirement additionally needs `degraded_allowed` and
a Coordinator-approved `inference_amendment`, with every gap in
`degraded_requirements`. A model id is unverified until `python3 -m
orchestration.adapter doctor --probe` confirms it (`model_verified`).
Delivery (`interactive` | `batch` | `auto` with `deadline_seconds`) is recorded
on every manifest and changes nothing else; `auto` never batches urgent work,
expired or errored batch results are infrastructure signal
(`docs/batch-inference.md`). Runtimes (Claude Code, OpenAI-protocol CLIs,
`api_direct`) are interchangeable over the same role contracts; under
`api_direct` write scope, no-overwrite, command allow-list and budget stops
are enforced, not requested.

## Core rules

1. Separate speculation, implementation, observation and conclusion.
2. A hypothesis states mechanism, predictions, test boundary and
   falsification criteria.
3. An experiment defines controls, metrics, budgets, stopping rules and
   required artifacts before execution.
4. Results are immutable records. Corrections create new records.
5. A timeout, crash or implementation failure is not evidence against a
   mathematical hypothesis.
6. Negative evidence closes only the exact tested scope.
7. Evidence at any scale is admissible; records state tested parameters,
   actual scope and every transfer or extrapolation assumption.
8. Unexpected observations are recorded, never silently discarded.
9. Never fabricate commands, outputs, timings, statistics, citations or runs.
   Every citation carries provenance `recalled | retrieved | kb | internal`
   (`templates/research-records.md`); a `recalled` reference is a pointer,
   never support, until an agent that read the source says so in a new
   record naming itself in `verified_by`.
10. Every conclusion cites the experiment IDs and artifacts supporting it.
11. An agent may request a stronger policy; it never silently alters its own
    model or reasoning level.
12. A claimed breakthrough, closure result or contradiction of established
    evidence receives independent `review-breakthrough` review at `max`,
    never degraded.
13. Goal closure quorum: see below (suspended).
14. Every new record id carries a random 6-hex suffix minted with
    `python3 tools/allocate_id.py --next <type> --area|--date <x>` and
    confirmed with `--check`. Never allocate by grepping for `max+1`: every
    concurrent worktree gets the same answer and mints the same id. Legacy
    `\d{3}` ids stay valid; ids no longer sort by creation, read
    `added`/`recorded_at`.
15. An identifier remap is a last resort. A record named in a *completed*
    archive's binding fields (`artifact_paths`, `write_scope`,
    `archive.path_sha256`, `archive.record_ids`, bound commit message) is
    superseded, never renamed.
16. **Amazon Bedrock is prohibited.** No runtime, fallback or probe selects a
    provider, endpoint or model id containing `bedrock`; refuse before any
    request. Missing alternatives are a terminal infrastructure stop, never
    permission. Historical receipts stay immutable. The adapter's offline
    guard enforces this; no record carries an attestation field for it.

## Research-direction integrity

Pursue promising paths in good faith; never abandon, suppress or steer away
from a plausible high-value lead to derail the program. A deprioritization or
closure names evidence, budget, test boundary, remaining uncertainty and a
successor or revisit condition. Decision records (candidate, evidence,
rationale, ranking, action, model/session provenance) are the audit trail;
private chain-of-thought is neither stored nor inferred.

## Goal closure quorum (suspended)

Rule 13 required three `CONCUR` attestations from pairwise-distinct resolved
models before `status: completed`. It is **suspended**
(`GOAL_CLOSURE_QUORUM_REQUIRED = False` in `tools/validate_ledger.py`) because
one deployed backend makes three attestations one model, which the rule
itself defines as no quorum; restore it when `doctor --probe` resolves more
than one. Still binding: a `completed` goal needs a committed Coordinator
decision showing a declared criterion was met; never record an attestation
you did not obtain; a recorded `DISSENT` blocks closure; `closed_at_budget`
and `cancelled` assert no success and never understate a met criterion.
`PRE_QUORUM_GOAL_IDS` must not grow. Full statement:
`docs/agent-contract-extended.md`.

## Goals are never paused

`paused` and `blocked` are not permitted `GOAL-*` statuses (user, 2026-09-04;
refused by `tools/validate_ledger.py`). An impeded campaign stays `active`
and records the impediment under `impediments` (`id`, `raised`, `condition`,
`what_is_blocked` — a task or claim, never "the goal" — `clears_when`,
`recheck`, `asserts_nothing_about`). `pause_conditions` keep their name;
triggering one records an impediment and changes no status.

This is a scheduling rule and relaxes nothing: an impediment is never
negative mathematical evidence (rule 5); an unservable `review-breakthrough`
(`degradable: false`) leaves the claim un-promoted, never downgraded to
`validator`. Routine estimates do not stop research: only the exceptional
stagnation policy caps a budget, and a watchdog stop is not campaign
exhaustion. Terminal retirement (`completed`, `closed_at_budget`,
`cancelled`) is a deliberate Coordinator act with a committed decision. A goal
that can never be parked always looks runnable: never dispatch a task you
cannot rank ahead of doing nothing; report an impeded goal with its
`recheck` and move on.

## ECC comes first, and its budget is unlimited

User instruction, 2026-09-04. The ECC area set is declared once in
`orchestration/research-priority.yaml` and read via `tools/ecc_priority.py`
(`--list-areas`, `--classify`, `--open-ideas`, `--budget-violations`); never
infer it from an identifier prefix.

1. **Unlimited budget.** An active or draft ECC goal has
   `campaign_budget.maximum_batches: null` and
   `total_wall_clock_seconds: null` (validated). `max_concurrent` stays
   bounded: it is machine headroom. Unlimited removes the batch ceiling, not
   the duty to rank; never dispatch a task you cannot
   rank ahead of doing nothing.
2. **ECC first, always.** At every selection point ECC goals are considered
   before all others; a non-ECC goal is worked only when no ECC goal offers a
   ranked, justified task. Priority orders the queue, manufactures no work,
   and lowers no evidence bar: an ECC result meets the same scope,
   certificate and claim-tier standards.
3. **Open ECC ideas are designed, not shelved.** An open idea is `proposed`
   with no hypothesis or experiment citing it; `/design-experiment` turns it
   into a hypothesis and a frozen contract, which sits at `approved_by: null`
   until a committed Coordinator decision approves it under the standing
   authorization.

### Approval is bounded by execution

Additive amendment, 2026-10-07 (`docs/track-record-review-20261006.md` P0.1,
P0.2, P0.4; operator request `DEC-20261005-138b51` F-1). An open ECC idea is
designed **when it can be approved**, and approval has two checked conditions:

- **Capacity.** A goal (or, without one, its area) holds at most
  `APPROVAL_CAPACITY_CAP` (three, `tools/portfolio_kpis.py`) approved
  contracts that have never run. `validate_ledger.py` refuses a `DEC-*`
  minted on or after the amendment date that approves past the cap unless it
  retires one (`supersedes_experiments` / `withdraws_experiments`). 1,137
  approved contracts had never run when this was written.
- **Runnable.** A contract is approved only when `python3
  tools/newest_experiments.py --experiment <EXP-ID>` reports
  `execution_state: ready`. Implementation belongs to the design lane; a
  contract not runnable in its designing session stays `review_required`
  with the reason recorded.

An idea that cannot be approved stays `proposed`, with the reason in the
session receipt (`tools/session_receipt.py --outcome refused_capacity`) and
the goal's `next_action`; the proposal is not edited. That is not shelving:
it remains ranked work, visible to `--open-ideas`, designed in the session
that has the headroom or the launcher. Designing it earlier manufactures
records the harness cannot act on. Unchanged: priority orders the queue,
designing is not approving, and an approved-but-unrun contract is neither
evidence nor a failure of its hypothesis.

## Research direction

The target result profile is Wesolowski's `p^{1/3+o(1)}` supersingular
isogeny result (`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`;
`docs/target-result-profile.md`, checklist C1–C18; `KN-TECH-055`):
exponent-first ambition, numbered heuristics each with random-model
justification, falsification condition and validation plan,
single-responsibility lemmas, external structural ingredients, validation at
scale, and cost/scope honesty (memory beside time, o(1) disclosed, concrete
cost table, affected-vs-safe scope). Before an asymptotic claim moves toward
`supported` the Coordinator verifies the promotion gates in
`agents/coordinator.md`. The profile biases direction and lowers no rule.

The **inventor protocol** (`docs/inventor-protocol.md`; `KN-TECH-056`,
`KN-TECH-080`) binds the Idea Generator, Validator, Red Team and, for §8,
the Coordinator: premature closure is a failure symmetric with overclaiming;
a closure needs a named obstruction recorded as a measured `obstruction`
block with a `resource_check`, an argument and forward guidance (a count of
rejected mechanisms is `unverified`); any signal is an artifact until run
against a null object of the same shape; every deliverable carries a checked
`dominated_by` and a quantitative `sota_delta`; and a proof-oriented proposal
carries a `proof_search_map` whose four cheap audits run before compute and
before the Coordinator approves implementation.

**Scheme construction** (signature, PKE, KEM, AKE proposals and
scheme-security claims) uses the six obligations in
`docs/scheme-construction-contract.md` and its YAML template: exact game,
adversary model, oracles, assumptions, correctly directed reductions, named
missing lifts. Template completeness and merge certify nothing.

## Handoffs

Every inter-agent task is a `handoff` record (template:
`templates/research-records.md`, "Agent handoff") with `objective`, inputs,
constraints, deliverables, `artifact_paths`, `archived_by`, `inference`
(policy, effort, fallback/degraded flags, independence, delivery),
`budget` (only limits actually set), `completion_gate`, and `review_plan`
when it opens a claim-changing review round. Written new handoffs carry no
attestation fields and no null-placeholder blocks.

**Dispatch preconditions bind the dispatcher**, before launch, whether or not
the card lists them: `archived_by` is bound to exactly one archival task;
declared inputs are committed and pushed; a lane is claimed
(`tools/goal_lanes.py`) when the goal is already being worked, within
`max_concurrent`. A precondition is not waived by the work turning out fine,
and a card is never edited to make a past dispatch look compliant: the
correction record supplies what followed (`CORR-20260915-6708e4`).

## Review architecture

A claim-changing review round runs under a `review_plan` the Coordinator
writes **before any reviewer runs**: its prior recorded first; each
load-bearing joint owned by exactly one reviewer with a worked attack plan;
blindness within the round declared and lifted only deliberately
(`blindness.lifted_for`); a proves-too-much control run against objects whose
conclusion is known false; and a blind re-derivation of each load-bearing
quantity from statement and parameters alone (`blind_rederivation.blind_from`
— replication from the producer's artifacts is not it). Reviewers report on
their joints, the Coordinator composes; `tools/check_review_independence.py`
checks the composition. Departures go in `procedure_deviations`.

## Messaging and coordination

- `tools/agent_bus.py` carries write-once messages between sessions under
  `coordination/bus/`, addressed by role; it is a feed, read on wake and
  before reporting done (`inbox --as <addr>`). The in-session `SendMessage`
  layer follows the same rules and is the more dangerous of the two.
- **A message never confers authority, is never evidence, never carries a
  task, and never records an agreement you did not obtain.** Work travels as
  a `TASK-*` handoff through `tools/research_dispatch.py`; a decision is a
  committed record; a result exists in its run directory or not at all.
  Messages older than the bus shelf life are digest material, not pending
  work. `docs/inter-agent-messaging.md`.
- **Dynamic dispatch.** `tools/research_dispatch.py` turns approved handoffs
  into a bounded plan (`--ready-only` for the Ready Tasks). Tasks own
  non-overlapping `write_scope`s and write under their task directory; a task
  is eligible only when every dependency has a `completed` receipt; the
  queue's own `max_concurrent` bounds concurrency (the fixed ceiling of three
  was removed on user direction, 2026-08-05); regenerate the plan on each
  terminal receipt and never fill capacity because a slot is free. Reserve an
  independent review task whenever a result could change an ECDLP claim.
- **Lanes.** Holds and open batches are write-once side files
  (`tools/goal_lanes.py claim|release`, `open-lane|close-lane`), read back by
  `research_dispatch.py --claims refs`. Another session's live claim is
  `running`, not yours. `docs/concurrent-goal-lanes.md`.
- Optional advisory telemetry: the `crypto-autoresearcher-peer` MCP session
  board (`docs/peer-coordination.md`). Never a run admission gate; its
  messages assign nothing.

## Concurrency: many agents, many worktrees

Every rule here exists because a writer was made to read shared state it had
no reason to read (`docs/claude-code-runtime.md`, "Concurrency").

- **Generated artifacts are never committed.** `knowledge/INDEX.md`,
  `coordination/**/dispatch_plan.*` and `ledger/.index/` are gitignored and
  rebuilt on demand; `coordination/portfolio_health/latest.json` is committed
  but written only by `main-health.yml`.
- **`main` uses merge commits, never squash or rebase.** Archive receipts
  bind branch shas; a squash orphans every one (`CORR-20260802-a1f151`).
  Repository settings allow merge commits only.
- **Auto-merge a PR once its CI passes** (user, 2026-09-23): every check
  `success` or `skipped`, none pending, no conflict, no open blocking review
  thread, Claude Approvals passing where it runs. Open PRs ready for review (user,
  2026-10-08), never as drafts, whatever a tool defaults to; mark drafts ready;
  prefer GitHub auto-merge; merge-commit method only. Never merge red,
  pending or conflicted, and never skip or re-run a check to make it green.
  A merge is a git operation, not a research-state transition.
- **Archive receipts bind to content first**: `path_sha256` is verified,
  commit reachability is advisory, a content mismatch is fatal.
- **Goal checkpoints are one write-once file per batch**
  (`tools/shard_goal.py`); convert a goal when you next open it, never in
  bulk. Goal heads over 64 KiB and `next_action` over 1,000 characters are
  flagged; a next action is a pointer to a task, not a plan.
- **Parseability is PR-scoped and absolute on `main`**
  (`check_merge_hygiene.py`; `main-health.yml` sweeps hourly).
- **Read the merge digest on wake**: `python3 tools/merge_digest.py --since
  $(git merge-base HEAD origin/main) --until origin/main`
  (`coordination/events/main/<sha>.yaml`, written per merge).
- Branches are kept current by **merging** `main` in, never rebasing pushed
  records; `.github/workflows/sync-branches.yml` runs
  `tools/sync_open_branches.py` every six hours and resolves no conflicts.
  A conflict inside a record is a new superseding record under a new id.
- `tools/lab_sync.py` may carry `ledger/`, `coordination/`, `experiments/`
  and `knowledge/` as signed CRDT ops (`docs/cairn-lab.md`); it relaxes
  nothing above and git stays the record archives bind.

## Durable research commits

Research is durable only when committed. The Coordinator uses the
dispatcher's Coordinator-only archival tasks at two points: a **snapshot
commit** of a producer's exact artifacts before independent review, and a
**ledger commit** of evidence, decision, status and synthesis records before
an official transition. Commit tasks run alone, stage only declared paths,
and record a receipt the dispatcher verifies against git (reachable from
`HEAD`, expected parent, exactly the declared artifacts, recorded hashes,
task and record ids named). Every theory, run receipt, review report,
checkpoint, ledger record and knowledge item belongs to exactly one archival
task; a missing or dirty commit blocks promotion and is an integrity failure,
not a result. Fetch and inspect `origin/main` at session start, before each
archival commit, and before requesting review or merge; record the base
commit and merge outcome in the receipt.

## Research states

Hypotheses: `proposed -> specified -> approved -> running -> analyzed ->
replicated -> supported | weakened | rejected | inconclusive | superseded`.

Experiments: `draft -> review_required -> approved -> running -> completed |
failed_infrastructure | invalid -> analyzed -> archived`.

Every transition has a decision record with rationale and evidence
references. A specification states, before any run, what each outcome
changes (`decision_impact`) and carries no outcome field
(`check_outcome_not_prewritten`).

## Artifact policy

Each run retains: exact command; git commit and dirty-tree state;
environment and dependency versions; parameters and seeds; requested policy,
backend and resolved model id with provenance and probe status; reasoning
effort, fallback and degraded requirements; stdout and stderr; raw
machine-readable results; validity status and reason; timestamps and
resource measurements. Claim tiers and solution certificates:
`docs/claims-and-verification.md`. Session receipts
(`tools/session_receipt.py`, `docs/session-receipts.md`) record what a
session cost; they are never evidence.

## Knowledge retrieval

`kb/` is a derived, read-only index over the corpus, exposed as one MCP
server. Use `search_knowledge` before asserting an avenue was tested or
known to fail, citing a paper or prior experiment, proposing a likely
duplicate, or changing an authoritative conclusion. Start with 4–6 results,
use exact identifiers, filter by `field_type`/`source_type`, call
`get_context` only where it affects the conclusion, read `claim_status`,
`evidence_level` and `authority`, report contradictions rather than picking
one, and never treat retrieval score as evidence quality. A passage is a
pointer to a record, not a citation; a remembered paper becomes `kb` or
`retrieved` only in a new record naming `verified_by`. Absence of a result is
not evidence of absence. No agent writes to the index. For dedup against the
ledger itself, read the generated `ledger/.index/*.jsonl`
(`tools/build_ledger_index.py`), not the corpus.

## Curve identity and measured bounds

New curve comparisons and UI exports follow `docs/curve-identities.md` and
`tools/curve_identity.py`: reuse EC1 aliases and full curve UIDs across IC
and Pollard rho, keep factor-base/isogeny identities separate, preserve
historical names, never infer identity from field degree alone.

A cost claim enters the ledger only as a **measured bound**: a sealed
`ECBND1h...` record from the measuring harness (aburan28/crypto
`docs/bounds/README.md`) carried in an evidence record's `measured_bound`
block with matching `claim_tier`; it names exactly one level (exponent,
constant, primitive weights, machine). A frontier moves only on a paired
challenge verdict; `inadmissible` is never negative evidence; the
Coordinator's decision, not the verdict, changes state. Wall time is never a
bound. `docs/bounds-and-frontiers.md`.

## Weak-curve and isogenous-representative audits

Before a weak-curve claim, use
[`audit-curve`](.claude/skills/audit-curve/SKILL.md) and
[`KN-TECH-6a2ef9`](knowledge/techniques/KN-TECH-6a2ef9.md). Trials still use the
canonical `run` entry point; audits are evidence, not state transitions.

Freeze the curve/subgroup/protocol, attacker, threshold, costs, path-knowledge
model, budgets, population, and stopping rule. Require certified arithmetic and
planted controls. Separate base-field isogeny-class invariants from
representative-dependent structure; unusual structure is only a lead.

An isogeny transfer claim requires explicit maps and subgroup preservation,
with path discovery, construction, evaluation, attack, memory, data, and
precomputation charged. Advice supports only an advice-holder claim. Singular
or invalid
formula-compatible companions can establish **implementation-weak**, never
elliptic-curve or isogeny-class weakness. A confirmation-only oracle needs an
explicit reduction; it does not inherit the companion group's DLP cost.

Use only the claim labels **class-weak**, **weak representative exists**,
**source-transfer-weak**, **implementation-weak**, or **no weakness found in
scope**, with the exact certified scope. Algebraic claims require proof or
certificates. Statistics address only a preregistered sampling law and detector:
report exclusions and indeterminate cases, dependence/effective sample size,
multiple-testing correction, and design-appropriate intervals. A bounded search
or zero-hit prevalence bound is not evidence that no weak representative exists.

## Cursor Cloud specific instructions

The Cloud Agent image's Ubuntu `python3` is not the interpreter this
repository tests against. `.python-version` pins CPython 3.12.8, and
`tests/test_harness.py` requires a default CPython build whose `_md5` is a
separate extension with a `__file__`; Ubuntu compiles it as a builtin, so
`test_md5_pin_mechanism_real_registry_is_distinct` fails there. Use
`/usr/local/bin/python3` (3.12.8) and do not fall back to `/usr/bin/python3`.

Install the CI extras, not only `make install` (`.[agent,dev]`):

```sh
python3 -m pip install -e ".[dev,agent,campaign-mcp,research-loop,gf2]"
```

`pip` puts `autoresearch` and `pytest` in `~/.local/bin`; the environment
links them into `/usr/local/bin`, and `python3 -m pytest` / `python3 -m
orchestration` work either way. `autoresearch doctor` is ready with no API
keys; `.env.example` variables are only for token-spending commands. The
dashboard is `python3 -m ui --host 127.0.0.1 --port 8787` with
`GITHUB_REPOSITORY=aburan28/crypto-autoresearcher` set (an unset value builds
source links from `origin`, whose Cloud Agent remote embeds a credential).
`formal/setup.sh` (Lean) is not part of this environment.
