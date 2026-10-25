#set page(paper: "a4", margin: (x: 17mm, y: 16mm))
#set text(font: "Helvetica", size: 9pt)
#set par(justify: true)

= A fixed minimum-order threshold cannot explain the eleven omissions

*2026-10-24 UTC. Post-observation, source-motivated audit.*

The 17 November 1997 ANSI X9.62 draft permits an operator-supplied minimum subgroup order $r_("min")$. For a prime full-order curve, the draft's test accepts exactly when $n >= r_("min")$. Across the four reconstructed fields with named omissions, any field-fixed minimum that admits all eight published controls also admits *seven of the eleven* omitted candidates. This excludes that one simple threshold as a complete selection rule, conditional on the original program having visited those positions.

== The exact comparison

Let $m = min(n_("published"))$ within one field. To admit all published curves, $r_("min") <= m$. Every omitted curve with $n_("omitted") >= m$ must then pass. A complete separator exists exactly when $max(n_("omitted")) < m$.

#table(
  columns: (1.15fr, 0.8fr, 0.8fr, 2.3fr),
  inset: 5pt,
  [Field], [Published], [Omitted], [Unavoidable omitted ordinals],
  [192-bit], [3], [2], [5405],
  [224-bit], [1], [3], [777, 1485, 5736],
  [239-bit], [3], [5], [1562, 2491, 2682],
  [256-bit], [1], [1], [none],
)

#image("order_ranks.svg", width: 100%)

_Figure 1. Within-field exact order ranks. Blue denotes publication; orange denotes an omission. Shaded positions pass every lower threshold that admits all published curves in that field. Spacing is rank rather than numeric distance. Source: analysis.json; editable source: render.py._

In the P-224 field, all three omitted orders exceed the published order. The 192- and 239-bit sets interleave. Only the P-256 pair permits a field-specific separating threshold; such a value would exceed the draft's advised upper bound $p+1-2 sqrt(p)$, under which every full-prime-order candidate passes.

== Evidence and limit

The source-pinned audit matched 19 exact $(p,n)$ rows to prior prime-order point certificates. An independent script recomputed the pairwise inequalities from the archived omitted and published rows. This is not evidence that the 1997–98 program evaluated all eleven positions, used a fixed threshold, or rejected any for a weakness. A changing threshold or another test remains possible. The original program or candidate log is the decisive missing source.

#image("inference.svg", width: 83%)

_Figure 2. Solid edges are source or arithmetic checks; the dashed historical edge is unknown. Editable source: inference.dot._

*Sources:* ANSI X9.62 working draft, 17 November 1997, sections F.2.2 and F.3.2; hash-pinned curve, label and certificate records. Exact URLs, digests, method and limits: report.md, analysis.json and SCOPE.md.
