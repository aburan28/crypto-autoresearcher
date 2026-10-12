# P-192 weighted-CM relation protocol — additive v2

This directory contains the prospective, unexecuted v2 amendment bundle for
`EXP-SCURVE-1a8daf`. The committed v1 specification and review directory are
immutable historical records; approval decision `DEC-20261007-0ed467` and
`experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml` make
`experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml` authoritative
for any future implementation or run.

- [`REPORT.md`](REPORT.md) is the human-readable design and evidence boundary.
- [`run-family.yaml`](run-family.yaml) describes eight ordered logical roles;
  all are `pending_not_executed`, roles 7–8 have null argv, and no `RUN-*` ID
  is reserved.
- [`protocol-flow.dot`](protocol-flow.dot) is the editable diagram source.
- `protocol-flow.svg` and `REPORT.pdf` are rendered review artifacts.
- [`check_protocol.py`](check_protocol.py) checks internal IDs, arithmetic,
  counts, statuses, paths, and links without executing a scientific search.
- [`ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md) states the role and evidence status
  of every archived deliverable.
- `SHA256SUMS` binds the exact published payload after rendering, excluding
  itself and the snapshot receipt; the archive commit and receipt bind those
  two self-reference exceptions.

Native prerequisite: <https://github.com/aburan28/crypto/pull/1507>.
Prior archive boundary: <https://github.com/aburan28/crypto-autoresearcher/pull/1942>.

Archive ownership is `TASK-20261007-66d44b`.  The corresponding correction
`CORR-20261007-f4d600` discloses that ownership was bound late; the post-commit
snapshot receipt is written in a second, receipt-only commit so it can bind the
first commit without self-reference.

Nothing in this directory is a curve-weakness result, benchmark, run receipt,
execution authorization, or permission to skip the separate dispatch gate.
