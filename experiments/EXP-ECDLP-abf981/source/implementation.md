# EXP-ECDLP-abf981 implementation return

Task `TASK-20260907-a08b20` supplies a partial implementation package: the finite
instrument body, controls, polynomial/recovery machinery and seven payload
serializers are implemented. Official runner integration is unresolved, so
`protocol_complete: false` and scientific readiness is false. This return does
not satisfy the complete runnable-instrument gate. It creates no scientific
result and changes no hypothesis, experiment, goal, approval or ledger status.
The Coordinator owns the terminal task classification and successor decision.

The CLI intentionally fails before creating a scientific output directory until
an approved integration connects the official verified LOCKED runner and its
immutable terminal manifest. An environment flag, invented lock JSON or the
implementation approval cannot supply that authority. Both frozen scientific
commands remain prospective and unexecuted in `planned-execution.json`.

## Authority, ownership and provenance

All work used `/Volumes/SSD990/1083/pending-ideas-swarm-20260907`, independently of
the native metadata's original-checkout cwd. Only the three assigned new files
under this experiment's `source/` were written. Each was absent at direct
preflight. No claim, release, commit, push, PR operation or shared ledger edit
was made by this Executor. Other agents' edits were preserved.

Directly read and hash-verified internal inputs:

| Input | SHA-256 |
|---|---|
| specification.yaml | `7d9a6cccbfdaf8d9efc1d565cf437c1e833d4de964c5fdc3cd77b72e3d3dbf93` |
| H-ECDLP-9cf3e6 | `26261aca1d6471ed1d5381a6ed3ef31d0bbd5725945ced0dacbfbb344ca882a8` |
| Original DEC-20260907-e3e3f1 | `21950738e224abbfbff76e604e39148bcb78be00b445d95e2f6d7bf3701b5d10` |
| admitted-task-cards.json | `a818379e370f0f382a949682dc571b96aaf66bc8e8f64b7a8bf36f6a48a5266b` |
| This task's compact JSON handoff | `39bdf9191e19274412681fc2d37798dfa5eaf98a11c73ef99153e19ddc113013` |
| Original proposed-execution-chain.json | `2a6601acaa1417da7bef947a64625c547de0643eebf73b21e2d3eaf29aa9caa8` |

The immutable specification's `approved_by: null` and
`execution_authorized: false` remain unchanged. DEC-20260907-e3e3f1 admits only
this zero-scientific-run implementation. The parent reports the additive same-ID
schema correction, publication/claim gates, and completed design archive
`5e148dd85032615c18d0ee2d6f5205a76e39a3b6`; these are parent control-plane
observations, not independent scientific reviews performed here.

The parent-held canonical claim is epoch 1, owner
`coordinator-pending-ideas-swarm-20260907`, parent session
`01a07e0d-9f07-7382-a7d3-e2f0b4cf08de`, acquired `2026-09-08T02:25:34Z`, expiring
`2026-09-08T05:25:34Z`. Claim observations come from the parent, which owns its
release and the future `TASK-20260907-bfc9b4` snapshot.

This Executor's actual native provenance was observed and supplied by the
parent: session `01a07ed7-61a9-7aa0-a56b-d93b75a63331`, role `executor`, provider
`openai`, model `gpt-6-astra`, reasoning effort `ultra`, requested policy
`executor-implementation`. No fallback or degradation was used.
`model_verified: false`: no adapter model probe occurred. Native session-meta
raw-line SHA is `355f78153d975f8b4130b2a51e508d109e03329a92d3d8974bedc28c6db58c43`;
first turn-context raw-line SHA is
`ae53179197a73b60b836a2e287ecdb73b9657d74abfeff719e2124d299f24d55`.
This Executor did not read those session files outside its scope. No provider
request, arithmetic network call, backend switch or Bedrock selection occurred.

The parent's direct Git observation at
`2026-09-08T02:32:40.753113+00:00` through
`2026-09-08T02:32:42.670851+00:00` reports HEAD
`9c7b9021a498adcd3bded3d614c4e04ac2b0e534`, dirty only for this untracked source
directory. That is an attributed observation at those timestamps, not a claim
about the final shared tree. An earlier approximate timestamp was replaced by
this exact supplied observation. The implementation snapshot commit is still
null pending the parent's archive.

## Implementation correspondence

