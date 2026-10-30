# Correction to the local review prose

2026-10-25 UTC, TASK-20261025-6d88b2. This dated addendum preserves the write-once `review.md`; read them together. The checker outputs were correct and remain unchanged.

1. The F4 small-prime exhaustive counting panel contains **20** cases, not the 21 stated in the “Inference and limits” paragraph. The exact case list in `independent-results.json` is authoritative. The producer's earlier panel has 18 cases; this independent panel includes two additional degree-seven cases.
2. The custody exception identifies **c35b9da6a65e019eaa517fc1a5f7774428ff35db** as its payload base commit. The actual checkout HEAD reported by this review's executed checker is **2c8c71cfff6f7f63297fbe4de4608cd94d857184**. The phrase “local base” in `review.md` must be read as the exception's payload-base field, not an assertion that checkout HEAD equals that field. This difference is retained as a custody limitation, and neither value satisfies the absent committed-and-pushed-input prerequisite.
3. The fixed `/usr/local/bin/python3` path was subsequently checked directly and is absent. Chart rendering exited successfully but emitted Matplotlib/fontconfig warnings about a read-only home cache; those warnings are retained in `render.stderr`. They do not occur in either scientific checker stderr, which are both empty. No chart warning was suppressed or treated as a mathematical result.

These corrections change no certificate result, F3 finding, rank, root count, determinant, capacity threshold or scope conclusion. No producer artifact or prior review file was modified. The coordinator will render and inspect the report and this correction through its common PDF pipeline.
