# P1481 finite-field serial-message propagation contract

## Objective

Replace P1480's generic bit-vector proof search with an exact, finite-field-aware
message evaluator for the same complete five-endpoint serial factor graph.
Measure whether the multiplicative-subgroup x deck produces enough collision or
quotient compression to make complete target membership cost strictly below
`L^(3/2)` after at most `L^2` target-independent setup.

The full objective remains a generic prime-field ECDLP algorithm below rho.
P1481 is a source-resolving membership experiment only. It cannot waive known-
RHS relation supply, rank, target descent, or asymptotic-transfer gates.

## Frozen lineage

- P1476 result/audit SHA-256:
  `c29426c61c687560b45e38cae1c50f18e89c2846a6d599c6f4583fc98ec70e5f` /
  `752190e01263740ed8b0db73ae4fe3d092797ff1e1991a48438a8f66d2bcc138`.
- P1477 result/audit SHA-256:
  `ca41939ef8f05d2579ac392d2651fc6bb3199f0e38b10b1d0e20a197caa51ae5` /
  `8b6eb71141b5a3deba12bd6969ddd0c10d9d6092c32e52e173d0145371f01245`.
- P1480 result/audit SHA-256:
  `d8107a1272a9ab0fd29c8243ea3527fadcc950d734c3b530d6a948c8a0cfd7e2` /
  `cb84adfd3b88edcebe776b0ba1359649c6e486b569c1da96bc503455dc8efbf0`.

## Fixtures, decks, and queries

Reuse the four ordinary prime-order P1477/P1480 fixtures:

| L | p | q | a | b |
|---:|---:|---:|---:|---:|
| 4 | 1033 | 1061 | 1 | 1 |
| 8 | 32801 | 32479 | 1 | 5 |
| 16 | 1048609 | 1047539 | 5 | 7 |
| 32 | 33554593 | 33563891 | 3 | 9 |

For each fixture use the frozen P1480 `subgroup_x` deck and matched
deterministic `random_x` deck. Every liftable x-coordinate contributes both
point signs. Use the same four planted-positive and four random-scalar targets
per `(L,deck)` as P1480.

## Target-independent setup

Build the exact forward two-endpoint message

`F2 = {P1+P2 : P1,P2 in D}`

by ordered endpoint generation. Store one canonical two-endpoint source per
distinct point. Charge every group addition, hash lookup, insertion, collision,
point record, and x-orbit. Setup must remain at most `L^2` in full and every
leave-one-out fit. No `A3`, target table, target label, or target secret may be
present in setup.

## Complete target message and join

For each nonidentity target R, compute exact backward messages:

`B1(R) = {R-P5 : P5 in D}`,

`B2(R) = {U3-P4 : U3 in B1(R), P4 in D}`.

Preserve one `(P4,P5)` witness per distinct B2 point. Identity states are
ordinary elliptic-curve group elements and therefore require no affine
exception. This is the native-group realization of P1480's homogeneous
projective auxiliaries.

Complete the serial join by scanning every pair `(U2,P3)` in `B2(R) x D`,
computing `needed=U2-P3`, and probing `F2`. Preserve the first verified source
`(P1,P2,P3,P4,P5)` but continue the full scan even after a hit. Thus SAT and
UNSAT queries receive the same complete-decision charge, and planted positives
cannot benefit from early stopping.

The candidate path may materialize `F2`, `B1`, and `B2`; it may not materialize
`A3`, `A4`, `A5`, a three-endpoint forward message, or a target-indexed cache.

## Exact accounting and quotient diagnostics

Per query record:

- B1 and B2 ordered generation, point support, x-orbit support, identity,
  collisions, and canonical witness failures;
- join group additions, F2 hash probes, hit count, distinct hit states, and
  source verification;
- complete candidate work
  `B1 additions + B2 additions + join additions + hash probes`;
- candidate wall time, storage records, and source multiplicity diagnostics.

At each `(L,deck)`, use the maximum complete candidate work across all eight
queries. Fit setup work, B2 point support, B2 x-orbit support, join work, and
complete work against nominal L with every leave-one-out slope. Compare the
subgroup deck with the endpoint-count-matched random-x control.

A useful exact quotient signal requires a written key or representation that
can replace B2 point records while preserving source retrieval and UNSAT
decisions. Collision counts alone are diagnostics.

## Independent oracle

Only after all eight candidate decisions for a deck are sealed, build exact
point supports `A1` through `A5` with one source witness per point. Verify all
candidate SAT/UNSAT labels and sources. Oracle generation, labels, and witnesses
may not influence setup, B1/B2 construction, join order, or candidate output.

## Promotion gate

`FINITE_FIELD_SERIAL_MESSAGE_SIGNAL` requires all of:

- all 64 candidate decisions agree with the independent A5 oracle;
- all SAT answers return verified five-endpoint sources;
- setup work slope and every leave-one-out slope are at most `2`;
- subgroup worst complete-query work slope and every leave-one-out slope are
  strictly below `3/2`;
- the same strict bound holds for B2 storage plus source-recovery metadata;
- subgroup compression beats the matched random-x control on every monotone
  fixture or has a frozen algebraic quotient explaining any equality;
- no A3-through-A5 materialization or target-indexed advice occurs on the
  candidate path;
- the measured cost is carried into the P1476 relation/rank/descent ledger.

Fast group operations, early SAT, small wall time, point-sign quotienting,
collision excess, a median fit, or a toy source without complete UNSAT support
does not promote.

## Outputs

- `ecdlp_index_calculus_state/p1481_finite_field_serial_message_propagation.json`
- `research/p1481_finite_field_serial_message_propagation.md`

## Interpretation boundary

A negative result closes raw exact point-message propagation with an explicit
B2 frontier and hash join. It does not rule out a non-materializing polynomial,
tensor, sketch, transform, or subgroup-specific quotient of the same message.
A positive result remains a membership signal, not a faster-than-rho ECDLP
algorithm, until relation, rank, descent, and asymptotic proof gates pass.
