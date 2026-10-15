#set page(paper: "a4", margin: 15mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.45em)
#show heading: set text(fill: rgb("#254f76"))
= Rare and higher-order Solinas point patterns
2026-10-12 · higher-order-20261012 · measured descriptive observations

*Measured:* 0 of 58 primary mean/accuracy intervals exclude zero; 0 of 20 published-prefix reference tests cross the corrected threshold. The tested features did not resolve a published-generator or fixed-S-prime effect in this fresh batch.

*Scope:* 77.4 million fresh public points; two exact standard curves; one
published G per curve; matched random generators and random-field models.
Page 6 adds 6.29 million fresh points for three selected rare-prefix candidates.
No independent scientific review, official hypothesis transition or relative
ECDLP-resistance result. Full values and provenance: report.md, comparisons.csv,
analysis.json and verification.json next to the portable task.

== A higher-order relation did appear — the ordinary curve law
For a generator with x coordinate u and consecutive points with x values L,X,R,
`(L+R)(X−u)^2 = 2((Xu+A)(X+u)+2B) mod p`.
Add the formulas for x(Q−H),x(Q+H), then substitute y²=x³+Ax+B. This exact
identity is derived for every nonsingular short Weierstrass curve with affine
neighbors. It is not specific to a Solinas prime and reveals no unknown scalar.

*Measured:* 1,677,840 spread triples satisfied it;
wrong step 0/2048, shuffled
0/2048 hits.
Low simple correlations never imply an absence of algebraic structure.

#image("workflow.svg", width: 100%, height: 106mm, fit: "contain")

#pagebreak()
= Fresh ordered-walk and targeted-generator comparisons
2,560 paired independent-start blocks ×2,048 points/cohort/case. 160
selected generators/case near x=0,2^64,2^96,p−2^64,p−1; four 1,024-point
starts averaged per generator. Targets are a finite chosen set, not a uniform
sample. All prefix comparisons use multiples 17 through 272, excluding the
first 16 multiples. Larger prefix scores measure the declared anomaly tails.

#image("ordering-intervals.svg", width: 100%, height: 174mm, fit: "contain")

Nominal 99.9% confidence for the 78-comparison primary family: Bonferroni
α/test=1.282051e-05. 58 mean/accuracy intervals use
Student/Welch approximations; 20 reference tests use random-generator ranks.
Mean plot units = difference / recorded standard error. Original units and
all values are in comparisons.csv. Binary Hankel rank is a sequence matrix
statistic, not group rank or ECDLP complexity. Companion controls are not
independent samples.

#pagebreak()
= Fresh spatial point comparisons and ML holdout
3,328 existing frozen random models; 578 distinct primes. Per case: 512
models on fixed S p, 144 R plus 144 C fields, four models/field, 1,024
uniform affine points/model. R matches field size; C also matches p mod 12.
Random control models are averaged by field. New points are independent of
the old scan; field/model draws themselves are reused, not new replicates.

#image("field-intervals.svg", width: 100%, height: 106mm, fit: "contain")

== Feature-only ML, evaluated once on fresh seed blocks
Train only on old walks trimmed to 2,048 points; test on new 2,048-point
walks. Algorithm and settings were fixed before scanning. Input = ten
numerical descriptors, with no G coordinates, IDs, seed, scalar or label.
Pair correctness values before interval estimation; no per-point inference.

#table(columns: (1fr, 1fr, 2fr, 0.7fr), inset: 5pt,
  [Case], [Accuracy], [Corrected approximate interval], [Pairs],
  [P-192], [49.4141%], [46.3903% to 52.4379%], [2560],
[P-224], [49.7461%], [46.6800% to 52.8122%], [2560],
)

Old scan: 46,399,488 points, 56 exploratory comparisons;
0 zero-excluding intervals. Fresh primary results are reported
separately. Secondary region intervals (100-test exploratory family):
0 exclude zero. All observations, favorable or otherwise,
remain in analysis.json. Uniform nonzero multiples have exactly identical
distributions for every generator; only ordering/window effects could differ.

#pagebreak()
= Published-prefix rarity and sampling limits
The random-generator bank has 98,304 independent H per exact standard curve.
Reference p = (1 + count with score ≥ official)/(98,304+1), ties included;
minimum p≈1.017×10^−5. 0 of 20 tests cross the corrected threshold.
This is a uniform-G benchmark, not a claim about historical G selection.

