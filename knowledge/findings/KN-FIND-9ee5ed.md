---
id: KN-FIND-9ee5ed
type: internal_finding
title: "The estimator pairing rule: an intercept is only meaningful paired with the slope of the same fit of the same series over the same window"
tags: [estimator-lemma, pairing-rule, intercept, slope, extrapolation, null-object-control, cost-model, calibration, wesolowski, supersingular-isogeny, p13, derivation, methodology]
confidence: derivation
evidence_level: derivation_plus_committed_counterexample
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-P13-001/batches/BATCH-003/reviews/TASK-20260802-8e00fe/red_team_report.yaml
  - coordination/goals/GOAL-P13-001/batches/BATCH-003/reviews/TASK-20260802-c50ea2/validation_report.yaml
  - experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/raw-result.json
  - experiments/EXP-PEC-49c773/specification.yaml
  - experiments/EXP-PEC-6be870/implementation/per_entry_cost.py
proof_refs_note: >-
  These are the same proof_refs as EV-PEC-857664, exactly as
  DEC-20260802-48c72c's schedule fixed them.
internal_refs:
  - H-WESO-001
  - EV-PEC-857664
  - EXP-PEC-49c773
  - DEC-20260802-48c72c
  - DEC-20260809-a2f829
  - EV-WESO-556063
  - TASK-20260809-4119f6
source_goal: GOAL-P13-001
source_batch: BATCH-003
source_evidence: EV-PEC-857664
source_decision: DEC-20260802-48c72c
promoted_by_decision: DEC-20260809-a2f829
promoted_by_task: TASK-20260809-4119f6
added: '2026-08-09'
superseded_by: null
---

## Why this entry exists, and why its content was fixed before it was written

This is the entry that `DEC-20260802-48c72c.knowledge_promotion` **scheduled as
a binding deliverable** on 2026-08-02, with its durable claim, its two
instances, its `proof_status` and its `proof_refs` all fixed **in advance**
precisely so the content could not drift between the decision that ordered it
and the archive that shipped it. It was deferred twice for a task-card scoping
omission (`knowledge/findings/` outside the archive task's declared
`write_scope`), and then a third time when the archive that should have shipped
it shipped two entries of unrelated content into the same slot instead
(`KN-FIND-4e7a92`, `KN-FIND-d1c853`; see `KN-FIND-e87720`).

**Nothing here is new mathematics.** This entry reproduces the scheduled content
faithfully and adds no result, no formula and no number that was not already in
`DEC-20260802-48c72c` and `EV-PEC-857664`.

## The durable claim

> An intercept is only meaningful **paired with the slope of the same fit of
> the same series over the same window**; a slope-only calibration law reports
> **ZERO overhead** for an object carrying a large constant one.

That is the whole promotable object: **an estimator lemma and the pairing rule
it implies.** It is a discipline for reading a log-log fit, and it is reusable
anywhere a cost is extrapolated from a fitted exponent.

