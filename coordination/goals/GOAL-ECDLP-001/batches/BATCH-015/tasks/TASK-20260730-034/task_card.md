# TASK-20260730-034 — Falsification and scope review of the probe

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-015 `dispatch_queue.json`. **Where they disagree, the queue governs.**

- **Role:** red-team — **independent session required**
- **Depends on:** TASK-20260730-032
- **May run concurrently with:** TASK-20260730-033 (disjoint write scopes)
- **Archived by:** TASK-20260730-035 (ledger, runs alone)
- **Budget:** 2400 s, 2 GB, `maximum_runs: 1`

## Objective

Attack the probe **and the reading that will be made of it**. Build the
strongest case that the probe does **not** establish what a successor will be
tempted to say it establishes.

In particular: the two facts it settles about **committed code** do not settle
**driver fidelity**, which is unreachable by any probe **because the driver has
never been written** — neither arm's closure is committed code. No measured
supply figure licenses any statement about alpha, rank, cost, diagnosticity or
H-STR-002. **No counterexample certificate exists**, and that is the honest
price of the stand-down.

## Required checks

1. **Was the falsification condition reinterpreted?** It was frozen in the
   BATCH-015 opening commit, **before the probe existed**: a **short list** at
   B = 192 or B = 193, or a base-row shortfall of **two or more** at any cell.
   Any artifact applying a different threshold, comparison or scope is a
   **BLOCKING** finding. **Check the commit order against Git** rather than
   taking it on assertion.
2. **Check the prohibition list item by item** — every entry of the queue's
   `preserved_specification_authority.WHAT_MUST_NOT_BE_CARRIED_FORWARD`. State
   whether any BATCH-015 artifact violates it and **quote the offending text**.
3. **Check for re-adjudication of BATCH-014.** DEC-20260729-004 `refine`, the
   REVISE contract review, the NOT APPROVED determination and the
   QUEUE-AMEND-20260729-005 stand-down are **committed facts**. Any artifact
   arguing for or against them, or treating EXP-STR-004 as approved, or
   treating it as ambiguous between the two frozen copies, is **BLOCKING**.
4. **Name the cheapest discriminating control you would actually run, and one
   you would NOT run**, so your recommendation is falsifiable. **Record what
   would falsify your own recommendation**, as the BATCH-014 red team did in
   its third dissent — the dissent this batch adopted and pre-registered.
5. **State the Pareto position honestly** with `dominated_by` and `sota_delta`.
   The only reproducible speedup measured anywhere in this lineage is the
   classical constant factor r = 3, already the specialized baseline of
   Wiener–Zuccherato and Duursma–Gaudry–Morain, and **a constant factor is not
   target-class under rule A1**.

## Both failure modes are live

**Premature closure is a failure mode symmetric with overclaiming**
(`docs/inventor-protocol.md`). If the probe's output genuinely supports
reopening the execution question **on the merits**, say so — do not decline
because the target looks saturated. Equally, do not manufacture a reason to
proceed.

## Standing prohibitions

- **Do not propose enlarging this batch.** Any control you name is a candidate
  for a successor and is **not dispatched here**. You may not recommend
  approving or executing EXP-STR-004 — that is not this batch's to approve.
- EV-STR-001's yield penalty is the **range 17.5x to 4128.6x** and is never
  quoted as 17.5x alone. The C-20 power sentence may never be quoted
  unaccompanied by the RT21-1 correction. **Do not issue RT-20260729-036 to
  anything.**
- **Mint no `RT-*` report identifier.** Your report is cited **by path and task
  id only** and must say so in its own text.
- **Session independence is required and asserted separately. Model
  independence is not available and is never claimed** (INT-BATCH015-D). Do not
  count this session toward any completion quorum.

## Deliverables

```
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-034/red_team_report.yaml
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-034/falsification_review.md
```

## MAKE NO COMMIT

Write nothing outside your review directory. **Your files must not be committed
before the TASK-20260730-035 ledger commit.**

If you cannot finish inside 2400 s, **stop and report a bounded partial review
naming exactly which lines of attack you did not reach.**
