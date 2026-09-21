# ECDLP-IDEA-394 — Weisfeiler–Leman tuple-refinement source quotient

## Status and claim labels

- Class: `combinatorial_refinement`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_wl_refinement_requires_materialized_neighbourhoods_and_colours_do_not_canonically_recover_sources`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; stable toy WL colours or successful graph distinction are not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructible bounded-dimensional Weisfeiler–Leman refinement of partial elliptic relation tuples stabilizes to a compact colour quotient in which a target colour has a restriction-stable canonical lift to one exact occurrence-labelled five-deck source, enabling full blind descent below the frozen gates.

## Mechanism-new operation

The screened operation is **encode partial relation states as tuples, iteratively recolour them by multisets of one-coordinate substitutions, quotient by stable colours, and lift a distinguished colour to factor occurrences**. It differs from generic partition refinement only if substitution-neighbour multisets can be evaluated without materializing the source-state product.

## Assumptions

1. Fixed dimension `k=O(1)` suffices uniformly for all curves, targets, signed strata, and restrictions.
2. Initial colours and refinement multisets are endpoint-computable within the frozen caps.
3. Stable colour equality is source-biconditional rather than merely an isomorphism invariant.
4. One stable colour has a canonical occurrence-labelled lift without enumerating its colour class.
5. State construction, every refinement round, multiset hashing, output, rank, factor logs, blind descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`partial_relation_tuple_structure | bounded_k_WL_refinement | substitution_multiset_colours | stable_colour_quotient | canonical_colour_to_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`; a quotient must satisfy the complete five-source query, rank, and descent gate.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`; serial partial-sum state representations densify beyond the gate.
3. `inputs/ledger_inventory.json` — imported `ECFG-MX-1478`; exact transition composition materializes a dense quadratic object.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact exact source-resolving quotient remains missing.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit substitution neighbourhoods are source edges in another encoding.

## Closest primary literature

- Weisfeiler and Leman, [The reduction of a graph to canonical form and the algebra which appears therein](https://www.iti.zcu.cz/wl2018/pdf/wl_paper_translation.pdf), defines the iterative graph-refinement operation on a supplied structure.
- Cai, Fürer, and Immerman, [An optimal lower bound on the number of variables for graph identification](https://doi.org/10.1007/BF01305232), constructs graph families indistinguishable by bounded-dimensional refinement.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no compact tuple-neighbourhood oracle or colour-to-source section.

No checked source supplies the proposed bounded-dimensional elliptic refinement and exact occurrence lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, tuple vocabulary, initial colours, dimension, update rule, canonicalization, restrictions, masks, and independent verifier.
2. Build target-independent tuple/refinement state within `B^(9/4+o(1))`, without materializing all partial tuples or substitution edges.
3. For known-log targets, refine the restricted structure to stability, identify a source colour, lift one occurrence-labelled five-point tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charging rounds, colour-class output, collisions, ambiguity, and dependent rows; solve and verify factor logs.
5. Apply the unchanged refinement and lift to fresh scalar-blind `Q+[t]P`, charging restrictions, target updates, and rebuilds.
6. Substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge state, refinement rounds, neighbourhood evaluation, colour storage, source lift, output, rank, factor logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

WL refinement compresses a supplied relational structure; it does not create its vertices or adjacency. A one-coordinate substitution multiset over elliptic partial states is the materialized product/transition surface already closed by the ledger. Stable colours are invariants, not witnesses, and bounded-dimensional WL admits indistinguishable structures, so equal colours need not select the same factor tuple. This merges with IDEAs 120, 123, 135, 377, and 383 unless a new endpoint-only neighbourhood oracle and source-biconditional refinement theorem are proved.

## Proof track

Prove a constant-dimensional endpoint-only refinement for every stratum, a stable-colour iff source theorem, a restriction-stable occurrence lift, and complete `lambda,mu<=0.45` bounds.

## Disproof track

Show that one refinement multiset requires enumerating partial states, construct equal-colour elliptic instances with different source fibres, or demonstrate dimension/round/output growth above the caps.

## Positive and negative controls

- Positive: supplied finite structures with known equitable partitions and planted labelled tuples must reproduce stable colours and labels.
- Negative: CFI-style indistinguishable pairs, label permutations, equal-colour/different-source instances, all signed strata, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 120/123/135/377/383, explicit tuple products, partition-refinement backends, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a subgate neighbourhood oracle, source-biconditional stable colours, `1,000` independent rows, `100` blind descents, frozen state/query caps, and `lambda,mu<=0.45`.
- Falsify on one materialized substitution surface, one equal-colour/different-source collision, one missing/spurious lift, unbounded required dimension, or either exponent at least `0.50`.
- A correct toy refinement or graph distinction is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-394/wl_neighbourhood_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-394/colour_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-394/colour_to_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-394/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic WL quotient, not Weisfeiler–Leman refinement. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; refinement correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-394/wl_neighbourhood_obligations.md` and count the distinct partial states touched by one exact refinement round on the smallest nontrivial signed deck.
