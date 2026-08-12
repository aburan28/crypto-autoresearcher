# Research Loop v2 Migration Plan

**Status:** Proposed  
**Date:** 2026-08-08  
**Architecture:** `docs/research-loop-v2.md`  
**Implementation:** `docs/research-loop-v2-implementation-plan.md`  
**Migration strategy:** per-goal, additive, shadow-first, reversible, and source-of-truth preserving

## 1. Purpose

This document defines how to introduce Research Loop v2 into the existing
crypto-autoresearcher without rewriting historical research state, invalidating
committed evidence, interrupting active campaigns, or turning a derived runtime
store into a second source of truth.

The migration is not a one-time database conversion. It is a staged change in
control-plane behavior:

1. project existing ledger, queue, inference, and knowledge state into typed v2
   views;
2. compare v2 retrieval, routing, frontier, and continuation decisions against
   the current system in shadow mode;
3. enable v2 components independently behind per-goal modes;
4. cut over one non-critical goal at a time;
5. retain a tested path back to the existing manual/static loop until v2 has
   demonstrated recovery, quality, and evidence-integrity parity.

A migration is successful only when the same committed research history remains
readable, the same authority boundaries remain enforceable, and disabling v2
returns the goal to the current workflow without reconstructing or editing
historical records.

## 2. Migration decision summary

The recommended migration is:

- **No big-bang conversion.** Goals opt in individually.
- **No destructive rewrite.** Existing `GOAL-*`, `RQ-*`, `H-*`, `EXP-*`,
  `EV-*`, `DEC-*`, `KN-*`, queue, handoff, run, review, and archive records are
  preserved byte-for-byte.
- **No dual authority.** Ledger decisions and immutable archive commits remain
  authoritative. Campaign SQLite, frontier projections, route telemetry, and
  Qdrant remain derived.
- **Dual read, single write.** v2 reads both legacy and v2 artifacts, but
  official state still changes only through the existing Coordinator ledger
  archive path.
- **Shadow before scheduling authority.** Retrieval, routing, successor
  generation, and controller transitions must first run without affecting live
  execution.
- **Per-goal cutover.** A committed `campaign.yaml` selects the migration mode
  for one goal.
- **Environment switches may disable, never silently enable.** An emergency
  environment flag can force legacy behavior; enabling active v2 behavior must
  be committed for the goal.
- **Rollback is behavioral, not historical.** Stop the v2 controller, restore
  static routing and the previous KB alias, and continue from the latest
  committed ledger checkpoint. Do not delete v2 records to pretend the trial
  did not happen.

## 3. Current-state constraints that the migration must preserve

### 3.1 Official research state

The repository already treats committed ledger and archive records as the
source of truth. Goal records may be sharded: a mutable head and append-only
checkpoint files are materialized together by validation tooling. Migration
code must consume the validated materialized view, not parse one convenient
file and assume it is current.

The migration must preserve:

- append-only correction and supersession semantics;
- explicit claim scope and evidence tier;
- distinction between infrastructure failure and mathematical evidence;
- independent review before claim-changing transitions;
- snapshot and ledger archive sequencing;
- exact Git provenance for every official state transition; and
- the rule that only the canonical Coordinator may change official state.

### 3.2 Bounded workers

`orchestration/agent/graph.py` is a bounded worker loop. Its normal completion
means that one task stopped requesting tools; it does not mean that a research
goal is complete. Migration must not retrofit indefinite campaign behavior
inside this worker graph. The new campaign controller remains a separate layer.

### 3.3 Dispatch queues

The current dispatcher validates `crypto.autoresearch.dispatch_queue.v1`, task
dependencies, budgets, write scopes, archive ownership, and independent-review
requirements. Queue v1 is already used by active and historical goals.

Migration must therefore:

- continue accepting queue v1 indefinitely during the rollout;
- add v2 fields as optional extensions or introduce a separately versioned
  queue reader with an explicit compatibility adapter;
- never reinterpret a terminal v1 task as runnable work;
- never infer a mathematical result from a task's terminal state alone; and
- preserve task IDs, archive relationships, and declared artifact paths.

### 3.4 Focus queues and research alternatives

The existing focused-loop machinery limits the active set and carries claims,
runs, corrections, attention contracts, resource estimates, and candidate
status. The v2 frontier is broader than the active dispatch queue, but it may
not erase or duplicate the focused-loop semantics.

Migration must distinguish:

- **frontier node:** a research alternative that may eventually be selected;
- **focus candidate:** a bounded candidate eligible for attention under the
  existing focus policy; and
- **dispatch task:** an approved, executable unit with exact scopes and gates.

### 3.5 Model policies and bindings

Model capability policies have immutable identifiers, explicit capability
floors, strict downgrade behavior, independent-session requirements, and
vendor-specific bindings kept in a separate file. The migration may automate
policy selection, but it may not weaken those contracts.

### 3.6 Knowledge base

`crypto-kb` already treats Git/object storage as source of truth and Qdrant as a
rebuildable index. It performs provenance-aware hybrid retrieval and exposes
bounded agent-facing results. Migration must extend this design rather than
replace it with an authoritative vector store or model-generated metadata.

### 3.7 Control-plane primacy

The repository already documents one canonical control plane at a time. The v2
lease enforces that rule; it does not create a second Coordinator. A migration
must fail closed when two controllers contend or when the checkout is behind the
committed source state.

## 4. Goals and non-goals

### 4.1 Goals

The migration must provide:

