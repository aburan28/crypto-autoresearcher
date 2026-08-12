# TASK-20260729-041 — Snapshot archive of the frozen EXP-STR-004 contract and derivation note

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-014 `dispatch_queue.json`. Where they disagree, the queue governs.

- **Role:** coordinator (archival task — **runs alone**)
- **Depends on:** TASK-20260729-040
- **Archive kind:** snapshot; `source_task_ids: [TASK-20260729-040]`
- **Budget:** 300 s, 1 GB, `maximum_runs: 1` (zero compute)

## Objective

Commit the exact TASK-20260729-040 artifacts and record a verified post-commit
receipt, so the pre-execution review reads an immutable hash-bound contract and
so the derivation note and every set-valued prediction **provably predate every
measurement**.

## Declared commit set — exactly 4 paths

```
experiments/EXP-STR-004/specification.yaml
experiments/EXP-STR-004/derivation_note.md
coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/tasks/TASK-20260729-040/feasibility_table.md
coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/archives/TASK-20260729-041/snapshot_commit_receipt.json
```

Any extra path is a scope-expanding commit and blocks the review chain.
**BATCH-010 is permanently unrenderable for declaring 7 paths against a
195-path commit.**

## Hazards this card must handle

- **Stale `.git/index.lock`.** Check before staging and record what you found —
  presence, size, modification time if obtainable. A zero-byte lock with no
  live git process is a **stale lock: report it and stop**. Do not delete it
  silently. One blocked a commit for 17 minutes in the session that opened this
  batch.
- **Slow git.** The volume is at 99% and `git fsck` has already timed out on
  it. **An unfinished verification is reported as unfinished — never as PASS
  and never as FAIL.**
- No AppleDouble `._` sidecar may be staged.

## Do not stage

Anything under `experiments/EXP-STR-004/driver`, `/runs` or `/results` (they
must not exist yet); anything under `experiments/EXP-STR-001`, `-002` or
`-003`; anything under `harness/`, `ledger/`, `knowledge/` or `tools/`.

## Record in the receipt, verbatim

The fourteen cell names; the two arm definitions; predictions P-1 to P-4;
falsification conditions F-1 to F-5; the verdict rule; `R_base(cell)`; the
sha256 of `derivation_note.md`; the `yaml.safe_load` result; the index.lock
check; the verification that the EXP-STR-003 frozen specification blob is
unchanged. The **solver fact stays a pre-freeze host observation** — the
receipt must not upgrade it to a verified result.

## INT-BATCH007-T

This receipt's own path is in the declared set and **cannot be changed by the
commit whose SHA it records**, so it lands in the immediately following commit.
State that; do not backdate it and do not invent a workaround.

## What this card does not do

Committing the contract is **not approving it**. TASK-20260729-044 stays
blocked until TASK-20260729-042 returns PASS and the approval determination is
recorded in the TASK-20260729-043 receipt.
