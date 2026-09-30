---
id: KN-TECH-01617b
type: technique
title: When a satisfiability sweep finds the admitting half of a differential development check itself unsatisfiable on a zero-run stage, pre-declare the fallback (delete the admitting half, name the residual, defer that admission to the first real gate) before the review runs, and separately declare cancellation-with-successor for a review chain that outlives its own producer
tags: [protocol-amendment, development-check, satisfiability, pre-declared-alternative, residual-limitation, known-answer-control, review-chain-regeneration, governance, methodology]
confidence: reported
complexity: >-
  not a cost model - a pre-approval audit and drafting pattern. The operative
  quantities are (1) per development predicate, whether a layer implementing
  every rule as worded can meet it in its own development world, given a
  zero-run stage's structural inability to ever hold a real production
  package at a fixed id; and (2) whether an already-declared successor
  obligation (a blocked review-chain placeholder) is re-pointable without
  losing what it was carrying
applicability: >-
  a protocol amendment that repairs a development check found unsatisfiable
  by construction (KN-TECH-c9dcd5), where the repair itself proposes both a
  refusal half and an admitting half, and the admitting half can only be
  exercised on "coherent" development copies rather than a real production
  package; and, orthogonally, any approval act that must decide seven or more
  blocked placeholder tasks whose sole content is "the act that performs this
  re-points them" successor obligation
source_refs: [DEC-20260925-fc8dbb, AMD-EXP-GFPN-05ff43-20260925-admitdev, TASK-20260925-5842cf, TASK-20260925-82235d, DEC-20260925-8b2bf7, CORR-20260925-ee6929, KN-TECH-c9dcd5, KN-TECH-d45927, DEC-20260924-daf670, EXP-GFPN-05ff43]
proof_status: derivation
proof_refs:
  - ledger/decisions/DEC-20260925-fc8dbb.yaml
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260925-5842cf/review-report.yaml
  - experiments/EXP-GFPN-05ff43/amendments/v2_addendum_admitdev.yaml
added: '2026-09-25'
superseded_by: null
---

## What this note is, and is not

A note about **protocol method**, amending `KN-TECH-c9dcd5` (itself amending
`KN-TECH-d45927`) by a new entry. Neither earlier entry is edited or
superseded. `KN-TECH-c9dcd5` section 3 explicitly flagged that it would need
amending again "if the review finds ... the admitting branch unsatisfiable on
coherent copies" -- this is that amendment.

It is drawn from the same lineage (`EXP-GFPN-05ff43`, `GOAL-GFPN-380702`): the
draft `AMD-EXP-GFPN-05ff43-20260925-admitdev`, its zero-run review
`TASK-20260925-5842cf`, and the approving decision `DEC-20260925-fc8dbb`. It
is **not** a finding about any GFPN object, about D, about `H-GFPN-9a29be` or
`HEUR-GFPN-DFLAT`, and nothing in it is a mathematical result.

## 1. What happened

`KN-TECH-c9dcd5` rule (c) called for stating a development admission check
differentially and exercising the admitting branch "on a world where every
admission predicate can hold." The admitdev draft did exactly that: it wrote
AD-1 (d1), a refusal branch on two copies of a real development package (which
the review confirmed satisfiable and discriminating), and AD-1 (d2), an
admitting branch on "coherent" development copies -- copies whose manifest
fields are recomputed by the delivered wrapper's own functions so that, in
principle, every admission predicate is genuinely met.

The review's satisfiability sweep found (d2)(i) **itself unsatisfiable**, for
a reason one level deeper than (c)'s "coherent copies" fix reaches: the
admission predicate does not just require the checker to exit 0 on a
regression comparison; the regression comparison (`reg1()`) looks up a
**real production package at a fixed id named by the plan**, and a zero-run
development stage (`maximum_runs 0`, binding) can never write one. No amount
of recomputing a development copy's own manifest fields produces a
production package at that id. So even the "coherent copy" method has a
structural floor: it can make every FIELD a check reads cohere, but it cannot
manufacture a PREDECESSOR PACKAGE the check's formula requires to exist on
disk under a fixed production id.

