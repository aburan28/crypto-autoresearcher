---
name: propose-ideas
description: >-
  Generate structured, falsifiable research proposals for an ECDLP research
  question. Use when starting ideation for a research question (RQ-*) or when
  the Coordinator requests fresh directions. Dispatches the idea-generator
  subagent and files proposals in the ledger.
---

# Propose ideas

Run the ideation stage of the research lifecycle (`docs/task-lifecycle.md`,
step 2).

## Steps

1. Identify the target research question. If the user named an `RQ-*` ID,
   read it from `ledger/questions/`. If no research question record exists
   yet, create one first from the template in `templates/research-records.md`
   and save it as `ledger/questions/RQ-<AREA>-<NNN>.yaml` (next free number).
2. Gather context for the prompt: the research question record, relevant
   entries from `knowledge/` (grep by area tags), existing hypotheses in
   `ledger/hypotheses/`, and existing proposals in `ledger/proposals/` so
   duplicates are avoided.
3. Dispatch the **idea-generator** subagent with a handoff that includes the
   research question, the context found above, how many ideas are wanted
   (default 3–5), and any user constraints. Remind it that every idea record
   must be schema-complete and novelty-checked against `knowledge/` before
   any novelty label stronger than `unverified`.
4. Verify each returned idea against the schema in
   `agents/idea-generator.md`: claim, mechanism, predictions with metrics,
   minimal test, controls, falsification conditions, cost. Send incomplete
   ideas back to the subagent for completion — do not repair them yourself.
5. Save each complete idea as `ledger/proposals/IDEA-YYYYMMDD-NNN.yaml`.
   The Coordinator then runs an isolated snapshot archive task that commits
   the exact research-question, proposal, and any literature-note paths before
   treating the ideas as filed. The task must pass the dispatcher's post-commit
   verification.
6. Report to the user: one-line summary per idea (ID, class, claim,
   novelty status, cost) plus the generator's recommended first test.

## Rules

- Ideas are proposals only. Do not create hypothesis records or approve
  anything here — that is `/design-experiment` under Coordinator authority.
- Never overwrite an existing proposal file.
- Do not let an uncommitted proposal become a candidate for `/design-experiment`.
