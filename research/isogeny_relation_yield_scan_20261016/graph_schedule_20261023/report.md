# Complete candidate graph discovery schedule

Date: 2026-10-22 (America/Los_Angeles). Conductor task: T-4766. Source branch:
`codex/ectd-graph-executor-20261022`. Status: **candidate, unapproved**.

This materializes one explicit resolution of the [draft protocol](../PROTOCOL-original-draft.md)'s
check-arm ambiguity. At every preselected check vertex, give `power_x`, the
graph-transported source `low_x`, `u2_native`, and `u2_transport` their own full
discovery quota. The last arm transports that vertex's native `low_x` base and
target by `(x,y) -> (4x,8y)`; its targetwise count reference is the same
vertex's `low_x` arm. The graph-transported source base instead references the
source `low_x` arm. Both exact-oracle comparisons must match target by target
on the committed discovery stream. The two `u=2` arms are separately named so
coordinate sensitivity is visible rather than pooled with graph transport.

| Stratum | Vertices | Check vertices | Main arms | Check arms | All arms | Targets/arm | Target probes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P29 | 2,049 | 257 | 6,147 | 1,028 | 7,175 | 8,192 | 58,777,600 |
| P37 | 257 | 65 | 771 | 260 | 1,031 | 2,048 | 2,111,488 |
| Total | 2,306 | 322 | 6,918 | 1,288 | **8,206** | mixed | **60,889,088** |

The ordered, write-once [schedule](discovery-arms.jsonl) retains all 6,918
previously verified main-arm rows unchanged and inserts check arms immediately
after them at the fixed indices. Its SHA-256 is recorded in [manifest.json](manifest.json),
which also binds the graph, original main-arm plan and verification, planner,
and terminal transport checkpoints. Each graph-transport arm additionally binds
its exact indexed checkpoint digest. The [independent verifier](verify.py)
replayed both archived walks using separate group arithmetic, checked all
2,306 generator subgroup equations, all 8,206 arm identities and quotas, and
all 322 indexed checkpoint bindings. Its [receipt](verification.json) reports
`pass` for this *schedule identity*. The diagram [arms.svg](arms.svg) and
[report.pdf](report.pdf) display these recorded counts.

This artifact has no root commitment, prepared targets, relation output, rank,
solver run, or Coordinator approval. It therefore changes no hypothesis status
and is not an `EXP-*` contract. The Coordinator must decide whether to adopt
this four-control mode, bind source and executable hashes, freeze roots and
artifact custody, create a runnable experiment plus handoff, and issue admission
under the standing authorization. Discovery then runs through `run`, retaining
all failed and censored arms. Fresh confirmation and complete same-point solve
stages remain as specified in the draft; this schedule does not shorten them.

The choice adds 2,238,464 target probes over the earlier three-control
inventory. This is a workload count, not a runtime estimate. Operational chunks
may be chosen after measuring the first admitted arms, but a chunk cannot omit
or reselect an arm.

Provenance: archived walks, main-arm plan, and checkpoint chain are `internal`
sources; this report's schedule and verification are new `internal` artifacts.
