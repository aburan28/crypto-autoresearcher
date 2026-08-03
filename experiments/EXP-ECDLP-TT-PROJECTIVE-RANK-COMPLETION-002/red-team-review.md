# Red-team review: second 16-bit projective relation-batch rank completion

## Scope

This review checks whether the second curve supports a robust rank-completion claim or only a candidate-family toy signal.

## Checks

- **Independent verification:** `RUN-TT-PROJECTIVE-RANK-COMPLETION-003` is valid. It regenerates the fixture, verifies source hashes, reconstructs projective source states, checks homogeneous zero-equivalence, validates support and witnesses, checks target count, weighted comparator rows, matched rho, and the immutable memory receipt.
- **Rank:** `source_prf_x` reaches `15/15`, but `random_x` reaches only `13/15`. The result therefore does not support a family-independent claim that `2B+1` targets restore rank.
- **Support and held-out targets:** full mode passes exact support and held-out witnesses for both families. Neither `96` budget passes the strict acceptance list: `source_prf_x` loses held-out support and `random_x` remains rank-deficient.
- **Arithmetic accounting:** projective weighted cost beats both affine comparators in all two family cells and all four registered inversion weights. This is a declared arithmetic-model result; point additions, cache bytes, bandwidth, matrix work, and descent are not collapsed into it.
- **Resources:** peak RSS is `6,184,501,248` bytes against a `6,442,450,944` byte limit. The result is within contract but leaves little headroom for larger fields or additional controls.
- **Controls:** `random_x` uses the same expanded target transcript and was not tuned after observing rank. Matched rho solves all targets. The control failure is evidence against a universal rank-completion mechanism, not evidence that the candidate is a break.

## Verdict

Retain as a mixed positive candidate-family signal and a scoped negative for family-independent rank completion. Do not promote it to an index-calculus improvement, a fixed-curve preprocessing win, or an ECDLP break. The uncompressed `2B+1` scan should not be escalated without reducing memory or compressing the relation construction.

## Required successor controls

1. Keep `random_x` as a mandatory negative control and add a second source-derived family if a selector is introduced.
2. Require full rank `15`, held-out support, and memory compliance before any larger-field run.
3. Measure sparse linear algebra, relation filtering, and target descent explicitly.
4. Compare a source-aware selector or compressed row-space basis against the full `2B+1` scan without target-dependent selection.
