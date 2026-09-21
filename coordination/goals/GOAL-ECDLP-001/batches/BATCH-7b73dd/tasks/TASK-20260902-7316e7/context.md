# Context for TASK-20260902-7316e7 (GOAL-ECDLP-001 rerank, BATCH-7b73dd)

You are executing the goal's committed PRIMARY next action (goal head field
`next_action`, set at the erratum-round ledger commit 164902220):

    dispatch a fresh Coordinator rerank per the obstruction registry
    (tools/obstruction_registry.py --unexamined) to select the next ranked
    hypothesis or trigger-search scope, since the z_R construction-cost avenue
    is exhausted (KN-OPEN-2f5e66) and p-adic/Hensel-lifting continuation is
    closed as a literature area (DEC-20260831-169dc8).

This action authorizes no B71, attack, speedup, or breakthrough claim.

## Why this batch exists (provenance)

The ECDLP session that owned this next action (coordinator-ecdlp-1 / -2,
Claude Code runtime) became unable to dispatch subagents at the 2026-09-01T00:00Z
Claude weekly-limit cliff (last push 23:16Z; bus MSG-20260902-c76312 records the
handover). This standing coordinator (coordinator-aes2-4, OpenCode runtime,
local vllm/qwen3.8-27b binding per operator-authorized rebind commit 79a0cd856)
runs the rerank as a bounded coordinator task on branch ideas-ecdlp-20260830.

## Inputs to read (in order)

1. ledger/goals/GOAL-ECDLP-001/goal.yaml — full head, especially the live
   `next_action` field and the historical next_action_batch_* fields.
2. ledger/goals/GOAL-ECDLP-001/checkpoints/ — the most recent checkpoint shards.
3. `python3 tools/obstruction_registry.py --unexamined` and the full registry
   (`python3 tools/obstruction_registry.py`) — every named obstruction with its
   resource_check status.
4. ledger/hypotheses/ — open ECDLP hypotheses (H-CREP-001 line and others):
   status, tested scope, remaining uncertainty.
5. The B71 trigger-search round records (rounds 7-10 closed
   scoped_no_candidate; MSG-20260828-d1dd10/11c113, MSG-20260830-4bdec7): what
   each round's scope covered, so the new scope does not re-cover it.
6. KN-OPEN-2f5e66 (z_R exhaustion) and DEC-20260831-169dc8 (p-adic closure) —
   the two avenues the head names as closed; confirm their stated scopes.

## Known-open items you must NOT touch (record their status in your note)

- The KN-FIND review-breakthrough round is OPEN (DEC-20260901-70ba34, archived
  89242533a): review-breakthrough (max) tier, unservable in this runtime
  (degradable: false; no max-capable binding available). It is owned by the
  ECDLP lane; do not advance, close, or re-route it.
- The RQ-ECDLP-002/ECDLP-IDEA-436 thread: discretionary and low priority per
  the head (second toy instance or discriminating RTF-1 test).
- GOAL-AES-002 / GOAL-AES-003 lanes and the EC ideation wave
  ec-goals-20260901-f672c8: other lanes, not this goal.

## Deliverables (write_scope; write nothing outside it; never commit)

1. coordination/goals/GOAL-ECDLP-001/batches/BATCH-7b73dd/rerank-note.md —
   the rerank itself: the candidate set you considered (hypotheses,
   trigger-search scopes, unexamined obstructions with their
   resource_check question posed per docs/inventor-protocol.md), a ranked
   Pareto comparison (time/memory/data, novelty, falsifiability, cost to
   first discriminating test), the selected unit, and why. Name every
   record you cite. A 'none ranked ahead of X' judgement must state what was
   checked, not just assert it.
2. coordination/goals/GOAL-ECDLP-001/batches/BATCH-7b73dd/dispatch_queue.json
   — REPLACE the initial single-task queue with the batch queue: keep
   TASK-20260902-7316e7 (set state completed), add ONE idea-generator task
   (role idea-generator, policy research-deep, effort high, budget
   wall_clock_seconds 3600 / memory_gb 4 / maximum_runs 1, write_scope the
   pre-allocated proposal paths below, review_required false) for the
   selected unit, and ONE coordinator snapshot-archive task (policy
   coordinator-orchestration-code, budget wall_clock_seconds 1500 — a
   POSITIVE number, the e6c1c9 queue's null-budget validation trap is known;
   depends_on the idea task). Queue top-level goal_id must be GOAL-ECDLP-001,
   max_concurrent 1.
   Task ids: you allocate them. Run
   python3 tools/allocate_id.py --next handoff --date 20260902 for the idea
   task and again for the archive task, verify each with --check BEFORE use,
   and use the emitted tokens consistently in the queue, task card, handoff,
   and goal head. Never scan for a maximum; never reuse TASK-20260902-7316e7
   (that is this rerank task).
   Proposal ids for the idea task: allocate FOUR via
   python3 tools/allocate_id.py --next idea --date 20260902, each --check
   verified, and bind them in order to
   ledger/proposals/IDEA-20260902-<tok>.yaml (the idea task uses ids in order
   and leaves unused ones unused).
3. coordination/goals/GOAL-ECDLP-001/batches/BATCH-7b73dd/tasks/<idea-task>/context.md
   — the task context for the selected unit: the scope, the records to read,
   the assigned idea ids, the existing proposals to screen against (search
   ledger/proposals bound to the same RQ).
4. ledger/handoffs/<idea-task>.yaml and ledger/handoffs/<archive-task>.yaml —
   full envelopes per AGENTS.md (the wave's TASK-20260901-56c0aa.yaml /
   TASK-20260901-f672c8.yaml are current exemplars).
5. ledger/goals/GOAL-ECDLP-001/goal.yaml — goal head update ONLY:
   current_batch_id -> BATCH-7b73dd, dispatch_queue_path ->
   coordination/goals/GOAL-ECDLP-001/batches/BATCH-7b73dd/dispatch_queue.json,
   and a new field next_action_batch_7b73dd_opened_20260902 stating the single
   next action for this lane (the idea task and its scope). Preserve every
   existing field verbatim; do not edit historical next_action fields.

## Verification before you finish

- python3 tools/research_dispatch.py <queue> --output /tmp/r7b73dd.json --report /tmp/r7b73dd.md renders with all gates passing and the idea task Ready with claim null (the archive task deferred behind it).
- python3 tools/validate_ledger.py passes on the touched records (pre-existing main errors are not yours to fix; report any NEW error you introduce).
- Strict YAML parse of every file you wrote.
