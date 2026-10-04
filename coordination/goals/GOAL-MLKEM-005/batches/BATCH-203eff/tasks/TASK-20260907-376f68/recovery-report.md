# Recovery report — TASK-20260907-376f68

Goal: GOAL-MLKEM-005. Batch: BATCH-203eff. Nature: CUSTODY/PRESERVATION only.
Zero scientific runs performed. Zero status changes of any kind performed.
The current goal head's `next_action` (custody/schema recovery text pointing
back at the zero-lattice instrument repair) was **not** touched, restored
over, or reinterpreted by this task.

## Method

All historical bytes were recovered with read-only Git object inspection:
`git show <revision>:<path>`. No `git checkout`, no `git reset`, no working-tree
mutation of any historical object was performed. The recovery revision named
by the task and by `source-git-evidence.json` is:

```
93c6be1becda0a25254f7086502a2256e8cbbfe0
```

Verified reachable in this clone (`git cat-file -e` succeeded; `git log -1`
resolved it to commit subject `ledger-archive(TASK-20260826-70d800): bind
BATCH-762807's close -- EV-MLKEM-09d715, DEC-20260826-9d7d93`, parent
`cfcbdccfa7d1396b65954b409c81617181e689e9`, matching `source-git-evidence.json`
exactly).

Repo state at recovery time: branch `claude/run-experiments-uq9jiv`, HEAD
`eee9ec41f02b045a893fe166da9e621b71256d8f`. (Working tree had two unrelated
pre-existing modified files, `.github/workflows/claude-pr-review.yml` and
`.github/workflows/claude.yml`, not touched by this task and unrelated to
GOAL-MLKEM-005.)

## Goal-head hash verification — the task's headline requirement

Recovered `ledger/goals/GOAL-MLKEM-005.yaml` at commit `93c6be1b...` via
`git show 93c6be1becda0a25254f7086502a2256e8cbbfe0:ledger/goals/GOAL-MLKEM-005.yaml`.

- Recovered bytes sha256: `181b8ac53dbd575e35b59bbea1e67072e25c4f30eb36ab977ed7925269dfed9d`
- Expected sha256 (from the task card and `source-git-evidence.json`
  `path_sha256` entry for this path under the `TASK-20260826-70d800` archive):
  `181b8ac53dbd575e35b59bbea1e67072e25c4f30eb36ab977ed7925269dfed9d`
- **Result: MATCH — confirmed, not assumed.** The recovered goal-head blob's
  sha256 is bit-for-bit identical to the expected hash.

This directly resolves the discrepancy flagged in `intake.md`'s "Frozen first
defect" line ("archive task TASK-20260826-70d800 content hash mismatch for
ledger/goals/GOAL-MLKEM-005.yaml: expected 181b8ac5..., observed
3a057682..."): the *historical committed blob at the cited revision* is
exactly the expected 181b8ac5... bytes. Whatever produced the `3a057682...`
observation cited in `intake.md` was a **different** copy of the file at a
**different** point in time than either the commit `93c6be1b` blob or the
current live head (see below) — this recovery neither confirms nor refutes
what produced that particular `3a057682...` reading; it establishes only
that the two byte-strings this task was asked to compare (recovered-historical
vs. expected) are identical.

## Per-path provenance

All eight paths bound by the `TASK-20260826-70d800` ledger archive
(`source-git-evidence.json`, `commit_sha: 93c6be1becda0a25254f7086502a2256e8cbbfe0`)
were recovered by `git show 93c6be1becda0a25254f7086502a2256e8cbbfe0:<path>`
and their sha256 checked against the `path_sha256` map in that same evidence
file. All eight matched exactly:

