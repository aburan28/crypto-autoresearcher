# TASK-20260817-4d5e6f -- Execute frozen EXP-SSI-697354: p*(w) crossover-locus reconstruction (zero-compute, stdlib-only)

     goal / batch    GOAL-SSI-001 / BATCH-5a3d0a
     role            executor
     policy          executor-implementation      effort medium
     state           queued
     depends_on      none (EXP-SSI-697354 is a frozen, coordinator-approved contract)
     review_required true (independent Validator + Red Team, review-adversarial,
                       after this task's own snapshot archive -- not yet
                       dispatched)
     budget           3600 s, 1 GB, 1 run
     claim tier      medium (per specification.yaml; unchanged by this task)
     execution       IMPLEMENTATION AND EXECUTION ARE AUTHORIZED. This is a
                     zero-compute stdlib-only run, not a design-gate task.

## What this task does

Materializes the ONE future-batch executor handoff that GOAL-SSI-001's own
current_batch BATCH-5a3d0a (mode coordinator_direct_correction,
batch_manifest.json "queued_not_dispatched" item 3) explicitly deferred.
Executing the FROZEN contract EXP-SSI-697354:

  (a) Re-read and re-extract the frozen inputs T1, T2, and T3
      per specification.yaml's own frozen_values_x /
      frozen_values_y / frozen columns. Any input drift
      INVALIDATES the run (AGENTS.md rule 5: infrastructure signal,
      not mathematical evidence).
  (b) Build the per-entry law, the two MC formulas, and the
      baseline formula per specification.yaml's cost_functions
      block exactly, and the crossover-procedure exactly as
      declared there.
  (c) Run the gate (RG-1..RG-5) FIRST. If any RG assertion
      fails, emit the gate report and stop (F1: run invalid).
  (d) Run the two null arms through the IDENTICAL code path
      with only E(.) swapped, and report D_null0, D_null1,
      and the locus displacement per specification's
      controls.NULL-OBJECT block.
  (e) Run the 4480 main-grid cells and the 2240 null-grid
      cells per the crossover-procedure; write a row for
      every cell with the declared categorical label
      (numeric p*, NO_CROSSOVER_IN_WINDOW,
      INFEASIBLE_AT_MEMORY, MULTIPLE_ROOTS,
      ROOT_OUTSIDE_WINDOW) plus the fit-window
      extrapolation stamp on every number.
  (f) Compute each of the 5 monotonicity limbs per
      specification's controls.MONO-MEMORY block, and
      report a verdict or NOT_EVALUABLE(n=count) for MONO-3.
  (g) Write all 12 declared artifact files under
      experiments/EXP-SSI-697354/runs/RUN-SSI-697354-a/
      exactly as enumerated in specification's
      required_artifacts list.
  (h) Return execution_report.yaml summarising per-control
      verdicts, protocol deviations, anomalies, and
      observations (recording-not-discarding rule).

## What it does not do

Does NOT make a C1/C2 statement in either direction. Does
NOT change any hypothesis, experiment, or goal status.
Does NOT assert that SQIsign or any SQIsign parameter set
is broken, weakened, or unsafe. Does NOT emit any sentence
from specification.yaml's claim_ceiling.forbidden_sentences
in any artifact. Does NOT run XCHK-2's numpy cross-check
unless numpy is importable; if not, it is NOT_RUN with the
ImportError text and no reported number changes. Does NOT
import sagemath, sage, g6k, fpylll, scipy, or mpmath at any
point (forbidden per specification.yaml's
dependency_contract.forbidden). Does NOT make any network
access. Exactly one run; seed 0; deterministic; a re-run
is byte-identical apart from timing fields. No
post-hoc change to the scenario grid, tolerance windows,
the w grid, or the frozen reference values after any
output has been observed.

## Execution boundary

Implementation and real execution are authorized for this
task because DEC-20260806-a00a28's predecessor decision
(BATCH-b3c87f) and its design_report at TASK-20260806-
976fd5 both explicitly commissioned execution of this
contract "with no new compute and no unavailable
dependency". Budget is maximum_runs=1,
wall_clock_seconds=3600, memory_gb=1, per
specification.yaml's own budget block. An outer OS-level
`timeout` backstop of 3660 s applies (60 s margin,
matching the TASK-20260815-f14d3c precedent in
GOAL-MLKEM-005).

## Next steps after this task

1. A Coordinator-only snapshot archive (TASK-20260817-
02b01b-style task id; here TASK-20260817-a1b2c3 per
this batch's dispatch queue) commits this task's own
artifacts alone, before either review reads them.
2. Independent Validator and Red Team tasks verify
the run's own controls and scope independently.
3. A Coordinator ledger archive decides -- explicitly,
not by default -- what, if anything, the outcome
promotes or records.

## Artifact

     coordination/goals/GOAL-SSI-001/batches/BATCH-5a3d0a/tasks/TASK-20260817-4d5e6f/
