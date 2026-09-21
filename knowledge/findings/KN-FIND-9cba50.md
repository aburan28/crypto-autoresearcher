---
id: KN-FIND-9cba50
type: internal_finding
title: "GOAL-DREG-001's subspace ladder measures a different object family from the one Semaev 2015 Assumption 1 quantifies over -- it uses Frobenius-invariant subspaces of dimension ord_n(2) where the assumption names arbitrary subspaces of dimension ceil(n/m), and the two dimensions coincide in 0 of 23 cells at m = 2 across n = 5..49 odd; measured ON the correct diagonal, first fall degree is flat at 3.00 for n = 7..63 against a shape-matched random null at 4.00, and the d_F4 <= 4 predicate reproduces at every cell n <= 21"
tags: [ecdlp, semaev-2015, assumption-1, d_f4, first-fall-degree, solving-degree, weil-descent, groebner, instrument-defect, null-object-control, binary-fields, toy-tier, external-provenance]
confidence: two_rust_instruments_with_a_shape_matched_null_plus_a_definitional_count_two_soundness_defects_found_by_automated_review_and_fixed_no_reviewer_in_this_program_has_read_them
evidence_level: toy_tier_measurement_plus_definitional_argument
source_refs: []
source_refs_note: >-
  Empty for the same reason as its sibling KN-FIND-aa2efc: the instruments are
  `cargo run --example` invocations in github.com/aburan28/crypto, not runs of
  this program's harness, so no TASK-* or RUN-* exists and inventing one would
  be a fabrication under AGENTS.md rule 5. Content binding by sha256 is in
  EV-ICPERF-a8080e's external_provenance block.
internal_refs: [EV-ICPERF-a8080e]
sibling_findings_narrowed: []
sibling_findings_note: >-
  Narrows no existing finding, but it QUALIFIES a body of measurement rather
  than adding to it: any GOAL-DREG-001 degree number taken through
  koblitz_bench::subspace_ladder is a statement about Frobenius-invariant
  subspaces of dimension ord_n(2), and cannot be read as evidence for or
  against Assumption 1 without being redone on the diagonal. The separate
  d_F4-versus-d_reg definitional gap is KN-OPEN-d218ec and is NOT closed here.
proof_status: empirical_only
proof_refs: []
proof_status_note: >-
  Empirical only, and the caveat is load-bearing. First fall degree and solving
  degree are NOT Semaev's d_F4. A value above 4 in either column would not by
  itself refute Assumption 1, and no such refutation is claimed anywhere below.
  The one exception is the dimension count, which is definitional rather than
  measured: ord_n(2) versus ceil(n/2) is checkable with no experiment at all.
review_refs: []
review_refs_note: >-
  None in this program. Automated review on the producing pull requests found
  two real defects and both are fixed: a hardcoded verdict string that ignored
  the degree flag, and -- materially -- a closure routine that returned the
  same "not capped" signal on genuine convergence and on rounds-exhaustion, so
  a partial closure could have emitted a positive `d_F4 >= 5` claim from an
  unfinished computation. The published rows are unaffected: all converged in
  2-3 rounds against a budget of 8.
added: '2026-09-17'
superseded_by: null
---

# Assumption 1 was being measured on the wrong subspaces

## The mismatch

Semaev 2015 (ePrint 2015/310) Assumption 1 asserts `d_F4 <= 4` for a Boolean
system equivalent to his eq. (5), where `V` is a subspace of `F_{2^n}` of
dimension `k = ceil(n/m)`. Two words there are load-bearing and this program's
instrument honours neither.

**`k = ceil(n/m)`.** `koblitz_bench::subspace_ladder` sets the dimension to
`ord_n(2)` instead. Across `n = 5..49` odd those two functions coincide
**never** at `m = 2` and exactly twice at `m = 3`. So 0 of 23 cells at `m = 2`
measured the dimension the assumption names.

**"a subspace".** `invariant_subspace_basis` returns a *Frobenius-invariant*
subspace, a linearised-polynomial kernel from a factor of `x^n - 1`. Assumption
1 quantifies over subspaces, not over that measure-zero special family.

Neither point depends on the separate `d_F4`-versus-`d_reg` definitional gap
(`KN-OPEN-d218ec`), which remains open independently.

## What the diagonal actually shows

Measured with `V` a **uniformly random** `F_2`-subspace of dimension exactly
`ceil(n/m)`, built by rejection on rank:

- First fall degree is **3.00, flat, across n = 7..63**.
- A matched random Boolean control -- same variables, equations, degree and
  mean monomial count -- sits at **4.00, flat**, over the same range.

That control is a null object, not a replicate. The first version of this
instrument used a replicate, which measures nothing; the 3-versus-4 separation
became a claim only after the null was swapped in. The separation says the
algebraic structure is buying exactly one degree, which also bounds how much a
structure-exploiting engine can be expected to gain.

Separately, a sound refutation predicate for `d_F4 <= 4` -- reporting a verdict
only on genuine degree-4 closure convergence -- returns REFUTED at **every cell
`n = 5..21`**, in 2 or 3 rounds against a budget of 8. Read the polarity with
care: REFUTED means the predicate that would witness `d_F4 > 4` is itself
refuted, so the assumption's bound is consistent with every cell reached.

## Consequence for the n = 40/45 boundary

With first fall flat at 3 through `n = 63` on the correct family, first fall is
**ruled out** as the explanation of the degree behaviour at the boundary
`GOAL-DREG-001` has been probing. What does explain it is unknown, and
`IMP-SEMBIN-ENGINE` stays binding for that cell: the engine headroom to settle
it does not exist on this host.

## Why this is a resource and not just a correction

A first fall degree **constant in n** on the correct subspace family is exactly
the input a Semaev-side cost derivation needs. It is the difference between a
cost formula whose degree parameter grows with the field and one whose degree
parameter does not, and the Certicom-binary and FIPS-binary cost table cannot
be stated conditionally on Assumption 1 without knowing which. Re-pointing the
ladder is also cheap: one parameter change from `ord_n(2)` to `ceil(n/m)` plus
random instead of invariant bases makes 23 dead cells live.

## What this does not say

Nothing at cryptographic `n`: the reachable range is `n <= 63` for first fall
and `n <= 21` for the refutation predicate, against targets at 131, 163, 233,
283, 409 and 571. Everything is at `m = 2`, whose swap symmetry is real
structure -- it is what confounded a first closure attempt, which tracked
decomposability rather than degree and is committed as a documented dead end
rather than shipped. Four trials per cell, so a cell with genuine variance
would look flat at this sample count. And the measured columns are first fall
and solving degree, which are not `d_F4`, so nothing here promotes anything.

## Successors

1. Re-point the `GOAL-DREG-001` ladder at `ceil(n/m)` with random subspaces and
   re-run the cells that matter. Cheap, and it converts uninformative cells into
   informative ones.
2. The derivation-only cost table for the Certicom binary challenge curves
   (prime extension degrees 97, 109, 131, 163, 191, 239, 359) and the FIPS
   binary curves (163, 233, 283, 409, 571), stated conditionally on Assumption
   1 and citing this entry for exactly what is and is not known about it at
   reachable `n`. That table must carry the coherent-baseline vOW rho
   comparison, which moves the crossover by `+85` in `n` and `-29.0` bits and
   puts the coherent crossovers at 520 dense and 460 sparse -- both above 409,
   which is what decides whether any listed curve is a target at all.
