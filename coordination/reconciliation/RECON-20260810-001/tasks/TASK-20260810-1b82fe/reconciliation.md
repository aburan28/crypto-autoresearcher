# Coordinator reconciliation memo — TASK-20260810-1b82fe (RECON-20260810-001)

Dispositions the factual audit produced by `TASK-20260810-c64cf0` at commit
`bb1c6e479296589819a8f5fbc93e6e2915bc4018`.

**This is a coordination act.** It opens no batch, moves no goal or hypothesis
status, files no evidence record, promotes no knowledge entry, approves no
experiment and closes no goal. No claim tier moves. Nothing here is admissible
toward a closure quorum. It edits no goal record and no dispatch queue: every
file edit this memo directs is named as a separate successor act, and each is
identified as such in `disposition.yaml`.

This session had no shell. Every sha, count, batch id, decision id and path
below was read out of the c64cf0 deliverables, the orchestrator correction, or
the prior memo `TASK-20260807-dcfaee/reconciliation.md`. **No value was
reconstructed, inferred from a filename or a date, or estimated.** Where the
audit left something unresolved it is left unresolved here and named as needing
a further task.

- Requested policy: `coordinator-orchestration-code`, `fallback_allowed: false`.
- Model that actually answered: `claude-opus-5` (Claude Code runtime,
  `coordinator` subagent, effort `high`). The requested policy was honoured;
  nothing was downgraded.

---

## 0. Headline figures, verified against the audit files

| Figure | Value | Where verified |
| --- | --- | --- |
| Active goals audited | 22 of 69 goal records | `goal_head_audit.scope` |
| HEAD_CURRENT / HEAD_STALE / UNRESOLVED | 13 / 9 / 0 | `goal_head_audit.counts`; no row carries `UNRESOLVED` |
| Strength of the 9 stale heads | 6 STRONG, 2 MODERATE, 1 WEAK | per-row `evidence_strength` |
| Strength of the 13 current heads | 6 STRONG, 3 MODERATE, 4 WEAK | per-row `evidence_strength` |
| Queue files examined / all committed | 223 / yes, `uncommitted_queue_files: []` for all 22 goals | `queue_state_audit.totals`, `coverage_per_goal` |
| Queued entries audited | 283 | `queue_state_audit.totals` |
| ARTIFACTS_PRESENT / PARTIAL / ARTIFACTS_ABSENT / NO_DECLARED_ARTIFACTS | 164 / 24 / 91 / 4 | `queue_state_audit.counts` |
| Declared-but-uncommitted **paths** | 224 | count of `committed: false` rows |
| …of which have committed siblings in the declared parent directory | 54 | count of `DECLARED FILENAME NOT COMMITTED` sibling notes |

Two precision corrections to how those numbers are usually quoted:

1. **54 is a count of PATHS, not of entries.** 224 declared artifact paths are
   uncommitted; 54 of them have at least one committed file in their declared
   parent directory. Those 54 paths are spread across both `ARTIFACTS_ABSENT`
   and `PARTIAL` entries, and the audit does not report how many distinct
   entries they belong to. That number is not established and is not stated
   here.
2. **HEAD_CURRENT is a weak negative, not a positive attestation.** The audit
   defines it as "no git-derived evidence that campaign activity moved past the
   recorded head." Four of the thirteen (AES-001, PATH-001, RELN-001, SDEG-001)
   carry `evidence_strength: WEAK`, meaning the absence of evidence rests on a
   directory listing. A HEAD_CURRENT/WEAK row is not a verified live head.

Per-goal verdict tallies for the 283 queued entries, derived by reading every
`goal_id`/`verdict` pair in `queue_state_audit.queued_entries`. The row totals
reconcile exactly with the audit's own `counts` block (164/24/91/4 = 283),
which is the check that the tally is complete:

| Goal | entries | PRESENT | PARTIAL | ABSENT | NO_DECL |
| --- | ---: | ---: | ---: | ---: | ---: |
| GOAL-AES-001 | 22 | 22 | 0 | 0 | 0 |
| GOAL-AES-003 | 21 | 6 | 2 | 13 | 0 |
| GOAL-DREG-001 | 14 | 0 | 2 | 12 | 0 |
| GOAL-ECDLP-001 | 128 | 68 | 14 | 46 | 0 |
| GOAL-ECTD-001 | 4 | 0 | 2 | 2 | 0 |
| GOAL-HQC-001 | 44 | 43 | 0 | 1 | 0 |
| GOAL-MCE-001 | 3 | 2 | 1 | 0 | 0 |
| GOAL-MLDSA-001 | 4 | 1 | 1 | 2 | 0 |
| GOAL-MLKEM-005 | 13 | 5 | 1 | 7 | 0 |
| GOAL-P13-001 | 5 | 0 | 1 | 3 | 1 |
| GOAL-SSI-001 | 25 | 17 | 0 | 5 | 3 |
| **total** | **283** | **164** | **24** | **91** | **4** |

