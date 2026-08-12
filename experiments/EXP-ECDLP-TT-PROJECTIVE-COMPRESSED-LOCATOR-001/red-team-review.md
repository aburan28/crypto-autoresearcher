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

## Schedule follow-up disposition

At 8 bits, interleaving improves the candidate family to exact full support,
but misses two randomized-control relations and has no held-out gate. A
source-hash permutation misses support in both families. The parity-balanced
schedule misses two candidate-family and three randomized-control relations at
the same `32/64` budget. These are useful control results, not a generic
positive signal.

## Required next gate

No tested 50% schedule passes the generic support gate. A future schedule
should be tested on fresh 12/16-bit curves only if it has a mechanism beyond
fixed prefix ordering; otherwise the positive search should move to
target-independent row-space compression. Any successor still requires exact
support, held-out coverage, complete advice, bandwidth, sparse-LA, descent,
and rho accounting.

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
- Interleaved, source-hash, and parity-balanced 8-bit controls do not jointly
  preserve candidate and randomized support at the same half-prefix budget.

### Failure modes
- Any fixed schedule misses structured relation fibers; balanced schedules
  may preserve support but erase all query savings.

### Next concrete action
Move to a target-independent row-space compressor or an explicitly
geometry-derived schedule; require a new positive mechanism before spending a
12/16-bit run.

### Artifact paths
- `runs/RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-014/raw-result.json`
- `runs/RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-015/raw-result.json`
- `runs/RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-017/raw-result.json`
- `runs/RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-024/raw-result.json`
- `runs/RUN-TT-PROJECTIVE-COMPRESSED-LOCATOR-025/raw-result.json`
