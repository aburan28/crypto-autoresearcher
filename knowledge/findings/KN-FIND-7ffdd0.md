---
id: KN-FIND-7ffdd0
type: internal_finding
title: "A mutation-testing (positive) control's own predicted-effect-size formula and its own detection threshold can be structurally, mathematically correlated -- two different functionals of the same small archived sample -- making near-certain detection uninformative about the instrument's genuine sensitivity, even when the injected defect, the prediction, and the causal mechanism are all honestly and correctly constructed"
tags: [instrument-design, positive-control, mutation-testing, null-object-control, order-statistics, small-sample, threshold-correlation, c3-lane, hkz, ml-kem, negative-result, toy-scale]
confidence: derivation_plus_two_independent_reviews_via_genuinely_different_methods_on_one_model
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-8d09f5, TASK-20260813-4aec9a, TASK-20260813-630414, TASK-20260813-01f482, TASK-20260813-0881f0]
internal_refs: [EV-MLKEM-552c58, DEC-20260813-9c7353, DEC-20260813-894568]
sibling_findings_narrowed: []
sibling_findings_note: >-
  This entry does not narrow KN-FIND-d29ece. That entry diagnoses why a two-route
  INDEPENDENCE COMPARISON can be confounded even when code-independence and
  fidelity-matching are both genuinely satisfied, and names a mutation-testing
  (positive) control as the decisive remedy. This entry diagnoses a SEPARATE,
  DIFFERENT-INSTRUMENT-TYPE confound discovered by actually building and
  reviewing that remedy for the first time in this campaign: the positive
  control itself can be uninformative for a structural reason unrelated to
  route independence at all. It stands beside KN-FIND-d29ece, not underneath
  it. `internal_refs` carries LEDGER records only, matching the shape prior
  entries in this goal use.
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-01f482/probes/probe5_structural_relationship_diagnostic.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-01f482/probes/probe5_structural_relationship_diagnostic_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/probes/rt_reverify.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/probes/rt_reverify_results.json
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-01f482/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/red_team_report.md
added: '2026-08-14'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. Measured on this
campaign's own frozen lattice/basis grid, no reduction above `d = 40`.

**THIS ENTRY DOES NOT SAY WHETHER THE `D_route` MECHANISM ACTUALLY HAS OR LACKS
SENSITIVITY TO A SUBTLE SHARED-CODE DEFECT.** That question -- the one
`KN-FIND-d29ece` named as open -- remains exactly as open as it was before the
batch this entry comes from. This entry is about why the specific check that was
built to answer it did not actually answer it, and how to recognize that failure
mode in advance next time.

The finding, in one sentence:

> A mutation-testing (positive) control's predicted-effect-size formula and its
> own pass/fail detection threshold can be **two different functionals of the
> same small reference sample** -- making "detection" of the injected defect
> **near-certain by construction**, independent of whether the injected defect
> has any real connection to the failure mode the control was built to catch.

## 1. Why this entry exists, and what it does not narrow

`KN-FIND-d29ece` established that a two-route independence comparison can be
confounded even when code-independence and fidelity-matching are both genuinely
satisfied, because the comparison's own fidelity-matching requirement forces
convergence to a canonical answer. It named the remedy explicitly: a
mutation-testing (positive) control, injecting a KNOWN defect and checking
whether the comparison mechanism actually flags it. `BATCH-8d09f5` built exactly
that remedy for the first time in this campaign -- and, on review, found the
remedy itself has an analogous but structurally distinct failure mode. This entry
does not narrow `KN-FIND-d29ece`; it is the next lesson in the same family,
discovered by actually constructing the tool that entry called for.

## 2. What was measured

`BATCH-8d09f5` injected a single, precisely-described defect (a seed-index
off-by-one) into a copy of licensed-shared basis-construction code, at two named
cells, and checked whether the existing comparison mechanism (unchanged formula)
flagged it. It did, at both cells, closely matching a prediction computed in
advance from already-archived data -- a clean, mechanically correct, bit-exact
reproducible positive result.

## 3. How the confound was diagnosed -- two methods, converging within a single batch

