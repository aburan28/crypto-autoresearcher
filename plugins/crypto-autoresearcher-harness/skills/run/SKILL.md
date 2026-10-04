---
name: run
description: Run existing experiment programs and report their outputs. Use for run, run experiments, run the harness, or execution of a named EXP-*, TASK-*, GOAL-*, or existing experiment command.
---

# Run

Execute existing experiments. Finish with actual run counts, results, failures,
and output paths. This is the single public execution entry point.

## Find the program

Preserve a named experiment, task, goal, command, and requested stopping point.
Read only the selected experiment's launch instructions, inputs, and relevant
source. Use an existing command-based runner directly; a missing trial-plan.json
is not a reason to migrate a working experiment.

For an unqualified request, inspect the existing experiment worklist once:

```sh
python3 tools/newest_experiments.py --limit 3 --json
```

Use `--experiment <ID>` or `--goal <ID>` for named scope. The selector's
`needs_implementation_or_plan` label is a preparation hint: look for the existing
documented launcher before declaring that experiment unavailable. Select runnable
work in the repository's existing priority order. Do not invent a new experiment,
recover private keys, or turn this skill into an autonomous attack workflow;
mathematical experiments use public synthetic inputs.

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
just to satisfy a run request. Do not fetch/merge branches, open a PR, or start
independent review as an automatic part of execution. Those are separate tasks.

If a launcher, necessary input, ownership, or runtime admission is unavailable,
report the exact impediment once. For an unqualified run, continue other runnable
experiments; for a named run, retain its scope. Do not replace execution with
paperwork or repeatedly poll unchanged state. A needed implementation or protocol
change is reported separately, not silently made during this skill.

## Return the results

Retain commands, parameters/seeds, code and environment identity, logs, raw
outputs, elapsed time, and failed attempts using the runner's existing output
format. Report what actually completed and where its outputs are. State any
missing data without fabricating receipts. A failed process is not a mathematical
refutation, and a successful run alone does not promote a scientific claim.

Continue existing runnable work within the user's requested scope. Stop at the
named boundary, user stop, or when no selected work can execute. Reporting results
does not require publication, ledger repair, or completion of a review cycle.
