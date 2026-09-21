---
id: KN-FIND-d29ece
type: internal_finding
title: "A two-route independence test whose own fidelity-matching requirement forces convergence to a canonical, essentially-unique invariant of the object under test demonstrates the absence of wrapper-level defects but has near-zero power against a defect shared by the code the two routes are licensed, or required, to share"
tags: [independence, fidelity-matching, exhaustive-enumeration, canonical-invariant, confound, instrument-design, cross-validation, c3-lane, hkz, ml-kem, negative-result, toy-scale]
confidence: derivation_plus_two_independent_reviews_via_different_methods_on_one_model
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-a6fab5, TASK-20260813-94e686, TASK-20260813-c0ec71, TASK-20260813-968dc8, TASK-20260813-5b09b0]
internal_refs: [EV-MLKEM-f65f00, DEC-20260813-894568, DEC-20260813-1aae44]
sibling_findings_narrowed: []
sibling_findings_note: >-
  This entry does not narrow KN-FIND-7de6b6. That entry is about DETECTING a fidelity
  MISMATCH (a lower-fidelity route disagreeing because it under-reduces), diagnosable by a
  statistical signature (sign consistency, dimension scaling, averaging-window shrinkage).
  This entry is about a SEPARATE failure mode that arises only once fidelity IS matched
  correctly -- the fix for KN-FIND-7de6b6's confound. It stands beside it as the natural
  next entry in the same family, anticipated by KN-FIND-7de6b6's own section 6 item 1
  ("declare, in advance, what comparable fidelity means") but not fully covered by it: even
  a correctly fidelity-matched test can still be confounded, by a DIFFERENT mechanism, once
  fidelity-matching itself forces near-canonical convergence. `internal_refs` carries LEDGER
  records only, matching the shape prior entries in this goal use.
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-968dc8/probes/probe1_reproduce_l7b5.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-968dc8/probes/probe2_all_cells_bit_identity.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-968dc8/probes/probe2_all_cells_bit_identity.out
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe3_samecode_rerun_null_control.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe3_samecode_rerun_null_control_output.txt
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe4_third_independent_implementation.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe4_third_independent_implementation_output_i1.txt
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-968dc8/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/red_team_report.md
added: '2026-08-13'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. Measured on this
campaign's own frozen lattice/basis grid, no reduction above `d = 40`.

**THIS ENTRY DOES NOT SAY WHETHER A DEFECT SHARED AT THE fpylll-ENUMERATION-KERNEL LEVEL,
OR IN THE ROUTES' COMMON DEFINITIONAL/BASIS-CONSTRUCTION CODE, ACTUALLY EXISTS.** That
question is explicitly left open by the batch this entry comes from. This entry is about
how to **diagnose a limitation of the test itself**, not about resolving what that test
cannot see.

The finding, in one sentence:

> A two-route independence test whose OWN fidelity-matching requirement forces both
> routes to converge on a canonical, essentially-unique invariant of the object under
> test demonstrates real power against implementation-quality (wrapper-level) defects,
> but has **near-zero power** against a defect in code the two routes are licensed, or
> required, to share — **even when code-level independence and fidelity-matching are
> both genuinely, verifiably satisfied.**

## 1. Why this entry exists, and what it does not narrow

`KN-FIND-7de6b6` addressed a confound discovered when fidelity is **mismatched**: a
genuinely non-code-shared route built at lower reduction quality than the route it checks
can produce a disagreement that looks like independent disconfirmation but is really a
quality gap. The batch this entry comes from (`BATCH-a6fab5`) was commissioned specifically
to fix that — build a route that is BOTH non-code-shared AND fidelity-matched — doing
exactly what `KN-FIND-7de6b6` recommends. It still hit a problem, of a **different kind**,
that only appears once the first confound is fixed: the fidelity-matching requirement
itself (build a route replicating the target's exhaustive-enumeration structure "as
closely as an independently-written wrapper allows") forces both routes toward the
mathematically unique answer an exhaustive search converges to, so agreement becomes
close to certain regardless of whether the code paths are independent. This entry does
not narrow `KN-FIND-7de6b6` — it names the **next** failure mode in the same family, one
that surfaces only once the first is fixed.

## 2. What was measured

`BATCH-a6fab5` built a genuinely non-code-shared, HKZ-quality-matched re-implementation of
`ROUTE-I` (`ROUTE-I''`) for the `hkz` observable, using `fpylll`'s own public reduction
API (a distinct code path — `fpylll.fplll.bkz.BKZReduction`, a low-level Cython class with
a 3-argument constructor — from the target's `fpylll.algorithms.bkz.BKZReduction`, a
high-level pure-Python class with a 1-argument constructor, confirmed structurally
distinct via direct class inspection). At all 6 covered cells (48/48 matched bases),
`ROUTE-I''` agreed with the archived target to `D_route'' = 1.7763568394002505e-15`
(binary64 machine epsilon) **uniformly** — thirteen orders of magnitude below the smallest
admissibility threshold at any covered cell.

## 3. How the confound was diagnosed — two methods, converging

Both reviews, working independently and via **genuinely different methods**, established
that this near-perfect agreement is close to a mathematical certainty for any two
correctly-converged implementations of this kind, not distinctive evidence of code-level
independence:

- **A from-scratch dual-route reimplementation, isolating the residual.** One review wrote
  a fresh implementation of BOTH routes' reduction algorithms (importing neither committed
  script) and found the raw HKZ-reduced Gram-Schmidt norms **bit-identical** between the two
  routes at every tested (cell, basis) pair — the entire measured deviation traced to a
  downstream arithmetic-formula choice in how the final scalar is computed from those
  norms, with **zero** disagreement in the actual reduction output itself.
