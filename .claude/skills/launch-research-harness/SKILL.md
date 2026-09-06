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

**The harness runs indefinitely.** It is a standing process, not a one-shot
errand: batches follow batches, and a goal reaching a terminal status hands off
to the next goal rather than ending the session. Only the conditions in
"Terminal stops" below end a run. Everything else — an empty ready set, a failed
candidate, an exhausted campaign budget, a completed goal — is a transition to
the next unit of work, taken through the standing loop in step 9. Indefinite
operation changes what you do when work runs out; it changes none of the
evidence, archival, or review rules, and it is never a licence to manufacture
work to stay busy.

Do not invent runs, timings, or review verdicts. Do not change hypothesis or
goal status outside Coordinator ledger archives.

## Required reads (once per session)

1. `AGENTS.md`, `CLAUDE.md`
2. `.claude/skills/coordinate-research-goal/SKILL.md`
3. `.claude/skills/research-status/SKILL.md` (read-only overview)
4. `docs/dynamic-subagent-dispatch.md`, `docs/task-lifecycle.md` (as needed)
5. `orchestration/model-policies.yaml` for role→policy aliases
6. `tools/goal_portfolio_health.py --help` if unfamiliar with the step 2.5 sweep

## Procedure

### 1. Research status (read-only)

Run the `/research-status` checklist and flag integrity issues (uncommitted
archives, broken refs). Its first two steps are tools, not a manual scan:

```sh
python3 tools/ledger_summary.py && python3 tools/validate_ledger.py
```

Do not mutate state in this step.

### 2. Discover goals

```sh
python3 tools/goal_head.py list --status active
```

That prints exactly the fields this step needs — `research_goal.{id,status,
title,current_batch_id,dispatch_queue_path,next_action}` — for every goal, in
~3k tokens (`--brief` drops the `next_action` prose for ~0.6k). Add
`python3 tools/goal_head.py show <GOAL>` for one goal's `campaign_budget`,
`completion_criteria` and `pause_conditions`, ~0.8k tokens.

**Never `cat` a goal record to get these.** The heads are append-only in
practice: 83% of their bytes are undeclared narrative keys, `GOAL-ECDLP-001`
is 651 keys and ~243k tokens, and reading all 102 the way this step used to
read is ~904k tokens. Every value the projection shortens is marked with the
command that returns it whole.

Those omitted keys are the campaign's history — why earlier batches closed,
what was superseded, which theories were refuted. They are preserved intact
and reachable; before re-opening a line of work, check whether it was already
tried and closed:

```sh
python3 tools/goal_head.py history <GOAL>              # dated index
python3 tools/goal_head.py history --grep '<term>'     # across all goals
```

Statuses: `draft | active | completed | cancelled | closed_at_budget`
(the tool also reports `unparseable` for a record that will not load — an
integrity signal, never a research state).

**There is no `paused` and no `blocked`.** Both were removed on user
instruction (2026-09-04); `tools/validate_ledger.py` refuses them by name. An
impeded campaign stays `active` and carries an `impediments` entry recording
what is blocked, what clears it, and the `recheck` that tests it. This is a
scheduling rule only — it is not licence to close a goal, to promote a claim
whose review tier cannot be served, or to spend past an exhausted budget. See
AGENTS.md "Goals are never paused".

Also note matching dirs under `coordination/goals/GOAL-*/batches/`.

### 2.5. Portfolio health sweep (mandatory, once per session)

**Run this before selecting a goal, every session.** This exists because the
harness used to stall goal-by-goal: a session would pick one `active` goal,
spend its whole context discovering its dispatch queue fails content-hash
verification or has nothing to run, then repeat that exact discovery on the
next goal with nothing recorded — every session paid the rediscovery cost
from scratch, and a single-goal deep dive reads as "stuck" even when the real
finding is portfolio-wide.

**Check for a shallow clone FIRST, before trusting any `needs_repair` result:**

```sh
git rev-parse --is-shallow-repository   # if "true":
git fetch --unshallow origin
```

