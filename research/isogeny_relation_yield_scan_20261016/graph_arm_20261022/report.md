# Graph-transported factor-base arm: fixed implementation control

**Date:** 2026-10-22 PDT. **Task:** Conductor T-4748, fence epoch 1.
This records input-construction observations only. It is not a scientific
relation-yield comparison or an ECDLP runtime result.
The implementation and raw fixed-control files were committed as `366dd01f19`.
The controls ran against those file contents in a working tree with this report
still uncommitted; the exact test output is [`test.stdout`](test.stdout).

## Question and exact scope

Can the prospective graph-wide collector prepare the image of the source
`low_x` factor base at the scheduled P29 and P37 check vertices, while keeping
the same generator, Q, and target coefficients as each vertex's native base?
The archived walks are `walk-p29-2048-attempt2.jsonl` and
`walk-p37-256.jsonl` [internal: `../manifest-v2.json`]. The P29 group is
`E/F_320092037: y²=x³+105931039x+284015384`, prime order `320091991`,
source `G=(0,50656410)`. The P37 group is
`E/F_81640512137: y²=x³+46677163888x+11713815639`, prime order
`81640511861`, source `G=(39752613976,79465703431)` [internal: archived
walk headers]. Each saved edge is a degree-7 separable map over its base field.
The target group and transported generator identity at each check vertex are
bound to the archived checkpoints.

## Implementation and checks

`preparation/prepare_graph_input.py` now accepts `graph_transport` only at
indices divisible by eight on P29 or four on P37. It reads that vertex's
archived checkpoint, checks the walk hash, field, group order, stride, model,
generator, signed-base count and point-list digest, and records the selected
checkpoint, manifest and terminal checkpoint hashes in the prepared metadata.
Its CLI requires the post-freeze seed commitment to include the transport
manifest and terminal hashes. `preparation/verify_prepared_graph.py` independently
checks the prepared signed pairs, group equations, actual walk hash and exact
checkpoint point list and binding. The full-chain map replay remains the
separate archived verification in [P29](../path_transport/full_path_20261016/report.md)
and [P37](../path_transport/p37_full_20261021/report.md).

The fixed public roots `B×32` and `T×32` generated eight target coefficients
per case solely for implementation checks. `python3 -B
research/isogeny_relation_yield_scan_20261016/preparation/test_prepare_graph_input.py`
passed **26** arm/vertex cases across both strata, including rejection of a
noncheck vertex and an altered checkpoint digest. The source `graph_transport`
base equals source `low_x`; at the first check vertex it is distinct from the
native `low_x` base. The direct metric command was `python3 -B
research/isogeny_relation_yield_scan_20261016/graph_arm_20261022/control_metrics.py`.
Its raw output is [`control-metrics.json`](control-metrics.json) [internal].

| Stratum and vertex | Base x-orbits | Native/graph x overlap | Q and G equal | Targets |
| --- | ---: | ---: | --- | ---: |
| P29 source 0 | 256 | 256 | yes | 8 |
| P29 check 8 | 256 | 0 | yes | 8 |
| P37 source 0 | 1,600 | 1,600 | yes | 8 |
| P37 check 4 | 1,600 | 0 | yes | 8 |

These overlap counts are derived from the fixed prepared point lists. Zero
overlap at the two check vertices does not predict relation yield or rank.
The editable [diagram source](diagram.dot) and [SVG](diagram.svg) show the
exact tested map prefixes and their base identities.

## Boundary and next check

No discovery or confirmation root has been drawn here. The 6,918 mandatory
native-base arms, check-vertex control quotas, ordered-count oracle, useful
rank verifier, and same-point end-to-end solve path remain to be frozen in a
runnable Coordinator contract [internal: `../discovery_capacity_20261022/report.md`,
`../../../problems/isogeny-graph-wide-relation-solver.md`]. The next check is
to bind the independent count/rank collector and all four check-vertex
controls to the post-freeze target stream, then obtain execution-state ready
and Coordinator approval before discovery trials. The P29/P37 canonical
graphs were checked: this implementation control adds no new curve, map, or
yield edge, so no earlier canonical graph changes.
