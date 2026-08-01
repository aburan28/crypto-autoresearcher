# ECDLP-IDEA-341 — Butterfly complementary-low-rank source transform

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `merged_rejected_low_rank_factorization_requires_ordered_source_operator_and_exact_inverse`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: relative top-lane draft is retired, `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; approximate low rank or fast aggregate application is not an ECDLP break.

## Falsifiable hypothesis

There is a public multiscale ordering of signed factor decks and endpoints for which the exact addition-incidence operator has bounded complementary rank, admits a source-labelled butterfly factorization inside `B^(9/4)`, and has exact inverse causal cones supporting fresh-target source recovery inside `B^(5/4)`.

## Mechanism-new operation

The screened operation is **factor an endpoint-to-source incidence operator across complementary multiscale partitions, retain noncancelling source labels in each butterfly block, and backtrack an exact inverse causal cone**. This is distinct from generic low rank only if the elliptic operator and ordering are constructed without source enumeration. Approximate FIO compression does not preserve zeros or labels; otherwise this merges with IDEAs 050, 077, 123, 224, 231, and 267.

## Assumptions

1. A target-independent public ordering gives uniformly bounded exact, not numerical, complementary rank.
2. Factor construction samples no hidden source entries and avoids an explicit pair or tuple table.
3. Intermediate blocks retain exact finite-field values and all signed source provenance without rank growth.
4. Every reported hit, zero, or candidate has a bounded exact inverse to every source tuple on every stratum.
5. Ordering, sampling, factors, output, rank, logs, descent, verification, bit cost, and memory are charged.

## Semantic fingerprint

`ordered_elliptic_incidence_operator | exact_complementary_low_rank | multiscale_butterfly_factorization | source_labelled_inverse_causal_cone | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the exact public value-matrix rank boundary.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the phase-feature full-rank and nonlinear gap.
3. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate/source compression frontier.
4. `inputs/ledger_inventory.json` — imported `P1478`, the compact local transition whose exact composition becomes dense.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry-edge floor.

## Closest primary literature

- Candès, Demanet, and Ying, [A Fast Butterfly Algorithm for the Computation of Fourier Integral Operators](https://doi.org/10.1137/080734339), exploits approximate complementary low rank of a supplied ordered oscillatory kernel; it does not construct an exact finite-field source operator or inverse witnesses.
- Frieze and Kannan, [Quick Approximation to Matrices and Applications](https://doi.org/10.1007/s004930050052), is an approximation control showing why cut/low-rank summaries do not imply exact zero localization.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint constraints rather than the ordered operator and source inverse.

No checked source establishes the exact elliptic factorization; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, decks, multiscale ordering, operator access rule, factorization, inverse, masks, and verifier.
2. Construct exact factors without materializing source pairs/tuples or choosing a favorable target order post hoc.
3. Apply them to known-log endpoints, replay all exact signed sources, and verify each relation.
4. Collect at least `B` independently ranked rows, solve factor logs, and verify them.
5. Apply the identical factors to fresh scalar-blind masked targets and retain all misses and collisions.
6. Backtrack exact causal cones, substitute logs, remove masks, and verify `[x]P=Q`.
7. Charge construction, transforms, output, rank, logs, descent, verification, bit operations, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, factorized query excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All sampled entries, interpolation nodes, blocks, labels, backtracking, and bit precision are charged; `0<=r<=o`. If there are `N^s` factor blocks of exact rank `N^k`, the construction and application exponents `a,q` must include the full block-count times rank times access/output cost; bounding `k` alone is insufficient. Promotion requires setup/state/campaign/log exponents at most `0.45` and fresh query at most `0.25`. Pollard rho has expected time exponent `0.50` with negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Butterfly rank is an approximate analytic property tied to a known phase and geometry. The finite-field addition-incidence operator has no public scalar ordering, and exact source indicators can have full complementary rank under every available coordinate order. Retaining noncancelling provenance turns small numerical blocks into source-sized dictionaries; approximate application may return counts or values but cannot certify exact zeros and factor points.

## Proof track

Give an explicit public order, prove uniform exact complementary rank and source-labelled factor construction, prove exact all-strata inversion, and derive complete `lambda,mu<=0.45`.

## Disproof track

Prove a block-rank lower bound under the proposed order, find aggregate-equal source collisions, show factor sampling materializes the operator, or demonstrate that block-count times rank plus exact labels exceeds `B^(9/4)` setup or `B^(5/4)` query.

## Positive and negative controls

- Positive: supplied exact low-rank finite-field butterfly matrices with planted labelled supports must apply and invert correctly.
- Negative: approximate real FIO blocks, source-permuted operators, full-rank random kernels, and count-only contractions must not emit elliptic sources.
- Baselines: IDEAs 050/077/123/224/231/267, dense operator application, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact block rank `B^(1/4+o(1))` or less, zero source errors, 1,000 verified rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify if full factor construction or label state exceeds `B^(9/4)`, a fresh inverse query exceeds `B^(5/4)`, one stratum is lost, the order uses scalar labels, or either exponent reaches `0.50`.
- Approximate low rank or fast aggregate application is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-341/operator_ordering_spec.md`
- `ideas/artifacts/ECDLP-IDEA-341/exact_block_rank_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-341/source_causal_cone_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-341/cost_analysis.md`

## Interpretation boundary

This rejects the proposed exact source-labelled butterfly transform, not butterfly algorithms. All finite evidence would be toy, heuristic, model-bound, and novelty-unverified. Fast approximation or a correct aggregate is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-341/operator_ordering_spec.md` defining one public multiscale order and the exact finite-field blocks without enumerating source tuples.
