# Mersenne rotation-class factor-base audit

## Audit basis

- Idea: `IDEA-20261009-354b14`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- The proposal is recorded as a negative control for the small-coordinate
  factor-base line, with `KR-IC-5931ee` and `H-ECDLP-bd1572` as nearby
  references.

## Mathematical boundary

For `p = 2^c - 1`, multiplication by 2 modulo `p` is a cyclic permutation of
the chosen `c`-bit integer representatives (apart from the zero convention).
That is an integer-representation identity, not a field automorphism: it does
not preserve addition or multiplication in `F_p` in the required way. The
displayed curve scaling `(x,y) -> (2x, 2^(3/2)y)` is not a map over `F_p`
without an explicitly supplied square root of 2, and even a valid coordinate
isomorphism between two separately parameterized curves would not turn the
integer rotation into a nontrivial endomorphism of one fixed curve.

Consequently the filed mechanism must not say that the rotation action
“respects nothing of the group law” by deriving that conclusion from a
purported curve action. The only admissible object here is a factor-base
membership rule on an integer encoding of `x(P)`, followed by a measured
comparison with matched controls.

## Contract repairs

The finite control can remain useful, but it needs these repairs before any
approval or run:

1. Define the encoding exactly: the unique representative in `[0,p-1]`, the
   treatment of `0`, the direction of rotation, and the tie rule for an orbit
   minimum. Prove or test the claimed rotation identity independently of the
   curve code.
2. Separate the cyclic orbit of field *integers* from any geometric action on
   `E`. Do not quotient points or claim a curve symmetry unless a complete
   field-defined map, inverse, and group-law compatibility certificate is
   supplied.
3. Specify whether `D_rot` contains x-values, affine points, or sign orbits.
   Give its exact cardinality, the induced point count, and the membership
   cost. “About `p/2^m`” is not enough when closure and decomposition ratios
   are compared across densities.
4. Match every null to the same object and cardinality: random x-values,
   random sign-complete point sets, the digit-graded base, and the random-prime
   base must each state whether they are x-level or point-level and how
   negation fibres are handled.
5. Replace the single `10^6`-pair result and the broad `[0.97,1.03]`
   criterion with predeclared binomial or finite-population intervals for
   every cell, plus the exact seed derivation and a deterministic ensemble of
   matched null subsets. The decomposition arm also needs its root-counting
   convention, target distribution, and cost accounting.
6. Certify that the selected Mersenne values are prime, that the comparison
   curves are nonsingular and ordinary, and that any subgroup/order and point
   enumeration receipts are independent of the factor-base membership code.

## Claim ceiling and disposition

A successful run could establish only the closure and decomposition statistics
of this particular integer-defined base over the declared finite fields and
controls. It would not establish a field automorphism, an elliptic-curve
endomorphism, a new relation mechanism, or an asymptotic ECDLP improvement.
A control result outside the proposed interval would falsify the filed null
prediction for that finite cell, not automatically supply an attack.

Disposition: **keep proposed as a conditional finite negative control; do not
approve it as filed.** Repair the encoding, orbit/object semantics, curve-map
claim, matched-null construction, and certificates. Because the goal-scoped
selector currently has no ready experiment, this audit does not create an
approval or a launch; the repaired item may be reconsidered only when it is a
complete, runnable contract and still ranks ahead of doing nothing.
