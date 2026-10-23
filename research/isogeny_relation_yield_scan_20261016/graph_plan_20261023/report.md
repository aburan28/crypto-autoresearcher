# Study-level graph admission implementation control

**Date:** 2026-10-23 America/Los_Angeles. **Conductor tasks:** T-4830, T-4834,
and T-4838. This is an executor-admission and trial-plan implementation control.
It records code and guard behavior; it makes no scientific relation-yield,
rank, or ECDLP claim and grants no Coordinator approval.

The graph runner previously required a separate admission for every prepared
arm. The new `ectd.graph-study-admission.v1` check permits one Coordinator
decision to bind the whole P29/P37 schedule, while still checking each arm's
prepared-input digest before the relation collector starts. The binding covers
the complete schedule and verifier, both graph commitments, shared roots,
source commit and file hashes, collector binaries, and experiment output
prefix. `graph_transport` rows also require their scheduled checkpoint, chain
manifest, and terminal checkpoint digests to match the prepared input.

The [saved guard checks](control/) show refusals at the study boundary for
candidate status, a non-Coordinator approver, and an unknown admission schema;
they also verify the authorized execution stage is present in both the
Coordinator decision and frozen specification. The materializer replay still
passes all three full-quota P37 vertex-zero inputs and rejects swapped roots,
an unscheduled arm, a changed target, and a changed graph checkpoint. The
trial adapter now passes the materializer binding to each study-admitted arm,
and the independent checker replays that binding and the frozen approval
identity. The [diagram](diagram.svg) shows where the study-wide decision is
reused and where per-arm data are rechecked.

The [plan compiler](build_discovery_plan.py) now emits one runbook trial per
scheduled arm. Its 8,206-row shape test passes, and the complete plan also
passes the repository's `experiment_execution.load_plan` validator. This
checks the actual supervisor schema, unique RUN IDs, command/source bindings,
artifacts, watchdogs, memory limits, and dependency ordering. It does not
launch any arm. A second full 8,206-row candidate fixture passes the same
loader only in explicit candidate-readiness mode and is refused by its default
execution mode.

A separate candidate-only compiler path writes `candidate-trial-plan.json`
for a frozen, unapproved `review_required` specification. The explicit
`newest_experiments --experiment EXP-*` query now reports candidate readiness
only when every row is valid and planned; default discovery omits candidates.
The run loader and public runner refuse the candidate plan, and approval still
requires a fresh approved plan and dispatch queue. The focused readiness tests
cover both sides of that boundary. Both plan paths bind
`stop_on_invalid_output: true`; the supervisor stops on the first invalid
certificate while preserving its receipt. Timeout and infrastructure failures
remain recorded under their separate statuses.

The plan is still discovery-only. The full protocol also requires independently
committed fresh confirmation and solve streams. No scientific roots or
canonical frozen `EXP-*` contract are present, and no relation collector ran.
The canonical [isogeny graph](../graph.svg) was checked and left unchanged;
this implementation does not change graph vertices or edges.

[PDF](report.pdf) · [Admission code](study_admission.py) ·
[Existing graph-wide problem record](../../../problems/isogeny-graph-wide-relation-solver.md)
