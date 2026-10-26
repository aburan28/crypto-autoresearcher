#set page(paper: "a4", margin: (x: 18mm, y: 16mm))
#set text(font: "DejaVu Sans", size: 9.5pt)
#set par(leading: 0.66em)

= BINSTD archived toy outcome audit
_26 October 2026 · crypto-autoresearcher main `6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad`_

This is a source-bound audit of four archived `n=17`, `ell=8/9` cells. It adds
no run or timing measurement.

== Inputs and independent check

The four frozen sheriff per-target receipts name 160 targets, 276 positive
hit witnesses and 44 misses. `check.py` rehashes six source/archive paths per receipt at
their historical commits; it checks receipt, raw-result and yield-matrix
bindings. It verifies all targets and witness triples on the curve
`y²+xy=x³+1` using independent interleaved field multiplication and Euclid
inversion, and rejects an on-curve witness mutation in each cell. The addition
formula is checked against SEC 1 v2 §2.2.2. It matches all seeded targets
exactly, and factor-base sizes and pair-sum cardinalities to the receipts, then independently
enumerates all base-pair sums and target-minus-base-point lookups. Each hit
and miss flag agrees; a deliberately flipped false hit is rejected where
misses exist.

#image("hits.svg", width: 100%)

== Observation

#table(
  columns: (2fr, 1.2fr, 1.2fr, 1.2fr), inset: 5pt,
  [Cell], [Tau hit/miss], [Open hit/miss], [Witnesses],
  [ell89 / ell 8], [16/24], [40/0], [56],
  [ell89 / ell 9], [40/0], [40/0], [80],
  [ell89r1 / ell 8], [20/20], [40/0], [60],
  [ell89r1 / ell 9], [40/0], [40/0], [80],
)

All archived count pairs satisfy the premises of the *conditional* Lean
`YieldCeiling.saturated_open_below_band` theorem. Exhaustive finite trial
division independently checks that the archived `t^17+t^3+1` modulus and
degree-eight factors are irreducible, and their product is `X^17+1`. This is
computed evidence. A new Lean theorem also kernel-checks the 510/30/30 exact
*bitmask* divisor trials using `decide`; its axiom audit lists only `propext`.
It does not yet prove polynomial irreducibility.
A separate set-polynomial Rabin test obtains Frobenius residue `X` and GCD `1`
for all three masks; reducible `X^17+1` and `X^8+1` controls fail.

== Boundary and next check

The finite exhaustive check covers each reported miss for the *source-generated*
factor bases and targets. It does not establish the original host's input
selection, per-target execution or timing. The normal-basis/Frobenius bridge
is also not formalized. Obtain the original trace or execution proof; then
prove that the encoded remainder agrees with `(ZMod 2)[X]`, identify the
archived masks with the polynomial factors, and prove the Frobenius bridge.

Source: `research/binstd_end_to_end_20261026/REPORT.md`, `evidence.json`,
`formal/CryptoResearch/Binstd/EncodedDivisors.lean`, and
SEC 1 v2 §2.2.2 (https://www.secg.org/sec1-v2.pdf). Rabin's criterion:
https://doi.org/10.1137/0209024.
