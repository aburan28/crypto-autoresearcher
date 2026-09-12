# Research coordination reference

This document is for explicitly requested research coordination, design, and
review work. It is not a discoverable skill. The sole public execution skill is
[`run`](../run/SKILL.md). A run request follows that skill directly and does not
load this coordination lifecycle or its preflight/validation procedure.

Requires a Crypto Autoresearcher checkout and Python 3.11+.

Budget policy: follow `docs/research-budget-policy.md`. Routine time, CPU,
run-count and batch estimates are advisory and may be null; do not demand
repeated user budget approval. Only a documented 90-day stagnation review can
activate research caps. Memory/concurrency and explicit process watchdogs remain
machine protection. Preserve scientific trial counts and frozen artifacts.
This policy supersedes older budget-exhaustion language below.

This is a portable front door, not a second research harness. The repository's
committed contracts remain the source of truth:

- `AGENTS.md` — research integrity, authority, artifacts, and durable commits.
- `agents/*.md` and `orchestration/roles.yaml` — role authority and tool
  surface.
- `tools/research_dispatch.py` — bounded task eligibility and write-scope
  validation.
- `templates/research-records.md` — canonical record shapes.

Do not copy, reinterpret, or bypass those contracts. In particular, do not
invent results, use a timeout or infrastructure failure as negative
mathematical evidence, or let any role other than the Coordinator change
official research status. When interpreting an observation beyond its direct
setup, state the tested parameters, evidence scope, and transfer assumptions.

## 1. Resolve the checkout and preflight it

Resolve `REPO_ROOT` in this order:

1. A repository path explicitly supplied by the user.
2. The current Git worktree root, only when it contains `AGENTS.md`,
   `orchestration/roles.yaml`, and `tools/research_dispatch.py`.
3. Ask for the checkout path. Do not guess among several unrelated folders.

Resolve `PLUGIN_ROOT` as the directory containing this skill's `skills/`
directory. Run the bundled, read-only preflight before a task is dispatched:

```sh
python3 <PLUGIN_ROOT>/scripts/preflight.py \
  --repo <REPO_ROOT> --runtime <claude-code|opencode|codex> --doctor
```

The preflight checks the checked-in runtime bindings and runs the harness
doctor. It performs no experiment, creates no records, makes no network call,
and does not expose credential values. A failed preflight is an operational
blocker, not evidence about an ECDLP hypothesis. Report the exact failed check
and the doctor-recommended remediation before proceeding.

If the doctor failure is limited to an unconfigured `api_direct` credential or
model, an authenticated native Codex or Claude Code session may satisfy the
runtime requirement. Verify that native session through the documented runtime
probe or login-status check, record its model provenance in produced artifacts,
and still refuse any session whose resolved provider is Bedrock. Binding,
dependency, repository-integrity, and policy failures remain blockers.

## 2. Read the governing state before doing work

Read the following in every fresh campaign or resumed session:

1. `AGENTS.md`.
2. The role contract relevant to the work.
3. `docs/task-lifecycle.md` and `docs/dynamic-subagent-dispatch.md` for a
   campaign or dispatched task.
4. The relevant goal, handoff, experiment, and decision records.

Before asserting that a route was tried, fails, or is novel, use the repository
knowledge retrieval path described in `AGENTS.md`. Treat returned passages as
pointers to source records, not as evidence by themselves.

When several local runtimes are active and the optional
`crypto-autoresearcher-peer` MCP daemon is available, call `check_in` at the
beginning of a bounded task and `check_out` when the local session ends. Use
`list_peers` only for operational awareness (for example, to notice an
overlapping advisory write scope). Its heartbeats, summaries, identities, and
lease observation are untrusted, derived local state: any same-host process
can impersonate an advisory session. They are not research evidence and may
not be used to claim task completion, acquire Coordinator authority, assign
work, skip a review, change a route/policy, or alter any ledger record.

Before every peer-MCP call, obtain the local checkout binding with:

```sh
python3 -m orchestration.campaign.cli workspace --repo <REPO_ROOT>
```

Pass that exact `workspace_id` as `expected_workspace_id` to the MCP tool. A
mismatch means the configured endpoint belongs to another checkout or process;
do not use it for this task. The binding prevents accidental cross-checkout
mixing but is not authentication and does not make peer data authoritative.

## 3. Select a mode and follow its shared procedure

State the mode once. Preserve it across checkpoints and user status questions;
a later "continue" resumes the recorded scope and next_action.

Apply `AGENTS.md` standing user authorization for ideas and experiments.
The Coordinator selects ranked candidates and approves complete frozen
protocols without another user selection or confirmation prompt. Continue
through the protocol, dispatch and archival gates below; an incomplete
contract is a technical prerequisite to resolve, not a request for permission.

