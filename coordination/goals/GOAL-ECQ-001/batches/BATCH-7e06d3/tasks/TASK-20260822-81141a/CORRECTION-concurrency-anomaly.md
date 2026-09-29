# Correction: the "another session committed during my runs" anomaly is the orchestrator

The producer's execution report records:

> Concurrency observation: repo HEAD moved from 79019cf to f7d9716 during this
> session and the task's run files now appear as tracked by git ls-files. I made
> no commit. **Another session in this worktree appears to have committed while
> runs were in flight** — flagged for the Coordinator before its snapshot.

The observation is exactly right and the inference is the only one available to
it. The "another session" was the **orchestrating session**, committing this
task's in-flight artifacts for durability because the container is ephemeral and
a session Stop hook requires a clean tree.

This is the SECOND time an orchestrator action surfaced inside a producer's
report as an unexplained external event; the first was anomaly A1 in
TASK-20260822-a7a9e8 (see CORRECTION-anomaly-A1-attribution.md there), where the
producer attributed orchestrator writes to an archive task that has never run.

## What it does and does not affect

* **No producer artifact was modified.** The orchestrator only added commits; it
  wrote nothing into this task's directory. Contrast A1 on the other task, where
  the orchestrator did write two files into a running producer's `write_scope` —
  that was a genuine write-scope violation and is recorded as such.
* **No number in this package is affected.** Commit timing does not touch a
  computation, and the producer recorded its own `implementation_sha256` for
  `src/pipeline.py` covering runs 001–004.
* **The snapshot archive must not treat this as a defect in the task.** It is an
  orchestration artifact of committing mid-flight.

## The reusable point

A producer cannot distinguish "my orchestrator is checkpointing my files" from
"a concurrent writer is racing me", and it is right to flag the second. The
durability-commit pattern is therefore not free: it injects events into every
producer's field of view. Recorded so the Coordinator prices that in rather than
reading two independent producers' anomaly sections as evidence of a concurrency
problem in the repository.
