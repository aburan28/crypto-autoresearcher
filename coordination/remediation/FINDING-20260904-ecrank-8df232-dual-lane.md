# FINDING-20260904-ecrank-8df232-dual-lane

**Superseding record.** Immutable records are never overwritten (AGENTS.md
rule 2). Two sessions recorded conflicting terminal states for the same task in
`coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/dispatch_queue.json`.
Neither session's record is deleted. This record states both facts and names
the state the queue now carries and why.

- **Goal:** `GOAL-ECRANK-002`
- **Batch:** `BATCH-e0caa5`
- **Task:** `TASK-20260822-8df232` — coset-structure measurement
- **Recorded at:** 2026-09-04, while merging `origin/main` into
  `claude/degree-regularity-polynomial-systems-pssesi`
- **Merge base:** `0d62bb5d874a272da6b2e4e15dbb22111e66d95d`

## What happened

The task was claimed and run twice, in two lanes, by two sessions that could
not see each other's terminal state at the time they wrote it. Both runs are
real and both records are retained.

### Run 1 — epoch 1, FAILED

| field | value |
| --- | --- |
| lane / branch | `harness-ecdlp-20260904` |
| owner | `coordinator-ecrank-1` |
| worktree | `/Volumes/SSD990/crypto-autoresearcher` |
| claimed | `2026-09-04T17:17:35Z` |
| released | `2026-09-04T17:38:31Z`, outcome `failed` |
| claim records | `claims/TASK-20260822-8df232.1.claim.json`, `.1.release.json` |

That session's own note, preserved verbatim in the queue under
`prior_completion_note`:

> FAILED incomplete (2026-09-04, session died at turn 62 leaving the profiling
> run orphaned; no deliverables; scaffolding src/ committed at 40507a154).
> Released failed, epoch 1. RE-DISPATCH PENDING.

Its scaffolding is retained in the merged tree and was not touched:
`tasks/TASK-20260822-8df232/src/_bench.py`, `src/_probe_cypari2.py`,
`src/twist_family_local.py`, and `runs/RUN-8df232-001-profile-n7/{stdout,stderr}.log`.

**This failure is an infrastructure failure — a session dying — and is not
negative mathematical evidence** (AGENTS.md rule 3). It says nothing about the
coset-structure hypothesis.

### Run 2 — epoch 2, COMPLETED

| field | value |
| --- | --- |
| lane / branch | `claude/degree-regularity-polynomial-systems-pssesi` |
| owner | `coordinator-aes-1` |
| claimed | `2026-09-04T18:59:33Z` (claim record carries `supersedes: {epoch: 1, status: released}`) |
| released | `2026-09-04T19:17:09Z`, outcome `completed` |
| claim records | `claims/TASK-20260822-8df232.2.claim.json`, `.2.release.json` |

Run 2 was a legitimate re-dispatch, not a collision: it acquired epoch 2 only
after epoch 1 had been released `failed`, and its claim record names that
supersession explicitly. It is the "RE-DISPATCH PENDING" the run 1 note asked
for; the two sessions simply never saw each other's queue write.

Deliverables, snapshot-archived at `2938068a3` (`binding_mode: content_first`),
digests recomputed from the committed blobs:

| path | sha256 |
| --- | --- |
| `tasks/TASK-20260822-8df232/coset_structure.json` | `a6eda120b352ce3d720e00a26e566a9eca3349915f11fb1f8f5819d87b61cd85` |
| `tasks/TASK-20260822-8df232/report.md` | `168e84abe3abf1783bc1ddf02f7cab901d094003a83438bbe0e970b01d955dab` |
| `tasks/TASK-20260822-8df232/src/coset_structure.py` | `6a08546ce897d1f578c1e26795d2f9fb0866468db9b86dcc7d26de9def3593b1` |

All three were re-verified byte-identical on both branches and against the
`TASK-20260822-e7c486` archive receipt after the merge.

Reviewed independently by `TASK-20260822-0de988` (validator) and
`TASK-20260822-de2fa2` (red team); carried into `EV-ECRANK-6695dc` and
`DEC-20260822-7d356e`, ledger-archived at `caa831835`.

## Resolution

The queue now carries `state: completed` for `TASK-20260822-8df232`, because
that is the outcome with archived, independently reviewed, digest-verified
deliverables. The failed record is not erased: `prior_state: failed`,
`prior_completion_note` (the other session's note verbatim), and a
`claim_epochs` array giving both epochs with their lanes, owners and timestamps
now sit on the task, and both pairs of claim/release files remain in
`claims/`. The task points at this record via `superseded_by`.

`TASK-20260822-8df232` must **not** be re-dispatched. Its measurement exists,
is archived, and has been reviewed.

## Also settled in the same merge

- **`TASK-20260822-a7a9e8` ran once, not twice.** Only `harness-ecdlp-20260904`
  ever claimed it (epoch 1, `17:17:42Z` → `completed 17:38:38Z`). Its
  deliverables date to `0d75a655f` (2026-08-22) and are byte-identical on both
  branches; this branch archived those same bytes without re-running the task.
  `origin/main`'s `completed` state and note were taken unchanged.
- **`TASK-20260822-0de988` and `TASK-20260822-de2fa2` are now `completed`.**
  Both released `completed` (20:22:16Z and 20:06:27Z) and both deliverables are
  digest-bound in the `TASK-20260822-0e9c74` ledger archive at `caa831835`, but
  this branch had only unblocked them, never marked them terminal. Left
  `queued`, the dispatcher would have listed two already-archived reviews as
  Ready Tasks — the same duplicate-dispatch failure that produced this finding.
- **`TASK-20260822-e7c486` and `TASK-20260822-0e9c74`** keep this branch's
  `completed` state and full archive blocks (`commit_sha`, `parent_sha`,
  `path_sha256`, `binding_mode: content_first`).

`BATCH-e0caa5` is now terminal in all six tasks.

## What this does not claim

Nothing here is evidence about elliptic-curve rank, coset structure, or any
hypothesis. It is a record-integrity resolution. The mathematical content of
run 2 stands or falls on `EV-ECRANK-6695dc` and `DEC-20260822-7d356e` and their
scope, unchanged by this record.
