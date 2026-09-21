# ECDLP-IDEA-281 — MacWilliams-Krawtchouk complete-weight source inversion

## Status and claim labels

- Class: `representation_changing`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_weight_transform_preserves_aggregate_spectrum_not_source_labels`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a weight enumerator, Krawtchouk coefficient, valid relation, recovered composition, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

ECDLP source tuples can be encoded as words of an endpoint-defined linear or additive code whose complete weight enumerator is compactly recoverable.  Applying the MacWilliams/Krawtchouk transform to a tractable dual code and inverting the endpoint slice would identify the exact source word and return its factor points for relation collection and fresh-target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode source tuples as codewords, compute a dual complete-weight spectrum, apply the MacWilliams/Krawtchouk transform, and invert an endpoint-conditioned coefficient to an exact source word**.  This is a representation change from algebraic fibers to coding spectra, not a solver swap or explicit large-prime table.  MacWilliams identities transform weight enumerators, which aggregate words by Hamming weight or symbol composition; they do not invert a coefficient to a labelled codeword.  A complete enumerator refined enough to retain positions or source pairings has monomial/state size tracking the word/source deck, while a compact symmetric enumerator identifies many tuples.  Once code construction, enumerator size, coefficient output, and word-to-factor return are charged, the proposal merges with character transforms, aggregate statistics, and materialized-source negatives.

## Assumptions

1. Public source equations and each endpoint canonically define a linear/additive code and dual without enumerating source tuples.
2. The dual complete weight enumerator or sufficient transformed coefficients are computable below rho on every endpoint stratum.
3. An endpoint-conditioned transformed coefficient canonically decodes one exact signed factor tuple rather than only its weight or symbol composition.
4. Code and dual construction, alphabets, enumerator terms, transforms, coefficient extraction, word output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | endpoint_source_code | dual_complete_weight_enumerator | MacWilliams_Krawtchouk_transform | exact_source_word_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `P1477`, the aggregate-invariant-to-exact-source return boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the invertible transform without source-label promotion.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the shared row statistic that preserves no endpoint-selected source.
5. `inputs/ledger_inventory.json` — imported `ECFG-H643`, the compressed spectral representation and inversion hypothesis.

## Closest primary literature

- MacWilliams, [A theorem on the distribution of weights in a systematic code](https://doi.org/10.1002/j.1538-7305.1963.tb04003.x), proves the weight-distribution transform relating a linear code and its dual that motivates the proposed inversion.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations whose factor tuples would have to be encoded and recovered.

No checked source turns a MacWilliams/Krawtchouk spectrum into a labelled source-word decoder for generic ECDLP fibers or gives complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the finite-field instance, source equations, code compiler, alphabet and coordinate ordering, dual construction, transform convention, factor base, masks, and verifier.
2. Build endpoint-defined codes for known-log relations and compute the complete dual spectra and transformed endpoint coefficients without enumerating source words.
3. Invert every accepted coefficient to all compatible labelled words and map each retained word to exact signed elliptic-curve factor points.
4. Verify the resulting relations, collect independent rows, solve every factor log, and verify all recovered logs.
5. Apply the identical frozen code, dual-spectrum, transform, and word-return pipeline to fresh masked targets `Q+[t]P` without target-specific tuning.
6. Retain every compatible word, return a complete factor decomposition or scalar residue, remove the mask, and verify the reconstructed endpoint.
7. Accept only exact `[x]P=Q`, charging code construction, dual state, enumerator terms, transform coefficients, word ambiguity, failed returns, rows, factor logs, fresh-target descent, verification, and live memory.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one code/enumerator/transform/word-return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, enumerator or word output be `N^o`, coefficient-to-word ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every code coordinate, alphabet symbol, generator/check entry, dual word, enumerator monomial, Krawtchouk coefficient, compatible word, failed return, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

The MacWilliams identity is an invertible transform between aggregate enumerators, not between an endpoint and an individual word.  Ordinary weight enumerators collapse all words of equal weight, and complete weight enumerators still collapse position permutations with the same symbol composition.  Refining variables by position and factor label can restore injectivity only by turning the enumerator into the full source-word generating function.  The dual may make some coefficients easier to compute, but transforming them cannot recover labels that the enumerator discarded or evade the output required to list compatible source words.

## Proof track

Construct a target-uniform compact source code whose sub-rho dual spectrum remains injective on labelled factor tuples, prove exact all-strata coefficient-to-word return, and certify both complete exponents at most `0.45`.

## Disproof track

Exhibit distinct source tuples with the same complete-weight data, prove injective refinement/enumerator/output at least `N^0.50`, show the code or endpoint slice imports source labels, demonstrate fresh-target ambiguity, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small linear code with its labelled word list, dual enumerator, and independently checked MacWilliams transform.
- Negative controls: codes with distinct words of equal weight/composition, coordinate permutations, aggregate-only Krawtchouk spectra, position-refined materialized enumerators, transposed full-rank transforms, random endpoint slices, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-faithful compact code and transform of exponent at most `0.45`, exact all-strata coefficient-to-word and factor return, full row rank and verified factor logs, blind fresh-target descent, and complete `lambda,mu<=0.45`.  Weight/composition collisions, source-labelled refinements, enumerator/word/output/state at least `N^0.50`, missing fresh-target return, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-281/macwilliams_source_inversion_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-281/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-281/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-281/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative conservative representation-changing proposal.  Every finite code transform would be toy and projections heuristic and model-bound.  A correct enumerator identity, transformed coefficient, valid relation, or recovered toy word does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-281/macwilliams_source_inversion_theorem.md` proving compact label-injective spectrum inversion or the aggregation/refinement-size/source-output obstruction.
