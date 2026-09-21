# Nested source-norm benchmark review v1

## Handoff: dense-interface accounting audit

### Claim or task

Audit the B-exponents, storage counts, direct and black-box costs, identity
membership, child work, and exact gate failures.

### Status

`REVISE`. The scoped negative is sound; three accounting repairs were required
and have been applied to the primary preflight.

### Assumptions

- Balanced collision-light specialization: `d_i=Theta(B)`,
  `n_I=Theta(B^2)`.
- Dense counts are allocated slots or worst-case nonzeros.
- Tier B requires target work/state `o(B^2)` and advice/workspace `o(B^3)`.

### Evidence so far

- `A_123`, `A_12`, direct tuples, and terminal lift have the stated exponents.
- Sequential and black-box negatives are correctly restricted to their explicit
  interfaces.
- Child factorization and the root-only identity exception are correctly scoped.
- Scalar-only transposed evaluation remains open.

### Required revisions applied

- The D2-identity decision now uses the charged `Theta(B)` factor scan against
  D2; the same scan returns its D3 witness.
- Explicit selectors and global units receive a `Theta(B^3)` coordinate census
  and Tier A/Tier B disposition.
- Every rejected interface is mapped to its exact work, traffic, live-state,
  workspace, or advice gate. The terminal scan is explicitly non-obstructive.

### Failure modes

Do not charge only the post-success witness while omitting its membership
decision. Do not turn dense interface dimensions into compact-circuit lower
bounds.

### Next concrete action

Perform a final accounting re-read before freezing this family as a scoped
negative.

### Artifact paths

- `nested-source-norm-preflight-v1.md`
- `contract.md`
- `object-dimension-ledger.md`
