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

The finalist stage has a domain-separated `solve` input preparer, materializer
route, stage-2 admission-chain checks, and a rootless worker path that runs the
candidate Sage modular solver and its independent checker after a successful
relation trial. `build_solve_plan.py` binds the exact confirmation finalist set
and expands it into paired `low_x`, `mid_x`, and `random_x` schedule rows. A
deterministic P37 vertex-0 preparation control confirms that all three base
treatments share the same Q and target vector while producing distinct bases;
an independent replay checked all 32,768 targets and 3,200 signed base points.
The control report, diagram, and PDF are in `solve_preparation_control/`.

The solve preparer now records public source G,Q coordinates in its custodian
manifest, without recording the verifier root or scalar. The new path-transfer
trial maps those points through every saved edge to a finalist, reports per-edge
map setup and point-evaluation durations, and has an independent Sage replay
checker. The solve plan binds one such trial per finalist and checks that all
three factor-base treatments use the same exact G,Q and target vector. These
checks also require one identical ordered target-vector digest across every
finalist within a stratum, as the solve contract specifies. These are
implementation changes only; no finalist path-transfer trial has run.

Stage 2 now has a candidate compiler that binds finalists and emits relation/
solver trials, one path-transfer trial, and ten matched-rho tasks per finalist.
The path-transfer worker receives public source G,Q points only. The rho runner
independently verifies any scalar and records work and resource fields. Unit
tests cover finalist pairing, rootless path-transfer argv, and a small exact-
point rho control. These additions have not passed the repository-wide
current-head checks. No scientific collector or path-transfer trial has run.

`finalist_solve_contract.yaml` fixes the candidate stage-2 choices: at most six
confirmation finalists per stratum, all three ordinary base treatments on each
finalist, a fresh 32,768-target stream, fixed rank prefixes, ten matched
plain-rho repetitions per finalist with a 60-million-step cap, public-point
path-transfer timing, and per-phase cost accounting. It remains a protocol
design artifact. A bounded P37 path-transfer implementation control now maps
the public pair across 24 saved edges and passes an independent replay; its
report, diagram, and PDF are in `path_transfer_control/reports/attempt-1/`.
This control covers the adapter only. The canonical frozen `EXP-*`
specification, committed scientific roots, approved stage-2 decision, and
complete handoff are absent. Therefore the candidate compiler is not an
admitted scientific run, and this file does not authorize execution.

The [report](report.md) records the test scope and next action. The admission
code does not create or approve an admission and this package contains no
scientific relation-yield measurements.

The solve-stage compiler now binds `aggregate_solve_costs.py` by source hash.
Preparation manifests split target-stream/source-pair construction, factor-base
generation, target-point construction, and serialization timing. The modular
solver separates individual-log extraction from point-equation verification;
its supervised child receipt retains CPU and sampled peak RSS. After execution,
the aggregator requires an exact candidate-plan-bound catalog containing every
planned relation, transfer, and rho run, checks each independent checker result,
retains censored cells as observed prefixes, and writes per-treatment yield/rank,
complete cold-start and per-target amortized costs, paired rho repetitions, and
the verified minimum/maximum with all cells retained. The source and schema
checks were syntax-compiled; no experimental run or test suite was run in this
turn, and the aggregator has not yet been exercised on scientific receipts.

[Control report](report.md) · [Admission validator](study_admission.py) ·
[Control outputs](control/)