1. a reproducible inventory of legacy state before any cutover;
2. an idempotent projection from existing records into v2 runtime state;
3. a compatibility reader for old queues, handoffs, receipts, and goals;
4. a versioned knowledge-index migration with measurable parity and rollback;
5. a shadow route comparison before the router controls model selection;
6. a bounded frontier bootstrap from current goal state;
7. an explicit protocol for draining or reconciling in-flight work;
8. per-goal activation and kill switches;
9. crash-safe cutover with exact source commits and idempotency keys;
10. a durable migration report that proves what was read, written, skipped, or
    blocked; and
11. acceptance gates that must pass before legacy behavior ceases to be the
    default.

### 4.2 Non-goals

The initial migration does not:

- rewrite historical records into a new canonical schema;
- convert model transcripts into authoritative memory;
- infer missing review, evidence, or status transitions;
- automatically reopen completed or paused goals;
- import every historical idea into the live frontier;
- require GraphRAG, a learned router, or embedding fine-tuning;
- delete old Qdrant collections immediately after alias cutover;
- remove queue v1, focus queue v3, or existing skills during the initial
  rollout; or
- change the canonical control plane merely because a stronger model is
  available elsewhere.

## 5. Migration modes

Each opt-in goal gets a committed file:

```yaml
schema: crypto.autoresearch.campaign_config.v1
goal_id: GOAL-ECDLP-001
mode: shadow
source_commit: <full-git-sha>
policy_versions:
  frontier: frontier-policy.v1
  router: router-policy.v1
  reflection: reflection-policy.v1
knowledge:
  required_index_generation: null
  freshness_mode: direct_record_fallback
routing:
  mode: shadow
memory:
  mode: shadow
controller:
  lease_required: true
  automatic_dispatch: false
```

Supported campaign modes:

| Mode | Reads legacy state | Builds v2 projections | Records v2 decisions | May schedule work | May change official state |
|---|---:|---:|---:|---:|---:|
| `legacy` | yes | no | no | existing workflow only | existing Coordinator only |
| `observe` | yes | yes | telemetry only | no | no |
| `shadow` | yes | yes | immutable shadow artifacts | no | no |
| `assist` | yes | yes | proposals presented to Coordinator | only after explicit Coordinator admission | existing Coordinator only |
| `active` | yes | yes | yes | yes, through existing dispatcher and archive gates | existing Coordinator ledger path only |
| `paused` | yes | yes | health and resume records only | no | no |

Mode transitions are monotonic only in authority, not irreversible. A goal may
move from `active` back to `assist`, `shadow`, or `legacy` without rewriting its
history.

An environment override may force a lower-authority mode:

```text
AUTORESEARCH_FORCE_CAMPAIGN_MODE=legacy|observe|shadow|assist
```

It may not force `active`. Active mode requires committed configuration and a
valid lease.

Component-level switches permit narrower rollback:

```text
AUTORESEARCH_ROUTER_MODE=static|shadow|active
AUTORESEARCH_FRONTIER_MODE=disabled|shadow|active
AUTORESEARCH_KB_BUNDLE_MODE=legacy|shadow|required
AUTORESEARCH_MEMORY_MODE=disabled|shadow|active
AUTORESEARCH_REFLECTION_MODE=disabled|shadow|active
```

The effective mode is the least authoritative of committed configuration and
forced environment overrides. The effective mode is recorded in every receipt.

## 6. Compatibility contract

| Existing artifact | v2 read behavior | v2 write behavior | Rollback behavior |
|---|---|---|---|
| `ledger/goals/**` | materialize through existing validator semantics | no in-place rewrite; normal superseding decisions only | legacy workflow reads unchanged records |
| goal checkpoint files | replay in committed order | append new checkpoint only through archive | retained and still authoritative |
| dispatch queue v1 | accepted through compatibility reader | active mode may continue emitting v1 initially | existing dispatcher remains usable |
| dispatch queue v2 | optional new fields, explicit schema version | emitted only after v1 replay parity | adapter can render equivalent v1 when fields permit |
| focus queue v3 | read as candidate/claim context | not rewritten by migration | existing focus selector continues to work |
| handoffs without `inference` | route using current role default | new tasks include explicit route/evidence references | old handoffs remain valid |
| handoffs with explicit policy | treat as a hard operator choice | router does not replace unless handoff explicitly opts into `auto` | static resolver executes original policy |
| inference receipts | parse when complete; tolerate legacy absence | new receipts add route/evidence/escalation IDs | legacy consumers ignore additive fields |
| model policies | immutable IDs and floors | additive policies/aliases only | static role defaults remain available |
| model bindings | current resolver remains authoritative for eligibility | router chooses among resolver-approved candidates | restore configured default backend/policy |
| knowledge corpus | source of truth | append/supersede through current curation rules | unchanged |
| Qdrant collection | legacy generation remains readable | build new generation in parallel | atomically restore old alias |
| worker checkpoints | resume only the same task/runtime contract | no cross-version mutation without compatibility hash | abandon derived checkpoint and replay from committed task state |
| campaign SQLite | rebuilt from committed records | derived transitions and caches | delete/rebuild safely |
| standing goal PR | remains review surface | v2 records are added to the same goal PR | legacy work continues on same branch/PR |

## 7. Source-of-truth hierarchy during migration

When records disagree, use this order:

1. reachable committed ledger/archive records after existing validation and
   correction materialization;
2. immutable experiment, review, receipt, and artifact files referenced by
   those records;
3. committed goal configuration and campaign checkpoint snapshots;
4. committed dispatch and focus queues;
5. direct repository/object-store knowledge sources;
6. Qdrant or other retrieval indexes;
7. campaign SQLite projection;
8. telemetry and caches;
9. agent final text.

A lower layer may signal an inconsistency but may not overwrite the higher
layer. In particular, a runtime database saying `completed` does not complete a
goal whose ledger says `active`.

