# Coordinator reconciliation — TASK-20260809-8c4759

Follow-on to `TASK-20260807-dcfaee`, which reconciled ONE dispatch-queue field
and named this task explicitly twice: "a dedicated bookkeeping task with git
access should reconcile all four remaining entries against the actual commit
history", and "This is flagged for a dedicated goal-head reconciliation task
... before GOAL-MLDSA-001's next batch is opened."

This memo is bookkeeping and disposition only. It creates no hypothesis, runs
no experiment, re-reviews no artifact, files no knowledge entry, and makes no
security assessment of ML-DSA / FIPS 204 / MLWE / MSIS / SelfTargetMSIS in
either direction. The official record of the judgements below is
`ledger/decisions/DEC-20260809-333a4c.yaml`; this memo is its human-readable
companion.

## 0. READ THIS BEFORE READING THE TABLE

Two BATCH-001 archive tasks terminate at `invalid` below. **That is a
BOOKKEEPING verdict about a receipt, not a finding that the reviewed content
was unfrozen, mutated, or contaminated.** The BATCH-001 literature package and
the two independent reviews that read it are untouched by this memo, and the
evidence for that is positive rather than merely absent:

- Each of the five declared producer artifacts has a **byte-identical sha256 at
  the snapshot commit `f44ffbad9` and at HEAD**. The bytes never moved.
- The review commit `aa1567c2f`'s **direct parent is `f44ffbad9`**, the snapshot
  commit itself. The reviewers demonstrably read the frozen object.

The freeze worked *materially*. What is missing is the receipt artifact that
would let `research_dispatch.py` verify it *mechanically*, and that artifact can
never be produced now without backdating a receipt for a commit another session
made on 2026-08-05 — fabrication under AGENTS.md rule 9, and refused.

Nobody reading the queue later should mistake `invalid` on `TASK-20260805-d47e12`
or `TASK-20260805-c60b84` for evidence contamination. It means: *this archive
receipt can never be verified as declared.*

## 1. Provenance of every git fact in this memo

This Coordinator session has **no shell and no git access**. Every commit sha,
content hash, date, commit message, and changed-path set below was computed and
supplied by the dispatching session and is reproduced verbatim — facts F1–F7 at
task start, then facts F8–F10 and F11 supplied mid-task in response to this
memo's own first pass, which had filed the `EV-MLDSA-faf2ec` snapshot-commit
question and the missing full head-commit sha as unreconciled (§2.6 and §2.7 now
close them). Nothing was reconstructed, estimated, or
inferred, and where a needed fact was not supplied the item is left unreconciled
in §4 rather than filled. An independent re-audit with shell access is the
correct way to check this memo.

## 2. What was fixed

### 2.1 The four remaining BATCH-001 queue entries

`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/dispatch_queue.json` listed
all four at `"state": "queued"` although their work was committed on 2026-08-05.
Each now carries a terminal state and an **additive** `reconciliation_note`
pointing at `DEC-20260809-333a4c`. No existing field was deleted or rewritten —
in particular the `archive` blocks still read `commit_sha: null`,
`parent_sha: null`, `path_sha256: {}`, and `TASK-20260805-c60b84` still declares
the two identifiers that were never minted.

The additive note is not decoration. A bare `"state": "invalid"` on a snapshot
archive, with no explanation in the file a dispatcher actually reads, is exactly
the string a later session would misread as "the reviewed package is suspect".
The note is the cheapest available control against that misreading.

### 2.2 The archive-gate defect, stated exactly

`research_dispatch.py` requires a `completed` archive task's `path_sha256` to
cover **exactly** (its own `artifact_paths`) ∪ (its source tasks'
`artifact_paths`), and requires the commit to change exactly that set
(`validate_queue`, and `verify_archive` for the commit binding). For
`TASK-20260805-d47e12` the expected set is the five declared `a1c3f9` artifacts
**plus** `archives/TASK-20260805-d47e12/snapshot-receipt.json`. The actual commit
`f44ffbad9` changed six paths:

- **MISSING**: `archives/TASK-20260805-d47e12/snapshot-receipt.json` — never
  written; the `archives/` directory does not exist in the repository at all.
- **EXTRA**: `tasks/TASK-20260805-a1c3f9/receipt.yaml` — a real and useful file,
  but not among `a1c3f9`'s declared `artifact_paths`.

`f44ffbad9` is immutable, so the declared set and the commit can never be
reconciled. `completed` is therefore unavailable as a matter of mechanism, not
of judgement.

### 2.3 Two identifiers retired unused

`EV-MLDSA-7e91a4` and `DEC-20260805-3d5f82` were declared in this queue
(`TASK-20260805-c60b84`'s `write_scope`, `artifact_paths`, and
`archive.record_ids`) and **were never minted**. Neither file exists at any
commit. They are **retired-unused** and **must never be reused** for any record
by any session (AGENTS.md rule 14). The batch's real records are
**`EV-MLDSA-faf2ec`** (strength `preliminary`, claim_tier `literature_survey`)
and **`DEC-20260805-0d59ff`** (`advance_with_filed_entries`), committed at
**`c37bb2c9d`**.

This is not an identifier remap under rule 15: nothing is renamed, the real
records keep the ids they were filed under, and the queue's declaration of the
dead ids is left in place as the immutable record of what was planned.

### 2.4 The goal head

`ledger/goals/GOAL-MLDSA-001.yaml` still directed a reader to BATCH-001 and to
`TASK-20260805-a1c3f9` — a task completed four days earlier — while three
committed decisions had moved the goal through `BATCH-66b482` and `BATCH-214d98`
and left it deferred. Reconciled against the committed decision order:

| decision | commit time | batch | decision | evidence |
|---|---|---|---|---|
| DEC-20260805-0d59ff | 17:51:55 | BATCH-001 | advance_with_filed_entries | EV-MLDSA-faf2ec |
| DEC-20260805-4843d6 | 18:22:31 | BATCH-66b482 | advance_ideas_with_screening | none |
| DEC-20260805-ae4a96 | 19:52:08 | BATCH-214d98 | refine | EV-MLDSA-56e35b |
| DEC-20260805-64abe7 | 19:55:15 | BATCH-214d98 | advance_lane_b_coverage_determined | EV-MLDSA-32d752 |
| **DEC-20260805-79d745** | **20:03:31** | **BATCH-214d98** | **defer_lane_a_pdf_access_blocked** | none |

- `current_batch_id`: `BATCH-001` → `BATCH-214d98`
- `latest_verified_commit`: `null` → `7ef705ca51c5861a14461085967413209a7934da`
  (full sha per F11; see §2.7)
- `dispatch_queue_path`: → `null`, **not** a BATCH-214d98 path — see §3.3
- `next_action`: replaced by exactly one action derived from
  `DEC-20260805-79d745`, with the prior text preserved under
  `next_action_superseded` (now a list, so the 2026-08-05 entry survives
  verbatim alongside the new one). Nothing was overwritten.
- `updated_at`: `2026-08-09`

`status`, `active_hypothesis_ids`, `completion_criteria`, and `campaign_budget`
are untouched, and **no completion criterion is claimed met**.

### 2.5 An outstanding promotion, checked rather than assumed