- **A same-code-rerun null baseline plus a third, independently-structured implementation.**
  The other review re-ran the target's own unmodified code fresh, in an independent
  session, and reproduced every archived value **bit-for-bit exactly** — proving zero
  execution-time numerical noise in the underlying library, so any nonzero
  cross-implementation deviation could only come from a genuine difference in
  floating-point operation sequence, not randomness. It then built a **third**,
  differently-structured implementation (a different top-level driver, a different sweep
  order) and found it converged to the target's value at the one basis it computed
  correctly, to the same quantized precision the producer reported — directly
  corroborating the first review's mechanism from a wholly independent code path.

**Neither method required resolving whether a shared-kernel defect actually exists**
(which no test built anywhere in this campaign can do, given the fidelity-matching
mandate). Both diagnosed the LIMIT OF THE INSTRUMENT'S OWN POWER from properties of the
measurement and from built controls, not from assuming the answer.

One review additionally found and quantified a **checkable factual error** in the
producer's own independence declaration: a claim that a sub-formula was "reused
identically" between the two routes was false — the target route uses an empirical,
basis-dependent estimator where the new route used a mathematically-equivalent-in-exact-
arithmetic but numerically distinct closed form, contributing exactly one identified,
quantified component of the residual. This is a concrete instance of the general pattern:
even a careful, well-intentioned "identical reuse" claim in an independence declaration
needs the same checking discipline `KN-FIND-9b5df0` established for code-provenance
claims generally.

## 4. Why this generalizes beyond this goal

The general shape: any two-route independence test that requires the second route to
match the first route's **fidelity** as closely as possible — precisely the fix for a
fidelity-mismatch confound (`KN-FIND-7de6b6`) — pushes both routes toward the SAME
canonical answer whenever the underlying computation is **exhaustive** (a search to a
provable fixed point, not a heuristic or truncated one). Once both routes reach that fixed
point, their outputs are near-identical by mathematical necessity, not by virtue of
sharing code. This means:

1. **Fidelity-matching and code-independence are not the same axis of confound
   protection, and satisfying both does not automatically buy protection against every
   kind of shared defect.** A test built to catch wrapper-level bugs (basis construction,
   initialization order, bookkeeping, tolerance handling) genuinely does catch them — the
   sharp contrast between this batch's near-zero deviation and an earlier,
   fidelity-**mismatched** attempt's real, structured 0.015–0.223 deviation at the SAME
   cells is direct, positive evidence the instrument has real power there.
2. **The SAME test has structurally low power against a defect in code the two routes are
   licensed, or required, to share** — a common definitional formula, a common
   basis-construction helper (both often deliberately, correctly licensed to be shared,
   since they are zero-degrees-of-freedom functions of public inputs), or a common
   underlying library call for the decisive computational step. A defect at that shared
   level is reproduced identically by both routes by construction, regardless of how
   independently the surrounding wrapper code is written.
3. **This is diagnosable, without resolving the underlying question**, by: (a) directly
   comparing the RAW intermediate output of both routes' core computation (not just the
   final derived scalar) to see whether it is bit-identical at a stage before any
   independently-written arithmetic is applied; (b) a same-code-rerun null baseline to
   establish the execution environment contributes zero noise, so any residual is
   attributable to a specific, traceable code difference; (c) building a genuinely THIRD,
   differently-structured implementation to corroborate that any two correct
   implementations converge to the same answer, independent of which two are compared.
4. **The decisive further check this failure mode calls for is a mutation-testing
   (positive) control on the instrument itself**: deliberately inject a known defect into
   a copy of the code the two routes are licensed to share, and confirm the comparison
   mechanism actually flags it. This is distinct from, and does not substitute for,
   checking code provenance (`KN-FIND-9b5df0`) or fidelity-matching (`KN-FIND-7de6b6`) —
   it tests whether the INSTRUMENT has power against the specific failure mode it is
   nominally designed to catch, using a KNOWN ground truth rather than an unknown one.

## 5. What this changes, and what it does not

