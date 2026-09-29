---
name: consolidate-lanes
description: >-
  Run a cross-lane consolidation pass over the agent bus: read traffic ACROSS
  lanes that cannot see each other and carry pointers between them, so two
  sessions circling one experiment find out before the second spends its
  budget. Use on a schedule (hourly to daily) while several sessions work one
  goal, when opening a second lane on a goal another session is already
  working, before approving a batch that overlaps another lane, or when asked
  to cross-pollinate or reconcile what parallel sessions are doing. Dispatches
  the consolidator subagent. Carries pointers, never findings; writes no
  ledger record and changes no status.
---

# Consolidate lanes

`inbox --as X` answers *what is waiting for X* — a worker's question. When
several sessions work one goal in separate lanes, **nobody asks the
portfolio's question**: are two lanes doing the same thing? Two Executors can
measure the same variant all day, each correctly addressing its own
Coordinator, and no inbox anywhere shows both.

Continuous cross-talk is not the fix — it collapses the diversity the lanes
were for. Let lanes diverge, then run **one pass** that reads across them.

Contract: `docs/inter-agent-messaging.md` ("The consolidation pass") and
`agents/consolidator.md`. Read both before anything non-obvious.

## Preconditions — check these first, and stop if they fail

1. **More than one lane is live.** `agent_bus.py peers` and
   `goal_lanes.py lanes <GOAL>`. One lane has nothing to consolidate across;
   say so and stop rather than running a pass that can only find nothing.
2. **You are not working the lanes you would read.** A consolidator that also
   works one of them carries its own lane's pointers outward and calls it a
   cross-cutting pass — the bias is invisible, because every carried item is
   individually true. This is why `consolidation-routing` sets
   `independent_session_required: true`. Dispatch the subagent (step 2) rather
   than doing the pass inline in a session that owns a lane.

## Steps

1. **Collect and survey.** Nothing delivers; the bus is a feed.

   ```sh
   python3 tools/agent_bus.py sync                                  # other containers
   python3 tools/agent_bus.py digest --since 36h --unconsolidated
   ```

   Pick the window from when the last pass ran, not from habit — `36h` for a
   daily cadence, `2h` for an hourly one. `--unconsolidated` hides traffic a
   previous pass already drew on, so a recurring pass sees only what is new.

2. **Dispatch the consolidator subagent** with the digest output, the goal(s)
   in play, and the window. It runs at `consolidation-routing` (effort `high`),
   independent of every lane. Give it the addresses of the live lanes so it
   knows who can be told what.

3. **It carries each item as its own message**, citing sources and refs:

   ```sh
   python3 tools/agent_bus.py consolidate --from consolidator --to <lane-addr> \
       --subject "<what this lane is about to spend, and what already exists>" \
       --source <MSG-id> --source <MSG-id> --ref <EXP-...> \
       --body "One sentence on why this matters to you. Then go read it."
   python3 tools/agent_bus.py sync --push
   ```

   `consolidate` refuses no `--source`, no `--ref`, or a ref naming no record.

4. **Report** the window, message and sender counts, what was carried and to
   whom, and what was considered and deliberately not carried. That last item
   is the one a reader cannot reconstruct from the bus.

## What is worth carrying

In rough priority order:

- two lanes pointing at the same `EXP-*`, `GOAL-*`, or `BATCH-*`;
- a lane about to spend budget on a measurement another lane has closed;
- a lane blocked on something another lane already resolved;
- a contract, protocol, or queue change one lane announced and another has not
  read.

Nothing else. **A pass that carries nothing is a successful pass** — report it
and stop. Ten pointers is not ten times better than one: every recipient pays a
wake for each, and a lane that learns to expect noise from the consolidator
stops reading it, which costs more than the pass ever returned.

## Running it on a schedule

The pass is periodic by design — that periodicity is what lets lanes diverge in
between. Cadence follows how fast lanes actually move: **hourly** while several
sessions are actively burning budget on one goal, **daily** otherwise. Below
hourly is noise; the lanes have not produced enough traffic to cross-pollinate.

Inside a session, `/loop 1h /consolidate-lanes`. Across sessions, a scheduled
trigger firing this skill into a session that owns no lane. Either way the
window in step 1 should match the cadence, or the pass re-reads the same
traffic and `--unconsolidated` becomes the only thing keeping it honest.

## Not this

- **Not a summary.** Carry the message id and the ref; let the reader read the
  record. Nothing reads the message body, so every check passes on a laundered
  finding — the discipline is the agent's, not the tool's.
- **Not authority.** A message is a pointer, never a permission: it cannot
  approve an experiment, move a hypothesis, or stand in as evidence.
- **Not work assignment.** Real work travels as a `TASK-*` handoff through
  `tools/research_dispatch.py`, with a write scope, a budget, and a completion
  gate. A lane that needs work done is told that in those words.
- **No ledger writes.** This skill changes no status and files no record.
