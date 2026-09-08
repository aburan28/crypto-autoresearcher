# Third corrected prospective runner — `TASK-20260908-111152`

This immutable-successor package copies the archived `TASK-20260908-6a010d`
implementation and applies S2-01 through S2-08 from
`DEC-20260908-94664e`. It retains V-01 through V-08, the original frozen
specification, and `DEC-20260907-38017a` without changing a scientific seed,
fixture definition, threshold, algorithm, control, or decision rule.

The package performed zero scientific runs. It did not generate fixtures,
perform a frozen candidate search, census, experimental null/control/timing
panel, or Cayley calibration. It did not create a real Coordinator key,
signature, lock, allocated run, or run directory. The tests exercise only
fixed static/synthetic/mock lower-level helpers, artifact serialization,
failure custody, process telemetry parsing, and a temporary synthetic Git
review graph; they do not invoke the prospective pipeline or measurement CLI.

S2-01 uses the frozen relabel-control tuple `(p,A,B,r,0,0,0)`. Shuffle arms
continue to use their actual `u`, so guarding does not change the frozen RNG
streams. S2-02 introduces `IncompleteFixtureStop`, which produces an
`incomplete_fixture_inconclusive` operational outcome; unexpected exceptions
produce `failed_implementation` with the retained partial sink.

S2-03 records every completed or interrupted diagnostic cost in the progress
sink. The future report derives accepted/rejected fixture counts, completed
cells, per-stream cells and seeds, partial certificates, and diagnostics from
the retained sink. It serializes actual secondary values and all diagnostic
cost rows, including relabel table/control, constant-O census, mutated
verifier, and partial records.

S2-04 distinguishes attempt, write, file fsync, directory fsync, quarantine
attempt, and quarantine completion for failure receipts. `annotated_final` is
available only after both receipt durability steps succeed. A receipt failure
returns explicit `unretained` custody and tries to remove an exposed final path
from the canonical location.

S2-05 accepts only `RUN-ECDLP-<six lowercase hex>` identifiers. A signed future
allocation must bind that identifier, experiment, a nonempty authority id, and
the exact non-symlink canonical experiment root. The pipeline checks that root
before creating a staging directory.

S2-06 replaces permissive report admission with a complete independent-review
attestation. It requires a precommitted plan with an owned joint, exact
source-read hashes at the reviewed snapshot, independent review-adversarial
inference/session provenance, and a later external queue binding. The queue
must bind the actual archive commit, parent, full changed path set, record IDs,
and all Git blob hashes. The in-snapshot receipt binds only its parent and
non-receipt sources; it must not self-name its containing commit.

S2-07 rejects empty, malformed, wrong-group, or missing-current-process RSS
rows as `InfrastructureStop`. S2-08 propagates cancellation/RSS guards and
resumable coordinates through table construction, relabeling, shuffling,
Fourier, and all nested Cayley loops. These guards add no RNG draws or
scientific arithmetic.

The next action is Coordinator snapshot custody under `TASK-20260908-c446f1`,
followed by a fresh independent review. This package is implementation ready
for that review only. It is not a launch admission, scientific result, or
claim about ECDLP security.
