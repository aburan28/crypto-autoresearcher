# Change log — TASK-20260810-e45e48

**Campaign:** RECON-20260810-002 · **Act type:** coordination · **Date:** 2026-08-10
**Branch:** `claude/goal-head-reconciliation-20260810` · **Committed by this task:** nothing. This task never commits.

**Inference provenance.** Requested policy `coordinator-orchestration-code`,
`fallback_allowed: false`. Answered by `claude-opus-5` under the `claude_code`
runtime as the `coordinator` subagent at `effort: high`, which is what
`orchestration/roles.yaml` → `orchestration/model-policies.yaml` bind that
policy to for this runtime. `fallback_used: false`, `degraded: false`. The
policy was honoured; nothing was downgraded.

**Fabrication guard.** This session had **no shell**. It verified no sha, no
commit reachability, no parent and no commit ordering, and it minted no
identifier. Every sha, id, path, verdict and count below was read out of a named
file in the working tree. Where a value could not be established from record
contents it is left UNRESOLVED and said so.

**What this act is not.** It opens no batch, moves no hypothesis status, files
no evidence record, promotes no knowledge entry, approves no experiment and
closes no goal. No claim tier moves. Nothing here is admissible toward a closure
quorum. It asserts nothing about ML-DSA, MLWE, MSIS or SelfTargetMSIS in either
direction.

---

## Files written

| Path | Nature of change |
|---|---|
| `coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/dispatch_queue.json` | four queue entries dispositioned (items a–d) |
| `ledger/goals/GOAL-MLDSA-001.yaml` | head fields corrected (items e–f) plus two consequential fields |
| `coordination/reconciliation/RECON-20260810-002/tasks/TASK-20260810-e45e48/change_log.md` | this file |
| `coordination/reconciliation/RECON-20260810-002/tasks/TASK-20260810-e45e48/gate_status.md` | gate ruling |

Nothing outside `write_scope` was written. No immutable record was edited: the
decisions, evidence records, review reports, `TASK-20260807-dcfaee/reconciliation.md`
and the RECON-20260810-001 disposition were all read only.

---

## (a) TASK-20260805-d47e12 — snapshot archive — SUPERSEDED AS UNPERFORMABLE

**What changed.** `state` `queued` → **`cancelled`**, plus a `supersession` block
recording why. **Not dispatched. Not satisfied. No receipt written.**
`archive.commit_sha`, `archive.parent_sha` and `archive.path_sha256` are left
`null`/`{}` untouched.

| | |
|---|---|
| old | `"state": "queued"`, no supersession block |
| new | `"state": "cancelled"` + `supersession` |

**Why `cancelled` and not `blocked`.** `blocked` is a hold a later dispatcher can
lift; this card can never be performed, so a terminal state is the honest one.
`cancelled` is also the only terminal state that does **not** require
`archive.commit_sha` and a complete `path_sha256`
(`tools/research_dispatch.py`, `validate_queue`: a *completed* archive task
requires both). A card whose whole defect is a missing receipt must not be given
a state that demands a fabricated receipt. Legal state set is
`{queued, running, blocked, completed, failed, invalid, cancelled}`; `superseded`
is not a member, which is why the supersession lives in a sibling block rather
than in `state`.

**Ruling.** The declared artifact
`…/BATCH-001/archives/TASK-20260805-d47e12/snapshot-receipt.json` does not exist,
and no `archives/` directory exists under BATCH-001 at all. BATCH-001's artifacts
nevertheless reached committed history **outside the declared archive path**.
Because the content is already in history, a Coordinator dispatched today cannot
make the commit this card describes; the only artifact it could produce is a
receipt naming a commit it did not make — the fabrication AGENTS.md core rule 5
forbids.

**A correction to RECON-20260810-001, recorded by supersession.** That
disposition ruled "d47e12 was never performed". That is right about the
*deliverable* and wrong about the *act*. The committed validator report
`…/reviews/TASK-20260805-5b8a06/validation_report.yaml` (CHK-1) states verbatim:

> "No separate archives/TASK-20260805-d47e12/ directory exists in the working
> tree — the archive is the git commit itself."

and records the snapshot commit `8242344ce106e324e3f42e5b163061a251b7e9f9`,
parent `8aca58a23644b2be4ebdd7a2d357957da26ae4fc`, commit message
`snapshot(TASK-20260805-d47e12): GOAL-MLDSA-001 BATCH-001 lit-acquisition`,
`files_changed_in_commit: 6`, `reachable_from_HEAD: true`, and six matching blob
hashes. `ledger/evidence/EV-MLDSA-faf2ec.yaml` carries the same
`snapshot_commit`. So the snapshot commit was made and independently verified at
the time; only the receipt artifact was never written. **The operative
conclusion is unchanged and strengthened**: the archive act is already in
history without a receipt, so the card can only be terminated, never satisfied.
Those shas are quoted from committed records at those records' own level of
assurance; this session verified none of them and copied none of them into the
`archive` block.

**Settling records.**
`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/reviews/TASK-20260805-5b8a06/validation_report.yaml`
(CHK-1); `ledger/evidence/EV-MLDSA-faf2ec.yaml`;
absence of `…/BATCH-001/archives/` (audit `TASK-20260810-c64cf0`, re-checked here).

---

## (b) TASK-20260805-5b8a06 — validator — COMPLETED

**What changed.** `state` `queued` → **`completed`**. **State field only. No
other field added at that level**, matching the pattern `TASK-20260807-dcfaee`
used for `TASK-20260805-a1c3f9`, which in turn matched
`GOAL-HQC-001/batches/BATCH-001/dispatch_queue.json`.

| | |
|---|---|
| old | `"state": "queued"` |
| new | `"state": "completed"` |

**Settling records.**
`…/reviews/TASK-20260805-5b8a06/validation_report.yaml` — committed, `verdict:
accept_with_qualifications`, four named duties answered with measured values —
and `ledger/decisions/DEC-20260805-0d59ff.yaml`, the committed Coordinator
decision for BATCH-001 that reports that verdict and cites `EV-MLDSA-faf2ec`.
This is the single entry RECON-20260810-001 placed in class A1 (DISCHARGED); the
present task adopts that discharge and does not re-derive it.

---

## (c) TASK-20260805-9f2d71 — red team — COMPLETED, WITH THE MISMATCH RECORDED

**What changed.** `state` `queued` → **`completed`**, plus a `completion_ruling`
block. **`artifact_paths` is NOT rewritten.**

| | |
|---|---|
| old | `"state": "queued"`; `artifact_paths: [".../red_team_report.md"]` |
| new | `"state": "completed"` + `completion_ruling`; `artifact_paths` **unchanged** |

**The entry's own completion_gate, read as written.**

| Gate item | Verdict | Where |
|---|---|---|
| All four named duties answered, including any that found nothing | SATISFIED | `red_team_report.yaml` answers `source_exhaustion_check`, `prejudgment_check`, `rule7_discipline_check`, `scope_inflation_check` as four separate blocks; `completion_gate_self_check` re-answers all four plus three supplementary duties; `falsification_review.md` carries the same four as Duty 1–4 plus an explicit "Non-findings (duties that found nothing)" section. Two duties found nothing and say so with `objection: null`. |
| Each objection carries the cheapest concrete control | SATISFIED | OBJ-A / OBJ-B / OBJ-C each carry `resolution`; each originating check block carries `cheapest_control`. |
| Explicit verdict on whether the batch may proceed to a ledger archive | SATISFIED | `verdict: pass_with_constraints`, restated as "Batch may proceed to TASK-20260805-c60b84 ledger archive subject to three named constraints in `required_for_ledger_archive`". |

