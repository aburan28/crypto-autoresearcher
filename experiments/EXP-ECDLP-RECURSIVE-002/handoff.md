## Handoff: Null-calibrated recursive coverage v3 execution gate

### Claim or task

Independently audit the repaired execution trust boundary before any canonical
31+31 finite-null run.

### Status

HYPOTHESIS

### Assumptions

- Thirty-one replicates per constructor are an exploratory toy percentile
  screen, not a calibrated family-wise test.
- Random-scalar and random-x are independently seeded samples of the same
  point-set null; random-x also controls construction cost.
- The charged binary-pow and lookup-byte models are disclosed proxies.
- The arithmetic programs are frozen, single-process Python under a non-root
  POSIX `RLIMIT_NPROC` boundary.
- No signing key exists; the final human audit of the external lock hash and
  approved commit is the trust anchor.

### Evidence so far

- The v1 audit returned `REVISE`; arithmetic protocol v2 repaired its
  arithmetic, control, order, and cost findings.
- The v2 audit returned `REVISE` on plan provenance, forged predecessors,
  descendant resources, post-run state, and path identity. No canonical run
  was launched.
- The v3 harness rejects plan removal/replacement, unisolated or inline Python,
  runtime-policy mismatch, forged predecessors, post-launch mutations, and
  same-inode aliases.
- A sampling-only fast-detach probe failed 12 of 12 trials. The failure is
  preserved, and locked runs now prohibit child creation with a passing
  regression.
- The frozen v2 generator/verifier hashes and nine-curve schedule are unchanged.

### Failure modes

- A third auditor may find another mutable trust input or receipt/transition
  ambiguity.
- The external lock ceremony may not match the reviewed commit exactly.
- Finite-null ranks may not survive the full 31+31 samples.
- A coverage pass may later fail rank, linear algebra, factor-base-log, or
  descent gates.

### Next concrete action

Freeze the final v3 protocol hashes in `specification.json`, commit the
review-required protocol, and request a third independent pre-run audit. Do not
launch run `003` without both that `GO` and a final lock/approval-commit check.

### Artifact paths

- `experiments/EXP-ECDLP-RECURSIVE-002/pre-run-audit-v2.md`
- `experiments/EXP-ECDLP-RECURSIVE-002/revision-response-v3.md`
- `experiments/EXP-ECDLP-RECURSIVE-002/pre-run-adversarial-probe-v3a.md`
- `experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py`
- `experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py`
- `tests/test_runner.py`
