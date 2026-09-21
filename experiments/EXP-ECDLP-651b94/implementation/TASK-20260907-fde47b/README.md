# Corrected prospective runner — `TASK-20260907-fde47b`

This directory is the immutable implementation successor authorized by
`DEC-20260907-38017a`.  It corrects the prior prospective implementation after
two archived independent reviews.  It contains no launch lock, run identifier,
scientific fixture, candidate search, collision census output, Cayley
calibration output, timing panel, or scientific result.

`driver.py` implements the exact future path while keeping its default CLI
non-measuring.  `python3 -B driver.py` prints help and
`python3 -B driver.py coverage` prints only the static finding-to-code map.
The `future-run` command refuses unless a later Coordinator provides all of
the following externally:

- a signed `coordinator_runtime_execution_lock` binding this source
  specification, amendment, driver, execution plan, clean reviewed snapshot,
  exact runtime, the 8 GiB process-group limit, one worker, and an allocated
  run identifier;
- a trusted Coordinator Ed25519 public key supplied by the future control
  plane; and
- an archived, reachable independent review receipt and PASS report which bind
  the corrected snapshot and the exact report bytes.

The driver does not accept an arbitrary hash-bound text file as a review
receipt.  It parses the review admission, checks the report verdict and source
snapshot, checks the archive receipt’s task/hash binding, and verifies that the
archive commit is an ancestor of the executing checkout.  Neither this README
nor the correction handoff is authority to run `future-run`.

The future runner scans the frozen fixture range in lexicographic order and
records every rejected candidate encountered before selection.  A singular
candidate is recorded and discarded before `Curve` construction, so it cannot
abort the scan.  It implements the pooled-side availability clarification:
`Zcoord > 0` and `sum(Znull_j) > 0` make a cell available.  A zero-yield null
arm stays in the pooled numerator and is retained in raw artifacts; only a
zero total on either side makes the cell unavailable.

Every future coordinate/null census retains a first-repeat certificate.  A
zero denominator is a fruitless collision.  A nonzero denominator whose
recovered scalar fails independent verification is a failed certificate, is
retained, and invalidates the measurement through one explicit validity
reduction.  The same reduction requires successful Cayley, relabel, occupancy,
constant-O, and mutated-candidate controls.  The constant-O control is an
actual all-start reset-map census whose coefficients reset to `(0,0)` and must
produce exactly zero nonzero denominators and zero solves.

The prospective result writer records accepted/rejected fixtures, raw cells,
all certificates, operation splits, pooled denominators, availability, the
separate reversible-Cayley gap, per-u means, and one all-u finite decision.  It
adds `command.txt`, `environment.json`, and `raw-result.json` to the nine
experiment-specific artifacts.  It writes the whole package in a sibling
same-filesystem staging directory, fsyncs and hashes it, then renames it to the
final run directory.  A publication failure leaves no final run directory and
keeps a typed failure receipt with the staging material under `runs/incomplete`.

The process-group RSS guard is 8 GiB, one worker is bound in the future lock,
and cancellation/resource checks occur in fixture, start, transition, and
control loops.  Completed fixture records, starts/certificates, and cells are
fsynced into staging progress before the next checkpoint.  Cancellation,
resource exhaustion, and infrastructure failures publish retained partial data
with an operational/inconclusive status; they are not invalid scientific
controls or evidence against the hypothesis.

The original 5,400-second / 1.5 CPU-hour estimates are still measured in total
and by stage.  Under the amendment and current budget policy they are advisory:
the future runner does not stop or invalidate a run merely for crossing them.
This does not weaken the 8 GiB process-group guard, one-worker bound, or
explicit cancellation checks.

`tests.py` is a fixed static/synthetic/mock regression suite.  It never calls
fixture selection, the future census, the Cayley calibration, the experimental
control panel, future publication, or a real/synthetic Coordinator lock.  Its
only executed reset-map case uses three fixed mock state labels; it verifies
the control’s executable semantics without creating an experimental curve or
measurement.  The truthful execution counts and results are in
`regression-receipt.json`.

This implementation is ready only for the Coordinator snapshot task
`TASK-20260907-916ec4` and a fresh independent review.  It remains
measurement-inadmissible and asserts no mathematical or cryptanalytic result.
