# ECDLP-IDEA-274 — Mather-Yau moduli-algebra source reconstruction

## Status and claim labels

- Class: `representation_changing`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_moduli_algebra_reconstructs_compiled_germ_not_canonical_source_branch`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a reconstructed germ, Tjurina algebra, valid relation, recovered branch, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Source equations for an ECDLP relation or target descent can be compiled into an isolated hypersurface singularity whose finite moduli/Tjurina algebra determines the germ and canonically exposes its rational branches.  Reconstructing the germ and selecting its target branch would return exact factor points or `x` below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the source fiber into an isolated singularity, compute its moduli algebra, reconstruct the analytic/formal germ, and extract the rational source branches**.  This is a representation-changing reconstruction theorem rather than a dense resultant or solver swap.  The classical Mather-Yau theorem is characteristic-zero analytic and reconstructs a germ up to contact equivalence from an already supplied finite algebra; it does not name rational roots of a positive-characteristic source system.  A compilation whose moduli algebra retains every source branch has dimension/structure tracking the dense fiber, while contact equivalence does not provide the target-selected branch or elliptic-curve return.  The proposal therefore merges with local-algebra, quotient-ring, and source-materialization negatives.

## Assumptions

1. Public summation/source equations admit a target-uniform compilation to an isolated hypersurface germ over a suitable lift or field.
2. A positive-characteristic or lifted Mather-Yau-type reconstruction is effective, branch-faithful, and below rho.
3. Contact-equivalence data and the moduli algebra admit a canonical inverse to exact finite-field factor points for every target stratum.
4. Compilation, lift precision, algebra basis, multiplication tables, germ reconstruction, branches, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | isolated_singularity_compilation | Tjurina_moduli_algebra | germ_reconstruction | rational_source_branch_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the quotient/local-algebra representation hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the scalar-coordinate and orientation barrier.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the reconstructed invariant without source inverse control.
5. `inputs/ledger_inventory.json` — imported `P1478`, the dense source-state and output frontier.

## Closest primary literature

- Mather and Yau, [Classification of isolated hypersurface singularities by their moduli algebras](https://homepages.math.uic.edu/~yau/35%20publications/Classification.pdf), proves the characteristic-zero analytic reconstruction theorem motivating the operation.
- K. Saito, [Period Mapping Associated to a Primitive Form](https://doi.org/10.2977/prims/1195182028), develops the primitive-form and singularity framework adjacent to reconstructing richer germ data.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the positive-characteristic source equations to be compiled.

No checked source provides the required positive-characteristic branch-faithful compilation or sub-rho source return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the finite-field instance, source equations, singularity compiler, lift/reduction rule, algebra representation, factor base, masks, and verifier.
2. Compile known-log relation endpoints into isolated germs and compute their complete moduli algebras without enumerating source tuples.
3. Reconstruct each germ, enumerate every finite-field rational branch under the frozen return map, and map accepted branches to exact signed factor points.
4. Verify relations, collect independent rows, solve every factor log, and verify recovered logs.
5. Compile fresh masked targets `Q+[t]P` with the identical rule and reconstruct their germs from the moduli algebras.
6. Return all rational source branches, obtain a complete factor decomposition or scalar residue, remove the mask, and verify exact equality.
7. Accept only `[x]P=Q`, charging lift search, algebra dimension, multiplication data, reconstruction, branch output, factor logs, descent, and live state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one compile/algebra/reconstruct/branch-return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, branch output be `N^o`, contact/lift ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every lifted coefficient, local-algebra basis element, multiplication entry, contact-equivalence choice, reconstructed monomial, rational branch, failed return, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Mather-Yau reconstructs the supplied isolated germ only up to an equivalence and in a setting unlike the positive-characteristic finite source fiber.  It is not a root-extraction theorem and supplies no canonical rational branch.  Preserving all factor tuples in a zero-dimensional local/moduli algebra forces its dimension or multiplication data to scale with the source multiplicity, while compressing it identifies branches.  Lifting to characteristic zero adds noncanonical choices and still leaves reduction and target branch selection unsolved.

## Proof track

Prove a characteristic-appropriate target-uniform compiler, compact branch-faithful moduli algebra, effective exact reconstruction and finite-field return, with both complete exponents at most `0.45`.

## Disproof track

Exhibit positive-characteristic counterexamples or branch collisions, prove the algebra dimension/output tracks the source deck, show contact equivalence loses rational labels, show lifting is noncanonical, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied characteristic-zero isolated hypersurface germ with its exact Tjurina algebra and labelled analytic branches.
- Negative controls: non-isolated source fibers, inseparable characteristic-`p` germs, contact-equivalent germs with different rational labels, dense quotient algebras, resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a branch-faithful algebra and compiler of exponent at most `0.45`, exact all-strata finite-field return, blind descent, and complete `lambda,mu<=0.45`.  Reconstruction only up to contact equivalence, branch collisions, algebra/output/state at least `N^0.50`, noncanonical lift, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-274/mather_yau_source_reconstruction_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-274/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-274/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-274/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation-changing proposal.  Every finite reconstruction would be toy and projections heuristic and model-bound.  A correct germ or Tjurina algebra does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-274/mather_yau_source_reconstruction_theorem.md` proving branch-faithful finite-field reconstruction or the characteristic/dimension/branch obstruction.
