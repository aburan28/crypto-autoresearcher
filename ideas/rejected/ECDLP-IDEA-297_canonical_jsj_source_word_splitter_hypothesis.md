# ECDLP-IDEA-297 — Canonical JSJ source-word splitter

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_jsj_splitting_consumes_source_word_and_forgets_abelian_ancestry`
- Cohort: `20260718-l`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a canonical splitting, normal form, valid relation, or toy leaf word is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform nonabelian lift of elliptic addition ancestry has a canonical cyclic JSJ decomposition whose vertex groups and edge maps recover the exact factor-point leaves from an endpoint below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift the endpoint relation to a finitely presented nonabelian group, derive a JSJ structural class, and decode vertex-group leaves to exact elliptic factors**. The cited JSJ results are structural: they organize splittings of a supplied group up to deformation, conjugacy, and stated rigidity conditions; they are not being claimed as a general computation algorithm. Elliptic addition exposes only the abelian endpoint and erases its source word. A presentation faithful to that word already contains source ancestry; a compact presentation identifies many words. This merges with IDEAs 084, 114, 175, 189, 208, and 217 after presentation construction and leaf output are charged.

## Assumptions

1. A public endpoint-only nonabelian presentation retains every signed factor tuple without listing source edges.
2. Its canonical JSJ pieces distinguish all source leaves and exceptional strata.
3. Vertex/edge data lift canonically to exact factor points with sub-rho ambiguity and output.
4. Presentation size, JSJ construction, conjugacy/deformation choices, leaf output, rows, logs, descent, and memory are charged.

## Semantic fingerprint

`elliptic_endpoint | nonabelian_source_word_lift | canonical_cyclic_JSJ_splitting | vertex_group_leaf_recovery | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit ancestry-edge negative.
2. `inputs/ledger_inventory.json` — imported `P1477`, the source-state materialization boundary.
3. `inputs/ledger_inventory.json` — imported `P1478`, the sparse-to-dense transition boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-H674`, the full relation-to-descent obligation.
5. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the source generator and exact-return boundary.

## Closest primary literature

- Rips and Sela, [Cyclic splittings of finitely presented groups and the canonical JSJ decomposition](https://doi.org/10.2307/2951832), gives canonical structure for supplied group presentations.
- Forester, [On uniqueness of JSJ decompositions of finitely generated groups](https://doi.org/10.1007/s00014-003-0780-y), distinguishes deformation-space equivalence from stronger uniqueness and records conditions for genuine uniqueness.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives x-coordinate relation equations; it does not supply signed or ordered factor labels.

No checked source constructs a source-faithful nonabelian presentation from an abelian endpoint or returns original factor leaves from a JSJ class; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, presentation grammar, JSJ convention, leaf decoder, masks, and verifier.
2. Build presentations for known-log endpoints without source-word advice or edge enumeration.
3. Apply the hypothesized compiler to derive every allowed JSJ representative under the frozen structural convention, then return every accepted vertex/edge leaf as exact signed factors.
4. Verify rows, collect independent rank, solve and verify factor logs.
5. Apply the identical presentation and splitting pipeline to fresh masked targets `Q+[t]P`.
6. Preserve conjugacy, deformation, and leaf ambiguities; substitute logs and remove masks.
7. Accept only exact `[x]P=Q`, charging presentation, splitting, normal forms, outputs, rows, logs, descent, verification, and memory.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one presentation/JSJ/inverse attempt `N^q,N^q_m`, rank gain `N^r`, output `N^o`, splitting ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes the named operation, exact inverse, and independent verification; `o` includes every enumerated relation branch; `u` is only residual scalar ambiguity in target descent.

Peak memory is included in `mu`; no table, representation, certificate, or output stream is free.

Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`. Every generator, relator, edge, conjugacy representative, leaf word, output factor, and live byte is charged.

## Likely fatal obstruction

JSJ decomposition cannot recover ancestry discarded before the group presentation exists. A faithful lift must encode source words or edges, making construction/state source-sized. Compact endpoint-only presentations abelianize many source words to the same element, and canonical splittings remain defined only up to transformations that do not label original leaves.

## Proof track

Construct a compact endpoint-only faithful presentation, prove JSJ-to-factor biconditionality, and certify complete exponents at most `0.45`.

## Disproof track

Exhibit source words with the same frozen presentation/JSJ data, prove presentation or output exponent at least `0.50`, show leaf selection needs advice, or derive either exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small graph-of-groups presentation with independently labelled JSJ leaves.
- Negative controls: abelianized presentations, conjugate/deformation-equivalent splittings with permuted leaves, explicit source-edge decks, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires compact endpoint-only faithfulness, exact all-source leaf return, verified logs, blind descent, and `lambda,mu<=0.45`. Word collisions, explicit ancestry input, state/output at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-297/jsj_source_word_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-297/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-297/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-297/cost_analysis.md`

All paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This novelty-unverified merged conservative proposal is toy-only if instantiated; extrapolations remain heuristic and model-bound. A correct JSJ decomposition or toy normal form is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-297/jsj_source_word_theorem.md` proving a compact endpoint-only faithful presentation and leaf inverse or the ancestry/materialization obstruction.
