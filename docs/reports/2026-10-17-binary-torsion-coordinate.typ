#set page(paper: "us-letter", margin: 0.58in)
#set text(font: "New Computer Modern", size: 9.2pt)
#set heading(numbering: "1.")

= Torsion-adapted affine coordinate for binary index calculus

_2026-10-17 · Target-blind input preparation and independent Sage replay. No index-calculus cost comparison._

The certified curve is $y^2+x y=x^3+31$ over $"GF"(2^61)$, with group order $4r$ and prime $r=576460752557211763$. Its rational two-torsion point is $T_2=(0,2147483661)$. A fourth root $gamma=70364449406991$ satisfies $gamma^4=31$ and $gamma^2=2147483661$ in the field.

== Coordinate and three-point identity

Set $t=phi(P)=gamma/(x(P)+gamma)$, so $x=gamma(1+1/t)$ away from the poles. The addition law gives $x(P+T_2)=gamma^2/x(P)$ and $phi(P+T_2)=phi(P)+1$. For three coordinates, let $e_1=t_1+t_2+t_3$ and $s_3=product_i(t_i^2+t_i)$. The characteristic-two relation is $P_(phi,3)=s_3+gamma e_1^2=0$. Substitution into the binary Semaev polynomial yields $S_3 (t_1 t_2 t_3)^2=gamma^3 P_(phi,3)$ wherever the denominators are nonzero. Sage checked 32 true and 32 false triples independently. The compact input formula establishes neither degree of regularity nor solver runtime.

== Affine input and recorded counts

The coordinate subspace $V="span"_(F_2){1,z,dots,z^9}$ is stable under $t mapsto t+1$. The equation $L_V(t)=L_V(c)$ has 11 nonzero Frobenius terms plus an affine constant, equivalent to 51 binary-linear constraints. Four predetermined offsets each scan 1,024 values. A point and its two-torsion partner become the same sign-folded subgroup log column after multiplication by four.

#figure(image("2026-10-17-binary-torsion-coordinate.svg", width: 82%), caption: [Recorded raw representatives and distinct projected log columns. Every pair and sign was independently replayed in Sage. Input counts only.])

Offsets 1024, 2048, 3072, 4096 yield respectively 267, 253, 237, 249 unique columns from 534, 506, 474, 498 raw representatives. The target-blind rule selects 1024 as nearest to the derived $m=8$ default of 287 columns. A seeded paired-random control has 267 columns and 534 raw representatives from 489 draws. Input preparation recorded 83.729985 s wall, 12.419274 s CPU and 69,484,544 bytes peak RSS on a shared host. This does not compare whole ECDLP cost.

== Scope and next test

Faugère, Huot, Joux, Renault and Vitse report a torsion-symmetrized eighth polynomial with 470,369 invariant monomials and 40.5 CPU hours of historical Magma construction. Their extension-field factor base and timing do not transfer to this input. An eighth summation polynomial represents seven summands plus target. Eight summands require a ninth polynomial or a chained system, both unconstructed here. The next frozen comparison must price the coordinate construction, full solver behavior, useful rank, four target torsion channels, linear algebra, verification, memory, and matched rho on identical unseen targets. The full-width arity-grid obstruction remains open.

Sources and full data: `research/icperf_binary_torsion_coordinate_20261017/base.json`, `research/icperf_binary_torsion_coordinate_20261017/sage_replay.json`, and the companion Markdown report with the retrieved primary-paper text. Canonical frontier graphs were checked and remain unchanged.