## 8. Inventory before migration

Before bootstrapping a goal, generate an immutable inventory report containing:

- repository and branch;
- exact source commit and merge base with the target branch;
- whether the checkout is ahead, behind, or dirty;
- goal ID and materialized goal status;
- current batch and dispatch queue path;
- latest verified archive commit;
- exact next action and its cited decision record;
- active, queued, blocked, running, and terminal tasks;
- unresolved archive or review obligations;
- active hypotheses and their committed statuses;
- open focus candidates and corrections;
- campaign budget and remaining allowance;
- model policy/binding configuration hashes;
- available and probed backends;
- KB corpus fingerprint, index generation, collection alias, and index watermark;
- active controller or writer leases;
- open PR and branch state; and
- every condition that would block cutover.

Proposed command:

```bash
python -m orchestration.campaign migrate inventory \
  --goal GOAL-ECDLP-001 \
  --output coordination/goals/GOAL-ECDLP-001/migration/inventory.json \
  --report coordination/goals/GOAL-ECDLP-001/migration/inventory.md
```

The inventory is hash-bound. `bootstrap`, `cutover`, and `rollback` accept its
hash and refuse to run if source state has changed without a new inventory.

## 9. Legacy-to-v2 state mapping

### 9.1 Goal status

| Materialized legacy status | Initial campaign status | Automatic behavior |
|---|---|---|
| `active` with valid next action | `active` in observe/shadow; eligible for assist/active cutover | seed next action, then other bounded frontier sources |
| `active` without valid next action | `needs_refill` projection | run refill in shadow; do not invent official state |
| `paused` | `paused` | preserve exact pause reason and resume action; never auto-resume |
| `completed` | `completed_read_only` | index for history; never dispatch or reopen automatically |
| unknown or contradictory | `migration_blocked` | require existing validator/Coordinator resolution |

The goal status is not copied by reading a single YAML field. Migration calls
or reuses the same materialization logic that validates sharded goal records and
ordered corrections.

### 9.2 Dispatch task state

| Legacy task state | v2 treatment |
|---|---|
| `queued` | import as an executable reference only if dependencies, scopes, budgets, archive ownership, and source commit still validate |
| `blocked` | import as blocked with the exact blocking dependency/reason |
| `running` | do not adopt automatically; mark `reconciliation_required` until the original runtime proves completion or the Coordinator records repair/cancellation |
| `completed` | historical execution node only; never rerun solely because it appears in an imported queue |
| `failed` | historical infrastructure/task outcome; branch only from the committed decision or verified receipt |
| `invalid` | historical invalid execution; no scientific inference |
| `cancelled` | historical terminal node; no automatic successor unless one is explicitly recorded |

### 9.3 Hypothesis and proposal status

Migration preserves status rather than translating it into a new evidentiary
scale. Frontier eligibility is a separate decision.

Recommended bootstrap rules:

- `approved`, `specified`, or `analyzed`: may seed a frontier node when the goal
  still references the hypothesis and an actionable test remains.
- `supported`: may seed replication, generalization, or adversarial-check nodes;
  never a duplicate proof of support.
- `weakened`: may seed a repair, missing-control, mechanism-separation, or
  alternative-mechanism node when a committed decision requests it.
- `rejected-scoped`: may seed only work outside the rejected scope or a
  correction backed by new evidence.
- completed/closed proposals: history only unless a Coordinator explicitly
  re-admits them.

### 9.4 Focus candidates

Only active or queued focus candidates with valid attention contracts,
resource estimates, dependencies, and corrections are eligible to seed the
frontier. Completed, invalid, or superseded candidates remain historical.

### 9.5 Decisions and evidence

Existing decisions and evidence are referenced, never re-authored. A migration
projection records:

```yaml
source_record_id: DEC-...
source_commit: <sha>
content_hash: <sha256>
projection_kind: decision|evidence|hypothesis|task|knowledge
projection_schema: crypto.autoresearch.projection.v1
```

No new `DEC-*` or `EV-*` ID is minted merely to state that migration read an old
record.

## 10. Stable identifiers and idempotency

Every imported object gets a deterministic projection ID derived from:

```text
SHA256(
  projection_schema ||
  repository_full_name ||
  source_commit ||
  source_path ||
  source_record_id ||
  source_content_hash
)
```

Frontier nodes imported from legacy state also carry an
`origin_fingerprint`. Re-running bootstrap against the same source commit must
produce the same nodes and no additional work.

Every side effect uses an idempotency key:

```text
<goal_id>:<campaign_epoch>:<transition>:<source_checkpoint_hash>:<target_id>
```

The controller stores the key before dispatch and records the resulting task,
archive, or checkpoint. On restart it reconciles rather than repeating the
operation.

## 11. Frontier bootstrap

The initial frontier is intentionally bounded. Importing the entire historical
corpus would create a noisy pseudo-backlog and make migration appear successful
by generating work that no current decision requested.

Seed sources, in priority order:

1. the goal's exact committed `next_action`;
2. valid nonterminal tasks in the current committed dispatch queue;
3. current focus candidates that are active or queued;
4. active hypotheses with an explicit unexecuted test or unresolved gate;
5. obligations carried by the latest committed decision, such as replication,
   missing control, cost accounting, or heuristic validation;
6. the weakest-supported live claim's replication/control path; and
7. one shadow refill invocation if all above produce no valid node.

Every imported node records:

- source path, record ID, commit, and content hash;
- why it is actionable now;
- dependencies and blocking obligations;
- expected information gain and decision impact;
- resource estimate or a flag that one must be produced before admission;
- required review class;
- deduplication key; and
- whether it is `legacy_bound`, `shadow_generated`, or `v2_native`.

