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
5. A Coordinator-only snapshot task commits a producer's exact artifacts before
   any dependent review begins.
6. A Coordinator-only ledger task commits reviews, evidence, decisions, and
   theory/status records before an official state transition.
7. The Coordinator records a terminal task state, regenerates the dispatch
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

## Which agent runs a task, and how hard it thinks

A queue task names a `role`; its optional `inference.policy` names a tier
within that role. The pair selects the agent, and the agent carries the
reasoning effort `orchestration/model-policies.yaml` calibrates for that policy:

| `role` | `inference.policy` | agent | effort |
|---|---|---|---|
| `executor` | `executor-mechanical` | `executor-mechanical` | low |
| `executor` | `executor-implementation` | `executor` | medium |
| `coordinator` | `coordinator-orchestration-code` / `-orchestration` | `coordinator` | high |
| `idea-generator` | `research-deep` | `idea-generator` | high |
| `validator` / `reviewer` | `review-adversarial` | `validator` | xhigh |
| `red-team` | `review-adversarial` | `red-team` | xhigh |
| `validator` / `reviewer` | `review-breakthrough` | `validator-breakthrough` | max |
| `red-team` | `review-breakthrough` | `red-team-breakthrough` | max |

The `-breakthrough` and `-mechanical` agents are **policy-tier variants**
declared in `orchestration/roles.yaml` with `variant_of`: same contract, same
authority, same tools, different depth. `tools/check_runtime_bindings.py`
enforces that — a variant that changed authority, or a binding whose `effort`
stopped matching its policy, fails the build rather than dispatching quietly.

Three rules follow, and none of them is a matter of judgement at dispatch time:

- **The tier is chosen by `routing_rules`, not by the dispatcher's sense of
  importance.** `claimed_breakthrough`, a proposed closure, or a result
  contradicting prior validated evidence routes to `review-breakthrough`.
- **No silent downgrade.** `review-breakthrough` is `degradable: false`:
  dispatching `validator` where `validator-breakthrough` was required is a
  policy violation, not a shortcut. If the tier cannot be served, the goal
  pauses.
- **Independence is per-session.** An independent review is a fresh agent
  invocation. Continuing the producing agent's session to obtain a review
  carries the producer's context and is exactly what
  `independent_session_required` exists to prevent.

Roles keep their canonical names in queues and handoffs
(`tools/research_dispatch.py` ROLES is unchanged) — the variant is a runtime
binding choice, not a new participant in the research contract.

## State and dependency rules

`queued` tasks can be selected only when every `depends_on` task is
`completed`. `running` tasks consume a slot. `failed`, `invalid`, and
`cancelled` tasks block their successors; they are not evidence against the
mathematical hypothesis unless their immutable run receipt says so.

The planner detects overlapping write scopes. A validator should therefore
write a separate report, such as `coordination/tasks/TASK-VAL-001/`, rather
than modifying `experiments/EXP-.../runs/...` while the Executor owns that
package.

## Commit and ledger gate

Every task declares exact `artifact_paths` under its own `write_scope`. Those
paths are not considered durable until an archival task claims them. An
archival task is a Coordinator task with an `archive` object:

- `kind: "snapshot"` commits the exact artifacts from a producer before a
  Validator, Reviewer, or Red Team reads them.
- `kind: "ledger"` commits the remaining review artifacts plus the required
  `ledger/evidence/` and `ledger/decisions/` records before a claim changes
  official status.

An archive task depends directly on every task whose artifacts it commits, and
it runs alone. This is deliberate: several workers can produce disjoint
artifacts concurrently, but they must not race on one Git index or `HEAD`.
The archive receipt names the target commit, its parent, the declared record
IDs, and a SHA-256 binding for every committed path. When an archive task is
marked complete, the dispatcher checks Git and rejects the result unless that
commit is reachable from `HEAD`, has the expected parent, changes exactly the
declared paths, and matches the recorded hashes.

For a ledger archive, its own artifact paths must include exact files under
both `ledger/evidence/` and `ledger/decisions/`; each filename must contain an
ID listed in `archive.record_ids`. This mechanically binds the commit receipt
to the immutable evidence and decision records it claims to preserve.

Each non-archive task must be claimed by exactly one archive task. Thus a
theory proposal, run package, validation report, red-team report, ledger
record, or knowledge item cannot silently remain only in a working tree.
Claim-relevant producers require both a snapshot archive before independent
review and a ledger archive after every required review.

## Persistent goals

`/coordinate-research-goal` binds a queue to a committed
`ledger/goals/GOAL-<AREA>-<tok>.yaml` record. New goal IDs use the random
six-hex token returned by `tools/allocate_id.py --next goal --area AREA` and
confirmed with `--check`; an existing three-digit legacy ID remains valid and
is carried unchanged. The record names the objective,
success and stop conditions, current queue, last decision, and exactly one next
action. Set the queue's optional top-level `goal_id` to that same record. It
remains `active` across snapshot/review/ledger cycles. A negative,
invalid, or inconclusive task narrows the route and creates a successor action;
it does not complete the larger research goal.

## Example lifecycle

```text
TASK-EXEC-001 (Executor)
  └─> TASK-SNAPSHOT-001 (Coordinator Git snapshot)
        ├─> TASK-VAL-001 (Validator)
        └─> TASK-RT-001 (Red Team)
TASK-VAL-001 + TASK-RT-001
  └─> TASK-LEDGER-001 (Coordinator Git ledger commit)
```

`TASK-LEDGER-001` commits the review reports and ledger evidence/decision
records, then records one of: replicate, expand, refine, scoped rejection,
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

Set `max_concurrent` to what the environment can run without degrading, not
to fill idle capacity. The tooling's fixed ceiling of three was removed on
explicit user direction (2026-08-05; see `MAX_CONCURRENT_CEILING` in
`tools/research_dispatch.py`), so nothing in the dispatcher itself will stop
an oversized value — sizing it is the dispatching Coordinator's job. More
task cards provide dynamic continuity; they do not justify starting more work
than can be independently reviewed.
