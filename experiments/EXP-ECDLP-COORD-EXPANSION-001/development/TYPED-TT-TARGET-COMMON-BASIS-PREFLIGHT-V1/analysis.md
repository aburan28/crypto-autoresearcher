# Analysis: TYPED-TT-TARGET-COMMON-BASIS-PREFLIGHT-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The two-target stacked rank census completed for all 12 curve/factor-base rows, using the first relation target and the first held-out target. Every enumerative tensor and modular-rank replay verified exactly, and all duplicate/independent synthetic controls passed.

The main signal is asymmetric:

- At cut 3, the stacked **row-union rank** stayed equal to the single-target rank on all 12 rows: `15/14` for B=5, `36` for B=8, and `55` for B=10. This is a concrete target-sharing signal for the source-prefix side.
- At cut 3, the stacked **column-union rank** increased to `28-30`, `72`, and `110`, respectively. The complementary target-dependent side therefore expands substantially.
- At cut 2, row-union rank was often close to the two-target ambient: `30-35` for B=5, `96` for B=8, and `218-220` for B=10. This cut does not show stable two-target sharing at larger B.
- Cut-2 column-union ranks were `34-35`, `48`, and `110`, also approaching ambient for the larger rows.

The full run used two target tensors per row, took approximately 35.7 seconds, and used approximately 58 MiB peak RSS. All tensor construction and rank work was enumerative and charged as diagnostic work.

## Interpretation

This is a positive but narrow fixed-curve preprocessing signal: a source-prefix row space at the third cut may be reusable across target specializations. It is not a compact full TT basis because the complementary column spaces grow, and it does not establish that the shared row basis can be generated from the RCB circuit without tensor enumeration.

The result supports a focused constructive question: can one precompute a target-independent cut-3 prefix basis once, then specialize the remaining target-dependent operator with less advice and online work than independent target tensors? The answer is still `OPEN`.

## Next action

Implement a target-specialization receipt that constructs the shared cut-3 prefix basis once, stores only its charged basis/core traffic, and verifies exact reconstruction for additional held-out targets. Compare against independent per-target factorization and report fixed-curve offline work, retained advice, memory bandwidth, target count, success probability, and individual-log relevance.