The draft had **pre-declared** this exact contingency before any review ran:
"if the review finds (d2) unsatisfiable ... the approving act may approve
with (d2) DELETED, on condition that its decision and the r5 stage card
declare residual RDL-1: '[the admitting branch] is first exercised at the r5
gate; a wrongful refusal there is fail-closed, an impediment for a
Coordinator decision, never evidence.' (d1) is never deleted." The approving
act applied exactly that alternative, on the review's finding, without a
fourth draft-review-approval cycle.

Separately, the same approving act had to dispose of seven review-chain
placeholder tasks that had never run (the r4 stage never reached a review
round) and whose only content was "the act that performs this re-points them
to the surviving lineage." The pattern already used once in this campaign
(`DEC-20260924-daf670`, cancelling an earlier seven under
`review_chain_handling`) was: cancel the current seven in the SAME revision
that declares their successors under fresh pool ids, carrying forward every
surviving obligation in text, and retiring the ids the cancelled entries
owned (unused, never reused).

## 2. Rules

**(a) Pre-declare the fallback for a differential check's admitting half
before any review runs it.** If a development admission check's admitting
branch can only be exercised on a constructed ("coherent") copy rather than a
real production package, name, in the SAME draft, before any review: (i) the
exact condition under which the admitting branch would be found
unsatisfiable; (ii) what is deleted if that condition holds (the admitting
branch only -- never the refusal branch, which is the one exercise of the
production refusal rule on real development bytes); and (iii) the exact
residual-limitation sentence the approving decision and the next stage's card
must carry verbatim, naming WHERE the admitting branch is first genuinely
exercised (the next real gate) and WHAT governs a wrongful refusal there
(fail-closed, an impediment, never evidence). This turns what would otherwise
be a fourth amendment cycle into a same-act disposition, without smuggling in
an unreviewed reading: the review still finds the break; the alternative was
fixed before anyone knew it would be needed, and only ADR-1's finding
triggers it.

**(b) Look one level below "coherent copies" for a fixed-id predecessor.**
When auditing whether a "coherent copy" method (recomputing a manifest's own
fields with the delivered wrapper's functions) makes an admission predicate
satisfiable, check separately whether any term of that predicate resolves a
path or comparison against a FIXED id that only a real, differently-scoped
production process can ever populate (here: `reg1()`'s lookup of the plan's
designated production G1 id under `runs/`). Recomputing a copy's OWN fields
cannot satisfy a predicate that reads a DIFFERENT object's fixed-id
existence; that gap is invisible to a check that only asks "are this copy's
own fields coherent."

**(c) Cancel a review chain and declare its successors in the same
revision, under fresh pool ids, never the old ones.** When a set of blocked
review-chain placeholders can never run because their sole dependency
terminally failed or was cancelled, and a later act needs a new set pointed
at the surviving lineage: cancel the old set and declare the new set in ONE
queue revision (not two acts, which would leave a window where the chain is
neither cancelled nor replaced); give the successors FRESH pool ids (never
reusing the cancelled ids, which research_dispatch.py keeps validating as
long as the cancelled entries remain in `tasks`); retire, unused, every
DEC/EV id the cancelled placeholders owned; and mint fresh DEC/EV ids for the
successors' own eventual review-plan and evidence-review acts, carrying every
surviving obligation forward in text (never by re-using an id, which would
give one id two meanings).

## 3. What remains untested

- **The remedy's actual exercise.** RDL-1 is a declared residual, not a
  result: whether the r5 gate's real admission run ever needs it (a wrongful
  refusal there) is unknown until R2-r5 runs.
- **Generality of (b).** One instance (`reg1()`'s fixed production G1 lookup);
  whether other "coherent copy" admission checks in other campaigns hide a
  similar fixed-id floor is untested.
- **Generality of (c).** Two instances in one campaign (the seven placeholders
  cancelled twice, both times re-pointed to a surviving lineage of the same
  experiment); untested across campaigns.

## 4. Confidence and limits of the evidence

`reported`, not `established`.

- **The (d2) unsatisfiability finding is the review's derivation**
  (`TASK-20260925-5842cf` AJ-1, independently re-derived against the raw
  bundle record, not merely cited from the draft's own text); this note
  restates it as a general pattern, not as a re-verification.
- **The pre-declared-alternative and review-chain-regeneration PATTERNS are
  the design of two drafts/decisions**, not a validated technique across
  campaigns.
- **Nothing here is evidence about any mathematical object.**
