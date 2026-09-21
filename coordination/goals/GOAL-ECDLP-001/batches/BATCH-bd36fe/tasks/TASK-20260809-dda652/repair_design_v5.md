# BATCH-bd36fe v5 executable freeze-control repair

This is a scoped successor to the v4 design after the independent review
`TASK-20260809-daa343` returned `REVISE`. It is a control-plane package, not an
ECDLP implementation or experiment specification. Its purpose is to make the
remaining admissibility claims executable before a Coordinator can freeze a
future specification.

The package has one complete canonical control run, one event ledger, one
complete 400-arm matrix, an arithmetic/input fixture, six accepted terminal
cases, and nine negative mutations. `validate_xor_v5.py` applies every case in
memory, validates JSON Schema plus cross-object equations, and fails closed.
The canonical data are synthetic control fixtures: they do not report an
ECDLP observation, a cost result, a security result, an asymptotic result, or a
SOTA delta.

## Findings repaired

| review finding | v5 closure |
|---|---|
| F-NEW-002 | `input_digest` has a byte-exact domain, length prefix, canonical JSON payload, field order, preimage hex, and digest. `arithmetic_fixture_xor_v5.json` is consumed by the validator and checks the prime/domain, integer B bound, nonsingular curve, first eligible point/order trace, lift/output identity encoding, positive F, and nonempty reference output. |
| F-NEW-003 | Timing records raw monotonic nanosecond endpoints, clock source, units, exit status, and flush state. The wrapper interval starts immediately before the spawn call and ends after the child's final output flush, so the included launch cost is unambiguous. Exactly five A and five B repeats are grouped per cell; a wall median or delta is non-null only when all ten are valid. |
| F-NEW-004 | The event schema requires candidate/relation/query/table identities and bucket sizes. The validator opens the event bytes, verifies their hash and run id, checks contiguous indices, recomputes every phase, exception, candidate, relation, query, and table equation, and compares the result to both run and ledger counters. |
| F-NEW-005 | The validator consumes a complete canonical run, event ledger, and 400-arm matrix. Six accepted cases are applied and checked, and every named negative mutation is applied and required to fail. Matrix/run key equality and terminal-state relations are semantic checks, not prose. |
| F-NEW-006 | The v5 contract fixes numeric b-cell order `(1/2),(2/5)` everywhere. Ordered shard arrays require `key.shard == containing_shard`, exact ordinal-modulo-four ownership, overlapping worker intervals, RSS sample recomputation, per-shard byte sums, campaign byte sums, and cap equations. |
| F-NEW-008 | The predecessor validator accepts a candidate future contract, approval lock, and dependency closure. It rejects any exact predecessor, any old Executor task, any hash mismatch, missing required gate, or newly discovered stale ID. The negative fixture exercises selected-contract and dependency-closure rejection. |

## Canonical input and arithmetic

The input preimage is:

```text
ASCII("XOR-INPUT-v5") || 0x00 || u32be(len(P)) || P
```

`P` is the UTF-8 byte sequence of the compact canonical JSON object, with no
whitespace and exactly this key order:
`{"m":3,"p":101,"b_num":2,"b_den":5,"seed":0}`. Its digest is SHA-256 of
that complete preimage. Decimal parsing is prohibited for binary floating
point. The matrix domain is `p={101,103,107,211}`, `m=3`, and b cells in
numeric order `{(1,2),(2,5)}`.

The arithmetic control fixture is normative for its canonical cell. It checks
that p is prime and greater than three, that B is the largest integer with
`B^b_den <= p^b_num`, that the selected curve is nonsingular, that the exact
first eligible point is on the curve and has the recorded least order, that
`lift_x` chooses the least root, that NONE is `u32be(0xffffffff)`, that point
and relation encodings are fixed, and that F and `R_star` are nonempty before
coverage or relative metrics are computed. The arithmetic fixture is a
control gate; it does not create an experiment implementation.

## Event and run identity

One complete arm has one event stream. Every event has one contiguous
zero-based index and one `E.add` operation. The validator derives:

```text
event_count                 = len(events)
phase_counters[p]           = count(event.phase == p)
candidate_attempts          = count(candidate_identity != null)
candidate_unique            = distinct candidate identities
candidate_duplicate_events  = attempts - unique
candidate_verified          = count(candidate_outcome == "verified")
candidate_aborted           = count(candidate_outcome == "aborted")
relation_events             = count(relation_identity != null)
relation_unique             = distinct relation identities
relation_duplicate_events   = relation_events - relation_unique
false_positive_events       = verified - relation_events
query_events                = count(query_identity != null)
query_unique                = distinct query identities
query_duplicate_events      = query_events - query_unique
table_insert_events         = sum(table_bucket_sizes)
```

Every derived value must equal the corresponding run and ledger fields. An
exception has a non-null exception digest, null returned identity, and counts
once; a returned event has the reverse. Missing event bytes, a hash mismatch,
an index gap, unknown phase, inconsistent identity, or any equation failure
is invalid.

## Timing, repeats, and matrix resources

The charged interval is `[started_monotonic_ns, finished_monotonic_ns]`, where
the wrapper records `started_monotonic_ns` immediately before the child spawn
call and `finished_monotonic_ns` only after child exit and final output flush.
It includes launch, input, curve/factor-base work, every E.add, serialization,
and output flush. Replay, analysis, global hashing, matrix aggregation, and
Coordinator operations are outside the arm interval. The validator checks
`c_wall_seconds=(finished-start)/1e9`, positive ordering, the exact clock and
unit fields, exit status, and flush completion.

The matrix has 400 keys: 40 A, 40 B, and 320 D. Keys are sorted by
`(p,b_num,b_den,arm,seed,process_replica,null_replica)` using the numeric b
order above, and shard is `ordinal mod 4`. Each shard array is canonical,
contains exactly 100 keys, and runs sequentially within a concurrently active
worker. Worker start/stop intervals and RSS samples are retained. The
validator recomputes worker wall, campaign wall, CPU, host RSS from coordinator
plus active workers, every output-byte class, and the 400-arm cap.

For each p,b cell, A and B have exactly five fresh valid repeats. The validator
groups the 40 A and 40 B entries into eight cells, checks the retained raw
values and validity, computes the median, and accepts a delta only when all ten
repeats are `completed_valid`. Partial or invalid repeat sets yield a null
estimand and cannot be treated as a measured comparison.

## Predecessor admission

The exact immutable historical set remains
`EXP-XOR-7267e4`, `H-XOR-a227dc`, and `TASK-20260808-e6022f`, with live source
hashes in `predecessor_exclusion_xor_v5.json`. A candidate object supplies the
selected contract id, approval-lock ids, dependency ids, and discovered stale
ids. The validator requires all exact gate booleans and rejects a candidate if
any old record is selected, any old Executor task is in its dependency closure,
any source hash mismatches, a member is missing, or a new stale id is reported.

## Claim ceiling and next gate

The v5 package is `design-only`. Its `VALIDATION_PASS` means only that the
control fixtures and negative mutations behave as declared. It authorizes no
specification, approval, freeze, implementation, Executor admission, run,
evidence record, or official status transition. A fresh independent
`review-adversarial` freeze review must pass the exact archived v5 bytes before
the Coordinator creates a separate frozen experiment specification.
