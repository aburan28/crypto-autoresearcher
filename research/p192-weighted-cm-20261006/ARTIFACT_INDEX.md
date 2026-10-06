# P-192 weighted-CM protocol artifact index

All entries below are prospective design evidence. No entry is a run receipt,
benchmark, discovered relation, explicit isogeny, or weakness result.

## Canonical research records

- `../../ledger/questions/RQ-SCURVE-42f1a3.yaml`: research question and scope.
- `../../ledger/proposals/IDEA-20261006-767793.yaml`: proposed principal-norm
  search mechanism and prior-art boundary.
- `../../ledger/hypotheses/H-SCURVE-ec34c4.yaml`: approved, falsifiable
  hypothesis; approval does not authorize execution.
- `../../experiments/EXP-SCURVE-1a8daf/specification.yaml`: authoritative
  experiment protocol, admission gates, cost contracts, controls, statistics,
  budgets, and claim limits.
- `../../ledger/decisions/DEC-20261006-a39750.yaml`: planning approval with
  `execution_authorized: false` and a required fresh dispatch decision.

## Review bundle

- `README.md`: directory boundary and prerequisite links.
- `REPORT.md`: human-readable protocol and evidence boundary.
- `REPORT.pdf`: rendered review copy of `REPORT.md`.
- `protocol-flow.dot`: editable flow-diagram source.
- `protocol-flow.svg`: vector render used by the report.
- `protocol-flow.png`: raster review render.
- `run-family.yaml`: noncanonical, nondispatchable plan for eight logical run
  roles; every role is `pending_not_executed` and no `RUN-*` ID is reserved.
- `check_protocol.py`: static arithmetic, identity, link, and pending-state
  checker; it does not enumerate norms or measure performance.
- `SHA256SUMS`: byte-level digest manifest for the records and review bundle.

## External lineage

- Native prerequisite: <https://github.com/aburan28/crypto/pull/1507>.
- Prior immutable archive boundary:
  <https://github.com/aburan28/crypto-autoresearcher/pull/1942>.

The next permissible action is source/schema implementation and independent
review. Scientific execution remains blocked until all admission requirements
pass and a new dispatch decision binds exact clean commits.
