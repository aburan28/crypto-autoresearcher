# ECDLP-IDEA-258 — Baur–Strassen reverse-derivative source decoder

## Status and claim labels

- Class: `arithmetic_circuit_differentiation`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_reverse_ad_preserves_source_circuit`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a derivative identity, a ranked coordinate, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A compact endpoint-only arithmetic circuit computes a source-sensitive scalar whose Baur–Strassen reverse circuit exposes all input adjoints at constant-factor overhead; ranking those adjoints would return the exact five signed factor-base points needed for relation collection and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **build a circuit `C` for a source-sensitive score, apply Baur–Strassen reverse differentiation to obtain every input partial/adjoint in `O(size(C))`, and rank the coordinates as exact source candidates**.  Reverse differentiation is the only operation receiving credit.  It merges with IDEA-106 and IDEA-194 because those records already apply Baur–Strassen differentiation to an implicit Semaev/source circuit; IDEA-243 and live `P1536` are derivative-localization controls, while live `P1539` is the endpoint-predicate-without-source-inverse control.  A solver swap, parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector, dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. For each endpoint, `C` is derived from compact public elliptic equations without an explicitly indexed candidate tuple, source tensor, or source-coloured transition state.
2. The endpoint aggregate is sufficiently source-sensitive that its exact reverse adjoints distinguish every signed factor point on every multiplicity and exceptional stratum.
3. Ranking adjoints has a target-uniform biconditional to valid source tuples and does not use known logs, post-hoc source advice, or a source dictionary.
4. Circuit construction, forward evaluation, reverse state, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`compact_endpoint_arithmetic_circuit | Baur_Strassen_reverse_adjoint | ranked_gradient_source_atoms | exact_signed_point_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate preprocessing barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank transposed representation boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear feature-to-source gap.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact transition primitive whose composition becomes dense and source-losing.

## Closest primary literature

- Baur and Strassen, The Complexity of Partial Derivatives, [https://doi.org/10.1016/0304-3975(83)90110-X](https://doi.org/10.1016/0304-3975(83)90110-X), computes all partial derivatives of a supplied arithmetic circuit at constant-factor overhead but does not construct hidden circuit inputs.
- Bostan, Lecerf, and Schost, Tellegen's Principle into Practice, [https://doi.org/10.1145/860854.860870](https://doi.org/10.1145/860854.860870), transposes supplied algebraic algorithms but does not turn an endpoint aggregate into source-labelled coordinates.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies compact endpoint equations but no compact source-sensitive reverse circuit.

These primary records were checked for the named reverse-differentiation operation.  None supplies the endpoint-only source circuit, exact point inverse, factor-log calibration, and fresh masked descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, circuit variables, score, adjoint ranking, masks, tie rules, exceptional strata, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct and evaluate `C_R` from compact endpoint and factor-base data without materializing `B^5` tuple inputs, `B^3` middle states, or a source-labelled score table.
3. Apply exact Baur–Strassen reverse differentiation, rank the adjoints, lift every returned coordinate to exact signed factor points, verify sums, and preserve every tie, collision, repeated point, infinity chart, ambiguity branch, false source, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen circuit and reverse decoder to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected circuit, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by adjoint ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one circuit construction/evaluation plus exact reverse source inverse cost `N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be `N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every circuit input, gate, stored forward value, adjoint, preprocessing query, failed target, source coordinate, relation row, rank defect, factor log, masked descent, verifier call, bit operation, and live byte is charged.  Promotion requires both complete exponents at most `0.45`; derivative correctness or relation validity alone has no performance meaning.

## Likely fatal obstruction

Baur–Strassen differentiates a circuit already supplied; it neither constructs the hidden tuple nor makes a symmetric endpoint aggregate source-selective.  If `C` has `B^5` source-indexed inputs, its input and forward state already are the missing dense source tensor.  If `C` descends only from the endpoint sum, distinct source tuples in the same fiber give the same aggregate and its gradient cannot recover their provenance.  Reverse mode therefore preserves the source-construction and output obstruction rather than removing it.

## Proof track

Give a compact endpoint-only circuit whose gradient is biconditional with every exact signed source on all strata, prove source-blind construction and ranking, and derive complete exponents at most 0.45.

## Disproof track

Exhibit two distinct source orbits with one endpoint and identical endpoint-derived adjoints, reduce any source-sensitive circuit to a source-indexed tensor or dense transition state, or prove circuit, output, or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: a supplied small source-indexed circuit with planted factors and symbolic derivatives independently checked against its reverse adjoints.
- Negative controls: source-label permutations, endpoint-only symmetric scores, dense candidate-input circuits, IDEA-106, IDEA-194, IDEA-243, live `P1536`, live `P1539`, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an endpoint-only circuit and reverse source decoder of exponent at most 0.45, exact all-source and multiplicity recall with zero false sources, no source-indexed inputs or transition state, full factor-log rank, blind descent, and complete lambda and mu at most 0.45.  Identical gradients for distinct source orbits, supplied source variables, `B^3/B^5` state or output, or either exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-258/reverse_derivative_source_no_go.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-258/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-258/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-258/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains heuristic and model-bound.  A correct reverse circuit, derivative identity, ranked coordinate, valid relation, recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-258/reverse_derivative_source_no_go.md` proving either an endpoint-only gradient-to-source biconditional or that reverse differentiation preserves the source-circuit/provenance barrier.
