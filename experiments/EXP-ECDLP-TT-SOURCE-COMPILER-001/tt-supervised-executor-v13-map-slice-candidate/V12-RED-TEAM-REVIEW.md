# Handoff: V12 Immutable Reap-Slice Red Team Attestation

### Claim or task

Verify the externally rooted V12 checkpoint after publication staging.

### Status

`OPEN` | `GO_FOR_IMMUTABLE_FINITE_MODEL_CHECKPOINT`

### Assumptions

- The reviewed root is
  `98dba44fb4e79fd4d156a04ec6a528d2fa98d528d8e7c8fa16f18f58fa4c60da`.
- The decision covers finite-model replay and publication integrity only.
- Runtime, OS, durability, campaign, cryptanalytic, and ECDLP claims are
  excluded.

### Evidence so far

- The external marker names the exact `SHA256SUMS` root.
- The publication verifier returns `ACCEPT` for 202 payloads.
- Manifest replay verifies 202 of 202 entries.
- Exact manifest equality and source-to-snapshot byte equality are true.
- Symlink and AppleDouble counts are zero.
- The post-fix reap suite passes 16 of 16 controls and local verification passes
  482 checks.

### Failure modes

- External publication equality is not runtime evidence.
- The finite observation gateway is not an attested OS witness.
- Later external event boundaries remain open.

### Next concrete action

Record this root as a frozen finite-model `GO` and open only the next typed
private-map observation slice.

### Artifact paths

- `tt-supervised-executor-v12-reap-slice-checkpoint.sha256`
- `tt-supervised-executor-v12-reap-slice-checkpoint.publication.json`
- `tt-supervised-executor-v12-reap-slice-checkpoint/SHA256SUMS`

