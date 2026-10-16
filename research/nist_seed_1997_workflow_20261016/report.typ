#set page(paper: "us-letter", margin: (x: 0.5in, y: 0.45in))
#set text(font: "Helvetica Neue", size: 8.7pt)
#set par(justify: true)
#set heading(numbering: none)

= A 1997 workflow reconstruction for the NIST/ANSI prime curves
_Historical analysis · 16 October 2026 · selection rule unresolved_

The curve family's shape is explained by the documented standards goals: several security levels, fast prime-field reduction, $a = -3$ for efficient arithmetic, a SHA-1-derived coefficient, and a large prime-order group. The exact reason eleven other qualifying seed blocks were passed over remains unknown. The six-stream recorded census has *21,753* 20-byte blocks, *11,042* point-count rows, and *21* curves passing known prime-order, order-size, and MOV screens: *ten published, eleven passed over*. This classification has been independently replayed given the stored point counts, not by replaying the unavailable 1997 generator.

#figure(image("workflow.svg", width: 72%), caption: [The documented design choices and the missing historical keep/skip decision.])

== What was being optimized

*Security levels.* NIST's July 1999 appendix maps 192-, 224-, 256-, 384-, and 521-bit prime fields to 80-, 112-, 128-, 192-, and 256-bit symmetric-key categories, including SKIPJACK, Triple-DES and prospective AES sizes. This is the final suite's documented purpose, not an original 1997 memo. All five field primes are generalized Mersenne numbers with special reduction formulas. NIST explicitly attributes $a = -3$ to efficiency. Its prime-field curves have prime group order and cofactor one. #link("https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf")[FIPS 186-2, Appendix 6] (retrieved).

*Checkable coefficients and examples.* ANSI X9.62 starts from an arbitrary seed of at least 160 bits, hashes it with SHA-1, and specifies near-prime order, MOV, and anomalous-curve checks. The published seed checks the coefficient relation; it does not certify how many candidates were tried. ANSI Annex J.5 calls its three 192-bit and three 239-bit curves implementation samples. #link("https://pdfcoffee.com/x9-62-1998-ecdsa-pdf-free.html")[ANSI X9.62-1998, Annexes A and J] (retrieved).

== The recovered schedule and base-point clue

The reconstructed clock seeds date the 239-bit run to 15 May 1997, the 192-bit run to 18 May, P-521 to 8 August, P-256 to 16 August, P-384 to 30 August, and P-224 to 3 April 1998. The smaller P-224 came last, consistent with a later project pass but not proof of one. These are reconstructed PRNG inputs, not independently witnessed wall-clock records. Anthropic recovered a *different FreeLIP generator* for six May base points. Their small integer seeds are 20000, 20420, 20507, 20509, 20512, and 20517 in an order different from both curve-stream dates and standard listing. This is consistent with a separate base-point or standards-assembly pass. The four later prime base points remain unexplained. #link("https://www.anthropic.com/research/ecdsa-curve-origins")[Anthropic] (retrieved).

#figure(image("stream_counts.svg", width: 72%), caption: [Qualifying blocks through each stream's last published block. Every row is right-censored; these counts do not estimate all generator attempts. Source: internal census/summary.json.])

Two actual software choices account for other exclusions. The census records *17* prime-order candidates whose orders are longer in bits than their field primes, rejected by an extra bit-length rule. In the four fields with $p equiv 3 mod 4$, the selected coefficient uses the simple exponentiation square-root convention; *31* other blocks have prime-order groups only on the opposite sign. These are separate from the eleven unresolved omissions. P-224 has $p equiv 1 mod 4$ and needs a different square-root path; its two coefficient signs are isomorphic, so sign choice does not explain its three omissions. A later P-224 software branch is a testable hypothesis, not an observed fact. Sources: internal census and sign audit.

== What might explain the passed-over curves?

*Software behavior or incomplete point counting.* ANSI describes recent point-counting improvements. A later, near-era MIRACL SEA implementation documents curve-dependent runtime and Elkies-prime variation; its use by the original designers is unknown. An early program could have timed out, failed a proof, crashed, or lost a result. A predeclared modern Elkies-coverage proxy did not split all 21 labels. This hypothesis needs original code, logs and limits, or a versioned replica whose behavior predicts every candidate. #link("https://github.com/miracl/MIRACL/blob/master/source/curve/sea.cpp")[MIRACL SEA source] (retrieved, later contextual example).

*Editorial or committee selection.* Multiple ANSI samples, months between runs, and separate base-point generation fit staged production. No contemporaneous marked table, correspondence, or rule explains the precise eleven omissions. *Extra RNG calls* could leave qualifying windows unevaluated, but all published seeds align to 20-draw boundaries. Five tested consumption models miss published positions; the best misses three. The May base points came from another generator. These are bounded model failures, not a full rejection of shared-state behavior.

*Extra quality test.* All 21 pass the checked ordinary order, MOV, anomalous and bounded CM screens. A rule requiring $n < p$ fails on published prime239v2; positive trace, prime twist, no small twist factor, and maximal twist-prime factor fail on other controls. A predeclared screen of roughly 60 deterministic features found no perfect classifier. The 2015 preliminary note about P-384's unusual prime twist is less persuasive as within-run evidence after the census: P-384 was the *first qualifying block* of its recovered run. A selected timestamp remains possible, but discarded timestamps are unknown. #link("https://arxiv.org/abs/1506.07269")[Elliptic-twins note] (retrieved); internal studies cited in Markdown report.

*Deliberate rare-class selection.* No specific weak class or retained witness has been identified. For fixed field and exact 20-consecutive-draw extraction, the 48-bit LCG permits at most $2^46$ distinct candidate-start states across all timestamps and block ordinals; arbitrary intervening draws between intact windows permit at most $2^48$. These are model-specific ceilings, not observed attempt counts. Earlier field-prime choice and any hidden method applicable to honestly generated curves are separate questions.

== Working reconstruction and next evidence

The most plausible *process-level hypothesis* is that a team fixed fast primes and $a=-3$, generated candidate seeds with a clock-seeded C RNG, derived coefficients under the ANSI/IEEE recipe, screened orders with period software, then assembled records for ANSI and NIST. At least one undocumented test, failure mode, RNG-state change, or editorial choice intervened. The recovered numbers cannot identify which. Bob Reiter's generator code or a contemporary run log is the strongest missing evidence. A historically plausible toolchain should be frozen before comparison with all 21 candidates; a failed replay would reject that toolchain only.

The published hash relation confirms the seed-to-coefficient calculation, not the number of seeds or timestamps inspected. No criterion or structural trait identified here supplies an ECDLP shortcut. A hidden-route claim needs a concrete mechanism, access model and complete construction, evaluation and per-target costs, including any costly intermediate advantage.

Full evidence, scoped counterexamples, editable visuals and the open problem record are linked in #link("report.md")[report.md] and #link("../../problems/nist-seed-selection-rule-unexplained.md")[the problem record] (internal).
