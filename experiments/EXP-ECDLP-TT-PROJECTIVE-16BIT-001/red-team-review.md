# Red-team review: 16-bit projective shared-sign sweep

## Scope

This review checks whether the 16-bit result supports a scale claim or only a scoped arithmetic observation.

## Checks

- **Independent verification:** `RUN-TT-PROJECTIVE-16BIT-002` is valid with 64 checks and no failures. It regenerates both curves, reconstructs projective source states, checks homogeneous scaling and support, validates witnesses, weighted comparator rows, relation metadata, and rho.
- **Full correctness versus rank:** full candidate support and witnesses pass, but candidate relation ranks are `11-13/15`. Full support is therefore not evidence of a complete relation compiler at this size.
- **Sub-full gate:** neither `64` nor `96` passes on either family or curve. The 14-bit `source_prf_x` budget signal does not replicate at 16 bits.
- **Arithmetic accounting:** projective field multiplications and inversions are lower than both comparators in all cells and all inversion weights. Point additions are essentially unchanged versus naive and higher than original; cache bytes are higher. Weighted advantage is therefore real only in the declared arithmetic model, not an end-to-end wall-clock or memory-bandwidth result.
- **Negative control:** `random_x` follows the same full-support/rank failure pattern and receives no post-hoc selector tuning. It remains a meaningful control, but the experiment does not claim that the candidate family is uniquely responsible for the arithmetic advantage.
- **Downstream boundary:** relation equations, matrix operations, witness operations, and rho are recorded. Individual-log descent and cryptographic-scale matrix elimination are absent and remain open gates.

## Verdict

Retain as a mixed positive arithmetic signal and a scoped negative result for the 16-bit sub-full/rank gate. Do not promote it to an index-calculus improvement. The projective operator should be reused only inside a rank-preserving selector or compressed row-space construction.

## Required successor controls

1. Require full target-matrix rank before any larger field-size escalation.
2. Test source-aware class orders and a projective-aware row-space basis without target or relation selection leakage.
3. Charge physical cache bandwidth and sparse matrix elimination, not only logical operation counters.
4. Keep `random_x` and one intentionally rank-deficient family as negative controls.
