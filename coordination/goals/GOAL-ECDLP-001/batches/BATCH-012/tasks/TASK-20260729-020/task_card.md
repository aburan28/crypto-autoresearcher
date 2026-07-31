# TASK-20260729-020 — Independent validation of the EXP-YIELD-002 run package

**Mirror.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/dispatch_queue.json`.
Where this file and that queue disagree, **the queue governs**.

| | |
|---|---|
| **Role** | validator |
| **Depends on** | TASK-20260729-018, TASK-20260729-019 |
| **Archived by** | TASK-20260729-022 |
| **Budget** | 3600 s, 4 GB, `maximum_runs: 2` (your own re-implementation and one repeat; authorizes no execution of the Executor's contract) |
| **Inference** | requested policy `review-adversarial`, effort `xhigh`, **independent session required** |

## Objective

Independently establish whether the package is **valid evidence at all**, before
anyone interprets it: expected run count, schema-complete manifests, seed
integrity, raw-to-summary agreement, control comparability against the committed
BATCH-011 null, and an **independent re-implementation** of both null processes
and of `occupancy_prediction` from the contract text alone, reproducing at least
the four `INV-4`-failing cells end to end.

## Artifact paths

- `.../BATCH-012/reviews/TASK-20260729-020/validation_report.yaml` — explicit
  `verdict` (`PASS` / `PARTIAL` / `FAIL`) and explicit `blocks_ledger_record`
  boolean; every required narrowing written as a **verbatim-adoptable sentence**.
- `.../BATCH-012/reviews/TASK-20260729-020/recount_note.md` — the independent
  re-implementation, its code sketch and its numbers.

## Constraints

- **Independent session**: no shared lineage with TASK-20260729-014, -016 or
  -018. **Model independence is not available and must not be claimed**
  (`INT-BATCH012-D`).
- Validate the **committed** package. Verify the snapshot commit's
  reachability, first parent, exact changed-path set and content hashes
  yourself, and record what you verified and what you did not.
- **Re-implement, do not re-read.** Write your own minimal simulator — not the
  Executor's driver — for both the pre-marked and the as-recorded processes, and
  your own `occupancy_prediction`, from the contract text alone. A recount that
  merely re-reads `results.json` is not a recount and must not be reported as
  one. Disagreements are reported with **both** numbers and not adjudicated by
  preference.
- **Recompute both denominator readings yourself** at every cell you check, and
  name any cell where the package reports only one.
- Check the bin accounting as an artifact risk: `(N−1)/2` antipodal-pair bins
  plus the identity bin; pre-marked bins counted once; pre-marking uniform
  without replacement; the odd-`C_red` rule; the `(N−1)`-versus-`N` bin-count
  term. Each shifts the mean by a stated amount; report any silent divergence
  from the frozen contract.
- Check the comparability arm specifically: does the as-recorded arm reproduce
  the committed `RUN-YIELD-001-NULL-RANDOM-SUMSET` per-cell means within the
  contract's numeric tolerance? A repaired arm that cannot be compared to the
  recorded package is an **invalidation**, not a result — and the contract says
  so in advance.
- A timeout, crash or resource exhaustion in the package is **infrastructure
  signal**, never negative evidence about the diagnostic.
- **If the prediction missed, validate the miss as carefully as you would
  validate a hit, and say so.** A miss is the higher-information outcome and the
  one most likely to be explained away; establish whether it is a real miss or a
  simulator artifact, and say which.
- **Do not interpret the mechanism.** Your verdict is on validity — receipt,
  simulator, controls, metric — not on what the result means for the BATCH-011
  reading. Change no official state. **Make no commit.**
- Name explicitly any check you did not reach inside the cap.

## Completion gate

`V1`–`V10` as listed in the queue entry.
