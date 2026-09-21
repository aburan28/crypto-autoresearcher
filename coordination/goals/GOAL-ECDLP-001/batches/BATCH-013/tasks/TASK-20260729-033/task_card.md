# TASK-20260729-033 — Independent pre-execution review of EXP-YIELD-003

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** reviewer — **independent session required, non-originating**
- **Depends on:** TASK-20260729-031, TASK-20260729-032
- **Archived by:** TASK-20260729-034
- **Budget:** 2400 s, 2 GB
- **Inference policy requested:** `review-adversarial`. The adapter may
  **refuse** it on the alternate backend (INT-BATCH013-D). Record
  `requested_policy`, `resolved_model_id`, `model_verified: false` and fallback
  status honestly. **Session** independence is what this card buys; **model**
  independence is not available and must not be claimed.

## Objective

Return **PASS or REVISE** on the committed contract *before any draw*, by
re-deriving its arithmetic independently and answering six questions:

1. Are the three master seeds genuinely disjoint from every committed seed
   block, and does the collision rule actually fire?
2. Is the DEV-4 repair the *named* repair, and does it in fact give the two
   high-precision legs **distinct** derived seeds at every tuple?
3. Does the contract smuggle in **any** criterion, threshold, verdict or branch
   on the replicated `z_sem` statistic?
4. Does the platform clause state honestly what a same-platform replication
   cannot establish — or is it satisfiable by silence?
5. Does the contract reproduce the false C-20 power sentence or create a new
   mandatory-sentence clause? Is `PRED-ID` extended to count and magnitude
   statements, and does that extension survive a test?
6. Does any number come from an unarchived source rather than the committed
   EXP-YIELD-002 or BATCH-011 packages?

## Exact artifact paths

- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-033/contract_review.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-033/independence_and_platform_note.md`

## Exclusive write scope

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-033`

## Constraints

- **Review the committed blobs, not the working tree.** Verify the snapshot
  yourself: reachability, first parent, exact changed-path set, content hashes.
  Record what you verified and what you did not.
- **Re-derive; do not adjudicate by quotation.** Recompute and display the
  single-replicate sd, the SEM at the fixed replicate count, and the SEM of the
  48-tuple `z_sem` mean under an independent-stream design, at the four
  INV-4-failing tuples and at a sample of passing tuples **you** choose.
- Derive **all** seeds yourself and check the disjointness claim against the
  105 EXP-YIELD-002 seeds and the BATCH-011 block. A declared disjointness the
  seed rule does not produce is **BLOCKING**.
- Check the DEV-4 repair **mechanically**. A nominal repair is **BLOCKING**.
- Hunt for a smuggled criterion. If any realised value could be reported as a
  pass or failure of anything, say so.
- Attack the platform clause adversarially. A clause satisfiable by silence is
  a defect.
- Check scope creep **in both directions** — anything computed or implied
  beyond RC-21A and RC-21B, and anything a binding freeze condition required
  that the contract answered in words without changing the thing required.
- `confirmatory_status` must be `exploratory_only`; flag any conflation of
  pre-registration *order* with confirmatory *standing*.
- **Zero curve compute, zero pre-emption. Do not run the replication.** Any
  probe outside the repository is labelled **UNARCHIVED AND NOT EVIDENCE** and
  carries no conclusion.
- State every pre-dispatch condition as a **numbered, self-contained sentence**
  the Coordinator can record verbatim, and state that it must appear in the
  TASK-20260729-034 receipt **before** TASK-20260729-035 is dispatched. D-2 is
  this program's worked example of what a late recording costs.
- Distinguish absence of evidence from impossibility; declare no direction
  impossible.
- `verdict` is PASS or REVISE. A REVISE with no blocking objection is not a
  REVISE; a PASS listing blocking objections is not a PASS.
- **Make no commit**; write nothing outside the write scope. Name explicitly
  anything not reached inside 2400 s.

## Why this card exists

BATCH-012's lesson is exact and not hypothetical: a **false** pre-registered
numeric claim survived **three** independent pre-execution reviews and was
caught only after execution.
