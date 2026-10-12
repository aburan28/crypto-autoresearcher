#set page(paper: "a4", margin: 15mm, footer: context [#text(size: 8pt)[RUN-ECDLP-6d910b • measured toy inputs] #h(1fr) #counter(page).display()])
#set text(font: "DejaVu Sans", size: 9.1pt)
#set par(leading: .5em)
#set heading(numbering: none)
= Solinas: point coverage and useful relations
Measured 2026-10-11 UTC • EXP-ECDLP-4c6a09 • H-ECDLP-4da36f

*Added rank expands point supply; these linear-combination methods do not beat generic BSGS.*
With generator information shared, Solinas recovered all *96/96* public synthetic
targets. BSGS recovered the same targets with less group work in every one of six
matched curve/prime cohorts. These are observations, not independently reviewed
claims, deployed-curve results or asymptotic bounds.

== Largest prime: p = 68,719,472,639
Coefficients in [-4,4]; rational ranks 1 → 3 and 2 → 4 over the Solinas cubic field.
#table(columns:(1.35fr,1.25fr,1.2fr,1fr,1fr,.8fr),inset:5pt,
 [Curve rhs],[Subgroup ell],[Q → K points],[K calls],[BSGS calls],[K/BSGS],
 [x³-3x+3],[5,385,547],[9 → 729],[92,149],[20,396],[4.52×],[x³+7x+1],[26,109,179],[81 → 6,561],[81,266],[36,989],[2.20×])
K points cover 0.01354% and 0.02513% of these subgroups. Both are *81×* the
rational-only point counts, with 81× as many coefficient vectors. Each row
recovered 16/16 targets for both methods. Calls include seed projection, table
construction and shared queries; exact-K and prior rank-discovery work are separate.

#image("relation-pipeline.svg",width:100%)

== A useful relation is new information
Unknown seed logs u and target logs q enter one modular linear system over F_ell.
Collisions give (c−d)·u=0; a target hit gives c·u−q=−jM. Only matrix-rank increases
count. A hit alone is not scalar recovery. Learned seed constraints are shared
across all 16 targets, and q is returned only when uniquely implied.

At this prime, Solinas yields *0.1953* and *0.2338 independent relations per 1,000
group calls*; the respective BSGS controls yield *0.7845* and *0.4326*.
The extra two or three equations pay for unknown seed logs. All recovered
scalars and independent relation witnesses were checked.

#pagebreak()
= Coverage and relation efficiency
#image("coverage-per-work.svg",width:100%)
Measured build operations at k=12. Algebraic boxes use B=1,2,4. Ordinary known
multiples of G reach at least as many points per construction call. Seed
projection and prior descent cost are excluded from this build-only chart.

#image("useful-relations-per-work.svg",width:100%)
Six fixed cohorts, 16 common targets each; one random finite-field seed set per
configuration. No population confidence interval is claimed. Random hidden
seeds have matching seed count, known generator slot, box and target inputs.
At k=12, Solinas takes 92,149 and 81,266 calls; the matching random hidden
sets take 92,465 and 80,996. This run does not establish a special Solinas advantage.

BSGS denotes the best measured control among the predeclared matched table sizes
and ceil(sqrt(ell)); it is not a claim of globally optimal batch parameters.

#pagebreak()
= Exact field cost and matched controls
K=Q(alpha), alpha³−alpha−1=0, reduces through alpha → 2^k. All exact-K table
reductions agree entry-for-entry with generation directly from reduced seeds.
Once those seeds are known, the cheaper finite-field path gives the same points.

#image("exact-field-cost.svg",width:100%)
Three timing repeats. Component medians for exact-K precomputation, generation
and reduction at k=12 total about *0.899 s* and *4.741 s*. Coordinate numerator/
denominator sizes reach 495 and 646 bits; this is not canonical height. GP timing
includes bit-size checks and first-repeat row output; cached Python timing includes
relation construction/checks. These machine timings are not portable primitive weights.

The preserved cold-target boundary resets learned generator constraints between
targets: 14/16 and 16/16 recoveries at k=12, costing 261,072 and 230,529 calls.
Its per-target relation counts are not global batch rank. The shared phase uses
the identical point sets, target order and 32,768-probe cap, with one common query jump.

