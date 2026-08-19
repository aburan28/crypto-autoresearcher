# Successor repair design — output-matched oracle/null cost instrument

Task `TASK-20260809-c21465`, BATCH-bd36fe. This is a Coordinator design
successor to the independent `REVISE` report
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/reviews/TASK-20260809-4a4203/review_report.yaml`.
It is a design artifact only. It does not approve, freeze, implement, execute,
interpret, or archive an experiment, and it changes no hypothesis or goal
status.

## 1. Scope and repair obligations

The predecessor design was rejected for approval consideration only because its
Arm D output was intentionally incomplete while its raw cost was compared with
the complete outputs of Arms A and B. It also left collision accounting,
budget semantics, retained Arm C, stopping logic, implementation provenance,
and the Pareto comparison under-specified. This successor addresses those
defects without changing the current batch claim ceiling:

- toy universe only: `m=3`, `p ∈ {101,103,107,211}`, `b ∈ {0.4,0.5}`;
- design and analysis validity only until a later Coordinator freeze;
- no ECDLP attack, security, asymptotic, exponent, cryptographic-scale, or
  deployed-scheme claim;
- no Executor task or experiment run is admitted by this record.

The historical Arm C is not a candidate in this repair. It remains a cited
continuity reference only, bound exactly to
`experiments/EXP-SEMAEV-f48dd1/specification.yaml` (SHA-256
`684b4d7f7d5193e2b3f7cbf731612c4d4fc87ca2bab9cf18f5b84cc09698988d`) and
`experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/analysis.yaml`
(SHA-256 `1f51fd95f5bdf87e3c4972ed612786ae9164f358aaebe5d5cb0d33b704083211`).
No new Arm C run is planned.

## 2. Charged-cost definition — before any comparison language

The future experiment is `EXP-XOR-0c39f3`. The word “speedup” is prohibited
unless its unit is named in the same sentence. Two separate costs are
pre-registered:

1. `C_add,j` is the exact count of every `harness.toycurve` `E.add` evaluation
   executed by arm `j`. The counter wraps the committed implementation path,
   including table construction, left-side preparation, oracle-query point
   additions, x-key extraction when it performs an addition, all candidate
   verification, x-bucket collision handling, point-sign normalization, and
   deduplication. The analysis may not replace this count with `2|F|^3` or a
   predicted formula. It must report the realized `|F|`, table rows, bucket
   sizes, duplicate triples, false candidates, verified candidates, and every
   add counter by cell, seed, arm, and phase.
2. `C_wall,j` is elapsed wall-clock time from the first input read through the
   last output flush, measured by a monotonic clock in a fresh process. It
   includes hashing, PRNG generation, memory allocation, lookup, logging, and
   serialization. The manifest records CPU time, peak RSS, disk bytes, and
   parallel-shard assignment separately. `C_wall` is not substituted for
   `C_add`, and a wall-clock comparison is never reported as an operation
   comparison.

The displayed asymptotic expressions are predictions only:
`C_add,A ≈ 2|F|^3` and `C_add,B ≈ |F|^2 + ...`; they are not accounting
identities. The primary normalized A/B quantity is
`Delta_AB_add = (C_add,A - C_add,B) / C_add,A`, evaluated only after both
arms reach the same deduplicated output target. A wall-clock analogue is
`Delta_AB_wall` and is labeled separately. The D arm has no raw same-task
speedup quantity; its valid comparison is the coverage-normalized curve
defined below.

## 3. Output targets and arm contract

For each `(p,b,seed)` cell, Arm A is the exhaustive reference. Its output is a
canonical sorted set of relation identities after sign normalization and
deduplication. Let `R_star` be that set and let `H_star` be its SHA-256 digest.
Arm B must return the same `H_star` and cardinality exactly; a mismatch is an
invalid control result, not evidence for or against a cost hypothesis.

Arm D is a matched true-null, not a cheaper incomplete solver. It emits a
coverage curve at query prefixes `q` and reports the deduplicated fraction
`coverage_D(q) = |R_D(q) ∩ R_star| / |R_star|`. Pre-registered target levels
are `Q = {0.25, 0.50, 0.75}`. For every target reached, define
`C_add,D(q)` and `C_wall,D(q)` as the cost at the first prefix reaching at
least `q`; if a null replicate never reaches `q`, the observation is
right-censored as `target_not_reached` and no lower cost is imputed.
Raw `C_add,D` at a fixed query count is retained as a null diagnostic but is
never compared with complete-output `C_add,A` or `C_add,B` as a same-task
result.

The valid questions are therefore separated:

- A versus B: same complete `R_star`, exact digest equality, paired cost
  comparison.
- D versus the A/B target: a coverage-normalized null curve at `Q`, with
  right-censoring and uncertainty; no raw partial-output speedup claim.
- Oracle-specific interpretation: permitted only if the A/B equality control
  passes and the D curve is analyzed at the same coverage targets. A D target
  that is not reached is unresolved, never a negative result.

## 4. Exact null and matched controls

For every `(p,b,seed)`, derive deterministic paired substreams by hashing the
tuple `(campaign_seed, p, b, arm_label, null_replica)` into the approved PRNG.
Arm A, B, and each D null replica use the same curve, factor-base bytes,
canonical table construction, query-prefix schedule, and output identity
encoding. Arm D draws an integer uniformly from `F_p` **with replacement** for
each query. Duplicate queries are retained. No ordinary random collision may
invalidate a run.

The raw result records separate counts for query-query duplicates,
query-table-key collisions, same-x opposite-sign buckets, candidate false
positives, candidate duplicates, and verified relation identities. It records a
digest of the shared table bytes and the complete seed/substream derivation.
It does not reject collisions or condition on a collision-free PRNG. The exact
controls are:

- `CTRL-OUTPUT-DIGEST`: A and B agree on `H_star` and `|R_star|`.
- `CTRL-SHARED-TABLE`: B and every D replica use identical table-byte hashes.
- `CTRL-PAIRED-QUERY-COUNT`: B and every D replica share each query-prefix
  length; the values, collisions, and replacements are allowed to differ.
- `CTRL-NULL-WITH-REPLACEMENT`: the D generator is uniform over `F_p` with
  replacement, and its raw collision counts are present.
- `CTRL-COST-REPLAY`: an independent parser recomputes every phase-level
  `C_add` total from the raw event ledger and matches the manifest.
- `CTRL-SOURCE-BLOB`: the future instrumented implementation is snapshot-bound
  before any run. The prior machinery reference is
  `experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py`, SHA-256
  `64d682e56e28472987ebd319f6250a09620c566ab7a881701d53acce3300a540`.
  The new instrumented source must be
  `experiments/EXP-XOR-0c39f3/implementation/xor_cost.py`; its exact hash is
  a mandatory non-null freeze field before approval and is deliberately absent
  now because this batch authorizes no implementation.

## 5. Matrix, metrics, and uncertainty

There are eight cells `(p,b)`, five primary seeds `{1,2,3,4,5}`, and eight D
null replicas `{0,...,7}` per seed. The future matrix is exactly:

- 80 A/B arm invocations: `8 cells × 5 seeds × 2 arms`;
- 320 D invocations: `8 cells × 5 seeds × 8 replicas`;
- 400 maximum arm invocations total; no C invocation.

The deterministic order is lexicographic `(p,b,seed,arm_index)`, with
`A=0`, `B=1`, and `D replica r = 2+r`. Primary metrics are, per cell and
seed: `H_star`, `|R_star|`, `C_add` by phase, `C_wall`, `coverage_D(q)` for
each `q ∈ Q`, and the collision/candidate counts above. Secondary resource
metrics are CPU, peak RSS, disk bytes, table size, and lookup probes.

The analysis reports every seed and null replica before aggregation. A paired
bootstrap over the five primary seeds, using a declared analysis seed, gives
intervals for `Delta_AB_add` and `Delta_AB_wall`; D coverage intervals use the
eight null replicas and report right-censored targets explicitly. No arbitrary
0.95 threshold is used. A missing target, invalid control, or unexpected
observation is a named result class and is never silently discarded.

## 6. Falsification and stopping rules

Predictions are:

1. B reaches `R_star` exactly and has lower `C_add` than A on the paired
   complete-output comparison in the declared cells.
2. D coverage is lower and more variable than B at the same query prefixes,
   but its curve is measured rather than inferred from raw partial cost.
3. Any observed D curve may be consistent with, or contradict, the null model;
   the result is scoped to the tested toy cells and null replicas.

Falsification/validity gates are:

- `F0`: A/B digest mismatch, malformed identity, or cost-replay mismatch makes
  that cell invalid; it is not mathematical evidence.
- `F1`: after valid cells only, the pre-registered paired interval for
  `Delta_AB_add` fails to support the direction `C_add,B < C_add,A` in a cell;
  report the cell and keep the scoped hypothesis unresolved or weakened as the
  Coordinator later decides. Do not close a lane automatically.
- `F2`: a D target not reached is right-censored. A reached D curve is compared
  only at `Q` to its coverage target and uncertainty interval; raw `C_add,D`
  never triggers an A/B speedup conclusion.
- `F3`: a control, timeout, resource cap, or implementation mismatch fires an
  infrastructure/invalid branch. It never closes the hypothesis.

All planned cells run in the fixed order. There is no early mathematical stop.
If the global resource cap stops collection, every unrun cell is marked
`not_attempted` or `cancelled_by_budget` with its reason. Collection stopping
does not close a direction and cannot change official status; only a later
Coordinator decision may interpret the complete review chain.

## 7. Future experiment budget and required artifacts

This task is design-only. Its dispatch invocation budget is one Coordinator
task invocation (`maximum_runs: 1`) because the dispatcher requires a positive
task budget; its experiment-run budget is exactly zero. The future frozen
experiment, if separately approved, has:

- 400 maximum arm invocations;
- 10 seconds wall and 10 seconds CPU per arm cap;
- 1 GiB peak memory cap and 64 MiB raw output cap per arm;
- four parallel shards, 1,800 seconds total wall cap, and 4,000 seconds total
  CPU cap; the Coordinator reconciles actual shard accounting before admitting
  execution;
- timeout/resource exhaustion/invalid control recorded as terminal non-evidence
  and counted against the cap.

Before approval the future specification must list, and every run must retain:
the exact command; Git commit and dirty-tree state; environment and dependency
versions; all cell, seed, replica, and substream values; policy/backend/
resolved-model/model-verification/reasoning/fallback/degraded metadata; stdout,
stderr, raw per-arm event ledgers, collision summaries, coverage curves,
`manifest.json`, `environment.json`, `resource_usage.json`, `analysis.yaml`, an
`unexpected_observations.yaml`, and the implementation/source hashes. The
specification and amendment directory, run package, snapshot receipt,
independent validator/red-team reports, and later ledger archive are all
required paths. None exists or is executable as a result of this design task.

## 8. Pareto audit and quantitative pre-run delta

The frontier rows checked for this design are:

| row | time | memory | data/queries | output | cost-model status |
|---|---|---|---|---|---|
| `EV-ECDLP-65b004` | not reported | not reported | no charged query metric | yield-only A/B scope | no charged model |
| `EXP-SEMAEV-f48dd1` | not reported | not reported | PRNG-null continuity | historical grid | no charged model |
| `TASK-20260809-9d39e8` | design-only | design-only | A/B/D proposal | raw D was output-mismatched | predecessor under review |

Every row was checked for whether it dominates this repaired contract on all
four axes. None supplies the repaired output-matched cost/coverage contract,
so `dominated_by: null` is auditable here; the table does not claim that the
future run will improve any measured cost.

The quantitative pre-run `sota_delta` vector is:

```yaml
sota_delta:
  complete_output_target_delta_vs_EV-ECDLP-65b004: 0.0
  candidate_arm_count_delta_vs_EXP-SEMAEV-f48dd1: 2
  D_null_replicates_per_seed: 8
  coverage_targets: 3
  measured_C_add_delta: null
  measured_C_wall_delta: null
  unmeasured_fields_are_not_claims: true
```

`measured_C_add_delta` and `measured_C_wall_delta` are explicitly unmeasured,
not zero or an implied speedup. The design does not call itself a breakthrough
or a state transition.

## 9. Single next action

After this repair is independently reviewed and its exact artifacts are
snapshot-archived, the Coordinator may decide whether to freeze a separate
experiment specification. Until then, no implementation or Executor task is
authorized.
