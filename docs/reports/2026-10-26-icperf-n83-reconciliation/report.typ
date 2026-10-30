#set page(paper: "us-letter", margin: (x: 0.7in, y: 0.55in))
#set text(font: "New Computer Modern", size: 9.5pt)
#set par(justify: true)

= Koblitz N83 baseline in the requested subgroup range
_Source reconciliation · 26 October 2026 · no new trial or performance claim_

The 16 October ICPERF assessment identified its local GF(2^53) comparator as a
45-bit subgroup. The current cryptanalysis baseline ledger also has Koblitz
N83 on curve `EC1N83Ce1h35c7ced6b497`, with subgroup order
`8,569,786,107,849,059` (52.93 bits). This is an in-range reference, but
the measured cold cost excludes factor-base construction. The full
three-family, arity-2-through-8 comparison remains open.

== Current source row

The ledger at cryptanalysis main commit `e7cf096b4e2f9020e1326e4ed0b5ac0e96cc99f9`
names rank-finder run `39527997793` as the N83 baseline. It reports 12 new
public points, 36 alternating predecessor/current pairs, same-point tuned
rho, and 282 valid rows. The source's paired cold ratio is 1.0196 with a
95% interval of [1.0147, 1.0255]. Its A/A cold control is 0.9982
[0.9928, 1.0036]. This PDF has not independently replayed those receipts.

The same run reports normalized IC S=0.4466 and rho S=0.1138, a point
IC/rho ratio of 3.9242. No interval was computed for that ratio in the
source run. The fixed recipe uses a K600 orbit base with a PDP4/S3-root-index
path; it does not measure every requested arity.

#figure(
  image("phase-chart.svg", width: 100%),
  caption: [Source-ledger N83 phase map. Rank, setup and online are from run
  39527997793; factor-base construction is from separate replay 39007026856
  on another host class. The separate bar is excluded from the current cold
  IC total.]
)

== Charging boundary and next measurement

The current run timed 2,806.5 ms of rank work, 4,308.5 ms of subsequent
setup, and 158.6 ms online. Root-index construction (about 3.25 s) and
self-test (about 0.84 s) are already inside setup. The K600 factor base was
loaded from a file. A different host class measured 427.524 ms of base
construction, which cannot be inserted into the current run to form an
accepted same-host total. The reported IC S is a lower bound on a cold total
that charges nonnegative construction time.

The discriminating comparison freezes the current N83 producer and same
unseen points, charges target-blind base construction through certificates
and verification, and runs matched rho in the same environment. An elite
orbit-base arm needs its own construction cost and a direct pairing against
this producer; an earlier K899 result used a different predecessor. Prime
and ordinary-binary complete rows and m=2..8 remain separate obligations.

== Source

Cryptanalysis `docs/ic/BASELINES.md` (Git blob
`4a444fac7f5c61992559a57601ee03c48cddab55`) and `baselines.json`
(Git blob `8cfddf76272ab0ffb3f5d3c71bdad1e0cba4928e`) at the pinned
commit above. Full links, distinctions and limitations are in `README.md`
beside this PDF. No scientific status or claim record changes here.
