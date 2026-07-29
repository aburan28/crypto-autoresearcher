# TASK-20260729-037 — Independent validation of the committed EXP-YIELD-003 run package

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** validator — **independent session required**
- **Depends on:** TASK-20260729-035, TASK-20260729-036
- **Runs concurrently with:** TASK-20260729-038 (`max_concurrent: 2`)
- **Archived by:** TASK-20260729-039
- **Budget:** 3600 s, 4 GB
- **Report id:** **VAL-20260729-002**. Do **not** reuse `VAL-20260729-001`,
  which already labels two committed reports and is a duplicated immutable
  identifier on this campaign's record.
- **Inference policy requested:** `review-adversarial`; see INT-BATCH013-D.
  Record `resolved_model_id` with `model_verified: false`. **Session**
  independence is what this card buys; **model** independence is not claimed.

## Objective

Establish independently whether the package is **valid and admissible before
anything is inferred from it**, and recompute its primary observation from the
raw per-tuple data. Return PASS or FAIL with `blocks_ledger_record` set
explicitly and every required narrowing stated as a self-contained sentence the
Coordinator can adopt verbatim.

## Exact artifact paths

- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-037/validation_report.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-037/recount_note.md`

## Exclusive write scope

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-037`

## Constraints

- **No shared conversation lineage** with TASK-20260729-031, -033, -035 or
  -038. **State the basis** of independence.
- **Validity before interpretation.** Expected run count, schema-complete
  manifests, seed integrity, raw-to-summary agreement, control comparability —
  checked first, and say plainly whether the run set is admissible. An invalid
  or incomplete run set goes back to the Executor with concrete defects listed;
  it is not evidence.
- Verify the snapshot yourself and **recompute every recorded SHA-256 from the
  Git blobs at that commit**.
- **Derive all seeds independently** from the contract text and check the
  disjointness claim against the 105 committed EXP-YIELD-002 seeds and the
  BATCH-011 block. Any collision is **BLOCKING**.
- **Recompute the primary observation from the raw per-tuple means and standard
  deviations** — the `z_sem` vector, its mean, sd and SEM, `n_neg` and the
  tuples it names — and report the maximum absolute difference against the
  package's own values.
- **Re-execute the committed driver blob** against the committed inputs in a
  scratch root **outside the repository** and diff at exact float equality;
  report every differing leaf. **Scope the result honestly:** a reproduction on
  the same platform, interpreter and numpy establishes **determinism of the
  recorded pipeline, not portability** — exactly as NARROW-5 required of
  BATCH-012.
- Check the DEV-4 repair independently and state whether the difference column
  now has a quantifiable error bar or still does not.
- **Audit the platform statement.** Report exactly what interpreter build,
  numpy version, OS and architecture were used, whether they differ from the
  committed EXP-YIELD-002 run, and whether the package's own language is honest
  about what did **not** change. **If the run describes itself as a
  fresh-platform replication without a changed platform, that is BLOCKING.**
- **Do not apply the resume condition and do not dispose of the shift.** Report
  the numbers and their reliability; the disposition is DEC-20260729-003's.
- Every required narrowing is a **numbered, self-contained sentence**;
  `blocks_ledger_record` is set explicitly true or false.
- Any probe outside the repository is **UNARCHIVED AND NOT EVIDENCE**.
- **Make no commit**; write nothing outside the write scope; name explicitly
  anything not reached inside 3600 s.