The remaining eleven active goals — AES-002, CRYPTO-001, ENDO-001, FAEST-001,
HAWK-001, ICEX-001, PATH-001, RELN-001, SDEG-001, SIG-001, SSIQ-001 — have zero
entries still at `queued`. All 22 active goals are therefore accounted for.

---

## 1. The superseded anomaly

`TASK-20260810-c64cf0`'s terminal report recorded, under `anomalies`, that the
two untracked `dispatch_plan` files present at audit start "were gone at audit
end; removed by something outside this session." The same claim is restated in
the audit's own `method.md` §0 ("Something outside this session removed or
regenerated them mid-task").

**That anomaly is SUPERSEDED**, by
`coordination/reconciliation/RECON-20260810-001/orchestrator_correction_20260810.md`.
The files were never removed. The orchestrating session added
`coordination/reconciliation/*/dispatch_plan.{json,md}` to `.gitignore` in
commit `b5d7b266` while the audit was in flight, so the files left `git status`
while remaining on disk. There is no evidence of concurrent interference in
this campaign. The Executor observed the effect accurately and could not have
observed the cause.

Per the correction's own scope statement, no sha, verdict, count or
evidence-strength label in the audit is affected, and every other finding in
`goal_head_audit.yaml`, `queue_state_audit.yaml` and `method.md` stands
unamended. Neither the audit deliverables nor `method.md` are edited by this
memo; supersession is recorded here and in the correction note, per AGENTS.md
immutability.

**One anomaly is not dispositioned here and is named as such.** The correction
states that "the three remaining anomalies" stand. Their text lives in
c64cf0's terminal report, which is not among this task's inputs and is not
reproduced in the three deliverable files. Two of the three are evidently the
GOAL-HAWK-001 and GOAL-AES-002 rulings in §3 below. The third is unknown to
this session and **must not be guessed**: retrieving c64cf0's terminal report
and dispositioning any anomaly it names beyond those two is a named successor
act (`SUCC-ANOM-3` in `disposition.yaml`).

---

## 2. Where the audit contradicts the prior memo `TASK-20260807-dcfaee`

`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/tasks/TASK-20260807-dcfaee/reconciliation.md`
is an immutable prior record. **It is not edited.** Two of its statements are
corrected here by supersession, citing it.

### 2.1 The contested claim

dcfaee §1, "Left unfixed, deliberately, and why", says of the four downstream
BATCH-001 entries (`TASK-20260805-d47e12`, `-5b8a06`, `-9f2d71`, `-c60b84`):

> …are *also* stale at `"state": "queued"` … **even though their artifacts
> exist and are cited by a committed decision.**

**The audit is right and the memo is wrong on that clause.** At `bb1c6e47…`:

| Entry | Role | Audit verdict | What is actually committed |
| --- | --- | --- | --- |
| TASK-20260805-d47e12 | coordinator (snapshot) | ARTIFACTS_ABSENT | Nothing at or under `…/BATCH-001/archives/TASK-20260805-d47e12/`. The audit records `sibling_note: Nothing is committed at or under the declared parent directory either.` |
| TASK-20260805-5b8a06 | validator | ARTIFACTS_PRESENT | `…/reviews/TASK-20260805-5b8a06/validation_report.yaml`, first added in `aa1567c2fe7bc75ec4284b1523e7d7cc5882b96b` |
| TASK-20260805-9f2d71 | red-team | ARTIFACTS_ABSENT | Declared `red_team_report.md` is not committed; `red_team_report.yaml` **and** `falsification_review.md` are committed in exactly that declared directory |
| TASK-20260805-c60b84 | coordinator (ledger) | PARTIAL | 2 of 5 declared paths committed |

So one of four, not four of four. The memo's clause was a plausible inference
from a batch that had visibly produced reviews and a committed decision; it was
not checked against git, and this session's predecessor said so honestly
("this task's tool surface does not have [git access]"). **The correct record
is the audit.** dcfaee's substantive decision — to refuse to file reconstructed
`commit_sha`/`parent_sha`/`path_sha256` values — was correct and is reaffirmed;
had it filed them, three of the four would now be receipts for work that does
not exist at the declared path.