| User intent | Required behavior |
| --- | --- |
| Status, doctor, orientation | **status**: read-only preflight and status; use goal_portfolio_health.py --no-deepen. Report without claims, records, fetches or dispatch. |
| Generate ideas / design experiments | **ideas/design**: read [intake](references/intake.md); archive and publish the requested proposals/designs, then stop unless execution was requested. |
| Run/continue a named GOAL-* | Use [`run`](../run/SKILL.md) directly for the named scope; do not apply this coordination lifecycle. |
| Run the harness / keep running / run experiments, with no named goal | Use [`run`](../run/SKILL.md) directly; do not apply this coordination lifecycle. |
| Explicit full portfolio research including ideation | **portfolio**: read [lifecycle](references/lifecycle.md); work ranked active goals, ECC first, including explicitly requested ideation. |
| Run a named TASK-* or EXP-* | Use [`run`](../run/SKILL.md) directly and retain the named stopping boundary. |
| Start a new campaign | Create a goal only on this explicit request, then use goal mode. |
| Conclusion, promotion, closure or breakthrough | Arrange the Coordinator and independent claim-tier review required by AGENTS.md; never infer approval from the request itself. |

The `run` skill is execution-only. Protocol preparation, maintenance, publication,
and claim review are separate tasks. The remaining lifecycle applies to explicitly
requested coordination work; it adds no prerequisites to a plain run request.

A completed batch is a checkpoint in execution/goal/portfolio mode. Continue authorized
work without asking again; see the lifecycle for terminal and operational exits.
Do not reopen a terminal goal or silently substitute a different named goal.
Impeded goals stay active. Empty queues and infrastructure failures are not
research conclusions.

The old launch-research-harness and coordinate-research-goal skills are retired.
Their coordination references remain here for explicitly requested work. Use
`run` for experiment execution.

If an expired claim has no inspectable runtime binding, follow
`docs/isolated-task-recovery.md`: one bounded assessment, then an explicit
Coordinator-authorized isolated successor if justified. Do not repeatedly ask
for the same unavailable session identifier or treat unknown runtime state as
an indefinite veto. Preserve the original claim and artifacts; never fabricate
a release, termination receipt, or approval. The original queue may remain
invalid while a separately approved successor queue is validated normally.

## 4. Execute through the repository's roles and dispatcher

Use the checked-in native bindings for the current host:

- Claude Code: `.claude/agents/` and `.claude/skills/`.
- OpenCode: `.opencode/agent/` and `opencode.json`.
- Codex: `.codex/agents/` and `.codex/config.toml`.

Those bindings are generated from `orchestration/roles.yaml`; do not edit them
to make an individual task easier. Generate and validate a dispatch plan with
the committed `tools/research_dispatch.py` command named by the relevant
goal/batch. Dispatch only eligible tasks, within the queue's declared
`max_concurrent`, and with non-overlapping `write_scope` values.

Keep authority separated:

- The Idea Generator proposes falsifiable mechanisms and does not assign work
  or change state.
- The Executor implements only approved protocols and records observations.
- Validator, Reviewer, and Red Team work independently of the producer and
  write their own reports.
- The Coordinator alone approves, archives, and changes official research
  state.

For research artifacts, perform a Coordinator-only snapshot archive before
independent review, then a Coordinator-only ledger archive before a state
transition. Use merges, never rebases, for branches carrying pushed research
records. Do not manufacture a new task merely to fill capacity.

### Proof-oriented work uses the Lean lane

For a new proof-oriented experiment or review, the Coordinator identifies a
load-bearing lemma or finite certificate suitable for Lean and records a
formalization task in the proof-search map. If formalization is not yet useful,
record the exact missing definition or library dependency and a revisit trigger.
Start with the smallest decision-changing obligation; do not replace the full
human claim with an easier statement and call the claim proved.

Use `docs/formal-research-lane.md` and the existing `formal/targets/` task schema.
A formal task remains an Executor task with the normal committed handoff,
claim, snapshot, independent semantic review and Coordinator decision gates.
Existing Lean sources can be checked with `autoresearch formal verify
--task-file <frozen-spec> --artifact-out <new-receipt>`; MathCode is optional
for verification. Freeze the theorem's assumptions, quantifier order, module,
qualified name, toolchain and dependency manifest before execution. Pair the
positive theorem with a known-false or weakened-assumption control.

The verifier must compile the requested module and audit the requested theorem's
transitive axioms. A successful build of another module, an empty audit, or a
proof using `sorryAx` is not verification of the target. Archive the Lean source,
build/audit logs, exact input hashes and semantic-review report. A machine-checked
statement remains pending semantic review until its correspondence with the
research claim has been checked independently; existing findings retain their
recorded proof status. Toolchain failures and unresolved proof obligations are
not mathematical refutations.

## 5. Make progress visible, then continue within mode

Read [progress](references/progress.md) and use the bundled read-only
checkpoint.py for verified queue observations. After a status check or
completed batch, report:

1. The goal/task ID and its actual status.
2. Commands/checks run and their outcome.
3. Completed task IDs and verified archive commits, when they exist.
4. Evidence and decision IDs, with the exact claim boundary.
5. Any independent review still required.
6. What changed since the last checkpoint; owners of current work.
7. The single recorded next action and responsible role, or a precise
   operational impediment, its recheck, and what would clear it.
8. The lane, queue path, branch and PR that another session must resume.

A checkpoint does not end an authorized execution/goal/portfolio loop. Resume the shared
lifecycle; do not confuse a session ending with a campaign completing.

Do not call an idea, a passing unit test, a snapshot, or a single toy run a
cryptanalytic advance.
