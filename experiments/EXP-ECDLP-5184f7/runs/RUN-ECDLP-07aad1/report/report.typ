#set page(paper: "a4", margin: 18mm, footer: context align(center)[#text(size: 8pt)[RUN-ECDLP-07aad1 · #counter(page).display()]])
#set text(font: "DejaVu Sans", size: 10pt)
= Wider Solinas prime comparison
2026-10-11 · EXP-ECDLP-5184f7 · RUN-ECDLP-07aad1

#text(size: 17pt, weight: "bold")[Native rho ratio 0.9952]

Marginal *99.9% interval: 0.9725–1.0185*. Reserved three-family 99.9667% Bonferroni interval: 0.9706–1.0207. Frozen practical-similarity margin: 0.8333–1.2000. Decision: practically similar normalized rho cost in this sampled scope.

*Prospective wider scope:* 72 fresh sparse-prime blocks, 288 random controls, four field-bit strata (24/28/32/36), 368,640 nonsingular prepared models and 46,080 unconditional audit models. Baseline moduli are excluded and baseline outcomes are not pooled.

#image("workflow.svg",width:100%)

The sparse integer catalog is p=2^b−2^a+s2^c+t, 1 ≤ c ≤ a−1, a ≤ b−2, s,t=±1. Each block has two size-matched random controls and two controls additionally matching p mod 12. Fixed pools give eight common S matches across all four control arms, within 10% subgroup order; largest ell has 16–28 bits. The unconditional audit does not exclude weak curves.

Whole-prime-block bootstrap: 500,000 replicates within bit-size strata. Targets and walk seeds are repetitions, not independent prime samples. Intervals have approximate nominal coverage. The three-family adjustment concerns primary tests only; other results use marginal intervals. This run does not identify or test the two other user-named prime cases.

#pagebreak()
= Attack results and controls
#image("attack-ratios.svg",width:100%)

All 150,864 jobs completed; main rho censors = 0. All recovered scalars and collision equations passed arithmetic checks. All 768 sham, replay and transported-isomorphism checks and four BSGS easy positive controls passed. 512 actual transported endpoint jobs were also checked; full identities accompany the report.

Rho endpoint: search group calls/sqrt(ell), capped at normalized horizon 20; setup and verification remain separate. Each comparison pools two control arms per slot, then averages eight slot log-ratios per block. BSGS uses setup+search normalized by M+ell/(2M), M≤4096, with table memory retained.

Every one of 11,536 BSGS jobs matches exact count identities: setup=M+popcount(M)+bit_length(M)−1; search=floor(q/M). Its empirical contrast includes target position and finite ell/table-size effects; it does not establish extra resistance from field-prime form.

#pagebreak()
= Implications and scope
The unconditional proxy (0.5 log2 largest prime factor of curve order) differs by 0.0256 bits, S minus pooled random controls. Its marginal 99.9% interval is -0.1061–0.1555. This is not a certified security bound.

The arithmetic panel has 6,480 exact-output-equal observations. Python folding and builtin modular arithmetic are implementation comparisons. Inversion uses identical builtin pow in both paths. report.md and analysis/summary.json retain every timing ratio and higher-confidence interval; production C/assembly arithmetic is untested.

Generic rho collision work depends mainly on subgroup size. Sparse binary expressions can affect field reduction. Equal-order cyclic groups being abstractly isomorphic supplies no efficient coordinate map between arbitrary curves. The implemented opaque interface limits this solver's coordinate access; it is not a formally enforced oracle against an adversarial program.

Scope is the declared finite sparse-prime catalog, uniform nonsingular coefficient models, matching rules and implemented toy attacks. This does not settle deployed ECDLP, structural attacks, all Solinas primes, number-field rank or unrelated prime families. No scientific claim, sealed bound or canonical frontier is promoted.

= Artifacts and provenance
See manifest.json and contract.json for preselection source commit, hashes, seeds and exact commands; execution-result.json for actual phase outcomes; analysis/summary.json for every estimate; report/all-curve-identities.csv for 3,260 full EC1 identities; report.md for links and detailed limitations. All raw outputs are retained. Committed per-block matching shards reconstruct the exact retained large array; this changes storage only. No independent scientific review was obtained.