Note the important distinction the audit draws and this memo adopts: `-9f2d71`
is a **declared-vs-produced filename mismatch, not missing work**. `-d47e12` is
genuinely nothing.

### 2.2 A second, weaker correction

dcfaee §1 also states that "the goal has since progressed through at least two
further batches on 2026-08-05 (`BATCH-66b482` … `BATCH-214d98`)". The audit
does not refute this, but it establishes that **git cannot confirm it**: all
three MLDSA batch directories and the three decisions citing the other two
batches entered history in the single bulk commit
`9514c07444c3c2bb4bbe1a78d6630c5a086c8f7f` (topo pos 920), while
`DEC-20260805-0d59ff.yaml`, which cites BATCH-001, was added *later* in
`c37bb2c9d7d6b66cb9481cc049c91eee1bdf04aa` (topo pos 899). The ordering claim
is therefore **unconfirmable, not false**, and no decision in this memo rests
on it. This is exactly the class of question §4 of my instructions forbids
resolving.

---

## 3. Rulings on the two named anomalies

### 3.1 GOAL-HAWK-001 — `current_batch_id: BATCH-002` names a batch with no directory

**Ruling: the missing directory is NOT evidence that the batch is fictitious,
and the head is stale on other grounds.**

A coordination batch directory is a dispatcher convention. The goal record's
own inline `batch_checkpoints` carries a checkpoint for BATCH-002 recording
`closed_at 2026-08-02` — a committed fact in a committed record. A batch that
ran and closed without ever having a `coordination/goals/.../batches/BATCH-002/`
directory leaves exactly this footprint. Declaring the id spurious would be an
inference the audit does not support, and would amount to overwriting a
committed checkpoint by disbelief.

What the missing directory *does* establish is operational and decisive: **no
dispatch queue can ever be rendered for BATCH-002**, so any dispatch plan that
resolves this goal's head finds nothing. Combined with the committed
`closed_at`, BATCH-002 is a *closed* head, not a live one. HEAD_STALE stands at
STRONG, resting on the committed checkpoint and on the two later batches cited
by committed decisions (`DEC-20260805-77a735`, `-a62164`, `-ed4cd3`, `-bdcb53`),
not on the directory listing.

**The replacement value is DEFERRED.** Two candidate successors exist —
BATCH-56498f and BATCH-d44912 — and *neither* appears in
`checkpoints_present_for_batches` (which lists only BATCH-001 and BATCH-002),
so neither is recorded closed. BATCH-d44912 is unambiguously the newer of the
two (directory first added in `af6bcaa717daa45c61606614c4069684dfa3b76d`, topo
pos 909, outside any bulk commit; BATCH-56498f entered in bulk commit
`9514c074…`, topo pos 920). But "newest open directory" is not "the live head"
when two batches are open at once, and choosing between them is a coordination
judgement the audit cannot make. Deferred to `SUCC-HAWK-HEAD`.

Compounding fact an operator must know: GOAL-HAWK-001 has 3 batch directories
and only 1 `dispatch_queue.json` (`batch_directories_without_a_dispatch_queue:
2`), and `dispatch_queue_path` points at BATCH-001's. **Both candidate live
batches have no queue at all.** This goal currently has exactly one renderable
queue and it is not its head.

### 3.2 GOAL-AES-002 — `current_batch_id_note` asserts "No GOAL-AES-002 batch exists"

**Ruling: the note's factual assertion is refuted and is corrected now. The
substance it was defending survives intact.**

The note reads: `NULL BY FACT. No GOAL-AES-002 batch exists. Naming a batch id
or a dispatch_queue_path for a file that has not been written would be a
fabrication…`. A `coordination/goals/GOAL-AES-002/batches/BATCH-001` directory
does exist, and `ledger/decisions/DEC-20260806-357b30.yaml` names it together
with GOAL-AES-002; that decision file was first added in
`1aa1c37f6bee07b32fe8bd9553ef438418222638` (topo pos 755), newer than the goal
record's last commit `65ce43f0045d31427382314440bfd76f51ca22a3` (topo pos 916).
So the flat assertion is false and must not stand in a committed record.

But the author's actual concern was **the queue file**, not the directory, and
on that they were and remain right: `coverage_per_goal.GOAL-AES-002` records
`queues_examined: 0` and `batch_directories_without_a_dispatch_queue: 1`. The
BATCH-001 directory contains no `dispatch_queue.json`. Therefore:

- `current_batch_id` → **BATCH-001** (CORRECT_NOW).
- `current_batch_id_note` → **superseded** (CORRECT_NOW), replaced by the
  factual statement above. This half of the correction is unconditional: the
  directory exists regardless of what `DEC-20260806-357b30` means.
- `dispatch_queue_path` → **stays `null`. It is not wrong.** Setting it would
  point at a file that does not exist — precisely the fabrication the original
  note was guarding against.
- `next_action` ("DRAFT, COMMIT AND DISPATCH THE GOAL-AES-002 BATCH-001 QUEUE")
  → **not stale, and undischarged.** It is the goal's one preserved next
  action and must be left exactly as it is.

This is the memo's cleanest result: a record whose *claim* was wrong while its
*caution* was right.

---

## 4. GOAL-MLDSA-001, by name

This is what the harness is blocked on, so it is stated at length.

### 4.1 The head

`current_batch_id: BATCH-001`; `next_action` reads "BATCH-001 is queued and
dispatch-ready at …/BATCH-001/dispatch_queue.json. Run TASK-20260805-a1c3f9
(idea-generator): acquire the FIPS 204 primary text and the …".

The committed queue records `TASK-20260805-a1c3f9` at `"state": "completed"` —
this is dcfaee's own §1 edit, now committed, and the audit confirms it
independently. **The operative directive of `next_action` is discharged: the
task it orders run has already run.** That is the ordering-free contradiction
on which the audit's STRONG label rests, and it stands.

`current_batch_id` is **deferred, not corrected**. BATCH-66b482 and
BATCH-214d98 exist and are cited by committed decisions, but as §2.2 records,
git cannot order them against BATCH-001. Setting the head to either would be
exactly the upgrade of an unorderable bulk-import fact that is forbidden.
`dispatch_queue_path` agrees with `current_batch_id` and is not wrong.

### 4.2 `TASK-20260805-d47e12` specifically

Role `coordinator`, `state_in_queue: queued`, one declared artifact:
`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/archives/TASK-20260805-d47e12/snapshot-receipt.json`.
Not in the working tree, not committed, and **nothing whatsoever is committed
at or under its declared parent directory.** Verdict `ARTIFACTS_ABSENT`, with
no sibling.

The handoff's stated uncertainty was that a harness dispatching this card
"would duplicate a completed archive or manufacture one for work it did not
witness." The audit resolves that disjunction, and it is the second horn:

- **It would not duplicate a completed archive.** No snapshot receipt for
  d47e12 exists anywhere in committed history. d47e12 was never performed.
- **It would manufacture one.** The artifacts a d47e12 snapshot would have
  staged reached committed history by some other route — the validation report
  is committed at `aa1567c2fe7bc75ec4284b1523e7d7cc5882b96b`, the goal record
  and queue at `33e4c62901b482994bcf945a4cdbd98afa8b1d10`, and
  `DEC-20260805-0d59ff.yaml` is committed. A Coordinator dispatched to d47e12
  today cannot make the snapshot commit that card describes, because the
  content is already in history; the only thing it could produce is a receipt
  naming a commit it did not make. That is the fabrication AGENTS.md core rule
  5 forbids, and it is what this two-task split exists to prevent.

**Disposition: `TASK-20260805-d47e12` is BLOCKED — DO NOT DISPATCH.** It is
neither discharged nor safely queued. Its entry must be superseded, not
re-run, and the superseding note must say that the batch's artifacts were
committed outside the declared archive path. The commits named above are
**first-add commits of individual files as reported by the audit's C9 index**;
this memo does not assert that any of them is "the archive commit" for
BATCH-001, because the audit does not establish that. Successor:
`SUCC-MLDSA-D47E12`.

### 4.3 The other three BATCH-001 entries

- **`TASK-20260805-5b8a06` (validator) — DISCHARGED.** Its declared
  `validation_report.yaml` is committed (`aa1567c2…`), and a committed
  Coordinator decision, `ledger/decisions/DEC-20260805-0d59ff.yaml`, closes the
  loop on the work it reviewed. dcfaee reports its verdict as
  `accept_with_qualifications` and reports `DEC-20260805-0d59ff`'s
  `evidence_refs: [EV-MLDSA-faf2ec]` and `knowledge_promotion.promoted` for five
  KN-LIT entries; those are the *memo's* reading of the decision's contents, not
  audit facts — the audit matched decision files textually only (limitation 5)
  and never parsed decision semantics. The discharge therefore rests on: a
  committed review artifact plus a committed decision for the same batch. That
  is sufficient for a validator card and it is the **only** one of the 164
  ARTIFACTS_PRESENT entries in the whole repository for which this memo can
  name such a link.
