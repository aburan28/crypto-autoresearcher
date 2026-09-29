---
id: KN-FIND-c2e9a7
type: internal_finding
title: >-
  A divisor-parity / residual-square-class obstruction predicate for
  ordinary PMA4 reciprocal-minor tables over k(t) is necessary but not
  sufficient for 4x4 matrix existence -- proven on a narrow, forced F_5(t)
  table family, including non-existence over the algebraic closure
tags:
  - pma4
  - principal-minor-assignment
  - divisor-parity
  - rational-function-field
  - toy-scale
  - derivation
  - negative-result
  - scoped-rejection
  - necessary-not-sufficient
confidence: established
confidence_note: >-
  Established via four independent, algorithmically distinct methods
  converging on the same conclusion on every one of the 5 distinct tested
  instances: (1) the predicate module's own factorization-based squareness
  test; (2) an independently implemented coefficient-matching constructive
  decider with branch enumeration and 16/16 witness reverification; (3) the
  Red Team's from-scratch brute-force polynomial-square-root search plus an
  independently re-derived 8-branch matrix construction; (4) the Red Team's
  from-scratch unconstrained (no WLOG normalization) Groebner basis
  computation over the algebraic closure of F_5(t), returning the trivial
  ideal -- proving non-existence even over the closure, not merely over
  F_5(t) itself. The Validator additionally reproduced every reported
  count from raw data with 0 mismatches. Neither reviewer read the other's
  report before filing (VAL-20260907-ae3832, RT-20260907-0df70c).
internal_refs:
  - H-PMA-001
  - RQ-PMA-001
  - IDEA-20260726-012
  - EXP-PMA-001
  - EV-PMA-fbdd4c
  - DEC-20260907-90a00d
correction_note: >-
  CORR-20260907-ae8418 and CORR-20260907-f41219 are cited in prose below
  (they are not ledger ids in ctx.ids's sense, so they are not listed in
  internal_refs, matching KN-FIND-002.md's established convention of
  keeping correction citations out of the cross-checked internal_refs
  list).
proof_status: derivation
proof_refs:
  - experiments/EXP-PMA-001/reviews/RT-20260907-0df70c.yaml
  - experiments/EXP-PMA-001/runs/RUN-PMA4-001-b/raw-result.json
  - experiments/EXP-PMA-001/runs/RUN-PMA4-001-c/raw-result.json
added: '2026-09-07'
superseded_by: null
---

## The finding

For ordinary PMA4 reconstruction over `k(t)` (`char k != 2`) from prescribed
reciprocal-minor data `p_emptyset = 1`, `p_S = (t+1)/(t+d_S)`, a predicate
that certifies only the squareness (in `k(t)`, including the valuation at
infinity and the residual constant class) of the three anchored orientation
discriminants `Delta_ijk = c_ijk^2 - 4*q_ij*q_jk*q_ki` is **necessary but
not sufficient** for the existence of an ordinary 4x4 matrix realizing the
prescribed principal minors. This was already anticipated as a possible
outcome in `H-PMA-001`'s own frozen `interpretation_limits` ("necessary,
not sufficient"); this record is what makes that anticipated limitation a
**proven, scoped, checkable result** rather than a caveat.

**Scope, stated exactly.** Proven on 5 distinct `F_5(t)` instances -- the
entirety of the distinct tables reachable by `EXP-PMA-001`'s frozen grid
construction for `F_5`, forced by that field's 3-element parameter box
(`allowed_values` has `q-2` elements) into exactly 3 distinct rational
functions `(t+1)/(t+2)`, `(t+1)/(t+3)`, `(t+1)/(t+4)`, each repeated across
5 of the 15 required subsets. On every one of those 5 instances: all three
anchor discriminants are squares in `F_5(t)` (predicate: compatible), yet
**no 4x4 matrix realization exists at all, even over the algebraic closure
of `F_5(t)`** -- an unconstrained Groebner basis computation over the 12
unknowns and 11 defining equations (no WLOG diagonal-conjugation
normalization) returns the trivial ideal.

**What is NOT claimed.** Nothing about a non-repeating `F_5(t)` table
(untested -- this grid's box construction cannot produce one), nothing
about any other field (F_3's 1 distinct instance, F_7's 3 distinct, and
Q's 5 distinct instances all showed *no* sufficiency failure in this run),
and nothing about any generic-family, all-size-PMA, or asymptotic/
cryptographic question. `claim_tier: toy` throughout;
`certificate.kind: none` in every run; no ECDLP, relation, or scalar
content anywhere.

## What survives, distinctly

The narrower, one-directional reading of the same mechanism -- **an odd
valuation (or nonsquare residual constant class) in a canonically reduced
anchor discriminant is fatal to matrix existence** -- is *unrefuted* by
this finding and is non-vacuously confirmed with zero counterexamples
across every decided instance in the same run (8 distinct nonvacuous
obstructions: F_7's 3, Q's 5). This finding does not extend to, and must
not be read as undermining, that separate claim; `DEC-20260907-90a00d`
records both as distinct tracked outcomes rather than collapsing them.

## Sample-size correction folded into this finding

The originally committed run package counted 18 "F_5 instances" as 18
independent observations; `CORR-20260907-ae8418` establishes these are 5
distinct tables repeated under different instance labels
(`grid`/`perturbed`/`widened_grid`), because the grid's "widening fallback"
is a dead no-op for any field whose parameter box is smaller than the
15-subset assignment stride's period (true for F_3 and F_5). This finding
is stated on the corrected, distinct-instance basis (5, not 18) throughout.

## Resource check

No theory currently active in this program takes "parity-necessity without
sufficiency" as its own premise. The candidate reading under which this
result becomes a resource rather than a dead end: a two-stage classifier
that uses the parity predicate only as a fast, cheap necessary-condition
pre-filter, deferring to a slower sufficient-condition confirmation (e.g.
the mask-15 four-minor gate `H-PMA-001`'s own `interpretation_limits`
already names as an independent requirement) only on filter-surviving
instances. No such record exists yet; this is a candidate reading, not an
existing spawned resource (`EV-PMA-fbdd4c`'s `obstruction.resource_check`).

## Open follow-up (not yet executed)

Whether this sufficiency failure is F_5-specific or a general property of
the repeated-value table family at any field is undecided. The
discriminating experiment -- a field whose box does not collide with the
15-subset stride (F_11 or F_13, `q-2 >= 9`), or a table built from >= 15
genuinely distinct rational functions -- is recommended in
`CORR-20260907-ae8418`'s `next_action` and is not yet designed or
executed.

## Attribution

Mechanism and predicate: `IDEA-20260726-012`. Predicate/decider
implementation and initial run package: Executor
(`DEC-20260906-9f036a`-authorized dispatch). Independent validation
(full recomputation, 0 mismatches) and red-team review (two additional
from-scratch refutation methods, including the Groebner-over-the-closure
computation that anchors this finding's `derivation` proof status):
`VAL-20260907-ae3832`, `RT-20260907-0df70c`. Sample-count and
box-collision correction: `CORR-20260907-ae8418`. Composition into this
evidence record and finding: Coordinator, `EV-PMA-fbdd4c` /
`DEC-20260907-90a00d`.
