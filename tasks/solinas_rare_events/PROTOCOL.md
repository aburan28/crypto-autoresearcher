# Prospective public-point rare-event study, 2026-10-12

This standalone, user-authorized descriptive study follows PR #2107. It changes
no official hypothesis status and measures no ECDLP attack cost. Its new source,
input files, power plan and protocol are committed and pushed before execution.
Observations remain provisional pending a separate independent research review.
No agent delegation or claims of literature novelty are involved.

## Question and fixed scope

Do the three previously selected rare bit-64 descriptors occur at a different
rate in fresh, uniformly started walks with the selected point, the actual NIST
published generator, or a fresh public random generator? Is the selected P-224
long-run rate different from ordinary-prime coefficient-matched field models?
The selection is historical; fresh observations are never used to change it.
The deterministic historical prefixes remain reproducible observations.

Input provenance is internal: `prior-inputs.json`, `prior-candidates.json`, and
PR #2107 source at ef9e09d96fa845f0a1614a421e47a5a25b950256. `inputs.json`
retains exact integers, full named-curve UIDs, published generators, step-point
hashes, and ordinary-model UIDs. The ordinary primes reuse the prior pool;
their new curves are coefficient-matched models, not new independent primes.

Each trial consists of 256 consecutive affine points, Q+jH, j=0..255. Extract
the bit at position 64 (LSB position zero) from the conventional affine x
integer. All named-curve cohorts start at **the same Q=kG**, with k uniform in
1..N-1, and the random cohort uses H=rG with independent fresh public r uniform
in 1..N-1. Published G is checked against the OpenSSL named curve, including
exact p,A,B,N. Their prime orders make every nonzero point a generator. The
public seed does not make these cryptographic private keys.

| Historical candidate | Event in a fresh 256-point window | Fixed windows per cohort |
| --- | --- | ---: |
| P-192-two64-23-motif64 | integer 16 sum(count(m)^2)-253^2 >=16199 for all overlapping 4-bit motifs | 1,048,576 |
| P-224-p_minus_two64-19-triple64 | absolute sum of overlapping 3-bit parity signs >=54 (normalized value 54/254) | 1,048,576 |
| P-224-two64-1-longrun64 | at least 22 identical consecutive bits | 4,194,304 |

The three cohorts consume 4,831,838,208 point observations. The shared Q and
within-window dependence mean these are not that many independent samples or
necessarily distinct points.

## Ordinary-prime controls

R and C are the prior random-prime control-pool labels. For each pool's P-224
fields in prior order, set A=-3 mod p, the standard P-224 integer B mod p, and
step x=2^64+2. Select the first 32 nonsingular models with a liftable step; use
the smaller root y. No descriptor, order, or point-run outcome determines
selection. Log the liftability decisions for all 144 fields in each pool in
`control-preparation.json`. PARI exact primality and group order and independent
Python [N]H=O checks are preparation evidence, not rare-event outcomes.

For each of 64 models, draw 65,536 independent uniform affine Q. Rejection
sample uniform x and a fair root parity; nonsquares are rejected and a y=0
point receives half acceptance, ensuring uniformity over affine points. O is
excluded prospectively. The fixed H is a step, not a certified full-group
generator. Use the same 22-bit threshold and 256 points. This contributes
1,073,741,824 point observations: total 5,905,580,032. Coefficients and step x
are matched; group order, subgroup order, and generator y are not. Any observed
difference is conditional on these models and this one S prime, not a general
causal Solinas-prime effect.

## Fixed statistical families and decision impact

11 primary comparisons: for each of the three candidates, selected/random,
published/random, and selected/published (9 exact two-sided conditional
McNemar/binomial tests on discordant paired windows); selected P-224 long-run
rate versus each ordinary-prime pool (2 approximate Welch comparisons, using
256 S-chunk rates and 32 ordinary-field rates per pool). Family alpha=0.001;
Bonferroni per-test alpha=0.001/11. The field comparisons are explicitly
approximate and do not have an exact 99.9% coverage guarantee. Field, not
pooled point or pooled window, is the ordinary-prime comparison unit.

