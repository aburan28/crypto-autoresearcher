# TASK-20260729-047 — Independent red-team falsification review of the committed EXP-STR-004 package

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-014 `dispatch_queue.json`. Where they disagree, the queue governs.

- **Role:** red-team — **independent session required, non-originating**
- **Depends on:** TASK-20260729-045
- **Archived by:** TASK-20260729-048
- **Report id:** `RT-20260729-035` (cite by path and task id everywhere)
- **Budget:** 3000 s, 4 GB
- **Inference policy:** `review-adversarial` (xhigh, independent session). If any
  claim in this batch is proposed as a **breakthrough, a closure result, or a
  contradiction of established evidence**, AGENTS.md rule 12 requires
  `review-breakthrough` at `max` effort and **that policy may not be degraded —
  if it cannot be reached, the claim is not made.**

## Objective — five rulings and exactly one recommended transition

1. Does the measured pattern licence any statement about the **instrument
   question**, or does it leave it UNADJUDICATED as EXP-STR-003 did?
2. Is the arm E-prime comparison a **matched** control this time, or does some
   nuisance variable still separate the arms?
3. Does anything licence a statement about H-STR-002's **mechanism** — the
   answer should be no — and is any record in this batch nevertheless drifting
   toward one?
4. Does the ladder licence **any** statement about independence of B beyond the
   ten named cells, and what is the strongest counter-reading of a favourable
   ladder?
5. What is the strongest checkable **refutation artifact** this result admits —
   counterexample certificate, derivation note, or declared `empirical_only` —
   and is the derivation note archived at the TASK-20260729-041 commit
   sufficient for whatever `DEC-20260729-004` will rest on?

## Why this card exists

**The precedent is this program's own.** `DEC-20260726-006` read an instrument
measurement as a mechanism result and recorded `supported`; `DEC-20260727-009`
had to weaken it, and `CORR-20260727-007` had to correct an in-place rewrite.
This card decides whether that is about to happen again.

## Method constraints

- **State the strongest case for the result first and do not soften it**, then
  take it apart. If the strongest case is weak, say so plainly rather than
  manufacturing a steelman.
- **Hunt for the cardinality-not-identity failure in every record this batch has
  produced, including the Coordinator's own receipts and commit messages.**
  RT31-5 found the fifth instance in exactly those places, and both had passed
  review.
- **Sweep the package and both receipts against the ceiling**, naming file and
  location for every excess: any mechanism statement; any asymptotic or scaling
  statement; any cost, density-penalty or baseline statement; any statement about
  `B > 193` or `field_bits > 16`; any quotation of the C-20 power sentence; any
  quotation of **17.5x without the full 17.5x–4128.6x range**; any statement that
  the ledger validates.
- **Rule on whether a favourable ladder is support.** If `alpha <= 3` holds at
  every named ladder cell for arm A-prime **and arm E-prime matches it**, say in
  terms whether that is support for H-STR-002 or a property of the closure
  convention. **This is the ruling the card exists for.**

## Output discipline

**Pre-state the transition label for the realised branch** and record that you
pre-stated it, with the check that neither `EV-STR-004` nor `DEC-20260729-004`
existed at the HEAD you reviewed. **Recommend exactly one label** from the
`docs/task-lifecycle.md` section 9 vocabulary.

Binding constraint: **`reject_scoped` on a single unreplicated empirical-only
run set is forbidden.** If you recommend anything stronger than `weaken`, name
**which archived artifact carries it** and whether that artifact is a
counterexample certificate or a derivation.

Name every required control you believe is missing, with its **cost** and its
**resume condition**, and say for each whether it should be dispatched. **Do not
name a control you would not run.**

**Record any dissent plainly and do not soften it.** A dissent from a
Coordinator ruling's *reasoning* rather than its conclusion is a legitimate and
useful output and was recorded verbatim in BATCH-013.

**Make no commit and stage nothing.** Your artifacts are committed by
TASK-20260729-048 and by nothing earlier. Change no status and create no
evidence, decision or knowledge record. Model independence is unavailable and is
not claimed; assert **session** independence. Name anything not reached inside
the cap.
