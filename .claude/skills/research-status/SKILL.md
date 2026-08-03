---
name: research-status
description: >-
  Summarize the current state of the research program: open questions,
  hypothesis statuses, experiments in flight, recent decisions, and next
  actions. Use at session start or whenever an overview of the ledger is
  needed. Read-only.
---

# Research status

Produce a read-only snapshot of the program. Make no state changes.

## Steps

1. Scan the ledger:
   - `ledger/questions/` — active research questions;
   - `ledger/proposals/` — proposals not yet converted to hypotheses;
   - `ledger/hypotheses/` — group by status
     (proposed/specified/approved/running/analyzed/…);
   - `ledger/decisions/` — most recent decisions and their `next_actions`;
   - `ledger/handoffs/` — handoffs without a matching completed deliverable.
2. Scan `experiments/*/specification.yaml` for status, and count run
   directories by terminal status from their manifests.
3. Check integrity while scanning and flag (do not fix):
   - hypotheses referencing missing questions, evidence referencing missing
     runs, experiments approved with null fields;
   - run directories missing required artifacts;
   - decisions whose `next_actions` have no follow-up handoff;
   - theory, experiment, task-report, knowledge, or ledger paths that remain
     uncommitted or lack a verified Coordinator archive receipt;
   - the working branch behind `origin/main` (un-merged-upstream) or with no
     open PR against `main` — flag it so the next generation step can merge
     `main` and open/refresh the PR before producing new records.
4. Report: a short table per ledger area, experiments in flight with run
   tallies, the latest decision per active hypothesis, integrity flags, and
   the concrete next action the lifecycle implies (e.g. "EXP-ISO-002 is
   approved but has no runs → /run-experiment EXP-ISO-002").
