# TASK-20260729-018 — Execute EXP-YIELD-002 (curve-free)

**Mirror.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/dispatch_queue.json`.
Where this file and that queue disagree, **the queue governs**.

| | |
|---|---|
| **Role** | executor |
| **Depends on** | TASK-20260729-016 (PASS), TASK-20260729-017 |
| **Archived by** | TASK-20260729-019 |
| **Budget** | 1800 s, 4 GB, `maximum_runs: 3` |
| **Inference** | requested policy `executor-implementation`; record the resolved model, provenance and probe status honestly, and any `policy_binding_mismatch` |

## Objective

Implement the frozen driver exactly as specified and execute three curve-free
runs, recording **observations only**: per cell, the mean and sd of the distinct
occupancy of the **pre-marked** antipodal null, the same for the **unrepaired**
as-recorded null, the known-answer checks, and the standardized residual of each
against the **unchanged** `P_pred` under **both** pre-registered denominator
readings.

## Exclusive write scope

`experiments/EXP-YIELD-002/driver`, `/runs`, `/results` — nothing else.

## Artifact paths — exactly 11 files, and no others

- `experiments/EXP-YIELD-002/driver/repaired_null.py` (**exactly one driver
  file**; no helper modules, notebooks, scratch output, plots or AppleDouble
  sidecars)
- `experiments/EXP-YIELD-002/results/summary.json`
- `experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-REPAIRED/{manifest.json, results.json, stdout.log}`
- `experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-ASRECORDED/{manifest.json, results.json, stdout.log}`
- `experiments/EXP-YIELD-002/runs/RUN-YIELD-002-KNOWNANSWER/{manifest.json, results.json, stdout.log}`

Every run directory gets all three files **even if the run does not complete**,
with the terminal status in the manifest. That is what makes the twelve-path
archive declaration exact in advance.

## Hard constraints

- **Zero curve arithmetic.** No point addition, doubling, scalar
  multiplication, DL table, sum set, factor base, census, summation polynomial
  or Gröbner basis. If you find yourself needing a curve, **stop and report** —
  the contract has a defect.
- **Do not read or import `experiments/EXP-YIELD-001/driver/yield_census.py`.**
  Implement `occupancy_prediction` and both null processes from the contract
  text and the committed recorded quantities alone, and record in every manifest
  that you did so and did not open that file. This is a declared independence
  condition. **It is not a discharge of RC-F and you may not claim one.**
- **Compare against the unchanged `P_pred`.** Do not repair, adjust, re-derive
  or re-fit it. The whole content of the experiment is whether the repaired
  *process* reaches the unmoved *prediction*.
- **Report both denominator readings at every cell, always** — never only the
  more favourable one — with the replicate count that produced each.
- Seeds recorded and distinct per run and per cell, derived by a recorded rule,
  every derived value recorded beside the number it produced. `summary.json` is
  derived by the driver from the three `results.json` files and must be
  reproducible from them; hand-write no number into it.
- Manifests schema-complete per the AGENTS.md artifact policy.
- **Observations only.** No interpretation, no efficiency `E`, no yield ratio,
  no outcome-branch evaluation, no `INV-4` re-disposition, no `INV-5`
  determination, no evidence or decision record, no hypothesis-status statement,
  no edit to any ledger, knowledge or coordination record.
- A timeout, crash, resource exhaustion or implementation failure is
  **infrastructure signal** and is never a negative result about the diagnostic,
  about `P_pred` or about anything else.
- **If the prediction misses, report the miss plainly and completely.** Do not
  re-run with different seeds, do not add replicates outside the pre-registered
  schedule, do not add an arm. A miss is an admissible, pre-registered outcome
  whose meaning is already recorded, and reporting it accurately is the
  highest-value thing this card can do.
- **Make no commit.** TASK-20260729-019 commits this package.
- If the cap binds, run the contract's declared priority order — **the four
  `INV-4`-failing cells first** — and name every cell not reached.

## Completion gate

`E1`–`E10` as listed in the queue entry.
