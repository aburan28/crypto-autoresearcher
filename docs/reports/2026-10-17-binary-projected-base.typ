#set page(paper: "us-letter", margin: 0.62in)
#set text(font: "New Computer Modern", size: 9.5pt)
#set heading(numbering: "1.")

= Cofactor-projected affine base on an ordinary binary curve

_2026-10-17 · Input construction and independent Sage replay; no index-calculus speed claim._

The exact fixture is $y^2 + x y = x^3 + 31$ over $"GF"(2^61)$ with field polynomial $z^61 + z^5 + z^2 + z + 1$ and group order $4r$, where $r = 576460752557211763$ is prime. The target subgroup has 60-bit order. The fixture certificate, producer, input record, and Sage replay are linked in the companion Markdown report.

== Sparse raw base

Let $V = "span"_(F_2){1,z,dots,z^8}$. The linearized polynomial $L_V(X)=product_(v in V)(X+v)$ has exact kernel $V$. For each predetermined offset $c$ in ${512,1024,1536,2048}$, the raw decomposition points have liftable x coordinates satisfying $L_V(x)=L_V(c)$. The polynomial has 10 nonzero Frobenius terms, plus the affine constant. Each placement scans 512 x values. The selected offset minimizes the gap to the default $m=8$ base size $B=287$ before target selection.

#figure(image("2026-10-17-binary-projected-base.svg", width: 90%), caption: [Measured realized base representatives at four predetermined offsets; all counts were independently replayed in Sage. These are input counts, not solver outcomes.])

The counts are 263, 263, 265, and 264; $c=1536$ is selected. An equal-size seeded random control needed 517 draws to retain 265 liftable x values. Preparation recorded 9.642826 s wall, 5.599027 s CPU, and 69,500,928 bytes peak RSS on a shared host. The timings describe this one preparation process only.

== Exact projection and target channels

For a raw point $P_i$, the log column is $F_i=[4]P_i$ in the order-$r$ subgroup. For target $R$, let $R_0=[4^(-1) mod r]R$ and choose order-four $T=[r]P_"source"$. Its four raw preimages are $R_0+j T$, $j in {0,1,2,3}$. Therefore a raw equality $sum_i P_i=R_0+j T$ implies $sum_i F_i=R$. The independent replay checked all four channels, one public scalar-17 target, and a planted three-point sum. The four-channel work remains unpriced.

The sparse predicate applies to raw x coordinates; subgroup columns are projected points. A future solver formulation must connect these two representations and include curve lifts, signs, torsion channels, relation yield, useful rank, linear algebra, and target work. No degree-of-regularity or complete ECDLP measurement exists for this construction. Direct $S_8$ has seven summands plus target; eight summands require $S_9$.

== Evidence boundary

Producer: `tools/icperf_binary_projected_base.py`; input: `research/icperf_binary_projected_base_20261017/base.json`; independent replay: `research/icperf_binary_projected_base_20261017/sage_replay.json`. The full-width arity-grid problem remains open. Canonical frontier graphs were checked and left unchanged because this is an input representation result.
