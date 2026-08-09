# Freeze-repair design v2 — canonical-output oracle/null cost instrument

Task `TASK-20260809-da79af`, BATCH-bd36fe. This is a Coordinator design
successor to the archived red-team report for `TASK-20260809-2d264c` and its
`REVISE` verdict. It is not an experiment specification, approval, freeze,
implementation, Executor admission, run, evidence record, hypothesis-status
transition, or goal transition.

The immutable inputs to this repair are:

- repaired design snapshot commit `af6e6f510f40a4db40a20bab0f22855518b9bbbe`,
  archived by `TASK-20260809-5d8ffb`;
- independent reviewer archive commit
  `58a470eebb2326577b67c600e973841e9a028d80`, archived by
  `TASK-20260809-41bbe3`;
- independent red-team archive commit
  `60bb4224f15727cbbce0be0b2b6a986f87797933`, archived by
  `TASK-20260809-503fdc`.

The future experiment identifier is freshly allocated and checked:
`EXP-XOR-44d232`. It has no implementation or run artifacts in this task.

## 1. Scope and the ten repair obligations

The exact future question remains toy-scale and instrument-oriented: does a
complete oracle-guided MITM implementation reach the same canonical relation
output as exhaustive enumeration with lower realized `E.add` count, and how
does a random-from-`F_p` true-null coverage curve behave at the same query
prefixes? The question is limited to `m=3`, `p ∈ {101,103,107,211}`, and
`b ∈ {0.4,0.5}`. It carries no ECDLP attack, security, asymptotic, exponent,
deployed-curve, or cryptographic-scale claim.

This version discharges the red-team findings as follows:

| finding | v2 gate |
|---|---|
| F-RT-001 | Exact canonical relation bytes, ordered point-index tuples, sign/multiplicity/deduplication rules, nonempty-output gate, and A/B byte equality are frozen below. |
| F-RT-002 | A canonical input serialization and digest is shared by A, B, and every D replica before table construction. Curve and factor-base selection are exact. |
| F-RT-003 | D uses an explicitly named unbiased `F_p` sampler with replacement, deterministic seed/replica derivation, and retained raw query stream; collisions are observations. |
| F-RT-004 | A complete prefix schedule and coverage estimands are defined. Raw D partial-output cost is diagnostic-only and cannot enter an A/B delta. |
| F-RT-005 | Every `E.add` call is event-ledgered, fresh-process setup is charged per arm, and conservation equations are independently replayed. |
| F-RT-006 | Freeze requires a complete non-null transitive `source_blobs` map and dependency-lock hashes; this design intentionally contains no implementation hash. |
| F-RT-007 | `C_add` is an exact per-cell estimand; wall time is descriptive across fresh process repeats, with no p-value or inferential F1 language. |
| F-RT-008 | Run-manifest terminal statuses, per-arm attempted/reason fields, and total resource equations use the repository enum and exclude non-valid arms from comparisons. |
| F-RT-009 | The old approved/frozen predecessor is historical and ineligible; a separate Coordinator supersession/ineligibility decision is required before any future freeze. |
| F-RT-010 | The Pareto audit includes every named current baseline, uses null for unmeasured dimensions, and separates planned arm-count arithmetic from measured SOTA deltas. |

The red-team finding is a design gate only. Passing this document does not
make any finding empirical and does not authorize the future experiment.

## 2. Frozen input identity and canonical relation output

The future specification must define a single serialized input blob before
any arm runs. Its fields, in this exact order, are UTF-8 ASCII lines:

```text
format=ECDLP-XOR-INPUT-v2\n
m=3\n
p=<decimal>\n
b=<decimal with one digit>\n
curve_a=<decimal>\n
curve_b=<decimal>\n
factor_base_x=<comma-separated decimal x values>\n
factor_base_points=<semicolon-separated decimal x,y pairs in F order>\n
```

