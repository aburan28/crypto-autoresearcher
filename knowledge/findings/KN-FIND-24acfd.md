---
id: KN-FIND-24acfd
type: finding
title: Two independent review sessions were lost because the batch design archives reviews only after both complete
tags: [process, harness, archival, durability, dispatch, review, infrastructure]
confidence: observed_directly
scope: process
source_refs: [GOAL-MLKEM-004, BATCH-d2a728, TASK-20260803-535d15, TASK-20260803-bc2f41, TASK-20260803-586a7f, KN-TECH-797223]
added: 2026-08-13
superseded_by: null
---

## What happened

`BATCH-d2a728` dispatched two independent reviews of its batch-1 measurement:
`TASK-20260803-535d15` (validator) and `TASK-20260803-bc2f41` (red team). Both ran.
The validator completed a thorough validation — 38 checks, a terminal verdict of
`ADMISSIBLE_WITH_DEFECTS`, seven numbered defects including two of high severity — and
wrote `report.yaml` plus nine recomputation scripts and their outputs into its write
scope. The red team ran six analysis scripts and captured their outputs.

**None of it survived.** The red-team session then hit a hard model usage limit before
writing its report, and in the interval before any Coordinator archive ran, the
container was recreated. Every uncommitted path was destroyed: both task directories,
the validator's completed report, every script, the rebuilt `/tmp/sagevenv`, and a
pinned `lattice-estimator` clone.

What survived is exactly what had been committed: the producer's snapshot at
`8cc51677`, and an infrastructure commit the Coordinator had made opportunistically
(`KN-TECH-797223`). Nothing else.

## The mechanism, which is a design property and not an accident

`AGENTS.md` already says research is not durable merely because it appears in a working
tree, and the dispatch contract already requires a Coordinator snapshot archive after a
producer reaches a terminal result. The gap is narrower and easy to miss:

**The batch assigned both reviews to a single terminal ledger archive**
(`TASK-20260803-586a7f`, `depends_on: [535d15, bc2f41]`). There was no archival task
between "a reviewer finished" and "both reviewers finished". So a completed review sat
uncommitted for as long as its sibling kept running, and the exposure window was the
runtime of the *slower* reviewer — precisely the one most likely to stall or die.

This is the reason the loss is asymmetric and unlucky-looking but is not luck: the
review that finished first was the one destroyed, and it was destroyed while waiting on
the review that never finished at all.

## What this does and does not say

- It says nothing about ML-KEM, the dual attack, `MATZOV.Nf`, or the batch-1
  measurement. No evidence record is created or changed; `EV-*` and `KN-*` statuses are
  untouched. AGENTS.md rule 12 remains UNMET and UNWAIVED.
- The lost validation is **not** recoverable as a record. Its verdict and defects were
  reported to the Coordinator in-session, but an unarchived in-session report is
  hearsay, not evidence, and must not be entered into the ledger as though it had been
  produced and archived. It is being re-derived from scratch instead.
- It cost roughly an hour of review compute twice over, and it is the second
  ephemerality loss in this campaign — the first being the `/tmp/sagevenv` instrument
  the goal record already warns about (`KN-TECH-14efa5`, `KN-TECH-797223`).

## The one mitigating fact

The validator's findings are re-derivable. Its analysis ran against
`raw_scores.json`, which is committed and intact, so a fresh validator can reach the
same checks from surviving artifacts. **This is a property of the batch, not a general
rescue**: a review whose evidence is a measurement the reviewer performed itself — a
re-run sieve, a timing, a resource record — would have been unrecoverable, because the
environment that produced it is gone.

## What to change

1. **Give every producing and reviewing task its own snapshot archive**, or at minimum
   an archive that fires when the *first* of a review pair completes. A terminal ledger
   archive gated on all reviewers is correct for the ledger transition and wrong as the
   only commit point.
2. **Instruct reviewers to write deliverables early and incrementally** rather than
   composing at the end. Both lost sessions held their results in context until the
   final step. A partial report on disk outranks a complete one in memory.
3. **Treat a long-running review as an exposure window** and commit opportunistically
   while it runs. The Coordinator did this for infrastructure and that commit is the
   only reason the instrument recipe survived; it did not do it for the reviews.
4. When a session dies on a usage limit, that is an infrastructure failure under
   AGENTS.md rule 5. It is never evidence about the mathematics, and the correct
   response is re-dispatch with recorded `fallback_used`, not a weakened conclusion.
