# Pre-ID duplicate draft — Steinitz bounded-partial-sum source automaton

## Status and claim labels

- Class: `steinitz_bounded_partial_sum_automaton`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_steinitz_norm_bound_is_not_finite_state_and_witness_ordering_presupposes_source`
- Cohort: `20260718-v`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired theorem preflight only; `review_required`, unapproved, zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid Steinitz reordering of supplied vectors is not an ECDLP break.

## Falsifiable hypothesis

The five signed factor decks admit an endpoint-computable, scalar-blind lift to bounded vectors of fixed dimension in a torsion-free normed space such that exact elliptic zero sums are biconditional with zero vector sums. Steinitz reordering then bounds every partial sum, enabling a subgate automaton to decide exact nonemptiness for every dyadic restriction; charged `O(log B)` bisection plus singleton verification recovers a relation below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift prime-cyclic deck elements to bounded torsion-free vectors, apply Steinitz reordering to confine all partial sums to a bounded region, run a bounded-state partial-sum dynamic program, and use its exact restricted-existence bit for self-reduction**. The required new operation is a faithful bounded scalar-blind lift that converts modular elliptic addition into bounded ordinary-vector addition without hidden carries.

## Assumptions

1. A public fixed-dimensional bounded-vector lift is computable for arbitrary group points without discrete logs or source enumeration.
2. The lift preserves and reflects all signed five-term sums on every chart and dyadic restriction.
3. The bounded region is intersected with a proved discrete bounded-precision lattice with a charged minimum separation, so its exact state cardinality is at most `B^(9/4+o(1))`; total online restriction work is at most `B^(5/4+o(1))`.
4. The automaton decides exact signed/chart-complete restricted existence; charged `O(log B)` positive-parent/negative-child bisection and singleton verification recover labels.
5. Lift construction, dimension, coordinate range, carries, ordering, states, transitions, all bisection queries, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`prime_cyclic_deck_points | scalar_blind_bounded_torsion_free_lift | steinitz_reordered_partial_sums | exact_bounded_state_existence_automaton_and_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the live frontier requires a public exact restricted source-fiber operation.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; coordinate expansion and preprocessing state must be charged.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; public coordinate predicates did not yield an exact source-resolving circuit.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; no compact faithful nonlinear lift has been established.
5. `inputs/ledger_inventory.json` — imported `P1479`; public low-dimensional features do not contain the hidden additive orientation.

## Closest primary literature

- Steinitz, [Bedingt konvergente Reihen und konvexe Systeme](https://doi.org/10.1515/crll.1913.143.128), gives bounded partial-sum reorderings for supplied bounded vectors summing to zero.
- Grinberg and Sevastyanov, [The value of the Steinitz constant](https://doi.org/10.1007/BF01086559), sharpens finite-dimensional bounds but still starts from explicit vectors in a torsion-free space.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives x-coordinate existential equations but no faithful bounded scalar-blind vector lift for the exact signed all-chart predicate.

No checked source supplies the proposed lift or bounded exact restriction automaton; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, all charts, restrictions, vector lift, norm, dimension, Steinitz rule, automaton state, transition convention, and verifier.
2. Build target-independent lifted decks and bounded-state transition structure within `B^(9/4+o(1))` without discrete logs, hidden scalar coordinates, or source-product enumeration.
3. On known-log targets, answer exact signed/chart-complete restricted-existence queries and recover five labels by charged `O(log B)` positive-parent/negative-child bisection plus singleton verification.
4. Collect at least `B` independent verified rows, charging carry branches, state output, negative child queries, dependent rows, and final tuple output; solve factor logs.
5. Reuse unchanged lift and automaton on fresh scalar-blind `Q+[t]P` targets under arbitrary restrictions.
6. Substitute factor logs, remove `t`, retain every lift/carry branch, and verify `[x]P=Q`.
7. Charge lift construction, dimension/range, ordering, automaton transitions, the full restriction sequence, singleton verification, output, rank, logs, descent, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`; the total fresh online restriction/bisection sequence plus singleton verification must be at most `B^(5/4+o(1))`; and promotion needs `lambda<=0.45` and `mu<=0.45`. Here `q` charges every `O(log B)` positive-parent/negative-child query and singleton verification, while `o` charges final tuple or direct output. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Steinitz only reorders an already supplied zero-sum family, so selecting the useful order presupposes the hidden witness. Its norm bound is not a finite-state theorem: a bounded region of a real or rational normed space can contain continuously or arbitrarily many exact states unless a discrete bounded-precision lattice, separation bound, and word-size analysis are supplied. For the fixed five-term arity, the triangle inequality already bounds every ordinary partial sum by `5M`, so Steinitz does not itself compress the search. A nontrivial homomorphism from the prime cyclic group to a torsion-free additive group is zero; a set-specific nonlinear lift is not ruled out by that fact, but it must separately prove the signed five-sum biconditional, modular carries, and finite continuation-equivalence quotient. These are the same bounded-state/source-compiler obligations recorded in IDEAs 027, 120, 198, 355, and 397, so the draft is a pre-ID semantic merge rather than a mechanism-new record.

## Proof track

Construct a public bounded scalar-blind lift, prove an all-chart signed five-sum biconditional and Steinitz state bound under every restriction, then certify charged bisection and the complete `lambda,mu<=0.45` descent.

## Disproof track

Show the Steinitz ordering requires the hidden tuple, exhibit arbitrarily many reachable exact states or unbounded denominator precision inside the same norm bound across the family, find equal retained states for restrictions with different existence bits, or show carry/dimension/state or total bisection work above the caps.

## Positive and negative controls

- Positive: supplied bounded integer vectors with planted zero sums must reorder, decide positive-parent/negative-child restrictions, and recover a verified singleton.
- Negative: different zero-sum witnesses requiring different reorderings, dense rational states inside one bounded ball, modular wrap pairs with equal ordinary summaries, hidden scalar-coordinate controls, carry-growing families, signed chart exceptions, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 027/166/198/355/397, explicit scalar lifts, full modular dynamic programming, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a public fixed-dimensional bounded scalar-blind lift, exact signed/chart-complete restricted existence, `1,000` independent rows, `100` blind descents, total bisection/query caps, and `lambda,mu<=0.45`.
- Falsify if the ordering presupposes a witness, if the bounded region lacks a discrete finite-state/separation proof, on one hidden discrete log/scalar coordinate, one equal-state/different-existence collision, unbounded carry/dimension, cap violation, or either exponent at least `0.50`.
- Correct Steinitz reordering on supplied toy vectors is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-410/steinitz_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-410/bounded_lift_no_go.md`
- `ideas/artifacts/ECDLP-IDEA-410/restricted_existence_bisection_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-410/cost_analysis.md`

## Interpretation boundary

This rejects the screened bounded-lift automaton route, not Steinitz's lemma. Every prospective check is toy, heuristic, model-bound, and novelty-unverified; reordering correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-410/steinitz_source_obligations.md` and audit the lift, modular carries, exact restricted-existence biconditional, positive-parent/negative-child bisection, and singleton verification for endpoint versus hidden-scalar dependence.