Stated operationally. If a cost model fits `log2(cost) = log2(A) + gamma *
log2(x)` over some window of a series, then any extrapolated level must be
computed from **that same pair** `(log2 A, gamma)`. Substituting a slope from
one fit into an intercept from another fit, from another series, or from another
window is not a conservative approximation and not a rounding — it is a
different estimator with no error bound relating it to either parent.
Discarding the intercept altogether (equivalently, asserting `A = 1` because the
model's derivation assumed a unit constant) is the degenerate case of the same
error, and it is the one that fails silently: the estimator returns "no
overhead" for an object whose overhead is large and measured.

## What is promoted, and what is expressly NOT

**PROMOTED: the estimator lemma and the pairing rule. NOT ANY `c` VALUE.**

This exclusion is the schedule's own and is repeated here because it is the
point of the entry. The corrected overhead parameter `c` that this programme
computed is an *extrapolation* to an abscissa 6.48 octaves (NIST-I) to about 18
octaves (`log2 p = 768`) beyond the top of the fitted window. It carries **no
claim tier** and travels under **eight mandatory attachments**
(`DEC-20260802-48c72c.citability_ruling`, MA-1..MA-8) and twelve standing
prohibitions (SP-1..SP-12, four of them permanent). Putting such a figure into
the corpus would put a caveated number where it will be quoted without its
caveats. Any reader wanting a `c` must go to `DEC-20260802-48c72c` and take the
bracket with its attachments, never from here.

## Instance (i): the C-NULL counterexample — the rule has a witness

The strongest evidence for a discipline is an object whose answer is known
independently, on which the undisciplined estimator gives the wrong answer.

`RUN-PEC-49c773-a` carries such an object: **C-NULL**, whose per-entry cost is
`O(1)` in `ell` **by construction**, and which was *measured* at
`2^12.26`–`2^12.32` counted `F_{p^2}` multiplications per entry
(`REF_null = 12.2595` bits above the Section 4.1 convention of one operation
per entry).

- The **slope-only law** — which maps the fit's slope and discards its
  intercept — returns approximately **zero overhead** for this object, and
  misses its measured level by **12.176314 to 12.605090 bits**, failing at
  **every one of the ten evaluation points** (two null windows x five field
  sizes).
- The **paired law** recovers the same object's level with a worst miss of
  **0.271670 bits** against a pre-registered 0.75-bit tolerance, at
  (W-MID, `log2 p = 768`).

That is a factor of roughly seventeen above tolerance for the unpaired
estimator against a passing paired one, on an object whose correct answer was
fixed by construction rather than by the fit. Both independent reviewers of
BATCH-003 recomputed the gate from the committed superseded null with their own
implementations and agreed to every reported digit.

## Instance (ii): the A-3 absorption — the rule earns its keep

Anomaly **A-3** of `RUN-PEC-49c773-a` is a genuine cross-window discrepancy in
the fitted exponent (`gamma_B = 0.810034` on the primary window W-MID against
`0.958496` on the top window W-TOP). Under the pairing rule the discrepancy
largely cancels, because **W-TOP's higher slope comes with a lower intercept**
(`8.6296` against W-MID's `9.7308`) and the two move together:

| reading | pairing | modelled NIST-I margin at `w = 2^30` |
|---|---|---|
| S-B, W-MID, `alpha = 1` | correct | `10.3578` bits |
| S-B, W-TOP, `alpha = 1` | correct | `9.3508` bits |
| W-TOP slope `0.9585` with the **W-MID** intercept | **forbidden by the rule** | `7.98` bits, overhead `26.29` bits |

So A-3 correctly paired is worth **1.007 bits** of margin — inside the
published bracket, and an implementation artifact rather than an exponent
revision. **Deleting the pairing rule makes the identical anomaly cost 2.4 bits
and fall outside the bracket.** The rule was stated *before* the data, it
survives deletion testing, and it closes an entire defect family of which the
discarded-intercept defect was one instance.

## Status of this claim

`proof_status: derivation`. This is a **checkable written argument plus a
committed counterexample**, not a machine-verified proof. The argument is
elementary — two parameters of one fit are estimated jointly and their
extrapolated combination is what the model uses, so the pair is the estimable
object and either component alone is not — and the counterexample is a measured
object in a committed artifact whose correct answer was fixed by construction
before it was measured.

## Limits — read before citing

1. **This is a statement about estimators, not about isogeny attacks.** It
   bears on how a fitted cost curve may be extrapolated. It says nothing about
   the Wesolowski attack's asymptotic exponent, nothing about Heuristic 1, and
   nothing about any concrete security margin.
2. **The counterexample's numbers are scoped.** They come from one run
   (`RUN-PEC-49c773-a`) at one prime `p = 1099511627563` (an 80-bit `F_{p^2}`)
   over 47 prime degrees `2 <= ell <= 211`, in pure Python, for one
   implementation pair sharing every line but `poly_mul`. Evidence strength
   `preliminary`. AGENTS.md rule 7 applies: nothing here is a
   cryptographic-scale measurement.
3. **The passing gate is not a validation of the corrected law.** Its tolerance
   derivation contains no variance term, so the pass sits at about 1.4 noise
   half-widths rather than on a 0.478-bit cushion, and it has no power against
   assumptions L1, L2, L5 or against the pairing rule itself. `SP-12` of
   `DEC-20260802-48c72c` forbids restating it otherwise. What the gate *does*
   discriminate is the defect it was built for, by 12.605090 bits against 0.75.
4. **The rule does not repair a quantifier-order defect.** `EV-PEC-857664`
   records that C-PSCALE's `alpha` was estimated on an `ell` range disjoint
   from the window the exponent is applied to; the pairing rule does not forbid
   that and a successor contract should.
5. **Do not confuse this "pairing rule" with the one named in
   `KN-FIND-d1c853`.** That entry uses the same words for an entirely different
   object (walk length against smooth-norm pair count under Heuristic 1). The
   two share a phrase and nothing else. See `KN-FIND-e87720`.

## Provenance

Scheduled by `DEC-20260802-48c72c.knowledge_promotion.scheduled_promotion_for_the_batch_004_ledger_archive.primary_entry`
(content, instances, `proof_status` and `proof_refs` all fixed there in
advance). Deferred twice for a task-card scoping omission and once by
non-delivery. Promoted by `DEC-20260809-a2f829` under
`TASK-20260809-4119f6`, which discharges that binding obligation. The
underlying evidence record is `EV-PEC-857664` (BATCH-003, `EXP-PEC-49c773` /
`RUN-PEC-49c773-a`, reviewed by `VAL-20260802-5a24d2` and
`RT-20260802-8e00fe`).
