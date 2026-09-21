# Pre-ID duplicate draft — Bareiss fraction-free source elimination

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U07`; no canonical ID allocated.
- Disposition: `merged_rejected_fraction_free_backend_on_supplied_source_system`.
- Class/risk/lane: algorithm / conservative / conservative pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; exact division, determinant correctness, or one valid relation is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-derived structured linear/elimination system for exact signed occurrences has severe
denominator swell but small determinantal minors. Bareiss integer-preserving elimination would keep
state compact, expose exact source rows, and enable factor logs plus 100 blind descents with complete
exponents at most `0.45`.

## Mechanism-new operation

The native operation uses Sylvester identities and exact divisions to perform fraction-free
Gaussian elimination with controlled intermediate growth. ECDLP mechanism credit requires the
input equations themselves to arise endpoint-only and the eliminated solution to lift to exact
occurrences. Replacing dense/fraction-field elimination after the source system is built is a backend substitution.

## Assumptions

1. Public endpoints compile a small exact source system without enumerated tuples.
2. Bareiss pivots/divisions remain exact and compact uniformly across restrictions and strata.
3. The solution identifies signed occurrences rather than only a determinant or compatibility bit.
4. System construction, pivoting, growth, replay, rank, factor logs, and descent satisfy both caps.
5. Frozen equations and pivot policy are scalar-blind and reusable.

## Semantic fingerprint

`public_endpoint_equation_system | Bareiss_fraction_free_pivots | compact_exact_solution | signed_occurrence_lift | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/deferred/ECDLP-IDEA-068_pre_event_elimination_motif_generator_hypothesis.md` — exact elimination must first create a source-bearing pre-event.
2. `ideas/rejected/ECDLP-IDEA-378_comprehensive_groebner_target_atlas_hypothesis.md` — dense elimination/state is already charged.
3. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — changing the linear solver is not the source operation.
4. `ideas/rejected/ECDLP-IDEA-115_source_labelled_ulrich_chow_complex_hypothesis.md` — source-labelled complexes/matrices carry the missing incidence.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted source decision and replay remain prerequisite.

## Closest primary literature

- Bareiss, [Sylvester's identity and multistep integer-preserving Gaussian elimination](https://doi.org/10.1090/S0025-5718-1968-0226829-0), starts from a supplied linear system.
- Berkowitz, [division-free determinant circuits](https://doi.org/10.1016/0020-0190(84)90018-8), similarly changes arithmetic after a matrix is represented.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not provide the compact source system or lift.

No checked source removes source construction or dense-resultant cost; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, equation compiler, pivot policy, restrictions, masks, ring, and verifier.
- Build reusable target-independent state within `B^(9/4+o(1))`, excluding source tables, dense resultants, factor logs, and target fitting.
- Charge every equation coefficient, pivot search, minor, multiplication, exact division, fallback, solution branch, and signed replay.
- Verify at least `max(d_FB+32,1000)` independent rows, rank `d_FB`, and all factor-base logarithms.
- Reuse identical eligible state on 100 fresh masked targets, subtract masks, and verify every scalar.
- Charge coefficient/bit growth, failures, outputs, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, elimination/replay work `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity/failure `N^u`, and log costs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`;
Pollard rho and BSGS retain exponent `0.50`.

## Likely fatal obstruction

Bareiss reduces coefficient swell after equations are supplied; it does not construct the exact
endpoint-to-source equations. A small endpoint aggregate system need not distinguish occurrence
fibres, while a point-faithful system or dense resultant restores the source-sized construction.
Exact divisions are arithmetic controls, not new information.

## Proof track

Prove a compact endpoint-only system, uniform exact-pivot/growth bound, injective all-strata
solution-to-source lift, full rank/log/descent, and complete sub-rho bit complexity.

## Disproof track

Identify one source-enumerated coefficient, hold the system fixed while changing exact fibres,
or show pivot/minor growth, source replay, or complete exponent reaches `0.50`.

## Positive and negative controls

- Positive: supplied integer/polynomial systems with planted sparse labelled solutions and exact Bareiss pivots.
- Negative: equal-system different-source fibres, singular/pivot-zero cases, dense minors, exceptional elliptic strata, and fresh targets.
- Baselines: ordinary elimination, Berkowitz, IDEA-068/378, P1553 R4, rho, and BSGS.
- Exact arithmetic or a valid solution is not a breakthrough.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/lift theorems, zero semantic errors, polynomially bounded measured bit growth within caps, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-derived equation, equal-system collision, inexact division, cap breach, missed/false occurrence, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u07_equation_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u07_equal_system_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u07_fraction_free_bit_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not Bareiss elimination. Correct exact division, a determinant,
or a valid relation remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Expand the smallest proposed endpoint equation system and account whether each coefficient can be computed without enumerating or querying exact source occurrences.
