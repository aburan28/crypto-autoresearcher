# Exact Test-Source Review V15

## Handoff: V15 exact test-source review

### Claim or task

Determine whether test source SHA-256
`19b4382666cdea34c4fe4405b9eb25dcc10269f0ebd3d4ea2d9e1d50c3c69040`
is ready for a separate execution-authorization design.

### Status

NEGATIVE RESULT

### Assumptions

- Trusted-local static plain-text review only.
- No source or test was parsed by a tool, imported, compiled, analyzed,
  formatted, tested, or executed.

### Evidence so far

- Accounting principal `019fac7a-7dcc-7923-8998-6cd929c64185` returned
  `GO` with `findings=[]`.
- Red-team principal `019fac7a-ad98-76f2-a74d-e7eea9820bf1` returned `GO`
  with `findings=[]`.
- Theory principal `019fac7a-473c-7bf0-a615-4690111f3611` returned
  `REVISE` with three blocking findings.
- All reviewers reproduced the exact V15 target, source/test hashes, commit,
  tree, and zero-runtime authority.

### Failure modes

- `V15-THEORY-001`: four ignored AppleDouble metadata files existed beside
  protected/V15 artifacts. Each was independently identified by `file` as
  AppleDouble and removed physically; no regular artifact was removed.
- `V15-THEORY-002`: combined-invalid controls did not pin a-versus-b exact-type
  order, x-versus-y point-field order, or point-validation index order.
- `V15-THEORY-003`: `_trial_remainder_count` remained structurally too close
  to the protected trial-division control flow.

### Next concrete action

The same bound independent author revises only the singleton test file by
adding the missing combined-invalid precedence controls and replacing the
remainder-count oracle with a structurally independent formulation, without
reading protected source or executing either file.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/test-source-exact-review-target-v15.json`
- `experiments/EXP-SGCP-SECANT-REP-001/test-source-exact-review-authorization-v15.json`
- `experiments/EXP-SGCP-SECANT-REP-001/test-source-exact-review-consistency-v15.json`
- `experiments/EXP-SGCP-SECANT-REP-001/tests/test_sgcp_secant_math_core.py`

No parsing, import, compilation, analysis, test, experiment, or runtime
authority is granted.
