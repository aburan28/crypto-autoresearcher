# Grouped recursion and shared-register algebra experiments

Status: experimental; no cryptanalytic speedup claimed.

Source: https://github.com/danadran01/exact-dft-power-saving (Apache-2.0, attribution required for copied code; this experiment copies no source).

## Hypotheses
H1: Grouping independent polynomial-product requests into batches reduces orchestration and repeated transform setup overhead.
H2: Hash-consing identical intermediate polynomial expressions reduces finite-field multiplication and allocation.
H3: Exact convolution kernels improve dense polynomial arithmetic at selected sizes; compare schoolbook, Karatsuba, and NTT where roots exist.
H4: Applying H1-H3 to Macaulay matrix assembly reduces total F4/F5 solve cost, without changing row semantics.

These are analogies inspired by grouped recursion and colour registers, NOT implementations of the paper's asymptotically improved exact complex DFT. No theorem transfers automatically to finite fields.

## Frozen experiment design
- Curves: binary-field m=31, 51, 53, 83; record defining polynomial, curve equation, factor base and solver revision.
- Paired controls: same seeds, input polynomials, matrix ordering, resource limits, hardware and thread affinity.
- Measure kernel latency, allocations, peak RSS, cache hit rate, finite-field operations, preprocessing, relation search, matrix assembly, elimination, verification, failures, duplicates, independent rank.
- Primary metric: total wall-clock seconds per NEW independently verified relation, including failures, setup and rank updates. Also report throughput, p50/p95, memory, and bootstrap confidence intervals.
- Negative controls: randomize subexpression identities while preserving algebraic values; disable batching while preserving arithmetic; sparse versus dense workloads.
- Correctness: exact equality against baseline for random/adversarial inputs, zero and singleton inputs, characteristic-two cases, duplicate products, non-power-of-two degrees; verify all relations on original curves.
- Progression: microbenchmark -> solver integration behind disabled feature flag -> paired end-to-end trials -> independent validator review.
- Promotion: at least 2x lower total time per new independent verified relation versus fastest compiled baseline at larger valid factor bases, with no correctness failures; otherwise retain as negative or scoped evidence.
- Record source commit SHA, source licensing, full commands, immutable receipts and failed runs. Never describe asymptotic DFT result as a demonstrated ECDLP improvement.

## Implementation tasks
1. Identify polynomial multiplication and Macaulay construction entry points in crypto and cryptanalysis repositories.
2. Implement reusable exact polynomial-product batch interface with baseline and grouped backends, including property tests.
3. Implement optional structural DAG interning/common-subexpression sharing with deterministic cache limits and memory counters.
4. Add optional exact convolution backend with field-validity checks and fallback.
5. Wire optional flags into F4/F5 and relation generation; preserve default behavior.
6. Run paired m=31/51/53/83 experiments and publish immutable per-run measurements.
7. Independent validation and red-team review of any claimed speedup.

## Stop rules
Abort an arm after correctness mismatch; report rather than hide negative trials. If memory exceeds baseline by 2x without throughput gain, stop that arm. If microbenchmarks fail to show measurable improvement, do not spend GPU/cloud budget on end-to-end trials.
