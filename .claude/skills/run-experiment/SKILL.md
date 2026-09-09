---
name: run-experiment
description: >-
  Execute existing approved experiments. Run named EXP-* IDs exactly; otherwise
  drain newest eligible ECC-first work through compact executor subagents,
  deterministic trial execution, immutable records, and required archives.
---

# Run experiment

This is an execution-stage adapter for the single public
`crypto-autoresearcher-harness` skill, not a second front door. Follow its
`references/execution.md`, repository `docs/experiment-execution.md`, and
lifecycle steps 6–7 (`docs/task-lifecycle.md`). Do not turn execution into
proposal generation, portfolio discussion or a hypothesis-closure session.

## Selection and continuation

When the user names EXP-* IDs, preserve that exact scope. Otherwise use:

```sh
python3 tools/newest_experiments.py --limit 3 --json
```

Use `--experiment <ID>` (repeatable) or `--goal <ID>` for named scope. Selection
reads top-level specifications, retains approval/frozen/authorization and
supersession gates, and calls `tools/ecc_priority.py` for ECC-first priority.
Within each priority class use `designed_at`, then ID, newest first.

Three rows are a selection page, not a limit on the campaign. After each
published checkpoint select again until the authorized backlog is drained or
impeded. Keep the user's named scope and requested stopping boundary.

Inspect `execution_state`, not directory presence:

- `ready`: unattempted plan trials exist; arrange actual dispatch authority.
- `needs_implementation_or_plan`: implement/prepare only the selected experiment
  under its proper handoff. Do not call it runnable code or complete the task
  with a design note alone.
- `needs_reconciliation` / `needs_plan_repair`: expose via
  `--include-blocked --limit 0 --json`; resolve the exact missing prerequisite
  additively, or continue another eligible experiment. Never blindly rerun an
  existing attempt or edit immutable evidence.

Measurement completion comes from explicit trial coverage; it does not establish
publication, review or a scientific conclusion. The selector is scheduling only.
Record selected IDs, design dates, plan pointers and remaining trial counts.
Empty queues do not authorize inventing work or repeatedly polling unchanged state.

## Compact executor context

Start one fresh executor session per selected experiment/task with paths to:

1. `docs/agent-runtime-core.md`;
2. `agents/executor.md`;
3. the exact frozen specification;
4. its matching committed TASK-* handoff;
5. explicitly referenced sources/evidence and its frozen trial plan, if present.

Do not inherit the parent transcript, complete AGENTS.md, full ledger or knowledge
corpus. Additional retrieval requires a concrete implementation/validation need.
Set `context_paths` where supported. Preserve complete immutable artifacts despite
the narrow model-visible context. Once the driver is implemented, routine trials
must use processes rather than fresh model deliberation for each seed.

## Execution and evidence gates

1. Before running, `git fetch origin && git merge origin/main` (never rebase
   research history). Stop affected work on conflicts; do not fix them by editing
   immutable records. Validate with `tools/validate_ledger.py` and
   `tools/check_merge_hygiene.py`. Recheck approved/frozen specification status,
   non-null approval and execution authorization immediately before dispatch.
2. Render the existing queue with current time and `--claims refs`. Dispatch only
   admitted work within `max_concurrent`, actual machine headroom and disjoint
   write scopes. Publish the claim before launching. The supervisor does not
   replace these steps or approve a zero-run prerequisite for execution.
3. The executor implements the approved protocol under its declared scope and
   documents the implementation. For an approved compatible trial plan invoke:

   ```sh
   python3 tools/experiment_execution.py run --plan <frozen-plan-path> \
     --owner <published-owner> --epoch <published-epoch>
   ```

   The adapter rechecks dispatcher/claim gates and processes the remaining
   authorized trials. It records exact code/environment bindings, raw outputs,
   operational failures and correctness-check outcomes. The driver must emit
   canonical manifests and all preregistered metrics/controls. Legacy drivers
   without this contract use their approved execution procedure until a
   Coordinator-approved additive migration is ready; never invent receipts.
4. An executor records observations and an execution report only. Preserve every
   attempt, deviation and anomaly. Bad/uncertain attempts require new IDs and
   explicit recovery, never deletion or overwrite. Valid negative results are
   not retried away. Scientific sample counts and stopping rules remain frozen.
5. The Coordinator inspects actual outputs and releases the claim with its real
   outcome. Run an isolated Coordinator snapshot archive covering every declared
   artifact/report and verify exact paths/hashes before independent review.
   Executors never commit into a shared worktree. Review stays independent;
   scientific state transitions still require the Coordinator's ledger archive.
6. Push and open/refresh the PR against main. Local receipts alone are unpublished.
   Report trial tallies, operational failures, outstanding review, verified
   archives, publication, and the next action; then continue within scope.

A timeout, crash, missing implementation or infrastructure failure is not negative
mathematical evidence. Output validation does not establish hypothesis support,
rejection, breakthrough or closure. Archive evidence without retiring the lead.
