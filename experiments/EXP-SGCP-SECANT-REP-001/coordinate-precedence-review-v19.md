# Coordinate-Precedence Review V19

## Handoff: V19 coordinate-precedence control review

### Claim or task

Determine whether V19 closes the V18 findings and may authorize the two scoped
coordinate-precedence text edits.

### Status

NEGATIVE RESULT

### Assumptions

- Trusted-local static plain-text review only.
- No source or test was parsed by a tool, imported, compiled, analyzed,
  formatted, tested, or executed.

### Evidence so far

- Theory principal `019facb2-4f9a-72e2-bbb9-c9b0b552343b` returned `GO`
  with `findings=[]`.
- Accounting principal `019facb2-8c80-7420-9e16-aa3792653d85` returned
  `GO` with `findings=[]`.
- Red-team principal `019facb2-ccae-7811-8312-a1cf3e4bb7d3` returned
  `REVISE` with three control-plane findings.
- Exact observed container, ancestry, one-file delta, all package hashes and
  modes, 17 exclusions, literal experiment identity, two-edit authority,
  V17 semantics, and zero-runtime locks passed.

### Failure modes

- `V19-RT-001`: a curated sidecar list did not close the ignored ambient-file
  class, especially future receipt/decision companions.
- `V19-RT-002`: the future post-repair target and transition were constrained
  by prose rather than exact target and decision schemas.
- `V19-RT-003`: pre-repair decision receipt references did not explicitly bind
  exact reference keys and `paths_by_role` equality.

### Remediation evidence

Before V20 design, all 113 ignored `._*` files under the experiment were
verified as AppleDouble, verified untracked, and physically removed. The
experiment subtree now has a closed empty `._*` inventory; the two ancestor
companions `._experiments` and `experiments/._EXP-SGCP-SECANT-REP-001` are also
absent.

### Next concrete action

Create V20 with subtree-wide ignored-ambient inventory fields in every review
and decision, exact receipt-reference cross-binding, and exact post-repair
target plus design-only transition-decision schemas.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/coordinate-precedence-review-protocol-v19.json`
- `experiments/EXP-SGCP-SECANT-REP-001/coordinate-precedence-review-v18.md`
- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-api-amendment-v17.md`

No source/test edit or execution-related authority is granted.
