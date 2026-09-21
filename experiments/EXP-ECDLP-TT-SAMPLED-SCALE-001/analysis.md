# Analysis: EXP-ECDLP-TT-SAMPLED-SCALE-001

## Handoff: p16267 sampled typed-TT locator

### Claim or task

Determine whether hash-ranked sampled suffix columns retain exact typed
five-term relation support and rank on the next fresh ordinary curve.

### Status

OBSERVATION, TOY-EVIDENCE, MODEL-BOUND

### Assumptions

- The p16267 fixture is generated public toy data at `p=16267`, `q=16057`.
- Materialized typed D4 support is the correctness baseline for projected
  `a`-support; the row-space candidate may emit multiple valid R^4 witnesses
  for one `a`.
- Pollard-rho group-operation counts are a matched generic baseline for the
  same public targets, not a proof of an asymptotic comparison.

### Evidence

- Harness generator `RUN-TT-SAMPLED-001` is `completed_valid` with wall time
  `170.133436958` seconds, CPU time `143.372504` seconds, and peak RSS
  `2,655,305,728` bytes.
- The adaptive row-space rank is `55` for all four families. The full-budget
  control is exact and every full-budget candidate witness is valid.
- The full held-out gate passes at 64/100 columns for `random_x`,
  `source_prf_x`, and `rational_union`. Their quotient ranks are `11/11`.
- `rational_union` already has exact projected support at 32/100 columns, but
  held-out coverage is incomplete there, so 32/100 is a support-only signal,
  not an accepted relation-locator result.
- `x_interval` has exact full-budget support and held-out coverage but remains
  rank `10/11`; it is a preserved family-specific negative control.
- At the accepted 64/100 budget, predicted entries fall from `1,800,000` to
  `1,152,000` per row. Source point additions fall from `122,400` to
  `105,300` for `random_x` and `rational_union`, and to `106,440` for
  `source_prf_x`. Reconstruction field multiplications fall from
  `153,450,000` to `117,810,000`.
- The harness rho baseline solves all 60 public targets across four families;
  total charged group operations are `109,548`.
- Independent verifier `RUN-TT-SAMPLED-002` is `completed_valid` and checks
  regenerated relation input hashes, full replay, candidate witness/support
  records, held-out structure, and direct rho certificates.

### Failure modes and limits

- The 64/100 signal is a constant-factor locator result on one p16267 curve,
  not a fitted exponent and not a generic ECDLP improvement.
- The candidate still constructs a large shared source cache; its measured
  cache peak is approximately `24.9-25.1 MB` at the accepted budget and
  `28.2 MB` at full budget. Advice construction, memory bandwidth, relation
  filtering, sparse linear algebra, and individual target descent remain
  incompletely charged against rho.
- The rho baseline is repeated per coordinate family, so it is a matched
  target cost context rather than a many-target deployment claim.
- Uniform hash-ranked sampling is not a general selector: x_interval fails
  rank, and 32/100 rational_union misses held-out coverage.

### Next concrete action

Replicate the 64/100 full-gate signal on at least two fresh ordinary curves,
then compare hash-ranked sampling with a target-independent structured suffix
selector while charging sparse linear algebra, target descent, bandwidth,
and the same harness rho baseline.

### Artifact paths

- `runs/RUN-TT-SAMPLED-001/`
- `runs/RUN-TT-SAMPLED-002/`
- `src/run_sampled_scale_harness.py`
- `src/verify_sampled_scale_harness.py`
- `contract.md`