- **`TASK-20260805-9f2d71` (red-team) — PRODUCED, NOT DISCHARGED, DO NOT
  DISPATCH.** The declared `red_team_report.md` is not committed;
  `red_team_report.yaml` and `falsification_review.md` are committed in exactly
  the declared directory. This is a filename mismatch, and the work exists.
  Dispatching it would re-run a red-team review that already ran and could
  produce a second, divergent verdict on the same evidence.
  **The declared `artifact_paths` must NOT be rewritten to match what was
  produced.** Retro-fitting a contract to its output after seeing the output is
  the prohibition on changing success criteria after observing outcomes; if the
  declaration is to change it goes through a versioned `protocol_amendment`.
  The honest successor act is to record the mismatch (this memo is that record)
  and to set the entry's `state` only after a Coordinator has read the entry's
  own `completion_gate` — which the audit did not capture and this session has
  never seen — against the two committed files. Successor: `SUCC-MLDSA-9F2D71`.
- **`TASK-20260805-c60b84` (coordinator, ledger archive) — BLOCKED, DO NOT
  DISPATCH; `PARTIAL` overstates it.** Of its five declared paths, the two
  committed ones are `ledger/goals/GOAL-MLDSA-001.yaml` and
  `coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/dispatch_queue.json` —
  **pre-existing inputs to the archive, not products of it.** All three actual
  products are absent: `ledger/evidence/EV-MLDSA-7e91a4.yaml`,
  `ledger/decisions/DEC-20260805-3d5f82.yaml`, and
  `…/archives/TASK-20260805-c60b84/ledger-receipt.json` (nothing committed under
  it). Read literally, 0 of 3 products exist.
  Dispatching this card as written would mint `EV-MLDSA-7e91a4` and
  `DEC-20260805-3d5f82` as new records for a batch whose decision
  (`DEC-20260805-0d59ff`) is already committed — i.e. it would duplicate a
  committed ledger archive under different identifiers. That the archive
  happened under *different ids than the queue declares* is the natural reading
  of these facts, but **this memo does not assert it as established**: the
  audit shows only that the declared ids are absent and that
  `DEC-20260805-0d59ff` is present and cites BATCH-001. Whether they are the
  same act is unresolved and is part of `SUCC-MLDSA-C60B84`.

### 4.4 The `TASK-20260807-dcfaee` gate

dcfaee §1 recorded: *"This is flagged for a dedicated goal-head reconciliation
task, following that precedent, before GOAL-MLDSA-001's next batch is opened."*

**Ruling: the gate is NOT discharged. It STILL STANDS, narrowed.**

- *Discharged limb (fact-finding).* The dedicated reconciliation dcfaee asked
  for now exists: the c64cf0 audit is committed at `bb1c6e47…` and this memo
  dispositions it. dcfaee's specific recommendation — "a dedicated bookkeeping
  task with git access should reconcile all four remaining entries against the
  actual commit history" — has been *performed as a factual matter*, and its
  answer is §4.2–4.3: one dischargeable, one produced-but-misdeclared, two
  blocked.
- *Standing limb (operative).* The goal head is still wrong in the committed
  record. This task is forbidden by its own write scope from editing goal
  records or queues, and it defers `current_batch_id` because git cannot order
  the candidates. So at this moment nothing has been *fixed*.

The gate is narrowed from "a goal-head reconciliation is required" to three
concrete preconditions on opening GOAL-MLDSA-001's next batch:

1. `next_action` is superseded in `ledger/goals/GOAL-MLDSA-001.yaml` (its
   directive is discharged), preserving exactly one next action —
   `SUCC-MLDSA-NEXTACTION`.
2. The three defective BATCH-001 queue entries (`-d47e12`, `-9f2d71`,
   `-c60b84`) are dispositioned in the committed queue so that no renderer
   presents them as READY — `SUCC-MLDSA-D47E12`, `SUCC-MLDSA-9F2D71`,
   `SUCC-MLDSA-C60B84`.
3. `current_batch_id` is resolved by a task that can read the three decisions
   citing BATCH-66b482/BATCH-214d98 and determine which batch is live —
   `SUCC-MLDSA-HEAD`. It may not be resolved by commit ordering; git cannot.

Until all three land, **GOAL-MLDSA-001's next batch does not open.**

---

## 5. Disposition of the 164 ARTIFACTS_PRESENT entries

The audit is explicit (`what_ARTIFACTS_PRESENT_does_not_mean`, limitation 6)
that this verdict means only that every declared path already exists in
committed history, and says nothing about discharge. That judgement is mine,
and I can only make it where committed evidence links the entry to a decision,
an evidence record or a review verdict.

