---
id: KN-FIND-aa2efc
type: internal_finding
title: "On ECC2K-130 the decomposition-oracle family is bounded below by its own arity arithmetic rather than by oracle quality: the product law relations x targets x oracle = m*2^131 is independent of dim V, so a FREE oracle at m = 3 still costs 2^68.58 against rho's 2^60.8090, and the Riemann-Roch encoding -- while decisively better than Semaev-via-SAT (32/32 vs 0/32 at d = 6) -- costs 2.02x a structureless brute-force pair enumeration on identical solution sets"
tags: [ecdlp, ecc2k-130, koblitz, index-calculus, point-decomposition, riemann-roch, nagao, semaev, null-object-control, method-ceiling, amortization, negative-result, toy-tier, external-provenance]
confidence: six_frozen_rounds_in_an_external_repository_with_a_null_object_control_and_two_adversarial_corrections_folded_in_no_reviewer_in_this_program_has_read_the_artifacts
evidence_level: toy_tier_measurement_plus_derivation
source_refs: []
source_refs_note: >-
  Empty and deliberately so. Every round ran under a contract frozen before its
  own execution, but in github.com/aburan28/crypto, not under a TASK-* of this
  program. Inventing a TASK id here would be a fabrication under AGENTS.md
  rule 5. The artifacts are bound by sha256 in EV-ICPERF-10c5fc's
  external_provenance block, which is the content-first binding CLAUDE.md
  requires and is stronger than a commit reference for exactly the reason that
  repository already demonstrated: two earlier pull requests there were
  squash-merged and made recorded commit shas unreachable.
internal_refs: [EV-ICPERF-10c5fc]
sibling_findings_narrowed: []
sibling_findings_note: >-
  Narrows nothing. It EXTENDS KN-FIND-007 (yield conservation: mean yield
  C(B+m-1,m)/N for every base of size B), which explains why widening the
  factor base or adding summands moves cost within this family and never out of
  it, and it is the measured companion to the coverage/scaling bound
  min(1, C(B+2,3)/r).
proof_status: derivation
proof_refs:
  - >-
    The free-oracle floor table is arithmetic on the product law, not a
    measurement: relations x targets x oracle = m * 2^131 independently of
    dim V gives a required oracle speedup of 2^-(70.19 + log_2 m), hence
    m = 2 -> 2^89.25, m = 3 -> 2^68.58, m = 4 -> 2^56.40, m = 5 -> 2^48.44,
    m = 6 -> 2^42.85, m = 8 -> 2^35.61.
  - >-
    The target-side degree-2 vanishing ideal is EXACTLY TRIVIAL for all d >= 6
    at m = 4, by monotonicity in d at that fixed arity: nested V_d implies
    nested D_d implies a shrinking degree-2 ideal, so triviality at d = 6
    forces triviality above. Base case at m = 4: d = 5 gives dim 6967 over 1680
    distinct points at rank 1680; d = 6 gives dim 0 over 140400 distinct points
    at rank 8647. The same claim at m = 3 is UNPROVED on this argument:
    monotonicity does not change arity, the m = 3 and m = 4 value sets are
    different maps, and I_2 of the m = 4 set being zero does not imply I_2 of
    the m = 3 set is zero.
review_refs: []
review_refs_note: >-
  None in this program. Two adversarial reviews did run in the producing
  session and both found real errors -- an arity error claiming the m = 4 prize
  of 2^56.40 for an m = 3 object whose floor is 2^68.58, and a headroom
  overstatement of 2^11.44 that silently assumed a materialised orbit-union
  base unavailable for an F_2-subspace. Both corrections are folded into the
  numbers above. That is not this ledger's independence check and is not
  presented as one.
added: '2026-09-17'
superseded_by: null
---

# The decomposition-oracle family on ECC2K-130 is arity-bounded, not quality-bounded

## The curve, exactly

`K_0 : y^2 + xy = x^3 + 1` over `GF(2^131)` in a permuted type-II optimal normal
basis, with `#E = 4r` and `r` the 129-bit prime
`680564733841876926932320129493409985129`. The rho reference is `2^60.8090`,
which already includes the `<-1> x <pi>` speedup. Every "versus rho" figure
below is arithmetic against that published number, not against a rho measured
on this host.

## What was measured

Six frozen rounds, each contract written before its own execution.

