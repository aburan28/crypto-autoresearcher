# ECDLP-IDEA-292 — Howe-theta first-occurrence source lift

## Status and claim labels

- Class: `representation_changing`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_theta_first_occurrence_classifies_packets_not_source_tuples`
- Cohort: `20260718-l`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a nonzero theta lift, first occurrence, valid relation, or toy packet is not an ECDLP break.

## Falsifiable hypothesis

Encoding endpoint source tuples inside one member of a reductive dual pair makes their Howe-theta lifts first occur in distinct partner representations whose canonical vectors decode to exact signed factors, enabling below-rho relation rows and blind descent.

## Mechanism-new operation

The screened operation is **construct a source representation for a reductive dual pair, apply the oscillator/theta correspondence, isolate first-occurrence packets, and invert their canonical vectors to exact factor points**. First occurrence distinguishes supplied representation classes across Witt towers; it does not label vectors or tuples within a packet. A faithful oscillator model, level structure, or basis that distinguishes every source tuple grows with the source deck. This semantically merges with IDEAs 096, 101, 127, 153, and 272, rather than supplying a new nonhomomorphic point transfer.

## Assumptions

1. Each endpoint canonically yields a dual-pair representation without source or scalar advice.
2. First-occurrence data separate all signed source tuples, not only isomorphism classes or packets.
3. A canonical vector-level inverse returns exact elliptic factors on every stratum.
4. Oscillator dimension, local extensions, level structure, packet search, output, rows, factor logs, descent, and memory are charged.

## Semantic fingerprint

`dual_pair_source_encoding | oscillator_theta_lift | first_occurrence_packet_split | canonical_vector_inverse | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the public source-fiber generator gap.
2. `inputs/ledger_inventory.json` — imported `P1477`, the materialized source-state negative.
3. `inputs/ledger_inventory.json` — imported `P1478`, the sparse transition whose composition becomes dense.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact target-local source-return obligation.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-H008`, the native auxiliary representation-transfer frontier.

## Closest primary literature

- Howe, [Transcending classical invariant theory](https://doi.org/10.1090/S0894-0347-1989-0985172-6), develops the oscillator/dual-pair correspondence and supplied-representation multiplicity structure.
- Kudla and Rallis, [On first occurrence in the local theta correspondence](https://doi.org/10.1515/9783110892703.273), treats the first-occurrence question for supplied local representations.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives x-coordinate relation equations; it does not supply signed or ordered factor labels.

No checked source compiles a generic endpoint into a point-faithful dual-pair representation or returns labelled factors from first occurrence; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, dual pair, oscillator model, first-occurrence rule, source decoder, masks, and verifier.
2. Compile known-log endpoints to representations without source labels or tuple enumeration.
3. Compute all theta lifts and first-occurrence packets, then return every accepted canonical vector as exact signed factors.
4. Verify relations, collect independent rows, solve and verify factor logs.
5. Run the identical lift and inverse on fresh masked targets `Q+[t]P`.
6. Preserve packet, vector, and Witt-tower ambiguity; substitute logs and remove masks.
7. Accept only exact `[x]P=Q`, charging representation construction, theta kernels, packets, output, rows, logs, descent, verification, and memory.

## Full rho/BSGS cost model

Let setup be `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one theta/first-occurrence/inverse attempt `N^q,N^q_m`, rank gain `N^r`, output `N^o`, packet ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes the named operation, exact inverse, and independent verification; `o` includes every enumerated relation branch; `u` is only residual scalar ambiguity in target descent.

Peak memory is included in `mu`; no table, representation, certificate, or output stream is free.

Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`. Every Weil-representation coefficient, tower level, packet, vector, branch, factor output, and live byte is charged.

## Likely fatal obstruction

Theta correspondence acts on supplied representation classes. First occurrence can isolate a packet but does not select a point-labelled vector or source tuple. Encoding the missing labels into oscillator or level data makes construction/state source-sized; omitting them yields packet collisions and no exact inverse.

## Proof track

Prove endpoint-only point-faithful representation construction, tuple-injective first occurrence, canonical exact vector inverse, and complete exponents at most `0.45`.

## Disproof track

Show distinct tuples share first-occurrence data, prove oscillator/level/output state at least `N^0.50`, expose noncanonical vector choices, or derive either exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small dual-pair representation with independently known theta partner and vector labels.
- Negative controls: isomorphic packet vectors with permuted labels, truncated oscillator models, source-indexed level structures, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires exact all-strata tuple separation, factor return, full factor-log calibration, blind descent, and `lambda,mu<=0.45`. Packet-only output, source-sized representation/state, one missing stratum, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-292/howe_theta_source_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-292/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-292/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-292/cost_analysis.md`

All paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This novelty-unverified merged representation-changing proposal is toy-only if instantiated; extrapolations remain heuristic and model-bound. A correct theta lift or packet match is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-292/howe_theta_source_lift_theorem.md` proving tuple-injective first occurrence and vector-level factor inversion or the packet/source-state obstruction.
