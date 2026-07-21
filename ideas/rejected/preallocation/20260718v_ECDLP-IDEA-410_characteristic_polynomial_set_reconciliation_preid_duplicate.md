# Pre-ID duplicate draft — characteristic-polynomial set-reconciliation source lift

## Status and claim labels

- Class: `characteristic_polynomial_set_reconciliation`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_extendible_set_sketch_is_query2p1_and_root_recovery_requires_source_payload`
- Cohort: `20260718-v`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired theorem preflight only; `review_required`, unapproved, zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; exact reconciliation of supplied sets is not an ECDLP break.

## Falsifiable hypothesis

For every dyadic restriction, endpoint-only evaluations of characteristic polynomials for the extendible pair-label sets admit a compact rational-difference sketch that decides exact nonemptiness; charged `O(log B)` dyadic bisection plus singleton verification then returns one five-factor relation below rho and BSGS.

## Mechanism-new operation

The screened operation is **form characteristic polynomials of two endpoint-derived extendible-label sets, divide their evaluation sketches, rationally reconstruct the symmetric difference, factor it, and lift a recovered label through the five decks**. This is not a moment-table parameter change: the proposed new step is an exact, restriction-stable reconciliation sketch constructed without first listing either hidden set.

## Assumptions

1. Characteristic-polynomial evaluations of the exact extendible sets are computable from public endpoint data without Query2P1 or enumeration.
2. Signed multiplicities, cancellations, and repeated labels are represented exactly in subgate state.
3. Rational reconstruction and factorization cost, degree, coefficients, and output remain below the frozen caps for every restriction.
4. The sketch decides exact restricted existence; direct occurrence roots are optional because charged `O(log B)` bisection plus singleton verification is sufficient.
5. Sketch construction, evaluations, interpolation, factorization, label lift, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`restricted_extendible_endpoint_sets | characteristic_polynomial_evaluation_ratio | exact_nonempty_bit | dyadic_bisection_singleton_verification | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; an exact public source-fiber generator and target join remain the live requirement.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; source-recoverable transposed generators already meet a materialized cubic boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; exact value sketches did not expose a low public source basis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; materialized source products fail the rank and cost gate.
5. `inputs/ledger_inventory.json` — imported `P1478`; sparse one-transition formulas still lack a compact common-root source operation.

## Closest primary literature

- Minsky, Trachtenberg, and Zippel, [Set reconciliation with nearly optimal communication complexity](https://doi.org/10.1109/TIT.2003.815784), reconstructs differences from characteristic-polynomial sketches when the parties can evaluate their supplied sets.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but not sketches of hidden extendible occurrence sets.

No checked source constructs the proposed endpoint-only exact extendible-set sketch; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, label encoding, restrictions, sketch points, multiplicity convention, reconstruction rule, and verifier.
2. Build target-independent reconciliation state within `B^(9/4+o(1))` without enumerating extendible pair or triple labels.
3. On known-log targets, answer arbitrary exact restricted-existence queries and recover five labels by charged `O(log B)` dyadic bisection plus singleton verification; a direct reconstructed root is only a stronger optional route.
4. Collect at least `B` independent verified rows, charging zero sketches, repeated roots, cancellations, full root output, and dependent rows; solve factor logs.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P` targets under arbitrary dyadic restrictions.
6. Substitute factor logs, remove `t`, retain all reconstruction branches, and verify `[x]P=Q`.
7. Charge sketch construction, probes, reconstruction, factorization, occurrence lift, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The reconciliation protocol assumes each party can evaluate the characteristic polynomial of its own set. Here that set is precisely the hidden collection of labels extendible to a five-term relation, so even one exact evaluation—and therefore even the weakest exact restricted-existence bit—requires Query2P1 or source enumeration. Signed multiplicities can restore `B^3` traffic. Noncanonical roots are not independently fatal because bisection would suffice if the exact predicate existed. This meets IDEAs 053, 105, 121, 199, and 266 at the hidden-set-to-exact-predicate boundary.

## Proof track

Construct an endpoint-only exact sketch evaluator, prove restriction-stable zero/nonzero correctness, recover labels by charged bisection and singleton verification, and certify the complete `lambda,mu<=0.45` descent.

## Disproof track

Reduce one sketch evaluation to Query2P1, exhibit equal retained sketches for restrictions with different existence bits, or prove evaluation/reconstruction traffic or memory above the caps.

## Positive and negative controls

- Positive: two supplied small sets with planted differences and unique labels must reconcile and replay exactly.
- Negative: equal endpoint sets with different repeated occurrences, signed cancellation, empty differences, rare singleton relations, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 053/105/121/199/266, full set tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only exact restricted-existence sketches, charged `O(log B)` bisection and singleton verification, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one hidden-set enumeration or Query2P1 call, one equal-sketch/different-existence collision, missed signed multiplicity, cap violation, or either exponent at least `0.50`.
- Correct reconciliation of supplied toy sets is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-410/sketch_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-410/multiplicity_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-410/restricted_root_lift_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-410/cost_analysis.md`

## Interpretation boundary

This rejects the screened hidden-set reconciliation route, not set reconciliation. Every prospective check is toy, heuristic, model-bound, and novelty-unverified; exact sketch algebra is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-410/sketch_source_obligations.md` and classify every set membership, polynomial evaluation, ratio coefficient, reconstructed root, and occurrence label by endpoint versus hidden-source dependence.
