#set page(paper: "a4", flipped: true, margin: (x: 16mm, y: 14mm))
#set text(size: 9pt)
#set par(justify: true)
#set heading(numbering: none)

= The eleven skipped prime-field seed candidates

_Structural assessment and trait-sheet correction · 16 October 2026 · exact data and code in the accompanying study directory_

#image("selection.svg", width: 100%)

== Question and method

Filippo Valsorda's recovered seed streams name eleven unpublished candidates that passed the visible criteria: five at 239 bits, two at 192 bits, one at 256 bits, and three at 224 bits. Ten published controls make 21 observed curves in this comparison. We reconstructed their complete 160-bit seeds with the 48-bit srand48 recurrence; all ten published prime-field seeds reproduced exactly. NIST's SHA-1 expansion then defines c, and the equations use a = −3 with c b² = −27 modulo p. Sage point counting, proven-prime n, an on-curve nonidentity point killed by n, and Hasse-interval uniqueness check each candidate's order. Published p, a, b, G, n and seed are OpenSSL controls. Source details and commands are in report.md, audit.py and postprocess.py.

All eleven have prime order, cofactor 1, n bit length no greater than p bit length, n ≠ p, j outside 0 and 1728. A supplemental modular screen checks every k from 1 through 1,000,000 for all 21 rows and finds no embedding degree in that range. A complete scan through fundamental CM discriminants of absolute value at most 2,000,000 found none for the skipped classes; this excludes noninteger endomorphisms below degree 500,000 within that screen. Exact CM fields and endomorphism conductors are unresolved.

== Candidate-by-candidate traits

The ordinal is one-based. Trace is t/(2√p), t = p + 1 − n. Twist factors shown are proven factors at most 10,000. P means the residual twist factor is proven prime and the factorization is complete; C means a composite residual remains. Full p, b, n, generator and EC1 representation identity appear in assessed.json.

#text(size: 7.1pt)[
#table(
  columns: (20mm, 17mm, 77mm, 14mm, 23mm, 48mm, 16mm),
  inset: 3pt,
  stroke: 0.4pt + gray,
  align: (center, center, left, center, center, left, center),
  [Bits], [Ordinal], [Recovered seed, hex], [n vs p], [Trace], [Twist factors ≤10,000], [Rest],
  [239], [36], [`25e56088185f8c3207b166cd2e007b88276afe78`], [<], [+0.730], [139], [C],
  [239], [1562], [`d09bfb7db85672dc700269f9189983f25f81958d`], [>], [−0.113], [41], [C],
  [239], [2491], [`1256fdd46eeb96b7d312ddb1de99bff159cf6701`], [>], [−0.151], [43, 173, 307, 953], [C],
  [239], [2682], [`d2c18e22558203444a2b33ea97c178675b438484`], [>], [−0.062], [29], [C],
  [239], [2863], [`3a700d3e6bf03255949804ba2a8677550c19ee11`], [<], [+0.447], [none found], [C],
  [192], [2198], [`692d90186057951de011733105bf1b3d3b0fc451`], [<], [+0.815], [11, 127, 5827], [P],
  [192], [5405], [`3ad10ff61797bc7258480cadd4e59c1ac1fb66d1`], [<], [+0.472], [7, 19²], [P],
  [256], [876], [`50c71a63f911db7b2f31618ecf609d37154437f9`], [<], [+0.156], [3, 11, 37, 8081], [C],
  [224], [777], [`d00720e7691d403449c0d91be84bfb2c7501a267`], [<], [+0.376], [3, 5, 683], [C],
  [224], [1485], [`18cfdbcbb825568171212bc1610a5b8a8004e5c4`], [<], [+0.015], [3, 31], [C],
  [224], [5736], [`3c170a30ee6709df9b4c9ea0b6c1e95fcd6200ce`], [<], [+0.311], [3, 1607, 3371], [C],
)
]

#pagebreak()

== Comparison with the published curves

#image("trace.svg", width: 85%)

All eleven omitted group orders differ from published orders over the same prime field, so there is no base-field isogeny to a published curve in the same field. Three omitted 239-bit curves have n greater than p, but published prime239v2 does too: n < p is not the missing selection rule. Trace signs, small twist factors, and the bounded CM screen reveal no rule that picks precisely the published subset. The three P-224 seeds yield two b signs each; because −1 is a square in that field, each pair is isomorphic by (x,y) → (−x,u³y), u² = −1.

The two 192-bit omitted twists have complete factorizations into the table's small factors and one proven large prime. The other nine twist residuals are composite and not completely factored. Twist factors are relevant to applications admitting unchecked off-curve points, not a weakness of the prime-order group itself.

== Inference boundary

