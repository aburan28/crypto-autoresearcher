# Change log — TASK-20260810-55845c (RECON-20260810-002)

Applies successor acts `SUCC-ECDLP-HEAD`, `SUCC-HAWK-HEAD` and `SUCC-ECTD-HEAD` of
`coordination/reconciliation/RECON-20260810-001/tasks/TASK-20260810-1b82fe/disposition.yaml`.

**Net effect: all three heads CORRECTED. `current_batch_id`, `next_action` and
`dispatch_queue_path` moved together in every case; no head-internal mismatch is
created or left standing. Nothing is recorded UNRESOLVED as a head value; three
narrower items are carried forward as unresolved and are listed at the end.**

This is a coordination act. It opens no batch, moves no hypothesis status, files
no evidence, promotes no knowledge entry, approves no experiment, authorizes no
run, and closes no goal. No claim tier moves. No committed decision, checkpoint,
evidence record, run record or archive receipt was edited; every correction is by
supersession, with the superseded text preserved verbatim in the same record.

Read first, as directed:
`coordination/reconciliation/RECON-20260810-002/tasks/TASK-20260810-08130e/change_log.md`.
Its finding — that all three premises it tested were textual co-occurrence
artifacts — governed this task's method. **Every batch-to-decision link asserted
below was established by opening the decision and confirming it is about this goal
and this batch.** Where a premise handed to this task failed, the failure is
recorded rather than routed around.

---

## 0. Method, and what it deliberately does not use

- **No shell.** No git command, parser, validator, allocator or dispatcher was run.
  No commit sha, parent sha, path sha256, timestamp beyond date precision, run id,
  receipt or verdict was created. No commit was made.
- **No ordering evidence.** Commit order, topological position, filenames and
  self-declared `created_at` / `opened_at` / `recorded_at` dates were **not** used
  to rank any batch. Every ranking below rests on an explicit statement inside a
  committed record: a `parent_batch` declaration, a checkpoint's `status` /
  `decision_id`, a decision's `batch_id` and `next_actions`, or a supersession note
  the goal record already carries.
- **The disposition's own ordering premises were therefore not testable as stated**
  (they are topological) and are neither upgraded nor relied on. Where a
  disposition conclusion survives, it survives on a different, content-based basis
  stated here.

---

## 1. GOAL-ECDLP-001 — `ledger/goals/GOAL-ECDLP-001/goal.yaml` (sharded)

### Premises tested

| # | premise (from the task card / disposition) | result |
|---|---|---|
| P1 | `BATCH-c3c474` is closed by its own checkpoint (`DEC-20260809-d5ff80`) | **HOLDS.** `checkpoints/BATCH-c3c474.yaml` carries `decision_id: DEC-20260809-d5ff80`, `evidence_id: EV-ECDLP-f32446`, verdict REVISE on EXP-ECDLP-ffa5c3, and a `next_action` directing a fresh successor batch. `ledger/decisions/DEC-20260809-d5ff80.yaml` has `batch_id: BATCH-c3c474` and reads "close only BATCH-c3c474 after its ledger archive" — about this goal and this batch. |
| P2 | `BATCH-fc86ca` is itself closed by its own checkpoint | **HOLDS.** `checkpoints/BATCH-fc86ca.yaml`, `decision_id: DEC-20260809-92e370`; `ledger/decisions/DEC-20260809-92e370.yaml` carries `batch_id: BATCH-fc86ca`. |
| P3 | "eleven topologically newer checkpoints exist" / fc86ca is the newest | **NOT USED — untestable without commit ordering, which is forbidden here.** Neither confirmed nor denied. Nothing below depends on it. |
| P4 | therefore "the live head is a batch the audit did NOT identify" | **CONFIRMED, on a different basis.** The batch is `BATCH-ea56c5`. |
| P5 | the head may be a deliberate refusal rather than drift (warning iii) | **PARTLY HOLDS, AND IS SCOPED.** See "the deliberate hold" below. |

### The deliberate hold, examined before replacing anything

