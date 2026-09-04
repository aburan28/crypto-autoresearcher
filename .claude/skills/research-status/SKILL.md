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

1. Run the census. It scans every ledger area plus every experiment
   specification and run manifest, and reports in ~2k tokens:

   ```sh
   python3 tools/ledger_summary.py
   ```

   **Do not rebuild this by reading `ledger/` file by file.** Followed
   literally that is ~18M tokens — proposals alone are ~10.5M — so every
   session that tried improvised a different partial scan and got a different,
   unreproducible answer. `--recent N` details more decisions, `--max-open N`
   lengthens the open-item lists, `--json` is for filtering.

2. Check integrity — dangling references, approved records with null fields,
   runs missing required artifacts, decisions whose `next_actions` have no
   follow-up handoff:

   ```sh
   python3 tools/validate_ledger.py
   ```

   Flag what it reports. Fix nothing in this skill.

3. Check the branch against `origin/main` (CLAUDE.md, "Conventions") and flag
   a branch that is behind or has no open PR, so the next generation step can
   merge and refresh the PR before writing new records:

   ```sh
   git fetch origin main && python3 tools/sync_open_branches.py --digest
   ```

   Also flag theory, experiment, task-report, knowledge, or ledger paths that
   remain uncommitted or lack a verified Coordinator archive receipt.

4. Report: the census tables as returned; experiments in flight with run
   tallies; the latest decision per active hypothesis; integrity flags from
   step 2 and unparseable records from step 1; and the concrete next action
   the lifecycle implies (e.g. "EXP-ISO-002 is approved but has no runs →
   /run-experiment EXP-ISO-002"). Cite record IDs.

   Counts are a census of records on disk. A record exists because some
   session wrote it, which is not itself a research result.

## Goal state

Read goal records through the projection, never the raw file — the largest
goal head is ~243k tokens and carries nothing these do not answer:

```sh
python3 tools/goal_head.py list --status active   # whole portfolio, ~3k tokens
python3 tools/goal_head.py show GOAL-ECDLP-001    # one goal, ~0.8k tokens
```

The narrative those heads accumulated — closeout reasoning, superseded next
actions, terminal notes on old theories — is omitted from the resume view but
kept and addressable. Reach it by date or by content when a status question
turns on why something closed:

```sh
python3 tools/goal_head.py history GOAL-ECDLP-001       # dated index
python3 tools/goal_head.py history --grep '<term>'      # across all goals
```