A migrated node does not become a dispatch task until the existing Coordinator
admission and queue validation gates pass.

## 12. Queue migration

### 12.1 Initial strategy

Keep emitting queue v1 during the first active canary. The campaign controller
owns continuity and frontier selection, while the current dispatcher continues
to own executable-task validation.

This isolates the migration:

```text
v2 frontier/controller
        ↓ selects bounded work
queue v1 adapter
        ↓
existing research_dispatch.py
        ↓
existing snapshot/review/ledger gates
```

### 12.2 Queue v2 introduction

Introduce queue v2 only after queue v1 replay parity. New fields should be
additive and related to routing/knowledge provenance, for example:

```yaml
schema: crypto.autoresearch.dispatch_queue.v2
campaign_checkpoint_id: CHECKPOINT-...
frontier_node_id: FRONTIER-...
evidence_bundle_id: EVIDENCE-BUNDLE-...
route_decision_id: ROUTE-...
idempotency_key: GOAL-...:...
```

The compatibility reader must:

- accept v1 unchanged;
- normalize v1 into the in-memory v2 model with absent optional fields;
- preserve the original schema and content hash in receipts;
- reject ambiguous coercions; and
- render a v1-compatible queue when no v2-only behavior is required.

Queue v1 removal is outside the initial migration.

## 13. In-flight work reconciliation

A goal cannot cut over while its state is ambiguous.

### 13.1 Drain protocol

Before active cutover:

1. prevent admission of a new batch for the target goal;
2. acquire the canonical-controller migration lease;
3. fetch and merge the latest target branch according to current merge policy;
4. render the current dispatch plan;
5. wait for or explicitly reconcile every `running` task;
6. run any due snapshot archive alone;
7. finish required independent reviews;
8. run any due ledger archive alone;
9. verify Git receipts and ledger materialization;
10. record the source commit for bootstrap; and
11. generate a new inventory hash.

This is a logical drain, not a requirement that the entire research goal have
no queued work. Queued tasks may be imported if still valid.

### 13.2 Ambiguous running task

When a task is marked running but no live runtime can prove ownership:

- do not mark it completed;
- do not silently rerun it;
- inspect checkpoint, process, receipt, artifact, and lease state;
- record `orphaned_running_task` in the migration report;
- require a Coordinator decision to resume, cancel, or create a repair task; and
- keep cutover blocked until that decision is committed.

### 13.3 Existing worker checkpoints

Resume an existing checkpoint only when all of these match:

- task ID;
- task content hash;
- role contract hash;
- inference-policy hash;
- tool-surface hash;
- source commit or compatible read scope;
- runtime/checkpointer format version; and
- write-scope contract.

Otherwise discard the derived checkpoint and resume from committed task state
through an explicitly recorded repair/replay path.

## 14. Knowledge-base migration

### 14.1 Versioned collection strategy

Do not mutate the live Qdrant collection in place for schema-affecting changes.
Build a new generation:

```text
crypto-kb-v1-current   ← existing alias target
crypto-kb-v2-build     ← parallel ingest and evaluation
crypto-kb-current      ← stable read alias
```

Recommended process:

1. fingerprint the current corpus and legacy collection;
2. create a v2 collection with a versioned schema;
3. ingest from the same source-of-truth objects and repository records;
4. retain deterministic source IDs and point lineage;
5. run existing retrieval evaluation plus migration-specific tests;
6. run dual queries against v1 and v2 in shadow mode;
7. produce a diff report for top-k sources, filters, citations, contradictions,
   and context size;
8. switch `crypto-kb-current` atomically only after gates pass;
9. retain the previous collection for rollback; and
10. delete old generations only under a later explicit retention policy.

### 14.2 Additional freshness metadata

Add or expose:

- `source_commit`;
- `source_content_hash`;
- `index_generation`;
- `indexed_at`;
- `ingest_manifest_hash`;
- `corpus_fingerprint`;
- `latest_source_commit_seen`; and
- `latest_source_commit_indexed`.

An evidence bundle records these values so routing and verification know
whether retrieval covered the latest committed research state.

### 14.3 Read-your-writes during migration

If a ledger archive is newer than the KB watermark:

1. retrieve exact referenced records directly from Git/object storage;
2. combine them with indexed background literature;
3. mark the evidence bundle `direct_record_fallback: true`;
4. lower freshness confidence for non-exact topical coverage;
5. schedule or signal ingestion refresh; and
6. refuse high-impact synthesis when required evidence remains unavailable.

A larger model is not a substitute for missing evidence.

### 14.4 Metadata admission

Migration may derive metadata deterministically from existing records. It may
not promote model-suggested status, authority, evidence level, supersession, or
experiment linkage into authoritative filters.

### 14.5 KB cutover gates

Before alias switch:

- exact-identifier recall does not regress below the current gate;
- filter correctness remains 1.0 on the migration suite;
- source attribution remains above the existing gate;
- superseded records remain excluded by default;
- contradiction fixtures retrieve both sides;
- median context remains within the configured budget;
- stale-index fallback is verified end to end;
- prompt-injection fixtures cannot alter route or tool authority; and
- every shadow evidence bundle can be reproduced from its source/index hashes.

## 15. Model-routing migration

### 15.1 Preserve explicit choices

Existing handoffs with an explicit `inference.policy` remain authoritative for
that task. The router may score alternatives in shadow mode, but it does not
replace an explicit policy unless the handoff opts into automatic routing:

```yaml
inference:
  policy: auto
  minimum_policy: executor-implementation
  fallback_allowed: false
  degraded_allowed: false
```

