# Small-modulus x-bucket design audit

## Audit basis

- Idea: `IDEA-20261007-41f810`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KR-RHO-13bf67`, `KR-RHO-5b1c0a`, and the finite
  representation controls for `RQ-ECDLP-bc7a54`.

## Scientific boundary

The proposed statistic is a finite concentration test for integer x-values
reduced modulo `M`. It is not an inversion procedure, an online algorithm, or
an exponent result. The current record has a denominator mismatch and a null
model mismatch: quotienting by negation changes the number of observations,
while a random injection into `F_p` does not reproduce the curve’s x-coordinate
fibres, which naturally contain the pair `{P,-P}`.

## Load-bearing repairs

1. Fix the counted population. State whether the histogram counts subgroup
   points, affine points, or x-orbits. For an odd prime-order group, the
   point at infinity is excluded and each nonzero affine x typically represents
   two signs; after the negation quotient the mean is based on the number of
   x-orbits, not `N/M`. Use one cardinality symbol consistently and report
   infinity, affine, and orbit counts separately.
2. Define the factor and modulus exactly. State the integer representative,
   `M=floor(p^(1/3))`, strictness and tie rules, and void cells for `M<2`.
   If F or another downstream set is used, specify its selection before the
   histogram and do not let the quotient convention alter the sample size
   after the fact.
3. Replace the injection null with matched nulls. Use at least two controls:
   a uniform sample of distinct x-values with the same orbit count, and a
   point-level random injection whose induced multiplicities match the
   `{P,-P}` structure. If the null is intended to model a random curve,
   sample random nonsingular curves and their x-orbit sets instead. State
   whether residues are sampled with or without replacement and quantify the
   finite `p mod M` bin imbalance.
4. Define the max-to-mean statistic and uncertainty. Report all bucket
   occupancies, maximum, mean, variance, empty bins, and the exact ratio using
   the observed population size. One random injection is insufficient for a
   void rule; use independent null draws or an exact occupancy tail bound and
   predeclare how the threshold is applied.
5. Certify the curve cells. Record the curve equation, prime field, ordinary
   and prime-order subgroup certificates, generator/order, cofactor, and the
   enumeration method. Exclude singular or nonordinary cells before choosing
   the smallest qualifying curve, and keep curve selection independent of the
   observed bucket statistic.
6. Preserve the interpretation boundary. A heavy residue is a public
   classification, not an omega or a discrete-log inversion. If a concentration
   appears, measure the cost of identifying, storing, and using the bucket,
   including its expected list size and target membership cost, before
   comparing with rho. A flat histogram only closes this modulus and tested
   curve panel.

## Readiness and disposition

The proposal is a useful low-cost finite control, but its current max-to-mean
claim cannot be evaluated until the orbit population, denominator, and null
distribution are made consistent. The selection rule for the smallest
qualifying curve also needs an anti-selection guard.

Disposition: **retain proposed as a conditional x-modulus concentration
control; do not approve or dispatch as filed.** Repair population and
denominator semantics, matched nulls, curve certification, uncertainty, and
the downstream bucket-use cost. Recheck runnable state, dependencies, and
approval capacity after a complete contract exists.
