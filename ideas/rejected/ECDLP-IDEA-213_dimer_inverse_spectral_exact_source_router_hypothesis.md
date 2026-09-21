# ECDLP-IDEA-213 — Dimer inverse-spectral exact-source router

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_spectral_consumer_requires_source_marked_dimer_data`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and information-flow audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a spectral curve, matching, or inverse map is not an ECDLP break.

## Falsifiable hypothesis

A compact torus dimer built from factor atoms has an endpoint-twisted Kasteleyn operator whose spectral data determine exactly all signed matchings corresponding to five-source elliptic decompositions. Rational inverse-spectral reconstruction would expose sources and enable blind descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **Kasteleyn spectral aggregation followed by rational inverse-spectral source routing**. It merges/rejects because determinants aggregate matchings, and known inverse maps recover edge weights from a supplied spectral curve and divisor; they do not select a matching or manufacture source labels.

## Assumptions

1. Public curve/group/factor base `B=N^beta` and target are frozen, with a target-independent torus dimer built without matching enumeration.
2. Finite-field and singular-chart specialization yields an `F_p`-rational spectral divisor without extension or source advice.
3. Endpoint spectral data determine every matching and exact signed factor point on all strata.
4. Graph construction, Kasteleyn determinant, divisor, inverse, matching output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`factor_atom_torus_dimer | endpoint_twisted_Kasteleyn_operator | rational_inverse_spectral_map | matching_to_exact_signed_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the determinant/full-rank control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear-phase/source gap.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`, the aggregate spectral invariant boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the source-edge floor.

## Closest primary literature

- Goncharov and Kenyon, [Dimers and cluster integrable systems](https://arxiv.org/abs/1107.5588), derives spectral data from a supplied dimer.
- George, Goncharov, and Kenyon, [The inverse spectral map for dimers](https://arxiv.org/abs/2207.10146), reconstructs weights from supplied spectral data rather than a distinguished matching.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations without a dimer compiler.

No checked source supplies the elliptic dimer identity and matching-to-point inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze graph grammar, atom weights, Kasteleyn signs, endpoint twist, spectral charts, divisor, inverse, masks, and verifier.
2. Build the graph without source matchings and prove spectral/source biconditional over `F_p` on every stratum.
3. For known endpoints, invert spectral data to all signed matchings, decode points, and verify rows.
4. Collect full rank, solve and verify factor-base logs.
5. Repeat unchanged on fresh `Q+[t]P`, substitute logs, subtract `t`, preserve ambiguity, and final-verify the scalar.

## Full rho/BSGS cost model

Rho and BSGS cost `N^(1/2+o(1))`; BSGS memory matches. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, spectral query/inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Extension, divisor, and matching output costs are included; both exponents must be at most `0.45`.

## Likely fatal obstruction

The characteristic polynomial sums matchings and erases which one occurred. An inverse-spectral map consumes a divisor and returns edge weights, not a matching. Supplying that divisor, distinct edge variables, or a source-marked graph stores the lost deck; nonrational divisors and matching collisions add further failures.

## Proof track

Give a compact finite-field dimer whose endpoint spectral data alone are biconditional with all exact sources, prove rational all-strata matching inversion, and derive `lambda,mu<=0.45`.

## Disproof track

Exhibit matching collisions, a nonrational/singular divisor, dependence on supplied source spectral data, state at least `B^3`, one lost source, or exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied dimers with known rational spectral divisors and planted edge weights.
- Negative controls: isospectral graphs with different matchings, source-marked divisors, matchgates/cluster networks, dense determinants, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires graph/state at most `B^2.25`, query at most `B^1.25`, `F_p`-rational all-strata inverse, 100% matching/source recall, zero false tuples, no source divisor, and `lambda,mu<=0.45`. Any collision, nonrational divisor, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective graph: `ideas/artifacts/ECDLP-IDEA-213/dimer_graph_spec.md`
- Prospective inverse: `ideas/artifacts/ECDLP-IDEA-213/inverse_spectral_identity.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-213/matching_source_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-213/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-213/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected representation analysis. Finite checks would be toy and projections heuristic and model-bound. A spectral identity, inverse map, or valid matching is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-213/inverse_spectral_identity.md` for the smallest torus dimer representing a symbolic two-plus-three transition and decide whether endpoint-only spectral data determine every signed matching without a source divisor.
