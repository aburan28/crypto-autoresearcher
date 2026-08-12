# TASK-20260810-2b1c3b — goal-head change log

Campaign `RECON-20260810-002`. Successor acts `SUCC-AES003-HEAD`,
`SUCC-P13-HEAD`, `SUCC-DREG-HEAD` from
`coordination/reconciliation/RECON-20260810-001/tasks/TASK-20260810-1b82fe/disposition.yaml`.

**Act type: coordination.** Opens no batch, closes no batch, moves no hypothesis
status, files no evidence record, promotes no knowledge entry, approves no
experiment, closes no goal. No claim tier moves.

**Method, and its hard limit.** No shell. Every value below was read out of a
committed record's *contents*. Nothing rests on commit ordering, filenames,
directory listings alone, or dates — bulk commit `65ce43f0` and (for
GOAL-AES-003) three separate merges of `origin/main` destroyed that ordering,
and the RECON-20260810-001 audit graded every verdict depending on it MODERATE
or WEAK. No such verdict is upgraded here.

**Inference.** requested_policy `coordinator-orchestration-code`;
model that answered `claude-opus-5` (claude_code coordinator subagent, effort
`high`); `fallback_used: false`; `degraded: false`.

---

## 0. Premises tested before use (per the mid-run correction from TASK-20260810-08130e)

The correction reported that RECON-20260810-001's "cited by a committed
decision" claims are sometimes textual co-occurrence artifacts. Every premise
this task was handed or would have relied on was therefore opened and read in
full. Results:

| Premise | Verdict | What reading it actually showed |
|---|---|---|
| `DEC-20260805-b42d5c` cites GOAL-AES-003 `BATCH-015` (given in the dispatch prompt) | **SUBSTANTIVE BUT MISLEADING AS A HEAD ARGUMENT** | It *is* a GOAL-AES-003 decision (`target_ids: [RQ-AES-003, GOAL-AES-003, EV-AES-dec938]`, context "GOAL-AES-003 BATCH-014 close"). But it names BATCH-015 only in `next_actions`, as the batch to **open** — a forward reference authored by the batch it closes. It establishes BATCH-015 as the *directed next* batch, not as a live or closed one, and on its own it does **not** make BATCH-014 stale. |
| `DEC-20260725-026` cites GOAL-DREG-001 `BATCH-004`/`BATCH-005` | **SUBSTANTIVE, LOAD-BEARING** | `context: "GOAL-DREG-001 BATCH-004: repaired CTRL-B protocol…"`, `target_ids` include GOAL-DREG-001 / H-DREG-001 / RQ-DREG-001, and `next_actions` reads "Open GOAL-DREG-001 BATCH-005 executor task to run admitted chunked CTRL-B…". Goal and batch match; the reference is an act, not a mention. |
| `DEC-20260804-e19a65` cites GOAL-P13-001 `BATCH-403f13` | **SUBSTANTIVE** | Structured fields `goal_id: GOAL-P13-001`, `batch_id: BATCH-403f13`. Used here **only** as ordering evidence; its seven recorded defects (BATCH-8e1671 `defects_found` D-1..D-6) mean it is not adopted as an official disposition. |
| `DEC-20260731-014` is GOAL-DREG-001 BATCH-005's decision (declared by BATCH-005's own ledger receipt) | **FALSE — IDENTIFIER COLLISION** | The committed `ledger/decisions/DEC-20260731-014.yaml` is `goal_id: GOAL-ECDLP-001`, `batch_id: BATCH-021`, a theater-repair approval for another campaign. GOAL-DREG-001 has BATCH-005 *evidence* and no BATCH-005 *decision*. This was found only by opening the file. |
| GOAL-P13-001's `next_action` directs opening `BATCH-004` | **TRUE, read in full (62 lines), and unexecutable** | The full text was read before superseding. No `BATCH-004` directory exists under this goal; the four ordered items it names were executed under `BATCH-403f13`, whose own design report self-labels `batch_number: 4`. |
| GOAL-DREG-001's `next_action` is conditioned on an external driver process | **TRUE, read in full** | "external driver since 14:39; takeover if stalled >30 min" — no committed artifact can confirm or refute a process state. |

