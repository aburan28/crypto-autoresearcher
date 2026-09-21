# Pre-ID duplicate draft — Collins CAD endpoint-cell source section

## Status and claim labels

- Prospect: `20260721-b-J04`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algebraic_cell_decomposition / representation-changing / representation pre-ID screen.
- State: solver_substitution_rejected_wrong_field_and_dense_projection.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no dispatchable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a sign-invariant cell or correct solver answer is not an ECDLP result.

## Falsifiable hypothesis

Lift finite-field endpoint equations to a bounded real-algebraic encoding, use cylindrical algebraic decomposition to partition target space into sign-invariant cells, and store a restriction-stable exact source section per positive cell under complete sub-rho cost.

## Mechanism-new operation

The native operation repeatedly projects and lifts polynomial sign information to obtain cylindrical cells for real quantifier elimination. It counts only if the lift is exact for finite-field arithmetic, cell construction is endpoint-only, and a cell section returns labelled finite-field sources; applying CAD to a supplied source formula is a solver control.

## Assumptions

1. Prime-field addition, multiplication, inverses, and exceptional elliptic charts have a bounded-variable exact real encoding with no growing carries.
2. Projection polynomials and cells fit `B^(9/4+o(1))` state.
3. Target restrictions map to cells in `B^(5/4+o(1))` work without target-trained advice.
4. Every positive cell has an exact signed occurrence section; nonreduced and boundary cases are complete.
5. Cell reuse yields independent relations, factor logs, and fresh blind descent.

## Semantic fingerprint

`public_endpoint_real_lift | Collins_projection_lifting_CAD | sign_invariant_restricted_cell_decision | cell_section_to_finite_field_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact finite-field source-return frontier.
2. `ideas/rejected/ECDLP-IDEA-125_uniform_cell_skolem_source_section_hypothesis.md` — uniform cells and Skolem sections require the missing source construction.
3. `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md` — projection trees operate after a represented algebra exists.
4. `ideas/rejected/ECDLP-IDEA-378_comprehensive_groebner_target_atlas_hypothesis.md` — target atlases are dense solver substitutions without source lift.
5. `ideas/rejected/ECDLP-IDEA-063_provenance_preserving_subresultant_forest_hypothesis.md` — projection/resultant propagation starts from supplied coefficients.

## Closest primary literature

- Collins, [Quantifier elimination for real closed fields by cylindrical algebraic decomposition](https://doi.org/10.1007/3-540-07407-4_17), supplies projection and lifting over real closed fields.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies finite-field endpoint equations, not a bounded real encoding with source sections.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source supplies an exact compact finite-field-to-real CAD compiler or labelled source lift; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the prime-order curve, field encoding, factor base, signed decks, all charts, restrictions, and point verifier.
2. Build the exact real formula, CAD projection set, lifted cells, and source-section certificates from public endpoints without enumerating tuples.
3. For each known-log target, perform exact restricted cell decisions and at most `5 ceil(log_2 B)+O(1)` self-reductions, replay a labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged CAD state for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge lift/carry constraints, projection polynomials, cell counts, algebraic-number operations, boundary strata, source sections, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge `T_lift+T_project+T_cells` and `M_polys+M_cells` in `a,a_m`; charge sign evaluation, cell location, and source lifting in `q,q_m`. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, counting degrees, coefficient heights, and bit complexity. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS are `0.50`.

## Likely fatal obstruction

CAD is a real-closed-field algorithm, whereas exact finite-field wraparound and inverses require growing bit/carry variables or nonlinear integer constraints. Even granting a lift, projection polynomials and cells can grow doubly exponentially in variables, and a representative real sample point is not a labelled finite-field source. The source formula itself already contains the missing incidence.

## Proof track

Give a bounded-variable exact lift, prove projection/cell and coefficient-height bounds, and construct an all-strata cell-to-source section with complete costs.

## Disproof track

Audit carries, wraparound, inverses, projection degrees, cell counts, and sample-point lifts; falsify on wrong-field equivalence, source-bearing input, dense growth, or missing boundary provenance.

## Positive and negative controls

- Positive: low-dimensional real semialgebraic systems with known sign cells and labelled rational samples.
- Negative: modular wraparound pairs, growing carries, nonreduced boundaries, empty restrictions, duplicate sources, and fresh targets.
- Baselines: comprehensive Gröbner systems, subresultants, uniform-cell Skolemization, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with a proved exact field lift, four growing instances, zero false decisions, complete boundary/source sections, full-rank relation collection, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on semantic mismatch, source-bearing formula construction, cell explosion, label loss, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j04_field_lift_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j04_cad_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j04_cost_analysis.md`

## Interpretation boundary

This rejects the stated finite-field endpoint CAD transplant, not CAD over real closed fields. Any finite result is toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct or run an experiment.