`goal.yaml` carries `merge_reconciliation_20260809_batchc3c474_cursor`, which
**deliberately retained** `BATCH-c3c474`:

> "This merge retains BATCH-c3c474, the newer source-lineage cursor **opened after**
> BATCH-f5d854's reviewed apparatus-design disposition. The merged mainline's
> BATCH-25dd46 cursor and its separately archived ICC2 serializer-only BATCH-fc86ca
> design remain in the merge parent as parallel immutable history."

This is a real deliberate hold and it is **not** overwritten. It is scoped: it is a
preference for `BATCH-c3c474` **as against** `BATCH-25dd46` / `BATCH-fc86ca`, it
describes `BATCH-c3c474` as an *open* cursor, and it does not mention the
`BATCH-ece945` / `BATCH-ea56c5` lane at all. `BATCH-c3c474` has since been closed by
its own checkpoint. A note retaining a batch as the open cursor is not a standing
refusal to advance past that batch's own subsequent closure. The note is preserved
verbatim and a superseding note is recorded alongside it, naming exactly what it
does and does not hold.

### How the live head was determined, from contents only

Every `coordination/goals/GOAL-ECDLP-001/batches/*/batch.yaml` in the
lineage-bearing set declares `parent_batch`. Following those declarations only:

```
... -> BATCH-3033bc -> BATCH-bca81e -> BATCH-56187a -> BATCH-af78b4
     |-> BATCH-14a462                                        (invalid opening)
     |-> BATCH-b0eac5 -> BATCH-dace3f -|-> BATCH-25dd46 -> BATCH-f5d854 -> BATCH-c3c474   [CLOSED]
     |                                 |-> BATCH-1ad844 -> BATCH-9fac23 -> BATCH-fc86ca   [CLOSED]
     |-> BATCH-79b44f -> BATCH-2e3767 -> BATCH-ba7d86 -> BATCH-e3a312 -> BATCH-eec496
             -> BATCH-3468a0 -> BATCH-ece945 -> BATCH-ea56c5                              [OPEN]
```

- **Two of the three lanes descending from `BATCH-af78b4` are closed** by committed
  checkpoints carrying decision ids, and **no `batch.yaml` in this goal declares
  `parent_batch: BATCH-c3c474` or `parent_batch: BATCH-fc86ca`** — so neither closed
  lane has a declared successor. Each closing checkpoint's restart condition is
  therefore **unexecuted**, and that fact is carried into the new `next_action`
  rather than dropped.
- **`BATCH-ea56c5` is the only lineage leaf with no checkpoint**, i.e. no committed
  record closes it. It carries a committed `dispatch_queue.json`, `focus_queue.json`,
  a task card, producer outputs under `tasks/TASK-20260809-ce341d/`, and two snapshot
  archives — a live batch, not an unused directory a concurrent session left behind.
- **Its citation is substantive, checked in both directions.**
  `batches/BATCH-ea56c5/batch.yaml` declares `goal_id: GOAL-ECDLP-001`,
  `parent_batch: BATCH-ece945`, `parent_decision: DEC-20260809-6bd04d`,
  `parent_evidence: EV-ECDLP-defc0b`. `ledger/decisions/DEC-20260809-6bd04d.yaml`
  was opened and read in full: `goal_id: GOAL-ECDLP-001`, `batch_id: BATCH-ece945`,
  `decision: revise_and_pause_pre_implementation`, first next action *"Open one fresh
  bounded static successor and first require the exact three-mount verification-count
  identity plus canonical-decoder reachability ... as cheap falsifiers"*. That is
  verbatim what `BATCH-ea56c5`'s objective says it does, against the eight blockers
  `checkpoints/BATCH-ece945.yaml` enumerates. Not a co-occurrence.
