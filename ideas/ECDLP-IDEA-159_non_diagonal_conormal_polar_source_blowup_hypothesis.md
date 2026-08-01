# ECDLP-IDEA-159 — Non-diagonal conormal-polar source blowup

## Status and claim labels

- Class: `algebraic-representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `proposed_unapproved_generic_stalk_rees_scoped_negative_pending_review`
- Cohort: `20260718-b`
- Evidence scale: primary-literature and symbolic preflight only; no experiment ran
- Contract posture: `review_required` and unapproved; the contract permits zero runs
- Scale labels: finite evidence is `toy`; asymptotic claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a nonunit ideal, exceptional divisor, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

There is a target-independent polar/Jacobian ideal on the source-labelled five-point addition incidence that is nonunit on the generic all-distinct étale stratum. Its normalized Rees blowup has bounded construction cost and exceptional valuations whose canonical atoms invert biconditionally to exact signed factor-base sources, permitting complete relation collection and masked descent below rho and BSGS.

## Mechanism-new operation

The operation is **generic-stratum conormal-polar blowup followed by valuation-to-source atomization**. IDEA-097 closed one specified relative Jacobian/Fitting ideal that becomes a unit generically; IDEA-085 closed diagonal blowups. This candidate survives only for an explicitly different non-diagonal ideal proved nonunit before sources are known. A new blowup package, backend, or post-hoc choice of polar direction is a control.

The theorem-only producer receipt now closes this ordinary-ideal escape. At every
generic point of the reduced all-distinct incidence, the local ring is a field, so
the polar ideal stalk is either zero or the unit ideal. Nonzero ideals are unit on
a dense open; zero ideals have no positive-degree Rees object; Cartier centers blow
up trivially; and proper critical centers cannot label generic source tuples.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta` and a projective source-labelled addition incidence are frozen.
2. One target-independent polar ideal `J` is defined from compact equations and is nonunit on the generic all-distinct relation stratum.
3. The normalized Rees algebra and relevant charts have sub-rho degree, coefficient, and memory growth.
4. Exceptional valuation atoms canonically identify all exact signed point sources, including multiplicities and boundary strata.
5. Construction, normalization, chart output, source inversion, retries, rank, linear algebra, descent, and memory are charged.

## Semantic fingerprint

`generic_all_distinct_relation_stratum | non_diagonal_polar_ideal | normalized_Rees_blowup | valuation_source_atoms | exact_masked_descent`

The removal test is a symbolic nonunit proof on the generic stratum plus an exact valuation/source biconditional.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate/source-ancestry barrier.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1449`, a held-out representation boundary for explicit source construction.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where a shared norm remains aggregate.
4. `inputs/ledger_inventory.json` — imported `P1478`, whose exact norm composition becomes dense.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1430-EXACT-AFFINE-PENCIL-SECANT-CONTROL`, the exact pencil/secant representation control.

## Closest primary literature

- Teissier, [Variétés polaires II](https://eudml.org/doc/142481), develops polar varieties and multiplicities but no elliptic source decoder.
- Duarte, Jeffries, and Núñez-Betancourt, [Nash blowups of toric varieties in prime characteristic](https://arxiv.org/abs/2208.05599), provide nearby characteristic-p blowup geometry, not this source biconditional.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies the relation equations but no non-diagonal polar compression.

No checked primary source supplies the proposed ideal, atom inverse, and complete descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the incidence, ideal formula, term orders, normalizations, charts, masks, and verifier.
2. Prove `J` nonunit on the generic all-distinct stratum without inspecting source tuples.
3. Construct the target-independent Rees representation within the declared setup budget.
4. For known `R_j=[r_j]P`, specialize, enumerate every valuation atom, invert it to signed sources, and independently verify each tuple.
5. Preserve unit-ideal cases, branch-only atoms, collisions, multiplicities, misses, and output sizes; collect rank `B` and verify factor logs.
6. Run the identical specialization on fresh `Q+[t]P` masks.
7. Substitute factor logs, remove `t`, retain every branch candidate, and verify `[x]P=Q`.
8. Report degrees, coefficients, charts, output, attempts, rank, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let Rees/normalization setup cost `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, specialization plus atom inversion `N^q,N^q_m`, output/ambiguity exponents `o,u`, and factor-log linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All coefficient bits, normalizations, exceptional components, and source branches are included in these exponents.

## Likely fatal obstruction

The producer theorem confirms the generic-stalk obstruction for every ordinary coherent ideal on the reduced incidence. Any surviving representation must leave ordinary Rees blowups or supply an explicit compact source-component rule; selecting source sheets as centers is the source dictionary the mechanism was meant to avoid.

## Proof track

Give the ideal explicitly; prove generic nonunitness, bounded Rees complexity, and a canonical all-strata valuation/source inverse; then derive `lambda,mu<=0.45` through blind descent.

## Disproof track

Compute the generic stalk and show `J=1`, restrict support to negligible branch strata, produce source-distinct fibers with identical valuations, or prove construction/output gives either exponent at least `0.5`.

## Positive and negative controls

- Published polar/Nash blowups with independently known exceptional data.
- IDEA-085 diagonal and IDEA-097 unit-ideal controls.
- Random ideals matched for degree and dense Rees normalization.
- Exhaustive toy fibers, rho, BSGS, known-log, and blind-target checks.

## Quantitative promotion and falsification gates

Remain proposed and unapproved. Before any run, prove generic nonunitness and exact atom inversion. A later approved preflight requires 100% all-strata source recall, zero false atoms, no target-selected ideal, and formal `lambda,mu<=0.45`. A unit generic stalk, aggregate collision, hidden source annotation, or exponent at least `0.5` falsifies this version.

## Artifact plan

- Existing theorem-only polar generic-stalk gate: `ideas/artifacts/ECDLP-IDEA-159/non_diagonal_polar_theorem.md`
- Rees/source inverse specification: `ideas/artifacts/ECDLP-IDEA-159/rees_source_inverse_spec.md`
- Fixtures and verifier: `ideas/artifacts/ECDLP-IDEA-159/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-159/independent_verifier.py`
- Cost receipt: `ideas/artifacts/ECDLP-IDEA-159/cost_analysis.md`

The generic-stalk gate is non-run producer evidence. Every other path is prospective; no experiment ran.

## Interpretation boundary

This is novelty-unverified representation research. Any finite computation is toy and every complexity projection is heuristic and model-bound. Correct blowup geometry or one relation is not a better-than-rho ECDLP result.

## Exactly one next executable action

1. Independently review `ideas/artifacts/ECDLP-IDEA-159/non_diagonal_polar_theorem.md` and either recommend scoped rejection or specify one nonordinary target-independent representation with a compact exact source-component rule and complete sub-rho cost; do not construct a Rees algebra.
