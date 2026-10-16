# Frozen design: m=51 conductor-271 volcano rho comparison

Frozen on 2026-10-13 before any m=51 rho outcomes were measured. Status:
**designed, not launched**. The exact machine-readable contract is
[`spec.json`](spec.json); the exact crater and 16 floor-orbit representatives
are in [`sample.csv`](sample.csv).

This is a bounded collision-walk experiment. It is not an isogeny-transfer
trial, a sealed ECDLP bound, an end-to-end attack-cost result, or evidence that
either level is weak.

## Requirement-to-evidence plan

| Requirement | Frozen evidence or gate |
|---|---|
| Compare every volcano level available in this m=51 slice | One certified crater model and one representative of every one of the 16 Frobenius orbits on the conductor-271 floor |
| Compare sampled levels while holding the implemented signed action fixed | Primary `floor-tau17 / crater-tau17` same-action contrast; this is a level/model association, not causal isolation of conductor |
| Retain ordinary rho controls | Matched `floor-neg / crater-neg` contrast |
| Test structural action predictions | Three quotient contrasts with predictions `+2.043731`, `-0.792481`, and `-2.836213` bits |
| Pair targets and algorithms | The same planted scalar `k` in all five arms of each target block; setup/target/walk seed namespaces frozen separately |
| Cover the floor without orbit pseudoreplication | All 16 floor orbits, exactly 192 inferential blocks plus 64 inferentially held-out A/A blocks per orbit |
| Account for implementation work | Separate per-target setup, online walk, group additions/doublings, canonicalizer field primitives, restarts/cycles, and descriptive seconds |
| Detect harness drift | An independent-walk A/A replicate for all five arms on a fixed 1,024-block balanced subset |
| Verify correctness | Exact subgroup/action self-tests plus recovered-scalar and `kP=Q` verification for every target; any failure invalidates the affected run |
| Quantify uncertainty | Fixed 50,000-draw paired bootstrap within each of the 16 exact sampled-orbit strata; orbit-resampling bootstrap retained only as a superpopulation sensitivity |
| Avoid an unsupported weakness claim | No transfer, scaling, security-bit, or weak-curve conclusion is permitted by this protocol |

## Exact mathematical objects

Work in

`F = GF(2)[z] / (z^51 + z^6 + z^3 + z + 1)`

with models

`E_b: y^2 + x*y = x^3 + b`.

The isogeny class has trace `t=-38,684,515`, ambient order
`#E(F)=2,251,799,852,369,764`, and prime subgroup order
`r=17,192,986,687` (`log2(r)=34.001101...`) with cofactor `130,972`.
Its Frobenius discriminant is

`Delta_pi = t^2 - 4*2^51 = -7*(271*120871)^2`,

so `D_K=-7` and `f_pi=32,756,041`. The crater model is `b=1`,
`f_E=1`. The sampled lower level has `f_E=271`, 272 curves, and 16
Frobenius orbits of size 17. `sample.csv` uses the least integer encoding in
each orbit as its exact representative; no post-outcome curve selection is
allowed.

The floor inventory comes from
`research/ecc2k130_conductor_isogenies_20261007/m51_m53/` at introducing
revision `f0bdf9f739462766a9060532c59f9bfed69d00b1`. The complete CM floor has
272/272 models of the required ambient order, and 40 explicit kernel-route
images were independently cross-checked inside it, reaching 14/16 orbits.
Those construction facts identify the level; they do not measure rho work.

### Trace-zero context is not a level difference

Every sampled floor coefficient lies in `GF(2^17)`, and the crater is defined
over `GF(2)`, hence also over `GF(2^17)`. The curve order over the subfield is
`130,972`; the order-`r` component over `GF(2^51)` therefore lies in the
degree-3 trace-zero subgroup. This observation applies to the crater as well
as the floor. It may motivate a separate representation experiment, but it
cannot explain a floor-versus-crater difference in this protocol and is not
counted as a discovered advantage.

## Five paired arms

| Arm | Curve level | Core mode | Signed action | Action order |
|---|---:|---:|---|---:|
| `crater-neg` | `f_E=1` | 0 | negation | 2 |
| `crater-tau51` | `f_E=1` | 1 | native `tau` | 102 |
| `crater-tau17` | `f_E=1` | 2 | `tau^17` | 6 |
| `floor-neg` | `f_E=271` | 0 | negation | 2 |
| `floor-tau17` | `f_E=271` | 2 | `tau^17` | 6 |

Mode 1 is admissible only for the exact crater. Mode 2 must verify that the
curve coefficients are fixed by the seventeenth-power Frobenius and that the
subgroup eigenaction used to update rho coefficients is exact. `tau` and
`tau^17` are inseparable endomorphism actions, not separable volcano edges.
The frozen core sources are `rho.c` SHA-256
`f86cf62f8c0bf6ea9bb35e5358e0aec99f995db5779b0cf179d1b896d7cb9327`
and `params.h` SHA-256
`cb3790db6122996da89b260a6bd57301b02f5f96760fe80caacb795b3bef18b2`.
Compile with `gcc -std=gnu11 -O2 -Wall -Wextra -Wconversion -Wshadow
-mpclmul -msse4.1`; record the compiler version, binary hash, CPU features,
host, affinity, command, stdout, stderr, and every exit status before accepting
the run.

