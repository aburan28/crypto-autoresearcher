# Pre-ID duplicate draft — Saad–Schultz GMRES source residual

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R02`; no canonical ID allocated.
- Disposition: `merged_rejected_arnoldi_residual_solver_substitution`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a small residual, valid relation, or verifier pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, a public nonsymmetric endpoint operator admits a short GMRES
Krylov basis whose minimum-residual iterate exactly returns signed factor-base sources often
enough for full factor logs and 100 fresh blind descents with complete exponents at most `0.45`.

## Mechanism-new operation

GMRES builds an Arnoldi basis for a supplied linear operator and minimizes the residual over the
current Krylov subspace. The transplant counts only if the operator is endpoint-derived without
source advice and residual zero has an exact charged inverse to signed occurrences. Restarting,
preconditioning, or replacing another backend after source compilation is a control.

## Assumptions

1. Public endpoints compile the nonsymmetric operator without an incidence table.
2. Arnoldi products and orthogonalization preserve exact finite-field semantics and all strata.
3. Restart dimension, precision, and workspace satisfy the online cap.
4. Minimum residual identifies a unique exact source occurrence rather than an aggregate vector.
5. Relation and fresh-target queries reuse byte-identical target-independent state.

## Semantic fingerprint

`public_endpoint_nonsymmetric_operator | arnoldi_minimum_residual_iteration | exact_zero_residual_source | charged_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260721-d_L12_arnoldi_hessenberg_source_projection_preid_duplicate.md` — directly owns the supplied-operator Arnoldi projection.
2. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — Krylov structure helps only after the transition operator exists.
3. `ideas/rejected/preallocation/20260719-d_D06_randomized_kaczmarz_source_projection_preid_duplicate.md` — iterative residual reduction cannot create source rows.
4. `ideas/rejected/preallocation/20260722-a_N10_residual_belief_source_scheduler_preid_duplicate.md` — residual scheduling changes solver order, not endpoint information.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and signed replay remain missing.

## Closest primary literature

- Saad and Schultz, [GMRES: A Generalized Minimal Residual Algorithm for Solving Nonsymmetric Linear Systems](https://doi.org/10.1137/0907058), minimizes residuals for a supplied matrix.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not provide the compact operator or occurrence inverse.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), controls the complete generic comparison.

The ECDLP operator compiler is outside GMRES; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, operator, restart policy, preconditioner, restrictions, precision, exceptional strata, and verifier.
2. Build target-independent state inside `B^(9/4+o(1))` without tuple enumeration, scalar labels, or hidden decomposition calls.
3. For each known-log target, run exact GMRES, replay signed occurrences from a certified zero residual, and verify the elliptic sum.
4. Obtain at least `max(d_FB+32,1000)` verified independent rows, rank `d_FB`, and all factor logs.
5. On 100 fresh `R=Q+[t]P`, reuse identical state, recover points, subtract `t`, and verify `[x]P=Q`.
6. Charge operator construction, Arnoldi products, orthogonalization, restart loss, precision, failures, output, rank, logs, bits, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, define `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m` as setup/state,
reciprocal densities, one query/workspace, verified-rank credit, output, ambiguity, and
factor-log costs. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain `0.50`.

## Likely fatal obstruction

GMRES consumes the operator that encodes source compatibility. Without that operator it has
nothing to iterate; with it, the missing Query2P1/source compiler has already been paid.
Moreover, a small residual is approximate and a zero residual need not expose a unique source.

## Proof track

Prove an endpoint-only operator, exact finite-field Arnoldi semantics, bounded basis dimension,
restriction-stable signed inversion, and the complete relation-to-descent caps.

## Disproof track

Find one materialized source column, false small-residual positive, restart blowup, lost
occurrence identity, source-dependent preconditioner, or full exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy nonsymmetric systems with a planted exact integral solution.
- Negative: equal Krylov moments with different sources, near-zero nonzero residuals, empty
  fibres, restart adversaries, exceptional strata, and blind targets.
- Baselines: Arnoldi, block Krylov, P1553 R4, rho, and BSGS.
- Residual minimization alone is toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only after exact four-size/all-strata controls, full rank/logs, 100 blind descents,
  both resource caps, and `lambda,mu<=0.45`.
- Falsify on any supplied source operator, approximate-only residual, replay ambiguity, cap
  violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r02_operator_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r02_restart_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r02_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not GMRES. Correct residuals or relations remain toy,
heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Trace one exact GMRES operator application from a public endpoint and stop at the first materialized source-incidence term or certify its absence and charged inverse.
