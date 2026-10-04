# Recovery report — TASK-20260907-57d38a

Custody/preservation task for GOAL-MD5-001 / BATCH-f1f479. **No experiment
was run, no hypothesis/goal/experiment status was changed.** This is a
metadata/custody reconstruction only, produced by read-only `git show
<rev>:<path>` object inspection plus on-disk reads of the current working
tree. No checkout, reset, commit, or historical edit was performed.

## Session / model disclosure

- Runtime: Claude Code (this session), role `executor`, policy
  `executor-implementation` per the handoff's `inference` block
  (`reasoning_effort: null`, `fallback_allowed: false`,
  `degraded_allowed: false`). No fallback or degradation occurred; no
  Bedrock backend was used. This report records only what this session
  itself did — no separate model-verification probe was run, and none is
  claimed.
- Repo state at generation: `HEAD = 51dbb8ed15fb0ff5b4a2b5b19c3ab1158700ba6f`
  on branch `claude/run-experiments-uq9jiv`. Working tree had pre-existing
  unrelated modifications/untracked files from other goals (`git status`
  showed changes in `.github/workflows/*` and untracked task directories
  under `GOAL-ENDO-001`, `GOAL-MCE-001`, `GOAL-MLKEM-005`, `GOAL-SIG-001`);
  none of those paths were read or touched by this task, and none intersect
  the file set below.
- Generated at: 2026-09-08T00:12:13Z (UTC, per this session's clock at the
  time the script ran).

## Method

For every path in the task's `read_scope`/`intake.md`/`source-git-evidence.json`
set that names a concrete file (i.e. excluding bare directory entries, which
were read for orientation only), this task:

1. Ran `git log --format=%H|%aI -- <path>` over the full, non-shallow local
   clone (`git rev-parse --is-shallow-repository` → `false`) to enumerate
   every commit that ever touched the path.
2. Read the **oldest** (creation) and **newest** (latest-committed) commit's
   blob for that path via `git show <commit>:<path>` — read-only Git object
   inspection, no working-tree mutation.
3. Read the **current on-disk bytes** directly and compared their sha256
   against the newest commit's blob sha256, to catch any uncommitted drift
   for that path (`dirty_vs_newest`). None was found: **zero** paths in
   scope have working-tree bytes that differ from their latest committed
   blob.
4. Recorded, per path, in `preservation-package.json`: `source_revision`
   (oldest commit), `current_revision` (newest commit), both sha256 values,
   `identical_historical_and_current` (byte equality of oldest vs. newest
   blob), a `mapping_difference_note`, `current_base64` (always present),
   and `historical_base64` (present only when the oldest blob differs from
   the newest — to avoid duplicating identical bytes).

No path was hash-retargeted, ID-remapped, or bypassed. No control was
skipped. The one intentionally-attempted "bad hash/path-map" rejection
control (see Controls, below) was exercised in-session and discarded before
writing the package — the package itself contains no fabricated or
substituted hash.

## Verification of the three named historical revisions

- **Snapshot commit** `55e316276085f9645b0bb145862e82dc4a81c9de` — exists
  (`git cat-file -t` → `commit`); commit subject: `archive(TASK-20260822-b325fe):
  snapshot GOAL-MD5-001 BATCH-ebac02 phase-1 producer package
  (EXP-MDFIVE-b6-phase1, TASK-20260822-767bb1) for independent review`.
- **Its declared parent** `9b79ac28714089ebc4b6dcf08ef5c01cf7a34468` — exists
  and is confirmed as the exact first parent (`git rev-parse
  55e316276...^` returns `9b79ac287...`).
- **Boundary check**: `coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/
  tasks/TASK-20260822-767bb1/execution-report.yaml` and
  `harness/run_md4_seed_sweep.py` both **exist at the snapshot commit** and
  are **absent at its parent** — i.e. they were introduced exactly in this
  commit, consistent with the batch note that TASK-20260822-b325fe performed
  the isolated content-first snapshot of the phase-1 producer package. Both
  files' current on-disk bytes are byte-identical to their content at the
  snapshot commit (sha256 match; see `preservation-package.json` entries).
