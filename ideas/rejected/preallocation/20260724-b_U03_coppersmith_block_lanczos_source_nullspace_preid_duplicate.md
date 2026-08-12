# Pre-ID duplicate draft — Coppersmith block-Lanczos source nullspace

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U03`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_symmetric_source_matrix_and_nullspace_backend`.
- Class/risk/lane: algorithm / conservative / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a nullspace vector or dependency certificate is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-derived symmetric bilinear operator on restricted source states has a block-Lanczos
nullspace whose sparse vectors decode to exact signed relations. Its orthogonality recurrence would
produce full factor-base logs and blind descent with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation iteratively builds mutually orthogonal blocks for a supplied sparse symmetric
finite-field system and extracts its nullspace. It becomes ECDLP-new only if symmetry, entries,
and a sparse nullspace-to-occurrence lift are constructed from endpoints without source incidence.
Using block Lanczos after materializing the relation matrix is a solver substitution.

## Assumptions

1. Endpoint data defines a symmetric exact-relation operator without enumerated sources.
2. Orthogonal blocks preserve signed occurrence ancestry.
3. Nullspace vectors are sparse enough and canonically decode to actual tuples.
4. Breakdown handling, matvecs, communication, replay, rank, logs, and descent satisfy both caps.
5. The state is target-independent and scalar-blind.

## Semantic fingerprint

`public_symmetric_relation_operator | block_Lanczos_orthogonalization | sparse_nullspace_vector | signed_occurrence_decode | full_descent`

## Five closest ledger entries

1. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — block Krylov is already occupied.
2. `ideas/rejected/preallocation/20260724-b_U02_coppersmith_block_wiedemann_source_multisequence_preid_duplicate.md` — the same represented-matrix boundary with another solver.
3. `ideas/rejected/ECDLP-IDEA-231_operator_scaling_shrunk_subspace_source_atomizer_hypothesis.md` — a subspace certificate does not orient exact source atoms.
4. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — sparse relation matrices carry source provenance and cost.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact source return remains required before linear algebra.

## Closest primary literature

- Coppersmith, [Solving linear equations over GF(2): block Lanczos](https://doi.org/10.1016/0024-3795(93)90235-G), operates on a supplied sparse matrix.
- Wiedemann, [sparse finite-field systems](https://doi.org/10.1109/TIT.1986.1057137), is the neighboring black-box solver.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not supply symmetric source incidence.

No checked source creates the matrix or occurrence decoder; the transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, symmetric compiler, block schedule, breakdown policy, restrictions, masks, and verifier.
- Build reusable state under `B^(9/4+o(1))` with no source table, factor logs, dense resultant, or target advice.
- Charge matrix construction, every matvec/inner product/block repair, nullspace branch, sparsification, and exact signed replay.
- Obtain at least `max(d_FB+32,1000)` verified rows, rank `d_FB`, and all factor-base logs.
- Reuse state for 100 fresh masked targets, decode exact tuples, subtract masks, and verify scalars.
- Charge failure, output, communication, bit work, and peak memory.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state are `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, Lanczos/replay work `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity/failure `N^u`, and log solve `N^ell,N^ell_m`.
Use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Nullspace algorithms consume a matrix whose columns already name source objects. Symmetrizing an
endpoint aggregate can preserve kernel dimension while destroying occurrence identity. A dependency
certificate is relation-only evidence; decoding it to exact tuples requires the missing source table
or restricted predicate.

## Proof track

Prove endpoint-only symmetric compilation, exact sparse nullspace semantics, all-strata source
decode, full rank/log/descent, and complete breakdown/communication accounting below both caps.

## Disproof track

Produce equal symmetric operators with different exact source fibres, show any source-labelled
column, or force dense null vectors/backpointers or complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied sparse symmetric systems with planted labelled null vectors.
- Negative: equal-operator different-source fibres, dense kernels, isotropic breakdowns, empty fibres, repeated points, and fresh targets.
- Baselines: block Wiedemann, IDEA-056, P1553 R4, rho, and BSGS.
- A correct null vector or dependency is not an attack result.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/decode theorems, zero errors across four sizes/all strata, failure at most `2^-80`, full rank/logs, 100 descents, and `lambda,mu<=0.45`.
- Falsify on one source column, equal-operator source collision, dense decode, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u03_symmetric_operator_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u03_nullspace_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u03_lanczos_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not block Lanczos. Correct nullspace recovery, a dependency, or one
relation is `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Test whether a smallest supplied symmetric relation matrix admits two source-label assignments with the same nullspace but different exact signed tuple replay.
