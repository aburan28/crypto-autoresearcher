# BATCH-278705 archive-verification incident report

Date: 2026-08-04
Producer: `TASK-20260804-6f7a48`
Classification: evidence-integrity failure; not mathematical evidence

## Verified commit facts

The attempted control-plane snapshot commit is
`e3aa4c9ae310b9f6ea76974aea52405dd9cf9b2f`, with first parent
`8dcbd8c03d917134c1fdf3502f450379a05a50da`.

It correctly changed the 20 declared control-plane paths. The dispatcher
reached its commit-message check only after the declared parent and every
declared content hash passed.

The commit subject is:

```text
research: snapshot ECDLP BATCH-278705 control plane
```

## Commands and actual results

1. Executed:

   ```sh
   git show -s --format='%H%n%P%n%s' "e3aa4c9ae310b9f6ea76974aea52405dd9cf9b2f" && git diff-tree --no-commit-id --name-only -r "e3aa4c9ae310b9f6ea76974aea52405dd9cf9b2f"
   ```

   Exit status: `0`. It returned the commit ID, the first parent above, the
   subject above, and 20 changed control-plane paths.

2. Executed:

   ```sh
   python3 tools/research_dispatch.py "coordination/goals/GOAL-ECDLP-001/batches/BATCH-278705/dispatch_queue.json" --output "/tmp/GOAL-ECDLP-001-BATCH-278705-failed-archive-dispatch.json" --report "/tmp/GOAL-ECDLP-001-BATCH-278705-failed-archive-dispatch.md"
   ```

   Exit status: `2`. The exact result was:

   ```text
   dispatch error: archive task TASK-20260804-533c6c commit message is missing IDs ['TASK-20260804-533c6c', 'TASK-20260804-cb6de3', 'GOAL-ECDLP-001']
   ```

## Consequence and boundary

The message omission makes `TASK-20260804-533c6c` inadmissible as a completed
archive task. The commit is not amended and none of its historical source
artifacts is altered. The attempted RC-46 author/review chain is cancelled.

No Sage command, experiment, implementation, run, result, relation, solve,
cryptanalytic outcome, asymptotic inference, evidence record, decision record,
goal-head change, or checkpoint occurred. The valid response is a scoped pause
recorded only after a fresh incident-report snapshot and a valid ledger archive.
