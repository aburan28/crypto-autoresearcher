# TASK-20260730-032 — Snapshot archive of the probe artifact package

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-015 `dispatch_queue.json`. **Where they disagree, the queue governs.**

- **Role:** coordinator (archival task — **runs alone**)
- **Depends on:** TASK-20260730-031
- **Archive kind:** snapshot; `source_task_ids: [TASK-20260730-031]`
- **Budget:** 300 s, 1 GB, `maximum_runs: 1` (zero compute — this card executes
  nothing; the 1 is there only because the schema rejects 0)

## Objective

Commit the exact eight TASK-20260730-031 probe artifacts and record a verified
post-commit receipt, so both independent reviews read an **immutable hash-bound
package** and every reported figure **provably predates every review of it**.

## Declared commit set — exactly 9 paths

```
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/probe_driver.py
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/command.txt
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/environment.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/stdout.log
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/stderr.log
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/structure_probe.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/supply_probe.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/probe_manifest.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/archives/TASK-20260730-032/snapshot_commit_receipt.json
```

Any extra path is a scope-expanding commit and blocks the review chain.
**BATCH-010 is permanently unrenderable for declaring 7 paths against a
195-path commit.** An undeclared producer file is **not staged and not
deleted** — record it in the receipt for the Coordinator to dispose of by
amendment.

## Do not stage

Anything under `ledger/`, `knowledge/`, `harness/`, `tools/` or `experiments/`.
`ledger/goals/GOAL-ECDLP-001.yaml` is owned by TASK-20260730-035;
`ledger/hypotheses/H-STR-002.yaml` is owned by nobody in this batch and is not
edited.

## Hazards this card must handle

- **Stale `.git/index.lock`.** Check before staging and record what you found —
  presence, size, modification time if obtainable. A zero-byte lock with no
  live git process is a **stale lock: report it and stop.** Do not delete it
  silently. One blocked a commit for 17 minutes earlier in this campaign.
- **Slow git.** The volume was reported at 99% and `git fsck` has already timed
  out on it. **An unfinished verification is reported as unfinished — never as
  PASS and never as FAIL.**
- No AppleDouble `._` sidecar may be staged.

## Record in the receipt, verbatim and auditable from the receipt alone

The eight path SHA-256 values; PART A's two returned lengths and two PASS/FAIL
pairs; the twenty-eight `(cell, arm)` triples of `len(relations)`, `R_base` and
shortfall; the measured distinct-target counts; the mechanically computed
`falsification_condition_fired` flag with its contributing cells named; the
determinism check result; the pre-flight disk figure; the harness code hashes.
**These cannot then be re-read later against a conclusion.**

**Transcribe, do not interpret.** The receipt draws no conclusion about D-3,
about the supply condition, about the stand-down, about H-STR-002 or about
anything else, and it makes **no approval determination**.

## INT-BATCH007-T

This receipt's own path is in the declared set and **cannot be changed by the
commit whose SHA it records**, so it lands in the immediately following commit.
State that; do not backdate it and do not invent a workaround.
