# Pre-ID duplicate draft — Wiedemann coordinate-recurrence source opener

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U01`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_sparse_operator_and_krylov_solver_substitution`.
- Class/risk/lane: algorithm / conservative / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; recovering a minimal polynomial, null vector, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

Public endpoint data compiles an implicit sparse operator whose scalar Krylov sequence has a
short recurrence encoding exact signed factor-base occurrences. Wiedemann recovery would open
those occurrences, give full-rank relations and 100 blind descents, and keep complete time and
memory exponents at most `0.45`.

## Mechanism-new operation

The native operation projects repeated applications of a sparse finite-field operator to a scalar
linearly recurrent sequence and recovers its minimal polynomial. It counts as ECDLP-new only if
the operator and its matvec are endpoint-derived without enumerating source tuples or embedding
their labels. Applying Wiedemann after a source matrix exists is the solver substitution expressly
barred by the corpus.

## Assumptions

1. A source-free public operator represents exact restricted relation incidence.
2. A scalar projection preserves signs, repetitions, exceptional strata, and occurrence identity.
3. The recovered recurrence has a canonical occurrence lift, not only a kernel certificate.
4. Operator construction, matvecs, recurrence recovery, replay, rank, logs, and descent satisfy both caps.
5. Frozen operator state is reusable without target fitting or factor logarithms.

## Semantic fingerprint

`public_endpoint_operator | scalar_Krylov_sequence | Wiedemann_minimal_polynomial | exact_signed_occurrence_lift | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — the exact block-Krylov owner and explicit solver-control boundary.
2. `ideas/ECDLP-IDEA-006_elliptic_net_short_annihilator_hypothesis.md` — a recurrence is useful only with a noncircular scalar/source inverse.
3. `ideas/rejected/ECDLP-IDEA-078_sparse_source_enumerator_interpolation_hypothesis.md` — black-box evaluations assume the missing source-sensitive oracle.
4. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — represented sparse rows and provenance already carry source cost.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable decision and signed replay remain the live gate.

## Closest primary literature

- Wiedemann, [Solving sparse linear equations over finite fields](https://doi.org/10.1109/TIT.1986.1057137), begins with a supplied sparse matrix and matvec.
- Coppersmith, [block Wiedemann over GF(2)](https://www.ams.org/journals/mcom/1994-62-205/S0025-5718-1994-1192970-7/), parallelizes that represented linear-system stage.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations, not the sparse source operator or its occurrence lift.

No checked source constructs the required operator from a generic-prime endpoint. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, decks, operator compiler, projections, restrictions, masks, and verifier.
- Build target-independent state within `B^(9/4+o(1))`, excluding source tables, dense resultants, target advice, and factor logs.
- Charge every operator entry or implicit matvec contribution, Krylov step, recurrence solve, factor, null-vector branch, and occurrence replay.
- Collect at least `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve every factor-base logarithm.
- Reuse byte-identical eligible state on 100 fresh `Q+[t]P` targets, return signed tuples, subtract masks, and verify `[x]P=Q`.
- Charge setup, densities, output, failure, rank, factor solve, bit work, and peak memory end to end.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal relation and target
densities `N^delta,N^delta_t`; operator/Krylov/replay work and workspace
`N^q,N^q_m`; rank credit `N^r`; output `N^o`; ambiguity/failure `N^u`; and
factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, with `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Wiedemann compresses and solves a represented linear operator; it does not create that operator.
An exact relation-incidence matvec either enumerates source contributions or calls Query2P1.
Endpoint-only aggregate matvecs can have identical Krylov transcripts while exact source fibres
differ, and a null vector does not identify its constituent elliptic occurrences.

## Proof track

Prove a source-free operator compiler, restriction-uniform exact matvec theorem, injective
projection-to-occurrence lift, full relation rank/log recovery, blind descent, and both cost caps.

## Disproof track

Hold all scalar Krylov samples fixed while changing exact source fibres, expose one source-labelled
operator entry, or show that source replay or the complete exponent reaches `0.50`.

## Positive and negative controls

- Positive: supplied sparse matrices with planted short minimal polynomials and labelled null vectors.
- Negative: equal-Krylov different-source fibres, dense operators, projection collisions, empty fibres, repeated points, and fresh targets.
- Baselines: IDEA-056, elliptic-net recurrence, P1553 R4, rho, and BSGS.
- A correct recurrence or relation row remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with a proved public compiler and exact lift, zero semantic errors across four sizes/all strata, miss probability at most `2^-80`, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-bearing matrix entry, equal-transcript source collision, missed/false occurrence, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u01_operator_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u01_equal_krylov_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u01_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Wiedemann's method. Correct linear solving, a minimal polynomial,
or a valid relation remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Construct the smallest pair of exact signed-source incidence operators with the same frozen scalar Krylov sequence but different accepting occurrence fibres.
