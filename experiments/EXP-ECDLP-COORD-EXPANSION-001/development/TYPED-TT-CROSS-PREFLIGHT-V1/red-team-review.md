# Red-Team Review: TYPED-TT-CROSS-PREFLIGHT-V1

## Verdict

Accept as a scoped negative for the tested random-cross construction. Do not call it a lower bound for TT cross methods or for prime-field ECDLP.

## Objections and responses

1. **The rank budget is oracle-guided.** Correct. It comes from the sealed exact factorization and is an explicit pilot input. This makes the test favorable to construction and says nothing about the cost of discovering ranks.

2. **The implementation says non-enumerative while querying the full tensor.** The receipt exposes this directly: every row has unique-query ratio `1.0`. The structural loop avoids `itertools.product`, but charged query work does not improve. The candidate therefore fails its operational non-enumeration bar.

3. **Random cross columns may be a weak pivot strategy.** Correct. The middle-cut rank failures may be repaired by max-volume, source-aware pivots, or shared elliptic fibers. That is the next positive question, not a reason to broaden the result.

4. **The end-cut full-query result is not an asymptotic lower bound.** Correct. It is a consequence of this skeleton formula and the measured near-ambient ranks. Different factorizations or circuit contractions may avoid evaluating those unfoldings.

5. **Holdouts do not prove exactness.** The passing holdouts at cuts 1 and 4 are only consistency checks; the middle cuts failed before holdout validation. A future passing candidate must verify every toy tensor entry and add an independent arithmetic implementation.

## Required follow-up

Use structured pivot selection or circuit contraction, report unique queried tuples before any cached reuse, and require a strict query ratio below one on all three sizes. Preserve the exact-factorization oracle as a diagnostic control and retain the full failure receipt.