| path | expected sha256 | recovered sha256 | match |
|---|---|---|---|
| `coordination/.../archives/TASK-20260826-70d800/ledger-receipt.json` | `3d499ff6...f93e00` | same | yes |
| `coordination/.../reviews/TASK-20260826-5ee48b/attestation.yaml` | `f92b6224...a96bc` | same | yes |
| `coordination/.../reviews/TASK-20260826-5ee48b/red-team-report.yaml` | `69a342e1...4726cc` | same | yes |
| `coordination/.../reviews/TASK-20260826-9605ae/attestation.yaml` | `48e2416e...50b2b` | same | yes |
| `coordination/.../reviews/TASK-20260826-9605ae/validation-report.yaml` | `aadcfbdc...e7615` | same | yes |
| `ledger/decisions/DEC-20260826-9d7d93.yaml` | `8c9dd6ab...d2d68` | same | yes |
| `ledger/evidence/EV-MLKEM-09d715.yaml` | `2f971099...2acf7f` | same | yes |
| `ledger/goals/GOAL-MLKEM-005.yaml` | `181b8ac5...9dfed9d` | same | yes |

(Full paths and full hashes are recorded in
`preservation-package.json`, one entry per row, each carrying `source_revision`,
`path`, `sha256`, `bytes_length`, and the base64 payload; abbreviated here for
readability.)

## Current-state counterparts and mapping differences

For every one of the eight recovered paths, the current on-disk copy at the
present repo HEAD (`eee9ec41f...`) was also read and hashed, and compared
byte-for-byte against the historical recovery:

- **Seven of eight paths are byte-identical, historical vs. current**: the
  `TASK-20260826-70d800` ledger-receipt, both reviewers' attestations, the
  red-team report, the validation report, `DEC-20260826-9d7d93.yaml`, and
  `EV-MLKEM-09d715.yaml` are all unchanged in the working tree relative to
  the committed historical blob. No drift, no re-key, no silent edit.

- **The goal head (`ledger/goals/GOAL-MLKEM-005.yaml`) differs, current vs.
  historical**, as expected of a living checkpoint record that has since
  accumulated further batches/decisions:
  - `current_batch_id` moved from `BATCH-762807` to `"BATCH-203eff"`.
  - `dispatch_queue_path` moved from the `BATCH-762807` queue to the
    `BATCH-203eff` queue.
  - `next_action` moved from the verbatim "ONE ACTION, SET BY
    DEC-20260826-9d7d93 ..." zero-lattice-instrument-repair successor-pass
    text (items a–e, D1..D6 successor residuals) to the present custody-task
    text: "Execute zero-scientific-run custody/schema recovery
    TASK-20260907-376f68 under DEC-20260907-46aa8f; snapshot and independent
    custody review precede administrative archival. Resume the preserved
    prior action only after its specific impediments clear."
  - A new block, `standing_directive_always_run_20260828` and
    `budget_amendments` (`BUDGET-AMEND-20260828-6716eb`, citing
    `DEC-20260828-6716eb`, "Fund every goal"), was inserted between the
    historical commit and the present head.
  - `updated_at` moved past `2026-08-26`.
  - Current live-head sha256: `4445bbe76cd1b5868b06ebe605e88dbb93350953c36eb32aa9f71a2fcf17cf15`
    (measured; recorded in `preservation-package.json` as
    `current_counterpart.sha256` for this entry). This is **not** the
    `3a057682...` value `intake.md` cites as the "observed" hash at the time
    of the original dispatch failure — i.e. the goal head has moved at least
    twice since the historical commit: once to the `3a057682...` state
    `intake.md` recorded, and again to the present `4445bbe7...` state. Both
    of those later states are outside the scope of `source-git-evidence.json`
    (which only names the `93c6be1b` / `181b8ac5...` historical pair), so
    this report states the fact of the discrepancy without attempting to
    locate or recover the `3a057682...` intermediate state — that would
    require a git revision this task was not given and was not authorized to
    search for.

  This goal-head divergence is **intrinsic evolution of a living record
  across multiple later batches and decisions**, not a custody defect
  introduced by this recovery task, and this task did not and must not
  restore the historical bytes over the live head. The current head's
  `next_action` is left exactly as found.

## Original dispatch queue