`Field` counts instrumented arithmetic primitives and reduction-input integer
bit lengths. `Poly` expands sparse coefficients modulo p, combines equal
exponent vectors, removes zero coefficients, and keeps every raw equation slot.
The leading coefficient is the coefficient of the greatest exponent vector in
the declared lex order; term lists serialize in ascending lex order. No factor
cancellation, exponent reduction, squarefree reduction, duplicate-equation
removal, Groebner operation or scientific support optimization is implemented.

The frozen symbol `lambda` is mapped to a private token only while parsing
Python expression syntax, then mapped immediately back to the declared
variable. Serialized formula text and variable names remain exact. The parser
accepts only integer/name/add/subtract/multiply/power expression nodes and never
uses `eval`, arbitrary calls or arbitrary external expression input.

The six W branches, complete Edwards branch, and seven Hessian branches follow
the frozen variable/equation lists. Hessian D=0 branches retain all map inverses,
W curve equations and generic/tangent/inverse fallback equations. All branches
consistent with target type and O-in-A are instantiated even when they have no
solutions. Zero slots remain in the raw descriptor and count separately from
normalized nonzero equations. Each unknown affine point retains its curve,
exact `I_A-1` membership and all field equations. Infinity membership is an
explicit branch Boolean. Edwards includes the affine images of O and T.

The selected point set is the mathematical union of O, T, and the first six
eligible lexicographic affine W points, serialized in the grammar's canonical
W order. All alternative models transport that same ordered point list. Each
of the four fixed-window sets is recorded with its exact cardinality, including
empty sets, and compared only to W on the same canonical points. Cross-set
comparisons report density unless the exact lists coincide.

The availability gate implements exact constant checks, all three frozen
p-squared affine candidate enumerations, the p+1 Hessian infinity candidates,
intermediate Montgomery/twisted-Edwards checks, complete forward/reverse and
H/Ed-through-W composition checks, denominator exceptions, and native addition
comparison on every full-group ordered pair. The map and pair certificates
retain O/T cases and the intermediate W point type. No such gate has run here.

C0 reserializes W descriptors through a bijection on declared variable names
and compares canonical bytes/metrics. C1 covers full point/map/pair transport.
C2 explicitly transports and rejects the equal-sized mismatched set. C3 retains
the missing-O decoder and ordinary-division-on-T failures. C4 checks the exact
frozen wrong H map. C5 scans the wrong H negation and cannot pass without a
witness. C6 records every projective coordinate fiber, every size-two window,
full-fiber selection, both exact counting identities, and the deliberately
false universal B=w equation. C7 transports every size-two and full-fiber
window under the fixed PGL2 map for k=0,1,2. C8 checks direct B-squared pair
addition against canonical-label table lookup. Control checks precede final
structural comparisons; failure withholds scoring and keeps the failing object.

Finite recovery enumerates every admitted ordered point pair for every target.
It solves only uniquely defined auxiliary variables from explicit nonzero
linear/inverse constraints, checking each auxiliary's roots over the entire
field. It then evaluates every raw equation slot. No true-sum lookup filters
candidate recovery. Rejected candidates retain per-branch residuals; accepted
solutions retain complete assignments, auxiliary uniqueness data and decoded
canonical pairs. Each target receives exact missing/spurious/duplicate counts
and sorted relation certificate hashes. Exact membership is separately checked
on the affine grid. These procedures are implemented but scientifically
unexecuted and unverified.

Metrics retain the four frozen integers, category subtotals, degree histograms,
zero/nonzero counts, branch metadata bytes and all support lists. They compare
native vectors only to their matched W vector, and separately compute the
frozen any-decrease and Pareto predicates. Empty arms cannot produce a positive
simplification. First-fall, Groebner, geometric elimination/summation degree,
rank, descent and DLP solving remain `outside_frozen_diagnostic`.

The density/proxy output labels historical degrees and proxy ratios as
conditional preregistered arithmetic, with empty full-fiber windows explicitly
inapplicable. They are never called a measured geometric degree, Bezout bound,
attack cost, speedup or ECDLP exponent improvement.

## Cost and artifact boundary

Term evaluation follows the frozen convention literally: powers start at
exponent zero and use repeated multiplication; factors multiply in declared
variable order; terms sum in serialized order; no cache is shared across
polynomials. Instrumented primitive counts and the modeled term-evaluation row
are separate. Actual Python integer inverse internals and interpreter overhead
are not misreported as counted field multiplications. CPU and wall measurements
include overhead; RSS is the process cumulative high-water mark sampled at each
phase end, not incremental per-phase allocation.

