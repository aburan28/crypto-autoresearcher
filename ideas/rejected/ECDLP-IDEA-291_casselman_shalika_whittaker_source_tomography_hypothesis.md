# ECDLP-IDEA-291 — Casselman–Shalika Whittaker source tomography

## Status and claim labels

- Class: `representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_whittaker_multiplicity_one_recovers_representation_not_point_labels`
- Cohort: `20260718-l`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exact Whittaker coefficient, multiplicity-one model, valid relation, or toy factor is not an ECDLP break.

## Falsifiable hypothesis

A canonical globalization maps each endpoint source fiber to an unramified representation whose generic Whittaker coefficients admit a multiplicity-one inversion to exact labelled factor points, providing full relation calibration and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile an endpoint into an unramified reductive representation, evaluate its Whittaker function through the Casselman–Shalika formula, and invert the multiplicity-one model to labelled source factors**. Casselman–Shalika evaluates a supplied representation from Satake data; multiplicity one identifies a model up to scale, not an individual vector or point-labelled source tuple. Making coefficients point-separating requires a source-indexed representation, basis, or test family. Compact Satake and Weyl-character data aggregate labels. The operation merges with IDEAs 095, 101, 127, 153, and 272 once representation construction and exact return are charged.

## Assumptions

1. A public scalar-compatible globalization and unramified representation are computable from each endpoint without source advice.
2. A sub-rho set of Whittaker coefficients separates every signed source tuple and all exceptional strata.
3. Multiplicity-one normalization has a canonical coefficient-to-factor inverse rather than only representation recovery.
4. Globalization, local fields, representation dimension, coefficient evaluation, inversion, rows, factor logs, descent, and memory are charged.

## Semantic fingerprint

`global_reductive_representation | generic_Whittaker_function | Casselman_Shalika_evaluation | multiplicity_one_source_tomography | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-H008`, the native auxiliary-object transfer frontier.
2. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-030`, the source-incidence construction boundary.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the hidden representation/orientation negative.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank transform without a compact inverse.
5. `inputs/ledger_inventory.json` — imported `P1479`, the end-to-end source-return and cost accounting frontier.

## Closest primary literature

- Casselman and Shalika, [The unramified principal series of p-adic groups. II. The Whittaker function](https://numdam.org/item/CM_1980__41_2_207_0/), derives the supplied-representation Whittaker formula.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives x-coordinate relation equations; it does not supply signed or ordered factor labels.

No checked source constructs the representation from a generic ECDLP endpoint or inverts aggregate Whittaker data to exact factor labels; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, globalization, reductive group, local data, Whittaker normalization, masks, and verifier.
2. Compile known-log endpoints into representations without source-tuple or scalar advice.
3. Evaluate the frozen coefficient family and invert every accepted packet to exact signed factor points.
4. Verify rows, collect independent rank, solve and verify all factor logs.
5. Repeat the identical representation and Whittaker pipeline on fresh masked targets `Q+[t]P`.
6. Retain all packet and normalization ambiguities, substitute factor logs, and remove masks.
7. Accept only exact `[x]P=Q`, charging global and local state, coefficients, packets, outputs, factor logs, descent, and verification.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one representation/Whittaker/inverse attempt `N^q,N^q_m`, rank gain `N^r`, output `N^o`, packet ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes the named operation, exact inverse, and independent verification; `o` includes every enumerated relation branch; `u` is only residual scalar ambiguity in target descent.

Peak memory is included in `mu`; no table, representation, certificate, or output stream is free.

Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`. Every local/global coefficient, Weyl term, representation basis vector, packet, factor output, verification, and live byte is charged.

## Likely fatal obstruction

Whittaker multiplicity one identifies a functional on a supplied representation; it does not recover source labels absent from that representation. Satake parameters and Weyl characters are symmetric packet data. A representation refined until each factor tuple is distinguishable materializes the source deck, and its construction from the endpoint is the missing operation.

## Proof track

Construct the endpoint-only representation, prove a bounded coefficient family is injective on all source tuples, give an exact inverse, and certify complete exponents at most `0.45`.

## Disproof track

Exhibit tuple collisions in the frozen coefficient family, show representation or coefficient state at least `N^0.50`, prove inversion returns only packets, or derive either exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small unramified representation with known Satake parameter and Whittaker values.
- Negative controls: Weyl-conjugate packets, permuted source labels, source-indexed coefficient tables, random endpoints, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires exact all-source coefficient injectivity and inversion, verified factor logs, blind descent, and `lambda,mu<=0.45`. Packet collisions, source-indexed state/output at least `N^0.50`, missing globalization, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-291/whittaker_source_tomography_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-291/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-291/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-291/cost_analysis.md`

All paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This novelty-unverified merged proposal is toy-only if instantiated; all extrapolations are heuristic and model-bound. Correct representation theory or coefficient evaluation is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-291/whittaker_source_tomography_theorem.md` proving endpoint-only coefficient injectivity and exact source inversion or the packet/source-state obstruction.