`coordination/goals/GOAL-MLKEM-005/batches/BATCH-203eff/original-dispatch-queue.json`
(the committed copy of the pre-recovery `BATCH-762807` queue, held in the
present custody batch) was read directly from the working tree (this is a
live-repo file, not a `git show` recovery of a named historical revision) and
hashed:

- sha256: `f8d5146c90b200da8a347206d13d0c3744fb644667fea00c9a8eebf7b95da7f9`
- This matches `intake.md`'s stated "Original SHA256:
  f8d5146c90b200da8a347206d13d0c3744fb644667fea00c9a8eebf7b95da7f9" exactly.
- It is also byte-identical to the *current, live*
  `coordination/goals/GOAL-MLKEM-005/batches/BATCH-762807/dispatch_queue.json`
  (same sha256), so the live `BATCH-762807` queue file itself has not drifted
  from the copy preserved for this custody task.

Both files' full bytes (base64) are included in
`preservation-package.json` under `original_dispatch_queue_entry`.

## What was recovered

- All 8 paths named in `source-git-evidence.json` under the
  `TASK-20260826-70d800` ledger archive at commit `93c6be1becda0a25254f7086502a2256e8cbbfe0`,
  bytes-for-bytes, base64-encoded, each hash-verified against the evidence
  file's declared `path_sha256`.
- All 8 current-state counterparts of those same paths, bytes-for-bytes,
  base64-encoded, hash-compared against the historical recovery.
- The current `BATCH-203eff/original-dispatch-queue.json` and current
  `BATCH-762807/dispatch_queue.json`, bytes-for-bytes, base64-encoded, hash
  checked against `intake.md`'s stated original hash.
- Independent confirmation that the base64 payloads in
  `preservation-package.json` round-trip to exactly the declared sha256 for
  every entry (verified programmatically after writing the package).

## What could NOT be recovered / unresolved scope

- **Nothing named in `source-git-evidence.json` was unavailable.** All eight
  declared paths at the declared revision resolved via `git show` on the
  first attempt; no bad revision, no missing object, no stop condition was
  triggered.
- The intermediate goal-head state that `intake.md` describes as producing
  the "observed 3a057682..." hash was **not** recovered, because no git
  revision for that intermediate state was named in
  `source-git-evidence.json` or `intake.md` — only the `93c6be1b` historical
  commit and the (implicit) live head were named/available. Locating that
  intermediate state would require searching git history for it, which this
  task's authorization ("read-only Git object inspection... for exact source
  revisions and paths named in source-git-evidence.json") does not extend to.
  This is recorded as an infrastructure/scope fact, not as evidence about
  anything scientific.
- The other 12 `staged_not_in_binding_set` files disclosed in the
  `TASK-20260826-70d800` ledger-receipt commit message (reviewer probe trees,
  raw kill-matrix journals, `blind-rederivation.yaml`, etc.) were **not**
  in this task's `read_scope` or in `source-git-evidence.json`'s
  `path_sha256` map, and were therefore out of this task's declared recovery
  scope; they were not attempted and are not claimed as recovered.

## Model / session record

- Runtime: Claude Code (this session).
- Requested policy per the handoff: `executor-implementation`.
- Model: Claude Sonnet 5 (`claude-sonnet-5`), per this session's actual
  resolved model identity — no Bedrock backend was used, no fallback or
  degradation occurred, and no model verification beyond this stated
  identity is claimed.
- Session reference: `https://claude.ai/code/session_01NV1n82ki22i5u8Db7JPpWj`.

## Completion-gate self-check

- All original source bytes remain unchanged: verified — every historical
  byte was only *read* (`git show`), never written back over any path;
  original current-state files were only *read*, never modified.
- Every measured hash is reported with its per-path provenance (this report
  plus `preservation-package.json`); no unavailable-source impediment was
  encountered for any declared path.
- No experiment run, scientific transition, historical completion
  normalization, or independent-review fabrication occurred. No ledger
  record was written or modified by this task. No commit was made by this
  task.
