# Rare and higher-order point patterns — frozen v1

Date: 2026-10-12. Run name: `higher-order-20261012`. This is a descriptive
extension of `cohorts-20261012`, under the user's standing authorization to
run public point-distribution studies and publish code, results and PRs.
It changes no official hypothesis status. Write scope: this task, its dated
report directory, and this session's receipt. Historical evidence stays frozen.

## Questions and separation of populations

1. On each exact prime-order P-192/P-224 standard curve, do the published
generator's random-start walks differ from fresh uniformly drawn generators
in the ten fixed higher-order features?
2. Is the published generator's **trimmed deterministic prefix** unusually
structured compared with a bank of uniformly random generators?
3. Do deliberately selected generators near special coordinates preserve
an ordering effect after independent uniform random starts?
4. Do higher-order/spatial point features of random models on each fixed
Solinas prime differ from models on R/C random fields?
5. Can a feature-only classifier trained on the old samples recognize the
two walk cohorts in genuinely new samples?

Uniform nonzero multiples have identical distributions for every generator:
H=rG permutes the nonzero scalar residues modulo prime n. Ordered walks and
chosen scalar windows remain meaningful comparisons. The official generator
is valid only on its exact curve; its integer coordinates are never copied
to random fields. Random coefficient models with composite order are not
called generator cohorts. S is one fixed prime per case, not 512 independent
Solinas primes. R is bit-size ±1% matched; C also matches p modulo 12. All
models/orders from the previous frozen pool are retained without filtering.

## Fixed counts, seeds, limits, stopping

The complete machine-readable counts are in `config.json`, public exact
curve/field parameters and identities in `inputs.json`, and the prospectively
prepared target coordinates in `targets.json`. The seed is
`solinas-higher-order-20261012-confirmation-v1`, distinct from the old run.
SHA-256 counter rejection produces public uniform scalar/coordinate draws;
statistical interpretation assumes its pseudorandom draws behave independently.

Per case: 2,560 independently seeded paired random-start blocks, 2,048
points/cohort/block. Each pair uses the same public scalar start, with a fresh
random H. Bank: 98,304 independent random H, grouped into chunks of 64,
measuring the 256 consecutive multiples **17H through 272H**. The first
16 points are deliberately skipped for published, random and targeted
prefixes alike. Official G gets the same trimmed prefix once.

Targets: five x centers (0, 2^64, 2^96, p−2^64, p−1), first 32 liftable
integer x values in a forward search for the first three, backward search
for the last two, maximum 4,096 trials/region. Select the smaller y root
only; ±H have identical x-multiple sequences and are not independent draws.
Each of the 160 generators/case gets its trimmed prefix and four independent
1,024-point random-start paired walks, with a fresh random H per start.
These are finite deliberately selected sets, not samples estimating their
density in the field. Input preparation verifies every target [n]H=O.

Fields: new independently seeded uniform affine samples (1,024/model) on
the existing 3,328 frozen random models across 578 distinct primes: 512
models on fixed S per case and 144 R plus 144 C fields, four models/field.
Point rejection treats y=0 with half acceptance for exact affine uniformity.
No new field/model draws are claimed in this extension.

Three workers, bounded machine memory; fixed jobs, no optional stopping,
no result-driven sample expansion, no secret scalars, endpoints or keys.
Any job/verification failure stops and preserves records; it is not a
mathematical result. Resume accepts only identical design/source/input hashes
and matching raw file hashes. No completed artifact is overwritten.

## Feature menu (locked before discovery and confirmation)

- 8-bin lagged mutual information, lags 1 and 4 (bits; finite-sample bias
  is shared by matched controls, not interpreted as a zero-mean estimator).
- Absolute third-order parity averages of x bits 64 and 96.
- Pearson dispersion of overlapping four-bit motifs, x bit 64.
- Longest equal-bit run and largest non-DC Fourier power/mean power, bit 64.
- Deficiency of a 32×32 GF(2) Hankel matrix built from the first 63 bit-64
  values. This is **binary matrix rank**, not elliptic-curve group rank or
  any measured ECDLP complexity.
- Adjacent-triple ordinal entropy deficit log2(6)−H (bits).
- Frequency of adjacent x values both below p/64.

Spatial/field features: 8×8 x/y mutual information; x<p/64 frequency;
joint x,y<p/64 frequency; 64-bin x mod 64 Pearson dispersion. Bins/bits
are exact, with integer correction near floating normalization boundaries.
No claim that this finite menu detects all possible relations.

