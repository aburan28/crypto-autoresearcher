# Pre-ID duplicate draft — Hestenes–Stiefel conjugate source solver

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R01`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_symmetric_system_krylov_solver`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; convergence, a valid relation, or a verifier pass is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, public endpoint equations induce a target-independent symmetric
positive-definite source-incidence system whose conjugate directions recover exact signed
factor-base occurrences. Relation collection, full factor logs, and 100 fresh scalar-blind
descents then have complete time and memory exponents at most `0.45`.

## Mechanism-new operation

The native operation minimizes a quadratic over successively `A`-conjugate directions, using
matrix-vector products and residual inner products. It counts as new here only if the SPD
operator is compiled from public endpoints without source rows and its solution has a charged,
restriction-stable inverse to actual signed occurrences. Running CG after materializing source
incidence is a solver control.

## Assumptions

1. An endpoint-only compiler produces the SPD operator and right-hand side inside the setup cap.
2. Operator application does not enumerate factor-base tuples or use scalar-labelled samples.
3. Conditioning, precision, and iteration count stay inside the online cap on all restrictions.
4. The recovered vector determines signs, multiplicities, and occurrence identities exactly.
5. Byte-identical target-independent state serves relations and fresh masked targets.

## Semantic fingerprint

`public_endpoint_spd_operator | conjugate_direction_residual_minimization | exact_source_vector | charged_signed_occurrence_inverse | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — owns public Krylov compression only if the transition operator is already available.
2. `ideas/rejected/preallocation/20260719-d_D06_randomized_kaczmarz_source_projection_preid_duplicate.md` — projection iterations begin from a supplied source matrix.
3. `ideas/rejected/preallocation/20260721-d_L12_arnoldi_hessenberg_source_projection_preid_duplicate.md` — Krylov projection does not compile source incidence.
4. `ideas/rejected/preallocation/20260721-d_L11_nesterov_accelerated_source_relaxation_preid_duplicate.md` — accelerated relaxation is a downstream optimizer.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — owns the missing endpoint-derived exact restricted predicate and signed replay.

## Closest primary literature

- Hestenes and Stiefel, [Methods of Conjugate Gradients for Solving Linear Systems](https://nvlpubs.nist.gov/nistpubs/jres/049/jresv49n6p409_a1b.pdf), solves a supplied SPD linear system by conjugate directions.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but not the claimed SPD source compiler.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic cost control.

The ECDLP compiler and exact occurrence inverse are not supplied by the CG paper; novelty is
unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, factor base, signs, restrictions, SPD compiler, preconditioner, precision, stopping rule, exceptional strata, and verifier.
2. Compile the target-independent operator within `B^(9/4+o(1))`, rejecting any source tuple, scalar residue, or hidden decomposition oracle.
3. For each known-log target, solve the restricted system, replay a signed occurrence, and verify the elliptic sum before admitting a row.
4. Collect at least `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve every factor log.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, recover points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge compilation, preconditioning, all iterations, precision, failures, replay, rank, logs, bit complexity, and peak live memory.

## Full rho/BSGS cost model

Let setup/state be `N^a,N^a_m`; relation and target reciprocal densities be
`N^delta,N^delta_t`; one solve/workspace be `N^q,N^q_m`; verified-rank credit be `N^r`;
output be `N^o`; ambiguity be `N^u`; and factor-log time/memory be `N^ell,N^ell_m`.
For `beta=1/5`, charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires
`lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace
`<=B^(5/4+o(1))`. Pollard rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

The SPD matrix is the source-incidence object. Constructing its rows or applying it exactly
requires the missing restricted source predicate, while approximate or ill-conditioned solves
cannot distinguish an empty fibre from a rare nonempty fibre or replay occurrence identities.

## Proof track

Prove an endpoint-only SPD compiler, subcap conditioning and iterations, exact all-strata
restriction stability, and a signed inverse through full-rank relations and blind descent.

## Disproof track

Expose one source-bearing matrix entry, exponential condition number, precision blowup,
fractional/nonunique output, restriction rebuild, or a complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy SPD incidence matrix with one planted integral source vector.
- Negative: equal spectra with different source rows, empty fibres, near-singular systems,
  exceptional additions, and fresh blind targets.
- Baselines: block Krylov, randomized Kaczmarz, P1553 R4, rho, and BSGS.
- Linear-solver correctness is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with zero semantic errors at four sizes/all strata, full rank/logs, 100 blind
  descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one supplied source row, nonintegral ambiguity, missed empty fibre, cap violation,
  or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r01_spd_compiler_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r01_conditioning_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r01_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not conjugate gradients. All evidence would be toy, heuristic,
model-bound, and novelty-unverified; convergence or a valid row is not a breakthrough.

## Exactly one next executable action

1. Expand one claimed endpoint-only matrix-vector product into base-field operations and preserve the first source-bearing lookup or prove exact signed replay within both caps.