Legacy handoffs without an inference block continue to resolve through current
role defaults. Their behavior must not change merely because the router was
installed.

### 15.2 Shadow comparison

For every eligible task, record:

- actual legacy policy and resolved model;
- v2 predicted policy and candidate set;
- hard-gate reasoning;
- KB coverage and freshness;
- predicted and actual cost/latency;
- verifier outcome;
- whether v2 would have escalated; and
- whether the choices disagree.

No shadow disagreement changes execution.

### 15.3 Activation order

Activate routing by task class, not globally:

1. deterministic/mechanical tasks with exact verifiers;
2. extraction, normalization, and bounded summarization;
3. routine implementation with repository tests;
4. experiment execution under frozen specifications;
5. general analysis only after calibrated evaluation;
6. hypothesis generation and meta-reflection remain direct strong-model routes;
7. adversarial and breakthrough review remain protected by their existing
   floors and independent-session requirements.

### 15.4 Static fallback

At any point:

```text
AUTORESEARCH_ROUTER_MODE=static
```

returns selection to explicit handoff policy or current role default. The
adapter resolver remains the final eligibility authority in both modes.

### 15.5 Learned router boundary

Historical telemetry may be backfilled where receipts contain sufficient
features, but it must be labeled observational. A learned router is not enabled
until project-specific shadow/active outcomes provide verifier-labeled data.
It may rank eligible candidates only; it may not waive capability floors,
review independence, write scopes, evidence requirements, or terminal policy.

## 16. Campaign runtime-store migration

### 16.1 Derived SQLite store

The v2 store is a materialized projection. Bootstrap writes:

- source repository/commit;
- inventory hash;
- materialized goal status;
- imported source objects and content hashes;
- frontier nodes and lineage;
- current controller mode;
- policy/configuration hashes;
- idempotency keys;
- outstanding obligations; and
- last committed campaign checkpoint.

It does not become authoritative merely because it supports transactions.

### 16.2 Store schema migrations

Use explicit forward migrations with a schema table:

```sql
CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL,
  code_commit TEXT NOT NULL,
  migration_hash TEXT NOT NULL
);
```

Rules:

- runtime DB migrations are repeatable in tests and applied once in production;
- every version has a backup/export path;
- destructive column removal is postponed until legacy readers are retired;
- unknown newer versions fail closed rather than being opened by older code;
- a derived DB may always be rebuilt from committed checkpoints and source
  records; and
- rebuild parity is part of every release gate.

### 16.3 Checkpoint compatibility

Committed campaign checkpoints are versioned documents, not SQLite dumps. A
new controller version must either read the old checkpoint schema or provide a
pure deterministic upgrader whose output hash is recorded.

## 17. Memory migration

### 17.1 What is imported

The migration may index and reference existing:

- curated knowledge entries;
- verified findings;
- negative results;
- experiment and review records;
- decisions and corrections;
- explicit strategic lessons already committed; and
- unresolved questions or obligations.

### 17.2 What is not imported as fact

Do not treat as authoritative memory:

- raw chain-of-thought or hidden reasoning;
- model final text without supporting artifacts;
- uncommitted working-tree notes;
- failed-task status without a verified receipt;
- a shadow route/proposal merely because it was generated; or
- inferred relationships that were not deterministically derived or reviewed.

### 17.3 Memory admission rollout

- `disabled`: current KB behavior only;
- `shadow`: produce proposed memory records and admission reasons, write no
  authoritative knowledge;
- `active`: write only records passing deterministic provenance checks and the
  existing Coordinator archive/curation path.

Existing knowledge entries are never rewritten merely to conform to a new
memory schema. Add projections or superseding records.

## 18. Migration phases and gates

### Phase M0 — Freeze the contract and establish baselines

**Changes**

- define migration-report, projection, and campaign-config schemas;
- add inventory and replay fixtures from real repository goals;
- capture current queue, routing, KB, recovery, and cost baselines;
- add global force-disable switches.

**Exit gates**

- current main behavior remains unchanged;
- all legacy queue/handoff fixtures validate;
- inventory is deterministic for a fixed commit;
- no v2 component can schedule work.

**Rollback**

Remove or disable read-only tooling; no state conversion occurred.

### Phase M1 — Compatibility readers and projections

**Changes**

- materialized goal reader;
- queue v1/handoff/receipt compatibility adapters;
- deterministic projection IDs;
- derived campaign store bootstrap in `observe` mode.

**Exit gates**

- projection replay is byte/hash stable;
- zero official-state writes;
- every imported object cites a reachable source commit/path/hash;
- completed and terminal tasks are never runnable.

**Rollback**

Delete the derived store and return to `legacy` mode.

### Phase M2 — KB v2 parallel generation

**Changes**

- v2 collection schema and freshness metadata;
- dual-query shadow comparison;
- direct-record fallback;
- migration-specific retrieval evaluation.

**Exit gates**

- retrieval gates pass;
- v1 remains the read alias until explicit switch;
- rollback alias operation is tested;
- evidence bundles reproduce from hashes.

**Rollback**

Keep or restore the v1 alias; delete/rebuild the v2 collection if needed.

### Phase M3 — Router shadow mode

**Changes**

- deterministic feature extraction;
- candidate enumeration through the current resolver;
- shadow route decisions and cost/quality telemetry;
- no change to actual model selection.

**Exit gates**

- zero proposed hard-gate violations;
- every disagreement is explainable from recorded features;
- explicit legacy policies remain untouched;
- cost inputs are versioned and missing prices do not cause unsafe routing.

**Rollback**

Disable shadow recording; actual routing was unchanged.

