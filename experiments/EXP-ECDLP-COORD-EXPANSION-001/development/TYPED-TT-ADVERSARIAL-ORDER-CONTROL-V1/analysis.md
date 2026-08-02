# Analysis: TYPED-TT-ADVERSARIAL-ORDER-CONTROL-V1

## Status

`NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

Both alternate schedules were independently rerun and verified. All 12 rows still stopped adaptively and matched their construction counters, but all rows failed full exact validation. The B = 5, 8, and 10 rows discovered apparent ranks 14, 25-26, and 40 instead of the positive-control ranks 15, 36, and 55. The first family rows had 144-151 mismatches for the first relation target and complete or near-complete mismatch counts for later targets; larger rows had thousands of mismatches.

## Interpretation

The plateau rule is schedule-sensitive. The diagonal-first order is exposing a structured prefix subspace that the two alternate schedules do not find before the plateau threshold. This is evidence for source-coordinate alignment, not evidence that the tensor is generically low-rank under arbitrary enumeration.

The control does not rule out a better schedule, a randomized certificate, or a circuit-native construction. It does rule out treating the diagonal schedule as a harmless enumeration detail.

## Next action

Search over source-derived orders and randomized factor-base permutations while recording delayed-independent-prefix failures. Any proposed production schedule must pass both exactness and adversarial-order diagnostics.