Two further premises of the audit were *not* used because reading showed they
prove less than the audit's phrasing implies: BATCH-713991's `closed_at`
being later than BATCH-014's (this record's own note declares BATCH-713991 not
durable), and "the newest-added directory" for any goal (a directory listing
is not a head).

---

## 1. GOAL-AES-003 — **UNRESOLVED**. No field changed.

`ledger/goals/GOAL-AES-003.yaml`

| Field | Old value | New value |
|---|---|---|
| `current_batch_id` | `BATCH-014` | **unchanged** (UNRESOLVED) |
| `dispatch_queue_path` | `coordination/goals/GOAL-AES-003/batches/BATCH-009/dispatch_queue.json` | **unchanged** (UNRESOLVED) |
| `next_action` | `OPEN GOAL-AES-003 BATCH-015 WITH THE O(1)-MEMORY IDEAL-PERMUTATION CONSTRUCTION…` | **unchanged** (UNRESOLVED) |

The only edit is an added flag block, `head_reconciliation_20260810`. The three
fields move together or not at all; the head could not be established, so none
moved — including the already-committed head-internal mismatch between
`current_batch_id: BATCH-014` and a `BATCH-009` queue path, which is left in
place and flagged rather than half-fixed.

### What the contents do establish

- **BATCH-015 is open and unstarted.** Directory holds `dispatch_queue.json`
  and nothing else — no `tasks/`, no `archives/` — and all four cards are
  `"state": "queued"`.
- **BATCH-6fe3c2 is also open and unstarted,** same shape, on the other
  lineage. Its queue objective is "execute `DEC-20260804-73977c` D-7's adopted
  dual-device repair" and it reads
  `BATCH-b41ba9/tasks/TASK-20260806-7a980b/repair-assessment.md` for its event
  numbering — so by its own contents it is downstream of BATCH-b41ba9. **No
  committed decision names BATCH-6fe3c2 at all.**
- **BATCH-b41ba9 is closed and reviewed,** and is the most recent closed batch
  on either lineage. Its ledger receipt records a validator PASS
  (TASK-20260806-7943b5), and the committed `DEC-20260804-73977c` carries its
  extensions D-6, D-7, D-8.
- **BATCH-b41ba9 is downstream of the BATCH-014 head state**, with no commit
  ordering used: the goal record's own `next_action` THIRD-MERGE ADDENDUM says
  item (a) of the SECOND-MERGE ADDENDUM — written while the head was BATCH-014
  — "IS ALREADY DONE. The identity/affine S-box arm was EXECUTED … (BATCH-b41ba9,
  TASK-20260806-47f217)."
- BATCH-9845b0 also exists, queue-only; it is a BATCH-002-era plan sourced from
  `DEC-20260802-b226fb` and is not a head candidate.

### Why the head still could not be moved

This record **defines its own head convention**, and that convention blocks the
move. The BATCH-713991 `merge_provenance_note` states it verbatim:
`current_batch_id` names "the most recent FULLY VERIFIED checkpoint on either
lineage", and it explicitly refused to move the head to BATCH-713991 because
that batch's `ledger_archive.commit` is null.

Applying the same test to BATCH-b41ba9 returns the same answer, because the
artifact class is identical:

- `coordination/goals/GOAL-AES-003/batches/BATCH-b41ba9/archives/TASK-20260806-3998cd/ledger-receipt.json`
  carries `"commit_pending": true`, declares **no** `path_sha256` binding, and
  records **no** dispatcher-verification result. That is the exact shape of
  BATCH-713991's receipt, whose archive this record itself says never landed.
- The contrast is on file: BATCH-014's ledger receipt carries four
  `path_sha256` digests and a `validator_verdict`, and the goal's
  `latest_verified_commit_note` says `research_dispatch.py` accepted it.
- The b41ba9 receipt's `goal_update` claims `latest_verified_commit=74e33ea35`
  and "checkpoint added" — neither of which the goal record shows. That sha
  cannot be checked without a shell and was not assumed.