Both reviews, working independently and via **genuinely different, non-overlapping
methods**, found that this "detection" carried almost no information about the
instrument's genuine sensitivity:

- **An exhaustive closed-form enumeration.** One review computed what would have
  happened under all 7 possible index shifts (not only the one actually chosen)
  against the same already-archived data, with no new reduction. All 7 would have
  read "detected," at both cells, with margins in a narrow band (1.66x-2.79x of
  the threshold).
- **A large-scale Monte Carlo null-object control.** The other review simulated
  200,000 trials per distribution, across three distributions, of the identical
  comparison (a max-of-n order statistic against that same n-sample's own
  standard deviation) on generic random samples with **zero lattice, HKZ, or
  fpylll content at all**. The comparison read "detected" in at least 99.998% of
  trials, with a margin distribution matching the campaign's own six archived
  cells almost exactly (2.29x-2.79x).

**Neither method required resolving whether a genuine shared-code defect actually
exists.** Both diagnosed the confound from the mathematical structure of the
comparison itself: the threshold (`s_c^fib`, a sample standard deviation) and the
predicted effect size (a max cyclic-adjacent difference) are both functionals of
the **same small (n=8) archived array**. For generic small samples, a
range-like statistic reliably exceeds the sample's own standard deviation by a
roughly constant factor -- a well-known small-sample order-statistics
relationship, not a lattice-specific or fpylll-specific fact at all.

## 4. Why this generalizes beyond this goal, and beyond the prior five findings' family

The general shape: any positive/mutation-testing control that computes its own
"this defect should trigger detection" prediction from the **same small reference
sample** that also defines its **pass/fail threshold** risks this confound,
because the two functionals of a small sample are frequently correlated in ways
that make "detection" close to guaranteed regardless of the injected defect's
actual connection to the failure mode under test. This is a **different failure
mode** from every prior finding in this goal's family (`KN-FIND-9b5df0`:
code-provenance auditing; `KN-FIND-7de6b6`: fidelity-matching; `KN-FIND-d29ece`:
canonical-convergence under fidelity-matching) -- those are all about two
COMPARED THINGS being secretly related. This is about a control's own **SIGNAL
and its own PASS/FAIL CRITERION** being secretly related, which can defeat a
positive control even when it is otherwise perfectly, honestly constructed: the
injected defect precisely described, the prediction computed honestly in
advance (not fitted after the fact), the mechanical change verified exactly
correct by independent extractors, and the causal mechanism confirmed by
direct, from-scratch re-computation that rules out an artifact explanation.

1. **A "clean" positive result is not, by itself, evidence the control has real
   discriminating power.** It must additionally be checked that the specific
   defect tested could plausibly have failed to be detected -- i.e., that the
   test was not structurally guaranteed to succeed regardless of instrument
   quality.
2. **The diagnostic is cheap and general: build a null-object control on the
   comparison's own formula**, substituting generic random data with no
   connection to the domain, and check how often it reads "detected" by
   construction alone. If the answer is "almost always," the specific positive
   result carries little marginal information beyond that structural fact.
3. **A defect construction whose predicted effect is NOT a functional of the
   same reference sample that defines the threshold** (e.g. a continuously
   parameterized perturbation swept from zero, rather than a substitution among
   already-archived values) is the natural next design, since its predicted
   magnitude is not automatically tied to the threshold the way a same-sample
   substitution's is.

## 5. What this changes, and what it does not

**It changes nothing about the termination branch's firing** -- the branch fired
correctly and mechanically, per its own frozen rule, on the data as measured;
neither review disputed the branch call. **It changes what the branch's default
license text may be cited as saying.** The pre-registration's own default reading
(a positive detection demonstrates the mechanism has real power against
shared-code defects, "at this approximate magnitude") is shown to overstate the
analogy: the specific defect class tested was, by its own construction, unable to
land anywhere near the actual sensitivity boundary at any archived cell.

**It does not resolve whether the `D_route` mechanism has genuine sensitivity to
a subtle shared-code defect.** That question, the one `KN-FIND-d29ece` named,
remains exactly as open as before this batch ran. What WAS learned: the mechanism
is not fixed-by-construction to always report "no disagreement" -- it has now
been positively exercised against a known, injected defect for the first time in
this campaign, and correctly flagged it; and the underlying reduction library
converges reliably on freshly-drawn matrices at this scale. Neither of those is
the sensitivity-near-the-boundary question this entry is about.

