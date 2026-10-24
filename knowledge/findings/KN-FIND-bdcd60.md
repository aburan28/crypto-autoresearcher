---
id: KN-FIND-bdcd60
type: internal_finding
title: "Generic monodromy of the Semaev summation cover over F_p is uniform in the curve: (Z/2)^{m-2} regular over the ordered base, (Z/2)^{m-2} semidirect S_{m-1} over the symmetric base (m >= 4), with an exact Frobenius rule on unramified F_p-fibres (derivation tier, toy corroboration)"
tags: [semaev-polynomial, summation-polynomial, monodromy, galois, chebotarev, frobenius, prime-field, elliptic-curve, derivation, toy-scale]
confidence: established
confidence_note: "established for the derivation (re-derived blind and independently in one rule-12 review round, agreeing with the original reviewer derivation); corroborated at toy primes with m <= 5 measured; model identities not probe-verified; not a statement about relation rates"
internal_refs: [DEC-20261022-a0f165, DEC-20260930-8553d4, DEC-20261017-435b01, DEC-20260904-dd58c3, H-MONO-ebd400, H-MONO-93bc4d, EV-MONO-e9dc3b, EXP-MONO-0e6e8f, RQ-MONO-001, TASK-20261017-8aff64, TASK-20261017-ccd10c, TASK-20260930-40470a, KN-FIND-4f0d84]
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MONO-001/review/TASK-20261017-ccd10c/blind_rederivation.md
  - coordination/goals/GOAL-MONO-001/review/TASK-20261017-ccd10c/computations.json
  - coordination/goals/GOAL-MONO-001/review/TASK-20261017-8aff64/review_report.md
  - coordination/goals/GOAL-MONO-001/review/TASK-20261017-8aff64/computations.json
  - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/review_report.md
  - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/s4_construction/computations.json
added: 2026-10-22
superseded_by: null
---

Promoted by DEC-20261022-a0f165 (knowledge_promotion, under
REVIEW-MONO-20261017-8aff64 composition key RA-C5). The Statement and Scope
sections are verbatim from that decision's statement_frozen and scope_frozen.
Counter-statements quoted below are verbatim from the record named with them.

## Statement

For every prime p > 3, every nonsingular E: y^2 = f(x) = x^3 + ax + b over
F_p (any j-invariant, ordinary or supersingular) and every m >= 3, let
F(T) = S_m(x_1, ..., x_{m-1}, T) with x_1..x_{m-1} independent indeterminates
and K an algebraic closure of F_p. (1) Ordered base. F has degree 2^{m-2} in
T and is squarefree; its Galois group over K(x_1..x_{m-1}), as a permutation
group on the roots, is elementary abelian (Z/2)^{m-2} acting regularly (V_4
at m = 4), and the arithmetic group over F_p(x_1..x_{m-1}) equals it. (2)
Symmetric base. Over K(e_1..e_{m-1}) the group is, for m >= 4, (Z/2)^{m-2}
semidirect S_{m-1}, the image of Z/2 wr S_{m-1} with kernel {+1, -1}, of
order 2^{m-2}(m-1)!: S_4 = AGL(2,2) at m = 4 and orders 192, 1920 and 23040
at m = 5, 6, 7; it is primitive iff m - 1 is odd (primitive at m = 4 and 6;
at m = 5 and 7 exactly one nontrivial block system, two blocks of size
2^{m-3}); at m = 3 it is S_2 of order 2. The arithmetic group equals the
geometric one. (3) Frobenius rule. For x_1..x_{m-1} in F_p, not required to
be x-coordinates of F_p-points, with every f(x_i) != 0 and F squarefree of
full degree, Frobenius acts on the roots as translation by the class of
(chi(f(x_1)), ..., chi(f(x_{m-1}))) modulo +-(1, ..., 1): the cycle type is
1^{2^{m-2}} iff all chi(f(x_i)) are equal, and 2^{2^{m-3}} otherwise. (4)
None of (1) to (3) depends on (a, b): no curve has a different generic
monodromy on either base.

## Scope

Derivation tier (docs/claims-and-verification.md level 2, never "proved");
generic monodromy only, nothing about specializations to proper closed
subvarieties. The "every m" extent rests on the derivations; group orders at
m = 6, 7 rest on the derivation plus a curve-free permutation-group
computation. Measured corroboration covers m in {3, 4, 5} only, at p in {53,
59, 101, 103, 997, 1009, 1013, 1019, 10007, 10009}, on the curves the two
reports tabulate; nothing at m >= 6 is measured. Toy tier; CS-R7 binds.

## Basis

- The derivation: the roots are x(P_1 + sum eps_i P_i) over sign classes; the
  Kummer group Gal(K(x, y)/K(x)) is (Z/2)^{m-1} because no nonempty product of
  the f(x_i) is a square (nonsingularity); it acts on sign classes by
  translation with the diagonal as kernel; generic distinctness of the root
  values (no Z-linear relation among generic points of E^{m-1}) makes the
  action faithful; the Frobenius rule is its specialization at unramified
  F_p-points; the symmetric base adds Gal(K(x)/K(e)) = S_{m-1}.
