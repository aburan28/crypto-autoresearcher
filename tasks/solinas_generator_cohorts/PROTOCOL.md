# Frozen point and generator cohorts

User-authorized descriptive measurement, 2026-10-12. No hypothesis state change,
key recovery, target logarithm, cryptanalytic bound, or security conclusion.
Freeze source and `config.json` in Git before execution. `inputs.json` contains
all public inputs and original source SHA-256 values; the runner is portable.

## Populations and controls

For each actual standard curve P-192 and P-224, hold **p, A, B, n, h=1** fixed.
Use the exact published G, preserving its existing EC1 identity, in cohort P.
In cohort H independently select H=[r]G, r uniform in 1..n-1 per block. Since n
is prime, every selected H is a full-order generator. Store H, the public seed
for r, and its own EC1 identity; the published identity is only the anchor.

1. **Ordered walks:** 2,560 independent paired blocks per case, each with
   4,096 points in each cohort: Q_i=[k+i]G or [k+i]H. Same public uniform k in
   1..n-1 for the two cohorts. This is 10,485,760 points per cohort per curve.
   Infinity is an explicit arithmetic failure; its chance in a walk is at
   most 4,096/(n-1), negligible here, and it is never silently discarded.
2. **Independent multiples:** 256 independent paired blocks, 1,024 independent
   uniform nonzero scalars per block per cohort. New random H per block;
   same scalar sequence in both cohorts. 262,144 points per cohort per curve.
   Sampling is conditional on the fixed standard curve and excludes infinity.
3. **Prime/random-model baseline:** reuse the immutable full-size input pool
   from RUN-ECDLP-d0e449: for each case 512 independent random nonsingular
   models on fixed Solinas p; 144 distinct R fields and 144 distinct C fields,
   four models per control field. R: same bit length, within ±1% of standard p.
   C: additionally p mod 12 matched. Draw 1,024 exact uniform affine points
   per model. Do not filter by order; do not call a random point a generator
   on a possibly noncyclic composite-order curve. R/C averages cluster the
   four models by field. S models are independent coefficient draws at one
   fixed prime and **are not 512 independent structured primes**.

Total: **46,399,488 point records**, exact coordinate pairs in fixed-width
big-endian encoding. The base pool is 3,328 random models on 578 distinct
fields, plus the two exact standard models on the already-counted fixed S
fields. Points use SHA-256 seed/counter streams and exact rejection sampling;
no biased modular reduction. These are deterministic public pseudorandom
replicates, analyzed with the usual independent-stream sampling assumption.

Exact uniform affine points: draw x uniformly and a sign bit. Nonzero square
RHS gives the unique root with that sign; reject nonsquares. If RHS=0 accept
only one of the two signs. Each affine point has equal acceptance probability
1/(2p). This avoids overweighting one-point fibers; infinity is excluded.

An official generator is defined only on its own standard curve. Its integer
coordinates cannot be assumed to be valid on a random-prime control curve.
The design estimates published-vs-random generator behavior **conditional on
each exact standard curve** and fixed-prime random-model behavior separately.
It cannot identify a universal generator-by-prime interaction across fields.
The difference between these populations also includes the standard model's
coefficient/order selection. A full factorial family claim needs additional
structured fields, matched models/orders, and a generator-selection rule
defined on every arm. Do not relabel field/model differences as G effects.

## Prespecified metrics and inference

Walk primary metrics: Pearson lag-1 correlation of normalized x; lag-1
correlation of exact x bit 64; lag-1 correlation of exact x bit 96; and x
32-bin dispersion (Pearson chi-square divided by 31). This tests means of
block features, not every possible pattern or an outlier rank among all Gs.
Independent-multiple primary metrics: x-bin dispersion and x/y correlation.
Random-model primary metrics: the same two, S versus R and S versus C.

Two cases × (four walk + two iid + four field) = **20 primary comparisons**.
Familywise alpha 0.001; Bonferroni individual alpha 0.00005, nominal individual
confidence 99.995% and nominal simultaneous confidence 99.9%. Paired Student
intervals on generator blocks; Welch intervals on S model units versus R/C
field-average units. These are **approximate sampling-distribution intervals**,
not an exact finite-sample coverage guarantee. Walk points within a block are
dependent; never use 10 million as the independent sample size for a walk CI.
Official G is one fixed instance; independent starts do not create more Gs.
Compute approximate 90% power detectable mean differences from actual block
variance and the frozen multiplicity; report these as variance-based planning
quantities, not a claim that arbitrary patterns would have been detected.

The field size does not set the necessary sampling fraction. For independent
draws and recognizable events with probability q, detection confidence c
needs ceil(log(1-c)/log(1-q)) draws. This formula does **not** apply to walk
points as independent trials. Mean-effect power instead depends on variance,
effect size, confidence, power, and the number of independent units. A global
sampling fraction does not ensure that a targeted rare coefficient family or
exceptional generator is present. A complete census is practical only in
small fields. No fraction of P-192/P-224 is claimed to have been covered.

## Diagnostic checks, validity, stopping, artifacts

First 32 blocks of each ordered cohort/case: shuffle the identical x values
as a negative dependence control; sort them as a deliberately synthetic
positive control; transport the same point pairs by (x,y)->(4x,8y), u=2, to
the isomorphic model (A,B)->(16A,64B). Diagnostics are outside the 20 primary
comparisons, descriptive only. They preserve point sets/group respectively;
numerical coordinate patterns are not themselves group-theoretic weaknesses.

Run the complete fixed queue; no effect-dependent stopping, extensions, or
discarded outcomes. Three process workers, one BLAS thread each. Stop with
arithmetic/integrity errors; a crash is infrastructure, not negative evidence.
Use a new directory/seed for prospective new batches. Never enlarge an old
completed batch or silently combine repeated analysis decisions. A repeated
batch reuses fixed fields/curves and adds conditional point/start/generator
replicates; it does not increase the number of independent prime fields.

Each output stores frozen design/source hashes, inputs, public seeds and
generators/identities, exact raw coordinates, per-block features and diagnostic
controls, timestamps, machine/compiler/library versions, logs, checksums,
immutable records, verification, comparisons CSV, and analysis JSON. Linux
file locking excludes two writers for the same batch. Atomic publication and
byte-identical replay make interrupted runs restartable. Existing results are
checksum-checked before resume. Source/config drift or corruption refuses
resume; corrections require new records. A separate verifier checks **every
point on its curve**, all hashes and feature recomputations, dispersed walk
transitions, and independent affine scalar multiplications on diagnostic
blocks. This is same-session arithmetic verification, not independent review.

Outputs are measured observations. Negative results only bound the tested
mean features and populations. Any apparent difference needs independent
seed replication and coordinate/model controls before mechanism interpretation.
No conclusion about relative ECDLP resistance follows from these statistics.
