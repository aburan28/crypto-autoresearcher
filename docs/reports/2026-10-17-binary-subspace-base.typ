#set page(paper: "a4", margin: 17mm)
#set text(size: 9pt)
#set heading(numbering: none)

= Binary affine-subspace factor-base input

*Preparation record, 2026-10-17 UTC.* On the certified ordinary-binary
GF(2^61) curve with prime subgroup order r=576,460,752,557,211,763, fix
V=span_F₂{1,z,…,z¹⁰}. Before target selection, scan four affine offsets
2048, 4096, 6144 and 8192. Keep liftable x with an order-r point, one
y representative per x and both signs implicit. Choose realized size nearest
the m=8 default B=287, then generate an equal-size random-x control.

#image("2026-10-17-binary-subspace-base.svg", width: 100%)

#table(
  columns: (1.3fr, 1fr, 1fr, 1fr), inset: 5pt,
  [Arm], [Lift fails], [Outside r], [Accepted x],
  [Offset 2048, selected], [995], [804], [249],
  [Offset 4096], [1,025], [775], [248],
  [Offset 6144], [1,028], [775], [245],
  [Offset 8192], [1,024], [788], [236],
  [Random control], [1,099], [797], [249],
)

The subspace polynomial Q(X) has 12 nonzero Frobenius terms and kernel V.
The affine-x prefilter Q(X)+Q(c)=0 has 13 nonzero field terms and 50 independent
F₂-linear constraints. Exact membership in this base also requires a curve
lift and the order-r subgroup predicate; its solver cost is not measured.
Sage independently replayed
all four scans, the 2,145 random-control draws, point coordinates, subgroup
membership and the predeclared selection rule.

Preparation including rejected offsets and control: 56.143 s wall,
38.774 s CPU, 68,960,256 bytes peak RSS on this shared host. This is
descriptive setup cost, not a solver or end-to-end speed comparison. The
field's multiplicative group has prime order 2^61−1, so no useful proper
multiplicative-coset divisor exists on this exact field.

The next design must price that subgroup predicate or an all-liftable,
cofactor-projected base with explicit torsion handling. Input sparsity alone
does not establish a lower degree of regularity. Relation yield, rank and target recovery,
matched rho, m=2…7 and direct S₈/S₉ comparisons remain unmeasured.

Data and source-bound Sage replay: research/icperf_binary_subspace_base_20261017/.
