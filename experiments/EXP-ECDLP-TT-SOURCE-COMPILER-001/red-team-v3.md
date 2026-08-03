## Handoff: v4 implementation authorization review

### Claim or task

Decide whether the v4 target-redacted protocol authorizes source
implementation.

### Status

`REVISE`

### Assumptions

- Status transitions occur only after independent reviews; a pending status is
  not itself evidence of a protocol defect.
- Source and campaign counts may differ if their scopes and reconciliation are
  explicit.

### Evidence so far

- The source-visible input reports zero target records, coordinates, digests,
  and labels.
- The source generator and source verifier read only the redacted manifest,
  target-free source matrix, and source raw result as applicable.
- Isolated staging, filesystem metadata/event auditing, environment controls,
  closed IR, transitive AST/call-graph audit, and stdout-only output are bound.
- Retained advice and non-retained control sources are separate frozen
  artifacts, and one receipt binds both before target availability.
- Python executable, NumPy closure, core extension, architecture, loader paths,
  dtype, order, and thread count are bound.
- M18A, M18B, M26, M27, and M28 exist with distinct rejection channels.
- The claim remains toy, restricted, model-bound, and explicitly not an ECDLP
  improvement.

### Blocking finding

The source matrix reports 1,022 source normalizations and 8,176 source
two-sweep factorizations, while the full matrix reports 1,047 and 8,376.
These are mathematically compatible subtotals, but v4 does not put a frozen
scope label and reconciliation equation next to both records. The same
ambiguity reaches the 9,688 source and 9,888 campaign total-factorization
upper bounds.

The `review_required` and `approved_by:null` fields are expected pending-state
markers and must not be transitioned until the repaired review returns `GO`;
changing them preemptively would be circular.

### Failure modes

- An implementation could compare a source subtotal to a campaign total and
  falsely report a mismatch or spare budget.
- An auditor could treat target work as omitted rather than phase-separated.

### Next concrete action

Version an explicit equation
`source subtotal + 25 target normalizations = campaign total`, including the
corresponding 200 two-sweep factorizations, then rerun the red-team gate.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/red-team-v3.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/source-execution-matrix-v1.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/execution-matrix-v3.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/revision-history-v4.md`
