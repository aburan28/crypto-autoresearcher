# P-192 weighted-CM relation protocol

This directory contains the prospective, unexecuted protocol for
`EXP-SCURVE-1a8daf`.

- [`REPORT.md`](REPORT.md) is the human-readable design and evidence boundary.
- [`run-family.yaml`](run-family.yaml) reserves eight sequential runs; all are
  `pending_not_executed`.
- [`protocol-flow.dot`](protocol-flow.dot) is the editable diagram source.
- `protocol-flow.svg` and `REPORT.pdf` are rendered review artifacts.
- [`check_protocol.py`](check_protocol.py) checks internal IDs, arithmetic,
  counts, statuses, paths, and links without executing a scientific search.
- [`ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md) states the role and evidence status
  of every archived deliverable.
- `SHA256SUMS` binds the review bundle after rendering.

Native prerequisite: <https://github.com/aburan28/crypto/pull/1507>.
Prior archive boundary: <https://github.com/aburan28/crypto-autoresearcher/pull/1942>.

Nothing in this directory is a curve-weakness result, benchmark, run receipt,
or permission to skip the separate dispatch gate.
