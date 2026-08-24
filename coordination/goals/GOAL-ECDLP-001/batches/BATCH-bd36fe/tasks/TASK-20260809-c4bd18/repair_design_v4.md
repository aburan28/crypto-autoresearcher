# Freeze-repair design v4 — closed domain, executable validation, and stale-contract exclusion

Task `TASK-20260809-c4bd18`, BATCH-bd36fe. This is a Coordinator successor to
the archived independent `REVISE` review `TASK-20260809-7c85e6`. It is a
pre-freeze control package: it creates no ECDLP arm implementation, experiment
specification, approval, freeze, Executor admission, run, evidence record,
hypothesis transition, or goal transition.

The exact v3 snapshot under repair is commit
`c2edd195ee726eb1f386147ee6bf7f403bcf9815`, archived by
`TASK-20260809-e239a2`; the exact review is archive commit
`102b254d4ea4c8f8c8b1bf697b3614ad9380c17b`, archived by
`TASK-20260809-2841c8`. The future experiment remains the already allocated
`EXP-XOR-44d232`. This package adds versioned schema drafts, an event-ledger
schema, a fixture/validator contract, and an exact immutable predecessor
exclusion record. All measured fields remain null.

## 1. Direct response to the eight review findings

| finding | v4 discharge artifact |
|---|---|
| F-NEW-001 | Section 2 and `validation_contract_xor_v4.json` assign every seed-field tag, field order, counter origin, display encoding, rejection record, and a byte-level first-reject fixture. |
| F-NEW-002 | Section 3 and the validator fixture enumerate the eight exact `(p,b)` cells, prime-field preconditions, integer search order, nonempty gates, and four-byte identity encodings. |
| F-NEW-003 | Section 4 fixes the wrapper interval, monotonic clock endpoints, units, exclusion boundary, five-repeat validity rule, and signed relative wall delta. |
| F-NEW-004 | Section 5 fixes arm-wide first-seen scope, prefix/table classification, the seven-phase sum domain, required event/counter artifacts, and exception normalization. `event_ledger_xor_v4.schema.json` binds the shape. |
| F-NEW-005 | Section 6 and `validation_contract_xor_v4.json` bind a versioned validator contract, six accepted fixtures, nine negative mutations, and the required semantic checks before freeze. The v4 schemas reject the previously accepted state-shape errors structurally where JSON Schema can express them; the validator enforces cross-record equations. |
| F-NEW-006 | Section 7 enumerates the exact domain, key order, shard schedule, wall/RSS/output boundaries, corrected terminal names, and every campaign equation. `matrix_summary_xor_v4.schema.json` requires the corresponding fields and complete-sized arrays. |
| F-NEW-007 | The v3 Pareto record remains hash-bound and unchanged; no measured or dominance claim is added here. |
| F-NEW-008 | `predecessor_exclusion_xor_v4.json` names and hashes `EXP-XOR-7267e4`, `H-XOR-a227dc`, and `TASK-20260808-e6022f`; Section 8 makes the exact set a future approval-lock and dispatch dependency gate. |

The v4 package is still not permission to use the drafts as an experiment
manifest. A future freeze task must install byte-identical authoritative copies,
create the validator source, bind all hashes, materialize the six fixtures, and
obtain a fresh independent review before approval or implementation.

## 2. Byte-exact `XOR-PRNG-v1` seed and replay contract

For a typed field with tag byte `T` and value bytes `V`, the encoding is exactly
`u8(T) || u32be(len(V)) || V`. The eight fields occur exactly once, in the
following order, with no count, omission, padding, separator, or terminator:

| field | tag | value encoding |
|---|---:|---|
| campaign seed | `0x01` | unsigned u64 big-endian |
| p | `0x02` | unsigned u32 big-endian |
| b numerator | `0x03` | unsigned u32 big-endian |
| b denominator | `0x04` | unsigned u32 big-endian |
| arm label | `0x05` | ASCII `A`, `B`, or `D` |
| process replica | `0x06` | unsigned u32 big-endian |
| null replica | `0x07` | unsigned u32 big-endian; A/B sentinel is `0xffffffff` |
| query schedule | `0x08` | ASCII `prefix-v4` |

The seed bytes are `S` in that exact order. The counter starts at `c=0` and
increments by one for every consumed word, including rejected draws:

```text
digest_c = SHA256(ASCII("XOR-PRNG-v1") || u32be(len(S)) || S || u64be(c))
word_c   = first 8 digest bytes as an unsigned big-endian integer
byte_c   = word_c & 0xff
L        = floor(256/p) * p
accept   = byte_c < L
query_x  = byte_c mod p if accepted, otherwise null
```

The raw ledger records every consumed word as a JSON object with `counter`,
exactly 16 lower-case hexadecimal `word_hex`, two lower-case hexadecimal
`byte`, boolean `accepted`, zero-based `query_index` or JSON null, and
`query_x` or JSON null. A rejected draw has both index and x null. The accepted
stream is with replacement; no collision or table-membership condition may
consume a word. Any replay mismatch, omitted rejection, or unexplained
duplicate makes the arm `completed_invalid`.

