# Experiments reported ready are refused by the supervisor's archive-coverage check

- **Status:** `open`
- **Kind:** implementation gap (readiness check and admission check disagree)
- **Affected work:** the 17 experiments listed below; the `run` skill's selector
  (`tools/newest_experiments.py`); mechanical-tier execution
  ([runbook execution](../docs/runbook-execution.md))
- **Next action owner:** Coordinator (the dispatch queues are its records)
- **Last updated:** 2026-10-17

## Problem

We cannot run 17 of the 18 experiments that `tools/newest_experiments.py`
reports `execution_state: ready`. Their executor tasks' `artifact_paths` name
only each run's `manifest.yaml` and `raw-result.json`. But
`tools/experiment_execution.py` `authorize()` refuses a trial unless the task
declares every file the supervisor writes into the run directory (the eight
`GENERATED` names plus the trial's artifacts). It raises "handoff archive
coverage missing" before the first trial starts. The readiness check does not
test archive coverage, so the selector ranks these contracts first, and an
executor discovers the refusal only after claiming and publishing the task.

## Evidence and uncertainty

- **Observed (2026-10-16, `main` at 9c8c0da54):** for every `ready` row from
  `python3 tools/newest_experiments.py --limit 0 --json`, the run files
  `authorize()` requires were compared with the plan's task `artifact_paths`.
  Each of the following misses all eight supervisor files per run:
  - EXP-SEMBIN-7c8e98, EXP-SEMBIN-22a1a2;
  - EXP-SCURVE-7003fe, EXP-SCURVE-41f104;
  - EXP-PAIR-f4584a;
  - EXP-OAKLEY-7f73ef, EXP-OAKLEY-4276c4, EXP-OAKLEY-2c0552;
  - EXP-ECDLP-f34097, EXP-ECDLP-bfbe6f, EXP-ECDLP-903c48, EXP-ECDLP-6f869c,
    EXP-ECDLP-5f4f14, EXP-ECDLP-422afc, EXP-ECDLP-3c166b, EXP-ECDLP-20ac31;
  - EXP-CSIDH-72413d.

  EXP-CMFB-cea1d2 declares them and passes. An earlier executor hit the same
  refusal and released its claim:
  `coordination/goals/GOAL-CSIDH-001/batches/BATCH-dedd56/claims/TASK-20261009-9ec9ef.1.release.json`.
- **Derived or proved:** the comparison is static; no claim was taken and no
  trial was launched to observe it.
- **Suspected explanation:** these queues were written before `authorize()`
  required the supervisor's own files, or by a template that predates it.
  This is unconfirmed.
- **Missing capability:** a readiness check that applies the same coverage
  rule `authorize()` applies.
- **What this evidence does not establish:** nothing about any hypothesis;
  an unrun contract is neither evidence nor a failure of its hypothesis.

## What would unblock it

- [ ] `tools/newest_experiments.py` reports these rows as something other
  than `ready` (for example `needs_dispatch_queue`) until coverage holds,
  using the same rule as `authorize()`.
- [ ] The Coordinator supersedes each affected queue with one whose executor
  task declares every supervisor file, under the existing record rules.

`tools/runbook.py lint` already refuses a supervisor runbook whose queue would
be refused, so no runbook can carry this gap; the 17 contracts above have no
runbook.

## Next discriminating step

- **Action or proof obligation:** apply the coverage rule in the selector,
  then re-list the ready rows.
- **Inputs and controls:** the 18 rows above. EXP-CMFB-cea1d2 is the control
  that must stay `ready`.
- **Execution limits and stop condition:** a static check; no trial runs.
- **Outcomes and next actions:** each affected row changes state, and the
  Coordinator's queue supersessions return it to `ready`.
- **Recheck trigger:** a change to `authorize()` or to the dispatch-queue
  template.

## Resolution and history

Unresolved.

## 2026-10-17 SNFS execution update

PR #2382 attempted EXP-ECDLP-f34097 and EXP-ECDLP-903c48 through the ordinary supervisor. Both were refused before a trial directory was created because their executor handoffs omit launch.json (and the other supervisor artifacts). The additive [repair packet](../coordination/design/SNFS-INSTRUMENT-REPAIR-20261017/README.txt) retains exact loader/coverage checks and approvable:false receipts; it grants no execution authority.

Static inspection also found that these two producers omit the current run-manifest provenance fields. Archive coverage alone is insufficient: a versioned implementation must supply the run schema while retaining the original scientific output and source identity.

A related live transport defect was observed in [RUN-ECDLP-2ac930](../experiments/EXP-ECDLP-8cc60d/runs/RUN-ECDLP-2ac930/execution-receipt.json): the complete frozen G2 workload and independent checker both exited 0, but the supervisor recorded invalid_output because manifest.yaml has no top-level run key. The raw data and all logs are retained, and validated coverage remains zero. This is an output-contract failure, not evidence against the mathematical hypothesis.

Exit criteria now explicitly include a supported additive repair/retry route, complete supervisor archive coverage, schema-valid provenance from a versioned implementation, unchanged scientific parameters, and a newly admitted immutable record. No historical failed receipt may be overwritten or retrospectively relabeled output_validated.
