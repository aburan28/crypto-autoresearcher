# Freeze-repair design v3 — executable schema and accounting contract

Task `TASK-20260809-47ae98`, BATCH-bd36fe. This is a Coordinator design
successor to the archived `REVISE` review
`TASK-20260809-9b8b55`. It is design-only: it creates no implementation,
experiment specification, approval, freeze, Executor task, run, evidence,
hypothesis transition, or goal transition.

The exact immutable inputs are the v2 snapshot
`d79bb2957076c5991287be052dd34f119785806c`, its review archive
`a2ad14f9e3b61e564c117b638ce69cce746481bc`, and the prior red-team archive
`60bb4224f15727cbbce0be0b2b6a986f87797933`. The future experiment remains the
freshly allocated `EXP-XOR-44d232`; no implementation or run record exists.

## 1. Seven new findings and their direct artifacts

| finding | v3 discharge |
|---|---|
| F-NEW-001 | Section 2 defines `XOR-PRNG-v1`, fixed-width words, rejection threshold, length-prefixed seed encoding, every seed/replica label, consumed-word retention, and accepted-query replay. |
| F-NEW-002 | Section 3 defines canonical decimal grammar, exact rational `b`, integer rational-power floor, exact curve order predicate, `lift_x` root selection, point-list cardinality, identity encoding, and per-cell input digests. |
| F-NEW-003 | Section 4 enumerates exact prefixes from the point-list order and selects median-of-five wall time only when all five repeats are valid. |
| F-NEW-004 | Section 5 defines ordered tuple identities, first-seen/duplicate scope, contiguous event indices, exception/aborted-candidate counters, and an exact phase-counter schema. |
| F-NEW-005 | The task includes hashable versioned `run_manifest_xor_v3.schema.json` and `matrix_summary_xor_v3.schema.json`; Section 7 binds their installation, hashes, six-hex IDs, attempted/terminal/source/matrix fields, and example validation before freeze. |
| F-NEW-006 | Section 6 enumerates every arm key, four shard assignment, concurrency, and exact worker/replay/analysis/hash/serialization/resource/output equations. |
| F-NEW-007 | The task includes machine-readable `pareto_audit_v3.json` with explicit `dominated_by`, row-wise comparability/reasons, null measured fields, and separate planned bookkeeping. |

The v3 artifacts are drafts for a future freeze task. Their existence is not
permission to use them as a run manifest or to modify the global schemas.

## 2. Exact null generator and replay stream

The future specification shall use the named deterministic generator
`XOR-PRNG-v1`, implemented as a SHA-256 counter stream rather than a runtime
library PRNG. For seed bytes `S`, counter `c` is an unsigned big-endian u64 and
the consumed word is:

```text
digest_c = SHA256(ASCII("XOR-PRNG-v1") || u32be(len(S)) || S || u64be(c))
word_c   = first 8 digest bytes interpreted as a big-endian unsigned integer
```

For the current `p ≤ 211`, `randbelow_p` consumes the low unsigned byte of
each word. Let `L = floor(256/p)*p`. If the byte is `< L`, accept
`x = byte mod p`; otherwise record a rejected draw and consume the next word.
There is no collision retry and no rejection based on table membership.
The exact algorithm is valid for every future `p` only after the specification
sets `w = 8*ceil(bit_length(p)/8)` and replaces `256` by `2**w`; for this toy
matrix it is fixed at `w=8` and the future source must reject a different p.

The seed tuple is serialized as a sequence of typed, length-prefixed fields:

```text
field := one-byte type tag || u32be(byte_length(value)) || value bytes
campaign_seed: u64be, p: u32be, b_num: u32be, b_den: u32be,
arm: ASCII label, process_replica: u32be, null_replica: u32be,
query_schedule_id: ASCII "prefix-v3"
```

`null_replica=0xffffffff` is the sentinel for A/B. A/B use `seed=0` and
`process_replica ∈ {0,1,2,3,4}`. D uses `seed ∈ {1,2,3,4,5}`,
`process_replica=0`, and `null_replica ∈ {0,...,7}`. All five seeds, all eight
null replicas, all five A/B process replicas, all eight `(p,b)` cells, and all
three arms are enumerated in the matrix summary and arm-key list; no implicit
or producer-selected label is allowed.

The raw PRNG ledger retains, for every consumed counter, `counter`, `word_hex`,
`byte`, `accepted`, `query_index` (or null for a rejection), and accepted
`query_x`. The accepted query stream and duplicate count are also retained.
An independent replay regenerates every word and accepted query from the seed
tuple. A mismatch, missing rejected draw, or unexplained duplicate count makes
the arm `completed_invalid`; ordinary duplicates are not themselves invalid.

## 3. Canonical input and relation identity

