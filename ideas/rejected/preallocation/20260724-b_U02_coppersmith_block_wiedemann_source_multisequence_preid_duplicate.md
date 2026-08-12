# Pre-ID duplicate draft — Coppersmith block-Wiedemann source multisequence

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U02`; no canonical ID allocated.
- Disposition: `merged_rejected_block_krylov_parallelization_of_supplied_source_matrix`.
- Class/risk/lane: algorithm / conservative / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a block minimal generator or nullspace basis is not an ECDLP break.

## Falsifiable hypothesis

Endpoint-derived block projections of an implicit relation operator expose a low-degree matrix
generator that preserves multiple exact source occurrences at once. Block Wiedemann would amortize
relation generation and descent below rho and BSGS with both complete exponents at most `0.45`.

## Mechanism-new operation

The native operation forms a matrix-valued Krylov sequence and recovers a minimal matrix generator,
allowing parallel black-box linear algebra. Mechanism credit requires an endpoint-derived,
source-free block matvec and a canonical generator-to-occurrence inverse. Merely widening the
scalar projections of IDEA-056/U01 is a parameter/solver change.

## Assumptions

1. Public endpoints define all block matvecs without source enumeration.
2. Block projections retain exact signed occurrence identity under every restriction.
3. Generator roots or nullspace vectors canonically lift to factor-base tuples.
4. Parallel work, communication, matrix-generator solve, replay, logs, and descent meet both caps.
5. The same state handles 100 fresh scalar-blind targets.

## Semantic fingerprint

`public_endpoint_block_operator | matrix_Krylov_multisequence | minimal_matrix_generator | exact_occurrence_backlift | full_descent`

## Five closest ledger entries

1. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — exact operation owner.
2. `ideas/rejected/preallocation/20260724-b_U01_wiedemann_coordinate_recurrence_source_opener_preid_duplicate.md` — scalar version with the same missing operator.
3. `ideas/ECDLP-IDEA-006_elliptic_net_short_annihilator_hypothesis.md` — annihilator recovery does not by itself orient a hidden scalar/source.
4. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — represented relation rows retain source traffic.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted decision/replay owner.

## Closest primary literature

- Coppersmith, [Solving homogeneous linear equations over GF(2) via block Wiedemann](https://www.ams.org/journals/mcom/1994-62-205/S0025-5718-1994-1192970-7/), assumes a supplied large sparse matrix.
- Wiedemann, [sparse finite-field linear equations](https://doi.org/10.1109/TIT.1986.1057137), supplies the scalar black-box predecessor.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not compile the exact source matvec.

No source provides endpoint-only block incidence or exact occurrence inversion; novelty is unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, block sizes, projections, decks, restrictions, masks, communication schedule, and verifier.
- Compile reusable state within `B^(9/4+o(1))` without source rows, target fitting, factor logs, or dense resultants.
- Charge all block matvec entries, projections, sequence terms, generator computation, communication, nullspace branches, and signed replay.
- Verify at least `max(d_FB+32,1000)` rows, rank `d_FB`, and every factor-base logarithm.
- Run 100 fresh masked-target queries with identical state, recover tuples, subtract masks, and verify each scalar.
- Include failure, ambiguity, output, bit work, extension arithmetic, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, block-Krylov/replay work `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity/failure `N^u`, and log solve `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
state `<=B^(9/4+o(1))`, online work/workspace `<=B^(5/4+o(1))`; rho and
BSGS retain exponent `0.50`.

## Likely fatal obstruction

Blocking improves throughput after a source-bearing operator is represented. It does not lower
the information cost of constructing exact elliptic incidence, and matrix generators quotient
the history of individual contributions. Source backpointers restore the state/traffic that the
block method was supposed to avoid.

## Proof track

Prove source-free block matvecs, subset-stable exact generator semantics, canonical all-strata
occurrence lift, full rank/log/descent, and complete communication-aware caps.

## Disproof track

Freeze the block sequence and vary hidden fibres, expose source-labelled blocks/backpointers,
or show block communication/state or complete work has exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied sparse block systems with labelled planted kernels.
- Negative: identical block sequences with different source fibres, rank-deficient blocks, shuffled projections, empty fibres, and fresh targets.
- Baselines: scalar Wiedemann, IDEA-056, P1553 R4, rho, and BSGS.
- Faster block solving or one valid row is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only with zero semantic errors, exact compiler/lift theorems, failure at most `2^-80`, full rank/logs, 100 blind descents, and both exponents at most `0.45`.
- Falsify on one supplied source block, sequence collision, ambiguous lift, missing relation, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u02_block_operator_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u02_equal_multisequence_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u02_communication_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not block Wiedemann. Correct generators, nullspaces, or relation
rows remain `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not breakthroughs.

## Exactly one next executable action

1. Symbolically expand one proposed endpoint block matvec and classify every term as public-endpoint, source-labelled, or hidden-predicate work.
