## Handoff: SGCP five-bit implementation preflight v3a

### Claim or task

Determine whether the complete balanced four-witness universe on the frozen
five-bit curve contains an injective formal order ideal satisfying the specified
structured-group axioms, while keeping the final pair join private and charged.

### Status

HYPOTHESIS, source repair v4 review GO and source freeze ready. No canonical run
exists and approval remains separate.

### Assumptions

- Generated toy prime-order EC group only.
- Builder sees coordinates and no scalar table.
- Main verifier and scalar-index oracle may use private scalar ground truth.
- Private optimizer and final pair-sum audit are not free public structure.
- Rank, relation yield, linear algebra, target descent, and rho comparison are
  outside this preflight.

### Evidence so far

- Specification v1/v2 negatives and mathematical v3/v3a GO are preserved.
- Source red-team v1 and v2 negatives are preserved without rewriting history.
- Repair v4 composes both roles using exact argv from the locked no-descendant
  execution plan and rejects a relative-versus-absolute provenance mutation.
- Literal target-pair maps, identity witnesses, charged operations/bytes, and corrected
  candidate-versus-parent-pair densities are now exact certificate fields.
- A separately structured scalar-index implementation reproduces all three
  candidate, conflict, subset, objective, outcome-digest, and retention rows.
- The proposed execution plan is hash-complete and schema-valid but remains
  unapproved.

### Failure modes

- Any source/protocol hash or external receipt mismatch invalidates execution.
- A common-mode semantic bug may remain despite three representations.
- A passing five-bit embedding may fail immediately at larger sizes.
- Even a scalable embedding may not yield useful relations or full-rank linear
  algebra, and may lose to rho after all costs are charged.

### Next concrete action

Freeze the reviewed source in Git, then ask for explicit approval before
launching the two canonical five-bit runs.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-001/source-red-team-v1.md`
- `experiments/EXP-SGCP-EMBED-001/source-red-team-v2.md`
- `experiments/EXP-SGCP-EMBED-001/source-review-response-v3.md`
- `experiments/EXP-SGCP-EMBED-001/source-red-team-v3.md`
- `experiments/EXP-SGCP-EMBED-001/source-review-response-v4.md`
- `experiments/EXP-SGCP-EMBED-001/source-red-team-v4.md`
- `experiments/EXP-SGCP-EMBED-001/specification.json`
- `experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_scalar_index.py`
- `experiments/EXP-SGCP-EMBED-001/oracles/scalar-index-oracle-v1.json`