- The **post-commit receipt** `.../archives/TASK-20260822-b325fe/
  snapshot-receipt.json` lives in a **separate, later** commit
  `f1f07a7e5f31054479ede7b4d45fc9f71584b25c`, whose first parent is exactly
  the snapshot commit `55e316276...` — consistent with the batch-ebac02
  queue's own note ("content_first receipt ... commit f1f07a7e5"), i.e. the
  receipt was committed in a follow-up commit after the snapshot it binds.
- **DEC-20260822-d7c2d0**, **EV-MDFIVE-b0def7**, **EXP-MDFIVE-8f0fe3/
  specification.yaml** all exist on disk today and all trace to a single
  git commit `fde5cad892867b4eb2ae784da7d534839b091c85` (the batch's ledger
  close, per the batch-ebac02 queue note: "Records: DEC-20260822-d7c2d0
  (sentinels replaced), EV-MDFIVE-b0def7, EXP-MDFIVE-8f0fe3 ... compiled at
  close"). Current on-disk bytes are byte-identical to that commit's blobs
  (single-commit history, no drift).

## Frozen queue byte-identity (intake.md claim)

`intake.md` claims: `Original SHA256:
63c8213613428492835e99e1eb163490329f3b11e0cf9061059af2973b39ae31` for
`coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/dispatch_queue.json`.
Measured independently in this task:

- current `.../BATCH-ebac02/dispatch_queue.json` sha256 =
  `63c8213613428492835e99e1eb163490329f3b11e0cf9061059af2973b39ae31` — **matches**.
- the frozen copy already held at
  `.../BATCH-f1f479/original-dispatch-queue.json` sha256 = the same value —
  **matches** (byte-for-byte `diff` against the current BATCH-ebac02 queue
  is empty).

This queue's own git history has 5 commits touching the path (creation
commit `4bf5a0e1735...`, latest `8f9b3a5a82b...`); its content changed
across that history (e.g. `state_update_20260823` was appended after the
initial open), so `identical_historical_and_current` is `False` for this
path in the package — the **creation-time** bytes and the **current/final**
bytes are both preserved, distinctly, in `preservation-package.json`. The
"Original SHA256" cited in `intake.md` refers to the **current/final**
state of the queue (post all state-update appends), not its creation-time
state — both are captured so this distinction is auditable rather than
asserted.

## Preserved failed/partial review scopes (verified, not re-adjudicated)

- **TASK-20260822-87c429 (red-team, failed_infrastructure)**: its declared
  artifact path
  `coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/reviews/
  TASK-20260822-87c429/red-team-report.yaml` has **zero commits in git
  history and is absent from the current working tree**. This is the
  expected, historically-accurate state: the batch-ebac02 dispatch queue's
  own note for this task states the session "died on its final synthesis
  turn ... yielding an empty final message and therefore an empty
  task_result with no report file written." The genuine absence of this
  file is preserved as an infrastructure fact, not fabricated, not
  substituted with the resume task's report, and not treated as negative
  evidence about anything. It is listed under `unresolved_or_missing` in
  `preservation-package.json` with that exact reason.
  `ledger/handoffs/TASK-20260822-87c429.yaml` (the handoff envelope, as
  opposed to the report the run never produced) does exist and is captured
  byte-for-byte.
- **TASK-20260822-40389d (validator, partial — V1 incomplete)**: its
  `validation-report.yaml` exists, is captured byte-for-byte from its sole
  commit `fde5cad892867b4eb2ae784da7d534839b091c85`, and the batch note's
  characterization (V2/V3/V4 PASSED, V1 INCOMPLETE due to a glm-5.2
  run_command wire-format quirk, later fixed and cold-re-run by successor
  TASK-20260822-7f5ed3) is preserved verbatim in the source batch-ebac02
  queue capture — this task does not re-adjudicate or restate that finding
  as its own conclusion.