### Phase M4 — Frontier shadow mode

**Changes**

- bootstrap bounded frontier from the current goal state;
- run successor generation and meta-reflection in shadow;
- compare proposed next actions against committed Coordinator actions;
- exercise deduplication and refill without dispatch.

**Exit gates**

- every node has source lineage and a falsifiable/actionable contract;
- no terminal task is reintroduced as executable work;
- duplicate and make-work rates meet policy gates;
- worker final text cannot terminate the campaign projection.

**Rollback**

Discard derived frontier/store; committed goal state is unchanged.

### Phase M5 — Assist mode

**Changes**

- present evidence bundle, route recommendation, and ranked successors to the
  Coordinator;
- Coordinator explicitly admits work to the existing queue/archive path;
- retain legacy next-action generation as fallback.

**Exit gates**

- accepted recommendations preserve existing scopes and review gates;
- rejection reasons are captured for calibration;
- no v2 proposal changes official state without Coordinator admission;
- crash/restart returns to the same advisory state.

**Rollback**

Set mode to `shadow` or `legacy` and continue manually.

### Phase M6 — Active canary

**Scope**

One non-critical goal with bounded costs, strong fixtures, no unresolved
running tasks, and a standing PR.

**Changes**

- v2 controller selects bounded frontier work;
- queue v1 adapter dispatches through existing machinery;
- router active only for already-qualified task classes;
- official state still changes through snapshot/review/ledger archives;
- every transition writes a campaign checkpoint.

**Exit gates**

- multiple batches complete across at least one process restart;
- zero duplicate side effects;
- zero silent downgrades or review bypasses;
- every nonterminal checkpoint has a valid successor or committed pause reason;
- rollback drill succeeds without editing history;
- cost reduction is measured without verifier-quality regression.

**Rollback**

Force `assist` or `legacy`, stop the controller, release the lease, and resume
from the latest committed ledger checkpoint.

### Phase M7 — Broaden active use

Expand by goal class only after replay and canary evidence. Keep high-impact or
publication-sensitive campaigns in `assist` until their specific verification
suite passes.

**Exit gates**

- recovery, retrieval, routing, and evidence-integrity metrics remain stable
  across diverse goals;
- operational runbooks have been exercised;
- no component requires deleting legacy artifacts to function.

### Phase M8 — Make v2 the default for new goals

New goals may default to `shadow` or `assist`, then `active` after preflight.
Existing goals remain in their committed mode. Legacy readers and the static
router remain until an explicit later deprecation decision.

## 19. Active cutover protocol for one goal

Proposed command sequence:

```bash
# 1. Refresh and validate repository state.
git fetch --all --prune
git merge origin/main
python tools/validate_ledger.py
python tools/check_merge_hygiene.py

# 2. Inventory and preflight.
python -m orchestration.campaign migrate inventory \
  --goal GOAL-ECDLP-001 \
  --output coordination/goals/GOAL-ECDLP-001/migration/inventory.json

python -m orchestration.campaign migrate preflight \
  --inventory coordination/goals/GOAL-ECDLP-001/migration/inventory.json

# 3. Bootstrap derived state without authority.
python -m orchestration.campaign migrate bootstrap \
  --goal GOAL-ECDLP-001 \
  --mode shadow \
  --inventory-hash <sha256>

# 4. Replay historical/current transitions and compare.
python -m orchestration.campaign migrate replay \
  --goal GOAL-ECDLP-001 \
  --through-commit <sha>

python -m orchestration.campaign migrate verify \
  --goal GOAL-ECDLP-001

# 5. Run assist mode before active cutover.
python -m orchestration.campaign mode set \
  --goal GOAL-ECDLP-001 \
  --mode assist

# 6. Drain/reconcile in-flight work and re-inventory.
python -m orchestration.campaign migrate reconcile \
  --goal GOAL-ECDLP-001

# 7. Cut over against an exact source commit and inventory hash.
python -m orchestration.campaign migrate cutover \
  --goal GOAL-ECDLP-001 \
  --source-commit <full-sha> \
  --inventory-hash <sha256> \
  --target-mode active
```

These commands are proposed interfaces, not existing commands. Every mutating
command defaults to dry-run unless `--apply` is present, prints the exact files
and runtime state it will alter, and refuses a dirty or stale source checkout.

## 20. Migration tooling layout

```text
orchestration/campaign/
├── migration.py            # inventory, bootstrap, replay, cutover, rollback
├── projection.py           # deterministic legacy -> v2 projection
├── compatibility.py        # goal, queue, handoff, receipt readers
├── reconcile.py            # running-task and archive reconciliation
├── migrations/             # runtime-store schema migrations
│   ├── 0001_initial.py
│   ├── 0002_route_records.py
│   └── ...
└── cli.py

schemas/
├── campaign-config.schema.json
├── migration-inventory.schema.json
├── migration-report.schema.json
├── projection-record.schema.json
└── rollback-record.schema.json

coordination/goals/<GOAL-ID>/migration/
├── inventory.json
├── inventory.md
├── bootstrap-report.json
├── replay-report.json
├── cutover-record.yaml
└── rollback-record.yaml
```

The migration directory is append-only in practice. A new inventory or report
gets a new content-addressed or timestamped path rather than overwriting the
record used for an earlier cutover.

## 21. Migration report contract

Each operation emits a machine-readable report:

