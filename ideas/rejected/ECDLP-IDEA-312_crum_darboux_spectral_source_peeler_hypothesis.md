# ECDLP-IDEA-312 — Crum–Darboux spectral source peeler

## Status and claim labels

- Class: `spectral_representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_darboux_peeling_requires_supplied_spectral_data_and_loses_point_labels`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an isospectral identity, correct eigenvalue deletion, valid relation, or toy peel is not an ECDLP break.

## Falsifiable hypothesis

An elliptic endpoint and its factor-source incidence can be compiled into a compact discrete Sturm–Liouville or Jacobi operator whose Crum iteration of Darboux transformations deletes one source eigenstate at a time, so the deleted eigenvalues and norming data canonically lift to exact signed factor points for reusable relations and blind target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile endpoint incidence into a Jacobi operator and apply a Crum chain of Darboux factorizations to peel spectral states, mapping each deleted state back to an exact factor point**. This is more specific than a generic eigenvalue solver: it uses successive intertwining transformations for a fixed operator with admissible seed and boundary/normalizability conditions. A Darboux step requires a seed eigenvalue/eigenfunction, and inverse spectral recovery generally needs additional norming or boundary data. In the proposed construction, a point-faithful operator or seed list would encode the source deck, so the operation merges with IDEAs 186, 213, 267, 278, and 279.

## Assumptions

1. Every elliptic endpoint fiber has a compact target-uniform self-adjoint Jacobi representation constructible without enumerating its source tuples.
2. Each exact signed factor point corresponds canonically and biconditionally to one peelable eigenstate on every multiplicity and collision stratum.
3. Seed eigenfunctions, eigenvalues, and norming constants can be derived from the public endpoint rather than supplied as the hidden source.
4. Operator construction, spectral precision, Crum determinants, all seeds and outputs, relation rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`elliptic_endpoint_Jacobi_operator | Crum_Darboux_chain | spectral_state_deletion | eigenstate_to_exact_factor_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate expansion boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the transposed spectral-rank control without source return.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the aggregate phase versus exact-source gap.
5. `inputs/ledger_inventory.json` — imported `P1479`, the factor-log public-feature compression control.

## Closest primary literature

- Crum, [Associated Sturm–Liouville systems](https://doi.org/10.1093/qmath/6.1.121), derives iterated transformations from supplied eigenfunctions of a Sturm–Liouville operator; it does not discover hidden combinatorial source labels.
- Deift and Trubowitz, [Inverse scattering on the line](https://doi.org/10.1002/cpa.3160320202), shows the role of scattering and norming data in inverse spectral reconstruction rather than an endpoint-only source inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies algebraic endpoint constraints without a canonical self-adjoint operator or spectral source peel.

No checked source gives the finite-field Jacobi compiler, seed-free Crum inverse, point-faithful lift, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed factor base, public Jacobi compiler, spectral normalization, Crum order, masks, and independent verifier.
2. For random known-log endpoints, build the operator without enumerating factor tuples, eigenstates, or source-labelled seeds.
3. Derive a seed from public spectral data, execute one Darboux deletion at a time, lift every deleted state to an exact signed factor point, and verify the elliptic relation.
4. Collect independent verified rows, solve the relation matrix, and independently verify every factor-base logarithm.
5. Apply the identical operator compiler and Crum peeler to fresh masked targets `Q+[t]P` without target-trained seeds or post-hoc spectral selectors.
6. Substitute factor logs, remove masks, preserve multiplicity and inverse-spectral ambiguity, and return all scalar candidates.
7. Accept only exact `[x]P=Q`, charging operator construction, precision, factorizations, seeds, norming state, outputs, failures, rows, logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one Crum–Darboux peel/inverse `N^q,N^q_m`, rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes operator construction, exact spectral arithmetic, seed derivation, every Darboux factorization, point lifting, and verification; `o` includes all peeled states and ambiguous point lifts. Rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

For a fixed operator, a Darboux deletion depends on an admissible seed eigenfunction together with the relevant boundary and normalizability conditions; those data are not constructed by the public endpoint in this proposal. Spectral data without the additional norming or boundary information need not determine the labelled inverse sought here. If the Jacobi matrix, norming table, or seed chain is built by explicitly indexing factor points, it imports the source deck rather than recovering it. Finite-field elliptic data additionally lack a canonical ordered self-adjoint lift whose spectral labels survive reduction.

## Proof track

Construct a compact exact Jacobi compiler and prove that public spectral data select every Crum seed and lift it biconditionally to exact signed factors on all strata; then prove independent row rank, factor logs, blind descent, and `lambda,mu<=0.45` including precision and output.

## Disproof track

Produce admissible operators or Darboux chains with the same accessible endpoint data but different factor labels, show that the required seed/norming/boundary input reconstructs the source deck in the frozen construction, or account for any explicitly point-faithful operator/precision/output that reaches exponent `0.50` or worse.

## Positive and negative controls

- Positive: a supplied toy Jacobi matrix with labelled eigenstates and seeds must reproduce the known Crum deletions and point map.
- Negative: isospectral or norming-constant-perturbed operators with identical eigenvalues must not be accepted as the same exact factor source.
- Baselines: dense eigendecomposition, explicit source enumeration, IDEAs 186/213/267/278/279, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with independent all-strata source biconditionals, 1,000 verified relation rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if a seed eigenfunction or norming table supplies the source, isospectral ambiguity changes point labels, any stratum fails, or operator/state/output/precision cost reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-312/darboux_source_peeling_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-312/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-312/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-312/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of the stated spectral peeler, not an impossibility theorem for all Darboux or inverse-spectral techniques. Correct eigenvalue deletion, a valid relation, or toy source recovery does not establish complete target descent or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-312/darboux_source_peeling_theorem.md` proving a seed-free endpoint-to-state biconditional or an explicit isospectral/different-factor counterexample before any spectral experiment.
