# P1480 bit-vector serial-S3 membership contract

## Objective

Test a source-resolving, non-materializing backend for complete five-term
membership over the sparse subgroup-x factor base. Compile the serial `S3`
chain directly to quantifier-free bit-vector constraints and require the solver
to return five endpoint indices, rather than a dense state polynomial, root
family, or `A2`/`A3` table.

The full objective remains a generic prime-field ECDLP algorithm below rho.
P1476 requires complete membership exponent `alpha<3/2` when the factor-model
dimension is not compressed. P1480 tests that missing backend only; it cannot
waive relation supply, rank, descent, or asymptotic-transfer obligations.

## Frozen lineage

- P1477 result/audit SHA-256:
  `ca41939ef8f05d2579ac392d2651fc6bb3199f0e38b10b1d0e20a197caa51ae5` /
  `8b6eb71141b5a3deba12bd6969ddd0c10d9d6092c32e52e173d0145371f01245`.
- P1478 result/audit SHA-256:
  `287a08a131ce7b56bd4e8468eb6c443d7bcba4b7fb2ba13c860866c21902b8df` /
  `d035cba39d08165c4b7dd336d4a095c1c99ff822f8db8c6cf5f3fca3b8c764f9`.
- P1479 result/audit SHA-256:
  `4367c4478f6b94a0213b0a4066f6d609ccbdb7a2eab311087145db28855c0500` /
  `0636b13b4932327dc541c85effe2e5f5dd479733e5f440e034a692f1bbfc52c3`.
- Solver: `/opt/homebrew/bin/z3`, version `4.15.4`, 64 bit.

## Deterministic fixtures and decks

Reuse the four ordinary prime-order P1477 fixtures, with `q approximately L^5`:

| L | p | q | a | b |
|---:|---:|---:|---:|---:|
| 4 | 1033 | 1061 | 1 | 1 |
| 8 | 32801 | 32479 | 1 | 5 |
| 16 | 1048609 | 1047539 | 5 | 7 |
| 32 | 33554593 | 33563891 | 3 | 9 |

For each fixture build two matched x decks:

- `subgroup_x`: every liftable x-coordinate in the order-L multiplicative
  subgroup of `F_p^*`;
- `random_x`: the same number of distinct liftable x-coordinates, selected by
  a frozen SHA-256 stream without replacement.

Every x-coordinate represents both point signs. Repetition of endpoint indices
is allowed. Sort the five indices to remove permutation symmetry without
removing multisets.

## Complete homogeneous serial encoding

Use the standard third summation polynomial

`S3(u,v,x)=(u-v)^2*x^2 - 2*((u+v)*(u*v+a)+2*b)*x`
`          +(u*v-a)^2 - 4*b*(u+v)`.

Affine auxiliaries omit decompositions whose partial sum is the identity.
Therefore compile the tri-homogeneous form for projective x-coordinates
`(X_i:Z_i)`:

`(X1*Z2-X2*Z1)^2*X3^2`
`-2*((X1*Z2+X2*Z1)*(X1*X2+a*Z1*Z2)+2*b*Z1^2*Z2^2)*X3*Z3`
`+((X1*X2-a*Z1*Z2)^2`
`  -4*b*(X1*Z2+X2*Z1)*Z1*Z2)*Z3^2`.

Endpoints and the nonidentity target use `(x:1)`. Each auxiliary is normalized
by one Boolean to either `(u:1)`, with `0<=u<p`, or the identity `(1:0)`.
This removes projective scaling ambiguity and includes all partial identities.

For `R=P1+P2+P3+P4+P5`, assert

`S3(U1,X1,X2)=0`,
`S3(U1,U2,X3)=0`,
`S3(U2,U3,X4)=0`,
`S3(U3,X5,x(R))=0`.

All field operations are unsigned 64-bit bit-vector additions,
subtractions, and multiplications reduced modulo p after every operation.
The largest fixture has `p<2^26`, so multiplying two reduced residues cannot
overflow 64 bits. Index-to-x selection is an explicit `O(L)` nested `ite`
table. No array containing pair, triple, or higher endpoint states is allowed
on the candidate path.

