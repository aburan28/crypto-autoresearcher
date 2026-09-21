# TASK-20260729-038 — Independent red-team falsification review of the committed EXP-YIELD-003 run package

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** red-team — **independent session required**
- **Depends on:** TASK-20260729-035, TASK-20260729-036
- **Runs concurrently with:** TASK-20260729-037 (`max_concurrent: 2`)
- **Archived by:** TASK-20260729-039
- **Budget:** 2400 s, 2 GB
- **Report id:** **RT-20260729-031**. Do not reuse any existing RT identifier.
- **Inference policy requested:** `review-adversarial`; see INT-BATCH013-D.
  Record `resolved_model_id` with `model_verified: false`. **Session**
  independence is required; **model** independence is not claimed.

## Objective

Attack the package **and the reading a Coordinator will want to take of it**.
State the **narrowest true statement** the package licenses, name every
objection at a declared severity, and **pre-state the decision label you would
accept for each realised branch before reading any disposition**.

## Exact artifact paths

- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-038/red_team_report.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-038/falsification_review.md`

## Exclusive write scope

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-038`

## The five attacks this card is bought for

1. **The platform framing — first and hardest.** If the interpreter build, OS
   and architecture did **not** change, say in terms what the replication
   therefore **cannot** establish, and whether any record produced by this
   batch overstates it. A run that changed only the seed separates *chance*
   from a *seed-independent deterministic property of the
   driver-build-platform combination* and separates none of those three from
   each other. Check whether the package and the receipts say so.
2. **The resume condition.** Both branches were pre-registered. Check that
   neither has been widened, narrowed or re-read against the realised number —
   and check whether a value in the interval between about 0.14 and about
   0.25 SEM, **which neither branch names**, has been handled honestly or
   silently assigned to the nearer branch.
3. **The stopping rule.** The queue's `scope_ruling` closes this lineage to
   further replication batches regardless of outcome. Say whether that is
   defensible on the committed record, or whether some outcome of this run
   would genuinely warrant another control — and if so, **name it and its
   cost**.
4. **The cardinality-not-identity failure**, which has now occurred **three
   times** in this campaign. Test every count-versus-magnitude statement in the
   package and in the receipts, including any power or sensitivity statement.
5. **The ceiling.** Name any sentence anywhere in the package or receipts that
   reaches beyond toy tier, asserts anything about decomposition yield,
   computes or quotes an efficiency or yield ratio, re-disposes INV-4,
   determines INV-5, moves a hypothesis, or touches a cost model.

## Standing prohibitions to verify

- No record quotes the **EXP-YIELD-002 high-precision difference column** as a
  confirmation of `T`.
- No record says the repaired null lands **on** `P_pred`; it lands **at or
  slightly above** it.
- The **C-20 power sentence** is not reproduced unaccompanied by the RT21-1
  correction.

## Constraints

- No shared conversation lineage with TASK-20260729-031, -033, -035 or -037.
  State the basis.
- **Name the strongest available refutation artifact and order the
  alternatives** — counterexample certificate, then derivation note, then
  declared `empirical_only` — saying which is available here and which is not,
  and why. **An undeclared basis is the failure; the absence of a proof is
  not.**
- Name required controls with **ids, costs and resume conditions**, and state
  which the stopping rule forecloses and whether you accept that.
- **Declare no lane dead**; distinguish absence of evidence from impossibility.
- Any probe is **UNARCHIVED AND NOT EVIDENCE**.
- **Make no commit**; write nothing outside the write scope; name explicitly
  anything not reached inside 2400 s.
