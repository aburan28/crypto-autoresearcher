---
name: run
description: Run existing experiment programs and report their outputs. Use for run, run experiments, run the harness, or execution of a named EXP-*, TASK-*, GOAL-*, or existing experiment command.
---

# Run

Execute existing experiments. Finish with actual run counts, results, failures,
output paths, and each experiment's run report. This is the single public
execution entry point.

## Find the program

Preserve a named experiment, task, goal, command, and requested stopping point.
Read only the selected experiment's launch instructions, inputs, and relevant
source. Use an existing command-based runner directly; a missing trial-plan.json
is not a reason to migrate a working experiment.

For an unqualified request, inspect the existing experiment worklist once:

```sh
python3 tools/newest_experiments.py --limit 3 --json
```

Use `--experiment <ID>` or `--goal <ID>` for named scope. The list is
decision-aware and readiness-first: committed `DEC-*` holds are already applied,
and within each priority group `ready` rows (a committed launcher or trial plan)
sort above `needs_implementation_or_plan`, so the top rows are the ones that can
start now. Each row carries `off_main_runs`: branches not yet on `main` that
already hold run records for that experiment. A non-empty value means someone
executed it elsewhere; name it in the report and do not run the same trials
again. The `needs_implementation_or_plan` label is a preparation hint: look for
the existing documented launcher before declaring that experiment unavailable.
Do not invent a new experiment, recover private keys, or turn this skill into an
autonomous attack workflow; mathematical experiments use public synthetic inputs.

For `$run GOAL-...`, select only that goal's experiments:

```sh
python3 tools/newest_experiments.py --goal <GOAL-ID> --limit 0 --json
```

Keep the goal filter throughout execution and in the result summary. If an older
experiment has no `goal_id` in its specification, follow the named goal's existing
experiment/queue pointers to its documented launcher; do not scan other goals or
infer membership from an identifier prefix. An empty or impeded goal-scoped list
never falls back to the whole portfolio. Report the selected goal, attempted
experiments, completed/failed trials, output paths, and any remaining impediment.

A sparse checkout (`python3 tools/sparse_checkout.py status`,
`docs/sparse-checkout.md`) keeps run archives and reference bundles off disk.
A `needs_materialization` row, or a launch the runner refuses because run
directories are off disk, needs one command: `python3 tools/sparse_checkout.py
add --experiment <EXP-ID>`. A declared input that `git ls-files` lists but the
disk lacks is outside the checkout, not missing: `add --path` it rather than
reporting an impediment.

## Execute

Run the existing program with its declared inputs, seeds, controls, and trial
count. Use a fresh output location, preserve earlier attempts, and respect live
ownership and machine resource limits. For a prepared trial plan with its existing
claim, use the process supervisor:

```sh
python3 tools/experiment_execution.py run --plan <existing-plan-path> \
  --owner <claim-owner> --epoch <claim-epoch>
```

Keep the runner's built-in admission, resource, and output-correctness checks.
Do not duplicate them in an agent-led validation phase or disable them to force
a launch. Routine trials are processes; they do not need a new agent per seed.
Show real progress while they run.

Do not run preflight, whole-ledger/schema validation, portfolio-health sweeps,
protocol review, or merge-hygiene checks as prerequisites to this skill. Do not
author protocols, approval records, migrations, repair queues, or review plans
just to satisfy a run request. Do not fetch/merge branches or start independent
review as an automatic part of execution. Those are separate tasks.

## Report each experiment

After an experiment's trials finish (completed, failed, or timed out), write
its run report as `research-visuals` describes under "Every experiment run"
(`.claude/skills/research-visuals/SKILL.md`): a write-once directory
`experiments/<EXP-ID>/reports/run-<YYYYMMDDTHHMMZ>/` holding a report of what
ran and what it measured, at least one graph of the recorded data (or a
diagram of what ran when there is nothing to compare), and `report.pdf`
rendered from them and inspected. One report per experiment per session,
covering every run directory this session wrote for it. Never write into a run
directory or edit an earlier report.

The report describes outputs; it is not a review. It states no verdict,
support, weakening, or significance, plots recorded values only, and computes
nothing new beyond labeled arithmetic on recorded values. It does not delay
the run records: commit and push those first (below), then the report. If no
renderer can be installed, commit the report source and graphs and state the
blocker; do not skip the report.

## Publish the run records

Run records left only in a working tree are not evidence and are invisible to
the next session, which then runs the same trials again. When trials finish,
commit the run directories this session wrote (`experiments/<EXP-ID>/runs/...`
and nothing else) on the session's own branch and push it, so the selector's
`off_main_runs` column shows them to every later `run` session. Commit and push
each experiment's report directory (`experiments/<EXP-ID>/reports/run-*/`)
next, on the same branch. Open or refresh
a PR for that branch with the runtime's PR tool when one is available; this is
publication of observations, not review, archival, or a research-state change.
Never amend or rewrite a pushed run commit, and never commit ledger records,
specification edits, generated indexes, or anything outside those run and report
directories from this skill.

If a launcher, necessary input, ownership, or runtime admission is unavailable,
report the exact impediment once. For an unqualified run, continue other runnable
experiments; for a named run, retain its scope. Do not replace execution with
paperwork or repeatedly poll unchanged state. A needed implementation or protocol
change is reported separately, not silently made during this skill.

## Return the results

Retain commands, parameters/seeds, code and environment identity, logs, raw
outputs, elapsed time, and failed attempts using the runner's existing output
format. Report what actually completed, where its outputs are, and where each
experiment's run report and PDF are. State any missing data without
fabricating receipts. A failed process is not a mathematical
refutation, and a successful run alone does not promote a scientific claim.

Continue existing runnable work within the user's requested scope. Stop at the
named boundary, user stop, or when no selected work can execute. Reporting results
does not require ledger repair or completion of a review cycle; it does include
the branch the run records were pushed to. End with a session receipt
(`python3 tools/session_receipt.py --skill run ...`, see `docs/session-receipts.md`).
