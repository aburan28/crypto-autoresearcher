# TASK-20260729-035 — Execute EXP-YIELD-003 (RC-21A replication, RC-21B block, known-answer arm)

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** executor
- **Depends on:** TASK-20260729-033, TASK-20260729-034
- **Archived by:** TASK-20260729-036
- **Budget:** 1800 s, 4 GB, `maximum_runs: 3`
- **Inference policy requested:** `executor-implementation`. The adapter is
  known to resolve this role to a different model than the session reports
  (INT-BATCH013-D) — **disclose, never substitute**.

## Gate

**Run only if the TASK-20260729-034 receipt records
`approval_determination: APPROVED`.** If it records NOT APPROVED, **STOP AND
REPORT** and write no run record.

## Objective

Execute the frozen contract exactly as written under fresh master seeds
**130301** (replicate arm), **130401** (known-answer arm) and **130501**
(high-precision block), on the most genuinely different interpreter build
available on this host, producing three immutable run records and one results
summary — reporting the mean, sd and SEM of `z_sem` over the 48 declared tuples
**as an observation feeding no criterion**.

## Exact artifact paths (11)

- `experiments/EXP-YIELD-003/driver/replicate_repaired_null.py`
- `experiments/EXP-YIELD-003/results/summary.json`
- `experiments/EXP-YIELD-003/runs/RUN-YIELD-003-REPLICATE-REPAIRED/{manifest.json, results.json, stdout.log}`
- `experiments/EXP-YIELD-003/runs/RUN-YIELD-003-HIGHPREC/{manifest.json, results.json, stdout.log}`
- `experiments/EXP-YIELD-003/runs/RUN-YIELD-003-KNOWNANSWER/{manifest.json, results.json, stdout.log}`

## Exclusive write scope

`experiments/EXP-YIELD-003/driver`, `experiments/EXP-YIELD-003/results`,
`experiments/EXP-YIELD-003/runs`

## Constraints

- **Provenance, stated honestly.** You **may** read
  `experiments/EXP-YIELD-002/driver/repaired_null.py` — EXP-YIELD-003 is a
  declared *replication* of that arm and pretending otherwise would be theatre
  — but you **must record in every manifest** whether you read it and which
  parts you reused. You **must not** read or import
  `experiments/EXP-YIELD-001/driver/yield_census.py`, and must record that.
- **Zero curve arithmetic.** No point addition, doubling, scalar
  multiplication, discrete-log table, sum set, factor base or census. Nothing
  imported from `harness/` or `tools/`. Permitted: Python standard library and
  numpy.
- **Change only the seed.** Use exactly 130301 / 130401 / 130501. Do not raise
  the replicate schedule, alter the tuple set, alter the denominators or alter
  the pre-marking. The whole evidentiary content is that only the seed changed.
- **Apply the DEV-4 repair** — legs `HIGHPREC-REPAIRED` and
  `HIGHPREC-ASRECORDED` in the seed string — and **verify and log** that the
  two legs derive different seeds at every high-precision tuple *before*
  drawing.
- **Record the environment before the first draw**: `sys.version`,
  `sys.executable`, `platform.platform()`, `platform.machine()`,
  `platform.processor()`, `numpy.__version__`, exact strings, in `stdout.log`
  and every manifest.
- **Attempt a genuinely different interpreter build** from the committed run's
  python 3.13.1 / numpy 2.4.0, and **record what you obtained and what you
  could not**. If no different build is available, **say so plainly**, naming
  what you looked for. If no different OS or architecture is available — the
  expected case on a single-host harness — **say so plainly**. **Do not
  describe the run as a fresh-platform replication if the platform did not
  change**, and do not omit the attempt silently. An honest *"no different
  build was available on this host"* is a complete answer; a claim of
  portability that was not tested is a fabrication.
- Verify the two hash-bound inputs before any draw. A mismatch is an
  invalidation, not a repair opportunity.
- **Every run directory gets all three files** — `manifest.json`,
  `results.json`, `stdout.log` — even for a cancelled, failed, exhausted or
  invalidated run, with the terminal status in the manifest.
- Report **both** denominator readings at every one of the 48 tuples.
- **Dispose of nothing.** Report mean, sd, SEM of `z_sem` and `n_neg` with the
  tuples named. Do **not** evaluate a criterion, declare a branch, apply the
  resume condition, or say whether the shift reproduced — that belongs to
  TASK-20260729-039 after two independent reviews.
- Every statement reporting a **count** says it is a count and names the
  tuples; every statement reporting a **magnitude** says so. The
  cardinality-not-identity failure has occurred three times in this campaign.
- Declare every protocol deviation explicitly, numbered, with its effect size
  where one exists.
- **Make no commit.** Write nothing under `ledger/`, `knowledge/`,
  `coordination/`, `harness/`, `tools/`; no AppleDouble sidecar; delete nothing
  outside the write scope.
- **Stop and report on overrun.** Name exactly which tuples were not reached.
  A timeout, crash or resource exhaustion is **infrastructure signal and never
  a negative mathematical result**.
