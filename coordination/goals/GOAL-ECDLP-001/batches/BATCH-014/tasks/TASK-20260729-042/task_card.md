# TASK-20260729-042 — Independent pre-execution review of the frozen EXP-STR-004 contract

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-014 `dispatch_queue.json`. Where they disagree, the queue governs.

- **Role:** reviewer — **independent session required, non-originating**
- **Depends on:** TASK-20260729-040, TASK-20260729-041
- **Archived by:** TASK-20260729-043
- **Report id:** `RT-20260729-034` (cite by path and task id everywhere)
- **Budget:** 3000 s, 2 GB
- **Inference policy:** `review-adversarial` (xhigh, independent session). A
  capability gap is recorded in `degraded_requirements` — **the review is not
  silently downgraded.**

## Objective — return PASS or REVISE before any measurement

Answer eight questions:

1. Is the derivation note's rule for `T(cell)` correct, and does it follow from
   the **committed source** rather than from an assumption about it?
2. Is every prediction genuinely a **set identity at a named cell**, with no
   cardinality anywhere doing dispositive work?
3. Is the base-row budget genuinely matched across the two arms and genuinely a
   function of B alone — controlled **by construction**, not by assertion?
4. Is the `mixed` verdict branch **reachable**, and can any of F-1…F-5 fail to
   be evaluable at any named cell?
5. Does the contract smuggle in a third arm, a cost claim, a density penalty, a
   scaling law, or any statement about H-STR-002's **mechanism**?
6. Is the Sage verifier genuinely **independent** of `harness/toycurve.py`, and
   is it invoked through the `sage` binary rather than as a Python import?
   (`import sage` from the system python3 **fails on this host** — a
   Python-import invocation is BLOCKING.)
7. Does any number in the contract come from an **unarchived source**?
8. Are the wall-clock and artifact-size budgets survivable on a volume at 99%,
   and does every breach have a disposition naming it **infrastructure signal**?

## Why this card exists

In BATCH-012 a **false pre-registered numeric claim survived three independent
pre-execution reviews** and was caught only after execution. In EXP-STR-003 a
**mis-specified comparative control passed review and fired F1**. This card
catches the analogous slip for 3000 seconds instead of after the fact.

## Method constraints

- **Re-derive the derivation note yourself from the committed source.** Do not
  check it by reading it. If you cannot re-derive `T(cell)`, say so and mark it
  **BLOCKING** — the whole of P-2 rests on it.
- **Hunt for a cardinality doing dispositive work.** RT31-5 records this failure
  as having recurred five times in this lineage, twice inside artifacts that had
  already passed independent review.
- **Check every arithmetic claim the contract makes about itself** — cell
  counts, run counts, path counts, budget sums — **and name the members behind
  each count**.
- **Say plainly whether a favourable outcome would support H-STR-002.** If the
  contract permits a reading in which `alpha <= 3` at every ladder cell is
  presented as support *while arm E-prime does the same*, that is **BLOCKING**.

## Output discipline

Rank objections BLOCKING / MAJOR / MINOR / INFORMATIONAL and state for each
BLOCKING item what would discharge it. **A PASS with conditions must state
those conditions in a form the Coordinator can record verbatim in the
TASK-20260729-043 receipt before dispatch** — conditions you do not state
cannot be imposed later, because *a condition recorded after the fact is not a
condition* (D-2).

**Pre-state the verdict label each realised branch should carry**, and record
that you pre-stated it and that neither `EV-STR-004` nor `DEC-20260729-004`
existed at the HEAD you reviewed.

Make no commit, change no research state, write nothing outside your write
scope. Model independence is unavailable and is not claimed; assert **session**
independence. Name explicitly anything you did not reach inside the cap.
