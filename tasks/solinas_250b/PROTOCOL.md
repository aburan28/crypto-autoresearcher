# Fixed 250-billion point-observation campaign, 2026-10-12

User authorization: “Do 250 billion.” This expands the descriptive public-point
study from PR2108 using fresh public streams. Source, public inputs, prospective
power and this protocol are committed and pushed before any scientific launch.
No official research status, ECDLP bound, or security claim is changed.

## Exactly what is sampled

256 consecutive points Q+jH per window; measure bit64 of conventional affine x,
all three integer descriptors from the prior study, and the fixed rare events.
Named-curve cohorts use selected H, actual published G, and fresh public rG.
All three use the **same** uniform nonzero starting Q=kG in each matched window.
Ordinary-prime models use uniform affine starts and a fixed public step, not a
certified full-group generator. SHA-counter masking/rejection and arithmetic
remain as in the verified PR2108 sampler; changes bound storage, not the draws.

| Candidate or population | Independent-start windows per cohort/model | Cohorts/models |
| --- | ---: | ---: |
| P-192 selected motif point, threshold integer16199 | 44,389,200 | 3 |
| P-224 selected parity point, threshold integer54 | 44,389,200 | 3 |
| P-224 selected long-run point | 177,556,850 | 3 |
| Ordinary-prime matched models | 1,420,454 | 125 |

There are62 R and63 C ordinary fields: **every** nonsingular, liftable model in
the frozen144 R+144 C P-224 pools. This adds61 coefficient/step-x models to the
prior64, but reuses earlier primes. All controls have A=-3, the standard P-224 B
integer modulo p, and x(H)=2^64+2 with the smaller root. Selection uses no new
event outcome, curve order or step order. PARI exact field primality/cardinality
and separate Python [N]H=O checks are retained in `control-preparation.json`.
Group/step orders are unmatched; N and full model UIDs are in `inputs.json`.

Total: **976,562,500 window observations ×256 =250,000,000,000 point
observations**, based on443,892,000 independent-start draws. Shared starts and
dependence inside a window prevent treating these as250 billion independent or
necessarily distinct points. Old data are not pooled into this fresh study.

Named curve anchors:

- P-192 `urn:ec-record:1:sha256:b4bdde6340ec696e5fa11f3baf1ef941462bc731a526029d2bdc9dc49812aa4b`.
- P-224 `urn:ec-record:1:sha256:e2397ca7cfb5bfad66d0ec042758a09a0ee496e566266b793d2a9f36cf555484`.

Exact p,A,B,N, published G, selected H and point-step hashes remain in the
public input file. Fields are not identified merely by bit length.

## Prospective statistics and impact

20 primary comparisons:3 paired generator contrasts for each motif/parity
candidate (6);3 generator contrasts at each long-run threshold22,28,30,32
(12); and selected P-224 run≥22 versus R and C field-mean rates (2). Generator
tests are exact conditional two-sided McNemar/binomial tests using discordant
paired windows. Field tests are approximate Welch tests, using S-chunk rates
and62/63 field rates as units. Alpha0.0001, per-test0.0001/20: nominal99.99%
family, with an explicit approximation caveat for the two field tests.

One separate30-rate CP interval family covers6 motif/parity marginal rates
plus8 long-run thresholds18,20,22,24,26,28,30,32 ×3 cohorts. Per-interval
alpha0.0001/30; nominal at-least-99.99% under independent windows. Conservative
pair-difference/ratio bounds derive from these simultaneous marginal bounds.
The two families' union is nominal99.98%, subject to Welch approximation. No
old-study family is silently combined. Fair-coin integer-DP probabilities are
benchmarks, not an assumption that point bits are IID.

`power-plan.json` records independent-arm-flag planning alternatives. For the
177,556,850-window long-run cohort, doubling a1e-6 baseline has about99.93%
modeled power at the corrected test alpha. Doubling the fair-coin run32
reference (~5.26e-8) has only about0.104% power. The larger sample does not
resolve every ultra-rare effect. Actual paired dependence changes power; the
exact tests use observed discordance.

A corrected crossing is a replication lead, never a mechanism or security
claim. No crossing constrains only these events and start populations.
Localization to particular starts, alternate coordinates/bits and other joint
statistics remains outside this experiment. Test no interim p-values; finish
the fixed samples before inference. No outcome-based seed selection, stopping
or enlargement. Full orbit coverage is the same for all generators on a
prime-order named curve; the statistics concern its ordering.

