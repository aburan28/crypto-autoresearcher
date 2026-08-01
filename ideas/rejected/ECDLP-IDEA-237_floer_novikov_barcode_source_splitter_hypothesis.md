# ECDLP-IDEA-237 — Floer–Novikov barcode source splitter

## Status and claim labels

- Class: `topological_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_filtered_complex_requires_source_generators_and_barcode_forgets_them`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Floer barcode, spectral invariant, or filtered-chain classification is not an ECDLP break.

## Falsifiable hypothesis

The endpoint relation correspondence admits a scalar-blind filtered Floer–Novikov complex whose
barcode intervals have canonical endpoint generators equal to the exact signed factor-base sources.
A non-Archimedean singular-value decomposition would split those generators and enable relation
collection and fresh masked descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **construct an endpoint filtered Novikov complex, compute its barcode normal
form, and lift interval endpoints to exact elliptic point sources**.  A supplied Hamiltonian or source
complex, ordinary persistence barcode, spectral-invariant score, generic filtered reduction, or
post-hoc generator choice is a duplicate/control.

## Assumptions

1. Symplectic/Novikov data, action filtration, generators, differential, masks, normalization, and point lift are defined uniformly from public finite-field curve and endpoint data.
2. Field lift, complex construction, filtration precision, barcode reduction, and state have exponents below `1/2`.
3. Each interval has a canonical all-strata inverse to exact signed finite-field point sources rather than only a filtered chain-homotopy class.
4. Lifting, source output, relation density, rank, factor logs, masked descent, verification, and memory are fully charged.

## Semantic fingerprint

`finite_field_endpoint_to_filtered_novikov_complex | floer_action_filtration | nonarchimedean_barcode_normal_form | canonical_interval_generator_point_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing endpoint source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the failed arithmetic source generator.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the source-ancestry edge boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transition boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact local composition/dense-payload boundary.

## Closest primary literature

- Usher and Zhang, [Persistent homology and Floer–Novikov theory](https://arxiv.org/abs/1502.07928), classifies supplied filtered Novikov complexes by barcodes using non-Archimedean singular-value methods.
- Polterovich and Shelukhin, [Autonomous Hamiltonian flows, Hofer's geometry and persistence modules](https://arxiv.org/abs/1412.8277), derives persistence invariants from supplied Hamiltonian Floer data.

Neither source constructs such a complex from a generic finite-field elliptic endpoint or provides a
canonical interval-to-point-source inverse.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, lift, symplectic data, filtration, differential, barcode normalization, source lift, and verifier.
2. Construct the endpoint filtered complex without enumerating signed point-source generators or trajectories.
3. Compute the barcode normal form, lift every admitted interval generator to exact finite-field sources, and verify elliptic sums.
4. Collect independent relation rows and solve and independently verify all factor logs.
5. Apply the identical lift/complex/barcode/source inverse to fresh `Q+[t]P`, retain ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging field/lift costs, complex state, output, target replay, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let lift/complex setup time and memory be `N^a,N^a_m`, reciprocal relation and target
densities `N^delta,N^delta_t`, one barcode/source inverse `N^q,N^q_m`, independent-rank
gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log completion `N^ell,N^ell_m`.
Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Lift degree, precision, generators, trajectories, filtration values, reduction state, interval output,
rank loss, factor logs, masked descent, and verification are charged.  Promotion requires
`lambda,mu<=0.45`.

## Likely fatal obstruction

Floer–Novikov barcodes classify a filtered complex that is already specified by generators and a
differential.  Encoding elliptic source tuples as generators or trajectories supplies the missing
source deck, and constructing an analytic/symplectic lift from a generic finite-field curve is itself
uncharged extra structure.  The barcode preserves filtered chain-homotopy type but not preferred
generator labels; basis changes can leave all intervals unchanged while permuting point sources.

## Proof track

Construct a canonical sub-rho finite-field-to-Novikov complex, prove a point-labelled interval basis
independent of all lifts and choices, and establish complete `lambda,mu<=0.45`.

## Disproof track

Exhibit filtered-chain-equivalent complexes with identical barcodes but different source labels, prove
the complex needs one generator/trajectory per source, or show lift, state, output, ambiguity, or
complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: published small filtered Novikov complexes with independently known barcodes and generator bases.
- Negative controls: basis-scrambled filtered complexes, lift changes, ordinary persistence, IDEA-073/218/220/224, P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a canonical lift and complex of exponent at most `0.45`, exact all-source recall,
zero false sources, no supplied source generators, full factor-log rank, 100 blind descents at each
large future toy size, and complete `lambda,mu<=0.45`.  Barcode-equal source collisions, lift
dependence, missed branches, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-237/floer_barcode_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-237/filtered_complex_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-237/independent_floer_barcode_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-237/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative high-risk hypothesis.  A valid lift, Floer
complex, barcode, spectral invariant, filtered-chain equivalence, toy source lift, relation, or toy
scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-237/floer_barcode_source_theorem.md` proving a canonical compact finite-field filtered complex with point-source interval lifts or a lift/generator-basis obstruction.
