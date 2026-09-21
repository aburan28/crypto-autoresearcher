# V13 Post-Fix Theory Review

## Handoff: Exact V13 checkpoint semantics

### Claim or task

Review the exact external V13 candidate root at manifest SHA-256
`856e016658cf5417b826514dee7e5fad18290e84796577570235d8b59a61fd5b`
for immutable-checkpoint acceptance.

### Status

`RESTRICTED THEOREM`, `MODEL-BOUND`, `ZERO-RUN`: `GO` for the exact external
content root only.

### Assumptions

- SHA-256 is treated as collision resistant.
- The publication verifier, policy, and manifest bytes are the reviewed bytes.
- The external root is no longer being written.
- The trusted host, filesystem, loader, and Node.js runtime are outside this
  finite-model review.

### Evidence so far

- The external root contains 227 manifest payloads, no symlinks, no special
  files, and no AppleDouble paths.
- The publication verifier pins the 227-path policy, requires exact directory
  equality, rejects forbidden metadata and non-regular paths, and verifies each
  payload digest.
- Independent manifest replay verified all 227 payloads.
- Independent isolated full verification passed 570 checks, five traces, 422
  journal transitions, and 30 artifact regressions with receipt SHA-256
  `a0020a2ecbce9beb1879c796470d2e5df2c9710e8d2bb49b34b36ea416378589`.
- The finite transition model requires a request-bound private-map observation
  after `P001`, followed by `P004` on `map_opened` or `P003` on
  `map_open_failed`; `P002` is not a canonical continuation.

### Failure modes

- This is a finite-model and publication theorem, not a live-process theorem.
- The repository mirror contains AppleDouble sidecars and is not the accepted
  checkpoint.
- Producer identity is syntactic rather than authenticated.
- Restart, process, durability, and hostile-host behavior remain outside the
  model.
- No source-compilation run, relation, target descent, scaling result, or
  ECDLP evidence exists.

### Next concrete action

Accept only the exact external content root as an immutable checkpoint, while
leaving implementation, campaign, and cryptanalytic authorization false.

### Artifact paths

- `/Volumes/Volume/autolab/research/tt-supervised-executor-v13-map-slice-candidate`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v13-map-slice-candidate.sha256`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor-v13-map-slice-candidate.publication.json`