The primary same-action sampled-level/model comparison is

`B_primary = log2(mean(W_floor-tau17) / mean(W_crater-tau17))`,

where `W=walk_ops`. Its random-map comparison prediction is 0 bits because
the two arms use the same signed action. This comparison still bundles the one
chosen crater model, the sampled floor models, generator construction, and hash
behavior; it does not isolate conductor as a causal variable. The four
secondary contrasts are:

| Ratio (numerator / denominator) | Predicted rho-work bits |
|---|---:|
| `floor-neg / crater-neg` | 0 |
| `floor-tau17 / crater-tau51` | `+0.5 log2(17) = +2.0437314206` |
| `floor-tau17 / floor-neg` | `-0.5 log2(3) = -0.7924812504` |
| `crater-tau51 / crater-neg` | `-0.5 log2(51) = -2.8362126710` |

`crater-tau17 / crater-neg`, predicted `-0.7924812504` bits, is retained as
an additional diagnostic but is not added to the four-comparison secondary
family.

## Frozen workload and pairing

There are 4,096 executed A-stream target blocks. Blocks `0..255` use floor orbit 1,
blocks `256..511` orbit 2, and so on. Thus every floor orbit has exactly 256
blocks. Within a block, all five arms use the same planted scalar `k`, derived
only from the target root seed and block ID. Each arm constructs its own
verified subgroup generator and `Q=kP`; equality of the scalar—not equality
of curve points—is the cross-curve pairing.

Jobs contain 64 consecutive targets. A single seeded shuffle orders all jobs;
at most four pinned workers may run concurrently. This prevents an entire arm
or level from occupying only one time segment. Seconds remain descriptive
because the environment is not claimed to be isolated.

The fixed A/A holdout contains the first 64 blocks within every orbit: 1,024
blocks total. These A-stream blocks are excluded from all level/model
contrasts, bootstraps, and arm summaries. Each of their five records is label
A. Label B repeats the
same curve, action, scalar, setup seed, and target seed with the independent
A/A walk seed. This adds 5,120 records. The complete frozen workload is
therefore 20,480 A-stream plus 5,120 A/A B-stream records, or 25,600 solves.
Within-orbit offsets `64..255` supply the 3,072 inferential blocks (192 per
orbit); offsets `0..63` supply the disjoint 1,024-block A/A gate. The A/A
records are a harness/randomisation control, not extra evidence for a sampled
level/model association.

No target may be replaced. Missing, failed, timed-out, capped, or incorrect
records remain in the archive and invalidate the affected frozen run.

### Runner interface contract

The core entry points are:

```text
rho selftest <b> <a2> <mode> <setup_seed>
rho run <b> <a2> <mode> <nruns> <setup_seed> <target_seed> <walk_seed> <target_start> <out.csv>
```

The launcher must build the 400 frozen 64-target jobs, shuffle them once with
the schedule root, propagate every nonzero exit or timeout, and never reuse an
output path. It must normalize core `target_scalar` to `k`, append the exact
block/replicate/arm/curve/orbit/seed metadata in `spec.json`, and preserve raw
CSV, stdout, stderr, command, and exit status. It must convert all 35 successful
`selftest` key-value lines to `certificates.json`, adding the source and binary
hash bindings, and emit `run_manifest.json` with the exact schema in
`spec.json`. `analyze.py` independently recomputes every planted scalar and
walk-stream seed from the frozen roots and rejects a substituted but internally
consistent workload.

`FROZEN.sha256` is the complete pre-launch commitment to `PROTOCOL.md`,
`TRACE_ZERO_LANE.md`, `spec.json`, `sample.csv`, `rho.c`, `params.h`,
`run_replication.py`, `analyze.py`, and `plot.py`. The launcher must verify that
commitment before work, copy and fsync those exact inputs into a new empty
output root, verify a single clean Git commit both before and after the copy,
and build only from the snapshot. Build time is capped at 120 seconds. Receipt
elapsed-time validation allows 2 seconds solely for post-process receipt
bookkeeping; it does not extend a subprocess timeout. Job
processes must be stopped on the first peer failure or launcher interrupt. Raw
files, receipts, normalized files, and the final tree seal are made durable
before their final names become visible; partial outputs are preserved after
failure and are never resumed. The analyzer revalidates the frozen commitment,
plan, commands, receipts, raw tree, normalized rows, binary, session, and
complete `MANIFEST.sha256` seal before producing inferential output.

### Why 4,096 executed A-stream blocks

Here `sqrt(r)=131,122.03`. Under an ideal random-map/Rayleigh planning model,
collision work has coefficient of variation about `0.5227`. Ignoring
between-orbit variation, the 3,072 inferential paired targets give an
approximate standard error of `0.01924` bit and 95% half-width of `0.03771` bit
for a log2 ratio of means. Each orbit's 192 inferential blocks give an
approximate 95% half-width of `0.15085` bit. The disjoint 1,024-block A/A
holdout gives an approximate Bonferroni-99% half-width of `0.08585` bit. These
are planning calculations, not results. The fixed-orbit interval governs the
exact sampled-orbit estimand; an orbit-resampling sensitivity may be wider if
the 16 orbit representatives differ.

