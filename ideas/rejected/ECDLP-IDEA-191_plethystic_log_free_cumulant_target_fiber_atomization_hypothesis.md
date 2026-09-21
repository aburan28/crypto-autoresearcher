# ECDLP-IDEA-191 — Plethystic-log/free-cumulant target-fiber atomization

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation_changing`
- Top lane: `none`
- State: `scoped_negative_cumulants_aggregate_moments_without_atoms`
- Cohort: `20260718-d`
- Evidence scale: checked primary literature and semantic preflight only; no experiment ran
- Contract posture: rejected at the compact moment-oracle and labeled-atom gates; no contract or run is authorized
- Scale labels: every future finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a cumulant identity, plethystic logarithm, relation count, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-only generating object supplies compact target-fiber moments whose plethystic logarithm or free-cumulant Möbius inversion separates the fiber into exact signed factor-point atoms, not just counts or isomorphism classes. Evaluated on known-log endpoints and fresh masked targets, those atoms would give complete factor-base relations and blind target descent with time and memory exponents below rho and BSGS.

## Mechanism-new operation

The proposed operation is **target-fiber moment construction followed by plethystic logarithm/free-cumulant inversion into labeled elliptic source atoms**. It is mechanism-new only if finitely many compact moments are computed directly from the endpoint and the inversion returns exact factor identities with multiplicity. Moments obtained by enumerating sources, a full coefficient table, post-hoc atom matching, relation counts, or a generic solver are controls.

The scoped result is negative. Moment-cumulant and plethystic-log formulae invert a supplied aggregate function into connected or indecomposable aggregate contributions. They do not manufacture labels absent from the moments. Supplying enough endpoint moments to recover every factor point is equivalent to a source enumerator or a full output-sized transform, so the operation remains behind the aggregate-to-labeled-source boundary.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta,m`, moment species/algebra, truncation rule, masks, and verifier are frozen.
2. A compact scalar-blind oracle computes all moments needed for inversion from one endpoint without source enumeration.
3. Plethystic or noncrossing-partition inversion returns exact signed factor-point identities, repeats, multiplicities, cancellations, infinity, and every declared stratum.
4. Moment order, coefficient precision, atom output, and ambiguity remain below generic time and memory rather than encoding all `B^m` tuples.
5. Moment construction, inversion, output, density, rank, factor logs, target descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`compact_endpoint_fiber_moments | plethystic_log_or_free_cumulant_Mobius_inversion | labeled_factor_point_atoms | exact_source_tuples | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, the additive aggregate-character boundary.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the full-phase nonlinear reconstruction boundary.
3. `inputs/ledger_inventory.json` — imported `P1478`, the closest aggregate transition/resultant proposal.
4. `inputs/ledger_inventory.json` — imported `P1479`, the closest representation-to-source proposal.
5. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the nearest independent aggregate/source review result.

## Closest primary literature

- Speicher, [Multiplicative functions on the lattice of non-crossing partitions and free convolution](https://eudml.org/doc/165189), derives free cumulants by Möbius inversion of supplied moment data.
- Nica and Speicher, [A “Fourier Transform” for Multiplicative Functions on Non-Crossing Partitions](https://doi.org/10.1023/A:1008643104945), develops noncrossing-partition cumulant combinatorics without an endpoint oracle for labeled elliptic atoms.

These primary sources transform supplied aggregate data; neither supplies a compact finite-field endpoint-moment oracle or exact factor-point source inverse, so novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B=N^beta,m`, the factor base, moment algebra, partition lattice, truncation, masks, exceptional strata, and verifier.
2. Define a scalar-blind endpoint oracle that produces every required fiber moment compactly without enumerating signed factor-base tuples.
3. For known-log endpoints `R_j=[r_j]P`, compute moments and apply the frozen plethystic-log or free-cumulant inversion to return all labeled factor-point atoms and their exact tuple incidence.
4. Verify every decoded tuple sum and preserve repeats, cancellations, infinity, moment collisions, misses, multiplicities, truncation errors, and full atom output.
5. Collect at least `B+sigma` verified independent relation rows of rank `B`, solve factor-base logs, and independently verify every recovered logarithm.
6. Apply the identical oracle and inversion to fresh masked targets `Q+[t]P`, with masks selected independently after setup.
7. Substitute verified factor logs, remove masks, retain all atom/tuple ambiguity candidates, and accept only `x` satisfying `[x]P=Q`.
8. Charge moment construction, coefficient precision, partition inversion, atom matching, source output, failed endpoints, rank, descent, total time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant-sized state; BSGS costs `N^(1/2+o(1))` time and memory. Let the endpoint moment oracle have time and memory exponents `a,a_m`; let reciprocal relation and target densities be `N^delta,N^delta_t`; let one plethystic/cumulant inversion cost `N^q,N^q_m`; let labeled atom output and target ambiguity have exponents `o,u`; and let factor-log algebra have exponents `ell,ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every moment coefficient, truncation order, partition, cumulant, atom label, tuple incidence, failed endpoint, and verification is charged.

## Likely fatal obstruction

Cumulants and plethystic logarithms recover connected aggregate contributions from supplied moments; they cannot distinguish point identities that the moments aggregate together. Exact labeled atoms require sufficiently many separating moments, and constructing those moments from an endpoint entails all-source enumeration, a source-indexed test family, or output on the scale of `B^m`. Coarse moments instead return counts or classes, not the factor leaves needed for logs and descent.

## Proof track

Specify a bounded endpoint-only moment family, prove its inversion is biconditional with every exact signed factor tuple on all strata, prove the moments and atoms are neither source-indexed nor output-sized, and derive complete blind-descent exponents `lambda,mu<=0.45`.

## Disproof track

Exhibit two source fibers with identical bounded moments but different labeled atoms, prove a separating moment basis indexes the sources, reduce the oracle to enumeration, show inversion returns only counts/classes, or derive `max(lambda,mu)>=0.50` after full precision and output charging.

## Positive and negative controls

- Positive control: published moment/cumulant pairs with supplied distributions and exact Möbius inversion.
- Positive control: toy elliptic source multisets supplied explicitly to test the algebraic inversion only.
- Negative control: source-label permutations and distinct multisets matched on all preregistered bounded moments.
- Negative control: explicit source enumeration, full coefficient tables, dense resultants, relation-only counts, rho, BSGS, known-log endpoints, and blind masked targets.

## Quantitative promotion and falsification gates

The present operation remains a scoped negative. A distinct successor must give a compact public moment oracle, 100% exact source/multiplicity recall with zero false tuples on preregistered toy strata, no source-indexed tests, and formal `lambda,mu<=0.45`. If `0.45<max(lambda,mu)<0.50`, the result is inconclusive; aggregate-only output, any collision or omitted tuple, output-sized moments, or `max(lambda,mu)>=0.50` falsifies it.

## Artifact plan

- Prospective oracle theorem: `ideas/artifacts/ECDLP-IDEA-191/compact_endpoint_moment_oracle_theorem.md`
- Prospective atomization biconditional: `ideas/artifacts/ECDLP-IDEA-191/cumulant_atomization_biconditional.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-191/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-191/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-191/cost_analysis.md`

All paths are prospective. No artifact root, contract, experiment, or run exists or is authorized.

## Interpretation boundary

This is rejected, novelty-unverified aggregate-representation evidence. Future finite checks would be toy and all projections heuristic and model-bound. A valid cumulant identity, correct relation count, or known-log result is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-191/cumulant_atomization_biconditional.md` proving whether a bounded endpoint-derived moment family can return exact labeled factor-point atoms or only aggregate source classes.