Setting the head to BATCH-b41ba9 would upgrade precisely the evidence class the
record declined to upgrade three fields above. Setting it to an open batch is
also unavailable: neither BATCH-015 nor BATCH-6fe3c2 is a checkpoint under this
convention, both are unstarted, and they answer to two *different* substantive
committed GOAL-AES-003 decisions (`DEC-20260805-b42d5c` "SINGLE NEXT ACTION: …
BATCH-015" vs `DEC-20260804-73977c` D-7 "the repair task itself is dispatched
next") that the contents do not order against each other.

### What would settle it

1. **Decisive and cheap.** A shell-capable session verifies the BATCH-b41ba9
   ledger archive: run `tools/research_dispatch.py` against `74e33ea35`,
   confirm reachability-or-content-verification against the tree, and confirm
   it changes exactly the paths its receipt declares. If it verifies →
   `current_batch_id: BATCH-b41ba9`, checkpoint appended,
   `latest_verified_commit` advanced. If it does not → BATCH-014 stands and the
   flag is discharged by confirming it, not by changing it.
2. **Separately required**, because the fields move together: a Coordinator
   ruling on precedence between the two open queues. The committed
   `next_action` already ranks BATCH-015's item rank 1 and says the D-7 repair
   "does not block BATCH-015" — so `.../BATCH-015/dispatch_queue.json` is the
   likely value — but that ranking was authored before BATCH-6fe3c2's queue
   existed, and confirming it is a research judgement, not bookkeeping.
3. **Not settled by** which directory or decision file is newer in git.

---

## 2. GOAL-P13-001 — **CORRECTED**. Three fields moved together.

`ledger/goals/GOAL-P13-001.yaml`

| Field | Old value | New value | Settling record (contents) |
|---|---|---|---|
| `current_batch_id` | `BATCH-003` | `BATCH-8e1671` | `coordination/goals/GOAL-P13-001/batches/BATCH-8e1671/batch.yaml` |
| `dispatch_queue_path` | `coordination/goals/GOAL-P13-001/batches/BATCH-003/dispatch_queue.json` | `coordination/goals/GOAL-P13-001/batches/BATCH-8e1671/dispatch_queue.json` | same, plus that queue's own task states |
| `next_action` | `OPEN BATCH-004, THE FINAL BUDGETED BATCH…` (62 lines) | Dispatch the reconciliation-and-repair task BATCH-8e1671's own SCOPE-DECISION.md specifies; open no further executor batch until it completes | `BATCH-8e1671/SCOPE-DECISION.md` + `batch.yaml` `defects_found` D-1..D-7 |

### The ordering argument, contents only

`BATCH-8e1671/batch.yaml` is a committed record of *this* goal (`goal_id:
GOAL-P13-001`, `opened_by: coordinator`, `recorded_by_task:
TASK-20260807-3fe1fe`) whose own text reads BATCH-403f13's artifacts and reports
them as "already executed, in this same working tree, **before this design gate
began**". A record that reads another batch's committed outputs and reports on
them is downstream of it by its own contents — no git required. Its queue lists
`TASK-20260807-3fe1fe` `completed` and `TASK-20260807-1a8858` (its snapshot
archive) `queued`, and no `archives/` directory exists under BATCH-8e1671. So
BATCH-8e1671 is the most recently opened batch of this goal, with one genuinely
pending card: that is the live head.

Choosing BATCH-8e1671 over BATCH-403f13 (the two candidates named in the
handoff) is therefore settled, not guessed: BATCH-403f13 is the batch
BATCH-8e1671 read and reported on.

### Why the old `next_action` is superseded rather than merely restated

Read in full first. "OPEN BATCH-004" is unexecutable: no BATCH-004 directory
exists under this goal, and the four ordered items it names were executed under
BATCH-403f13, whose design report self-labels `batch_number: 4` and restates the
same four items, rerank trigger and KN-FIND obligation.

**The supersession is bookkeeping and carries no scientific ruling.** It does
not assert items (1)–(3) are officially discharged; it does not assert item (4)
was answered — BATCH-8e1671's committed D-7 records the opposite, that NC-3/NC-6
has never successfully executed once in this goal's history and its one attempt
was a `failed_infrastructure` outcome, which is never evidence about Heuristic 1
(AGENTS.md rule 5); and it does not accept the defective archive attempt
(`DEC-20260804-e19a65`, `EV-WESO-b6ceff`, `KN-FIND-4e7a92`, `KN-FIND-d1c853`).

Superseded text is preserved verbatim in
`next_action_superseded_20260810_verbatim` with its reason in
`next_action_superseded_20260810_reason`. The old `dispatch_queue_path_note` is
preserved verbatim in `dispatch_queue_path_note_superseded_20260810`; its
reasoning was sound and its premise had expired.

### Standing holds carried forward, unweakened

All four are restated inside the single new `next_action`: no handoff may direct
an execution order/tolerance/window/estimator/prediction differing from the
frozen contract it dispatches (`INCIDENT-20260802-P13-03`); every standing
prohibition of `DEC-20260802-48c72c` binds, four permanently; no task may claim
a `review-breakthrough` tier; and the KN-FIND obligation of
`DEC-20260802-48c72c.knowledge_promotion` remains outstanding, not discharged.
The record's pre-committed terminal-status call (`paused` or
`closed_at_budget`, never `completed`) is named as item (4) of the successor
task — **not made here.**

