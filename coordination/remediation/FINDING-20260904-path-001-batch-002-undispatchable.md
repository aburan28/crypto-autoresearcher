# GOAL-PATH-001's "exactly one next action" cannot be dispatched, and the reason is structural

Recorded 2026-09-04 by the standing coordinator session (`coordinator-aes-1`) during
`/launch-research-harness`. **Nothing is repaired, no task is invented, no batch is opened,
no record is edited.** A speculative queue I wrote while diagnosing this was deleted rather
than committed — see "What I did not do".

## The situation

`DEC-20260810-2f92d8` gives GOAL-PATH-001 a single authorized next action (N-1):

> EXACTLY ONE NEXT ACTION FOR GOAL-PATH-001: dispatch TASK-20260810-9e7f4c, a
> coordinator-only, zero-run reconciliation of GOAL-DREG-001's head against its committed
> BATCH-004 and BATCH-005 archives and against defects CD-1 and CD-2 … NO DREG BATCH MAY BE
> OPENED BEFORE THAT RECONCILIATION IS COMMITTED.

Everything that action needs exists **except the means to dispatch it**:

| | state |
|---|---|
| `ledger/handoffs/TASK-20260810-9e7f4c.yaml` | present, 16 KB, declares `batch_id: BATCH-002`, `write_scope`, `artifact_paths` |
| goal head `current_batch_id` | `BATCH-002` |
| goal head `dispatch_queue_path` | **`…/BATCH-001/dispatch_queue.json`** — stale, points at the completed batch |
| `coordination/goals/GOAL-PATH-001/batches/BATCH-002/` | **does not exist** |
| the task in any dispatch queue | **in none**, repository-wide |

N-2 of the same decision **was** discharged: commit `1d8130352` ("ledger: GOAL-PATH-001
BATCH-002 checkpoint + reopened Tier-path prioritization") staged the decision and the
handoff together. So the commissioned archive happened. What never happened is the batch
directory and its queue.

That is also why `tools/goal_portfolio_health.py` files this goal under *batch complete*: it
renders BATCH-001, which really is finished, because the pointer still aims there.

## The structural half, established empirically

Creating a minimal BATCH-002 queue carrying only the commissioned task does not work. The
dispatcher rejects it:

    dispatch error: non-archive task TASK-20260810-9e7f4c must be assigned exactly once
    to an archive task

`dispatch_queue.v1` requires every non-archive task to be assigned to an in-queue archive
task. But the archive `DEC-20260810-2f92d8` commissions is **not** an in-queue archive task
— N-2 specifies a Coordinator **ledger commit** staging exactly three ledger files. So the
batch shape the decision commissions is not representable in the queue schema, and the only
way to make it dispatchable is to invent an archive task the decision never authorized.

This is the same defect family GOAL-AES-002's own history records for BATCH-2b0fd1 as DEF-5
and DEF-6 — *"a leaf task with no archive key must still be assigned to some other archive
task"* and *"an archive task's `source_task_ids` can never be empty, so a task cannot both
author and self-archive."* PATH's BATCH-002 is a third instance: a one-task batch whose
archive is a ledger commit rather than a task.

## Defect CD-1 is real, and I confirmed it directly

The decision alleges that the goal head and `DEC-20260802-505759` both attribute a DREG
protocol PASS to `DEC-20260731-014`, which has no DREG content. Checked against the
committed record:

    DEC-20260731-014.target_ids = [EXP-DS-001, H-DS-001, GOAL-ECDLP-001, BATCH-021,
                                   PA-DS-001-v2-ctrl-theater-repair, CTRL-RT025-…, …]
    mentions "DREG"      : False
    mentions "BATCH-021" : True

So the citation is genuinely misdirected. Per N-3 that repair belongs to whoever owns the
GOAL-DREG-001 lane, must be a **superseding record under a new identifier** (AGENTS.md rule
15, because `DEC-20260731-014` is named in the binding fields of the completed BATCH-005
ledger receipt), and neither file may be edited nor renamed. **Not repaired here.**

## What I did not do, and why

- **I did not dispatch the task outside the dispatcher.** The handoff is complete and I
  could have run a coordinator against it directly, but `/launch-research-harness` says
  execute only tasks listed under a rendered plan's `dispatches` array. A task that the
  dispatcher will not offer is not made dispatchable by ignoring the dispatcher.
- **I did not invent an archive task** to satisfy the schema. That would author work no
  committed decision authorized, in a goal whose own next action says NO DREG BATCH MAY BE
  OPENED, and would make the queue agree with the tool rather than with the decision.
- **I did not repair the stale `dispatch_queue_path`.** It is a goal-head field on a goal
  this session does not own, and changing it would silently move which batch the portfolio
  tool reports without any committed decision behind it.
- **I deleted the diagnostic queue I wrote.** An invalid queue left in the tree would be
  offered to the next session as if it were real. Nothing of it is committed.

## Suggested disposition, for the owning lane

1. Decide the batch shape first: either amend the queue schema's expectation for a one-task
   coordinator batch whose archive is a ledger commit, or supersede N-2 with a shape that
   includes an in-queue archive task. Both are decisions, not edits.
2. Then create `BATCH-002/` with a queue in whichever shape that decision picks, and repair
   `dispatch_queue_path` in the same act so the pointer and `current_batch_id` agree.
3. CD-1's repair stays with the GOAL-DREG-001 lane, as a superseding record under a new
   identifier.

No mathematical result is asserted in either direction, no claim tier moves, and no
hypothesis or goal status changes. A dispatcher rejection is an infrastructure signal, never
negative evidence.
