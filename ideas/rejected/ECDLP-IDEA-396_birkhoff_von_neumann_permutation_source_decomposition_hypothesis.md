# ECDLP-IDEA-396 — Birkhoff–von Neumann permutation source decomposition

## Status and claim labels

- Class: `polyhedral_decomposition`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_doubly_stochastic_matrix_materializes_source_incidence_and_permutation_decomposition_is_noncanonical`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct toy doubly stochastic decomposition is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructible sparse doubly stochastic matrix encodes all signed partial-source compatibilities, and a Birkhoff–von Neumann decomposition exposes a restriction-stable permutation matrix whose selected entries canonically lift to one exact five-deck relation for complete blind descent below the frozen gates.

## Mechanism-new operation

The screened operation is **normalize endpoint-derived compatibility weights to a doubly stochastic matrix, peel permutation matrices with positive coefficients, select one source-valid permutation, and decode its entries to occurrence-labelled factor points**. It is distinct from matching/transport backends only if the matrix and selected permutation are constructed without explicit source incidence or a post-hoc selector.

## Assumptions

1. Every signed stratum admits a compact endpoint-only nonnegative matrix with exact row and column sums one.
2. Positive permutation support is source-biconditional: at least one component encodes an exact relation and no selected component is spurious.
3. A canonical qualifying component can be found without enumerating a large nonunique decomposition.
4. Restrictions preserve stochasticity and a canonical occurrence-labelled matrix-entry inverse.
5. Matrix construction, scaling, matching/decomposition, coefficient precision, output, rank, factor logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_doubly_stochastic_compatibility_matrix | Birkhoff_von_Neumann_permutation_peeling | canonical_source_permutation | matrix_entry_to_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`; the complete source/descent gate applies to every matrix component.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1431-CANONICAL-ROOT-PRODUCT-NO-PROMOTION`; canonical output traversal still pays source construction.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; exact compatibility matrices retained full source rank.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`; no compact exact source-resolving matrix has been supplied.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; a materialized Cartesian compatibility surface is a no-promotion control.

## Closest primary literature

- Birkhoff, [Tres observaciones sobre el algebra lineal](https://www.scienceopen.com/document?vid=fa429ed1-6420-401f-9c52-ddff427af671), proves the finite-dimensional extreme-point characterization underlying decomposition of a supplied doubly stochastic matrix.
- von Neumann, [A certain zero-sum two-person game equivalent to the optimal assignment problem](https://doi.org/10.1515/9781400881723-010), connects doubly stochastic structure with assignment after the payoff matrix is supplied.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no sparse stochastic compatibility matrix or permutation-to-point inverse.

No checked source supplies the proposed elliptic matrix compiler or canonical source component; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, matrix rows/columns, compatibility weights, normalization, permutation-peeling order, selection rule, restrictions, masks, and verifier.
2. Build target-independent stochastic state within `B^(9/4+o(1))` without materializing the full compatibility matrix or one nonzero per source edge.
3. For known-log targets, update and restrict the matrix, decompose or isolate one supported permutation, decode an occurrence-labelled five-point tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charging normalization failures, spurious components, decomposition length, ambiguity, and dependent rows; solve and verify factor logs.
5. Apply the unchanged matrix compiler, decomposition, and inverse to fresh scalar-blind `Q+[t]P`, charging restrictions and rebuilds.
6. Substitute factor logs, remove `t`, retain all ambiguity branches, and verify `[x]P=Q`.
7. Charge matrix/scaling state, matching or peeling calls, coefficient arithmetic, component selection, source lift, output, rank, factor logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Birkhoff–von Neumann decomposes an already supplied matrix. Populating a nonzero compatibility entry requires the source relation information that the proposal is meant to discover, while scaling does not create it. Decompositions are generally nonunique, and a permutation encodes a perfect matching of rows to columns rather than a five-ary elliptic sum; selecting a valid component is a post-hoc source selector. This merges with IDEAs 143, 212, 231, 321, and 382 unless a compact endpoint-only stochastic matrix with a canonical source component is proved.

## Proof track

Construct a subgate implicit stochastic matrix for every stratum, prove supported permutation iff exact source, prove a restriction-stable canonical component and occurrence lift, and derive complete `lambda,mu<=0.45` bounds.

## Disproof track

Show one nonzero needs a source edge, construct the same stochastic matrix/decomposition support with different occurrence labels, or prove that scaling/decomposition/output exceeds a frozen cap.

## Positive and negative controls

- Positive: supplied rational doubly stochastic matrices with planted permutation decompositions must reproduce exact coefficients and labelled entries.
- Negative: alternative decompositions of one matrix, row/column relabellings, supported permutations unrelated to elliptic sums, all strata, restrictions, and blind targets.
- Baselines: IDEAs 143/212/231/321/382, explicit matching and transport matrices, post-hoc component selectors, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only implicit matrix, source-biconditional supported permutations, `1,000` independent rows, `100` blind descents, frozen state/query caps, and `lambda,mu<=0.45`.
- Falsify on one explicit compatibility entry, one same-matrix/different-source collision, one spurious selected permutation, decomposition above cap, or either exponent at least `0.50`.
- A correct toy decomposition or assignment is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-396/stochastic_matrix_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-396/decomposition_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-396/permutation_to_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-396/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic permutation decomposition, not the Birkhoff–von Neumann theorem. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; decomposition correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-396/stochastic_matrix_source_obligations.md` and classify every proposed nonzero as endpoint-computable or explicit source-incidence advice.