A shallow clone makes `tools/research_dispatch.py`'s commit-reachability
checks fail for perfectly good, correctly-archived work whose commit is real
but older than the shallow fetch boundary, or on a branch never fetched deep
enough to see. This was discovered the hard way: a sweep once reported 31 of
47 active goals as `needs_repair` (widespread content-hash mismatches and
unreachable `commit_sha` values), which read exactly like the repository-wide
integrity failure this step exists to catch — but after `git fetch
--unshallow`, that dropped to 12. Nearly all of the apparent corruption was
the shallow clone, not `main`. The sweep tool detects this itself and prints
a warning (`shallow_clone_warning` in `--json` output, a stderr banner
otherwise). **The sweep now applies the fix itself**: on a shallow clone it
runs `git fetch --unshallow origin` and says so on stderr, so the results
below it are already trustworthy. It is a fetch — it only adds history, and
rewrites nothing. Pass `--no-deepen` to suppress that (offline, or when you
want the shallow behaviour deliberately); the `needs_repair` bucket is then
untrustworthy and the banner says so.

```sh
python3 tools/goal_portfolio_health.py
```

This renders `tools/research_dispatch.py` against every `active` goal's
current queue (read-only — it writes no ledger or coordination state) and
sorts the whole portfolio into three buckets in one pass:

- **ready** — dispatch succeeded and at least one Ready Task has `claim:
  null`. These are your candidates for step 3.
- **blocked** — dispatch succeeded but nothing is dispatchable right now
  (everything gated, claimed, or deferred). Ordinary campaign state, not a
  problem to chase.
- **needs_repair** — dispatch itself failed: a hash mismatch, an
  unreachable `commit_sha`, a malformed queue. This is an integrity problem
  with the queue or `main`, never a research result and never evidence about
  the goal's hypothesis (core rule 5). Do **not** spend this session's budget
  root-causing each one individually — record the bucket's contents in this
  session's report (goal ID + the one-line reason) and move on. Root-causing
  `needs_repair` at scale is separate remediation work, not a step of running
  a batch.

If `needs_repair` covers most or all of the active portfolio, that is itself
the finding: report it plainly (see "Terminal stops" — a ledger that will not
validate on `main` across many goals is a harness-wide integrity signal, even
when each individual dispatch error looks goal-specific) rather than
diving into one goal's history to explain it, unless the user asks for that
investigation specifically.

### 3. Select a goal

**ECC GOALS COME FIRST, ALWAYS.** Before applying the order below, partition
the candidates with `python3 tools/ecc_priority.py --classify <GOAL-ID>...` (or
read the `ECC` marker `goal_portfolio_health.py` now prints). A non-ECC goal is
selected only when NO ECC goal offers a ranked, justified task. The area set is
declared in `orchestration/research-priority.yaml` — never infer it from an
identifier prefix, since `GOAL-CRYPTO-001` is an ECDLP search and
`DREG`/`SDEG`/`SIG`/`MONO`/`RELN`/`ICEX` are Semaev machinery. Priority orders
the queue; it never manufactures ECC work, and never puts an unranked ECC task
ahead of a ranked non-ECC one already in flight. See AGENTS.md "ECC comes
first".

Then pick in this order, drawing only from the **ready** bucket unless noted:

