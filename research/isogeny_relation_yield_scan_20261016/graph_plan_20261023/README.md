# Study-level graph admission and trial plan

`study_admission.py` defines the executor-side check for one Coordinator
admission covering the full P29/P37 discovery study. The admission binds the
complete 8,206-arm graph discovery schedule plus four P29 E2/E3 same-conductor
controls, graph manifest and verification, both
stratum-specific commitment files, the base/target/verifier roots, source
commit and hashes, collector binaries, and experiment output tree. For each
run it replays the selected schedule row and materializer's prepared-arm
binding before the collector starts.

The checked decision and frozen specification must both authorize the exact
integer `execution_stage`; a Boolean value cannot stand in for stage zero. The
discovery compiler remains restricted to `execution_stage: 0`. The admission
validator also supports stage 1, requiring the selected discovery arms, a
bound stage-0 admission, reused base/verifier roots, and a fresh target root.
The graph trial adapter forwards the arm's `binding.json`, and its independent
checker recomputes the admission and binding before accepting the receipt.

The required admission schema is `ectd.graph-study-admission.v1` with
`status: approved`, `approved_by: coordinator`, `experiment_id`,
`source_commit`, `source_sha256`, `schedule`, `root_files`, `strata`,
`binaries`, and `output_prefix`. `strata` has exactly `P29` and `P37`; each
entry names its commitment file and binds graph and root digests. A
`candidate_unapproved` record is rejected. This module does not create or
approve an admission.

`build_discovery_plan.py` emits one supervisor trial for each of the 8,206 graph
arms and four separately identified P29 E2/E3 controls, with unique RUN IDs,
fixed P29/P37 memory and watchdog limits, and explicit dependencies for the
graph-transport and `u=2` conservation checks. The E2/E3 arms use the exact
P29 discovery target coefficient stream and are reported separately; they can
never enter graph finalist selection. A shape test checks all 8,210 trials; an
integration test passes the complete plan through
the repository's `experiment_execution.load_plan` validator. These establish
plan-schema compatibility, not scientific readiness.
The full 8,210-trial candidate fixture also passes in explicit readiness mode
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

`build_confirmation_plan.py` now compiles the post-discovery selection into
one confirmation trial for every selected `low_x`, `mid_x`, and `random_x`
arm, with 32,768 targets each. Its candidate path binds the selection, prior
discovery admission, new target root, reused base/verifier roots, graph-specific
commitments, sources, binaries, RUN IDs, output tree and supervisor stop/resource
rules. Candidate output is rejected by the execution loader. The approved path
copies that exact workload only when a Coordinator decision and stage-1
admission bind the same selection, roots, prior admission, and binaries.
`study_admission.py`, the materializer, and the trial adapter now verify the
confirmation stage and selected-arm boundary. The control suite verifies the
32,768-target preparation and candidate-plan schema; it does not create an
approved study plan or launch collectors.

The finalist stage now has a domain-separated `solve` input preparer,
materializer route, stage-2 admission-chain checks, and an adapter path that
runs the candidate Sage modular solver and its independent checker after a
successful relation trial. `build_solve_plan.py` binds the exact confirmation
finalist set and expands it into paired `low_x`, `mid_x`, and `random_x`
schedule rows. A deterministic P37 vertex-0 preparation control confirms that
all three base treatments share the same Q and target vector while producing
distinct bases; an independent replay checked all 32,768 targets and 3,200
signed base points. The control report, diagram, and PDF are in
`solve_preparation_control/`.

Stage 2 now has a candidate compiler that binds finalists and emits paired
relation/solver trials plus ten matched-rho tasks per finalist. The trial
adapter invokes the candidate Sage solver and its independent checker after
the relation trial succeeds; the rho runner independently verifies any scalar
and records work and resource fields. Unit tests cover finalist pairing and a
small exact-point rho control. These additions are still uncommitted and have
not passed the repository-wide current-head checks. No scientific collector
has been launched by these controls.

`finalist_solve_contract.yaml` now fixes the candidate stage-2 choices: at most
six confirmation finalists per stratum, all three ordinary base treatments on
each finalist, a fresh 32,768-target stream, fixed rank prefixes, ten matched
plain-rho repetitions per finalist with a 60-million-step cap, and per-phase
cost accounting. This is a protocol design artifact only. Stage-2 admission
ancestry is implemented, but the canonical frozen `EXP-*` specification,
committed scientific roots, approved stage-2 decision, and complete handoff are
absent. The verifier root is currently supplied to the same trial adapter that
materializes and executes the input, so the contract's
`scalar_hidden_from_executor` requirement is not yet satisfied by this custody
path. Rho cost aggregation and source-to-endpoint map-transfer timing also
remain open. Thus, the candidate compiler is not an admitted scientific run,
and this file does not authorize execution. The transfer/setup account must
include the mapped generator and DLP target before end-to-end costs can be
reported.

The [report](report.md) records the test scope and next action. The admission
code does not create or approve an admission and this package contains no
scientific relation-yield measurements.

[Control report](report.md) · [Admission validator](study_admission.py) ·
[Control outputs](control/)
