# Rejected PARI acceptance-specific pilot

On 2026-10-16 the command
`python3 research/nist_seed_followthrough_20261016/pilot_tors.py` stopped at
P-256 block 3 before writing an output JSON. The shell invocation returned
exit code 1. PARI 2.17.3 returned process code 0 but wrote this error to
stderr when passed the product of all primes at most 255 as `ellsea`'s
`tors` argument:

```text
***   this should be a small integer: ...95533631308867097853951),
***   642663309179086448723
***   ^---------------------
```

The exact attempted script is [pilot_tors.py](pilot_tors.py), specified by
[AMENDMENT_1.md](AMENDMENT_1.md). No `ellsea` point-count result was produced.
The earlier twenty-block `ellcard` run had a separate GP one-line parsing
failure retained as `raw/x9/P-256/00001-00020.jsonl`; its corrected retry is
`raw/x9/P-256/00001-00020-retry1.jsonl`. Neither failure classifies a curve.

This pilot establishes only that this PARI interface rejects the proposed
large `tors` value. The complete exact X9 reference still uses `ellcard`.