**The mismatch, recorded and not repaired.** Declared:
`…/reviews/TASK-20260805-9f2d71/red_team_report.**md**` — absent. Produced and
committed in the same task-scoped directory:
`red_team_report.**yaml**` and `falsification_review.md`, the second never
declared at all. This is RECON-20260810-001's subclass **M1** (task-scoped
declared parent): real evidence the work exists under a different filename, not
missing work.

**`artifact_paths` was deliberately left wrong.** Rewriting a declared path to
match what was produced, after seeing what was produced, retro-fits a contract to
its output — the prohibition on changing success criteria after observing
outcomes. If the declaration is to change it goes through a versioned
`protocol_amendment`, not through this task. The honest consequence is stated in
the entry: **this card is completed with a live declared-artifact mismatch**, its
gate met in substance and its declared path empty, and any future presence check
against `artifact_paths` will correctly flag it. The `completion_ruling` block,
not a rewritten path, is the answer to that flag.

**Settling records.**
`…/reviews/TASK-20260805-9f2d71/red_team_report.yaml`;
`…/reviews/TASK-20260805-9f2d71/falsification_review.md`;
the entry's own `handoff.completion_gate` in this queue file.

---

## (d) TASK-20260805-c60b84 — ledger archive — RESOLVED, THEN SUPERSEDED

**The question RECON-20260810-001 left UNRESOLVED** (`C60B84-IDENTITY`): are
`DEC-20260805-0d59ff` / `EV-MLDSA-faf2ec` the ledger archive this entry declared
under `EV-MLDSA-7e91a4` / `DEC-20260805-3d5f82`?

**RESOLVED — YES, THE SAME ACT.** Established from record contents only, with no
appeal to commit ordering. The audit could not answer it because it never read
the records; the answer was inside them.

- **Decisive:** `ledger/evidence/EV-MLDSA-faf2ec.yaml` carries
  `recorded_by_task: TASK-20260805-c60b84`. The evidence record names this card
  as the task that produced it.
- `EV-MLDSA-faf2ec` also carries `goal_id: GOAL-MLDSA-001`, `batch_id: BATCH-001`,
  `validator_verdict: accept_with_qualifications` and `red_team_verdict:
  pass_with_constraints` — matching this card's two declared `source_task_ids`
  exactly (5b8a06's and 9f2d71's committed verdicts).
- `DEC-20260805-0d59ff` carries `batch_id: BATCH-001`, `evidence_refs:
  [EV-MLDSA-faf2ec]`, and a `red_team_gates_resolved` block that answers, one for
  one, the three items 9f2d71's report listed under `required_for_ledger_archive`
  as rulings that "`DEC-20260805-3d5f82`" must carry: gate_1 (does the partial
  FIPS 204 entry satisfy `RQ-MLDSA-001.constraints[0]`), gate_2 (correction
  propagation, OBJ-C), gate_3 (Ravi 2022 dominance, OBJ-A).
- `DEC-20260805-0d59ff.knowledge_promotion.promoted` lists five KN-LIT ids and
  all five files exist under `knowledge/literature/` (`KN-LIT-4dadec`, `-340675`,
  `-4f3b80`, `-180ad5`, `-8ce0b5`).

**What changed.** `state` `queued` → **`cancelled`**, plus a `supersession` block
carrying the identity ruling and the list of what was *not* performed.

| | |
|---|---|
| old | `"state": "queued"`, no supersession block |
| new | `"state": "cancelled"` + `supersession` |

**What was not performed, recorded rather than papered over.** The two declared
ids were never minted (`ledger/evidence/EV-MLDSA-7e91a4.yaml` and
`ledger/decisions/DEC-20260805-3d5f82.yaml` do not exist);
`…/archives/TASK-20260805-c60b84/ledger-receipt.json` was never written and no
post-commit verification receipt exists for this archive; the declared
goal-record deliverables (BATCH-001 checkpoint, `latest_verified_commit`, a
superseded `next_action`) were not completed until this task, five days later;
and the queue was never brought to its terminal state. **BATCH-001 therefore has
a committed ledger archive with no receipt and no recorded post-commit
verification.** That gap is left visible and must not be repaired by writing a
receipt after the fact.

