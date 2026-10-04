# Native orbit-canonical pair lookup: finite N19 result

The primary x-only orbit-canonical implementation completed every fixed target correctly and used **0.750927 times the expanded table's cold native-process wall time** on the preregistered statistic. This is **24.91% less time**, or a **1.332-fold speedup**. The descriptive stratified bootstrap 95% interval for the ratio is **[0.655143, 0.864423]**. The required threshold was a ratio at most 0.80 with an upper endpoint below 1.

This comparison fixes the curve, factor base, targets, native binary, arithmetic, and witness-verification rules. It concerns finite point decomposition on one host. It is not a new full index-calculus-versus-rho measurement.

## Fixed mathematical object and timing panel

The curve is K1 over F2^19, using the field polynomial z^19 + z^5 + z^2 + z + 1 and prime subgroup order 262543. The previously accepted affine-orbit base has 152 signed points, 76 x-values, and four effective Frobenius columns. Its seed x-set is

    12009 + span_F2{257473, 353192}
    = {12009, 246568, 347457, 434304}.

Field addition in that expression is XOR. The base includes both point signs over every Frobenius conjugate of the seed set. Every implementation represents exactly the same pair-sum set and exact-three-point relation.

There are eight fixed public target cases: four decomposable and four nondecomposable. Each method has six fresh-process technical repetitions per target, with all six method orders represented. These are technical repetitions on eight targets, not 144 independent target samples. The cases also appeared in the preceding SAT pilot; this is not a fresh target holdout.

| Native implementation | Table keys | Pair additions to construct anchors | Median process wall | Median CPU | Median peak RSS |
|---|---:|---:|---:|---:|---:|
| Expanded pair table | 11,097 | 11,628 | 9.7260 ms | 6.0745 ms | 2,818,048 bytes |
| Full-point canonicalization | 293 | 380 | 7.3718 ms | 4.3805 ms | 1,851,392 bytes |
| Normal-coordinate x-only canonicalization | 293 | 380 | 7.4814 ms | 3.7560 ms | 1,867,776 bytes |

These are marginal medians over 48 processes per method. They do not define the primary ratio: the frozen rule first takes six-repeat medians for each case and method, then the median of the eight paired case ratios.

Full-point canonicalization has a descriptive paired ratio of 0.784478 versus expanded. X-only versus full-point has a paired ratio of 0.949354 and interval [0.805296, 1.092471], so this panel does not establish x-only as faster than full-point. X-only was selected as the primary candidate before timing. Seven of its eight case ratios are below 1; one is 1.039978. The result is not a speed guarantee for every target.

## Construction, query, and memory

The gain comes mainly from construction. The expanded table's median internal build is 2.854396 ms; x-only is 0.601959 ms, plus 0.041667 ms for fresh normal-basis and nibble-map preparation. Median query, transport, and replay cost is 0.034479 ms for expanded and 0.036980 ms for x-only. These separate stage medians are not additive and do not replace whole-process wall. Full-point query and transport has a median of 0.096834 ms.

The expanded comparator is a compact inline key-to-pair-index map: an 8-byte key and a 4-byte value. Each canonical value uses 48 bytes for normalized points and transport metadata, plus its 8-byte key. Logical key/value payload is **133,164 bytes versus 16,408 bytes**, an **8.116-fold reduction**. That count excludes map buckets, node allocations, runtime storage, and allocator overhead. Measured x-only median process RSS is about 66.3% of expanded; it is not an eightfold RSS reduction.

Each canonical hit retains a real pair witness. The query's Frobenius shift and sign are inverted, and the recovered points must belong to the original base and sum exactly to the original residual. The x-only method restores y/sign alignment after the key hit. A matching orbit key alone is never accepted as a decomposition. Direct polynomial squaring performs inverse transport in this implementation; no post-result optimization was applied.

## Controls and independent review

The native controls check all 524,288 field elements for normal-conversion roundtrip and Frobenius rotation, 4,457 field products, 4,096 group batches, and every stored table witness. Both 293-key tables agree with the 11,097-point expanded pair-sum set across **all 262,543 subgroup points**.

All 6,909 target orbits agree on **6,189 exact-three successes and 720 absences**, including first-hit third-point indices. There are also 153 separate infinity/base-point queries: all 152 base-point queries succeed, while infinity does not. Controls reject corrupted shifts, signs, keys, stored sums, off-curve inputs, and noninvariant bases. A separately written Python checker passed before benchmark admission.

All 144 benchmark processes completed correctly, without a fault, censor, watchdog, memory-cap event, or fast-exit registration-race recovery. The scientific snapshot is `c7f01acd95478bcbb4cf3c799f8b251d019d89c9`, binding 46 paths. The raw archive contains 589 hash-bound files.

The source-aware Validator and a separate permanently blind Validator independently reconstruct the pair tables, membership and witness transport, and reproduce the frozen timing statistic. Their reports are `review/source_report.yaml` and `review/blind_report.yaml`; the blind calculation is retained in `review/blind_results.json`. The canonical independence checker exits 0 with PASS for both owned joints, declared blindness, and controls. Coordinator decision `DEC-20260921-c084cb` accepts only this finite positive measurement; hypothesis and goal statuses remain unchanged, and knowledge promotion is deferred. The review setup uses independent sessions from the producer and discloses that adapter serving-model probe metadata is older configuration, not a fresh probe.

## Measurement boundary and limits

Primary wall runs from direct native-process launch through event-driven exit notification and sole `wait4` reap. It includes startup, input, base construction and validation, fresh normal conversion where used, table construction, query, witness recovery, verification, and output. There is no Python worker inside this boundary. It is therefore not directly comparable with the preceding SAT pilot's approximately 48.5 ms Python-wrapped native median; no old timing is subtracted.

The measurement loop uses `kqueue NOTE_EXIT` rather than periodic millisecond polling. No worker reached a 50 ms footprint sample, so sampled footprint remains unavailable; `wait4` peak RSS is present for every worker. No operating-system cache flush, thermal or background-load invariance, or portable execution environment is claimed.

The 144 native worker intervals sum to **1.2059595 seconds**. The entire benchmark supervisor took **4.104262292 seconds**, including source and input checks, parent validation, hashes, and archives. Native-control supervisor wall of 6.314426791 seconds and independent-checker supervisor wall of 50.473086041 seconds are validation costs, not per-query solve times. Compilation and reviewer work are separate. Supervisor and child CPU/RSS scopes overlap and are not added together.

The fixed eight-case bootstrap describes this technical-replication panel. It is not a confidence claim about arbitrary targets, other bases, larger fields, or future hosts. No asymptotic, novelty, or security conclusion follows.

## Next decision and publication

A cold single-target IC job can build its table once and reuse it across relation attempts for that same target. This experiment charged fresh construction to every query. Its construction savings therefore cannot be multiplied by the number of relation attempts; per-query canonicalization still has to be paid. The next design should freeze that within-job reuse boundary and a larger finite parameter or representative base, then compare complete costs against the expanded method. The existing full IC/rho gap remains unchanged.

The supporting cost-model boundary is in `REUSE_SCOPE_NEXT_ACTION.md`. This report and all cited experiment/review evidence have internal provenance. They are locally committed research records. Automatic approval review rejected public GitHub export because experiment authorization did not authorize publication of the branch's full payload. No push, PR creation, or indirect export has occurred.
