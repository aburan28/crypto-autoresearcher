# BATCH-228222 fresh incident-repair snapshot design

Date: 2026-08-04
Producer: `TASK-20260804-209c69`
Classification: evidence-integrity repair design only

## Immutable commit audit

1. The original failed snapshot commit is
   `e3aa4c9ae310b9f6ea76974aea52405dd9cf9b2f`, with first parent
   `8dcbd8c03d917134c1fdf3502f450379a05a50da`.

   Its subject is:

   ```text
   research: snapshot ECDLP BATCH-278705 control plane
   ```

   The BATCH-278705 incident report and verification result record that this
   commit changed the declared 20 control-plane paths and passed its
   first-parent and content-hash checks. It is nevertheless inadmissible as a
   completed archive: the dispatcher reported that its message omitted
   `TASK-20260804-533c6c`, `TASK-20260804-cb6de3`, and `GOAL-ECDLP-001`.

2. The later replacement snapshot commit is
   `986593921085579ac504296f9a0cdc30bac77f0a`, with first parent
   `14108f4b31a844a363ee3b1663eaeba08d4c27a3`.

   Its subject is:

   ```text
   research: snapshot TASK-20260804-8c6faa TASK-20260804-6f7a48 GOAL-ECDLP-001 incident
   ```

   It contains the replacement package's declared source paths and receipt
   path, with the stated parent and content bindings, but its subject omits
   `BATCH-278705`. For `TASK-20260804-8c6faa`, the archive gate therefore
   remains unsatisfied: its required message identifiers are the archive task,
   source task, goal, and batch. This commit is not asserted to be a completed
   archive.

Neither immutable commit is amended, replaced in place, or treated as durable
archive evidence.

## Fresh snapshot requirement

`BATCH-228222` is a new design-only repair package. Its completed producer
creates exactly these three snapshot source artifacts:

1. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-228222/tasks/TASK-20260804-209c69/incident_repair.md`
2. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-228222/task-cards/TASK-20260804-209c69.md`
3. `ledger/handoffs/TASK-20260804-209c69.yaml`

The sole queued archive task, `TASK-20260804-d80f46`, must run alone and commit
exactly those three paths plus
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-228222/archives/TASK-20260804-d80f46/snapshot_commit_receipt.json`.
Its commit message must contain all of:
`TASK-20260804-d80f46`, `TASK-20260804-209c69`, `GOAL-ECDLP-001`, and
`BATCH-228222`. The receipt's commit, parent, and path-hash bindings remain
null or empty until that future archive runs and the dispatcher accepts it.

## Boundary

This package makes no research-state change and creates no evidence,
execution, data, experiment, run, hypothesis transition, pause decision, or
ECDLP/cryptanalytic conclusion. It is an auditable design for repairing a
commit-message archive gate only.
