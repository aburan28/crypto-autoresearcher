# ECDLP-IDEA-315 — Stein-factor connected-source section

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_stein_factor_materializes_finite_source_algebra`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a finite factor, connected-fiber theorem, relation, or toy source section is not an ECDLP break.

## Falsifiable hypothesis

The Abel–Jacobi source projection admits a target-independent Stein factor whose finite intermediate algebra has sub-rho size and a canonical rational section returning exact signed factor points on every source stratum.

## Mechanism-new operation

The screened operation is **Stein-factor the proper source projection into a connected-fiber morphism followed by a finite morphism, then invert one finite sheet to exact factor points**. Unlike generic normalization or a new elimination backend, this asks whether connected components themselves provide a compact canonical source index. The name is new in the corpus, but the generic source fiber is already finite: its Stein factor is the finite source algebra, and selecting one sheet requires the missing primitive idempotent or point section. It merges with IDEAs 068, 089, 125, 216, and 245.

## Assumptions

1. A proper compactification of the signed coloured relation projection is public, target-independent, and compatible with masked descent.
2. Its Stein intermediate space and finite algebra are constructible without enumerating source points or a dense eliminant.
3. Connected components remain point-faithful across repeated, nonreduced, boundary, and sign strata.
4. A canonical finite-sheet section returns exact finite-field factor points rather than only a component or residue field.
5. Compactification, factor construction, output, relation density, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`proper_abel_jacobi_source_projection | Stein_connected_fiber_factorization | finite_sheet_algebra | canonical_exact_factor_section | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the public source-fiber generator requirement.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed batch source-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge compression boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the compact-transition versus dense source-complete composition boundary.

## Closest primary literature

- The Stacks Project, [Stein factorization, Noetherian case](https://stacks.math.columbia.edu/tag/0A18), gives the algebraic factorization of a supplied proper morphism through a proper map with connected geometric fibers and a finite map; it constructs `Spec_Y(f_*O_X)`, not a canonical point section.
- Stein, [Analytische Zerlegungen komplexer Räume](https://eudml.org/doc/160505), is the historical analytic result and does not by itself establish the finite-field scheme-theoretic application.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the endpoint relation variety but not a compact finite-sheet constructor or point section.

No checked source proves a sub-rho Stein algebra or canonical exact section for the generic prime-field relation fiber; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, factor decks, signs, masks, the proper source compactification, projection, Stein factor, finite-sheet convention, and verifier.
2. On known-log targets, construct the intermediate finite algebra without source enumeration, select exact sheets, lift them to signed factor points, and verify every relation.
3. Collect independent rows, solve all factor-base logarithms, and independently verify them.
4. Apply the identical compactification, factor, and section to fresh `Q+[t]P` endpoints with no target-specific branch table.
5. Substitute factor logs, remove masks, preserve all sheet ambiguity, and obtain scalar candidates.
6. Accept only `[x]P=Q`, charging every geometric, algebraic, output, rank, factor-log, descent, verification, and memory cost.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one factor/section/source return `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Finite degree, residue-field work, all sheets, and boundary replay belong to `q,o,u`. Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

On the generic zero-dimensional source fiber, connected components are already individual geometric points. The finite Stein algebra therefore has degree equal to the source-fiber length; computing primitive sheets is the original factorization/source enumeration. At collisions, the connected component can be nonreduced and still lacks a canonical ordered lift to signed factor points.

## Proof track

Prove a public compactification, a finite Stein algebra of exponent at most `0.45`, a canonical all-strata rational point section, sufficient rank, reusable factor logs, blind descent, and both complete exponents at most `0.45`.

## Disproof track

Show that the Stein degree equals generic source length, that sheet inversion requires primitive idempotents or dense factorization, that a nonreduced component lacks an exact point section, or that either complete exponent is at least `0.50`.

## Positive and negative controls

- Positive: a supplied finite cover with labelled sheets and known connected fibers must factor and return the planted sheet.
- Negative: finite covers with identical base point and permuted sheets must not acquire a preferred source without extra labels.
- Baselines: IDEAs 068/089/125/216/245, P1434, P1478, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact all-strata point return, 1,000 independently verified rows and 100 blind descents per large size, and `lambda,mu<=0.45`.
- Falsify if finite degree/source output has exponent at least `0.50`, a primitive-idempotent oracle is required, or one admitted stratum lacks a section.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-315/stein_factor_degree_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-315/sheet_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-315/independent_stein_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-315/cost_analysis.md`

## Interpretation boundary

This rejects only the stated Stein-factor source section. A correct factorization, finite algebra, sheet count, relation, or toy point lift is not an asymptotic ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-315/stein_factor_degree_theorem.md` proving a sub-source-length finite factor with exact section or the generic equality between Stein degree and source-fiber length.