**The audit establishes no such link for any entry except one.** It matched
decision files to *batch* ids by textual co-occurrence (limitation 5), never to
task ids, and it never read a task's `completion_gate`. So:

| Class | Count | Disposition |
| --- | ---: | --- |
| **A1 — DISCHARGED** | 1 | GOAL-MLDSA-001 `TASK-20260805-5b8a06`. Discharged on a committed review artifact (`validation_report.yaml`, `aa1567c2…`) plus the committed decision `DEC-20260805-0d59ff.yaml` for the same batch. See §4.3. |
| **A2 — LEFT_QUEUED, DISPATCH HOLD** | 163 | No task-level link to a committed decision, evidence record or review verdict was established by the audit, so discharge cannot be claimed. **But every declared artifact already exists in committed history, so re-dispatch would overwrite or duplicate committed work.** These entries are simultaneously not-discharged and not-safe-to-run. |

A2 by goal: GOAL-AES-001 22, GOAL-AES-003 6, GOAL-ECDLP-001 68,
GOAL-HQC-001 43, GOAL-MCE-001 2, GOAL-MLKEM-005 5, GOAL-SSI-001 17.
Plus A1's single GOAL-MLDSA-001 entry: 22+6+68+43+2+5+17+1 = **164**. The
classes are exhaustive and every goal holding such an entry is named.

That 163 entries land in one class is not a shortcut; it is the finding. **The
information needed to discharge them was never captured by any artifact this
campaign produced**, and it is not recoverable from git. Discharging them
requires reading, per entry, the queue entry's own `completion_gate` and the
goal's committed decisions — cheap per entry, but 163 of them, and a
Coordinator judgement each time. That is `SUCC-DISCHARGE-SWEEP`, and it is
correctly sized per goal rather than as one task.

### The other 119 entries, for completeness

| Class | Count | Disposition |
| --- | ---: | --- |
| **B — PARTIAL** | 24 | LEFT_QUEUED, DISPATCH HOLD. A partially-produced entry is the most dangerous card to re-run: it will re-derive artifacts that exist alongside ones that do not. Per goal: AES-003 2, DREG-001 2, ECDLP-001 14, ECTD-001 2, MCE-001 1, MLDSA-001 1, MLKEM-005 1, P13-001 1. |
| **C — ARTIFACTS_ABSENT** | 91 | LEFT_QUEUED. Genuinely pending *or* misdeclared; see the sibling split below. Per goal: AES-003 13, DREG-001 12, ECDLP-001 46, ECTD-001 2, HQC-001 1, MLDSA-001 2, MLKEM-005 7, P13-001 3, SSI-001 5. |
| **D — NO_DECLARED_ARTIFACTS** | 4 | LEFT_QUEUED and flagged as **declaration defects**: an entry with no `artifact_paths` can never be shown complete by artifact inspection and violates the requirement that a task card name exact artifact paths. GOAL-P13-001 1, GOAL-SSI-001 3. |

### The 54 sibling paths — a class the memo must split, and cannot

The headline framing "declared-vs-produced filename mismatch, not missing work"
is **right for some of these 54 paths and badly wrong for others**, and the
audit does not distinguish them. Both cases appear inside a single
GOAL-MLDSA-001 entry:

- *Meaningful (class M1).* `…/reviews/TASK-20260805-9f2d71/red_team_report.md`
  is uncommitted while `red_team_report.yaml` and `falsification_review.md` are
  committed in that same **task-scoped** directory. Here the sibling list is
  real evidence: the work exists under another name.
- *Spurious (class M2).* `ledger/evidence/EV-MLDSA-7e91a4.yaml` is uncommitted,
  and the audit dutifully lists its "committed siblings":
  `ledger/evidence/.gitkeep`, `EV-AES-001.yaml`, `EV-AES-002.yaml`… These are
  simply the other records in a **shared ledger directory**. They carry no
  information at all about the declared record, which genuinely does not exist.
  The same applies to the `ledger/decisions/` sibling list for
  `DEC-20260805-3d5f82.yaml`.

**Ruling: sibling evidence counts only when the declared parent directory is
task-scoped** (`…/tasks/<TASK-ID>/`, `…/reviews/<TASK-ID>/`,
`…/archives/<TASK-ID>/`). Where the parent is a shared ledger or knowledge
directory, the sibling list must be read as noise and the declared record
treated as absent.

