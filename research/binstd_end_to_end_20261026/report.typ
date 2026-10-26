#set page(paper: "a4", margin: (x: 18mm, y: 16mm))
#set text(font: "DejaVu Sans", size: 9.5pt)
#set par(leading: 0.66em)

= BINSTD archived toy witness audit
_26 October 2026 · crypto-autoresearcher main `6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad`_

This is a source-bound audit of four archived `n=17`, `ell=8/9` cells. It adds
no run or timing measurement.

== Inputs and independent check

The four frozen sheriff per-target receipts name 160 targets and 276 positive
hit witnesses. `check.py` rehashes six source/archive paths per receipt at
their historical commits; it checks receipt, raw-result and yield-matrix
bindings. It verifies all targets and witness triples on the curve
`y²+xy=x³+1` using independent interleaved field multiplication and Euclid
inversion, and rejects an on-curve witness mutation in each cell. The addition
formula is checked against SEC 1 v2 §2.2.2.

#image("hits.svg", width: 100%)

== Observation

#table(
  columns: (2fr, 1fr, 1fr, 1.2fr), inset: 5pt,
  [Cell], [Tau], [Open], [Witnesses],
  [ell89 / ell 8], [16/40], [40/40], [56],
  [ell89 / ell 9], [40/40], [40/40], [80],
  [ell89r1 / ell 8], [20/40], [40/40], [60],
  [ell89r1 / ell 9], [40/40], [40/40], [80],
)

All archived count pairs satisfy the premises of the *conditional* Lean
`YieldCeiling.saturated_open_below_band` theorem. Exhaustive finite trial
division independently checks that the archived `t^17+t^3+1` modulus and
degree-eight factors are irreducible, and their product is `X^17+1`. This is
computed evidence, not an added Lean proof.

== Boundary and next check

The checker validates positive witnesses but does not independently prove
every reported miss. No original per-target execution trace or host timing
certificate is established. The normal-basis/Frobenius bridge is also not
formalized. Obtain the original trace or execution proof; then add a pinned
Lean irreducibility and model-bridge proof with axiom and semantic review.

_Source: `research/binstd_end_to_end_20261026/REPORT.md`, `evidence.json`, and
SEC 1 v2 §2.2.2 (https://www.secg.org/sec1-v2.pdf)._
