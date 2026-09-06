# Concurrent goal lanes: several sessions on one `GOAL-*`

**Status:** binding for every runtime from the merge of this document.
**Tooling:** `tools/goal_lanes.py`, `tools/research_dispatch.py --claims`.
**Tests:** `tools/test_goal_lanes.py`, `tools/test_research_dispatch.py`.

## The problem, stated exactly

On 2026-08-25 two harness sessions were launched against GOAL-ENDO-001 within
minutes of each other. The second one could do nothing: BATCH-90392b was open,
its producer was already running in the first session's worktree, and every
rule in the harness said the right thing — do not dispatch a duplicate
producer, do not edit a queue another coordinator is editing, do not open a
second batch by rewriting the goal head the first session is about to rewrite.
The second session's only options were to wait for the first to finish or to
work a different goal.

That is not a scheduling accident; it is a consequence of where two facts were
stored:

| fact | where it lived | who had to write it |
|---|---|---|
| "task T is being worked by session S" | `state: running` (+ optional `lease`) **inside** `dispatch_queue.json` | every session that starts a task, in the one file every session on the batch edits |
| "batch B is open on goal G" | scalar `current_batch_id` / `dispatch_queue_path` / one `next_action` **inside** `goal.yaml` | every session that opens a batch, in the one file every session on the goal edits |

Both are the failure mode CLAUDE.md "Concurrency" names — *a writer made to
write shared state it had no reason to write* — and both are fixed the same
way the bus receipts, identifier minting, and checkpoint shards were fixed:
**one write-once file per fact, with a name no two writers can both choose.**

## The mechanism

```text
<batch>/claims/<TASK-ID>.<epoch>.claim.json       "S holds T's write_scope until time X"
<batch>/claims/<TASK-ID>.<epoch>.release.json     "S ended epoch e with outcome O"
coordination/goals/<GOAL>/lanes/<BATCH>.lane.json "B is open on G, branch R, opened by S under DEC-…"
coordination/goals/<GOAL>/lanes/<BATCH>.closed.json
```

### Claims

For expired claims whose original runtime cannot be identified, use
[isolated successor recovery](isolated-task-recovery.md). Unknown process state
does not mean stopped, but it must not become an indefinite scheduling veto.
Do not release as another owner; use a new bounded decision and disjoint
successor namespace when recovery is justified.

A **claim** is a bounded hold on one queued task's `write_scope`.

- Created with `O_EXCL`; never rewritten. `epoch` is per task and strictly
  increasing — a fencing token, so a session that comes back from the dead
  cannot release or renew a hold a newer session has taken.
- Carries `expires_at`. A crashed session frees its scope by doing nothing;
  nobody edits a record to reclaim it. Size `--ttl-minutes` to the task's
  `budget.wall_clock_minutes` plus review slack, not to "forever".
- A **release** ends the claim early with `completed | failed | abandoned`.
  Only the owner of the live epoch may release (fencing). `completed` is
  final: the task is then the Coordinator's to archive, and cannot be
  re-claimed.
- Claims are made only on tasks whose queue `state` is `queued`. A task the
  Coordinator has already recorded as `running`, `completed`, or terminal has
  more truth in the queue than a claim could add.

```sh
python3 tools/goal_lanes.py claim   <queue.json> TASK-… --as coordinator-endo-2 --ttl-minutes 120 --publish
python3 tools/goal_lanes.py release <queue.json> TASK-… --as coordinator-endo-2 --outcome completed --publish
python3 tools/goal_lanes.py claims  <queue.json>            # every task's current hold, across refs
```

### The dispatcher reads claims; it never writes them

`tools/research_dispatch.py --claims {off,local,refs}` (default `local`)
overlays claims on a **copy** of the queue before selection. The queue file on
disk is untouched.

| claim state on a `queued` task | plan treats the task as | why |
|---|---|---|
| `live` | `running`, with a lease derived from the claim | scope held; counts toward `max_concurrent`; listed under Ready Tasks with `claim: {owner…}` so you **do not start it** |
| `expired` | *unchanged* (`queued`, scope free) and listed under **Expired Leases** with `source: claim` | the task is offered again; the next session claims it at `epoch+1`, and the previous owner's silence is on the record |
| `released: completed` (producer) | `completed` | so its successors become ready for whoever claims them next |
| `released: completed` (archive) | *unchanged* | an archive is complete only when its commit verifies; that binding is in the queue's `archive` block, written by the Coordinator |
| `released: failed \| abandoned` | *unchanged* (`queued`, scope free) | reported; the Coordinator decides on a repair or successor |
| any, on a task whose `depends_on` this reader has not seen complete | *unchanged*, reported as `ignored:dependencies_incomplete_from_this_view` | a claim made from a worktree that had fetched more than this one is a fact this plan cannot yet admit, not a broken queue |

