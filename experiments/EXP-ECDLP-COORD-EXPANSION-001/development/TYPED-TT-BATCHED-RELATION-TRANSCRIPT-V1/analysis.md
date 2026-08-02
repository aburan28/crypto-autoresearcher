# Analysis: TYPED-TT-BATCHED-RELATION-TRANSCRIPT-V1

## Handoff: batching bound to typed relations

### Claim or task

Carry fixed-curve shared source sums through exact row-space witness
generation, materialized-D4 support comparison, and quotient relation-basis
insertion.

### Status

OBSERVATION, TOY-EVIDENCE, MODEL-BOUND

### Assumptions

- The input is the committed fresh-seed generated fixture and the experiment
  uses only the smallest curve, `recursive-toy-p947-a659-b11-q971`.
- The candidate uses adaptive cut-3 row-space reconstruction and scans every
  predicted suffix column, but obtains source values only through build and
  pivot queries; it does not materialize the typed D4 tensor.
- The shared and target-separated modes use identical target streams and
  adaptive row-space construction.
- Materialized D4 is an independent support and witness baseline, not attack
  advice.

### Evidence so far

- Four coordinate families all pass direct predicate-reference checks, exact
  candidate witness replay, and candidate-versus-D4 `a_index` support equality.
- Shared and target-separated row-space ranks agree at 15 in all four rows.
- The six generated relation targets plus four supported held-out targets
  reach quotient rank `6/6` in all four rows, and the recovered solution
  digests match the fixture's independent post-hoc diagnostic solution digest.
- Every held-out expected witness replays and appears in the candidate hit set.
- Width ten source point additions fall from `29,940-29,960` in the
  target-separated control to `3,165-3,185` with shared source sums, a ratio
  of `0.1057-0.1063`.
- The shared cache retains `2,815-2,835` source sums, `11,260-11,340`
  logical point-payload bytes, and `647,060-654,344` measured Python bytes.
- The candidate predicts `26,250` suffix entries per row across the six target
  transcript, while relation rank remains far below the quotient width. This
  is exact witness-bearing toy evidence, not a solved relation system.
- Independent verifier receipt is valid and the promotion gate remains false.

### Failure modes

- The full quotient rank here is a small toy rank on one 10-bit curve. The
  solution digest is matched to a post-hoc diagnostic census record, not
  presented as a deployed-key recovery or an independent logarithm attack.
- Source point-addition savings are not total attack savings: target predicate,
  row-space reconstruction, matrix, target descent, cache bandwidth, and
  materialized-baseline costs remain separate.
- The largest curves were intentionally excluded after the dense full
  predicted-suffix run exceeded a bounded execution budget; this package is a
  smallest-curve family control, not a scale result.
- Full predicted suffix scanning remains expensive and the row-space itself is
  still an imported exact toy construction. A non-enumerative locator is open.

### Interpretation

The fixed-curve batching signal survives the witness, held-out coverage, and
small quotient-relation layers for the smallest committed curve: source sums
can be reused without changing support, diagnostic solution, or rank. The
experiment still exposes the real next gate. The method must accumulate rank
on fresh larger curves without proportional source work and compress the
predicted suffix operator before any ECDLP relevance can be assessed.

### Next concrete action

Use a held-out-target transcript and independent sparse matrix/descent replay
to test whether the shared operator can accumulate rank without increasing
source-point work proportionally; compare all charged costs with the existing
typed D4 and Pollard-rho baselines.

### Artifact paths

- `src/typed_tt_batched_relation_transcript.py`
- `src/verify_typed_tt_batched_relation_transcript.py`
- `tests/test_typed_tt_batched_relation_transcript.py`
- `development/TYPED-TT-BATCHED-RELATION-TRANSCRIPT-V1/RUN-001/raw-result.json`
- `development/TYPED-TT-BATCHED-RELATION-TRANSCRIPT-V1/RUN-001/verification.json`
