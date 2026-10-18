This packet implements six frozen finite worksheets. It is source preparation,
not a scientific run, result, hypothesis transition, or execution approval.
The formal implementation-only authority is
`ledger/handoffs/TASK-20261018-1cb336.yaml`, archived in commit
`323663e23d292ebd42876332cd3dbc9448fdd3bc`.

| Contract | Native route A | Independent native route B |
| --- | --- | --- |
| 95f69f | Pair-first residue images | Residue-first pair loops and vector deduplication |
| c9110e | Enumerate both involution compositions | Enumerate doubling kernel and required non-torsion witness |
| c9c5a4 | Forward first-hit walks | Reverse-preimage BFS |
| d68ac9 | Binary scalar multiplication and binary-limb integer bounds | Sequential curve multiples, cubic restriction, decimal-digit bounds |
| efafc0 | Slope addition and determinant | Cubic restriction, remaining root, negation |
| f7310e | Subtract both expressions | Three times curve defect and independent cross-products |

Both C++ headers are self-contained and do not import each other. They share
no scientific helper. Each contract has two tiny entrypoints, a `config.json`
and a `bindings.json` under its own `implementation/`. Binding files quote and
hash the exact cited inputs; the C++ runtime accepts no arithmetic parameter
overrides. The metadata-only `envelope.py` is shared explicitly.

Every prospective layout retains two separately allocated native RUN IDs, one
for each primary route. Each native check independently builds/recomputes the
opposite route; that check does not replace the second required primary run.
Route B depends on route A and binds/computes their final cross-run comparison.
The supervisor remains responsible for claims, ownership, admission and process
limits. There is no standalone frozen-worksheet launch through the envelope.

The six driver artifacts are `raw-result.json`, `primary-output.json`,
`native-primary.json`, `independent-check.json`, `certificate.yaml`, and
`manifest.yaml`. The exact native primary stdout is retained byte for byte;
the raw result references it. Compilation, synthetic controls and arithmetic
commands each retain their real stdout/stderr, status, timestamps and wait4
resources. The envelope validates actual `launch.json`, `environment.json`
and `command.txt`, source/spec/plan digests, both independent outputs and
explicit frozen invalidations. It rejects duplicate/nonfinite JSON, scalar
type substitution, changed receipt commands/source/scope and invalid resource
fields. Writes are exclusive; an interrupted or failed attempt is never reused.

The compiler, helper binaries, transitive system includes, startup objects,
selected runtime/static libraries and their hashes are recorded in each config
(268 paths on this machine). The full research-source closure is in each
prospective layout. The actual compiler is GCC 14; the actual Python path and
version are recorded. Neither the absent repository-recommended interpreter
path nor its pinned version is claimed. Kernel/firmware reproducibility is
outside this source packet's boundary.

Resources cover both wrappers and all their compilation/control/worksheet
children through core-artifact hashing, before final manifest serialization.
The elapsed boundary includes the supervisor transition between primary and
checker. Outer `certificate.kind` remains `none`; `certificate.yaml` is only a
finite recomputation witness. All deterministic inputs carry `seed: null`.

The original efafc0 prediction remains unchanged, including its suspected
sign swap. Passing controls and independently agreeing arithmetic may produce
`prediction_match: false` while the measurement is valid. No predicted table
is used in place of a native computation, and no scientific observation has
been produced during this preparation.

For c9c5a4, D is the cap and tau is the first hitting distance (infinity for
unreachable nodes). The two explicit descriptive arms are `min(D,tau)` and
`min(D+1,tau)`. The proposal's Step 1 and OBJECT FRAME use different conventions;
the old specification never resolves that discrepancy. The original predicted
table is scored only against its labeled prediction-compatible arm; the other
arm remains descriptive. The path/cycle maps, spacing residual convention and
lambda/probe-density formula are stated explicitly in `bindings.json`.
An additive Coordinator-admitted interpretation protocol is required before
either actual run. The envelope requires that protocol's path, digest and
admission reference in the frozen native plan. This preparation does not
resolve the ambiguity by choosing whichever convention looks favorable.

The minimum native run validator permits honest `seed:null`; the separate
`schemas/run-manifest.schema.json` still declares an integer-only seed. No
schema amendment or fabricated seed is included. Coordinator must preserve or
resolve that documented schema discrepancy before any claim of full JSON
schema parity.

The implementation gate is compile plus synthetic controls only. Twelve
native entrypoints compiled and ran `--self-test` on other F5/F7 curves,
including closure/associativity and large-integer controls. No compiled source
was invoked without `--self-test`. The first receipt is preserved under
`synthetic-checks/`; the subsequent receipt under `synthetic-checks-v2/`
removes misleading-indentation warnings in route B. Metadata controls are
synthetic and explicitly exercise false predictions, write-once files and
receipt/type tampering. See `implementation-receipt.json` for final hashes and
actual validation receipts.

Remaining work is concrete: Coordinator review/publication and source closure;
allocation/freezing of the two native RUN IDs and claim for each contract;
admission of the c9 interpretation; actual supervised primary/checker execution;
route comparison and independent result review; reports/graphs/PDFs for the
actual observations; and any authorized scientific state transition. These
finite toy worksheets cannot establish an attack improvement or larger-field
conclusion.
