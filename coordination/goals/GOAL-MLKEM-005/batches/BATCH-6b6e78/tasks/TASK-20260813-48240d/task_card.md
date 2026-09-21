# TASK-20260813-48240d — SNAPSHOT ARCHIVE of the lead producer (runs alone)

    goal / batch    GOAL-MLKEM-005 / BATCH-6b6e78
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-2ce014
    review_required false
    archive         snapshot, sources TASK-20260813-2ce014
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## Why it runs alone, and before either review

So that both independent reviews read **committed immutable bytes** rather than a
working tree that can still move under them. **NO REVIEW IS DISPATCHED UNTIL THIS
COMMIT EXISTS.**

## Declared path set — EXACTLY ELEVEN

    archives/TASK-20260813-48240d/snapshot-receipt.json
    tasks/TASK-20260813-2ce014/measure_a1.py
    tasks/TASK-20260813-2ce014/results_a1.json
    tasks/TASK-20260813-2ce014/report_a1.md
    tasks/TASK-20260813-2ce014/rerun_probe_precision_null_output.json
    tasks/TASK-20260813-2ce014/rerun_probe_precision_null_stdout.log
    tasks/TASK-20260813-2ce014/rerun_probe_precision_null_stderr.log
    tasks/TASK-20260813-2ce014/command.txt
    tasks/TASK-20260813-2ce014/stdout.log
    tasks/TASK-20260813-2ce014/stderr.log
    tasks/TASK-20260813-2ce014/run_manifest.yaml

The commit changes **exactly** those eleven. **0 extra and 0 missing.** Compare
the change set against the declared set explicitly and record both counts in the
receipt.

## The one comparison that costs nothing and prevents defect D3

`report_a1.md` lists every path the lead wrote. **If that list and the declared
set differ in either direction, DO NOT COMMIT** — return the run to the producer
with the discrepancy stated. Look specifically for a `__pycache__` directory and
for any stray probe output left inside the repository.

**Also confirm the probe was RE-RUN and not COPIED:** the archived
`probe_precision_null.py` at its `BATCH-4ed139` path is unmodified in the working
tree, and no vendored copy of it exists under this batch's task directory.

## Validity BEFORE anything is interpreted

Expected run count against `AM-18(f)`'s definition of a run; schema-complete
manifest **including the adapter binding**; seed integrity; agreement between
`results_a1.json` and `report_a1.md`; control comparability — **the per-candidate
fibre guard printout exists PER CANDIDATE**; and the artifact policy (durable
`command.txt` / `stdout.log` / `stderr.log`, no path inside a folded YAML scalar).
An invalid or incomplete run set goes **back to the producer** with concrete
defects listed. It is not evidence and it is not archived.

## Receipt pattern, merge, verifier

Receipt carries `commit_sha: null` and rides **inside** its own commit; the real
sha and parent go into the queue's `archive` block afterwards with `path_sha256`
for all eleven paths read **from the commit**. Fetch and **MERGE** `origin/main`
(never rebase), recording the base commit and the merge outcome in the receipt and
in the commit message. **RUN THE POST-COMMIT VERIFIER BEFORE THE PUSH, NOT
AFTER**, record its verdict, then push and refresh the PR naming `BATCH-6b6e78`.

**DO NOT INTERPRET the lead's result here and DO NOT write any ledger record.**
This archive makes bytes durable; the decision comes after review. Stage paths
explicitly; never `git add -A`. `knowledge/INDEX.md` is not written, regenerated
or staged.
