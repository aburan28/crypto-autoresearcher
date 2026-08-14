---
id: KN-FIND-7de6b6
type: internal_finding
title: "A two-route independence test can be confounded by mismatched computational fidelity even when code-sharing is genuinely absent, and the confound is diagnosable by its statistical signature without resolving the underlying computation exactly"
tags: [independence, reduction-quality, computational-fidelity, confound, instrument-design, cross-validation, c3-lane, statistical-signature, ml-kem, negative-result, toy-scale]
confidence: derivation_plus_two_independent_reviews_via_different_methods_on_one_model
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-6e08fe, TASK-20260813-cdcd88, TASK-20260813-ea2e96, TASK-20260813-71d65d, TASK-20260813-7930a6]
internal_refs: [EV-MLKEM-5aa471, DEC-20260813-1aae44, DEC-20260813-28d7b2]
sibling_findings_narrowed: []
sibling_findings_note: "This entry does not narrow KN-FIND-9b5df0. That entry is about auditing code PROVENANCE before naming a route independent, discovered BEFORE any independence test runs. This entry is about a SEPARATE failure mode that persists EVEN AFTER code-sharing has been ruled out. `internal_refs` carries LEDGER records only, matching the shape prior entries in this goal use."
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-71d65d/probes/probe_pattern_correlation.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-71d65d/probes/probe_pattern_correlation_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-71d65d/probes/probe_reduction_quality.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/probes/probe_second_lll_hkz_control.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/probes/probe_second_lll_hkz_control_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-71d65d/validation_report.yaml
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-71d65d/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/red_team_report.md
added: '2026-08-13'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. Measured on this
campaign's own frozen lattice/basis grid, no reduction above `d = 40`.

**THIS ENTRY DOES NOT SAY WHETHER `hkz`'s ORIGINAL `EXCEEDS` VERDICTS ARE TRUE UNDER
GENUINE, QUALITY-MATCHED INDEPENDENCE.** That question is explicitly left open by the
batch this entry comes from — neither newly confirmed nor newly flagged unsupported.
This entry is about how to **diagnose the confound**, not about resolving the
question it confounds.

The finding, in one sentence:

> A two-route independence test can be confounded by **mismatched computational
> fidelity** (reduction quality, precision, iteration depth) even when code-sharing
> is genuinely absent — and this confound is **distinguishable from code-sharing**
> by its own statistical signature, without needing to resolve the underlying
> computation exactly.

## 1. Why this entry exists, and what it does not narrow

`KN-FIND-9b5df0` addressed a pre-registration failure discovered **before** any
independence test runs: a route named "independent" without auditing its code
provenance can turn out to share a kernel with the route it is meant to check.
`BATCH-6e08fe` was commissioned specifically to build the genuine second route that
should have existed, doing exactly what `KN-FIND-9b5df0` recommends — and it still
hit a problem, of a **different kind**, that persists even after code-sharing is
genuinely ruled out: the new route was correctly non-code-shared, but used
LLL-quality reduction where the original used HKZ-quality reduction. This entry does
not narrow `KN-FIND-9b5df0` — it names the **next** failure mode in the same family,
one that surfaces only once the first is fixed.

## 2. What was measured

`BATCH-6e08fe` built a genuinely non-code-shared re-implementation of the second
route for two observables, `lam1n` and `hkz`, and compared each to the same frozen
baseline. The two split cleanly:

- **`lam1n`**: agreement to floating-point precision (`~1e-15`–`1e-14`) — `lam1n` is
  an exact, algorithm-independent invariant (the minimum of a discrete lattice), so
  any correct computation of it agrees with any other correct computation, regardless
  of the reduction method used to get there.
- **`hkz`**: disagreement at `0.015`–`0.223` — but the new route's reduction was
  LLL-quality (`delta = 0.99`), not HKZ-quality, because the intended library was
  unavailable in the run environment.

The disagreement alone cannot distinguish "the original measurement was a
code-sharing artifact" from "this new route is simply a lower-fidelity computation
of the same quantity." Both would produce nonzero disagreement.

## 3. How the confound was diagnosed — two methods, converging

Both reviews, working independently and via **genuinely different methods**,
concluded the disagreement is better explained by the reduction-quality mismatch
than by code-sharing:

- **Pattern-correlation analysis, with zero new computation.** One review examined
  only the already-committed numbers: the sign of the disagreement was consistent
  across the large majority of basis comparisons (41 of 48, one-directional), it grew
  geometrically with lattice dimension at matched `(beta, d)`, and it shrank as the
  averaging window widened. This signature was then contrasted against **this same
  goal's own precedent for what genuine code-sharing looks like** — an earlier batch
  measured `D_route = 0.0` **exactly**, with no scaling structure of any kind, because
  code-sharing reproduces the identical computation bit-for-bit. A reduction-quality
  gap does not behave that way; it behaves like a real, monotone, dimension-scaling
  quantity — which is what was observed.
- **A built control, independently.** The other review constructed a **second**,
  independently-structured LLL implementation and ran it against the same baseline on
  all 24 bases. It reproduced essentially the same `0.015`–`0.223` disagreement at
  every covered cell, and matched the first route's LLL output to machine epsilon —
  direct evidence that the disagreement tracks the reduction method, not the specific
  implementation.

**Neither method required resolving `hkz` exactly** (which would need the
HKZ-quality route that was unavailable). Both diagnosed the confound from properties
of the disagreement itself.

