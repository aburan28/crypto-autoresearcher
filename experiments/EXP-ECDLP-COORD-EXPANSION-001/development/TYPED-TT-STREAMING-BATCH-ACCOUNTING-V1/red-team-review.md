# Red-Team Review: TYPED-TT-STREAMING-BATCH-ACCOUNTING-V1

## Verdict

Accept as verified fixed-curve target-batching evidence. Do not promote it to an asymptotic ECDLP result.

## Checks

1. The loop order is explicitly prefix, target, suffix, and every batch uses full validation.
2. Prefix recomputation is counted and equals the number of prefix fibers, demonstrating actual state reuse.
3. The full batch contains all eight relation targets and all supported held-out targets; direct arithmetic and witness replay are checked independently.
4. Advice construction, adaptive construction, source reads, target operations, and direct-reference operations are included in the charged ratios.
5. The lexicographic control preserves arithmetic exactness while reproducing the schedule-sensitive failure.

## Remaining objections

- Python object size remains an implementation-specific memory proxy.
- The target pool is inherited from a toy fixture; it is not an independent success-probability estimate.
- The relation matrix and individual-log solve are replayed/bound through fixture data, not newly generated end to end here.
- The measured batch gain is a small constant-factor effect and has no larger dimension sweep.
- Cache, allocator, and hardware bandwidth effects are not represented by logical payload counts.

## Required follow-up

Add an independent relation-matrix and target-coefficient accounting receipt, then generate larger source-dimension fixtures and repeat the same balanced/full batch schedule with a matched materialized-D4 and rho baseline.
