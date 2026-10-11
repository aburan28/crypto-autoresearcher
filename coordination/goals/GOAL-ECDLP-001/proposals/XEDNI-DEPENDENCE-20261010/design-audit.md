# Xedni fitted-lift dependence design audit

## Audit basis

- Idea: `IDEA-20261009-321a1d`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KN-LIT-020`, `KN-LIT-021`, `KR-IC-cd159a`, and the
  function-field Xedni findings.

## Scientific boundary

The proposed experiment is a possible finite replication of the Xedni
negative-control literature, but “dependence of a fitted k-tuple” is not yet
an observable. The curve-fitting rule, lift distribution, rank certification,
relation search region, and distinction between a height-pairing numerical
signal and an exact group relation must all be fixed. A low observed rate on a
selected family would close only that search procedure and parameter panel.

## Load-bearing repairs

1. Define the fitted family. State what is sampled over `F_p`, how each point
   is lifted to characteristic zero, which coefficients are fitted for each
   `k`, and whether the resulting curve is a single curve or a parameterized
   family. For `k >= 3`, a curve through the points is generally not unique;
   the selection rule and coefficient-height distribution are part of the
   experiment.
2. Match the control distribution. The unfitted random-lift control must
   match fitted curves on discriminant/conductor scale, good reduction,
   torsion, point heights, and rank-certification method. Otherwise a
   dependence-rate difference may measure curve-family selection rather than
   Xedni fitting.
3. Define dependence exactly. State whether a relation means an equality in
   `E(Q)`, a relation modulo torsion, a bounded integer relation among the
   supplied points, or a rank drop in a saturated Mordell--Weil lattice.
   Numerical height-pairing determinants are screening signals only; every
   candidate needs an exact group-law and coefficient certificate.
4. Bound the relation search. Give the coefficient box, basis of the relation
   lattice, saturation/index checks, precision and exact-arithmetic fallback.
   The claim that every found relation has `|c_i| <= 2` is not meaningful
   unless the search would detect larger coefficients with known probability.
   Report missed-relation and false-positive rates on planted relations.
5. Separate rank intervals from exact ranks. A rank bound or a failed descent
   does not prove independence. Record exhibited independent points, height
   matrices, descent upper/lower bounds, unresolved Tate--Shafarevich and
   saturation status, and classify censored trials without treating them as
   zero-dependence observations.
6. Make the probability claim finite. Specify the exact denominator after
   discarding singular, failed-fit, and unresolved cells; use binomial or
   beta-binomial intervals for 10,000 trials; and predeclare correction for
   the three `k` arms. A threshold of `10^-3` needs enough successful,
   independently sampled trials and a complete failure accounting.
7. Include positive and negative instrument controls. Plant a relation with
   known coefficients, include sign/torsion relations, and run curves with a
   certified independent basis. Require exact recovery of the planted case
   before interpreting a low natural rate.
8. Keep the cryptanalytic boundary explicit. An exact relation among lifted
   points is useful only if it supplies independent equations for a target
   ECDLP and its construction/verification costs are charged. This proposal
   measures a fitted-lift dependence rate, not an attack or an asymptotic
   impossibility result.

## Readiness and disposition

The Xedni control has a plausible negative-control role, but the current
contract does not define the fitted curve distribution, exact dependence
event, relation-search completeness, or censoring policy. The published
negative result it references does not substitute for those finite controls.

Disposition: **retain proposed as a conditional Xedni dependence control; do
not approve or dispatch as filed.** Repair the fitted-family sampler, matched
control, exact relation certificate, rank intervals, finite probability model,
and planted positive controls. Recheck runnable state, dependencies, and
approval capacity after a complete contract exists.
