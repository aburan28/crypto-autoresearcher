#set page(paper: "a4", margin: 16mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.55em)
#show heading: set text(fill: rgb("#254f76"))
= Solinas primes and generator cohorts
2026-10-12 · Measured descriptive study · cohorts-20261012

*Measured:* None of the 20 corrected intervals excludes zero. These data did not resolve a mean difference in the prespecified features.

== The prime, the curve, the generator
The prime defines residues modulo p. A and B define y²=x³+Ax+B. A generator
defines an ordering of its finite group. P192 uses 2^192−2^64−1; P224 uses
2^224−2^96+1. The exact standard curves have prime group orders and cofactor 1.

*Derived:* H=rG, with r nonzero modulo prime n, permutes the nonzero multiples.
Uniform kG and kH therefore have exactly the same point distribution. Ordered
walks Q, Q+G, Q+2G versus Q, Q+H, Q+2H can expose ordering features. Consecutive
points are dependent. Generator comparisons hold each standard curve fixed.

== Fixed sample and controls
Each generator cohort on each standard curve: 2,560 random-start walks ×4,096
points (10,485,760) and 256 iid-multiple blocks ×1,024 (262,144). Random generators
are fresh per block; published generators use identical public scalar schedules.
Each case also uses 512 random models on fixed S p; 144 R and 144 C fields,
four models/field, 1,024 uniform affine points/model. C matches p mod 12.

#image("workflow.svg", width: 100%)

20 primary mean tests, nominal 99.9% simultaneous confidence via Bonferroni.
Student/Welch approximations use generator blocks and control field means.
The two fixed S primes are not a sample of all structured prime families.

#pagebreak()
= Corrected comparison intervals
Published minus random G for walks/iid; fixed-S random models minus R/C field
means for the field baseline. Correlations and bin dispersion are dimensionless.
Each interval has nominal 99.995% confidence; simultaneous nominal 99.9% applies
to these 20 tests in this batch. Sampling-distribution coverage is approximate.

#image("primary-comparisons.svg", width: 100%)

Zero-compatible intervals bound tested mean features; they do not exclude every
rare generator type, higher-order coordinate feature, or discovery from ML.
No relative ECDLP resistance is measured. Official G is one fixed instance;
many independent starts do not turn it into many independently chosen Gs.

#pagebreak()
= Values and software checks
#set text(size: 8pt)
#table(columns: (1.15fr, 1.45fr, 0.8fr, 2fr, 0.7fr), inset: 4pt,
  table.header([Case/population], [Metric], [Difference], [Corrected interval], [Units]),
  [P192/walk], [x_lag1], [1.9446e-05], [(-0.0017556, 0.0017945)], [2560/2560], [P192/walk], [bit64_lag1], [-0.00020067], [(-0.0019492, 0.0015479)], [2560/2560], [P192/walk], [bit96_lag1], [-0.00040879], [(-0.0021588, 0.0013412)], [2560/2560], [P192/walk], [x_bin_dispersion], [0.00049557], [(-0.027751, 0.028742)], [2560/2560], [P192/iid], [x_bin_dispersion], [0.0045363], [(-0.089816, 0.098889)], [256/256], [P192/iid], [xy_correlation], [-0.002146], [(-0.014252, 0.00996)], [256/256], [P192/field R], [x_bin_dispersion], [0.0040563], [(-0.058508, 0.06662)], [512/144], [P192/field C], [x_bin_dispersion], [0.022054], [(-0.040193, 0.084302)], [512/144], [P192/field R], [xy_correlation], [-0.0042983], [(-0.011682, 0.0030855)], [512/144], [P192/field C], [xy_correlation], [-0.0028499], [(-0.010134, 0.0044338)], [512/144], [P224/walk], [x_lag1], [-0.00049816], [(-0.0023239, 0.0013275)], [2560/2560], [P224/walk], [bit64_lag1], [2.4061e-05], [(-0.001761, 0.0018091)], [2560/2560], [P224/walk], [bit96_lag1], [-0.00023775], [(-0.0020189, 0.0015434)], [2560/2560], [P224/walk], [x_bin_dispersion], [-0.010583], [(-0.039162, 0.017996)], [2560/2560], [P224/iid], [x_bin_dispersion], [-0.030336], [(-0.12304, 0.062366)], [256/256], [P224/iid], [xy_correlation], [-0.0030399], [(-0.013925, 0.0078449)], [256/256], [P224/field R], [x_bin_dispersion], [-0.012278], [(-0.071982, 0.047426)], [512/144], [P224/field C], [x_bin_dispersion], [-0.0020713], [(-0.063298, 0.059155)], [512/144], [P224/field R], [xy_correlation], [0.0011342], [(-0.0064444, 0.0087129)], [512/144], [P224/field C], [xy_correlation], [0.00018856], [(-0.0076359, 0.008013)], [512/144]
)
#set text(size: 9pt)
*Verified:* 46,399,488 points on their exact curves;
14,592 SHA-256/feature replays; 163,840
independent walk transitions; 768 scalar arithmetic
checks; 524,288 isomorphic transports. Separate Python affine
arithmetic checks OpenSSL outputs. This is same-session software verification.

