# Pre-run theory review: SGCP-EMBED-001 v3a

Date: 2026-07-17

Execution state: no canonical certificate or experiment run was launched.

## Handoff: monotonic subset-audit compression

### Claim or task

Decide whether invalid-vertex witness replay plus exhaustive valid-vertex
subsets proves feasibility for every subset of `U4_BAL`.

### Status

RESTRICTED THEOREM / GO

### Assumptions

- The generated family is exactly `I0` union the selected candidate
  submultiset ideals.
- Every invalid vertex has an independently replayed internal collision.
- Every subset of valid vertices is checked without sampling.

### Evidence so far

- Any family containing an invalid vertex contains its colliding `I(M)`, and
  noninjectivity persists under supersets.
- Every other selection is a subset of the individually valid vertices.
- The two cases partition every subset of `U4_BAL`.
- The contract requires invalid-witness replay, exactly `2^valid_count` direct
  checks, mismatch count, and an ordered outcome digest.
- At `B=8`, this replaces a redundant `2^124` loop with 110 replayed invalid
  witnesses and exactly `2^14=16384` direct valid-subset checks.

### Failure modes

- A collision witness is not replayed.
- A valid-vertex subset is omitted or sampled.
- The generated closure contains mixed formal objects outside the stated union.

### Next concrete action

Implement the exact audit and preserve its counts and ordered digest in both
builder and independent verifier output.

### Artifact paths

- `notes/sgcp_embed_001_contract_20260717.md`
- `experiments/EXP-SGCP-EMBED-001/implementation-clarification-v3a.md`
- `experiments/EXP-SGCP-EMBED-001/pre-run-theory-review-v3a.md`
