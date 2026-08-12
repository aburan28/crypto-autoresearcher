# Pre-ID duplicate draft — Arnoldi Hessenberg source projection

## Status and claim labels

- Prospect: `20260721-d-L12`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: linear_algebra_algorithm / high-risk / high-risk pre-ID screen.
- State: merged_rejected_krylov_solver_substitution_and_source_operator_state.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a Ritz value, invariant subspace, kernel vector, or verified relation is not an ECDLP result.

## Falsifiable hypothesis

Construct a compact endpoint-derived nonsymmetric transition operator on source states, use Arnoldi orthogonalization to expose a small Hessenberg invariant subspace carrying an exact target/source section under restrictions, replay signed occurrences, and finish factor logs plus blind descent below rho and BSGS.

## Mechanism-new operation

The native operation builds an orthonormal Krylov basis and upper-Hessenberg projection by repeatedly applying a supplied linear operator and orthogonalizing. It counts only if the operator/matvec is endpoint-derived, the small projection preserves exact restricted kernels and occurrence provenance, and total orthogonalization/state fits the caps; replacing one solver on a supplied matrix is a control.

## Assumptions

1. Public endpoint data defines an exact low-cost transition operator without materializing source incidence.
2. A target-independent small Krylov dimension captures all restriction-relevant source strata.
3. Finite-field or exact-arithmetic Arnoldi avoids numerical-only convergence and preserves biconditional kernels.
4. A Hessenberg witness lifts to one occurrence-distinct signed tuple with charged ambiguity.
5. The same basis/operator serves known-log relations and fresh scalar-blind targets.

## Semantic fingerprint

`public_endpoint_nonsymmetric_transition_operator | Arnoldi_Krylov_Hessenberg_projection | exact_restricted_invariant_subspace | Hessenberg_witness_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact target predicate, source lift, rank, and descent frontier.
2. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — direct semantic owner for Krylov transition/kernel extraction and its full cost obligations.
3. `ideas/rejected/preallocation/20260719-d_D06_randomized_kaczmarz_source_projection_preid_duplicate.md` — iterative linear algebra assumes an explicit source system.
4. `ideas/rejected/ECDLP-IDEA-231_operator_scaling_shrunk_subspace_source_atomizer_hypothesis.md` — invariant/shrunk subspaces do not return source atoms without an exact section.
5. `ideas/rejected/ECDLP-IDEA-387_balanced_truncation_hankel_mode_source_reduction_hypothesis.md` — reduced operator modes can discard rare exact source directions.

## Closest primary literature

- Arnoldi, [The principle of minimized iterations in the solution of the matrix eigenvalue problem](https://doi.org/10.1090/qam/42792), builds a Hessenberg Krylov projection for a supplied matrix/operator.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations without the compact exact transition operator.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), gives the generic baseline.

No checked source constructs the source-free operator, proves small exact restricted Krylov dimension, or supplies occurrence inversion; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional strata, operator field/arithmetic, and independent point verifier.
2. Construct and certify the endpoint-derived operator, matvec, Krylov basis, Hessenberg projection, and source lift without explicit source-state materialization or scalar labels.
3. For each known-log target, impose at most `5 ceil(log_2 B)+O(1)` restrictions, extract/replay `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `R=Q+[t]P`, replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge operator construction, every matvec, basis vectors, orthogonalization, restrictions, source lift, density, rank, logs, blind descent, bit time, and peak memory.

## Full rho/BSGS cost model

Charge operator/basis setup in `a,a_m`, restricted projection/lift in `q,q_m`, and outputs/ambiguity in `o,u`. With `B=N^beta`, `beta=1/5`, `delta,delta_t,r,ell,ell_m` as usual, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS remain `0.50`.

## Likely fatal obstruction

Arnoldi changes the linear-algebra backend after an exact operator and matvec exist. The source transition operator is itself the missing incidence representation, and generic exact Krylov dimension can be source-scale. Orthogonalization stores many full vectors; a small approximate Ritz space need not preserve zero/nonzero decisions or rare occurrence directions. Exact source lifting remains outside the Hessenberg projection.

## Proof track

Construct a source-free exact operator with a proved uniformly small restriction-stable Krylov dimension and exact Hessenberg-to-occurrence inverse, then charge complete operator, basis, rank, and descent costs.

## Disproof track

Audit operator entries/matvec traffic, measure minimal polynomials and source-lift ambiguity under adversarial restrictions, and falsify on supplied matrices, source-scale basis, false kernel decision, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied low-minimal-polynomial operators with planted labelled kernel/source vectors.
- Negative: random full-degree operators, rare directions orthogonal to early Krylov spaces, defective/repeated spectra, empty restrictions, and fresh targets.
- Baselines: explicit Arnoldi, block Krylov IDEA-056, Kaczmarz, balanced truncation, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only operator construction, four increasing sizes, zero false kernel decisions, exact replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied operator state, Krylov/source dimension beyond caps, one lift failure, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l12_operator_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l12_arnoldi_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l12_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only Arnoldi transplant as a Krylov solver substitution, not Arnoldi iteration on supplied operators. Every finite projection remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not execute an experiment.
