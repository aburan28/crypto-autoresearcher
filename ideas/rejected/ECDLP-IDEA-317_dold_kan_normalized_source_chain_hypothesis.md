# ECDLP-IDEA-317 — Dold–Kan normalized source chain

## Status and claim labels

- Class: `homological_representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_dold_kan_requires_source_simplices_and_forgets_labels`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a chain equivalence, normalized complex, relation, or toy lift is not an ECDLP break.

## Falsifiable hypothesis

A public simplicial abelian object built from partial elliptic decompositions has a Dold–Kan normalized chain complex of sub-rho rank whose canonical nondegenerate generators invert to every exact signed factor tuple and support blind descent.

## Mechanism-new operation

The screened operation is **encode partial decompositions as simplices, apply normalized chains to quotient degeneracies, and lift a canonical nondegenerate chain generator back to exact source points**. Degeneracy removal is a precise representation change rather than a generic homology computation. But the simplicial object starts with source-labelled simplices; normalization preserves chain information only up to natural equivalence and does not create preferred point labels. It merges with IDEAs 073, 176, 218, 220, and 234.

## Assumptions

1. A target-independent simplicial abelian source object is constructible from public endpoint data without enumerating factor tuples.
2. Degenerate simplices contain the dominant source redundancy, leaving normalized rank and construction below rho.
3. Every nondegenerate normalized generator has a canonical all-strata inverse to exact signed factor points.
4. Faces, degeneracies, normalization, source output, relation density, rank, factor logs, descent, verification, and memory are charged.
5. The same simplicial grammar and inverse apply to fresh masked targets.

## Semantic fingerprint

`partial_source_simplicial_abelian_object | Dold_Kan_normalized_chains | degeneracy_quotient | canonical_generator_to_factor_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed source-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-edge boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the tested explicit ancestry compression boundary.

## Closest primary literature

- Dold, [Homology of symmetric products and other functors of complexes](https://doi.org/10.2307/1970043), and Kan, [Functors involving c.s.s. complexes](https://doi.org/10.1090/S0002-9947-1958-0131873-8), establish the equivalence between supplied simplicial abelian objects and nonnegative chain complexes.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), does not supply a compact source simplicial object or generator-to-point inverse.

No checked source proves the required endpoint-only constructor, label-faithful normalization, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor decks, signs, source simplices, face/degeneracy maps, normalization, masks, lift convention, and verifier.
2. On known-log endpoints, construct normalized chains without source enumeration, extract exact generators, lift them to signed factor points, and verify relations.
3. Collect independent rows, solve all factor-base logs, and independently verify them.
4. Reuse the identical simplicial construction and lift on fresh `Q+[t]P` targets with no source-labelled basis.
5. Substitute logs, remove masks, retain all chain/lift ambiguity, and return scalar candidates.
6. Accept only `[x]P=Q`, charging construction, ranks, reductions, output, factor logs, descent, verification, and peak memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one normalization/generator/source lift `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All simplices, boundary matrices, reductions, and generator lifts are charged in `a,q,o`. Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

The Dold–Kan equivalence converts a supplied simplicial abelian object; it does not infer that object from its endpoint augmentation. Source-faithful simplices or face maps materialize the hidden ancestry deck, while normalized chains are invariant under basis changes that permute exact point labels. Degeneracy removal can delete redundant syntax but cannot select one tuple from a many-to-one Abel–Jacobi fiber.

## Proof track

Prove a compact endpoint-derived simplicial object, a sub-rho normalized rank theorem, canonical all-strata generator-to-point lifts, sufficient relation rank, reusable factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Construct equal normalized complexes with different point-labelled simplices, show that a face/degeneracy oracle encodes source incidence, or prove source state/output or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied small simplicial abelian group must round-trip through normalized chains with its planted labelled basis retained externally.
- Negative: basis-permuted simplicial models with identical normalized complexes must not yield preferred factor points.
- Baselines: IDEAs 073/176/218/220/234, P1434, explicit chain reduction, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a source-free all-strata round trip, 1,000 verified rows and 100 blind descents per large future toy size, and complete `lambda,mu<=0.45`.
- Falsify if simplices or maps require source labels, if equal-chain/different-source collisions occur, or if state/output or either exponent reaches `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-317/dold_kan_source_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-317/normalized_chain_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-317/independent_dold_kan_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-317/cost_analysis.md`

## Interpretation boundary

This rejects the stated endpoint-to-normalized-source operation only. Correct Dold–Kan conversion, homology, a relation, or a toy source round trip is not a complete ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-317/dold_kan_source_theorem.md` proving a source-free normalized generator lift or an equal-normalized-complex/different-point-source collision.
