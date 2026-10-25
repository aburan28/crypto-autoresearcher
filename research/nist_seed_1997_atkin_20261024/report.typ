#set page(paper: "a4", margin: (x: 16mm, y: 16mm))
#set text(font: "Helvetica", size: 9.5pt)
#set par(justify: true)

= Atkin information changes the point-counting comparison

*24 October 2026 UTC. Source-bound arithmetic audit of nineteen NIST/ANSI seed candidates.*

Including Atkin trace information changes the earlier Elkies-only comparison from 24 of 25 same-field pairs favoring an earlier cutoff for the omitted curve to *20 earlier, three later, and two ties*. The P-256 pair now ties, and the 192-bit field has mixed directions. Neither measure supplies one threshold separating all eleven omissions from the eight published controls.

== A method available before the seed streams

Schoof's 1995 paper, printed pages 239–242, describes projective Frobenius order, Atkin trace restrictions and the additional search needed to resolve ambiguous residues. The source predates the recovered timestamp inputs; it does not identify the original parameter-generator program. The source PDF's digest and visually inspected pages are bound in source.json.

For each of 167 odd primes $ell <= 997$, the frozen protocol keeps one exact trace residue in the Elkies case, the two possible trace residues in the ramified case, and every trace with the observed projective Frobenius order in the Atkin case. The archived scan contains *3,173 cells*. An independent Sage path uses eigenvalue ratios in $"GF"(ell^2)$ to reconstruct *945 distinct Atkin sets* and checks all *1,613 real Atkin cells*, every other cell, and every cutoff.

== The declared information proxy

Let $M$ be the product of primes scanned and $A$ the product of the numbers of allowed residues. There are exactly $A$ allowed CRT classes modulo $M$. The declared cutoff is the first prime for which

$ M^2 > 16 p A^2. $

This density criterion does not guarantee a unique trace in the Hasse interval. It omits modular-polynomial work, the cost of acquiring projective orders, and the final ambiguity search. It is not a historical runtime model.

#table(
  columns: (0.8fr, 2.5fr, 1.8fr, 1.1fr), inset: 5pt,
  [Field], [Omitted cutoffs], [Published cutoffs], [Earlier / later / tie],
  [192-bit], [127, 113], [113, 107, 137], [2 / 3 / 1],
  [P-224], [113, 137, 149], [163], [3 / 0 / 0],
  [239-bit], [127, 109, 131, 137, 131], [139, 139, 139], [15 / 0 / 0],
  [P-256], [151], [151], [0 / 0 / 1],
)

#image("inference.svg", width: 100%)

_Solid edges show source and arithmetic checks. The historical program and decision log remain missing. Editable source: inference.dot._

The first Sage verification stopped on an API call. Its code and traceback remain archived; the corrected complete replay passed without changing the metric. See VERIFIER_CORRECTION.md. Full source URLs, exact curve UIDs, code and protocol hashes, raw records, controls and commands are linked in report.md. No historical acceptance or ECDLP weakness is established by this comparison.

#pagebreak()

== All nineteen paired cutoffs

#image("cutoffs.svg", width: 100%)

_Diamonds give the new residue-density cutoff; open circles give the prior strict Elkies-only cutoff. Units are prime values. Exact finite sample: nineteen curves, twenty-five same-field pairs. Source: runs/scan-v1/raw.json; independent replay: runs/verification-v2/verification.json; editable chart: render.py._

Published and omitted cutoffs remain mixed in the 192-bit field, and P-256 ties. A source-identical point-counter with its invocation and candidate log would resolve more than further tuning of retrospective proxies. The open selection-rule problem's exit conditions remain unmet.
