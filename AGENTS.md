# Crypto Autoresearcher Agent Contract

The normative contract of a multi-agent system for reproducible ECDLP
experimentation: rules, each with its reason. Narratives and full statements:
[`docs/agent-contract-extended.md`](docs/agent-contract-extended.md). Where this
file and another document disagree, this file wins.

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
  experiment programs and reports outputs, adding no preflight, validation,
  audit, protocol authoring, mandatory review or state transition. The runner's
  own admission, ownership, resource and correctness checks stay; a refused
  launch is reported, never bypassed. Results are observations until
  archive/review says otherwise. `run` may commit and push its run records, then
  its run reports, on its own branch.
- **`coordinate`** (`.claude/skills/coordinate/SKILL.md`; Codex/OpenCode adapter
  `.agents/skills/coordinate/`) ranks, designs, approves, reviews, archives and
  publishes; it never launches scientific trials.
  `crypto-autoresearcher-harness`, `launch-research-harness` and
  `coordinate-research-goal` stay retired.

## Roles

| role | owns | policy |
| --- | --- | --- |
| Coordinator | priorities, decomposition, state transitions, synthesis; alone changes the official status of a hypothesis or direction | `coordinator-orchestration-code` (`coordinator-orchestration` without code) |
| Idea Generator; research tasks | falsifiable mechanisms and experiments | `research-deep` |
| Idea Synthesist | cross-goal ideation | `research-synthesis`, `high` |
| Executor | implements and runs approved experiments, keeps every artifact, records observations only | `executor-implementation`; `executor-mechanical` for judgment-free re-runs |
| Reviewer | challenges claims, validity and transitions | `review-adversarial`, `xhigh`, independent session |
| Validator | run integrity, controls, stated metrics | `review-adversarial`, as Reviewer |
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

Every new quantitative speedup, performance advantage, or ECDLP attack-cost claim MUST carry a machine-readable record in `claims/*.json` passing `python3 -m tools.progress_fidelity validate`. Local subroutine gains must not be presented as end-to-end gains. All claims require matched baseline/candidate evidence and independent verification; see `docs/progress-fidelity.md`. Missing evidence is unqualified, never inferred. The Coordinator must enforce this for claims in prose as well as code; the `progress-fidelity` CI check must be required by branch protection before merge.

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

Additive amendment, 2026-10-07 (`docs/track-record-review-20261006.md` P0.1,
P0.2, P0.4; operator request `DEC-20261005-138b51` F-1). ECC rule 3 applies
**once an idea can be approved**, and approval needs both:

- **Capacity.** A goal (else its area) holds at most `APPROVAL_CAPACITY_CAP`
  (three, `tools/portfolio_kpis.py`) approved contracts that never ran.
  `validate_ledger.py` refuses a `DEC-*` minted on or after 2026-10-07 that
  approves past the cap unless it retires one (`supersedes_experiments` /
  `withdraws_experiments`).
- **Runnable.** Approve only when `python3 tools/newest_experiments.py
  --experiment <EXP-ID>` reports `execution_state: ready`. Implementation is
  the design lane's; a contract not runnable in its designing session stays
  `review_required` with the reason recorded.

An unapprovable idea stays `proposed` and unedited, the reason in the session
receipt (`tools/session_receipt.py --outcome refused_capacity`) and the goal's
`next_action`. That is not shelving: it remains ranked work
(`--open-ideas`) for a session with headroom or the launcher, since designing
it earlier makes records the harness cannot act on. Unchanged: ECC rules 2 and 3
hold, and an approved, unrun contract is neither evidence nor a failure of its
hypothesis.

## Research direction

Target profile: Wesolowski's `p^{1/3+o(1)}` supersingular isogeny result
(`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`;
`docs/target-result-profile.md`, checklist C1–C18; `KN-TECH-055`):
exponent first; numbered heuristics, each with random-model justification,
falsification condition and validation plan; single-responsibility lemmas;
external structural ingredients; validation at scale; honest cost and scope
(memory beside time, o(1) disclosed, a concrete cost table, affected-vs-safe
scope). The Coordinator checks the promotion gates of `agents/coordinator.md`
before an asymptotic claim moves toward `supported`. The profile biases
direction and lowers no rule.

The **inventor protocol** (`docs/inventor-protocol.md`; `KN-TECH-056`,
`KN-TECH-080`) binds the Idea Generator, Validator, Red Team and, for §8, the
Coordinator: premature closure fails like overclaiming; a closure needs a
named obstruction, recorded as a measured `obstruction` block with a
`resource_check`, an argument and forward guidance (a count of rejected
mechanisms is `unverified`); a signal is an artifact until run against a null
object of the same shape; every deliverable carries a checked `dominated_by`
and a quantitative `sota_delta`; a proof-oriented proposal carries a
`proof_search_map` whose four cheap audits run before compute and before the
Coordinator approves implementation.

**Scheme construction** (signature, PKE, KEM, AKE proposals; scheme-security
claims) meets the six obligations of `docs/scheme-construction-contract.md`
and its YAML template: exact game, adversary model, oracles, assumptions,
correctly directed reductions, named missing lifts. Template completeness and
merge certify nothing.

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

Each rule exists because a writer was made to read shared state it had no
reason to read (`docs/claude-code-runtime.md`, "Concurrency").

