# ECDLP-IDEA-371 — Jeż recompression source grammar

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_elliptic_sum_is_not_a_free_monoid_word_equation`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; compressing a supplied word equation or witness word is not an ECDLP break.

## Falsifiable hypothesis

Elliptic factor-base decompositions admit an endpoint-only word-equation encoding on which pair/block recompression constructs a compact solution grammar and returns one exact relation tuple within the P1553 gates.

## Mechanism-new operation

The screened operation is **encode admissible factor sequences as a word equation, repeatedly compress adjacent pairs and blocks, and expand one solution grammar into a labelled elliptic tuple**. It is distinct only if the equation is built from endpoints without embedding a source word, group-law equality is preserved biconditionally, the grammar supports arbitrary source restrictions, and expansion does not enumerate the solution fibre.

## Assumptions

1. Elliptic sum equality has a faithful free-monoid word-equation encoding with subgate size.
2. Pair/block compression is independent of unknown source ordering and retains a compact nonempty-solution grammar.
3. Deck restrictions and target translations update the equation/grammar below the fresh-query gate.
4. A grammar decision expands one exact signed tuple on every distinct, repeated, singular, infinity, coloured, and ambiguous stratum.
5. Encoding, equation solving, grammar construction, updates, expansion, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_endpoint_word_equation | pair_block_recompression | compressed_solution_grammar | exact_factor_word_to_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact representation must still expose a source-resolving section.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; public source-fibre generation and target batching remain the missing operations.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; embedding adjacent source symbols reproduces explicit incidence advice.
4. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; compression after an exact source stream exists is only a control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`; a group-law reparameterization preserved the original inversion burden.

## Closest primary literature

- Jeż, [Recompression: A Simple and Powerful Technique for Word Equations](https://doi.org/10.1145/2743014), solves equations in free monoids through pair and block compression.
- Plandowski, [Satisfiability of word equations with constants is in PSPACE](https://doi.org/10.1145/800057.808715), bounds the supplied word-equation problem but does not create an elliptic source equation.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), expresses unordered abelian group addition through polynomial constraints, not free-monoid concatenation.

No checked source supplies a faithful subgate encoding and exact source section; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, point alphabet, equation encoding, compression schedule, deck restrictions, target masks, and verifier.
2. Build a target-independent endpoint equation and compact grammar without reading or ordering relation witnesses.
3. On known-log targets, update the equation, decide restricted solvability, expand one word, map it to points, and replay the group sum.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Apply the identical encoding/compression path to fresh scalar-blind `Q+[t]P` targets.
6. Expand a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge equation construction, grammar size, recompression passes, restrictions, expansion, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Recompression exploits ordered concatenation and cancellation-free word structure, whereas elliptic decomposition is an unordered abelian group equality with a large permutation fibre. Supplying an ordered witness in the equation is source advice; representing all orderings or enforcing point addition restores the original polynomial/source surface. The operation therefore merges with compressed-certificate and representation routes in IDEAs 084, 106, 120, 189, and 297.

## Proof track

Give a source-free polynomial-size word-equation reduction with a biconditional mapping between every restricted elliptic fibre and grammar solutions, then prove charged construction and expansion exponents at most `0.45`.

## Disproof track

Prove that any faithful encoding either contains source order/incidence, has source-sized solution grammar, or requires an oracle equivalent to exact restricted elliptic existence.

## Positive and negative controls

- Positive: supplied free-monoid equations with planted compressed solutions and an external point-word map.
- Negative: permutations of one elliptic tuple, repeated and inverse points, two words with the same group sum, arbitrary deck restrictions, and blind targets.
- Baselines: IDEAs 084/106/120/189/297, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a faithful endpoint-only equation, restriction-stable compact grammar, exact source expansion, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on embedded source words, factorial permutation expansion, an exact-existence oracle, one missed stratum, source-sized grammar, or either exponent at least `0.50`.
- Successful recompression of a supplied toy word equation is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-371/word_equation_biconditional.md`
- `ideas/artifacts/ECDLP-IDEA-371/permutation_fibre_cases.json`
- `ideas/artifacts/ECDLP-IDEA-371/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-371/cost_analysis.md`

## Interpretation boundary

This rejects the screened free-monoid encoding, not recompression. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. A compressed supplied word is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-371/word_equation_biconditional.md` and test whether elliptic sum equality has any source-free faithful word-equation encoding smaller than its source fibre.
