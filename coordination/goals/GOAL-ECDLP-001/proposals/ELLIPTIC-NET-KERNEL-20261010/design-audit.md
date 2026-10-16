# Elliptic-net hidden-kernel lattice audit

## Audit basis

- Idea: `IDEA-20261009-8d09c0`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KN-TECH-009`, `KN-OPEN-005`, and the existing
  elliptic-net block-zero diagnostic under
  `experiments/EXP-ECDLP-COORD-EXPANSION-001/development/`.

## Mathematical boundary

For a fixed tuple of reduced points, the homomorphism
`Z^r -> <P_1,...,P_r>` has a kernel lattice whose index is the size of its
image. An elliptic-net zero can be a useful way to recognize a kernel member,
but that statement requires a fixed net normalization, good reduction, and
complete exceptional-value semantics. It does not imply that the finite set of
zeros found in a box is already a basis for the full kernel lattice.

The existing block-zero diagnostic is an adjacent representation test with a
separate recurrence gate. It does not validate this proposal's smoothness or
cross-prime mutual-information claims, and its finite observations cannot be
promoted into a general statement about elliptic nets.

## Load-bearing contract repairs

1. Bind the source curves and lifted generators exactly: integral model,
   reduction certificate at every `p` and `q`, generator coordinates, bad
   reduction exclusions, subgroup orders, and the map whose kernel is being
   measured. Define the net normalization and prove the equivalence between
   `W(v) = 0` and the reduced group sum being the identity, including zero and
   denominator cases.
2. Do not reconstruct a full lattice from an unqualified box sample. Either
   compute a certified kernel basis by modular group arithmetic and verify its
   index, or state the finite-box observable as a sample statistic. If HNF is
   used, specify the saturation/completion procedure, the box coverage
   condition, and an independent index certificate. A mismatch can indicate
   an incomplete box or bad net semantics rather than a failure of the lattice
   claim.
3. Define the integer value used for smoothness. State numerator/denominator
   normalization, sign and zero handling, the smoothness bound `B`, repeated
   factors, values equal to zero, and the exact factorization or certification
   cost. Exact net values can grow rapidly with height; the cost of producing
   and factoring them must be charged separately from modular membership.
4. Replace the Dickman comparison with a frozen height and size model. A
   Dickman-type estimate needs the observed log-size distribution and a
   declared smoothness population; it is not determined by the box size alone.
   Use matched random integers or a model calibrated from held-out net values,
   and report the full yield distribution rather than only one ratio.
5. Make the mutual-information experiment statistically identifiable. The
   event `v in Lambda_p` can be extremely sparse, so a plug-in estimator over
   an unstratified box is biased and may have no useful power. Predeclare
   balanced membership sampling or importance sampling, the estimator, bias
   correction, confidence interval, bootstrap unit, and multiple-testing
   correction over the twenty `q` values and all cells. Do not treat a
   nonzero plug-in estimate as a signal without the matched random-lattice
   calibration.
6. Specify the random-lattice null precisely. Matching only the index does not
   match the geometry of a lattice in a finite box or the quotient labels
   induced by the reductions. Use a declared distribution over homomorphisms
   or quotient maps, preserve the same box and membership density, and verify
   estimator calibration on null data generated independently of the net code.
7. Account for cross-prime dependence. The same exact integer `W(v)` is used
   across reductions; exact zeros, shared factors, and CRT-related events can
   correlate `Lambda_p`, `Lambda_q`, and smoothness even under the null. The
   design must separate exact-zero rows, condition or model the dependence,
   and avoid calling independence a theorem.
8. Keep the claim ceiling explicit. A signal in smoothness or mutual
   information would be a finite correlation in this representation, not a
   scalar-recovery method. To support an algorithmic direction it would need a
   target-independent membership/sieving procedure, a below-birthday cost
   model, relation rank and target replay, and independent same-point controls.

## Readiness and disposition

The proposal is proposal-only and has no executable implementation binding.
Its net source, lifted-generator family, smoothness definition, lattice
reconstruction proof, and sparse-event statistical protocol remain open. The
prior block-zero diagnostic is not a substitute for these inputs.

Disposition: **retain proposed as a conditional finite null test; do not
approve or dispatch as filed.** Repair the kernel certificate, finite-box
semantics, smoothness model, sparse-event estimator, cross-prime null, and
charged costs. Recheck runnable state and approval capacity only after a
complete contract exists.
