# Point-count implementation pilot

Observed 2026-10-16 on the local macOS host, before launching the 79-shard
family-profile campaign. These values are transcribed from the interactive
shell output and are implementation/resource observations, not scientific
acceptance results. The reproducible evaluator and its per-candidate elapsed
times are in `evaluate_candidates.py` and the JSONL records under `raw/`.

| Published prime anchor | PARI `ellcard` seconds | 256 MiB PARI stack result |
| --- | ---: | --- |
| P-192 | 4.569 | order matched OpenSSL |
| P-224 | 13.354 | order matched OpenSSL |
| P-256 | 14.457 | order matched OpenSSL |
| P-384 | 132.77 | order matched OpenSSL |
| P-521 | 631.358 | PARI stack overflow; no count from this attempt |

The initial prime239v1 pilot returned its published order in 15.279 seconds.
The next prime239v2 attempt exhausted the default roughly 8 MiB PARI stack;
that sequence ended without a full prime239 anchor table. These failures say
nothing about the curves' group orders. Ten published prime orders were later
certified independently by the affine-scalar/Hasse method in
`raw/prime_order_certificates.json`.

With a 1024 MiB PARI stack, P-521 candidate index 2 counted in 257.880886
seconds; its exact order and checks are retained in
`raw/evaluations/P-521/00002-00002.jsonl`. The cost and stack behavior of one
candidate need not predict every other candidate, so the full campaign keeps
per-shard watchdogs and `INDETERMINATE` for any failed count.

Binary published-anchor Sage cardinality pilot timings, including field and
curve setup, were 0.814 s (B-233), 0.274 s (B-283), 0.845 s (B-409), and
1.544 s (B-571); all four orders matched OpenSSL. The complete 320 binary
evaluations now provide the durable per-candidate timing record.

No measured speedup, ECDLP advantage, or historical stopping rule is inferred
from these implementation timings.
