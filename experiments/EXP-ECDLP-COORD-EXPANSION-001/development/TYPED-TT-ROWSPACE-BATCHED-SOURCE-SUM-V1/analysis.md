# Analysis: TYPED-TT-ROWSPACE-BATCHED-SOURCE-SUM-V1

## Handoff: fixed-curve source-sum batching

### Claim or task

Test whether target-independent source-point caching lowers fixed-curve
batched row-space evaluation cost while preserving exact sampled predicates.

### Status

OBSERVATION, TOY-EVIDENCE, MODEL-BOUND

### Assumptions

- The generated curve is ordinary, prime-order, and used only as a toy public
  benchmark.
- The first target constructs an adaptive cut-3 row space with a 64-prefix
  cap; this cap is a measured budget, not a claimed exact rank certificate.
- The source tuple set is not enumerated in the candidate; only 256 deterministic
  validation prefixes and four suffix columns are evaluated.
- The target batch is fixed-curve and uses the same deterministic 15-target
  stream in both modes.
- The target predicate remains a separate target-specific field computation.

### Evidence so far

- Four matched rows use `p=63311`, `q=63199`, `A=B=14`, and rank 64.
- The shared source-sum cache is exact against the independent direct oracle on
  every sampled value in all four rows and preserves the same row-space rank and
  target stream as the target-separated control.
- At batch width 15, source point additions fall from `273,444-277,552` in the
  target-separated control to `29,732-30,256` with shared source sums, a ratio
  of `0.1087-0.1092`.
- The shared cache retains `28,912-29,428` source sums, with `115,648-117,712`
  logical point-payload bytes and `6,857,928-6,956,736` measured Python bytes.
- Target predicate work still grows with the batch: the final shared rows have
  `530,912-539,108` predicate field multiplications, and reconstruction adds
  `16,711,680` field multiplications per full 15-target batch.
- The `x_interval` row is a sampled-exact positive control for the bounded
  row-space (`0` reconstruction mismatches); `random_x`, `source_prf_x`, and
  `rational_union` retain sampled row-space mismatches. All four have zero
  independent direct-reference mismatches.

### Failure modes

- The cache is a fixed-curve memory tradeoff, not a new single-target
  algorithm. Its logical payload is small here, but Python storage overhead is
  much larger and production bandwidth has not been modeled.
- Row-space reconstruction is still the dominant charged field-work block in
  this sampled implementation; source point-add savings do not establish a
  net rho improvement.
- No full support, relation filtering, quotient rank, individual-log descent,
  success probability, or cryptographic-scale result was measured.
- The source cache is populated by a bounded row-space build and sampled
  validation. A complete compiler still needs a non-enumerative locator and a
  fresh witness-bearing relation path.

### Interpretation

The hypothesis receives a positive fixed-curve batching observation: a shared
target-independent source-sum cache removes repeated elliptic additions across
the tested target batch. This is a practical preprocessing lead, not an
asymptotic ECDLP improvement. The result also sharpens the next bottleneck:
the useful successor must compress or transpose the row-space reconstruction
and then carry the saving through relation rank and target descent.

### Next concrete action

Implement a batched relation transcript over the shared source sums, with
independent quotient-rank and held-out-descent checks, then compare complete
source, predicate, matrix, memory, and rho costs against the target-separated
control.

### Artifact paths

- `src/typed_tt_batched_source_sum.py`
- `src/verify_typed_tt_batched_source_sum.py`
- `tests/test_typed_tt_batched_source_sum.py`
- `development/TYPED-TT-ROWSPACE-BATCHED-SOURCE-SUM-V1/RUN-001/raw-result.json`
- `development/TYPED-TT-ROWSPACE-BATCHED-SOURCE-SUM-V1/RUN-001/verification.json`
