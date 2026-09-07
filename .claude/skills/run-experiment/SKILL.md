---
name: run-experiment
description: >-
  Execute an approved experiment (EXP-*): validate the frozen specification,
  implement it, run bounded replicated runs with deterministic seeds, and
  write immutable run records and an execution report. Use after
  /design-experiment has produced an approved contract.
---

# Run experiment

Run lifecycle steps 6–7 (`docs/task-lifecycle.md`): execution and validation.

## Compact-context rule

This skill launches the **executor subagent**. Do not prime that subagent with a
full ledger scan, full knowledge corpus, or the complete `AGENTS.md`. Its initial
context is deliberately small and reproducible:

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

1. Locate `experiments/<EXP-ID>/specification.yaml`. Confirm status is
   `approved` and `approved_by` is set; otherwise stop and report a
   `specification_error` — do not "just run it anyway". Before running, merge
   `origin/main` into the working branch (merge, never rebase) so the run
   captures current repository state — see "Branch and PR hygiene" below.
2. Dispatch the **executor** subagent using the compact-context rule above. Give
   it the specification path and matching handoff path, not a prose dump of the
   surrounding campaign. It must:
   - validate the contract and refuse on missing fields;
   - implement the experiment (code lives under
     `experiments/<EXP-ID>/`, described in `implementation.md`);
   - execute every planned run inside the budget (timeouts, memory caps),
     one immutable directory per run:
     `runs/<RUN-ID>/{manifest.yaml,command.txt,environment.json,stdout.log,stderr.log,raw-result.json}`;
   - fill the run manifest per `docs/evidence-and-reproducibility.md`
     (commit, dirty flag, seeds, environment, timing, resources, validity);
   - classify every non-valid outcome with the failure taxonomy in
     `agents/executor.md`;
   - run the pre-analysis validation checks (run count, schema, seeds,
     raw/summary agreement, control comparability, deviations);
   - for heuristic-validation runs, compute the pre-registered comparison
     metric exactly as specified — including tail checks and controls —
     against the frozen prediction only;
   - return the `execution_report` YAML.
3. The Coordinator runs an isolated snapshot archive task that stages and
   commits only the declared run package and execution report. Do not ask the
   Executor to commit into a shared worktree. The post-commit verifier must
   bind the exact paths and hashes before `/review-evidence` begins; never
   amend or squash over earlier run commits for the same experiment.
4. Push the branch and open or refresh a PR against `main` naming the
   `EXP-*`/`RUN-*`/`TASK-*` records (see "Branch and PR hygiene"). A run whose
   receipts exist only in a local commit has not been executed for the
   program — it is unpublished.
5. Report to the user: run tally by terminal status, anomalies, protocol
   deviations, and whether the completion gate passed. Do NOT interpret
   results — that is `/review-evidence`.

## Branch and PR hygiene

Runs are immutable evidence, and every run of this skill also pulls in `main`
and surfaces the run package as a PR:

- **Before running:** `git fetch origin && git merge origin/main` — merge,
  never rebase. If the merge conflicts, stop and report; never resolve a
  conflict by editing a record. Re-run `tools/validate_ledger.py` and
  `tools/check_merge_hygiene.py` after the merge.
- **After the snapshot archive:** `git push -u origin <branch>` then
  `gh pr create --base main --head <branch> --title "runs: <EXP-ID>" --body "<EXP-*/RUN-* IDs>"`
  (or `gh pr edit <number>` when a PR for the branch already exists).

## Rules

- Runs are immutable. A bad run is marked invalid and superseded by a new
  run ID; it is never deleted or edited.
- Infrastructure failures and timeouts are not negative evidence; report
  them as their own classes.
- Predictions are frozen before runs. The pre-registered prediction or cost
  model in an approved specification is read-only during execution. A
  post-hoc adjustment is a new record via the amendment path and re-approval
  — never an edit of the frozen prediction, and never a silent re-scoring of
  completed runs against a new one.
- Record, never discard. Protocol deviations, infrastructure failures, and
  unexpected observations all go into the run manifest and the execution
  report (`protocol_deviations`, `anomalies`, `observations`). An observation
  that does not fit the prediction is still an observation.
- The Executor records observations only. For heuristic-validation runs it
  reports the frozen prediction reference, the comparison statistics, and
  the tail-check outcomes — never a conclusion that the heuristic is
  supported or refuted. That judgment belongs to `/review-evidence` under
  Coordinator authority.