## 4. Why this generalizes beyond this goal

The general shape: any two-route agreement test implicitly assumes both routes
compute the target quantity to comparable fidelity. When one route's fidelity is
lower (courser reduction, lower precision, fewer iterations, an early-terminated
search), the resulting disagreement is **structurally different** from a
code-sharing artifact and can be told apart by:

1. **Sign structure.** A code-sharing artifact reproduces the identical value
   exactly; a fidelity gap produces a disagreement with a consistent sign, tracking
   which route is more conservative.
2. **Scaling with the parameter that should amplify a genuine quality gap** (here,
   lattice dimension). A code-sharing artifact does not scale — it is exactly zero
   regardless of dimension. A fidelity gap grows with the parameter that makes the
   lower-fidelity method's shortfall larger.
3. **Shrinkage under averaging.** A fidelity gap that is itself a biased estimate of
   a quantity with some intrinsic variability shrinks as the averaging window widens;
   a genuine artifact does not, because there is nothing to average away.

A built cross-check (a second implementation at the SAME lower fidelity, as this
batch's red team did) directly confirms the diagnosis; the pattern analysis alone is
a cheap first pass that can flag the confound before spending the compute to build
one.

## 5. What this changes, and what it does not

**It changes nothing about `T-INDVERIFY-ARTIFACT-PARTIAL`'s firing** — that branch
fired correctly and mechanically, per its own frozen rule, on the disagreement as
measured. **It changes what the branch's default attribution may be cited as
saying.** The pre-registration's own default reading (any disagreement means
code-sharing) is shown to be too narrow: a genuinely independent, non-code-shared
route can still produce a false positive under this reading if its fidelity does not
match the route it is checking.

**It does not resolve `hkz`'s open question.** Whether `hkz`'s original `EXCEEDS`
verdicts would survive a **quality-matched** independent route remains unanswered.

## 6. What a successor must do, and what it must not

1. **State fidelity-matching as an explicit precondition of a two-route independence
   test, alongside code-provenance auditing.** `KN-FIND-9b5df0` says: audit code
   provenance before naming a route independent. This entry adds: also declare, in
   advance, what "comparable fidelity" means for the specific quantity being
   compared, and verify both routes meet it — or explicitly flag the comparison as
   fidelity-mismatched before running it, not after finding a disagreement.
2. **When fidelity cannot be matched (a required library is unavailable), the cheap
   diagnostic in §3 is available as a fallback**, not as a substitute for eventually
   running the matched comparison. It tells you *whether* to trust a disagreement as
   evidence of code-sharing; it does not tell you the answer to the original
   question.
3. **This is not a claim that lower-fidelity comparisons are useless.** For an exact,
   algorithm-independent invariant (like `lam1n`), fidelity does not matter and the
   comparison is fully informative regardless. The failure mode is specific to
   statistics whose value depends on the quality of an intermediate computation
   (like `hkz`, which depends on how close to optimal the reduction actually is).

## 7. Scope and limits — read before citing

1. **THE FINDING IS REACHED BY TWO INDEPENDENT REVIEWS VIA DIFFERENT METHODS.** One
   found it via pattern analysis of already-committed numbers; the other via a built
   control. Neither saw the other's write scope. Each is otherwise a single session
   and must be cited as such.
2. **INDEPENDENCE IS PROCEDURAL — NEVER MODEL-LEVEL, AND HERE NOT ENVIRONMENTAL
   EITHER.** AGENTS.md rule 12 is **UNMET AND UNWAIVED**. Both reviews ran on the
   SAME model and the SAME host as the producer.
3. **IT DOES NOT SAY WHETHER `hkz`'s DISPUTED VERDICTS ARE TRUE.** That question is
   explicitly and deliberately left open (§2, §5).
4. **NOTHING HERE IS AN IMPOSSIBILITY RESULT.** §6 names what a successor must do;
   it is untested, not unavailable.
5. **DERIVATIONS AND CONSTRUCTIONS, NOT THEOREMS.** The three-signature diagnostic in
   §3 is a heuristic pattern observed in this campaign's own data, cross-validated
   by a built control — not a proven general test.
6. **IT ESTABLISHES NOTHING ABOUT ANY LATTICE.** `BATCH-6e08fe` adjudicates no
   proposition about a lattice, revalidates no prior batch, retires no prior
   amendment, and closes, pauses and completes nothing.

## Identifier provenance

`KN-FIND-7de6b6` was drawn **without scanning state** (AGENTS.md rule 14) and then
confirmed in **two scopes** by the dispatching session at the Coordinator's request:
worktree `tools/allocate_id.py --check` (well-formed, 0 occurrences across 6,638
identifier-bearing paths) **and** a cross-ref sweep of the 25 most-recently-updated
remote branches (0 hits), plus confirmation that it is not tracked under
`knowledge/findings/` on `origin/main`. Recorded as two-scope confirmed and **never**
as `--check` alone. The Coordinator that specified this entry's content held no
shell and claimed neither check as its own; both were performed by the dispatching
harness session.

## Superseding relationship

This entry does not narrow any prior finding in this goal. **No prior entry is
edited and no `superseded_by` is set** on any of them. It stands beside
`KN-FIND-9b5df0` as a companion instrument-design lesson in the same family —
provenance before independence, fidelity-matching after — cross-referenced from
`DEC-20260813-1aae44`'s `knowledge_promotion` field.
