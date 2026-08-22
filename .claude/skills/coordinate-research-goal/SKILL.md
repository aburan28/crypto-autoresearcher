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

The loop below runs indefinitely: each batch is bounded, the sequence of
batches is not. Finishing a batch is a checkpoint, never an exit — do not stop
to ask whether to continue, and do not treat a quiet batch as a reason to wind
down. The campaign ends only at a committed terminal status (see "Completion
and pause"), and when it does, control returns to
`/launch-research-harness` step 9, which selects the next goal. Indefinite
operation adds no urgency and removes no gate: every batch still archives,
reviews, and scopes its claims exactly as before.

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
6. Before that snapshot archive, and again before every later batch, merge
   `origin/main` into the working branch (merge, never rebase) and re-validate
   (`tools/validate_ledger.py`). Push the branch and open or refresh a PR
   against `main` the moment the snapshot lands — see "Branch and PR hygiene"
   below. A goal whose artifacts cannot be pushed and reviewed is not launched.

## Continuous loop

For every batch, run this sequence:

1. Render the dispatch plan. Start at most the queue's declared
   `max_concurrent` non-archive tasks with disjoint write scopes, **each in a
   subagent** — never in this session. Choose the subagent from the task's
   (`role`, `inference.policy`) pair using the table in
   `.claude/skills/launch-research-harness/SKILL.md` step 6; each agent carries
   the reasoning effort its policy calibrates (`executor-mechanical` low →
   `executor` medium → `coordinator`/`idea-generator` high →
   `validator`/`red-team` xhigh → the `-breakthrough` review pair max).
   Launch them in one message so they run concurrently. The
   tooling's fixed ceiling of three was removed on explicit user direction
   (2026-08-05); size `max_concurrent` to the environment's real headroom —
   see `.claude/skills/launch-research-harness/SKILL.md`'s "Concurrency" note.
2. When a producer reaches a terminal result, run its Coordinator-only
   `snapshot` archive task alone. Its Git receipt must verify before a
   Validator, Reviewer, or Red Team reads the result.
3. Write the `review_plan` on the handoff opening the round, BEFORE launching
   any reviewer (AGENTS.md "Review architecture"): your prior, the joints with
   exactly one owner and a worked attack each, the blindness declaration, the
   proves-too-much objects, and a blind re-derivation of any load-bearing
   quantity with its `blind_from` paths. Writing it afterwards recovers none of
   its value — a prior recorded after the verdicts is not a prior, and joints
   assigned after the fact cannot buy coverage the round did not have.

   Then run the required independent review tasks, each as a FRESH subagent
   call rather than a continuation of the producer's session — a continuation
   carries the producer's context and is not an independent session. Launch
   them in one message so they run concurrently and cannot see each other's
   output. A claimed
   breakthrough, a proposed closure, or a result contradicting prior validated
   evidence routes to the `review-breakthrough` tier
   (`validator-breakthrough` / `red-team-breakthrough`, effort max), which is
   `degradable: false`: if it cannot be served, pause the goal rather than
   review it at a lower tier. Treat receipt validity, mathematical
   interpretation, and baseline comparison as separate checks.

   Before treating the round as complete, run
   `python3 tools/check_review_independence.py --batch <batch-dir>`. It checks
   the plan against the reviewers' attestations: every joint owned and
   attested, no undeclared sibling reads, controls declared, and no re-deriver
   whose declared sources intersect its `blind_from`. Record any departure from
   the plan in `procedure_deviations` — acting on a partial round may be the
   right call, and it is still a deviation.
4. Run the Coordinator-only `ledger` archive task alone. It commits exact
   review reports, analysis, evidence, decision, hypothesis status, and any
   knowledge update; its Git diff, parent, record IDs, and file hashes must
   verify.
5. In that same ledger commit, update the `GOAL-*` record with the batch,
   decision, latest verified commit, and exactly one next action. Rerank the
   remaining hypotheses only after this committed checkpoint.

   **Read the obstruction registry before you rerank.** Run
   `python3 tools/obstruction_registry.py --unexamined`. For each entry, ask
   the reversal question: which theory takes this measurement as its
   *hypothesis* rather than its refutation? A form that is indefinite blocks
   every argument needing positivity and is the premise of the operator theory
   built for indefinite forms; a degree that grows blocks elimination and
   bounds the object it grows in. The registry crosses goals deliberately —
   the reversal that matters is usually not available to the session that
   measured the obstruction, and arrives later against a theory nobody had in
   hand at the time. A candidate that survives this question enters the
   ranking as an ordinary hypothesis with its own record; it gets no priority
   for having come from here. "No theory takes it up" is a complete answer,
   and belongs in that record's `resource_check.reading` so the next rerank
   does not re-ask it blind.
6. Generate the next bounded batch and return to step 1 while the goal remains
   `active`. Preserve failed, invalid, deferred, and anomalous tasks as scoped
   evidence and route them to a repair, replication, or new positive search
   direction.

The loop has no batch count. Iterate until the goal takes a committed terminal
status or the campaign budget is exhausted — and an exhausted budget is a
`paused` checkpoint with a resume action, handed back to the launcher, not a
conclusion about the science.

**When a batch has nothing ready.** An empty ready set means the queue needs
work, not that the campaign is over. In order: run the goal's recorded
`next_action`; failing that, dispatch the highest-ranked open hypothesis under
the goal; failing that, dispatch a replication or a control run for the
weakest-supported live claim; failing that, run `/propose-ideas` on the bound
`RQ-*` to refill the candidate pool. Only when none of these yields a ranked,
justified task do you record the goal as `paused` with that finding as its
resume action. Never dispatch a task you cannot rank ahead of doing nothing —
under a loop that never stops, make-work is the standing temptation, and it
costs budget while producing evidence nobody asked for.

## Branch and PR hygiene

New goals, ideas, and experiments are not generated by writing files — they
are generated when the work is committed, pushed, and reviewable. Every batch
carries two git duties:

**Pull in changes from `main` before generating.** Before creating or resuming
a goal, and before each new batch, merge `origin/main` into the working branch
with `git fetch origin && git merge origin/main`. Never rebase — the branch
carries pushed run records, and rebasing rewrites the commits they were
archived in (AGENTS.md "Durable research commits"). If the merge conflicts,
do not resolve it by picking a side: stop and report so the Coordinator can
create a new superseding record. Re-run `tools/validate_ledger.py` and
`tools/check_merge_hygiene.py` on the merged tree before dispatching.

**Open or update the PR with every generation step.** Whenever a batch or
snapshot/ledger archive creates new `GOAL-*`, `RQ-*`, `IDEA-*`, `H-*`, `EXP-*`,
`EV-*`, `DEC-*`, `TASK-*`, or `KN-*` records, push the branch and open or
refresh a PR against `main`:

```sh
git push -u origin <branch>
gh pr create --base main --head <branch> --title "research: <summary>" --body "<record IDs>"
# or, for an existing PR:
gh pr edit <number> --title "research: <summary>" --body "<record IDs>"
```

Keep the PR open for the goal's lifetime. It makes each new goal, idea, and
experiment reviewable and mergeable; a record that exists only in a local
commit has not been surfaced to the program.

## Promotion gates and dispatch bias

Prioritize exponent-targeting mechanisms over logarithmic- or
constant-cofactor improvements; the canonical target profile is
`docs/target-result-profile.md`.

When a batch dispatches a conditional result, include in the same or the
following batch a heuristic-validation experiment — sampling the relevant
distribution at target scale, comparing the empirical distribution against
the prediction, and checking tail consistency — and, where feasible, a
proof-of-concept implementation task.

An asymptotic-complexity claim may not transition toward `supported` in a
ledger archive until all four gates are satisfied by committed artifacts:

1. archived proof decomposition into single-responsibility lemmas, with the
   main theorem assembling them under explicit per-attempt cost × inverse
   success probability bookkeeping;
2. explicit numbered heuristics, each with archived validation evidence or a
   scheduled validation experiment;
3. a concrete-cost table at standardized parameter sets with honest
   hidden-overhead (o(1) terms) and memory accounting, time–memory
   tradeoffs, parallelization, flagged optimistic assumptions, and an
   affected-vs-safe scope statement;
4. independent `review-xhigh` review plus a red-team pass on the cost model
   and heuristics.

A claim missing any gate may advance through `analyzed`, but the batch report
must name the missing gates instead of requesting promotion.

## Completion and pause

Mark the persistent goal `completed` only when a committed Coordinator decision
shows that a declared completion criterion was met. (The three-model closure
quorum that also gated this is **suspended** — see below.) Mark it `paused`
only when the user requests it or
a committed decision records the stated scoped pause condition. A failed
candidate, empty queue, timeout, or temporary lack of a promising idea does not
complete the goal: record the narrowest result and add the next concrete action
instead.

Both terminal statuses return control to `/launch-research-harness` step 8,
which picks up the next goal. Because the run continues either way, there is no
incentive to reach for `completed` — an honest `paused` with a resume action
costs the harness nothing.

### Closure quorum (AGENTS.md rule 13) — SUSPENDED

The three-model quorum is **not currently required**. Close a goal on the
committed Coordinator decision alone; `completion_quorum` is optional. It was
suspended because every policy alias in this harness resolves to one model, so
the quorum blocked all closures rather than distinguishing good ones.

That makes the closing decision carry the full weight. Before setting
`status: completed`, satisfy yourself that:

1. a declared `completion_criteria` item is actually met — not approximately,
   not in spirit — and the decision record names which one and cites the
   evidence IDs establishing it;
2. the claim is scoped to what was tested, at the tier the runs support;
3. no unresolved `DISSENT` sits in a `completion_quorum` block. A recorded
   dissent still blocks closure and stands until a new Coordinator decision
   supersedes it on the merits — do not outvote it, and do not re-roll for a
   friendlier verdict.

Attestations remain supported and are worth gathering when you can, especially
for a high-impact closure. If you record one it asserts that a review happened,
so it must be real: **never record an attestation you did not obtain**, and do
not describe a single-model review as independent corroboration. Whenever a
`completion_quorum` block is present, `tools/validate_ledger.py` still checks
attestation shape, `independent_session: true`, cited record IDs, and
`quorum_satisfied` consistency.

**To restore the requirement**, set `GOAL_CLOSURE_QUORUM_REQUIRED = True` in
`tools/validate_ledger.py`. The enforcing behaviour is unchanged and still
tested. Under it: three sessions on three **different** models (distinctness
judged on `resolved_model_id`, not the policy alias), all `CONCUR`, committed
with `quorum_satisfied: true` in the archive that performs the transition; if
three distinct models cannot be resolved, the goal does not close.

## Output after each batch

Report the following, then start the next batch without waiting:

- goal ID and active/paused/completed status;
- completed task IDs and verified commit IDs;
- evidence and decision IDs, with claim boundaries;
- knowledge entries promoted this batch (KN-* IDs), or each decision's
  recorded `not_warranted` reason — a batch that proved something but
  promoted nothing must say why;
- for any asymptotic-complexity claim advanced this batch, which of the four
  promotion gates passed and which remain open;
- the PR number and branch the batch was pushed to, and the last commit from
  `main` merged into it;
- the exact next action and why it reduces the remaining uncertainty.

Never call a passing validator or a snapshot commit a cryptanalytic
improvement. A small-instance result may be an improvement when its mechanism,
scope, and transfer assumptions are stated and supported by the cited
artifacts. The ledger archive makes work durable; it does not by itself upgrade
the evidence.
