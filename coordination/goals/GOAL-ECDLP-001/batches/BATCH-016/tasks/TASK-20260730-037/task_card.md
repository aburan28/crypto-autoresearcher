# TASK-20260730-037 — Coordinator — Snapshot archive, ALONE

> **NON-AUTHORITATIVE MIRROR.** The authoritative card is the `tasks[]` entry
> for `TASK-20260730-037` in
> `coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/dispatch_queue.json`.
> Where this mirror and that queue disagree, **THE QUEUE GOVERNS**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-016
- **Role:** coordinator · **depends_on:** TASK-20260730-036
- **Archive:** `kind: snapshot`, `source_task_ids: [TASK-20260730-036]`
- **Budget:** 300 s, 1 GB. `maximum_runs: 1` **because the schema rejects 0**;
  the semantically correct value is zero. **This card executes nothing.**

## Objective

Commit the exact seven TASK-20260730-036 mutation artifacts and record a
verified post-commit receipt, so both independent reviews read an immutable
hash-bound package and every reported PASS/FAIL provably predates every review
of it.

## The eight declared paths

```
coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/mutation_driver.py
coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/command.txt
coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/environment.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/stdout.log
coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/stderr.log
coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/mutation_probe.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/mutation_manifest.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/archives/TASK-20260730-037/snapshot_commit_receipt.json
```

## Constraints

- **RUN ALONE.** No other task may hold the Git index concurrently.
- **Commit exactly these eight paths and nothing else.** BATCH-010 is
  permanently unrenderable for declaring 7 paths against a 195-path commit.
- An undeclared producer file is **not staged and not deleted** — record it in
  the receipt for the Coordinator to dispose of by amendment.
- **Check `.git/index.lock` before staging** and record what you found. A
  zero-byte lock with no live git process is stale: **report it and stop.** Do
  not delete it silently.
- **Stage no AppleDouble `._` sidecar.**
- **Stage nothing under `ledger/`, `knowledge/`, `harness/`, `tools/` or
  `experiments/`.** `ledger/goals/GOAL-ECDLP-001.yaml` is owned by
  TASK-20260730-040; `ledger/hypotheses/H-STR-002.yaml` is owned by nobody here.
- **Verify `harness/` is unmodified in the working tree and record the result.**
  A modified harness invalidates the batch and is reported, not committed.
- **An unfinished verification is reported as unfinished** — never as PASS and
  never as FAIL. Git on this volume is slow and `git fsck` has already timed out.
- **INT-BATCH007-T:** this receipt's own path is in the declared set and cannot
  be changed by the commit whose SHA it records, so it lands in the immediately
  following commit. State that; do not backdate and do not invent a workaround.

## What the receipt must transcribe verbatim (auditable from the receipt alone)

The seven path SHA-256 values; per-case condition (i), condition (ii) and joint
PASS/FAIL for case 0, case 1 at z = 5, case 1 at z = 1234, case 2 and case 3;
the failing (j, k) lists as reported; the SHA-256 and provenance of the copied
checker text; the computed instance parameters; the computed cubes of z = 5 and
z = 1234; the chosen case-2 replacement x; the mechanically computed
`assertion_passed_a_mutated_case` flag with contributing cases named; the
determinism check result; the pre-flight disk figure; the harness code hashes.

**Transcribe, do not interpret.** The receipt draws no conclusion about CTRL-4's
retirement or rewrite, about phi-invariance, about H-STR-002 or about anything
else, and makes no approval determination.

## Completion gate

G1 exactly eight paths (receipt deferred one commit, stated) · G2 index.lock
check performed and recorded · G3 figures and checker provenance transcribed and
uninterpreted · G4 nothing outside the declaration staged, no sidecar,
undeclared files recorded · G5 `harness/` verified unmodified · G6 any
unfinished git verification reported as unfinished.