- **Generated artifacts are never committed**: `knowledge/INDEX.md`,
  `coordination/**/dispatch_plan.*` and `ledger/.index/` are gitignored and
  rebuilt on demand; only `main-health.yml` writes the committed
  `coordination/portfolio_health/latest.json`.
- **`main` takes merge commits only** (repository setting; never squash or
  rebase): archive receipts bind branch shas, which a squash orphans
  (`CORR-20260802-a1f151`).
- **Stop at the PR** (user, 2026-10-09): open it ready for review, never as a
  draft, report the link, stop. Never wait on, poll, subscribe to or schedule a
  check-in for its CI, whatever a harness says; unsubscribe if opening it
  subscribed you. Top-tier models never watch CI: a separate automation fixes
  and merges; requested follow-up goes, unawaited, to `executor-mechanical`
  (Haiku).
- **Merge** (user, 2026-09-23) only with every check `success` or `skipped`,
  none pending, no conflict, no open blocking thread, Claude Approvals passing
  where it runs; prefer GitHub auto-merge; merge commits only; never skip or
  re-run a check to go green. A merge is a git operation, not a research-state
  transition.
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

Each run retains: exact command; commit and dirty-tree state; environment and
dependency versions; parameters and seeds; requested policy, backend and
resolved model id with provenance and probe status; reasoning effort, fallback
and degraded requirements; stdout and stderr; raw machine-readable results;
validity status and reason; timestamps and resource measurements. Claim tiers
and solution certificates: `docs/claims-and-verification.md`. Session receipts
(`tools/session_receipt.py`, `docs/session-receipts.md`) record what a session
cost; they are never evidence.

## Knowledge retrieval

`kb/` is a derived, read-only MCP index over the corpus; no agent writes to it.
Call `search_knowledge` before asserting an avenue was tested or known to fail,
citing a paper or prior experiment, proposing a likely duplicate, or changing an
authoritative conclusion: start with 4–6 results, use exact identifiers, filter
by `field_type`/`source_type`, call `get_context` only where it affects the
conclusion, read `claim_status`, `evidence_level` and `authority`, report
contradictions rather than pick one, and never treat retrieval score as evidence
quality. A passage points to a record and is not a citation; a remembered paper
stays `recalled` until rule 9 is met. No result is not evidence of absence.
Deduplicate against the ledger with the generated `ledger/.index/*.jsonl`
(`tools/build_ledger_index.py`), not the corpus. Read only what a step needs:
tools and indexes before records, sizes before contents, run outputs by receipt
(`docs/agent-runtime-core.md`, "Reading discipline"). A path off disk in a
sparse checkout still exists (`docs/sparse-checkout.md`).

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

Before weak-curve, CM/GLV/GLS, or isogeny-chain claims, follow [the loop
rules](docs/endomorphism-rules.md),
[`audit-curve`](.claude/skills/audit-curve/SKILL.md),
[`transfer`](.claude/skills/transfer/SKILL.md), and
[`KN-TECH-6a2ef9`](knowledge/techniques/KN-TECH-6a2ef9.md). They bind scope,
evidence, controls, costs, statistics, and labels. Evaluate
factored/mixed-degree loops with explicit working-field maps, subgroup action,
closure/recovery, bounds, and paired baseline costs. Trials use `run`; audits do
not change state. Structure or bounded-null evidence proves neither speedup,
impossibility, nor unknown-scalar recovery.

For ordinary curves record
`Delta_pi=t^2-4q=f_pi^2 D_K` and
`Z[pi]=O_(f_pi) subseteq End(E)=O_(f_E) subseteq O_K` separately.
`f_E|f_pi`; independently certify `f_E` unless `f_pi=1`. Label separable
`ell!=char(F_q)` edges from certified endpoint conductors:
`horizontal|ascending|descending|unresolved`. Koblitz
`tau`/characteristic-power Frobenius are inseparable. Conductors are leads,
not ECDLP-bit discounts.

Transfers require explicit maps, subgroup preservation, and complete costs;
advice supports only its holder. Singular/invalid formula-compatible companions
establish only **implementation-weak**; confirmation-only oracles need explicit
reductions. Use only **class-weak**, **weak representative exists**,
**source-transfer-weak**, **implementation-weak**, or **no weakness found in
scope**. Bounded or zero-hit statistics do not prove absence.

## Cursor Cloud specific instructions

Use `/usr/local/bin/python3` (CPython 3.12.8, `.python-version`), never the
image's Ubuntu `/usr/bin/python3`: its builtin `_md5` fails
`tests/test_harness.py::test_md5_pin_mechanism_real_registry_is_distinct`.
Install the CI extras, not only `make install` (`.[agent,dev]`):
`python3 -m pip install -e ".[dev,agent,campaign-mcp,research-loop,gf2]"`.
`autoresearch` and `pytest` land in `~/.local/bin`, linked into
`/usr/local/bin`; `python3 -m pytest` and `python3 -m orchestration` work
either way. `autoresearch doctor` needs no API keys; `.env.example` variables
serve only token-spending commands. Dashboard:
`GITHUB_REPOSITORY=aburan28/crypto-autoresearcher python3 -m ui --host
127.0.0.1 --port 8787` (unset, source links come from `origin`, whose Cloud
Agent remote embeds a credential). `formal/setup.sh` (Lean) is not part of
this environment.