The byte-level fixture in `validation_contract_xor_v4.json` is normative: for
`(campaign_seed,p,b_num,b_den,arm,process_replica,null_replica)=(1,101,2,5,D,0,0)`,
the first four counters are accept 87, reject, reject, accept 25, with their
full words and seed bytes retained. A future validator must recompute this
fixture before accepting any run.

## 3. Closed input domain and canonical identities

The exact matrix domain is the Cartesian product:

```text
p ∈ {101, 103, 107, 211}
(b_num,b_den) ∈ {(2,5), (1,2)}
m = 3
```

Every p is required to be prime and greater than three; the validator checks
the primality predicate rather than inheriting it from a source comment. The
eight cells are explicitly the lexicographically ordered pairs
`(101,2/5),(101,1/2),(103,2/5),(103,1/2),(107,2/5),(107,1/2),
(211,2/5),(211,1/2)`.

All decimal integers use `0|[1-9][0-9]*`, and b is never parsed from a binary
floating-point value. The factor-base size is the exact largest integer B with
`B^b_den <= p^b_num`, found by integer binary search. Curve search loops
`A=0..p-1`, then `B=0..p-1`, rejects singular curves, and selects the first
curve whose first on-curve point under the exact nested search
`x=0..p-1`, `y=0..p-1` has exact order at least five. The order is the least
positive k for which kP is the identity, using the audited group-addition
routine; a bounded-loop fall-through is not an order proof.

For every x, `lift_x` computes all roots and selects the smallest y in
`[0,p)`. The factor-base x list is the first B x values with a lift. The point
list is `(x,y)` followed by `(x,(-y) mod p)` when distinct, in x-list order.
The point-list cardinality F must be positive. The complete exhaustive output
`R_star` must also be nonempty before any q, denominator, coverage, or relative
metric is computed; otherwise the cell is `completed_invalid` with
`empty_reference_output`.

Every coordinate, point index, relation index, and count field has explicit
u32 big-endian encoding. The identity is exactly four bytes
`u32be(0xffffffff)` for NONE; a point is exactly `u32be(x)||u32be(y)`.
Relations are ordered u32 triples `(i1,i2,i3)`, permutations and signs remain
distinct, and output is `ASCII("RST2") || u32be(count) || sorted 12-byte tuples`.

## 4. Prefixes, wall interval, and selected estimands

For F>0, the only query prefixes are `q_k=(kF+3)//4` for k=1,2,3,4. B uses
point-list indices 0 through F-1. D uses its accepted random stream in the
same prefix schedule. D coverage is first-seen relation identity coverage
against nonempty `R_star`; missing targets are right-censored and never zero.

The charged wall interval is defined by the wrapper's monotonic clock:

```text
C_wall = t_monotonic(child_process_spawn_returned)
         through t_monotonic(child_process_exit_after_last_output_flush)
```

It includes process launch, input read, curve/factor-base setup, every E.add,
serialization, stdout/stderr writes, and the final output flush. It excludes
replay, global hashing, analysis, matrix aggregation, and Coordinator queue
operations, which are separately charged in campaign totals. The wrapper
records raw start/stop timestamps, clock source, exit status, and unit
(`seconds`, decimal). A/B use exactly five fresh processes per cell. A wall
estimand exists only when all five repeats are `completed_valid`; the selected
value is the median of the five raw C_wall values, with every repeat and reason
retained.

The only wall delta is the dimensionless signed relative quantity:

```text
Delta_AB_wall = (median(C_wall,A) - median(C_wall,B)) / median(C_wall,A)
```

It is positive when B is faster, zero when equal, and null when any required
repeat or output/control is invalid. `C_add` is the exact event count, and
`Delta_AB_add=(C_add,A-C_add,B)/C_add,A` is defined only after all five A and B
controls agree. No p-value, confidence interval, or pseudo-replication is
permitted.

## 5. Arm-wide event and conservation contract

The event ledger scope is one complete arm, not one prefix, table bucket, or
worker. Candidate and relation identity is the ordered point-index triple;
first-seen means first occurrence anywhere in that arm's canonical event
stream. Prefix views are projections of that arm-wide stream and never reset
the seen set. Table-key collisions are table events; query duplicates are query
events; candidate duplicates are counted before output deduplication.

The only phase keys are exactly
`{input,curve,factor_base,table,query,verify,serialize}`. `total` is outside
that set and is not included in the phase sum. The required equations are:

```text
candidate_attempts = candidate_verified + candidate_aborted
candidate_verified = relation_events + false_positive_events
relation_events = relation_unique + relation_duplicate_events
candidate_attempts = candidate_unique + candidate_duplicate_events
query_events = query_unique + query_duplicate_events
table_insert_events = sum(bucket_sizes)
event_count = sum(phase_counters[p] for p in the seven phases)
event_count = phase_counters.total = C_add_total
event_index set = {0,1,...,event_count-1}
```