**Why cancelled, not completed.** Its own completion gate is not met, and marking
an archive task completed would require `archive.commit_sha` plus a complete
`path_sha256` this session cannot obtain and must never reconstruct. Dispatching
it as written is worse: it would mint `EV-MLDSA-7e91a4` and `DEC-20260805-3d5f82`
as new records for a batch whose evidence and decision are already committed,
duplicating a committed archive under new identifiers.

**Settling records.** `ledger/evidence/EV-MLDSA-faf2ec.yaml`
(`recorded_by_task`); `ledger/decisions/DEC-20260805-0d59ff.yaml`
(`red_team_gates_resolved`, `evidence_refs`, `knowledge_promotion`);
`…/reviews/TASK-20260805-9f2d71/red_team_report.yaml`
(`required_for_ledger_archive`); the five `knowledge/literature/KN-LIT-*.md`
files; the absence of the two declared ledger paths.

---

## (e) GOAL-MLDSA-001 `current_batch_id` — RESOLVED FROM RECORD CONTENTS

**What changed.**

| field | old | new |
|---|---|---|
| `current_batch_id` | `BATCH-001` | **`BATCH-214d98`** |
| `current_batch_id_superseded` | — | added: prior value, reason, ordering-free derivation, settling records |
| `current_batch_id_note` | — | added: BATCH-214d98 is the most recent batch **and it is closed** |

**Derivation, using record contents only — no commit ordering, no dates, no
directory listings.** Bulk commit `9514c074` destroyed the git ordering and this
session has no shell; neither of those is used below.

1. `DEC-20260805-0d59ff` (BATCH-001) closes BATCH-001 and directs "Open
   BATCH-002: run `/propose-ideas RQ-MLDSA-001` against the now-filed KN-LIT
   entries."
2. `DEC-20260805-4843d6` (BATCH-66b482) is that ideation batch's closing
   decision — producer `TASK-20260805-a44587` ran `/propose-ideas` on
   RQ-MLDSA-001 — and it consumes what BATCH-001 filed (KN-LIT-3907, KN-LIT-056,
   the corrected Jendral values, the FIPS 204 body gap). It directs dispatching
   `IDEA-a8d531`, `IDEA-2b6f17`, `IDEA-3f7ab2` as frozen experiment contracts.
3. `DEC-20260805-ae4a96` (BATCH-214d98) reports on exactly those three
   (`EXP-MLDSA-a8d531`, `EXP-MLDSA-2b6f17`, `IDEA-3f7ab2`). BATCH-214d98
   consumes BATCH-66b482's output, so it strictly follows it. **This is a
   producer-to-consumer dependency between record contents, not a timestamp.**
4. `DEC-20260805-64abe7` carries the explicit field `supersedes:
   DEC-20260805-ae4a96`, same batch.
5. `DEC-20260805-79d745` carries `note: BATCH-005 substitute — no new batch
   opened; data-gap recorded in existing BATCH-214d98 closure`. "BATCH-005" is
   named as a next action **only** by `DEC-20260805-64abe7`, so 79d745 answers it
   and is the terminal committed decision for this goal.
6. No committed decision names any other GOAL-MLDSA-001 batch, and 79d745 states
   "No new batch authorized under this constraint."

Therefore the goal's most recent batch is **BATCH-214d98**, and it is **closed**.
The head now names the goal's last batch, not an open one. The four
`ledger/corrections/schema-supersessions/20260808/` v2 files for these decisions
were checked: they are schema normalisations (they add `target_ids`) and change
no `batch_id`, no `supersedes` and no `note`.

