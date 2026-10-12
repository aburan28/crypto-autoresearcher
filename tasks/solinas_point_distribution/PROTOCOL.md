# Frozen point-distribution measurement, 2026-10-12

This is a user-authorized descriptive measurement task. It extends the public
data workflow without changing an official hypothesis status. It measures whole
elliptic curves over prime fields, with no discrete-log targets or scalar search.
Source and this specification are committed before the measurement begins.

## Population, controls and stopping

Seed 20261012; three workers; fixed counts in `config.json`. Enumerate all primes
in the 18- and 20-bit intervals by sieve. The structured population consists of
primes with nonadjacent signed binary weight at most six. This is a specified
Solinas-style sparse-prime population, not all Solinas primes or the earlier
number-field construction. Choose 512 distinct structured primes per stratum.
For each, draw two unrestricted random primes (R) and two primes matching p mod
96 (C), within 5% and the same bit interval. Choose C first, then R, uniformly
from the eligible unused primes; all five fields per block, and all moduli in
the stratum, are distinct. Controls can themselves be sparse: R samples the
prime population rather than an artificially dense-only population. Matching
and global nonreuse induce dependencies; inference below is approximate and
conditional on this design. If candidates are exhausted, preparation fails
instead of silently relaxing matching or reducing sample size.

Draw four independent uniformly distributed nonsingular short-Weierstrass
models y^2=x^3+Ax+B per field. Count every affine point by exact integer
arithmetic, plus the point at infinity: 1,024 blocks, 5,120 fields and 20,480
curves. Retain full bitpacked x-liftability masks and every zero of the cubic.

At P-192 = 2^192-2^64-1 and P-224 = 2^224-2^96+1, reuse the complete, previously
prepared nonsingular whole-curve pools from RUN-ECDLP-d0e449: per case, 512
structured-field curves and 144 random fields plus 144 residue-matched fields,
with four models per control field. These old controls match bit size, a 1%
window and p mod 12 for C. Use all 3,328 curves, regardless of old subgroup
availability or flags. Existing PARI full curve counts are source data; the
x probes are new. This is conditional on an existing pool and two fixed
structured primes, not a fresh sample from a 192- or 224-bit prime family.

Every curve has 4,096 uniform x probes without replacement and a contiguous
2,048-coordinate window with a uniform random starting coordinate, wrapping
mod p. Evaluate the quadratic character exactly. Store inputs and outcomes.
For each field, independently calculate an isomorphic companion of the first
model using one public nonzero u: A'=u^4 A, B'=u^6 B, (x,y)->(u^2 x,u^3 y).
Toy maps are checked for every x; large maps are checked algebraically for
every uniform probe and by independent character evaluations for 32 probes.
Companions are descriptive controls, not independent statistical samples.

Finish the fixed sample regardless of outcomes; retain failures and treat
them as implementation problems, not mathematical results. No result-driven
early stopping or sample extension. No runtime cutoff beyond resource
protection; three workers keep memory and CPU headroom.

## Measurements and theory

For f(x)=x^3+Ax+B, each x has weight w(x)=1+chi(f(x)) in {0,1,2}; chi(0)=0.
The full order N=1+sum_x w(x), trace t=p+1-N, and |t|<=2 sqrt(p).
The point at infinity is a separate point. Liftability I(x)=1[w(x)>0] is
different from affine point mass w(x). If Z cubic roots are rational, the
number of liftable x coordinates is (N-1+Z)/2. This is an exact check, not an
assumption that all fields have precisely 50% coverage.

Three primary field/curve metrics, each compared with both R and C:

1. trace_square = (t/(2 sqrt(p)))^2, describing variation in point count;
2. Pearson correlation between adjacent liftability indicators in the fixed
   window (noncyclic; retain a constant-window failure instead of inventing
   a correlation);
3. weighted x-bin dispersion on uniform probes: with 32 equal-coordinate
   bins, proposal count n_b, point weight W_b and pooled mean mu, calculate
   sum_b (W_b-mu*n_b)^2/(mu*n_b), omitting empty proposal bins. It is a
   descriptive score compared with matched controls, not a claimed chi-square
   p-value or a uniform-point sampler.

Secondary data include signed normalized trace, exact and probed coverage,
point density, full x-bin masses, full circular gap histograms (1..32 and
overflow), maximum empty run, window gaps, the declared additional lags,
and the same window statistics after a seeded permutation preserving the
liftability count. Companion-model changes show coordinate dependence.
Numerical gaps, bins and correlations are not invariants of the abstract group.
Known clustered synthetic sequences check that the statistic detects a pattern;
they are labelled synthetic and never counted as elliptic curves.

## Uncertainty and interpretation

24 prespecified mean-difference comparisons: four cases, three metrics, two
control arms. Reserve total alpha .001; each two-sided interval has nominal
coverage 1-.001/24 = 99.9958333%, giving nominal 99.9% joint coverage by
Bonferroni if the component intervals have their stated coverage.

For toys, average the four curves within each field, average the two controls
within each arm/block, then use a paired Student t interval across 512 block
differences (df 511). At large fields, average controls within field and use
a Welch interval comparing 512 S curve draws with 144 independent control
field means. The structured prime remains fixed. Report approximate intervals,
sample variances, standard errors and degrees of freedom; no bootstrap point
rows, no claim of exact finite-sample coverage or power, and no security or
equivalence claim merely because an interval includes zero. Descriptive
99% intervals are secondary. Failure/missingness invalidates a primary
comparison rather than quietly removing rows.

## Provenance and artifacts

Canonical whole-curve identity hashes exact p, A, B and the short-Weierstrass
model in `urn:ec-point-distribution:1:sha256:...`. Whole curves can be noncyclic
and have no chosen generator; these are explicitly not EC1 subgroup IDs.
Record exact inputs, source hashes, environment, runtime, checksums, census
masks/probes, metrics, controls, failure rows, statistical outputs and logs in
`tasks/solinas_point_distribution/runs/point-distribution-20261012/`.
Live progress is a replaceable derived view; completed field outputs and the
final result record are immutable. Prior runs remain untouched.

Verify exact counts against an exhaustive independent y-loop on small primes,
Hasse and coverage identities, gap wraparound, deterministic inputs,
isomorphism maps, probe decoding and rejection of singular models. Derived
communication belongs to `docs/reports/solinas-point-distribution-20261012/`:
source-linked Markdown, editable diagram, quantitative plot and inspected PDF.
PR tracking is required; credential failure is recorded without implying a
published PR. No official weak-curve or ECDLP finding is promoted here.
