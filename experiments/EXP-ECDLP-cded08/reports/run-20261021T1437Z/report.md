# Fixed public-source witness audit

Observations only; no scientific verdict, performance advantage or ECDLP security claim.

EXP-ECDLP-cded08 (schema-only successor of EXP-ECDLP-ad0ffe), H-ECDLP-51f052, GOAL-ECDLP-001. One trial requested, one completed, zero failed or timed out. RUN-ECDLP-d25f6a passed the independent checker with zero failed checks. Raw records were published first at 7b34b21ff.

Command: `python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-cded08/trial-plan.json --owner executor-prym-witness --epoch 1`. Clean source revision `3d3e2c96cfafa14709af8b526921ba27ba6b7c0c`. Eight frozen fresh curves, three within-curve seeds [0,1,2], 64 public scalars and 64 tuple branches each: 24 cells and 98,304 attempts (derived: 8*3*64*64). The 11 planted/invalid/rank controls matched their expected outcomes. Exact fixture/base IDs, seeds, source/input hashes and dependency versions are in the native manifest.

| p | Curve UID prefix | U | Accepted rows by seeds 0,1,2 | Projected ranks by seeds 0,1,2 |
|---|---|---:|---|---|
| 101 | 0d2d57718ff0 | 0 | 57, 63, 53 | 0, 0, 0 |
| 101 | e305321d608f | 0 | 48, 78, 58 | 0, 0, 0 |
| 211 | 53f0a5d06f1b | 1 | 13, 10, 22 | 1, 1, 1 |
| 211 | dc86a1ba8c12 | 3 | 9, 18, 9 | 3, 3, 3 |
| 431 | 075648ed0f48 | 4 | 0, 1, 2 | 0, 1, 2 |
| 431 | 4b98c364abf6 | 6 | 4, 0, 3 | 4, 0, 3 |
| 4099 | 82e5b5f1902a | 5 | 0, 0, 0 | 0, 0, 0 |
| 4099 | 77b2fb3c4890 | 7 | 0, 0, 0 | 0, 0, 0 |

Entries are measured integer counts from the recorded matrices, modulo each target prime r. Both F101 bases have U=0 because the already-declared public source inputs expose every base log; their 0/0 ranks supply no new unknown-log recovery evidence. The two F211 curves have ranks U in all three seeds. The F431 cells record incomplete ranks. Every F4099 cell records zero accepted rows. Seeds are repeated measurements within a curve, not 24 independent curves. No confidence intervals or asymptotic exponent are reported.

Recorded accepted rows total 448 (derived sum of the table). Every accepted row has an independently checked explicit principal-function certificate, public E1 source equation and auxiliary E2 norm cancellation; the checker independently recomputed all ranks and verified any full-rank recovered base logs. Transported atom reencodings were checked by the producer. Independent verification covers accepted witnesses and event coverage, not replay of every rejected branch. This limitation remains explicit.

![Exact recorded projected rank and U, RUN-ECDLP-d25f6a](graph.svg)

Measured producer wall 9.407047016 s; CPU 9.402666941 s; peak self RSS 43,618,304 bytes. Checker wall 0.628591363 s; CPU 0.628588297 s; peak self RSS 145,575,936 bytes. Host: Linux x86_64, Python 3.12.14. Full environment is in environment.json. Native RLIMIT_AS is 2 GiB; process-group peak sampling was not provided.

Raw field calls, group additions, hashes/cache events and matrix updates remain separate units. Pow internals, Python bookkeeping and independent verifier operations are not included in the attack operation vector; wall time includes the producer checks. No complete weighted S cost or comparison to the best IC pipeline was measured.

The finite constructor stream has not supplied full unknown-column rank on the complete fixed panel. This observation limits this tested stream only. Selector-stage benefit and blind complete recovery remain conditional on the preregistered source/rank and matched-cost gates. No mathematical impossibility or deployed-curve security statement follows.

[Immutable run and exact attempts](../../runs/RUN-ECDLP-d25f6a/). Graph source contains recorded counts only; the PDF was opened and inspected before this report was published. No canonical scientific-evidence graph changes follow from an execution-only report.