## 6. What a successor must do, and what it must not

1. **Before trusting a positive-control result, check whether its predicted
   signal and its pass/fail threshold are functionals of the same small
   reference sample.** If they are, build the cheap null-object control in
   advance (or immediately upon review) rather than after the fact.
2. **Prefer a continuously-parameterized defect construction** whose predicted
   effect size is swept from a genuinely negligible value upward, to locate the
   actual detection/non-detection crossover, over a same-sample substitution
   whose magnitude is fixed by the reference data's own dispersion.
3. **This is not a claim that mutation-testing controls are useless.** The
   specific defect class this batch tested genuinely demonstrated the mechanism
   is not vacuously "always detects" or a fixed constant -- that is real,
   positive information, just not the near-the-boundary sensitivity information
   the control was originally commissioned to produce.

## 7. Scope and limits -- read before citing

1. **THE FINDING IS REPLICATED WITHIN A SINGLE BATCH, VIA TWO GENUINELY DIFFERENT
   METHODS SHARING NO COMPUTATIONAL PRIMITIVE.** One review used exhaustive
   closed-form enumeration against already-archived data; the other built a
   large-scale Monte Carlo simulation with zero domain content. Neither saw the
   other's write scope. Each is otherwise a single session and must be cited as
   such.
2. **INDEPENDENCE IS PROCEDURAL -- NEVER MODEL-LEVEL, AND HERE NOT ENVIRONMENTAL
   EITHER.** AGENTS.md rule 12 is **UNMET AND UNWAIVED**. Both reviews
   self-report the same model; one review's own session additionally disclosed
   an unreconciled model-resolution discrepancy between its self-report and the
   orchestration adapter's own resolution.
3. **IT DOES NOT SAY WHETHER A GENUINE SHARED-CODE DEFECT EXISTS ANYWHERE IN
   THIS CAMPAIGN'S ROUTE-P/ROUTE-I'' PIPELINE.** That question is explicitly and
   deliberately left open (sections 2, 5).
4. **NOTHING HERE IS AN IMPOSSIBILITY RESULT.** Section 6 names what a successor
   must do; a continuously-parameterized mutation-testing design is untested,
   not unavailable, in this campaign.
5. **DERIVATIONS AND CONSTRUCTIONS, NOT THEOREMS.** The underlying order-statistic
   relationship (a max-of-n statistic vs. that same n-sample's own standard
   deviation) is a well-established small-sample statistical fact, not a novel
   proof of this entry's own; the empirical corroboration (the exhaustive
   enumeration, the Monte Carlo simulation) is this campaign's own built
   evidence for it applying here.
6. **IT ESTABLISHES NOTHING ABOUT ANY LATTICE.** `BATCH-8d09f5` adjudicates no
   proposition about a lattice's admissibility, revalidates no prior batch,
   retires no prior amendment, and closes, pauses and completes nothing.

## Identifier provenance

`KN-FIND-7ffdd0` was drawn **without scanning state** (AGENTS.md rule 14) and
confirmed in **two scopes** by the dispatching session at the Coordinator's
request: worktree `tools/allocate_id.py --check` (well-formed by the KN-*
convention, 0 occurrences across 6,731 identifier-bearing paths) **and** a
cross-ref sweep of the 25 most-recently-updated remote branches (0 hits), plus
confirmation that it is not tracked under `knowledge/findings/` on `origin/main`.
Recorded as two-scope confirmed and **never** as `--check` alone. The Coordinator
that specified this entry's content held no shell and claimed neither check as
its own; both were performed by the dispatching harness session.

## Superseding relationship

This entry does not narrow any prior finding in this goal. **No prior entry is
edited and no `superseded_by` is set** on any of them. It stands beside
`KN-FIND-d29ece` as the next entry in the same instrument-design family --
comparison confounds, then positive-control confounds -- cross-referenced from
`DEC-20260813-9c7353`'s `knowledge_promotion` field.