The historical reason the eleven curves were skipped remains unidentified. Presence in a reconstructed stream does not prove that the original program evaluated and explicitly rejected a candidate. This study reconstructed precisely the candidates named in the two primary accounts; it did not enumerate every earlier rejected block or other timestamps. Neither the surviving numbers nor this trait comparison reveal how many separate timestamp runs took place. A historical code or log recovery, or a predeclared deterministic rule that correctly predicts accepted and skipped cases on a held-out run, would resolve the selection question. The current screens do not assess a hypothetical undisclosed map, extension-field transfer, or intermediate-cost advantage; each would need a construction, subgroup-preserving transport, destination solver, secrecy analysis, and cold-start and amortized costs.

#pagebreak()

== Audit of a supplied complete-traits sheet

The separately supplied _NIST/ANSI Pseudorandom Prime Curves Complete Trait Analysis_ is bound by SHA-256 `4076201e051737c9c7086ed577ddfb7912d0c729611b5a67f153e53d80765f34`. Of 21 rows, 18 match exactly, one skipped P-224 row uses the opposite isomorphic coefficient sign, and two published rows contain incorrect fields. All eleven skipped seeds, fields, orders, traces and twist orders match; their coefficients match a recorded sign model. The sheet is identified by digest and is not copied into this repository.

#set par(justify: false)
#table(
  columns: (49mm, 205mm),
  inset: 5pt,
  stroke: 0.4pt + gray,
  [Claim in supplied sheet], [Checked correction],
  [“9 published”; “all 20”], [Ten published controls plus eleven skipped candidates = 21 observed curves.],
  [Six UTC timestamps], [All six displayed conversions are wrong. The table below lists the correct values.],
  [prime192v2 coefficient], [The pasted value is 228 bits and does not reduce to either published sign in the 192-bit field. Correct b is `0xcc22d6dfb95c6b25e49c0d6364a4e5980c393aa21668d953`.],
  [P-521 field and derived traits], [The pasted field is 513 bits; the correct prime is 2^521 − 1. The pasted trace violates Hasse's bound and its twist order is negative. The corrected twist order is positive, 522 bits, composite, and divisible by 5 and 7. Its Frobenius discriminant has factor 5 as the only prime factor below 100,000; twist-order-minus-one has factor 2.],
  [P-384 twist prime], [Confirmed on the published parameters by PARI/GP isprime.],
)

_Correct UTC dates for the six cited srand48 timestamps_

#table(
  columns: (28mm, 74mm, 28mm, 74mm),
  inset: 3pt,
  stroke: 0.4pt + gray,
  [Timestamp], [UTC date and time], [Timestamp], [UTC date and time],
  [`863711343`], [1997-05-15 15:49:03], [`863966734`], [1997-05-18 14:45:34],
  [`871002724`], [1997-08-08 01:12:04], [`871696354`], [1997-08-16 01:52:34],
  [`872952608`], [1997-08-30 14:50:08], [`891607927`], [1998-04-03 12:52:07],
)
#set par(justify: true)

== Which security inferences survive

The supplemental checker iterated p^k modulo n for every k from 1 through 1,000,000 for all 21 curves; no row returned 1. This is a bounded result, stronger than NIST SP 800-186's k ≥ 2^10 criterion, and does not determine any exact embedding degree. It also checked all three small-factor lists per row through 100,000: only P-521's discriminant and twist-order-minus-one lists differ. The candidate table on the first page gives factors of the actual twist orders. Factors of n−1 and twist-order-minus-one do not factor the curve groups. Pohlig–Hellman uses the group order; smooth n−1 does not weaken a prime-order curve by that method.

The observed ratio 11/21 is not a historical rejection probability. No sampling model or equivalence test supports “statistically indistinguishable,” and the checked traits identify no universal selection rule. The trace graph and selection diagram were rechecked against the exact records and need no changed point or edge. The checked canonical frontiers also gain no new established mechanism edge. An estimate near 30 bits of search freedom is conditional on an assumed timestamp window and candidate cap. The historical selection procedure and any proposed withheld mathematical route remain separate open questions.

== Sources and reproducibility

- Valsorda, #link("https://words.filippo.io/seeds-solved/")[The NIST Elliptic Curves Seeds Bounty Has Been Claimed], 16 October 2026 [retrieved].
- Anthropic, #link("https://www.anthropic.com/research/ecdsa-curve-origins")[Claude reveals ECDSA curve origins], 16 October 2026 [retrieved].
- NIST, #link("https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf")[SP 800-186], Appendix C.3.1 [retrieved].
- Local exact records: traits.json, assessed.json, audit.py, postprocess.py and run logs [internal].
- Supplemental 21-curve screen and published-control correction: supplemental_checks.py and supplemental_checks.json [internal].
