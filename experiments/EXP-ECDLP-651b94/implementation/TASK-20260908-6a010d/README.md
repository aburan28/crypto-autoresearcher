# Second corrected prospective runner — `TASK-20260908-6a010d`

This is the immutable successor to `TASK-20260907-fde47b`, authorized by
`DEC-20260908-0d2555` after the archived source-conformance review
`TASK-20260907-2fd901`. It repairs V-01 through V-08 under the unchanged
frozen specification and `DEC-20260907-38017a`. This task did not create a
launch lock, a trusted key, a signature, a real run identifier, a scientific
fixture, a frozen candidate search, a census, a calibration, a timing panel,
or a scientific result.

`driver.py` contains the complete future runner, but importing it and its
default CLI do no measurement. `python3 -B driver.py` prints help and
`python3 -B driver.py coverage` emits only the code map. The future-run command
remains fail-closed until a later Coordinator supplies an authenticated lock,
a trusted Ed25519 key, an allocated run identifier, and an archived independent
PASS review.

The future lock distinguishes three committed positions. Its
`reviewed_source_snapshot` is the producer snapshot read by the reviewer; the
review archive must descend from it. Its `executing_commit` must descend from
that archive and equal the clean `HEAD`. The live specification, amendment,
driver, and plan must all match the lock hashes and the corresponding blobs in
both the reviewed snapshot and executing commit. A synthetic PASS report used
by a regression cannot satisfy those real authority requirements.

The future fixture path enumerates the certified subgroup as
`O, G, ..., (r-1)G` through one checked repeated-addition accumulator. It
retains the method, order, distinctness, and `rG = O` certificate before it
uses the canonical point ordering. Candidate rejection, fixture selection,
starts, certificates, cells, and Cayley guard-boundary state are append-only
progress records fsynced in the staging directory.

The future census retains every first-repeat certificate and distinguishes a
fruitless zero denominator from a failed scalar certificate. A failed
certificate or named validity control writes the cell and certificates, then
immediately stops with `completed_invalid`; it does not schedule the next cell.
It records first-repeat length, useful fraction, fixed points, two-cycles,
component sizes, maximum tail/cycle length, scalar inversion/comparison counts,
collision-table peak bytes, and diagnostic CPU/wall costs in the canonical raw,
cost, manifest, and report artifacts.

All sixteen frozen seeds have executable custody. Seeds `606300..606307` are
labeled exploratory and retained separately. They cannot select a fixture,
coordinate arm, partition, metric, threshold, or decision. Seeds
`606308..606315` are labeled held-out, and only their 96 cells reach the
all-u finite decision. Zero-yield individual null arms remain charged under the
pooled-side availability rule.

`ResourceMeter` captures one UTC/monotonic/CPU bracket at pipeline entry and
one terminal bracket after the outcome. The manifest and report serialize that
same interval. The former wall/CPU estimates stay advisory; the 8 GiB
process-group guard, one-worker bound, and cancellation checks do not.

The dense Cayley control checks cancellation and process-group memory at a
documented stride of 16 through allocation, row/column reduction,
matrix-vector, inverse-Fourier, and total-variation loops. It records the last
bounded phase/index before each probe, so a stop has durable partial-control
custody. The Cayley gap remains a separate reversible calibration and makes no
rho spectral or cryptanalytic claim.

Publication writes a same-filesystem staging tree, verifies all hashes and the
full canonical set, fsyncs before rename, then fsyncs the parent after rename.
If that post-rename boundary fails, the now-exposed final tree first receives a
typed `publication-failure.json` state receipt and is moved to `runs/incomplete`
when possible. The function never reports an unlabeled canonical final path as
a successful run after a durability failure.

`tests.py` is a 34-case fixed static/synthetic/mock suite. It does not call
fixture selection, a frozen candidate search, a collision census, an
experimental control/timing panel, or a Cayley calibration. Its two temporary
filesystem controls exercise only synthetic publication and synthetic Git
review objects; they create no persistent experiment artifact, real authority,
or scientific measurement. The truthful command output, case count, duration,
and final hashes are recorded in `regression-receipt.json`.

The only next action is Coordinator snapshot custody under `TASK-20260908-8e93d0`,
followed by a fresh independent source-bound review. These files are not launch
admission and assert no result about ECDLP security, the spectral proposal, or
a mathematical hypothesis.