The byte encoding is UTF-8 with no BOM and LF terminators. The curve is the
first lexicographic `(A,B)` nonsingular curve over `F_p` for which the
existing `harness.toycurve.EllipticCurve` search finds a point of order at
least five. The factor base is `floor(p**b)` on-curve x-coordinates in
increasing x order. For each x, the point list is `(x,y)` followed by
`(x,-y mod p)` unless the two points coincide. The list index in this exact
order is the point identity used by all arms. The future source must record
the resulting curve coefficients, factor-base list, and input-blob SHA-256;
no arm may independently reinterpret the rule.

The canonical output is a binary blob, not only a digest:

```text
magic: ASCII RST2
count: unsigned big-endian u32
records: count records, each three unsigned big-endian u32 point indices
```

Records are sorted lexicographically by `(i1,i2,i3)`, where the indices refer
to the exact point list above. A record is present exactly when
`E.add(E.add(F[i1], F[i2]), F[i3])` returns the identity. The tuple is ordered:
permutations are distinct records, both point signs are distinct identities,
and no quotient by sign is performed. There is no hidden multiplicity beyond
the ordered point-index tuple. Candidate events may repeat, but the canonical
output is deduplicated by its tuple identity before serialization. The
nonempty gate is `count > 0`; an empty `R_star` makes the cell
`completed_invalid` with reason `empty_reference_output`, never a zero-cost
comparison.

Arm A must emit the complete canonical blob `R_star.bin` and
`H_star = SHA256(R_star.bin)`. Arm B must emit the same bytes, byte-for-byte,
and independently recompute the same digest and count. A byte mismatch, count
mismatch, malformed record, or `H_star` mismatch is `completed_invalid` and
cannot enter any comparative metric. The report must preserve A and B blobs,
not only their hashes, so an independent parser can compare the bytes.

## 3. Arm and null protocol

The future implementation path is
`experiments/EXP-XOR-44d232/implementation/xor_cost.py`. It must reuse the
curve/factor-base machinery from
`experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py`, whose archived
reference SHA-256 is
`64d682e56e28472987ebd319f6250a09620c566ab7a881701d53acce3300a540`.
Reuse is a source audit requirement, not permission to copy an unverified
working-tree file.

Arm A exhaustively enumerates all ordered triples and emits `R_star`.
Arm B builds the same right-half table, queries the exact x-coordinate for
each left point, verifies candidates, and must emit exactly `R_star`.

Arm D is a true null and is never treated as an incomplete A/B solver. For
each D replica, the query stream is `Q=|F|` integers sampled uniformly from
`{0,...,p-1}` **with replacement**. The sampler is rejection-free: for each
query, draw a fixed-width unsigned integer from the approved PRNG and use the
specified unbiased rejection rule to avoid modulo bias. The raw query integer
stream is retained. Query duplicates, table-key collisions, opposite-sign
buckets, false candidates, and duplicate candidate identities are retained in
the event ledger and summary; no collision-free retry loop is allowed.

The seed tuple is `(campaign_seed, p, b, arm_label, process_replica,
null_replica)`. It is serialized with length prefixes and hashed into the
approved PRNG seed. A, B, and D use the same input blob, point list, table
construction, and prefix lengths. D values may differ; D input/table bytes may
not.

The controls are:

- `CTRL-INPUT-DIGEST`: all arms for a cell have the exact input-blob digest;
- `CTRL-OUTPUT-BYTES`: A and B canonical output blobs and counts are equal;
- `CTRL-TABLE-BYTES`: B and every D replica have the exact shared-table digest;
- `CTRL-PAIRED-PREFIXES`: B and D use the same query-prefix lengths;
- `CTRL-NULL-UNIFORM-REPLACEMENT`: sampler, raw stream, and duplicate counts
  prove uniform with-replacement generation;
- `CTRL-COST-EVENT-REPLAY`: independent replay of the event ledger equals all
  manifest phase and total counts;
- `CTRL-SOURCE-BLOBS`: every transitive source/dependency hash is non-null,
  recomputed, and bound before freeze.

