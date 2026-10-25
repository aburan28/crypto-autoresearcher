# Full-quota P37 graph input preparation control

**Date:** 2026-10-22 America/Los_Angeles. **Conductor task:** T-4822.
**Scope:** implementation control at P37 vertex 0, with public roots. This
report records preparation and replay observations only. It makes no relation
yield, useful-rank, ECDLP-cost, or hypothesis-status decision.

The question was whether one schedule-bound materializer could preserve the
exact discovery coefficient stream while making three separately identified
P37 arms: native `low_x`, `u2_transport`, and `graph_transport`. The input was
the independently checked [8,206-arm candidate schedule](../graph_schedule_20261023/report.md),
the certified P37 256-edge walk, and [public control roots](../seed_custody_20261022/report.md).
The public roots and [control commitment](control/commitment.json) are marked
`control_only`; the scientific roots remain to be committed after source freeze.

The [source](materialize.py) checks schedule and graph digests, root and source
commitments, arm identity, P37's exact 2,048-target quota, the prepared rows,
and the reconstructed coefficient vector before writing `binding.json`. A
separate `check` action recomputes that binding. The saved [control check](control/checks.json)
replayed three full-quota arms: each has 3,200 signed base points and 2,048
targets. Each prepared input passed the existing independent group-law checker
on all those points. Its `deterministic_seed_replay` field is false because
that checker was invoked without seed files; the materializer separately
reconstructed and compared every target coefficient from the supplied roots.

The three `coefficient_vector_sha256` values match at
`d1badde64225ab5b35faef9ba9239ccbd31394cd16557d43a686380eaae958fb`.
At index zero, native and graph-transport prepared input bytes are identical.
The `u2_transport` base and all 2,048 target points match `(x,y) -> (4x,8y)`
pointwise against native input. Swapping a root, requesting an unscheduled
check arm, and changing one target coefficient were each rejected. The raw
inputs, manifests, bindings, preparation stdout/stderr and measured preparation
process wall durations are retained under [control](control/).

The [diagram](diagram.svg) shows this control's three prepared arms and the
later admission boundary. No relation collector or rank solver ran in this
control. The result checks one source vertex and three arms; it does not
establish discovery-stream transported-base count conservation at later check
vertices or graph-wide yield. The next step is to freeze scientific roots and
an approved `EXP-*` contract, bind the materializer and arm runner by source
commit, and run the fixed schedule through `run` with exact count and rank
replay. The study's canonical [graph](../graph.svg) was checked and left
unchanged because this control does not change certified vertices or edges.

[PDF](report.pdf) · [Control checks](control/checks.json) ·
[Preparation receipts](control/prepare-results.json) · [Problem record](../../../problems/isogeny-graph-wide-relation-solver.md)
