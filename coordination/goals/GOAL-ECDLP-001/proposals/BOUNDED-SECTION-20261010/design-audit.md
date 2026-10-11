# Bounded-height prescribed-fibre section audit

## Audit basis

- Idea: `IDEA-20261009-581f5d`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: the E1 surface-construction dependency, the E4 height/
  covering dependency, `KN-TECH-06bb4e` face F5, and `KR-RHO-13bf67`.

## Scientific boundary

The proposal asks whether a bounded-height section through a prescribed fibre
point can be found cheaply on a selected elliptic surface. That is a legitimate
open measurement, but the filing currently conflates four different objects:
the section-finding system, specialization at the fibre, relation collection,
and the final ECDLP cost. A section solver result is not an ECDLP result unless
the reductions are shown to produce certified, novel relations in the declared
subgroup and the target path is replayed end to end.

## Load-bearing contract repairs

1. Bind the surface and fibre before any solver run: base field, explicit
   Weierstrass model over `F_p(t)`, Euler/conductor data needed for the height,
   fibre parameter `t_0`, nonsingularity certificate, Mordell-Weil rank and
   generators, and the exact specialization map to the target curve. E1's
   existence of a surface or a high-rank fallback is not a substitute for
   these per-cell inputs.
2. Define the section object and degree parameter exactly. State the allowed
   polynomial/rational function denominators, height bound `H`, degree `d`,
   coefficient field, leading-coefficient conventions, and all exceptional
   sections. The claim that the system has about `1.5 d` variables and one
   solution needs a derivation for the selected model; dimension counting alone
   does not control dependencies, singular solutions, or degree of regularity.
3. Separate planted recovery from target solving. An oracle or planted section
   proves only that the encoding and solver can recover a supplied witness.
   For the target arm, freeze one unseen target per cell, bind its source
   receipt, and report whether the solver found a section, whether its
   specialization equals the target, and the complete replay cost.
4. Define what a relation is. Sections through the identity or through a
   prescribed point must be converted into an explicit relation over the
   certified factor base or generator basis. Report relation rank novelty,
   duplicate/conjugate handling, failed specializations, and the cost of
   relation collection, sparse linear algebra, target solve, and verification.
   The statement that `r + 1` section solves give the ECDLP is not established
   by the current proposal.
5. Freeze the degree from the E4 record before solver tuning. If E4 has not
   produced a committed, measured covering contract, this item is not ready
   for approval. A fallback to unconstrained surfaces is a different
   experiment and must not be silently substituted for the prescribed-fibre
   question.
6. Make the structured-system control comparable. Match variable count,
   polynomial degrees, coefficient distribution, planted-witness treatment,
   preprocessing, solver version, memory limit, and stopping rule. Record
   degree of regularity and first-fall degree from the actual systems; a random
   dense control cannot by itself certify that the structured system has no
   useful algebraic representation.
7. Correct the cost claim. A threshold such as `p^0.45` across finite
   parameters is descriptive until it is tied to a preregistered fit, one
   unseen same-point target, matched rho with the same group/order, and full
   phase sums. Include memory, failed attempts, parameter-search cost, and
   solver startup/preprocessing; abort rules must be recorded as infrastructure
   outcomes rather than mathematical failures.
8. State inference limits. A solver success at several small field sizes can
   establish only the measured section and end-to-end costs. It cannot establish
   an asymptotic exponent, a generic advantage, or a new ECDLP algorithm
   without a scale-appropriate transfer argument and independent replay.

## Readiness and disposition

The filed record is proposal-only, has no executable experiment contract, and
depends on E1/E4 inputs whose exact committed readiness is not supplied here.
Its compute estimate is high, while the repository's approval-capacity rule
also requires a ready contract and available headroom before approval. “Reuse”
of solver tooling is not an execution binding.

Disposition: **retain proposed as an open flagship measurement; do not approve
or dispatch as filed.** A successor contract must bind a concrete surface and
fibre, exact section equations and height, relation-rank and target metrics,
one unseen target with a matched rho baseline, structured/random controls,
complete cost accounting, and `execution_state: ready`. Recheck dependencies
and approval capacity only after those repairs exist.