`DEC-20260805-64abe7` scheduled a KN-FIND promotion ("Dilithium/ML-DSA formal
proof boundary excludes physical fault adversaries") and left it unfulfilled at
that decision. **Verified against the corpus in this session: it is no longer
outstanding.** `knowledge/findings/KN-FIND-720727.md` exists with exactly that
finding (`claim_status: supported_scoped`, `source_decisions:
[DEC-20260805-64abe7, DEC-20260805-79d745]`), and `DEC-20260805-79d745` records
it under `knowledge_promotion.promoted`. The gap `64abe7` named was closed by
the later decision in the same batch. No pending promotion is carried forward on
that account, and none is invented.

### 2.6 The `EV-MLDSA-faf2ec` snapshot-commit question — RESOLVED, no supersession

`EV-MLDSA-faf2ec` records `snapshot_commit:
8242344ce106e324e3f42e5b163061a251b7e9f9`, which is not the BATCH-001 snapshot
commit `f44ffbad97856fc9170f89ce8684639427f1e1be` used throughout this memo.
The first pass of this reconciliation refused to guess at that and filed it as
unreconciled. Three further verified facts then resolved it:

- **F8** — `8242344ce106e324e3f42e5b163061a251b7e9f9` **exists** in this
  repository's object database (`git cat-file -t` returns `commit`) but is
  **unreachable from any ref**: `git branch -a --contains` returns empty and it
  appears in no `git log --all`. It is a dangling object.
- **F9** — it is the **same snapshot act** as `f44ffbad9`, made on the working
  branch before integration. `8242344ce` has parent
  `8aca58a23644b2be4ebdd7a2d357957da26ae4fc`; `f44ffbad9` has parent
  `1245602e1040f3dfcfea556fc52d0db2a0becb6a`. Identical author
  ("Dispatch Test"), identical author date `2026-08-05 17:38:44 -0700`,
  identical commit message, identical 6-file change set. **Only the parent
  differs.**
- **F10** — all five declared producer artifacts are **byte-identical at
  `8242344ce` and at `f44ffbad9`** (per-path sha256 compared pairwise, all five
  IDENTICAL), matching the five hashes already recorded in §0 and in
  `DEC-20260809-333a4c`.

**Conclusion.** The recorded sha is **not** a transcription error and **not**
evidence of a second, divergent snapshot. The evidence record captured the
**branch-side** sha, which became unreachable when the branch was integrated —
the exact failure mode CLAUDE.md's Concurrency section documents, and the exact
reason `research_dispatch.py` binds to **content first**, treating commit
reachability as advisory while a content mismatch stays fatal. Under that rule
the archive is **content-verified**: the sha is unreachable, the bytes are
identical, the binding holds. **No superseding record is warranted and
`EV-MLDSA-faf2ec` is left unedited** (as it must be — it is immutable).

Two boundaries, neither of which weakens that. "Same snapshot act on a
pre-integration branch" is a reading of five agreements (author, author date,
message, change set, content) against one difference (parent); it is the only
reading they support, but it is a reading rather than a direct observation. And
a dangling object can be garbage-collected at any time — which is precisely why
the **content** binding, not the sha, is what carries the archive.

This resolution says nothing about the separate `d47e12` / `c60b84` archive-gate
failures. Those remain permanently unsatisfiable for their own reasons (a
receipt never written; record ids never minted) and neither task becomes
`completed`.

### 2.7 The abbreviated `latest_verified_commit` — RESOLVED

The first pass recorded `latest_verified_commit: 7ef705ca5` exactly as supplied
and filed the missing full sha as unreconciled rather than expanding it. **F11**
supplied it:

- Full sha `7ef705ca51c5861a14461085967413209a7934da`, parent
  `8eb145682dff3498e2dc4bb6ae0b8e7fe269f1fd`, message *"ledger: GOAL-MLDSA-001 —
  DEC-20260805-79d745 Lane A deferred (PDF blocked); KN-FIND-720727 Shin+Jendral
  outside formal model; pivot to GOAL-HAWK-001"*. It changed exactly three
  paths: `knowledge/findings/KN-FIND-720727.md`,
  `ledger/decisions/DEC-20260805-79d745.yaml`,
  `ledger/goals/GOAL-MLDSA-001.yaml`.

The goal record now carries the full sha, and its note records the parent,
message, and change set instead of the (now false) statement that the full form
was unavailable. **No other head field changed.**

F11 also **independently corroborates §2.5**: the same commit that carries the
last decision also carries `KN-FIND-720727.md`, so `DEC-20260805-64abe7`'s
scheduled promotion is confirmed **fulfilled by that archive**, not merely
present in the working tree. The corpus check and the git history agree.

## 3. Disposition table

