# V13 Post-Fix Red-Team Review

## Handoff: Immutable-checkpoint falsification

### Claim or task

Try to falsify immutable-checkpoint acceptance of the exact external V13 root
at manifest SHA-256
`856e016658cf5417b826514dee7e5fad18290e84796577570235d8b59a61fd5b`.

### Status

`OBSERVATION`: `GO` for content-bound immutable-checkpoint acceptance.
Preserve `MODEL-BOUND`, `ZERO-RUN`, and `NOVELTY-UNVERIFIED`.

### Assumptions

- Independent replay results apply to the exact manifest above.
- Writers have stopped and the external marker remains preserved.
- Acceptance identifies content, not an absolute path as a cryptographic
  identity.

### Evidence so far

- The publication verifier independently accepts the external root and pins the
  policy digest, exact path set, file types, metadata exclusions, and payload
  digests.
- The repaired policy closes the earlier completeness and AppleDouble
  objections.
- The stored checkpoint retains the finite-model and zero-run boundaries.
- A fresh two-location falsification replay passed all seven meta-publication
  controls at both locations, and the normalized case IDs, decisions,
  rejection codes, pass flags, and stable content hashes were identical.

### Failure modes

- The stored meta-publication receipt is environment-bound: it records an old
  draft path and manifest rather than the accepted external root.
- Consequently, it cannot support a claim of byte-identical receipt
  reproduction or independently bind the current root.
- The two fresh receipts also differ bytewise because their diagnostic paths
  differ. Their normalized semantic projections are identical.
- Shared-model defects, unauthenticated producer identity, restart/process
  gaps, durability gaps, and the absence of live execution remain.

### Required interpretation

- Say that the meta-publication control decisions reproduce 7/7.
- Do not say that the meta-publication receipt reproduces byte-identically.
- Say content-bound immutable checkpoint, not path-bound checkpoint.
- Do not use the stored old-manifest meta receipt to attest the current
  manifest.

### Next concrete action

Record an external `GO` for the exact manifest without modifying the immutable
root and without authorizing implementation or a campaign.

### Artifact paths

- `/Volumes/Volume/autolab/research/tt-supervised-executor-v13-map-slice-candidate`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor-v13-local-replay.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor-v13-map-slice-candidate.publication.json`
