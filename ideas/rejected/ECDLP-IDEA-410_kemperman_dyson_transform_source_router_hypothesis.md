# ECDLP-IDEA-410 — Kemperman–Dyson transform source router

## Status and claim labels

- Class: `kemperman_dyson_e_transform_router`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `rejected_scoped_no_public_witness_preserving_e_transform_pivot_or_subgate_transform_tree`
- Cohort: `20260718-v`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired theorem preflight only; `review_required`, unapproved, zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid e-transform identity or critical-pair classification is not an ECDLP break.

## Falsifiable hypothesis

For every restricted signed factor-deck pair `A,B` and endpoint `R`, an endpoint-only pivot rule chooses `e` so that the Kemperman–Dyson transform `A_e=A union (e+B)`, `B_e=(A-e) intersection B` preserves `R in A+B` biconditionally, strictly reduces a charged support potential, and stores compact reversible ancestry. Iterating this support-changing transform through the five decks yields an exact restricted-existence bit; charged `O(log B)` positive-parent/negative-child bisection plus singleton verification then recovers a relation below rho and BSGS.

## Mechanism-new operation

The screened operation is **apply the Kemperman/Dyson union–intersection e-transform to public restricted deck sets, recurse on a strictly reduced critical pair, and reverse the stored transform ancestry after exact-existence bisection**. Unlike a sumset-growth estimate, approximate almost-period, quotient, or solver substitution, the proposed operation changes the two source supports while conserving their total cardinality and would be useful only if a public pivot preserves the particular endpoint biconditionally.

## Assumptions

1. Every signed/all-chart restricted deck is materialized or queried within the frozen setup cap, with exact group-set union, translation, and intersection.
2. A target- and restriction-uniform pivot rule computes `e` without a source representation and proves `R in A+B` if and only if `R in A_e+B_e` at every transform node.
3. A charged potential falls at every node, the complete transform tree and ancestry state are at most `B^(9/4+o(1))`, and the total fresh online transform/restriction sequence is at most `B^(5/4+o(1))`.
4. The final transform state decides exact signed/chart-complete restricted existence; charged `O(log B)` positive-parent/negative-child bisection and singleton verification recover original occurrences.
5. Set construction, pivot search, failed pivots, translations, unions, intersections, transform branches, ancestry, all restriction queries, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`public_restricted_deck_pair | kemperman_dyson_union_intersection_e_transform | exact_target_support_preserving_transform_tree | reverse_ancestry_and_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H673`; any replacement for pair traffic must preserve exact public provenance rather than only aggregate sumset structure.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION`; additive energy without a public exact source return did not promote.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; tested public predicates did not provide an exact source-resolving circuit.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`; explicit source-bearing representations hit materialized cost.
5. `inputs/ledger_inventory.json` — imported `P1476`; exact target support, failed branches, and reusable source-return work must be charged together.

## Closest primary literature

