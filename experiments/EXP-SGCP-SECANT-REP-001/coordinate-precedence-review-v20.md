# Coordinate-Precedence Review V20

## Handoff: V20 coordinate-precedence control review

### Claim or task

Determine whether V20 closes the V19 findings and may authorize the two scoped
coordinate-precedence text edits.

### Status

NEGATIVE RESULT

### Assumptions

- Trusted-local static plain-text review only.
- No source or test was parsed by a tool, imported, compiled, analyzed,
  formatted, tested, or executed.

### Evidence so far

- Theory principal `019facbf-c2c8-7d42-8c4e-4fd438eb1802` returned `REVISE`.
- Accounting principal `019facbf-edf3-7eb3-8ede-ed02d4df6f63` returned
  `REVISE`.
- Red-team principal `019facc0-21dd-7f63-8a1b-9bd98c7a7dfc` returned
  `REVISE`.
- Exact V20 container, one-file delta, protocol hash, 20 exclusions, empty
  experiment-subtree inventory, absent repository-local ancestors, exact
  receipt-reference keys, future target identity, design-only transition
  fields, V17 semantics, and zero current source/test delta passed.

### Failure modes

- V20 inherited stale V19 observed-parent/tree/delta literals instead of
  replacing them with the V20 container.
- Pre-repair receipts and decision did not add the V20 protocol digest, literal
  V20 decision ID/path, or full current observed tuple.
- The post-repair target named commit/tree/diff fields without exact relational
  rules tying commits to trees, sole-parent ancestry, two mode-`100644` paths,
  blob identities, and independently enumerated zero extras.
- Full ignored-inventory fields were absent from post-repair receipts.
- The design-only transition omitted explicit false seed, child,
  protected-source-runtime, and test-source-runtime fields.
- A confirmed AppleDouble companion of the checkout directory existed one
  level above the repository; it was physically removed.

### Next concrete action

Create V21 as a full replacement rather than an amendment. It must bind the
actual V20 container and V21 digest in every pre-repair receipt and decision,
provide one exact pre-decision path/schema, impose relational post-repair Git
rules and full inventories, and enumerate every false transition lock.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/coordinate-precedence-review-protocol-v20.json`
- `experiments/EXP-SGCP-SECANT-REP-001/coordinate-precedence-review-protocol-v19.json`
- `experiments/EXP-SGCP-SECANT-REP-001/coordinate-precedence-review-v19.md`

No source/test edit or execution-related authority is granted.