#image("prefix-rarity.svg", width: 100%, height: 127mm, fit: "contain")

#image("rare-coverage.svg", width: 100%, height: 72mm, fit: "contain")

Encounter probabilities: q=10^−4 → 99.9946%;
q=10^−5 → 62.5830%;
q=10^−6 → 9.3627%.
Encountering a type does not guarantee recognition by these features. Types
with density near 1/p need deliberate targeting. Point count does not imply
proportional coverage of a 192-/224-bit field.

#pagebreak()
= Joint score behavior, integrity and reproducibility
#image("score-correlations.svg", width: 100%, height: 120mm, fit: "contain")
*Exploratory:* these descriptors share bits/points. Correlations and joint
tail counts (bank-joint-tails.csv) describe that dependence. Empirical 99th
thresholds use the same bank; no independence or prime-specific effect is
inferred. Selected bank maxima are expected order statistics in a large search.

*Measured integrity:* 77,414,912 points on-curve; all raw SHA-256
matched; 213,058 feature units replayed. Separate
integer EC oracle: 1,677,840 transitions,
5,314 scalar/start checks. All sorted positive controls
passed; 606,720 isomorphic u=2 points checked. Same-session
verification is not an independent research review.

Sampling: 819.92 s wall,
2383.03 summed job CPU s, three workers,
11,842 jobs, zero failures. Frozen source:
`29f2459899a4b8c5a6581a459132bb4d1103a582`.
Exact standard aliases: EC1P192Cniststandardhb4bdde6340ec and
EC1P224Cniststandardhe2397ca7cfb5. Full UIDs, p,A,B,n,G and internal certificate
provenance are in inputs.json and report.md. Environment/command/dirty-state
metadata and content hashes are retained.

Agent-free reruns: use research.py batch with a new public seed and a new
output directory. The dataset includes old discovery features for
--reuse-discovery; no old raw rescan is needed. Keep coordinate/JSONL shards
and manifests for future analyses; pool batches only under a prospective plan.

No relative ECDLP hardness, recovery, security exponent or attack-cost bound
is measured. Finite feature scope and rare families remain open beyond the
declared observations. Historical reports/frontier graphs remain unchanged.

#pagebreak()
= Three rare-prefix candidates: independent fresh follow-up
Three of 3,200 targeted descriptors fell in a tail containing at most 0.1%
of the random-G bank. Strongest: P224 x(H)=2^64+2, bit-64 run length 22
in its trimmed prefix (3/98,304 bank generators as extreme); same-point
u=2 changes that score to 13. These are exploratory selected outliers.

New protocol frozen and pushed before its distinct public seed: 4,096 paired
random-start windows ×256 points per candidate/cohort, fresh random control
G per pair. 6,291,456 additional points, all verified;
total in both scientific stages: 83,706,368.

#image("rare-followup-intervals.svg", width: 100%, height: 104mm, fit: "contain")

*Measured:* 0 of six mean intervals excludes
zero; 0 of three exact paired event-rate tests
crosses the corrected threshold. This is a separate nominal 99.99% nine-test
family (α=.0001), alongside the primary 99.9% family. Do not combine them
into a claimed 87-test 99.9% family; simple union coverage is nominal 99.89%,
with approximate mean-interval assumptions.

#table(columns: (1.3fr, 1fr, 1fr, 1fr), inset: 5pt,
  [Original rare score], [Threshold], [Target hits], [Random hits],
  [P192 motifs], [4.2685], [2/4096], [1/4096],
  [P224 triple parity], [0.2126], [7/4096], [5/4096],
  [P224 longest run], [22], [0/4096], [0/4096],
)

The exact paired p values are 1, 0.7744 and 1. Zero 22-bit runs leave a
corrected arm-rate upper bound of 0.285%; very rare effects remain possible.
The earlier deterministic prefix remains reproducible. Fresh tests concern
random starts, not erasing a selected scalar-window observation. Same-point
u=2 is a coordinate control, not an independent curve.

All 6,291,456 points/hash/score replays passed;
independent integer oracle checked 196,608
transitions, 1,536 starts and
384 control generators. Wall
55.91s; CPU sum
164.82s; zero job failures. Full raw
mean/rate bounds and candidate G are in report.md and follow-up analysis.json.
Ordinary-prime matched candidates would be needed for prime-specific inference.