`finite_payload` keeps caller-visible partial dictionaries and records a
terminal failure object on exception. `scientific_artifact_data` serializes the
raw results, map certificates, relation certificates, complete systems,
controls, costs and execution report. `emit_scientific_artifacts` uses exclusive
writes and refuses existing files or symlinks. These emitters have only been
checked with in-memory synthetic fixtures. No scientific run directory or file
has been created. Runner-owned manifest, stdout/stderr, final all-artifact
hashing and process failure handling remain the integration prerequisite below.
No independent validation cost or timing is assumed free or invented.

## Mechanical checks and preserved implementation failure

Observed runtime for mechanical checks: CPython 3.13.1, build
`v3.13.1:06714517797, Dec 3 2024, 14:00:22`, Clang 15.0.0,
`/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`,
`macOS-26.6-arm64-arm-64bit-Mach-O`. The program body uses only Python's standard
library. The future scientific Python version, runner dependencies and exact
environment hashes are planned/unresolved; these mechanical observations are
not scientific runtime pins.

The final repeatable mechanical command executed successfully was:

```sh
python3 -B experiments/EXP-ECDLP-abf981/source/run_model_comparison.py --mechanical-check
```

It reports:

- Exact sparse expansion and scalar normalization on arbitrary F5 polynomials.
- Term evaluation at 25 assignments on the non-curve affine grid.
- Exact two-point membership at all 25 non-curve grid assignments.
- Preservation of the keyword-named variable, zero equation slots and JSON/name
  round-trip; rejection of executable expression calls.
- Syntax and declared count metadata for all fourteen frozen branch records,
  without polynomial construction or field evaluation of those records.
- In-memory serialization/JSON parsing of all seven instrument artifact shapes
  with a synthetic payload; zero files written by that fixture.

`ast.parse` and `compile(source, path, 'exec')` passed without bytecode output.
A static API check confirmed the required machinery is defined and had no
top-level scientific calls. `python3 -B` was used throughout; no pycache or
unassigned test artifact was written.

One schema-only check initially failed with `SyntaxError: invalid syntax` at
`lambda*(X2-X1)-(Y2-Y1)`. The frozen name is a Python keyword. The lexical alias
repair described above fixed this implementation issue without changing the
protocol, and the repeat passed. This failure is retained here as an
implementation anomaly, not scientific evidence. An early read-only file
search also found that guessed `docs/experiment-runner.md`,
`docs/locked-execution-plan.md`, and `orchestration/runner.py` paths do not exist;
subsequent allowed docs searches located the actual runner references.

## Remaining prerequisite and exact next action

The current handoff requires the normal harness immutable manifest and the
repository LOCKED runner, while its original read scope omits both runner
source directories. A scoped interface request was sent to the Coordinator.
The parent interface auditor reports that `harness/runner.py` writes immutable
YAML run packages but does not enforce LOCKED plans, whereas
`src/crypto_autoresearcher/runner.py` has the LOCKED interface and incompatible
`specification.json`/`contract.md`, numeric-only RUN and `manifest.json`
conventions. These are attributed parent observations pending this Executor's
permitted interface readback, not an asserted completed integration.

The CLI has no invented bypass for that mismatch. Its scientific branch
returns `not_executed` / `infrastructure_error` with exact prerequisites before
creating output. Neither p11 nor p23 scientific argv was invoked. This is an
infrastructure integration impediment, and says nothing about the hypothesis.

The Coordinator's next action is to archive the exact three-file package under
`TASK-20260907-bfc9b4` as a partial return, resolve and authorize the minimal
runner/manifest adapter repair without changing scientific formulas, record
identifiers or output scope, and only then bind actual runtime/source hashes,
process protection, LOCKED plan and separate scientific authorization. The
8 GiB memory requirement, one worker and 1800-second watchdog remain frozen
future requirements; their actual runner enforcement is unverified. Watchdog
expiry must preserve a checkpoint and report resource_exhaustion without a
mathematical conclusion.

Zero-scientific-run receipt: completed scientific runs 0; invalid scientific
runs 0; failed scientific runs 0; scientific run attempts 0; p11/p23 curve
point enumerations 0; scientific map calls 0; lock creation 0. All reservation
states remain unexecuted. No claim about map availability, finite correspondence,
structural improvement or scalar recovery is made.