- Kemperman, [On small sumsets in an abelian group](https://doi.org/10.1007/BF02546525), develops the recursive transform method and structural theory for supplied critical pairs.
- Dyson, [A theorem on the densities of sets of integers](https://doi.org/10.1112/jlms/s1-20.1.8), introduces the supplied-set transform behind the union/intersection recursion; it is not an endpoint-only pivot theorem.
- Boothby, DeVos, and Montejano, [A new proof of Kemperman's theorem](https://arxiv.org/abs/1301.0095), gives a modern critical-pair formulation for finite subsets of abelian groups; it does not provide a pivot preserving target nonemptiness for an arbitrarily prescribed endpoint.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies compact endpoint equations but no exact e-transform pivot or reversible finite-deck ancestry.

No checked source gives the required fixed-target biconditional transform tree; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, repeated occurrences, tangent/vertical/infinity cases, exceptional or nonreduced charts, dyadic restrictions, deck-pair schedule, pivot rule, support potential, ancestry encoding, exact predicate, and verifier.
2. Build target-independent deck indices and transform primitives within `B^(9/4+o(1))` without pair-product enumeration or discrete logs.
3. On known-log targets, construct the complete endpoint-only transform tree, decide exact restricted existence, and recover five occurrences by charged `O(log B)` positive-parent/negative-child bisection plus singleton verification and reverse ancestry.
4. Collect at least `B` independent verified rows, charging every failed pivot, branch, negative-child query, ancestry output, dependency, and final tuple; solve factor logs.
5. Reuse unchanged deck indices and pivot rule on fresh scalar-blind `Q+[t]P` targets under arbitrary restrictions.
6. Substitute factor logs, remove `t`, retain every transform-ancestry branch, and verify `[x]P=Q`.
7. Charge set construction, pivot search, translations, unions/intersections, transform recursion, the full restriction sequence, singleton verification, output, rank, logs, descent, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`; the total fresh online transform/restriction/bisection sequence plus singleton verification must be at most `B^(5/4+o(1))`; and promotion needs `lambda<=0.45` and `mu<=0.45`. Here `q` charges every failed pivot and every `O(log B)` positive-parent/negative-child query plus singleton verification, while `o` charges final tuple or direct output. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The e-transform guarantees `A_e+B_e` is a subset of `A+B`, not equality or preservation of a prescribed target. If `R=a_0+b_0`, the sufficient pivot `e=a_0-b_0` retains that witness, but it is derived from the hidden representation; no checked theorem constructs an endpoint-only pivot that preserves target nonemptiness. Covering all public candidates in `A-B` may require `Theta(B^2)` distinct pivots for hash-like decks before five-deck composition and restores the pair-product boundary. Kemperman's recursion applies to critical small-sumset pairs; generic size-`B` subsets of the prime cyclic group can have near-`B^2` pair sumsets and no critical-pair compression. Thus the concrete transform is operation-distinct, but the required fixed-target pivot and compact reversible ancestry remain unconstructed.

## Proof track

Prove an endpoint-only pivot theorem giving a strict potential decrease and fixed-target biconditional under every restriction, bound the complete reversible transform tree, then certify charged bisection and the complete `lambda,mu<=0.45` descent.

## Disproof track

Exhibit an endpoint-only pivot rule that destroys a unique target witness, show that covering the known sufficient witness-derived pivots requires `Omega(B^2)` candidates on a generic family, prove noncritical generic sumsets, or force transform/ancestry state above the caps.

## Positive and negative controls

- Positive: supplied critical pairs with a planted target witness and a supplied witness-preserving pivot must satisfy the transform identity, exact existence bit, reverse ancestry, and singleton verification.
- Negative: identical public pairs with different planted target witnesses requiring different pivots, generic random prime-cyclic decks, noncritical sumsets, repeated occurrences, signed/chart exceptions, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 027/057/340/351/389, explicit pair tables, untransformed sumset membership, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a public fixed-target biconditional pivot, strict transform potential, reversible ancestry, exact signed/chart-complete restricted existence, `1,000` independent rows, `100` blind descents, total transform/bisection caps, and `lambda,mu<=0.45`.
- Falsify on one destroyed target witness, one pivot depending on a hidden summand, `Omega(B^2)` branching, one ancestry collision, cap violation, or either exponent at least `0.50`.
- Correct e-transform identities or critical-pair classifications on supplied toy sets are only controls.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-410/e_transform_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-410/fixed_target_pivot_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-410/restricted_existence_bisection_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-410/cost_analysis.md`

## Interpretation boundary

This rejects the screened fixed-target e-transform router, not Kemperman's critical-pair theory. Every prospective check is toy, heuristic, model-bound, and novelty-unverified; transform correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-410/e_transform_source_obligations.md` and audit every pivot, support update, transform branch, ancestry token, exact restricted-existence bit, positive-parent/negative-child bisection query, and singleton verification for endpoint versus hidden-witness dependence.
