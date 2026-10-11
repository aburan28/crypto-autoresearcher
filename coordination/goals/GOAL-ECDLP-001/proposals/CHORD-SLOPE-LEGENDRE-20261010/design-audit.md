# Chord-slope Legendre imbalance design audit

## Audit basis

- Idea: `IDEA-20261006-5899d8`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-4fcbd3`, `KR-RHO-13bf67`, and the coordinate-
  predicate controls.

## Scientific boundary

This proposal is a deterministic census with a carefully chosen pairing
control. The `F_1031` arm can validate the sign/Legendre implementation, while
the `F_1093` arm measures a finite gap after negation pairs remain in the same
character bin. Even a nonzero gap is only a property of one curve and one
predicate; it does not provide an inversion, relation collection, or ECDLP
advantage.

## Load-bearing repairs

1. Certify both field and curve cells. Record primality certificates,
   discriminant convention/residues, curve point enumeration, point-at-
   infinity handling, and the exact affine point set. Keep the all-points
   census separate from any prime-order subgroup census.
2. Define eligibility before counting. State how `y=0`, `[2]P=O`,
   `x([2]P)=x(P)`, zero slopes, and vertical chords are classified. Emit the
   complete excluded-point tallies and ensure the eligibility rule is fixed
   before observing the bin counts.
3. Verify the chord identity independently. Recompute `[2]P`, the slope, and
   the swapped-point slope with a second implementation; check that the latter
   is the negative of the former. Verify the Legendre symbol by an independent
   exponentiation or square-root test and record zero separately.
4. Make the forced-balance proof match the counted population. On `p=1031`,
   pair `P` with `-P` only after confirming that the map sends eligible points
   to eligible points and preserves all exclusions. State what happens to
   self-negating points and to slope-zero/vertical exceptions; otherwise the
   exact-zero control is not guaranteed.
5. Report finite uncertainty and selection. The claim is existential for the
   fixed `F_1093` curve, so exact counts suffice, but curve selection and the
   optional `F_1031` control must be frozen independently of results. If a
   broader bias claim is desired, add multiple curves/primes and a
   predeclared correction rather than generalizing from one gap.
6. Preserve the cost boundary. Record the `Theta(p)` enumeration and modular
   arithmetic cost as finite observations. A character imbalance is a public
   predicate; any use as a factor base or oracle would require a separate
   membership/precomputation/target-cost contract and a matched rho baseline.

## Readiness and disposition

The proposal has a coherent forced-balance control and a precise finite
observable. It needs only the exact eligibility, field/curve certificates,
independent formula checks, and pair-preservation receipt before conversion
to an executable bounded experiment.

Disposition: **retain proposed as a candidate finite chord-slope control; do
not approve or dispatch the idea record itself.** Convert it to a complete
ready experiment with exact enumeration and artifact paths, then recheck
capacity and selector admission.
