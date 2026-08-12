# Pre-ID duplicate draft — Berkowitz division-free source characteristic circuit

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U06`; no canonical ID allocated.
- Disposition: `merged_rejected_division_free_matrix_invariant_without_source_inverse`.
- Class/risk/lane: representation / representation-changing / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; determinant, adjugate, or characteristic-polynomial correctness is not an ECDLP break.

## Falsifiable hypothesis

Endpoint-defined relation compatibility has a compact division-free matrix circuit whose
characteristic coefficients preserve enough provenance to reconstruct every exact signed source.
Berkowitz recursion would avoid bad denominators and dense elimination while enabling full blind
descent with `lambda,mu<=0.45`.

## Mechanism-new operation

The native operation computes determinant, adjugate, and characteristic polynomial over a
commutative ring via uniform division-free circuits. ECDLP novelty requires the matrix to be
endpoint-derived and its invariant coefficients to admit a point-faithful inverse. Swapping
division-free characteristic-polynomial computation for another resultant/linear solver is a backend change.

## Assumptions

1. A compact public matrix represents restricted source existence without enumerated incidence.
2. Berkowitz coefficients retain occurrence identity, not merely spectrum/determinant.
3. An exact coefficient-to-signed-point inverse exists for all strata.
4. Circuit construction, ring growth, inversion, replay, logs, and descent satisfy both caps.
5. The circuit is target-independent and scalar-blind.

## Semantic fingerprint

`public_compatibility_matrix | Berkowitz_division_free_Toeplitz_recursion | characteristic_coefficients | point_faithful_source_inverse | full_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-001_ambient_spectral_incidence_oracle_hypothesis.md` — spectral invariants aggregate away source incidence.
2. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — characteristic/minimal polynomial after a supplied operator is occupied.
3. `ideas/deferred/ECDLP-IDEA-068_pre_event_elimination_motif_generator_hypothesis.md` — elimination must create exact pre-event sources, not only a polynomial.
4. `ideas/rejected/ECDLP-IDEA-378_comprehensive_groebner_target_atlas_hypothesis.md` — dense algebraic preprocessing/state is already charged.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — coefficients must still support exact restricted replay.

## Closest primary literature

- Berkowitz, [On computing the determinant in small parallel time](https://doi.org/10.1016/0020-0190(84)90018-8), computes invariants of a supplied matrix over a commutative ring.
- Keller–Gehrig, [fast characteristic polynomial algorithms](https://doi.org/10.1016/0304-3975(85)90049-0), supplies a neighboring matrix-invariant route.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not supply a compact source matrix or inverse.

No checked source connects characteristic coefficients to exact elliptic occurrences; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, matrix compiler, ring, recursion order, restrictions, masks, and verifier.
- Build target-independent state within `B^(9/4+o(1))`, excluding source tables, dense resultants, factor logs, and target advice.
- Charge every matrix entry, Toeplitz block, ring multiplication, coefficient, factor/inverse branch, and signed replay.
- Verify at least `max(d_FB+32,1000)` rows, rank `d_FB`, and solve every factor-base logarithm.
- Apply byte-identical eligible state to 100 fresh masked targets, subtract masks, and verify scalars.
- Charge coefficient growth, bit work, failure, output, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, setup/state are `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, circuit/inverse/replay work `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, and logs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`. Rho/BSGS remain `0.50`.

## Likely fatal obstruction

Characteristic data is invariant under similarity and therefore cannot recover source labels.
Building a point-faithful matrix already materializes incidence, while a matrix small enough to
avoid that cost has collisions between exact fibres. Division-freedom fixes arithmetic
denominators, not the missing information flow.

## Proof track

Prove a compact endpoint matrix, injective restriction-uniform characteristic encoding,
all-strata source inverse, full rank/log/descent, and complete ring/bit costs below both caps.

## Disproof track

Find two source-labelled matrices with equal characteristic circuits/invariants, identify any
enumerated matrix entry, or show coefficient growth/source inverse/complete cost reaches `0.50`.

## Positive and negative controls

- Positive: supplied labelled companion matrices whose source basis is retained separately.
- Negative: similar/permuted matrices, isospectral nonisomorphic matrices, repeated factors, exceptional fibres, and fresh targets.
- Baselines: spectral IDEA-001, IDEA-056, dense resultants, P1553 R4, rho, and BSGS.
- Correct determinant or characteristic coefficients are not ECDLP progress.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/inverse proofs, zero collisions/errors, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one equal-invariant source collision, source-sized matrix, missed occurrence, coefficient/cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u06_matrix_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u06_isospectral_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u06_ring_growth_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Berkowitz's circuit. Correct determinant/adjugate computation or
a valid relation remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Enumerate the smallest isospectral pair of source-labelled compatibility matrices and test whether their exact signed occurrence fibres differ.