**Consequential edit — `dispatch_queue_path` → `null`.** RECON-20260810-001 ruled
this field NOT_WRONG *only because* it agreed with a `current_batch_id` of
BATCH-001. Once the head moves, leaving it creates exactly the head-internal
mismatch that audit flagged in GOAL-AES-003, GOAL-ECDLP-001 and GOAL-HAWK-001,
and points a renderer at BATCH-001's queue, every entry of which is now terminal.
BATCH-214d98 has no `dispatch_queue.json` (neither does BATCH-66b482; only
BATCH-001 ever had one), so `null` is the only truthful value, and it is a legal
committed value for this field elsewhere in this ledger. This edit is inside
`write_scope` and is flagged here because it was not one of the six named items;
a reviewer who disagrees should supersede it, not revert it silently.

**Consequential edit — `latest_verified_commit_note`.** Field stays `null`. The
note records why: no shell, and BATCH-001's ledger archive left no receipt, so
there is no verified commit to record. Writing one from a sha quoted elsewhere is
the reconstruction `TASK-20260807-dcfaee` correctly refused.

**Consequential edit — `updated_at`** `2026-08-05` → `2026-08-10`, with
`updated_at_note` stating that the edit is head bookkeeping only: `status` stays
`active`, `active_hypothesis_ids` stays empty, no completion criterion is
approached, no claim tier moves, no batch is opened.

**Settling records.** The five decisions named above, plus their v2 schema
supersessions.

---

## (f) GOAL-MLDSA-001 `next_action` — SUPERSEDED, EXACTLY ONE LEFT

**What changed.** `next_action` replaced; `next_action_history` added carrying
the old text verbatim with `superseded_because`; **the pre-existing
`next_action_superseded` block is preserved verbatim and unedited** and the new
history entry points at it. `next_action_history` is this repository's own
pattern for repeat supersession (`ledger/goals/GOAL-MCE-001/goal.yaml`).

**Old (operative directive discharged).** "BATCH-001 is queued and dispatch-ready
… **Run TASK-20260805-a1c3f9** … Then run its snapshot archive
(TASK-20260805-d47e12) alone, independent validator (TASK-20260805-5b8a06) and
red-team (TASK-20260805-9f2d71) review, and the ledger archive
(TASK-20260805-c60b84) that records EV-MLDSA-7e91a4 and DEC-20260805-3d5f82…"

Discharged: `TASK-20260805-a1c3f9` is recorded `completed` in the committed queue.
Unperformable: all four downstream directives, for the reasons in items (a)–(d)
above — two now completed, two now cancelled, and the two record ids the text
names were never minted.

**New — exactly one action, with the standing hold preserved.** The goal is
**HELD**: `DEC-20260805-79d745` states "No new batch authorized under this
constraint", Lane A deferred on an infrastructure blocker (ePrint 2023/246 PDF,
HTTP 403 across four recorded routes; under AGENTS.md rule 5 that is
infrastructure, never evidence about the tightness loss). That hold is carried
forward unchanged. The one action is the conditional directive
`DEC-20260805-79d745` itself records: *if and only if* full-text access to ePrint
2023/246 becomes available, open the next batch — id minted with
`tools/allocate_id.py --next batch` and `--check`ed, not assumed to be the
literal "BATCH-005" — to extract the CMA-to-NMA tightness factor, re-run
`EXP-MLDSA-3f7ab2` with a formula verified from the source rather than from the
idea generator (`DEC-20260805-ae4a96` ANO-3), and carry `H-MLDSA-d1e509` out of
`inconclusive`. It names its preconditions and points at `gate_status.md`.

**This does not authorize anything.** The conditional authorization is
`DEC-20260805-79d745`'s, quoted forward; this task neither grants nor widens it,
and the `next_action` says so explicitly.

**Settling records.** `ledger/decisions/DEC-20260805-79d745.yaml` (the hold and
the conditional directive); `DEC-20260805-64abe7`, `DEC-20260805-ae4a96` (the
work the conditional directive resumes);
`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/dispatch_queue.json`
(`TASK-20260805-a1c3f9` at `completed`).

