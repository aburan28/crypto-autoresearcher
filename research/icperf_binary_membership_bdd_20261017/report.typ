#set page(paper: "a4", margin: 17mm)
#set text(size: 10pt)

= Exact membership encoding screen for two binary factor bases

*Scope.* Target-blind structural search on the certified ordinary-binary GF(2^61)
fixture, subgroup order 576460752557211763, cofactor 4. The two archived k11
bases each contain 316 projected columns and 632 accepted coordinates in one
11-bit affine block. No solver, relation collector, degree-of-regularity
measurement, rank calculation, or end-to-end comparison was run.

#align(center)[#image("figure.svg", width: 88%)]

== Exact input calculation

`analyze.py` reads the archived weighted and matched local-random bases and
their XCNF manifests. It checks the algebraic normal form and both reduced
ordered decision diagrams against all 2,048 Boolean inputs per predicate.
The proposed BDD clause count uses one node variable, conditional equivalence
clauses for each edge, and an accepted-root unit per independent block.

#table(
  columns: (1fr, auto, auto),
  inset: 5pt,
  [*Quantity*], [*Weighted*], [*Local random*],
  [ANF terms / degree], [520 / 9], [516 / 9],
  [BDD nodes, low-bit-first], [188], [212],
  [BDD nodes, high-bit-first], [193], [216],
  [Archived forbidden clauses, eight blocks], [11,328], [11,328],
  [Proposed BDD clauses, eight blocks], [5,640], [6,424],
  [Additional BDD variables, eight blocks], [1,504], [1,696],
)

The archived full channel-0 formulas contain 89,122 CNF clauses and 62,655
native XOR rows for both bases. Substitution of only the membership clauses
would imply 83,434 and 84,218 CNF clauses, plus the added variables shown.
This is a derived description of an unbuilt encoding. Formula clause count,
ANF degree, degree of regularity, solver time, and complete index-calculus
cost are distinct quantities.

== Provenance and next check

The exact base and manifest SHA-256 values, source digest, execution command,
and full computed counts are in `result.json`. `result_initial.json` preserves
a scratch metadata error in the first output: its timestamp was sampled after
the calculation. The corrected output samples it before the calculation.
The numerical results agree. Provenance for the frozen base and manifest
records: internal; all other counts above are derived from those exact bytes.

Next, serialize the BDD encoding and independently replay its truth table and
planted full-point controls. Compare both bases and both encodings on one
frozen common-target panel under an admitted protocol. Charge generation,
solver, model filtering, useful rank, linear algebra, target work, and matched
rho before interpreting any whole-pipeline effect.

No canonical ECDLP cost graph was changed; this search establishes input
predicate representation counts only.
