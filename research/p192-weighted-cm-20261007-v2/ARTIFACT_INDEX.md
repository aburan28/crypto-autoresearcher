# P-192 weighted-CM protocol v2 artifact index

All entries below are prospective design evidence. No entry is a run receipt,
benchmark, discovered relation, explicit isogeny, or weakness result.

## Canonical research records

- `../../ledger/questions/RQ-SCURVE-42f1a3.yaml`: research question and scope.
- `../../ledger/proposals/IDEA-20261006-767793.yaml` and
  `../../ledger/hypotheses/H-SCURVE-ec34c4.yaml`: immutable v1 motivation and
  hypothesis context; the v2 amendment supplies the corrected executable
  ordering without rewriting either record.
- `../../experiments/EXP-SCURVE-1a8daf/specification.yaml`: immutable v1
  protocol at commit `4b9207e`; historical and nondispatchable.
- `../../experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml`:
  additive v1-to-v2 change record and immutable-v1 hash binding.
- `../../experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml`:
  authoritative future protocol, admission gates, costs, controls, statistics,
  budgets, and claim limits.
- `../../ledger/decisions/DEC-20261007-0ed467.yaml`: v2 planning approval with
  `execution_authorized: false`; it supplies the allocated amendment identity
  and requires a fresh dispatch decision.
- `../../ledger/handoffs/TASK-20261007-66d44b.yaml`: sole Coordinator archive
  owner for the additive v2 payload; maximum scientific runs is zero.
- `../../ledger/corrections/CORR-20261007-f4d600.yaml`: disclosure and remedy
  for binding archive ownership only after the v1 precursor work and reviews
  had begun; it changes no scientific conclusion.
- `../../coordination/p192-weighted-cm-20261007/archives/TASK-20261007-66d44b/snapshot-receipt.json`:
  post-commit receipt binding the first archive commit, its parent, exact path
  set, sizes, and hashes; written in the receipt-only second commit.

## Review bundle

- `README.md`: directory boundary and prerequisite links.
- `REPORT.md`: human-readable protocol and evidence boundary.
- `REPORT.pdf`: rendered review copy of `REPORT.md`.
- `protocol-flow.dot`: editable flow-diagram source.
- `protocol-flow.svg`: vector render used by the report.
- `protocol-flow.png`: raster review render.
- `run-family.yaml`: v2 nondispatchable plan for eight logical roles; every role
  is `pending_not_executed`, roles 7–8 have null argv, and no `RUN-*` ID is
  reserved.
- `check_protocol.py`: static arithmetic, identity, link, and pending-state
  checker; it does not enumerate norms or measure performance.
- `SHA256SUMS`: byte-level digest manifest for the exact records and review
  payload, excluding itself and the snapshot receipt; the enclosing archive
  commit and receipt bind the two exclusions.

## External lineage

- Native prerequisite: <https://github.com/aburan28/crypto/pull/1507>.
- Prior immutable archive boundary:
  <https://github.com/aburan28/crypto-autoresearcher/pull/1942>.

The next permissible action is source/schema implementation and independent
review. Scientific execution remains blocked until all admission requirements
pass and a new dispatch decision binds exact clean commits.