## Solver policy and queries

Use Z3 `QF_BV`, model production, a 30,000 ms timeout, one solver process per
query, and no post-outcome tactic or seed selection. Freeze random seed `0`.
Parse status, model values, wall time, formula bytes, and all available Z3
statistics including `rlimit-count`, conflicts, decisions, and propagations.

For each deck and fixture run eight queries in fixed order:

- four planted positives, each the nonidentity sum of five deterministic
  signed deck endpoints;
- four deterministic nonzero random-scalar targets, whose membership label is
  unknown until the exact oracle runs.

Implementation smoke tests may use one planted `L=4` query but may not score or
alter the frozen deck, formula, solver, seed, query, timeout, or gate. The
campaign is staged at `L=4,8`, then `L=16,32`; continue to the larger stage only
if every smaller decision is `sat` or `unsat`, every SAT model replays, and the
oracle agrees. A stopped stage is a preserved negative, not a missing result.

## Witness replay, blocking, and exact oracle

For every SAT model, enumerate the at most `2^5` sign assignments for its five
selected x-coordinates and require a point sum equal to `R` or `-R`. Verify the
endpoint indices, curve points, serial constraints, and source sum. If a model
is locally satisfying but has no global sign assignment, block that exact
five-index tuple and rerun under the same remaining timeout budget. Charge all
retries and solver effort. An `unknown`, timeout, malformed model, or exhausted
budget fails completeness.

Only after the candidate decision, construct the sign-complete deck and exact
point supports `A1` through `A5`, preserving one witness per point. This oracle
may label SAT/UNSAT and validate a returned source, but its work is reported
separately and cannot enter candidate setup, query, formula, blocking, or
selection.

## Charged cost and asymptotic fit

Per query charge:

- formula bytes and selector entries;
- Z3 `rlimit-count`, summed across retries;
- wall time, summed across retries;
- blocked tuples and model-replay sign trials.

Define deterministic solver effort as
`formula_bytes + max(1,total_rlimit_count)`. At each `(L,deck)`, use the maximum
over all eight complete decisions, not the median. Fit this worst-query effort
against nominal L over all four fixtures and report every leave-one-out slope.
Also fit formula bytes, SAT effort, UNSAT effort when both labels have enough
fixtures, and wall time as diagnostics. Runtime alone is not a field-operation
proof; a promoted route must later expose an implementation-independent circuit
or proof-search bound.

## Controls and promotion gate

`BITVECTOR_SERIAL_S3_MEMBERSHIP_SIGNAL` requires all of:

- all 64 frozen decisions terminate as SAT or UNSAT;
- exact agreement with the independent `A5` oracle;
- all 32 planted positives return verified five-endpoint witnesses;
- every SAT answer returns a replayed source after charged blocking retries;
- no candidate access to `A2`, `A3`, `A4`, `A5`, oracle labels, or target
  secrets;
- subgroup worst-query effort slope and every leave-one-out slope are strictly
  below `3/2`;
- subgroup formula-byte slope and every leave-one-out slope are at most `1`;
- subgroup effort is asymptotically lower than the matched random-x control or
  a written structure-specific reason explains equality without a selected
  fixture effect;
- a source-level serial circuit construction accounts for the measured effort;
- the result is carried into the P1476 relation/rank/descent exponent ledger.

Tiny-fixture SAT, planted-only success, median speed, SAT-only speed,
timeout-as-UNSAT, hidden oracle filtering, explicit state enumeration, or a Z3
heuristic slope without a portable cost argument does not promote.

## Outputs

- `ecdlp_index_calculus_state/p1480_bitvector_serial_s3_membership.json`
- `research/p1480_bitvector_serial_s3_membership.md`

## Interpretation boundary

A negative result closes this frozen bit-vector serial-S3 encoding and solver
policy at the tested sizes. It does not rule out algebraic SAT, custom finite
field propagation, sparse resultants, tensor methods, or another factor graph.
A positive result is a membership signal only, not a faster-than-rho ECDLP
algorithm, until the full relation, rank, descent, and asymptotic proof gates
pass.