**It changes nothing about the termination branch's firing** — the branch fired correctly
and mechanically, per its own frozen rule, on the data as measured; neither review disputed
the branch call. **It changes what the branch's default license text may be cited as
saying.** The pre-registration's own default reading (near-perfect agreement discharges the
qualification "exactly as" an earlier, unrelated discharge that rested on an EXACT,
algorithm-independent invariant) is shown to overstate the analogy: the earlier discharge's
strength held REGARDLESS of fidelity-matching, because its underlying quantity is an exact
invariant at any sufficient reduction quality; THIS discharge's strength is
CONDITIONAL on the fidelity-matching mandate itself, which is what forces the canonical
convergence in the first place. A genuinely code-independent, genuinely fidelity-matched
route can still fail to test what a two-route comparison is nominally designed to catch.

**It does not resolve whether a shared-kernel or shared-definitional defect exists** for
the specific measurement this entry comes from. That question remains open and is not
addressed by anything in this entry.

## 6. What a successor must do, and what it must not

1. **State explicitly, alongside any discharge that rests on a fidelity-matched
   comparison whose target computation is exhaustive, what class of defect the comparison
   has power against and what class it structurally cannot address** — not merely that
   the routes are "independent," which by itself does not establish the comparison has
   power against every kind of shared defect.
2. **Before citing a fidelity-matched, code-independent agreement as ruling out a shared
   defect, check whether the decisive computational step is itself literally the same
   underlying library call or routine in both routes.** If so, the comparison cannot
   distinguish "both routes are correct" from "both routes share the same defect at that
   step," regardless of how independent the surrounding code is.
3. **The cheapest available check that closes this gap is a mutation-testing (positive)
   control**: inject a known, small defect into a copy of the shared code and confirm the
   existing comparison mechanism detects it. This is not a repeat of the original
   comparison (it uses a KNOWN ground truth, not an unknown lattice quantity) and is not,
   by itself, subject to a bar against repeating an already-answered measurement.
4. **This is not a claim that fidelity-matched two-route comparisons are useless.** For a
   quantity whose computation is NOT exhaustive-search-based, or where the two routes
   genuinely cannot share any code component (no licensed basis-construction or
   definitional-formula reuse), this confound does not arise. The failure mode is specific
   to instruments where matching fidelity requires matching algorithm structure closely
   enough that both routes are pushed toward the same canonical fixed point.

## 7. Scope and limits — read before citing

1. **THE FINDING IS REACHED BY TWO INDEPENDENT REVIEWS VIA DIFFERENT METHODS.** One found
   it via a from-scratch dual-route reimplementation isolating the residual to a
   downstream formula choice; the other via a same-code-rerun null baseline plus a third,
   independently-structured implementation. Neither saw the other's write scope. Each is
   otherwise a single session and must be cited as such.
2. **INDEPENDENCE IS PROCEDURAL — NEVER MODEL-LEVEL, AND HERE NOT ENVIRONMENTAL EITHER.**
   AGENTS.md rule 12 is **UNMET AND UNWAIVED**. Both reviews ran on the SAME model and,
   very likely, the SAME host/container as the producer.
3. **IT DOES NOT SAY WHETHER A SHARED-KERNEL OR SHARED-DEFINITIONAL DEFECT EXISTS.** That
   question is explicitly and deliberately left open (§2, §5).
4. **NOTHING HERE IS AN IMPOSSIBILITY RESULT.** §6 names what a successor must do; it is
   untested, not unavailable — the mutation-testing control it names has not yet been
   built anywhere in this campaign.
5. **DERIVATIONS AND CONSTRUCTIONS, NOT THEOREMS.** The mathematical argument (exhaustive
   enumeration to a fixed point computes a genuine lattice invariant) is a well-established
   property of exact lattice enumeration, not a novel proof of this entry's own; the
   empirical corroboration (bit-identical raw output, zero-noise reruns, a converging
   third implementation) is this campaign's own built evidence for it applying here.
6. **IT ESTABLISHES NOTHING ABOUT ANY LATTICE.** `BATCH-a6fab5` adjudicates no proposition
   about a lattice's admissibility, revalidates no prior batch, retires no prior
   amendment, and closes, pauses and completes nothing.

## Identifier provenance

`KN-FIND-d29ece` was drawn **without scanning state** (AGENTS.md rule 14) and confirmed in
**two scopes** by the dispatching session at the Coordinator's request: worktree
`tools/allocate_id.py --check` (well-formed by the KN-* convention, 0 occurrences across
6,680 identifier-bearing paths) **and** a cross-ref sweep of the 25 most-recently-updated
remote branches (0 hits), plus confirmation that it is not tracked under
`knowledge/findings/` on `origin/main`. Recorded as two-scope confirmed and **never** as
`--check` alone. The Coordinator that specified this entry's content held no shell and
claimed neither check as its own; both were performed by the dispatching harness session.

## Superseding relationship

This entry does not narrow any prior finding in this goal. **No prior entry is edited and
no `superseded_by` is set** on any of them. It stands beside `KN-FIND-7de6b6` as a
companion instrument-design lesson in the same family — fidelity-matching after
provenance-auditing, and now: even genuine code-independence plus genuine fidelity-matching
does not by itself demonstrate protection against every shared-code failure mode —
cross-referenced from `DEC-20260813-894568`'s `knowledge_promotion` field.
