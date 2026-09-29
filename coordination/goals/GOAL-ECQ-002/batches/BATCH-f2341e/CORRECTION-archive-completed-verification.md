# CORRECTION: the dispatcher's `completed`-archive verification cannot pass under durability commits

Raised by: orchestrating session (Coordinator role), BATCH-f2341e of GOAL-ECQ-002.
Status: DEFECT RECORDED, NOT FIXED. No tooling was changed.

## What happened

After the ledger archive TASK-20260823-d26c06 landed, I marked both archive tasks
`completed` in `dispatch_queue.json` and populated their `archive` blocks, then ran
`tools/research_dispatch.py` as the post-commit verifier. It rejected the queue through
a chain of four successively deeper checks:

1. `path_sha256 contains paths outside its commit scope` — the hash set must be a
   subset of `archive.artifact_paths | sources' artifact_paths`. My hash set was a
   superset because the queue's declared `artifact_paths` (2 per producer, written
   before the work existed) never covered what the producers actually delivered.
   FIXED honestly by declaring the real artifacts: TASK-20260823-01d3d9 went 2 -> 125,
   TASK-20260823-07a54b went 2 -> 3 (adding analysis/redteam_controls.py, which the
   ledger archive independently required).
2. `requires archive.commit_sha` — supplied.
3. `path_sha256 must cover every archive and source artifact` — EXACT set equality,
   which additionally requires the archive's own `receipt.yaml`. Satisfied in the
   QUEUE (a structure separate from the receipt file), so no receipt contains its own
   hash and there is no circularity.
4. `commit must change exactly declared archive and source artifacts` — **UNSATISFIABLE
   HERE.** The check's model is that the archive commit itself introduces every declared
   artifact. In this batch it does not: the session Stop hook requires a clean tree at
   every turn, so the producers' artifacts were committed as durability commits BEFORE
   the archive ran, and the archive commit therefore changed only `receipt.yaml`.

## Why I did not force it

The only ways to satisfy check 4 are to rewrite history so the archive commit contains
everything — forbidden for pushed run records (AGENTS.md; CLAUDE.md "never rewrite
history over pushed run records") — or to shrink the declared artifact set until it
matches what the commit touched, which would bind LESS content and is the opposite of
what the check exists to guarantee. Neither is acceptable, so the check stays unsatisfied
and is reported rather than worked around.

## What I did instead, and what is actually guaranteed

The archive blocks in the queue were reverted to the pre-run shape GOAL-ECQ-001 used
(state `blocked`, empty `path_sha256`, null shas). That is the established repository
precedent: GOAL-ECQ-001 BATCH-7e06d3 never marked its archives `completed` either, so
this strict branch has, as far as this batch can tell, never been exercised on `main`.
The queue is a dispatch input; completion lives in the receipts and the ledger records.
With that shape the verifier passes and lists no ready tasks, so no finished archive is
re-dispatched.

CONTENT VERIFICATION, WHICH `CLAUDE.md` DESIGNATES AS THE PRIMARY BINDING, PASSES IN
FULL and was checked independently by the orchestrating session against committed blobs:

  snapshot TASK-20260823-744c38 : 127/127 paths verified, 0 problems
  ledger   TASK-20260823-d26c06 :   8/8   paths verified, 0 problems

Per CLAUDE.md ("Archive receipts bind to CONTENT first"), commit reachability is
advisory and a content mismatch is the fatal condition. There is no content mismatch.

## The real defect, and who owns it

TWO things are wrong and only one of them is the tool's:

- MINE: I declared `artifact_paths` before the work existed and they did not cover the
  deliverables. That is the third time in two campaigns a declared artifact set has been
  too narrow, and the snapshot archive already logged the systemic fix — the hash set
  handed to an archive should be DERIVED from the producer's `write_scope`, not
  hand-listed. Doing that would also have made checks 1 and 3 pass first time.
- THE TOOL'S: check 4 assumes the archive commit is the first commit to touch the
  artifacts. Any session under a clean-tree Stop hook violates that, because the hook
  forces intermediate commits. The two requirements are mutually exclusive as written.

## Options for whoever fixes this (not chosen here)

1. Relax check 4 to "the archive commit must not change anything OUTSIDE the declared
   set", allowing artifacts to have landed earlier, and rely on `path_sha256` for
   coverage. This preserves every guarantee the check actually provides.
2. Make the archive the only committer inside a batch, and exempt batch directories from
   the Stop hook's clean-tree requirement.
3. Leave it, and document that archive tasks are never marked `completed` in the queue —
   the current de facto behaviour, which should then be written down rather than
   discovered.

Option 1 looks correct and cheap; that is a recommendation, not a decision, and it is
not mine to make unilaterally.