The first 32 blocks/cohort/case also test shuffle, sorted positive dependence,
and u=2 isomorphic coordinate transport on exactly the same points. Sorted
sequences are deliberately synthetic. These diagnostics do not enter primary
multiplicity or create a security claim. See the Markdown report for values.

Per-cohort walk units =2,560; iid units =256. Field baseline uses 512 fixed-prime
coefficient draws versus 144 independent field means per control arm. The data
reuse 578 prime fields. The published generator exists only on its standard
curve; the field baseline does not identify a universal prime-by-G interaction.

#pagebreak()
= Sampling size and a reusable runner
The *sampling fraction* is sampled points / population size. A fixed fraction
of a 192-bit field is infeasible. Ten million / P192 p is about 1.6×10^−51.
*Power analysis* uses effect size, variance, confidence and independent units.
*Rare-event detection* uses event probability q: independent draws needed for
99.9% chance of at least one recognizable event are ceil(log(.001)/log(1−q)).

#table(columns: (1fr, 1fr), inset: 5pt, table.header([Event probability q], [Independent draws]),
  [1%], [688], [0.1%], [6,905], [0.01%], [69,075], [1 in a million], [6,907,752])
For rare fields count independent fields; for rare generators count generator
draws. Walk points do not supply independent event trials. The finite-population
correction is negligible at these fractions and applies to simple sampling
without replacement, not to walks. Variance-based detectable effects appear in
the Markdown comparison table; they do not bound all possible patterns.

== Run batches without an agent
Linux, Python 3.10+, C compiler and OpenSSL development headers. A standalone
package bundles public inputs. Each batch freezes source, seed and configuration,
then writes restartable exact coordinate chunks, SHA-256 manifests and features.

```bash
bash bootstrap.sh
bash run_batch.sh /large-filesystem/ec-study/batch-0001 batch-0001 3
.venv/bin/python catalog.py --root /large-filesystem/ec-study --output /large-filesystem/ec-study/catalog.sqlite
```

The same batch command resumes; a new seed gets a new output directory. A
deduplicated SQLite index retains field/model/generator identities for analysis
and ML. Default raw bytes: 2,412,773,376 (2.41 GB). Measured wall time:
577.7s, job CPU sum 1654.7s, three workers.

New seeds add conditional point/start/G replicates; they add no new primes.
Use independent confirmation seeds and field/curve-aware ML splits. Repeated
batch inference needs a prospectively declared pooled or sequential policy.

== Sources and identities
Frozen source: #text(size: 7pt)[18e4cca389b76f208b8fec37c1f0c73eb24a1f1c]. Full exact standard
EC1 identities and parameter preimages are in inputs.json and report.md; all
random-G identities retain the changed generator. Public baseline inputs:
EXP-ECDLP-5184f7 / RUN-ECDLP-d0e449. Receipt, analysis, verification, lossless
record shards, source/PDF, graphs and data bundles are linked from report.md.
No canonical frontier edge changes; no hypothesis promotion or security claim.
