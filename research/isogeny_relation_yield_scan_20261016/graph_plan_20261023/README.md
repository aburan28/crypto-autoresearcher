# Study-level graph admission and trial plan

`study_admission.py` defines the executor-side check for one Coordinator
admission covering the full P29/P37 discovery study. The admission binds the
complete 8,206-arm discovery schedule, graph manifest and verification, both
stratum-specific commitment files, the base/target/verifier roots, source
commit and hashes, collector binaries, and experiment output tree. For each
run it replays the selected schedule row and materializer's prepared-arm
binding before the collector starts.

The checked decision and frozen specification must both authorize the exact
integer `execution_stage`; a Boolean value cannot stand in for stage zero. The
current compiler and launcher additionally require `execution_stage: 0`, so an
approval for confirmation or finalist solving cannot pass through the
discovery entry point. Dedicated launchers for those later stages remain to be
implemented. The graph trial adapter forwards the arm's `binding.json`, and
its independent checker recomputes the admission and binding before accepting
the receipt.

The required admission schema is `ectd.graph-study-admission.v1` with
`status: approved`, `approved_by: coordinator`, `experiment_id`,
`source_commit`, `source_sha256`, `schedule`, `root_files`, `strata`,
`binaries`, and `output_prefix`. `strata` has exactly `P29` and `P37`; each
entry names its commitment file and binds graph and root digests. A
`candidate_unapproved` record is rejected. This module does not create or
approve an admission.

`build_discovery_plan.py` now emits one supervisor trial for every scheduled
arm, with unique RUN IDs, fixed P29/P37 memory and watchdog limits, and explicit
dependencies for the graph-transport and `u=2` conservation checks. A shape
test checks all 8,206 rows; an integration test passes the complete plan through
the repository's `experiment_execution.load_plan` validator. These establish
plan-schema compatibility, not scientific readiness.
The full 8,206-row candidate fixture also passes in explicit readiness mode
and is rejected by the default execution loader.

The compiler also has a candidate-only path for a frozen `review_required`
specification. It writes `candidate-trial-plan.json`; an explicitly named
`newest_experiments --experiment ...` query can report that candidate `ready`
when every planned row validates. Default selection omits it. Both the
execution loader and public run path reject candidate-only plans, so approval
still requires a newly built approved plan and dispatch queue. Tests exercise
the explicit readiness path and refusal to execute.

Candidate and approved graph plans also set `stop_on_invalid_output: true`.
The supervisor halts at the first invalid arm certificate, including map,
group, count, row, or rank replay failures, and preserves that receipt.
Resource and infrastructure failures remain recorded under their own statuses.

The remaining design gap is staged custody: the compiler covers discovery
only and does not yet bind fresh confirmation and finalist solve streams, each
with their own committed roots. Scientific roots, a canonical frozen experiment
contract, approval decision, and complete handoff are absent. No collector was
launched by these controls.

The [report](report.md) records the test scope and next action. The admission
code does not create or approve an admission and this package contains no
scientific relation-yield measurements.

[Control report](report.md) · [Admission validator](study_admission.py) ·
[Control outputs](control/)
