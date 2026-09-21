# ECDLP-IDEA-277 — Stable-envelope fixed-point source basis

## Status and claim labels

- Class: `representation_changing`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_quiver_fixed_point_basis_materializes_source_alphabet`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a stable envelope, fixed-point coefficient, valid relation, recovered label, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform Nakajima-quiver or symplectic-resolution realization of the ECDLP source fiber has a stable-envelope basis indexed by factor tuples, while a compact endpoint state is given in a geometric basis.  Applying stable-envelope and Baxter/quantum-group transforms would reveal the exact fixed-point/source label below rho and BSGS.

## Mechanism-new operation

The screened operation is **realize source tuples as torus fixed points of a symplectic resolution, apply chamber-dependent stable-envelope basis change and commuting quantum operators, and invert the endpoint state to a fixed-point label**.  This is a geometric-representation basis change, not an ordinary solver substitution.  Stable envelopes act after the variety, torus action, chamber, polarization, and fixed-point set are supplied.  Making fixed points correspond bijectively to factor tuples constructs the source alphabet; a state resolving all labels has matching rank/output, while a compressed geometric state has collisions and no canonical endpoint-selected basis vector.  It merges with character/spectral transforms, direct labels, and materialized-product negatives after state and basis costs are charged.

## Assumptions

1. Public source equations and endpoint canonically determine a compact quiver variety or symplectic resolution without enumerating source tuples.
2. Its torus fixed points biject with all exact factor tuples, and stable envelopes/quantum operators remain computable below rho.
3. The endpoint determines a compact state whose fixed-point expansion has one recoverable label and an exact factor return.
4. Variety construction, fixed points, chambers, polarization, stable-envelope matrix, quantum operators, output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | quiver_symplectic_source_realization | stable_envelope_basis_change | fixed_point_label_decode | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank basis transform without source inversion control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the materialized source-product control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the compressed row invariant without source output control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the geometric representation and exact-return boundary.

## Closest primary literature

- Maulik and Okounkov, [Quantum Groups and Quantum Cohomology](https://doi.org/10.24033/ast.1074), constructs stable envelopes and their relation to quantum groups for symplectic resolutions.
- Maulik and Okounkov, [Quantum Groups and Quantum Cohomology, preprint](https://arxiv.org/abs/1211.1287), gives the detailed primary construction and fixed-point framework.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations whose tuples would have to become fixed points.

No checked source gives a compact ECDLP source realization or endpoint-state-to-fixed-point inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the source equations, quiver/symplectic compiler, torus action, chamber and polarization, stable-envelope convention, factor base, masks, and verifier.
2. Construct the variety, fixed-point scheme, endpoint state, and stable-envelope/quantum operators for known-log relations without source enumeration.
3. Expand the state in the fixed-point basis, decode every accepted label, and return exact signed factor points.
4. Verify relations, collect independent rows, solve and verify every factor log.
5. Apply the identical frozen construction to fresh masked targets `Q+[t]P`.
6. Decode all surviving fixed-point branches to a complete factorization or scalar residue, remove the mask, and verify the endpoint.
7. Accept only exact `[x]P=Q`, charging variety/fixed-point construction, stable-envelope entries, operator evaluation, output ambiguity, factor logs, descent, and peak state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one realization/envelope/operator/decode attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, fixed-point output be `N^o`, state ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every quiver vertex/arrow, stability parameter, fixed point, chamber wall, polarization weight, envelope coefficient, quantum-operator entry, failed label, source branch, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Stable envelopes give an invertible change of basis only after the fixed-point set and geometric representation are built.  If fixed points enumerate source tuples, their construction and the envelope matrix materialize the deck; if the representation is compressed, multiple tuples share states or eigenvalues.  Nothing in the public endpoint canonically selects a single fixed-point vector.  Thus the transform reorganizes supplied source information but does not create the missing section from endpoint to factor tuple.

## Proof track

Construct a compact target-uniform quiver realization with injective fixed-point labels, prove endpoint-state selection and exact factor return, and certify complete exponents at most `0.45`.

## Disproof track

Prove fixed-point/state rank or envelope output at least `N^0.50`, exhibit label collisions under compression, show endpoint-state construction imports the source, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small Nakajima variety with known torus fixed points and a labelled stable-envelope matrix.
- Negative controls: permuted fixed-point labels, compressed representations with repeated weights, random endpoint states, explicit source tables, character transforms, materialized products, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-faithful realization and basis transform of exponent at most `0.45`, exact all-strata endpoint-state selection, blind descent, and complete `lambda,mu<=0.45`.  Fixed-point collisions, source-labelled input, representation/output/state at least `N^0.50`, missing factor return, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-277/stable_envelope_source_basis_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-277/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-277/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-277/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation-changing proposal.  Every finite quiver check would be toy and projections heuristic and model-bound.  A valid stable envelope, eigenvalue, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-277/stable_envelope_source_basis_theorem.md` proving compact fixed-point selection and factor return or the representation-rank/source-state obstruction.
