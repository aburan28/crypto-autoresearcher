# ECDLP-IDEA-386 — Twin-width red-edge contraction source quotient

## Status and claim labels

- Class: `combinatorial`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_red_edges_restate_source_incidences_and_exact_uncontraction_requires_the_hidden_dictionary`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run theorem-preflight only; `review_required`, unapproved, and never dispatchable
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct contraction sequence or toy source replay is not an ECDLP break.

## Falsifiable hypothesis

The exact endpoint-conditioned compatibility graph of signed two- and three-deck partial sums has a publicly constructible bounded-twin-width contraction sequence whose red-edge quotient supports complete five-factor membership and occurrence-labelled source recovery below the P1476/P1434 gates.

## Mechanism-new operation

The screened operation is **repeatedly contract partial-sum vertices with almost equal neighborhoods, retain the red edges that record disagreements, answer a target query on the quotient, and exactly uncontract one accepted quotient path to five signed factor occurrences**. It is mechanism-new only if the contraction sequence and red-edge annotations are derived from endpoints without first materializing the source compatibility edges.

## Assumptions

1. The frozen signed factor decks induce an endpoint-only compatibility graph of twin-width `B^(o(1))`, uniformly over curves, strata, restrictions, and target shifts.
2. A contraction sequence and its red-edge annotations are constructible within `B^(9/4+o(1))` time and state without enumerating the `B^4` terminal-witness surface.
3. Quotient membership is exact: no accepted or rejected five-factor source is changed by contraction.
4. Every accepted quotient witness uncontracts canonically to occurrence-labelled factors under arbitrary prospective restrictions.
5. Sequence construction, red edges, quotient queries, ambiguity, output, rank, factor logs, blind descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`partial_sum_compatibility_graph | twin_width_red_edge_contraction_sequence | exact_target_quotient_query | canonical_uncontraction_to_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; an exact compact source-resolving circuit remains missing.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform public source generation remains unconstructed.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless compression cannot hide one ancestry edge per distinguishable source transition.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit endpoint compatibility edges retain the terminal-witness cost.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; a source-complete materialized product misses the promotion gate.

## Closest primary literature

- Bonnet et al., [Twin-width I: Tractable FO Model Checking](https://arxiv.org/abs/2004.14789), introduces red-edge contraction sequences and bounded-twin-width algorithmics for a supplied graph.
- Bonnet et al., [Twin-width I: Tractable FO Model Checking](https://doi.org/10.1145/3486655), is the journal version and does not construct an implicit elliptic source graph or an occurrence-labelled inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies algebraic endpoint membership but not a bounded-red-degree source quotient.

No checked primary source proves bounded twin-width for these endpoint-conditioned graphs or constructs their exact inverse source map; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the ordinary prime-order curve, `B=N^(1/5)` signed factor decks, partial-sum graph definition, contraction tie-breaks, red-edge semantics, restrictions, masks, and independent verifier.
2. From public factor points, construct the target-independent contraction sequence and quotient within `B^(9/4+o(1))`, without enumerating all compatibility edges or source tuples.
3. For known-log targets, apply the target shift and restrictions to the frozen quotient, decide exact five-factor membership, uncontract one path to five occurrence-labelled factors, and verify their signed group sum.
4. Collect at least `B` independent verified relation rows, charging failed queries, red-edge branching, duplicate rows, and output; solve factor logs and verify every recovered log.
5. Apply the unchanged construction and query algorithm to fresh scalar-blind points `Q+[t]P`, with restrictions selected before outcomes and all target-specific rebuilding charged.
6. Recover a factor tuple, substitute verified factor logs, remove `t`, retain every ambiguity branch, and verify `[x]P=Q`.
7. Charge contraction discovery, red-edge state, quotient queries, uncontraction, output, rank, factor logs, blind descent, verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Twin-width compresses a graph after its adjacency relation and a useful contraction sequence are available. Here an adjacency disagreement is precisely a different source continuation, so red edges preserve rather than remove the hidden incidence dictionary. Generic target shifts and prospective restrictions can give contracted vertices different neighborhoods, forcing red degree, sequence construction, or uncontraction state back toward the explicit source boundary. This therefore merges with IDEAs 123, 135, 338, 377, and 383 unless an endpoint-only bounded-red-degree theorem includes exact source lift.

## Proof track

Prove a uniform bounded-twin-width theorem, give a source-oblivious sequence constructor, establish a restriction-stable quotient/source biconditional, and derive complete measured exponents at most `0.45`.

## Disproof track

Exhibit a prospective target/restriction family whose neighborhood disagreements force polynomial red degree, or two source graphs with the same quotient transcript but different occurrence-labelled witnesses.

## Positive and negative controls

- Positive: supplied bounded-twin-width graphs with known contraction sequences and planted labelled paths must query and uncontract exactly.
- Negative: matched random bipartite graphs, source-label permutations, adversarial target shifts, arbitrary restrictions, all signed strata, and graphs with identical quotients but different source labels.
- Baselines: IDEAs 123/135/338/377/383, explicit edge materialization, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only sequence, maximum red degree `B^(o(1))`, exact source lift, `1,000` independent rows, `100` blind descents, the frozen state/query caps, and `lambda,mu<=0.45`.
- Falsify on one source-dependent sequence choice, red degree or stored disagreement exponent above `9/4` in `B`, one quotient/source collision, one restriction-specific rebuild above the query cap, or either exponent at least `0.50`.
- A correct toy contraction or model-checking result is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-386/twin_width_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-386/red_edge_scaling.json`
- `ideas/artifacts/ECDLP-IDEA-386/quotient_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-386/cost_analysis.md`

## Interpretation boundary

This rejects the screened source-quotient construction, not twin-width theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; quotient correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-386/twin_width_source_obligations.md` and enumerate every red-edge annotation needed to uncontract one exact five-factor witness.