== Controls and actual scope
- Two selected rank-gain models; three primes k=6,7,12; 78 coverage cells; 90
  configurations in each cold/shared phase; 96 unique synthetic targets.
- Pure cubic control y³−3: ranks 2 and 3. Random low-weight control y³+y−1:
  rank 1 and bounds [2,3]. The supplied point sets are not claimed saturated bases.
- The random field has no degree-one reduction at k=7,12. Four unavailable
  model/prime comparisons are retained; no substitute prime was selected.
- Sign-change control alpha=−beta, beta³−beta+1=0 matches all six Solinas cohorts.
  It is an isomorphic null, not an independent sample.
- A first GP preparation failed on t_FFELT conversion. The retained retry uses
  the identity trace in degree one. All failures and source versions are preserved.

Incomplete searches remain censored. Small subgroups, selected models and one
random seed set restrict inference. Higher fields and deployed NIST curves are
untested. Cheaper new relations or a better height-bounded lift mechanism remain
separate opportunities; these measurements do not rule them out.

#pagebreak()
= Evidence, identities and reproduction
Full identities bind the exact prime field, rational model, subgroup, cofactor
and public generator. The same identity is used by every compared method.
#text(size:7.1pt)[EC1P18Csolinaslifth8344f218e663 • A=-3, B=3, k=6\
urn:ec-record:1:sha256:8344f218e66391b3a2c10bf4d3f538d257cd9b958603aa387e6fa9b017669b6c]

#text(size:7.1pt)[EC1P21Csolinaslifth7f5aebdfe3ce • A=-3, B=3, k=7\
urn:ec-record:1:sha256:7f5aebdfe3ce06dc6fb333edcf906eec91e660ae5e5a5f74411435f6f96635d1]

#text(size:7.1pt)[EC1P36Csolinaslifth55d93546292c • A=-3, B=3, k=12\
urn:ec-record:1:sha256:55d93546292c07c17b3387818426a571b1590bb818b7744fc040c477068d85b3]

#text(size:7.1pt)[EC1P18Csolinaslifthaecb5e3fd711 • A=7, B=1, k=6\
urn:ec-record:1:sha256:aecb5e3fd7115bdbfd214d14535a7fa414643bc3c2c9b3681d66d49a5ae7cac7]

#text(size:7.1pt)[EC1P21Csolinaslifth2f53a922e551 • A=7, B=1, k=7\
urn:ec-record:1:sha256:2f53a922e551928386c48f1afe98a9e2e9924dd67a49ef874908bcdc580b15ef]

#text(size:7.1pt)[EC1P36Csolinaslifthc3394223ab66 • A=7, B=1, k=12\
urn:ec-record:1:sha256:c3394223ab666ffa15217079258f3a281d9cacf2964ede7b08388d87b18b6985]


== Immutable sources
Run directory: experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-6d910b.
Raw run commit: #text(size:7.8pt)[2ee51a2b6a4c9919fd7102d8baae524d8cab80ec].

Principal result: benchmark-shared-attempt-01/raw-result.json. Frozen plan and
shared-relations-plan.json define the boundaries; benchmark-attempt-01 retains
the cold result. point-preparation-attempt-02/exact-grids retains exact GP
tables and repeats. Earlier failed preparation and four matched descents remain
beside them. Every recovered scalar was checked against both the public point
and separately held synthetic truth; solver inputs exclude that truth.

Adjacent report.md links all evidence. methods.csv, paired-results.csv,
coverage.csv and curve-identities.csv provide the full measurements. Editable
build_report.py generates the SVG figures and PDF. Source snapshots, command
arguments, logs, GPL-2 license, script hashes and integrity checks are retained.
PARI/GP 2.17.2; Python 3.12.14. Reproduction uses fresh output locations.

No independent review, research-status change or sealed frontier-bound claim
occurred. Historical coverage/rank reports remain unchanged; this new report
adds the scoped observations. Canonical ECDLP frontier graphs require reviewed
bound evidence and are unaffected. GitHub publication remains unavailable under
the prior unchanged authentication failure; records are committed locally.
