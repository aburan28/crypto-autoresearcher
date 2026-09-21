# Red-Team Review: Source-Aware Pair-Sum-X Selector

## Handoff: Pair-sum-x replication

### Claim or task
Determine whether a source-only affine pair-sum-x suffix order preserves the
strict typed relation gate on two fresh ordinary 14-bit curves.

### Status
NEGATIVE RESULT

### Assumptions
- The selector sees only public curve and factor-base source points and their
  pair sums.
- The strict gate requires exact projected support, held-out coverage, valid
  witnesses, and full quotient rank at a strict sub-full budget.
- The full replay and rho paths are correctness controls, not a cryptographic
  attack claim.
- Two fresh curves are enough to falsify this replication claim, but not to
  characterize all source-aware selectors.

### Evidence so far
- `source_prf_x` passes at 64/100 on p15667 and fails the two-curve replication
  because no family passes on p15683.
- Full replay, direct witnesses, selector records, independent regeneration,
  and all rho certificates pass.
- Pair-sum construction costs are recorded as 100 group operations per family
  and curve.
- Three implementation failures are preserved separately from the valid
  generator/verifier pair.

### Failure modes
- The result is toy-scale and does not establish an exponent trend.
- The primary feature may be too coarse; a compositional invariant could retain
  structure that x-order loses.
- The locator still relies on the existing adaptive row-space and repeated
  source advice; this experiment does not solve non-enumerative construction.
- No sparse linear algebra or individual-log descent improvement is claimed.

### Next concrete action
Test one predeclared compositional source invariant, with diagonal/orbit and
reversed-order controls, on the same two fresh curves and the same strict gate;
reject any candidate chosen using target support.

### Artifact paths
- `experiments/EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001/contract.md`
- `experiments/EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001/runs/RUN-TT-SOURCE-AWARE-003/`
- `experiments/EXP-ECDLP-TT-SOURCE-AWARE-REPLICATION-001/runs/RUN-TT-SOURCE-AWARE-005/`

