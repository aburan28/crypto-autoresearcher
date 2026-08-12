# Pre-ID duplicate draft — Kannan–Bachem Smith source quotient

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U09`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_incidence_lattice_and_noncanonical_source_multipliers`.
- Class/risk/lane: representation / representation-changing / representation-changing pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a Smith form, invariant factors, or quotient coordinate is not an ECDLP break.

## Falsifiable hypothesis

The integral relation-incidence lattice has a compact Smith normal form whose invariant-factor
coordinates canonically orient exact signed factor-base occurrences. Computing the quotient and
multipliers would expose factor logs and blind target coordinates with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation applies unimodular row/column transformations to a supplied integer matrix
and returns canonical invariant factors. It becomes ECDLP representation-changing only if the
incidence lattice is endpoint-derived and quotient coordinates have a canonical point-labelled
section. Supplying the matrix or retaining full multipliers repeats the source catalogue.

## Assumptions

1. Public endpoints compile a compact integral lattice without enumerated source columns.
2. Smith invariant factors distinguish exact restricted occurrence fibres.
3. A canonical section resolves unimodular gauges to signed factor points.
4. Matrix construction, multiplier growth, section, replay, logs, and descent satisfy both caps.
5. The quotient state is reusable and target-independent.

## Semantic fingerprint

`public_relation_lattice | Kannan_Bachem_Smith_reduction | invariant_factor_quotient | canonical_point_labelled_section | full_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-029_newton_okounkov_semigroup_scalar_coordinate_hypothesis.md` — Smith form appears only after a faithful lattice coordinate exists.
2. `ideas/ECDLP-IDEA-007_miller_s_unit_descent_hypothesis.md` — lattice quotient orientation remains the source/scalar obstruction.
3. `ideas/deferred/ECDLP-IDEA-173_gain_graph_switching_potential_descent_hypothesis.md` — quotient potentials require a faithful non-DLP orientation.
4. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — columns/provenance already encode factor sources.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact source replay cannot be replaced by invariant factors.

## Closest primary literature

- Kannan and Bachem, [Polynomial algorithms for Smith and Hermite normal forms](https://doi.org/10.1137/0208040), canonicalize a supplied integer matrix and also compute multipliers.
- Storjohann, [Computing Hermite and Smith normal forms of triangular integer matrices](https://doi.org/10.1016/S0024-3795(98)10012-5), improves the supplied-matrix canonicalization stage.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not construct a faithful integral source lattice or canonical section.

No checked source resolves the ECDLP point gauge; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, lattice compiler, reduction policy, sign conventions, restrictions, masks, and verifier.
- Build target-independent state within `B^(9/4+o(1))`, excluding source columns, factor logs, dense resultants, and target fitting.
- Charge every lattice entry, gcd/pivot, unimodular transformation/multiplier, invariant factor, section branch, and signed replay.
- Collect at least `max(d_FB+32,1000)` verified rows, rank `d_FB`, and solve all factor-base logs.
- Reuse byte-identical eligible quotient state on 100 fresh masked targets, subtract masks, and verify scalars.
- Charge integer bit growth, output, ambiguity, failure, and peak memory.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, Smith/section/replay work `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, and log costs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require `lambda,mu<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Smith form forgets row/column labels up to unimodular equivalence. Invariant factors can be
identical for differently labelled source lattices, while the multipliers or a canonical section
carry the full source orientation. Constructing the incidence columns already performs the missing
factor-base/source representation.

## Proof track

Prove an endpoint-only compact lattice, point-faithful invariant theorem, canonical all-strata
section, full rank/log/descent, and complete bit/multiplier costs below both caps.

## Disproof track

Construct two unimodularly equivalent lattices with different factor-point labels, expose
source-sized multipliers/columns, or show section/complete cost has exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied labelled lattices with known Smith form and an external canonical basis.
- Negative: column-permuted/unimodularly equivalent lattices, repeated invariant factors, torsion ambiguity, exceptional fibres, and fresh targets.
- Baselines: IDEAs 007/029/173, ordinary SNF, P1553 R4, rho, and BSGS.
- Correct invariant factors or quotient coordinates are representation controls.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/section theorems, zero gauge/source errors, bounded bit/multiplier state, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source column, equivalent-lattice source collision, noncanonical section, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u09_lattice_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u09_equivalent_lattice_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u09_multiplier_bit_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP representation, not Smith reduction. Correct invariant factors, multipliers,
or a quotient relation remain `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Construct the smallest pair of column-permuted source lattices with identical Smith form and test whether any invariant-only rule returns their differing exact factor-point labels.
