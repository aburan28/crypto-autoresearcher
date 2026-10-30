# Final consistency and custody checks

2026-10-25, TASK-20261025-6d88b2. This supplements the write-once main command record.

Read `independent-results.json` directly to check derived counts and actual checkout HEAD. This exposed the two prose transcription issues corrected in `review-correction-01.md`: 20 independent cyclic enumeration cases; actual HEAD 2c8c71cfff6f7f63297fbe4de4608cd94d857184 differs from the exception's payload-base commit. A direct filesystem check confirms `/usr/local/bin/python3` is absent. Render stderr records cache/font warnings while the render process exits 0.

The sealed ZIP exists, has 3,128,627 bytes and SHA-256 `31d35a0cf3c2977e56c84d3bcd23fe730c8ee396a3de6eda009c8c08a7c0d28a`, matching the custody exception. The first `finalize_review.py` invocation exited 1 because it incorrectly required `baseline/parameters.py` in this **delta** archive. Its exact source is preserved as `finalize_review-attempt1.py`, with `finalize-attempt1.stdout` and the full traceback in `finalize-attempt1.stderr`. No result.json or manifest had been written at that failure point.

The only absent requested archive member is the committed baseline. A read-only `git show HEAD:research/p256_factor_base_parallel_20261025/baseline/parameters.py` and the corresponding `git show c35b9da6a65e019eaa517fc1a5f7774428ff35db:...` both return exactly the local baseline bytes and SHA-256 `cd7723bdeac329e745a98355ba518f9141b7be95a8fb50e34c6edcb87ccbd856`. Finalization now explicitly distinguishes that unchanged committed baseline from ZIP-contained inputs. This is a custody check, not satisfaction of the normal committed-and-pushed requirement for the whole review input set.

Second invocation:

```text
/workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261025/reviews/relations_and_bounds/finalize_review.py > research/p256_factor_base_parallel_20261025/reviews/relations_and_bounds/finalize.stdout 2> research/p256_factor_base_parallel_20261025/reviews/relations_and_bounds/finalize.stderr
```

Its outcome is recorded in those complete stdout/stderr files and the write-once `result.json`. Finalization checks every listed ZIP member byte for byte, the baseline against both Git revisions, XML parseability of both SVGs, empty scientific checker stderr and final artifact hashes. It does not execute a scientific trial or modify Git. The quantitative SVG exceeds the preferred 64 KiB by 12.6 KiB; all Markdown, code, JSON and text logs remain below 64 KiB, and the vector is far below the repository's non-code size limit. The smaller scope diagram is also available for compact rendering. PDF rendering and visual inspection are assigned to the coordinator.