1. Explicit `GOAL-*` in the user request — if it is not in `ready`, say which
   bucket it landed in and why (cite the sweep's reason) instead of silently
   substituting another goal.
2. Single `ready` goal that matches the request text or current branch/area.
3. Any other `ready` goal, highest ranked first, when the request names no
   specific one. In a standing run this is the ordinary case and needs no user
   prompt — the harness is expected to keep working the active portfolio.
4. Otherwise list every `active` goal with its open impediments (ID, batch,
   next action, `clears_when`) and ask which to run. No goal is ever `paused`,
   so nothing needs "resuming": an impeded goal is picked up like any other,
   and the first thing you do is run its impediment's `recheck` to see whether
   the blocker still holds. Do not silently resume a `completed` goal, and do
   not silently pick from `needs_repair` — a broken dispatch queue
   cannot safely launch a subagent against it.

If the `ready` bucket is empty, do not stop and do not fall back to
`needs_repair` — go to step 9's "when the portfolio is empty".

**Resume** an existing goal: use its `dispatch_queue_path` and
`current_batch_id`; continue from `next_action`.

**Another session already on this goal is not a stop.** Before treating a
goal as taken, `git fetch origin` and run
`python3 tools/goal_lanes.py lanes <GOAL-ID>`; for each open lane render its
plan with `--claims refs`. Then, in order: (1) if that plan lists Ready Tasks
with `claim: null` that your role table may run, claim one and run it under
that lane (its branch, its PR); (2) otherwise open a **disjoint lane** — a new
`BATCH-<tok>` against the goal's ranked candidates, registered with
`goal_lanes.py open-lane … --publish` before any worker runs, on its own branch
when a concurrent writer would otherwise race you on push and on the branch you
are already on when none would (step 8);
(3) only if neither is justified, pick another goal. A goal with no lane
records is worked the old way (one batch, via `current_batch_id`) until
someone opens a lane on it. Register on the bus under a distinct address
(`coordinator-<area>-2`, …) and post a pointer message naming your lane; the
message is a pointer, never a permission. See `docs/concurrent-goal-lanes.md`.

**Start new**: only when the user asks for a new campaign. Mint the goal with
`python3 tools/allocate_id.py --next goal --area AREA`, confirm the emitted
`GOAL-<AREA>-<tok>` with `--check`, and create its YAML record from
`templates/research-records.md`. Never choose a suffix or scan for a maximum.
Bind `RQ-*`, then create `coordination/goals/GOAL-.../batches/BATCH-<tok>/`
with handoffs + queue
(`goal_id` set), then follow `/coordinate-research-goal` launch steps.
Snapshot-archive the goal/queue/handoffs before any worker runs.

### 4. Bind committed state

Confirm before dispatching workers:

- Goal record is committed (or about to ride a Coordinator snapshot).
- `dispatch_queue_path` exists and queue top-level `goal_id` matches.
- Campaign budget still allows another batch. **ECC goals have an UNLIMITED
  budget** — `maximum_batches` and `total_wall_clock_seconds` are `null` and a
  finite value is a validation error, so this check is a no-op for them. It
  still binds for non-ECC goals. Unlimited removes the batch ceiling, NOT the
  duty to rank: never dispatch a task you cannot rank ahead of doing nothing,
  and `max_concurrent` stays bounded by real machine headroom. Fields
  (`maximum_batches`,
  `total_wall_clock_seconds`, and `max_concurrent` sized to what the
  environment can run without degrading — see "Concurrency" below). An
  exhausted budget stops *this campaign's spending*, not the harness and not
  the goal: record a budget impediment, leave the goal `active`, and move to
  the next one via step 9. Never quietly raise a budget to keep a campaign
  running — a budget extension is a Coordinator decision with a recorded
  rationale, and "goals are never paused" is not licence to spend past one.
- `next_action` is concrete; empty queue alone does not complete the goal.
- `goal_lanes.py lanes <GOAL>` and `goal_lanes.py claims <queue>` (after
  `git fetch`) show which batches are open elsewhere and which tasks are
  held. If you are opening a batch on a goal that already has an open lane,
  your batch is a second lane: `open-lane … --publish` it now.
- There is a working branch, it is pushed to origin, and it has an open PR
  against `main`. If not, create or adopt one, push it, and open the PR now —
  do not run a campaign that cannot surface its artifacts. **Which** branch is
  open to judgement: the branch the session is already on is fine, including
  one carrying unrelated work and one the runtime pins the session to. Step 8
  says when a campaign earns a branch of its own.
- The working branch is current with `main` (see "Branch and PR hygiene").

If a completion criterion already holds, stop and report. If a declared
`pause_conditions` item already holds, record it as an impediment, leave the
goal `active`, and move to the next goal — do not invent work to fill capacity,
and do not park the goal.

### 5. Render dispatch

From repo root, using the goal's queue path:

```sh
git fetch origin
python3 tools/research_dispatch.py <dispatch_queue_path> \
  --output <batch-dir>/dispatch_plan.json \
  --report <batch-dir>/dispatch_plan.md \
  --claims refs --now "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

`--claims refs` overlays every claim pushed from any worktree: a task held by
another session is listed as `running` with its `claim`, a completed release
unblocks successors, and an expired hold shows under Expired Leases. Only
Ready Tasks with `claim: null` are yours to start.

Use the paths the goal/batch already use (e.g. `dispatch_queue.json` or
`dispatch_queue.v2.json`). Fix validation errors before starting agents.
Execute only tasks listed under the plan's `dispatches` array (Ready Tasks).

### 6. Launch the subagents

**Ready tasks are executed BY SUBAGENTS, never by this session.** The top-level
session orchestrates: it renders the plan, launches agents, archives their
output, and reports. Doing a worker's job here loses the role's tool
restrictions, its reasoning-effort calibration, and — for review tasks — the
independence the policy requires.

**Pick the subagent from (queue role, `inference.policy`).** Each agent carries
its own reasoning effort, calibrated in `orchestration/model-policies.yaml` and
enforced against the binding by `tools/check_runtime_bindings.py`:

| queue `role` | `inference.policy` | `subagent_type` | effort |
|---|---|---|---|
| `executor` | `executor-mechanical` | `executor-mechanical` | low |
| `executor` | `executor-implementation` | `executor` | medium |
| `coordinator` | `coordinator-orchestration-code`, `coordinator-orchestration` | `coordinator` | high |
| `idea-generator` | `research-deep` | `idea-generator` | high |
| `validator`, `reviewer` | `review-adversarial` | `validator` | xhigh |
| `red-team` | `review-adversarial` | `red-team` | xhigh |
| `validator`, `reviewer` | `review-breakthrough` | `validator-breakthrough` | max |
| `red-team` | `review-breakthrough` | `red-team-breakthrough` | max |

A task that names no policy takes its role's `default_policy` from
`orchestration/roles.yaml`. Resolve any doubt with the table the harness itself
reads — never from memory:

```sh
python3 tools/check_runtime_bindings.py --list   # role → policy → effort → binding
```

Which tier a review gets is not a judgement call: `routing_rules` in
`model-policies.yaml` sends `claimed_breakthrough`, a proposed closure, or a
result contradicting prior validated evidence to `review-breakthrough`, and
that policy is `degradable: false`.

**Effort is a property of the agent, not of the call.** Do not pass a `model`
override to the Agent tool, and do not reach for a cheaper tier to get a stuck
task moving — substituting `validator` for `validator-breakthrough` is exactly
the silent downgrade the policy layer forbids. If the required tier cannot be
served, record an impediment against the CLAIM (step 4) and leave the goal
`active` — never a substitution. What is blocked is the claim's promotion, not
the campaign.

**How to launch:**

- Put every ready task with a disjoint `write_scope` in **one message, one
  Agent call each**, so they run concurrently. Separate messages serialize the
  batch and waste the whole point of `max_concurrent`.
- Never exceed the queue's `max_concurrent`, and size it to real headroom (see
  "Concurrency").
- **Independent review is a fresh Agent call.** Never continue the producing
  agent's session with `SendMessage` to obtain a review — a continuation
  carries the producer's context and is the opposite of the independent session
  `review-adversarial` and `review-breakthrough` require.
- Producers may run with `run_in_background: true`; the snapshot archive waits
  for their terminal results. Coordinator `snapshot` and `ledger` archive tasks
  run **alone**, never alongside other agents.
- Subagents do not spawn subagents. Nesting puts work outside the batch the
  Coordinator authorised.

**Claim before you launch, release when it returns.** For each task you are
about to start:

```sh
python3 tools/goal_lanes.py claim <queue> <TASK-ID> --as <your-bus-addr> \
  --ttl-minutes <budget.wall_clock_minutes + slack> --publish
```

A refusal means another session holds it — take the next unclaimed Ready
Task instead; never `--force` a live claim without a recorded reason. When the
agent returns, `goal_lanes.py release <queue> <TASK-ID> --as <addr>
--outcome completed|failed|abandoned --publish` and record the claim epoch in
the task receipt. The claim commit is its own commit; archive commits exclude
`claims/` exactly as they exclude `dispatch_queue.json`.

**Bind every prompt to the committed task card** rather than restating it:

```text
Execute task <TASK-ID> for goal <GOAL-ID>.

Read first, and follow exactly:
  - <batch-dir>/tasks/<TASK-ID>/task_card.yaml   (your task card)
  - ledger/handoffs/<TASK-ID>.yaml               (your handoff envelope)
  - AGENTS.md and your role contract

Snapshot commit to read (review roles): <sha>
write_scope: <exact paths>  — write nothing outside it; never commit.
Budget: <wall clock / trials / cells>.
Requested policy: <policy-id>. Record it alongside the model that actually
answered; if this session cannot honour it, refuse rather than downgrade.
Deliverable: <artifact_paths>.
Return only the output record your role contract declares.
```

**When an agent returns**, record its result in the task receipt and move to
the archive step. A returned artifact is not evidence until a Coordinator
archive commits it and the dispatcher's post-commit verifier accepts it.

### 7. Run the coordinate loop

Follow `/coordinate-research-goal` for every batch:

1. Start ≤ the queue's declared `max_concurrent` non-archive ready tasks with
   disjoint `write_scope` and `claim: null`, each claimed first and then run
   via the subagent chosen in step 6. Other sessions' live claims count
   toward the cap: their work runs on the same repository and usually the
   same host.
2. On producer terminal: Coordinator-only `snapshot` archive alone; verify
   via dispatcher/Git before any review reads artifacts.
3. Independent Reviewer / Validator / Red Team as required, at the tier step 6
   selects (`review-adversarial` → `validator` / `red-team`;
   `review-breakthrough` → `validator-breakthrough` / `red-team-breakthrough`).
   Fresh agent call, independent session; never the producing agent alone on
   claim-changing results.
4. Coordinator-only `ledger` archive alone; verify parent, paths, hashes,
   record IDs.
5. Update the `GOAL-*` record in that ledger commit: batch checkpoint, decision
   refs, `latest_verified_commit`, exactly one `next_action` **for this lane**,
   and — if the goal has lane records — your lane's `open_batches` entry,
   touching no other lane's. Then `goal_lanes.py close-lane … --publish`.
   Rerank only after the verified checkpoint.
6. Regenerate the dispatch plan; open the next bounded batch while status is
   `active`. Do not pause between batches for user confirmation — return to
   step 5 and keep going. When the goal leaves `active`, go to step 9.

Lifecycle stage skills when a ready task maps to them: `/propose-ideas`,
`/design-experiment`, `/run-experiment`, `/review-evidence`,
`/curate-knowledge`.

Handoffs live in `ledger/handoffs/` (envelope in `AGENTS.md`). Task cards and
receipts stay under the batch/task `write_scope`.

### 8. Branch and PR hygiene

Research only exists as durable evidence when it is committed AND pushed to a
branch that has an open PR against `main`. Two git duties ride alongside every
generation step — new goals, ideas, experiments, evidence, decisions, and
knowledge entries all require them.

**Which branch carries them is a judgement call, not a rule.** Nothing here
requires a branch per goal, per batch, or per lane. Run the campaign on the
working branch the session already has — including one carrying unrelated
work, one shared with another campaign, or one the runtime pins the session to
— and let a single PR carry several goals or batches when that is what the
situation gives you. Durability comes from the commit being pushed under an
open PR; keeping concurrent writers apart comes from disjoint `write_scope`,
lane registration, and task claims. Neither comes from branch topology, so a
campaign is never blocked, delayed, or re-targeted to another goal because the
"right" branch does not exist.

Take a separate branch when there is a concrete reason, and name it in the
batch report:

- Another session is writing concurrently and would otherwise race you on push.
- The campaign's archive must be reviewable or mergeable on its own, without
  dragging unrelated records along with it.
- A record or receipt must bind to a commit that unrelated work would disturb.

Absent one of those, prefer the branch you are on. Mixing campaigns in one PR
costs some review tidiness; stalling a campaign over branch layout costs the
research.

**Pull in changes from `main` before generating.** Before creating or resuming
a goal, and before each new batch, merge `origin/main` into the working branch:

```sh
git fetch origin
git merge origin/main          # merge, never rebase — AGENTS.md rule
```

Never rebase: the branch carries pushed run records and rebasing rewrites the
commits they were archived in. If the merge conflicts, do NOT resolve it by
picking a side — stop, report the conflict, and let the Coordinator create a
new superseding record (the same rule as any other immutable-record conflict).
After the merge, re-run the ledger validator (`tools/validate_ledger.py`) and
`tools/check_merge_hygiene.py` before dispatching workers.

**Open or update the PR when new records are generated.** Each time a snapshot
or ledger archive adds new `GOAL-*`, `RQ-*`, `IDEA-*`, `H-*`, `EXP-*`, `EV-*`,
`DEC-*`, `TASK-*`, or `KN-*` records, push the branch and open or refresh a PR
against `main`:

```sh
git push -u origin <branch>
gh pr create --base main --head <branch> --title "research: <summary>" --body "<records>"
# or, for an existing PR:
gh pr edit <number> --title "research: <summary>" --body "<records>"
```

Keep the PR open for the life of the campaign and mark it draft only while the
batch is mid-flight; it exists so the work is reviewable and mergeable, not as
a claim of closure. A goal, idea, or experiment that exists only in a local
commit is not generated — it is unpublished.

### 9. Standing loop: goal terminal → next goal

A goal ending is a campaign boundary, not the end of the run. When the selected
goal leaves `active`, record its terminal state properly and then re-enter the
loop at step 2:

- **Completed.** The goal reached a declared `completion_criteria` item via a
  committed Coordinator decision → mark `completed`. The three-model closure
  quorum that also gated this is **suspended** (AGENTS.md rule 13), so a met
  criterion now suffices; a quorum without a met criterion still does not close
  a goal. The decision record must name which criterion was met and cite the
  evidence for it. Then rediscover goals and select the next one.
- **Impeded — NEVER paused.** A declared `pause_conditions` item triggered
  (budget exhausted, archive verification failure, unresolved required model
  policy with `fallback_allowed: false`) → the goal **stays `active`**. Record
  an `impediments` entry naming what is blocked, what clears it, and the
  `recheck` that tests it, then select the next goal. `paused` and `blocked`
  are not permitted statuses and the validator refuses them (AGENTS.md "Goals
  are never paused").
  Not parking the goal is a scheduling change and nothing more. The pressure to
  keep running is still never a reason to press on through a triggered
  condition: an archive that will not verify, or a policy that cannot be
  honored, still halts *that work* immediately. What continues is the
  campaign's eligibility to be picked up again, not the blocked task.
- **Required model policy cannot be honored** without a silent downgrade —
  refuse the substitution, record the impediment against the affected CLAIM,
  and move on with the goal still `active`. The claim stays un-promoted. This
  is unchanged by the quorum suspension and by the no-pause rule: it governs
  review policies such as `review-breakthrough`, which is still
  `degradable: false`. If the policy is unresolvable for every goal in the
  portfolio, that is a terminal stop below.

**When the `ready` bucket is empty** — whether because there is no `active`
goal, or because the sweep put every `active` goal into `blocked` or
`needs_repair` — the harness still does not exit on that alone. In priority
order:

1. Re-check the open `impediments` on active goals and pick up any whose
   `clears_when` is now demonstrably satisfied (budget renewed by decision,
   archive repaired, policy resolvable). Run the recorded `recheck` rather than
   assuming; the clearing goes in a Coordinator decision, and the impediment is
   marked cleared rather than deleted.
2. **Design open ECC ideas into experiments.** Run
   `python3 tools/ecc_priority.py --open-ideas`. Every entry is a `proposed`
   ECC proposal that no hypothesis or experiment references, and these are
   ranked work rather than backlog. Take the highest-ranked and run
   `/design-experiment` on it: a hypothesis plus a frozen contract. Designing
   is NOT approving — the contract sits at `approved_by: null` until a
   committed Coordinator decision approves it. This step comes before opening
   any new campaign, because a designed contract against an existing question
   is cheaper and better-grounded than a fresh goal.
3. Open a new campaign against the highest-ranked open `RQ-*` or
   `KN-OPEN-*` item, following step 3's "Start new" path — ECC questions first.
4. If no open question justifies a campaign, run `/propose-ideas` on the
   best-supported ECC research question to generate candidates, then rank them
   and open a campaign against the winner.

None of these apply when the sweep shows a large `needs_repair` bucket
across otherwise-unrelated goals: that pattern is a repository-wide integrity
signal (see "Terminal stops"), and opening a new campaign or re-checking an
impediment does not address it — report it instead.

Idling is a last resort and is reported as such. Continuous operation must not
degrade into make-work: a campaign opened only to keep the loop turning, with
no ranked justification, is worse than an honest report that the portfolio
needs direction. If you reach that point, say so plainly and stop.

### Terminal stops

Only these end the run itself:

- The user asks to stop.
- Every goal is terminal and none of the three portfolio-refill paths above
  yields a justified campaign.
- An attempted Amazon Bedrock resolution. Refuse it before inference and
  reroute only to an allowed backend that satisfies the same model policy. If
  none exists, report a harness-wide infrastructure stop; fallback or downgrade
  permission never authorizes Bedrock.
- A missing `api_direct` credential is not itself terminal when an authenticated
  native Codex or Claude Code session satisfies the requested policy. Verify and
  record that direct session's model provenance, and refuse it if its resolved
  provider is Bedrock.
- A harness-wide integrity failure that makes *any* durable work impossible:
  no resolvable backend for a `degradable: false` policy, a repository that
  cannot be pushed, or a ledger that will not validate on `main`. Report the
  failure and what would clear it; do not keep dispatching work that cannot be
  archived. The step 2.5 sweep putting most or all of the active portfolio
  into `needs_repair` — especially with unrelated goals failing on the same
  shape of error (content-hash mismatch, an archived `commit_sha` that is not
  an ancestor of `HEAD`) — is exactly this signal on `main`, not a run of bad
  luck across many goals. Report the sweep's bucket counts and the distinct
  error shapes seen; do not silently work around it by hand-repairing one
  goal's queue to get a batch moving, since that treats a repository-wide
  finding as a one-off.

A failed candidate, empty ready set, or timeout is none of these. It is scoped
evidence: record it, set the next action, continue.

Attestations are optional but never fictional. If you record one it asserts a
review that happened; never record a quorum you did not obtain, and do not
present a single-model review as independent corroboration. Nothing in
indefinite operation relaxes this — a long run produces more claims, not
cheaper ones.

## Safety rules (non-negotiable)

- Only the Coordinator changes official hypothesis/goal status or shared ledgers.
- Snapshot archive before independent review; ledger archive before promotion.
- Never fabricate commands, outputs, timings, statistics, citations, or runs.
- Infra failures/timeouts are not mathematical counterevidence.
- Small- or toy-curve results are admissible; record the tested parameters and
  any transfer or extrapolation assumptions explicitly. Toy-curve results
  never become crypto-scale claims.
- Record requested policy + resolved model; no silent policy downgrade —
  including by dispatching a lower-effort subagent than the task's policy
  selects (step 6).
- Research work runs in subagents, not in the top-level session; independent
  review is a fresh agent call, never a continuation of the producer's.
- Never use Amazon Bedrock. OpenCode and the inference adapter must reject any
  Bedrock provider, backend, endpoint, or model before a request is sent.
- Workers do not commit into a shared worktree; Coordinator archive tasks alone
  stage declared paths and must pass post-commit verification.
- Concurrency ("Concurrency" note below): do not fill idle slots without a
  ranked next action, regardless of how high `max_concurrent` is set.
- Every batch merges `origin/main` into the working branch (never rebases) and
  pushes with an open/updated PR against `main` before the next batch starts;
  never resolve a sync conflict by editing a record. WHICH branch that is is a
  judgement call (step 8): the duty is that the work is merged, pushed, and
  under an open PR — not that the branch is new or campaign-exclusive.

## Concurrency

The fixed ceiling of three concurrent tasks was REMOVED on the user's
EXPLICIT DIRECTION of 2026-08-05 ("remove the concurrent limit from the code
rules") — see `tools/research_dispatch.py`'s `MAX_CONCURRENT_CEILING` for the
mechanism and its restore path. A dispatch queue's `max_concurrent` field is
no longer bounded by the tooling; it is bounded by what the Coordinator sets.

That does not make sizing it a formality. GOAL-AES-003 BATCH-002 dispatched
three producers onto a 4-core machine against that batch's own instruction
that it wait rather than run degraded: load average reached 13, one
producer's entire first segment produced zero numbers, another lost five of
eight trials to timeouts (`DEC-20260802-b226fb` budget_accounting). Removing
the tooling ceiling removes the thing that used to catch an oversized value
before dispatch; it does not remove the machine's actual headroom. Check
available cores/memory before raising `max_concurrent` past what the prior
ceiling of three assumed, and size to the environment, not to the absence of
a check.

## Output after each batch (and on stop)

Report: goal ID + status; completed task IDs + verified commits; evidence /
decision IDs with claim boundaries; knowledge promotions or `not_warranted`
reasons; exact next action (or impediment/complete rationale); PR number/branch
the batch was pushed to and how current it is with `main` — and, if you took a
branch of its own rather than the one the session was already on, the concrete
reason from step 8.

The report is a checkpoint, not a handover — write it and immediately begin the
next batch or the next goal. When the run does end, say which terminal stop
fired and what would let it resume.

## Quick examples

```text
User: run the harness for GOAL-ECDLP-001
→ status scan → bind GOAL-ECDLP-001 → render its dispatch_queue_path →
  execute ready tasks → snapshot → review → ledger → rerank / next batch

User: continue the active ECDLP goal
→ prefer matching active GOAL-* → same loop from next_action

User: launch a new research goal for RQ-SSI-001
→ allocate and check GOAL-SSI-<tok> + BATCH-<tok> → snapshot → then coordinate loop

User: just keep the harness running
→ select highest-ranked active goal → batch → checkpoint → next batch → ...
  → on goal completion or impediment, select or open the next goal → until a
  terminal stop
```