All decimal integers use the grammar `0|[1-9][0-9]*`; no sign, whitespace, or
leading zero is accepted. The registered b values are exact rationals:
`0.4` means `(b_num,b_den)=(2,5)` and `0.5` means `(1,2)`. The factor-base
cardinality is the exact integer

```text
B = max { t ∈ Z_{≥0} : t^b_den ≤ p^b_num }
```

computed by integer binary search; floating-point exponentiation is forbidden.

For each p, the curve search enumerates `A=0,...,p-1`, then `B=0,...,p-1`,
rejects singular curves, and accepts the first curve for which the exact point
order of the first lexicographically found on-curve point is at least five.
The exact order is the least positive `k` for which `kP=O`, found by the
repository's auditable group addition; no “no identity in a bounded loop”
shortcut is permitted. `lift_x(x)` computes all square roots, selects the
smallest y in `[0,p)`, and returns `(x,y)`; the negated point is
`(x,(-y) mod p)` and is appended only when distinct. The factor-base x list is
the first B x values with a lift, and F is the resulting point-list cardinality.

The canonical input blob is UTF-8 ASCII LF text with exactly these fields in
this order and the exact decimal grammar:

```text
format=ECDLP-XOR-INPUT-v3\n
m=3\n
p=<p>\n
b_num=<b_num>\n
b_den=<b_den>\n
curve_a=<a>\n
curve_b=<b>\n
factor_base_size=<B>\n
factor_base_x=<x0,x1,...>\n
factor_base_points=<x0:y0;x1:y1;...>\n
point_list_cardinality=<F>\n
identity_encoding=NONE=ffffffff;POINT=u32be(x)||u32be(y)\n
```

The SHA-256 of this blob is `input_digest` and is required to match in A, B,
and every D replica before table construction. A canonical point index is the
zero-based index in `factor_base_points`. A relation identity is the ordered
u32 tuple `(i1,i2,i3)`; permutations and both signs remain distinct, and no
quotient by sign is applied. The binary `RST2` output is `ASCII("RST2")`, a
big-endian u32 count, and lexicographically sorted 12-byte tuples. A and B
must retain and compare the complete bytes, count, and SHA-256 digest. Empty
output is `completed_invalid:empty_reference_output`, never a zero denominator.
Candidate duplicates are counted in the ledger, then deduplicated by tuple
identity for the output and coverage set.

## 4. Prefixes and exactly selected wall estimands

Let F be the point-list cardinality. The complete query schedule is the four
point-list prefixes:

```text
q_k = ceil(k*F/4) = (k*F + 3)//4 for k in {1,2,3,4}
```

The query order is point-list index 0 through F-1 for B. D consumes its
accepted random stream in that same prefix schedule. The future source emits
all four q values, query counts, and coverage values for every valid arm;
there is no unspecified prefix ordering.

For reference, A's complete canonical set is `R_star`. For each prefix q,
`R_D(q)` is the set of first-seen relation tuple identities verified by D and
`coverage_D(q)=|R_D(q) intersect R_star|/|R_star|`. D target levels are
`{0.25,0.50,0.75}`. The cost at the first q reaching a target is recorded;
missing targets are `target_not_reached` and right-censored. Raw D partial cost
is diagnostic-only and cannot appear in an A/B delta.

For each cell and arm A/B, exactly five fresh processes are required. The
single wall-time estimand is the median of those five `completed_valid`
`C_wall` values. If any of the five repeats is not `completed_valid`, the cell
has no wall estimand and `Delta_AB_wall` is null with a reason. Every repeat
value is retained. `C_add` is an exact per-cell value only when all five A and
all five B output/control records agree; otherwise `Delta_AB_add` is null and
the cell is excluded. No inferential p-value or confidence interval is
permitted.

## 5. Exception-aware event ledger and conservation

The future wrapper emits a zero-based contiguous `event_index` for every
attempted `E.add` call. Each event has `phase`, canonical argument digests,
`outcome` in `{returned, exception}`, returned point/identity encoding, and a
digest of the exception type/message when applicable. An exception event still
counts exactly once in `C_add_total`; the arm must then terminate invalid or
failed according to the run schema. The wrapper cannot silently retry an
exception.

Every candidate attempt has an ordered point-index tuple and a first-seen
boolean. The manifest counters are:

```text
candidate_attempts = candidate_verified + candidate_aborted
candidate_verified = relation_events + false_positive_events
relation_events = relation_unique + relation_duplicate_events
candidate_attempts = candidate_unique + candidate_duplicate_events
query_events = query_unique + query_duplicate_events
table_insert_events = sum(bucket_sizes)
event_count = sum(phase_counters[p]) = C_add_total
event_index values = 0,1,...,event_count-1
```