**Riemann-Roch beats Semaev-via-SAT decisively.** Encoding the decomposition in
`L(4O)` as `f = x^2 + ax + c + by` with
`div(f) = (P_1)+(P_2)+(P_3)+(-R)-4(O)`, and running matched ECC2K-130 targets
under identical factor-base constraints and identical budgets: 32 of 32 at
`d = 6` for Riemann-Roch against 0 of 32 for Semaev-via-SAT. 128 trials, 0
errors, 28 relations re-derived independently rather than compared to a stored
answer key.

**The structureless null is twice as cheap.** Brute-force pair enumeration over
the factor base carries none of the Riemann-Roch structure and cost `0.494x`
the field operations at `d = 6`, on identical solution sets. The control was run
before belief, not after a disappointing result.

**The method realises the generic quadratic cost.** Candidates against
`|F|^2/2` read 3.00, 3.12, 2.33, 1.92, 1.99 at `d = 4..8`, with the operation
ratio falling 2.83 to 1.55. So the oracle sits at the `Theta(|F|^2)` that pair
enumeration realises for 3SUM over a group, with a constant near 2. The frozen
prediction said "roughly flat" and is partially falsified: the ratio fell.

**Amortisation is three orders of magnitude short.** The share of the relation
search amortisable across a target batch measured 0.12% at `d = 6` and 0.07% at
`d = 7`. Rho amortises `k` simultaneous DLPs as `sqrt(kr)`, so per-target cost
falls as `1/sqrt(k)`. A 0.12% shared prefix does not compete with that.

**The cheap structural certificate expires at d = 6.** Weil descent of `S_4` in
a V-basis gives 131 Boolean equations in `3d` unknowns, total degree 6,
multidegree (2,2,2). A linear NO-certificate -- a functional `lambda` with
`lambda(S_4(x_1,x_2,x_3,x(R))) = 1` on all of `V^3` -- exists iff the affine
span of the value set misses 0. Span dimensions measured 71, 97, 123 at
`d = 4, 5, 6`, and the span saturates the full 131 from `d = 7` onward
(confirmed directly at `d = 45`). The certificate that could cheaply rule out
decomposability stops existing right where the interesting dimensions start.

## Why this bounds the family and not just the implementation

The product law is independent of `dim V`. Charge the oracle **nothing at all**
and the floor at `m = 3` is still `2^68.58`, which is `2^+7.77` **worse** than
rho. No amount of oracle engineering at `m = 3` produces a crossover. The first
row that is even in principle below rho is `m = 4`, at `2^56.40`, and that is
`2^-4.41` of headroom before any oracle cost is charged at all. The best
measured configuration in the family, orbit-union at `m = 2`, bottoms at
`2^124.99`, or `2^+64.18` times rho; its implicit base is `2^132.58`.

## Read the other way

The product law is a **specification**, not only a bound. It says exactly what
an `m >= 4` oracle must cost to clear rho, which converts an open-ended search
into a costed target and is why the `m >= 4` rows stay live work. The span
saturation at `d = 7` is likewise a resource for the converse question: it says
`S_4`'s Weil descent is non-degenerate there, which is the input a
first-fall-degree argument wants.

Against that, one route is now closed by derivation rather than fatigue: the
target-side degree-2 vanishing ideal is exactly trivial for all `d >= 6` at
`m = 4`. Do not re-propose a low-degree target-side certificate at `m = 4`.
The same statement at `m = 3` is not proved here: the only exact-kernel base
case is `m = 4`, and d-monotonicity cannot carry it across arities.

## What this does not say

Nothing about any other curve, including the other Certicom challenge curves
and the FIPS binary curves. Every relation-search and cost-ratio number is at
`d = 4..8` against a real base of `d = 131`. No relation matrix and no full DLP
was computed, and no rho was measured on this host, so
`GOAL-ICPERF-e6b6a4` criterion C1 is **unmet** and untouched. The `d = 7`
operation ratio from the null-object round is **withdrawn** -- it compared a
completed enumeration against timed-out arms, which reads a timeout as negative
mathematical evidence and breaks AGENTS.md rule 3. Only the `d = 6` figure of
`0.494x` is citable.

## Revisit condition

A decomposition oracle with a demonstrated sub-quadratic candidate count at
`m >= 4`, or a matched same-host rho column that materially changes the
`2^60.8090` reference.
