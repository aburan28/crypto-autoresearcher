# Analysis: TYPED-TT-ADAPTIVE-SKELETON-PREFLIGHT-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The adaptive source-prefix constructor used no exact-rank input. It stopped after a dependent-prefix plateau and discovered ranks `14/15` for B=5, `36` for B=8, and `55` for B=10 on all 12 rows. It examined only `18-19`, `40`, or `60` prefix fibers out of `175`, `384`, or `1,100` total.

Construction query ratios were `0.0545-0.1086` of a full tensor; target specialization remained `0.55-0.60`. The actual construction oracle counters matched the recorded query counts, and all eight relation targets plus the first held-out target reconstructed with zero mismatches. The full run took approximately 38.3 seconds and used approximately 51 MiB peak RSS.

## Interpretation

This removes the strongest artificial assumption in the previous source-aware result: the exact rank budget is no longer supplied by the rank oracle. On the frozen toy rows, a simple plateau certificate found the right rank and preserved exact target specialization.

This is still a representation-level result, not an ECDLP improvement. The stopping rule is heuristic and validated only after full tensor replay; the construction uses direct affine oracle evaluations rather than a circuit-native RCB compiler; persistent advice, memory bandwidth, relation rank, target descent, and rho comparison remain uncharged. A later independent direction after the plateau would be caught by validation but would invalidate the adaptive construction claim for that row.

## Next action

Replicate the adaptive rule on fresh ordinary prime-field curves and adversarial prefix orders, then connect the discovered skeleton to the existing typed relation/descent verifier. Promote only if adaptive discovery remains exact with full fixed-curve offline/online accounting.
