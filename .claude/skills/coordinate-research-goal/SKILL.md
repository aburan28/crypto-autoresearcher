---
name: coordinate-research-goal
description: >-
  Start or resume a durable, multi-batch ECDLP research goal through the
  Coordinator and dynamic-dispatch harness. Bind the goal to committed ledger
  state, run bounded task batches with independent review, archive every theory
  and research artifact, rerank after each checkpoint, and continue until an
  explicit terminal condition is met.
---

# Coordinate research goal

Use this skill for a persistent research program, not an unbounded prompt. It
continuously narrows uncertainty while preserving every theory, run, review,
and ledger transition as committed evidence.

## Launch or resume

1. Read `AGENTS.md`, `CLAUDE.md`, `docs/task-lifecycle.md`,
   `docs/dynamic-subagent-dispatch.md`, and the relevant ledger records.
2. Reuse an active `ledger/goals/GOAL-<AREA>-<NNN>.yaml` when it matches the
   request; otherwise create the next free goal record from
   `templates/research-records.md`. Bind it to one or more `RQ-*` records.
3. State an explicit objective, completion criteria, pause conditions, campaign
   budget, and exactly one next action. A negative result is not a completion
   criterion.
4. If the host provides a durable goal API and the user explicitly asked to
   launch the goal, create or resume the matching runtime goal and store its
   returned ID in the goal record. Keep it active across turns; do not mark it
   complete merely because one batch, idea, or experiment finished.
5. Create the first bounded batch under
   `coordination/goals/GOAL-<AREA>-<NNN>/batches/BATCH-<NNN>/`, with committed
   handoff records and a dispatch queue. Each task names exact `artifact_paths`,
   an exclusive `write_scope`, a budget, and an archival task. Commit the goal,
   question, queue, and handoff records through a Coordinator snapshot archive
   before starting workers. Set the queue's top-level `goal_id` to the matching
   `GOAL-*` so every rendered plan remains bound to the persistent campaign.

## Continuous loop

For every batch, run this sequence:

1. Render the dispatch plan. Start at most three non-archive tasks with
   disjoint write scopes.
2. When a producer reaches a terminal result, run its Coordinator-only
   `snapshot` archive task alone. Its Git receipt must verify before a
   Validator, Reviewer, or Red Team reads the result.
3. Run the required independent review tasks. Treat receipt validity,
   mathematical interpretation, and baseline comparison as separate checks.
4. Run the Coordinator-only `ledger` archive task alone. It commits exact
   review reports, analysis, evidence, decision, hypothesis status, and any
   knowledge update; its Git diff, parent, record IDs, and file hashes must
   verify.
5. In that same ledger commit, update the `GOAL-*` record with the batch,
   decision, latest verified commit, and exactly one next action. Rerank the
   remaining hypotheses only after this committed checkpoint.
6. Generate the next bounded batch and continue while the goal remains
   `active`. Preserve failed, invalid, deferred, and anomalous tasks as scoped
   evidence and route them to a repair, replication, or new positive search
   direction.

## Completion and pause

Mark the persistent goal `completed` only when a committed Coordinator decision
shows that a declared completion criterion was met. Mark it `paused` only when
the user requests it or a committed decision records the stated scoped pause
condition. A failed candidate, empty queue, timeout, or temporary lack of a
promising idea does not complete the goal: record the narrowest result and add
the next concrete action instead.

## Output after each batch

Report:

- goal ID and active/paused/completed status;
- completed task IDs and verified commit IDs;
- evidence and decision IDs, with claim boundaries;
- the exact next action and why it reduces the remaining uncertainty.

Never call a passing validator, a snapshot commit, or a toy result a
cryptanalytic improvement. The ledger archive makes work durable; it does not
upgrade the strength or scope of the evidence.
