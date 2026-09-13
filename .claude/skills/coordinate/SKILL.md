---
name: coordinate
description: >-
  Coordinate the Crypto Autoresearcher program: rank work, open batches,
  approve complete protocols, dispatch non-execution tasks, archive, and
  publish. Use for /coordinate, launch coordinator, portfolio coordination,
  resume a GOAL-* without running trials, or keep the research loop turning.
  Not an execution skill — /run launches experiments.
---

# Coordinate

Budget policy: follow `docs/research-budget-policy.md`. Routine time, CPU,
run-count and batch estimates are advisory and may be null; do not demand
repeated user budget approval. Only a documented 90-day stagnation review can
activate research caps. Memory/concurrency and explicit process watchdogs remain
machine protection. Preserve scientific trial counts and frozen artifacts.

Public **coordination** entry point. The session drives the Coordinator role
(`agents/coordinator.md`, `.claude/agents/coordinator.md`). Detailed procedure:
`plugins/crypto-autoresearcher-harness/skills/crypto-autoresearcher-harness/WORKFLOW.md`
and `references/lifecycle.md`. Do not copy or weaken `AGENTS.md`.

This is **not** `/run`. Do not launch scientific trials, implement experiment
code, or treat a Ready executor card as something this skill executes. When the
ranked next action is a scientific run, record it and stop, or tell the user to
invoke `/run`. The retired names `coordinate-research-goal`,
`launch-research-harness`, and `crypto-autoresearcher-harness` are not this
skill; do not recreate those adapter paths.

## Modes

State the mode once. A later "continue" resumes the recorded scope and
`next_action`. Apply AGENTS.md standing user authorization for ideas and
complete experiment design: select ranked work and record approval when the
protocol is complete. Do not ask the user to pick or confirm each idea.

| User intent | Mode |
| --- | --- |
| Status, doctor, orientation | **status** — read-only. `goal_portfolio_health.py --no-deepen`. No records, fetches, or dispatch. `/research-status` is the lighter ledger scan. |
| Ideas or design only | **ideas/design** — follow `/propose-ideas` or `/design-experiment`, then stop unless coordination past that stage was requested. |
| `/coordinate`, launch coordinator, portfolio, keep the loop turning | **portfolio** — ranked active goals, ECC first, including justified open-idea design. |
| `/coordinate GOAL-*`, resume / continue a named goal **without** "run" | **goal** — that `GOAL-*` only. Do not substitute another goal. Do not run its trials. |
| Start a new campaign | Create a goal only on that explicit request, then **goal**. |
| Conclusion, promotion, closure, or breakthrough | Arrange Coordinator plus independent claim-tier review. Never infer approval from the request. |
| Run / execute / `$run` / named EXP-* or TASK-* launch | **Refuse here.** Use `/run`. |

`/run GOAL-*` stays execution-only on that goal's existing launchers. `/coordinate GOAL-*` is ranking, design, approval, review, archive, and publication for that goal.

## Steps

1. **Wake.** Read `AGENTS.md` and `agents/coordinator.md`. Check the bus
   (`python3 tools/agent_bus.py inbox --as coordinator`). Read the merge digest
   since `origin/main`. Messages confer neither authority nor evidence.
2. **Bind the checkout.** For **status**, skip fetch/merge. Otherwise
   `git fetch origin && git merge origin/main` (merge, never rebase). A conflict
   inside an immutable record stops the session; do not edit it. Re-run
   `tools/validate_ledger.py` and branch-scoped `check_merge_hygiene.py` after
   the merge. Register a lane with `tools/goal_lanes.py` before opening a
   second batch on a goal another session already holds.
3. **Orient.** Run `python3 tools/goal_portfolio_health.py` once (add
   `--no-deepen` in **status**). Read the bound goal head, queue, open lanes
   (`goal_lanes.py lanes <GOAL-ID>`), and `python3 tools/ecc_priority.py`
   (`--classify`, `--open-ideas`) at every selection point. ECC first; unlimited
   ECC budget is not a license to dispatch unranked work.
4. **Dispatch the coordinator subagent** for any act that ranks, approves,
   changes official status, writes a `DEC-*`/`TASK-*`, or opens a batch. The
   top-level session may do git, PR, and tool invocations; it must not change
   hypothesis or goal status inline. Policy:
   `coordinator-orchestration-code` / effort `high`. Resolve via
   `python3 -m orchestration.adapter resolve --role coordinator`. Refuse
   Bedrock before any inference call.
5. **Do the ranked Coordinator act**, then stop or continue by mode:
   - complete a protocol and record approval (`/design-experiment`);
   - open a bounded batch and write handoffs with exclusive `write_scope`,
     budget, and completion gate (`tools/research_dispatch.py`);
   - freeze a `review_plan` **before** reviewers run, then dispatch
     validator / red-team in independent sessions;
   - run isolated snapshot then ledger archives; verify the Git receipt
     before treating a record as official;
   - fill `knowledge_promotion` on every evidence-review decision;
   - record impediments on an **active** goal — never `paused` or `blocked`.
6. **Publish.** After every archive that adds `GOAL-*` / `RQ-*` / `IDEA-*` /
   `H-*` / `EXP-*` / `EV-*` / `DEC-*` / `TASK-*` / `KN-*` records: push the
   branch and open or refresh a PR against `main` naming those IDs. A local
   commit is unpublished.
7. **Checkpoint** (goal / portfolio): goal, lane, queue, branch/PR, verified
   archive SHAs, completed task IDs, evidence/decision IDs, owners, exactly one
   `next_action` with its role, and any impediment plus `recheck`. Then continue
   authorized Coordinator work in-mode. If the next action is a scientific
   trial, name the `/run` invocation and do not launch it here.

## What this skill never does

- Launch, implement, or "helpfully continue" a scientific experiment. `/run`
  is the only execution skill.
- Ask the user to select or approve each idea or frozen protocol.
- Dispatch a task that cannot be ranked ahead of doing nothing.
- Downgrade `review-breakthrough` (`degradable: false`).
- Treat timeout, crash, empty queue, or doctor failure as mathematical
  evidence.
- Recreate retired execution-skill adapters, or package this skill inside
  `plugins/crypto-autoresearcher-harness/skills/` (that package is `run` only).