The plan's new `claims` block and gate `claimed_tasks_are_not_offered_to_others`
make the overlay auditable. **Start only Ready Tasks whose `claim` is `null`,
and claim each one before launching its subagent.**

### Lanes

A **lane** is an open batch on a goal. One goal may have several.

- `open-lane` writes the write-once lane record; it refuses a second record
  for the same batch and a queue path outside the batch directory.
- Lanes are disjoint by construction: each has its own batch directory, mints
  its own `BATCH-*`/`TASK-*`/`EV-*`/`DEC-*` tokens (never scanned), writes its
  own checkpoint shard under `ledger/goals/<GOAL>/checkpoints/`, and lives on
  its own branch with its own PR.
- The one file lanes would otherwise share is `goal.yaml`. A lane edits it
  **only inside its own ledger archive, only additively**: it appends its
  `open_batches` entry, its checkpoint pointer, and its own `next_action`
  line. It never rewrites another lane's entries. `current_batch_id` becomes
  "the lane opened most recently" — a pointer, not a lock.
- `close-lane` records that the lane's ledger archive landed (or that it was
  abandoned/superseded), with the closing `DEC-*` and commit.

```sh
python3 tools/goal_lanes.py lanes GOAL-ENDO-001                      # what is open, on which branch, by whom
python3 tools/goal_lanes.py open-lane GOAL-ENDO-001 BATCH-<tok> \
    --queue coordination/goals/GOAL-ENDO-001/batches/BATCH-<tok>/dispatch_queue.json \
    --decision DEC-<…> --objective "…" --as coordinator-endo-2 --publish
python3 tools/goal_lanes.py close-lane GOAL-ENDO-001 BATCH-<tok> --outcome archived \
    --decision DEC-<…> --ledger-commit <sha> --as coordinator-endo-2 --publish
```

### Visibility is git, and it is a feed

Every reader scans `git log --all --diff-filter=A -- <prefix>` — one call,
about a second with 400+ remote refs — so a claim or lane pushed from any
worktree is visible to every other after `git fetch`. `--publish` commits the
new file on the current branch and pushes it; `--no-push` commits only.

This is a **feed, not a lock server**, same as the bus and the merge digest.
Two sessions that claim the same task within one fetch interval both succeed
locally and discover the collision on the next scan. The rule is mechanical:
**the lower epoch wins; the other releases as `abandoned` and moves on.** The
window is seconds wide and is the price of having no server that outlives the
session holding the lock.

## What this changes in the harness

- **Another session on the same goal is not a stop.** `launch-research-harness`
  step 3 no longer treats a goal being worked elsewhere as unavailable. List
  its lanes; if the open lane's plan has unclaimed Ready Tasks you are
  permitted to run, claim one and run it; otherwise open a disjoint lane
  against the goal's ranked candidates.
- **Claim before launch, release on return.** Every subagent launch of a Ready
  Task is preceded by a published claim and followed by a published release.
  The task receipt records the claim epoch.
- **Independent review stays independent.** A claim on a review task by a
  session that did not produce the artifact is exactly the fresh, disjoint
  session `review-adversarial` asks for. The blindness rule (no sibling
  report reads) is unchanged and is checked by
  `tools/check_review_independence.py` as before.
- **Archive tasks stay Coordinator-only and run alone**, but *which*
  coordinator session runs one is whoever holds its claim. Claiming an
  archive task means being the session that commits it; the queue's own
  `state`/`archive` fields are still written by that commit's author, and the
  post-commit verifier still decides whether it is official.
- **Goal head edits are additive per lane.** "Exactly one next action" is now
  "exactly one next action per lane"; the goal's ranked candidate list is what
  a new lane draws from.

## What this does not change

- Nothing here approves an experiment, moves a hypothesis, or stands in as
  evidence. A claim is a pointer to who is working, never a permission.
- Rule 4/6 scoping, the review tiers and their `degradable: false` policies,
  and the snapshot-before-review / ledger-before-promotion order are untouched.
- `max_concurrent` is still the batch's declared cap and still has to fit the
  machine; claims from other sessions count toward it because their work runs
  on the same repository, and often the same host.
- Queues written before this document need no migration: with no `claims/`
  directory the overlay is empty and the plan is byte-identical to before.

## Cost, stated plainly

- The feed window above: a same-task double claim is possible for a few
  seconds and is resolved by epoch, not prevented.
- One extra small commit per claim/release/lane when `--publish` is used.
  That is the point — the fact is durable and visible — but it does mean
  branches carry control-plane commits alongside research commits. Archive
  commits still exclude `dispatch_queue.json` and should exclude `claims/`;
  the claim commit is its own commit.
- A lane's ledger archive still edits `goal.yaml`. Two lanes archiving in the
  same minute can still conflict on that file at merge time; because the edits
  are additive and disjoint, the merge is mechanical, but it is still a merge
  a human or `sync_open_branches.py` performs. Sharding the goal head
  entirely (one file per lane) would remove even that and is the natural next
  step if it happens often.
