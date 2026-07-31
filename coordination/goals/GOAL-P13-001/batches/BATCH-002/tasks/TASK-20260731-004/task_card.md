# TASK-20260731-004 — Red team — Attack the NC-2 measurement in whichever direction it fell

**Goal** GOAL-P13-001 · **Batch** BATCH-002 · **Role** red-team · **Priority** 85
**Depends on** TASK-20260731-001, TASK-20260731-002 · **Archived by** TASK-20260731-005
**Budget** 3600 s wall clock · 4 GB · maximum_runs 1 · **independent session required**

> **The queue governs.** This card mirrors the `handoff` block for
> TASK-20260731-004 in
> `coordination/goals/GOAL-P13-001/batches/BATCH-002/dispatch_queue.json`.

---

## Objective

**Falsify the interpretation** of the NC-2 measurement — in whichever direction
it fell.

## Attack the direction that actually came out, and say which one

- If the batch reports a **small `c`** (threatened margin): attack the
  measurement for **understating** the true cost — unmeasured overheads (EA-2),
  the tiny-`B` regime (EA-3), the very small tables at this scale, the ℓ-mixture
  confound.
- If it reports a **large `c`** (comfortable margin): attack it for
  **overstating** — interpreter overhead, the absence of batched Φ evaluation
  (EA-4), Sage's generic root finding, per-call dispatch cost dominating real
  arithmetic at 20–40 bits.

**The program's failure mode here is accepting whichever direction is
comfortable. Your job is to make that impossible.**

## The highest-value attack is the extrapolation

`p ≤ 2^40` to `log2 p = 256` is a **6.4-fold extrapolation in `log2 p`** from a
fit with at most 8 points, in a `B` regime that never reaches the operating `B`.
**State plainly whether you believe the extrapolation supports any NIST-I
statement at all.** *"The extrapolation does not support a NIST-I statement"* is
an admissible and valuable finding.

## Attack identifiability on all four axes

1. Is the fitted slope separable from the **drifting ℓ-mixture**? Check FIT-ELL
   (ℓ = 2 alone, ℓ = 3 alone) against the pooled fit.
2. Separable from the **host**? Check CTRL-CAL's own fit.
3. Separable from **nothing at all**? Check CTRL-NULL.
4. Are **M-A and M-B distinguishable** on this range, and does the report admit
   that they are not?

## Adversarial mutation selection is binding practice here

**CTRL-RT039-A**: select **your own** perturbations; do not merely re-run the
producer's controls. A control chosen by the author of the thing under test is
weaker evidence than one chosen by an adversary.

Required perturbations, with **how far `c` moves under each**:

- leave-one-prime-out;
- refit on the shortest 5-prime sub-range;
- median vs mean;
- normalised vs raw seconds.

**If `c` moves more than its own reported interval under leave-one-out, the
interval is too narrow — say so.**

## Attack the seeding decision

SEED-A was chosen by the Coordinator with a stated basis. Say whether the basis
holds, whether SEED-B's measured effect makes the reported constant
**seeding-dependent**, and whether a *third* strategy would move it further.
**GAP-1 is an open defect and the choice made here is a decision, not a
derivation.**

## Rules

- **Independent session.** You did not originate the run and you did not write
  the contract. **Attack both.**
- Do **not** call a scoped failure an impossibility result, and do **not** call
  an implementation artifact a mathematical fact.
- A timeout, crash or infrastructure failure is **never** a negative
  mathematical result and may not be used as one in your attack.
- **Name an end-to-end baseline and one concrete next control**, with the reason
  it is the cheapest discriminating one. If it is NC-1 or NC-3 as already
  recorded, **say so** rather than renaming an existing control.
- Do **not** reopen GAP-2, Section 4.1 or Heuristic 1 on the merits. You may
  cite them as limitations of what this batch can conclude.
- **Failed attacks are reported as failed.** A red team that found nothing says
  so; it does not manufacture an objection.
- **Make no commit.** Write only under your own review directory.
- Record provenance honestly, including that **model-level independence from the
  producer is unavailable under this harness** and that your adversarial
  mutation selection is the **mitigation** for that, not a substitute for it.
- Bounded card. If you cannot finish, **stop and report a bounded partial red
  team naming exactly which attacks you did not run**. Never fabricate an attack
  you did not perform or a number you did not compute.

## A note on your predecessor

The BATCH-001 red team's `c ~ 1.8` calibration and the resulting 2.3-bit NIST-I
margin are **committed estimates, not measurements**. You are the first reviewer
in this campaign who can check them **against a measurement**. Do so, in both
directions, and say plainly whether the measurement supports, contradicts or
cannot discriminate against that estimate.

## Deliverables

```
.../reviews/TASK-20260731-004/red_team_report.yaml
.../reviews/TASK-20260731-004/red_team_notes.md
```

## Completion gate

RT1–RT10 as stated in the queue's `handoff.completion_gate` for this task.
