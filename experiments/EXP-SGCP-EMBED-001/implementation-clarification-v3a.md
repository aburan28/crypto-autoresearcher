# SGCP-EMBED-001 implementation clarification v3a

Date: 2026-07-17

Execution state: scratch recount only; no canonical certificate or experiment
run was launched.

## Handoff: exact subset audit compression

### Claim or task

Implement the v3 conflict-graph cross-check exactly without attempting a
literal `2^|U4_BAL|` loop over subsets already known infeasible.

### Status

RESTRICTED THEOREM CANDIDATE / REVIEW REQUIRED

### Assumptions

- Evaluation noninjectivity is monotone under enlarging a formal family.
- Every individually invalid candidate stores a direct collision witness.
- Every subset of individually valid vertices is enumerated at five bits.

### Evidence so far

- Scratch coordinate recounts give balanced candidate counts `31`, `68`, and
  `124` for `B=4,6,8`.
- Only `12`, `8`, and `14` candidates respectively are individually closure
  injective.
- Literal loops would demand up to `2^124` checks, while all subsets containing
  any of the 110 invalid `B=8` vertices are already rejected by that vertex's
  preserved collision.
- For the remaining valid vertices, the conflict-graph lemma requires only
  `2^12`, `2^8`, and `2^14` direct subset comparisons.

### Failure modes

- An invalid-vertex collision is not independently replayed.
- A subset of valid vertices is sampled or omitted.
- Graph independence and direct full-family injectivity disagree.

### Next concrete action

Review the monotonic compression. If accepted, require the verifier to replay
every invalid-vertex witness and enumerate every subset of valid vertices,
recording checked subset counts and a digest of all feasibility outcomes.

### Artifact paths

- `notes/sgcp_embed_001_contract_20260717.md`
- `experiments/EXP-SGCP-EMBED-001/implementation-clarification-v3a.md`