At roughly `2^34` subgroup order this design is tractable for the native C
solver while being large enough to resolve sub-bit constant-factor effects.
The launch count is fixed; there is no optional stopping or sample-size
extension after inspecting outcomes.

## Accounting interval and correctness gates

The primary metric is `walk_ops`: every online group addition or doubling from
the start of the collision search through all successful and abandoned walks,
look-ahead work, starts, and cycle escapes. Per-target `setup_ops` separately
counts the 34 target-power doublings and 128 target-dependent jump additions.
The identity `ops = setup_ops + walk_ops` must hold, along with the separate
addition/doubling identities in `spec.json`.

Canonicalisation is not free. Record exact `canon_calls`, x-coordinate field
squarings, y-coordinate field squarings, sign tests, and negations for every
solve. Report these primitives beside group operations. Do not combine them
without separately frozen primitive weights.

For every arm and separately for every orbit x arm slice, report the mean,
standard deviation, and 5th, 25th, 50th,
75th, and 95th percentiles of walk, setup, total group-operation, action-
primitive, restart/cycle, and seconds fields. Preserve the raw target-level
distribution and the 16 equal-size floor-orbit slices; a grand mean alone is
not a volcano-level measurement. Per-orbit contrast points have no frozen
multiplicity-adjusted intervals and are explicitly descriptive/exploratory.

The current core intentionally excludes one-time `Pgen/Ust` construction and
certificates, planted `Q=kP` generation, final scalar-recovery multiplication,
and certificate verification. Record their invocation provenance and wall
interval externally, but label them unmeasured exclusions. Consequently even
`ops` is not a fully charged end-to-end cost.

Before accepting records, require:

1. the exact field, ambient order, prime subgroup order, cofactor, and curve
   equation;
2. `P != O`, `[r]P=O`, `Q=[k]P`, and an exact recovered `k` for every solve;
3. mode/action closure and eigenvalue certificates, including `tau^17` on
   every floor representative;
4. the exact 25,600-row design, seed pairing, orbit balance, and counter
   identities;
5. a sealed run manifest binding the source, parameter, sample, spec,
   certificate, record, binary, compiler, CPU-feature, schedule, timeout, and
   failure-preservation provenance;
6. preservation of every timeout, crash, cap, and failed verification.

## Frozen inference

The estimand for each contrast is a ratio of arithmetic means transformed to
bits, never a mean of per-target ratios. Only within-orbit offsets `64..255`
enter these estimands. Use 50,000 paired percentile-bootstrap draws with root
seed `202610135106`. For the primary exact-sample interval, retain all 16
sampled floor-orbit strata exactly once and independently resample the 192
paired inferential target blocks within each stratum. All arms attached to a
selected block move together. Also report a clearly labelled hierarchical
sensitivity that resamples orbit strata and then paired blocks; that sensitivity
targets a modeled orbit superpopulation, not the exact sampled-orbit census.

Report a pointwise 95% interval for the primary contrast and diagnostic. The
four secondary contrasts use Bonferroni 98.75% marginal intervals for 95%
family coverage.
Report prediction residuals (`observed bits - predicted bits`) with the same
intervals. Prediction inside an interval is compatibility, not proof of the
random-map model.

The predeclared practical-equivalence band for the primary collision-walk
contrast is +/-0.10 bit. Only a 95% interval wholly inside that band permits
the narrow statement “no same-action sampled-level/model association larger
than 0.10 collision-work bit was resolved in this tested implementation and
sample.” An interval excluding zero permits a measured direction and magnitude
in the same narrow scope. Equivalence and direction are separate report fields;
one never overwrites the other. Any other interval is inconclusive.

For A/A, form B/A log2 ratios separately for all five arms using only the
held-out within-orbit offsets `0..63`. The primary A/A gate retains all 16
orbits once and resamples paired blocks within each orbit. Use Bonferroni 99%
marginal intervals for 95% family coverage. Every primary interval must lie inside
+/-0.15 bit. Otherwise label the study `A/A_ALERT` and withhold inferential
labels until the implementation, scheduling, and random streams are audited.

## Reporting boundary

Always report group-operation counts, action primitives, setup exclusions,
verification status, all 16 per-orbit results, uncertainty, and the exact run
identity. The experiment estimates a same-action association between these
fixed sampled level/model implementations. Its one-crater choice, floor models,
generator construction, and hash behavior remain confounded with level; a
conductor gap is structural metadata, not an isolated causal effect or an
ECDLP-bit discount.
No observation here establishes a useful isogeny transfer, an endpoint-to-
crater map, scaling to larger subgroups, a NIST-curve attack, or a weak curve.
Those require explicit maps, subgroup preservation, recovery, fully charged
costs, and separate reviewed evidence.
