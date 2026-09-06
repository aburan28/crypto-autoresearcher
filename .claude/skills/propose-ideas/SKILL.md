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
   Before generating, merge `origin/main` into the working branch (merge,
   never rebase) so ideation runs against current ledger state — see
   "Branch and PR hygiene" below.
2. Gather context for the prompt: the research question record, relevant
   entries from `knowledge/` (grep by area tags), existing hypotheses in
   `ledger/hypotheses/`, and existing proposals in `ledger/proposals/` so
   duplicates are avoided.
3. Dispatch the **idea-generator** subagent with a handoff that includes the
   research question, the context found above, how many ideas are wanted
   (default 3–5), and any user constraints. Remind it that every idea record
   must be schema-complete and novelty-checked against `knowledge/` before
   any novelty label stronger than `unverified`. The handoff must also direct
   it to the exemplar search heuristics in `agents/idea-generator.md` and the
   target profile in `docs/target-result-profile.md`: exponent-first ambition,
   hunting external structural ingredients, meet-in-the-middle decompositions,
   distribution heuristics plus re-randomization, and reduction-network
   cascades — and require the `heuristic_assumptions` and `target_complexity`
   fields on every idea.
   When the question targets a heavily mined ECDLP lane — index calculus,
   factor-base design, point representations, quotient or coordinate
   objects — also paste the constraint block from
   `docs/object-frame-ideation.md` into the handoff, so the generator
   searches (representation, operation set) pairs against the recorded
   rigidity results instead of regressing to a known family in new notation.
4. Verify each returned idea against the schema in
   `agents/idea-generator.md`: claim, mechanism, predictions with metrics,
   minimal test, controls, falsification conditions, named heuristic
   assumptions each with an experimental validation route, target time and
   memory exponents versus the best known, and cost. Send incomplete
   ideas back to the subagent for completion — do not repair them yourself.
5. Save each complete idea as `ledger/proposals/IDEA-YYYYMMDD-NNN.yaml`.
   The Coordinator then runs an isolated snapshot archive task that commits
   the exact research-question, proposal, and any literature-note paths before
   treating the ideas as filed. The task must pass the dispatcher's post-commit
   verification.
6. Push the branch and open or refresh a PR against `main` naming the new
   `RQ-*`/`IDEA-*` records (see "Branch and PR hygiene"). A filed idea that
   exists only in a local commit is not a proposal the program can use.
7. Report to the user: one-line summary per idea (ID, class, claim,
   novelty status, cost) plus the generator's recommended first test.

## Branch and PR hygiene

Ideation generates shared research records, so every run of this skill also
pulls in `main` and surfaces the new proposals as a PR:

- **Before generating:** `git fetch origin && git merge origin/main` — merge,
  never rebase. If the merge conflicts, stop and report; never resolve a
  conflict by editing a record (corrections supersede, per AGENTS.md rule 4).
  Re-run `tools/validate_ledger.py` after the merge.
- **After the snapshot archive:** `git push -u origin <branch>` then
  `gh pr create --base main --head <branch> --title "ideas: <summary>" --body "<RQ-*/IDEA-* IDs>"`
  (or `gh pr edit <number>` when a PR for the branch already exists).

## Rules

- Ideas are proposals only. Do not create hypothesis records or approve
  anything here — that is `/design-experiment` under Coordinator authority.
- Never overwrite an existing proposal file.
- Do not let an uncommitted proposal become a candidate for `/design-experiment`.
- Do not strip or soften `heuristic_assumptions` or `target_complexity` when
  filing ideas: a conditional claim must stay conditional, with its validation
  route and exponents intact.