### Noted, not repaired (outside write_scope)

`experiments/EXP-P13-NC2b/specification.yaml` and
`experiments/EXP-P13-NC2d/specification.yaml` are reported non-parsing. They are
the frozen contracts under which BATCH-403f13's items (1)–(3) ran, so this is
head-relevant: the successor reconciliation task must not treat those runs as
contract-bound durable evidence until the defect is characterised, and a
genuinely malformed contract is superseded under a new `EXP` id, never edited.
Recorded in `head_correction_20260810.known_defect_noted_not_repaired`. **No
attempt at repair was made and neither file was opened for writing.**

### Deliberately not changed

`latest_verified_commit`, `batch_checkpoints`, `batches_consumed` (still 3,
uncorrected for BATCH-403f13), `batches_remaining`, `status` (`active`),
`status_note`, `closure_requirements`, `last_decision`. Each is a research-state
or durability field whose correct value depends on the git verification this
session could not perform.

---

## 3. GOAL-DREG-001 — **CORRECTED**. Three fields moved together.

`ledger/goals/GOAL-DREG-001.yaml`

| Field | Old value | New value | Settling record (contents) |
|---|---|---|---|
| `current_batch_id` | `BATCH-003` | `BATCH-005` | `ledger/decisions/DEC-20260725-026.yaml` `next_actions`; `.../BATCH-005/dispatch_queue.json`; `ledger/evidence/EV-DREG-008.yaml` |
| `dispatch_queue_path` | `coordination/goals/GOAL-DREG-001/batches/BATCH-003/dispatch_queue.json` | `coordination/goals/GOAL-DREG-001/batches/BATCH-005/dispatch_queue.json` | same |
| `next_action` | `Monitor the co-driver's EXP-DREG-004 … external driver since 14:39 …` | Close BATCH-005 in the ledger under a freshly minted decision id; C2's condition restated as an artifact check | `.../BATCH-005/archives/TASK-20260731-027/ledger-receipt.json` vs `ledger/decisions/DEC-20260731-014.yaml` |

### BATCH-004 vs BATCH-005, settled three independent ways

1. `DEC-20260725-026` — substantively a GOAL-DREG-001 decision, closing
   BATCH-004 — reads in `next_actions`: "Open GOAL-DREG-001 BATCH-005 executor
   task to run admitted chunked CTRL-B at the frozen cell with
   CTRL-B-Q-MACHINE-v1 path-pinned checks."
2. BATCH-005's own committed queue has all four cards `"state": "completed"`,
   and its executor card's objective reads "Run the **BATCH-004** repaired
   CTRL-B protocol (snapshot 8f4f1d605038 / DEC-20260725-026)" — BATCH-005
   naming BATCH-004 as its antecedent from inside BATCH-005.
3. Committed `EV-DREG-008` records that `TASK-20260731-016` executed chunked
   CTRL-B "under protocol TASK-20260725-701 / DEC-20260725-026", with
   `certificate_refs` pointing at BATCH-005 task artifacts.

Three content paths, one direction. No date, filename or commit was consulted.

### The defect this uncovered

