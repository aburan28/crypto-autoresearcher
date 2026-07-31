# TASK-20260731-002 — Coordinator — Snapshot archive, ALONE

**Goal** GOAL-P13-001 · **Batch** BATCH-002 · **Role** coordinator · **Priority** 95
**Depends on** TASK-20260731-001 · **Archive kind** `snapshot`
**Budget** 600 s wall clock · 2 GB · maximum_runs 1

> **The queue governs.** This card mirrors the `archive` and `handoff` blocks for
> TASK-20260731-002 in
> `coordination/goals/GOAL-P13-001/batches/BATCH-002/dispatch_queue.json`.

---

## Objective

Commit the exact **thirteen** TASK-20260731-001 artifacts plus this receipt —
**fourteen paths** — in one isolated commit, and record a verified post-commit
receipt, so that both independent reviews read an **immutable, hash-bound**
package and so that every measured number and every fitted interval **provably
predates every review of it**.

## Constraints

- **RUN ALONE.** No other task may hold the Git index concurrently and no
  non-archive task may run beside it.
- **Stage only the declared paths.** The thirteen run artifacts and this
  receipt. Nothing else.
- **Do not re-stage** `experiments/EXP-SSI-002/specification.yaml` or
  `derivation_note.md`. They are already committed in the BATCH-002 **opening
  control-plane commit**, and *that ordering is the pre-registration* — it is
  what makes the fired reading meaningful and what the validator checks against
  the commit graph.
- **Do not stage ledger records.** That is TASK-20260731-005's job.
- If a declared file is missing, record the shortfall as a **declare-then-deviate**
  entry in the receipt **naming the exact missing paths**. Do not create a
  placeholder, do not fabricate content, do not silently narrow the declaration.
- Compute and record the **SHA-256 of every committed path**, the commit SHA and
  the parent SHA, and write them back into the task's `archive` object.
- **Never rewrite history** over a pushed run record. A conflict inside an
  immutable record is resolved by **superseding it under a new identifier**,
  never by an in-place edit. Any branch sync is a **merge**, never a rebase.
- **No ledger change and no status transition.** This card commits artifacts; it
  decides nothing.

## Gate

The **post-commit verifier must accept** the exact Git diff and file hashes
before any review is dispatched. Until it does, the run package is **not durable
and not official**.

## Deliverable

```
coordination/goals/GOAL-P13-001/batches/BATCH-002/archives/TASK-20260731-002/snapshot_commit_receipt.json
```

Containing: commit SHA, parent SHA, the exact staged path list, per-path
SHA-256, the verifier result, and any declare-then-deviate shortfall named.

## Completion gate

S1–S5 as stated in the queue's `handoff.completion_gate` for this task.
