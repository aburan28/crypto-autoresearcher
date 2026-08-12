# Pre-ID duplicate draft — McMillan Craig-interpolant source separator

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q08`; no canonical ID allocated.
- Disposition: `merged_rejected_unsat_certificate_without_source_return`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; an interpolant, UNSAT proof, or excluded fibre is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, partition an endpoint/source formula and derive Craig
interpolants from failed bounded searches. Iterated interpolants form an exact
target-independent separator for empty versus nonempty restricted fibres, while positive
traces replay signed occurrences for rank-complete relations and 100 blind descents below
exponent `0.45`.

## Mechanism-new operation

The native operation extracts an interpolant over shared variables from an unsatisfiability
proof and iterates it as an overapproximate image. It counts only if the partitioned formulas
and proofs are endpoint-derived, the separator is exact for all restrictions, and positive
cases return occurrences without a separate source solver. Using interpolants only to prune
an explicit source search is a control.

## Assumptions

1. Endpoint/source formula partitions are constructed without enumerated source clauses or scalar labels.
2. Proof production and interpolant size stay within the setup and online caps.
3. Iteration converges to exact nonemptiness rather than only a sound exclusion.
4. Positive cases retain a charged signed trace on every exceptional stratum.
5. One target-independent separator serves relations and fresh masked targets.

## Semantic fingerprint

`public_endpoint_formula_partition | craig_interpolant_image_refinement | exact_restricted_separator | positive_trace_signed_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260722-a_N02_davis_putnam_source_resolution_elimination_preid_duplicate.md` — resolution proofs start from supplied source clauses.
2. `ideas/rejected/preallocation/20260722-a_N04_grasp_conflict_clause_source_search_preid_duplicate.md` — learned clauses are a solver artifact, not an endpoint compiler.
3. `ideas/rejected/preallocation/20260722-b_O08_provan_shier_minimal_cut_source_listing_preid_duplicate.md` — separation certificates do not replay positive source occurrences.
4. `ideas/rejected/ECDLP-IDEA-138_sumcheck_source_self_reduction_hypothesis.md` — certificates and self-reduction still need exact source-return queries.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- McMillan, [Interpolation and SAT-Based Model Checking](https://doi.org/10.1007/978-3-540-45069-6_1), derives interpolants from supplied unsatisfiable bounded-model-checking formulas to overapproximate reachable states.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not compact proofs, exact separators, or positive replay.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

Interpolation is native-scope distinct, but its negative certificates do not construct the
positive endpoint-to-source inverse. Formula/proof construction remains charged and novelty
is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, formula partition, proof system, interpolation system, image iteration, restrictions, positive replay, strata, and verifier.
2. Build target-independent formulas/separator state within `B^(9/4+o(1))`; forbid source tables, target fitting, scalar residues, and hidden decomposition calls.
3. For each known-log target, decide the restricted fibre, replay a positive signed occurrence or preserve the negative proof, and verify each elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs while charging formulas, SAT/proofs, interpolants, iterations, output, and sparse linear algebra.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge proof construction/checking, interpolant size, every SAT query and refinement, restrictions, failures, positive replay, rank, logs, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, proof/query workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; proof and interpolant output are charged.
Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh
work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain exponent-`0.50` controls.

## Likely fatal obstruction

Craig interpolation starts with an UNSAT proof over supplied formulas and yields a separator,
not a positive witness. Building source-complete formulas reproduces the relation circuit;
positive replay still invokes SAT/source search, while exact convergence can require large
proofs or one refinement per source state.

## Proof track

Prove endpoint-only formula construction, subcap proof/interpolant size, exact convergence
under all restrictions, positive signed replay, and complete relation/log/descent costs.

## Disproof track

Expose source clauses, a proof/interpolant blowup, a false/missed separator, positive-source
solver call, restriction rebuild, lost replay, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy transition formula with one UNSAT partition and one labelled reachable trace.
- Negative: identical shared projections with different source satisfiability, empty fibres, hard proof families, interpolant-system mutations, and blind targets.
- Baselines: resolution, GRASP/CDCL, CEGAR, P1553 R4, rho, and BSGS.
- A checked UNSAT proof is only toy/model-bound negative evidence.

## Quantitative promotion and falsification gates

- Promote only with exact separators and positive replay at four sizes/all strata, bounded proofs/iterations, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one supplied source formula, separator/replay error, proof cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q08_formula_partition_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q08_interpolant_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q08_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Craig interpolation. All evidence remains toy, heuristic,
model-bound, and novelty-unverified; an UNSAT proof or valid positive trace is not a
breakthrough.

## Exactly one next executable action

1. Expand one proposed interpolation partition through proof generation and preserve the first source-complete clause set or separate positive-source solver it requires.