- **The other uncheckpointed leaves are excluded by the goal record's own committed
  notes, not by dates.** `BATCH-14a462` — recorded an *invalid* opening by
  `current_batch_id_note_at_batchb0eac5_open_20260809`. `BATCH-bd36fe` — recorded
  *stale* by `current_batch_id_note_at_batch3033bc_open_20260808`. `BATCH-7288c4` and
  `BATCH-d8bb19` — both declare `parent_batch: BATCH-fd61e4`, which
  `historical_batch_id_note_at_batch284817_close_20260808_from_PR243` records as
  *superseded and subsumed*.

### Fields

| field | old value (committed) | new value | committed record that settled it |
|---|---|---|---|
| `current_batch_id` | `BATCH-c3c474` | **`BATCH-ea56c5`** | `batches/BATCH-ea56c5/batch.yaml` (opening record, goal + parent + parent_decision); `ledger/decisions/DEC-20260809-6bd04d.yaml`; `checkpoints/BATCH-ece945.yaml` (parent closed, "Open a fresh static successor"); absence of any `checkpoints/BATCH-ea56c5.yaml`; `checkpoints/BATCH-c3c474.yaml` (head closed) |
| `dispatch_queue_path` | `.../batches/BATCH-dace3f/dispatch_queue.json` | **`.../batches/BATCH-ea56c5/dispatch_queue.json`** | same; the file is committed inside the live batch's own directory. Repairs the head-internal mismatch the audit reported (queue named `BATCH-dace3f`, head named `BATCH-c3c474`). |
| `next_action` | "Complete and verify the isolated BATCH-c3c474 opening snapshot, then freeze EXP-ECDLP-ffa5c3 ..." (preserved verbatim at `prior_next_action_batch_c3c474_20260810`) | **carry the committed BATCH-ea56c5 queue to its ledger disposition**, with the standing holds restated | `checkpoints/BATCH-c3c474.yaml` — EXP-ECDLP-ffa5c3 is already frozen, hash-bound, independently reviewed (TASK-20260809-923ede, REVISE) and the batch closed, so the directive cannot be executed as written |
| `updated_at` | `'2026-07-29'` | **`'2026-08-10'`** | the date of this correction itself; explicitly **not** an inference about any commit. The disposition's question (the date of goal.yaml's last commit) is untouched and stays unanswered. |

Exactly one `next_action` remains. The standing holds are carried forward
unweakened: **no implementation, execution, run, ECDLP claim, status transition or
goal completion is authorized**; `DEC-20260809-6bd04d` records
`implementation_granted: false`, `execution_granted: false`,
`budget_increase_granted: false`, and admits nothing before dual independent PASS.
The two closed sibling lanes and their unexecuted restart conditions are named in
the new `next_action` so they are not silently lost, and reviving either is stated
to be a separate Coordinator decision that this act does not make.

### Not done, and why

- **The ~140 batch directories were not audited**, per the task card. Directories
  with no `batch.yaml` and no `parent_batch` declaration are outside the lineage set
  and are neither claimed nor denied to be live. Recorded as residual uncertainty in
  the goal record itself.
- **`coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-IV-20260808/dispatch_queue.json`**,
  which `SUCC-ECDLP-HEAD` also names, was **not** audited. Out of this task's scope
  and carried forward.
- `latest_verified_commit` is **not** advanced: this act made no commit.

---

## 2. GOAL-HAWK-001 — `ledger/goals/GOAL-HAWK-001.yaml`

### Premises tested

| # | premise | result |
|---|---|---|
| P1 | `BATCH-002` has no directory, but its inline checkpoint records `closed_at 2026-08-02`, so the batch is real and closed | **HOLDS.** `batch_checkpoints` entry: `status: closed`, `closed_at: '2026-08-02'`. The missing directory is a dispatcher-convention gap and is not treated as evidence the batch is fictitious. |
| P2 | `BATCH-56498f` and `BATCH-d44912` are both open, neither checkpointed | **HOLDS.** `batch_checkpoints` lists only `BATCH-001` and `BATCH-002`. |
| P3 | four decisions cite the two batches | **HOLDS AND IS SUBSTANTIVE.** All four opened and read: `DEC-20260805-bdcb53` (`goal_id: GOAL-HAWK-001`, `batch_id: BATCH-56498f`), `DEC-20260805-77a735`, `DEC-20260805-ed4cd3`, `DEC-20260805-a62164` (all three `batch_id: BATCH-d44912`). These are goal-and-batch decisions with `batch_id` fields, not passing mentions. |
| P4 | `next_action` "directs opening BATCH-003, which does not exist" | **FALSE.** See below. |
| P5 | a deliberate hold keeps the head at `BATCH-002` | **FALSE.** No note in the record holds it; the value is simply stale. |

