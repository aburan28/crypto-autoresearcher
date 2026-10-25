# Owner implementation compatibility and actual launch gates

2026-10-25. This is an operational implementation assessment, not a scientific
run, a new bound, an experiment approval or a change to the selected lead.
The original reach-cost and verified IC-improvement objective remains open.

The zero-run design is complete. Its seven outputs and the prospective 24-call
panel remain frozen in snapshot `d1387a9d7f6bb31840a26cde4d5213cb737e05ea`.
The broader task may proceed through its next implementation workflow; the
completed `coordinate` stage is not a permanent restriction on that task.

## Owner constraints, observed directly

Canonical executable scientific implementation belongs in `aburan28/crypto`,
as the published handoff preview and shared lab contract state. At owner
commit `5cb553810e5bbfbd8691ec614ffcaacefc625757`, `AGENTS.md` imposes two
requirements relevant to the proposed launcher:

- Under **Implementation language: no Python**, it says: "Do not use Python
  for cryptographic research or performance work in this repository." It
  explicitly includes experiment harnesses, solvers, correctness tests and
  verifiers, and prohibits "compiled wrappers that delegate this work to a
  Python process."
- The Conductor instruction says: "Before making code changes, obtain or
  attach to a Conductor task. Run `conductor check ...` first."

Pinned sources: [native implementation rule](https://github.com/aburan28/crypto/blob/5cb553810e5bbfbd8691ec614ffcaacefc625757/AGENTS.md#L427)
and [Conductor prerequisite](https://github.com/aburan28/crypto/blob/5cb553810e5bbfbd8691ec614ffcaacefc625757/AGENTS.md#L1551).

Consequently a Rust/C++ wrapper around the pinned Sage/cuso Python path does
not satisfy the owner implementation rule. The archived Sage calibration
remains historical evidence. It is not a permitted new owner execution path
merely because a native executable launches it. The frozen mathematical
workload remains useful as a specification for a native implementation;
backend compatibility must be made explicit before approval.

## Actual environment observations

- The owner checkout is at the commit above and has no code changes.
- `conductor check --summary 'Prepare native joint-smallroot implementation
  under the published design' --scope path:experiments/joint-smallroot`
  exits **127**, with `conductor: command not found`. No task or successful
  ownership check is asserted. The proposed scope was a readiness probe, not
  an acquired reservation or an implemented experiment directory.
- `git ls-tree HEAD .conductor/WORKFLOW.md` returns no tracked entry in that
  owner tree. This missing citation does not establish that an external
  ownership service approved any scope.
- `/usr/bin/g++` is installed. The installed native Singular executable at
  `/workspace/skeleton_sage-runtime/bin/Singular` reports version **4.4.1**
  (44105), with GMP 6.3.0, NTL 11.6.0 and FLINT 3.3.1 in its banner.
  This was a version query, not an algebra computation or trial.
- No `cargo` command was found on the current PATH. A Rust toolchain can be
  provisioned if chosen; its absence is not mathematical evidence or a
  permanent implementation limitation.

No alternative Conductor tool was available in the active tool catalog. No
owner file was edited, no fake ownership record was created, and no Python
path was relocated to another repository to evade its ownership rule.

## Concrete native implementation obligations

Native Singular is a possible algebra component, not an implemented replacement
for the pinned cuso strategy. Before the fixed panel is runnable, implementation
must provide all of the following under the owner workflow:

1. Native exact polynomial/affine-window construction, coefficient and support
   serialization, and the six-variable/seven-coordinate ordering from the
   published applicability specification. Check the exact term-order semantics
   independently; a version banner proves no order equivalence.
2. The specified ideal powers, finite convex integer domain and support closure,
   optimal-shift construction within its stated domain, exact coefficient
   matrix/echelon logic, construction-statistic interpolation and bound
   normalization. A Gröbner-basis call alone does not implement these stages.
3. Native known-answer checks against the already published algebraic fixtures,
   univariate calibration and exact sign/divisibility/corruption controls.
   Preserve reference-source provenance and any applicable upstream license
   obligations. Do not call the Python reference for new owner measurements or
   represent a port as equivalent before its checks pass.
4. The deterministic 24-case plan, supervisor, cold-process instrumentation,
   enforceable process-tree memory protection, watchdog and complete success,
   failure and censored-output retention. No first joint call occurs during
   this zero-scientific-run implementation stage.
5. An additive backend/dependency specification and independent interface review,
   followed by exact-byte runnable preapproval, runbook/task-card lint, committed
   Coordinator approval and published execution readiness. Do not rewrite the
   old design or silently substitute a new engine in a frozen contract.

Reduction/root extraction and a matched complete IC comparison remain later
obligations. Native implementation, software checks or a symbolic bound do not
establish an IC improvement.

## Exact impediment and exit condition

Owner code edits are presently blocked by the unavailable required Conductor
task/check. A lawful task reservation on a host where that workflow is
available, followed by the native implementation and checks above, clears
this operational impediment. No additional scientific permission is being
requested; existing user authorization persists. No such check, code change,
native equivalence result or experiment approval has been obtained here.

The owner's broad native-code rule also prevents treating the existing Sage
adapter preview as an immediately executable final deliverable. This is an
implementation-policy compatibility gap, not evidence against the joint
small-root method. Keep the preview `review_required` and the research goal
active. The prepared artifact-tool owner patch is subject to the same genuine
ownership-check issue before it can land and unblock audit PR #2547.

Next action: on a host with the owner workflow, acquire the exact implementation
scope and prepare the native adapter/launcher, trial plan and supervisor without
scientific execution, then return for independent review and prospective
preapproval. Do not repeat the earlier overbroad runtime/capacity or
coordination-mode blocker claims.