| Task | Role | Terminal state | Why |
|---|---|---|---|
| TASK-20260805-d47e12 | coordinator (snapshot archive) | **invalid** | The commit happened and the freeze demonstrably held, but the completion gate is permanently unsatisfiable (missing `snapshot-receipt.json`, extra `receipt.yaml`, immutable commit). `invalid` = the *receipt* is invalid, not the freeze. Not `failed` (the act occurred and its product is durable); not `cancelled` (it was not withdrawn). |
| TASK-20260805-5b8a06 | validator | **completed** | Produced and committed its declared deliverable at its declared path in `aa1567c2f`; verdict `accept_with_qualifications`, carried on `EV-MLDSA-faf2ec` and cited by `DEC-20260805-0d59ff`. Not an archive task, so no receipt gate applies. No known defect. |
| TASK-20260805-9f2d71 | red-team | **completed** | The independent review really happened, was committed before the ledger archive, reached `pass_with_constraints`, and its three constraints were adjudicated as `DEC-20260805-0d59ff`'s `gate_1`/`gate_2`/`gate_3`. Declared-path mismatch recorded below, **not** repaired. |
| TASK-20260805-c60b84 | coordinator (ledger archive) | **invalid** | Same permanent unsatisfiability: its two declared records were never minted and the real ledger commit `c37bb2c9d` overlaps the declared path set in one path only. `invalid` rather than `cancelled` because the substantive work **was** performed and **is** durable — `EV-MLDSA-faf2ec` carries `recorded_by_task: TASK-20260805-c60b84`. Calling it `cancelled` would tell a reader BATCH-001 never got a ledger archive, which is false. |

Non-task items dispositioned in the same pass:

| Item | Disposition | Why |
|---|---|---|
| `EV-MLDSA-faf2ec.snapshot_commit` = `8242344ce` ≠ `f44ffbad9` | **Resolved — no supersession, record left unedited** | F8/F9/F10: `8242344ce` is a dangling but existing object, the same snapshot act on the pre-integration branch (identical author, date, message, change set; only the parent differs), with all five artifacts byte-identical to `f44ffbad9`. Content-first binding holds. §2.6. |
| `EV-MLDSA-7e91a4`, `DEC-20260805-3d5f82` | **Retired-unused, never reusable** | Declared in this queue, never minted, exist at no commit. §2.3. |
| `GOAL-MLDSA-001` head fields | **Reconciled to the last committed decision** | Four days and two batches stale. §2.4. |
| `DEC-20260805-64abe7`'s scheduled KN-FIND | **Not outstanding — verified, then corroborated** | `KN-FIND-720727` exists and `DEC-20260805-79d745` records it promoted (§2.5); F11 shows the commit carrying that decision also carries the finding file, so it was fulfilled by that archive (§2.7). |
| `latest_verified_commit` abbreviated to `7ef705ca5` | **Resolved — full sha recorded** | F11: `7ef705ca51c5861a14461085967413209a7934da`, parent `8eb14568…`, three changed paths. §2.7. |

### 3.1 The 9f2d71 declared-path mismatch (recorded, not repaired)

The queue declares
`reviews/TASK-20260805-9f2d71/red_team_report.md`. **No file of that name exists
at any commit.** The actual committed deliverables are
`reviews/TASK-20260805-9f2d71/red_team_report.yaml` and
`reviews/TASK-20260805-9f2d71/falsification_review.md`.

The declared `artifact_paths` are deliberately **not** edited to match. Fitting a
contract to its result converts a pre-declared commitment into a post-hoc
description and destroys the only mechanism by which a declared-versus-delivered
gap can ever be detected again. The mismatch stands as a finding about the task
card; the forward guidance is that a future queue must declare each review
role's exact filename **and extension**.

### 3.2 Why `completed` was not forced onto the archive tasks

Marking either archive `completed` would require writing `commit_sha`,
`parent_sha`, and a full `path_sha256` map into the queue's `archive` block —
i.e. asserting a receipt that was never produced, for commits made by other
sessions on 2026-08-05. The verified commit binding is instead recorded in
`DEC-20260809-333a4c` under `observed_commit_not_a_receipt`, a block that names
its own gate failures and is explicitly labelled as an observation of history
rather than a receipt. That keeps the facts durable and keeps the dispatcher
from ever reading them as a passing gate.