## Execution, checks, records and storage

Seed `solinas-250-billion-20261012-v1`; job chunks16,384 windows; workers3.
Per-job streams and source/model/config/storage hashes are fixed at launch.
Every native point is finite/on-curve. Every chunk's complete measured bit
strings independently reproduce all integer scores. Separate Python checks
verify the stored frame inventory, equations, affine recurrence, public start
and random-generator draws, and universal x-triple relations. These are
independent implementations in one session, not a separate research review.

All chunk records are write-once gzip JSON with checksum seals, published by
atomic directory rename. Resume refuses changed source/config/storage or
corrupted records. Only a bounded number of jobs is in flight. Operational
failure stops new scheduling and preserves partial attempts. It establishes
no mathematical failure. A failed attempt is not counted as a completed job.
An external interruption or declared per-invocation chunk count can stop a
process; the global fixed target and seed streams do not change on resume.

**Full compact retention:** selected by `--storage filesystem` or `s3`.
Retain every measured bit string, every exact score, public random-step scalar,
every selected-threshold event frame (all paired arms), fixed witness frames,
first8 run≥28 frames/chunk, invocation/counter/source metadata and stream hashes.
Each lossless chunk ZIP is checked entry by entry. A filesystem copy is reread
and hashed; S3 uses an immutable content-addressed key, server SHA256 and length
confirmation. Only then release this new transfer scratch. Approximately60 GB
is expected; reserve~70 GB for filesystem mode. Non-event full xy streams are
hashes and regenerable seeds, not a stored all-coordinate survey.

**Explicit bounded aggregate retention:** selected only by `--storage aggregate`.
Measure and verify every window, retaining exact event marginal/joint counts,
descriptor sums/squares, source/counter/coordinate/bit/score file hashes and all
chunk validity records. Individual bit strings/scalars are not persisted.
The native engine writes only first8 selected-threshold and first8 run≥28
frames/chunk for checking. Before outcomes, select64 named and64 ordinary
witness jobs by seed hash, and2 example jobs/model. Persist only their
corresponding full frames. This is sufficient for the declared count-based
inference, but not a substitute for the full dataset for later arbitrary ML
feature searches. The storage choice is required and included in the design.

Resource protection: full event files have a32 MiB/chunk bound; encountering
it causes a visible infrastructure stop with partial files, not resampling or
silently changing retention. Scratch admission reserves working capacity; it
is not a research budget or scientific stop rule. Earlier datasets, archives
and receipts are preserved. Existing exposed chat credentials are not embedded
in scripts or source; S3 uses the configured SDK identity.

The parent finishes with exact completion counts, then runs the locked analyzer
automatically. An agent is not needed per chunk or seed. The machine must
remain running; restarts use the identical command and output directory.
Runtime/source versions, commands, compiler stdout/stderr, wall/CPU facts,
failures and unexposed-null model/usage metadata are preserved. CPU estimates
from the prior run are advisory, not speedup or attack-cost claims.

## Launch retention selection, 2026-10-14

The working filesystem has about550 MB free and the managed environment has
no configured AWS outbound identity (current runtime revision128). On
2026-10-14 the user directed “Go”; the announced execution choice is the
prepared bounded aggregate mode when full storage remains unavailable.
Launch uses `--storage aggregate --workers 3`. It measures the complete fixed
target with identical statistics, preserving exact counts and fixed witness
samples, while most individual bit strings/scalars will not be retained for
later arbitrary ML searches. This retention choice is recorded in the immutable
run design before the first scientific draw. Full compact retention still
requires a larger filesystem or configured S3 connection. See the named
[storage obstruction](../../problems/solinas-250b-storage-unavailable.md).
No250-billion scientific observation is claimed before launch.

Publication paths: this task, immutable run metadata, dated report under
`docs/reports/solinas-250b-20261012/`, and a ready PR. Source/results precede
derived report pushes; earlier reports and official frontier states remain
unchanged. Future final reporting uses a fresh directory after full completion.
The current launch report uses `docs/reports/solinas-250b-launch-20261014/`;
the October12 preparation report remains a historical preparation snapshot.
