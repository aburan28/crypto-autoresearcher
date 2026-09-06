---
name: crypto-autoresearcher-harness
description: >-
  Run, resume, or inspect a Crypto Autoresearcher ECDLP research campaign.
  Use when the user asks to run the harness, continue a GOAL-*, inspect
  research status, generate ideas, design experiments, execute a dispatch task,
  or keep the full research harness making progress.
metadata:
  openai/plugin: crypto-autoresearcher-harness
---

# Crypto Autoresearcher Harness

Requires a Crypto Autoresearcher checkout and Python 3.11+.

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

| Request | Mode and boundary |
| --- | --- |
| Status, doctor, orientation | **status**: read-only preflight and status; use goal_portfolio_health.py --no-deepen. Report without claims, records, fetches or dispatch. |
| Generate ideas / design experiments | **ideas/design**: read [intake](references/intake.md); archive and publish the requested proposals/designs, then stop unless execution was requested. |
| Run/continue a named GOAL-* | **goal**: read [lifecycle](references/lifecycle.md); continue batches for that exact goal through approval, execution, review and archival. |
| Run the harness / keep running, with no named goal | **portfolio**: read [lifecycle](references/lifecycle.md); work ranked active goals, ECC first, and move to the next when one is terminal or impeded. |
| Run a named TASK-* or EXP-* | **task**: follow the lifecycle gates for that task and required archives/reviews; stop at that requested boundary. |
| Start a new campaign | Create a goal only on this explicit request, then use goal mode. |
| Conclusion, promotion, closure or breakthrough | Arrange the Coordinator and independent claim-tier review required by AGENTS.md; never infer approval from the request itself. |

A completed batch is a checkpoint in goal/portfolio mode. Continue authorized
work without asking again; see the lifecycle for terminal and operational exits.
Do not reopen a terminal goal or silently substitute a different named goal.
Impeded goals stay active. Empty queues and infrastructure failures are not
research conclusions.

The old launch-research-harness and coordinate-research-goal commands are
compatibility aliases for this procedure. Their presence does not create a
second workflow. Stage skills are implementation references, not additional
front doors the user must know.

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

A checkpoint does not end an authorized goal/portfolio loop. Resume the shared
lifecycle; do not confuse a session ending with a campaign completing.

Do not call an idea, a passing unit test, a snapshot, or a single toy run a
cryptanalytic advance.
