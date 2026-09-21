# Red-Team Review: EXP-ECDLP-TT-SAMPLED-SCALE-001

- The full-budget run is a correctness control, not a new algorithmic result.
- Projected `a`-support must be separated from exact witness multiplicity;
  multiple valid R^4 witnesses are not false positive support.
- The p16267 `x_interval` rank `10/11` result must remain visible; averaging
  it with the three rank-11 families would hide a real negative control.
- The 32/100 `rational_union` result is support-only because held-out coverage
  fails. It cannot be promoted to the accepted locator gate.
- The accepted 64/100 result still spends substantial source and memory work;
  rho, sparse linear algebra, target descent, bandwidth, and advice
  construction must be charged before any Pareto claim.
- The harness run is valid only as toy/model-bound evidence. No statement
  about cryptographic-size curves, deployed keys, or a square-root exponent
  change follows from this receipt.

## Handoff

### Claim or task

Challenge the p16267 sampled-locator signal and its matched-baseline framing.

### Status

MIXED RESULT; POSITIVE LOCATOR SIGNAL WITH REQUIRED REPLICATION

### Assumptions

- The generated fixture and runner records are immutable and hash-bound.

### Evidence so far

- Generator and independent verifier harness runs are both `completed_valid`.
- All direct rho certificates verify; full typed support/witness controls pass.
- Only three families reach the full held-out/rank gate at the 64/100
  budget; one family remains rank-deficient.

### Failure modes

- One curve can favor a selector accidentally.
- The sampled selector may be exploiting fixture-specific support geometry.
- End-to-end relation matrix and target descent costs may erase the measured
  reconstruction reduction.

### Next concrete action

Run fresh curves and a structured-selector control under the same harness
contract, with a complete charged cost table.

### Artifact paths

- `runs/RUN-TT-SAMPLED-001/`
- `runs/RUN-TT-SAMPLED-002/`