### 3.3 Why `dispatch_queue_path` is `null`

`BATCH-214d98` and `BATCH-66b482` have **no committed `dispatch_queue.json` and
no `batch.yaml`** — only task artifacts under
`coordination/goals/GOAL-MLDSA-001/batches/<batch>/tasks/`. The only queue file
this goal has is BATCH-001's, which this reconciliation retires as a description
of the head. Pointing the goal at a non-existent BATCH-214d98 queue would be a
fabricated path. `null` plus a note is the honest state; the next batch opened
for this goal must create its queue and set the field.

## 4. What was deliberately left unfixed, and why

This section carried two more items in the first pass, both since **resolved** by
verified facts supplied mid-task, and both recorded as resolved rather than
deleted so the memo shows what was open and what closed it: the
`EV-MLDSA-faf2ec` snapshot-commit question (closed by F8–F10, now §2.6) and the
missing full sha behind `latest_verified_commit` (closed by F11, now §2.7). The
four below were **not** verified by anyone and are **not** asserted resolved.

1. **Whether BATCH-66b482 / BATCH-214d98 ever had queues that went uncommitted.**
   Not determinable from the working tree and no git fact was supplied.
2. **The four corpus follow-ons from `TASK-20260807-dcfaee`** — the Kosuge &
   Xagawa (ePrint 2025/904) candidate, the Jendral/Mattsson/Dubrova FDTC 2024
   candidate, the `KN-LIT-4f3b80` title-identity concern, and the
   `KN-LIT-4dadec` `partial → read` upgrade. Still open, still tracked, and named
   in `DEC-20260809-333a4c`'s `next_actions` so none is silently dropped. They
   are corpus actions requiring their own producer → snapshot → independent
   review → ledger-archive chain, not queue bookkeeping, and they are **not**
   authorized by this decision.
3. **`DEC-20260805-0d59ff`'s `gate_2` ruling** and everything else in the
   committed decision chain. Not revisited, not superseded, not weakened.
4. **The task-level records of BATCH-66b482 and BATCH-214d98.** Not audited
   against their commits; only the decision order for those batches was used, and
   only as supplied.

## 5. What this task did NOT do

- Did not run any experiment, re-run any run, or re-review any artifact. Nothing
  here is empirical evidence of any kind.
- Did not run a single command. This session has no shell, no git, and no
  network; every sha and hash was copied verbatim from the dispatching session's
  audit.
- Did not write a snapshot or ledger receipt for any 2026-08-05 commit, and did
  not put any `commit_sha`, `parent_sha`, or `path_sha256` value into the queue.
- Did not edit or supersede any evidence record, decision record, hypothesis,
  experiment, or knowledge entry. `EV-MLDSA-faf2ec`, `EV-MLDSA-56e35b`,
  `EV-MLDSA-32d752`, all five BATCH-001 KN-LIT entries, `KN-FIND-720727`, and all
  five committed MLDSA decisions stand exactly as filed. In particular
  `EV-MLDSA-faf2ec` is left unedited **and needs no superseding record**: after
  F8–F10 its `snapshot_commit` is explained, not wrong (§2.6).
- Did not change `GOAL-MLDSA-001.status`, `active_hypothesis_ids`,
  `completion_criteria`, or `campaign_budget`, and claimed no completion
  criterion met.
- Did not change any hypothesis status or claim tier. `RQ-MLDSA-001`'s
  toy/until-certified ceiling stands.
- Did not retro-edit `TASK-20260805-9f2d71`'s declared `artifact_paths`.
- Did not mint any identifier beyond the two supplied
  (`DEC-20260809-333a4c`, `TASK-20260809-8c4759`); all further work is described
  by objective only, for a future dispatcher to mint with
  `tools/allocate_id.py` and `--check` before use — the `TASK-20260807-dcfaee`
  precedent.
- **Obtained no attestation and recorded none.** Nothing here is admissible
  toward goal closure.
- Asserted nothing about ML-DSA, FIPS 204, MLWE, MSIS, or SelfTargetMSIS
  security in either direction.
