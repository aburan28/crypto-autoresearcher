---
name: run-experiment
description: >-
  Execute approved experiments: run a named EXP-* when supplied, otherwise
  select the newest approved runnable experiments, launch executor subagents,
  and write immutable run records and execution reports.
---

# Run experiment

Run lifecycle steps 6–7 (`docs/task-lifecycle.md`): execution and validation.

## Experiment selection

When the user names one or more `EXP-*` IDs, run exactly those experiments after
the approval gates below.

When no experiment ID is supplied, do **not** scan the experiment corpus into
model context. Run the deterministic selector instead:

```sh
python3 tools/newest_experiments.py --limit 3 --json
```

Treat the returned rows as the execution queue, newest first within the standing
research priority. The selector:

- reads only top-level `experiments/EXP-*/specification.yaml` records;
- requires `status: approved`, non-null `approved_by`, `frozen: true`, and no
  explicit `execution_authorized: false`;
- skips an experiment once any `execution-report.yaml` exists under its
  experiment directory, so the skill does not re-run completed work by default;
- preserves the repository's binding ECC-first selection policy by calling
  `tools/ecc_priority.py` rather than re-deriving ECC membership;
- orders eligible experiments newest-first by `designed_at`, with experiment ID
  as the deterministic tie-break when records have the same date.

By default take up to three results so newly approved experiments can be worked
without serial user prompts. Respect machine `max_concurrent`; dispatch in
parallel only when write scopes do not overlap. If the selector returns nothing,
report that there is no approved runnable experiment instead of inventing work.

Record the selected experiment IDs and their `designed_at` values in the
checkpoint/dispatch receipt. Automatic newest-selection is scheduling only; it
is not scientific evidence and does not alter a hypothesis or goal status.

## Compact-context rule

This skill launches a fresh **executor subagent** per selected experiment. Do
not prime that subagent with a full ledger scan, full knowledge corpus, the
parent Coordinator transcript, or the complete `AGENTS.md`. Its initial context
is deliberately small and reproducible:

1. `docs/agent-runtime-core.md` — compact binding invariants;
2. `agents/executor.md` — executor authority/failure semantics;
3. `experiments/<EXP-ID>/specification.yaml` — frozen source of truth;
4. the exact matching `TASK-*` handoff from `ledger/handoffs/`;
5. source/evidence paths explicitly named by the specification or handoff.

Pass paths/references rather than copying entire file bodies into the dispatch
prompt. The executor may retrieve another file only when a concrete
implementation or validation question requires it. The parent Coordinator may
have broader context; that broad context is **not inherited** by the executor.
The immutable run transcript and artifacts remain complete even though the
model-visible working context is narrow.

If a task queue supports `context_paths`, set it to the specification, matching
handoff, and explicitly referenced source/evidence files. `api_direct` exposes
those paths in the task brief and loads `docs/agent-runtime-core.md` instead of
injecting all of `AGENTS.md` into every model turn.

## Steps

1. Resolve the experiment set using the selection rules above. For every
   selected experiment, locate `experiments/<EXP-ID>/specification.yaml` and
   re-check `status: approved`, non-null `approved_by`, `frozen: true`, and
   execution authorization immediately before dispatch. Otherwise report a
   `specification_error`; never "just run it anyway". Before running, merge
   `origin/main` into the working branch (merge, never rebase) so the run
   captures current repository state — see "Branch and PR hygiene" below.
2. Dispatch one **executor** subagent per eligible selected experiment using the
   compact-context rule above. Give each executor its own specification path and
   matching handoff path, not a prose dump of the surrounding campaign. Each
   executor must:
   - validate the contract and refuse on missing fields;
   - implement the experiment under `experiments/<EXP-ID>/` and document it in
     `implementation.md`;
   - execute every planned run inside the frozen protocol and machine limits,
     one immutable directory per run:
     `runs/<RUN-ID>/{manifest.yaml,command.txt,environment.json,stdout.log,stderr.log,raw-result.json}`;
   - fill the run manifest per `docs/evidence-and-reproducibility.md`;
   - classify every non-valid outcome with `agents/executor.md`;
   - run pre-analysis validation checks;
   - for heuristic-validation runs, compute only the pre-registered comparison
     metrics/tail checks/controls against the frozen prediction;
   - return the `execution_report` YAML.
3. The Coordinator runs isolated snapshot archive tasks that stage and commit
   only each declared run package and execution report. Do not ask Executors to
   commit into a shared worktree. The post-commit verifier must bind exact paths
   and hashes before `/review-evidence` begins.
4. Push branches and open or refresh PRs against `main` naming the relevant
   `EXP-*`/`RUN-*`/`TASK-*` records. A run whose receipts exist only locally is
   unpublished.
5. Report the selected experiment IDs, run tally by terminal status, anomalies,
   protocol deviations, and whether each completion gate passed. Do **not**
   interpret results — that is `/review-evidence`.

## Branch and PR hygiene

Runs are immutable evidence, and every run of this skill also pulls in `main`
and surfaces the run package as a PR:

- **Before running:** `git fetch origin && git merge origin/main` — merge,
  never rebase. If the merge conflicts, stop and report; never resolve a
  conflict by editing an immutable record. Re-run `tools/validate_ledger.py`
  and `tools/check_merge_hygiene.py` after the merge.
- **After the snapshot archive:** push the branch, then create or refresh its PR.

## Rules

- Runs are immutable. A bad run is marked invalid and superseded by a new run
  ID; it is never deleted or edited.
- Infrastructure failures and timeouts are not negative evidence.
- Predictions, controls, metrics, sample counts, and stopping rules are frozen
  before runs. Changes require an amendment and Coordinator approval.
- Record, never discard, deviations, failures, and unexpected observations.
- Executors record observations only; they never declare a hypothesis or
  heuristic supported, rejected, validated, refuted, or closed.
