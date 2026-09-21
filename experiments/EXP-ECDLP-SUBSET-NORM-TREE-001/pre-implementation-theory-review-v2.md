# Pre-implementation theory review v2

## Handoff: repaired subset-norm correctness

### Claim or task

Re-review the exact intersection encoding and conditional witness self-reduction
after v1 repairs.

### Status

`RESTRICTED THEOREM`: `GO` for the correctness layer only.

Compact-operator, displacement-rank, child-restriction, and Tier B feasibility
remain `REVIEW_REQUIRED`. No implementation or execution is authorized.

### Assumptions

- `K/F_p` is the registered genuine quadratic extension.
- D2 and D3 use distinct oriented finite points with identity separate.
- Each support point retains one deterministic signed witness and separate audit
  multiplicity.
- Tree descent is conditional on exact node predicates and terminal lift.

### Evidence so far

- `x+omega*y` and target translation are injective on the registered domains.
- Common root, nontrivial gcd, zero resultant, and finite D2-translated-D3
  intersection are equivalent.
- Identity, empty product, and target degree-drop semantics are exact.
- Left-first descent returns a five-id witness in logarithmically many oracle
  calls without claiming logarithmic time.

### Failure modes

No mathematical defect remains in the conditional correctness layer. The tree
does not supply a compact node oracle; hereditary restriction and all operator
dimensions remain open.

### Next concrete action

Derive the root translated-D3 operator, displacement equation, rank, storage,
query work, certificates, and child restriction. Do not implement.

### Artifact paths

- `theory.md`
- `contract.md`
- `object-dimension-ledger.md`
