# EXP-RELN-dc761f implementation

This package implements the version-1 RELN protocol specified by
`experiments/EXP-RELN-dc761f/specification.yaml`, with the additive input
freeze in `AMD-20261011-594c01.yaml` and the admission ruling in
`DEC-20261011-09f449.yaml`.

## Scope of this handoff

This is an implementation/readiness handoff only. The experiment remains
unapproved and unadmitted. No scientific trial, protocol-labelled draw, run
directory, ledger edit, queue/lane edit, or commit is made here. The exact
declared artifacts are:

- `implementation/run_reln.py`
- `implementation/check.py`
- `implementation/implementation.md`
- `implementation/implementation_report.yaml`
- `trial-plan-v1.json`

The F-1 fixtures and all F-2 fixtures are represented as immutable constants.
The F-2 constants and the P-5 columns/values are checked at load time against
AMD-20261011-594c01. The plan carries the P-5 table and uses the four exact
nested budgets `A_1/4`, `A_1/2`, `A_1`, and `A_2`; no recomputed or estimated
budget is substituted.

## Admission and machine protection

`run_reln.py --readiness` is a non-execution check and reports
`execution_state: ready` when the plan and frozen records agree. It does not
evaluate a protocol label. Any scientific invocation requires all of the
following before creating a `RUN-*` directory:

1. an explicit Coordinator decision naming `EXP-RELN-dc761f` whose
   `execution_admission.currently_admitted` is exactly `true`, and which is
   not superseded or withdrawn;
2. a Coordinator snapshot receipt under `archives/` that pins all five
   declared artifacts (the report may use the standard self-binding marker);
3. a plan whose protocol hashes and F-2/P-5 values still match the frozen
   records;
4. C-7/M-1 host checks: 15-minute load at most 14, at least 5 GiB free on
   `/`, at least 20 GiB free on the repository volume, one worker, a
   4 GiB RSS watchdog, and a declared writable `TMPDIR`;
5. execution under the declared `nice -n 10`/one-worker contract.

Unreadable machine readings, missing `TMPDIR`, missing `psutil`, an absent or
non-admitting decision, a missing snapshot, a changed frozen table, and an
existing immutable run directory all refuse closed. A refusal is an
infrastructure/admission observation, never a scientific result.

The plan's `execution_authorized: false` is intentional. Readiness means the
implementation and plan are structurally runnable for a later Coordinator
admission; it does not grant admission. `DEC-20261011-09f449` is expected to
refuse because it records `hold_approval` and `execution_admission: false`.

## Protocol path

After admission, the driver uses the exact SHA-256 rejection sampler, target
and attempt labels, affine short-Weierstrass arithmetic, full sorted scan,
first-decomposition rule, LP multigraph construction, conditioned N-1 rewires,
and the frozen nested budgets. The implementation records relation
certificates, per-cell C1--C4/C34 and graph descriptors, rewire tries, and
raw attempt records beneath the admitted `RUN-*` directory. The protocol
sampler is not called by plan construction, readiness, static checks, or
absent-admission refusal.

The admitted scientific path now emits the complete frozen run package:

- `manifest.yaml`, `command.txt`, `stdout.log`, `stderr.log`, and
  `environment.json`;
- one `attempts/<fixture>.jsonl` stream per fixture;
- one `cells/<fixture>-k<kappa>.json` record per all 48 cells, including the
  graph, S-1--S-4 values, every N-1 rewire metric, every N-2 ER metric,
  timing/RSS, and control details;
- `pooled-analysis.json` for S-5--S-9 and the frozen tail checks;
- `accounting-certificate.json` for G-6 certificates and the L-8 independent
  audit replay; and
- `provenance/git.json`, `provenance/resource.json`, and
  `provenance/failures.json`.

The validity gate is fail-closed and requires all 48 cells plus K-POS,
K-FALSE-1, K-FALSE-2, K-ID, and K-AUD. K-POS uses the frozen
`ceil(1.5 * mu_c)` target; K-FALSE-2 runs all 100 pooled pseudo-treatment
replicates; K-AUD verifies every kept relation and independently replays the
L-8 selected attempts. A failed gate produces `invalid` with a procedure
failure record and no verdict; an RSS, signal, or other runtime failure
produces `failed_infrastructure` with partial artifacts preserved.

M-2 is implemented as a main-thread-installed, daemon polling watchdog at
4 GiB RSS. It checks its sampler and thread liveness, raises a distinct
resource-exhaustion failure on sampling failure or limit breach, and restores
the prior signal handler after finalization. It is installed before the first
protocol draw and cannot be bypassed by the readiness path.

This handoff itself does not exercise the scientific path. The self-checks
exercise plan binding, artifact/control-path presence, injected M-2 failure,
machine fail-closed fields, admission refusal, and no-protocol-draw
readiness. Therefore it reports no observation about the RELN hypothesis and
makes no claim about any verdict.

## Deviations

None from the frozen protocol. The only intentional implementation boundary
is that the smoke option refuses rather than creating output: this handoff is
for implementation/readiness and explicitly forbids scientific execution or
protocol-labelled values. A later admitted execution must use the frozen
namespace and exact budgets, not smoke data.