BATCH-005's ledger receipt declares `record_ids: [EV-DREG-008,
DEC-20260731-014, GOAL-DREG-001]` with `commit_sha: null` and
`verification.status: "pending_post_commit"`. The committed
`ledger/decisions/DEC-20260731-014.yaml` is a **GOAL-ECDLP-001 / BATCH-021**
decision authored by another campaign — an identifier collision of exactly the
class `CLAUDE.md`'s ID-minting rule describes. **GOAL-DREG-001 has committed
BATCH-005 evidence and no committed BATCH-005 decision.** Neither the receipt
nor `DEC-20260731-014` is edited; the new `next_action` directs minting a fresh
id and superseding by naming.

Consequently **no `checkpoints` entry was appended** for BATCH-004 or BATCH-005:
a checkpoint records a closure, and BATCH-005 has no closing decision to record.
`latest_verified_commit` stays `bedd64c` — no committed artifact names a
verified BATCH-005 commit, and naming one would be fabrication.

### Replacing the external-driver condition

The superseded `next_action` gated this goal on the live state of a process
("external driver since 14:39; takeover if stalled >30 min"), which no committed
artifact can ever confirm or refute. The replacement states chain C2's status as
a checkable artifact fact: BATCH-003 carries `archives/` for
`TASK-20260727-N21-SNAP-C1` and `reviews/` for `TASK-20260727-N21-VAL-C1`
**only** — there is no committed artifact for `TASK-20260727-N21-SNAP-C2`,
`-VAL-C2` or `-LEDGER-C2`, and `PREREG-20260727-N21-C2.md` stands unmatched by
any receipt. C2 is unarchived; whether some other session's process still runs
is not consulted, and its absence is unarchived work, never evidence about
`d_reg`.

### Standing hold carried forward, unweakened

**The raw 17947 headline stays QUARANTINED as confounded.** BATCH-005 did not
lift it: `EV-DREG-008` states in its own words that the raw headline "remains
quarantined_confounded" and that the numerical equality with `deficit_genuine`
is the upper-interval case `rank(null|sem_support)=sr_pred`, not a re-citation
of the confounded label. `H-DREG-001` does not move on this next action.

Superseded text preserved verbatim in `next_action_superseded_20260810`.

---

## 4. Paths written

- `ledger/goals/GOAL-AES-003.yaml` — added `head_reconciliation_20260810` only;
  **no field moved**.
- `ledger/goals/GOAL-P13-001.yaml` — `current_batch_id`,
  `dispatch_queue_path`, `next_action` moved together; three superseded-text
  fields added.
- `ledger/goals/GOAL-DREG-001.yaml` — `current_batch_id`,
  `dispatch_queue_path`, `next_action` moved together; two superseded-text
  fields added.
- `coordination/reconciliation/RECON-20260810-002/tasks/TASK-20260810-2b1c3b/change_log.md`
  — this file.

Nothing was committed. No other goal record was read for writing or touched.
Each corrected goal carries **exactly one** `next_action`.

## 5. Unresolved carried forward

| id | value | successor |
|---|---|---|
| `LIVE-HEAD-AES003` | the live `current_batch_id` of GOAL-AES-003, and with it its `dispatch_queue_path` and `next_action` | verify the BATCH-b41ba9 ledger archive against `74e33ea35` with a shell, then rule on BATCH-015 vs BATCH-6fe3c2 precedence |
| `DREG-B005-DECISION` | GOAL-DREG-001 BATCH-005 has no committed closing decision; its declared `DEC-20260731-014` belongs to GOAL-ECDLP-001 BATCH-021 | item (1) of GOAL-DREG-001's new `next_action` |
| `P13-EXP-CONTRACTS` | whether `EXP-P13-NC2b` / `EXP-P13-NC2d` specifications parse, and what BATCH-403f13's runs are if they do not | item (2) of GOAL-P13-001's new `next_action` (outside this task's write_scope) |
| `P13-ARCHIVE-DEFECT` | whether BATCH-403f13's snapshot and the `DEC-20260804-e19a65` / `EV-WESO-b6ceff` / two-`KN-FIND` archive are reachable and pushed | items (1) and (3) of GOAL-P13-001's new `next_action` |
