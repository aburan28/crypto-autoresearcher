#set page(paper: "a4", flipped: true, margin: (x: 15mm, y: 13mm))
#set text(size: 8.5pt)
#set par(justify: true)
#set heading(numbering: none)

= Why did the eleven qualifying seed candidates go unpublished?

_Historical selection audit · 16 October 2026 · exact data and code in the accompanying study directory_

#image("seed_slots.svg", width: 100%)

== Supported answer

The recovered timestamp-initialized lrand48 streams reproduce all ten published prime-field seeds. Eleven other reported 20-byte blocks in those streams produce valid prime-order curves under the same seed-to-coefficient procedure. Four precede a NIST curve: one before P-256 and three before P-224. Seven lie in the two May 1997 streams that produced the ANSI example curves. A qualifying block in a reconstructed stream is not proof that the original program evaluated and rejected it.

The checked ordinary criteria do not separate the published curves from the passed-over ones. Rules requiring n < p, positive trace, prime twist, no small twist factors, or the first qualifying block all fail a published control. A bounded PARI/GP factorization comparison also refutes a uniform preference for a larger prime factor of the twist order: some passed-over 192- and 239-bit curves have larger factors than an earlier published curve over the same field. A historical cause remains unknown.

== What the historical standard establishes

FIPS 186-2 Appendix 6.4 says to choose an arbitrary 160-bit seed, derive the curve coefficient through SHA-1, and test for suitable order. It does not prescribe the seed progression or retain an acceptance log. Appendix 6.5 lets a reader verify the published seed-to-coefficient relation only. The source-bound earlier assessment checked the eleven exact groups by Sage point counting, proven-prime order, point-order and Hasse uniqueness, and found cofactor one for all. Its 21-curve bounded modular screen found no embedding degree at or below one million; the skipped classes had no CM-field discriminant at or below two million in absolute value. Those bounds are not complete endomorphism-ring or isogeny audits.

#pagebreak()

== Selection hypotheses and counterexamples

#set par(justify: false)
#table(
  columns: (58mm, 168mm, 39mm),
  inset: 4pt,
  stroke: 0.4pt + gray,
  [Candidate rule], [Observed counterexample or missing evidence], [Result],
  [First qualifying block], [P-256 follows slot 876; P-224 follows slots 777, 1485 and 5736. The 239-bit stream is interleaved.], [Refuted],
  [Require n < p or positive trace], [Published prime239v2 has n > p and negative trace. Eight skipped classes have n < p.], [Refuted globally],
  [Require no small twist factor], [Nine of ten published curves have a twist factor at most 10,000.], [Refuted globally],
  [Require a larger twist prime factor], [Skipped 192-bit slots 2198 and 5405 have largest certified factors of 170 and 181 bits; published prime192v1 has 95 bits.], [Refuted globally],
  [Per-field twist or other rule], [P-224 has 118-bit largest twist factor versus 83 and 106 bits for two omissions, but slot 1485 timed out. No criterion or historical record was found.], [Open],
  [Same RNG consumed by other work], [All published seeds remain aligned to 20-draw boundaries; May 1997 published base points use a distinct FreeLIP generator. Other calls remain possible.], [Open],
  [Historical arithmetic or bookkeeping error], [Current computations confirm eleven suitable orders, but no historical program or defect is available to replay.], [Open],
)
#set par(justify: true)

== The eleven passed-over classes

The ordinal is a one-based 20-byte block position. Trace is t/(2√p), where t = p + 1 − n. L is the bit length of the largest certified prime factor of the quadratic-twist order after PARI/GP factorization. A question mark means the 20-second residual-factorization limit expired. Full seed bytes, curve equations, group orders and EC1 identities are in the linked earlier assessment.

#table(
  columns: (27mm, 27mm, 26mm, 57mm, 20mm, 108mm),
  inset: 3pt,
  stroke: 0.4pt + gray,
  [Field / slot], [Trace], [n > p], [Twist factors ≤ 10,000], [L], [Relevant comparison],
  [239 / 36], [+0.730], [No], [139], [138], [Published prime239v1 has L = 86.],
  [239 / 1562], [−0.113], [Yes], [41], [179], [Published prime239v2 also has n > p.],
  [239 / 2491], [−0.151], [Yes], [43, 173, 307, 953], [129], [Small twist factors occur in published controls.],
  [239 / 2682], [−0.062], [Yes], [29], [?], [Square factor of 5 in Frobenius discriminant also occurs in prime239v2.],
  [239 / 2863], [+0.447], [No], [none found], [125], [No twist factor ≤ 10,000, yet passed over.],
  [192 / 2198], [+0.815], [No], [11, 127, 5827], [170], [Remaining twist factor is prime; published P-192 has L = 95.],
  [192 / 5405], [+0.472], [No], [7, 19²], [181], [Remaining twist factor is prime; other published 192-bit L values are 139 and 161.],
  [256 / 876], [+0.156], [No], [3, 11, 37, 8081], [201], [P-256 has L = 241; one pair does not establish a rule.],
  [224 / 777], [+0.376], [No], [3, 5, 683], [83], [P-224 has L = 118.],
  [224 / 1485], [+0.015], [No], [3, 31], [?], [Complete twist factorization timed out.],
  [224 / 5736], [+0.311], [No], [3, 1607, 3371], [106], [P-224 has L = 118.],
)

== Inference boundary

The 18 completed twist factorizations give exact factors; three residuals timed out, so their L is unknown. A large twist prime factor is a structural feature, not an ECDLP or protocol-security verdict. The two P-224 coefficient signs for each seed are isomorphic, leaving three seed-level classes. Every ordinary group order here is prime, so factors of n − 1 are irrelevant to Pohlig–Hellman on that group.

The reported stream slots do not reveal how many timestamps or alternative generator runs were tried. A 30-bit search-space illustration assumes a year-scale time window and a small fixed candidate cap; it is not a measured historical upper bound. Deliberate selection of a weak instance, an unpublished method applicable to honest instances, and an implementation flaw require separate evidence. An explicit hidden route would also need subgroup-preserving maps, recovery and verification, discovery cost, and cold-start versus amortized cost accounting.

The unresolved historical step is tracked in problems/nist-seed-selection-rule-unexplained.md. A provenanced original generator and call trace, or a predeclared rule that predicts independent historical decisions, would be discriminating evidence. The new stream plot changes no established isogeny or attack edge in knowledge/frontiers/ecdlp/.

== Sources and reproducibility

Retrieved: #link("https://www.anthropic.com/research/ecdsa-curve-origins")[Anthropic's discovery], #link("https://words.filippo.io/seeds-solved/")[Valsorda's candidate list], and #link("https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf")[FIPS 186-2 Appendices 6.4–6.5]. Internal exact inputs: assessed.json, traits.json, supplemental_checks.json. New reproducible data: selection_matrix.json and twist_factor_probe.json, generated by the adjacent scripts. Full citations and limits are in report.md.