```yaml
schema: crypto.autoresearch.migration_report.v1
operation_id: MIG-...
operation: inventory|bootstrap|replay|preflight|cutover|rollback
goal_id: GOAL-...
mode_before: legacy
mode_after: shadow
source:
  repository: aburan28/crypto-autoresearcher
  branch: agent/...
  commit: <sha>
  inventory_hash: <sha256>
configuration_hashes:
  campaign: <sha256>
  router: <sha256>
  frontier: <sha256>
  model_policies: <sha256>
  model_bindings: <sha256>
  kb_retrieval: <sha256>
read_records:
  count: 0
  digest: <sha256>
projected_records:
  count: 0
  digest: <sha256>
skipped_records:
  - source: ...
    reason: terminal_history|superseded|out_of_scope|duplicate
blocked_items:
  - id: ...
    reason: ...
side_effects:
  files_written: []
  runtime_store_changes: []
  alias_changes: []
validation:
  legacy_replay_passed: true
  source_reachable: true
  hard_gate_violations: 0
  duplicate_side_effects: 0
result: passed|blocked|failed|rolled_back
```

A report saying `passed` does not promote scientific evidence. It proves only
that a migration operation satisfied its technical and provenance gates.

## 22. Rollback plan

### 22.1 Immediate behavioral rollback

1. force the target goal to `assist`, `shadow`, or `legacy`;
2. stop the v2 controller after its current atomic transition;
3. prevent new v2 dispatch admission;
4. release or expire the controller lease;
5. restore static routing;
6. restore the prior KB alias if the KB migration is implicated;
7. render the existing dispatch/goal state through legacy tooling;
8. verify the latest committed ledger/archive checkpoint; and
9. record a rollback artifact naming the reason, last v2 checkpoint, and exact
   resume action.

### 22.2 What rollback does not do

Rollback does not:

- erase v2 checkpoints, telemetry, or migration reports;
- revert legitimate ledger decisions already committed through normal gates;
- pretend a dispatched experiment did not run;
- change hypothesis status without a new decision;
- delete the source corpus; or
- force-push/rewrite branch history.

### 22.3 Component rollback

| Component | Rollback action |
|---|---|
| campaign controller | stop process, force lower mode, release lease |
| frontier | stop admission; retain snapshot for audit; derive next action through legacy skill |
| router | set `static`; execute explicit policy or role default |
| KB | switch stable alias to previous collection; retain direct-record fallback |
| memory admission | set `disabled`; keep already committed valid records |
| reflection | set `disabled`; ignore unadmitted shadow proposals |
| runtime store | archive/delete and rebuild from committed state |
| queue v2 | render/read compatible v1 queue when possible; otherwise keep goal in assist until resolved |

### 22.4 Rollback acceptance test

A canary is not approved until this drill passes:

1. begin active mode;
2. complete at least one normal checkpoint;
3. inject a controlled controller or KB failure;
4. force legacy mode;
5. render the goal and queue using existing tooling;
6. execute or plan the recorded next action without using campaign SQLite;
7. prove no duplicate task/archive was created; and
8. re-enter shadow mode from the same committed state.

## 23. Failure handling during migration

| Failure | Required response |
|---|---|
| checkout behind target branch | stop; fetch/merge and regenerate inventory |
| dirty working tree in authoritative paths | stop; separate or archive changes before migration |
| two controller leases | fail closed; neither advances official state until primacy is resolved |
| goal materialization fails | block migration; repair through existing correction/validation process |
| queue v1 cannot normalize losslessly | continue legacy for that queue; add fixture and adapter support |
| unresolved running task | block active cutover; reconcile explicitly |
| task imported twice | deduplicate by source hash/idempotency key; treat duplicate side effect as release blocker |
| KB v2 misses required evidence | keep v1 alias or direct fallback; do not compensate with a stronger model |
| v2 route violates a policy floor | fail the route; record hard-gate bug; retain static routing |
| price/latency data missing | optimize for eligibility and quality only; never guess a cheap route |
| crash after dispatch before checkpoint | reconcile idempotency key and existing task before retry |
| crash after archive commit before runtime update | rehydrate from Git and mark transition complete; do not recommit |
| generated frontier contains make-work | reject admission, record reason, rerun bounded refill or pause honestly |
| retrieved prompt injection | treat as data; tools, route floors, role, and write scopes remain external constraints |
| branch/PR diverges during cutover | stop admission, merge according to current policy, validate, re-inventory |

## 24. Test plan

### 24.1 Golden legacy fixtures

Use representative committed fixtures, including:

- a sharded, long-running goal with many corrections and checkpoints;
- a small completed goal;
- a paused goal with a resume action;
- queue v1 with completed and review-required tasks;
- queue v1 with blocked dependencies;
- legacy handoff without an inference block;
- explicit-policy handoff;
- focus queue v3 with corrections and resource estimates;
- valid and invalid archive receipts;
- stale and current KB generations; and
- an orphaned running-task scenario.

Fixtures should come from real record shapes but may be minimized and
content-sanitized for stable tests.

### 24.2 Unit tests

- status and task-state mapping;
- deterministic projection IDs;
- queue v1 normalization and round-trip;
- materialized goal reader parity;
- inventory hashing;
- idempotency-key generation;
- feature-mode precedence;
- explicit-policy preservation;
- KB alias selection and freshness comparison;
- rollback plan generation; and
- unknown schema fail-closed behavior.

### 24.3 Integration tests

- bootstrap from Git into an empty runtime store;
- delete/rebuild store and compare digests;
- replay source checkpoints in order;
- dual-read v1/v2 KB results;
- direct-record fallback after a new ledger commit;
- router shadow versus actual resolution;
- frontier bootstrap from next action, queue, focus, and hypotheses;
- queue v1 dispatch from a v2 frontier selection;
- snapshot/review/ledger sequence under active canary mode;
- force rollback and continue through legacy tooling; and
- re-enter shadow/assist after rollback.

