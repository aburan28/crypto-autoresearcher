# ECDLP-IDEA-265 — Saito higher-residue source pairing

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_higher_residue_requires_supplied_brieskorn_lattice_and_has_no_point_section`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a residue-pairing identity, a valid relation, a recovered source tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The summation-polynomial source fiber can be converted target-uniformly into an isolated hypersurface singularity and universal unfolding whose Brieskorn lattice carries a Saito higher-residue pairing.  A canonical orthogonal or primitive decomposition of that pairing would expose the exact five factor-point branches and complete descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the endpoint source fiber into a universal unfolding and Brieskorn lattice, evaluate Saito's higher-residue pairing, and invert pairing components to exact factor-point branches**.  Higher-residue pairings are defined on the filtered de Rham/Gauss-Manin data of a supplied unfolding of an isolated hypersurface singularity.  They provide an aggregate bilinear form, with primitive-form/good-section and basis normalization issues, rather than a canonical section to individual elliptic source points.  The operation merges with IDEA-044 stationary-phase residues, IDEA-069 higher operations, IDEA-089 residue idempotents, IDEA-133 flat-extension extraction, IDEA-159 conormal/polar data, and IDEA-228 Bernstein-Sato data when the unfolding, lattice basis, Milnor-rank output, and point lift are charged.  A solver swap, parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector, dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. Every frozen endpoint fiber is transformed without source advice into an isolated hypersurface singularity with a computable target-uniform universal unfolding.
2. Its Brieskorn lattice and higher-residue pairing have a sub-rho representation whose rank does not scale with the dense source degree.
3. A canonical pairing decomposition maps biconditionally to exact signed factor points on every smooth, singular, nonreduced, repeated-point, and infinity stratum.
4. Unfolding construction, lattice basis, Gauss-Manin connection, primitive form/good section, pairing coefficients, point lift, ambiguity output, rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`summation_source_fiber | isolated_hypersurface_universal_unfolding | Brieskorn_lattice | Saito_higher_residue_pairing | canonical_point_branch_section | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate and tensor-source barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the scalar/aggregate-coordinate boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the supplied dual-object/full-rank negative.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact-transition and dense-composition control.

## Closest primary literature

- Saito, The higher residue pairings K_F^(k) for a family of hypersurface singular points, [https://doi.org/10.1090/pspum/040.2/713270](https://doi.org/10.1090/pspum/040.2/713270), defines the pairing for a supplied family/unfolding and its filtered de Rham data.
- Saito, Period Mapping Associated to a Primitive Form, [https://doi.org/10.2977/prims/1195182028](https://doi.org/10.2977/prims/1195182028), constructs period mappings from a universal unfolding and good sections/primitive-form data.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies compact endpoint equations but not a source-faithful Brieskorn lattice or point section.

These primary records were checked for the required unfolding, lattice, pairing, and supplied-input boundary.  None gives an endpoint-only sub-rho lattice compiler, canonical exact point-branch section, factor-log calibration, and fresh masked descent.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, summation model, singularity compactification, unfolding rule, lattice basis rule, primitive-form normalization, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct its isolated-singularity model, universal unfolding, Brieskorn lattice, and higher-residue pairing without expanding the dense source fiber or inserting source-labelled vanishing cycles.
3. Decompose the pairing, map every accepted component to exact signed factor points, and verify the elliptic sum.  Preserve every non-isolated fiber, Milnor-rank jump, basis/normalization dependence, collision, repeated point, infinity chart, nonreduced component, ambiguity branch, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and source output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen unfolding, lattice, pairing, and point-section inverse to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected good section, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by pairing or branch ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every unfolding coefficient, singular chart, Milnor-basis element, Brieskorn-lattice operation, connection matrix, primitive-form/good-section choice, pairing coefficient, failed target, branch, source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation, and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness or relation validity alone has no performance meaning.

## Likely fatal obstruction

The higher-residue pairing starts from a supplied universal unfolding and its Brieskorn lattice; constructing source-faithful lattice data can already require the dense source fiber.  The pairing is an aggregate bilinear form on cohomological classes, not a canonical primitive-point idempotent decomposition.  Basis changes, good-section/primitive-form normalization, and a Milnor rank tracking the fiber degree preserve aggregate singularity information while losing exact factor-point ancestry.  Restoring that ancestry requires the missing source deck.

## Proof track

Give an endpoint-only universal-unfolding/lattice compiler of exponent at most `0.45`, prove a basis-independent biconditional point-branch section of the higher-residue pairing on every frozen stratum, and derive both complete exponents at most `0.45`.

## Disproof track

Reduce lattice construction or Milnor-rank output to the dense source fiber, exhibit different exact source sets with isometric/identical pairing data, prove unavoidable good-section/basis dependence, or show construction, point lift, output, or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied isolated singularity with known universal unfolding, Brieskorn basis, primitive form, and independently labelled branches.
- Negative controls: basis changes preserving the pairing, two good sections/normalizations, non-isolated or nonreduced fibers, aggregate residue values with permuted point labels, IDEA-044, IDEA-069, IDEA-089, IDEA-133, IDEA-159, IDEA-228, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an endpoint-only unfolding/lattice/pairing compiler of exponent at most `0.45`, a basis-independent exact point section with zero false sources and complete recall, bounded Milnor/output rank, full factor-log rank, blind masked descent, and complete `lambda` and `mu` at most `0.45`.  A supplied unfolding or source-labelled lattice, aggregate/basis-dependent output, dense Milnor rank, no point section, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-265/higher_residue_source_section_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-265/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-265/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-265/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains heuristic and model-bound.  A correct pairing identity, primitive form, valid relation, recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-265/higher_residue_source_section_theorem.md` proving a sub-rho endpoint pairing with a canonical exact point section or the supplied-lattice/aggregate-pairing no-go.
