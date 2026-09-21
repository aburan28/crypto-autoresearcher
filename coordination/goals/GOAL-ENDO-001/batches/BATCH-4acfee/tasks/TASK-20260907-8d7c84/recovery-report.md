# Recovery report — TASK-20260907-8d7c84

Custody/schema preservation task only. Zero scientific runs, zero experiment,
goal, or hypothesis status changes were made or attempted by this task.

## Session / model provenance

- Runtime: Claude Code (Claude Agent SDK), role `executor`.
- Requested policy (per handoff `inference` block): `executor-implementation`,
  `reasoning_effort: null` in the handoff (per `.claude/agents/executor.md`
  frontmatter this maps to `effort: medium` under
  `orchestration/model-policies.yaml`).
- Model: this session is the `Sonnet 5` model (model id `claude-sonnet-5`) as
  identified in the runtime system context. I have not independently verified
  this against a backend API response; I am reporting the identity the
  runtime itself supplies and am not fabricating any separate "verification"
  step or credential check. `fallback_used`: not applicable — no fallback or
  degradation occurred; `AUTORESEARCH_POLICY` / `AUTORESEARCH_BACKEND` were
  not explicitly re-resolved via `orchestration/adapter` in this task (no run
  manifest is produced by this task, since `experiment_runs_authorized: 0`
  and no `harness/runner.py` invocation occurred).
- Working tree HEAD at task start: `eee9ec41f02b045a893fe166da9e621b71256d8f`
  (`git log -1`, committed 2026-09-08 00:02:21 +0000). The tree had pre-existing
  unstaged modifications to `.github/workflows/claude-pr-review.yml` and
  `.github/workflows/claude.yml` at task start, made by prior work in this
  worktree, not by this task; this task did not touch those files.
- No `git checkout`, `git reset`, or any write to Git history was performed.
  All historical bytes were recovered exclusively via `git show <rev>:<path>`
  (a read-only object read), exactly as authorized for the revisions and
  paths named in `source-git-evidence.json`.

## What was recovered, and from where

### 1. Ledger-archive commit `fb11e4c6b1b87a8b3ee012507e4fb2c985f44345`

Verified with `git cat-file -t fb11e4c6b1b87a8b3ee012507e4fb2c985f44345` (returns
`commit`) and `git log -1 --format='%H|%P|%s'`. Both the commit and its declared
parent `9abd9cd20d06c601711fbd1187a98ccdd8e89126` exist and are reachable in
this clone.

Full commit message (`git show -s --format='%B'`), reproduced exactly:

```
archive(TASK-20260830-20a761): ledger REVISE disposition for GOAL-ENDO-001/BATCH-bde652 (EV-JINV-a50d47, DEC-20260830-93c01b, CORR-20260830-778068)
```

This matches `source-git-evidence.json`'s recorded `commit.text` byte-for-byte
(sha, parent-sha, subject line, trailing blank line). The message names
`EV-JINV-a50d47`, `DEC-20260830-93c01b`, and `CORR-20260830-778068` but **never**
`EXP-JINV-bd141d`, `TASK-20260830-3ebb0b`, or `TASK-20260830-4213a6` — confirming
the omission documented in `intake.md`'s "Frozen first defect" line and in
`BATCH-4acfee`'s `objective`, even though the archive's own `record_ids` and
`source_task_ids` (in `source-git-evidence.json`) cite all three of those
IDs. This omission is preserved, not corrected — this task does not amend the
old commit or its message.

All ten files declared under this commit's `path_sha256` in
`source-git-evidence.json` were recovered with `git show fb11e4c6...:<path>`
and their SHA-256 hashes match the declared hashes exactly (10/10 match, 0
mismatches):

- `ledger/evidence/EV-JINV-a50d47.yaml`
- `ledger/decisions/DEC-20260830-93c01b.yaml`
- `ledger/goals/GOAL-ENDO-001/checkpoints/BATCH-bde652.yaml`
- `ledger/goals/GOAL-ENDO-001/goal.yaml`
- `ledger/corrections/CORR-20260830-778068.yaml`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/archives/TASK-20260830-20a761/ledger-receipt.json`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/reviews/TASK-20260830-3ebb0b/validation-report.yaml`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/reviews/TASK-20260830-3ebb0b/runtime-session-receipt.json`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/reviews/TASK-20260830-4213a6/red-team-report.yaml`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/reviews/TASK-20260830-4213a6/runtime-session-receipt.json`

This is exactly the "ten matching files from fb11e4c6b1b87a8b3ee012507e4fb2c985f44345"
named in `intake.md`.

### 2. Snapshot-archive commit `691684e68ae6b7c936a01ea29248d608d6b5d72d`

Also named in `source-git-evidence.json` (task `TASK-20260830-e7db0d`) and
covered by the handoff's instruction to "include every historical AND current
archive artifact named in intake.md/source-git-evidence.json". Verified with
`git cat-file -t` (both commit and its declared parent
`00d8cf9c20667e837dabb39590e50c32fa591b60` resolve to `commit`), and the full
commit message matches `source-git-evidence.json`'s recorded text exactly:

```
archive(TASK-20260830-e7db0d): snapshot sixth-generation host-binding repair package (TASK-20260830-31b79c, GOAL-ENDO-001/BATCH-bde652, DEC-20260830-a575a3)
```

All seven declared files were recovered via `git show 691684e6...:<path>` and
all seven SHA-256 hashes match declared values exactly (7/7 match, 0
mismatches):

- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/repair-package-v6.yaml`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/emit_host_binding_v2.sh`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/emit_procedure_v2.md`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/demo-receipt-v2.json`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/stop-control-report-v6.yaml`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/tasks/TASK-20260830-31b79c/runtime-session-receipt.json`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/archives/TASK-20260830-e7db0d/snapshot-receipt.json`