`candidate_aborted` includes an exception or early termination before
verification completes. A non-reconciling counter, missing event, duplicate
event index, unknown phase, unexplained exception, or output identity absent
from the input point list makes the arm invalid and ineligible for any delta.
The exact phase counters and all required manifest fields are defined in
`run_manifest_xor_v3.schema.json`; the matrix state and resource counters are
defined in `matrix_summary_xor_v3.schema.json`.

## 6. Complete matrix, shard, and resource equations

The canonical arm keys are:

```text
A/B: (p,b_num,b_den,arm,seed=0,process_replica=0..4,null_replica=ffffffff)
D:   (p,b_num,b_den,arm,seed=1..5,process_replica=0,null_replica=0..7)
```

This gives `8*5*2=80` A/B and `8*5*8=320` D invocations, exactly 400.
Sort all keys lexicographically by `(p,b_num,b_den,arm,seed,process_replica,
null_replica)`, then assign `shard = ordinal mod 4`. Four shard workers run
sequentially (`max_concurrent=1` per shard; four active processes maximum).
The matrix summary contains all 400 keys, even when an arm is unattempted.

The future caps are 10 seconds wall and 10 seconds CPU per arm, 1 GiB peak
RSS, and 64 MiB output per arm. Campaign caps and exact equations are:

```text
worker_wall = max(shard.wall_seconds)
campaign_wall = coordinator + worker_wall + replay + analysis + hashing + serialization
campaign_cpu = sum(arm_cpu) + replay_cpu + analysis_cpu + hashing_cpu + serialization_cpu
host_rss_peak = max_t(sum(rss_of_active_shards_at_t) + coordinator_rss_at_t)
output_bytes = sum(arm_raw + arm_stdout + arm_stderr) + replay + analysis + global_logs
declared_counts = attempted + not_attempted
attempted = valid + invalid + failed_infrastructure + failed_implementation
               + resource_exhaustion + cancelled_by_budget
```

The caps are `campaign_wall ≤ 1800`, `campaign_cpu ≤ 4000`, and
`output_bytes ≤ 400*64MiB + 256MiB = 27111981056`. `host_rss_peak` is bounded
by the four-shard host reservation and reported in bytes. Replay, hashing,
serialization, and analysis are charged in campaign totals even though they
are outside per-arm `C_wall`. A cap breach records the applicable terminal
state and preserves every unattempted arm as `not_attempted`; it never shrinks
the declared matrix or closes a direction.

The run-manifest schema uses six-hex random suffixes for fresh `EXP-*` and
`RUN-*` IDs and requires `attempted`, `terminal_reason`, `source_blobs`,
`matrix_key`, and phase counters. The matrix schema permits the explicit
unattempted bookkeeping state while preserving the repository run-manifest
terminal enum for actual run artifacts.

## 7. Schema installation and validation gate

Before any future freeze, the Coordinator must create versioned authoritative
copies at `schemas/run-manifest-xor-v3.schema.json` and
`schemas/matrix-summary-xor-v3.schema.json`, byte-identical to the two task
drafts, record their SHA-256 hashes in the frozen experiment specification,
and validate six fixtures: completed-valid, completed-invalid,
failed-infrastructure, resource-exhaustion, cancelled-by-budget, and an
unattempted matrix arm. The run schema must reject a missing attempted flag,
terminal reason, source blob, matrix key, phase counter, or an old numeric-only
ID. The matrix schema must reject fewer/more than 400 arm keys, duplicate arm
keys, totals that fail the equations, or missing unattempted entries.

No global schema is edited by this design task. The future freeze task owns the
authoritative copy and hash binding; until then, the drafts are ordinary
design artifacts and no run can be admitted.

## 8. Machine-readable Pareto audit

`pareto_audit_v3.json` is the structured record for this design. It contains
every current relevant row (`EV-ECDLP-65b004`, `EXP-SEMAEV-f48dd1`,
`EXP-XOR-7267e4`, `TASK-20260809-5d8ffb`, `TASK-20260809-b41925`, and this
task), each axis as `{value, comparable, reason}`, explicit
`dominated_by: null`, and a `sota_delta` object. Measured time, memory,
data/query, output, and charge fields are all null because no v3 run exists.
Planned arm counts and shards are under `planned_bookkeeping`, not
`sota_delta`. The record is therefore auditable without turning a planned
400-arm matrix into evidence or a zero-performance claim.

## 9. No-run boundary and next gate

The present dispatch task has one Coordinator design invocation and zero
experiment invocations. The v3 design, schema drafts, Pareto record, and
handoff must be snapshot-archived together. A fresh independent
`review-adversarial` freeze review must then inspect that exact snapshot. Only
after a `PASS` may the Coordinator separately create a frozen experiment
specification, install/hash-bind the schemas, write the predecessor
ineligibility decision, and request Executor implementation. A `REVISE` or
`NO-GO` creates another superseding design record and preserves this one.
