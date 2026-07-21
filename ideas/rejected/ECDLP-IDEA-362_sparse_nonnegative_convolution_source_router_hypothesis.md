# ECDLP-IDEA-362 — Sparse nonnegative-convolution source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_sparse_convolution_needs_endpoint_support_and_source_ancestry`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `retired review_required preflight; execution prohibited`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exact convolution value or one valid relation is not an ECDLP break.

## Falsifiable hypothesis

The pair-endpoint decks in P1553 admit a public nonnegative sparse encoding whose output-sensitive exact convolution supports subset-stable `2+2+1` nonemptiness queries and source bisection within `B^(9/4+o(1))` setup/state and `B^(5/4+o(1))` fresh-target work.

## Mechanism-new operation

The screened operation is **encode partial elliptic endpoints as sparse nonnegative coefficient arrays, compute only the nonzero support of their exact convolution, and use positivity to turn a nonzero target coefficient into an exact restricted-existence decision**. Nonnegativity avoids cancellation, while dyadic restrictions would recover one labelled source tuple. The operation is distinct from dense FFT/resultant routes only if the encoding is endpoint-derived, source ancestry is retained without explicit source tables, and output support stays below the frozen gates.

## Assumptions

1. Elliptic partial endpoints have a public collision-free or publicly corrected integer/cyclic index that does not compute discrete logarithms.
2. The encoded pair supports and their convolution output have `B^(9/4+o(1))` total setup/state despite arbitrary prime-order decks.
3. Target translation and arbitrary dyadic source restrictions update the sparse convolution in `B^(5/4+o(1))` work.
4. A positive coefficient identifies existence on every signed, repeated, singular, infinity, coloured, and ambiguous stratum, and charged bisection returns one tuple.
5. Coordinate packing, carries, collisions, support construction, output, rank, factor logs, descent, verification, and bit costs are charged.

## Semantic fingerprint

`elliptic_pair_endpoint_sparse_arrays | nonnegative_output_sensitive_exact_convolution | target_coefficient_nonemptiness | subset_stable_restriction_updates | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the open object is the public source-resolving arithmetic interface, not convolution after a source index exists.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target batching and arithmetic source-fibre generation remain above the complete gate.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit endpoint/source incidences retain the missing witness surface.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; pair advice restores cubic work when extended through the fifth source or targets.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; a sorted exact complement stream is a correctness control, not a new complete-cost route.

## Closest primary literature

- Bringmann, Fischer, and Nakos, [Deterministic and Las Vegas Algorithms for Sparse Nonnegative Convolution](https://arxiv.org/abs/2107.07625), gives output-sensitive exact convolution when sparse arrays and their integer indices are already supplied.
- Cole and Hariharan, [Verifying candidate matches in sparse and wildcard matching](https://doi.org/10.1145/775047.775058), is a sparse-convolution/matching control on represented strings rather than elliptic endpoint fibres.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but not a DLP-free sparse convolution index or source ancestry.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, five signed coloured decks, endpoint index, nonnegative coefficient convention, collision policy, restrictions, masks, and verifier.
2. Build target-independent sparse pair arrays without scalar labels or enumerated triple/five-source tables.
3. For known-log targets, issue restricted exact coefficient queries, bisect to one tuple, and replay it by direct group addition.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Apply the identical arrays and target update to fresh scalar-blind `Q+[t]P` endpoints.
6. Recover one tuple, substitute factor logs, remove `t`, retain all ambiguity, and verify `[x]P=Q`.
7. Charge encoding, support generation, convolution, restrictions, source output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; one fresh target must be at most `B^(5/4+o(1))`; complete promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Sparse convolution is fast in its represented input and output support. A DLP-free one-dimensional index compatible with elliptic addition is unconstructed; ordinary coordinate packing creates carries/collisions and target-dependent correction. Even if `B^2` pair arrays fit setup, the pair-pair-plus-singleton output is generically `B^3`/`B^4`, and retaining exact source ancestry restores the source surface. Thus output sensitivity does not remove Query2P1.

## Proof track

Construct the public index and restriction update, prove nonnegative coefficient biconditionals and exact source bisection on all strata, and bound complete exponents by `0.45`.

## Disproof track

Show that any DLP-free encoding has super-gate support/collision correction, or exhibit restricted fibres with identical accessible coefficients but different exact nonemptiness.

## Positive and negative controls

- Positive: planted sparse integer sumsets with collision-free indices and labelled summands.
- Negative: random elliptic decks, coordinate packings with carries, dense pair-pair outputs, permuted source labels, and P1435 exact complement streams.
- Baselines: IDEAs 117/121/134/165/353, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only sparse arrays, zero-error restricted coefficients plus charged bisection, 1,000 verified rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on a DLP-derived index, explicit source table, one false coefficient, one missed stratum, `B^3` output/support traffic, or either exponent at least `0.50`.
- Fast convolution on supplied toy arrays is only a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-362/endpoint_index_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-362/sparse_support_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-362/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-362/cost_analysis.md`

## Interpretation boundary

This rejects the screened sparse-convolution encoding, not sparse convolution or all specialized product circuits. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Correct coefficients or a relation are not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-362/endpoint_index_obligations.md` and prove whether a DLP-free nonnegative index supports exact restricted elliptic convolution without super-gate support.
