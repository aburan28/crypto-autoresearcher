# Red-team review: source-aware compressed projective locator

## Disposition

The corrected experiment is a reproducible negative for first-half prefix
truncation. The query and arithmetic reductions are real measurements of the
candidate subproblem, but exact relation support fails at both smoke and
16-bit scale.

## Checks that passed

- The selector uses only public source-prefix indices and never target values.
- Nested-runner binding is covered by a direct unit test.
- Projective reconstruction, homogeneous zero-equivalence, and nonzero
  projective counters pass.
- Every returned witness is valid, and matched rho solves all targets.
- The 16-bit peak RSS is `4,426,481,664` bytes, below 6 GiB.
- Independent verifier `RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-017` reproduces
  the negative result and returns a valid integrity receipt.

## Objections and limitations

1. The full source skeleton and source-orbit advice remain materialized. The
   prefix reduction does not yet reduce fixed-curve advice construction or
   prove a memory/preprocessing frontier improvement.
2. Lost support is not repaired by full toy rank. A rank-complete matrix can
   omit valid relation targets and therefore cannot serve as an exact relation
   compiler.
3. The weighted projective advantage is not an end-to-end win. Sparse linear
   algebra, bandwidth, target descent, and relation filtering remain charged
   costs for a real attack.
4. The 8- and 16-bit tests use one fresh seed/curve family per scale. They are
   sufficient to falsify this selector, not to prove a universal obstruction.
5. The earlier full-scan receipts are retained for audit but excluded from the
   selector claim because their delegated-run binding was incomplete.

## Required next gate

Compare three source-only schedules at equal prefix budget: first-half
diagonal, interleaved diagonal, and deterministic source-hash permutation.
Require exact support and held-out coverage on at least three sizes before
any query-reduction signal is promoted. Then add complete advice, bandwidth,
sparse-LA, descent, and rho accounting.

## Handoff

### Claim or task
Find a target-independent prefix schedule that preserves exact support while
reducing source-prefix queries, or produce a stronger scoped negative.

### Status
OPEN

### Assumptions
- Ordinary prime-order prime-field curves.
- The projective predicate and source cache remain exact.
- Prefix order can be changed without using target or relation labels.

### Evidence so far
- First-half truncation cuts queries by about half but loses support at 8 and
  16 bits; source-family rank can survive the loss.

### Failure modes
- Any fixed schedule misses structured relation fibers; balanced schedules
  may preserve support but erase all query savings.

### Next concrete action
Implement interleaved and source-hash prefix schedules under the same contract
and run the 8-bit falsifying sweep before another 16-bit run.

### Artifact paths
- `runs/RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-014/raw-result.json`
- `runs/RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-015/raw-result.json`
- `runs/RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-017/raw-result.json`