## 4. Prefix estimands and the forbidden comparison

The complete query-prefix schedule is

```yaml
prefix_fractions: [0.25, 0.50, 0.75, 1.00]
prefix_lengths: floor(prefix_fraction * |F|), with |F| at least 1
coverage_targets: [0.25, 0.50, 0.75]
```

The implementation records, for every prefix `q`,
`R_A(q)=R_star`, `R_B(q)` for B's prefix, and
`R_D(q)=unique canonical identities observed by D through q`. The D coverage
estimand is
`coverage_D(q) = |R_D(q) ∩ R_star| / |R_star|`.

For each target `t` in `coverage_targets`, `C_add,D(t)` and `C_wall,D(t)` are
the first-prefix costs at which `coverage_D(q) >= t`. If no prefix reaches t,
the result is `target_not_reached` and is right-censored; no lower cost or
zero is imputed. Raw `C_add,D(q)` at a fixed prefix is retained as a
`diagnostic_only` field. It is forbidden to compute `C_add,A-C_add,D`,
`C_add,B-C_add,D`, or any raw D-to-A/B speedup field.

The only primary cost comparison is complete-output A versus B:

```yaml
Delta_AB_add: (C_add_A - C_add_B) / C_add_A
Delta_AB_wall: (C_wall_A - C_wall_B) / C_wall_A
```

The first is an exact per-cell operation-count ratio and the second is a
descriptive fresh-process wall-time ratio. Either is reported only when A and
B are both `completed_valid`, have equal canonical output bytes, and pass all
controls. No significance, confidence, or inferential F1 claim is permitted
in the future analysis. D coverage is reported as per-replica values plus
descriptive min/median/max across null replicas, with censoring counts.

## 5. Complete charged-cost event ledger

Each arm runs in a fresh process. The primary cost starts at the first input
read and ends after the last output flush; no shared setup is amortized. Every
call to `EllipticCurve.add`, including calls returning the identity and calls
that raise an implementation exception, emits one immutable event:

```yaml
event_index: monotonically increasing u64
phase: input|curve|factor_base|table|query|verify|serialize
operation: E.add
arguments_digest: sha256 of canonical point arguments
returned_identity: true|false|null
exception: null|string
```

`C_add_total` is the number of `E.add` events and equals the sum of the phase
counts. The manifest must also satisfy, per arm:

```text
query_events = query_unique + query_duplicate_events
candidate_events = candidate_unique + candidate_duplicate_events
candidate_verified_events = relation_events + false_positive_events
relation_events = relation_unique + relation_duplicate_events
table_insert_events = sum(bucket_sizes)
C_add_total = sum(C_add_phase[p] for every declared phase p)
```

An independent parser checks these equations, event indices, phase names,
and output identity membership. A mismatch makes the arm `completed_invalid`;
partial or invalid arms never enter a delta. A separate table-setup report may
show amortized values for context, but the primary `C_add` and `C_wall` values
remain fully charged fresh-process measurements.

## 6. Matrix, aggregation, and terminal status

The future matrix is exactly eight `(p,b)` cells, five fresh process replicas
for A and B, and eight D null replicas for each primary seed:

- A/B: `8 cells × 5 process_replica values × 2 = 80` invocations;
- D: `8 cells × 5 seed values × 8 null_replica values = 320` invocations;
- total maximum: `400` arm invocations, no Arm C invocation.

The order is lexicographic `(p,b,seed,arm_index)`, with A index 0, B index 1,
and D replica index `2 + null_replica`. The five A/B process replicas are
fresh-process repeats for descriptive wall time; they are not independent
mathematical instances. `C_add` is aggregated exactly per cell because it is
deterministic for a fixed input and source. Wall time is reported per repeat
and as min/median/max only. D reports every seed and replica before descriptive
aggregation. No p-value, confidence interval, or pseudo-replicated n=40 claim
is allowed.

