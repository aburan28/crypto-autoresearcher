# Correction: anomaly A1 is misattributed, and the fault is the orchestrator's

The producer's execution report records:

> **A1** `infrastructure_error` — Concurrent EXTERNAL write into this task's run
> directory during RUN-004: `raw-result.json.gz` and `RAW-RESULT-STORAGE.md`
> appeared under `runs/RUN-a7a9e8-002-m10-main/`, plus a `.git/info/exclude`
> entry, **evidently authored by archiving task TASK-20260822-e7c486**.

**The attribution is wrong, and the producer had no way to know that.**
`TASK-20260822-e7c486` has never run. It is still `blocked` in the dispatch
queue and owes the snapshot archive to this day.

Those writes were made by the **orchestrating session**. While RUN-004 was in
flight, a push was rejected because
`RUN-a7a9e8-002-m10-main/raw-result.json` is 112,301,654 bytes and exceeds
GitHub's 100 MB limit (`GH001`). To preserve the bytes without putting them in
git history, the orchestrator wrote `raw-result.json.gz` and
`RAW-RESULT-STORAGE.md` into this task's run directory and added a local
`.git/info/exclude` entry.

## Why this is a fault and not a footnote

The producer's `write_scope` is
`coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-a7a9e8`.
Write-scope discipline exists so exactly one process writes a path. The
orchestrator wrote inside a **running producer's scope**, and the producer
noticed the collision and correctly logged it as an anomaly against its own run.
It then had to reason about files it did not create while deciding what to trim
— its D1/D2 deviations say the collision interacted with that decision.

Recorded consequences:

* the producer's A1 must be read as **orchestrator interference**, not as a
  defect in the archiving task, which has not run;
* nothing in A1 casts doubt on any rank claim — the interference was additive
  (a compressed copy plus a note), never a modification of a result file;
* the correct handling would have been to preserve the oversized artifact
  **outside** the producer's scope until it terminated, and only then place it.

## What is NOT wrong

The producer's own deviations D1 (RUN-004 trimmed) and D3 (manifest lines
appended) are genuinely the producer's, are self-reported, and stand as recorded.
D2 notes that RUN-002's raw result was trimmed and then fully restored from the
orchestrator's `.gz` with sha256
`ff0935a0c68c58da7da3fdb861f36d80e33f72365fb2ecb57d8196b0af5ccb47` verified
equal — net effect none. That interaction is only legible because both sides
wrote it down.
