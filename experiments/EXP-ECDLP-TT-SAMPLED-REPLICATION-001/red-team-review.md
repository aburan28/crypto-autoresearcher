# Red-Team Review: Two-Seed Fresh Sampled Locator Replication

## Handoff: Fresh-curve replication interpretation

### Claim or task
Assess whether the p16267 sampled typed-TT locator signal replicates under the
declared two-seed fresh-curve protocol.

### Status
NEGATIVE RESULT

### Assumptions
- The committed typed-five-EC generator produces ordinary 14-bit prime-order
  toy curves for both seeds.
- The strict gate requires exact projected support, exact held-out coverage,
  valid witnesses, and full quotient rank at a sub-full budget.
- Full replay and direct rho certificates are correctness controls, not attack
  evidence.
- The selector is hash-ranked uniform suffix sampling; this result does not
  generalize to every selector or compiler.

### Evidence so far
- Both fresh curves pass full replay and full witness checks.
- Both fresh curves pass independent fixture regeneration and all direct rho
  certificates.
- No family on either curve has an accepted strict sub-full budget.
- Failed verifier receipts preserve the timing-hash bug and its correction.

### Failure modes
- Two curves are still toy-scale and do not establish an asymptotic trend.
- Partial support or rank signals may be hidden by the strict all-target gate.
- The sampled selector may be the wrong object; a structured source-aware
  selector could behave differently.
- The experiment does not include sparse linear algebra or individual-log
  descent beyond the declared quotient/rho controls.

### Next concrete action
Run a source-aware or circuit-derived selector on the same two fresh fixtures,
requiring the same strict support/held-out/rank gate and charging advice,
bandwidth, relation filtering, sparse linear algebra, descent, and matched rho.

### Artifact paths
- `experiments/EXP-ECDLP-TT-SAMPLED-REPLICATION-001/analysis.md`
- `experiments/EXP-ECDLP-TT-SAMPLED-REPLICATION-001/runs/RUN-TT-REPLICATION-005/`
- `experiments/EXP-ECDLP-TT-SAMPLED-REPLICATION-001/runs/RUN-TT-REPLICATION-006/`

