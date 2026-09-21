# ECDLP-IDEA-247 — BNR spectral-cover eigenline source lift

## Status and claim labels

- Class: `spectral_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_spectral_cover_requires_source_spectral_data`
- Cohort: `20260718-h`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a local identity, a source tuple, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The endpoint relation fiber is the spectral curve of a compact Higgs-like operator whose eigenline sheaf has one rational sheet per exact factor source.  Beauville-Narasimhan-Ramanan spectral correspondence would recover the line bundle and eigenlines, yielding exact sources and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile an endpoint spectral operator, recover its BNR spectral curve/eigenline sheaf, and invert rational eigenline sheets to factor points**.  The candidate uses eigenline sheaves rather than IDEA-186's Krichever divisor or IDEA-213's dimer spectral weights, but all three start from spectral data that already encode the source divisor.  BNR is an equivalence for a supplied Higgs field and spectral sheaf, not an endpoint-to-source constructor.  A solver swap,
parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector,
dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. A compact scalar-blind operator is derived from the public endpoint without one matrix block or eigenline per source state.
2. Its spectral cover and line sheaf have sub-rho degree, construction, and represented state and are rational over admitted curves.
3. Every eigenline sheet maps canonically to exact signed factor points on singular and ramified strata.
4. Operator construction, spectral computation, sheaf recovery, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_higgs_operator | bnr_spectral_cover | eigenline_sheaf | rational_sheet_to_factor_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured spectral-coordinate barrier.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank value/tensor boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear spectral-feature boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`, the exact aggregate divisor-fiber control.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.

## Closest primary literature

- Beauville, Narasimhan, and Ramanan, Spectral curves and the generalised theta divisor, [https://doi.org/10.1515/crll.1989.398.169](https://doi.org/10.1515/crll.1989.398.169), recovers Higgs data from a supplied spectral curve and sheaf.
- Hitchin, Stable bundles and integrable systems, [https://math.mit.edu/events/talbot/2011/library/hitchin_stable_bundles_integrable_systems.pdf](https://math.mit.edu/events/talbot/2011/library/hitchin_stable_bundles_integrable_systems.pdf), defines the spectral integrable-system setting but no elliptic relation compiler.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies the relation equations, not spectral eigenlines.

These sources were checked as primary records for the named supplied-input operation.  None gives
the endpoint-only compiler, exact point-source inverse, factor-log calibration, and fresh masked
descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, public colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, derive the compact Higgs-like operator and spectral cover directly from each endpoint without a source divisor, eigenvalue list, or point-labelled matrix.
3. Compute the eigenline sheaf, lift every rational spectral sheet to exact signed factor points, preserve ramification/multiplicity, and verify sums. Preserve every failure, duplicate, ambiguity branch, repeated point, infinity chart, nonreduced case, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen constructor and source inverse to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected parameter, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by source ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every constructor coefficient, represented state, preprocessing query, failed target, branch,
source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation,
and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness
or relation validity alone has no performance meaning.

## Likely fatal obstruction

BNR correspondence is invertible only after the spectral curve and sheaf are supplied.  A characteristic polynomial aggregates eigenvalues, while eigenlines/eigenvectors contain the missing source basis.  Building a point-faithful operator or spectral sheaf therefore materializes the source divisor or a matrix of source dimension.

## Proof track

Construct an endpoint-only operator of sub-rho size, prove a canonical all-strata eigenline-to-point bijection, and derive complete exponents at most 0.45.

## Disproof track

Show the characteristic/spectral data forget eigenline labels, reduce any faithful operator to the source divisor, or prove cover degree, sheaf state, output, or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: supplied Higgs fields with independently known smooth spectral covers, line sheaves, and eigenlines.
- Negative controls: isospectral operators with changed eigenlines, ramified covers, IDEA-022, IDEA-186, IDEA-213, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-free operator compiler, exact rational eigenline-to-point recall with zero false sources, bounded cover/sheaf state, full factor-log rank, blind descent, and complete lambda and mu at most 0.45.  Supplied spectral divisors, basis-dependent eigenlines, missed ramification, or exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-247/bnr_source_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-247/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-247/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-247/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains
heuristic and model-bound.  A correct identity, canonical form, decomposition, valid relation,
recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale
validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-247/bnr_source_lift_theorem.md` proving an endpoint-only spectral operator/eigenline source inverse or a spectral-sheaf/source-divisor factorization no-go.
