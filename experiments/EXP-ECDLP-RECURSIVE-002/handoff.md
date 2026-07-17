## Handoff: Null-calibrated recursive coverage v2

### Claim or task

Repair and independently audit the finite-null experiment before any canonical
execution.

### Status

HYPOTHESIS

### Assumptions

- Thirty-one replicates per constructor are an exploratory toy percentile
  screen, not a calibrated family-wise test.
- Random-scalar and random-x are independently seeded samples of the same
  point-set null; random-x also controls construction cost.
- The charged binary-pow and lookup-byte models are disclosed proxies.
- The `p mod 4 = 3` restriction remains explicit.

### Evidence so far

- The v1 audit preserved curve arithmetic, seed uniqueness, exact supports,
  percentile direction/ties, and reduced reconstruction.
- The audit returned `REVISE` on two S0 and three S1 protocol defects; no
  canonical run was launched.
- The v2 generator makes positive, order, curve, rho, field-distinctness, and
  seed controls mandatory.
- A 128-target reduced smoke passed on nine curves over nine distinct fields.
- The structured-group literature map identifies a formal embedding gap rather
  than claiming that coordinate density equals the model's `delta`.

### Failure modes

- The independent v2 verifier or execution-plan enforcement may still find a
  mismatch.
- Finite-null ranks may not survive all 31+31 samples.
- Charged operation proxies may conceal hardware or bandwidth costs.
- A coverage pass may fail rank, linear algebra, factor-base-log, or descent
  gates.

### Next concrete action

Finish the independent v2 verifier and execution-plan tests, freeze every hash
and exact argv, then request a second pre-run audit. Launch nothing without
`GO`.

### Artifact paths

- `experiments/EXP-ECDLP-RECURSIVE-002/pre-run-audit-v1.md`
- `experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py`
- `experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py`
- `tests/test_null_calibrated_coverage.py`
- `notes/structured_group_coordinate_predicates_literature_20260717.md`
