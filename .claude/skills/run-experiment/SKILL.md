---
name: run-experiment
description: >-
  Execute an approved experiment (EXP-*): validate the frozen specification,
  implement it, run bounded replicated runs with deterministic seeds, and
  write immutable run records and an execution report. Use after
  /design-experiment has produced an approved contract.
---

# Run experiment

Run lifecycle steps 6–7 (`docs/task-lifecycle.md`): execution and
validation.

## Steps

1. Locate `experiments/<EXP-ID>/specification.yaml`. Confirm status is
   `approved` and `approved_by` is set; otherwise stop and report a
   `specification_error` — do not "just run it anyway".
2. Dispatch the **executor** subagent with the specification and the matching
   handoff record from `ledger/handoffs/`. It must:
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
4. Report to the user: run tally by terminal status, anomalies, protocol
   deviations, and whether the completion gate passed. Do NOT interpret
   results — that is `/review-evidence`.

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