### 24.4 Crash matrix

Inject a crash:

- before lease acquisition;
- after lease acquisition;
- after inventory but before bootstrap;
- after runtime projection write;
- before dispatch;
- after dispatch request but before response;
- after worker completion before snapshot;
- after snapshot commit before runtime checkpoint;
- after reviews before ledger archive;
- after ledger commit before runtime update;
- during KB alias switch; and
- during rollback.

Every restart must produce either the same next transition or an explicit
reconciliation state, never a duplicate side effect.

### 24.5 Adversarial tests

- malicious instructions inside retrieved papers or internal notes;
- forged model name in provider response;
- overstated binding capability;
- stale Qdrant result contradicting a newer direct ledger record;
- superseded record ranked above current evidence;
- two processes racing to cut over the same goal;
- manually altered campaign SQLite state;
- replay from an unreachable Git commit;
- task result claiming campaign completion; and
- shadow proposal attempting to mint authoritative memory.

## 25. Metrics and migration dashboard

Track by goal and component:

### Compatibility

- percentage of legacy goals inventoried successfully;
- percentage of queue v1/handoffs normalized without loss;
- replay digest parity;
- number of blocked/ambiguous records;
- rebuild parity of the derived store.

### Knowledge

- v1/v2 top-k overlap;
- exact-identifier recall;
- contradiction retrieval rate;
- filter correctness;
- citation/source attribution;
- stale-index fallback rate;
- evidence-bundle token count and coverage.

### Routing

- shadow disagreement rate;
- hard-gate violation count;
- static-versus-routed cost;
- escalation rate;
- verifier pass/fail by task class;
- silent downgrade count, which must remain zero.

### Loop continuity

- nonterminal checkpoints with at least one valid successor;
- frontier refill success and make-work rejection rate;
- duplicate dispatch/archive count;
- process restarts recovered;
- lease-contention events;
- manual interventions per batch.

### Scientific integrity

- unsupported state transitions, which must remain zero;
- evidence bundles missing required contradictory evidence;
- negative results later retrieved and used;
- review bypass attempts;
- claims whose scope changed during migration without a normal correction
  record, which must remain zero.

## 26. Cutover acceptance gates

A goal may enter active mode only when:

- the inventory is current and hash-bound to the source commit;
- repository validation and merge-hygiene checks pass;
- no ambiguous running task or archive obligation exists;
- legacy records normalize without lossy coercion;
- runtime projection rebuild matches its recorded digest;
- KB generation/freshness gates pass or direct fallback fully covers required
  exact records;
- router shadow reports zero hard-gate violations;
- the task classes enabled for active routing meet verifier-quality gates;
- frontier bootstrap produces bounded, lineage-complete nodes;
- controller lease and crash-recovery tests pass;
- legacy rollback has been exercised for the goal class;
- the goal has a standing reviewable PR/branch; and
- a Coordinator commits the mode/configuration change.

A goal stays in assist or legacy when any gate fails. Migration pressure is not
a reason to reinterpret missing evidence or waive review.

## 27. Integration with the implementation PR sequence

Migration work is woven into the existing sequence rather than postponed until
all v2 components exist.

| Existing implementation PR | Required migration deliverable |
|---|---|
| 1 — contracts | campaign-config, inventory, migration-report, projection schemas; golden legacy fixtures |
| 2 — KB evidence bundles | versioned collection builder, dual-query comparison, freshness/read-your-writes migration |
| 3 — router shadow | legacy-policy preservation, route comparison report, static kill switch |
| 4 — escalation | task-class activation gates and fallback-to-static tests |
| 5 — frontier | deterministic bounded bootstrap from legacy state, deduplication, shadow comparison |
| 6 — controller | compatibility reader, runtime-store migrations, lease, reconciliation, cutover/rollback commands |
| 7 — memory/reflection | shadow admission for existing knowledge, no historical rewrite, KB refresh semantics |
| 8 — canary | active per-goal cutover, rollback drill, dashboard, operational runbook |
| 9 — learned router | observational-data labeling, training-data lineage, shadow-only initial deployment |

No implementation PR is migration-complete unless it can be disabled without
invalidating records written by earlier phases.

## 28. Recommended first migration slice

Build the following before any active controller work:

1. `campaign-config`, `migration-inventory`, `migration-report`, and projection
   schemas;
2. a materialized legacy goal reader that reuses existing validation semantics;
3. queue v1, handoff, and receipt compatibility adapters;
4. deterministic `inventory`, `bootstrap --mode observe`, `replay`, and
   `verify` commands;
5. an empty-store rebuild parity test;
6. versioned KB collection generation and dual-query shadow evaluation; and
7. static/shadow router mode with explicit-policy preservation.

This slice creates measurable migration safety without granting scheduling
or state-transition authority. It should be merged before frontier or controller
activation so every later phase has a tested route back to current behavior.

## 29. Definition of migrated

Research Loop v2 is considered migrated for a particular goal when:

- the goal's legacy history remains readable and authoritative;
- inventory, bootstrap, replay, and rebuild are deterministic;
- all imported objects carry source commit/path/hash lineage;
- v2 can recover from process loss without duplicate work;
- KB retrieval is current or explicitly falls back to direct records;
- actual model routes satisfy unchanged policy floors;
- the frontier advances the goal without reintroducing terminal or superseded
  work;
- official transitions still pass existing archive and independent-review
  gates;
- a rollback returns the goal to legacy operation from the latest committed
  checkpoint; and
- the migration and rollback records are present in the standing goal PR.

Repository-wide migration is achieved only after each supported goal class has
passed these gates. It is not achieved merely because new goals default to v2.
