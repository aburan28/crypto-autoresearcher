# Existing pair-cardinality control for the next representation step

This is a post-run reading of already archived and independently reproduced N19 measurements, not a new experiment or an amendment to the SAT pilot. Provenance is internal.

| Base | Signed points | Distinct two-point sums, including infinity | Exact-three covered target orbits |
|---|---:|---:|---:|
| Null[0,1,2,3]|152|11097|5950|
| Selected plane[13,24,28,35]|152|11097|6189|
| Prior/global winner[6,9,22,28]|152|11097|6224|

Source: EXP-KIC-3df18c/RUN-KIC-234d11/independent_replay.json, reproduced independently in research/admissible_affine_factor_base_20260921/review/blind_results.json under `coverage.*.distinct_pair_sums_including_infinity`. The scalar statistics are supported by the frozen N19 coordinate checks; the reviewers' own replay elapsed times are not an additional benchmark.

For these three bases, equal base size and equal pair-image cardinality coexist with different three-point coverage. Pair-image size alone therefore cannot select the best of these three bases. No equality of their full pair-multiplicity histograms, conditional support domains, encoding behavior or solve cost is claimed.

This supplies an existing control for IDEA-20260921-0d2a43, which proposes conditional backward pair-support propagation. If that approved idea is later designed for execution, it should compare conditional support emptiness/forced selectors and complete query cost on these matched-size objects, not attribute a gain merely to having fewer distinct pair sums. Exact target joins can already solve the problem; charge them and keep direct MITM as the comparator.

No new novelty, asymptotic or family-closure claim follows. The current P7 pilot continues to test only its frozen affine-membership encodings.