## Discovery, independent confirmation, multiplicity

Scan all 46,399,488 old points into lossless higher-order feature records.
Record all 56 exploratory old-data comparisons (walk/iid ×10×2 plus
field features ×4×2 arms×2); never treat them as independent confirmation.
For ML training truncate old walks to the first 2,048 points, matching the
new test-window size. Fit one locked HistGradientBoosting classifier/case,
100 iterations, 7 leaves, learning rate .05, L2=1, fixed random state.
No tuning/search. Inputs contain only ten statistics, never generator
coordinates, prime/curve IDs, job/seed identifiers, labels or scalar values.
Labels are used solely as training targets. Test once on the new paired
blocks, averaging correctness within each pair for uncertainty.

**78 primary comparisons:** 20 fresh walk mean intervals, 16 field mean
intervals, 20 finite-target-set mean intervals, 20 published-prefix random-G
reference tests, 2 ML accuracy-minus-half intervals. Nominal family α=.001;
Bonferroni α/test=.001/78. Student/Welch intervals are approximate, clustered
at paired walk/target units and R/C fields. Four target starts are averaged
before inference. An official generator is not a new independent generator
each time its walk starts. No bootstrap/per-point pseudo-replication.

For each nonnegative prefix score, compare the right tail only: reference
p=(1+#random scores ≥ official score)/(98,304+1), including ties. Minimum
p≈1.017×10^−5 is below the corrected test threshold≈1.282×10^−5. This
measures unusualness under a uniform random-generator benchmark, not the
actual historical selection procedure. Separately report exact
Clopper–Pearson bounds for the fraction of random generators at least that
extreme; those bounds are not the Monte Carlo rank test itself.

Report all 100 regional comparisons as a separate **exploratory** family
with .001/100 intervals, plus selected bank maxima as order statistics.
An extreme found by scanning 98,304 generators is expected and is not itself
a discovered mechanism. No unregistered cohort or favorable feature is
promoted after looking at the data.

## Controls, exact identities, verification

32 blocks/case: within-block shuffled negative control, sorted-x positive
control, and same-point isomorphic transport u=2 (x→4x,y→8y,A→16A,B→64B).
Transport published/target prefixes and first 1,024 bank generators/case too.
These are companions of the same samples, not independent observations.

The addition law gives an exact universal three-point identity, for a walk
with generator x coordinate u and consecutive x values L,X,R:

`(L+R)(X−u)^2 = 2((Xu+A)(X+u)+2B) mod p`.

Derivation: add the affine formulas for x(Q−H) and x(Q+H), substitute
y²=x³+Ax+B, and collect terms. It assumes affine neighbors (no infinity),
and reveals x(H) only up to sign, not any unknown scalar/log. Check eight
spread transitions/triples per ordered unit using a separate Python affine
oracle; shuffle and deliberately wrong step x(2G) on the diagnostic blocks.
This known curve-law control applies to any ordinary prime and is not
evidence of a Solinas-specific or security effect.

Verify every raw point's equation and hash; replay every feature unit; check
selected scalar starts and bank generator derivations independently in Python;
verify u=2 points, counts, matched jobs and positive controls. This same-session
verification is not an independent scientific review and promotes no claim.

## Publication and interpretive limits

Freeze and commit all executable inputs, feature lists and this protocol
before either discovery or new sampling. Preserve source copies, environment,
commands, receipts, raw coordinates, feature records, lossless compressed
record shards, comparisons/analysis and checksum inventories. Raw byte files
stay outside Git in the immutable run and a standalone downloadable bundle.
Ship an agent-free runner and archived old-data features so later seeds need
no old raw rescan. Build the dated report, quantitative uncertainty plots,
editable workflow diagram and inspected PDF; open a ready PR and stop there.

At 98,304 uniform generator draws, the probability of encountering at least
one q-frequency type is 1−(1−q)^98304: approximately 99.995% for q=10^−4,
62.58% for q=10^−5, and 9.36% for q=10^−6. Encountering a type is not
guaranteed recognition by a 256-point descriptor. Targeted small-x families
can have frequency on the order of 1/p and will not be covered by any
practical uniform sample; deliberate selection addresses only the named sets.
None of these tests measures relative ECDLP resistance, full group rank,
point equality across all primes, or absence of all rare/higher-order effects.
