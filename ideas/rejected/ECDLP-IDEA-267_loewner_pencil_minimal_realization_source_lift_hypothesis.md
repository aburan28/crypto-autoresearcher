# ECDLP-IDEA-267 — Loewner-pencil minimal-realization source lift

## Status and claim labels

- Class: `spectral_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_transfer_samples_or_source_degree_realization_required`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a low-rank pencil, an interpolant, a valid relation, a recovered source tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Scalar-blind endpoint queries provide two tangential sample sets of a rational source-resolvent whose Loewner and shifted-Loewner matrices have sub-rho rank.  A minimal descriptor realization would expose poles and residues biconditional with the exact factor points, enabling relation collection and fresh target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **derive endpoint-only tangential transfer samples, build the Loewner/shifted-Loewner pencil, and recover exact source poles from its generalized eigenstructure**.  The Loewner framework reconstructs a realization from supplied interpolation data; it does not produce source-sensitive transfer samples from one aggregate endpoint.  If the samples are moments or resolvent values of all compatible tuples, their computation or McMillan degree carries the source deck.  This merges with IDEA-041 Cauchy chords, IDEA-056 block Krylov, IDEA-071 displacement reporters, IDEA-194 fiber log derivatives, and IDEA-209 Hermite-Pade denominators once sample production, realization degree, and point lift are charged.  Backend changes and relation-only spectral certificates receive no mechanism credit.

## Assumptions

1. A frozen public query rule maps an endpoint to left and right tangential samples without known source points, factor logs, or a source table.
2. The resulting rational transfer function has McMillan degree and pencil rank below `N^0.45` while retaining exact signed factor-point poles or residues.
3. Generalized eigenvalues lift canonically to factor points on every singular, repeated, infinity, and collision stratum.
4. Sample generation, field extensions, pencil storage, rank decisions, eigenvalue output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`elliptic_endpoint | scalar_blind_tangential_samples | Loewner_shifted_Loewner_pencil | minimal_descriptor_realization | pole_residue_to_factor_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H679`, the compact cyclic-sequence hypothesis.
2. `inputs/ledger_inventory.json` — imported `P1474`, the orbit-sampling and recurrence boundary.
3. `inputs/ledger_inventory.json` — imported `P1477`, the dense serial-state control.
4. `inputs/ledger_inventory.json` — imported `ECFG-MX-1478`, the exact sparse-transition/dense-composition collision.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`, the compact-feature/source-orientation barrier.

## Closest primary literature

- Mayo and Antoulas, [A framework for the solution of the generalized realization problem](https://doi.org/10.1016/j.laa.2007.03.008), constructs descriptor realizations from supplied tangential interpolation data.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the endpoint relation equations but no source-sensitive transfer samples.

Neither source supplies an endpoint-only Loewner data oracle, exact point lift, or complete sub-rho ECDLP path.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F`, feature maps, left/right interpolation nodes, tangential directions, rank rule, masks, and verifier.
2. For known-log endpoints, evaluate the proposed transfer samples without source enumeration or factor-log advice.
3. Form Loewner and shifted-Loewner matrices, compute a minimal descriptor pencil, and recover every pole/residue branch.
4. Lift accepted spectral data to exact signed factor points and verify the elliptic sum; retain failures, multiplicities, and infinity branches.
5. Collect verified rows to rank `B`, solve factor logs, and verify them by scalar multiplication.
6. Apply the identical sample and realization procedure to fresh masks `Q+[t]P`, retaining all ambiguity.
7. Substitute logs, subtract masks, and accept only `[x]P=Q`, with complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one sample/realization/source inverse cost `N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be `N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every transfer sample, interpolation node, field operation, pencil entry, rank decision, eigenvalue, residue, failed endpoint, source output, relation, factor log, mask, and live byte is charged.

## Likely fatal obstruction

Loewner realization is an inverse for supplied transfer data, not an endpoint-to-transfer compiler.  Source-sensitive moments or resolvent samples already require the hidden tuple or aggregation over the full source fiber.  If that information is retained, the minimal realization degree tracks the number of source states; if it is compressed below that degree, distinct tuples share the same pencil and exact ancestry is lost.

## Proof track

Give a scalar-blind sample identity computable below `N^0.45`, prove a bounded-rank pencil with biconditional all-strata point lift, and complete factor-log and masked-target recovery with both exponents at most `0.45`.

## Disproof track

Show sample evaluation requires source moments or dense fiber aggregation, construct distinct source fibers with identical samples, prove McMillan degree tracks source degree, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied low-degree rational transfer function with independently labelled poles and exact tangential samples.
- Negative controls: endpoint-only aggregate samples, permuted poles, colliding residues, rank-truncated pencils, IDEA-041, IDEA-209, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires target-uniform sample generation, pencil rank and total output at most `N^0.45`, exact all-strata source recovery, full rank, blind descent, and complete `lambda,mu<=0.45`.  Supplied source samples, realization degree or output at least `N^0.50`, noncanonical pole lift, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-267/loewner_source_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-267/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-267/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-267/cost_analysis.md`

All four paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This novelty-unverified proposal is merged/rejected at the transfer-sample and realization-degree boundary.  Every finite check would be toy and every projection heuristic and model-bound.  A correct realization or recovered toy pole is not an ECDLP break or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-267/loewner_source_lift_theorem.md` proving an endpoint-only low-rank transfer identity or the sample-production/McMillan-degree obstruction.
