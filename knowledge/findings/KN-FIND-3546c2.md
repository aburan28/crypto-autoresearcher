---
id: KN-FIND-3546c2
type: internal_finding
title: A goal resumed without reading the merge digest re-reviewed a batch that was already archived and a campaign that was already closed
tags: [process, harness, concurrency, dispatch, review, durability, replication, ml-kem]
confidence: observed_directly
evidence_level: observed_directly
scope: process
source_refs: [GOAL-MLKEM-004, BATCH-d2a728, TASK-20260803-535d15, TASK-20260803-bc2f41, TASK-20260803-586a7f, DEC-20260805-0b3e11, KN-FIND-24acfd]
internal_refs: [DEC-20260805-0b3e11]
proof_status: not_applicable
proof_refs:
  - coordination/goals/GOAL-MLKEM-004/independent-replication-20260813/README.md
  - coordination/goals/GOAL-MLKEM-004/independent-replication-20260813/red_team_report.yaml
  - coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/archives/TASK-20260803-586a7f/ledger_commit_receipt.json
review_refs: []
supersedes: KN-FIND-24acfd
added: 2026-08-13
superseded_by: null
---

## What happened

A session resumed `GOAL-MLKEM-004` from a working tree whose last fetch of
`origin/main` predated the goal's entire remaining life. On that stale snapshot
the goal read `status: active`, `current_batch_id: BATCH-d2a728`, with a
`next_action` naming batch 1 of 6 and two queued reviews. The session dispatched
those two reviews.

Both were redundant. On `main`, `BATCH-d2a728` had been reviewed, ledger-archived
under `TASK-20260803-586a7f`, and superseded by five further batches; the campaign
had closed as `closed_at_budget` under `DEC-20260805-0b3e11` with its only
result-asserting criterion unmet. The stale snapshot's `next_action` was not
merely out of date, it described a state the program had left behind entirely.

The duplication surfaced only when a merge was attempted and Git refused to
overwrite untracked files — that is, by accident, at the end, rather than by a
check at the start.

## Why the existing guard did not fire

`CLAUDE.md` already requires running `tools/merge_digest.py` before resuming a
goal, precisely because sessions are ephemeral and most sessions that care about
a merge do not exist when it lands. The session did fetch and merge `main` when
it began. The defect is that "before resuming a goal" was treated as an
event that happens once at session start, whereas this session's start and its
resumption of the goal were separated by nine days of wall-clock and a container
recreation. Nothing re-fired the check across that gap.

A stale `next_action` is *confidently wrong*. It is a written instruction from
the Coordinator naming a specific task, so it reads as authority rather than as
cached state, and every subsequent step inherits its premise.

## The near-miss

Merging the duplicate work would have overwritten three files that
`TASK-20260803-586a7f` binds by `path_sha256`:
`TASK-20260803-535d15/notes.md`, `TASK-20260803-bc2f41/notes.md` and
`TASK-20260803-bc2f41/report.yaml`. That is the permanent archive breakage
AGENTS.md rule 15 describes: the commit is immutable, so its declared hashes and
the live tree could never be reconciled again. The duplicate artifacts were
relocated to `coordination/goals/GOAL-MLKEM-004/independent-replication-20260813/`
rather than merged.

Worth stating plainly: the batch directory layout gave a *duplicate* session the
exact write paths of an *archived* one, and nothing in the write scope itself
signalled that those paths were already spent.

## What the duplicate work is nonetheless worth

The redundant red team had no access to the archived reviews and re-derived, by
a different route, the conclusion the campaign reached eight days earlier.

The campaign's closing decision found the departure real but localised out of its
own subject matter: the validator's ablated-Y-only arm, holding the real sieve `X`
exactly fixed, reproduced the whole effect, so it is not a property of sieve
geometry, lattice membership, or vector shortness.

The duplicate red team instead permuted coordinates and signs within every `X`
row, preserving each row's exact norm and coefficient multiset while destroying
lattice and sieve direction structure. Real `X` gives a variance design effect of
404x against an independence baseline — an effective sample size near 44 rather
than 17,919, which read alone looks like a spectacular violation of exactly the
assumption `MATZOV.Nf` encodes. The norm-matched null returns 402x. The effect is
dominated by the shared error vector common to all rows and is not identified as
sieve correlation.

Two different nulls, two sessions with no contact, one conclusion. That is a
genuine independent replication of the campaign's central negative result, and it
is the only reason this record is worth keeping rather than merely reverting.

The same session also derived the candidate-class offset analytically —
`+0.008567389` for centred-binomial candidates against `0` for uniform, from
candidate-prior Fourier mass against a fixed population baseline, with a
4,096-permutation pairing test at z = -0.84. That is consistent with a mechanical
account and not with residual LWE structure.

## Recommendations

1. Re-run the merge-digest check when a session *resumes a goal*, not when a
   session starts. Any gap containing a container recreation, a model-quota
   stall, or a wall-clock discontinuity invalidates the earlier check.
2. Treat a goal's `next_action` as cached state carrying the commit it was read
   at, never as a standing instruction. Verify the goal's `status` against
   `origin/main` before acting on it; `closed_at_budget` and `completed` goals
   must refuse dispatch outright.
3. Before dispatching into a batch directory, check whether that batch already
   carries an `archives/*/ledger_commit_receipt.json`. A ledger receipt means
   every write path beneath it is spent, and dispatch should refuse rather than
   collide.
4. The durability autosave recommended by `KN-FIND-24acfd` was implemented and
   did work — it captured the red team's output within three minutes of it
   landing, and that output survived. Keep it. Note the sharper lesson: it made
   *duplicate* work durable, so durability and relevance are independent
   properties and neither substitutes for the other.

## Scope

This is a process finding about the harness. It asserts nothing about ML-KEM,
LWE, or the dual attack beyond the replication noted above, which is itself
scoped to the reduced-dimension single-instance measurement archived in
`BATCH-d2a728` and is not crypto-scale evidence.
