# Acceptance-specific point-count pilot

Recorded before running this pilot. The first exact P-256 shard, blocks 1–20,
completed with `ellcard` under host load. Test PARI `ellsea(E,tors)` at
`tors=product(primes at most 255)` on the published-compatible coefficient of
blocks 3, 8 and 12, where a nonsingular seeded curve and exact `ellcard` order
are already recorded in `raw/x9/P-256/00001-00020-retry1.jsonl`. Use the same
root as that record. Compare every nonzero SEA result to the exact order;
record zero as an early abort, not as a curve rejection or an exact count.
Keep GP version, command, input hashes, stdout, stderr, elapsed time and all
three outcomes. This is a performance/compatibility pilot only; a faster
method needs an independently justified treatment of zero cases before it
can replace exact counting in the full X9 reference study.
