---
name: launch-research-harness
description: >-
  Discover, select, and run a crypto-autoresearcher research goal through the
  Coordinator + dynamic-dispatch harness. Use when the user asks to run the
  harness, launch a research goal, continue GOAL-*, resume a campaign, or run
  crypto-autoresearcher.
---

# Launch research harness

Entry point for starting or resuming a persistent `GOAL-*` campaign. This skill
selects the goal and binds committed state; the continuous batch loop is
`/coordinate-research-goal`.

Do not invent runs, timings, or review verdicts. Do not change hypothesis or
goal status outside Coordinator ledger archives.

## Required reads (once per session)

1. `AGENTS.md`, `CLAUDE.md`
2. `.claude/skills/coordinate-research-goal/SKILL.md`
3. `.claude/skills/research-status/SKILL.md` (read-only overview)
4. `docs/dynamic-subagent-dispatch.md`, `docs/task-lifecycle.md` (as needed)
5. `orchestration/model-policies.yaml` for role→policy aliases

## Procedure

### 1. Research status (read-only)

Run the `/research-status` checklist: scan `ledger/` and flag integrity issues
(uncommitted archives, broken refs). Do not mutate state in this step.

### 2. Discover goals

List `ledger/goals/GOAL-*.yaml`. For each, read `research_goal.{id,status,
title,current_batch_id,dispatch_queue_path,next_action,campaign_budget,
completion_criteria,pause_conditions}`.

Statuses: `draft | active | paused | blocked | completed | cancelled`.

Also note matching dirs under `coordination/goals/GOAL-*/batches/`.

### 3. Select a goal

Pick in this order:

1. Explicit `GOAL-*` in the user request.
2. Single `active` goal that matches the request text or current branch/area.
3. Otherwise list `active` / `paused` goals (ID, status, batch, next action)
   and ask which to run. Do not silently resume a `paused` or `completed` goal.

**Resume** an existing goal: use its `dispatch_queue_path` and
`current_batch_id`; continue from `next_action`.

**Start new**: only when the user asks for a new campaign. Create the next free
`GOAL-<AREA>-<NNN>.yaml` from `templates/research-records.md`, bind `RQ-*`,
create `coordination/goals/GOAL-.../batches/BATCH-001/` with handoffs + queue
(`goal_id` set), then follow `/coordinate-research-goal` launch steps.
Snapshot-archive the goal/queue/handoffs before any worker runs.

### 4. Bind committed state

Confirm before dispatching workers:

- Goal record is committed (or about to ride a Coordinator snapshot).
- `dispatch_queue_path` exists and queue top-level `goal_id` matches.
- Campaign budget still allows another batch (`maximum_batches`,
  `total_wall_clock_seconds`, `max_concurrent` ≤ 3).
- `next_action` is concrete; empty queue alone does not complete the goal.

If a pause/completion criterion already holds, stop and report — do not invent
work to fill capacity.

### 5. Render dispatch

From repo root, using the goal's queue path:

```sh
python3 tools/research_dispatch.py <dispatch_queue_path> \
  --output <batch-dir>/dispatch_plan.json \
  --report <batch-dir>/dispatch_plan.md
```

Use the paths the goal/batch already use (e.g. `dispatch_queue.json` or
`dispatch_queue.v2.json`). Fix validation errors before starting agents.
Execute only tasks listed under the plan's `dispatches` array (Ready Tasks).

### 6. Run the coordinate loop

Follow `/coordinate-research-goal` for every batch:

1. Start ≤ `max_concurrent` (≤ 3) non-archive ready tasks with disjoint
   `write_scope`, via the matching subagent role
   (`.claude/agents/{coordinator,idea-generator,executor,validator,red-team}.md`).
2. On producer terminal: Coordinator-only `snapshot` archive alone; verify
   via dispatcher/Git before any review reads artifacts.
3. Independent Reviewer / Validator / Red Team as required (`review-xhigh`
   policy; independent session; never the producing agent alone on claim-changing
   results).
4. Coordinator-only `ledger` archive alone; verify parent, paths, hashes,
   record IDs.
5. Update the `GOAL-*` record in that ledger commit: batch checkpoint, decision
   refs, `latest_verified_commit`, exactly one `next_action`. Rerank only after
   the verified checkpoint.
6. Regenerate the dispatch plan; open the next bounded batch while status is
   `active`.

Lifecycle stage skills when a ready task maps to them: `/propose-ideas`,
`/design-experiment`, `/run-experiment`, `/review-evidence`,
`/curate-knowledge`.

Handoffs live in `ledger/handoffs/` (envelope in `AGENTS.md`). Task cards and
receipts stay under the batch/task `write_scope`.

### 7. Stop conditions

Stop the harness when any of these hold:

- User asks to stop or pause.
- Goal reaches a declared `completion_criteria` via committed Coordinator
  decision **and** the three-model closure quorum concurs → mark `completed`
  only then. Three CONCUR attestations with pairwise-distinct
  `resolved_model_id` (AGENTS.md rule 13). A criterion met without the quorum
  does not close the goal; a quorum without a met criterion does not either.
- A declared `pause_conditions` item triggers (budget exhausted, archive
  verification failure, unresolved required model policy with
  `fallback_allowed: false`) → mark `paused` with a concrete resume action.
- Required model policy cannot be honored without silent downgrade — refuse
  and pause rather than substitute.
- Three distinct models cannot be resolved for a closure quorum → leave the goal
  `paused` and say closure was blocked on model availability, not on the
  research. Never record a quorum you did not obtain.

A failed candidate, empty ready set, or timeout is scoped evidence, not goal
completion: record it and set the next action.

## Safety rules (non-negotiable)

- Only the Coordinator changes official hypothesis/goal status or shared ledgers.
- Snapshot archive before independent review; ledger archive before promotion.
- Never fabricate commands, outputs, timings, statistics, citations, or runs.
- Infra failures/timeouts are not mathematical counterevidence.
- Toy-curve results never become crypto-scale claims.
- Record requested policy + resolved model; no silent policy downgrade.
- Workers do not commit into a shared worktree; Coordinator archive tasks alone
  stage declared paths and must pass post-commit verification.
- At most three concurrent non-archive tasks; do not fill idle slots without a
  ranked next action.

## Output after each batch (and on stop)

Report: goal ID + status; completed task IDs + verified commits; evidence /
decision IDs with claim boundaries; knowledge promotions or `not_warranted`
reasons; exact next action (or pause/complete rationale).

## Quick examples

```text
User: run the harness for GOAL-ECDLP-001
→ status scan → bind GOAL-ECDLP-001 → render its dispatch_queue_path →
  execute ready tasks → snapshot → review → ledger → rerank / next batch

User: continue the active ECDLP goal
→ prefer matching active GOAL-* → same loop from next_action

User: launch a new research goal for RQ-SSI-001
→ create GOAL-SSI-00N + BATCH-001 → snapshot → then coordinate loop
```