### 3. Original dispatch queue

`coordination/goals/GOAL-ENDO-001/batches/BATCH-4acfee/original-dispatch-queue.json`
is byte-identical (`sha256sum`, both `d3b07105f3c109de5b515cd94a8c7c86445417b9560c5aff276d0d67b9a976b8`)
to both:
- the declared "Original SHA256" in `intake.md`, and
- the live current file `coordination/goals/GOAL-ENDO-001/batches/BATCH-bde652/dispatch_queue.json`.

`diff` between the two files reports no differences. Both are stored in the
preservation package (as the `original_dispatch_queue` group entry).

### 4. Current counterparts

For every one of the 17 historical paths above, the current working-tree
file at the same path was also read and hashed (present in the repository
now; the `path_hashes` recorded in `source-git-evidence.json` name exactly
these paths). 16 of 17 are byte-identical to their historical (recovered)
content. One differs:

- `ledger/goals/GOAL-ENDO-001/goal.yaml` — current SHA-256
  `49b571018244e2fce6ce9b378203faa340c996c855d56933339fa2253e1a2206`
  differs from the historical (commit `fb11e4c6...`) SHA-256
  `d5641a45cd4c423a452d5850ea21f56f9fc50c4d9dba3d491a5a581f37f9c336`.
  `diff` shows the current file:
  - repoints `current_batch_id` from `BATCH-bde652` to `BATCH-4acfee` and
    `dispatch_queue_path` likewise;
  - replaces the top-level `next_action` with a short pointer to this
    recovery task (`TASK-20260907-8d7c84` under `DEC-20260907-46aa8f`);
  - **additively** appends an `integrity_recovery_20260907` block that
    reproduces the entire historical `next_action` text verbatim under
    `prior_selection.next_action` (word-for-word match against the
    recovered commit content, confirmed by direct comparison), together
    with `historical_queue_sha256: d3b07105f3c109de5b515cd94a8c7c86445417b9560c5aff276d0d67b9a976b8`
    (matching item 3 above) and an explicit
    `scope: New recovery tasks own the prior queue impediment; historical
    archive validity and substantive reviews are not certified by selecting
    this queue.`;
  - leaves the top-level `status: active` field unchanged in both the
    historical and current versions — no goal-status transition occurred.

  This is reported as an observed content difference only; this task takes
  no position on whether that edit was well-formed or sufficient — that is
  outside this task's scope (custody/schema recovery, not review).

## Independent cross-check performed

- Recomputed every SHA-256 with a second, independent read path
  (`hashlib.sha256` over bytes returned by `git show`, not by trusting any
  value already recorded in `source-git-evidence.json` or elsewhere) and
  compared against the declared values field-by-field. 17/17 declared
  hashes matched (10 ledger-archive files + 7 snapshot-archive files); 0
  mismatches.
- Deliberate bad-hash/path-map rejection control: none of the 17 recomputed
  hashes were forced or copied from the declared values — each was computed
  independently from the recovered bytes before comparison, so a mismatch
  would have been visible had one existed (as designed, none did). No
  hash was retargeted, no path was remapped, and no historical file content
  was altered to make a check pass.
- Commit and parent SHAs for both cited commits were confirmed to exist as
  `commit` objects in this clone (`git cat-file -t`), and their exact commit
  messages were independently re-read from the object store and diffed
  character-for-character against the `commit.text` fields recorded in
  `source-git-evidence.json`.

## Unresolved / missing items

None. All 18 declared artifacts (10 ledger-archive files, 7 snapshot-archive
files, 1 original dispatch queue file) were fully recovered, all commits and
parents named in `source-git-evidence.json` resolved successfully in this
clone, and every declared SHA-256 hash matched the independently recomputed
hash of the recovered bytes. No source object was unavailable; no revision
was unreachable; no path produced a Git error. There is therefore no
"stop the affected recovery step" case to report for this task.

The one content difference identified (`ledger/goals/GOAL-ENDO-001/goal.yaml`,
item 4 above) is a **measured difference between historical commit content
and current working-tree content**, not a missing- or unrecoverable-object
condition; both versions are fully captured (base64, losslessly) in
`preservation-package.json`.

## Deliverables

- `coordination/goals/GOAL-ENDO-001/batches/BATCH-4acfee/tasks/TASK-20260907-8d7c84/preservation-package.json`
  — 18 entries, each with source commit/parent, recovery command, recovered
  bytes (base64), recovered SHA-256, declared SHA-256 from
  `source-git-evidence.json` (or `intake.md` for the original queue file),
  match flag, current-counterpart bytes (base64), current-counterpart
  SHA-256, and a mapping/content-difference note. Top-level `commits_verified`
  block records both commits' message text and the confirmed ID omission.
  Top-level `summary` records `recovered_file_count: 18`,
  `unresolved_file_count: 0`, `hash_mismatch_count: 0`, and the one
  current-vs-historical content difference (`ledger/goals/GOAL-ENDO-001/goal.yaml`).
- This file.

## Completion-gate self-check

- All original source bytes remain unchanged: yes — this task only read
  (`git show`) and wrote under its own exclusive `write_scope`; it never
  wrote to any path outside
  `coordination/goals/GOAL-ENDO-001/batches/BATCH-4acfee/tasks/TASK-20260907-8d7c84/`.
- Original failures/omissions retained: yes — the commit-message ID omission
  is documented, not corrected; the old commit was not amended.
- Measured hashes and per-path provenance reported for all paths: yes, with
  zero impediments.
- No experiment run, scientific transition, historical completion
  normalization, or independent-review fabrication occurred: confirmed — this
  task performed no experiment, changed no ledger/goal/hypothesis status, and
  fabricated no review or model-verification claim.
