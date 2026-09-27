# SQIsign Round 3 reference signing timing probe — frozen protocol

Frozen before the measurements below were run, 2026-09-27 UTC. This is an
exploratory implementation measurement, not a cryptanalytic result or a formal
ledger status transition. It complements `GOAL-SQISIGN-001` without modifying
that goal. The target is upstream `SQISign/the-sqisign` commit `f417ebd`,
`SQISIGN_BUILD_TYPE=ref`, `CMAKE_BUILD_TYPE=Release`, `p324_3` (level I).

## Mechanism and prediction

The signer converts a secret-derived quaternion ideal to an isogeny. The
`quat_qlapoty_loop_two` search in
`src/quaternion/ref/lvlx/qlapoty.c` increments a candidate `lambda` and exits
when it finds a solution; the surrounding code includes secret-derived inputs.
We hypothesize that its iteration count varies, contributes to signing time,
and might allow a repeated-key observer to distinguish independently generated
keys by signing time alone. The first two claims are source-level and measurable;
the third is a separate, harder claim. Per-signature randomness and other signer
work may mask it. A key distinction is not key recovery or a signature forgery.

## Fixed test and controls

1. First require upstream `sqisign_p324_3_KAT` to pass. Generate eight local
   key pairs using 48 zero bytes as the deterministic test RNG seed. Sign 32
   fixed, distinct 32-byte messages with *every* key, one round per message.
   Shuffle the eight key positions independently each round using an explicit
   fixed-seed xorshift generator, independent of SQIsign's RNG. Make 256 valid
   signatures. Check every signature with `crypto_sign_open`; abort on failure.
2. Record raw monotonic wall-clock signing time in nanoseconds, key index,
   message index, order position, and a nonsecret signature checksum. Exclude
   key generation and verification time. Do not write secret keys. Print
   metadata separately from CSV.
3. Run the same source driver twice with the same deterministic RNG seed: first
   with the pristine library, then with a local-only counter incremented on
   each loop-two iteration. Rebuild the instrumented library. The checksum
   sequence should match between runs; if it does not, flag the comparison
   invalid. The counter measures an internal operation and perturbs time; only
   pristine timing is the externally observable quantity.
4. Assess internal counter variability and its Spearman correlation with
   *instrumented* time descriptively. Assess pristine repeated-key timing with
   a prespecified statistic: Spearman correlation between eight per-key median
   times on rounds 0–15 and eight per-key medians on rounds 16–31. Estimate its
   one-sided permutation probability by 10,000 independent random permutations
   of the held-out key labels, seeded with 20260927, and counting values at
   least as large as the observed value. Also report per-key medians and overall
   time distribution. Roundwise balanced message control and shuffled order
   limit message and drift confounding; they do not eliminate host load or RNG
   correlation. This is exploratory: the result alone does not certify an
   exploitable side channel.

## Stop rules and artifacts

The run ends after 256 signing attempts per build. Abort on failed build, KAT,
key generation, signature, or verification. Do not extend the sample in response
to observed significance. Preserve driver source, local instrumentation patch,
reproduction script, raw CSVs, metadata, exact commands, software versions,
commit and dirty status, timestamps, stdout/stderr, and analysis output. If
failure occurs, save partial files and report it as an implementation failure.

This test cannot infer security of other parameter sets, optimized targets,
production RNGs, remote network timing, or theoretical isogeny-path hardness.
Any positive key-label result calls for independent collection on new keys and
machines, followed by review of leakage-to-key-recovery feasibility.
