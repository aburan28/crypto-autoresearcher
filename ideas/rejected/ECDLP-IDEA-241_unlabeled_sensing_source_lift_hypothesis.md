# ECDLP-IDEA-241 — Unlabeled-sensing source lift

## Status and claim labels

- Class: `inverse_problem_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_endpoint_lacks_public_linear_measurements_and_permutation_resolution_imports_labels`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; injective unlabeled measurements or recovered toy coordinates are not an ECDLP break.

## Falsifiable hypothesis

One can derive, from a public elliptic endpoint and target-independent masks, enough scalar-blind
linear measurements of a compact source vector even though the measurement rows arrive under
unknown permutations.  Universal unlabeled-sensing inversion would recover the permutation and
coordinates, which would lift canonically to exact factor points for relation collection and fresh
masked-target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **endpoint-derived multi-measurement compilation with unknown row
permutations, universal unlabeled linear recovery, and recovered-coordinate-to-point source lift**.
An ordered-row oracle, explicit point features, Fourier bucket table, solver substitution, extra
endpoint queries carrying hidden logs, or post-hoc row alignment is a duplicate or control.

## Assumptions

1. `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, masks, source vector, and measurement matrices are target-independent and scalar-blind.
2. At least the required number of generic linear measurements is derivable from one endpoint without revealing ordered source rows or querying hidden scalar multiples.
3. Permutation recovery and coordinate-to-point lifting are exact on all strata with time, memory, measurement, and ambiguity exponents below `1/2`.
4. Measurement construction, source output, relation density, rank loss, factor logs, masked descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`elliptic_endpoint_multiple_scalar_blind_linear_measurements | unknown_row_permutations | universal_unlabeled_sensing_inverse | canonical_coordinates_to_exact_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1449`, the ordered-row recovery and permutation-ambiguity boundary.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1448-PREFLIGHT`, the permutation-floor-normalized coordinate-matrix preflight boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1449`, the frozen coordinate-expansion matrix and profile-faithful-null negative.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, the known-difference orientation and permutation-closed state boundary.
5. `inputs/ledger_inventory.json` — imported `P1434`, the open endpoint source-fiber generator.

## Closest primary literature

- Unnikrishnan, Haghighatshoar, and Vetterli, [Unlabeled Sensing With Random Linear Measurements](https://doi.org/10.1109/TIT.2018.2809002), proves recovery results when a vector is observed through sufficiently many supplied generic linear measurements with unknown ordering.
- Tsakiris and Peng, [Homomorphic sensing](https://arxiv.org/abs/1901.07852), studies generic recovery under families of linear transformations, including permutation-type ambiguities.

These results assume actual linear measurements of an unknown vector.  They do not derive those
measurements from a generic elliptic sum endpoint or provide a scalar-blind coordinate-to-factor-point
lift.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, source vectorization, measurement matrices, permutation model, recovery normalization, point lift, and verifier.
2. Derive the required public measurement arrays from each known-log endpoint without ordered source rows, hidden-scalar queries, or source-labelled features.
3. Recover the source vector and row permutations, lift every coordinate to exact signed factor-base tuples, and verify elliptic sums.
4. Collect independent relation rows, solve all factor logs, and independently verify rank and logs.
5. Apply the identical measurement compiler, unlabeled inverse, and point lift to fresh `Q+[t]P`, retain all permutation/source ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging measurements, permutations, source output, failed endpoints, rank loss, target replay, verification, and peak memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let measurement setup time and memory be `N^a,N^a_m`, reciprocal relation and target
densities `N^delta,N^delta_t`, one unlabeled inverse plus point lift `N^q,N^q_m`,
independent-rank gain `N^r`, source output and ambiguity `N^o,N^u`, and factor-log
completion `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Measurement count, matrix construction/storage, field conversions, permutation search, inverse
precision, coordinate lift, source output, relation rows, factor logs, target retries, verification,
and peak state are charged.  Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Unlabeled-sensing guarantees begin with several generic linear measurements of the same unknown
vector.  A public elliptic endpoint is one nonlinear group sum, not such a measurement family.
Generating independent scalar-blind rows that retain point coordinates appears to require
materializing or labelling the source tuple; ordering those rows restores the P1449 obstruction.
Even an abstract recovered coordinate vector has no canonical inverse to finite-field points without
a public feature dictionary whose construction and storage reproduce the factor/source deck.

## Proof track

Construct the required endpoint-only generic linear measurements without ordered source leakage,
prove exact permutation and point recovery on every stratum, and establish complete
`lambda,mu<=0.45`.

## Disproof track

Prove any sufficient measurement family factors through ordered source features or hidden scalar
queries, exhibit measurement-equivalent fibres with different point labels, or show measurement,
permutation, dictionary, output, ambiguity, or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: synthetic generic linear systems satisfying published measurement counts, with independently permuted rows and known source vectors.
- Negative controls: a single nonlinear endpoint, ordered-row leakage, feature dictionaries keyed by points, IDEA-053/124/131/155/168, P1449, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-blind endpoint measurement compiler of exponent at most `0.45`, exact
permutation and point recall with zero false sources, no ordered-row/feature leakage, full factor-log
rank, 100 blind descents at each of two largest future toy sizes, and complete
`lambda,mu<=0.45`.  Failure to supply enough public linear measurements, any source dictionary,
measurement/output exponent at least `0.50`, or complete exponent at least `0.50` falsifies this
version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-241/unlabeled_source_measurement_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-241/unlabeled_measurement_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-241/independent_unlabeled_sensing_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-241/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative high-risk hypothesis.  Correct recovery on a
synthetic linear system, a resolved permutation, a valid relation, or recovered toy scalar is not a
complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-241/unlabeled_source_measurement_theorem.md` proving an endpoint-only measurement family and point lift or a measurement/dictionary source-leakage no-go.
