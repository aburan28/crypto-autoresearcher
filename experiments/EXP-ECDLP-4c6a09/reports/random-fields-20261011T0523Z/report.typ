#set page(paper:"a4",margin:15mm,footer:context [#text(size:8pt)[RUN-ECDLP-9e6cc1 • toy observations] #h(1fr) #counter(page).display()])
#set text(font:"DejaVu Sans",size:9.1pt)
#set par(leading:.5em)
= Seeded random cubic fields
Measured 2026-10-11 UTC • EXP-ECDLP-4c6a09

*24 distinct fields, 48 rank descents, 104 eligible matched benchmarks.*
Reused six identical curve/prime/subgroup/generator cases and 96 synthetic target points from RUN-ECDLP-6d910b. 1075/1664 repeated field-target attempts recovered correctly; 55 complete 16-target batches. Repeated attempts share targets and fields.

None of the random-field cases that recovered all 16 targets used fewer group calls than the declared best generic BSGS control.

== Largest prime: p=68,719,472,639
Independent global equations per 1,000 finite-field group calls. Random medians below match the Solinas supplied-point count and unknown-log count.
#table(columns:(1.1fr,.8fr,.8fr,1fr,1fr,1fr),inset:5pt,
 [Curve rhs],[Eligible],[Matched n],[Random median],[Solinas],[BSGS],[x³-3x+3],[18/24],[1],[0.123],[0.195],[1.235],[x³+7x+1],[18/24],[1],[0.323],[0.234],[0.433])
The selected generic controls store 6,561 and 6,561 points; Solinas stores 729 and 6,561. Equal-entry BSGS costs 58,263 and 36,989 calls for 16/16. Storage payloads differ; all declared controls are retained.

#image("sampling-pipeline.svg",width:100%)

== Rank is not a known discrete logarithm
• x³-3x+3: 18 exact, 6 bounded, 0 unfinished/error; 9/24 certified rank gains.\
• x³+7x+1: 10 exact, 5 bounded, 9 unfinished/error; 6/24 certified rank gains.\
Rank supplies independent directions over the number field. After reduction and cofactor projection, all seeds lie in a cyclic group and satisfy F_i=u_iG. Their u_i remain unknown. A collision gives (c−d)·u=0; a hit Q−jMG=Σc_iF_i gives c·u−q=−jM. Only matrix-rank increases count as useful. Recover q only when uniquely implied. BSGS instead stores known iG and gets q=i+jM immediately from a hit.

#pagebreak()
= Observed coverage and useful relations
#image("relation-rates.svg",width:100%)
All eligible random cases are shown; their supplied point counts vary. Dots are individual observations, not confidence intervals. The same 24 fields are reused on two selected curves and three fixed primes. A partial target batch cannot be compared as a complete recovery merely by its total cost.

#image("point-supply.svg",width:100%)
Coefficients in [-4,4], capped at four supplied points. Point representatives need not form an independent or saturated basis. Exact/sign duplicates are removed before selection; reduction can create further dependencies, measured through table collisions.

#pagebreak()
= Scope, evidence and complete group identities
RNG seeds 2026101102, 2026101103, 2026101104: eight accepted fields each. Monic cubic coefficients are drawn from [-4,4], with nonzero constant. Rejections remove reducible and isomorphic duplicate fields, plus prior control classes. All draws are retained. Acceptance never uses rank, roots, points or coverage. This is not a uniform ensemble of number fields.

Least modular root selects one embedding; absent degree-one reductions remain unavailable with no replacement. Timeouts retain emitted rank bounds and checked points. If no descent vector is emitted, coverage uses labeled inherited rational points. Exact-K grids agree entry-for-entry with cached finite-field generation; three exact-K timing repeats and coordinate-bit proxies are retained separately.

Primary work counts include seed projection, finite-field table construction and shared queries. Descent, exact-K arithmetic, and validation are reported separately. No universal CPU conversion or deployed-curve security conclusion is asserted. Fixed toy models were selected for earlier Solinas rank gains; at most four points and 32,768 probes per target were tested. No independent scientific review or official status change occurred.

== Same identities for every eligible method
#text(size:7pt)[A=-3, B=3, k=6, ell=947, h=276\
G=(237963, 249012)\
urn:ec-record:1:sha256:8344f218e66391b3a2c10bf4d3f538d257cd9b958603aa387e6fa9b017669b6c]

#text(size:7pt)[A=-3, B=3, k=7, ell=2097833, h=1\
G=(1, 1)\
urn:ec-record:1:sha256:7f5aebdfe3ce06dc6fb333edcf906eec91e660ae5e5a5f74411435f6f96635d1]

#text(size:7pt)[A=-3, B=3, k=12, ell=5385547, h=12760\
G=(39306801954, 30775010499)\
urn:ec-record:1:sha256:55d93546292c07c17b3387818426a571b1590bb818b7744fc040c477068d85b3]

#text(size:7pt)[A=7, B=1, k=6, ell=293, h=895\
G=(173214, 38192)\
urn:ec-record:1:sha256:aecb5e3fd7115bdbfd214d14535a7fa414643bc3c2c9b3681d66d49a5ae7cac7]

#text(size:7pt)[A=7, B=1, k=7, ell=6803, h=308\
G=(1165070, 837767)\
urn:ec-record:1:sha256:2f53a922e551928386c48f1afe98a9e2e9924dd67a49ef874908bcdc580b15ef]

#text(size:7pt)[A=7, B=1, k=12, ell=26109179, h=2632\
G=(12970623466, 67126316800)\
urn:ec-record:1:sha256:c3394223ab666ffa15217079258f3a281d9cacf2964ede7b08388d87b18b6985]

== Reproduction and supporting records
The adjacent report.md links plan.json, sampling-result.json, random-ranks-result.json and benchmark-attempt-02/raw-result.json under RUN-ECDLP-9e6cc1. Fields, ranks, method costs, seed-count strata and full identities are exported to CSV. Editable build_random_report.py generates every figure and this PDF. Raw source, GP scripts, stdout/stderr, per-process timing and source hashes are preserved; provenance is internal immutable run evidence. Initial sampler parse failure is retained and its correction reuses the exact original draw output. Earlier report and raw evidence remain unchanged. GitHub authentication is still unavailable; publication is local with a downloadable archive.
