# P-256 covers lack a costed target-component solver

- **Status:** `investigating`
- **Kind:** implementation gap; geometric and cost questions
- **Affected work:** [F7 covers](../research/p256_factor_base_parallel_20261025/tracks/f7/report.md), TASK-20261025-7144c5, TASK-20261025-2fec58
- **Next action owner:** Coordinator for the explicit component/arithmetic follow-on
- **Last updated:** 2026-10-25

## Problem

Explicit same-field covers now transport the P-256 r-subgroup injectively into
Jacobians, but a useful relation algorithm on that component and its full cost
are not supplied by the cover geometry.

## Evidence and uncertainty

- **Derived and checked:** the smooth plane quartic U^4=X^3 Z-3 X Z^3+b Z^4
  is nonhyperelliptic of genus three. The genus-two control is
  w^2=z^6-3 z^2+b. Both map with degree two to the fixed P-256 curve.
- **Subgroup certificate:** pushforward after pullback is multiplication by
  two. Since r is odd, pullback is injective on the target r-subgroup. Fourteen
  rational/nonsplit fibre fixtures are retained. General Jacobian arithmetic
  is not implemented by these fibre encodings.
- **Observed:** the genus-two complementary elliptic trace was computed by
  Sage/PARI SEA. Its order is below r, so this factor supplies no additional
  r-component. Independent replay remains a review obligation.
- **Open:** the quartic Prym coefficient and r-primary multiplicity, generic
  norm/arithmetic, image-specific relations, descent and complete cost. A
  Cartier-eigenspace follow-on is proposed; its conclusion is not assumed.
- **Not established:** that a full ambient-Jacobian algorithm is competitive
  on this component, a smaller-field descent, or an ECDLP advantage.

## What would unblock it

- [ ] Explicit arbitrary-class arithmetic and norm with independent subgroup
  and scalar-recovery certificates, including exceptional divisors.
- [ ] A complete image-specific relation/descent algorithm, rather than a
  genus label or ambient solver bound.
- [ ] Complete setup, map, solving, rank, memory and recovery costs against
  the matched source-group reference.

Resolving a component-multiplicity question alone would not resolve the solver
or cost obligations. No goal or hypothesis status is changed.

## Next discriminating step

Audit the order-four automorphism's differential eigenspaces and Cartier
action, and determine what they actually imply about the Prym polynomial.
Retain the exact-field residue checks separately from any geometric theorem.
Then rank an arbitrary-class norm or relation-interface implementation on the
certified component. A missing implication remains open, and a failed process
is not a geometric obstruction. Recheck on the follow-on proof or an executable
arithmetic interface.

## Resolution and history

2026-10-25: opened from explicit cover and fibre certificates. Unresolved.


### 2026-10-25: local Cartier-component derivation

The [new derivation](../research/p256_factor_base_parallel_20261025/analysis/cartier-proposal/derivation.md) and [isolated local proof note](../research/p256_factor_base_parallel_20261025/reviews/maps_and_covers/cartier-proof-note.md) give p|A for the quartic Prym polynomial. The even Weil polynomial then has A=c*p with c=-2,-1,0,1,2, and all five order candidates are coprime to the actual target r. Thus the extra-r-component question is addressed by this scoped derivation without computing exact A. The local review reproduces a p=1 mod4 counterexample to extending it. Custody/model/blindness exceptions are explicit; no canonical scientific promotion is asserted. Exact A, arbitrary-class arithmetic and the target-component solver/cost requirements remain unresolved, so the problem stays investigating.