Every per-arm manifest uses the repository run-manifest terminal enum:
`completed_valid`, `completed_invalid`, `failed_infrastructure`,
`failed_implementation`, `resource_exhaustion`, or `cancelled_by_budget`.
It also records `attempted: true|false` and a required `terminal_reason`.
`not_attempted` is a matrix bookkeeping state in the campaign summary, not a
run-manifest status. Every timeout, invalid, failed, unrun, or cancelled arm
consumes its declared budget and is excluded from comparative metrics.

## 7. Provenance, budgets, and no-run freeze gates

The future frozen specification must require these non-null pre-run fields:

- exact command, commit, dirty-tree state, environment/dependency versions,
  lockfile hashes, parameters, seed tuples, and source-blobs map;
- the SHA-256 of `xor_cost.py`, every imported repository module affecting
  curve/point arithmetic, PRNG, serialization, and counters, plus every
  dependency lock; no placeholder or producer-provided unchecked hash;
- stdout, stderr, raw event ledger, query streams, canonical A/B output blobs,
  D coverage data, collision summary, manifest, environment, resource usage,
  analysis, and unexpected-observations artifacts;
- requested policy, backend, resolved model identifier, model verification,
  reasoning effort, fallback, and degraded-requirements fields for the agent
  that creates each future artifact.

The future budget is 10 seconds wall and CPU per arm, 1 GiB peak RSS, 64 MiB
raw output per arm, four shards, 1,800 seconds total wall, and 4,000 seconds
total CPU. The present design task has one Coordinator dispatch invocation and
zero experiment invocations. A future resource cap cannot silently reduce the
matrix or convert unrun arms into data.

Before any future approval, a separate Coordinator decision must bind the
complete specification and source-blobs map, and must record that
`EXP-XOR-7267e4`, `H-XOR-a227dc`, and `TASK-20260808-e6022f` are historical
predecessor records, not the repaired contract. Those immutable records are
not edited here. A fresh independent freeze review must read that decision,
the exact specification, and the v2 snapshot before any Executor task is
created.

## 8. Pareto audit and quantitative pre-run bookkeeping

The row-by-row frontier audit is:

| row | time | memory | data/queries | output identity | cost status |
|---|---|---|---|---|---|
| `EV-ECDLP-65b004` | null, not reported | null, not reported | no charged query metric | yield/count only | no comparable charge |
| `EXP-SEMAEV-f48dd1` | null, historical wall only | null | old PRNG continuity arm | no canonical output blob binding | no comparable charge |
| `EXP-XOR-7267e4` | null, predecessor contract | null | 120-arm old grid | relation counts, not byte-bound output | stale/omitted event charge |
| `TASK-20260809-5d8ffb` | design-only | design-only | A/B/D proposal | raw D was not comparable | superseded design |
| `TASK-20260809-da79af` | design-only | design-only | 400 planned invocations | canonical bytes specified | unmeasured |

Every row was checked for dominance in all listed dimensions. No row supplies
the v2 complete-output/event-ledger contract, so `dominated_by: null` is
auditable for this design artifact only. Null means “not measured or not
comparable”; it is not a zero. The quantitative pre-run vector is:

```yaml
sota_delta:
  measured_time_delta: null
  measured_memory_delta: null
  measured_data_query_delta: null
  measured_complete_output_cost_delta: null
  planned_arm_invocations: 400
  predecessor_exp_xor_7267e4_arm_invocations: 120
  planned_arm_count_delta: 280
  inferential_claims: none
  unmeasured_fields_are_not_claims: true
```

The planned count delta is execution bookkeeping, not a performance or SOTA
claim. No breakthrough, support, weakening, rejection, closure, or security
conclusion is made.

## 9. Next gate

After this design and handoff are snapshot-archived, dispatch exactly one
fresh independent freeze review. If that review returns `PASS`, the Coordinator
may separately write and archive the frozen specification and predecessor
ineligibility decision. If it returns `REVISE` or `NO-GO`, create another
scoped successor and preserve this record. No implementation or Executor run
is authorized by this design.