**How the 54 split between M1 and M2 is UNRESOLVED.** The audit does not
partition them and this session has no shell to do so. Only three instances are
established, all in GOAL-MLDSA-001: one M1 (`-9f2d71`) and two M2 (`-c60b84`).
The remaining 51 are unclassified and are **not** to be described as filename
mismatches until partitioned. Successor: `SUCC-SIBLING-SPLIT` — a purely
mechanical path-prefix classification, no judgement required.

---

## 6. Ordering inside the three bulk-import commits

Three commits added batch directories en masse:
`33e4c62901b482994bcf945a4cdbd98afa8b1d10` (88),
`9514c07444c3c2bb4bbe1a78d6630c5a086c8f7f` (60),
`65ce43f0045d31427382314440bfd76f51ca22a3` (36). Within any one of them git
cannot say which came first.

**No verdict resting on such ordering is upgraded by this memo.** Concretely:

- GOAL-DREG-001 (MODERATE) and GOAL-P13-001 (MODERATE) keep their strength.
  Both remain HEAD_STALE at MODERATE — accepting the audit's own verdict is not
  an upgrade — and in both cases the *replacement value* is deferred anyway.
- GOAL-MLDSA-001's STRONG label is used only for the ordering-free
  `next_action`/queue-state contradiction, never for batch order (§2.2, §4.1).
- GOAL-HAWK-001's replacement value is deferred precisely because BATCH-56498f
  entered in bulk commit `9514c074…` (§3.1).
- GOAL-AES-003's replacement value is deferred: its newest-added directory
  BATCH-6fe3c2 is cited by **no** committed decision, and the newest
  decision-cited candidates (BATCH-015, BATCH-b41ba9) cannot be ordered against
  each other from git. Self-declared `DEC-YYYYMMDD-` dates are not git facts
  (limitation 4) and were not used.

### GOAL-ECTD-001 — the WEAK verdict, deferred rather than acted on

The audit graded GOAL-ECTD-001 HEAD_STALE at **WEAK**, and said why: its sole
basis is that a `BATCH-33b207` directory exists (first added
`061123d06a0d91b3a5ce78961531cf65a2756890`, topo pos 756), **no committed
decision names it**, and all four entries in its `dispatch_queue.json` are at
`queued`. That is a directory listing. A concurrent session can create a batch
directory it never uses — which is exactly what an unused directory with an
all-queued queue looks like.

**Ruling: I decline to treat GOAL-ECTD-001's head as stale on this evidence.**
`current_batch_id: BATCH-e722dd` stands as the recorded head until a committed
decision or checkpoint says otherwise. Deferred to `SUCC-ECTD-HEAD`.

One observation is passed forward as an *unresolved question*, not as a
stronger argument: the audit's `checkpoints_present_for_batches` for this goal
lists BATCH-e722dd itself, i.e. the goal's own inline `batch_checkpoints` carry
an entry for its current batch. For GOAL-AES-003, GOAL-HAWK-001 and
GOAL-P13-001 the audit quoted a `closed_at` for such checkpoints; **for
GOAL-ECTD-001 it quoted none**, and it did not use this fact. This memo
therefore does **not** conclude BATCH-e722dd is closed — that would be building
a new, stronger case the audit neither made nor graded, on a field whose
contents this session has not read. `SUCC-ECTD-HEAD` must read that checkpoint.

---

## 7. What a harness operator may and may not trust in a rendered dispatch plan

### May trust

1. **Every dispatch queue file under an active goal is committed and parses.**
   223 files, zero parse failures, `queue_files_all_committed: true` and
   `uncommitted_queue_files: []` for all 22 goals. A rendered plan is not
   reading uncommitted or corrupt queue state.
2. **The list of active goals and their recorded head fields**, as literal
   values, at commit `bb1c6e47…`. What those values *mean* is §7's second half.
3. **The four dispositions in §3.2 for GOAL-AES-002** and the single discharge
   in §4.3. Those are the only positive statements this memo makes.

### May not trust

4. **Any rendered plan for the 9 HEAD_STALE goals**: GOAL-AES-002,
   GOAL-AES-003, GOAL-DREG-001, GOAL-ECDLP-001, GOAL-ECTD-001, GOAL-HAWK-001,
   GOAL-ICEX-001, GOAL-MLDSA-001, GOAL-P13-001. For 7 of the 9 the correct head
   is unknown. (GOAL-ECTD-001 is listed here because its status is *unverified*
   after §6, not because it is confirmed stale.)
