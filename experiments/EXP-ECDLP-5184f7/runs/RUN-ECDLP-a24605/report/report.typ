#set page(paper: "a4", margin: 18mm, footer: context align(center)[#text(size: 8pt)[RUN-ECDLP-a24605 · #counter(page).display()]])
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false)
= Solinas prime comparison
2026-10-11 · EXP-ECDLP-5184f7 · RUN-ECDLP-a24605

#text(size: 17pt, weight: "bold")[Native rho ratio 1.0009]

Requested marginal 99.9% interval: *0.9656–1.0367*. Original prespecified 99% interval: 0.9742–1.0303. Both fall within the predeclared practical-similarity margin 0.8333–1.2000. The sampled primes show similar normalized generic rho cost.

*Measured scope:* 36 sampled prime blocks across 24/28/32-bit fields; 72 random control primes; 864 matched main groups; 96 separate anchor groups; three easy groups. All 47,292 attack jobs completed. Raw outputs, exact seeds, curves, points and counts are retained.

#image("workflow.svg", width: 100%)

The prime family is p = 2^b − 2^a + s 2^c + t, with 1 ≤ c < a ≤ b−2 and s,t = ±1. Integer duplicates are removed. Random primes match size within 1%; the second control also matches p mod 12. Curves match largest prime subgroup order within 10%, with fixed weak-curve exclusions for conditional attacks. The first 32 unconditional curves per modulus are retained separately.

The higher-confidence sensitivity was requested after trials. It uses 200,000 whole-prime-block percentile bootstrap samples within bit-size strata. Original frozen results stay unchanged. Larger prospective sampling is recorded separately. Nominal bootstrap coverage is approximate; intervals are marginal, not simultaneous.

#pagebreak()
= Attacks and controls
#image("attack-ratios.svg", width: 100%)

Rho's primary endpoint is search group calls / sqrt(ell), restricted at horizon 20. Setup and scalar verification counts are separate. BSGS includes setup and search, normalizes by M+ell/(2M), and retains memory allocation with M ≤ 4096.

All 288 sham, replay and transported-isomorphism controls passed. All recovered scalars and collision equations passed independent arithmetic checks within the runner. Main rho censoring is zero. Two tiny easy-group rho attempts hit their cap; all complete-coverage BSGS easy controls succeeded. Tiny capped attempts are not interpreted as mathematical resistance.

*BSGS difference retained:* the original 99% Solinas/random interval excluded 1 (ratio 1.027099). Every one of 3,852 BSGS jobs matches exact operation accounting: setup = M + popcount(M) + bit_length(M) − 1; search = floor(q/M). At fixed ell and M, scalar position explains this count. This is a derived diagnostic, not a changed primary endpoint.

Six explicit degree-1 isomorphic endpoints and 192 associated jobs are additionally checked on the actual transported models. The full endpoint UIDs and subgroup checks are in isomorphism-identities.json.

#pagebreak()
= What the findings mean
Generic collision attacks depend mainly on subgroup order ell. Sparse binary expressions can change the cost of field reduction. That is a separate question from how many group operations an attack needs. An abstract cyclic-group isomorphism does not supply an efficient coordinate map between arbitrary curves.

The unconditional audit gives a Solinas/random difference of −0.153680 generic-proxy bits, with requested 99.9% interval -0.5306–0.2351. The proxy is 0.5 log2(largest prime factor of curve order). It is not a certified security bound.

The Python arithmetic panel has 2,520 observations over 126 moduli, all output-equal. Generic Solinas/random timings have ratios 1.0267 (products), 1.0294 (inversions), and 1.0659 (point additions), with intervals including 1. The Python folding prototype is slower than builtins: median product ratio 9.1994 and point-addition ratio 1.7259. The inverse code is identical in both paths. These observations describe a prototype, not optimized assembly or deployed resistance.

This run does not establish a result for production-size ECDLP, structural attacks, all Solinas primes, number-field rank, or industrial field arithmetic. The 56/72-bit anchors were audited and timed only. Four smaller anchors are descriptive case studies, excluded from main confidence intervals. No sealed bound, frontier update or scientific claim promotion is made.

= Reproduce and inspect
All raw preparation, attack and arithmetic records are adjacent to this report. See analysis/summary.json for the unchanged prespecified results and report/requested-confidence-99_9.json for every higher-confidence contrast. all-curve-identities.csv contains 1,095 exact curve identities including generators and subgroup orders. Sources froze at fa315f9ef before selection and 054f1988e before attacks. report.md links all supporting files. This is not an independently reviewed result.
