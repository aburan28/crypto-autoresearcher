#set page(paper: "a4", margin: 1.65cm)
#set text(size: 10pt)
#set par(justify: true)

= What remains open in NIST prime-curve seed generation?

_16 October 2026. Derived historical-process assessment of ten published and eleven reported passed-over qualifying blocks._

The ten published prime-field seeds are exact 20-byte blocks from six timestamp-initialized `lrand48` streams. The missing historical fact is why eleven other reported blocks in those streams, also yielding prime-order curves of the required size, were passed over. The original program might not have evaluated every window. The complete data and citations are in #link("report.md")[the Markdown report], with exact derived checks in #link("process_checks.json")[process_checks.json].

#figure(image("process_space.svg", width: 100%), caption: [Known seed source, unknown acceptance step, and the two state-space ceilings.])

== What the new check rules out

For all 17 reported qualifying blocks with `p mod 4 = 3`, the recorded prime-order coefficient is the usual exponentiation square root of `-27/c`, including all eight passed-over blocks in those fields. The other four blocks are P-224: its two coefficient signs define isomorphic curves, so sign choice cannot disqualify its three passed-over blocks. All 21 satisfy the checked ANSI order-size and MOV screens. These results rule out a simple fixed-sign or documented-order-filter explanation for the reported omissions.

The earlier exact audit also found that a rule requiring positive trace, `n < p`, or a twist without small prime factors conflicts with published controls. A later factorization showed that passed-over P-224 block 1485 has a 122-bit largest twist prime factor, versus 118 bits for published P-224. Maximizing that twist metric cannot explain the choice.

== How much generator choice remains?

The 48-bit `lrand48` recurrence has a full `2^48`-state cycle. `srand48(t)` fixes the low 16 state bits to `0x330E`. The first output state of each consecutive 20-draw block is 1 modulo 4, and moving to the next block advances 20 states. Since `gcd(20, 2^48)=4`, a complete strict-block stream visits exactly `2^46` possible first states; changing the timestamp changes the starting position within that set. Thus at most `2^46` distinct 20-byte seeds are available under the exact reconstructed block rule, irrespective of timestamp restarts. Extra calls *between* 20-byte windows allow any start state and raise the ceiling to `2^48`. Both ceilings assume consecutive draws *within* each candidate; changing that rule is a different model. They count possible generator states, not observed attempts.

#figure(image("stream_counts.svg", width: 100%), caption: [The 21 reported qualifying blocks; orange blocks were passed over.])

== Remaining process models

Extra generator calls could bypass otherwise qualifying windows, but must reproduce the observed 20-draw alignment of published seeds. A historical point-count or certificate implementation could reject curves that modern arithmetic verifies, but no such failure has been reproduced. An additional curve-quality test or manual choice is logically possible; it needs a rule specified before testing an independent historical decision. Arbitrary timestamp restarts are also uncounted. The six May 1997 published base points were reconstructed using a separate FreeLIP generator, weakening one specific same-stream consumption explanation for those six.

The fastest decisive evidence is a provenanced copy of Bob Reiter's program, call log, or contemporary output files. A second route is a frozen process model that predicts independent historical selections. Neither the reported 21 labels nor the `2^46` ceiling establishes how many candidates were actually inspected, a hidden mathematical weakness, or a universal security conclusion.

_Sources:_ #link("https://www.anthropic.com/research/ecdsa-curve-origins")[Anthropic's reconstruction]; #link("https://words.filippo.io/seeds-solved/")[Valsorda's candidate list]; #link("https://pdfcoffee.com/x9-62-1998-ecdsa-pdf-free.html")[text copy of ANSI X9.62-1998]; #link("https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf")[FIPS 186-2]; prior internal research and source hashes in #link("report.md")[the full report].
