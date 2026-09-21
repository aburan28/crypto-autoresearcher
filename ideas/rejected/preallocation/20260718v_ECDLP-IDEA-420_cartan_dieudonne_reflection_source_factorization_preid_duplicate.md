# Pre-ID duplicate draft — Cartan–Dieudonné reflection source factorization

## Status and claim labels

- Class: `cartan_dieudonne_reflection_factorization`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_supplied_orthogonal_factorization_has_no_endpoint_representation_or_deck_reflection_dictionary`
- Cohort: `20260718-v`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired theorem preflight only; `review_required`, unapproved, zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; reflection factorization of a supplied orthogonal map is not an ECDLP break.

## Falsifiable hypothesis

There is a compact endpoint-computable, scalar-blind orthogonal representation of the prime-order curve group in dimension below the frozen state gate such that each signed factor-base occurrence has a public reflection dictionary and each restricted five-term relation is biconditional with a bounded reflection product. Cartan–Dieudonné factorization then decides exact restricted existence; charged `O(log B)` bisection plus singleton verification recovers a relation below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile curve points into a nondegenerate orthogonal representation, factor the endpoint transformation into at most the representation dimension many hyperplane reflections, constrain five factors through the public deck-reflection dictionary, and use exact factorability as a restriction predicate**. The required new operation is a compact scalar-blind orthogonal representation with an exact finite-deck reflection dictionary, not a generic linear solver.

## Assumptions

1. The bilinear space and representation matrices are computed for arbitrary points without discrete logs, source enumeration, or a regular-representation-sized construction.
2. The representation is faithful enough that exact signed five-term elliptic equality is reflected by matrix products on every chart and restriction.
3. A public deck-reflection dictionary and exact factorability predicate fit setup/state `B^(9/4+o(1))` and the total online `B^(5/4+o(1))` cap.
4. Charged `O(log B)` positive-parent/negative-child bisection plus singleton verification recovers occurrences; a canonical reflection factorization is optional.
5. Representation construction, dimension, matrix entries, form arithmetic, reflection factorization, dictionary membership, all restriction queries, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`prime_order_curve_group | compact_scalar_blind_orthogonal_representation | cartan_dieudonne_reflection_factorization | exact_restricted_factorability_and_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the open frontier requires exact restricted existence from public state.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; representation dimension and preprocessing are charged.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; public predicates did not yield an exact source-resolving representation.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; exact public matrices did not expose a low faithful factor state.
5. `inputs/ledger_inventory.json` — imported `P1479`; low-dimensional public features do not contain factor orientation.

## Closest primary literature

- Fuller, [A constructive proof of the Cartan–Dieudonné–Scherk theorem in the real or complex case](https://doi.org/10.1016/j.jpaa.2010.08.002), factors a supplied generalized orthogonal matrix into a minimal number of generalized Householder reflections in its stated real/complex scope.
- Rodríguez-Andrade et al., [An algorithm for the Cartan–Dieudonné theorem on generalized scalar product spaces](https://arxiv.org/abs/1011.1027), gives a supplied-matrix constructive control over generalized real scalar-product spaces. Neither checked source proves the proposed finite-field endpoint compiler; the characteristic-not-two, nondegenerate finite-field extension remains an unsupplied theorem obligation here.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives x-coordinate existential equations but no compact orthogonal representation, deck-reflection dictionary, or exact signed all-chart predicate.

No checked source constructs the proposed finite-field endpoint representation and restriction predicate; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, all charts, restrictions, field/form, representation compiler, reflection convention, deck dictionary, factorability predicate, and verifier.
2. Build target-independent representation matrices and dictionary state within `B^(9/4+o(1))` without discrete logs, regular-representation dimension, or source-product enumeration.
3. On known-log targets, answer exact signed/chart-complete restricted factorability queries and recover five labels by charged `O(log B)` positive-parent/negative-child bisection plus singleton verification.
4. Collect at least `B` independent verified rows, charging reflection branches, dictionary tests, negative child queries, dependencies, and final tuple output; solve factor logs.
5. Reuse unchanged representation/dictionary state on fresh scalar-blind `Q+[t]P` targets.
6. Substitute factor logs, remove `t`, retain all reflection branches, and verify `[x]P=Q`.
7. Charge representation construction, matrix/form arithmetic, factorization, dictionary tests, the full restriction sequence, singleton verification, output, rank, logs, descent, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`; the total fresh online restriction/bisection sequence plus singleton verification must be at most `B^(5/4+o(1))`; and promotion needs `lambda<=0.45` and `mu<=0.45`. Here `q` charges every `O(log B)` positive-parent/negative-child query and singleton verification, while `o` charges final tuple or direct output. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Cartan–Dieudonné starts from a supplied orthogonal transformation and only factors that matrix. It constructs neither an endpoint-computable faithful representation nor the deck-reflection dictionary; those are precisely the orientation and source-incidence maps needed for ECDLP. The regular representation is a tautological dimension-`N` baseline, not a lower bound: small faithful orthogonal representations can exist over suitable coefficient fields, with dimension depending on root-of-unity arithmetic. Even for a supplied representation, arbitrary and nonunique reflections need not correspond to deck elements, so exact restricted dictionary factorability is the original source-incidence problem. This endpoint representation to supplied factor dictionary flow is already owned by IDEAs 075, 167, 229, and 398; the theorem substitution is not mechanism-new.

## Proof track

Construct a compact public finite-field orthogonal representation and deck dictionary, prove exact signed/chart-complete restricted factorability, then certify charged bisection and the complete `lambda,mu<=0.45` descent.

## Disproof track

Show the endpoint compiler is a DLP transfer/orientation map, exhibit equal retained matrix state for restrictions with different existence bits, or show dictionary/factorability/bisection cost above the caps; dimension `N` applies only to the regular-representation baseline.

## Positive and negative controls

- Positive: supplied low-dimensional orthogonal matrices with planted deck reflections must return correct positive-parent/negative-child factorability bits and a verified singleton.
- Negative: the dimension-`N` regular-representation baseline, small faithful representations without a deck dictionary, small nonfaithful quotients, nonunique arbitrary reflection factors, repeated/isotropic vectors, signed chart exceptions, restrictions, and blind targets.
- Baselines: IDEAs 075/167/202/229/398, explicit regular representations, supplied reflection dictionaries, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a compact endpoint-only scalar-blind representation, exact signed/chart-complete restricted factorability, `1,000` independent rows, `100` blind descents, total bisection/query caps, and `lambda,mu<=0.45`.
- Falsify on one hidden scalar/discrete log, a source-bearing representation or dictionary, one equal-state/different-existence collision, cap violation, or either exponent at least `0.50`; an order-`N` regular representation is a cost failure but not a universal dimension theorem.
- Correct factorization of a supplied toy matrix is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-420/reflection_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-420/representation_dimension_no_go.md`
- `ideas/artifacts/ECDLP-IDEA-420/restricted_existence_bisection_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-420/cost_analysis.md`

## Interpretation boundary

This rejects the screened reflection-factorization source route, not Cartan–Dieudonné. Every prospective check is toy, heuristic, model-bound, and novelty-unverified; supplied-matrix factorization is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-420/reflection_source_obligations.md` and audit representation construction/dimension, the deck-reflection dictionary, exact restricted factorability, positive-parent/negative-child bisection, and singleton verification.
