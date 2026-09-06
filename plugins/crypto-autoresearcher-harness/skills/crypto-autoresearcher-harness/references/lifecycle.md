# Shared campaign lifecycle

Read this for goal and portfolio execution. The mode selected in SKILL.md
controls the scope and exit; a batch checkpoint alone never ends either mode.
Use repository-relative paths from the resolved checkout.

## Orient and bind

1. Read AGENTS.md, the Coordinator contract, docs/task-lifecycle.md,
   docs/dynamic-subagent-dispatch.md, docs/concurrent-goal-lanes.md, and the
   relevant goal head, queue, decisions and handoffs. Read the bus inbox on wake
   and before reporting done; messages confer neither authority nor evidence.
2. Refresh origin/main and claim refs. Preserve other sessions' dirty files.
   Use an isolated worktree when needed; merge, never rebase research history.
   Before each new batch, merge origin/main, validate the ledger and run
   branch-scoped merge hygiene. Do not repair immutable records in place.
3. Run python3 tools/goal_portfolio_health.py once per session before selection.
   It can deepen a shallow clone. For read-only status use --no-deepen and
   disclose missing history; do not call unreachable history corruption.
   Report ready / blocked / needs_repair counts and reasons. These are
   diagnostic buckets, never goal statuses. Widespread failures require a
   repository-integrity diagnosis, not serial attempts to dispatch broken queues.
4. For a named goal, bind its exact ID and recorded next_action; never substitute
   another goal. For portfolio mode, select ranked, justified active work with
   ECC first, using tools/ecc_priority.py and orchestration/research-priority.yaml.
   Explicit scope takes precedence over selecting unrelated work.
5. Read open lanes with tools/goal_lanes.py lanes <GOAL-ID>. Reuse the declared
   batch/queue and its branch/PR. Join only unclaimed eligible tasks. If justified
   work needs a concurrent disjoint lane, register it with open-lane --publish
   before workers run. Follow the tool's --help for exact arguments. Never
   overwrite another lane's next_action or silently force a live claim.
6. A new goal requires an explicit user request. Allocate/check random IDs with
   tools/allocate_id.py, bind a question and completion criteria, and create
   the first bounded batch through Coordinator archival. An empty portfolio
   alone does not authorize a new campaign.

## Prepare and execute a batch

1. Bind committed task cards, handoffs, input revisions, write_scope, artifacts,
   budgets, stopping rules and archival tasks in the queue. Set goal_id.
   An execution request authorizes arranging design and Coordinator approval
   within scope; approved_by: null is a pending workflow step, not an approval
   and not by itself a reason to return to the user. No Executor starts before
   a frozen approved contract and committed Coordinator decision exist.
2. Snapshot/archive the authority records and verify the receipt. Push and open
   or update the lane PR against main before workers start. Local files alone
   are not a published handoff. Use exact staged paths; never git add -A in a
   shared checkout. Verify remote head, PR scope and checks on publication.
3. Render tools/research_dispatch.py with the declared queue, --claims refs,
   an explicit current --now, --output and --report. An invalid plan stops
   affected dispatch. A preflight success never replaces queue or archive gates.
4. Claim eligible unclaimed tasks with tools/goal_lanes.py claim ... --publish
   before launch. Re-render on a claim refusal. Run non-archive research tasks
   in separate role sessions, each bound to its committed card, budget and
   exclusive scope. Resolve (role, inference.policy) through
   orchestration/model-policies.yaml and checked runtime bindings; use
   python3 tools/check_runtime_bindings.py --list rather than a copied model
   table. Record requested policy and actual resolved model. Refuse unsupported
   policies and Bedrock before inference. Use the host's available dispatch API,
   not Claude-specific Agent arguments on another runtime.
5. Run independent tasks concurrently only within max_concurrent and real
   machine headroom, accounting for other sessions. Workers neither commit nor
   spawn untracked work. Coordinator archives run alone. Release claims with
   their real outcome and record the claim epoch in receipts. A returned message
   is not a deliverable; inspect the declared artifacts.
6. After producer termination, run its Coordinator snapshot archive alone and
   verify its Git receipt before reviews read the result. Freeze the review_plan
   before reviewers run: prior, owned joints and attacks, blindness,
   proves-too-much control, and blind re-derivation where required.
7. Dispatch reviews in fresh independent sessions with only their allowed
   sources. Follow AGENTS.md claim-tier rules: review-breakthrough at max is
   never degraded. Check tools/check_review_independence.py --batch <batch-dir>.
   Record deviations; do not invent attestations or treat a partial round as
   concurrence.
8. Run the Coordinator ledger archive alone. Verify parent, exact diff, record
   IDs and hashes. Only this committed decision can change official research
   state. Apply agents/coordinator.md promotion gates and the target-result and
   inventor protocols; a verified archive is not a mathematical result.
9. In that archive update only this lane's goal entries with evidence, decision,
   latest verified commit and exactly one next_action. Publish the checkpoint,
   then close the lane with close-lane --publish when its work is finished.
   Report knowledge promotions or the recorded not_warranted reason.
10. Rerank after the committed checkpoint, reading
    python3 tools/obstruction_registry.py --unexamined and the ECC priority
    worklist. Generate the next justified bounded batch and repeat.

## Continuation and impediments

For an empty ready set, distinguish work already owned from absent work.
Observe owned work; never duplicate it. Otherwise inspect the recorded
next_action, ranked open hypotheses, justified replications/controls, and
scoped ideation in that order. Design open ECC ideas using
python3 tools/ecc_priority.py --open-ideas; an unapproved design still needs
a committed Coordinator approval before execution. Never create tasks merely
to fill capacity. Re-render after artifacts, claims or dependencies change;
repeating an unchanged check is not progress.

Keep impeded goals active. Record condition, what_is_blocked, clears_when,
recheck and asserts_nothing_about according to AGENTS.md. Infrastructure,
timeouts, failed candidates and budget limits assert nothing about the science.
ECC campaign budgets are unlimited as specified by the priority authority;
per-task budgets and concurrency remain bounded. Non-ECC exhausted budgets stop
spending until a committed Coordinator budget decision permits more.

- Goal mode: continue that goal through batches. Return a precise checkpoint
  when it reaches a committed terminal status, the user stops, or no justified
  in-scope action can proceed after checking the impediment.
- Portfolio mode: after a terminal or impeded goal, select the next ranked
  active goal, ECC first. Recheck each unchanged impediment once per sweep,
  not in a busy loop. If none offers justified work, report the concrete
  impediments/rechecks and the last durable progress. Do not open a new goal
  without an explicit request.
- A repository-wide integrity or publication failure stops affected durable
  work. Diagnose the actual scope: an unavailable review tier impedes its claim,
  not every task that does not require that tier.
- Completion requires the committed Coordinator decision and current AGENTS.md
  closure rules. Never change a goal to paused or blocked.
- A session/time limit ends this session with a durable continuation pointer;
  it does not complete the campaign or promise background execution. A later
  "continue" binds that pointer rather than beginning another candidate search.

## Checkpoint that another session can use

Follow references/progress.md. Report the goal, lane, queue path, branch and
PR, verified archive commits, completed task IDs, evidence/decision IDs and
exact claim boundaries. State what changed since the previous checkpoint,
current owner(s), required reviews, exactly one recorded next_action with its
responsible role, and any impediment with its recheck. Then continue according
to mode without asking whether to run the already-authorized next batch.
