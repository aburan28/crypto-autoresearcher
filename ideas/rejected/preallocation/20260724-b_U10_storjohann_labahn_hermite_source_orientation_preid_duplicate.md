# Pre-ID duplicate draft — Storjohann–Labahn Hermite source orientation

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U10`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_source_lattice_and_basis_orientation`.
- Class/risk/lane: representation / representation-changing / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; Hermite form or a unimodular multiplier is not an ECDLP break.

## Falsifiable hypothesis

A public endpoint-derived relation lattice has a triangular Hermite normal form whose ordered pivots
select a canonical signed factor-base orientation. Fast HNF with multipliers would compress source
incidence and enable relation rank, logs, and blind descent with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation transforms a supplied integer matrix to a canonical row-lattice form with
unimodular multipliers. ECDLP credit requires the lattice to be constructed without source columns
and the HNF order to induce a canonical point section. Using HNF as downstream exact linear algebra
or retaining multipliers is a solver/representation substitution.

## Assumptions

1. Endpoint-only observables generate the integral relation lattice.
2. HNF pivots preserve exact signs, multiplicities, and occurrence identity.
3. A public ordering resolves basis and point gauges without DLP or source dictionaries.
4. Compilation, reduction, multiplier traffic, replay, logs, and descent meet both caps.
5. The form and ordering are scalar-blind and reusable for fresh targets.

## Semantic fingerprint

`public_relation_lattice | fast_Hermite_row_reduction | ordered_triangular_pivots | canonical_signed_point_orientation | full_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260724-b_U09_kannan_bachem_smith_source_quotient_preid_duplicate.md` — same supplied-lattice and gauge boundary.
2. `ideas/rejected/ECDLP-IDEA-029_newton_okounkov_semigroup_scalar_coordinate_hypothesis.md` — canonical lattice solving follows, rather than creates, a faithful scalar coordinate.
3. `ideas/ECDLP-IDEA-007_miller_s_unit_descent_hypothesis.md` — lattice relations still need target/source coset orientation.
4. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — labelled relation columns carry the source object.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable source return remains the front end.

## Closest primary literature

- Storjohann and Labahn, [Asymptotically fast computation of Hermite normal forms](https://doi.org/10.1145/236869.237083), starts from a supplied integer matrix and returns a canonical form/multiplier.
- Kannan and Bachem, [polynomial Smith/Hermite algorithms](https://doi.org/10.1137/0208040), supplies the earlier exact-matrix route.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not construct a source-faithful lattice orientation.

No checked source gives an endpoint compiler or factor-point section; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, lattice compiler, row/column ordering, HNF convention, restrictions, masks, and verifier.
- Build reusable state within `B^(9/4+o(1))` without source tables, factor logs, dense resultants, or target fitting.
- Charge every matrix entry, triangularization, modular reduction, multiplier, pivot, orientation branch, and signed replay.
- Verify `max(d_FB+32,1000)` independent rows, rank `d_FB`, and all factor-base logs.
- Use byte-identical state on 100 fresh masked targets, subtract masks, and verify each scalar.
- Charge bit growth, output, ambiguity, failure, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, HNF/orientation/replay work `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, and logs `N^ell,N^ell_m`.
Use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require both `<=0.45`,
state `<=B^(9/4+o(1))`, online work/workspace `<=B^(5/4+o(1))`; rho/BSGS are `0.50`.

## Likely fatal obstruction

HNF canonically represents a lattice relative to an ordered ambient basis; the factor-point
labelling and order are exactly the missing source dictionary. Reordering columns changes the
occurrence orientation without changing the abstract lattice. Multipliers preserve that dictionary
at source-scale, so triangularization cannot manufacture it.

## Proof track

Prove endpoint-only lattice construction, order-independent point-faithful HNF semantics,
canonical all-strata source orientation, full rank/log/descent, and complete sub-rho bit costs.

## Disproof track

Permute the ambient source basis while preserving the abstract lattice, expose source-scale
multipliers, or show orientation/replay/complete exponent reaches `0.50`.

## Positive and negative controls

- Positive: supplied ordered lattices with externally labelled bases.
- Negative: column permutations, equivalent lattices, repeated pivots, sign changes, exceptional fibres, and fresh targets.
- Baselines: Smith form, IDEAs 007/029, P1553 R4, rho, and BSGS.
- Correct HNF or a triangular solve is not an ECDLP result.

## Quantitative promotion and falsification gates

- Promote only with compiler/orientation theorems, zero ordering/gauge errors, bounded multipliers, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one supplied source basis, permutation collision, ambiguous orientation, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u10_lattice_order_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u10_permuted_basis_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u10_hnf_bit_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Hermite reduction. Correct HNF, a multiplier, or a valid row
remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Apply two source-basis permutations to the same toy relation lattice and test whether the HNF alone can recover the differing factor-point labels.
