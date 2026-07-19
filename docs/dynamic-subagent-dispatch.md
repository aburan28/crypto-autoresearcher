# Dynamic Subagent Dispatch

This layer decides *which bounded tasks are ready now* and assigns them to
independent roles. It does not execute experiments, change research status, or
turn a receipt into a conclusion.

## Dispatch loop

1. The Coordinator freezes an approved experiment or review task as a task
   card in a dispatch queue.
2. `tools/research_dispatch.py` validates task IDs, dependencies, budgets,
   role, completion gates, and exclusive write scopes.
3. The tool emits only the currently ready tasks, limited by `max_concurrent`.
4. Agents write only under their assigned `write_scope` and return an immutable
   receipt or report.
5. The Coordinator records a terminal task state, regenerates the dispatch
   plan, then reranks research priorities before admitting successors.

The queue is an append-only coordination history in practice: do not erase a
failed task. A repair uses a new task with a new ID and an explicit dependency
or rationale.

## Roles and handoffs

Use the roles as a research cell, not a collection of agents all attempting
the same broad objective:

| Role | Owns | May conclude |
|---|---|---|
| Coordinator | queue, priority, official ledger | official state transition |
| Executor | one approved implementation/run package | observations only |
| Reviewer | independent claim and experiment review | review verdict |
| Validator | independent receipt/control checks | validity of a receipt |
| Red Team | cost/scope/falsification review | objections and next control |
| Idea Generator | one novelty-screened mechanism proposal | proposed hypothesis only |

For a result that could change an ECDLP claim, dispatch the Executor alongside
an independent Reviewer, Validator, or Red Team task where dependencies allow
it. Do not let the producing agent be the sole interpreter. Mark its task card
`review_required: true`; the queue validator then requires at least one
dependent independent-review task.

## State and dependency rules

`queued` tasks can be selected only when every `depends_on` task is
`completed`. `running` tasks consume a slot. `failed`, `invalid`, and
`cancelled` tasks block their successors; they are not evidence against the
mathematical hypothesis unless their immutable run receipt says so.

The planner detects overlapping write scopes. A validator should therefore
write a separate report, such as `coordination/tasks/TASK-VAL-001/`, rather
than modifying `experiments/EXP-.../runs/...` while the Executor owns that
package.

## Example lifecycle

```text
TASK-EXEC-001 (Executor) ──completed──> TASK-VAL-001 (Validator)
                                      └> TASK-RT-001 (Red Team)
TASK-VAL-001 + TASK-RT-001 ──completed──> TASK-COORD-001 (Coordinator decision)
```

`TASK-COORD-001` records one of: replicate, expand, refine, scoped rejection,
inconclusive, or pause. Only then may a new experiment be prioritized. A
passing validator confirms the receipt, not a better-than-rho result.

## Commands

Start from the template, replace placeholders, and keep it outside immutable
run directories:

```sh
python3 tools/research_dispatch.py coordination/dispatch_queue.json \
  --output coordination/current_dispatch.json \
  --report coordination/current_dispatch.md
python3 -m unittest tools/test_research_dispatch.py
```

Use a concurrency cap of at most three subagent tasks. More task cards provide
dynamic continuity; they do not justify starting more work than can be
independently reviewed.