- Three derivations agree: the original reviewer derivation
  (TASK-20260930-40470a, recorded as DEC-20260930-8553d4 CU-9), the blind
  re-derivation TASK-20261017-ccd10c (from the statement and parameters
  alone), and the independent re-derivation of TASK-20261017-8aff64 (written
  before it opened the predecessor report, by its attestation).
- Corroboration, all at toy primes: TASK-20261017-ccd10c checked its own S_3,
  S_4, S_5 on 24,000 tuples, enumerated F_p^{m-1} exhaustively at m = 3, 4 on
  four curves with p <= 103, sampled 50,000 tuples at m = 4 and 5,000 at m = 5
  on four curves with p >= 997, and 20,000 symmetric-base points at m = 4 on
  four curves plus one exhaustive enumeration at p = 101, with the Frobenius
  rule exact on every admissible tuple. TASK-20261017-8aff64 sampled j = 0,
  j = 1728, two supersingular and one generic curve at p near 10^4 and the
  EXP-MONO-0e6e8f census curves, found no cycle type outside the claimed
  group on 334,354 sampled nondegenerate fibres plus 95,328 exhaustive at
  p = 53, matched identity frequencies to exact finite-p expectations, and
  regenerated the EXP-MONO-0e6e8f OBS-1 instances: all 12,243 g-split "2+1+1"
  fibres on C1 and C2 are non-squarefree, none a counterexample.
- Semaev 2004 is cited in both reports as a recalled pointer only; the two
  facts used (the defining property and the resultant recursion) were
  verified numerically at m = 3, 4, 5 by each reviewer.

## Where the argument stops (proves-too-much control, TASK-20261017-8aff64 section 6)

- PT-1, generic points of E^{m-1}: the y_i lie in the base, the Kummer group
  is trivial, and so is the monodromy.
- PT-2, the [2]-graph x_2 = x([2]P_1) at m = 3: f(x_1) f(x_2) is a square, the
  independence step fails, and the group is trivial.
- PT-3, the square-discriminant cover at m = 4: S_3 becomes A_3 and the image
  is A_4.

## Corrections this finding carries

CS-PR of DEC-20261022-a0f165, verbatim:

> H-MONO-93bc4d (statement and claim_boundary "a proper imprimitive
> subgroup of Sym(2^{m-2}) at m>=5"), DEC-20260904-dd58c3's limitation
> ("PROPER, imprimitive") and DEC-20260930-8553d4 CU-9 ("primitivity
> varying for m = 5..7") are read with the corrected wording: for m >= 4
> the symmetric-base group (Z/2)^{m-2} semidirect S_{m-1} is primitive
> iff m - 1 is odd. It is primitive at m = 4 (S_4) and at m = 6 (order
> 1920, proper); at m = 5 and m = 7 it is imprimitive with exactly one
> nontrivial block system, two blocks of size 2^{m-3} (the parity classes
> of the number of minus signs).

CS-M3 of DEC-20261022-a0f165, verbatim:

> The order 2^{m-2}(m-1)! of the symmetric-base group holds for m >= 4.
> At m = 3 the symmetric-base group is S_2 of order 2 (the kernel has
> order 4), as CORR-20260904-d2c631 records for H-MONO-93bc4d (D3).

## What this does not settle

CS-K1d2 of DEC-20261022-a0f165, verbatim:

> Nothing in this decision or its projections states or implies that
> GOAL-MONO-001 criterion (a) is met. On KN-OPEN-009's ordered base the
> generic monodromy is (Z/2)^{m-2} acting regularly, for every
> nonsingular curve; it is not full symmetric or wreath. The completion
> rests on criterion (c) alone.

CS-R7 of DEC-20261022-a0f165, verbatim:

> Toy tier. Nothing here concerns the relation-rate question, the D-4
> factor-base-point count beyond "not condemned", extension fields or
> cryptographic scale. No exponent moves and no security estimate moves.

The objective's dichotomy "full monodromy versus an exceptional locus" is not
exhaustive for this cover: on the ordered base the generic group is uniformly
small and imprimitive for every m >= 4, for every curve, which is neither
branch; "full symmetric" holds literally only at m = 4 on the symmetric base.
Nothing is asserted about specializations to proper closed subvarieties
(PT-2 shows the group can shrink there). On the factor-base locus, where
every chi(f(x_i)) = +1, the Frobenius rule gives complete splitting on
nondegenerate fibres, consistent with KN-FIND-4f0d84, whose statement also
covers the degenerate fibres and is not restated here. The open questions are
in KN-OPEN-62c870.

Literature: the ordered-base irreducibility of S_m is published
(arXiv:1403.0126 Theorem 1, as the H-MONO-93bc4d status note records it;
pointer only, not read by DEC-20261022-a0f165). Whether the group
determinations are already published was not checked; this entry records an
internal re-derivation, not a new theorem.

## Independence

CS-IND of DEC-20261022-a0f165, verbatim:

> Independence in REVIEW-MONO-20261017-8aff64 is by session and role.
> The blind re-derivation (TASK-20261017-ccd10c) ran first, read no
> blind_from path and could not see the joint review. The joint owner
> (TASK-20261017-8aff64) attests that it never opened the re-deriver's
> files, which sat in a scratchpad it could list; that rests on its
> attestation and on method divergence. Both reviewers report
> claude-fable-5-1 and the composer claude-opus-5-5; no identifier is
> probe-verified.