Every E.add call, including an exception, emits exactly one event. An exception
has `outcome=exception`, null returned identity, a digest of exception type and
message, increments exception_count once, and terminates the arm without a
silent retry. Missing ledger bytes, missing counter fields, a non-contiguous
index, an unknown phase, or any failed equation makes the arm invalid and
ineligible for every comparison.

## 6. Versioned schemas and validator/fixture gate

The three task-local drafts are authoritative only after a future freeze copies
them byte-for-byte to `schemas/run-manifest-xor-v4.schema.json`,
`schemas/matrix-summary-xor-v4.schema.json`, and
`schemas/event-ledger-xor-v4.schema.json`. The run schema requires attempted
records, terminal relations, all source blobs, phase counters, event-ledger
hashes, candidate/query counters, and explicit timing/resource boundaries. The
matrix schema requires 400 entries, 4 shards, 100-key shard arrays, arm state,
resource bytes, and campaign totals. JSON Schema handles local shape and
state constraints; cross-object equations are handled by the versioned
validator contract and must not be replaced by prose.

`validation_contract_xor_v4.json` names the exact validator command, six
accepted fixture cases, nine negative mutations, semantic checks, and the
required hash bindings. The fixture files are task-local control records, not
run artifacts. Before approval the future freeze must create the validator
source at the command path, hash it and every fixture, run every accepted and
negative case, and record `VALIDATION_PASS`. Any failure blocks approval and
Executor admission. No experiment implementation is hidden in this gate.

## 7. Complete matrix, scheduling, and resource ledger

The canonical keys are:

```text
A/B: p,b_num,b_den,arm,seed=0,process_replica=0..4,null_replica=0xffffffff
D:   p,b_num,b_den,arm,seed=1..5,process_replica=0,null_replica=0..7
```

This is 40 A + 40 B + 320 D = 400 keys. Sort all keys by
`(p,b_num,b_den,arm,seed,process_replica,null_replica)` and assign shard
`ordinal mod 4`. Four shard workers execute concurrently; each shard processes
its 100 keys sequentially (`max_concurrent=1`). Thus
`worker_wall=max(shard.wall_seconds)`, while four arm processes can be active
at once. The matrix validator requires the exact complete key set, disjoint
100-key shard ownership, and shard numbers exactly 0,1,2,3.

The exact campaign equations and byte boundaries are:

```text
declared = attempted + not_attempted = 400
attempted = completed_valid + completed_invalid + failed_infrastructure
          + failed_implementation + resource_exhaustion + cancelled_by_budget
worker_wall = max(shard.wall_seconds)
campaign_wall = coordinator_wall + worker_wall + replay_wall + analysis_wall
                + hashing_wall + serialization_wall
campaign_cpu = sum(arm_cpu) + replay_cpu + analysis_cpu + hashing_cpu
              + serialization_cpu
host_rss_peak = max over each sampled time of coordinator_rss
                 + sum(rss of active shard workers)
output_bytes = arm_raw_bytes + arm_stdout_bytes + arm_stderr_bytes
             + replay_bytes + analysis_bytes + global_log_bytes
```

The wrapper records a monotonic interval for every arm and samples each
worker's resident set at process start, every event boundary, output flush,
and worker exit; the maximum sampled value is the declared metric. The
sampling schedule and platform byte conversion are recorded in the matrix
summary. `arm_raw_bytes` includes the manifest, event ledger, PRNG ledger,
canonical output, and arm metadata exactly once; stdout and stderr are separate
classes. Per-arm raw output is at most 64 MiB, RSS is at most 1 GiB, and the
campaign caps are wall <=1800 seconds, CPU <=4000 seconds, host RSS <= the
declared host reservation, and output <=
`400*64*1024*1024 + 256*1024*1024 = 27111981056` bytes. A cap breach records
the terminal state and leaves all undispatched keys `not_attempted`.

## 8. Immutable predecessor exclusion

The exact historical set is the three records
`EXP-XOR-7267e4`, `H-XOR-a227dc`, and `TASK-20260808-e6022f`, with their source
paths and hashes in `predecessor_exclusion_xor_v4.json`. A future specification,
approval lock, and dispatch plan must all bind that record and assert for every
member: historical=true, selected_contract=false, eligible_dependency=false.
The future validator fails on a missing member, hash mismatch, selected old
experiment/hypothesis/handoff, or old Executor task in the dependency closure.
This is a provenance/admission gate, not a change to the immutable predecessor
records.

## 9. Claim ceiling and next gate

This package carries `design-only` claim tier. It asserts no ECDLP observation,
cost result, security result, asymptotic result, or SOTA delta. All measured
fields remain null; planned counts are bookkeeping only. A fresh independent
freeze review must read this exact snapshot, run the validator/fixture gate,
and check the stale-predecessor exclusion before the Coordinator may create a
future frozen specification. If that review returns `REVISE` or `NO-GO`, create
another scoped successor and preserve every prior record. No implementation or
Executor run is authorized by this design.
