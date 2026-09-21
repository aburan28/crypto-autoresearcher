# ECDLP-IDEA-268 — Multiplicity-code Hasse-jet local lift

## Status and claim labels

- Class: `code_theoretic_source_inversion`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_local_decoder_requires_source_jet_codeword_oracle`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; local correction, a decoded polynomial value, a valid relation, a recovered tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The endpoint relation polynomial and enough Hasse derivatives form a high-rate multiplicity-code word whose local line restrictions can be queried from public elliptic data.  Sublinear local correction would recover source coordinates or a point-valued branch and thereby support complete relation collection and masked target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode the source relation by value-and-Hasse-jet evaluations, locally correct selected coordinates along frozen affine lines, and lift the corrected jets to exact factor points**.  Multiplicity-code local decoding assumes oracle access to the received word.  Here the desired word symbols are derivative evaluations of a source-faithful relation object; producing them at a hidden source or all compatible tuples is the missing source problem.  Decoding values also does not invert a many-to-one endpoint map.  The route merges with IDEA-130 folded AG decoding, IDEA-136 Wronskian condensers, IDEA-138 sum-check self-reduction, IDEA-140 differential residues, and IDEA-156 Nullstellensatz self-reduction when oracle construction and point lift are charged.

## Assumptions

1. A target-uniform public oracle returns the frozen polynomial value and all required Hasse derivatives at decoder queries without source advice.
2. The elliptic source relation lies within the degree/multiplicity regime required for local correction at rate sufficient for `B=N^beta`.
3. Corrected jet symbols determine exact signed factor points, not merely an endpoint polynomial value.
4. Oracle setup, every query, derivative order, list size, point lift, relation rank, factor logs, target descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`elliptic_relation_polynomial | multiplicity_codeword | Hasse_jet_line_queries | local_correction | exact_source_point_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact coordinate-predicate source-resolution boundary.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, where source generation and transposed joins retain materialization cost.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1407-NO-PROMOTION`, the tested predicate-basis no-promotion result.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1408-NO-EC-PROMOTION`, the low-degree map/image compression negative.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.

## Closest primary literature

- Kopparty, Saraf, and Yekhanin, [High-rate codes with sublinear-time decoding](https://doi.org/10.1145/2629416), introduces multiplicity codes and local decoding from value-and-derivative oracle access.
- Kopparty, [List-Decoding Multiplicity Codes](https://theoryofcomputing.org/articles/v011a005/), studies global/list decoding of supplied multiplicity-code words.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations but not a source-jet oracle.

No checked source constructs the required elliptic oracle or exact source lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, source polynomial, derivative order, code domain, local lines, query distribution, masks, and verifier.
2. For known-log endpoints, expose the exact multiplicity-code oracle without enumerating compatible source tuples.
3. Run the frozen local decoder, retain every list branch, and lift corrected jets to exact signed factor points.
4. Verify each elliptic relation, collect rows to full rank, and charge oracle failures and rank defects.
5. Solve and independently verify all factor logs.
6. Apply the same decoder to fresh masked targets `Q+[t]P` with no known-log branch.
7. Substitute logs, remove masks, verify `[x]P=Q`, and record complete time and memory.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one oracle-backed decode plus point lift cost `N^q,N^q_m`, independent-rank gain be `N^r`, output/list and target ambiguity be `N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every code symbol, Hasse derivative, query, line restriction, list branch, source point, failed target, relation, factor log, verification, bit operation, and live byte is charged.

## Likely fatal obstruction

Local decoding saves queries only after random access to a codeword close to a low-degree multiplicity encoding.  Public endpoint data does not supply source-sensitive Hasse-jet symbols.  Computing them either evaluates a source object already containing the hidden tuple or aggregates the dense fiber, and corrected polynomial values do not canonically select a preimage.

## Proof track

Construct the public jet oracle below exponent `0.45`, prove local correction and a biconditional all-strata point lift, and complete rank, factor-log, and masked descent with both exponents at most `0.45`.

## Disproof track

Reduce any source-sensitive oracle query to source enumeration, exhibit equal endpoint jets with distinct source tuples, prove list/output growth at least `N^0.50`, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied multiplicity-code word with planted sparse errors and labelled polynomial evaluations.
- Negative controls: endpoint-only value oracle, missing derivatives, equal-jet distinct sources, random low-degree words, IDEA-130, IDEA-138, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a public source-jet oracle and exact point lift of exponent at most `0.45`, zero false sources, full factor-log rank, blind descent, and complete `lambda,mu<=0.45`.  A supplied codeword, hidden-source query, list/output exponent at least `0.50`, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-268/multiplicity_jet_source_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-268/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-268/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-268/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped negative.  Every future finite check would be toy, and all scaling claims heuristic and model-bound.  Local correction or a toy source lift is not a generic-prime ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-268/multiplicity_jet_source_lift_theorem.md` proving a public source-jet oracle and point lift or the oracle/preimage obstruction.
