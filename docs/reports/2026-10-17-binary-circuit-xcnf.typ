#set page(paper: "us-letter", margin: (x: 0.7in, y: 0.6in))
#set text(font: "Arial", size: 9.3pt)
#set par(leading: 0.5em)

= Membership-constrained binary m=8 circuit inputs

*2026-10-17 · Prepared and checked solver inputs, without a solver trial*

On the certified ordinary-binary GF(2^61) fixture, two selected bases feed seven three-point equations for one raw target channel. Every external coordinate is constrained to its exact target-blind accepted-value set. Live AND gates become three CNF clauses; XOR gates remain native parity rows; all 427 equation output bits are fixed to zero. This is a fixed schoolbook circuit encoding, with no curve-lift, sign, pole or other-channel branches.

#table(
  columns: (auto, auto, auto, auto, auto),
  inset: 5pt,
  stroke: (bottom: 0.35pt + rgb("CCD8DE")),
  [*Selected arm*], [*Allowed / space*], [*CNF variables*], [*CNF clauses*], [*XOR rows*],
  [Torsion φ], [534 / 1,024], [86,559], [79,626], [61,020],
  [Raw x], [265 / 512], [137,744], [130,029], [94,764],
)

#image("2026-10-17-binary-circuit-xcnf.svg", width: 100%)

A separate parser checked both compressed formula hashes, every gate definition, all eight complete coordinate-membership truth tables per arm, and the serialized formula's counts. For torsion φ, the archived planted primary assignment extends to every gate and satisfies all 79,626 CNF clauses and 61,020 XOR rows. The underlying point sum had independent Sage verification. The raw-x arm has no supplied satisfying assignment for that torsion-selected target; no satisfiability conclusion follows. Retained tiny format controls confirmed the installed CryptoMiniSat binary's `x` and `x-` parity syntax; neither selected formula was given to a solver.

*Boundary.* Additional point lifts, signs, poles, three other target channels, root certificates, useful-rank deduplication, linear algebra and complete phase costs remain. Exact source, gzip artifacts, digests and verification: `docs/reports/2026-10-17-binary-circuit-xcnf.md`.
