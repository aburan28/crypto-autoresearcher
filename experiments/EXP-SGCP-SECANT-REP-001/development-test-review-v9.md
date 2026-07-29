# Development-Test Execution Review V9

## Handoff: dangling symbolic-ref CAS alias

### Claim or task

Determine whether V9 safely constructs and authorizes exactly one isolated
five-test development run.

### Status

NEGATIVE RESULT

### Evidence so far

- Static review at commit
  `2e1912db8ac3c11f329795f4c287bb1f11d1cf93`, tree
  `304b8c8f40199babddc4ed61de8197a644248808`.
- Sole parent:
  `d73da7e526342153782703d877c1bbf9d4e93281`.
- Protocol SHA-256:
  `2ae3b80ba7601b47b7093ffbc6d9fef02d50e8fb877313694ebf26840b0e08f7`.
- Host SHA-256:
  `9944e8985c198045cb73928d8f6b3593a401093cb9f88c7c2815221ffc19b81c`.
- Theory principal `019fadc2-25a9-71b0-ab3a-d674f7a1cca4` and
  accounting principal `019fadc2-4973-7b62-840e-4dd4b925120d` returned
  scoped `GO`.
- Red-team principal `019fadc2-6b4e-72c1-9103-368f15c887fb` returned
  `REVISE`.
- No protected parser, import, compile, test, runner, validator, or Docker
  execution occurred.

### Failure mode

`DANGLING_SYMREF_CAS_ALIAS`: a pre-existing C or R ref can be a dangling
symbolic ref to an absent hidden target. `show-ref --verify` reports the named
ref as absent, but `update-ref` without `--no-deref` follows the symbolic ref
and installs the candidate at the hidden target. Later `rev-parse` resolves
through the alias and can pass, despite the named custody ref having pre-existed
and not directly storing the candidate.

### Strongest valid statement

V9 removes the V8 authorization-commit fixed point: P-derived naming is
constructible while A remains bound in labels and receipts. It remains
unauthorized because exact C/R custody is not protected against dangling
symbolic-ref aliases.

### Next concrete action

Create V10 that rejects symbolic C/R refs before CAS, uses
`update-ref --no-deref` with the all-zero old value for both refs, and verifies
the installed C ref is nonsymbolic. Preserve result CAS as the terminal
fallible seal operation; `--no-deref` itself guarantees direct R installation.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v9.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v9.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v9.md`

No development-test or experiment-execution authority is granted.
