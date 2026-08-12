# Red-team review of v1

## Handoff: repaired bundle audit

### Claim or task

Determine whether v1 resolves the prior launch blockers for a `SANITY_ONLY`
first-norm diagnostic.

### Status

`REVISE`. R1-R4 and R6-R8 passed; the mutation protocol remained incomplete.

### Assumptions

- No compiler, asymptotic, locator, relation-generation, or ECDLP claim is
  approved.

### Evidence so far

- Independent checks passed for curve and manifest consistency, Frobenius,
  norm identity, source coefficients, identity target, and Hilbert caps.
- Producer/verifier separation, rank fields, accounting boundary, selection
  firewall, and interpretation firewall were adequately specified.
- Numeric rank cannot detect a wrong field label on an `F_p`-valued matrix;
  rank-field provenance needs a static gate.
- Symmetric known-rank controls cannot guarantee detection of reversed cuts.
- The flipped RCB gate and every mutation's exact transformation, cell,
  detector, and required outcome were not frozen.

### Failure modes

- A cut-order or rank-field metadata bug can survive numerically plausible
  values without an asymmetric control and provenance lint.
- A post-hoc mutation choice does not test the frozen verifier.

### Next concrete action

Freeze `mutation-manifest-v2.json` with exact transformations and an
independently certified `(1,2,3,4)` cut-rank tensor.

### Artifact paths

- `mutation-manifest-v2.json`
- `contract-v2.md`
- `specification-v2.json`