5. **HEAD_CURRENT is not an attestation.** Four of the thirteen (AES-001,
   PATH-001, RELN-001, SDEG-001) rest on WEAK evidence — absence of a newer
   directory. Three more (CRYPTO-001, FAEST-001, SIG-001) are MODERATE.
6. **Any READY card whose artifacts already exist.** 164 entries. Running one
   overwrites or duplicates committed work. 24 more (PARTIAL) are worse.
7. **A card's existence is not evidence that its work is pending.** Up to 54
   declared paths are filename mismatches rather than missing work, and the
   split is unresolved (§5).
8. **Any goal whose `dispatch_queue_path` disagrees with its
   `current_batch_id`.** Three do, inside the same committed record:
   GOAL-AES-003 (queue BATCH-009 vs head BATCH-014), GOAL-ECDLP-001 (queue
   BATCH-dace3f vs head BATCH-c3c474), GOAL-HAWK-001 (queue BATCH-001 vs head
   BATCH-002). A plan rendered for these describes a *different batch* from the
   one the head names.
9. **Goals that cannot render anything meaningful.** GOAL-AES-002 and
   GOAL-ENDO-001 have zero queue files. GOAL-HAWK-001's two candidate live
   batches have none. GOAL-SSIQ-001 has 14 batch directories, 12 without a
   queue, and a null `dispatch_queue_path`. GOAL-ECDLP-001 has 47 of 140 batch
   directories without a queue.
10. **`GOAL-ECDLP-001`'s head in particular.** `BATCH-c3c474` is closed by its
    own committed checkpoint (`decision_id DEC-20260809-d5ff80`), eleven further
    checkpoints were added in topologically newer commits, and the newest,
    `checkpoints/BATCH-fc86ca.yaml` (`1f41348d98d63a03aed2735ceafe9d490ce3b882`,
    topo pos 33, `decision_id DEC-20260809-92e370`), **closes BATCH-fc86ca
    too**. The live head is therefore a batch this audit did not identify, and
    the goal record still carries `updated_at: 2026-07-29` although its file's
    last commit is `aed9e814ce4cb76c15bdf367cda3ba64cc6ce4b1` at topo pos 27.

### Remains unaudited — do not read silence here as clearance

11. **47 of 69 goal records** (`draft`, `paused`, `completed`,
    `closed_at_budget`) and the 46 queue files outside the active set.
12. **`coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-IV-20260808/dispatch_queue.json`**
    — an in-goal queue belonging to an active goal, outside the `batches/` glob,
    explicitly named by the audit as the one a reader would expect to be
    covered and is not.
13. **`coordination/dispatch_queue.json`** and the `RECON-20260802-001` /
    `RECON-20260810-001` campaign queues.
14. **Every entry not at `state: queued`.** The audit listed queued entries
    only. An entry marked `completed` whose artifacts are absent would not have
    been caught by any part of this campaign. This is the largest unexamined
    surface and it is the mirror image of the problem the campaign was chartered
    to find.
15. **Decision semantics.** Batch-to-decision matching was textual
    co-occurrence; a decision that merely mentions a batch is counted like one
    that closes it (limitation 5). Every "cited by a committed decision" claim in
    this memo inherits that.
16. **Task completion gates.** None were read, anywhere. This is why 163 of 164
    ARTIFACTS_PRESENT entries could not be discharged.
17. **Experiment run records, ledger validity, and branch/PR state.** Nothing in
    `experiments/`, no `tools/validate_ledger.py` run, and no check that
    `bb1c6e47…` is reachable from `origin/main`.

### One value stays UNRESOLVED and is not reconstructed

`goal_head_audit` reports GOAL-AES-002's
`commit_that_introduced_current_batch_id_value` as the literal string
`UNRESOLVED: current_batch_id is null, so no -S search string exists`. **It
remains UNRESOLVED.** It is not inferred from `65ce43f0…`, from the goal
record's `updated_at`, or from anything else. It becomes answerable only after
`SUCC-AES002-HEAD` writes a non-null value, at which point the question
dissolves rather than being answered.

---

## 8. Terminal position

`PARTIALLY_RECONCILED`. Four field corrections are stated with committed
evidence, across two goals. Eighteen field-level dispositions are deferred to
nine named successor acts, because the audit establishes that a head is stale
without establishing what it should be — which is the honest outcome of a
git-only audit, not a shortfall of effort. One of 164 ARTIFACTS_PRESENT entries
is discharged; 163 are held. The `TASK-20260807-dcfaee` gate on GOAL-MLDSA-001
**still stands**, narrowed to three named preconditions.

Full structured detail, including every successor act, is in
`disposition.yaml` in this directory.