---

## Correction to TASK-20260807-dcfaee §1 — BY SUPERSESSION, NEVER BY EDIT

`TASK-20260807-dcfaee/reconciliation.md` is **not edited**. It is an immutable
record and stays exactly as written. This section supersedes one clause of it.

**The clause.** dcfaee §1: the four downstream BATCH-001 entries are stale at
`queued` "**even though their artifacts exist and are cited by a committed
decision**".

**THE AUDIT IS RIGHT AND THE MEMO IS WRONG ON THAT CLAUSE.** At the **declared
paths**, one of four has its artifacts, not four of four:

| entry | at its declared paths |
|---|---|
| TASK-20260805-5b8a06 | **present** (1) |
| TASK-20260805-c60b84 | **partial** (2 of 5, and both committed paths are pre-existing *inputs*, not products — read literally, 0 of 3 products) |
| TASK-20260805-d47e12 | **absent** |
| TASK-20260805-9f2d71 | **absent** (filename mismatch, not missing work) |

**And, from the record contents this task read, the act-level picture is
different from the path-level one — stated so that neither is overstated.** Three
of the four acts left committed traces under other names: 9f2d71's report exists
as `.yaml` beside an undeclared `falsification_review.md`; c60b84's evidence and
decision exist as `EV-MLDSA-faf2ec` / `DEC-20260805-0d59ff`; d47e12's snapshot
commit is evidenced by a committed independent validation report though its
receipt was never written. c60b84 is genuinely incomplete: no receipt, no
recorded post-commit verification, and its goal-record deliverables unfinished
until today. **Neither reading rescues the memo's clause**: "their artifacts
exist and are cited by a committed decision" was not true of the four entries as
declared, and the audit's path-level count is the one that governs what a
dispatcher may do.

**dcfaee's refusal to file reconstructed hashes was CORRECT, and is reaffirmed.**
It declined to fill `commit_sha`/`parent_sha`/`path_sha256` for the four
archive-bearing entries because it had no git access and filing placeholder or
reconstructed hashes would itself be a fabrication. Had it filed them, **three of
the four would now be receipts for work absent at the declared path** — and the
one archive whose commit *is* evidenced would carry a sha this program still
cannot verify. This task took the identical position: it wrote no sha anywhere,
left both `archive` blocks null, and terminated both archive cards rather than
completing them.

---

## UNRESOLVED, carried forward

- **`AES002-CBID-COMMIT`**, **`SIBLING-SPLIT`**, **`SIBLING-ENTRY-COUNT`**,
  **`ANOMALY-3`**, and the remaining six **`LIVE-HEADS`** — untouched by this
  task, still owned by RECON-20260810-001's successor acts. Only
  `C60B84-IDENTITY` and GOAL-MLDSA-001's own head are resolved here.
- **BATCH-001's missing archive receipts.** No snapshot receipt and no ledger
  receipt exist, and no post-commit verification is recorded for either archive.
  Left as a visible defect. **It must not be repaired by writing a receipt after
  the fact**; the only honest repair would be a superseding record that states
  the gap.
- **Whether `8242344ce106e324e3f42e5b163061a251b7e9f9` is reachable from
  `origin/main` today**, and whether BATCH-001's records were pushed to a branch
  with an open PR. No shell; not established.
- **Whether `tools/validate_ledger.py` and `tools/research_dispatch.py` accept
  the two files this task edited.** They were written to the schemas as read
  (`state` drawn from the legal set; no required field removed; no unknown-key
  rejection exists in `validate_queue`), but **neither tool was run**. The
  session that commits this work must run both before treating it as durable.
- **Every BATCH-001 queue entry not at `queued`** was outside the audit's scope
  and remains so; this task read all five entries of this one queue but claims
  nothing about the other 222 queue files.