### P4, read in full before superseding anything

The committed `next_action` was read whole. **It contains no directive to open any
batch.** Its only occurrence of `BATCH-003` is:

> "A conforming BATCH-003 dispatch queue - receipts inside their own archive
> commits - is owed before any batch that dispatches workers."

That is a standing **obligation**, not an "open BATCH-003" directive — the same
class of error the sibling task found in GOAL-ICEX-001, caught here by the same
full read. The obligation is genuinely **undischarged**: neither `BATCH-56498f` nor
`BATCH-d44912` has a `dispatch_queue.json` at all. It is carried forward, restated
against the live batch, and explicitly **not** cancelled. Only the identifier
`BATCH-003` — never minted — is corrected.

### Choosing between two simultaneously open batches

The audit could not rank them and correctly refused to. **The decisions rank them,
and by content, not by date.** `DEC-20260805-bdcb53` disposes `BATCH-56498f`
(`advance_with_repair_required`) and states its successor's work as one next action:

> "Open BATCH-003: (1) Repair the two proof gaps identified by the red team
> (Claims 2.1 and 2.2 — two-sentence edits); (2) Confirm Case C is the correct
> complexity classification ...; (3) Promote the repaired derivation as KN-FIND ..."

All three limbs are discharged under `BATCH-d44912` by that batch's own committed
decisions: `DEC-20260805-77a735` (`promote_kn_find` — "Both proof gaps repaired
(Claims 2.1/2.2). KN-FIND-528ca0 promoted", context "Coordinator repair task
TASK-20260805-a39814") = limbs (1) and (3); `DEC-20260805-ed4cd3`
(`case_c_confirmed_from_paper_body`, `amends: DEC-20260805-77a735`) = limb (2).
So `BATCH-d44912` **is** the successor `BATCH-56498f`'s own disposing decision
called for. Independently, the goal's own `next_action` already cited
`DEC-20260805-a62164 / EV-HAWK-21edba` — a `BATCH-d44912` decision — so the head now
agrees with the next action the record already carried. This is a coordination
judgement, and it is stated with its reasoning rather than guessed.

### Fields

| field | old value (committed) | new value | committed record that settled it |
|---|---|---|---|
| `current_batch_id` | `BATCH-002` | **`BATCH-d44912`** | own `batch_checkpoints` BATCH-002 entry (`status: closed`, `closed_at 2026-08-02`); `DEC-20260805-bdcb53` (BATCH-56498f, names the successor's three-limb work); `DEC-20260805-77a735` + `DEC-20260805-ed4cd3` + `DEC-20260805-a62164` (all `batch_id: BATCH-d44912`, discharging exactly those limbs) |
| `dispatch_queue_path` | `.../batches/BATCH-001/dispatch_queue.json` | **`null`** | neither candidate batch directory contains a `dispatch_queue.json`; `null` is a legal committed value here; the BATCH-001 queue belongs to a closed batch and, per this record's own `known_defect`, does not render. Moved with the head so no new head-internal mismatch is created. |
| `next_action` | "KN-OPEN-028 ALL QUESTIONS CLOSED ..." through "... closure quorum." (preserved verbatim at `prior_next_action_head_reconciliation_20260810`) | **quiescence restated with all five standing holds and the corrected queue obligation** | the committed text itself, read in full |
| `updated_at` | `'2026-08-02'` | **`'2026-08-10'`** | date of this correction only |

Standing holds carried forward unweakened: (1) **DO NOT run `/propose-ideas`** —
RQ-HAWK-001 forbids experiment design until the primary sources are filed;
(2) the **contact-author request for iacr:2026/1318 requires explicit user
authorization** (`CORR-20260802-bc9e33` OI-1), is outward-facing and must not be
sent otherwise, and circumventing the Cloudflare challenge remains forbidden
outright; (3) the conforming-queue obligation, undischarged; (4) claim tier stays
**toy**; (5) nothing is admissible toward the AGENTS.md rule 13 closure quorum and
no completion criterion is met.

### Not claimed

`BATCH-d44912` is **not** recorded closed — no committed checkpoint or decision
closes it, and none is invented; `batch_checkpoints` was not extended. Its
successor, called "BATCH-004" by `DEC-20260805-77a735`, was never opened and is
gated on a user authorization no committed record grants. One tension is recorded
and deliberately **not** adjudicated: the superseded `next_action` lists "which case
(B/C/A) applies" as remaining uncertainty, while `DEC-20260805-ed4cd3` records the
body text as provided and Case C confirmed. Resolving that is a research-state
judgement, not bookkeeping; it is passed forward, in the record.

---

## 3. GOAL-ECTD-001 — `ledger/goals/GOAL-ECTD-001.yaml`

### Premises tested

| # | premise | result |
|---|---|---|
| P1 | read `BATCH-e722dd`'s inline checkpoint for `closed_at` and `decision_id` | **HALF FAILED.** `decision_id: DEC-20260806-160175` and `evidence_id: EV-ECTD-14f9a2` are present. **No ECTD inline checkpoint carries a `closed_at` field at all** — not BATCH-001, BATCH-002, BATCH-fca4e2 or BATCH-e722dd. This is why the audit "quoted none". No `closed_at` was read, and none is inferred, invented or reconstructed. The ruling does not depend on one. |
| P2 | the audit's basis was a directory cited by no decision, with an all-queued queue (graded WEAK) | **HOLDS as a description of the audit, and the audit's basis is indeed too weak to act on.** This act does **not** rest on it. |
| P3 | "was `BATCH-33b207` ever dispatched?" | **ANSWERED: it was OPENED, by a committed Coordinator opening record; and NOTHING IN IT HAS RUN.** |
| P4 | a deliberate hold keeps the head at `BATCH-e722dd` | **FALSE.** No note in the record holds it. |

### The record the audit did not read

`coordination/goals/GOAL-ECTD-001/batches/BATCH-33b207/batch.yaml` is a committed
batch-opening record. It declares `goal_id: GOAL-ECTD-001`, `opened_by: coordinator`,
`opened_at: '2026-08-06'`, `approval_basis.standing_decision: DEC-20260806-160175`
with that decision's commit, `hypothesis_id: H-ECTD-19017a`,
`experiment_id: EXP-ECTD-9e4248`, its own `dispatch_queue_path`, a four-task
executor / snapshot / validator / ledger card set, a toy `claim_ceiling` and a
`standing_prohibition`. Its `sequence_note` reads:

> "Fifth dispatched batch for GOAL-ECTD-001 (BATCH-001, BATCH-002, BATCH-fca4e2,
> BATCH-e722dd precede it)"

and its objective — execute approved EXP-ECTD-9e4248 v2, implementation smoke then
the ≥8-edge vertical-conductor screen — is **exactly the batch this goal's own
`next_action` directed be opened**. The committed `dispatch_queue.json` carries
`"goal_id": "GOAL-ECTD-001"` and four fully specified task cards, one of whose
handoffs instructs the ledger archivist to "checkpoint GOAL-ECTD-001
(batch_checkpoints entry, current_batch_id ...)".

**Why the audit missed it: its matching ran decision → batch only.** The citation
here runs batch → decision. "No committed decision names BATCH-33b207" is true and
is not the right question. This is the mirror image of the co-occurrence failure the
sibling task found: there, two strings in one file were mistaken for a reference;
here, a real reference was missed because it points the other way.

### Fields

| field | old value (committed) | new value | committed record that settled it |
|---|---|---|---|
| `current_batch_id` | `BATCH-e722dd` | **`BATCH-33b207`** | `batches/BATCH-33b207/batch.yaml` (opening record: goal, opener, approval basis `DEC-20260806-160175` + its commit, hypothesis, experiment, queue path, four cards, predecessors enumerated); own `batch_checkpoints` BATCH-e722dd entry (`decision_id: DEC-20260806-160175`, "Design stage only, no runs ... EXP-ECTD-9e4248 v2 approved") |
| `dispatch_queue_path` | `.../batches/BATCH-e722dd/dispatch_queue.json` | **`.../batches/BATCH-33b207/dispatch_queue.json`** | the same `batch.yaml` declares that exact path; the file is committed and its schema block names `GOAL-ECTD-001` |
| `next_action` | "Open a batch that runs /run-experiment on the now-approved EXP-ECTD-9e4248 v2 ..." (preserved verbatim at `prior_next_action_head_reconciliation_20260810`) | **carry the already-open, stalled BATCH-33b207 to its ledger disposition**, with every constraint and prohibition carried forward | the operative directive is discharged by BATCH-33b207's committed opening |
| `updated_at` | `'2026-08-06'` | **`'2026-08-10'`** | date of this correction only |

Carried forward verbatim in substance: the `n_bit_range_sampling_requirement` (do
**not** reuse EXP-ECTD-001's `driver/fp.py` `random_prime` unmodified —
`DEC-20260806-4a9604` F-3 / `DEC-20260806-160175` D3); mandatory
`CTRL-END-RING-CERTIFICATE` and `CTRL-HORIZONTAL-BASELINE` certification; prefer the
Hilbert-class-polynomial route (D4); five decision-table branches computed from raw
data; **claim tier toy**, no trapdoor / Galbraith path-finding hardness /
isogeny-evaluation hardness / crypto-scale language; do not read BATCH-fca4e2's
`scoped_homogeneity` as evidence beyond exactly 40-bit N on the 5 tested classes;
do not read the approval as a claim about continuity or discontinuity — **no run has
occurred**.

One arithmetic change is disclosed rather than buried: the superseded text reads
"Four of eight campaign batches remain after BATCH-e722dd"; the successor reads
three after BATCH-33b207. That follows from BATCH-33b207 being the fifth dispatched
batch per its own `sequence_note` and `campaign_budget.maximum_batches: 8`. **No
budget is raised, lowered or waived.**

### What is explicitly not claimed

`BATCH-33b207` **has produced nothing.** All four queue entries stand at `queued`;
its directory holds only `batch.yaml` and `dispatch_queue.json`; no run, review,
receipt or artifact exists; no committed decision disposes it. It is an **opened and
stalled** batch, and naming it as the head asserts only that it is the batch this
goal has open. Consequence stated plainly in the record: this goal will now render a
plan whose first entry is an Executor run card. **Rendering is not dispatch and the
field is not an authorization** — the approval that would govern a run is the
pre-existing `DEC-20260806-160175`, and the Validator and archive gates written into
that queue bind unchanged. `latest_verified_commit` is not advanced.

Deferring again was an acceptable outcome and was considered. It was declined
because the ground for deferral — that the only basis was a bare directory — no
longer holds once `batch.yaml` is read, and leaving a discharged "open a batch"
directive standing would keep directing the opening of a batch that is already open.

---

## 4. Unresolved, carried forward

| id | value | status | what would settle it |
|---|---|---|---|
| `ECDLP-NONLINEAGE-DIRS` | whether any GOAL-ECDLP-001 batch directory **without** a `batch.yaml` / `parent_batch` declaration is live | UNRESOLVED | per-directory read of the ~140 batch directories against the goal's committed decisions; explicitly out of scope here ("the head is the job"), and no claim either way is made |
| `ECDLP-PROPOSALS-QUEUE` | `coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-IV-20260808/dispatch_queue.json`, named by `SUCC-ECDLP-HEAD` and never reached by `TASK-20260810-c64cf0` | UNRESOLVED | a queue-state read of that file; not attempted here |
| `HAWK-CASE-BCA` | whether `DEC-20260805-ed4cd3`'s paper-body confirmation already answers the "which case (B/C/A)" uncertainty the `next_action` still lists | UNRESOLVED | a research-state judgement by this goal's driver, recorded in a decision — not a bookkeeping act |
| `HAWK-D44912-CLOSURE` | whether `BATCH-d44912` is closed | UNRESOLVED | a committed checkpoint or decision closing it; none exists and none was invented |
| `LIVE-HEADS` (disposition) | correct `current_batch_id` for GOAL-AES-003, GOAL-DREG-001, GOAL-MLDSA-001, GOAL-P13-001 | UNRESOLVED, untouched | their own successor acts; those goals belong to a concurrently running task and were not read or written here |

Also unchanged: the disposition's `ANOMALY-3`, `SIBLING-SPLIT`,
`SIBLING-ENTRY-COUNT` and `C60B84-IDENTITY` entries. Nothing in this act bears on
them.

---

## Provenance

- `records_read_in_full`: `ledger/handoffs/TASK-20260810-55845c.yaml`;
  `coordination/reconciliation/RECON-20260810-002/tasks/TASK-20260810-08130e/change_log.md`;
  `coordination/reconciliation/RECON-20260810-001/tasks/TASK-20260810-1b82fe/disposition.yaml`;
  `ledger/goals/GOAL-ECDLP-001/goal.yaml` (head-field, next_action, updated_at and
  supersession-note regions); `ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-c3c474.yaml`,
  `.../BATCH-fc86ca.yaml`, `.../BATCH-ece945.yaml`;
  `ledger/decisions/DEC-20260809-6bd04d.yaml`, `DEC-20260809-cb25a0.yaml` (read and
  **excluded** — it is a GOAL-MCE-001 decision, not ECDLP);
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-ea56c5/batch.yaml`,
  `.../BATCH-c3c474/batch.yaml`, `.../BATCH-7288c4/batch.yaml`, `.../BATCH-d8bb19/batch.yaml`;
  `ledger/goals/GOAL-HAWK-001.yaml`; `ledger/decisions/DEC-20260805-bdcb53.yaml`,
  `DEC-20260805-77a735.yaml`, `DEC-20260805-ed4cd3.yaml`;
  `ledger/goals/GOAL-ECTD-001.yaml`;
  `coordination/goals/GOAL-ECTD-001/batches/BATCH-33b207/batch.yaml` and
  `.../dispatch_queue.json`.
- `shell_access`: **false**. No git command, no parser, no validator, no allocator,
  no dispatcher, no commit, no push, no PR. No commit sha, parent sha, path sha256,
  batch id, task id, decision id or wall-clock time was minted, reconstructed,
  estimated or inferred from a filename or a date.
- `ordering_evidence_used`: **none**. Commit order, topological position and
  self-declared record dates were not used to rank any batch.
- `fabrication_guard`: every value written into a goal record was read out of a
  named committed record, except the three `updated_at` values, which are the date
  of this correction itself and are labelled as such in each record.
- `writes_performed`: this file;
  `ledger/goals/GOAL-ECDLP-001/goal.yaml`; `ledger/goals/GOAL-HAWK-001.yaml`;
  `ledger/goals/GOAL-ECTD-001.yaml`. Nothing outside `write_scope` was written. No
  other goal record was opened for writing. **No commit was made.**
- `immutability`: no committed decision, checkpoint, evidence record, run record,
  dispatch queue or archive receipt was edited. Every superseded value and text is
  preserved verbatim in a `prior_*` key alongside a supersession note naming what
  overtook it.
- `inference`: `requested_policy: coordinator-orchestration-code`;
  `model_that_answered: claude-opus-5`; `runtime: claude_code` (coordinator subagent,
  `effort: high`, the effort that policy requests per CLAUDE.md's derived table);
  `fallback_used: false`; `degraded: false`; `independent_session: false`. Per-role
  model selection is process-level under this runtime; no substitution was requested
  and none was made.
