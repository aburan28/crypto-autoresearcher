# PROTOCOL-DEVIATIONS.md — GOAL-AES-003 BATCH-9845b0

Authored by the Coordinator before the snapshot commit, per this archive
task's own handoff constraint.

## 1. BATCH-9845b0 is not the campaign's current head

`ledger/goals/GOAL-AES-003.yaml`'s own head-verification block records
BATCH-9845b0 as a stale BATCH-002-era plan, roughly 30 batches behind the
campaign's `current_batch_id` (`BATCH-060cb4`), and explicitly states it
"is not a candidate for the head." This batch's three producer tasks were
nonetheless dispatched by name by the orchestrating session, on the
understanding that the underlying research question each names may still
be open even though the batch itself is not live. Each producer
independently re-checked that premise before doing any work; see below.

## 2. TASK-20260804-fdafdf — no artifacts produced

Independently confirmed (by its own dispatched executor, and cross-checked
here) that this task's objective — RANK 1/RANK 2 segment-3 review and
independent-key arm under the four-zero mixing matrix — was already
satisfied by different, later work committed under
`coordination/goals/GOAL-AES-003/batches/BATCH-003/`. The task produced no
new artifacts and made no commits. There is nothing to archive for it.

## 3. TASK-20260804-7092fa — specification_error, no artifacts produced

Independently confirmed (by its own dispatched executor, and cross-checked
here) that this task's objective — RANK 4/RANK 5 hint corruption at slots
t=1/t=2, null arms N2-N5 — falls under a standing, more recent, committed
embargo: `ledger/goals/GOAL-AES-003.yaml` records the campaign's live design
lineage as `DEC-20260905-ace928` ("repaired design lineage") with an
explicit note that no arm runs are authorized until that decision is
committed, and it is not yet committed as of this archive. The executor
correctly refused rather than running an arm against a design the
Coordinator has not yet authorized. The task produced no new artifacts and
made no commits. There is nothing to archive for it.

## 4. TASK-20260804-8965ec — genuinely executed; this archive covers it

Confirmed via git history and `coordination/reconciliation/RECON-20260810-001/`
that this specific cross-instrument anchor (count5.c vs cnt.c) had never
been run anywhere in the repository; the task's own pre-execution check
independently reached the same conclusion. This is real, previously
undone research work. Its full producer package (7 declared
`artifact_paths` plus the undeclared-but-archived reproducibility set the
task itself named: `count5_copy.c`, `cnt_copy.c`, `finalize.py`,
`raw.jsonl`, `driver.log`) is what this archive commits.

Independently spot-checked before archiving: `raw.jsonl` shows both engines
report `n=0` on the zero case and `n=2147544888` on the non-zero case,
matching `RESULTS.json`'s verdict; `pin_receipt.json` records a bit-for-bit
PINNED verdict against the independent third `anchor.c` reference
implementation before either full-coset count is trusted.

## 5. Coordinator's own deviation

This archive commits only TASK-20260804-8965ec's producer package, not a
full BATCH-9845b0 closure. TASK-20260804-fdafdf and TASK-20260804-7092fa
produced nothing to archive, so `dispatch_queue.json`'s executor entries for
them are separately marked `invalid` (not `completed`) in this same commit,
citing this note. Downstream validator/red-team/coordinator tasks
(TASK-20260804-1970c7, TASK-20260804-e4fb2a, TASK-20260804-87a68f) are left
`queued`: real independent review of the 8965ec finding has not yet
happened and is out of this archive task's and `/run-experiment`'s scope.
No hypothesis status changes and no BATCH-9845b0 head-candidacy claim is
made by this archive.
