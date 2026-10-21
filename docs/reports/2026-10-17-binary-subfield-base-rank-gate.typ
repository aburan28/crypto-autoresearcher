#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Proper-subfield x bases and large-prime rank

*Derived conditional lemma, 2026-10-17 UTC.* Let E descend to Fq, where
q=2^d and d is a proper divisor of n. For a point P with x(P) in Fq,
q-Frobenius fixes x(P), so Frobenius(P)=+P or −P. Applying its characteristic
polynomial gives (q+1−t)P=O or (q+1+t)P=O, where |t|≤2√q.
Thus any prime factor of the order of P is at most q+1+⌊2√q⌋.

#image("2026-10-17-binary-subfield-base-rank-gate.svg", width: 100%)

#table(
  columns: (1fr, 1fr, 2fr), inset: 5pt,
  [Ambient n], [Largest proper d], [Maximum point-order ceiling],
  [50], [25], [33,566,018],
  [53], [1], [5],
  [63], [21], [2,100,049],
)

The diagram compares these exact ceilings with the explicit condition
r≥2^(n−1). The reviewed n=53 Koblitz comparator has r=21,044,858,204,113;
this is below that illustrative threshold but above its actual ceiling 5.
A pure subfield x base therefore has zero projected rank in that target group.

== Scope and next test

This proof requires E to descend to the selected subfield. It does not cover
non-descended ordinary-binary curves, near-subfield sets, displaced sparse
predicates, or any complete-cost advantage. The next gate is a target-blind
base with independently verified nonzero projected points and rank, then
matched-size solver and complete ECDLP comparisons. The canonical frontier
graph is unchanged.

Proof and provenance: companion Markdown report; exact integers:
research/icperf_subfield_rank_gate_20261017/hasse_bounds.json.