Report all nine marginal event rates with two-sided Clopper-Pearson intervals,
per-interval alpha=0.001/9, a separate nominal at-least-99.9% family under
independent windows. Conservative paired-rate difference intervals subtract
these simultaneous marginal bounds; do not label them exact paired intervals.
The primary p-value family and the rate-interval family are separate; their
union has at most 0.002 nominal family error, with the field approximation caveat.

For the long-run candidate only, record the predeclared thresholds
18,20,22,24,26,28,30,32 for all three cohorts: 24 separate exploratory CP
intervals with alpha=0.001/24. Exact fair-coin 256-bit run probabilities come
from integer dynamic programming and are **benchmarks**, not an IID assumption
for elliptic-curve point bits. The union of all three declared families has at
most 0.003 nominal error, with the same approximation caveat.

Planning power is in `power-plan.json`: exact binomial mixtures of the paired
test under independent arm flags, not a sensitivity guarantee for every point
process. With baseline 3e-5, the 4,194,304-window design has about 99.54% power
for a doubled rate at the primary per-test alpha. At baseline 1e-6 it has only
about 0.057% power for a doubled rate. The other 1,048,576-window cohorts have
about 97.83% modeled power for a doubled rate at baseline 1e-4. Dependence
between paired flags changes power; the exact conditional test uses observed
discordance.

A primary threshold crossing is a lead for fresh-seed replication and model
matching, not proof of a mechanism. No crossing narrows the tested event-rate
scope; it does not establish security, uniformity of every statistic, or absence
of rarer effects. Zero counts yield an upper interval bound, not a zero true rate.
There is no post-outcome family redefinition or sample enlargement.

## Sampling, stop, correctness, retention

Scientific seed: `solinas-rare-events-20261012-powered-v1`. Independent job
streams are SHA256(seed|jobID|starts/generators), followed by SHA256(streamseed
|| counterBE64), width masking and rejection. This is a reproducible
pseudorandom sampling experiment. Chunk size16,384, 640 fixed jobs, workers3.
Engineering checks use distinct seeds and do not consume scientific streams.
Stop only at fixed completion or a recorded native/arithmetic/disk/process
failure. Never discard a failed scientific attempt. Resume verifies immutable
file hashes and refuses altered source/config. A window containing infinity
fails visibly rather than being silently resampled.

Native checks: exact named parameters, step membership and [N]H=O; every
measured point checked on-curve and finite. Separate Python checks replay every
stored bit-string descriptor and every rare/witness coordinate frame, including
affine recurrence, uniform starts, public r, and the universal x-triple law.
This is implementation independence in one session; no separate research
reviewer has signed the results. Engineering full-coordinate runs separately
check every coordinate, bit and complete coordinate-stream hash.

Default compact retention: **all measured bit-64 strings**, all 3 exact integer
scores, all public random-generator scalars, full 256-point coordinate frames
for every threshold event (all paired cohorts if any hits), fixed witness
windows0,1,mid,last per chunk, per-file SHA256 and full transient coordinate
stream SHA256 per cohort/chunk. Most non-event full coordinates are deliberately
not persisted; they are reproducible from the seeds, counters and source. This
study is a bit-level measurement, not a stored survey of every coordinate bit.
`--full-coordinates` enables complete xy streams for future machines with a
large filesystem, with different config and new output directory.

Frozen source copies, exact command/commit/dirty state, dependency versions,
compiler output, timestamps, per-job wall/CPU facts, attempt errors, completion,
analysis and verification records remain under `runs/powered-20261012/`.
Unexposed model/usage metadata is null. Runtime facts are not speedup or ECDLP
cost claims. Fixed observations are summarized only after complete execution.
Output is write-once; a scientific correction requires a new record/run.

## Execution and publication

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research.py --output runs/powered-20261012
python verify.py runs/powered-20261012
python analyze.py runs/powered-20261012
```

The only runtime dependencies are CPython, pinned NumPy/SciPy, a C compiler,
OpenSSL development headers and libcrypto. No network service, credential or
agent is needed. A lossless compact-data ZIP, per-entry manifest, portable
source bundle and committed small result records accompany a dated report,
editable diagram, uncertainty plots and visually inspected PDF. Source/results
are committed and pushed before derived reports; publication stops at a ready
PR. Earlier raw datasets and reports remain immutable. No canonical mechanism,
frontier, attack-cost or official research state is changed by this study.
