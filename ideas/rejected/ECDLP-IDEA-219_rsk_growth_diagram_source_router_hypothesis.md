# ECDLP-IDEA-219 — RSK growth-diagram source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_recording_tableau_requires_source_word`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: retired zero-run `review_required` theorem preflight
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a tableau identity, bijection, or recovered planted word is not an ECDLP break.

## Falsifiable hypothesis

Signed factor-base decompositions admit a public matrix/word encoding for which elliptic addition fixes one RSK tableau and the endpoint determines the other through a local growth diagram. Reverse growth would then return exact factor points and relation rows, enabling factor logs and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **endpoint-derived RSK growth followed by local reverse insertion to exact sources**. It merges/rejects because RSK is bijective only for the pair `(P,Q)`: the recording tableau retains insertion order and ancestry. An endpoint invariant can supply at most a shape or aggregate insertion tableau; furnishing the recording tableau or input matrix is the source word/deck itself.

## Assumptions

1. Public `E/F_p`, prime-order `G`, factor base `F` of size `B=N^beta`, and a target-independent ordered alphabet are frozen.
2. The endpoint supplies both tableau data needed for inverse RSK without enumerating source words, matrices, or completion edges.
3. Reverse growth is sign-, repeat-, infinity-, and multiplicity-complete and returns exact point identities.
4. Encoding, tableaux, output, rank, factor logs, masked descent, verification, and memory are fully charged.

## Semantic fingerprint

`signed_factor_word_matrix | elliptic_endpoint_growth_rule | paired_RSK_tableaux | reverse_insertion_to_exact_points | factor_logs | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the public source-fiber generation gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact-source predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the arithmetic source-generator boundary.
4. `inputs/ledger_inventory.json` — imported `P1477`, the dense serial-state control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry floor.

## Closest primary literature

- Knuth, [Permutations, matrices, and generalized Young tableaux](https://doi.org/10.2140/pjm.1970.34.709), proves the matrix-to-paired-tableaux correspondence.
- Schensted, [Longest increasing and decreasing subsequences](https://doi.org/10.4153/CJM-1961-015-3), supplies the insertion/recording correspondence for permutations.
- Fomin, [Schensted algorithms for dual graded graphs](https://emis.de/ft/43641), develops local growth-diagram rules for supplied paths.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives the elliptic relation baseline, not an endpoint recording tableau.

No checked source derives the missing tableau from an elliptic endpoint. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the factor alphabet, word/matrix encoding, local growth rule, endpoint tableau, inverse, masks, and verifier.
2. For known endpoints, derive paired tableaux without listing source words and reverse every accepted growth path to exact signed points.
3. Verify each elliptic row, preserve multiplicity, and reject any tableau with incomplete or ambiguous source output.
4. Collect full rank, solve and verify every factor-base logarithm.
5. Apply the unchanged growth rule to fresh `Q+[t]P`, reverse all sources, substitute factor logs, and subtract `t`.
6. Accept only `[x]P=Q`, charging preprocessing, tableau state, output, rank, descent, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. With setup `N^a,N^a_m`, reciprocal base/target densities `N^delta,N^delta_t`, paired-tableau construction plus exact inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

The input matrix, recording tableau, and every reverse branch are charged. Promotion requires both exponents at most `0.45`.

## Likely fatal obstruction

RSK moves provenance rather than deleting it: `P` alone or the common shape does not determine the input; `Q` is precisely the recording data needed to undo insertion. Source-order quotienting still leaves point identities and multiplicities. Computing a source-complete `Q` from the endpoint materializes the missing completion graph or an equivalent `B^m` dictionary.

## Proof track

Derive a local elliptic growth rule whose endpoint boundary determines both tableaux and prove exact all-source reverse insertion with `lambda,mu<=0.45`.

## Disproof track

Construct two distinct signed source matrices with the same endpoint-supplied tableau data, prove the recording tableau carries source entropy, or reduce construction to explicit source enumeration.

## Positive and negative controls

- Positive control: planted words with both RSK tableaux supplied and exact reverse insertion verified.
- Negative controls: fixed shape only, insertion tableau only, shuffled recording tableaux, plactic/crystal/Tamari normal forms (IDEA-188/190), source dictionaries, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires target-independent endpoint tableau construction, 100% exact-source recall, zero false words, state and output exponents at most `0.45`, and complete `lambda,mu<=0.45`. Needing the recording tableau/source matrix or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-219/rsk_endpoint_growth_theorem.md`
- Prospective collision set: `ideas/artifacts/ECDLP-IDEA-219/tableau_collision_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-219/independent_rsk_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-219/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected algorithm analysis. Finite checks would be toy and projections heuristic and model-bound. Correct RSK inversion on supplied tableaux, a valid relation, or a toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-219/rsk_endpoint_growth_theorem.md` proving that an elliptic endpoint determines the recording data without a source word, or preserving a same-endpoint/same-visible-tableau collision.