- **Successor TASK-20260822-7f5ed3** (`validation-report-v1.yaml`, scoped
  completion of joint V1 only) and **TASK-20260823-80125f** (red-team
  resume: `red-team-report.yaml`, `blind-rederivation.yaml`,
  `red_team_analysis.py`, `run-receipt.json`, `run-stdout.jsonl`) were all
  located, exist on disk, and are captured byte-for-byte from their single
  respective commits (`fde5cad892867b4eb2ae784da7d534839b091c85` and
  `b4d0c586e705a47de4f816c5c0a28a3052c029da`). Their content is preserved
  as-is; this task does not restate their verdicts as newly validated —
  those verdicts are exactly what the composing decision(s)
  (`DEC-20260822-d7c2d0`, `DEC-20260823-4c072b` — the latter referenced in
  the batch-ebac02 queue but **not** in this task's read_scope, so it was
  not independently opened here) already record.

## Controls exercised

- **Compare all original hashes before and after**: every entry's
  `current_sha256` was computed fresh from the on-disk bytes actually read
  in this session (not copied from any prior report), and compared against
  the git blob sha256 for the same path/commit.
- **Independent Git blob comparison**: content for every path came from
  `git show <commit>:<path>`, not from any cached index or working-tree
  copy claiming to represent history; the working-tree copy was compared
  against it, not substituted for it.
- **Intentional bad-hash/path-map rejection control**: before writing the
  final package, this session hand-computed one deliberately wrong sha256
  for a known file (`AGENTS.md`'s newest-commit content, with one hex digit
  flipped) and confirmed the mismatch against the measured value would be
  caught (obviously non-equal string comparison) rather than silently
  accepted; the wrong value was discarded and does not appear anywhere in
  the delivered package. This was a session-local check exercised to
  confirm the comparison logic distinguishes correct from incorrect hashes
  — it was not committed or persisted as an artifact, since persisting a
  deliberately wrong hash would itself violate "no fabricated hash."

## What could NOT be recovered

- `coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/reviews/
  TASK-20260822-87c429/red-team-report.yaml` — **genuinely never existed**
  (infrastructure failure during the original run; no git commit ever
  added it, and it is absent from the working tree today). This is not a
  gap in this recovery task's access — it is the accurate historical
  record of a run that produced no report file. No remedy is available or
  needed beyond what is already recorded in the batch-ebac02 queue's own
  note and in `ledger/handoffs/TASK-20260822-87c429.yaml`, both of which
  are captured in this package.
- `DEC-20260823-4c072b` (the round-completion composing decision named in
  the batch-ebac02 queue's `state_update_20260823` block) was **not** in
  this task's declared `read_scope` and was therefore not opened or
  captured here, even though it exists on disk
  (`ledger/decisions/DEC-20260823-4c072b.yaml` was not checked by this
  task). This is a scope boundary, not a missing-object impediment — the
  handoff's `read_scope` is authoritative for what this task reads, and
  widening it was not requested.
- No other named path (from `read_scope`, `intake.md`, or
  `source-git-evidence.json`) was found unavailable. All 42 other files
  resolved to at least one git commit and to current on-disk bytes with no
  drift between the latest commit and the working tree.

## Completion-gate self-check

- All original source bytes captured are byte-for-byte reproductions of
  either the working tree or a named git commit; none were altered.
- The one genuine historical failure (TASK-20260822-87c429's missing
  report) is retained as missing, not backfilled or reinterpreted.
- `preservation-package.json` reports measured sha256 values and per-path
  git provenance (`source_revision` / `current_revision`) for every
  resolved path, and an explicit `unresolved_or_missing` entry for the one
  unavailable path.
- No experiment was run (`maximum_runs: 0`, `experiment_runs_authorized: 0`
  in the handoff budget — none were used). No hypothesis, goal, or
  experiment status was changed by this task. No independent-review outcome
  was fabricated or re-adjudicated; existing review verdicts are quoted
  from their source records, not re-derived.

## Artifacts produced by this task

- `coordination/goals/GOAL-MD5-001/batches/BATCH-f1f479/tasks/TASK-20260907-57d38a/preservation-package.json`
- `coordination/goals/GOAL-MD5-001/batches/BATCH-f1f479/tasks/TASK-20260907-57d38a/recovery-report.md` (this file)

Both were written only under this task's declared `write_scope`
(`coordination/goals/GOAL-MD5-001/batches/BATCH-f1f479/tasks/
TASK-20260907-57d38a/`). Nothing was committed; per the handoff and
`agents/executor.md`, the Coordinator's snapshot task
(TASK-20260907-3a43da) is responsible for the archive commit.
